from datetime import datetime,timezone
from decimal import Decimal
from pathlib import Path
import json
import httpx
import pytest
import yaml

from secfragility.annexes import dependency_outcome,link_outcome,chronology_outcome,nondiscrimination
from secfragility.database import create,insert
from secfragility.evidence import tier,filing_status
from secfragility.network import SecClient,SessionLock,AccessPaused,AccessStopped
from secfragility.text import normalize_html,content_key,autonomous_amendment
from secfragility.xbrl import inline_number,instance_number,half_unit,parse_instance

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('text,scale,sign,expected',[
    ('1,250','6',None,'1250000000'),('2.5','-2','-','-0.025'),
    ('(10)','0',None,'-10'),('0','9',None,'0')])
def test_inline_scale_and_sign(text,scale,sign,expected):
    assert inline_number(text,scale=scale,sign=sign)==Decimal(expected)


def test_extracted_instance_is_already_scaled():
    assert instance_number('1250000000')==Decimal('1250000000')
    assert inline_number('—',transform='ixt:fixed-zero')==0
    assert inline_number('—',nil=True) is None
    with pytest.raises(Exception): inline_number('—')


def test_precision_is_tolerance_not_multiplier():
    assert half_unit('-6')==Decimal('500000')
    assert half_unit('2')==Decimal('.005')
    assert half_unit('INF')==half_unit(32767)==0


def test_text_preserves_split_names_and_excludes_hidden_content():
    raw=b'<div>Open<span>AI</span>&nbsp;Inc. &amp; Anthropic<ix:hidden>Invented party</ix:hidden></div>'
    assert normalize_html(raw)=='OpenAI Inc. & Anthropic'


def test_ix_continuation_is_joined_once():
    raw=b'<div><ix:nonNumeric continuedAt="c">Contract with </ix:nonNumeric><ix:continuation id="c">OpenAI.</ix:continuation></div>'
    assert normalize_html(raw)=='Contract with OpenAI.'


def test_table_rowspan_keeps_header_next_to_value():
    raw=b'<table><tr><th rowspan="2">Customer A</th><td>2025</td><td>10%</td></tr><tr><td>2026</td><td>12%</td></tr></table>'
    assert normalize_html(raw)=='Customer A | 2025 | 10%\nCustomer A | 2026 | 12%'


def test_read_limit_and_occurrence_id_do_not_change_content_key():
    fact={'fact_id':'old','canonical_concept':'us-gaap:Revenues','value':'100','unit':'USD','dimensions':'{}'}
    changed=dict(fact,fact_id='new')
    assert content_key('Revenue',[fact],'1')==content_key('Revenue',[changed],'1')
    assert content_key('Revenue',[fact],'1')!=content_key('Revenue',[dict(fact,value='101')],'1')


@pytest.mark.parametrize('status,kind,assurance,incorporated,expected',[
    ('filed','financial_statements','audited',False,'A'),
    ('filed','financial_note','reviewed',False,'B'),
    ('filed','contract','unknown',False,'D'),
    ('furnished','financial_statements','audited',False,'E'),
    ('furnished','financial_statements','audited',True,'A'),
    ('filed','marketing','audited',False,'E')])
def test_evidence_precedence(status,kind,assurance,incorporated,expected):
    assert tier(edgar=True,filing_status=status,document_kind=kind,assurance_level=assurance,
        incorporated_by_reference=incorporated)==expected


def test_filed_furnished_and_draft_are_different():
    assert filing_status('8-K','7.01')=='furnished'
    assert filing_status('8-K','1.01')=='filed'
    assert filing_status('8-K')=='unclassified'
    assert filing_status('DRS')=='submitted_draft'


@pytest.mark.parametrize('title,exhibit,items,expected',[
    ('Limited Waiver','EX-10.1',[],True),
    ('Omnibus Amendment','EX-10.1',[],True),
    ('Amendment No. 3 to Amended and Restated Credit Agreement','EX-10.1',[],True),
    ('Third Amended and Restated Credit Agreement','EX-10.1',[],False),
    ('First Supplemental Indenture','EX-4.1',['3.03'],True),
    ('First Supplemental Indenture','EX-4.1',['2.03'],False)])
def test_amendments_are_read_even_with_financial_parties(title,exhibit,items,expected):
    assert autonomous_amendment(title,exhibit,items)==expected


def test_enums_and_measure_specific_terms_are_enforced():
    db=create(ROOT)
    row={'measure':'capex_to_cfo','group_id':'S','period_start':'2025-01-01','period_end':'2025-03-31',
        'view':'as_known','as_of':'2026-01-01T00:00:00+00:00','term':'opening','status':'not_determinable',
        'nd_reason':'not_processed','coverage_state':'not_processed'}
    with pytest.raises(Exception): insert(db,'measures',row)
    row['term']='without'
    insert(db,'measures',row)
    with pytest.raises(Exception): insert(db,'measures',row)
    assert db.execute('select count(*) from measures').fetchone()[0]==1


def test_403_suppresses_all_sec_requests_for_ten_minutes(tmp_path):
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text())
    clock=[1000.0]
    calls=[]
    def transport(request):
        calls.append(request)
        return httpx.Response(403,text='denied')
    with SessionLock(tmp_path,120) as lock:
        c=SecClient(tmp_path,cfg,'2026-01-01T00:00:00+00:00',lock,
            transport=httpx.MockTransport(transport),clock=lambda:clock[0],sleep=lambda d:clock.__setitem__(0,clock[0]+d))
        with pytest.raises(AccessPaused): c.get('https://www.sec.gov/files/company_tickers.json')
        clock[0]=1599.9
        with pytest.raises(AccessPaused): c.get('https://data.sec.gov/submissions/CIK0000002488.json')
        assert len(calls)==1
        clock[0]=1600
        with pytest.raises(AccessStopped): c.get('https://www.sec.gov/files/company_tickers.json')
        assert len(calls)==2
        assert c.state['stopped']
        c.close()


def test_contact_is_never_sent_to_non_sec_host(tmp_path):
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text())
    with SessionLock(tmp_path,120) as lock:
        c=SecClient(tmp_path,cfg,'2026-01-01T00:00:00+00:00',lock,
            transport=httpx.MockTransport(lambda req:pytest.fail('Network must not be called')))
        with pytest.raises(ValueError): c.get('https://example.com/')
        c.close()


def test_e2_requires_consecutive_years_and_strict_refutation():
    criteria={'min_consecutive_support_years':2,'min_evaluable_refutation_years':2}
    def year(y,low,high): return {'fiscal_year':y,'status':'bounded','value_lower':low,'value_upper':high}
    assert dependency_outcome([year(2023,'.10','.11'),year(2024,'.10','.11')],Decimal('.1'),criteria)['outcome']=='supported'
    assert dependency_outcome([year(2022,'.10','.11'),year(2024,'.10','.11')],Decimal('.1'),criteria)['outcome']=='indeterminate'
    assert dependency_outcome([year(2023,'0','.05'),year(2024,'0','.05')],Decimal('.1'),criteria)['outcome']=='indeterminate'
    assert dependency_outcome([year(2023,'0','.049'),year(2024,'0','.049')],Decimal('.1'),criteria)['outcome']=='refuted'
    assert link_outcome(active=True,linkage_classes=[],search_complete=False)['outcome']=='indeterminate'


def test_nondiscrimination_threshold_is_strict_and_pair_based():
    outcomes=[{'statement':'E1','outcome':'indeterminate' if i<7 else 'supported'} for i in range(10)]
    assert not nondiscrimination(outcomes,Decimal('.70'))['publish_statement']
    outcomes[7]['outcome']='indeterminate'
    assert nondiscrimination(outcomes,Decimal('.70'))['publish_statement']
    assert nondiscrimination([],Decimal('.70'))['status']=='not_determinable'


def test_sql_ratio_uses_exact_arithmetic_and_bankers_rounding():
    db=create(ROOT)
    db.execute((ROOT/'queries.sql').read_text())
    for a,b,expected in [('1','3','0.333333'),('1','2000000','0.000000'),
                         ('3','2000000','0.000002'),('-3','2000000','-0.000002'),
                         ('9000000000000001','9000000000000000','1.000000')]:
        value=db.execute('SELECT exact_ratio6(?::DECIMAL(38,6),?::DECIMAL(38,6))',[a,b]).fetchone()[0]
        assert value==Decimal(expected)
