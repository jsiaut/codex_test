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


def test_reader_semantic_conflict_blocks_numeric_use_without_changing_raw_fact(tmp_path):
    from secfragility.database import create, insert
    source = Path(__file__).resolve().parents[1]
    (tmp_path / 'schema.sql').write_text((source / 'schema.sql').read_text())
    (tmp_path / 'work').mkdir()
    bad = fact(instance())
    duplicate = fact(instance(), document_id='companyfacts-copy')
    duplicate['document_rank'] = -1
    good = fact(instance(dimensions=True), document_id='unrelated')
    corrected = fact(instance(), document_id='later-corrected-filing')
    corrected['accession'] = '0000000123-25-000002'
    (tmp_path / 'work/fact_semantic_quarantines.json').write_text(json.dumps([{
        'fact_id': bad['fact_id'], 'affected_quantity': 'private_investment_stock',
        'reason': 'Deposited concept contradicts the fully read marketable-securities clause',
        'status': 'exclude_dependent_numeric_attribution_keep_raw_fact'}]))
    db = create(tmp_path)
    insert(db, 'facts', bad)
    insert(db, 'facts', duplicate)
    insert(db, 'facts', good)
    insert(db, 'facts', corrected)
    db.execute((source / 'queries.sql').read_text())
    assert db.execute('SELECT value FROM facts WHERE fact_id=?', [bad['fact_id']]).fetchone()[0] == Decimal('1000000')
    assert db.execute('SELECT value,coverage_state FROM eligible_facts WHERE fact_id=?',
                      [bad['fact_id']]).fetchone() == (None, 'conflicting')
    assert db.execute('SELECT value FROM eligible_facts WHERE fact_id=?', [duplicate['fact_id']]).fetchone()[0] is None
    assert db.execute('SELECT value FROM eligible_facts WHERE fact_id=?', [good['fact_id']]).fetchone()[0] == Decimal('1000000')
    assert db.execute('SELECT value FROM eligible_facts WHERE fact_id=?', [corrected['fact_id']]).fetchone()[0] == Decimal('1000000')


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


def test_quote_across_declared_continuations_excludes_page_footer():
    raw=b'<div>Investor paid $100</div><div>Page 12</div><div>for the services.</div>'
    first_end=raw.index(b'<div>Page');last_start=raw.index(b'<div>for')
    block={'content_key':'continuation','text':'Investor paid $100\nfor the services.','candidates':[],
        'source_ranges':[[0,first_end],[last_start,len(raw)]]}
    row={'content_key':'continuation','raw_byte_start':0,'raw_byte_end':len(raw),
        'quote':'Investor paid $100\nfor the services.','amount':'100','unit':'USD','currency':'USD','amount_origin':'narrative_only'}
    validate_semantics(row,block,raw)
    bad=dict(block,source_ranges=[[0,first_end],[last_start,len(raw)+1]])
    with pytest.raises(ObservationRejected):validate_semantics(row,bad,raw)


def test_wrapped_legal_name_preserves_all_words_and_punctuation():
    raw=b'<div>We paid BCH San<br>Jose LLC $100.</div>'
    body=normalize_html(raw)
    block={'content_key':'wrapped','text':body,'candidates':[]}
    row={'content_key':'wrapped','raw_byte_start':0,'raw_byte_end':len(raw),
        'quote':body,'counterparty':'BCH San Jose LLC','counterparty_evidence':'named',
        'amount':'100','amount_origin':'narrative_only','unit':'USD','currency':'USD'}
    validate_semantics(row,block,raw)
    for other in ['BCH San Jose Holdings LLC','BCH San Jose, LLC','bch San Jose LLC']:
        with pytest.raises(ObservationRejected):
            validate_semantics(dict(row,counterparty=other),block,raw)


def test_table_scale_requires_explicit_heading_and_currency_amount_cell():
    raw=b'<div>Fiscal year 2018</div><div>(In millions)</div><table><tr><td>Total revenue</td><td>$</td><td>664</td></tr></table>'
    body=normalize_html(raw)
    block={'content_key':'scaled-table','text':body,'candidates':[]}
    row={'content_key':'scaled-table','raw_byte_start':0,'raw_byte_end':len(raw),
        'quote':body,'amount':'664000000','amount_origin':'narrative_only','unit':'USD','currency':'USD'}
    validate_semantics(row,block,raw)
    for bad in ['2018000000','664000']:
        with pytest.raises(ObservationRejected):validate_semantics(dict(row,amount=bad),block,raw)


def test_sterling_narrative_requires_actual_currency_evidence():
    raw='<div>The estimated net proceeds were approximately £4.235 billion.</div>'.encode()
    body=normalize_html(raw)
    block={'content_key':'sterling','text':body,'candidates':[]}
    row={'content_key':'sterling','raw_byte_start':0,'raw_byte_end':len(raw),
        'quote':body,'amount':'4235000000','amount_origin':'narrative_only',
        'unit':'GBP','currency':'GBP'}
    validate_semantics(row,block,raw)
    for wrong_currency in ['USD','EUR']:
        with pytest.raises(ObservationRejected,match='Devise narrative'):
            validate_semantics(dict(row,currency=wrong_currency,unit=wrong_currency),block,raw)


def test_canadian_dollars_do_not_prove_US_dollars():
    raw='<div>The public offering price was C$13.967 billion.</div>'.encode()
    body=normalize_html(raw)
    block={'content_key':'canadian','text':body,'candidates':[]}
    row={'content_key':'canadian','raw_byte_start':0,'raw_byte_end':len(raw),
        'quote':body,'amount':'13967000000','amount_origin':'narrative_only',
        'unit':'CAD','currency':'CAD'}
    validate_semantics(row,block,raw)
    with pytest.raises(ObservationRejected,match='Devise narrative'):
        validate_semantics(dict(row,currency='USD',unit='USD'),block,raw)
