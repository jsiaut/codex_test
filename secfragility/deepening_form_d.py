"""Structured Form D disclosure: a vehicle offering is never underlying-company cash."""
from pathlib import Path
import json, re
from datetime import datetime
from zoneinfo import ZoneInfo
from lxml import etree
from .deepening_sources import client, fetch
from .network import atomic_json


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


if __name__=='__main__':collect(Path('.').resolve())
