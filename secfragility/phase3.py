"""Deterministic offline assembly after the reading queue has been exhausted."""
from pathlib import Path
import argparse,json
import faulthandler
from .database import create,export,table_counts
from .calculation import core_calibration
from .assembly import load


def run(root,reconstruct=False,resume=False):
    faulthandler.enable()
    state=json.loads((root/'work/run.json').read_text());as_of=state['as_of']
    queue=json.loads((root/'work/queue.json').read_text())
    assert all((root/'work/observations'/(r['content_key']+'.jsonl')).exists() for r in queue),'Phase2 queue not empty'
    state.update(phase='phase3',status='assembling');(root/'work/run.json').write_text(json.dumps(state,indent=2)+'\n')
    if resume:
        from .assembly_checkpoint import resume as restore
        db=restore(root,as_of);db.execute('BEGIN TRANSACTION')
        return finish(db,root,as_of,state)
    if reconstruct:
        from .rebuild import rebuild
        db=rebuild(root)
    else:
        path=root/'work/phase3.duckdb'
        if path.exists():path.unlink()
        wal=root/'work/phase3.duckdb.wal'
        if wal.exists():wal.unlink()
        db=create(root,path)
        for t in ['documents','facts']:
            where=" WHERE document_kind IS DISTINCT FROM 'submission_metadata'" if t=='documents' else ''
            db.execute(f"INSERT INTO {t} BY NAME SELECT * FROM read_parquet('tables/{t}.parquet'){where}")
    db.execute('BEGIN TRANSACTION')
    collection=json.loads((root/'work/collection.json').read_text())
    from .mapping import refresh
    refresh(db,root,collection)
    core_calibration(db,root,as_of)
    load(db,root,as_of)
    print(json.dumps(dict(stage='observations',counts=table_counts(db))),flush=True)
    from .entities import assemble as assemble_entities
    entities,observations,resolve=assemble_entities(db,root,as_of)
    print(json.dumps(dict(stage='entities',count=len(entities))),flush=True)
    from .graph import assemble,nonadditive
    assemble(db,root,as_of,entities,observations,resolve)
    print(json.dumps(dict(stage='amount_links',counts=table_counts(db))),flush=True)
    nonadditive(db,root,as_of)
    print(json.dumps(dict(stage='graph',counts=table_counts(db))),flush=True)
    from .controls import component_controls,concentration_controls,lease_controls,eps_controls
    from .controls_extended import run as extended_controls
    component_controls(db,root,collection,as_of);concentration_controls(db,as_of)
    lease_controls(db,as_of);eps_controls(db,as_of,'0.10');extended_controls(db,root,collection,as_of)
    print(json.dumps(dict(stage='controls',counts=table_counts(db))),flush=True)
    from .quarter_series import prepare,measures
    prepare(db,root,as_of);measures(db,as_of)
    print(json.dumps(dict(stage='quarters',counts=table_counts(db))),flush=True)
    from .tier1_numeric import stocks,tagged_components,liquidity_and_leases
    stocks(db,as_of);tagged_components(db,as_of)
    print(json.dumps(dict(stage='stocks',counts=table_counts(db))),flush=True)
    from .ttm import run as ttm
    ttm(db,as_of)
    print(json.dumps(dict(stage='ttm',counts=table_counts(db))),flush=True)
    liquidity_and_leases(db,as_of)
    from .numeric_extended import run as numeric
    numeric(db,as_of)
    from .metadata_signals import run as signals
    signals(db,root,as_of)
    db.execute('UPDATE measures SET information_cutoff=as_of,as_of=?',[as_of])
    from .bilateral import run as bilateral
    bilateral(db,as_of)
    from .pairs import run as pairs
    pairs(db,root,as_of,entities,observations,resolve)
    print(json.dumps(dict(stage='pairs',counts=table_counts(db))),flush=True)
    from .assembly_checkpoint import save
    save(db,root,as_of)
    return finish(db,root,as_of,state)


def finish(db,root,as_of,state):
    from .events import run as events
    events(db,root,as_of)
    from .evaluation import run as evaluation
    evaluation(db,root,as_of)
    from .coverage import run as coverage
    coverage(db,root,as_of)
    print(json.dumps(dict(stage='coverage',counts=table_counts(db))),flush=True)
    from .enrichment import run as enrichment
    enrichment(db,as_of)
    for g,data in json.loads((root/'work/inventory.json').read_text())['groups'].items():
        db.execute("DELETE FROM measures WHERE group_id=? AND period_end!='none' AND period_end<?",[g,data['analysis_start']])
    from .universe import DEPENDENCIES
    import yaml
    rank1=set(yaml.safe_load((root/'config.yaml').read_text())['tier1'])|DEPENDENCIES
    db.execute('UPDATE measures SET tier=2 WHERE measure::VARCHAR NOT IN ('+','.join("'"+x+"'" for x in sorted(rank1))+')')
    from .verify_delivery import run as verify
    source,verification=verify(db,root,as_of)
    db.execute('COMMIT')
    from .reports import render,package
    render(db,root,as_of,source,verification)
    package(root,as_of)
    state.update(phase='phase3',status='validated_ready_for_final_commit')
    (root/'work/run.json').write_text(json.dumps(state,indent=2)+'\n')
    export(db,root/'work/phase3_tables')
    print(json.dumps(dict(stage='numeric',counts=table_counts(db))),flush=True)
    return db


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reconstruct',action='store_true');p.add_argument('--resume',action='store_true');a=p.parse_args()
    run(Path('.').resolve(),a.reconstruct,a.resume)
