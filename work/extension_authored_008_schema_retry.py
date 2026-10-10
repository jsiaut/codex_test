import json
from extension_authoring import ROOT
from secfragility.reader import store
k='8094e9b40e159af0fc9629e714c5edae7d70aac6ad5f221828233530b62f6b0a'
# One schema retry: preserve the rejected original and correct only field name.
rows=[]
for line in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines():
 r=json.loads(line)
 if r['phase']=='schema':
  row=r['raw_line'];row['trigger_occurred']=row.pop('actual_trigger_met');rows.append(row)
result=store(ROOT,k,rows,schema_retry=True);print(result)
assert not result['rejected']
