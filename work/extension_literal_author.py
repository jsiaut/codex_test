"""Write literal quotations chosen manually after a complete block reading."""
from pathlib import Path
from secfragility.reader import block_for
ROOT=Path(__file__).resolve().parents[1]

def span(key,start,end,*,start_occurrence=0):
    body=block_for(ROOT,key)['text']
    left=-1
    for _ in range(start_occurrence+1):
        left=body.index(start,left+1)
    right=body.index(end,left)+len(end)
    return body[left:right]

def write(number,key,rows):
    target=ROOT/'work'/f'extension_authored_{number}.py'
    if target.exists():
        raise RuntimeError('Authored file already exists')
    calls=['dict('+','.join(f'{name}={value!r}' for name,value in row.items())+')' for row in rows]
    target.write_text('from extension_authoring import save\nk='+repr(key)+'\nsave(k,['+','.join(calls)+'])\n')
