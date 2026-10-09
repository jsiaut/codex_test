from pathlib import Path
import json,yaml
from .xbrl import digest
from .mapping import build_mapping,apply_mapping


def rows(root:Path,collection:dict,as_of:str,mappings:list):
    validation=json.loads((root/'work/spcx_annual_validation.json').read_text())
    if not validation['annual_series_admitted']:return
    annual=collection['filings'][validation['source_accession']];m=annual['metadata'];res=annual['resources'][m['primaryDocument']]
    quarter=collection['filings']['0001628280-26-052535']
    meta=json.loads((root/quarter['resources']['MetaLinks.json']['path']).read_text())
    mapping=build_mapping(meta,yaml.safe_load((root/'config.yaml').read_text()),'SPCX',m['accessionNumber'])
    for choice in mapping:
        choice['rule']='D1_annual_html_label_correspondence_to_quarter_mapping'
        choice['mapping_source_accession']='0001628280-26-052535'
    mappings.extend(mapping);document_id=digest([res['url']])
    for rank,r in enumerate(validation['rows']):
        unit='http://www.xbrl.org/2003/iso4217:USD'
        fact={'fact_id':digest(['annual_html',document_id,r['statement_kind'],r.get('html_row_rank',rank),r['period_end']]),
            'semantic_key':digest([r['concept'],'reporter:SPCX',r['period_start'],r['period_end'],unit,'{}','us_gaap','as_if_combined']),
            'document_id':document_id,'accession':m['accessionNumber'],'entity_id':'cik:'+m['cik'],'group_id':'SPCX',
            'concept':r['concept'],'canonical_concept':r['concept'],'model_quantity':None,'taxonomy_namespace':'issuer_label_correspondence',
            'period_start':r['period_start'],'period_end':r['period_end'],'unit':unit,'currency':'USD','dimensions':'{}',
            'accounting_framework':'us_gaap','reporting_scope':'as_if_combined','source_perspective':'reporting_entity',
            'value':r['value'],'is_nil':False,'explicit_zero':r['value'] in ['0','-0'],'decimals':r['decimals'],
            'is_tagged':False,'locator':f"rawbytes:{r['raw_byte_start']}:{r['raw_byte_end']};label={r['label']};year={r['period_end'][:4]}",
            'primary_statement_occurrence':True,'primary_statement_role':r['statement_kind'],'occurrence_rank':rank,'document_rank':0,
            'acceptance_datetime':m['acceptanceDateTime'],'knowledge_date':m['filingDate'],'filing_status':'filed','assurance_level':'audited',
            'location':'annual_audited_statements_in_424B4','tier':'A','coverage_state':'explicit_zero' if r['value'] in ['0','-0'] else 'observed',
            'recast_cause':'common_control_combination','as_of':as_of}
        apply_mapping([fact],mapping)
        yield fact
