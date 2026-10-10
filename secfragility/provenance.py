from __future__ import annotations
from pathlib import Path
import csv
import hashlib
import json
import re
import subprocess
import yaml


def freeze_manifest(root: Path):
    original=subprocess.check_output(['git','rev-list','--max-parents=0','HEAD'],cwd=root,text=True).strip()
    committed=yaml.safe_load(subprocess.check_output(['git','show',original+':config.yaml'],cwd=root,text=True))
    current=yaml.safe_load((root/'config.yaml').read_text())
    dates=subprocess.check_output(['git','show','-s','--format=%cI',original],cwd=root,text=True).strip()
    journal=[json.loads(l) for l in (root/'journal.jsonl').read_text().splitlines()]
    requests=[j for j in journal if 'timestamp' in j and 'status' in j and 'url' in j]
    first=min(j['timestamp'] for j in requests) if requests else None
    manifest={'original_commit':original,'original_commit_date':dates,'first_sec_request':first,
        'config_sha256':hashlib.sha256((root/'config.yaml').read_bytes()).hexdigest(),
        'criteria_unchanged':all(committed[k]==current[k] for k in ('annex_e','annex_f','thresholds')),
        'original_criteria':{k:committed[k] for k in ('annex_e','annex_f','thresholds')},
        'current_criteria':{k:current[k] for k in ('annex_e','annex_f','thresholds')}}
    audit=root/'audit';audit.mkdir(exist_ok=True)
    (audit/'criteria_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    for annex in ('e','f'):
        name='annex_'+annex
        source=committed[name]['source_text']
        header=f'Commit original : {original}\nDate du commit : {dates}\nPremière requête SEC : {first}\nCritères inchangés : {manifest["criteria_unchanged"]}\n\n'
        (audit/(name+'.txt')).write_text(header+source)
    contact=current['user_agent'].rsplit(' ',1)[-1]
    with (audit/'journal.jsonl').open('w') as f:
        for row in journal:
            f.write(json.dumps(row,ensure_ascii=False,sort_keys=True).replace(contact,'[contact masqué]')+'\n')
    return manifest


def network_review(root: Path) -> dict:
    rows=[r for l in (root/'journal.jsonl').read_text().splitlines() if 'status' in (r:=json.loads(l)) and 'url' in r]
    from datetime import datetime
    stamps=[datetime.fromisoformat(r['timestamp']).timestamp() for r in rows]
    max_count=0;left=0
    for right,stamp in enumerate(stamps):
        while stamp-stamps[left]>=1:left+=1
        max_count=max(max_count,right-left+1)
    pause_violations=[]
    for i,row in enumerate(rows):
        if row['status']==403 and i+1<len(rows) and stamps[i+1]-stamps[i]<600:
            pause_violations.append({'refusal':row['timestamp'],'next_request':rows[i+1]['timestamp'],
                'seconds':stamps[i+1]-stamps[i]})
    result={'max_requests_in_rolling_second':max_count,'sec_limit_respected':max_count<=10,
        'pipeline_rate_respected':max_count<=5,'pause_violations':pause_violations,
        'requests':len(rows),'bytes_received':sum(r['bytes'] for r in rows)}
    (root/'work/network_review.json').write_text(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    root=Path('.').resolve();print(json.dumps(freeze_manifest(root),ensure_ascii=False)[:550]);print(json.dumps(network_review(root)))
