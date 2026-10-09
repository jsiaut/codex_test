"""Reconstruct proxy/Item-13 bounds without reparsing numeric instances."""
from pathlib import Path
import json,yaml
from .blocks import section_blocks
from .xbrl import digest
from .evidence import periodic_assurance

def run(root):
    cfg=yaml.safe_load((root/'config.yaml').read_text());inv=json.loads((root/'work/inventory.json').read_text())
    state=json.loads((root/'work/collection.json').read_text());run=json.loads((root/'work/run.json').read_text())
    old=json.loads((root/'work/queue.json').read_text());records=[r for r in old if r['block_class']!='item404']
    for accession,filing in state['filings'].items():
        if filing['status']!='collected':continue
        m=filing['metadata'];group=filing['group']
        if m['form'] not in ('DEF 14A','DEFA14A','10-K','10-K/A','424B4'):continue
        floor=inv['groups'][group].get('read_start',inv['groups'][group]['read_start_provisional'])
        if (m.get('reportDate') or m['filingDate'])<floor:continue
        res=filing['resources'].get(m['primaryDocument'])
        if not res:continue
        for block in section_blocks((root/res['path']).read_bytes(),form=m['form'],config=cfg):
            if block['item']!='404':continue
            block.update(group=group,accession=accession,entity_id='cik:'+m['cik'],form=m['form'],
             knowledge_date=m['filingDate'],acceptance_datetime=m['acceptanceDateTime'],source_path=res['path'],
             document_id=digest([res['url']]),as_of=run['as_of'],assurance_level='not_applicable',block_class='item404',priority=0)
            occurrence=digest([block['content_key'],block['document_id'],block['raw_byte_start']]);block['occurrence_id']=occurrence
            path=root/'work/blocks'/(occurrence+'.json');path.write_text(json.dumps(block,ensure_ascii=False))
            records.append({'content_key':block['content_key'],'occurrence_id':occurrence,'path':str(path.relative_to(root)),
             'group':group,'accession':accession,'block_class':'item404','chars':len(block['text'])})
    def order(r):
        b=json.loads((root/r['path']).read_text())
        return (b['priority'],-int(b['knowledge_date'].replace('-','')),b['group'],b['accession'])
    records.sort(key=order);seen=set()
    for r in records:r['duplicate']=r['content_key'] in seen;seen.add(r['content_key'])
    (root/'work/queue.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    (root/'work/section_boundary_changes.json').write_text(json.dumps({'old_item404_keys':sorted({r['content_key'] for r in old if r['block_class']=='item404'}),
        'new_item404_keys':sorted({r['content_key'] for r in records if r['block_class']=='item404'})},indent=2))
    print(json.dumps({'occurrences':len(records),'unique_keys':len(seen)}))

if __name__=='__main__':run(Path('.').resolve())
