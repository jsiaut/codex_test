"""Authorized issuer expansion: SEC bytes and natural-note inventory, no authored extraction."""
from pathlib import Path
from datetime import date, timedelta
from collections import Counter
import argparse, json, re
import yaml
from .network import atomic_json
from .deepening_sources import client, fetch, collect_filing
from .inventory import collect_submissions
from .xbrl import parse_instance, digest
from .metadata import load
from .text import extract_inline_blocks, extract_classic_blocks
from .extension import families, contains
from .deepening_reading import save

PERIODIC = {'10-K','10-K/A','10-Q','10-Q/A','20-F','20-F/A','40-F','40-F/A'}

def configuration(root):
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    auth=json.loads((root/'work/expansion/authorization.json').read_text())
    return cfg,auth

def inventory(root):
    cfg,auth=configuration(root);sec=client(root)
    saved_path=root/'work/expansion/issuers.json'
    saved=json.loads(saved_path.read_text()) if saved_path.exists() else {}
    target={str(cik).zfill(10):group for group,cik in auth['new_groups'].items()}
    target.update({cik:'external:'+cik for cik in cfg['expansion_decision']['additional_issuers']})
    try:
        for cik,group in target.items():
            if cik not in saved:
                official=collect_submissions(sec,cik)
                if str(official['metadata']['cik']).zfill(10)!=cik:raise ValueError('CIK identity mismatch')
                raw=fetch(root,sec,'https://data.sec.gov/api/xbrl/companyfacts/CIK'+cik+'.json')
                saved[cik]=dict(group=group,official=official,companyfacts_path=str(raw.relative_to(root)))
                atomic_json(saved_path,saved)
            s=saved[cik];filings=s['official']['filings']
            eligible=[dict(f,cik=cik) for f in filings if f['filingDate']<=sec.as_of[:10]
                and f.get('acceptanceDateTime','')<=sec.as_of
                and (f.get('reportDate') or f['filingDate'])>='2021-01-01']
            periodic=sorted([f for f in eligible if f['form'] in PERIODIC],
                key=lambda f:(f['filingDate'],f['accessionNumber']))
            annual=[f for f in periodic if f['form'] in {'10-K','20-F','40-F'}]
            if not annual:raise ValueError('Latest annual not found: '+cik)
            latest=annual[-1]
            selected=[f for f in periodic if f['filingDate']>=latest['filingDate']]
            s.update(periodic_filings=periodic,latest_annual=latest,text_filings=selected,
                supplemental_6k=[f for f in eligible if f['form'] in ('6-K','6-K/A') and f['filingDate']>=latest['filingDate']],
                historical_notes_state='not_processed',name=s['official']['metadata']['name'])
            atomic_json(saved_path,saved)
            print(json.dumps(dict(stage='inventory',cik=cik,name=s['name'],periodic=len(periodic),
                text_filings=len(selected),supplemental_6k=len(s['supplemental_6k']),pages=len(s['official']['pagination']['read']))),flush=True)
        # Preserve all old groups and publication cutoffs. New identifiers are
        # the already used external CIK IDs, not renamed immutable observations.
        inv=json.loads((root/'work/inventory.json').read_text())
        for cik,s in saved.items():
            if s['group'] not in auth['new_groups']:continue
            issuer=s['official'];end=sec.as_of[:10]
            rows=[dict(f,cik=cik) for f in issuer['filings'] if '2018-01-01'<=f['filingDate']<=end]
            inv['groups'][s['group']]=dict(cik=cik,status='resolved',issuers={cik:dict(issuer,role_hint='current')},
                analysis_start='2021-01-01',analysis_start_basis='authorized_expansion_fiscal_year_floor',
                read_start_provisional='2018-01-01',read_start_basis='historical_notes_not_processed_in_first_text_tranche',
                filings_in_read_window=rows,form_counts=dict(Counter(f['form'] for f in rows)),
                item_counts=dict(Counter(i.strip() for f in rows for i in f.get('items','').split(',') if i.strip())),
                membership_added_at=auth['authorized_at'],previous_main_perimeter_member=False)
        atomic_json(root/'work/inventory.json',inv)
    finally:sec.close()

def collect(root, latest_only=False):
    cfg,auth=configuration(root);sec=client(root)
    saved=json.loads((root/'work/expansion/issuers.json').read_text())
    try:
        for cik,s in saved.items():
            # A short first stage makes the natural notes reviewable while
            # the separately resumable structured history is collected.
            source=s['text_filings'] if latest_only else s['periodic_filings']
            queue=sorted(source,key=lambda f:(f['filingDate'],f['accessionNumber']),reverse=True)
            for f in queue:
                result=collect_filing(root,sec,f,s['group'])
                print(json.dumps(dict(stage='filing',issuer=s['name'],form=f['form'],accession=f['accessionNumber'],
                    files=len(result['resources']),text_selected=f in s['text_filings'])),flush=True)
            for f in s['supplemental_6k']:
                result=collect_filing(root,sec,f,s['group'])
                # Financial statements often reside in a furnished exhibit.
                resources=result['resources'];d=result['discovery']
                for h in d['headers']:
                    if not h['type'].startswith(('EX-99','EX-10')):continue
                    name=h['filename']
                    if not name or name in resources:continue
                    raw=sec.get(d['base']+name);p=root/'work/deepening_data'/f['accessionNumber']/name;p.write_bytes(raw)
                    import hashlib
                    resources[name]=dict(path=str(p.relative_to(root)),url=d['base']+name,
                        sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),document_rank=h['document_rank'])
                registry=json.loads((root/'work/deepening_filings.json').read_text());registry[f['accessionNumber']]=result
                atomic_json(root/'work/deepening_filings.json',registry)
                print(json.dumps(dict(stage='6k',issuer=s['name'],accession=f['accessionNumber'],files=len(resources))),flush=True)
    finally:sec.close()

def notes(root):
    cfg,auth=configuration(root);as_of=auth['source_cutoff']
    issuers=json.loads((root/'work/expansion/issuers.json').read_text())
    registry=json.loads((root/'work/deepening_filings.json').read_text())
    blocks=[];coverage=[];report_inventory=[]
    for cik,s in issuers.items():
        selected={f['accessionNumber'] for f in s['text_filings']}
        for accession in selected:
            filing=registry[accession];m=filing['metadata'];resources=filing['resources']
            metadata=load(root,resources,accession)
            if not metadata:
                coverage.append(dict(cik=cik,accession=accession,reason='parse_failed',detail='Natural notes require explicit HTML bounds'))
                continue
            facts=[];assurance='audited' if m['form'] in ('10-K','20-F','40-F') else 'reviewed'
            for name in filing['discovery']['instances']:
                r=resources[name]
                facts+=parse_instance((root/r['path']).read_bytes(),entity_id='cik:'+cik,reporting_identity='reporter:'+s['group'],
                    group_id=s['group'],document_id=digest([r['url']]),accession=accession,acceptance_datetime=m['acceptanceDateTime'],
                    knowledge_date=m['filingDate'],assurance_level=assurance,as_of=as_of)
            primary=resources[m['primaryDocument']];raw=(root/primary['path']).read_bytes()
            bs=extract_inline_blocks(raw,metadata,facts,normalizer_version=cfg['normalizer_version'])
            if not bs:
                # Classic instances contain the deposited escaped HTML blocks.
                for name in filing['discovery']['instances']:
                    res=resources[name]
                    for b in extract_classic_blocks((root/res['path']).read_bytes(),metadata,facts,normalizer_version=cfg['normalizer_version']):
                        b['resource_override']=res;bs.append(b)
            eligible=[]
            financial_roles={r['role'] for instance in metadata['instance'].values() for r in instance['report'].values()
                if r.get('menuCat')=='Notes' and r.get('groupType')=='disclosure'
                and not r['role'].startswith('http://xbrl.sec.gov/ecd/')}
            for b in bs:
                if not financial_roles.intersection(b.get('note_roles',[])):continue
                fs=families(b.get('label','')+' '+b.get('concept',''))
                if re.search(r'related.?part|\bequity\b|warrant|stockholders.?equity|share.?based|stock.?based|organization|subsequent',b.get('label','')+' '+b.get('concept',''),re.I):
                    fs=fs or ['investments_note']
                report_inventory.append(dict(cik=cik,accession=accession,label=b.get('label'),concept=b.get('concept'),families=fs))
                if not fs:continue
                b['note_families']=fs;eligible.append(b)
            # Parent natural notes contain their component/table blocks.
            parents=[b for b in eligible if not any(o is not b and contains(o,b)
                and (len(o['text'])>len(b['text']) or o['raw_byte_start']<b['raw_byte_start']) for o in eligible)]
            for b in parents:
                resource=b.pop('resource_override',primary)
                b.update(group=s['group'],accession=accession,entity_id='cik:'+cik,form=m['form'],knowledge_date=m['filingDate'],
                    acceptance_datetime=m['acceptanceDateTime'],as_of=as_of,source_path=resource['path'],document_id=digest([resource['url']]),
                    assurance_level=assurance,location='financial_statements_and_notes',block_class=b['note_families'][0],financial_note=True)
                b['occurrence_id']=digest([b['content_key'],b['document_id'],b['raw_byte_start']]);blocks.append(b)
            coverage.append(dict(cik=cik,name=s['name'],accession=accession,reason='collected',notes=len(parents)))
        for f in s['periodic_filings']:
            if f['accessionNumber'] not in selected:
                coverage.append(dict(cik=cik,accession=f['accessionNumber'],reason='not_processed',detail='Historical structured source; text outside first tranche'))
    blocks.sort(key=lambda b:(-int(b['knowledge_date'].replace('-','')),b['group'],b['accession'],b['raw_byte_start']))
    # A repeated source occurrence retains its original immutable metadata.
    blocks=[json.loads((root/'work/blocks'/(b['occurrence_id']+'.json')).read_text())
        if (root/'work/blocks'/(b['occurrence_id']+'.json')).exists() else b for b in blocks]
    rows=save(root,blocks)
    atomic_json(root/'work/expansion/queue.json',rows);atomic_json(root/'work/expansion/note_coverage.json',coverage)
    atomic_json(root/'work/expansion/note_reports.json',report_inventory)
    print(json.dumps(dict(blocks=len(rows),chars=sum(r['chars'] for r in rows),by_group=dict(Counter(r['group'] for r in rows)),
        unread=sum(not (root/'work/observations'/(r['content_key']+'.jsonl')).exists() for r in rows))),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['inventory','collect','notes']);p.add_argument('--latest-only',action='store_true');args=p.parse_args()
    if args.action=='collect':collect(Path('.').resolve(),args.latest_only)
    else:globals()[args.action](Path('.').resolve())
