"""Additional primary documents. Foreign requests never use the SEC client."""
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse
import hashlib, json, subprocess
import httpx

ROOT = Path('.').resolve()
BASE = ROOT / 'work/softbank'
records = json.loads((BASE / 'sources.json').read_text())
known = {r['url'] for r in records}
client = httpx.Client(timeout=45, follow_redirects=True,
                     headers={'User-Agent': 'SEC_Project_2 quavas-s@hotmail.fr'})

def get(url, role):
    if url in known: return
    assert urlparse(url).hostname in {'group.softbank', 'disclosure2dl.edinet-fsa.go.jp','www.fsa.go.jp','laws.e-gov.go.jp'}
    response = client.get(url)
    response.raise_for_status()
    raw = response.content
    pdf = raw.startswith(b'%PDF')
    key = hashlib.sha256(url.encode()).hexdigest()
    path = BASE / 'sources' / (key + ('.pdf' if pdf else '.html'))
    path.write_bytes(raw)
    record = dict(url=url, role=role, path=str(path.relative_to(ROOT)),
                  sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw),
                  retrieved_at=datetime.now(timezone.utc).isoformat(),
                  source_jurisdiction='JP_regulator' if urlparse(url).hostname!='group.softbank' else 'JP_issuer_website',
                  sec_core_tier='F', eligible_for_sec_core=False,
                  publication_date_verified=False)
    if pdf:
        text = BASE / 'text' / (key + '.txt')
        subprocess.run(['pdftotext', '-layout', str(path), str(text)], check=True)
        record.update(text_path=str(text.relative_to(ROOT)), pages=len(text.read_text().split('\f'))-1)
    records.append(record)
    known.add(url)
    (BASE / 'sources.json').write_text(json.dumps(records, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(dict(url=url, bytes=len(raw))), flush=True)

if __name__ == '__main__':
    for path in ['/en/news/press/20260924', '/en/news/press/20260924_0',
                 '/en/ir/stock/bond', '/en/ir/stock/bond/bond4',
                 '/en/news/press/20260805', '/en/news/press/20260619',
                 '/en/news/press/20260327', '/en/news/press/20250808',
                 '/en/news/press/20250901', '/en/news/press/20251111']:
        try: get('https://group.softbank'+path, 'issuer_financing_chronology')
        except httpx.HTTPStatusError as e: print(json.dumps(dict(unavailable=path, status=e.response.status_code)))
    originals = [r['url'].replace('_en.pdf', '_ja.pdf') for r in records
                 if '/financial_reports/financial-report_' in r['url'] and r['url'].endswith('_en.pdf')]
    for url in originals:
        try: get(url, 'TSE_original_Japanese')
        except httpx.HTTPStatusError as e: print(json.dumps(dict(unavailable=url, status=e.response.status_code)))
    get('https://disclosure2dl.edinet-fsa.go.jp/searchdocument/pdf/S100G1JI.pdf',
        'EDINET_direct_historical_identity_proof')
    client.close()
