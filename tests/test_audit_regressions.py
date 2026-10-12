"""Reproductions of the audit's failure cases; no simulated financial defaults."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime,timezone
import hashlib,json,shutil
import httpx,pytest,yaml
from secfragility.database import create,insert,export,connect
from secfragility.observations import validate_semantics,ObservationRejected
from secfragility.text import normalize_html
from secfragility.network import SessionLock,SecClient

ROOT=Path(__file__).resolve().parents[1]

def minimal(tmp):
    (tmp/'work').mkdir(exist_ok=True)
    shutil.copy2(ROOT/'schema.sql',tmp/'schema.sql')
    return create(tmp)

@pytest.mark.parametrize('zone',['UTC','Europe/Paris','America/New_York'])
def test_same_day_boundary_has_identical_cutoff_and_value(tmp_path,zone):
    from tests.test_identity_and_guards import fact,instance
    from secfragility.calculation import prepare_views
    from secfragility.quarter_series import prepare
    db=minimal(tmp_path)
    for n in ('queries.sql','config.yaml'):shutil.copy2(ROOT/n,tmp_path/n)
    (tmp_path/'work/expected_universe.json').write_text(json.dumps({'quarters':[dict(group_id='S',period_start='2024-10-01',period_end='2024-12-31',fiscal_year_start='2024-01-01',quarter_number=4)]}))
    for did,accepted,amount in [('first','2025-02-04T23:00:00Z','1000000'),('later','2025-02-05T04:00:00Z','2000000')]:
        f=dict(fact(instance(),document_id=did),accession=did,period_start='2024-10-01',acceptance_datetime=accepted,
               knowledge_date='2025-02-05',model_quantity='revenue_total',value=Decimal(amount))
        insert(db,'facts',f)
        insert(db,'documents',dict(document_id=did,group_id='S',accession=did,url='https://www.sec.gov/'+did,cache_path=did,sha256=did,
            form='10-K',filing_status='filed',acceptance_datetime=accepted,knowledge_date='2025-02-05',as_of='2026-10-09T00:00:00Z'))
    db.execute("SET TimeZone='"+zone+"'")
    prepare_views(db,tmp_path,'2026-10-09T00:00:00Z')
    db.execute("SET TimeZone='"+zone+"'")
    prepare(db,tmp_path,'2026-10-09T00:00:00Z')
    cutoff=db.execute('SELECT public_at FROM quarter_cutoffs').fetchone()[0]
    assert cutoff.astimezone(timezone.utc)==datetime(2025,2,5,tzinfo=timezone.utc)
    assert db.execute('SELECT value FROM quarter_quantities_as_known').fetchone()[0]==Decimal('1000000')

def test_named_amount_cannot_borrow_a_name_from_another_sentence():
    raw=b'<p>We paid OpenAI $100. We paid Anthropic $200.</p>';text=normalize_html(raw)
    block=dict(content_key='k',text=text,candidates=[])
    row=dict(content_key='k',raw_byte_start=0,raw_byte_end=len(raw),quote='We paid OpenAI $100.',
             counterparty='Anthropic',counterparty_evidence='named',amount='100',amount_origin='narrative_only',currency='USD',unit='USD')
    with pytest.raises(ObservationRejected,match='citation du montant'):validate_semantics(row,block,raw)
    row['counterparty']='OpenAI';validate_semantics(row,block,raw)

def test_documentary_reference_requires_a_separate_binding_proof():
    raw=b'<p>Investee A received $100. See contract A. Contract A names OpenAI.</p>';text=normalize_html(raw)
    row=dict(content_key='k',raw_byte_start=0,raw_byte_end=len(raw),quote='Investee A received $100. See contract A.',model_quantity='funding',
             counterparty='OpenAI',counterparty_evidence='derivable',counterparty_method='explicit_cross_reference',amount='100',amount_origin='narrative_only',currency='USD',unit='USD')
    block=dict(content_key='k',text=text,candidates=[])
    with pytest.raises(ObservationRejected,match='preuve séparée'):validate_semantics(row,block,raw)
    block['attribution_evidence']=dict(method='explicit_cross_reference',quantity='funding',amount_quote=row['quote'],binding_quote='Contract A names OpenAI.')
    validate_semantics(row,block,raw)

def test_checkpoint_changes_for_code_but_not_markdown(tmp_path):
    from secfragility.assembly_checkpoint import inputs
    (tmp_path/'secfragility').mkdir();p=tmp_path/'secfragility/calculation.py';p.write_text('value=1\n')
    initial=inputs(tmp_path);(tmp_path/'README.md').write_text('more explanation')
    assert inputs(tmp_path)==initial
    p.write_text('value=2\n');assert inputs(tmp_path)!=initial

def test_lost_network_lock_sends_no_request(tmp_path):
    cfg=yaml.safe_load((ROOT/'config.yaml').read_text());calls=[]
    with SessionLock(tmp_path,120) as lock:
        client=SecClient(tmp_path,cfg,'2026-01-01T00:00:00Z',lock,transport=httpx.MockTransport(lambda req:calls.append(req) or httpx.Response(200,content=b'{}')))
        lock.path.write_text(json.dumps({'token':'another-owner'}))
        with pytest.raises(RuntimeError,match='verrou'):client.get('https://data.sec.gov/submissions/CIK0000002488.json')
        client.close()
    assert not calls

def test_failed_export_keeps_all_old_files_and_pointer(tmp_path):
    from secfragility.publication import sha
    db=minimal(tmp_path)
    insert(db,'documents',dict(document_id='d',url='old',cache_path='d',sha256='d',filing_status='filed',as_of='2026-01-01T00:00:00Z'))
    export(db,tmp_path/'tables');before={p.name:sha(p) for p in (tmp_path/'tables').glob('*.parquet')};pointer=(tmp_path/'tables').resolve()
    db.execute("UPDATE documents SET url='new'")
    class Broken:
        def execute(self,query,*args):
            if query.startswith('COPY') and 'FROM entities ' in query:raise OSError('injected export failure')
            return db.execute(query,*args)
    with pytest.raises(OSError):export(Broken(),tmp_path/'tables')
    assert (tmp_path/'tables').resolve()==pointer
    assert before=={p.name:sha(p) for p in (tmp_path/'tables').glob('*.parquet')}

def test_validation_failure_does_not_select_candidate(tmp_path):
    db=minimal(tmp_path);export(db,tmp_path/'tables');old=(tmp_path/'tables').resolve()
    def fail(p):raise RuntimeError('final check failed')
    with pytest.raises(RuntimeError):export(db,tmp_path/'tables',validator=fail)
    assert (tmp_path/'tables').resolve()==old

def test_deferred_intermediate_export_leaves_current_untouched(tmp_path):
    from secfragility.publication import defer
    db=minimal(tmp_path);export(db,tmp_path/'tables');old=(tmp_path/'tables').resolve()
    with defer(tmp_path):export(db,tmp_path/'tables')
    assert (tmp_path/'tables').resolve()==old

def test_existing_directory_migrates_as_one_generation(tmp_path):
    db=minimal(tmp_path);old=tmp_path/'tables';old.mkdir();(old/'legacy.txt').write_text('preserved')
    export(db,old)
    assert old.is_symlink() and (tmp_path/'current.json').exists()
    assert any((p/'legacy.txt').exists() for p in (tmp_path/'work/table_generations').glob('legacy-*'))

def test_final_check_rejects_unconfirmed_and_dimensioned_ratio(tmp_path):
    from secfragility.verify_delivery import final,normalize_dimensions
    db=minimal(tmp_path)
    for name,state in [('a','confirmed'),('b','pending')]:
        insert(db,'entities',dict(entity_id=name,membership_id=name,legal_name=name,normalized_name=name,entity_status=state,consolidation_treatment='undetermined',as_of='2026-01-01T00:00:00Z'))
    insert(db,'links',dict(link_id='loan',edge_kind='amount',family='financing',type='loan_or_facility',from_entity_id='a',to_entity_id='b',amount=100,
                          period_end='2025-12-31',tier='B',counterparty_evidence='named',stage='recognized',as_of='2026-01-01T00:00:00Z'))
    with pytest.raises(RuntimeError,match='no_pending_amount_edges'):final(db,'2026-01-01T00:00:00Z')
    db.execute("UPDATE entities SET entity_status='confirmed'")
    insert(db,'measures',dict(measure='capex_to_cfo',group_id='S',view='revised',term='without',as_of='2026-01-01T00:00:00Z',unit='ratio',currency='USD',status='not_determinable',nd_reason='not_disclosed',coverage_state='not_disclosed'))
    assert normalize_dimensions(db)==1
    assert final(db,'2026-01-01T00:00:00Z')['checks']['no_pending_amount_edges']

def test_sql_extension_paths_are_resolved_from_explicit_root(tmp_path,monkeypatch):
    from secfragility.database import load_queries
    (tmp_path/'queries.sql').write_text("CREATE VIEW core AS SELECT 1 n;\n-- SoftBank official-source extension:\nCREATE VIEW extra AS SELECT * FROM read_parquet('data.parquet');")
    db=connect();db.execute("COPY (SELECT 2 n) TO '"+str(tmp_path/'data.parquet')+"' (FORMAT PARQUET)")
    monkeypatch.chdir(tmp_path.parent);load_queries(db,tmp_path)
    assert db.execute('SELECT n FROM extra').fetchone()[0]==2

def test_current_snapshot_has_no_pending_amounts_or_ratio_currency():
    db=connect()
    pending=db.execute("SELECT count(*) FROM read_parquet(?) l WHERE edge_kind='amount' AND (NOT EXISTS (SELECT 1 FROM read_parquet(?) e WHERE e.entity_id=l.from_entity_id AND e.entity_status='confirmed') OR NOT EXISTS (SELECT 1 FROM read_parquet(?) e WHERE e.entity_id=l.to_entity_id AND e.entity_status='confirmed'))",
                      [str(ROOT/'tables/links.parquet'),str(ROOT/'tables/entities.parquet'),str(ROOT/'tables/entities.parquet')]).fetchone()[0]
    assert pending==0
    assert db.execute("SELECT count(*) FROM read_parquet(?) WHERE unit='ratio' AND currency IS NOT NULL",[str(ROOT/'tables/measures.parquet')]).fetchone()[0]==0

def test_stale_test_attestation_rejected_after_code_change(tmp_path):
    from secfragility.attestation import fingerprint,require
    db=minimal(tmp_path);export(db,tmp_path/'tables')
    (tmp_path/'secfragility').mkdir();code=tmp_path/'secfragility/calculation.py';code.write_text('value=1\n')
    directory=tmp_path/'work/audit_20261012';directory.mkdir()
    p=directory/'test_attestation.json';p.write_text(json.dumps({'fingerprint':fingerprint(tmp_path),'runs':[dict(returncode=0,failed=0,errors=0)]}))
    require(tmp_path);code.write_text('value=2\n')
    with pytest.raises(ValueError,match='changed'):require(tmp_path)
