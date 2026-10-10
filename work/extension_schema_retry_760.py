from extension_authoring import ROOT
from secfragility.reader import store
import json
k='7d94de71ec5edeaf6c629f4fb363f475083a4e4bd7674c8433710f3a54b11b8c'
failures=[json.loads(x) for x in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines()]
rows=[x['raw_line'] for x in failures if x['phase']=='schema']
assert len(rows)==2
for row,quote in zip(rows,['Current portion of long-term debt, net | | | $ | 752','Long-term debt, net of current portion | | | $ | 1,715']):
    row['category_id']=row.pop('category')
    row['quote']=quote
r=store(ROOT,k,rows,schema_retry=True)
print({x:r[x] for x in ['accepted','rejected','path']})
