from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import json
import hashlib
import re
import yaml
import zstandard
from .archives import filing_base
from .database import create,export,sql_literal,table_counts
from .evidence import periodic_assurance,tier,filing_status
from .mapping import build_mapping,apply_mapping
from .xbrl import parse_instance,digest
from .text import parse_html,local_tag,render,normalize_space
from .metadata import load as load_metadata


def load_jsonl(db,table: str,path: Path):
    if path.stat().st_size:
        db.execute(f'INSERT INTO {table} BY NAME SELECT * FROM read_json({sql_literal(str(path))}, format="newline_delimited", maximum_object_size=33554432)')


def write_jsonl(path: Path,rows):
    with path.open('w') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False,default=str,sort_keys=True)+'\n')


def companyfacts_rows(root: Path,collection: dict,inventory: dict,as_of: str):
    replacements=json.loads((root/'work/deprecations.json').read_text())['mapping'] if (root/'work/deprecations.json').exists() else {}
    for cik,source in collection['companyfacts'].items():
        group=source['group']
        meta={r['accessionNumber']:r for issuer in inventory['groups'][group]['issuers'].values() for r in issuer['filings']}
        data=json.loads((root/source['path']).read_text())
        document_id=digest([source['url'],as_of])
        for taxonomy,concepts in data.get('facts',{}).items():
            for concept,entry in concepts.items():
                for unit,series in entry.get('units',{}).items():
                    for rank,fact in enumerate(series):
                        accession=fact['accn']; form=fact['form']
                        context=meta.get(accession,{})
                        start,end=fact.get('start'),fact['end']
                        canonical=replacements.get(taxonomy+':'+concept,taxonomy+':'+concept)
                        normalized_unit='http://www.xbrl.org/2003/iso4217:'+unit if re.fullmatch('[A-Z]{3}',unit) else (
                            'http://www.xbrl.org/2003/iso4217:USD/http://www.xbrl.org/2003/instance:shares' if unit=='USD/shares' else
                            'http://www.xbrl.org/2003/instance:'+unit)
                        assurance=periodic_assurance(form)
                        evidence_tier={'audited':'A','reviewed':'B'}.get(assurance,'E')
                        value=Decimal(str(fact['val']))
                        framework='ifrs' if taxonomy.startswith('ifrs') else 'us_gaap'
                        scope='as_if_combined' if group=='SPCX' and fact['filed']>='2026-05-20' else 'consolidated'
                        semantic=digest([canonical,'reporter:'+group,start,end,normalized_unit,'{}',framework,scope])
                        yield {'fact_id':digest(['companyfacts',cik,accession,taxonomy+':'+concept,unit,start,end]),
                            'semantic_key':semantic,'document_id':document_id,'accession':accession,
                            'entity_id':'cik:'+cik,'group_id':group,'concept':taxonomy+':'+concept,
                            'canonical_concept':canonical,'taxonomy_namespace':taxonomy,'taxonomy_version':None,
                            'period_start':start,'period_end':end,'unit':normalized_unit,
                            'currency':unit if re.fullmatch('[A-Z]{3}',unit) else None,'dimensions':'{}',
                            'accounting_framework':framework,'reporting_scope':scope,
                            'source_perspective':'reporting_entity','value':value,'is_nil':False,'explicit_zero':value==0,
                            'is_tagged':True,'locator':f'companyfacts:{taxonomy}/{concept}/units/{unit};accn={accession};start={start};end={end}',
                            'occurrence_rank':0,'document_rank':-1,
                            'acceptance_datetime':context.get('acceptanceDateTime',fact['filed']+'T23:59:59+00:00'),
                            'knowledge_date':fact['filed'],'filing_status':'filed' if evidence_tier!='E' else 'unclassified',
                            'assurance_level':assurance,'location':'companyfacts_unbounded',
                            'tier':evidence_tier,'coverage_state':'explicit_zero' if value==0 else 'observed','as_of':as_of}


def instance_rows(root: Path,collection: dict,as_of: str,mappings: list[dict]):
    replacements=json.loads((root/'work/deprecations.json').read_text())['mapping'] if (root/'work/deprecations.json').exists() else {}
    for accession,filing in collection['filings'].items():
        if filing['status']!='collected':
            continue
        row=filing['metadata'];group=filing['group'];resources=filing['resources']
        meta=load_metadata(root,resources,accession)
        mapping=build_mapping(meta,yaml.safe_load((root/'config.yaml').read_text()),group,accession,replacements) if meta else []
        mappings.extend(mapping)
        discovery=json.loads((root/filing['discovery_path']).read_text()) if filing.get('discovery_path') else {}
        primary_ids=set()
        primary_roles={}
        primary_parenthetical={}
        primary_document=row.get('primaryDocument')
        primary_known=False
        if primary_document in resources:
            tree=parse_html((root/resources[primary_document]['path']).read_bytes())
            nodes=list(tree.iter())
            numeric=[n for n in nodes if local_tag(n) in ('ix:nonfraction','ix:fraction')]
            primary_known=bool(numeric)
            first_balance=next((i for i,n in enumerate(nodes) if local_tag(n) in ('ix:nonfraction','ix:fraction')
                and (n.get('name') or '').split(':')[-1]=='Assets'
                and not any(local_tag(a) in ('ix:hidden','ix:header','ix:nonnumeric','ix:continuation') for a in n.iterancestors())),0)
            note_boundary=next((i for i,n in enumerate(nodes) if i>first_balance and
                local_tag(n) in ('span','p','div','b','strong','font','h1','h2','h3') and
                re.match(r'^\s*(?:Note\s*1\s*(?:[.\-–—:]|\bNature\b)|Notes\s+to\s+(?:the\s+)?(?:Condensed\s+)?Consolidated)',n.text or '',re.I)
                and len(n.text or '')<200 and not any(local_tag(a)=='a' for a in n.iterancestors())),None)
            positions={n:i for i,n in enumerate(nodes)}
            statement_role=None
            for node in nodes:
                heading=re.sub(r'\s+',' ',(node.text or '').strip())
                if len(heading)<220 and re.match(r'^(?:CONDENSED\s+)?CONSOLIDATED\s+',heading,re.I) and not any(local_tag(a)=='a' for a in node.iterancestors()):
                    if re.search(r'BALANCE\s+SHEETS?',heading,re.I):statement_role='balance_sheet'
                    elif re.search(r'STATEMENTS?\s+OF\s+CASH\s+FLOWS?',heading,re.I):statement_role='cash_flow'
                    elif re.search(r'STATEMENTS?\s+OF\s+(?:OPERATIONS|INCOME|EARNINGS|LOSS)',heading,re.I):statement_role='income_statement'
                    elif re.search(r'STATEMENTS?\s+OF.*(?:EQUITY|STOCK)',heading,re.I):statement_role='equity_statement'
                    elif re.search(r'STATEMENTS?\s+OF\s+COMPREHENSIVE',heading,re.I):statement_role='comprehensive_income_statement'
                if local_tag(node) not in ('ix:nonfraction','ix:fraction'):continue
                if node.get('id') and note_boundary is not None and positions[node]<note_boundary and not any(local_tag(a) in ('ix:nonnumeric','ix:continuation','ix:hidden','ix:header') for a in node.iterancestors()):
                    primary_ids.add(node.get('id'))
                    primary_roles[node.get('id')]=statement_role
                    cells=[a for a in node.iterancestors() if local_tag(a) in ('td','th')]
                    row_nodes=[a for a in node.iterancestors() if local_tag(a)=='tr']
                    if cells and row_nodes:
                        row_cells=row_nodes[0].xpath('./td|./th')
                        label_cell=next((c for c in row_cells if re.search(r'[A-Za-z]',normalize_space(render(c)))),None)
                        primary_parenthetical[node.get('id')]=cells[0] is label_cell
                    else:primary_parenthetical[node.get('id')]=None
        for name,resource in resources.items():
            if name not in discovery.get('instances',[]) and not name.endswith('_htm.xml'):
                continue
            if periodic_assurance(row['form'])=='unknown':
                # Nonperiodic forms require period/excerpt assurance analysis.
                assurance='unknown'
            else:
                assurance=periodic_assurance(row['form'])
            facts=parse_instance((root/resource['path']).read_bytes(),entity_id='cik:'+row['cik'],
                reporting_identity='reporter:'+group,group_id=group,document_id=digest([resource['url']]),
                accession=accession,acceptance_datetime=row['acceptanceDateTime'],knowledge_date=row['filingDate'],
                assurance_level=assurance,as_of=as_of,reporting_scope='as_if_combined' if group=='SPCX' else 'consolidated',taxonomy_replacements=replacements)
            apply_mapping(facts,mapping)
            for fact in facts:
                fact['primary_statement_occurrence']=(fact['locator'][3:] in primary_ids) if primary_known and fact['locator'].startswith('id:') else None
                fact['primary_statement_role']=primary_roles.get(fact['locator'][3:]) if fact['locator'].startswith('id:') else None
                fact['primary_statement_parenthetical']=primary_parenthetical.get(fact['locator'][3:]) if fact['locator'].startswith('id:') else None
            if assurance=='unknown':
                for fact in facts:
                    fact.update(filing_status='unclassified',tier='E',coverage_state='not_processed')
            yield from facts


def document_rows(root: Path,collection: dict,as_of: str):
    for cik,source in collection['companyfacts'].items():
        version=as_of.replace(':','-').replace('+','_')
        p=root/'cache/api'/hashlib.sha256(source['url'].encode()).hexdigest()/(version+'.bin.zst')
        raw=zstandard.ZstdDecompressor().decompress(p.read_bytes())
        yield {'document_id':digest([source['url'],as_of]),'group_id':source['group'],'entity_id':'cik:'+cik,
            'cik':cik,'url':source['url'],'cache_path':str(p.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest(),
            'filing_status':'unclassified','document_kind':'api_aggregate',
            'byte_count':len(raw),'parse_status':'observed','as_of':as_of}
    for accession,filing in collection['filings'].items():
        row=filing['metadata']
        for name,res in filing['resources'].items():
            raw=(root/res['path']).read_bytes()
            status=filing_status(row['form'])
            assurance=periodic_assurance(row['form'])
            yield {'document_id':digest([res['url']]),'group_id':filing['group'],
                'entity_id':'cik:'+row['cik'],'cik':row['cik'],'accession':accession,
                'url':res['url'],'cache_path':res['path'],'sha256':hashlib.sha256(raw).hexdigest(),
                'form':row['form'],'filing_status':status,'assurance_level':assurance,
                'document_kind':'instance' if name.endswith('_htm.xml') else 'metadata' if name.endswith(('.xml','.json','.xsd')) else 'unclassified',
                'acceptance_datetime':row['acceptanceDateTime'],'filing_date':row['filingDate'],
                'knowledge_date':row['filingDate'],'byte_count':len(raw),'parse_status':'observed','as_of':as_of}


def rebuild(root: Path):
    config=yaml.safe_load((root/'config.yaml').read_text())
    run=json.loads((root/'work/run.json').read_text());as_of=run['as_of']
    inventory=json.loads((root/'work/inventory.json').read_text())
    collection=json.loads((root/'work/collection.json').read_text())
    db=create(root)
    scratch=root/'work/rebuild';scratch.mkdir(parents=True,exist_ok=True)
    mappings=[]
    # Parse and calculate are entirely reconstructed; source files are immutable.
    write_jsonl(scratch/'documents.jsonl',document_rows(root,collection,as_of))
    load_jsonl(db,'documents',scratch/'documents.jsonl')
    write_jsonl(scratch/'companyfacts.jsonl',companyfacts_rows(root,collection,inventory,as_of))
    # Companyfacts can contain identical repeats: occurrence key is semantic
    # per accession, as required, independent of transient array order.
    db.execute(f'''INSERT INTO facts BY NAME
        SELECT * EXCLUDE (value,coverage_state,explicit_zero),
          CASE WHEN count(DISTINCT value) OVER (PARTITION BY fact_id)>1 THEN NULL ELSE value END AS value,
          CASE WHEN count(DISTINCT value) OVER (PARTITION BY fact_id)>1 THEN 'conflicting' ELSE coverage_state END AS coverage_state,
          CASE WHEN count(DISTINCT value) OVER (PARTITION BY fact_id)>1 THEN false ELSE explicit_zero END AS explicit_zero
        FROM read_json({sql_literal(str(scratch/"companyfacts.jsonl"))}, format="newline_delimited")
        QUALIFY row_number() OVER (PARTITION BY fact_id ORDER BY fact_id)=1''')
    write_jsonl(scratch/'instances.jsonl',instance_rows(root,collection,as_of,mappings))
    load_jsonl(db,'facts',scratch/'instances.jsonl')
    if (root/'work/spcx_annual_validation.json').exists():
        from .annual_html import rows as annual_rows
        write_jsonl(scratch/'annual_html.jsonl',annual_rows(root,collection,as_of,mappings))
        load_jsonl(db,'facts',scratch/'annual_html.jsonl')
    (root/'work/concept_mappings.json').write_text(json.dumps(mappings,ensure_ascii=False,indent=2))
    export(db,root/'tables')
    print(json.dumps(table_counts(db)))
    return db


if __name__=='__main__':
    rebuild(Path('.').resolve())
