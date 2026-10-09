from pathlib import Path
from secfragility.xbrl import namespace_family,canonical_qname,parse_instance
from secfragility.spacex_annual import label_key
from secfragility.blocks import section_blocks


def test_issuer_namespace_date_is_attribute_even_inside_uri():
    assert namespace_family('http://www.microsoft.com/20260331/taxonomy')==namespace_family('http://www.microsoft.com/20250331/taxonomy')
    assert namespace_family('http://www.xbrl.org/2003/instance')=='http://www.xbrl.org/2003/instance'


def test_normalizer_keeps_debt_current_distinct_from_noncurrent():
    assert label_key('Debt and finance leases, current (related party of $455)')!=label_key('Debt and finance leases, net of current')
    assert label_key('Net income (loss)')==label_key('Net loss')


def test_proxy_toc_is_pointer_and_next_peer_bounds_body():
    raw=b'''<html><body><table><tr><td><a href="#related">Related Party Transactions</a></td></tr><tr><td><a href="#ownership">Security Ownership</a></td></tr></table>
      <a name="related"></a><p style="font:14pt Arial"><b>Related Party Transactions</b></p><p>The company purchased equipment from a director-owned entity for a disclosed price.</p><p>These terms were approved by the committee. Additional details cover this section.</p>
      <a name="ownership"></a><p>Security Ownership</p><p>Unrelated ownership table content.</p></body></html>'''
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1
    assert 'company purchased equipment' in blocks[0]['text']
    assert 'Unrelated ownership' not in blocks[0]['text']


def test_proxy_subheading_anchor_does_not_truncate_related_transactions():
    raw=b'''<html><body><table><tr><td><a href="#related">Certain Relationships and Related Transactions</a>
      <a href="#policy">Related Party Transactions Policy and Procedure</a><a href="#next">Security Ownership</a></td></tr></table>
      <div id="related"></div><div style="font-size:7pt">Navigation banner</div>
      <div style="font-size:20pt;font-weight:700">Certain Relationships and Related Transactions</div>
      <div id="policy"></div><div style="font-size:16pt;font-weight:700">Related Party Transactions Policy and Procedure</div>
      <p>The committee reviews the terms of transactions involving directors.</p>
      <p>The company obtained equipment from a related entity on market terms.</p>
      <div id="next"></div><div style="font-size:20pt;font-weight:700">Security Ownership</div><p>Unrelated material.</p></body></html>'''
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1
    assert 'obtained equipment' in blocks[0]['text']
    assert 'Navigation banner' not in blocks[0]['text']
    assert 'Unrelated material' not in blocks[0]['text']


def test_iso_duration_preserved_without_guessing_days_to_years():
    raw=b'''<xbrl xmlns="http://www.xbrl.org/2003/instance" xmlns:us-gaap="http://fasb.org/us-gaap/2026">
    <context id="c"><entity><identifier scheme="s">1</identifier></entity><period><instant>2026-06-30</instant></period></context>
    <us-gaap:PropertyPlantAndEquipmentUsefulLife contextRef="c" id="life">P5Y7M</us-gaap:PropertyPlantAndEquipmentUsefulLife></xbrl>'''
    facts=parse_instance(raw,entity_id='cik:0000000001',reporting_identity='reporter:T',group_id='T',document_id='d',accession='a',
       acceptance_datetime='2026-08-01T12:00:00Z',knowledge_date='2026-08-01',assurance_level='reviewed',as_of='2026-10-09T00:00:00Z')
    assert len(facts)==1 and facts[0]['text_value']=='P5Y7M'
    assert facts[0]['value'] is None and not facts[0]['is_nil']
