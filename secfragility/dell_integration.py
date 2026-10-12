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
    cfg['concept_anchors_overrides']={'debt_carrying_current':['DebtCurrent'],
        'interest_expense':['InterestExpenseDebt'],
        'cash_and_restricted_cash_total':['CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations']}
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
            if typ.startswith(('EX-21','EX-23')):
                assure='not_applicable';tier='C'
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
    from .dell_sources import restore
    if not all((root/r['path']).exists() for f in json.loads((state(root)/'filings.json').read_text()).values() for r in f['resources'].values()):restore(root)
    base=state(root);mini,collection,facts=prepare(root);asof=json.loads((base/'issuer.json').read_text())['source_cutoff']
    db=create(root);documents(db,root,collection,asof)
    bulk_insert(db,'facts',facts,root,'dell_native_facts')
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
    print(json.dumps(dict(stage='Dell_native_tables',counts=table_counts(db))),flush=True)
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
    bulk_insert(db,'observations',authored,root,'dell_authored_observations')
    return authored

def entities(db,root,asof):
    from .assembly import rows
    reg=json.loads((state(root)/'filings.json').read_text());annual=reg['0001571996-26-000008']
    r=next(r for r in annual['resources'].values() if r.get('exhibit_type')=='EX-21.1')
    from .text import normalize_html
    text=normalize_html((root/r['path']).read_bytes())
    selected=['Dell Technologies Inc.','Dell Inc.','Denali Intermediate Inc.','Dell International L.L.C.','EMC Corporation',
        'Dell Financial Services L.L.C.','Dell Bank International Designated Activity Company',
        'Dell Financial Services International Ireland Designated Activity Company','Dell Asset Revolving Trust-B',
        'Dell Conduit Funding-B L.L.C.','Dell Depositor L.L.C.','Dell Asset Syndication L.L.C.',
        'Dell Equipment Finance Trust 2023-1','Dell Equipment Finance Trust 2023-2','Dell Equipment Finance Trust 2023-3',
        'Dell Equipment Finance Trust 2024-1','Dell Equipment Finance Trust 2024-2','Dell Equipment Finance Trust 2025-1',
        'Dell Equipment Finance Trust 2025-2','Dell Financial Services Canada Limited','Dell Financial Services Pte. Ltd.',
        'Dell Financial Services Pty Ltd','Dell Technologies Capital, LLC']
    ids={}
    for name in selected:
        assert name in text
        eid=PRIMARY if name=='Dell Technologies Inc.' else 'legal:'+digest(name)
        ids[name]=eid
        insert(db,'entities',dict(entity_id=eid,membership_id=digest(['Dell_snapshot_20260130',eid]),legal_name=name,
            normalized_name=name.casefold(),cik=CIK if eid==PRIMARY else None,entity_status='confirmed',group_id=GROUP,
            economic_group_id=GROUP,consolidation_treatment='parent' if eid==PRIMARY else 'consolidated_subsidiary',
            membership_start='2026-01-30',knowledge_date=annual['metadata']['filingDate'],
            resolution_rule='EX21_named_subsidiary_plus_audited_consolidation_policy;current_snapshot_not_first_acquisition_date',
            evidence_document_id=digest([r['url']]),evidence_locator='EX21_exact_named_row',source_perspective='reporting_entity',as_of=asof))
    # Dated Broadcom ownership is evidenced by Dell's audited related-party
    # note; a brand does not merge historical VMware balances into Dell now.
    vm='legal:'+digest('VMware LLC')
    insert(db,'entities',dict(entity_id=vm,membership_id=digest(['Dell_VMware_Broadcom_20231122']),legal_name='VMware LLC',
        normalized_name='vmware llc',entity_status='confirmed',group_id='AVGO',economic_group_id='AVGO',
        consolidation_treatment='consolidated_subsidiary',membership_start='2023-11-22',
        knowledge_date=annual['metadata']['filingDate'],resolution_rule='audited_note_explicit_Broadcom_acquisition;no_Dell_control_inference',
        evidence_document_id=digest([annual['resources'][annual['metadata']['primaryDocument']]['url']]),
        evidence_locator='Note19_related_party_control_cutoff',as_of=asof))
    ids['VMware']=vm
    return ids

def supplemental(db,root,asof,authored,ids):
    from .assembly import rows
    # Generic descriptive stock/flow ledger. The issuer-specific labels and
    # dimensions remain in every row; no client identification is invented.
    dictionary={
        'us-gaap:NotesReceivableNet':'dfs_financing_receivables_net',
        'us-gaap:NotesReceivableGross':'dfs_customer_receivables_gross_and_credit_buckets',
        'us-gaap:NotesAndLoansReceivableNetCurrent':'dfs_financing_receivables_current',
        'us-gaap:NotesAndLoansReceivableNetNoncurrent':'dfs_financing_receivables_noncurrent',
        'us-gaap:FinancingReceivableAllowanceForCreditLosses':'dfs_credit_loss_allowance',
        'us-gaap:ProvisionForLoanLossesExpensed':'dfs_credit_loss_provision',
        'us-gaap:PaymentsToAcquireFinanceReceivables':'dfs_financing_originations_reported',
        'us-gaap:SalesTypeLeaseRevenue':'dfs_sales_type_lease_product_revenue',
        'us-gaap:PropertySubjectToOrAvailableForOperatingLeaseNet':'dfs_lessor_equipment_net',
        'us-gaap:PropertySubjectToOrAvailableForOperatingLeaseGross':'dfs_lessor_equipment_gross',
        'us-gaap:SalesTypeAndDirectFinancingLeasesLeaseReceivablePaymentsToBeReceived':'dfs_sales_type_lease_undiscounted_receipts',
        'us-gaap:LessorOperatingLeasePaymentsToBeReceived':'dfs_operating_lease_undiscounted_receipts',
        'us-gaap:SupplierFinanceProgramObligation':'supplier_finance_already_in_AP',
        'us-gaap:GuaranteeObligationsMaximumExposure':'contract_manufacturer_guarantee_maximum',
        'us-gaap:DebtCurrent':'debt_current_carrying',
        'us-gaap:LongTermDebt':'debt_total_carrying',
        'us-gaap:UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount':'purchase_obligations_total',
        'us-gaap:ContractualObligationFutureMinimumPaymentsDueRemainderOfFiscalYear':'purchase_obligations_FY_remainder',
        'us-gaap:PurchaseObligationDueInNextTwelveMonths':'purchase_obligations_next_fiscal_bucket',
        'us-gaap:PurchaseObligationDueInSecondYear':'purchase_obligations_second_fiscal_bucket',
        'us-gaap:PurchaseObligationDueInThirdYear':'purchase_obligations_third_fiscal_bucket'}
    selected=rows(db,"""SELECT * FROM eligible_instance_occurrences WHERE group_id='DELL' AND tier IN ('A','B','C') AND filing_status='filed'
        AND document_rank>=0 AND value IS NOT NULL AND NOT is_nil AND coverage_state IN ('observed','explicit_zero') AND period_end>='2020-02-01'
        QUALIFY row_number() OVER (PARTITION BY semantic_key ORDER BY acceptance_datetime DESC,accession DESC,
          document_rank DESC,try_cast(decimals AS INTEGER) DESC,occurrence_rank DESC,fact_id)=1""")
    for f in selected:
        dims=json.loads(f['dimensions']);quantity=dictionary.get(f['canonical_concept'])
        if f['canonical_concept']=='us-gaap:Revenues' and any('AIOptimizedServersAndNetworkingMember' in str(v) for v in dims.values()):quantity='ai_optimized_server_revenue'
        if f['canonical_concept']=='us-gaap:DebtInstrumentCarryingAmount' and any('DFS' in str(v) or 'FinanceLeasesandRevolvingLoan' in str(v) for v in dims.values()):quantity='dfs_debt_instrument_reported;consult_issuer_principal_label'
        if not quantity:continue
        if f['canonical_concept']=='us-gaap:NotesReceivableNet' and f['dimensions']!='{}':quantity='dfs_customer_or_residual_component'
        for view in ('revised',):
            measure(db,asof,'dell_reported_quantity',str(f['period_end']),f['value'],[f['fact_id']],
                str(f['period_start']) if f['period_start'] else None,view,
                breakdown_key=quantity+'|'+f['canonical_concept']+'|'+digest(dims)[:20],unit=f['unit'],currency=f['currency'],
                knowledge_date=f['knowledge_date'],evidence_profile=f['tier']+';filed;'+f['assurance_level']+';'+f['dimensions'])
    obs_by={o.get('model_quantity'):o for o in authored if not o['abstained']}
    for o in authored:
        if o.get('amount') is None:continue
        measure(db,asof,'dell_reported_quantity',str(o['period_end']),Decimal(o['amount']),[o['observation_id']],o.get('period_start'),
            breakdown_key='authored|'+o['model_quantity'],unit=o['unit'],currency=o['currency'],knowledge_date=o['knowledge_date'],evidence_profile=o['tier']+';'+o['location'])
        if o.get('block'):
            measure(db,asof,'exposure_matrix',str(o['period_end']),Decimal(o['amount']),[o['observation_id']],o.get('period_start'),
                breakdown_key=o['block']+'|'+o['category_id']+'|'+o['measurement_basis'],unit=o['unit'],currency=o['currency'],
                knowledge_date=o['knowledge_date'],overlap_possible=True,tier=1)
    def ratio(name,quantity,denominator='dfs_customer_receivables_gross'):
        n=obs_by[quantity];d=obs_by[denominator]
        measure(db,asof,name,n['period_end'],(Decimal(n['amount'])/Decimal(d['amount'])).quantize(Decimal('.000001')),
            [n['observation_id'],d['observation_id']],breakdown_key=quantity,unit='ratio',currency=None,
            numerator=n['amount'],denominator=d['amount'],knowledge_date=n['knowledge_date'])
    ratio('dfs_credit_quality_share','dfs_lower_credit_quality');ratio('dfs_allowance_share','dfs_credit_loss_allowance')
    ratio('dfs_past_due_share','dfs_past_due_over_90')
    relation=obs_by['vmware_embedded_commercial_relation']
    relation['counterparty_entity_id']=ids['VMware']
    db.execute('UPDATE observations SET counterparty_entity_id=? WHERE observation_id=?',[ids['VMware'],relation['observation_id']])
    insert(db,'links',dict(link_id=digest(['Dell_VMware_integrator_relation',relation['observation_id']]),edge_kind='relation',family='commercial',type='purchase',
        from_entity_id=PRIMARY,to_entity_id=ids['VMware'],from_group_id=GROUP,to_group_id='AVGO',period_end='2026-07-31',
        knowledge_date=relation['knowledge_date'],stage='recognized',observation_id=relation['observation_id'],document_id=relation['document_id'],
        locator=relation['locator'],filing_status='filed',assurance_level='reviewed',tier='B',counterparty_evidence='named',
        source_perspective='reporting_entity',accounting_framework='us_gaap',sales_channel='integrator',financing_state='unknown',
        linkage_evidence='search_incomplete',relationship_conclusion='causality_not_established',elimination_status='external',as_of=asof))
    # Cash and carrying debt get separately dated measures; leases are not
    # added twice and management's core/DFS allocation never changes principal.
    for pe in sorted({str(f['period_end']) for f in selected if f['period_start'] is None}):
        for concept,name in [('us-gaap:CashAndCashEquivalentsAtCarryingValue','cash_consolidated'),('us-gaap:LongTermDebt','debt_interest_bearing')]:
            f=next((f for f in selected if f['canonical_concept']==concept and f['dimensions']=='{}' and str(f['period_end'])==pe and f['period_start'] is None),None)
            if f:measure(db,asof,name,pe,f['value'],[f['fact_id']],knowledge_date=f['knowledge_date'],evidence_profile=f['tier']+';USD_US_GAAP_consolidated')
    ai=next(f for f in selected if f['canonical_concept']=='us-gaap:Revenues' and f['period_start'] and str(f['period_start'])=='2026-05-02' and str(f['period_end'])=='2026-07-31' and 'AIOptimizedServersAndNetworkingMember' in f['dimensions'])
    revenue=next(f for f in selected if f['canonical_concept']=='us-gaap:Revenues' and str(f['period_start'])=='2026-05-02' and str(f['period_end'])=='2026-07-31' and f['dimensions']=='{}')
    measure(db,asof,'ai_optimized_server_revenue_share','2026-07-31',(ai['value']/revenue['value']).quantize(Decimal('.000001')),
        [ai['fact_id'],revenue['fact_id']],'2026-05-02',unit='ratio',currency=None,numerator=ai['value'],denominator=revenue['value'],knowledge_date=ai['knowledge_date'])

def coherent_controls(db,root,asof):
    """Same-deposit corroboration; original mixed-comparative flags retained."""
    # The original selector can combine old maturity/rate disclosures with
    # newer revised comparative balances. Keep those flags visible, while
    # independently testing complete equations within each deposit.
    for control,terms in [('c9_lease_liability',['operating_lease_payments_undiscounted','operating_lease_imputed_interest','operating_lease_liability_current','operating_lease_liability_noncurrent']),
        ('c15_tax_rate',['effective_tax_rate','pretax_income_continuing','income_tax_expense'])]:
        source=[]
        for f in __import__('secfragility.assembly',fromlist=['rows']).rows(db,'SELECT * FROM eligible_instance_occurrences WHERE dimensions=\'{}\' AND value IS NOT NULL AND model_quantity IN ('+','.join(sql_literal(x) for x in terms)+')'):
            source.append(f)
        from collections import defaultdict
        groups=defaultdict(dict)
        for f in source:groups[(f['accession'],str(f['period_start']) if f['period_start'] else 'none',str(f['period_end']),f['reporting_scope'])][f['model_quantity']]=f
        for key,g in sorted(groups.items()):
            if set(g)!=set(terms):continue
            ordered=[g[t] for t in terms]
            radii=[db.execute('SELECT precision_radius(?)',[f['decimals']]).fetchone()[0] for f in ordered]
            if any(x is None for x in radii):continue
            v=[f['value'] for f in ordered]
            if control=='c9_lease_liability':lhs=v[0]-v[1];rhs=v[2]+v[3];tol=sum(radii)
            else:
                lhs=v[0]*v[1];rhs=v[2];tol=abs(v[0])*radii[1]+abs(v[1])*radii[0]+radii[0]*radii[1]+radii[2]
            insert(db,'controls',dict(control=control,group_id=GROUP,period_start=key[1] if key[1]!='none' else key[2],period_end=key[2],
                view='as_known',as_of=asof,breakdown_key='same_deposit|'+key[0],variant='Dell_same_deposit',
                status='ok' if abs(lhs-rhs)<=tol else 'mismatch',lhs=lhs,rhs=rhs,residual=lhs-rhs,tolerance=tol,tolerance_basis='instance',
                explanation_code=None if abs(lhs-rhs)<=tol else 'same_deposit_equation_residual',evidence=json.dumps([f['fact_id'] for f in ordered])))
    from .assembly import rows
    review=[]
    for c in rows(db,"SELECT * FROM controls WHERE group_id='DELL' AND status='mismatch' AND variant='original'"):
        ids=json.loads(c['evidence']);facts=rows(db,'SELECT * FROM facts WHERE fact_id IN ('+','.join('?' for _ in ids)+')',ids)
        if len({f['accession'] for f in facts})>1:
            review.append(dict(control=c['control'],period_start=c['period_start'],period_end=c['period_end'],original_residual=str(c['residual']),
                explanation='Comparison mixes different deposited comparative bases; not a within-statement accounting residual.',
                original_flag_retained=True,source_accessions=sorted({f['accession'] for f in facts}),
                deposited_values=[dict(accession=f['accession'],concept=f['canonical_concept'],value=str(f['value']),decimals=f['decimals']) for f in facts],
                cause='VMware_discontinued_perimeter_for_2021_leases;tax_comparative_revision_cause_not_asserted',
                check_variant='Dell_same_deposit'))
    persist(state(root)/'control_explanations.json',review)

def assemble(root,target_db=None):
    base=state(root);asof=json.loads((base/'issuer.json').read_text())['source_cutoff'];mini=base/'assembly'
    db=create(root)
    for t in TABLES:db.execute(f"INSERT INTO {t} BY NAME SELECT * FROM read_parquet('{base}/native_tables/{t}.parquet')")
    db.execute("UPDATE documents SET assurance_level='not_applicable',tier='C' WHERE exhibit_type LIKE 'EX-21%' OR exhibit_type LIKE 'EX-23%'")
    from .calculation import prepare_views
    from .quarter_series import prepare as quarter_views
    prepare_views(db,mini,asof);quarter_views(db,mini,asof)
    coherent_controls(db,root,asof)
    authored=load_readings(db,root,asof);ids=entities(db,root,asof);supplemental(db,root,asof,authored,ids)
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
    db.execute("DELETE FROM measures WHERE period_end!='none' AND period_end<'2020-02-01'")
    db.execute("UPDATE measures SET nd_reason='historical_text_search_incomplete_or_named_customer_allocation_not_published' WHERE status='not_determinable' AND nd_reason='public_attribution_or_complete_terms_not_established'")
    for reason,detail,coverage_state in [
        ('historical_note_reading_outside_current_tranche','All historical structured statements collected; complete natural-note reading covers latest annual and two later quarters, not all archived historical notes.','not_processed'),
        ('customer_financing_AI_allocation_not_disclosed','DFS aggregate portfolio and AI credit-risk narrative do not identify financed clients or quantify the AI portion.','not_disclosed'),
        ('anonymous_major_customer','FY2026 customer represents 12% of revenue; identity is not supplied in the audited note.','not_disclosed'),
        ('private_customer_and_DFS_securitization_contracts_not_established','Funding-stop mechanism known; precise trigger thresholds, collateral/customer allocations and private contracts not all available in collected scope.','not_collected'),
        ('september_balance_not_reported','September issued notes are a dated completed transaction; do not retrospectively add net issuance to July carrying debt or infer October cash.','not_disclosed'),
        ('MSD_personal_affiliates_not_Dell_consolidated','Michael Dell personal investment firms and unnamed portfolio-company sales do not prove financing by Dell or a relationship with MSD Investment Corp.','policy_excluded')]:
        insert(db,'exclusions',dict(exclusion_id=digest(['Dell_gap',reason]),group_id=GROUP,entity_id=PRIMARY,element_type='Dell_scope',element_id=reason,
            reason=reason,detail=detail,coverage_state=coverage_state,as_of=asof))
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
    from .dell_reports import render
    render(db,root,asof,validation)
    if target_db is None:db.close()
    return validation

def verify(db,root,asof):
    from .assembly import rows
    base=state(root);checks={};preservation={}
    def bag(v):return json.dumps(sorted(json.loads(v),key=lambda x:json.dumps(x,sort_keys=True)),separators=(',',':'))
    db.create_function('dell_source_bag',bag,['VARCHAR'],'VARCHAR')
    for t in TABLES:
        columns=[r[1] for r in db.execute(f"PRAGMA table_info('{t}')").fetchall()]
        from .database import comparison_fields
        fields=comparison_fields(db,t,'dell_source_bag')
        missing=db.execute(f"SELECT count(*) FROM (SELECT {fields} FROM read_parquet('{base}/baseline/{t}.parquet') EXCEPT ALL SELECT {fields} FROM {t})").fetchone()[0]
        preservation[t]=missing
    checks['all_previous_24_group_rows_preserved']=all(x==0 for x in preservation.values())
    checks['eight_tables']=len(TABLES)==8
    checks['no_future_Dell_fact']=db.execute("SELECT count(*) FROM facts WHERE group_id='DELL' AND (acceptance_datetime>as_of OR knowledge_date>as_of::DATE)").fetchone()[0]==0
    checks['ND_never_zero']=db.execute("SELECT count(*) FROM measures WHERE status='not_determinable' AND (value IS NOT NULL OR nd_reason IS NULL)").fetchone()[0]==0
    checks['no_anonymous_Dell_amount_edge']=db.execute("SELECT count(*) FROM links WHERE from_group_id='DELL' AND edge_kind='amount' AND counterparty_evidence='anonymous'").fetchone()[0]==0
    checks['no_undrawn_Dell_financing_edge']=db.execute("SELECT count(*) FROM links WHERE 'DELL' IN (from_group_id,to_group_id) AND family='financing' AND edge_kind='amount' AND stage NOT IN ('drawn_or_paid','recognized')").fetchone()[0]==0
    checks['frozen_E_F_criteria']=json.loads((base/'baseline/criteria_manifest.json').read_text())==json.loads((root/'audit/criteria_manifest.json').read_text())
    checks['all_current_notes_have_personal_disposition']=all(any(o['accession']==r['accession'] and o['content_key']==r['content_key'] for o in json.loads((base/'authored_observations.json').read_text())) for r in json.loads((base/'reading_queue.json').read_text()) if r['report_date'] in ('2026-01-30','2026-05-01','2026-07-31'))
    checks['all_Dell_numeric_lineage_resolves']=db.execute("""SELECT count(*) FROM measures m,json_each(m.lineage) j
       WHERE m.group_id='DELL' AND m.value IS NOT NULL AND NOT EXISTS (SELECT 1 FROM facts f WHERE f.fact_id=json_extract_string(j.value,'$'))
       AND NOT EXISTS (SELECT 1 FROM observations o WHERE o.observation_id=json_extract_string(j.value,'$'))
       AND NOT EXISTS (SELECT 1 FROM documents d WHERE d.document_id=json_extract_string(j.value,'$'))
       AND NOT EXISTS (SELECT 1 FROM links l WHERE l.link_id=json_extract_string(j.value,'$'))""").fetchone()[0]==0
    checks['Dell_source_bytes_match']=all(sha(root/r['path'])==r['sha256'] for f in json.loads((base/'filings.json').read_text()).values() for r in f['resources'].values())
    result=dict(as_of=asof,checks=checks,previous_row_differences=preservation,table_counts=table_counts(db),
        Dell_delta=json.loads((base/'delta_counts.json').read_text()),Dell_accounting_mismatches=rows(db,"SELECT * FROM controls WHERE group_id='DELL' AND status='mismatch'"),
        subagents_used=False,independent_audit_performed=False)
    persist(base/'validation.json',result)
    if not all(checks.values()):raise ValueError('Dell validation failed: '+str([k for k,v in checks.items() if not v]))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['native','assemble','overlay']);a=p.parse_args()
    result=globals()[a.action](Path('.').resolve())
    if result:print(json.dumps(result,default=str))
