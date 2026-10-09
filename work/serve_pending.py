"""Display a queue prefix within one tool-output budget; never author observations."""
from pathlib import Path
import json
from secfragility.reader import serve

def display_pending(root, *, max_blocks=3, serialized_budget=28000):
    rows=json.loads((root/'work/queue.json').read_text())
    seen=set(); displayed=0; size=0
    for row in rows:
        key=row['content_key']
        if key in seen or (root/'work/observations'/(key+'.jsonl')).exists():continue
        seen.add(key)
        packet=serve(root,key)
        encoded=json.dumps(packet,ensure_ascii=False)
        if size+len(encoded)>serialized_budget and displayed:
            break  # This packet must be displayed afresh before any authored pass.
        print(encoded); size+=len(encoded); displayed+=1
        if packet['parts']>1 or displayed>=max_blocks:break
    if not displayed:print(json.dumps({'queue_empty':True}))

if __name__=='__main__':display_pending(Path('.').resolve())
