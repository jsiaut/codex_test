import json
from extension_authoring import ROOT
from secfragility.reader import store
k='d503de2d97b54d083c56437cc6be4ab32f9f6bde06529b96b92efd75291d3baf'
rows=[]
for line in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines():
    r=json.loads(line)
    if r['phase']=='schema':
        row=r['raw_line'];row['category_id']='capacity_backstop';rows.append(row)
result=store(ROOT,k,rows,schema_retry=True)
print(dict(accepted=result['accepted'],rejected=result['rejected']))
assert not result['rejected']
