import json
from pathlib import Path
from secfragility.document_order import provenance,fact_order


def test_derived_instance_requires_unambiguous_physical_fact_origin(tmp_path):
    folder=tmp_path/'work';folder.mkdir()
    (folder/'one.htm').write_text('<html><body><ix:nonFraction id="unique" name="g:Revenue">10</ix:nonFraction><ix:nonFraction id="shared" name="g:Revenue">11</ix:nonFraction></body></html>')
    (folder/'two.htm').write_text('<html><body><ix:nonFraction id="shared" name="g:Revenue">12</ix:nonFraction></body></html>')
    headers=[{'filename':'one.htm','document_rank':3},{'filename':'two.htm','document_rank':7},
        {'filename':'classic.xml','document_rank':9}]
    (folder/'discovery.json').write_text(json.dumps({'headers':headers}))
    filing={'discovery_path':'work/discovery.json','resources':{
        'one.htm':{'path':'work/one.htm','url':'https://example.test/one.htm'},
        'two.htm':{'path':'work/two.htm','url':'https://example.test/two.htm'}}}
    (folder/'collection.json').write_text(json.dumps({'filings':{'a':filing}}))
    source=provenance(str(tmp_path),'a')
    fact={'locator':'id:unique','concept':'g:Revenue','document_id':'derived'}
    rank,rule,parent=fact_order('derived.xml',fact,source)
    assert rank==3 and rule=='exact_inline_fact_id_and_concept' and parent!='derived'
    assert fact_order('derived.xml',dict(fact,locator='id:shared'),source)==(-2,'unresolved_physical_document_order',None)
    assert fact_order('derived.xml',dict(fact,concept='g:Debt'),source)==(-2,'unresolved_physical_document_order',None)
    assert fact_order('classic.xml',fact,source)==(9,'SGML_DOCUMENT_order','derived')
