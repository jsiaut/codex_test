import json
from extension_authoring import ROOT
from secfragility.reader import store
k='5304461260728b251da2dca00dba5ee9c88616c64db2b835ff4fcaba74cd2f80'
rows=[]
for line in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines():
    r=json.loads(line)
    if r['phase']=='schema':
        row=r['raw_line'];row['event_type']='repayment';rows.append(row)
result=store(ROOT,k,rows,schema_retry=True);print(result)
assert not result['rejected']
