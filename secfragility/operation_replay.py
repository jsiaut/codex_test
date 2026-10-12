"""Offline replay of the transaction extension, not the historical collection."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,os,shutil,subprocess,sys
from .database import connect,sql_literal,TABLES
from .operation_sources import BASE,read,save,sha,restore,prepare_native

def certify_encoding(root):
    root=Path(root).resolve();base=root/BASE;original=base/'baseline/facts.parquet'
    temporary=base/'portable_baseline.parquet';db=connect()
    try:
        db.execute('COPY (SELECT * FROM read_parquet('+sql_literal(str(original))+') ORDER BY fact_id) TO '+sql_literal(str(temporary))+' (FORMAT PARQUET)')
        difference=sum(db.execute('SELECT count(*) FROM (SELECT * FROM read_parquet(?) EXCEPT ALL SELECT * FROM read_parquet(?))',[str(a),str(b)]).fetchone()[0]
            for a,b in ((original,temporary),(temporary,original)))
        if difference:raise ValueError('Portable baseline changes logical rows')
        selected=read(base/'selected_native_facts.json');existing={r[0] for r in db.execute('SELECT fact_id FROM read_parquet(?)',[str(original)]).fetchall()}
        added=sorted(f['fact_id'] for f in selected if f['fact_id'] not in existing)
        proof=dict(original_sha256=sha(original),portable_sha256=sha(temporary),difference_rows=difference,
            baseline_rows=db.execute('SELECT count(*) FROM read_parquet(?)',[str(original)]).fetchone()[0],new_native_fact_ids=added,
            method='DuckDB pinned version; ORDER BY fact_id; EXCEPT ALL in both directions; only physical Parquet encoding differs')
        save(base/'baseline_encoding_proof.json',proof);return proof
    finally:
        db.close();temporary.unlink(missing_ok=True)

def restore_baseline(root):
    root=Path(root).resolve();base=root/BASE;target=base/'baseline/facts.parquet'
    if target.exists():return
    proof=read(base/'baseline_encoding_proof.json');current=root/'tables/facts.parquet'
    manifest=read(root/'current.json')
    if sha(current)!=manifest['tables']['facts']['sha256']:raise ValueError('Current facts differ from published manifest')
    excluded=','.join(sql_literal(x) for x in proof['new_native_fact_ids']);target.parent.mkdir(parents=True,exist_ok=True)
    db=connect()
    try:
        db.execute('COPY (SELECT * FROM read_parquet('+sql_literal(str(current))+') WHERE fact_id NOT IN ('+excluded+') ORDER BY fact_id) TO '+sql_literal(str(target))+' (FORMAT PARQUET)')
        if sha(target)!=proof['portable_sha256']:raise ValueError('Restored baseline encoding SHA differs')
    except Exception:
        target.unlink(missing_ok=True);raise
    finally:db.close()

def replay(root):
    root=Path(root).resolve();restore_baseline(root);restore(root);prepare_native(root)
    for module in ('work.dependencies.author_notes','work.dependencies.author_ledger'):
        subprocess.run([sys.executable,'-m',module],cwd=root,check=True)
    from .operation_dependencies import apply
    db,proof=apply(root);db.close();return proof

def isolated(root):
    root=Path(root).resolve();scratch=root/BASE/'replay'
    if scratch.exists():raise ValueError('Replay directory exists; retain it for inspection or remove only this scratch directory')
    scratch.mkdir();base=root/BASE
    for name in ('secfragility','tests'):
        shutil.copytree(root/name,scratch/name,ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('schema.sql','queries.sql','operation_views.sql','config.yaml','requirements.txt'):
        shutil.copy2(root/name,scratch/name)
    for name in ('audit/criteria_manifest.json','work/run.json'):
        p=scratch/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,p)
    target=scratch/BASE;target.mkdir(parents=True,exist_ok=True)
    for p in base.iterdir():
        if p.is_file() and p.suffix in ('.json','.py','.zst') and p.name not in ('delivery_archive.json','replay_verification.json'):
            shutil.copy2(p,target/p.name)
    (target/'baseline').mkdir()
    for t in TABLES:
        if t!='facts':os.link(base/'baseline'/(t+'.parquet'),target/'baseline'/(t+'.parquet'))
    (scratch/'tables').mkdir()
    for t in TABLES:os.link(root/'tables'/(t+'.parquet'),scratch/'tables'/(t+'.parquet'))
    shutil.copy2(root/'current.json',scratch/'current.json')
    command=[sys.executable,'-m','secfragility.operation_replay','replay']
    result=subprocess.run(command,cwd=scratch,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (base/'replay.log').write_text(result.stdout)
    if result.returncode:raise RuntimeError('Isolated replay failed: see work/dependencies/replay.log')
    checks={t:dict(root_sha256=sha(root/'tables'/(t+'.parquet')),replay_sha256=sha(scratch/'tables'/(t+'.parquet')))
        for t in TABLES}
    for v in checks.values():v['byte_identical']=v['root_sha256']==v['replay_sha256']
    if not all(v['byte_identical'] for v in checks.values()):raise ValueError('Isolated tables differ')
    authored={n:sha(base/n)==sha(target/n) for n in ('authored_observations.json','selected_native_facts.json','entity_decisions.json','edge_decisions.json','measure_decisions.json','derived_decisions.json','operations.json')}
    if not all(authored.values()):raise ValueError('Regenerated authored selections differ')
    tests=subprocess.run([sys.executable,'-m','pytest','-q','tests/test_operation_dependencies.py'],cwd=scratch,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (base/'isolated_tests.log').write_text(tests.stdout)
    if tests.returncode:raise RuntimeError('Isolated extension tests failed')
    proof=dict(verified_at=datetime.now(timezone.utc).isoformat(),method='Fresh isolated directory; restored original archive; native parsing and authored selection regeneration; prior baseline restored from current facts minus eight explicit additions.',
        all_eight_tables_byte_identical=True,tables=checks,authored_selections_identical=authored,isolated_test_returncode=tests.returncode,
        source_cutoff=read(base/'scope.json')['source_cutoff'],full_historical_reconstruction=False,subagents_used=False)
    save(base/'replay_verification.json',proof)
    shutil.rmtree(scratch)
    return proof

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=('certify','replay','isolated'));a=p.parse_args()
    {'certify':certify_encoding,'replay':replay,'isolated':isolated}[a.action](Path('.'))
