"""Closed structural signals from all submissions pages, independent of text."""
from pathlib import Path
from datetime import datetime
import json,hashlib,zstandard
from .database import insert
from .xbrl import digest

def run(db,root:Path,as_of):
    inv=json.loads((root/'work/inventory.json').read_text())
    universe=json.loads((root/'work/expected_universe.json').read_text())
    version=as_of.replace(':','-').replace('+','_')
    documents={};events=[]
    for group,g in inv['groups'].items():
        for cik,issuer in g['issuers'].items():
            urls=['https://data.sec.gov/submissions/CIK'+cik+'.json']+[
                'https://data.sec.gov/submissions/'+p for p in issuer['pagination']['read']]
            for url in urls:
                cache=root/'cache/api'/hashlib.sha256(url.encode()).hexdigest()/(version+'.bin.zst')
                raw=zstandard.ZstdDecompressor().decompress(cache.read_bytes())
                data=json.loads(raw);series=data.get('filings',{}).get('recent',data)
                doc=digest([url,as_of]);documents.setdefault(group,[]).append(doc)
                insert(db,'documents',{'document_id':doc,'group_id':group,'entity_id':'cik:'+cik,'cik':cik,
                    'url':url,'cache_path':str(cache.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest(),
                    'filing_status':'filed','assurance_level':'not_applicable','document_kind':'submission_metadata',
                    'tier':'C','byte_count':len(raw),'parse_status':'observed','as_of':as_of})
                for i,accession in enumerate(series.get('accessionNumber',[])):
                    form=series['form'][i];items=(series.get('items') or ['']*len(series['form']))[i]
                    date=series['filingDate'][i]
                    if date<g['analysis_start'] or date>as_of[:10]:continue
                    kinds=[]
                    if form in ('NT 10-K','NT 10-Q'):kinds.append(('sig_late_filing',form))
                    if form.startswith('8-K'):
                        for item in ('1.03','2.04','2.06','3.01'):
                            if item in items.split(','):kinds.append(('sig_distress_8k_items',item))
                        for item in ('4.01','4.02'):
                            if item in items.split(','):kinds.append(('sig_auditor_change_or_nonreliance',item))
                    for metric,label in kinds:events.append((group,date,accession,metric,label,doc,i))
    for group,date,accession,metric,label,doc,rank in events:
        q=next((q for q in universe['quarters'] if q['group_id']==group and q['period_start']!='none'
            and q['period_start']<=date<=q['period_end']),None)
        if not q:continue
        for view in ('as_known','revised'):
            insert(db,'measures',{'measure':metric,'group_id':group,'period_start':q['period_start'],'period_end':q['period_end'],
                'view':view,'as_of':as_of,'value':1,'unit':'event','status':'computed','coverage_state':'observed',
                'knowledge_date':date,'breakdown_key':accession+'|'+label,'evidence_profile':'["C"]',
                'lineage':json.dumps([doc]),'basis_break_reason':f'submissions row {rank}; form/item {label}',
                'source_perspective':'reporting_entity','accounting_framework':'us_gaap'})
