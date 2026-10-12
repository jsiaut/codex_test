"""Source collection for the authorized, transaction-bounded dependency layer.

This module serves original documents and native facts. It authors no financial
observations and never chooses a counterparty or a numerical interpretation.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re, zipfile, tarfile
import yaml, zstandard
from .network import SecClient, SessionLock
from .inventory import collect_submissions
from .archives import discover, read_xbrl_archive
from .text import normalize_html

BASE = 'work/dependencies'

def sha(path):
    with Path(path).open('rb') as file:
        return hashlib.file_digest(file, 'sha256').hexdigest()

def save(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n')
    temporary.replace(path)

def read(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default

def seed_review(root):
    """Reuse the four verified originals, without another HTTP request."""
    review = root/'work/feedback_review'
    sources = read(review/'collection/manifest.json')
    with zipfile.ZipFile(review/'review_sources.zip') as archive:
        for source in sources:
            raw = zstandard.ZstdDecompressor().decompress(archive.read(source['cache_path']))
            if hashlib.sha256(raw).hexdigest() != source['sha256']:
                raise ValueError('Review original changed')
            parts = source['cache_path'].split('/')[2:]
            target = root/'cache/archives'/Path(*parts)
            if target.exists():
                if zstandard.ZstdDecompressor().decompress(target.read_bytes()) != raw:
                    raise ValueError('Existing cached original differs')
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zstandard.ZstdCompressor(level=6).compress(raw))

def inventory(root):
    root = Path(root).resolve(); seed_review(root)
    config = yaml.safe_load((root/'config.yaml').read_text())
    cutoff = read(root/'work/run.json')['as_of']; base = root/BASE
    issuers = read(base/'issuers.json', {})
    with SessionLock(root, config['session_stale_minutes']) as lock:
        client = SecClient(root, config, cutoff, lock)
        try:
            for cik in ('0002133037','0002110365','0002007691','0001964789','0001326801'):
                if cik not in issuers:
                    issuers[cik] = collect_submissions(client, cik)
                    save(base/'issuers.json', issuers)
                eligible = [f for f in issuers[cik]['filings'] if f.get('acceptanceDateTime')
                    and datetime.fromisoformat(f['acceptanceDateTime'].replace('Z','+00:00')) <= datetime.fromisoformat(cutoff)
                    and f['form'] in ('S-1','S-1/A','F-1','F-1/A','424B4','10-K','10-Q','8-K')]
                print(json.dumps(dict(cik=cik,name=issuers[cik]['metadata']['name'],
                    filings=eligible[-12:],pagination=issuers[cik]['pagination'])), flush=True)
        finally:
            client.close()
    return issuers

def filing(root, client, cik, accession, *, contracts=(), native=False):
    """Collect an explicitly selected filing and explicitly selected exhibits."""
    root = Path(root); base = root/BASE
    registry = read(base/'filings.json', {})
    issuers = read(base/'issuers.json', {})
    official = issuers.get(cik, {})
    selected = [f for f in official.get('filings', []) if f['accessionNumber'] == accession]
    discovery = discover(client, cik, accession)
    if len(selected) == 1:
        metadata = dict(selected[0], cik=cik)
    else:
        header = client.get(discovery['base'] + accession + '-index-headers.html')
        from lxml import html
        text = html.fromstring(header).text_content()
        stamp = re.search(r'<ACCEPTANCE-DATETIME>\s*(\d{14})', text)
        if not stamp:
            raise ValueError('Original acceptance datetime absent')
        # EDGAR SGML clock is US Eastern, including daylight saving.
        from zoneinfo import ZoneInfo
        accepted = datetime.strptime(stamp.group(1), '%Y%m%d%H%M%S').replace(tzinfo=ZoneInfo('America/New_York')).astimezone(timezone.utc)
        main = discovery['headers'][0]
        metadata = dict(cik=cik,accessionNumber=accession,form=main['type'],primaryDocument=main['filename'],
            acceptanceDateTime=accepted.isoformat(),filingDate=accepted.astimezone(ZoneInfo('America/New_York')).date().isoformat(),reportDate='')
    if datetime.fromisoformat(metadata['acceptanceDateTime'].replace('Z','+00:00')) > datetime.fromisoformat(client.as_of):
        raise ValueError('Filing after frozen cutoff')
    files = read_xbrl_archive(client, discovery) if native else {}
    keep = {metadata['primaryDocument'], *contracts}
    if native:
        keep |= set(discovery['instances']) | {n for n in files if n.endswith(('.xml','.xsd')) and not re.fullmatch(r'R\d+\.xml',n)}
        keep |= {n for n in (discovery.get('metalinks'),discovery.get('filing_summary')) if n}
    resources = registry.get(accession, {}).get('resources', {})
    for name in sorted(keep):
        if name in resources:
            if sha(root/resources[name]['path']) != resources[name]['sha256']:
                raise ValueError('Collected original differs')
            continue
        raw = files[name] if name in files else client.get(discovery['base'] + name)
        target = base/'sources'/accession/name; target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(raw)
        header = next((h for h in discovery['headers'] if h['filename']==name), {})
        resources[name] = dict(path=str(target.relative_to(root)),url=discovery['base']+name,sha256=sha(target),
            bytes=len(raw),document_rank=header.get('document_rank',-2),exhibit_type=header.get('type'))
        if name.endswith(('.htm','.html')):
            text = base/'text'/accession/(name+'.txt'); text.parent.mkdir(parents=True,exist_ok=True)
            text.write_text(normalize_html(raw))
    registry[accession] = dict(metadata=metadata,discovery=discovery,resources=resources,
        group='external:'+cik,status='collected',native_collected=native or registry.get(accession,{}).get('native_collected',False))
    save(base/'filings.json',registry)
    print(json.dumps(dict(accession=accession,resources=len(resources),headers=discovery['headers'])),flush=True)
    return registry[accession]

def collect_selected(root):
    root = Path(root).resolve(); config = yaml.safe_load((root/'config.yaml').read_text())
    cutoff = read(root/'work/run.json')['as_of']
    selection = read(root/BASE/'selected_filings.json')
    with SessionLock(root, config['session_stale_minutes']) as lock:
        client = SecClient(root, config, cutoff, lock)
        try:
            for choice in selection:
                filing(root,client,**choice)
        finally:
            client.close()

def prepare_native(root):
    """Recreate native candidates; financial selection remains in author_notes."""
    from .xbrl import parse_instance,digest
    from .database import connect
    root=Path(root).resolve();base=root/BASE;facts=[];cutoff=read(base/'scope.json')['source_cutoff']
    for acc,filing_data in read(base/'filings.json').items():
        if not filing_data.get('native_collected'):continue
        metadata=filing_data['metadata']
        for name,resource in filing_data['resources'].items():
            if name not in filing_data['discovery']['instances']:continue
            parsed=parse_instance((root/resource['path']).read_bytes(),entity_id='cik:'+metadata['cik'],
                reporting_identity='reporter:'+filing_data['group'],group_id=filing_data['group'],
                document_id=digest([resource['url']]),accession=acc,acceptance_datetime=metadata['acceptanceDateTime'],
                knowledge_date=metadata['acceptanceDateTime'][:10],assurance_level='reviewed' if metadata['form']=='10-Q' else 'unaudited',as_of=cutoff)
            for fact in parsed:fact.update(document_rank=resource['document_rank'],document_rank_source='original_SEC_SGML_header_sequence',source_document_id=fact['document_id'])
            facts.extend(parsed)
    db=connect()
    for choice in read(base/'legacy_native_selections.json',[]):
        query=db.execute("SELECT * FROM read_parquet(?) WHERE accession=? AND locator=? AND document_rank>=0",
            [str(base/'baseline/facts.parquet'),choice['accession'],'id:'+choice['inline']])
        columns=[c[0] for c in query.description];selected=[dict(zip(columns,r)) for r in query.fetchall()]
        if len(selected)!=1:raise ValueError('Legacy native selection ambiguous')
        facts.extend(selected)
    db.close()
    (base/'native_catalog.jsonl').write_text(''.join(json.dumps(f,default=str)+'\n' for f in facts))
    return len(facts)

def backup(root):
    root=Path(root).resolve();base=root/BASE;archive=base/'originals.tar.zst'
    paths=sorted(p for p in (base/'sources').rglob('*') if p.is_file())
    with archive.open('wb') as raw,zstandard.ZstdCompressor(level=8).stream_writer(raw) as compressed,tarfile.open(fileobj=compressed,mode='w|') as tar:
        for path in paths:tar.add(path,arcname=str(path.relative_to(root)))
    result=dict(path=str(archive.relative_to(root)),sha256=sha(archive),bytes=archive.stat().st_size,
        sources={str(p.relative_to(root)):sha(p) for p in paths},source_cutoff=read(base/'scope.json')['source_cutoff'])
    save(base/'source_backup.json',result);return result

def restore(root):
    root=Path(root).resolve();base=root/BASE;meta=read(base/'source_backup.json');archive=root/meta['path']
    if sha(archive)!=meta['sha256']:raise ValueError('Original archive SHA differs')
    with archive.open('rb') as raw,zstandard.ZstdDecompressor().stream_reader(raw) as decompressed,tarfile.open(fileobj=decompressed,mode='r|') as tar:
        for member in tar:
            path=Path(member.name)
            if not member.isfile() or path.is_absolute() or '..' in path.parts or str(path) not in meta['sources']:
                raise ValueError('Unsafe or unregistered original archive member')
            data=tar.extractfile(member).read()
            if hashlib.sha256(data).hexdigest()!=meta['sources'][str(path)]:raise ValueError('Original member SHA differs')
            target=root/path
            if target.exists():
                if sha(target)!=meta['sources'][str(path)]:raise ValueError('Existing original differs; never substituted')
            else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    return meta

if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('action',choices=('inventory','collect','native','backup','restore'))
    args=parser.parse_args(); actions=dict(inventory=inventory,collect=collect_selected,native=prepare_native,backup=backup,restore=restore)
    actions[args.action](Path('.'))
