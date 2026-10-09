"""Annual E cutoffs from filed DEI category, Form 10-K and official holidays."""
from pathlib import Path
from datetime import datetime,date,time,timedelta,timezone
from zoneinfo import ZoneInfo
import json,re,hashlib
from lxml import etree,html

def build(root):
    run=json.loads((root/'work/run.json').read_text());as_of=datetime.fromisoformat(run['as_of'])
    universe=json.loads((root/'work/expected_universe.json').read_text())
    collection=json.loads((root/'work/collection.json').read_text())
    holidays=set()
    page=root/'work/reference/opm_holidays.html'
    tree=html.fromstring(page.read_bytes().decode('utf-8'))
    for table in tree.xpath('//table[contains(@class,"HolidayTable")]'):
        caption=' '.join(table.xpath('./caption//text()'));match=re.search(r'\b(20\d{2})\b',caption)
        if not match:continue
        year=match.group(1)
        for cell in table.xpath('.//tr/td[1]'):
            text=re.sub(r'[*\s]+',' ',' '.join(cell.itertext())).strip()
            if not re.search(r'\b20\d{2}\b',text):text+=', '+year
            try:holidays.add(datetime.strptime(text,'%A, %B %d, %Y').date())
            except ValueError:continue
    records=[]
    for a in universe['annuals']:
        candidates=[f for f in collection['filings'].values() if f['group']==a['group_id']
            and f['metadata']['form'] in ('10-K','10-KT') and f['metadata'].get('reportDate')==a['period_end']]
        category=None;source=None
        for f in sorted(candidates,key=lambda f:f['metadata']['acceptanceDateTime']):
            disc=json.loads((root/f['discovery_path']).read_text()) if f.get('discovery_path') else {}
            for name in disc.get('instances',[]):
                if name not in f['resources']:continue
                x=etree.fromstring((root/f['resources'][name]['path']).read_bytes(),etree.XMLParser(resolve_entities=False,no_network=True,huge_tree=True))
                values=[n.text for n in x if isinstance(n.tag,str) and n.tag.endswith('}EntityFilerCategory') and n.text]
                if values:category=values[0].strip();source=f['metadata']['accessionNumber'];break
            if category:break
        days={'large accelerated filer':60,'accelerated filer':75,'non-accelerated filer':90}.get((category or '').lower())
        deadline=None
        if days and a['period_end']!='none':
            d=date.fromisoformat(a['period_end'])+timedelta(days=days)
            while d.weekday()>4 or d in holidays:d+=timedelta(days=1)
            deadline=datetime.combine(d,time(23,59,59),ZoneInfo('America/New_York')).astimezone(timezone.utc)
        records.append(dict(a,category=category,category_source_accession=source,
            annual_deadline=deadline.isoformat() if deadline else None,
            as_known_cutoff=min(deadline,as_of).isoformat() if deadline else run['as_of'],
            cutoff_reason=None if deadline else 'historical_filer_category_or_fiscal_dates_unestablished',
            deadline_sources=['https://www.sec.gov/files/form10-k.pdf',
              'https://www.ecfr.gov/current/title-17/chapter-II/part-240/section-240.0-3',
              'https://www.opm.gov/policy-data-oversight/pay-leave/federal-holidays/']))
    out={'as_of':run['as_of'],'annuals':records,'official_holidays_count':len(holidays),
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (root/'work/reference').iterdir() if p.suffix in ('.pdf','.html')}}
    (root/'work/annual_cutoffs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print(json.dumps({'annuals':len(records),'cutoffs_established':sum(a['annual_deadline'] is not None for a in records),'official_holidays_count':len(holidays)}))

if __name__=='__main__':build(Path('.').resolve())
