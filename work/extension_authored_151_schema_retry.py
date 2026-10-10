import json
from extension_authoring import ROOT
from secfragility.reader import store
k='1fa39e0dd853e9f8b33929bf0ead24b0d3156af4f1e03715c0f8a11c3db57b85'
r=json.loads((ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines()[0])['raw_line']
r['abstention_reason']=r.pop('reason')
result=store(ROOT,k,[r],schema_retry=True)
print(dict(accepted=result['accepted'],rejected=result['rejected']))
assert not result['rejected']
