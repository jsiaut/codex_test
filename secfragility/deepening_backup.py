"""Supplement the original LFS cache with the targeted source bytes and blocks."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,tarfile,subprocess
import zstandard


def source_paths(root):
    paths={r['path'] for r in json.loads((root/'work/queue.json').read_text())}
    for f in json.loads((root/'work/deepening_filings.json').read_text()).values():
        paths.update(r['path'] for r in f['resources'].values())
        d=f['discovery']
        base=Path('cache/archives')/str(int(d['cik']))/d['accession'].replace('-','')
        paths.update(str(base/(n+'.zst')) for n in ['index.json',d['accession']+'-index-headers.html']+d['xbrl_archives'])
    for url,r in json.loads((root/'work/deepening_contract_sources.json').read_text()).items():
        paths.add(r['resource']['path']);m=r['metadata']
        # The physical exhibit rank comes from the original SEC header page.
        base=Path('cache/archives')/str(int(m['cik']))/m['accessionNumber'].replace('-','')
        paths.update(str(base/(n+'.zst')) for n in ['index.json',m['accessionNumber']+'-index-headers.html'])
    for r in json.loads((root/'work/deepening_form_d_filings.json').read_text()).values():paths.update([r['path'],r['header_path']])
    paths.update(r['source_path'] for r in json.loads((root/'work/deepening_issuer_metadata.json').read_text()).values())
    paths.update(['work/deepening_data/formd.pdf','work/deepening_data/formd.txt'])
    missing=[p for p in sorted(paths) if not (root/p).is_file()]
    assert not missing, ('Missing supplemental source bytes',missing)
    return paths


def snapshot(root):
    paths=source_paths(root)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    archive=root/'backup'/('sec-project-2-deepening-'+stamp+'.tar.zst')
    inventory={p:hashlib.file_digest((root/p).open('rb'),'sha256').hexdigest() for p in sorted(paths)}
    with archive.open('wb') as raw:
        with zstandard.ZstdCompressor(level=6,threads=2).stream_writer(raw) as compressed:
            with tarfile.open(fileobj=compressed,mode='w|') as tar:
                for p in sorted(paths):tar.add(root/p,arcname=p,recursive=False)
    sha=hashlib.file_digest(archive.open('rb'),'sha256').hexdigest()
    archive.with_suffix(archive.suffix+'.sha256').write_text(sha+'  '+archive.name+'\n')
    manifest=dict(archive=archive.name,sha256=sha,bytes=archive.stat().st_size,
        source_as_of=json.loads((root/'work/run.json').read_text())['as_of'],
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        purpose='Targeted original source bytes and every queued reading block; supplement to initial cache, not a replacement of current observations or code.',
        omitted_discovery_scan_archives=True,files=inventory)
    archive.with_suffix(archive.suffix+'.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k!='files'}),flush=True)
    return archive


if __name__=='__main__':snapshot(Path('.').resolve())
