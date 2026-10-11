"""Serve frozen remaining notes; save the executor's authored review only."""
from pathlib import Path
import argparse,json,math,re
from datetime import datetime,timezone
from .expansion_reading import show,submit

def manifest(root):
    return json.loads((root/'work/continuation398/scope.json').read_text())['rows']

def display(root,start,count=1,part=None):
    for index,row in enumerate(manifest(root)[start:start+count],start):
        b=json.loads((root/row['path']).read_text())
        parts=range(math.ceil(len(b['text'])/24000)) if part is None else [part]
        for p in parts:
            packet=show(root,row['content_key'],p)
            print(f"BLOCK {index} {row['content_key'][:12]} | {b['group']} | {b['accession']} | {b.get('label')} | PART {p+1}/{packet['parts']}")
            # Collapse only repeated empty table separators for reading. Every
            # word, populated cell and number remains; sources stay immutable.
            print(re.sub(r'(?:\|[ \t]*){2,}', '| ', packet['text']))

def save(root,path):
    authored=json.loads(path.read_text());out=[]
    ledger=root/'work/continuation398/reviews.jsonl'
    records=[json.loads(x) for x in ledger.read_text().splitlines()] if ledger.exists() else []
    prior={x['content_key']:x for x in records};existing=set(prior)
    rows=manifest(root)
    for a in authored:
        row=rows[a['index']];key=row['content_key']
        if key in existing:
            if prior[key]['summary']!=a['summary'] or prior[key]['classification']!=a['classification']:
                raise ValueError('An immutable completed review cannot be replaced')
            continue
        if not a['summary'] or not a['rows']:raise ValueError('An authored assessment and quoted observation are required')
        result=submit(root,key,a['rows'])
        if result.get('reused'):raise ValueError('Frozen remaining block was already passed without this review')
        record=dict(content_key=key,index=a['index'],group=row['group'],accession=row['accession'],
            summary=a['summary'],classification=a['classification'],accepted_observations=result['accepted'],
            reviewed_at=datetime.now(timezone.utc).isoformat(),reviewer='sole_executor',subagents_used=False)
        with ledger.open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
        existing.add(key);out.append(dict(index=a['index'],accepted=result['accepted']))
    print(json.dumps(dict(saved=out,completed=len(existing),remaining=398-len(existing))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['show','save','progress']);p.add_argument('--start',type=int,default=0);p.add_argument('--count',type=int,default=1);p.add_argument('--part',type=int);p.add_argument('--file',type=Path);a=p.parse_args();r=Path('.').resolve()
    if a.action=='show':display(r,a.start,a.count,a.part)
    elif a.action=='save':save(r,a.file)
    else:
        path=r/'work/continuation398/reviews.jsonl';done=len(path.read_text().splitlines()) if path.exists() else 0
        print(json.dumps(dict(target=398,completed=done,remaining=398-done)))
