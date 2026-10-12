"""Native SEC Dell assembly, isolated from the preserved 24-group model."""
from pathlib import Path
from datetime import datetime
import argparse, hashlib, json, os, shutil
from decimal import Decimal
import duckdb,yaml
from .database import create,bulk_insert,insert,export,table_counts,TABLES,sql_literal
from .xbrl import digest,canonical_qname,filing_namespaces
from .dell_sources import CIK,GROUP,state,sha,persist

PRIMARY='cik:'+CIK

def prepare(root):
    base=state(root);mini=base/'assembly';(mini/'work').mkdir(parents=True,exist_ok=True)
    cfg=yaml.safe_load((root/'config.yaml').read_text());cfg['groups']['DELL']=CIK
    cfg['groups']['external:0001065521']='0001065521'
    (mini/'config.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False,allow_unicode=True))
    for name in ['schema.sql','queries.sql']:shutil.copy2(root/name,mini/name)
    # All paths in resources are absolute within this isolated calculation.
    registry=json.loads((base/'filings.json').read_text());collection={'companyfacts':{},'filings':{}}
    for acc,f in registry.items():
        f=json.loads(json.dumps(f))
        for r in f['resources'].values():r['path']=str(root/r['path'])
        d=mini/'work'/('discovery_'+acc+'.json');persist(d,f['discovery']);f['discovery_path']=str(d)
        collection['filings'][acc]=f
    cf=base/'companyfacts.json';url='https://data.sec.gov/api/xbrl/companyfacts/CIK'+CIK+'.json'
    collection['companyfacts'][CIK]=dict(group=GROUP,path=str(cf),url=url)
    persist(mini/'work/collection.json',collection)
    issuer=json.loads((base/'issuer.json').read_text());asof=issuer['source_cutoff']
    known=[f for f in issuer['official']['filings'] if f.get('acceptanceDateTime') and
        datetime.fromisoformat(f['acceptanceDateTime'].replace('Z','+00:00'))<=datetime.fromisoformat(asof)]
    official=dict(issuer['official'],filings=known)
    ends=sorted({f['reportDate'] for f in known if f['form'] in ('10-K','10-Q') and f.get('reportDate')})
    g=dict(cik=CIK,status='resolved',issuers={CIK:official},analysis_start='2020-02-01',
        analysis_start_basis='FY2021_begins_after_January31_2020',quarter_boundaries=ends,
        read_start_provisional='2018-02-01',history_left_censored=not issuer['history_pages_complete'])
    persist(mini/'work/inventory.json',dict(as_of=asof,groups={GROUP:g}))
    persist(mini/'work/run.json',dict(as_of=asof))
    persist(mini/'work/extension_authorization.json',dict(components=['investments_note','debt_note','lease_note','commitments_note','concentration_narrative']))
    for name in ['deprecations.json','fact_semantic_quarantines.json']:
        shutil.copy2(root/'work'/name,mini/'work'/name)
    for name in ['cache','work/reference']:
        target=mini/name;target.parent.mkdir(parents=True,exist_ok=True)
        if not target.exists():target.symlink_to(root/name,target_is_directory=True)
    # SEC API aggregation is collected without a date bound; facts are admitted
    # only at their actual acceptance time, never by API retrieval time.
    from .rebuild import instance_rows,companyfacts_rows
    mappings=[];facts=list(instance_rows(mini,collection,asof,mappings))
    from .document_order import provenance
    for f in facts:
        if f['document_rank']!=-2 or not f['locator'].startswith('id:'):continue
        filing=collection['filings'][f['accession']]
        ns=filing_namespaces(mini,filing['resources'])
        choices=provenance(str(mini),f['accession'])['inline'].get(f['locator'][3:],set())
        if len(choices)==1:
            rank,did,lexical=next(iter(choices))
            if canonical_qname(lexical,ns)==f['concept']:
                f.update(document_rank=rank,document_rank_source='exact_inline_id_and_namespace_resolved_concept',source_document_id=did,
                    coverage_state='unknown' if f['is_nil'] else 'explicit_zero' if f['explicit_zero'] else 'observed')
    api=list(companyfacts_rows(mini,collection,dict(groups={GROUP:g}),asof))
    facts += [f for f in api if datetime.fromisoformat(f['acceptance_datetime'].replace('Z','+00:00'))<=datetime.fromisoformat(asof)]
    # Reject same-ID conflicting API occurrences; never average their values.
    unique={}
    for f in facts:
        if f['fact_id'] in unique and unique[f['fact_id']]['value']!=f['value']:
            unique[f['fact_id']].update(value=None,coverage_state='conflicting',explicit_zero=False)
        else:unique.setdefault(f['fact_id'],f)
    facts=list(unique.values())
    (base/'native_facts.jsonl').write_text(''.join(json.dumps(f,default=str,ensure_ascii=False)+'\n' for f in facts))
    persist(base/'concept_mappings.json',mappings)
    from .universe import build
    from .deadlines import build as deadlines
    from .extension_assembly import extend_universe
    build(mini);deadlines(mini);extend_universe(mini)
    print(json.dumps(dict(stage='Dell_native_inputs',facts=len(facts),mapped=sum(bool(f.get('model_quantity')) for f in facts))),flush=True)
    return mini,collection,facts

def documents(db,root,collection,asof):
    for accession,f in collection['filings'].items():
        m=f['metadata'];periodic=m['form'] in ('10-K','10-K/A','10-Q','10-Q/A')
        for name,r in f['resources'].items():
            typ=r.get('exhibit_type') or ''
            contract=bool(__import__('re').match(r'^EX-(?:10|4)(?:\.|$)',typ))
            is_primary=name==m['primaryDocument']
            assure='audited' if m['form'].startswith('10-K') and periodic else 'reviewed' if periodic else 'not_applicable' if contract else 'unaudited'
            tier='A' if assure=='audited' else 'B' if assure=='reviewed' else 'D' if contract else 'C'
            path=Path(r['path'])
            insert(db,'documents',dict(document_id=digest([r['url']]),group_id=GROUP,entity_id=PRIMARY,cik=CIK,accession=accession,
                document_rank=r['document_rank'],url=r['url'],cache_path=str(path.relative_to(root)),sha256=sha(path),form=m['form'],
                item=m.get('items'),exhibit_type=typ or None,filing_status='filed' if periodic or contract else 'unclassified',
                assurance_level=assure,tier=tier,incorporated_by_reference=False,
                document_kind='primary_filing' if is_primary else 'contract' if contract else 'instance' if name.endswith('_htm.xml') else 'metadata',
                acceptance_datetime=m['acceptanceDateTime'],filing_date=m['filingDate'],knowledge_date=m['filingDate'],
                period_end=m.get('reportDate') or None,byte_count=r['bytes'],parse_status='observed',as_of=asof))
    cf=state(root)/'companyfacts.json';url=collection['companyfacts'][CIK]['url']
    insert(db,'documents',dict(document_id=digest([url,asof]),group_id=GROUP,entity_id=PRIMARY,cik=CIK,url=url,
        cache_path=str(cf.relative_to(root)),sha256=sha(cf),filing_status='unclassified',document_rank=-1,
        document_kind='api_aggregate',assurance_level='unknown',tier='E',byte_count=cf.stat().st_size,parse_status='observed',as_of=asof))

def native(root):
    base=state(root);mini,collection,facts=prepare(root);asof=json.loads((base/'issuer.json').read_text())['source_cutoff']
    db=create(root);documents(db,root,collection,asof)
    bulk_insert(db,'facts',facts,root,'dell_native_facts')
    from .mapping import refresh
    refresh(db,mini,collection)
    from .calculation import core_calibration
    core_calibration(db,root,asof)
    from .controls import component_controls,concentration_controls,lease_controls,eps_controls
    from .controls_extended import run as extended_controls
    component_controls(db,mini,collection,asof);concentration_controls(db,asof);lease_controls(db,asof);eps_controls(db,asof,'0.10')
    extended_controls(db,mini,collection,asof)
    from .quarter_series import prepare as quarters,measures as quarter_measures
    quarters(db,mini,asof);quarter_measures(db,asof)
    from .tier1_numeric import stocks,tagged_components,liquidity_and_leases
    stocks(db,asof);tagged_components(db,asof)
    from .ttm import run as ttm
    ttm(db,asof);liquidity_and_leases(db,asof)
    from .numeric_extended import run as numeric
    numeric(db,asof)
    from .metadata_signals import run as signals
    signals(db,mini,asof)
    from .enrichment import run as enrichment
    enrichment(db,asof)
    db.execute('UPDATE measures SET information_cutoff=COALESCE(information_cutoff,as_of),as_of=?',[asof])
    export(db,base/'native_tables')
    persist(base/'native_counts.json',table_counts(db))
    print(json.dumps(dict(stage='Dell_native_tables',counts=table_counts(db))),flush=True)
    db.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['native']);a=p.parse_args()
    globals()[a.action](Path('.').resolve())
