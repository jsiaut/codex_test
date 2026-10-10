import json
from extension_authoring import ROOT
from secfragility.reader import store
k='e7f35348ba450b604937c94b043d7f382f62e26f53803fbf1e6f803c07279c75'
rows=[]
for line in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines():
    r=json.loads(line)
    if r['phase']=='schema':
        row=r['raw_line'];row.pop('block');rows.append(row)
result=store(ROOT,k,rows,schema_retry=True)
print(dict(accepted=result['accepted'],rejected=result['rejected']))
assert not result['rejected']
