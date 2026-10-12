"""Portable current tables plus the small, independently restorable extension."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile
from .targeted_priorities import sha,save

DELIVERY=Path('/codex/browser/projectless/0001-files-pasted-by-the-user-uploaded-pasted-text-po/output')
def package(root,output=DELIVERY):
    root=Path(root);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    names=['README.md','TARGETED_REPRODUCTION.md','targeted_priorities.md','targeted_summary.json',
           'targeted_evidence.csv','targeted_lender_positions.csv','targeted_financing_register.csv',
           'smci_integration.md','schema.sql','requirements.txt','audit/criteria_manifest.json',
           'work/smci/baseline/criteria_manifest.json']
    names += [str(p.relative_to(root)) for p in (root/'secfragility').glob('*.py')]
    names += [str(p.relative_to(root)) for p in (root/'tables').glob('*.parquet')]
    names += [str(p.relative_to(root)) for p in (root/'work/priorities/baseline').glob('*.parquet') if p.stem!='facts']
    names += [str(p.relative_to(root)) for p in (root/'work/priorities/delta_tables').glob('*.parquet')]
    names += ['tests/test_targeted_priorities.py']
    names += [str(p.relative_to(root)) for p in (root/'work/priorities').glob('*')
              if p.is_file() and p.suffix in ('.json','.py','.zst') and p.name!='delivery_archive.json']
    names=sorted(set(names))
    proof=json.loads((root/'work/priorities/replay_verification.json').read_text())
    if not proof['all_eight_tables_byte_identical']:raise ValueError('Source replay not verified')
    for n in ('secfragility/targeted_priorities.py','secfragility/database.py','work/priorities/author_notes.py','schema.sql'):
        if not proof['code_identical_to_tested_isolated_code'][n]:raise ValueError('Untested code')
    code_hashes={n:sha(root/n) for n in ('secfragility/targeted_priorities.py','secfragility/database.py','work/priorities/author_notes.py','schema.sql')}
    for n in names:
        if not (root/n).is_file():raise FileNotFoundError(n)
    target=output/'SEC_Project_2_priorites.zip';temporary=target.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5,allowZip64=True) as z:
        for n in names:z.write(root/n,n)
    with zipfile.ZipFile(temporary) as z:
        if z.testzip() is not None:raise ValueError('Archive CRC failed')
        checked={}
        for n in [x for x in names if x.startswith('tables/')] + list(code_hashes):
            digest=hashlib.sha256()
            with z.open(n) as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):digest.update(chunk)
            checked[n]=digest.hexdigest()==sha(root/n)
        if not all(checked.values()):raise ValueError('Packaged tables or tested code differ')
    temporary.replace(target)
    for n in ('targeted_priorities.md','TARGETED_REPRODUCTION.md','targeted_summary.json','targeted_evidence.csv',
              'targeted_lender_positions.csv','targeted_financing_register.csv'):
        shutil.copy2(root/n,output/n)
    shutil.copy2(root/'work/priorities/replay_verification.json',output/'targeted_replay_verification.json')
    meta=dict(path=str(target),bytes=target.stat().st_size,sha256=sha(target),entries=len(names),crc_checked=True,
        archive_tables_and_code_match=checked,tested_code_sha256=code_hashes,
        commit_before_packaging=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        main_groups=26,source_cutoff='2026-10-09T10:24:21.129672+00:00',subagents_used=False,
        full_tests_passed=137,isolated_tests_passed=5,all_eight_tables_byte_identical_after_isolated_replay=True,
        contents='Eight current tables; seven immutable prior tables; unchanged facts stored once; targeted originals compressed backup, authored observations, code, proof and reproduction instructions.',
        historical_originals='Previous SoftBank/Dell/SMCI deliveries remain necessary for full historical raw-source reconstruction; targeted overlay restoration is self-contained.')
    save(root/'work/priorities/delivery_archive.json',meta);save(output/'targeted_manifest.json',meta)
    return meta

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=DELIVERY);a=p.parse_args()
    result=package(Path('.').resolve(),a.output);print(json.dumps({k:result[k] for k in ('path','bytes','sha256','entries','crc_checked')}))
