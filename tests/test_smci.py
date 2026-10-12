from pathlib import Path
from decimal import Decimal
import json
import pytest
from secfragility.smci_evidence import inline_bridge

ROOT=Path(__file__).resolve().parents[1]
def readings():
    return {o['model_quantity']:o for o in json.loads((ROOT/'work/smci/authored_observations.json').read_text())}

def test_inline_instance_bridge_checks_identity_and_scaled_signed_value():
    raw=b'<html><ix:nonfraction id="a" name="us-gaap:Cash" scale="3" sign="-">1,234</ix:nonfraction></html>'
    fact=dict(locator='id:a',canonical_concept='us-gaap:Cash',value='-1234000')
    assert inline_bridge(raw,fact)['value']=='-1234000'
    with pytest.raises(ValueError):inline_bridge(raw,dict(fact,value='1234000'))
    with pytest.raises(ValueError):inline_bridge(raw,dict(fact,canonical_concept='us-gaap:Debt'))
    with pytest.raises(ValueError):inline_bridge(raw,dict(fact,locator='id:absent'))

def test_isolated_native_queries_have_no_older_snapshot_dependency():
    from secfragility.smci_integration import isolated_queries
    full=(ROOT/'queries.sql').read_text();core=isolated_queries(full)
    assert 'CREATE TEMP TABLE eligible_instance_occurrences' in core
    assert 'read_parquet(' not in core and 'legacy_EDGAR_documents' not in core
    with pytest.raises(ValueError):isolated_queries("SELECT * FROM read_parquet('other_group.parquet')")

def test_uncommitted_factoring_and_unused_ATM_are_not_funded_financing():
    b=readings()
    assert b['receivable_purchase_uncommitted']['stage']=='available'
    assert b['receivable_sales']['amount']=='831674000'
    assert b['ATM_program_limit']['stage']=='signed'
    assert b['ATM_not_drawn_at_closing'].get('amount') is None
    assert b['Compuware_trade_credit_limit']['family']=='commercial'
    assert Decimal(b['Compuware_receivable']['amount'])<Decimal(b['Compuware_trade_credit_limit']['amount'])

def test_anonymous_concentrations_and_sublicensee_do_not_gain_a_guessed_name():
    b=readings()
    for name in ['revenue_customer_concentration','supplier_concentration_anonymous','sublicensee_equity_investment']:
        assert b[name]['counterparty_evidence']=='anonymous'
        assert not b[name].get('counterparty')
    assert 'did not relieve' in b['lease_original_obligation']['quote']

def test_ICFR_adverse_and_financial_statements_unqualified_are_distinct():
    b=readings()
    assert b['annual_auditor_ICFR_adverse']['event_observable']=='F5'
    assert b['annual_auditor_ICFR_adverse']['event_present'] is True
    assert not b['auditor_financial_statements_unqualified'].get('event_observable')
    assert b['special_committee_position']['tier']=='C'
    assert b['taiwan_audit_qualification_trigger']['tier']=='D'
    assert b['taiwan_audit_qualification_trigger']['trigger_occurred']=='unknown'

def test_F4_financial_ratio_waiver_not_reporting_waiver_or_calendar_correction():
    b=readings()
    assert b['financial_covenant_waiver']['event_observable']=='F4'
    assert b['financial_covenant_waiver']['event_date']=='2026-06-26'
    assert 'October 31, 2026' in b['financial_covenant_waiver']['quote']
    assert not b['convertible_reporting_waiver_exception'].get('event_observable')
    assert not b['us_revolver_year_end_correction'].get('event_observable')

def test_negative_FCF_and_carrying_debt_do_not_add_working_capital_or_equity_twice():
    b=readings()
    assert Decimal(b['cfo_annual']['amount'])-Decimal(b['capex_paid_annual']['amount'])==Decimal('-6971885000')
    assert Decimal(b['bank_debt_total']['amount'])+Decimal(b['convertible_debt_total_book']['amount'])==Decimal('8720287000')
    assert b['preferred_issue_cash']['stage']=='drawn_or_paid'
    assert 'equity classification' in b['preferred_dividend_rate']['issuer_treatment']

def test_reading_scope_and_knowledge_dates_are_explicit():
    ledger=json.loads((ROOT/'work/smci/reading_ledger.json').read_text())
    current=[r for r in ledger if r.get('status')=='completed']
    assert len(current)==11 and all(r['report_date']=='2026-06-30' for r in current)
    assert any(r.get('status')=='historical_inventory_outside_current_text_tranche' for r in ledger)
    obs=json.loads((ROOT/'work/smci/authored_observations.json').read_text())
    fy24=next(o for o in obs if o['model_quantity']=='annual_management_ICFR_ineffective' and o['period_end']=='2024-06-30')
    assert fy24['knowledge_date']=='2025-02-25'
    assert all(o['knowledge_date']<='2026-10-09' for o in obs)

def test_personally_authored_evidence_satisfies_the_frozen_table_schema(tmp_path):
    from secfragility.database import create,bulk_insert
    (tmp_path/'schema.sql').write_text((ROOT/'schema.sql').read_text())
    (tmp_path/'work').mkdir()
    db=create(tmp_path)
    evidence=json.loads((ROOT/'work/smci/authored_observations.json').read_text())
    bulk_insert(db,'observations',evidence,tmp_path,'smci_test_evidence')
    assert db.execute('SELECT count(*) FROM observations').fetchone()[0]==len(evidence)
    db.close()
