from __future__ import annotations
from pathlib import Path
import json
import re
import yaml
from .text import parse_html,render,normalize_space,extract_inline_blocks,extract_classic_blocks,content_key,local_tag
from .xbrl import parse_instance,digest
from .evidence import periodic_assurance,filing_status,tier


def offsets(raw: bytes,tree):
    tokens=list(re.finditer(rb'<([A-Za-z][A-Za-z0-9:_.-]*)\b[^>]*>',raw))
    cursor=0;mapping={}
    for node in tree.iter():
        tag=local_tag(node)
        if not tag:
            continue
        found=None
        for i in range(cursor,min(cursor+100,len(tokens))):
            if tokens[i].group(1).decode().lower()!=tag:
                continue
            if node.get('id') and not re.search(rb'\bid\s*=\s*["\']'+re.escape(node.get('id').encode())+rb'["\']',tokens[i].group(),re.I):
                continue
            found=i;break
        if found is not None:
            mapping[node]=tokens[found].start();cursor=found+1
    return mapping


def section_blocks(raw: bytes, *, form: str, config: dict) -> list[dict]:
    tree=parse_html(raw);positions=offsets(raw,tree)
    item_heading=re.compile(r'^\s*Item\s+(\d+(?:\.\d{2})?[A-C]?)\b',re.I)
    governance=re.compile(r'^(?:certain\s+relationships(?:\s+and\s+related.*)?|related\s+(?:party|person)\s+transactions|transactions\s+with\s+related\s+(?:parties|persons)|related\s+persons?\s+transactions)$',re.I)
    headings=[]
    anchors={key:n for n in tree.iter() for key in (n.get('id'),n.get('name') if local_tag(n)=='a' else None) if key}
    # Proxy TOCs provide actual section anchors. A TOC entry is a pointer,
    # never the start of the related-person narrative.
    governance_sections=[]
    for link in tree.iter('a'):
        label=normalize_space(render(link)).rstrip('.: ')
        target=anchors.get((link.get('href') or '').split('#',1)[-1]) if '#' in (link.get('href') or '') else None
        if not governance.match(label) or target is None or target not in positions:
            continue
        tables=[p for p in link.iterancestors() if local_tag(p)=='table']
        container=tables[0] if tables else link.getparent()
        following=[]
        for peer in container.iter('a'):
            plabel=normalize_space(render(peer)).strip()
            ptarget=anchors.get((peer.get('href') or '').split('#',1)[-1]) if '#' in (peer.get('href') or '') else None
            if not plabel or plabel.isdigit() or ptarget is None or ptarget not in positions:
                continue
            if positions[ptarget]>positions[target]:following.append(positions[ptarget])
        governance_sections.append({'node':target,'pos':positions[target],'label':label,
            'item':'404','end':min(following) if following else None})
    for node,pos in positions.items():
        if local_tag(node) not in ('p','div','span','b','strong','font','h1','h2','h3','h4','td'):
            continue
        text=normalize_space(render(node))
        if len(text)>240 or '\n' in text:
            continue
        if any(sum(1 for a in p.iter('a') if '#' in (a.get('href') or ''))>=5
                for p in node.iterancestors() if local_tag(p)=='table'):
            continue
        if any((a.get('href') or '').startswith('#') for a in node.iter('a')):
            continue
        match=item_heading.match(text)
        if match:
            item=match.group(1).upper()
            headings.append({'node':node,'pos':pos,'label':text,'item':item})
        elif form in ('DEF 14A','DEFA14A','424B4','10-K/A') and governance.match(text.rstrip('.:')) and not governance_sections:
            headings.append({'node':node,'pos':pos,'label':text,'item':'404'})
    headings.extend(governance_sections)
    # Remove nested copies of one heading by retaining the outermost position.
    unique=[]
    for h in sorted(headings,key=lambda h:h['pos']):
        if unique and h['item']==unique[-1]['item'] and h['pos']-unique[-1]['pos']<500:
            continue
        unique.append(h)
    output=[]
    for index,h in enumerate(unique):
        item=h['item'];label=h['label']
        wanted=(form in ('8-K','8-K/A') and item in {'1.01','1.02','3.03','8.01'}) or (
            form.startswith('10-K') and item=='9A' and 'control' in label.lower()) or (
            form.startswith('10-Q') and item=='4' and 'control' in label.lower()) or item=='404'
        if not wanted:
            continue
        start=h['pos'];end=h.get('end') or (unique[index+1]['pos'] if index+1<len(unique) else len(raw))
        if item=='404' and not h.get('end'):
            # Fallback: a peer heading with the same explicit typography.
            current_nodes=[h['node'],*h['node'].iterdescendants()]
            size_pattern=r'font(?:-size)?\s*:\s*(?:[a-z]+\s+)*([0-9.]+)pt'
            current_sizes=[float(m.group(1)) for n in current_nodes
                for m in re.finditer(size_pattern,n.get('style') or '',re.I)]
            current_size=max(current_sizes,default=0)
            for n,pos in positions.items():
                if pos<=start+500 or pos>=end:continue
                t=normalize_space(render(n));style=n.get('style','')
                if len(t)<5 or len(t)>180 or '\n' in t:continue
                bold_nodes=[x for x in n.iter() if local_tag(x) in ('b','strong','h1','h2','h3') or
                    re.search(r'font-weight\s*:\s*(?:bold|[7-9]00)',x.get('style') or '',re.I)]
                bold=max((len(normalize_space(render(x))) for x in bold_nodes),default=0)>=len(t)*0.8
                sizes=[float(m.group(1)) for x in n.iter() for m in re.finditer(size_pattern,x.get('style') or '',re.I)]
                if bold and sizes and max(sizes)>=current_size and not governance.match(t.rstrip('.:')):
                    end=pos;break
        fragment=raw[start:end]
        try:text=normalize_space(render(parse_html(fragment)))
        except Exception:continue
        # A table of contents heading ends almost immediately at its next item.
        if len(text)<150:
            continue
        output.append({'text':text,'candidates':[],'item':item,'label':label,
            'raw_byte_start':start,'raw_byte_end':end,'source_ranges':[[start,end]],
            'content_key':content_key(text,[],config['normalizer_version'])})
    return output


def queue(root: Path):
    cfg=yaml.safe_load((root/'config.yaml').read_text());run=json.loads((root/'work/run.json').read_text())
    state=json.loads((root/'work/collection.json').read_text());inv=json.loads((root/'work/inventory.json').read_text())
    queue=[];excluded=[];all_blocks=[]
    blockdir=root/'work/blocks';blockdir.mkdir(parents=True,exist_ok=True)
    for accession,filing in state['filings'].items():
        if filing['status']!='collected':continue
        meta=filing['metadata'];group=filing['group'];resources=filing['resources']
        read_start=inv['groups'][group].get('read_start',inv['groups'][group]['read_start_provisional'])
        if meta.get('reportDate') and meta['form'].startswith(('10-K','10-Q')) and meta['reportDate']<read_start:continue
        if not meta['form'].startswith(('10-K','10-Q')) and meta['filingDate']<read_start:continue
        name=meta.get('primaryDocument')
        if name not in resources:continue
        resource=resources[name];raw=(root/resource['path']).read_bytes()
        candidates=[]
        disc=json.loads((root/filing['discovery_path']).read_text()) if filing.get('discovery_path') else {}
        for ins_name,res in resources.items():
            if ins_name not in disc.get('instances',[]) and not ins_name.endswith('_htm.xml'):continue
            candidates.extend(parse_instance((root/res['path']).read_bytes(),entity_id='cik:'+meta['cik'],
                reporting_identity='reporter:'+group,group_id=group,document_id=digest([res['url']]),accession=accession,
                acceptance_datetime=meta['acceptanceDateTime'],knowledge_date=meta['filingDate'],
                assurance_level=periodic_assurance(meta['form']),as_of=run['as_of']))
        natural=[]
        note_resource=resource
        if 'MetaLinks.json' in resources and b'ix:nonnumeric' in raw.lower():
            try:
                natural=extract_inline_blocks(raw,json.loads((root/resources['MetaLinks.json']['path']).read_text()),
                    candidates,normalizer_version=cfg['normalizer_version'])
            except Exception as exc:
                excluded.append({'group':group,'accession':accession,'reason':'parse_failed','element':'natural_notes','detail':str(exc)})
        elif 'MetaLinks.json' in resources:
            for ins_name in disc.get('instances',[]):
                if ins_name not in resources:continue
                note_resource=resources[ins_name]
                try:
                    natural=extract_classic_blocks((root/note_resource['path']).read_bytes(),
                        json.loads((root/resources['MetaLinks.json']['path']).read_text()),candidates,
                        normalizer_version=cfg['normalizer_version'])
                except Exception as exc:
                    excluded.append({'group':group,'accession':accession,'reason':'parse_failed','element':'classic_notes','detail':str(exc)})
                break
        for block in natural:
            label=re.sub(r'[^a-z0-9]','',(block['label']+' '+block['concept']).lower())
            wanted=('relatedparty' in label or 'relatedperson' in label)
            going='goingconcern' in label
            if not any('goingconcern' in (b['label']+b['concept']).lower() for b in natural):
                # First Notes role, determined by issuer presentation order,
                # covers the note-1 fallback without guessing a concept name.
                meta_inst=next(iter(json.loads((root/resources['MetaLinks.json']['path']).read_text())['instance'].values()))
                roles={r['role']:int(r.get('order',999999)) for r in meta_inst['report'].values()
                    if r.get('menuCat')=='Notes' and r.get('groupType')=='disclosure'}
                if roles:
                    first_role=min(roles,key=roles.get)
                    going=first_role in block.get('note_roles',[])
            block['block_class']='related_parties' if wanted else 'going_concern' if going else 'outside_first_pass'
            if going and meta['filingDate']<inv['groups'][group]['analysis_start']:
                block['block_class']='outside_first_pass'
            block['priority']=0 if wanted else 1
            all_blocks.append(dict(block,group=group,accession=accession))
            if block['block_class']!='outside_first_pass':natural_block=block;queue.append((filing,note_resource,natural_block))
            else:excluded.append({'group':group,'accession':accession,'reason':'not_processed','element':block['content_key'],'detail':'texte hors de la tranche initiale'})
        for block in section_blocks(raw,form=meta['form'],config=cfg):
            item=block['item']
            if item in ('4','9A') and meta['filingDate']<inv['groups'][group]['analysis_start']:continue
            block['block_class']='item404' if item=='404' else 'controls' if item in ('4','9A') else '8k_item'
            block['priority']=0 if item=='404' else 1 if item in ('4','9A') else 2
            queue.append((filing,resource,block))
        # Every eligible EX-10/EX-4 enters the queue, initially by its first
        # page; classification by actual parties occurs only after human reading.
        if meta['form'] in ('8-K','8-K/A') and filing.get('discovery_path'):
            disc=json.loads((root/filing['discovery_path']).read_text())
            for header in disc['headers']:
                if not header['type'].startswith(('EX-10','EX-4')) or header['filename'] not in resources:continue
                res=resources[header['filename']];exraw=(root/res['path']).read_bytes()
                text=normalize_space(render(parse_html(exraw)))
                block={'text':text,'candidates':[],'label':header.get('description',''),'exhibit_type':header['type'],
                    'block_class':'exhibit','priority':3,'raw_byte_start':0,'raw_byte_end':len(exraw),
                    'source_ranges':[[0,len(exraw)]],'content_key':content_key(text,[],cfg['normalizer_version'])}
                queue.append((filing,res,block))
    seen=set()
    queue.sort(key=lambda e:(e[2]['priority'],-int(e[0]['metadata']['filingDate'].replace('-','')),e[0]['group'],e[0]['metadata']['accessionNumber']))
    records=[]
    for filing,res,block in queue:
        meta=filing['metadata'];key=block['content_key']
        block.update(group=filing['group'],accession=meta['accessionNumber'],entity_id='cik:'+meta['cik'],
            form=meta['form'],knowledge_date=meta['filingDate'],acceptance_datetime=meta['acceptanceDateTime'],
            source_path=res['path'],document_id=digest([res['url']]),as_of=run['as_of'],
            assurance_level=periodic_assurance(meta['form']))
        occurrence=digest([key,block['document_id'],block['raw_byte_start']])
        block['occurrence_id']=occurrence
        path=blockdir/(occurrence+'.json');path.write_text(json.dumps(block,ensure_ascii=False,default=str))
        records.append({'content_key':key,'occurrence_id':occurrence,'path':str(path.relative_to(root)),
            'group':block['group'],'accession':block['accession'],'block_class':block['block_class'],
            'chars':len(block['text']),'duplicate':key in seen})
        seen.add(key)
    (root/'work/queue.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
    (root/'work/block_exclusions.json').write_text(json.dumps(excluded,ensure_ascii=False,indent=2))
    print(json.dumps({'occurrences':len(records),'unique_keys':len(seen),'text_chars':sum(r['chars'] for r in records if not r['duplicate']),
        'not_processed_outside_scope':len(excluded)}))


if __name__=='__main__':queue(Path('.').resolve())
