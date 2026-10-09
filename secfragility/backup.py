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
        if name == 'backup' or name.startswith('backup/') or any(p in skip_parts for p in Path(name).parts) or name in skip_paths:
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


def restore(root: Path, archive: Path, manifest: Path):
    metadata = json.loads(manifest.read_text())
    with archive.open('rb') as f:
        actual = hashlib.file_digest(f, 'sha256').hexdigest()
    if actual != metadata['sha256']:
        raise ValueError('Archive SHA-256 differs from the saved manifest.')
    tracked = set(subprocess.run(['git', 'ls-files'], cwd=root, check=True,
        capture_output=True, text=True).stdout.splitlines())
    count = 0
    with archive.open('rb') as raw:
        with zstandard.ZstdDecompressor().stream_reader(raw) as decompressed:
            with tarfile.open(fileobj=decompressed, mode='r|') as tar:
                for member in tar:
                    name = member.name.removeprefix('./')
                    relative = Path(name)
                    if relative.is_absolute() or '..' in relative.parts:
                        raise ValueError('Unsafe archive member path.')
                    if name in tracked or name in ('work/session.lock', 'work/foreground_owner.json', 'work/checkpoint_state.json'):
                        continue
                    if not member.isfile():
                        if member.isdir():
                            (root / relative).mkdir(parents=True, exist_ok=True)
                            continue
                        raise ValueError('Non-regular member in restart archive.')
                    target = root / relative
                    # Preserve existing restart data; this command is for a fresh clone.
                    if target.exists():
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as source, target.open('wb') as output:
                        while chunk := source.read(1024 * 1024):
                            output.write(chunk)
                    count += 1
    return dict(restored_files=count, source_commit=metadata['source_commit'])


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--destination', type=Path)
    p.add_argument('--restore', type=Path)
    p.add_argument('--manifest', type=Path)
    a = p.parse_args()
    if a.restore:
        if not a.manifest:p.error('--restore requires --manifest')
        result=restore(Path('.').resolve(),a.restore,a.manifest)
    else:
        if not a.destination:p.error('--destination is required for a snapshot')
        result=snapshot(Path('.').resolve(),a.destination)
    print(json.dumps(result))
