"""Durable intermediate commits, distinct from the final execution delivery."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import subprocess


def command(root, *args):
    return subprocess.run(args, cwd=root, check=True, text=True, capture_output=True)


def progress(root: Path):
    queue = json.loads((root / 'work/queue.json').read_text())
    keys = {r['content_key'] for r in queue}
    completed = {k for k in keys if (root / 'work/observations' / (k + '.jsonl')).exists()}
    observations = 0
    rejected = Counter()
    for key in completed:
        for line in (root / 'work/observations' / (key + '.jsonl')).read_text().splitlines():
            observations += json.loads(line)['record_kind'] == 'observation'
        reject_file = root / 'work/observations' / (key + '.rejected.jsonl')
        if reject_file.exists():
            rejected.update(json.loads(line)['phase'] for line in reject_file.read_text().splitlines())
    return {
        'as_of': json.loads((root / 'work/run.json').read_text())['as_of'],
        'active_unique_keys': len(keys), 'completed_unique_keys': len(completed),
        'remaining_unique_keys': len(keys - completed), 'accepted_observations': observations,
        'completed_occurrences_by_class': dict(Counter(r['block_class'] for r in queue if r['content_key'] in completed)),
        'validation_rejected_attempts_by_phase': dict(rejected),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'read_packet_logging_started_2026_10_09': True,
        'independent_audit_performed': False,
    }


def checkpoint(root: Path, *, force=False):
    settings_path = root / 'work/github_backup.json'
    if not settings_path.exists() and not force:
        return None
    settings = json.loads(settings_path.read_text()) if settings_path.exists() else {}
    state_path = root / 'work/checkpoint_state.json'
    previous = json.loads(state_path.read_text()) if state_path.exists() else {}
    state = progress(root)
    elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(previous['saved_at'])).total_seconds() if previous else float('inf')
    if not force and state['completed_unique_keys'] - previous.get('completed_unique_keys', 0) < 10 and elapsed < 600:
        return None
    (root / 'work/reading_progress.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    with (root / 'journal.jsonl').open('a') as f:
        f.write(json.dumps(dict(as_of=state['as_of'], timestamp=state['updated_at'],
            event='intermediate_checkpoint', completed_unique_keys=state['completed_unique_keys'],
            remaining_unique_keys=state['remaining_unique_keys'], final_delivery=False)) + '\n')
    command(root, 'git', 'add', '-A')
    staged = subprocess.run(
        ['git', 'diff', '--cached', '--quiet'], cwd=root, capture_output=True)
    if staged.returncode == 1:
        phase=json.loads((root/'work/run.json').read_text())['phase']
        command(root, 'git', 'commit', '-m', f"Checkpoint: {state['completed_unique_keys']} blocks read; {phase} in progress")
    elif staged.returncode != 0:
        raise RuntimeError(staged.stderr.decode())
    commit = command(root, 'git', 'rev-parse', 'HEAD').stdout.strip()
    # A failure leaves the local commit intact and is reported to the driver.
    if settings.get('enabled'):
        pushed = command(root, 'git', 'push', 'origin', settings['branch'])
        print(pushed.stderr.strip())
    saved = dict(saved_at=state['updated_at'], completed_unique_keys=state['completed_unique_keys'], commit=commit)
    state_path.write_text(json.dumps(saved, indent=2) + '\n')
    return saved


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--force', action='store_true')
    a = p.parse_args()
    print(json.dumps(checkpoint(Path('.').resolve(), force=a.force)))
