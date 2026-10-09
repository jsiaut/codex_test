from __future__ import annotations
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile
from lxml import html
from .network import SecClient, ResourceUnavailable


def filing_base(cik: str, accession: str) -> str:
    if not re.fullmatch(r'\d{10}-\d{2}-\d{6}', accession):
        raise ValueError('Accesssion invalide.')
    if not re.fullmatch(r'\d{1,10}', cik):
        raise ValueError('CIK invalide.')
    return f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace("-", "")}/'


def parse_document_headers(raw: bytes) -> list[dict]:
    # The index-headers resource contains the SGML header as an HTML pre.
    text = html.fromstring(raw).text_content() if b'<html' in raw.lower() else raw.decode('utf-8', errors='replace')
    records = []
    for rank, body in enumerate(re.findall(r'<DOCUMENT>(.*?)(?:</DOCUMENT>|(?=<DOCUMENT>)|\Z)', text, re.S | re.I)):
        record = {'document_rank': rank}
        for tag in ('TYPE','SEQUENCE','FILENAME','DESCRIPTION'):
            match = re.search(rf'<{tag}>\s*([^\r\n<]*)', body, re.I)
            if match:
                record[tag.lower()] = match.group(1).strip()
        if 'filename' in record:
            records.append(record)
    return records


def discover(client: SecClient, cik: str, accession: str) -> dict:
    base = filing_base(cik, accession)
    index = client.json(base + 'index.json')
    names = [entry['name'] for entry in index['directory']['item']]
    headers_name = accession + '-index-headers.html'
    headers = parse_document_headers(client.get(base + headers_name))
    return {'cik': cik, 'accession': accession, 'base': base, 'inventory': index['directory']['item'],
        'names': names, 'headers': headers,
        'xbrl_archives': [n for n in names if n.endswith('-xbrl.zip')],
        'instances': sorted(set([n for n in names if n.endswith('_htm.xml')] +
            [h['filename'] for h in headers if h['type']=='EX-101.INS'])),
        'filing_summary': 'FilingSummary.xml' if 'FilingSummary.xml' in names else None,
        'metalinks': 'MetaLinks.json' if 'MetaLinks.json' in names else None}


def read_xbrl_archive(client: SecClient, discovery: dict) -> dict[str,bytes]:
    names = discovery['xbrl_archives']
    if not names:
        return {}
    if len(names) != 1:
        raise ValueError('Plusieurs archives XBRL : classement nécessaire.')
    raw = client.get(discovery['base'] + names[0])
    files = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for entry in archive.infolist():
            # Keep resource bytes; never extract remote paths to the filesystem.
            if entry.is_dir():
                continue
            name = Path(entry.filename).name
            if name in files:
                raise ValueError('Archive avec noms de documents ambigus.')
            files[name] = archive.read(entry)
    return files
