"""One complete model archive, including original SEC and Japanese evidence."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil,subprocess,zipfile

OUTPUT=Path('output')

def run(root,output=None):
    output=Path(output) if output is not None else Path(root)/'output'
    output.mkdir(parents=True,exist_ok=True)
    replay=json.loads((root/'work/idempotency_verification.json').read_text())
    assert replay['all_tables_identical'] and replay['input_manifest_unchanged']
    validation=json.loads((root/'work/softbank/validation.json').read_text())
    assert all(validation['checks'].values())
    from .deepening_backup import source_paths
    original_sources=source_paths(root)
    target=output/'SEC_Project_2_SoftBank.zip';temporary=output/'SEC_Project_2_SoftBank.partial.zip'
    files=[]
    files.extend((root/'tables').glob('*.parquet'))
    for path in sorted(root.rglob('*')):
        rel=path.relative_to(root);parts=rel.parts
        if not path.is_file() or '__pycache__' in parts or '.git' in parts:continue
        include=parts[0] in ('audit','tables','secfragility','tests')
        include=include or len(parts)==1 and path.suffix in ('.md','.yaml','.sql','.csv','.json','.txt')
        include=include or parts[:2]==('work','observations')
        include=include or str(rel) in original_sources
        include=include or str(rel) in ['backup/sec-project-2-20261009T150746Z.tar.zst',
            'backup/sec-project-2-20261009T150746Z.tar.zst.json','backup/sec-project-2-20261009T150746Z.tar.zst.sha256']
        include=include or parts[0]=='work' and len(parts)==2 and path.suffix in ('.json','.py') and not path.name.endswith('_bulk.jsonl')
        include=include or parts[:2] in [('work','expansion'),('work','continuation398')] and path.suffix in ('.json','.py','.jsonl')
        include=include or parts[:2]==('work','softbank') and (
            path.suffix in ('.json','.csv','.py','.sql') or
            len(parts)>=3 and parts[2] in ('sources','text','baseline') or
            path.name in ('annual_audit_146.png','annual_audit_149.png'))
        if include and path.suffix!='.log':files.append((path,rel))
    manifest=dict(as_of=validation['as_of'],created_at=datetime.now(timezone.utc).isoformat(),
        archive=target.name,repository='https://github.com/jsiaut/codex_test',
        commit_before_packaging=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        files=len(files),all_tables_replayed_identically=True,legacy_SEC_records_preserved=True,
        subagents_used=False,independent_audit_performed=False)
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for path,rel in files:archive.write(path,str(rel))
    with zipfile.ZipFile(temporary) as archive:
        bad=archive.testzip()
        if bad:raise ValueError('CRC failure: '+bad)
        manifest['entries']=len(archive.infolist())
    with temporary.open('rb') as handle:manifest['sha256']=hashlib.file_digest(handle,'sha256').hexdigest()
    manifest['bytes']=temporary.stat().st_size;temporary.replace(target)
    (root/'work/softbank/delivery_archive.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    (output/'softbank_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    for name in ['softbank_integration.md','softbank_summary.json','softbank_measures.csv','softbank_evidence.csv',
        'softbank_controls.csv','softbank_links.csv','softbank_sources.csv','softbank_reading_coverage.csv',
        'softbank_events.csv','softbank_annex_e.csv','softbank_bond_register.csv']:
        shutil.copy2(root/name,output/name)
    shutil.copy2(root/'work/idempotency_verification.json',output/'softbank_idempotency.json')
    shutil.copy2(root/'work/softbank/validation.json',output/'softbank_validation.json')
    shutil.copy2(root/'audit/softbank_numbers.csv',output/'softbank_numbers.csv')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);a=p.parse_args()
    print(json.dumps(run(Path('.').resolve(),a.output),ensure_ascii=False))
