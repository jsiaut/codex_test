"""Explicit analyst-selected USD table-cell bindings, with no table scan authoring."""
from decimal import Decimal
import re

def table_amount(quote,label,value,*,column=0,occurrence=-1):
    if not re.search(r'\(in millions(?:, [^)]*)?\)',quote,re.I) or '$' not in quote:
        raise ValueError('Table scale and dollar currency must be explicit')
    rows=[]
    for line in quote.splitlines():
        cells=[c.strip() for c in line.split('|') if c.strip() and c.strip()!='$']
        if cells and cells[0]==label:
            numbers=[c for c in cells[1:] if re.fullmatch(r'\(?-?[\d,]+(?:\.\d+)?\)?',c)]
            rows.append(numbers)
    if not rows or column>=len(rows[occurrence]):raise ValueError('Explicit selected row/column absent')
    token=rows[occurrence][column]
    amount=Decimal(token.replace(',','').replace('(','-').replace(')',''))*1000000
    if amount!=Decimal(str(value)):raise ValueError('Selected amount differs from its exact source cell')
    return dict(label=label,column=column,occurrence=occurrence,token=token,scale=1000000,currency='USD',value=str(amount))
