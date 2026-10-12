"""Find historical source bytes by SHA, without refreshing a SEC snapshot."""
from pathlib import Path
import argparse,hashlib,json,tarfile,zstandard
from .database import connect

def raw_bytes(path):
    raw=Path(path).read_bytes()
    return zstandard.ZstdDecompressor().decompress(raw) if str(path).endswith('.zst') else raw

def metadata(root,path):
    manifest=root/'work/audit_20261012/submission_metadata_manifest.json'
    if not manifest.exists():return raw_bytes(root/path)
    m=json.loads(manifest.read_text());entry=next((e for e in m['entries'] if e['cache_path']==path),None)
    if entry is None:raise ValueError('Historical submissions response not registered: '+path)
    p=root/path
    if not p.exists():
        archive=root/m['archive']
        with archive.open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=m['sha256']:raise ValueError('Metadata archive SHA differs')
        with archive.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z,tarfile.open(fileobj=z,mode='r|') as t:
            for member in t:
                if member.name==path:
                    compressed=t.extractfile(member).read()
                    if hashlib.sha256(compressed).hexdigest()!=entry['compressed_sha256']:raise ValueError('Archived response differs')
                    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(compressed);break
    raw=raw_bytes(p)
    if hashlib.sha256(raw).hexdigest()!=entry['raw_sha256']:raise ValueError('Historical submissions SHA differs; no current response substituted')
    return raw

def resolve(root,path):
    """Materialize an archived equivalent only after verifying its old SHA."""
    root=Path(root).resolve();p=Path(path);p=p if p.is_absolute() else root/p
    index=root/'work/audit_20261012/source_preflight.json'
    if not index.exists():
        if p.exists():return p
        raise FileNotFoundError(p)
    data=json.loads(index.read_text());relative=str(p.relative_to(root))
    entry=next((e for e in data['entries'] if e['expected_path']==relative),None)
    if entry is None:
        if p.exists():return p
        raise FileNotFoundError('Source not registered: '+relative)
    if p.exists():
        if hashlib.sha256(raw_bytes(p)).hexdigest()!=entry['sha256']:raise ValueError('Existing source differs from historical SHA')
        return p
    location=entry['location']
    if not location:raise FileNotFoundError('Historical source absent: '+relative)
    if location['kind']=='file':raw=raw_bytes(root/location['path'])
    else:
        archive=root/location['archive'];expected=next(a['sha256'] for a in data['archives'] if a['path']==location['archive'])
        with archive.open('rb') as f:
            if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise ValueError('Source archive changed')
        raw=None
        with archive.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z,tarfile.open(fileobj=z,mode='r|') as t:
            for member in t:
                if member.name==location['member']:
                    raw=t.extractfile(member).read()
                    if member.name.endswith('.zst'):raw=zstandard.ZstdDecompressor().decompress(raw)
                    break
        if raw is None:raise FileNotFoundError('Archived source member absent')
    if hashlib.sha256(raw).hexdigest()!=entry['sha256']:raise ValueError('Equivalent source SHA differs')
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_bytes(zstandard.ZstdCompressor().compress(raw) if str(p).endswith('.zst') else raw)
    return p

def preflight(root):
    root=Path(root).resolve();db=connect()
    rows=db.execute('SELECT document_id,url,cache_path,sha256 FROM read_parquet(?)',[str((root/'tables').resolve()/'documents.parquet')]).fetchall();db.close()
    remaining={sha:[] for _,_,_,sha in rows};locations={};wrong=[]
    for did,url,path,sha in rows:remaining[sha].append((did,url,path))
    for did,url,path,expected in rows:
        p=root/path
        if p.is_file():
            try:actual=hashlib.sha256(raw_bytes(p)).hexdigest()
            except zstandard.ZstdError:actual=None
            if actual==expected:locations[expected]=dict(kind='file',path=path)
            else:wrong.append(dict(document_id=did,path=path))
    print(json.dumps({'stage':'local_sources','matched_hashes':len(locations),'remaining_hashes':len(set(remaining)-set(locations))}),flush=True)
    archives=sorted((root/'backup').glob('*.tar.zst'))+[root/p for p in ('work/dell/SEC_Dell_originals.tar.zst','work/smci/SEC_SMCI_originals.tar.zst','work/priorities/originals.tar.zst','work/audit_20261012/submission_metadata.tar.zst')]
    manifest=[]
    for archive in archives:
        if not archive.is_file():continue
        with archive.open('rb') as f:archive_sha=hashlib.file_digest(f,'sha256').hexdigest()
        manifest.append(dict(path=str(archive.relative_to(root)),sha256=archive_sha))
        with archive.open('rb') as f,zstandard.ZstdDecompressor().stream_reader(f) as z,tarfile.open(fileobj=z,mode='r|') as t:
            for member in t:
                if not member.isfile() or Path(member.name).suffix in ('.parquet','.py','.csv','.zip','.md'):continue
                stream=t.extractfile(member)
                if member.name.endswith('.zst'):
                    try:
                        with zstandard.ZstdDecompressor().stream_reader(stream,closefd=False) as decoded:actual=hashlib.file_digest(decoded,'sha256').hexdigest()
                    except zstandard.ZstdError:continue
                else:actual=hashlib.file_digest(stream,'sha256').hexdigest()
                if actual in remaining and actual not in locations:locations[actual]=dict(kind='tar_zst',archive=str(archive.relative_to(root)),member=member.name)
        print(json.dumps({'stage':'archive_sources','archive':archive.name,'matched_hashes':len(locations)}),flush=True)
    entries=[dict(document_id=did,url=url,expected_path=path,sha256=sha,location=locations.get(sha)) for did,url,path,sha in rows]
    result=dict(documents=len(rows),verified=sum(e['location'] is not None for e in entries),missing=[e for e in entries if e['location'] is None],
        direct_path_mismatches=wrong,source_cutoff='2026-10-09T10:24:21.129672+00:00',fresh_SEC_requests=0,archives=manifest,entries=entries)
    out=root/'work/audit_20261012/source_preflight.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('.'));a=p.parse_args();r=preflight(a.root)
    print(json.dumps({k:r[k] for k in ('documents','verified','missing')}))
    if r['missing']:raise SystemExit(1)
