"""SEC-only targeted discovery. Scans nominate sources; they author no observations."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin
import argparse, csv, hashlib, io, json, re, zipfile
import yaml
from .network import SecClient, SessionLock, atomic_json
from .text import normalize_html

csv.field_size_limit(8_000_000)
SUBJECTS = re.compile(r'\b(?:CoreWeave|OpenAI|Anthropic)\b', re.I)


def records(z, suffix):
    name = next(n for n in z.namelist() if n.endswith(suffix))
    with z.open(name) as raw:
        yield from csv.DictReader(io.TextIOWrapper(raw, encoding='utf-8-sig'), delimiter='\t')


def client(root):
    cfg = yaml.safe_load((root / 'config.yaml').read_text())
    as_of = json.loads((root / 'work/run.json').read_text())['as_of']
    lock = SessionLock(root, cfg['session_stale_minutes'])
    lock.token = json.loads((root / 'work/foreground_owner.json').read_text())['token']
    lock.touch()
    return SecClient(root, cfg, as_of, lock)


def fetch(root, sec, url):
    directory = root / 'work/deepening_data'
    directory.mkdir(exist_ok=True)
    raw = sec.get(url)
    path = directory / Path(url.split('?')[0]).name
    if path.suffix not in ('.zip', '.pdf'):
        path = directory / (hashlib.sha256(url.encode()).hexdigest() + '.bin')
    path.write_bytes(raw)
    manifest = root / 'work/deepening_source_manifest.json'
    saved = json.loads(manifest.read_text()) if manifest.exists() else {}
    saved.setdefault(url, dict(url=url, path=str(path.relative_to(root)),
          cache_path=str(sec._cache_path(url).relative_to(root)), sha256=hashlib.sha256(raw).hexdigest(),
          bytes=len(raw), retrieved_at=datetime.now(timezone.utc).isoformat(), source_as_of=sec.as_of))
    atomic_json(manifest, saved)
    return path


def bdc(root):
    sec = client(root)
    results, vintages = [], []
    try:
        links = json.loads((root / 'work/bdc_dataset_index.json').read_text())['links']
        for label, href in links:
            if not href.endswith('.zip'): continue
            path = fetch(root, sec, urljoin('https://www.sec.gov', href))
            matches, count = [], 0
            with zipfile.ZipFile(path) as z:
                for rank, row in enumerate(records(z, 'soi.tsv')):
                    count += 1
                    if row['filed'] > sec.as_of[:10]: continue
                    # Identification axes only: incidental mentions in a rate label
                    # or the lender's own legal name do not nominate an investment.
                    identifying = ' '.join(v for k, v in row.items()
                        if 'Axis' in k and ('Issuer' in k or 'Identifier' in k))
                    if SUBJECTS.search(identifying):
                        matches.append(dict(row, source_vintage=label,
                            source_archive=path.name, source_row=rank + 2))
            results.extend(matches)
            vintages.append(dict(vintage=label, archive=path.name, rows=count, matched_rows=len(matches)))
            atomic_json(root / 'work/deepening_bdc_candidates.json', results)
            atomic_json(root / 'work/deepening_bdc_vintages.json', vintages)
            print(json.dumps(vintages[-1]), flush=True)
    finally:
        sec.close()
    return results


def notes(root):
    sec = client(root)
    candidates, coverage = [], []
    known = set(yaml.safe_load((root / 'config.yaml').read_text())['groups'].values())
    try:
        links = json.loads((root / 'work/notes_dataset_index.json').read_text())['links']
        for label, href in links:
            if not href.endswith('.zip'): continue
            # A declared first discovery tranche; older periods are recorded as
            # incomplete coverage, never interpreted as absence of a relationship.
            name = Path(href).name
            selected = bool(re.match(r'2026_0[1-9]_notes.zip$|2025_(?:10|11|12)_notes.zip$', name))
            if not selected:
                coverage.append(dict(archive=name, status='not_collected', reason='outside_initial_discovery_tranche'))
                continue
            path = fetch(root, sec, urljoin('https://www.sec.gov', href))
            found, scanned = [], 0
            with zipfile.ZipFile(path) as z:
                submissions = {r['adsh']: r for r in records(z, 'sub.tsv')
                    if r['filed'].replace('-', '') <= sec.as_of[:10].replace('-', '')
                    and r['cik'].zfill(10) not in known}
                note_reports = {(r['adsh'], r['report']) for r in records(z, 'ren.tsv')
                    if r['adsh'] in submissions and r['menucat'] in ('N', 'Notes')}
                note_keys = {(r['adsh'], r['tag'], r['version']) for r in records(z, 'pre.tsv')
                    if (r['adsh'], r['report']) in note_reports}
                for rank, row in enumerate(records(z, 'txt.tsv')):
                    scanned += 1
                    if (row['adsh'], row['tag'], row['version']) not in note_keys: continue
                    if not SUBJECTS.search(row['value']): continue
                    text = normalize_html(row['value'].encode())
                    subjects = sorted(set(m.group(0).lower() for m in SUBJECTS.finditer(text)))
                    if not subjects: continue
                    # All original TSV identity columns, notably dimh, are retained.
                    row = dict(row, subjects=subjects, submission=submissions[row['adsh']],
                        source_archive=name, source_row=rank + 2,
                        mention_class='related_parties' if re.search(r'related.?part', row['tag'], re.I) else 'note',
                        tagged_named_amount=None, text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                        text_chars=len(text), txt_length_state='shorter_than_published_length'
                            if len(row['value']) < int(row.get('txtlen') or 0) / 2 else 'not_flagged')
                    found.append(row)
                # Ranking uses only deposited tagged numbers with a subject in
                # their dimensions. No authored observation supplies this amount.
                dims = {r['dimhash'] for r in records(z, 'dim.tsv')
                    if SUBJECTS.search(r.get('segments', '') + ' ' + r.get('segt', ''))}
                amounts = {}
                for r in records(z, 'num.tsv'):
                    if r['adsh'] not in submissions or r['dimh'] not in dims or r['uom'] != 'USD': continue
                    try: value = abs(__import__('decimal').Decimal(r['value']))
                    except Exception: continue
                    amounts[r['adsh']] = max(amounts.get(r['adsh'], 0), value)
                for row in found:
                    if row['adsh'] in amounts: row['tagged_named_amount'] = str(amounts[row['adsh']])
            candidates.extend(found)
            coverage.append(dict(archive=name, status='scanned', txt_rows=scanned, eligible_blocks=len(found)))
            atomic_json(root / 'work/deepening_discovery_candidates.json', candidates)
            atomic_json(root / 'work/deepening_discovery_coverage.json', coverage)
            print(json.dumps(coverage[-1]), flush=True)
        candidates.sort(key=lambda r: (0 if r['mention_class'] == 'related_parties' else 1,
            -__import__('decimal').Decimal(r['tagged_named_amount'] or '0'), -len(r['subjects']), r['adsh'], r['tag'], r['dimh']))
        atomic_json(root / 'work/deepening_discovery_candidates.json', candidates)
        atomic_json(root / 'work/deepening_discovery_coverage.json', coverage)
    finally:
        sec.close()
    return candidates


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('action', choices=['bdc', 'notes'])
    args = p.parse_args(); root = Path('.').resolve()
    globals()[args.action](root)
