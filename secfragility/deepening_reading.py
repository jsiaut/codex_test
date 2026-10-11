"""Nominate original financial-note blocks; no semantic extraction or authored rows."""
from pathlib import Path
import json
import yaml
from .metadata import load
from .text import extract_inline_blocks,normalize_html,content_key
from .xbrl import parse_instance,digest


def save(root,blocks):
    queue=json.loads((root/'work/queue.json').read_text());seen={r['occurrence_id'] for r in queue}
    rows=[]
    for block in blocks:
        path=root/'work/blocks'/(block['occurrence_id']+'.json')
        path.write_text(json.dumps(block,ensure_ascii=False,default=str))
        row={k:block[k] for k in ['content_key','occurrence_id','group','accession','block_class','knowledge_date']}
        row.update(path=str(path.relative_to(root)),chars=len(block['text']),candidates=len(block['candidates']),
            duplicate=any(r['content_key']==block['content_key'] for r in queue))
        rows.append(row)
        if row['occurrence_id'] not in seen:queue.append(row);seen.add(row['occurrence_id'])
    (root/'work/queue.json').write_text(json.dumps(queue,ensure_ascii=False,indent=2)+'\n')
    return rows


def notes(root,ciks):
    registry=json.loads((root/'work/deepening_filings.json').read_text())
    run=json.loads((root/'work/run.json').read_text());cfg=yaml.safe_load((root/'config.yaml').read_text())
    output=[]
    for acc,filing in registry.items():
        m=filing['metadata']
        if int(m['cik']) not in ciks:continue
        resources=filing['resources'];primary=resources[m['primaryDocument']];facts=[]
        assurance='audited' if m['form']=='10-K' else 'reviewed'
        for name in filing['discovery']['instances']:
            r=resources[name]
            facts+=parse_instance((root/r['path']).read_bytes(),entity_id='cik:'+m['cik'],
                reporting_identity='reporter:'+filing['group'],group_id=filing['group'],
                document_id=digest([r['url']]),accession=acc,acceptance_datetime=m['acceptanceDateTime'],
                knowledge_date=m['filingDate'],assurance_level=assurance,as_of=run['as_of'])
        metadata=load(root,resources,acc)
        for b in extract_inline_blocks((root/primary['path']).read_bytes(),metadata,facts,normalizer_version=cfg['normalizer_version']):
            if not any(s.lower() in b['text'].lower() for s in ('CoreWeave','OpenAI','Anthropic')):continue
            b.update(group=filing['group'],accession=acc,entity_id='cik:'+m['cik'],form=m['form'],
                knowledge_date=m['filingDate'],acceptance_datetime=m['acceptanceDateTime'],as_of=run['as_of'],
                source_path=primary['path'],document_id=digest([primary['url']]),assurance_level=assurance,
                location='financial_statements_and_notes',block_class='investments_note',financial_note=True)
            b['occurrence_id']=digest([b['content_key'],b['document_id'],b['raw_byte_start']])
            output.append(b)
    return output


if __name__=='__main__':
    root=Path('.').resolve()
    # The scan only nominates blocks. Selection of these natural notes is recorded
    # before serving; long notes are not split at lexical hits.
    nominated=notes(root,{1858681,2021728,1892492,1108524,1585521,1083301,1144879,1944366})
    (root/'work/deepening_note_inventory.json').write_text(json.dumps([
        {k:b[k] for k in ['content_key','group','accession','label','concept']}|
        dict(chars=len(b['text']),candidates=len(b['candidates'])) for b in nominated],ensure_ascii=False,indent=2)+'\n')
    # Only selected financial notes enter the reading queue, not all matched prose.
    print(json.dumps(json.loads((root/'work/deepening_note_inventory.json').read_text()),ensure_ascii=False))
