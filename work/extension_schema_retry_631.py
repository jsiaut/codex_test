from extension_authoring import ROOT
from secfragility.reader import store
import json
k='a33c2de2884ff00314c1aa730b927c07a3d318160d14fdec1bc39fed03d9e8f5'
failures=[json.loads(x) for x in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines()]
rows=[x['raw_line'] for x in failures if x['phase']=='schema']
assert len(rows)==1
rows[0]['event_observable']='F4'
r=store(ROOT,k,rows,schema_retry=True)
print({x:r[x] for x in ['accepted','rejected','path']})
