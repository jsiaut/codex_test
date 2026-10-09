from __future__ import annotations
from decimal import Decimal, InvalidOperation
import hashlib
import json
import re
from lxml import etree

XBRLI = 'http://www.xbrl.org/2003/instance'
XBRLDI = 'http://xbrl.org/2006/xbrldi'
XSI = 'http://www.w3.org/2001/XMLSchema-instance'
NS = {'xbrli':XBRLI,'xbrldi':XBRLDI}


def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',',':')).encode()).hexdigest()


def namespace_family(uri: str) -> str:
    # Taxonomy year/date is an attribute, never semantic identity.
    if '/us-gaap/' in uri or 'fasb.org/us-gaap' in uri:
        return 'us-gaap'
    if '/dei/' in uri:
        return 'dei'
    if '/srt/' in uri:
        return 'srt'
    if 'ifrs' in uri:
        return 'ifrs'
    if uri in {XBRLI,XBRLDI,XSI} or uri.startswith(('http://www.xbrl.org/','http://www.w3.org/','http://www.iso.org/')):
        return uri
    return re.sub(r'/(?:\d{4}(?:-\d{2}-\d{2})?|\d{8})(?=/|$)', '', uri).rstrip('/')


def filing_namespaces(root,resources):
    for name,res in resources.items():
        if name.endswith('_htm.xml') or name.endswith('.xml') and not name.endswith(('_cal.xml','_pre.xml','_def.xml','_lab.xml')):
            raw=(root/res['path']).read_bytes()[:50000]
            marker=re.search(rb'<(?:[\w.-]+:)?xbrl\b[^>]*>',raw,re.I)
            if marker:
                return {p.decode() if p else None:u.decode() for p,u in re.findall(rb'xmlns(?::([^\s=]+))?\s*=\s*["\']([^"\']+)',marker.group())}
    return {}


def canonical_qname(name: str, nsmap: dict) -> str:
    if name.startswith('{'):
        uri,local = name[1:].split('}',1)
    else:
        prefix,local = name.split(':',1) if ':' in name else ('',name)
        uri = nsmap.get(prefix or None,'')
    return namespace_family(uri) + ':' + local


def instance_number(text: str) -> Decimal:
    # Extracted SEC instances already apply inline scale and sign.
    return Decimal(text.strip())


def inline_number(text: str, *, scale='0', sign=None, transform=None, nil=False) -> Decimal | None:
    if nil:
        return None
    if transform and transform.rsplit(':',1)[-1] in ('fixed-zero','zerodash'):
        return Decimal(0)
    cleaned = text.strip().replace('\u00a0','').replace(' ','')
    local = (transform or '').rsplit(':',1)[-1].lower()
    if 'commadecimal' in local or 'comma-decimal' in local:
        cleaned = cleaned.replace('.','').replace(',','.')
    else:
        cleaned = cleaned.replace(',','')
    if cleaned.startswith('(') and cleaned.endswith(')'):
        cleaned = '-' + cleaned[1:-1]
    value = Decimal(cleaned) * Decimal(10) ** int(scale)
    if sign == '-':
        value = -value
    return value


def half_unit(decimals: str | int) -> Decimal:
    if str(decimals) in ('INF','32767'):
        return Decimal(0)
    return Decimal('0.5') * Decimal(10) ** (-int(decimals))


def parse_instance(raw: bytes, *, entity_id: str, reporting_identity: str,
                   group_id: str, document_id: str, accession: str,
                   acceptance_datetime: str, knowledge_date: str,
                   assurance_level: str, as_of: str, taxonomy_replacements=None,reporting_scope='consolidated') -> list[dict]:
    parser = etree.XMLParser(resolve_entities=False, no_network=True, huge_tree=True)
    tree = etree.fromstring(raw, parser)
    contexts = {}
    for ctx in tree.findall(f'{{{XBRLI}}}context'):
        p = ctx.find(f'{{{XBRLI}}}period')
        instant = p.findtext(f'{{{XBRLI}}}instant')
        start,end = (None,instant) if instant else (p.findtext(f'{{{XBRLI}}}startDate'),p.findtext(f'{{{XBRLI}}}endDate'))
        if not end:
            continue  # forever contexts require a distinct measure rule.
        dims = {}
        for member in ctx.iter(f'{{{XBRLDI}}}explicitMember'):
            dims[canonical_qname(member.get('dimension'),member.nsmap)] = canonical_qname(member.text.strip(),member.nsmap)
        for member in ctx.iter(f'{{{XBRLDI}}}typedMember'):
            dims[canonical_qname(member.get('dimension'),member.nsmap)] = etree.tostring(member[0],method='c14n').decode()
        identifier = ctx.find(f'{{{XBRLI}}}entity/{{{XBRLI}}}identifier')
        contexts[ctx.get('id')] = (start,end,json.dumps(dims,sort_keys=True,separators=(',',':')),
            identifier.text.strip() if identifier is not None else None)
    units = {}
    for unit in tree.findall(f'{{{XBRLI}}}unit'):
        direct = unit.findall(f'{{{XBRLI}}}measure')
        if direct:
            units[unit.get('id')] = '*'.join(canonical_qname(m.text.strip(),m.nsmap) for m in direct)
        else:
            num = unit.find(f'{{{XBRLI}}}divide/{{{XBRLI}}}unitNumerator')
            den = unit.find(f'{{{XBRLI}}}divide/{{{XBRLI}}}unitDenominator')
            if num is not None and den is not None:
                units[unit.get('id')] = '*'.join(canonical_qname(m.text.strip(),m.nsmap) for m in num) + '/' + '*'.join(canonical_qname(m.text.strip(),m.nsmap) for m in den)
    output = []
    replacements = taxonomy_replacements or {}
    for rank,node in enumerate(tree):
        if not node.get('contextRef') or node.get('contextRef') not in contexts:
            continue
        start,end,dimensions,cik_context = contexts[node.get('contextRef')]
        duration_text=(node.text or '').strip()
        is_duration=not node.get('unitRef') and bool(re.fullmatch(r'P(?:\d+(?:\.\d+)?Y)?(?:\d+(?:\.\d+)?M)?(?:\d+(?:\.\d+)?D)?',duration_text)) and duration_text!='P'
        unit = 'xbrli:duration' if is_duration else units.get(node.get('unitRef'))
        if not unit:
            continue
        nil = node.get(f'{{{XSI}}}nil') in ('true','1')
        try:
            value = None if nil or is_duration else instance_number(node.text or '')
        except InvalidOperation:
            continue
        namespace,local = node.tag[1:].split('}',1)
        concept = canonical_qname(node.tag,node.nsmap)
        canonical = replacements.get(concept,concept)
        currency_match = re.fullmatch(r'.*:([A-Z]{3})',unit)
        currency = currency_match.group(1) if currency_match else None
        framework = 'ifrs' if 'ifrs' in namespace else 'us_gaap'
        context_entity_id=entity_id
        context_reporting_identity=reporting_identity
        other_entity=False
        if entity_id.startswith('cik:') and cik_context and cik_context.isdigit():
            if cik_context.zfill(10)!=entity_id[4:].zfill(10):
                context_entity_id='cik:'+cik_context.zfill(10)
                context_reporting_identity=context_entity_id
                other_entity=True
        semantic = digest([canonical,context_reporting_identity,start,end,unit,dimensions,framework,reporting_scope])
        fact_id = digest([document_id,rank])
        output.append({'fact_id':fact_id,'semantic_key':semantic,'document_id':document_id,
            'accession':accession,'entity_id':context_entity_id,'group_id':group_id,
            'concept':concept,'canonical_concept':canonical,'taxonomy_namespace':namespace,
            'taxonomy_version':re.search(r'(\d{4}(?:-\d{2}-\d{2})?)/?$',namespace).group(1)
                if re.search(r'(\d{4}(?:-\d{2}-\d{2})?)/?$',namespace) else None,
            'period_start':start,'period_end':end,'unit':unit,'currency':currency,
            'dimensions':dimensions,'accounting_framework':framework,'reporting_scope':reporting_scope,
            'source_perspective':'counterparty' if other_entity else 'reporting_entity','value':value,'is_nil':nil,
            'text_value':duration_text if is_duration and not nil else None,
            'explicit_zero':value == 0 if value is not None else False,
            'decimals':node.get('decimals'),'is_tagged':True,
            'locator':'id:' + node.get('id') if node.get('id') else f'instance_child_rank:{rank}',
            'occurrence_rank':rank,'acceptance_datetime':acceptance_datetime,'knowledge_date':knowledge_date,
            'filing_status':'unclassified' if other_entity else 'filed','assurance_level':assurance_level,
            'location':'financial_statements_or_notes',
            'tier':'E' if other_entity else {'audited':'A','reviewed':'B'}.get(assurance_level,'C'),
            'coverage_state':'unknown' if nil or other_entity else 'explicit_zero' if value == 0 else 'observed',
            'as_of':as_of})
    return output
