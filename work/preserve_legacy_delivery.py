"""Restore the preceding deliverables from their recorded delivery commit."""
import subprocess,zipfile,json,hashlib
from pathlib import Path
root=Path('.').resolve();ref='8447583af02b80647beab7b81e8f3ac97b61bcea'
out=Path('/codex/browser/projectless/0001-files-pasted-by-the-user-uploaded-pasted-text-po/output')
for name in ('user_brief_extension.md','notes_complementaires.md','notes_components.csv'):
 data=subprocess.check_output(['git','show',ref+':'+name]);(root/name).write_bytes(data)
 if name.endswith('.md'):(out/name).write_bytes(data)
entries=subprocess.check_output(['git','ls-tree','-rz',ref]).split(b'\0')
chosen=[]
for entry in entries:
 if not entry:continue
 head,path=entry.split(b'\t',1);p=Path(path.decode());parts=p.parts
 keep=(parts[0] in ('audit','tables','secfragility','tests') and '__pycache__' not in parts)
 keep=keep or len(parts)==1 and p.suffix in ('.md','.yaml','.sql','.csv','.json','.txt')
 keep=keep or parts[:2]==('work','observations')
 keep=keep or parts[0]=='work' and len(parts)==2 and p.suffix=='.json'
 if keep:chosen.append((head.split()[2].decode(),str(p)))
proc=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
zip_path=out/'SEC_Project_2_notes_complementaires.zip'
lfs=0
with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for oid,name in chosen:
  proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
  header=proc.stdout.readline().split();data=proc.stdout.read(int(header[2]));assert proc.stdout.read(1)==b'\n'
  if data.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
   sha=data.decode().split('oid sha256:')[1].splitlines()[0]
   p=root/'.git/lfs/objects'/sha[:2]/sha[2:4]/sha
   assert p.exists(),name
   z.write(p,name);lfs+=1
  else:z.writestr(name,data)
proc.stdin.close();assert proc.wait()==0
manifest=dict(archive=zip_path.name,regenerated_from_delivery_commit=ref,content_scope='previous notes delivery only',files=len(chosen),lfs_files_restored=lfs,bytes=zip_path.stat().st_size,sha256=hashlib.file_digest(zip_path.open('rb'),'sha256').hexdigest())
(out/'manifest_notes_complementaires.json').write_text(json.dumps(manifest,indent=2)+'\n')
(root/'work/deepening_legacy_preservation.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps(manifest))
