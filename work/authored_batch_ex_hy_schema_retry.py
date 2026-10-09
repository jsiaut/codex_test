import json
from work.authored_helpers import ROOT
from secfragility.reader import store

# Only the rejected schema field is removed; no semantic rejection is retried.
for key in ['52e85c772039ba10092080d52a0b722c1178948ace99a57331780ba6b587d649','a8248cb7267e5d2f3a8e141b732b5dc58eabbeac56c6ee3107c81ca69b9d073f']:
 failures=[json.loads(s) for s in (ROOT/'work/observations'/(key+'.rejected.jsonl')).read_text().splitlines()]
 assert len(failures)==1 and failures[0]['phase']=='schema'
 row=dict(failures[0]['raw_line']);assert row.pop('guarantee_nature')=='primary'
 result=store(ROOT,key,[row],schema_retry=True)
 print(dict(key=key,accepted=result['accepted'],rejected=[r['error'] for r in result['rejected']]))
