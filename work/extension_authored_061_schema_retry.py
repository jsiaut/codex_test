from pathlib import Path
import json
from secfragility.reader import store
k='f86a04ce606e914b6c45895b9d469c0c701dd549ddb9754d475a04e1699ef73d'
p=Path('work/observations')/(k+'.rejected.jsonl')
row=json.loads(p.read_text().splitlines()[0])['raw_line']
row['trigger_description']='energy equipment procurement backstop; precise triggering event not specified in this note'
result=store(Path('.').resolve(),k,[row],schema_retry=True)
print(result)
assert not result['rejected']
