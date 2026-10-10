"""Exact identities only; a fund and its manager always remain separate."""
import json,re
from collections import defaultdict
from .database import insert
from .xbrl import digest
from .assembly import rows,exclusion


def normalize(name):
    s=re.sub(r'^the\s+','',name.strip(),flags=re.I).lower()
    s=re.sub(r'[^\w\s]',' ',s)
    s=re.sub(r'\s+',' ',s).strip()
    for long,short in [('corporation','corp'),('incorporated','inc'),('limited','ltd'),('public benefit corporation','pbc')]:
        s=re.sub(r'\b'+long+r'$',short,s)
    return s


def jurisdiction(name,quote):
    # Validation of an already authored party name, not passage extraction.
    expression=r'\s+'.join(re.escape(w) for w in name.split())
    for m in re.finditer(expression,quote,re.I):
        tail=quote[m.end():m.end()+180]
        match=re.match(r'\s*,?\s*(?:a|an)\s+(Delaware|California|Washington|Nevada|Texas|Bermuda|Israeli|Singapore|Cayman Islands)\b',tail,re.I)
        if match:return match.group(1).lower()
    return None


def assemble(db,root,as_of):
    inv=json.loads((root/'work/inventory.json').read_text())
    records=[];index=defaultdict(list);issuer_by_group={}
    proof=json.loads((root/'work/parent_membership_evidence.json').read_text())
    dates={'AVGO': [('Avago Technologies LTD',None,'2016-02-01'),('Broadcom Pte. Ltd.','2016-02-01','2018-04-04'),('Broadcom Inc.','2018-04-04',None)],
           'MRVL':[('MARVELL TECHNOLOGY GROUP LTD',None,'2021-04-20'),('Marvell Technology, Inc.','2021-04-20',None)]}
    # Dates above are evidence decisions, not indicative CIKs or financial values.
    for g,data in inv['groups'].items():
        for cik,issuer in data['issuers'].items():
            meta=issuer['metadata'];eid='cik:'+cik;name=meta['name'];start=end=None
            for n,a,z in dates.get(g,[]):
                if normalize(name)==normalize(n):start,end=a,z
            jurisdiction_code=meta.get('stateOfIncorporation') or None
            row=dict(entity_id=eid,membership_id=digest([eid,g,start,end,'parent']),legal_name=name,normalized_name=normalize(name),
              cik=cik,jurisdiction=jurisdiction_code,entity_status='confirmed',group_id=g,economic_group_id=g,
              consolidation_treatment='parent',membership_start=start,membership_end=end,legal_date=start,
              knowledge_date=as_of[:10],resolution_rule='same_CIK_submissions_and_dated_successor_evidence',
              source_perspective='reporting_entity',as_of=as_of)
            records.append(row);index[normalize(name)].append(row)
            if cik==data['cik']:issuer_by_group[g]=row
            for old in meta.get('formerNames',[]):
                alias=dict(row,alias_key=digest(old),alias=old['name'],alias_start=old.get('from','')[:10] or None,
                           alias_end=old.get('to','')[:10] or None,resolution_rule='same_CIK_formerNames')
                records.append(alias);index[normalize(old['name'])].append(row)
    # The completed redomiciliation also preserves the predecessor as a subsidiary.
    for row in list(records):
        if row.get('alias_key') or row['group_id'] not in dates or not row.get('membership_end'):continue
        after=dict(row,membership_id=digest([row['entity_id'],'subsidiary',row['membership_end']]),
                   consolidation_treatment='consolidated_subsidiary',membership_start=row['membership_end'],membership_end=None,
                   resolution_rule='completed_successor_transaction_distinct_legal_person')
        records.append(after)
    conso=json.loads((root/'work/entity_decisions.json').read_text())
    collection=json.loads((root/'work/collection.json').read_text())
    f=collection['filings'][conso['source_accession']]
    doc=digest([f['resources'][f['metadata']['primaryDocument']]['url']])
    for e in conso['entities']:
        norm=normalize(e['legal_name']);eid='legal:'+digest([norm,'consolidation_note_identity'])
        row=dict(entity_id=eid,membership_id=digest([eid,e['legal_date'],'SPCX']),legal_name=e['legal_name'],normalized_name=norm,
            entity_status='confirmed',group_id='SPCX',economic_group_id='SPCX',consolidation_treatment=e['consolidation_treatment'],
            combination_method='common_control_combination',membership_start=e['legal_date'],legal_date=e['legal_date'],
            common_control_start=e['common_control_start'],knowledge_date=conso['knowledge_date'],
            resolution_rule='published_consolidation_note_distinct_legal_identity',evidence_document_id=doc,
            evidence_locator=f"rawbytes:{conso['raw_byte_start']}:{conso['raw_byte_end']}",source_perspective='reporting_entity',as_of=as_of)
        records.append(row);index[norm].append(row)
    evidence=defaultdict(list)
    observations=rows(db,'SELECT * FROM usable_observations')
    for o in observations:
        for field in ['counterparty','payer','receiver','ultimate_obligor']:
            name=o.get(field)
            if not name or name in inv['groups']:continue
            norm=normalize(name);j=jurisdiction(name,o['quote'])
            evidence[(norm,j)].append((name,o))
    for (norm,j),mentions in sorted(evidence.items(),key=str):
        if norm in index:continue
        independent={o['accession'] for _,o in mentions}
        full=bool(re.search(r'\b(?:inc|corp|llc|lp|ltd|plc|pbc)\b$',norm))
        confirmed=bool(full and j and len(independent)>=2)
        name,o=mentions[0];eid='legal:'+digest([norm,j])
        row=dict(entity_id=eid,membership_id='standalone',legal_name=name,normalized_name=norm,jurisdiction=j,
          entity_status='confirmed' if confirmed else 'pending',economic_group_id=eid,consolidation_treatment='parent' if confirmed else 'undetermined',
          knowledge_date=o['knowledge_date'],resolution_rule='same_normalized_full_name_and_jurisdiction_two_independent_filings' if confirmed else 'identity_or_control_not_established',
          evidence_document_id=o['document_id'],evidence_locator=o['locator'],source_perspective='counterparty',as_of=as_of)
        records.append(row);index[norm].append(row)
        if not confirmed:exclusion(db,as_of,'pending_entity','entity',eid,entity_id=eid,counterparty_id=eid,
            detail='Name retained without alias, jurisdiction or consolidation guess.',coverage_state='unknown')
    for row in records:insert(db,'entities',row)
    def resolve(name,o):
        if not name:return None
        if name==o['group_id']:
            # Explicit author-supplied issuer shorthand, identified by the filing CIK.
            own=next((r for r in records if r['entity_id']==o['entity_id'] and r.get('alias_key') is None),None)
            return own or issuer_by_group[o['group_id']]
        options=index.get(normalize(name),[])
        ids={r['entity_id'] for r in options}
        if len(ids)==1:return options[0]
        j=jurisdiction(name,o['quote'])
        options=[r for r in options if r.get('jurisdiction')==j and j]
        return options[0] if len({r['entity_id'] for r in options})==1 else None
    return records,observations,resolve
