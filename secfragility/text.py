from __future__ import annotations
from copy import deepcopy
import html as html_std
import json
from pathlib import Path
import re
import unicodedata
from lxml import html
from lxml import etree
from .xbrl import digest


def decode(raw: bytes) -> str:
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('windows-1252')


def parse_html(raw: bytes):
    text = re.sub(r'^\s*<\?xml[^>]*\?>', '', decode(raw), flags=re.I)
    return html.fromstring(text, parser=html.HTMLParser(huge_tree=True))


def normalize_space(text: str) -> str:
    text = unicodedata.normalize('NFC', html_std.unescape(text)).replace('\u00a0',' ')
    return '\n'.join(re.sub(r'[\t\r\f\v ]+',' ',line).strip()
        for line in text.split('\n') if line.strip())


def local_tag(node):
    return str(node.tag).rsplit('}',1)[-1].lower() if isinstance(node.tag,str) else ''


def table_text(node) -> str:
    grid, occupied = [], {}
    # Rows belong to this table, not to nested tables.
    rows = node.xpath('./tr|./thead/tr|./tbody/tr|./tfoot/tr')
    for r,row in enumerate(rows):
        cols = []
        c = 0
        for cell in row.xpath('./td|./th'):
            while (r,c) in occupied:
                cols.append(occupied[(r,c)])
                c += 1
            content = normalize_space(render(cell)).replace('\n',' / ')
            colspan,rowspan = int(cell.get('colspan','1')),int(cell.get('rowspan','1'))
            if colspan < 1 or rowspan < 1 or colspan > 1000 or rowspan > 1000:
                raise ValueError('Portée de cellule de tableau invalide.')
            for dc in range(colspan):
                cols.append(content if dc == 0 else '')
                for dr in range(1,rowspan):
                    occupied[(r+dr,c+dc)] = content if dc == 0 else ''
            c += colspan
        while (r,c) in occupied:
            cols.append(occupied[(r,c)]); c += 1
        if any(cols):
            grid.append(' | '.join(cols))
    return '\n'.join(grid)


def render(node) -> str:
    tag = local_tag(node)
    if tag in ('ix:header','ix:hidden','ix:exclude','script','style','head'):
        return ''
    if tag == 'table':
        return '\n' + table_text(node) + '\n'
    parts = [node.text or '']
    for child in node:
        parts.extend((render(child),child.tail or ''))
    text = ''.join(parts)
    if tag == 'br':
        return '\n' + text
    if tag in ('p','div','h1','h2','h3','h4','h5','h6','li','tr'):
        return '\n' + text + '\n'
    return text


def normalize_html(raw: bytes) -> str:
    tree = parse_html(raw)
    ids = {node.get('id'):node for node in tree.iter() if node.get('id')}
    used = set()
    for node in list(tree.iter()):
        target = node.get('continuedat')
        visited = set()
        while target:
            if target in visited or target not in ids:
                raise ValueError('Chaîne de continuation iXBRL invalide.')
            visited.add(target)
            continuation = ids[target]
            copy = deepcopy(continuation)
            node.append(copy)
            used.add(target)
            target = continuation.get('continuedat')
    for target in used:
        node = ids[target]
        # Tail belongs to the enclosing document and must survive exclusion.
        if node.getparent() is not None:
            node.drop_tree()
    return normalize_space(render(tree))


def content_key(text: str, candidates: list[dict], normalizer_version: str) -> str:
    # No accession, occurrence ID, locator or reading limit in content identity.
    fields = ('canonical_concept','period_start','period_end','dimensions','unit','value','decimals')
    semantic = [{k:str(c.get(k)) if c.get(k) is not None else None for k in fields} for c in candidates]
    semantic.sort(key=lambda c:json.dumps(c,sort_keys=True))
    return digest([normalizer_version,text,semantic])


def extract_inline_blocks(raw: bytes, meta: dict, facts: list[dict], *, normalizer_version: str) -> list[dict]:
    """TextBlock type AND a note role, not a concept suffix (§9.2)."""
    inst = next(iter(meta['instance'].values()))
    tags, reports = inst['tag'],inst['report']
    note_roles = {r['role'] for r in reports.values()
        if r.get('groupType') == 'disclosure' and r.get('menuCat') in ('Notes','Tables','Details','Policies')
        and not r['role'].startswith('http://xbrl.sec.gov/ecd/')}
    eligible = {k.replace('_',':',1):v for k,v in tags.items()
        if v.get('xbrltype') == 'textBlockItemType' and note_roles.intersection(v.get('presentation',[]))}
    tree = parse_html(raw)
    inline_facts = {node.get('id'):node for node in tree.iter() if node.get('id')}
    by_inline_id = {f['locator'][3:]:f for f in facts if f['locator'].startswith('id:')}
    blocks = []
    # Map start/end offsets in original BYTES before decoding. These remain
    # stable if parser versions or Unicode normalization change.
    pattern = re.compile(rb'<ix:nonNumeric\b[^>]*>',re.I)
    for match in pattern.finditer(raw):
        start_tag = match.group()
        name_match = re.search(rb'\bname\s*=\s*["\']([^"\']+)',start_tag,re.I)
        id_match = re.search(rb'\bid\s*=\s*["\']([^"\']+)',start_tag,re.I)
        if not name_match or not id_match:
            continue
        name,inline_id = name_match.group(1).decode(),id_match.group(1).decode()
        if name not in eligible or inline_id not in inline_facts:
            continue
        closing = re.search(rb'</ix:nonNumeric\s*>',raw[match.end():],re.I)
        if not closing:
            raise ValueError('TextBlock sans fermeture.')
        end = match.end() + closing.end()
        node = inline_facts[inline_id]
        fragment = raw[match.start():end]
        normalized = normalize_space(render(parse_html(fragment)))
        source_ranges = [[match.start(),end]]
        candidates = []
        for child in node.iter():
            if child.get('id') in by_inline_id:
                candidates.append(by_inline_id[child.get('id')])
        continuation = node.get('continuedat')
        seen = set()
        while continuation:
            if continuation in seen or continuation not in inline_facts:
                raise ValueError('Continuation de note absente ou cyclique.')
            seen.add(continuation)
            cn = inline_facts[continuation]
            normalized += '\n' + normalize_space(render(cn))
            continuation_tag = re.search(rb'<ix:continuation\b[^>]*\bid\s*=\s*["\']' +
                re.escape(continuation.encode()) + rb'["\'][^>]*>', raw, re.I)
            if continuation_tag:
                continuation_end = re.search(rb'</ix:continuation\s*>',raw[continuation_tag.end():],re.I)
                if continuation_end:
                    source_ranges.append([continuation_tag.start(),continuation_tag.end()+continuation_end.end()])
            for child in cn.iter():
                if child.get('id') in by_inline_id:
                    candidates.append(by_inline_id[child.get('id')])
            continuation = cn.get('continuedat')
        definition = eligible[name]
        labels = definition.get('lang',{}).get('en-us',{}).get('role',{})
        blocks.append({'concept':name,'inline_id':inline_id,'text':normalized,
            'raw_byte_start':min(r[0] for r in source_ranges),'raw_byte_end':max(r[1] for r in source_ranges),
            'source_ranges':source_ranges,'candidates':candidates,
            'note_roles':sorted(note_roles.intersection(definition.get('presentation',[]))),
            'label':labels.get('label',name),'definition':labels.get('documentation',''),
            'content_key':content_key(normalized,candidates,normalizer_version)})
    return blocks


def extract_classic_blocks(raw: bytes, meta: dict, facts: list[dict], *, normalizer_version: str) -> list[dict]:
    inst=next(iter(meta['instance'].values()))
    note_roles={r['role'] for r in inst['report'].values() if r.get('groupType')=='disclosure'
        and r.get('menuCat') in ('Notes','Tables','Details','Policies') and not r['role'].startswith('http://xbrl.sec.gov/ecd/')}
    definitions={k.replace('_',':',1):v for k,v in inst['tag'].items() if v.get('xbrltype')=='textBlockItemType'
        and note_roles.intersection(v.get('presentation',[]))}
    tree=etree.fromstring(raw,etree.XMLParser(resolve_entities=False,no_network=True,huge_tree=True))
    contexts={node.get('id'):node for node in tree if str(node.tag).endswith('}context')}
    output=[]
    for node in tree:
        if not node.get('contextRef'):continue
        if not isinstance(node.tag,str) or not node.tag.startswith('{'):continue
        uri,name=node.tag[1:].split('}',1)
        prefix=node.prefix or next((k for k,v in node.nsmap.items() if v==uri),'')
        concept=(prefix+':'+name).lstrip(':')
        if concept not in definitions:continue
        text=normalize_space(render(parse_html((node.text or '').encode())))
        pattern=rb'<'+re.escape(concept.encode())+rb'\b[^>]*>'
        markers=list(re.finditer(pattern,raw,re.I))
        marker=next((m for m in markers if (not node.get('id') or re.search(rb'\bid=["\']'+re.escape(node.get('id').encode())+rb'["\']',m.group()))
            and re.search(rb'\bcontextRef=["\']'+re.escape(node.get('contextRef').encode())+rb'["\']',m.group(),re.I)),None)
        if marker is None:continue
        close=re.search(rb'</'+re.escape(concept.encode())+rb'\s*>',raw[marker.end():],re.I)
        if close is None:continue
        end=marker.end()+close.end()
        # Context equality is the eligibility filter; actual amount matching is
        # validated later. It never attributes an anonymous amount to a name.
        ctx=contexts.get(node.get('contextRef'))
        end_date=ctx.findtext('.//{http://www.xbrl.org/2003/instance}endDate') if ctx is not None else None
        if not end_date and ctx is not None:end_date=ctx.findtext('.//{http://www.xbrl.org/2003/instance}instant')
        candidates=[f for f in facts if f['period_end']==end_date]
        definition=definitions[concept];label=definition.get('lang',{}).get('en-us',{}).get('role',{}).get('label',concept)
        output.append({'text':text,'concept':concept,'label':label,'candidates':candidates,
            'raw_byte_start':marker.start(),'raw_byte_end':end,'source_ranges':[[marker.start(),end]],
            'source_format':'escaped_html_instance','content_key':content_key(text,candidates,normalizer_version),
            'note_roles':sorted(note_roles.intersection(definition.get('presentation',[])))})
    return output


def chunks(block: dict, max_chars: int, overlap_chars=1500):
    text = block['text']
    start = 0
    while start < len(text):
        end = min(start+max_chars,len(text))
        if end < len(text):
            natural = text.rfind('\n',start+max_chars//2,end)
            if natural != -1:
                end = natural
        yield text[start:end]
        if end == len(text):
            break
        start = max(start+1,end-min(overlap_chars,max_chars//4))


def autonomous_amendment(title: str, exhibit_type: str, filing_items: list[str]) -> bool:
    stripped = re.sub(r'^\s*(?:\d+(?:st|nd|rd|th)?|first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+', '', title, flags=re.I)
    if exhibit_type.startswith('EX-10'):
        return bool(re.search(r'\b(Amendment|Waiver|Consent)\b',stripped,re.I)) and not re.match(r'Amended\s+and\s+Restated\b',stripped,re.I)
    if exhibit_type.startswith('EX-4'):
        return bool(re.match(r'Supplemental\s+Indenture\b',stripped,re.I)) and '3.03' in filing_items
    return False
