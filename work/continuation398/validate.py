"""Verify this completed tranche against its newly reconstructed delivery."""
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import csv,json,re,subprocess
import duckdb
from secfragility.continuation_reports import verify_scope
from secfragility.database import TABLES

root=Path('.').resolve();base=root/'work/continuation398'
frozen,reviews,scope=verify_scope(root)
summary=json.loads((root/'continuation398_summary.json').read_text())
assert summary['completed_blocks']==398 and summary['remaining_blocks']==0
ledger=list(csv.DictReader((root/'revue_398_blocs.csv').open()))
assert len(ledger)==398 and {int(x['index']) for x in ledger}==set(range(398))
assert len({x['content_key'] for x in ledger})==398
coverage=list(csv.DictReader((root/'expansion_note_coverage.csv').open()))
assert {x['state'] for x in coverage}=={'read'}
assert len({x['content_key'] for x in coverage})==465
ids=[i for x in ledger for i in json.loads(x['observation_ids'])]
assert len(ids)==len(set(ids))==sum(x['accepted_observations'] for x in reviews)==409
db=duckdb.connect()
counts={t:db.execute(f"SELECT count(*) FROM read_parquet('tables/{t}.parquet')").fetchone()[0] for t in TABLES}
actual={x[0] for x in db.execute("SELECT observation_id FROM read_parquet('tables/observations.parquet') WHERE content_key IN (SELECT unnest(?))",[[x['content_key'] for x in ledger]]).fetchall()}
assert actual==set(ids)
assert db.execute("SELECT count(*) FROM read_parquet('tables/exclusions.parquet') WHERE reason='not_processed' AND COALESCE(content_key,element_id) IN (SELECT unnest(?))",[[x['content_key'] for x in ledger]]).fetchone()[0]==0
db.close()
verification=json.loads((root/'work/delivery_verification.json').read_text())
replay=json.loads((root/'work/idempotency_verification.json').read_text())
assert all(verification['checks'].values()) and verification['missing_expected_cells']==0
assert replay['input_manifest_unchanged'] and replay['all_tables_identical']
assert set(replay['tables'])==set(TABLES)
assert {t:r['rows'] for t,r in replay['tables'].items()}==counts
assert all(r['original_only']==r['replay_only']==0 for r in replay['tables'].values())
assert replay['verified_at']>max(r['reviewed_at'] for r in reviews)
testlog=(base/'tests.log').read_text();m=re.search(r'(\d+) passed in ',testlog)
assert m and int(m[1])==105 and 'failed' not in testlog.lower()
criteria=subprocess.check_output(['git','show','f015631733a8cf5ae4009ac5b07c905884a9f121:audit/criteria_manifest.json'],cwd=root)
assert criteria==(root/'audit/criteria_manifest.json').read_bytes()
assert replay['as_of']==summary['source_cutoff']=='2026-10-09T10:24:21.129672+00:00'
integrity=json.loads((base/'source_integrity.json').read_text())
assert integrity['verified_files']==9123 and not integrity['changed_files']
report=dict(source_cutoff=summary['source_cutoff'],verified_at=datetime.now(timezone.utc).isoformat(),
    requested_blocks=398,read_blocks=398,deferred_blocks=0,all_nominated_notes_read=465,
    accepted_continuation_observations=409,all_reviews_present_in_eight_tables=True,
    full_text_parts_verified=True,sole_executor=True,subagents_used=False,tests_passed=int(m[1]),
    delivery_checks=verification['checks'],full_offline_replay_all_eight_tables_identical=True,
    reproduction_inputs_unchanged=True,criteria_manifest_unchanged=True,table_counts=counts,
    frozen_source_snapshot_verified_files=integrity['verified_files'],
    accounting_mismatch_rows=sum(x['n'] for x in verification['accounting_mismatches']),
    localized_invalid_aggregates=len(verification['localized_invalid_aggregates']),
    historical_notes_complete=False,complete_contract_review=False,independent_audit_performed=False)
(base/'validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False))
