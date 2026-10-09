from __future__ import annotations
from datetime import date,timedelta
from pathlib import Path
import json
import yaml
from lxml import etree


def refine(root: Path):
    inv=json.loads((root/'work/inventory.json').read_text());cfg=yaml.safe_load((root/'config.yaml').read_text())
    collection=json.loads((root/'work/collection.json').read_text())
    derived={}
    for accession,f in collection['filings'].items():
        if f['metadata']['form'] not in ('10-K','10-KT','10-Q','10-QT'):continue
        disc=json.loads((root/f['discovery_path']).read_text()) if f.get('discovery_path') else {}
        for name in disc.get('instances',[]):
            if name not in f['resources']:continue
            tree=etree.fromstring((root/f['resources'][name]['path']).read_bytes(),
                etree.XMLParser(resolve_entities=False,no_network=True,huge_tree=True))
            dates=[n.text.strip() for n in tree if isinstance(n.tag,str) and n.tag.endswith('}DocumentPeriodEndDate') and n.text]
            if len(set(dates))==1:derived[accession]=dates[0]
    discrepancies=[]
    for group,g in inv['groups'].items():
        end_set=set()
        for issuer in g.get('issuers',{}).values():
            for r in issuer['filings']:
                if r['form'] not in ('10-K','10-KT','10-Q','10-QT'):continue
                end=derived.get(r['accessionNumber'],r.get('reportDate'))
                if end and end<=inv['as_of'][:10]:end_set.add(end)
                if r['accessionNumber'] in derived and r.get('reportDate')!=end:
                    discrepancies.append({'group':group,'accession':r['accessionNumber'],
                        'submissions_report_date':r.get('reportDate'),'instance_period_end':end})
        ends=sorted(end_set)
        if g.get('analysis_start_basis')=='previous_fiscal_year_end_plus_one_day':
            previous=(date.fromisoformat(g['analysis_start'])-timedelta(days=1)).isoformat()
            try:index=ends.index(previous)
            except ValueError:index=-1
            if index>=12:
                # The actual issuer quarter boundaries handle 52/53-week years.
                boundaries=ends[index-12:index+1]
                continuous=all(65<=(date.fromisoformat(b)-date.fromisoformat(a)).days<=110 for a,b in zip(boundaries,boundaries[1:]))
                if continuous:
                    g['history_left_censored']=False
                    g['read_start']=(date.fromisoformat(ends[index-12])+timedelta(days=1)).isoformat()
                    g['extended_start']=(date.fromisoformat(ends[index-4])+timedelta(days=1)).isoformat()
                    g['read_start_basis']='twelve_actual_fiscal_quarters_before_analysis_start'
                else:g['history_left_censored']=True
            else:g['history_left_censored']=True
        else:
            g['history_left_censored']=True
            g['read_start_basis']='not_established_missing_historical_fiscal_reports'
        g['quarter_boundaries']=ends
    (root/'work/inventory.json').write_text(json.dumps(inv,indent=2))
    (root/'work/period_metadata_discrepancies.json').write_text(json.dumps(discrepancies,indent=2))
    print(json.dumps({k:{'analysis_start':g['analysis_start'],'read_start':g.get('read_start'),
        'basis':g['read_start_basis'] if 'read_start_basis' in g else 'unestablished',
        'history_left_censored':g.get('history_left_censored',False)} for k,g in inv['groups'].items()}))


if __name__=='__main__':refine(Path('.').resolve())
