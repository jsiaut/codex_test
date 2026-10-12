"""Financial interpretation and hostile-input guards for the transaction layer."""
from pathlib import Path
from decimal import Decimal
from copy import deepcopy
import json
import duckdb,pytest
from secfragility.operation_dependencies import customer_share,validate_ledger,author_record
from secfragility.operation_sources import restore,save

ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'work/dependencies'
def rows(name):return json.loads((BASE/(name+'.json')).read_text())
def notes():return {r['model_quantity']:r for r in rows('authored_observations')}

def test_sb_receipt_is_one_paid_flow_and_future_subscription_is_signed():
    n=notes();receipt=n['sb_energy_cash_forward_received_and_contributed']
    assert Decimal(receipt['amount'])==Decimal('1500000000') and receipt['stage']=='drawn_or_paid'
    future=n['sb_energy_additional_nvidia_subscription_conditional']
    assert future['stage']=='signed'
    case=next(c for c in rows('operations') if c['operation_id']=='SB_PORTS')
    paths=case['cash_or_resource_paths']
    assert len(paths)==2 and {p['amount_reference'] for p in paths}=={receipt['observation_id']}
    assert len({p['economic_flow_id'] for p in paths})==1
    # Two legal hops of the same receipt, not two independent investments.

def test_ionic_coverage_is_rent_years_one_to_five_not_gpu_debt():
    n=notes();r=n['ionic_nvidia_first_five_year_guarantee_cap']
    assert Decimal(r['amount'])==Decimal('860300000')
    case=next(x for x in rows('operations') if x['operation_id']=='IONIC_WARD')
    window=next(x for x in case['contract_features'] if x['kind']=='Nvidia_coverage_window')
    assert (window['first_lease_year'],window['last_lease_year'])==(1,5)
    ward=next(x for x in rows('operations') if x['operation_id']=='NSCALE')
    assert 'emprunteur' in ' '.join(r['role'] for r in ward['roles'])

def test_project_bonds_have_no_parent_or_tenant_guarantee():
    for case in rows('operations'):
        if case['operation_id'] in ('HUT_RIVER','HUT_BEACON'):
            assert next(c for c in case['contract_features'] if c['kind']=='parent_or_tenant_bond_guarantee')['present'] is False
    beacon=next(c for c in rows('operations') if c['operation_id']=='HUT_BEACON')
    assert not any('Google' in r['name'] for r in beacon['roles'])

def test_capacity_purchase_replaces_monetary_backstop_without_deleting_history():
    c=duckdb.connect();c.execute("CREATE VIEW links AS SELECT * FROM read_parquet(?)".replace('?',"'"+str(ROOT/'tables/links.parquet')+"'"))
    c.execute((ROOT/'operation_views.sql').read_text().split('CREATE OR REPLACE VIEW operation_quantities')[0])
    old='d311556f39a2859f9a7dc7be8aeb7db762b87df817e04b250f6c4c2c77cd5d67'
    assert c.execute('SELECT count(*) FROM links WHERE link_id=?',[old]).fetchone()[0]==1
    assert c.execute('SELECT count(*) FROM effective_links WHERE link_id=?',[old]).fetchone()[0]==0
    edge=c.execute("SELECT family,type,amount FROM effective_links WHERE instrument_key='NVIDIA_CRWV' AND type='purchase_commitment'").fetchone()
    assert edge==('commercial','purchase_commitment',None)

def test_external_loan_and_agency_numbers_are_not_core_amounts():
    assert all(r.get('amount') is None for r in rows('authored_observations') if r['tier']=='E')
    ids={r['observation_id'] for r in rows('authored_observations') if r['tier']=='E'}
    assert not any(e['observation_id'] in ids for e in rows('edge_decisions'))
    case=next(c for c in rows('operations') if c['operation_id']=='LAMBDA_COMPUTE_I')
    assert all(not q['admitted_to_core'] for q in case['reported_unadmitted_quantities'])

def test_named_customer_ratio_is_descriptive_and_period_matched():
    c=duckdb.connect();r=c.execute("SELECT value,numerator,denominator,currency,relationship_conclusion FROM read_parquet(?) WHERE variant='operation_dependencies_v1' AND measure='operation_derived_quantity' AND view='as_known'",[str(ROOT/'tables/measures.parquet')]).fetchone()
    assert r==(Decimal('0.199188'),Decimal('74400000'),Decimal('373516000'),None,'causality_not_established')

@pytest.mark.parametrize('field,value',[('period_end','2025-12-31'),('currency','EUR'),('entity_id','other'),('accounting_framework','ifrs')])
def test_ratio_rejects_scope_period_and_currency_mismatch(field,value):
    a=dict(group_id='G',entity_id='E',period_start='2026-01-01',period_end='2026-06-30',accounting_framework='us_gaap',currency='USD',tier='B',stage='recognized',amount='74')
    b=dict(a,amount='373');b[field]=value
    with pytest.raises(ValueError,match='incompatible'):customer_share(a,b)

def test_existing_wrong_original_is_never_overwritten(tmp_path):
    import shutil
    base=tmp_path/'work/dependencies';base.mkdir(parents=True)
    for n in ('originals.tar.zst','source_backup.json'):shutil.copy2(BASE/n,base/n)
    meta=rows('source_backup');name=next(iter(meta['sources']))
    target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'wrong original')
    with pytest.raises(ValueError,match='never substituted'):restore(tmp_path)
    assert target.read_bytes()==b'wrong original'

def test_native_fact_wrong_namespace_is_rejected(monkeypatch):
    import secfragility.operation_dependencies as module
    row=notes()['cerebras_H1_total_revenue_denominator'];fact=deepcopy(next(f for f in rows('selected_native_facts') if f['fact_id']==row['tagged_fact_id']))
    fact['taxonomy_namespace']='https://wrong.example/taxonomy'
    monkeypatch.setattr(module,'native_catalog',lambda root:[fact])
    source=next(s for s in rows('source_manifest') if s['document_id']==row['document_id'])
    with pytest.raises(ValueError,match='namespace'):author_record(ROOT,source['key'],row['model_quantity'],row['quote'],row['issuer_treatment'],inline=fact['locator'][3:])

def test_baseline_rows_are_preserved_in_all_eight_tables():
    c=duckdb.connect()
    for t in ('documents','facts','observations','entities','links','measures','controls','exclusions'):
        assert c.execute('SELECT count(*) FROM (SELECT * FROM read_parquet(?) EXCEPT ALL SELECT * FROM read_parquet(?))',[str(BASE/'baseline'/(t+'.parquet')),str(ROOT/'tables'/(t+'.parquet'))]).fetchone()[0]==0
    assert rows('negative_search_certificates')==[]
    assert all(len(c['questions'])==8 for c in rows('operations'))

def test_source_after_frozen_cutoff_is_rejected(monkeypatch):
    import secfragility.operation_dependencies as module
    source=deepcopy(rows('source_manifest')[0]);source['acceptance_datetime']='2026-10-10T00:00:00Z'
    monkeypatch.setattr(module,'catalog',lambda root:{source['key']:source})
    with pytest.raises(ValueError,match='frozen cutoff'):module.validate_inputs(ROOT)

@pytest.mark.parametrize('mutation',['identity_date','signed_only','external_numeric'])
def test_monetary_edge_guards_reject_misleading_financial_claims(mutation):
    c=duckdb.connect()
    c.execute("CREATE TABLE entities AS SELECT entity_id,entity_status,knowledge_date FROM read_parquet(?)",[str(BASE/'baseline/entities.parquet')])
    for e in rows('entity_decisions'):c.execute('INSERT INTO entities VALUES (?,?,?)',[e['entity_id'],e['entity_status'],e['knowledge_date']])
    c.execute("CREATE TABLE observations AS SELECT observation_id,tier,amount,stage,knowledge_date FROM read_parquet(?)",[str(BASE/'baseline/observations.parquet')])
    for r in rows('authored_observations'):c.execute('INSERT INTO observations VALUES (?,?,?,?,?)',[r['observation_id'],r['tier'],r.get('amount'),r['stage'],r['knowledge_date']])
    target=next(e for e in rows('edge_decisions') if e['edge_kind']=='amount' and e['family']=='financing')
    if mutation=='identity_date':
        c.execute("UPDATE entities SET knowledge_date='2099-01-01' WHERE entity_id=?",[target['from_entity_id']])
    else:c.execute('UPDATE observations SET '+('stage' if mutation=='signed_only' else 'tier')+'=? WHERE observation_id=?',
        ['signed' if mutation=='signed_only' else 'E',target['observation_id']])
    with pytest.raises(ValueError):validate_ledger(ROOT,c)
