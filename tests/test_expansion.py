import hashlib,json
from pathlib import Path
import pytest
from secfragility.evidence import periodic_assurance,filing_status,tier
from secfragility.expansion_assembly import reported_control,qualifies_source,stage_scope
from secfragility.entities import normalize

def test_foreign_report_is_not_automatically_audited_or_filed():
    assert periodic_assurance('20-F')=='audited'
    assert periodic_assurance('6-K')=='unknown'
    assert filing_status('6-K')=='furnished'
    args=dict(edgar=True,filing_status='furnished',document_kind='financial_note',assurance_level='unknown')
    assert tier(**args)=='E'
    assert tier(**args,incorporated_by_reference=True)=='C'

def test_control_requires_explicit_reporter_parent_judgment():
    parent=dict(entity_id='cik:apo',cik='apo',economic_group_id='APO',legal_name='Apollo Global Management, Inc.')
    child=dict(entity_id='cik:ath',cik='ath',economic_group_id='ATH',legal_name='Athene Holding Ltd.')
    fund=dict(entity_id='legal:whco',economic_group_id='legal:whco',legal_name='WarehouseCo Intermediate Holdings LP')
    records=[parent,child,fund];idx={normalize(parent['legal_name']):[parent]}
    base=dict(entity_id='cik:ath',counterparty=parent['legal_name'],document_id='original-note',locator='rawbytes:1:10',knowledge_date='2026-08-10')
    reported_control(records,idx,[dict(base,model_quantity='managed_fund_purchase_obligor')])
    assert child['economic_group_id']=='ATH'
    reported_control(records,idx,[dict(base,model_quantity='parent_control_membership')])
    assert child['economic_group_id']=='APO'
    assert child['legal_date'] is None
    assert fund['economic_group_id']=='legal:whco'

def test_source_qualification_checks_original_bytes_and_exact_quote(tmp_path):
    raw=b'<p>This Report is incorporated by reference.</p>'
    (tmp_path/'proof.htm').write_bytes(raw)
    record=dict(proof_path='proof.htm',proof_sha256=hashlib.sha256(raw).hexdigest(),quote='This Report is incorporated by reference.')
    assert qualifies_source(tmp_path,record)
    with pytest.raises(ValueError):qualifies_source(tmp_path,dict(record,quote='No such incorporation.'))
    (tmp_path/'proof.htm').write_bytes(b'changed')
    with pytest.raises(ValueError):qualifies_source(tmp_path,record)

def test_deferred_scope_never_creates_read_markers(tmp_path):
    work=tmp_path/'work';(work/'expansion').mkdir(parents=True);(work/'observations').mkdir()
    q=[dict(content_key=k,occurrence_id=k,group='g',accession='a',path=k,chars=1) for k in ['old','selected','pending']]
    (work/'queue.json').write_text(json.dumps(q))
    (work/'expansion/queue.json').write_text(json.dumps(q[1:]))
    (work/'run.json').write_text(json.dumps(dict(as_of='2026-10-09T00:00:00+00:00')))
    (work/'observations/old.jsonl').write_text('{}\n')
    with pytest.raises(ValueError):stage_scope(tmp_path,{'selected'})
    (work/'observations/selected.jsonl').write_text('{}\n')
    assert stage_scope(tmp_path,{'selected'})==dict(active=1,deferred=1)
    assert not (work/'observations/pending.jsonl').exists()
    excluded=json.loads((work/'expansion/scope_exclusions.json').read_text())
    assert excluded[0]['reason']=='not_processed'
    assert {r['content_key'] for r in json.loads((work/'queue.json').read_text())}=={'old','selected'}
