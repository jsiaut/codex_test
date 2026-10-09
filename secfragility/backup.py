"""Snapshot cached SEC responses and restart files outside versioned Git data."""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import tarfile
import zstandard


def snapshot(root: Path, destination: Path):
    destination.mkdir(parents=True, exist_ok=True)
    commit = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, check=True, capture_output=True, text=True).stdout.strip()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archive = destination / f'sec-project-2-{stamp}.tar.zst'
    skip_parts = {'.git', '.venv', '__pycache__', '.pytest_cache'}
    skip_paths = {'work/session.lock', 'work/foreground_owner.json', 'work/checkpoint_state.json'}
    def selected(info):
        name = info.name.removeprefix('./')
        if any(p in skip_parts for p in Path(name).parts) or name in skip_paths:
            return None
        return info
    with archive.open('wb') as raw:
        with zstandard.ZstdCompressor(level=6, threads=2).stream_writer(raw) as compressed:
            with tarfile.open(fileobj=compressed, mode='w|') as tar:
                tar.add(root, arcname='.', filter=selected)
    digest = hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest()
    checksum = archive.with_suffix(archive.suffix + '.sha256')
    checksum.write_text(f'{digest}  {archive.name}\n')
    cached = sorted((root / 'cache').rglob('*.zst'))
    manifest = archive.with_suffix(archive.suffix + '.json')
    manifest.write_text(json.dumps(dict(source_commit=commit,
        as_of=json.loads((root / 'work/run.json').read_text())['as_of'],
        created_at=datetime.now(timezone.utc).isoformat(), archive=archive.name,
        archive_bytes=archive.stat().st_size, sha256=digest,
        cached_responses=len(cached), cached_response_bytes=sum(p.stat().st_size for p in cached),
        excludes=sorted(skip_parts | skip_paths),
        final_delivery=False, independent_audit_performed=False), indent=2) + '\n')
    return dict(archive=str(archive), checksum=str(checksum), manifest=str(manifest), source_commit=commit)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--destination', type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(snapshot(Path('.').resolve(), a.destination)))
