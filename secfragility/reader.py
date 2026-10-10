"""Serve natural blocks; persist only observations authored after actual reading."""
from pathlib import Path
import json,argparse
from datetime import datetime,timezone
import hashlib
import re
from lxml import etree
from .database import create
from .observations import submit
from .text import chunks,exhibit_first_page
from .session import command as session_command

# The specification allows up to 80,000 serialized characters. Smaller
# packets also survive the execution tool's output limit without truncation.
DISPLAY_CEILING=30000

def financial_note(block):
    return block['block_class'] in ('related_parties','going_concern',
        'investments_note','debt_note','lease_note','commitments_note','concentration_narrative')

def display_dimensions(value):
    """Remove unused XML namespace declarations only in served typed dimensions."""
    if not value:return value
    dims=json.loads(value)
    for axis,member in list(dims.items()):
        if isinstance(member,str) and member.startswith('<'):
            node=etree.fromstring(member.encode(),etree.XMLParser(resolve_entities=False,no_network=True))
            prefixes={m.group(1) for n in node.iter() for text in [n.text or '',*n.attrib.values()]
                for m in re.finditer(r'\b([A-Za-z_][\w.-]*):[A-Za-z_][\w.-]*',text)}
            etree.cleanup_namespaces(node,keep_ns_prefixes=sorted(prefixes))
            dims[axis]=etree.tostring(node,encoding='unicode')
    return json.dumps(dims,ensure_ascii=False,separators=(',',':'))

def block_for(root,key):
    q=json.loads((root/'work/queue.json').read_text())
    row=next(r for r in q if r['content_key']==key or r['occurrence_id']==key)
    return json.loads((root/row['path']).read_text())

def serve(root,key=None,part=0,body=False,compact=False):
    q=json.loads((root/'work/queue.json').read_text())
    row=next((r for r in q if not (root/'work/observations'/(r['content_key']+'.jsonl')).exists()),None) if not key else next(r for r in q if r['content_key']==key or r['occurrence_id']==key)
    if row is None:return {'queue_empty':True}
    block=json.loads((root/row['path']).read_text())
    if not financial_note(block):
        block=dict(block,assurance_level='not_applicable')
    exhibit_header=block['block_class']=='exhibit' and not body
    page=None
    if exhibit_header:
        page=exhibit_first_page((root/block['source_path']).read_bytes())
        block=dict(block,text=page['text'])
    metadata={k:block.get(k) for k in ['content_key','occurrence_id','group','entity_id','accession','form','item',
      'exhibit_type','label','block_class','raw_byte_start','raw_byte_end','knowledge_date','assurance_level']}
    collection_path=root/'work/collection.json'
    collection=json.loads(collection_path.read_text()) if collection_path.exists() else {}
    filing=collection.get('filings',{}).get(block.get('accession'),{})
    metadata['report_date']=filing.get('metadata',{}).get('reportDate') or None
    metadata['filing_items']=filing.get('metadata',{}).get('items') or None
    if page:
        metadata['header_raw_byte_start']=0
        metadata['header_raw_byte_end']=page['raw_byte_end']
        metadata['header_boundary_status']=page['boundary_status']
    fields=['fact_id','canonical_concept','value','unit','currency','period_start','period_end','dimensions','decimals']
    candidates=[{k:f.get(k) for k in fields} for f in block['candidates']]
    dictionaries={}
    if compact:
        # Lossless dictionary encoding of repeated fields. Candidate indexes
        # address the immutable full fact IDs in this natural block. The
        # validator still requires the full tagged_fact_id when storing.
        for c in candidates:c['dimensions']=display_dimensions(c['dimensions'])
        for field in fields[1:]:
            dictionaries[field]=list(dict.fromkeys(json.dumps(c[field],ensure_ascii=False,sort_keys=True) for c in candidates))
        candidates=[[i,*[dictionaries[field].index(json.dumps(c[field],ensure_ascii=False,sort_keys=True))
            for field in fields[1:]]] for i,c in enumerate(candidates)]
        dictionaries={field:[json.loads(value) for value in values] for field,values in dictionaries.items()}
        axes=[];members=[];encoded=[]
        for value in dictionaries['dimensions']:
            pairs=[]
            for axis,member in json.loads(value or '{}').items():
                if axis not in axes:axes.append(axis)
                if member not in members:members.append(member)
                pairs.append([axes.index(axis),members.index(member)])
            encoded.append(pairs)
        dictionaries['dimensions']=encoded
        metadata['dimension_axes']=axes
        metadata['dimension_members']=members
    if compact:
        metadata['candidate_columns']=['candidate_index',*fields[1:]]
        metadata['candidate_dictionaries']=dictionaries
    header=json.dumps({'metadata':metadata,'candidates':candidates},ensure_ascii=False)
    candidate_packets=[]
    text_candidates=candidates
    if len(header)>DISPLAY_CEILING//2:
        # Header pieces are presentation fragments of the SAME natural block.
        # Every candidate is served before its complete text; none is filtered.
        start=0;group=[]
        for candidate in candidates:
            trial=group+[candidate]
            size=len(json.dumps({'metadata':metadata,'candidates':trial},ensure_ascii=False))+500
            if size>DISPLAY_CEILING and group:
                candidate_packets.append((start,group));start+=len(group);group=[candidate]
            elif size>DISPLAY_CEILING:
                raise ValueError('One candidate exceeds display ceiling; explicit candidate continuation required.')
            else:group=trial
        if group:candidate_packets.append((start,group))
        text_candidates=[]
    header=json.dumps({'metadata':metadata,'candidates':text_candidates},ensure_ascii=False)
    ceiling=DISPLAY_CEILING-len(header)-500
    def packet(i,portions):
        common={'metadata':metadata,'exhibit_header':exhibit_header,'part':i,
            'parts':len(candidate_packets)+len(portions),'candidate_header_parts':len(candidate_packets),
            'total_candidates':len(candidates)}
        if i<len(candidate_packets):
            start,group=candidate_packets[i]
            return dict(common,packet_kind='candidate_header',candidates=group,
                candidate_start=start,candidate_end=start+len(group),text='')
        return dict(common,packet_kind='text',candidates=text_candidates,
            text_part=i-len(candidate_packets),text=portions[i-len(candidate_packets)])
    while True:
        portions=list(chunks(block,ceiling))
        largest=max(len(json.dumps(packet(i,portions),ensure_ascii=False)) for i in range(len(candidate_packets)+len(portions)))
        if largest<=DISPLAY_CEILING:break
        ceiling-=largest-DISPLAY_CEILING+200
        if ceiling<2000:raise ValueError('Serialized packet header exceeds reading ceiling.')
    result=packet(part,portions)
    encoded=json.dumps(result,ensure_ascii=False)
    log=root/'work/read_packets.jsonl'
    with log.open('a') as f:
        f.write(json.dumps(dict(content_key=block['content_key'],occurrence_id=block['occurrence_id'],
            part=part,parts=result['parts'],packet_kind=result['packet_kind'],
            exhibit_header=exhibit_header,text_chars=len(result['text']),
            packet_chars=len(encoded),packet_sha256=hashlib.sha256(encoded.encode()).hexdigest(),
            served_at=datetime.now(timezone.utc).isoformat()))+'\n')
    return result

def store(root,key,authored,*,schema_retry=False):
    block=block_for(root,key);run=json.loads((root/'work/run.json').read_text())
    rows=[]
    for authored_row in authored:
        row={k:block[k] for k in ['content_key','document_id','accession','group','entity_id','knowledge_date','assurance_level']}
        row['group_id']=row.pop('group')
        is_note=financial_note(block)
        if not is_note:row['assurance_level']='not_applicable'
        row.update(abstained=False,locator=f"rawbytes:{block['raw_byte_start']}:{block['raw_byte_end']}",
            raw_byte_start=block['raw_byte_start'],raw_byte_end=block['raw_byte_end'],
            filing_status='filed',tier='D' if block['block_class']=='exhibit' else
                'A' if is_note and block['assurance_level']=='audited' else 'B' if is_note and block['assurance_level']=='reviewed' else 'C',
            location=block.get('location',block['block_class']),source_perspective='reporting_entity',accounting_framework='us_gaap')
        row.update(authored_row);rows.append(row)
    result=submit(create(root),root,block,(root/block['source_path']).read_bytes(),rows,run['as_of'],schema_retry=schema_retry)
    if result['accepted']:session_command(root,'touch')
    # Persist actual reading work regularly even if a later block is interrupted.
    from .checkpoint import checkpoint
    try:
        saved=checkpoint(root)
        if saved:result['checkpoint']=saved
    except Exception as exc:
        # Observation persistence precedes GitHub; a remote failure cannot erase it.
        result['checkpoint_error']=str(exc)
        print('GitHub checkpoint failed: '+str(exc))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['serve','store']);p.add_argument('--key');p.add_argument('--part',type=int,default=0)
    p.add_argument('--body',action='store_true');p.add_argument('--compact',action='store_true');p.add_argument('--rows',type=Path);a=p.parse_args();r=Path('.').resolve()
    print(json.dumps(serve(r,a.key,a.part,a.body,a.compact) if a.action=='serve' else store(r,a.key,json.loads(a.rows.read_text())),ensure_ascii=False,default=str))
