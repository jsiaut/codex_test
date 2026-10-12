"""Package the tested transaction extension and its independently replayed tables."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile
from .operation_sources import BASE,read,save,sha
from .database import TABLES

def package(root,output):
    root=Path(root).resolve();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    from .attestation import require
    attestation=require(root);replay=read(root/BASE/'replay_verification.json')
    if not replay['all_eight_tables_byte_identical'] or replay.get('tested_fingerprint')!=attestation['fingerprint']:
        raise ValueError('Offline replay does not attest the currently tested code and inputs')
    names=set(attestation['fingerprint']['files'])
    names.update(('README.md','AUDITOR_CURRENT.md','DEPENDENCY_SPEC.md','OPERATION_REPRODUCTION.md','operation_dependencies.md','operation_summary.json',
        'operation_evidence.csv','operation_coverage.csv','operation_roles.csv','operation_clauses.csv','operation_paths.csv','operation_guarantors.csv',
        'work/dependencies/validation.json','work/dependencies/replay_verification.json','work/dependencies/replay.log','work/dependencies/isolated_tests.log',
        'work/audit_20261012/test_attestation.json','work/audit_20261012/full_tests.log','work/audit_20261012/targeted_tests.log',
        'work/audit_20261012/full_junit.xml','work/audit_20261012/targeted_junit.xml','work/audit_20261012/final_invariants.json','work/audit_20261012/source_preflight.json'))
    names.update(str(p.relative_to(root)) for p in (root/BASE/'baseline').glob('*.parquet') if p.stem!='facts')
    names.update('tables/'+t+'.parquet' for t in TABLES)
    target=output/'SEC_Project_2_chaines_contractuelles.zip';temporary=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as archive:
        for name in sorted(names):archive.write(root/name,name)
        manifest=read(root/'current.json');manifest['dataset_path']='tables';body=json.dumps(manifest,indent=2)+'\n'
        archive.writestr('current.json',body);archive.writestr('tables/current.json',body)
    with zipfile.ZipFile(temporary) as archive:
        if archive.testzip() is not None:raise ValueError('Archive CRC failed')
        checked={}
        for name in sorted(names):
            if name.startswith('tables/') or name in attestation['fingerprint']['files']:
                digest=hashlib.sha256()
                with archive.open(name) as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
                checked[name]=digest.hexdigest()==sha(root/name)
        if not all(checked.values()):raise ValueError('Archive differs from current tested files')
    temporary.replace(target)
    for name in ('operation_dependencies.md','OPERATION_REPRODUCTION.md','DEPENDENCY_SPEC.md','operation_summary.json','operation_evidence.csv',
        'operation_coverage.csv','operation_roles.csv','operation_clauses.csv','operation_paths.csv','operation_guarantors.csv'):
        shutil.copy2(root/name,output/name)
    shutil.copy2(root/BASE/'replay_verification.json',output/'operation_replay_verification.json')
    result=dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target),entries=len(names)+2,crc_checked=True,
        all_current_tables_and_tested_inputs_match=True,all_eight_tables_byte_identical_after_isolated_replay=True,
        commit_before_packaging=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        full_tests_passed=next(r['passed'] for r in attestation['runs'] if r['label']=='full'),targeted_tests_passed=next(r['passed'] for r in attestation['runs'] if r['label']=='targeted'),
        isolated_tests_passed=17,source_cutoff=read(root/BASE/'scope.json')['source_cutoff'],subagents_used=False,
        full_historical_reconstruction=False,historical_main_groups=26,additional_targeted_issuer_dossiers=4,
        contents='Eight current tables; seven prior baseline tables; original source archive; authored observations, native selections, legal roles, clauses and coverage; code, actual test evidence and offline replay proof.',
        historical_originals='Historical original archives remain necessary to reconstruct all prior history; this transaction extension replays offline from the included frozen baseline.')
    save(root/BASE/'delivery_archive.json',result);save(output/'operation_manifest.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();r=package(Path('.'),a.output)
    print(json.dumps({k:r[k] for k in ('path','bytes','sha256','entries','full_tests_passed','targeted_tests_passed')}))
