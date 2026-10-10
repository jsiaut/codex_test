"""Helpers for manually authored, source-validated extension observations."""
from pathlib import Path
import json
from secfragility.reader import block_for, store
ROOT = Path(__file__).resolve().parents[1]

def tagged(key, index, quote, **fields):
    fact = block_for(ROOT, key)['candidates'][index]
    assert fact['value'] is not None
    return {k:fact.get(k) for k in ('unit','currency','period_start','period_end')} | dict(
        quote=quote,amount=fact['value'],amount_origin='tagged_reference',
        tagged_fact_id=fact['fact_id'],amount_qualifier='exact') | fields

def save(key, rows):
    path=ROOT/'work/observations'/(key+'.jsonl')
    if path.exists():
        as_of=json.loads((ROOT/'work/run.json').read_text())['as_of']
        old=[r for line in path.read_text().splitlines()
            if (r:=json.loads(line))['record_kind']=='observation' and r['as_of']==as_of]
        if len(old)==len(rows) and all(all(old[i].get(k)==v for k,v in row.items()) for i,row in enumerate(rows)):
            print(dict(content_key=key,already_validated=True));return
        raise RuntimeError('Existing reading differs; never silently overwrite or reread it.')
    result = store(ROOT,key,rows)
    print(result)
    if result['rejected']:raise RuntimeError('Observation validation failed; original attempts retained.')
    return result
