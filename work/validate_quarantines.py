"""Check the raw and eligible rows for every explicitly authored quarantine."""
from pathlib import Path
import json
from secfragility.database import create

def validate(root):
    db=create(root)
    db.execute('INSERT INTO facts BY NAME SELECT * FROM read_parquet(?)',[str(root/'tables/facts.parquet')])
    db.execute((root/'queries.sql').read_text())
    missing=[row[0] for row in db.execute('SELECT q.fact_id FROM semantic_fact_quarantines q LEFT JOIN facts f USING(fact_id) WHERE f.fact_id IS NULL').fetchall()]
    rows,nonnull=db.execute('SELECT count(*),count(*) FILTER(WHERE e.value IS NOT NULL) FROM eligible_facts e JOIN semantic_fact_quarantines q USING(fact_id)').fetchone()
    result=dict(quarantine_count=db.execute('SELECT count(*) FROM semantic_fact_quarantines').fetchone()[0],missing_fact_ids=missing,direct_eligible_rows=rows,unexpected_nonnull_values=nonnull,raw_fact_count=db.execute('SELECT count(*) FROM facts').fetchone()[0],final_delivery=False)
    (root/'work/semantic_quarantine_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    if missing or nonnull:raise RuntimeError('Semantic quarantine validation failed: '+str(result))
    return result

if __name__=='__main__':print(validate(Path('.').resolve()))
