from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import json,re,unicodedata
from lxml import etree
from .text import parse_html,render,normalize_space
from .xbrl import digest
from .controls import XLINK,LINK


def label_key(text: str) -> str:
    text=unicodedata.normalize('NFKC',text).lower()
    text=re.sub(r'\.{2,}',' ',text)
    text=re.sub(r'\([a-z0-9]\)|\[\d+\]','',text)
    text=re.sub(r'\s*\(related party.*?\)','',text,flags=re.S)
    text=re.sub(r', net of allowance for credit losses.*','',text,flags=re.S)
    text=text.split(';',1)[0]
    # Issuer labels use "loss" in a loss-only quarter and "income (loss)" in
    # the annual table. These grammatical variants do not change a quantity.
    text=text.replace('income (loss)','loss').replace('provision for (benefit from)','provision for')
    text=re.sub(r'\bbeginning of (?:year|the period)\b','beginning of period',text)
    text=re.sub(r'\bend of (?:year|the period)\b','end of period',text)
    return re.sub(r'[^a-z0-9]+',' ',text).strip()


def statement_roles(meta):
    result={}
    for r in meta['report'].values():
        if r.get('groupType')!='statement':continue
        title=r.get('shortName','').lower()
        kind='balance_sheet' if 'balance sheet' in title else 'cash_flow' if 'cash flow' in title else 'income_statement' if 'operations' in title else None
        if kind:result[r['role']]=kind
    return result


def parse_primary_tables(root: Path):
    state=json.loads((root/'work/collection.json').read_text())
    annual=state['filings']['0001628280-26-042639'];quarter=state['filings']['0001628280-26-052535']
    resource=annual['resources'][annual['metadata']['primaryDocument']];raw=(root/resource['path']).read_bytes()
    bounds={'balance_sheet':(6704012,6824776),'income_statement':(6824776,raw.find(b'Consolidated Statements of Comprehensive',6824776)),
        'cash_flow':(7158566,7336456)}
    meta=next(iter(json.loads((root/quarter['resources']['MetaLinks.json']['path']).read_text())['instance'].values()))
    roles=statement_roles(meta);labels={};preferred={}
    for name,res in quarter['resources'].items():
        if not name.endswith('_pre.xml'):continue
        tree=etree.fromstring((root/res['path']).read_bytes(),etree.XMLParser(resolve_entities=False,no_network=True))
        for link in tree.iter(f'{{{LINK}}}presentationLink'):
            kind=roles.get(link.get(f'{{{XLINK}}}role'))
            if not kind:continue
            loc={n.get(f'{{{XLINK}}}label'):n.get(f'{{{XLINK}}}href').split('#')[-1].replace('_',':',1) for n in link if n.tag==f'{{{LINK}}}loc'}
            for arc in link:
                if arc.tag==f'{{{LINK}}}presentationArc':preferred[(kind,loc.get(arc.get(f'{{{XLINK}}}to')))]=arc.get('preferredLabel','').split('/')[-1]
    for name,tag in meta['tag'].items():
        if tag.get('xbrltype')!='monetaryItemType':continue
        for role in tag.get('presentation',[]):
            kind=roles.get(role)
            if not kind:continue
            for label_role,value in tag.get('lang',{}).get('en-us',{}).get('role',{}).items():
                if label_role=='documentation' or not isinstance(value,str):continue
                concept=name.replace('_',':',1)
                labels.setdefault((kind,label_key(value)),set()).add(concept)
    rows=[];rejections=[];native=[]
    for kind,(start,end) in bounds.items():
        if end<start:rejections.append({'kind':kind,'reason':'heading_bound_not_found'});continue
        for table in parse_html(raw[start:end]).iter('table'):
            text=normalize_space(render(table))
            if len(text)<300:continue
            years=[]
            for year in re.findall(r'\b202[345]\b',text[:3500]):
                if year not in years:years.append(year)
            if len(years)<2:continue
            for tr in table.xpath('./tr|./tbody/tr|./thead/tr'):
                strings=[normalize_space(render(c)) for c in tr.xpath('./td|./th')]
                first=next((s for s in strings if s),'')
                if not first:continue
                key=label_key(first);numeric=[]
                for value in strings[1:]:
                    stripped=value.replace('$','').replace(',','').strip()
                    if stripped in ('-','–','—'):numeric.append(Decimal(0));continue
                    if not re.fullmatch(r'\(?-?\d+(?:\.\d+)?\)?',stripped) or stripped in years:continue
                    number=Decimal(stripped.strip('()'))
                    if stripped.startswith('('):number=-number
                    numeric.append(number)
                if len(numeric)!=len(years):continue
                native.append({'kind':kind,'label_key':key,'display_values':dict(zip(years,map(str,numeric)))})
                concepts=labels.get((kind,key),set())
                if len(concepts)!=1:
                    rejections.append({'kind':kind,'label':first,'reason':'unmatched_label' if not concepts else 'ambiguous_label_match','concepts':sorted(concepts)});continue
                concept=next(iter(concepts));negated=preferred.get((kind,concept),'').startswith('negated')
                for year,value in zip(years,numeric):
                    if negated:value=-value
                    rows.append({'concept':concept,'label':first,'statement_kind':kind,'period_start':None if kind=='balance_sheet' else year+'-01-01',
                        'html_row_rank':len(native)-1,
                        'period_end':year+'-12-31','value':str(value*Decimal(1000000)),'decimals':'-6',
                        'raw_byte_start':start,'raw_byte_end':end,'source_path':resource['path'],'display_sign_role':preferred.get((kind,concept)),
                        'accession':annual['metadata']['accessionNumber'],'is_tagged':False,
                        'mapping_rule':'issuer_label_and_statement_role_with_documented_loss_grammar_and_metadata_clause_normalization',
                        'reporting_scope':'as_if_combined','assurance_level':'audited'})
    result={'source_accession':annual['metadata']['accessionNumber'],'rows':rows,'rejections':rejections,'native_rows':native,
        'status':'candidate_mapping_pending_internal_controls_and_comparative_reconciliation','annual_series_admitted':False}
    (root/'work/spcx_annual_candidates.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    print(json.dumps({'candidate_rows':len(rows),'rejections':len(rejections),'annual_series_admitted':False}))
    return result

if __name__=='__main__':parse_primary_tables(Path('.').resolve())
