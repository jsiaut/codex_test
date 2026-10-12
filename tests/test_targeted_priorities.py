"""Evidence-level checks for errors that would change economic conclusions."""
from pathlib import Path
from decimal import Decimal
import hashlib,json
import duckdb

ROOT=Path(__file__).resolve().parents[1]
def authored():return {r['model_quantity']:r for r in json.loads((ROOT/'work/priorities/authored_observations.json').read_text())}

def test_fund_scale_and_funded_vs_capacity():
    rows=authored()
    assert Decimal(rows['ares_helios_current_funded_principal']['amount'])==Decimal('90590000')
    assert Decimal(rows['ares_helios_current_unfunded_commitment']['amount'])==Decimal('9410000')
    assert Decimal(rows['ares_helios_current_total_commitment']['amount'])==Decimal('100000000')
    assert Decimal(rows['blackrock_ddtl_v_funded_principal']['amount'])==Decimal('806571')
    assert Decimal(rows['blackrock_ddtl_v_unfunded_commitment']['amount'])==Decimal('1464429')
    c=duckdb.connect()
    assert c.execute("SELECT count(*) FROM read_parquet(?) WHERE variant='targeted_priorities_v1' AND residual=0 AND status='ok'",[str(ROOT/'tables/controls.parquet')]).fetchone()[0]==10
    assert c.execute("SELECT count(*) FROM read_parquet(?) WHERE from_entity_id IN ('cik:0002031750','cik:0001902649') AND edge_kind='amount' AND stage!='recognized'",[str(ROOT/'tables/links.parquet')]).fetchone()[0]==0

def test_vernon_documentary_identity_does_not_guess_revenue_customer():
    rows=authored();r=rows['vernon_investment_identity_resolved']
    assert r['counterparty']=='Lambda, Inc.' and r['counterparty_method']=='explicit_cross_reference'
    assert 'Lambda, Inc.' in rows['vernon_current_cross_reference']['quote']
    assert Decimal(r['amount'])==Decimal('92500000')
    c=duckdb.connect()
    original=c.execute("SELECT counterparty_evidence,counterparty FROM read_parquet(?) WHERE group_id='SMCI' AND model_quantity='revenue_customer_concentration'",[str(ROOT/'tables/observations.parquet')]).fetchall()
    assert original==[('anonymous',None)]
    assert Decimal(rows['vernon_original_estimate']['amount'])==Decimal('600000000')
    lease=c.execute("SELECT amount FROM read_parquet(?) WHERE group_id='SMCI' AND model_quantity='vernon_lease_liability'",[str(ROOT/'tables/observations.parquet')]).fetchone()[0]
    assert lease==Decimal('290200000')

def test_parallel_guarantees_are_distinct_and_not_called():
    rows=authored()
    assert '[***]' in rows['apld_eln02_letter_of_credit']['quote']
    assert rows['apld_eln03_no_section12_lc']['quote']=='12.\n[Reserved].'
    for key in ('apld_eln02_springing_scope','apld_eln03_springing_scope'):
        assert rows[key]['stage']=='signed' and rows[key]['trigger_occurred']=='unknown'
        assert rows[key].get('amount') is None and rows[key].get('event_observable') is None
    assert 'full refinancing' in rows['apld_eln02_refinance_trigger']['quote']
    c=duckdb.connect()
    memberships=c.execute("SELECT membership_start FROM read_parquet(?) WHERE resolution_rule LIKE 'EX21_body_explicit_named_subsidiary%'",[str(ROOT/'tables/entities.parquet')]).fetchall()
    assert len(memberships)==2 and all(str(r[0])=='2026-05-31' for r in memberships)

def test_old_facts_and_frozen_cutoff_survive():
    scope=json.loads((ROOT/'work/priorities/scope.json').read_text())
    assert scope['source_cutoff']=='2026-10-09T10:24:21.129672+00:00'
    baseline=ROOT/'work/dependencies/baseline/facts.parquet'
    if not baseline.exists():baseline=ROOT/'tables/facts.parquet'
    assert hashlib.sha256(baseline.read_bytes()).hexdigest() in {
        scope['baseline_tables']['facts']['sha256'],
        json.loads((ROOT/'work/dependencies/baseline_encoding_proof.json').read_text())['portable_sha256']}
    c=duckdb.connect()
    assert c.execute('SELECT count(*) FROM (SELECT * FROM read_parquet(?) EXCEPT ALL SELECT * FROM read_parquet(?))',
        [str(baseline),str(ROOT/'tables/facts.parquet')]).fetchone()[0]==0
    proof=json.loads((ROOT/'work/priorities/validation.json').read_text())
    assert all(v.get('baseline_rows_missing_or_changed',0)==0 for v in proof['conservation'].values())
    assert (ROOT/'audit/criteria_manifest.json').read_bytes()==(ROOT/'work/smci/baseline/criteria_manifest.json').read_bytes()

def test_valuation_ratio_has_no_currency_and_no_false_draw():
    c=duckdb.connect()
    assert c.execute("SELECT count(*) FROM read_parquet(?) WHERE variant='targeted_priorities_v1' AND measure='bdc_fv_to_cost' AND (unit!='ratio' OR currency IS NOT NULL)",[str(ROOT/'tables/measures.parquet')]).fetchone()[0]==0
    obs=authored()
    assert not any(r['group_id']=='external:0001065521' and r['stage']=='drawn_or_paid' for r in obs.values())
