from pathlib import Path
from decimal import Decimal
import copy,json
import pytest
from secfragility.softbank_sources import qualify,extract,extract_japanese,row_values,GROUP,VARIANT
from secfragility.softbank_integration import approved_source,stamp

ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(scope='module')
def sources():return json.loads((ROOT/'work/softbank/source_qualifications.json').read_text())

def test_native_dash_is_not_zero_and_scale_is_millions():
    assert row_values('cash (1,000) -')==[Decimal('-1000000000'),None]
    assert row_values('cash 0 12')==[Decimal(0),Decimal('12000000')]

def test_original_Japanese_and_English_current_balance(sources):
    jp=next(s for s in sources if s.get('regulatory_identifier')=='S100YGH5')
    en=next(s for s in sources if s['source_profile']=='issuer_audited_IFRS_financial_statements')
    a=extract_japanese(ROOT,jp);b=extract(ROOT,en)
    key=lambda f:(f['concept'],f['period_start'],f['period_end'])
    original={key(f):f['value'] for f in a}
    compared=[f for f in b if key(f) in original]
    assert len(compared)>=75
    assert all(f['value']==original[key(f)] for f in compared)
    assert original[('equity',None,'2026-03-31')]=='20468432000000'
    assert original[('parent_equity',None,'2026-03-31')]=='17621823000000'

def test_latest_CF_and_multiline_capex(sources):
    q=next(s for s in sources if 'q1fy2026_01_en.pdf' in s['url'])
    facts={f['concept']:f for f in extract(ROOT,q) if f['period_end']=='2026-06-30'}
    assert facts['cfo']['value']=='-439860000000'
    assert facts['capex_signed']['value']=='-1208669000000'
    assert facts['cash_opening']['value']=='5362150000000'
    assert facts['cash_closing']['value']=='3927072000000'
    # Cash is a balance; purchases are a duration, not the balance at close.
    assert facts['cash']['period_start'] is None
    assert facts['capex_signed']['period_start']=='2026-04-01'

def test_foreign_source_cannot_enter_legacy_or_bypass_qualification(sources,tmp_path):
    source=sources[0];doc=dict(document_id=source['document_id'],cache_path=source['path'],as_of='2026-10-09T10:24:21+00:00')
    assert approved_source(ROOT,doc,{source['document_id']:source},VARIANT)
    assert not approved_source(ROOT,doc,{source['document_id']:source},'legacy_EDGAR_only')
    assert not approved_source(ROOT,doc,{},VARIANT)
    tampered=copy.deepcopy(source);tampered['sha256']='0'*64
    assert not approved_source(ROOT,doc,{source['document_id']:tampered},VARIANT)

def test_publication_not_backdated_to_financial_close(sources):
    q=next(s for s in sources if 'q1fy2026_01_en.pdf' in s['url'])
    assert q['period_end']=='2026-06-30'
    assert q['publication_date']=='2026-08-06'
    assert q['original_url'].endswith('_ja.pdf')
    assert stamp(q['publication_date'])>'2026-06-30T23:59:59+00:00'

def test_chronology_preserves_decision_execution_and_currencies():
    rows=json.loads((ROOT/'work/softbank/chronology_observations.json').read_text())
    items={r['quantity']:r for r in rows}
    assert items['march_bridge_prepayment_decision']['stage']=='signed'
    assert items['march_bridge_outstanding_closed']['stage']=='settled'
    assert items['march_bridge_outstanding_closed']['amount']=='0'
    assert items['senior_notes_new_EUR_nominal']['currency']=='EUR'
    assert items['senior_notes_new_USD_nominal']['currency']=='USD'
    assert items['OpenAI_annual_service_spend_announced']['stage']=='intent_non_binding'
    assert items['OpenAI_annual_service_spend_announced']['counterparty']=='OpenAI, Inc.'

def test_Tsubaki_signed_and_Apollo_only_arranger():
    items={r['quantity']:r for r in json.loads((ROOT/'work/softbank/authored_observations.json').read_text())}
    assert items['signed_loan_nominal']['stage']=='signed'
    assert items['arranger_roles'].get('amount') is None
    assert items['parent_guarantee'].get('amount') is None
    assert items['energy_warrants_customer_incentive']['counterparty_evidence']=='anonymous'

def test_cash_flow_transfer_component_is_preserved(sources):
    q=next(s for s in sources if s.get('regulatory_identifier')=='S100W4HN')
    frame={f['concept']:Decimal(f['value']) for f in extract_japanese(ROOT,q) if f['period_end']=='2025-03-31'}
    assert frame['cash_held_for_sale_transfer']==Decimal('33011000000')
    assert frame['cash_change']==sum(frame[c] for c in ['cfo','cfi','cff','cash_fx','cash_held_for_sale_transfer'])
