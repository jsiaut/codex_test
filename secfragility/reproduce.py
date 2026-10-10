"""Compare two offline deliveries, including exact decimals and provenance."""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import shutil
import duckdb
from .database import TABLES, sql_literal


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def capture(root):
    reference = root / 'work/replay_reference'
    reference.mkdir(exist_ok=True)
    for table in TABLES:
        shutil.copy2(root / 'tables' / (table + '.parquet'), reference / (table + '.parquet'))
    path=root/'work/reproduction_inputs.json'
    names=set(json.loads(path.read_text())) if path.exists() else set()
    names.update(str(p.relative_to(root)) for p in (root/'secfragility').rglob('*.py'))
    names.update(str(p.relative_to(root)) for p in (root/'tests').glob('*.py'))
    names.update(str(p.relative_to(root)) for p in (root/'work/observations').glob('*.jsonl'))
    names.update('work/'+name for name in ['extension_authorization.json','extension_attribution_reviews.json',
        'extension_html_bounds.json','extension_exclusions.json','queue.json','expected_universe.json',
        'inventory.json','collection.json','annual_cutoffs.json'])
    names.update(['config.yaml','schema.sql','queries.sql','requirements.txt'])
    path.write_text(json.dumps({name:sha256(root/name) for name in sorted(names) if (root/name).is_file()},indent=2)+'\n')
    return {'captured_tables': list(TABLES)}


def compare(root):
    db = duckdb.connect()
    db.execute("SET memory_limit='4GB'")
    db.execute('SET threads=2')
    spill = root / 'work/replay_spill'
    spill.mkdir(exist_ok=True)
    db.execute('SET temp_directory=' + sql_literal(str(spill)))

    def source_bag(value):
        # These two columns are unordered source-ID lists. Preserve duplicates.
        parsed = json.loads(value)
        if not isinstance(parsed, list):
            raise ValueError('Expected an array of source IDs')
        return json.dumps(sorted(parsed, key=lambda x: json.dumps(x, sort_keys=True)), separators=(',', ':'))

    db.create_function('source_bag', source_bag, ['VARCHAR'], 'VARCHAR')
    results = {}
    for table in TABLES:
        a = root / 'work/replay_reference' / (table + '.parquet')
        b = root / 'tables' / (table + '.parquet')
        db.execute('CREATE OR REPLACE VIEW original AS SELECT * FROM read_parquet(' + sql_literal(str(a)) + ')')
        db.execute('CREATE OR REPLACE VIEW replay AS SELECT * FROM read_parquet(' + sql_literal(str(b)) + ')')
        columns = [r[0] for r in db.execute('DESCRIBE original').fetchall()]
        assert columns == [r[0] for r in db.execute('DESCRIBE replay').fetchall()], table
        fields = ','.join('source_bag("' + c + '") AS "' + c + '"' if c in ('lineage', 'evidence') else '"' + c + '"' for c in columns)
        forward = db.execute(f'SELECT count(*) FROM (SELECT {fields} FROM original EXCEPT ALL SELECT {fields} FROM replay)').fetchone()[0]
        backward = db.execute(f'SELECT count(*) FROM (SELECT {fields} FROM replay EXCEPT ALL SELECT {fields} FROM original)').fetchone()[0]
        results[table] = dict(rows=db.execute('SELECT count(*) FROM replay').fetchone()[0],
            original_only=forward, replay_only=backward, identical=forward == backward == 0,
            original_sha256=sha256(a), replay_sha256=sha256(b))
    manifest = json.loads((root / 'work/reproduction_inputs.json').read_text())
    input_changes = [name for name, expected in manifest.items() if not (root / name).exists() or sha256(root / name) != expected]
    report = dict(as_of=json.loads((root / 'work/run.json').read_text())['as_of'],
        verified_at=datetime.now(timezone.utc).isoformat(),
        method='Offline full-cache reconstruction; bidirectional EXCEPT ALL across every column; source-ID lists compared as multisets.',
        input_manifest_unchanged=not input_changes, changed_inputs=input_changes, tables=results,
        all_tables_identical=all(r['identical'] for r in results.values()), independent_audit_performed=False)
    (root / 'work/idempotency_verification.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['all_tables_identical'] and report['input_manifest_unchanged'], 'Offline replay differs; inspect work/idempotency_verification.json'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['capture', 'compare'])
    args = parser.parse_args()
    print(json.dumps((capture if args.action == 'capture' else compare)(Path('.').resolve())))
