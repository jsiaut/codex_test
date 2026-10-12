"""Bind actual command results to the code, inputs and table snapshot tested."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,subprocess,sys,xml.etree.ElementTree as ET
from .assembly_checkpoint import inputs
from .database import TABLES

def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def fingerprint(root):
    root=Path(root)
    files=set((root/'secfragility').glob('*.py'))|set((root/'tests').glob('*.py'))
    files.update(root/n for n in ('requirements.txt','schema.sql','queries.sql',
       'work/priorities/scope.json','work/priorities/source_manifest.json','work/priorities/source_backup.json',
       'work/priorities/originals.tar.zst','work/priorities/author_notes.py','work/priorities/authored_observations.json',
       'work/audit_20261012/submission_metadata_manifest.json','work/audit_20261012/submission_metadata.tar.zst'))
    return dict(files={str(p.relative_to(root)):sha(p) for p in sorted(files) if p.is_file()},
       tables={t:sha(root/'tables'/(t+'.parquet')) for t in TABLES},runtime={k:v for k,v in inputs(root).items() if k.startswith('@')})

def require(root,path=None):
    root=Path(root);path=Path(path) if path else root/'work/audit_20261012/test_attestation.json'
    evidence=json.loads(path.read_text())
    if evidence['fingerprint']!=fingerprint(root):raise ValueError('Tested code, inputs or tables changed; rerun validation before packaging')
    if not evidence['runs'] or any(r['returncode'] or r['failed'] or r['errors'] for r in evidence['runs']):raise ValueError('Tests did not pass')
    return evidence

def run(root,python=None):
    root=Path(root).resolve();directory=root/'work/audit_20261012';directory.mkdir(parents=True,exist_ok=True)
    before=fingerprint(root);results=[]
    for label,selection in [('full',[]),('targeted',['tests/test_targeted_priorities.py','tests/test_audit_regressions.py'])]:
        junit=directory/(label+'_junit.xml');command=[str(python or sys.executable),'-m','pytest','-q',*selection,'--junitxml='+str(junit)]
        execution=subprocess.run(command,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (directory/(label+'_tests.log')).write_text(execution.stdout)
        report=ET.parse(junit).getroot();suites=report.findall('testsuite') if report.tag=='testsuites' else [report]
        counts={key:sum(int(s.get(key,'0')) for s in suites) for key in ('tests','failures','errors','skipped')}
        results.append(dict(label=label,command=command,returncode=execution.returncode,passed=counts['tests']-counts['failures']-counts['errors']-counts['skipped'],
                            failed=counts['failures'],errors=counts['errors'],skipped=counts['skipped'],log_sha256=sha(directory/(label+'_tests.log'))))
        print(json.dumps(results[-1]),flush=True)
        if execution.returncode:raise RuntimeError('Test command failed; inspect '+str(directory/(label+'_tests.log')))
    after=fingerprint(root)
    if before!=after:raise ValueError('Test inputs changed while commands were running')
    proof=dict(verified_at=datetime.now(timezone.utc).isoformat(),fingerprint=after,runs=results,independent_audit_performed=False)
    (directory/'test_attestation.json').write_text(json.dumps(proof,indent=2)+'\n');return proof

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--python',type=Path);p.add_argument('--root',type=Path,default=Path('.'));a=p.parse_args();run(a.root,a.python)
