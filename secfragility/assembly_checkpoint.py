"""Offline calculation checkpoint; immutable inputs checked before resume."""
import json,hashlib
from .database import export,create,sql_literal,TABLES
from .calculation import prepare_views

AUX=['quarter_candidates','quarter_cutoffs','snapshot_stocks_as_known','snapshot_stocks_revised',
     'ttm_quantities_as_known','ttm_quantities_revised','excluded_observations']
INPUTS=['config.yaml','schema.sql','queries.sql','work/run.json','work/observation_quarantines.json',
        'work/fact_semantic_quarantines.json','work/exhibit_body_policy_overrides.json',
        'work/extension_authorization.json','work/extension_attribution_reviews.json',
        'work/expected_universe.json']


def inputs(root):
    files=[root/x for x in INPUTS if x!='work/run.json' and (root/x).exists()]
    files+=list((root/'work/observations').glob('*.jsonl'))
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}


def save(db,root,as_of):
    path=root/'work/assembly_checkpoint';export(db,path)
    for t in AUX:db.execute('COPY '+t+' TO '+sql_literal(str(path/(t+'.parquet')))+' (FORMAT PARQUET)')
    (path/'manifest.json').write_text(json.dumps(dict(as_of=as_of,inputs=inputs(root),final_delivery=False),indent=2)+'\n')


def resume(root,as_of):
    path=root/'work/assembly_checkpoint';manifest=json.loads((path/'manifest.json').read_text())
    if manifest['as_of']!=as_of or manifest['inputs']!=inputs(root):raise ValueError('Assembly checkpoint input mismatch; rebuild required')
    db=create(root)
    for t in TABLES:db.execute('INSERT INTO '+t+' BY NAME SELECT * FROM read_parquet('+sql_literal(str(path/(t+'.parquet')))+')')
    prepare_views(db,root,as_of)
    for t in AUX:db.execute('CREATE TEMP TABLE '+t+' AS SELECT * FROM read_parquet('+sql_literal(str(path/(t+'.parquet')))+')')
    from .extension_assembly import interpretations
    interpretations(db,root,as_of)
    db.execute('''CREATE VIEW usable_observations AS SELECT o.* FROM interpreted_observations o
      WHERE NOT abstained AND tier IN ('A','B','C','D') AND filing_status='filed'
       AND EXISTS (SELECT 1 FROM documents d WHERE d.document_id=o.document_id AND d.acceptance_datetime<=o.as_of)
       AND NOT EXISTS (SELECT 1 FROM excluded_observations q WHERE q.observation_id=o.observation_id)
       AND (tagged_fact_id IS NULL OR EXISTS (SELECT 1 FROM eligible_facts f WHERE f.fact_id=o.tagged_fact_id
        AND f.value IS NOT NULL AND f.coverage_state IN ('observed','explicit_zero')))''')
    return db
