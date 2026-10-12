"""Native SEC SMCI assembly, isolated from the preserved 25-group model."""
from pathlib import Path
from datetime import datetime
import argparse, hashlib, json, os, shutil
from decimal import Decimal
import duckdb,yaml
from .database import create,bulk_insert,insert,export,table_counts,TABLES,sql_literal
from .xbrl import digest,canonical_qname,filing_namespaces
from .smci_sources import CIK,GROUP,state,sha,persist

PRIMARY='cik:'+CIK

def isolated_queries(source):
    # The appended views are presentation helpers for older cohorts. They do
    # not participate in the SEC calculation and must not bind external files
    # while constructing an isolated issuer delta.
    core=source.split('-- SoftBank official-source extension:',1)[0]
    if 'read_parquet(' in core:raise ValueError('Unexpected file-backed dependency in isolated SEC queries')
    return core

def prepare(root):
    base=state(root);mini=base/'assembly';(mini/'work').mkdir(parents=True,exist_ok=True)
    cfg=yaml.safe_load((root/'config.yaml').read_text());cfg['groups']['SMCI']=CIK
    cfg['groups']['external:0001065521']='0001065521'
    cfg['groups']['DELL']='0001571996'
    cfg['concept_anchors_overrides']={}
    (mini/'config.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False,allow_unicode=True))
    for name in ['schema.sql','queries.sql']:shutil.copy2(root/name,mini/name)
    (mini/'queries.sql').write_text(isolated_queries((root/'queries.sql').read_text()))
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
    g=dict(cik=CIK,status='resolved',issuers={CIK:official},analysis_start='2020-07-01',
        analysis_start_basis='FY2021_begins_July1_2020',quarter_boundaries=ends,
        read_start_provisional='2018-07-01',history_left_censored=not issuer['history_pages_complete'])
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
    # A filed MD&A remains unaudited even when its amounts are tagged. Map
    # assurance to actual primary-statement and financial-note occurrences.
    from .metadata import load as metadata
    from .text import extract_inline_blocks
    byaccession={}
    for f in facts:
        if f['document_rank']>=0:byaccession.setdefault(f['accession'],[]).append(f)
    for acc,fs in byaccession.items():
        filing=collection['filings'][acc]
        if filing['metadata']['form'] not in ('10-K','10-K/A','10-Q','10-Q/A'):continue
        meta=metadata(mini,filing['resources'],acc)
        if not meta:continue
        roles={r['role'] for inst in meta['instance'].values() for r in inst['report'].values()
            if r.get('menuCat')=='Notes' and r.get('groupType')=='disclosure'
            and not r['role'].startswith('http://xbrl.sec.gov/ecd/')}
        raw=(Path(filing['resources'][filing['metadata']['primaryDocument']]['path'])).read_bytes()
        blocks=extract_inline_blocks(raw,meta,fs,normalizer_version=cfg['normalizer_version'])
        if not blocks:continue # Original classic EX101 is separately deposited.
        note_ids={c['fact_id'] for b in blocks if roles.intersection(b.get('note_roles',[])) for c in b['candidates']}
        for f in fs:
            if not f['primary_statement_occurrence'] and f['fact_id'] not in note_ids:
                f.update(tier='C',assurance_level='unaudited',location='filed_MDandA_or_other_outside_reviewed_notes')
    (base/'native_facts.jsonl').write_text(''.join(json.dumps(f,default=str,ensure_ascii=False)+'\n' for f in facts))
    persist(base/'concept_mappings.json',mappings)
    from .universe import build
    from .deadlines import build as deadlines
    from .extension_assembly import extend_universe
    build(mini);deadlines(mini);extend_universe(mini)
    print(json.dumps(dict(stage='SMCI_native_inputs',facts=len(facts),mapped=sum(bool(f.get('model_quantity')) for f in facts))),flush=True)
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
            if typ.startswith(('EX-21','EX-23','EX-16','EX-99')):
                assure='not_applicable';tier='C'
            path=Path(r['path'])
            insert(db,'documents',dict(document_id=digest([r['url']]),group_id=GROUP,entity_id=PRIMARY,cik=CIK,accession=accession,
                document_rank=r['document_rank'],url=r['url'],cache_path=str(path.relative_to(root)),sha256=sha(path),form=m['form'],
                item=m.get('items'),exhibit_type=typ or None,filing_status='furnished' if typ.startswith('EX-99') and any(x in (m.get('items') or '') for x in ('2.02','7.01')) else 'filed' if periodic or contract or (is_primary and not any(x in (m.get('items') or '') for x in ('2.02','7.01'))) or typ.startswith('EX-16') else 'unclassified',
                assurance_level=assure,tier=tier,incorporated_by_reference=False,
                document_kind='primary_filing' if is_primary else 'contract' if contract else 'instance' if name.endswith('_htm.xml') else 'metadata',
                acceptance_datetime=m['acceptanceDateTime'],filing_date=m['filingDate'],knowledge_date=m['filingDate'],
                period_end=m.get('reportDate') or None,byte_count=r['bytes'],parse_status='observed',as_of=asof))
    cf=state(root)/'companyfacts.json';url=collection['companyfacts'][CIK]['url']
    insert(db,'documents',dict(document_id=digest([url,asof]),group_id=GROUP,entity_id=PRIMARY,cik=CIK,url=url,
        cache_path=str(cf.relative_to(root)),sha256=sha(cf),filing_status='unclassified',document_rank=-1,
        document_kind='api_aggregate',assurance_level='unknown',tier='E',byte_count=cf.stat().st_size,parse_status='observed',as_of=asof))

def native(root):
    from .smci_sources import restore
    if not all((root/r['path']).exists() for f in json.loads((state(root)/'filings.json').read_text()).values() for r in f['resources'].values()):restore(root)
    base=state(root);mini,collection,facts=prepare(root);asof=json.loads((base/'issuer.json').read_text())['source_cutoff']
    db=create(root);documents(db,root,collection,asof)
    bulk_insert(db,'facts',facts,root,'smci_native_facts')
    from .mapping import refresh
    refresh(db,mini,collection)
    from .calculation import core_calibration
    core_calibration(db,mini,asof)
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
    print(json.dumps(dict(stage='SMCI_native_tables',counts=table_counts(db))),flush=True)
    db.close()

def measure(db,asof,name,pe,amount=None,lineage=(),ps=None,view='revised',**extra):
    row=dict(measure=name,group_id=GROUP,entity_id=PRIMARY,period_start=ps or 'none',period_end=pe,
        view=view,as_of=asof,information_cutoff=asof,value=amount,unit='USD',currency='USD',status='computed',
        coverage_state='observed',lineage=json.dumps(list(lineage)),tier=2,source_perspective='reporting_entity',accounting_framework='us_gaap')
    row.update(extra)
    if amount is None and row['status']=='computed':row.update(status='not_determinable',nd_reason='public_amount_not_established',coverage_state='not_disclosed')
    insert(db,'measures',row)

def load_readings(db,root,asof):
    authored=json.loads((state(root)/'authored_observations.json').read_text())
    bulk_insert(db,'observations',authored,root,'smci_authored_observations')
    return authored

def supplemental(db,root,asof,authored):
    from .assembly import rows
    annual=next(f for f in json.loads((state(root)/'filings.json').read_text()).values() if f['metadata']['accessionNumber']=='0001375365-26-000022')
    url=annual['resources'][annual['metadata']['primaryDocument']]['url']
    insert(db,'entities',dict(entity_id=PRIMARY,membership_id=digest(['SMCI_primary',PRIMARY]),legal_name='Super Micro Computer, Inc.',normalized_name='super micro computer, inc.',cik=CIK,entity_status='confirmed',group_id=GROUP,economic_group_id=GROUP,consolidation_treatment='parent',membership_start='2026-06-30',knowledge_date='2026-08-31',resolution_rule='official_SEC_CIK_plus_audited_consolidation_policy',evidence_document_id=digest([url]),evidence_locator='annual_financial_statements',source_perspective='reporting_entity',as_of=asof))
    for o in authored:
        if o.get('amount') is not None:
            measure(db,asof,'smci_reported_quantity',str(o['period_end']),Decimal(o['amount']),[o['observation_id']],o.get('period_start'),breakdown_key=o['model_quantity'],unit=o['unit'],currency=o.get('currency'),knowledge_date=o['knowledge_date'],evidence_profile=json.dumps([o['tier']]))
    by={o['model_quantity']:o for o in authored}
    def derived(name,value,sources,start=None):
        measure(db,asof,'smci_derived_quantity','2026-06-30',value,[by[q]['observation_id'] for q in sources],start,breakdown_key=name,knowledge_date='2026-08-31',evidence_profile='A;USD_US_GAAP_consolidated')
    derived('fcf_basic_annual',Decimal(by['cfo_annual']['amount'])-Decimal(by['capex_paid_annual']['amount']),['cfo_annual','capex_paid_annual'],'2025-07-01')
    derived('debt_interest_bearing_carrying_total',Decimal(by['bank_debt_total']['amount'])+Decimal(by['convertible_debt_total_book']['amount']),['bank_debt_total','convertible_debt_total_book'])
    # Named commercial relations remain separate from financing amounts.
    for alias,name,quantity in [('Ablecom','Ablecom Technology Inc','Ablecom_dependency'),('Compuware','Compuware Technology Inc','Compuware_trade_credit_limit')]:
        o=by[quantity];eid='legal:'+digest(name);g='EXT:'+alias
        insert(db,'entities',dict(entity_id=eid,membership_id=digest(['SMCI_related_party_20260630',eid]),legal_name=name,normalized_name=name.casefold(),entity_status='confirmed',group_id=g,economic_group_id=g,consolidation_treatment='undetermined',membership_start='2026-06-30',knowledge_date=o['knowledge_date'],resolution_rule='audited_note_named_related_party;no_consolidation_from_family_interest',evidence_document_id=o['document_id'],evidence_locator=o['locator'],source_perspective='reporting_entity',as_of=asof))
        insert(db,'links',dict(link_id=digest(['SMCI_commercial_relation',eid]),edge_kind='relation',family='commercial',type='purchase',from_entity_id=PRIMARY,to_entity_id=eid,from_group_id=GROUP,to_group_id=g,period_end='2026-06-30',knowledge_date=o['knowledge_date'],stage='recognized',observation_id=o['observation_id'],document_id=o['document_id'],locator=o['locator'],filing_status='filed',assurance_level='audited',tier='A',counterparty_evidence='named',source_perspective='reporting_entity',accounting_framework='us_gaap',financing_state='unknown',linkage_evidence='search_incomplete',relationship_conclusion='causality_not_established',elimination_status='external',as_of=asof))
        for x in authored:
            if x.get('counterparty')==alias:db.execute('UPDATE observations SET counterparty_entity_id=? WHERE observation_id=?',[eid,x['observation_id']])
    # The dated EX21 snapshot supplies current legal entities, not acquisition dates.
    from .text import normalize_html
    er=next(r for r in annual['resources'].values() if (r.get('exhibit_type') or '').startswith('EX-21'))
    text=normalize_html((root/er['path']).read_bytes())
    names=['Super Micro Computer B.V.','Super Micro Computer Holdings B.V.','Super Micro Computer International Inc.','Super Micro Computer Limited','Super Micro Management Consulting Inc.','Super Micro Computer, Inc. Taiwan','Super Micro Computer US LLC','Super Micro Computer Malaysia Sdn Bhd','Supermicro KK','Supermicro Technology (Beijing) Co., Ltd.','Super Micro Computer SARL','Super Micro Computer GmbH','Super Micro Computer Arabia Ltd.','Super Micro Computer Singapore Pte. Ltd.','Super Micro Computer Korea Limited','Super Micro Computer Spain, S.L.','Super Micro Computer, S.R.L.','Super Micro Computer Middle East FZ-LLC','Super Micro Computer Mexico, S. de. R.L.de C.V.','Super Micro Computers Systems Pvt. Ltd.','Super Micro Computer Federal LLC','Super Micro Computer Canada Inc.','Super Micro Computer Australia Pty. Ltd.','Advanced Business Computer.AI']
    for name in names:
        assert name in text
        eid='legal:'+digest(name)
        insert(db,'entities',dict(entity_id=eid,membership_id=digest(['SMCI_EX21_20260630',eid]),legal_name=name,normalized_name=name.casefold(),entity_status='confirmed',group_id=GROUP,economic_group_id=GROUP,consolidation_treatment='consolidated_subsidiary',membership_start='2026-06-30',knowledge_date='2026-08-31',resolution_rule='EX21_named_subsidiary_plus_audited_consolidation_policy;current_snapshot',evidence_document_id=digest([er['url']]),evidence_locator='EX21_named_row',source_perspective='reporting_entity',as_of=asof))
    o=by['consolidated_management_company_VIE'];name=o['counterparty'];eid='legal:'+digest(name)
    insert(db,'entities',dict(entity_id=eid,membership_id=digest(['SMCI_VIE_20260630',eid]),legal_name=name,normalized_name=name.casefold(),entity_status='confirmed',group_id=GROUP,economic_group_id=GROUP,consolidation_treatment='vie_consolidated',membership_start='2026-06-30',knowledge_date=o['knowledge_date'],resolution_rule='audited_policy_explicit_consolidated_VIE;not_ownership_percentage_alone',evidence_document_id=o['document_id'],evidence_locator=o['locator'],source_perspective='reporting_entity',as_of=asof))

def assemble(root,target_db=None):
    base=state(root);asof=json.loads((base/'issuer.json').read_text())['source_cutoff'];mini=base/'assembly'
    db=create(root)
    for t in TABLES:db.execute(f"INSERT INTO {t} BY NAME SELECT * FROM read_parquet('{base}/native_tables/{t}.parquet')")
    db.execute("UPDATE documents SET assurance_level='not_applicable',tier='C' WHERE exhibit_type LIKE 'EX-21%' OR exhibit_type LIKE 'EX-23%'")
    from .calculation import prepare_views
    from .quarter_series import prepare as quarter_views
    prepare_views(db,mini,asof);quarter_views(db,mini,asof)
    authored=load_readings(db,root,asof);supplemental(db,root,asof,authored)
    db.execute("CREATE TEMP VIEW usable_observations AS SELECT * FROM observations WHERE NOT abstained")
    # Reuse the original event definitions and expected-cell publication.
    from .events import run as events
    events(db,mini,asof)
    # Annex E stays indeterminate without identified funded clients and the
    # relevant private contracts. Annual cutoffs/grid are the frozen originals.
    from .evaluation import run as evaluation
    cfg=yaml.safe_load((mini/'config.yaml').read_text());persist(mini/'work/pair_registry.json',dict(pairs={GROUP:[g for g in cfg['groups'] if g!=GROUP]+['LAB:OpenAI','LAB:Anthropic']}))
    evaluation(db,mini,asof)
    from .coverage import run as coverage
    coverage(db,mini,asof)
    db.execute("DELETE FROM measures WHERE period_end!='none' AND period_end<'2020-07-01'")
    db.execute("UPDATE measures SET nd_reason='historical_text_search_incomplete_or_named_customer_allocation_not_published' WHERE status='not_determinable' AND nd_reason='public_attribution_or_complete_terms_not_established'")
    for reason,detail,state_code in [('historical_narrative_outside_current_tranche','Historical structured series retained; complete selected natural-note reading covers latest annual; historical audit and debt chronology separately reviewed.','not_processed'),('anonymous_customer_AI_allocation','No attribution of anonymous customer or aggregate balances to AI.','not_disclosed')]:
        insert(db,'exclusions',dict(exclusion_id=digest(['SMCI_gap',reason]),group_id=GROUP,entity_id=PRIMARY,element_type='SMCI_scope',element_id=reason,reason=reason,detail=detail,coverage_state=state_code,as_of=asof))
    from .universe import DEPENDENCIES
    rank1=set(yaml.safe_load((root/'config.yaml').read_text())['tier1'])|DEPENDENCIES
    db.execute('UPDATE measures SET tier=2 WHERE measure::VARCHAR NOT IN ('+','.join(sql_literal(x) for x in sorted(rank1))+')')
    # No existing group is recalculated in this isolated assembly.
    export(db,base/'delta_tables');persist(base/'delta_counts.json',table_counts(db));db.close()
    return overlay(root,target_db)

def overlay(root,target_db=None):
    base=state(root);asof=json.loads((base/'issuer.json').read_text())['source_cutoff'];db=target_db or create(root)
    manifest=json.loads((base/'baseline/manifest.json').read_text())
    for t in TABLES:
        p=root/manifest[t]['path'];assert sha(p)==manifest[t]['sha256']
        if target_db is None:db.execute(f"INSERT INTO {t} BY NAME SELECT * FROM read_parquet('{p}')")
        db.execute(f"INSERT INTO {t} BY NAME SELECT * FROM read_parquet('{base}/delta_tables/{t}.parquet')")
    validation=verify(db,root,asof)
    export(db,root/'tables')
    from .smci_reports import render
    render(db,root,asof,validation)
    if target_db is None:db.close()
    return validation

def verify(db,root,asof):
    from .assembly import rows
    base=state(root);checks={};preservation={}
    def bag(v):return json.dumps(sorted(json.loads(v),key=lambda x:json.dumps(x,sort_keys=True)),separators=(',',':'))
    db.create_function('smci_source_bag',bag,['VARCHAR'],'VARCHAR')
    for t in TABLES:
        columns=[r[1] for r in db.execute(f"PRAGMA table_info('{t}')").fetchall()]
        from .database import comparison_fields
        fields=comparison_fields(db,t,'smci_source_bag')
        missing=db.execute(f"SELECT count(*) FROM (SELECT {fields} FROM read_parquet('{base}/baseline/{t}.parquet') EXCEPT ALL SELECT {fields} FROM {t})").fetchone()[0]
        preservation[t]=missing
    checks['all_previous_25_group_rows_preserved']=all(x==0 for x in preservation.values())
    checks['eight_tables']=len(TABLES)==8
    checks['no_future_SMCI_fact']=db.execute("SELECT count(*) FROM facts WHERE group_id='SMCI' AND (acceptance_datetime>as_of OR knowledge_date>as_of::DATE)").fetchone()[0]==0
    checks['ND_never_zero']=db.execute("SELECT count(*) FROM measures WHERE status='not_determinable' AND (value IS NOT NULL OR nd_reason IS NULL)").fetchone()[0]==0
    checks['no_anonymous_SMCI_amount_edge']=db.execute("SELECT count(*) FROM links WHERE from_group_id='SMCI' AND edge_kind='amount' AND counterparty_evidence='anonymous'").fetchone()[0]==0
    checks['no_undrawn_SMCI_financing_edge']=db.execute("SELECT count(*) FROM links WHERE 'SMCI' IN (from_group_id,to_group_id) AND family='financing' AND edge_kind='amount' AND stage NOT IN ('drawn_or_paid','recognized')").fetchone()[0]==0
    checks['frozen_E_F_criteria']=json.loads((base/'baseline/criteria_manifest.json').read_text())==json.loads((root/'audit/criteria_manifest.json').read_text())
    checks['all_current_notes_have_personal_disposition']=all(any(o['accession']==r['accession'] and o['content_key']==r['content_key'] for o in json.loads((base/'authored_observations.json').read_text())) for r in json.loads((base/'reading_queue.json').read_text()) if r['report_date'] in json.loads((base/'integration_contract.json').read_text())['current_periods'])
    checks['all_SMCI_numeric_lineage_resolves']=db.execute("""SELECT count(*) FROM measures m,json_each(m.lineage) j
       WHERE m.group_id='SMCI' AND m.value IS NOT NULL AND NOT EXISTS (SELECT 1 FROM facts f WHERE f.fact_id=json_extract_string(j.value,'$'))
       AND NOT EXISTS (SELECT 1 FROM observations o WHERE o.observation_id=json_extract_string(j.value,'$'))
       AND NOT EXISTS (SELECT 1 FROM documents d WHERE d.document_id=json_extract_string(j.value,'$'))
       AND NOT EXISTS (SELECT 1 FROM links l WHERE l.link_id=json_extract_string(j.value,'$'))""").fetchone()[0]==0
    checks['SMCI_source_bytes_match']=all(sha(root/r['path'])==r['sha256'] for f in json.loads((base/'filings.json').read_text()).values() for r in f['resources'].values())
    checks['no_future_SMCI_observation']=db.execute("SELECT count(*) FROM observations WHERE group_id='SMCI' AND knowledge_date>as_of::DATE").fetchone()[0]==0
    checks['current_F4_F5_admitted']=db.execute("SELECT count(*) FROM measures WHERE group_id='SMCI' AND measure='fragility_event' AND period_end='2026-06-30' AND breakdown_key IN ('F4','F5') AND status='computed' AND value=1").fetchone()[0]==4
    result=dict(as_of=asof,checks=checks,previous_row_differences=preservation,table_counts=table_counts(db),
        SMCI_delta=json.loads((base/'delta_counts.json').read_text()),SMCI_accounting_mismatches=rows(db,"SELECT * FROM controls WHERE group_id='SMCI' AND status='mismatch'"),
        subagents_used=False,independent_audit_performed=False)
    persist(base/'validation.json',result)
    if not all(checks.values()):raise ValueError('SMCI validation failed: '+str([k for k,v in checks.items() if not v]))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['native','assemble','overlay']);a=p.parse_args()
    result=globals()[a.action](Path('.').resolve())
    if result:print(json.dumps(result,default=str))
