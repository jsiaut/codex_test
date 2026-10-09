from decimal import Decimal
from pathlib import Path
import json
import pytest
from secfragility.xbrl import parse_instance
from secfragility.invariants import guarded_sum,InvalidAggregate
from secfragility.observations import validate_semantics,ObservationRejected
from secfragility.text import normalize_html,content_key


def instance(year=2025,dimensions=False):
    dimension='''<xbrli:segment><xbrldi:explicitMember dimension="g:StatementBusinessSegmentsAxis">g:CloudMember</xbrldi:explicitMember></xbrli:segment>''' if dimensions else ''
    return f'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
        xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:g="http://fasb.org/us-gaap/{year}"
        xmlns:iso="http://www.xbrl.org/2003/iso4217">
      <xbrli:context id="c"><xbrli:entity><xbrli:identifier scheme="SEC">123</xbrli:identifier>{dimension}</xbrli:entity>
        <xbrli:period><xbrli:startDate>2024-01-01</xbrli:startDate><xbrli:endDate>2024-12-31</xbrli:endDate></xbrli:period></xbrli:context>
      <xbrli:unit id="u"><xbrli:measure>iso:USD</xbrli:measure></xbrli:unit>
      <g:Revenues id="f1" contextRef="c" unitRef="u" decimals="-6">1000000</g:Revenues>
    </xbrli:xbrl>'''.encode()


def fact(raw,document_id='d'):
    return parse_instance(raw,entity_id='legal:successor',reporting_identity='reporter:S',group_id='S',
        document_id=document_id,accession='0000000123-25-000001',acceptance_datetime='2025-02-01T12:00:00Z',
        knowledge_date='2025-02-01',assurance_level='audited',as_of='2026-10-09T00:00:00Z')[0]


def test_taxonomy_versions_do_not_split_semantic_identity():
    old,new=fact(instance(2025)),fact(instance(2026),document_id='later')
    assert old['semantic_key']==new['semantic_key']
    assert old['fact_id']!=new['fact_id']
    assert old['taxonomy_version']!=new['taxonomy_version']
    assert old['value']==Decimal('1000000')


def test_dimensions_are_part_of_identity():
    consolidated,segment=fact(instance()),fact(instance(dimensions=True))
    assert consolidated['semantic_key']!=segment['semantic_key']
    assert consolidated['dimensions']=='{}'


def element(amount_id,value='100',**kwargs):
    return dict({'amount_id':amount_id,'value':value,'tier':'A','currency':'USD','unit':'USD',
        'node_id':'S','source_perspective':'reporting_entity','accounting_framework':'us_gaap',
        'entity_status':'confirmed','measurement_basis':'carrying_value','elimination_status':'external'},**kwargs)


def test_guaranteed_debt_cannot_be_summed_with_guarantee():
    amounts=[element('debt'),element('guarantee')]
    relation={'amount_a_id':'debt','amount_b_id':'guarantee','relation_type':'covers','resolved':True}
    result=guarded_sum(amounts,[relation],homogeneous_basis='carrying_value',expected_count=2)
    assert result['status']=='blocked_overlap' and result['value'] is None


@pytest.mark.parametrize('change,invariant',[
    ({'tier':'E'},'a_inadmissible_evidence'),
    ({'currency':'EUR'},'b_mixed_currency'),
    ({'unit':'shares'},'incompatible_units'),
    ({'accounting_framework':'ifrs'},'f_mixed_accounting_frameworks'),
    ({'entity_status':'pending'},'g_pending_entity_or_abstention'),
    ({'source_perspective':'counterparty'},'e_mixed_source_perspectives')])
def test_inadmissible_aggregates_are_rejected(change,invariant):
    with pytest.raises(InvalidAggregate) as exc:
        guarded_sum([element('a'),element('b',**change)],[],homogeneous_basis='carrying_value',expected_count=2)
    assert exc.value.invariant==invariant


def test_absence_does_not_become_zero_in_a_sum():
    result=guarded_sum([element('a'),element('b',None)],[],homogeneous_basis='carrying_value',expected_count=2)
    assert result=={'status':'partial','value':Decimal('100'),'nd_reason':'missing_terms'}
    assert guarded_sum([],[],homogeneous_basis='carrying_value',expected_count=1)['value'] is None


def test_citation_amount_and_named_counterparty_are_verified():
    raw=b'<div>We paid OpenAI $100.</div>'
    text=normalize_html(raw)
    candidate={'fact_id':'f','value':'100','unit':'USD','currency':'USD','period_start':'2025-01-01','period_end':'2025-12-31'}
    block={'content_key':content_key(text,[candidate],'1'),'text':text,'candidates':[candidate]}
    row={'content_key':block['content_key'],'raw_byte_start':0,'raw_byte_end':len(raw),
        'quote':'We paid OpenAI $100.','counterparty':'OpenAI','counterparty_evidence':'named',
        'amount':'100','amount_origin':'tagged_reference','tagged_fact_id':'f','unit':'USD','currency':'USD',
        'period_start':'2025-01-01','period_end':'2025-12-31'}
    validate_semantics(row,block,raw)
    with pytest.raises(ObservationRejected): validate_semantics(dict(row,amount='101'),block,raw)
    with pytest.raises(ObservationRejected): validate_semantics(dict(row,counterparty='Anthropic'),block,raw)
    with pytest.raises(ObservationRejected): validate_semantics(dict(row,quote='We paid Anthropic $100.'),block,raw)
