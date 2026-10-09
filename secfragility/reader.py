"""Serve natural blocks; persist only observations authored after actual reading."""
from pathlib import Path
import json,argparse
from .database import create
from .observations import submit
from .text import chunks
from .session import command as session_command

def block_for(root,key):
    q=json.loads((root/'work/queue.json').read_text())
    row=next(r for r in q if r['content_key']==key or r['occurrence_id']==key)
    return json.loads((root/row['path']).read_text())

def serve(root,key=None,part=0,body=False):
    q=json.loads((root/'work/queue.json').read_text())
    row=next((r for r in q if not (root/'work/observations'/(r['content_key']+'.jsonl')).exists()),None) if not key else next(r for r in q if r['content_key']==key or r['occurrence_id']==key)
    if row is None:return {'queue_empty':True}
    block=json.loads((root/row['path']).read_text())
    if block['block_class'] not in ('related_parties','going_concern'):
        block=dict(block,assurance_level='not_applicable')
    exhibit_header=block['block_class']=='exhibit' and not body
    if exhibit_header:
        # Initial disclosure is the opening natural paragraphs. Long exhibits
        # never enter the context before their parties have been read.
        end=block['text'].rfind('\n',2500,6000)
        block=dict(block,text=block['text'][:end if end!=-1 else 6000])
    metadata={k:block.get(k) for k in ['content_key','occurrence_id','group','entity_id','accession','form','item',
      'exhibit_type','label','block_class','raw_byte_start','raw_byte_end','knowledge_date','assurance_level']}
    fields=['fact_id','canonical_concept','value','unit','currency','period_start','period_end','dimensions','decimals']
    candidates=[{k:f.get(k) for k in fields} for f in block['candidates']]
    header=json.dumps({'metadata':metadata,'candidates':candidates},ensure_ascii=False)
    ceiling=80000-len(header)-200
    if ceiling<2000:raise ValueError('Candidate header exceeds readable packet; split the candidates with explicit reading progress.')
    portions=list(chunks(block,ceiling))
    return {'metadata':metadata,'candidates':candidates,'exhibit_header':exhibit_header,'part':part,'parts':len(portions),'text':portions[part]}

def store(root,key,authored):
    block=block_for(root,key);run=json.loads((root/'work/run.json').read_text())
    rows=[]
    for authored_row in authored:
        row={k:block[k] for k in ['content_key','document_id','accession','group','entity_id','knowledge_date','assurance_level']}
        row['group_id']=row.pop('group')
        financial_note=block['block_class'] in ('related_parties','going_concern')
        if not financial_note:row['assurance_level']='not_applicable'
        row.update(abstained=False,locator=f"rawbytes:{block['raw_byte_start']}:{block['raw_byte_end']}",
            raw_byte_start=block['raw_byte_start'],raw_byte_end=block['raw_byte_end'],
            filing_status='filed',tier='D' if block['block_class']=='exhibit' else
                'A' if financial_note and block['assurance_level']=='audited' else 'B' if financial_note and block['assurance_level']=='reviewed' else 'C',
            location=block.get('location',block['block_class']),source_perspective='reporting_entity',accounting_framework='us_gaap')
        row.update(authored_row);rows.append(row)
    result=submit(create(root),root,block,(root/block['source_path']).read_bytes(),rows,run['as_of'])
    if result['accepted']:session_command(root,'touch')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['serve','store']);p.add_argument('--key');p.add_argument('--part',type=int,default=0)
    p.add_argument('--body',action='store_true');p.add_argument('--rows',type=Path);a=p.parse_args();r=Path('.').resolve()
    print(json.dumps(serve(r,a.key,a.part,a.body) if a.action=='serve' else store(r,a.key,json.loads(a.rows.read_text())),ensure_ascii=False,default=str))
