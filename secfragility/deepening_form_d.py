"""Structured Form D disclosure: a vehicle offering is never underlying-company cash."""
from pathlib import Path
import json, re
from datetime import datetime
from zoneinfo import ZoneInfo
from lxml import etree
from .deepening_sources import client, fetch
from .network import atomic_json
from .xbrl import digest
from .database import insert


def collect(root):
    sec=client(root)
    registry=root/'work/deepening_form_d_filings.json'
    saved=json.loads(registry.read_text()) if registry.exists() else {}
    hits={h['_id']:h for h in json.loads((root/'work/deepening_form_d_hits.json').read_text())}
    try:
        for key,h in sorted(hits.items()):
            if key in saved:continue
            s=h['_source'];acc=s['adsh'];cik=s['ciks'][0];name=key.split(':',1)[1]
            base=f'https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace("-","")}/'
            path=fetch(root,sec,base+name)
            tree=etree.fromstring(path.read_bytes(),etree.XMLParser(resolve_entities=False,no_network=True))
            header=fetch(root,sec,base+acc+'-index-headers.html')
            match=re.search(rb'ACCEPTANCE-DATETIME[^0-9]*(\d{14})',header.read_bytes(),re.I)
            if not match:raise ValueError('Official acceptance timestamp missing: '+acc)
            accepted=datetime.strptime(match[1].decode(),'%Y%m%d%H%M%S').replace(tzinfo=ZoneInfo('America/New_York')).isoformat()
            def value(xpath):return tree.findtext(xpath)
            fields={k:value(x) for k,x in dict(issuer_name='primaryIssuer/entityName',
                entity_type='primaryIssuer/entityType',jurisdiction='primaryIssuer/jurisdictionOfInc',
                industry='offeringData/industryGroup/industryGroupType',
                investment_fund_type='offeringData/industryGroup/investmentFundInfo/investmentFundType',
                total_offering_amount='offeringData/offeringSalesAmounts/totalOfferingAmount',
                total_amount_sold='offeringData/offeringSalesAmounts/totalAmountSold',
                total_remaining='offeringData/offeringSalesAmounts/totalRemaining',
                first_sale='offeringData/typeOfFiling/dateOfFirstSale/value',
                first_sale_yet_to_occur='offeringData/typeOfFiling/dateOfFirstSale/yetToOccur',
                is_amendment='offeringData/typeOfFiling/newOrAmendment/isAmendment').items()}
            saved[key]=dict(search_subject=h['subject'],source=s,url=base+name,path=str(path.relative_to(root)),
                header_path=str(header.relative_to(root)),acceptance_datetime=accepted,fields=fields,
                underlying_primary_cash_established=False)
            atomic_json(registry,saved)
            if len(saved)%20==0:print(json.dumps(dict(collected=len(saved),unique_candidates=len(hits))),flush=True)
    finally:sec.close()
    print(json.dumps(dict(collected=len(saved),unique_candidates=len(hits))),flush=True)


def load(db,root,as_of):
    import hashlib
    from decimal import Decimal
    from .reports import csv_write
    registry=root/'work/deepening_form_d_filings.json'
    if not registry.exists():return
    manifest=json.loads((root/'work/deepening_source_manifest.json').read_text());disclosures=[]
    def add(table,row):
        pk='document_id' if table=='documents' else 'fact_id'
        if not db.execute(f'SELECT count(*) FROM {table} WHERE {pk}=?',[row[pk]]).fetchone()[0]:insert(db,table,row)
    for key,r in sorted(json.loads(registry.read_text()).items()):
        s=r['source'];f=r['fields'];acc=s['adsh'];cik=s['ciks'][0];url=r['url'];did=digest([url])
        raw=(root/r['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=manifest[url]['sha256']:raise ValueError('Form D bytes changed')
        original=etree.fromstring(raw,etree.XMLParser(resolve_entities=False,no_network=True))
        original_cik=original.findtext('primaryIssuer/cik')
        if original_cik and int(original_cik)!=int(cik):raise ValueError('Form D issuer CIK mismatch')
        add('documents',dict(document_id=did,group_id='external:'+cik,entity_id='cik:'+cik,cik=cik,
            accession=acc,document_rank=0,document_rank_source='primary_XML_form',url=url,cache_path=r['path'],
            sha256=manifest[url]['sha256'],form=s['file_type'],filing_status='filed',assurance_level='not_applicable',
            location='Form_D_Item_13',document_kind='structured_offering_disclosure',tier='C',
            acceptance_datetime=r['acceptance_datetime'],filing_date=s['file_date'],knowledge_date=s['file_date'],
            byte_count=len(raw),parse_status='observed',as_of=as_of))
        for field,tag in [('total_offering_amount','totalOfferingAmount'),('total_amount_sold','totalAmountSold')]:
            value=f[field];numeric=Decimal(value) if value is not None and re.fullmatch(r'\d+(?:\.\d+)?',value) else None
            fid=digest([url,tag]);xpath='/edgarSubmission/offeringData/offeringSalesAmounts/'+tag
            add('facts',dict(fact_id=fid,semantic_key=offering_key(cik,f['first_sale'],acc,tag),document_id=did,accession=acc,
                entity_id='cik:'+cik,group_id='external:'+cik,concept='secFormD:'+tag,canonical_concept='secFormD:'+tag,
                taxonomy_namespace='SEC_Form_D_XML',model_quantity='form_d_offering_amount',period_end=s['file_date'],
                unit='USD',currency='USD',dimensions=json.dumps(dict(first_sale=f['first_sale'],issuer_name=f['issuer_name'],
                    kind=field,underlying_primary_cash_established=False),sort_keys=True),accounting_framework='unknown',
                reporting_scope='issuer_offering',source_perspective='reporting_entity',value=numeric,text_value=value,
                is_nil=False,explicit_zero=numeric==0,decimals=None,
                is_tagged=False,locator='XPath:'+xpath,occurrence_rank=1 if field=='total_offering_amount' else 2,
                document_rank=0,document_rank_source='primary_XML_form',source_document_id=did,
                acceptance_datetime=r['acceptance_datetime'],knowledge_date=s['file_date'],filing_status='filed',
                assurance_level='not_applicable',location='Form_D_Item_13',tier='C',coverage_state='explicit_zero' if numeric==0 else 'observed' if numeric is not None else 'unknown',
                mapping_rule='original_Form_D_XML_Item_13_in_US_dollars',mapping_evidence='https://www.sec.gov/files/formd.pdf#Item13',as_of=as_of))
            disclosures.append(dict(cik=cik,issuer_name=f['issuer_name'],entity_type=f['entity_type'],jurisdiction=f['jurisdiction'],
                industry=f['industry'],first_sale=f['first_sale'],kind=field,value=numeric,raw_value=value,
                accession=acc,filing_date=s['file_date'],url=url,fact_id=fid,search_subject=r['search_subject'],
                underlying_primary_cash_established=False))
    csv_write(root/'form_d_disclosures.csv',disclosures)


def offering_key(cik,first_sale,accession,field):
    # Without a first-sale date we cannot establish that two offerings coincide.
    return digest([cik,first_sale if first_sale else 'unresolved:'+accession,field])


def measures(db,root,as_of):
    """Latest disclosure per issuer/first sale, not the sum of D and D/A."""
    db.execute('''CREATE OR REPLACE TEMP TABLE form_d_latest AS
      SELECT *,row_number() OVER(PARTITION BY entity_id,semantic_key ORDER BY knowledge_date DESC,
        acceptance_datetime DESC,accession DESC) AS offering_version
      FROM facts WHERE canonical_concept LIKE 'secFormD:%' AND knowledge_date<=?::DATE
        AND acceptance_datetime<=?::TIMESTAMPTZ''',[as_of[:10],as_of])
    for view in ('as_known','revised'):
        db.execute(f'''INSERT INTO measures
          (measure,group_id,entity_id,period_start,period_end,view,as_of,information_cutoff,breakdown_key,
           value,unit,status,nd_reason,coverage_state,knowledge_date,lineage,evidence_profile,tier,source_perspective,accounting_framework)
          SELECT 'form_d_offering_amount',group_id,entity_id,'none',period_end::VARCHAR,'{view}',?::TIMESTAMPTZ,
            ?::TIMESTAMPTZ,dimensions||'|'||accession,value,unit,
            CASE WHEN value IS NULL THEN 'not_determinable' ELSE 'computed' END,
            CASE WHEN value IS NULL THEN 'indefinite_or_missing_offering_amount' END,coverage_state,knowledge_date,
            to_json([fact_id]),to_json([tier]),2,source_perspective,accounting_framework
          FROM form_d_latest WHERE offering_version=1''',[as_of,as_of])
    # Structured amendments refer to the same offering; retaining raw facts does
    # not turn cumulative amounts into successive financing events.
    db.execute('''INSERT INTO links(link_id,edge_kind,relation_type,amount_a_id,amount_b_id,resolved,resolution_evidence,as_of)
      SELECT sha256(a.fact_id||b.fact_id||'same_Form_D_offering'),'relation','covers',a.fact_id,b.fact_id,true,
       'Same issuer CIK, first-sale date and Item 13 field; newer disclosure covers older cumulative disclosure.',?::TIMESTAMPTZ
      FROM form_d_latest a JOIN form_d_latest b ON a.entity_id=b.entity_id AND a.semantic_key=b.semantic_key
      WHERE a.offering_version=1 AND b.offering_version>1
        AND json_extract_string(a.dimensions,'$.first_sale') IS NOT NULL''',[as_of])


if __name__=='__main__':collect(Path('.').resolve())
