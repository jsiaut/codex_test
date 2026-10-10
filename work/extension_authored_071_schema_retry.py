from pathlib import Path
import json
from secfragility.reader import store
k='994c41535cfbb8e678b795281ae2a8102aef46f0ce2959d02a631d24163619af'
row=json.loads((Path('work/observations')/(k+'.rejected.jsonl')).read_text().splitlines()[0])['raw_line']
row['link_type']='purchase_commitment'
result=store(Path('.').resolve(),k,[row],schema_retry=True)
print(result)
assert not result['rejected']
