from pathlib import Path
import json
from secfragility.reader import store
k='b92b4699d5c10a6ae66bd82c5886ffd55c2d5745eaef1bf2ed9cf2480d4515fa'
row=json.loads((Path('work/observations')/(k+'.rejected.jsonl')).read_text().splitlines()[0])['raw_line']
row['abstention_reason']='no_named_AI_investee_or_bank_counterparty_in_cash_management_note'
result=store(Path('.').resolve(),k,[row],schema_retry=True)
print(result)
assert not result['rejected']
