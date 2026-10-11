"""Serve complete natural-note text; persist only human-authored, validated rows."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,math
from .reader import block_for,store
from .network import atomic_json
from .observations import validate_semantics
from .database import create, insert
from .reader import financial_note
from .xbrl import digest

def show(root,prefix,part=0):
    q=json.loads((root/'work/expansion/queue.json').read_text())
    matches=[r for r in q if r['content_key'].startswith(prefix)]
    if len({r['content_key'] for r in matches})!=1:raise ValueError('Ambiguous block prefix')
    r=matches[0];b=json.loads((root/r['path']).read_text());size=24000
    n=math.ceil(len(b['text'])/size);text=b['text'][part*size:(part+1)*size]
    if not text:raise ValueError('Part out of range')
    packet=dict(content_key=b['content_key'],accession=b['accession'],group=b['group'],label=b.get('label'),
        part=part,parts=n,packet_kind='complete_note_text',candidate_count=len(b['candidates']),text=text)
    with (root/'work/expansion/read_packets.jsonl').open('a') as f:
        f.write(json.dumps({k:v for k,v in packet.items() if k!='text'}|dict(text_sha256=hashlib.sha256(text.encode()).hexdigest(),
            served_at=datetime.now(timezone.utc).isoformat()))+'\n')
    return packet

def submit(root,prefix,authored):
    q=json.loads((root/'work/expansion/queue.json').read_text())
    key=next(r['content_key'] for r in q if r['content_key'].startswith(prefix))
    if (root/'work/observations'/(key+'.jsonl')).exists():return dict(reused=True,key=key)
    b=block_for(root,key);served=[json.loads(line) for line in (root/'work/expansion/read_packets.jsonl').read_text().splitlines()]
    parts={r['part'] for r in served if r['content_key']==key}
    if parts!=set(range(math.ceil(len(b['text'])/24000))):raise ValueError('Complete natural note not served')
    out=[]
    for item in authored:
        item=dict(item);idx=item.pop('candidate_index',None)
        if idx is not None:
            f=b['candidates'][idx]
            item.update(tagged_fact_id=f['fact_id'],amount=str(f['value']),unit=f['unit'],currency=f['currency'],
                period_start=f.get('period_start'),period_end=f['period_end'],amount_origin='tagged_reference')
        if b.get('filing_status')=='furnished':
            item.update(filing_status='furnished',tier='C' if b.get('incorporated_by_reference') else 'E',
                assurance_level='unknown')
        out.append(item)
    # Validate the entire authored batch before making an immutable pass.
    # A mistyped citation must not leave a partially accepted reading record.
    db=create(root)
    for item in out:
        row={k:b[k] for k in ['content_key','document_id','accession','entity_id','knowledge_date','assurance_level']}
        row.update(group_id=b['group'],abstained=False,
            locator=f"rawbytes:{b['raw_byte_start']}:{b['raw_byte_end']}",
            raw_byte_start=b['raw_byte_start'],raw_byte_end=b['raw_byte_end'],
            filing_status='filed',tier='D' if b['block_class']=='exhibit' else
                'A' if financial_note(b) and b['assurance_level']=='audited' else
                'B' if financial_note(b) and b['assurance_level']=='reviewed' else 'C',
            location=b['location'],source_perspective='reporting_entity',accounting_framework='us_gaap',
            as_of=b['as_of'])
        row.update(item)
        row['observation_id']=digest(['preflight',row])
        db.execute('BEGIN TRANSACTION')
        try:
            insert(db,'observations',row)
            validate_semantics(row,b,(root/b['source_path']).read_bytes())
        finally:db.execute('ROLLBACK')
    db.close()
    result=store(root,key,out)
    if result.get('rejected'):raise ValueError(json.dumps(result['rejected'],ensure_ascii=False))
    return result

def candidates(root,prefix,concept='',amount=None):
    q=json.loads((root/'work/expansion/queue.json').read_text());r=next(r for r in q if r['content_key'].startswith(prefix))
    b=json.loads((root/r['path']).read_text());out=[]
    for i,f in enumerate(b['candidates']):
        if concept and concept.lower() not in f['canonical_concept'].lower():continue
        if amount is not None and str(f.get('value'))!=amount:continue
        out.append(dict(index=i,**{k:f.get(k) for k in ['canonical_concept','value','unit','currency','period_start','period_end','dimensions']}))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['show','candidates']);p.add_argument('prefix');p.add_argument('--part',type=int,default=0)
    p.add_argument('--concept',default='');a=p.parse_args();root=Path('.').resolve()
    print(json.dumps(show(root,a.prefix,a.part) if a.action=='show' else candidates(root,a.prefix,a.concept),ensure_ascii=False,default=str))
