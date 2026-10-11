"""Explicit natural statement/section bounds on original SEC HTML."""
from pathlib import Path
import json,re
import yaml
from .blocks import offsets
from .text import parse_html,render,normalize_space,normalize_html,local_tag,content_key
from .xbrl import digest
from .deepening_reading import save
from .network import atomic_json

def section(root,accession,filename,start,end,label,kind,*,incorporated=False):
    registry=json.loads((root/'work/deepening_filings.json').read_text());f=registry[accession]
    m=f['metadata'];res=f['resources'][filename];raw=(root/res['path']).read_bytes()
    text=normalize_html(raw[start:end]);cfg=yaml.safe_load((root/'config.yaml').read_text())
    key=content_key(text,[],cfg['normalizer_version']);did=digest([res['url']])
    return dict(content_key=key,occurrence_id=digest([key,did,start]),text=text,candidates=[],
        group=f['group'],entity_id='cik:'+m['cik'],accession=accession,document_id=did,
        source_path=res['path'],raw_byte_start=start,raw_byte_end=end,source_ranges=[[start,end]],
        knowledge_date=m['filingDate'],acceptance_datetime=m['acceptanceDateTime'],
        as_of=json.loads((root/'work/run.json').read_text())['as_of'],
        assurance_level='reviewed' if m['form']=='10-Q' else 'unknown',
        location='financial_statements_and_notes' if kind!='section' else 'management_discussion',
        block_class='investments_note' if kind=='statement' else 'debt_note' if kind=='note' else 'section',
        form=m['form'],label=label,incorporated_by_reference=incorporated,
        filing_status='furnished' if m['form']=='6-K' else 'filed')

def nominate(root):
    registry=json.loads((root/'work/deepening_filings.json').read_text());blocks=[]
    # Entire current-date schedules, every row and every legend, to the next
    # comparative schedule. Selection uses statement structure, not borrowers.
    for acc,beg,ending in [('0001193125-26-335023',2508655,3830756),
                          ('0001193125-26-352436',3765571,8386215)]:
        f=registry[acc];blocks.append(section(root,acc,f['metadata']['primaryDocument'],beg,ending,
            'Complete June 30 2026 schedule of investments and footnotes','statement'))
    acc='0001859392-26-000091';f=registry[acc]
    blocks.append(section(root,acc,f['metadata']['primaryDocument'],2875113,2886627,
        'Complete MD&A overview, highlights and recent developments','section'))
    # The whole 6-K expressly incorporates the report and its financial exhibit.
    acc='0001104659-26-094844';f=registry[acc];name='nbis-20260812xex99d2.htm'
    raw=(root/f['resources'][name]['path']).read_bytes();tr=parse_html(raw);pos=offsets(raw,tr)
    heads=[]
    for n in tr.iter():
        if local_tag(n)!='table' or len(list(n.iter()))>100:continue
        t=normalize_space(render(n));match=re.match(r'^\|?\s*(\d+)\.\s*\|\s*([A-Z].+)$',t)
        if match and len(t)<220:heads.append((int(match.group(1)),pos[n],t))
    heads.sort(key=lambda x:x[1])
    for i,(num,start,label) in enumerate(heads):
        if num not in {1,8,11,12,16}:continue
        end=heads[i+1][1] if i+1<len(heads) else len(raw)
        blocks.append(section(root,acc,name,start,end,label,'note',incorporated=True))
    # Full balance sheet and full cash-flow statement with all comparatives.
    selected=[]
    for n in tr.iter():
        if local_tag(n)!='p':continue
        t=normalize_space(render(n))
        if t.startswith('UNAUDITED CONDENSED CONSOLIDATED') and len(t)<180:
            selected.append((pos[n],t))
    selected.sort()
    for i,(start,label) in enumerate(selected):
        if '(Continued)' in label:continue
        if 'BALANCE SHEETS' not in label and 'STATEMENTS OF CASH FLOWS' not in label:continue
        later=[z for z,title in selected[i+1:] if '(Continued)' not in title]
        end=later[0] if later else heads[0][1]
        blocks.append(section(root,acc,name,start,end,label,'statement',incorporated=True))
    rows=save(root,blocks)
    queue=json.loads((root/'work/expansion/queue.json').read_text());seen={r['occurrence_id'] for r in queue}
    queue.extend(r for r in rows if r['occurrence_id'] not in seen)
    atomic_json(root/'work/expansion/queue.json',queue)
    atomic_json(root/'work/expansion/sections.json',[{k:b[k] for k in ['content_key','accession','label','raw_byte_start','raw_byte_end','incorporated_by_reference']} for b in blocks])
    return [dict(key=b['content_key'][:12],label=b['label'],chars=len(b['text'])) for b in blocks]

if __name__=='__main__':print(json.dumps(nominate(Path('.').resolve()),ensure_ascii=False))
