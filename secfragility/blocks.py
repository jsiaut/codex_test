from __future__ import annotations
from pathlib import Path
import json
import re
import yaml
from .text import parse_html,render,normalize_space,extract_inline_blocks,extract_classic_blocks,content_key,local_tag,requested_contract_exhibit
from .xbrl import parse_instance,digest
from .evidence import periodic_assurance,filing_status,tier
from .metadata import load as load_metadata,first_financial_note_role


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
    def heading_size(node):
        sizes=[]
        for n in [node,*node.iterdescendants()]:
            for m in re.finditer(r'font(?:-size)?\s*:\s*(?:[a-z]+\s+)*([0-9.]+)(pt|px)',n.get('style') or '',re.I):
                sizes.append(float(m.group(1))*(0.75 if m.group(2).lower()=='px' else 1))
        return max(sizes,default=0)
    def anchor_heading(target,label):
        desired=re.sub(r'\s+',' ',label).strip().lower()
        # An empty TOC anchor can sit INSIDE the actual heading. Searching
        # forward from it would skip that heading and select a repeated
        # "continued" caption on the next page, dropping the first page.
        for parent in target.iterancestors():
            candidate=re.sub(r'\s+',' ',normalize_space(render(parent))).strip().lower()
            if candidate==desired and not any((a.get('href') or '').startswith('#') for a in parent.iter('a')):
                return target,positions[target]
        for n,pos in positions.items():
            if positions[target]<=pos<=positions[target]+18000 and len(n)<8 and local_tag(n) in ('p','div','span','h1','h2','h3','b','strong'):
                candidate=re.sub(r'\s+',' ',normalize_space(render(n))).strip().lower()
                if candidate==desired and not any((a.get('href') or '').startswith('#') for a in n.iter('a')):
                    return n,pos
        return target,positions[target]
    # Proxy TOCs provide actual section anchors. A TOC entry is a pointer,
    # never the start of the related-person narrative.
    governance_sections=[]
    for link in tree.iter('a'):
        label=normalize_space(render(link)).rstrip('.: ')
        target=anchors.get((link.get('href') or '').split('#',1)[-1]) if '#' in (link.get('href') or '') else None
        if not governance.match(label) or target is None or target not in positions:
            continue
        heading,start=anchor_heading(target,label);level=heading_size(heading)
        tables=[p for p in link.iterancestors() if local_tag(p)=='table']
        container=tables[0] if tables else link.getparent()
        following=[]
        for peer in container.iter('a'):
            plabel=normalize_space(render(peer)).strip()
            ptarget=anchors.get((peer.get('href') or '').split('#',1)[-1]) if '#' in (peer.get('href') or '') else None
            if not plabel or plabel.isdigit() or ptarget is None or ptarget not in positions:
                continue
            if positions[ptarget]>start:
                # TOC peers may include nested policy/transaction headings.
                # Their semantic membership, rather than typography shared
                # imperfectly across pages, keeps them inside Item 404.
                if re.search(r'related\s+(?:party|person)\s+transactions?',plabel,re.I) or governance.match(plabel):continue
                following.append(positions[ptarget])
        governance_sections.append({'node':heading,'pos':start,'label':label,
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
            if re.search(r'\s\d{1,3}$',text):
                continue  # unlinked table-of-contents entry with page number
            if text[:1].islower() and text.endswith('.'):
                continue  # trailing sentence span in committee responsibilities
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
            current_size=heading_size(h['node'])
            current_legacy=[int(x.get('size')) for x in h['node'].iter()
                if local_tag(x)=='font' and (x.get('size') or '').isdigit()]
            capitals=h['label'].isupper()
            for n,pos in positions.items():
                if pos<=start or pos>=end or h['node'] in n.iterancestors():continue
                t=normalize_space(render(n));style=n.get('style','')
                if len(t)<5 or len(t)>180 or '\n' in t:continue
                if capitals and not re.sub(r'\([a-z]\)','',t).isupper():continue
                bold_nodes=[x for x in n.iter() if local_tag(x) in ('b','strong','h1','h2','h3') or
                    re.search(r'font-weight\s*:\s*(?:bold|[7-9]00)',x.get('style') or '',re.I)]
                bold=max((len(normalize_space(render(x))) for x in bold_nodes),default=0)>=len(t)*0.8
                sizes=[float(m.group(1)) for x in n.iter() for m in re.finditer(size_pattern,x.get('style') or '',re.I)]
                nested_related=bool(re.search(r'related\s+(?:party|person)\s+transactions?',t,re.I))
                distinct_large_heading=current_size>=14 and heading_size(n)>=current_size
                peer_legacy=[int(x.get('size')) for x in n.iter()
                    if local_tag(x)=='font' and (x.get('size') or '').isdigit()]
                # Legacy HTML specifies a font-size ordinal instead of CSS.
                # Compare the filed ordinals directly, without inventing points.
                legacy_peer=capitals and current_size==0 and current_legacy and peer_legacy and bold and max(peer_legacy)>=max(current_legacy)
                if ((bold and sizes and max(sizes)>=current_size) or distinct_large_heading or legacy_peer) and not governance.match(t.rstrip('.:')) and not nested_related:
                    end=pos;break
        fragment=raw[start:end]
        if item=='404' and any(b.get('item')=='404' and b['raw_byte_start']<=start and end<=b['raw_byte_end'] for b in output):
            continue
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
    replacements=json.loads((root/'work/deprecations.json').read_text())['mapping'] if (root/'work/deprecations.json').exists() else {}
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
                assurance_level=periodic_assurance(meta['form']),as_of=run['as_of'],taxonomy_replacements=replacements,
                reporting_scope='as_if_combined' if group=='SPCX' else 'consolidated'))
        natural=[]
        note_resource=resource
        metadata=load_metadata(root,resources,accession)
        if metadata and b'ix:nonnumeric' in raw.lower():
            try:
                natural=extract_inline_blocks(raw,metadata,
                    candidates,normalizer_version=cfg['normalizer_version'])
            except Exception as exc:
                excluded.append({'group':group,'accession':accession,'reason':'parse_failed','element':'natural_notes','detail':str(exc)})
        elif metadata:
            for ins_name in disc.get('instances',[]):
                if ins_name not in resources:continue
                note_resource=resources[ins_name]
                try:
                    natural=extract_classic_blocks((root/note_resource['path']).read_bytes(),
                        metadata,candidates,
                        normalizer_version=cfg['normalizer_version'])
                except Exception as exc:
                    excluded.append({'group':group,'accession':accession,'reason':'parse_failed','element':'classic_notes','detail':str(exc)})
                break
        has_going_concern=any('goingconcern' in (b['label']+b['concept']).lower() for b in natural)
        first_role=first_financial_note_role(next(iter(metadata['instance'].values()))) if metadata and not has_going_concern else None
        for block in natural:
            label=re.sub(r'[^a-z0-9]','',(block['label']+' '+block['concept']).lower())
            wanted=('relatedparty' in label or 'relatedperson' in label)
            going='goingconcern' in label
            if not has_going_concern:
                # First Notes role, determined by issuer presentation order,
                # covers the note-1 fallback without guessing a concept name.
                if first_role:
                    going=first_role in block.get('note_roles',[])
            block['block_class']='related_parties' if wanted else 'going_concern' if going else 'outside_first_pass'
            if going and (meta.get('reportDate') or meta['filingDate'])<inv['groups'][group]['analysis_start']:
                block['block_class']='outside_first_pass'
            block['priority']=0 if wanted else 1
            all_blocks.append(dict(block,group=group,accession=accession))
            if block['block_class']!='outside_first_pass':natural_block=block;queue.append((filing,note_resource,natural_block))
            else:excluded.append({'group':group,'accession':accession,'reason':'not_processed','element':block['content_key'],'detail':'texte hors de la tranche initiale'})
        for block in section_blocks(raw,form=meta['form'],config=cfg):
            item=block['item']
            if item in ('4','9A') and (meta.get('reportDate') or meta['filingDate'])<inv['groups'][group]['analysis_start']:continue
            block['block_class']='item404' if item=='404' else 'controls' if item in ('4','9A') else '8k_item'
            block['priority']=0 if item=='404' else 1 if item in ('4','9A') else 2
            queue.append((filing,resource,block))
        if group=='SPCX' and accession=='0001628280-26-042639':
            # Annual notes in this prospectus are audited HTML, not iXBRL.
            # Bounds are the actual annual note headings (D1/D2).
            annual_ranges=[('related_parties','Note 18 — Related Party Transactions',
                raw.rfind(b'<div ',0,9609692),raw.rfind(b'<div ',0,9628654)),
                ('going_concern','Note 1 — annual basis of presentation',7336456,7361893)]
            for cls,label,start,end in annual_ranges:
                text=normalize_space(render(parse_html(raw[start:end])))
                block={'text':text,'candidates':[],'label':label,'concept':'untagged_annual_note',
                    'block_class':cls,'priority':0 if cls=='related_parties' else 1,
                    'raw_byte_start':start,'raw_byte_end':end,'source_ranges':[[start,end]],
                    'assurance_level':'audited','location':'annual_audited_notes_in_424B4',
                    'content_key':content_key(text,[],cfg['normalizer_version'])}
                queue.append((filing,resource,block))
        if group=='CRWV' and accession=='0001193125-25-067651':
            # Annual Note 14 is covered by the Deloitte 2024/2023 and RSM
            # 2022 opinions in this same prospectus (D0012).
            start,end=3463351,3477806
            text=normalize_space(render(parse_html(raw[start:end])))
            queue.append((filing,resource,{'text':text,'candidates':[],
                'label':'Note 14 — annual Related Party Transactions','concept':'untagged_annual_note',
                'block_class':'related_parties','priority':0,'raw_byte_start':start,'raw_byte_end':end,
                'source_ranges':[[start,end]],'assurance_level':'audited','location':'annual_audited_notes_in_424B4',
                'content_key':content_key(text,[],cfg['normalizer_version'])}))
        # Every eligible EX-10/EX-4 enters the queue, initially by its first
        # page; classification by actual parties occurs only after human reading.
        if meta['form'] in ('8-K','8-K/A') and filing.get('discovery_path'):
            disc=json.loads((root/filing['discovery_path']).read_text())
            for header in disc['headers']:
                if not requested_contract_exhibit(header['type']):
                    if header['type'].startswith('EX-101') and header['filename'] in resources:
                        excluded.append({'group':group,'accession':accession,'reason':'policy_excluded',
                            'element':digest([resources[header['filename']]['url']]),
                            'detail':'ressource XBRL EX-101 de phase 1, hors file des contrats EX-10/EX-4'})
                    continue
                if header['filename'] not in resources:continue
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
            assurance_level=block.get('assurance_level',periodic_assurance(meta['form'])))
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
