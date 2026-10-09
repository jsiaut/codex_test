"""Persist explicitly chosen conflicts after personal full reading, without meaning selection."""
from pathlib import Path
from datetime import datetime, timezone
import json
def record(decision,key,accession,choices,description):
    p=Path('work/fact_semantic_quarantines.json');rows=json.loads(p.read_text())
    for fid,quantity,reason in choices:
        if any(r['fact_id']==fid for r in rows):raise ValueError('Already quarantined: '+fid)
        rows.append(dict(fact_id=fid,content_key=key,accession=accession,affected_quantity=quantity,reason=reason,decision=decision,status='exclude_dependent_numeric_attribution_keep_raw_fact'))
    p.write_text(json.dumps(rows,indent=2)+'\n')
    with Path('decisions.md').open('a') as f:f.write('\n'+decision+' — '+description+'\n')
    with Path('journal.jsonl').open('a') as f:f.write(json.dumps(dict(as_of=json.loads(Path('work/run.json').read_text())['as_of'],timestamp=datetime.now(timezone.utc).isoformat(),event='semantic_quarantine_added',decision=decision,added=len(choices),final_delivery=False))+'\n')
