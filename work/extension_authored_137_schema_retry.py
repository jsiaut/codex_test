import json
from extension_authoring import ROOT
from secfragility.reader import store
k='47a9d8bfc15256f68496478dd68b152657ad448dc236c8181d27029fae8bb7a6'
rows=[]
for line in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines():
    r=json.loads(line)
    if r['phase']=='schema':
        row=r['raw_line'];row['block']='contingent_obligations';rows.append(row)
result=store(ROOT,k,rows,schema_retry=True)
print(dict(accepted=result['accepted'],rejected=result['rejected']))
assert not result['rejected']
