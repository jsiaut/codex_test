"""Archive official SoftBank source indexes and first-priority reports.

This discovery layer does not change EDGAR-only eligibility or core tables.
"""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urljoin,urlparse
from datetime import datetime,timezone
import hashlib,json,re,subprocess
import httpx

ROOT=Path('.').resolve();BASE=ROOT/'work/softbank';BASE.mkdir(parents=True,exist_ok=True)
RAW=BASE/'sources';RAW.mkdir(exist_ok=True);TXT=BASE/'text';TXT.mkdir(exist_ok=True)
client=httpx.Client(timeout=40,follow_redirects=True,headers={'User-Agent':'SEC_Project_2 official-source research'})
records=[]
def get(url,role):
    if urlparse(url).hostname!='group.softbank':raise ValueError('Official issuer domain only')
    key=hashlib.sha256(url.encode()).hexdigest();p=RAW/(key+('.pdf' if urlparse(url).path.endswith('.pdf') else '.html'))
    if p.exists():raw=p.read_bytes()
    else:
        r=client.get(url);r.raise_for_status();raw=r.content;p.write_bytes(raw)
    record=dict(url=url,role=role,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),
        retrieved_at=datetime.now(timezone.utc).isoformat(),source_jurisdiction='JP_issuer_website',
        sec_core_tier='F',eligible_for_sec_core=False,publication_date_verified=False)
    if p.suffix=='.pdf':
        dest=TXT/(key+'.txt');subprocess.run(['pdftotext','-layout',str(p),str(dest)],check=True)
        record['text_path']=str(dest.relative_to(ROOT));record['pages']=len(dest.read_text().split('\f'))-1
    records.append(record);return raw
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.href=None;self.label=[]
    def handle_starttag(self,t,a):
        if t=='a':self.href=dict(a).get('href');self.label=[]
    def handle_data(self,s):
        if self.href:self.label.append(s)
    def handle_endtag(self,t):
        if t=='a' and self.href:
            self.links.append(dict(url=urljoin('https://group.softbank',self.href),label=' '.join(' '.join(self.label).split())))
            self.href=None
indexes={}
for path,role in [('/en/ir/financials/financial_reports','quarterly_financial_reports_index'),
 ('/en/ir/financials/annual_reports','integrated_reports_index'),
 ('/ir/financials/security_reports','japanese_regulatory_reports_index'),
 ('/en/ir/financials','annual_financial_statements_index'),
 ('/en/ir/financials/annual_reports/2026','latest_integrated_report_index')]:
    parser=Links();parser.feed(get('https://group.softbank'+path,role).decode())
    indexes[role]=parser.links
(BASE/'links.json').write_text(json.dumps(indexes,ensure_ascii=False,indent=2)+'\n')
targets={}
for role,links in indexes.items():
    for link in links:
        u=link['url']
        if not urlparse(u).path.endswith('.pdf'):continue
        if role=='quarterly_financial_reports_index' and re.search(r'fy202[1-6]_',u):targets[u]='quarterly_financial_report'
        if role=='annual_financial_statements_index' and '/annual_reports/' in u and re.search(r'financial[-_]report.*2026|financial[-_]report.*fy2025',u):targets[u]='latest_full_financial_statements'
        if role=='japanese_regulatory_reports_index' and re.search(r'202[1-6]|fy202[1-6]',u):targets[u]='regulatory_report_mirror_filing_status_to_verify'
for u,role in targets.items():get(u,role)
for path in ['/en/news/press/20261001','/en/news/press/20260909','/en/news/press/20260327',
 '/en/news/press/20260701','/en/news/press/20260401_0','/en/news/press/20260227',
 '/en/ir/financials/annual_reports/2026/message/goto','/en/news/press/20250122']:
    get('https://group.softbank'+path,'issuer_statement_discovery_pointer')
client.close()
(BASE/'sources.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(archived=len(records),pdfs=sum(x['path'].endswith('.pdf') for x in records),
 bytes=sum(x['bytes'] for x in records),sec_core_modified=False)))
