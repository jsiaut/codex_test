from pathlib import Path
from secfragility.xbrl import namespace_family,canonical_qname,parse_instance
from secfragility.spacex_annual import label_key
from secfragility.blocks import section_blocks


def test_nested_inline_tags_preserve_full_text_and_physical_ranges():
    from secfragility.text import extract_inline_blocks,normalize_space,render,parse_html
    meta={'instance':{'x':{'tag':{'g_Note':{'xbrltype':'textBlockItemType',
        'presentation':['r']}},'report':{'r':{'role':'r','groupType':'disclosure','menuCat':'Notes'}}}}}
    for raw in [
        b'<html><body><ix:nonNumeric id="n" name="g:Note"><p>First</p>'
        b'<ix:nonNumeric id="inner" name="g:Policy">Inner</ix:nonNumeric>'
        b'<p>Last after nested policy.</p></ix:nonNumeric><p>Outside.</p></body></html>',
        b'<html><body><ix:nonNumeric id="n" name="g:Note" continuedAt="outer">First</ix:nonNumeric>'
        b'<ix:continuation id="outer"><p>Next</p><ix:continuation id="inner">Inner</ix:continuation>'
        b'<p>Last after nested continuation.</p></ix:continuation><p>Outside.</p></body></html>',
    ]:
        blocks=extract_inline_blocks(raw,meta,[],normalizer_version='1')
        assert len(blocks)==1
        block=blocks[0]
        assert 'Last after nested' in block['text']
        assert 'Outside' not in block['text']
        physical='\n'.join(normalize_space(render(parse_html(raw[a:z]))) for a,z in block['source_ranges'])
        assert 'Last after nested' in physical
        assert 'Outside' not in physical


def test_exhibit_101_is_not_contract_exhibit_10():
    from secfragility.text import requested_contract_exhibit
    assert requested_contract_exhibit('EX-10.1')
    assert requested_contract_exhibit('EX-4.23')
    assert requested_contract_exhibit('EX-10')
    assert not requested_contract_exhibit('EX-101.SCH')
    assert not requested_contract_exhibit('EX-40')


def test_contract_header_follows_physical_page_even_after_six_thousand_chars():
    from secfragility.text import exhibit_first_page
    raw=(b'<html><body><div style="page-break-before:always"></div><p>Agreement</p><p>'
        +b'Opening text. '*700+b'</p><p>Customer Corp is a party.</p>'
        +b'<div style="page-break-before:always"></div><p>Second page body.</p></body></html>')
    page=exhibit_first_page(raw)
    assert page['boundary_status']=='explicit_physical_page_break'
    assert 'Customer Corp is a party.' in page['text']
    assert 'Second page' not in page['text']
    assert page['raw_byte_end']>6000


def test_contract_break_after_parent_and_unpaginated_document():
    from secfragility.text import exhibit_first_page
    raw=(b'<html><body><div style="page-break-after:always"><div>Nested</div>'
        b'<p>First page parties.</p></div><p>Second page.</p></body></html>')
    page=exhibit_first_page(raw)
    assert 'First page parties.' in page['text'] and 'Second page.' not in page['text']
    page=exhibit_first_page(b'<html><body><p>Unpaginated agreement.</p></body></html>')
    assert page['boundary_status']=='unpaginated_full_document'
    assert 'Unpaginated agreement.' in page['text']


def test_large_candidate_header_is_served_completely_before_text(tmp_path):
    import json
    from secfragility.reader import serve,DISPLAY_CEILING
    folder=tmp_path/'work';folder.mkdir()
    candidates=[{'fact_id':str(i),'dimensions':json.dumps({'typed_member':'x'*900}),
        'value':str(i),'unit':'USD','period_end':'2026-06-30'} for i in range(65)]
    block={'content_key':'k','occurrence_id':'o','block_class':'item404','text':'The complete contract clause.',
        'candidates':candidates}
    (folder/'block.json').write_text(json.dumps(block))
    (folder/'queue.json').write_text(json.dumps([{'content_key':'k','path':'work/block.json'}]))
    first=serve(tmp_path,'k');parts=[first]+[serve(tmp_path,'k',part=i) for i in range(1,first['parts'])]
    assert all(len(json.dumps(p,ensure_ascii=False))<=DISPLAY_CEILING for p in parts)
    assert [f['fact_id'] for p in parts for f in p['candidates']]==[str(i) for i in range(65)]
    assert all(p['packet_kind']=='candidate_header' for p in parts[:-1])
    assert parts[-1]['text']=='The complete contract clause.'


def test_committee_sentence_fragment_is_not_a_proxy_heading():
    raw=(b'<div><p>The committee reviews <span>related party transactions.</span></p>'
         b'<p>Its audit oversight report describes review of financial statements and '
         b'independence policies. This text describes committee responsibilities only.</p>'
         b'<p style="font-size:14pt;font-weight:bold">CERTAIN RELATIONSHIPS AND RELATED PARTY TRANSACTIONS</p>'
         b'<p>The company purchased services from a named related entity. The transaction '
         b'is described here together with its approval process and reporting obligations.</p>'
         b'<p style="font-size:14pt;font-weight:bold">OTHER INFORMATION</p></div>')
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1
    assert 'The company purchased services' in blocks[0]['text']
    assert 'audit oversight report' not in blocks[0]['text']


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


def test_unlinked_proxy_toc_and_nested_same_font_heading_are_not_boundaries():
    raw=b'''<html><body>
    <div style="font-size:10pt;font-weight:700">CERTAIN RELATIONSHIPS AND RELATED PARTY TRANSACTIONS 57</div>
    <div>QUESTIONS AND ANSWERS 64</div>
    <div style="font-size:10pt;font-weight:700">CERTAIN RELATIONSHIPS AND RELATED PARTY TRANSACTIONS</div>
    <p>The following paragraph introduces reportable transactions with related investors.</p>
    <div style="font-size:10pt;font-weight:700">Equity Investment Agreements</div>
    <p>The investor purchased shares pursuant to the described securities purchase agreement.</p>
    <div style="font-size:10pt;font-weight:700">Policies for Related Party Transactions</div>
    <p>The committee reviews these arrangements and applicable transactions.</p>
    <div style="font-size:10pt;font-weight:700">QUESTIONS AND ANSWERS ABOUT THE MEETING</div>
    <p>Unrelated meeting mechanics.</p></body></html>'''
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1
    assert 'investor purchased shares' in blocks[0]['text']
    assert 'Unrelated meeting' not in blocks[0]['text']


def test_large_nonbold_proxy_heading_bounds_section():
    raw=b'''<html><body><div style="font-size:22pt;color:#ff9e15">Certain Relationships and Related Person Transactions</div>
    <p>The company reports purchases from a related entity in the ordinary course of business.</p>
    <p>Additional terms were reviewed by its audit committee on the stated dates.</p>
    <div style="font-size:22pt;color:#ff9e15">Expenses of Solicitation</div><p>Unrelated solicitation costs.</p></body></html>'''
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1 and 'Unrelated solicitation' not in blocks[0]['text']


def test_serialized_read_packets_respect_ceiling_with_escaping(tmp_path):
    import json
    from secfragility.reader import serve
    folder=tmp_path/'work';folder.mkdir()
    text=('A quoted description: "preserve the contractual wording"\n'*1800)
    block={'content_key':'k','occurrence_id':'o','block_class':'item404','group':'T',
        'text':text,'candidates':[]}
    (folder/'block.json').write_text(json.dumps(block))
    (folder/'queue.json').write_text(json.dumps([{'content_key':'k','occurrence_id':'o','path':'work/block.json'}]))
    first=serve(tmp_path,'k');assert first['parts']>1
    packets=[first]+[serve(tmp_path,'k',i) for i in range(1,first['parts'])]
    assert all(len(json.dumps(p,ensure_ascii=False))<=80000 for p in packets)
    assert all(p['text'] in text for p in packets)
    assert packets[0]['text'].startswith('A quoted description:')
    assert packets[-1]['text'].endswith('"preserve the contractual wording"\n')


def test_anchor_inside_caption_does_not_jump_to_continued_page():
    raw=b'''<html><body><table><tr><td><a href="#rp">Certain Relationships and Related Transactions</a></td></tr>
    <tr><td><a href="#next">Other Matters</a></td></tr></table>
    <p><b><a name="rp"></a>Certain Relationships and Related Transactions</b></p>
    <p>The company bought equipment from a named related supplier during the fiscal year. The first page contains the actual identity and the commercial terms.</p>
    <p><b>Certain Relationships and Related Transactions</b> (continued)</p>
    <p>The second page states the purchase amount and a conditional minimum purchase obligation.</p>
    <div id="next">Other Matters</div><p>Unrelated meeting details.</p></body></html>'''
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1
    assert 'actual identity and the commercial terms' in blocks[0]['text']
    assert 'conditional minimum purchase' in blocks[0]['text']
    assert 'Unrelated meeting details' not in blocks[0]['text']


def test_legacy_font_peer_bounds_related_section_before_section_16a():
    raw=b'''<html><body><p><font size="2"><b>CERTAIN RELATIONSHIPS AND RELATED PERSON TRANSACTIONS</b></font></p>
    <p>A named related company purchased equipment in the fiscal year on ordinary commercial terms. The issuer reports the value and the type of goods delivered.</p>
    <p><font size="2"><b>SECTION 16(a) BENEFICIAL OWNERSHIP REPORTING COMPLIANCE</b></font></p>
    <p>Unrelated compliance and meeting procedures.</p></body></html>'''
    blocks=section_blocks(raw,form='DEF 14A',config={'normalizer_version':'1'})
    assert len(blocks)==1
    assert 'value and the type of goods' in blocks[0]['text']
    assert 'Unrelated compliance' not in blocks[0]['text']
