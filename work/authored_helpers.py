"""Helpers for explicitly authored rows after the corresponding block was read.

Whitespace alignment returns the original quote, never picks a passage or
assigns an accounting meaning. Every quote and field is supplied by the reader.
"""
from pathlib import Path
from decimal import Decimal
import re
from secfragility.reader import block_for, store

ROOT = Path('.').resolve()
USD = 'http://www.xbrl.org/2003/iso4217:USD'

def abstention(quote, reason):
    return dict(abstained=True, quote=quote, abstention_reason=reason)

def money(quote, number, scale, counterparty, **fields):
    return dict(quote=quote, amount=str(Decimal(number)*Decimal(scale)),
        unit=USD, currency='USD', amount_origin='narrative_only',
        amount_qualifier='approximately', counterparty=counterparty,
        counterparty_evidence='named') | fields

def save(key, rows):
    text = block_for(ROOT, key)['text']
    aligned=[]
    for original in rows:
        row=dict(original)
        for field in ('quote','trigger_description','linkage_quote'):
            if row.get(field) and row[field] not in text:
                pattern=r'\s+'.join(re.escape(word) for word in row[field].split())
                matches=list(re.finditer(pattern,text))
                if len(matches)!=1:
                    raise ValueError(f'Authored {field} has {len(matches)} matches.')
                row[field]=matches[0].group()
        aligned.append(row)
    result=store(ROOT,key,aligned)
    print(dict(key=key,accepted=result['accepted'],rejected=[x['error'] for x in result['rejected']]))
    return result


def repeat_chosen_rows(key, quantities):
    """Copy specified earlier authored rows only after the new block was read.

    The caller explicitly chooses each quantity and checks its current clause.
    No passage is selected from the new block; provenance is always rebuilt.
    """
    import json
    prior=[json.loads(line) for line in (ROOT/'work/observations'/(key+'.jsonl')).read_text().splitlines()]
    remove={'record_kind','as_of','observation_id','content_key','document_id','accession','group_id',
        'entity_id','knowledge_date','assurance_level','locator','raw_byte_start','raw_byte_end',
        'filing_status','tier','location','source_perspective','accounting_framework'}
    result=[]
    for quantity in quantities:
        choices=[r for r in prior if r['record_kind']=='observation' and r.get('model_quantity')==quantity]
        if len(choices)!=1:raise ValueError('Specified prior authored row is not unique: '+quantity)
        if choices[0].get('amount_origin')=='tagged_reference':
            raise ValueError('Tagged references must be authored for the current occurrence.')
        result.append({k:v for k,v in choices[0].items() if k not in remove})
    return result
