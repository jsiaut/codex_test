"""SEC-only targeted discovery. Scans nominate sources; they author no observations."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urljoin
import argparse, csv, hashlib, io, json, re, zipfile
import yaml
from .network import SecClient, SessionLock, atomic_json
from .text import normalize_html
from .archives import discover, read_xbrl_archive

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


def collect_filing(root, sec, metadata, group=None):
    """Preserve official bytes and physical SGML ordering for offline replay."""
    registry = root / 'work/deepening_filings.json'
    saved = json.loads(registry.read_text()) if registry.exists() else {}
    accession = metadata['accessionNumber']
    if accession in saved: return saved[accession]
    cik = str(metadata['cik']).zfill(10)
    d = discover(sec, cik, accession)
    files = read_xbrl_archive(sec, d)
    files[metadata['primaryDocument']] = sec.get(d['base'] + metadata['primaryDocument'])
    for name in d['instances'] + [n for n in (d.get('filing_summary'), d.get('metalinks')) if n]:
        if name not in files: files[name] = sec.get(d['base'] + name)
    directory = root / 'work/deepening_data' / accession; directory.mkdir(exist_ok=True)
    resources = {}
    for name, raw in files.items():
        if Path(name).name != name: raise ValueError('Unsafe remote resource path')
        path = directory / name; path.write_bytes(raw)
        resources[name] = dict(path=str(path.relative_to(root)),url=d['base']+name,
            sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
            document_rank=next((h['document_rank'] for h in d['headers'] if h['filename']==name),-2))
    saved[accession] = dict(metadata=dict(metadata,cik=cik),group=group or 'external:'+cik,
        resources=resources,discovery=d,status='collected',retrieved_at=datetime.now(timezone.utc).isoformat())
    atomic_json(registry,saved)
    sec.lock.touch()
    return saved[accession]


def submissions(root, sec, cik):
    cik=str(cik).zfill(10)
    url='https://data.sec.gov/submissions/CIK'+cik+'.json'
    path=fetch(root,sec,url)
    meta=json.loads(path.read_text())
    registry=root/'work/deepening_issuer_metadata.json'
    saved=json.loads(registry.read_text()) if registry.exists() else {}
    saved[cik]=dict(source_url=url,source_path=str(path.relative_to(root)),metadata=meta)
    atomic_json(registry,saved)
    recent=meta['filings']['recent']
    filings=[dict((k,v[i]) for k,v in recent.items())|dict(cik=cik)
        for i in range(len(recent['accessionNumber']))]
    return meta,filings


def lenders(root):
    sec=client(root)
    try:
        nominated=json.loads((root/'work/deepening_bdc_candidates.json').read_text())
        extra=json.loads((root/'work/deepening_discovery_candidates.json').read_text())
        ciks={str(r['cik']).zfill(10) for r in nominated}
        ciks|={r['submission']['cik'].zfill(10) for r in extra if 'coreweave' in r['subjects']
            and re.search(r'fund|BDC|capital|investment',r['submission']['name'],re.I)
            and r['submission']['form'] in ('10-K','10-Q')}
        for cik in sorted(ciks):
            meta,filings=submissions(root,sec,cik)
            periodic=sorted((f for f in filings if f['form'] in ('10-K','10-Q')
                and f['filingDate']<=sec.as_of[:10]),key=lambda f:(f['filingDate'],f['accessionNumber']),reverse=True)
            for f in periodic[:2]:
                x=collect_filing(root,sec,f)
                print(json.dumps(dict(cik=cik,name=meta['name'],accession=f['accessionNumber'],form=f['form'],files=len(x['resources']))),flush=True)
    finally:sec.close()


def form_d(root):
    from urllib.parse import urlencode
    sec=client(root);all_hits=[];coverage=[]
    try:
        for subject,form in ((s,f) for s in ('OpenAI','Anthropic') for f in ('D','D/A')):
            offset=0
            while True:
                query=dict(q='"'+subject+'"',forms=form,dateRange='custom',
                    startdt='2021-01-01',enddt=sec.as_of[:10],**{'from':offset,'size':100})
                url='https://efts.sec.gov/LATEST/search-index?'+urlencode(query)
                path=fetch(root,sec,url);data=json.loads(path.read_text());hits=data.get('hits',{})
                total=hits.get('total',0);total=total.get('value',0) if isinstance(total,dict) else total
                rows=hits.get('hits',[])
                coverage.append(dict(subject=subject,form=form,offset=offset,total=total,returned=len(rows),url=url))
                all_hits.extend(dict(subject=subject,**hit) for hit in rows)
                atomic_json(root/'work/deepening_form_d_hits.json',all_hits)
                atomic_json(root/'work/deepening_form_d_searches.json',coverage)
                print(json.dumps(coverage[-1]),flush=True)
                if total>=10000:raise ValueError('Saturated query must be split before interpreting coverage')
                offset+=len(rows)
                if not rows or offset>=total:break
    finally:sec.close()
    return all_hits


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
                    if re.search(r'RiskFactor|ProspectusSummary|InvestmentObjectivesAndPractices', row['tag'], re.I): continue
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
