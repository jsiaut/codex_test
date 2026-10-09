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
