"""Personally authored transaction layer, preserving the eight-table baseline.

The analytical ledger is an explicit sidecar: roles, payment conditions, phases,
amount bases and gaps cannot be compressed into a single monetary graph edge.
Only admissible, personally attributed quantities enter the eight core tables.
"""
from pathlib import Path
from datetime import datetime
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
import argparse, csv, hashlib, json, re
from functools import lru_cache
from lxml import html
from .database import create, connect, insert, bulk_insert, export, TABLES, sql_literal, table_counts
from .xbrl import digest, inline_number
from .text import normalize_html
from .observations import validate_semantics
from .operation_sources import BASE, read, save, sha

VARIANT = 'operation_dependencies_v1'

def customer_share(a,b):
    if any(a[k]!=b[k] for k in ('group_id','entity_id','period_start','period_end','accounting_framework','currency')):
        raise ValueError('Derived quantity combines incompatible periods/scopes/currencies')
    if any(r['tier'] not in ('A','B','C') or r['stage']!='recognized' for r in (a,b)):
        raise ValueError('Derived ratio needs recognized filed financial quantities')
    numerator,denominator=Decimal(a['amount']),Decimal(b['amount'])
    if not 0<=numerator<=denominator or denominator<=0:raise ValueError('Invalid customer revenue numerator/denominator')
    with localcontext() as ctx:
        ctx.prec=60;value=(numerator/denominator).quantize(Decimal('.000001'),rounding=ROUND_HALF_EVEN)
    return numerator,denominator,value

@lru_cache(maxsize=1)
def catalog(root):
    path=Path(root)/BASE/'source_manifest.json'
    return {s['key']:s for s in read(path)}

@lru_cache(maxsize=32)
def served(root,key):
    source=catalog(root)[key];raw=(Path(root)/source['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Source SHA differs: '+key)
    return raw,normalize_html(raw)

@lru_cache(maxsize=1)
def native_catalog(root):
    path=Path(root)/BASE/'native_catalog.jsonl'
    return [json.loads(line) for line in path.read_text().splitlines()]

def author_record(root,key,quantity,quote,finding,*,inline=None,binding_quote=None,**extra):
    """Validate an analyst-selected quotation and optional native inline ID."""
    root=Path(root);source=catalog(str(root))[key];raw,text=served(str(root),key)
    if isinstance(quote,tuple):
        start=text.index(quote[0]);end=text.index(quote[1],start)+len(quote[1]);quote=text[start:end]
    fact=None
    if inline:
        selected=[f for f in native_catalog(str(root)) if f['accession']==source['accession'] and f['locator']=='id:'+inline]
        if len(selected)!=1:raise ValueError('Native occurrence absent or ambiguous: '+inline)
        fact=selected[0]
        tree=html.fromstring(raw);nodes=tree.xpath('//*[@id=$ident]',ident=inline)
        if len(nodes)!=1:raise ValueError('Inline original absent or ambiguous')
        node=nodes[0]
        parsed=inline_number(node.text_content(),scale=node.get('scale','0'),sign=node.get('sign'),transform=node.get('format'))
        if parsed!=Decimal(fact['value']):raise ValueError('Inline amount/scale differs from native instance')
        # Exact identity, namespace, unit and context must agree; the analyst
        # separately chooses the column role and whether a value is a stock.
        lexical=node.get('name');prefix,local=lexical.split(':',1)
        namespace=re.search(rb'xmlns:'+re.escape(prefix.encode())+rb'=["\']([^"\']+)["\']',raw)
        if not namespace or namespace.group(1).decode()!=fact['taxonomy_namespace'] or local!=fact['canonical_concept'].rsplit(':',1)[-1]:
            raise ValueError('Inline namespace or concept differs')
        context=tree.xpath('//*[@id=$ident]',ident=node.get('contextref'))
        unit=tree.xpath('//*[@id=$ident]',ident=node.get('unitref'))
        if len(context)!=1 or len(unit)!=1:raise ValueError('Inline context or unit absent')
        dates={n.tag.rsplit(':',1)[-1]:n.text.strip() for n in context[0].iter()
               if n.tag.rsplit(':',1)[-1] in ('instant','startdate','enddate') and n.text}
        if dates.get('instant',dates.get('enddate'))!=fact['period_end'] or dates.get('startdate')!=fact['period_start']:
            raise ValueError('Inline period differs')
        measures=[n.text.strip() for n in unit[0].iter() if n.tag.rsplit(':',1)[-1]=='measure' and n.text]
        if measures!=['iso4217:'+fact['currency']]:raise ValueError('Inline currency differs')
        if quote is None:
            ancestors=node.xpath('ancestor::tr')
            if not ancestors:raise ValueError('Select an explicit narrative quote for this inline occurrence')
            quote=normalize_html(b'<table>'+html.tostring(ancestors[-1])+b'</table>')
        # The inline number must occur in the quoted fragment, not elsewhere
        # in the same original document.
        if not normalize_html(html.tostring(node,with_tail=False)) in quote:raise ValueError('Selected inline number outside quote')
    if not quote or quote not in text:raise ValueError('Literal quotation absent: '+quantity)
    cutoff=read(root/BASE/'scope.json')['source_cutoff']
    row=dict(observation_id=digest([VARIANT,source['document_id'],quantity]),content_key=hashlib.sha256(text.encode()).hexdigest(),
        document_id=source['document_id'],accession=source['accession'],group_id=source['group_id'],entity_id=source['entity_id'],
        abstained=False,quote=quote,locator='rawbytes:0:'+str(len(raw))+';selection='+quantity,
        raw_byte_start=0,raw_byte_end=len(raw),model_quantity=quantity,amount_nature=quantity,
        issuer_treatment=finding,counterparty_evidence='anonymous',stage='signed',period_end=source.get('period_end'),
        filing_status=source['filing_status'],assurance_level=source['assurance_level'],tier=source['tier'],
        location=source['location'],knowledge_date=source['knowledge_date'],source_perspective='reporting_entity',
        accounting_framework=source.get('accounting_framework','us_gaap'),as_of=cutoff)
    row.update(extra)
    if fact:
        row.update(amount=fact['value'],unit=fact['unit'],currency=fact['currency'],amount_origin='tagged_reference',
            tagged_fact_id=fact['fact_id'],period_start=fact['period_start'],period_end=fact['period_end'])
    elif row.get('amount') is not None:
        row.setdefault('amount_origin','narrative_only');row.setdefault('unit','USD');row.setdefault('currency','USD')
    block=dict(content_key=row['content_key'],text=text,candidates=[fact] if fact else [])
    if binding_quote:
        if isinstance(binding_quote,tuple):
            start=text.index(binding_quote[0]);end=text.index(binding_quote[1],start)+len(binding_quote[1]);binding_quote=text[start:end]
        block['attribution_evidence']=dict(method=row.get('counterparty_method'),quantity=quantity,amount_quote=quote,binding_quote=binding_quote)
    validate_semantics(row,block,raw)
    if source['tier']=='E' and row.get('amount') is not None:raise ValueError('External numeric claim cannot enter core observations')
    return row,fact,block.get('attribution_evidence')

def validate_inputs(root):
    root=Path(root);base=root/BASE;scope=read(base/'scope.json');sources=catalog(str(root))
    cutoff=datetime.fromisoformat(scope['source_cutoff'])
    for source in sources.values():
        if sha(root/source['path'])!=source['sha256']:raise ValueError('Original SHA differs')
        accepted=source.get('acceptance_datetime') or source['published_at']
        if datetime.fromisoformat(accepted.replace('Z','+00:00'))>cutoff:raise ValueError('Source after frozen cutoff')
    observations=read(base/'authored_observations.json');facts={f['fact_id']:f for f in read(base/'selected_native_facts.json')}
    proofs=read(base/'attribution_proofs.json',{})
    for row in observations:
        source=next(s for s in sources.values() if s['document_id']==row['document_id'])
        raw,text=served(str(root),source['key']);fact=facts.get(row.get('tagged_fact_id'))
        block=dict(content_key=row['content_key'],text=text,candidates=[fact] if fact else [])
        if row['observation_id'] in proofs:block['attribution_evidence']=proofs[row['observation_id']]
        validate_semantics(row,block,raw)
        if fact:
            regenerated,_,_=author_record(root,source['key'],row['model_quantity'],row['quote'],row['issuer_treatment'],
                inline=fact['locator'][3:],binding_quote=proofs.get(row['observation_id'],{}).get('binding_quote'),
                **{k:v for k,v in row.items() if k in ('stage','counterparty','counterparty_evidence','counterparty_method')})
            if Decimal(regenerated['amount'])!=Decimal(row['amount']):raise ValueError('Native numeric selection differs')
    if sha(root/'audit/criteria_manifest.json')!=scope['frozen_E_F_criteria_sha256']:raise ValueError('Frozen E/F criteria changed')
    return observations,facts

def validate_ledger(root,db):
    base=Path(root)/BASE;operations=read(base/'operations.json');edges=read(base/'edge_decisions.json')
    observations={r[0]:r for r in db.execute('SELECT observation_id,tier,amount,stage,knowledge_date FROM observations').fetchall()}
    entities={r[0] for r in db.execute('SELECT entity_id FROM entities').fetchall()}
    seen=set()
    for operation in operations:
        if operation['operation_id'] in seen:raise ValueError('Duplicate operation')
        seen.add(operation['operation_id'])
        if len(operation['questions'])!=8:raise ValueError('Each operation must disclose eight coverage questions')
        for role in operation['roles']:
            if role.get('entity_id') and role['entity_id'] not in entities:raise ValueError('Unresolved role entity')
            if not role.get('entity_id') and not role.get('unknown_reason'):raise ValueError('Unknown role lacks a reason')
        for reference in operation['evidence']:
            if reference not in observations:raise ValueError('Unresolved operation evidence')
        for question in operation['questions']:
            if question['state'] not in ('documented','partial','not_collected','collected_not_read','read_not_structured','identity_unresolved','amount_unattributable','redacted','public_unavailable_in_bounded_search'):
                raise ValueError('Unknown coverage state')
            if question['state']!='documented' and not question.get('gap'):raise ValueError('Coverage gap not explained')
        for quantity in operation.get('reported_unadmitted_quantities',[]):
            if quantity['admitted_to_core'] or quantity['source_key'] not in catalog(str(Path(root))):raise ValueError('External quantity admission or provenance invalid')
    for edge in edges:
        row=observations.get(edge['observation_id'])
        if not row:raise ValueError('Unresolved edge evidence')
        for reference in edge.get('identity_binding_evidence',[]):
            if reference not in observations:raise ValueError('Unresolved identity binding evidence')
        if row[1] in ('E','F'):raise ValueError('External evidence cannot create a core graph edge')
        if edge['edge_kind']=='amount' and (row[2] is None or edge.get('family')=='financing' and row[3] not in ('drawn_or_paid','recognized')):
            raise ValueError('Signed commitment is not drawn financing')
        if edge['edge_kind']=='amount':
            for endpoint in ('from_entity_id','to_entity_id'):
                if not db.execute("SELECT count(*) FROM entities WHERE entity_id=? AND entity_status='confirmed' AND knowledge_date<=?",[edge[endpoint],row[4]]).fetchone()[0]:
                    raise ValueError(f"Identity not confirmed at edge knowledge date: {edge['operation_id']} {endpoint} {edge[endpoint]} {row[4]}")
    return dict(operations=len(operations),authored_edges=len(edges),coverage_questions=len(operations)*8,
        no_global_exposure_sum=True,no_inferred_causality=True,negative_search_certificates=0)

def apply(root,target_db=None,publish=True):
    root=Path(root).resolve();base=root/BASE;scope=read(base/'scope.json');asof=scope['source_cutoff']
    authored,facts=validate_inputs(root)
    db=target_db or create(root)
    if target_db is None:
        # The large historical fact table stays immutable on disk. Only
        # personally selected new native facts are materialized in memory.
        db.execute('ALTER TABLE facts RENAME TO dependency_native_facts')
        db.execute('CREATE VIEW facts AS SELECT * FROM read_parquet('+sql_literal(str(base/'baseline/facts.parquet'))+') UNION ALL SELECT * FROM dependency_native_facts')
        for table in TABLES:
            if table!='facts':db.execute(f'INSERT INTO {table} BY NAME SELECT * FROM read_parquet(?)',[str(base/'baseline'/(table+'.parquet'))])
    conservation={}
    for table,meta in scope['baseline_tables'].items():
        path=base/'baseline'/(table+'.parquet')
        allowed={meta['sha256']}
        if table=='facts' and (base/'baseline_encoding_proof.json').exists():
            encoding=read(base/'baseline_encoding_proof.json')
            if encoding['original_sha256']!=meta['sha256'] or encoding['difference_rows']!=0:
                raise ValueError('Invalid baseline encoding proof')
            allowed.add(encoding['portable_sha256'])
        if sha(path) not in allowed:raise ValueError('Baseline SHA differs: '+table)
        missing=db.execute(f'SELECT count(*) FROM (SELECT * FROM read_parquet(?) EXCEPT ALL SELECT * FROM {table})',[str(path)]).fetchone()[0]
        if missing:raise ValueError('Prior rows missing or changed: '+table)
        conservation[table]=dict(baseline_rows_missing_or_changed=missing)
    for source in catalog(str(root)).values():
        if db.execute('SELECT count(*) FROM documents WHERE document_id=?',[source['document_id']]).fetchone()[0]:continue
        row={k:source[k] for k in ('document_id','group_id','entity_id','cik','accession','url','form','tier','filing_status','assurance_level','location','knowledge_date','period_end') if k in source}
        row.update(cache_path=source['path'],sha256=source['sha256'],document_rank=source.get('document_rank',0),
            document_rank_source='original_SEC_SGML_header_sequence' if source.get('acceptance_datetime') else 'publisher_original',
            exhibit_type=source.get('exhibit_type'),document_kind=source.get('document_kind','primary_filing'),
            acceptance_datetime=source.get('acceptance_datetime'),filing_date=source.get('filing_date'),
            byte_count=(root/source['path']).stat().st_size,parse_status='observed',as_of=asof)
        insert(db,'documents',row)
    for fact in facts.values():
        if db.execute('SELECT count(*) FROM facts WHERE fact_id=?',[fact['fact_id']]).fetchone()[0]:continue
        if target_db:insert(db,'facts',fact)
        else:
            keys=list(fact);db.execute('INSERT INTO dependency_native_facts ('+','.join(keys)+') VALUES ('+','.join('?' for _ in keys)+')',[fact[k] for k in keys])
    for entity in read(base/'entity_decisions.json'):
        if db.execute('SELECT count(*) FROM entities WHERE entity_id=? AND membership_id=? AND alias_key=?',
            [entity['entity_id'],entity['membership_id'],entity.get('alias_key','none')]).fetchone()[0]:continue
        insert(db,'entities',dict(entity,as_of=asof))
    for row in authored:
        if not db.execute('SELECT count(*) FROM observations WHERE observation_id=?',[row['observation_id']]).fetchone()[0]:insert(db,'observations',row)
    obs={row['observation_id']:row for row in __import__('secfragility.assembly',fromlist=['rows']).rows(db,'SELECT * FROM observations')}
    for decision in read(base/'measure_decisions.json'):
        source=obs[decision['observation_id']]
        if source['tier'] in ('E','F') or source['amount'] is None:raise ValueError('Inadmissible quantity')
        for view in ('as_known','revised'):
            row=dict(measure=decision.get('measure','operation_reported_quantity'),group_id=source['group_id'],
                entity_id=source['entity_id'],counterparty_id=decision.get('counterparty_id','none'),
                period_start=str(source['period_start'] or 'none'),period_end=str(source['period_end'] or source['knowledge_date']),
                view=view,as_of=asof,information_cutoff=asof,variant=VARIANT,
                breakdown_key=decision['operation_id']+'|'+source['model_quantity'],value=source['amount'],unit=source['unit'],
                currency=source['currency'],status='computed',coverage_state='observed',knowledge_date=source['knowledge_date'],
                lineage=json.dumps([source['observation_id']]+([source['tagged_fact_id']] if source['tagged_fact_id'] else [])),
                evidence_profile=json.dumps([source['document_id']]),tier=2,source_perspective=source['source_perspective'],accounting_framework=source['accounting_framework'])
            insert(db,'measures',row)
    for rule in read(base/'derived_decisions.json',[]):
        a,b=obs[rule['numerator_observation_id']],obs[rule['denominator_observation_id']]
        numerator,denominator,value=customer_share(a,b)
        for view in ('as_known','revised'):
            insert(db,'measures',dict(measure='operation_derived_quantity',group_id=a['group_id'],entity_id=a['entity_id'],
                counterparty_id=rule['counterparty_id'],period_start=str(a['period_start']),period_end=str(a['period_end']),
                view=view,as_of=asof,information_cutoff=asof,variant=VARIANT,breakdown_key=rule['operation_id']+'|'+rule['quantity'],
                value=value,numerator=numerator,denominator=denominator,unit='ratio',currency=None,
                status='computed',coverage_state='observed',knowledge_date=max(a['knowledge_date'],b['knowledge_date']),
                lineage=json.dumps([a['observation_id'],b['observation_id']]),tier=2,
                source_perspective=a['source_perspective'],accounting_framework=a['accounting_framework'],
                relationship_conclusion='causality_not_established',numerator_coverage='complete',denominator_coverage='complete'))
    for decision in read(base/'edge_decisions.json'):
        source=obs[decision['observation_id']]
        if source['tier'] in ('E','F'):raise ValueError('External core edge forbidden')
        edge=dict(link_id=digest([VARIANT,decision['operation_id'],source['observation_id'],decision['type']]),
            from_entity_id=decision['from_entity_id'],to_entity_id=decision['to_entity_id'],
            family=decision['family'],type=decision['type'],edge_kind=decision['edge_kind'],
            from_group_id=decision.get('from_group_id'),to_group_id=decision.get('to_group_id'),
            amount=source['amount'] if decision['edge_kind']=='amount' else None,unit=source['unit'],currency=source['currency'],
            period_start=source['period_start'],period_end=source['period_end'] or source['knowledge_date'],event_date=source['event_date'],
            knowledge_date=source['knowledge_date'],stage=source['stage'],event_type=source['event_type'],
            instrument_key=decision['operation_id'],fact_id=source['tagged_fact_id'],observation_id=source['observation_id'],
            document_id=source['document_id'],locator=source['locator'],filing_status=source['filing_status'],
            assurance_level=source['assurance_level'],tier=source['tier'],counterparty_evidence=decision['counterparty_evidence'],
            accounting_framework=source['accounting_framework'],source_perspective=source['source_perspective'],
            financing_state='unknown',financing_policy='none',relationship_conclusion='causality_not_established',
            conditionality=source['conditionality'],trigger_description=source['trigger_description'],trigger_occurred=source['trigger_occurred'],
            vehicle_level=decision.get('vehicle_level'),as_of=asof)
        insert(db,'links',edge)
        if decision.get('replaces_link_id'):
            insert(db,'links',dict(link_id=digest([VARIANT,decision['replaces_link_id'],edge['link_id']]),edge_kind='relation',
                relation_type='replaces',amount_a_id=decision['replaces_link_id'],amount_b_id=edge['link_id'],resolved=True,
                resolution_evidence='Dated manual identity or instrument classification refinement; replacement is not additive.',as_of=asof))
    ledger=validate_ledger(root,db)
    from .verify_delivery import final,snapshot
    verification=final(db,asof)
    for table in TABLES:
        conservation[table]['baseline_rows_missing_or_changed']=db.execute(f'SELECT count(*) FROM (SELECT * FROM read_parquet(?) EXCEPT ALL SELECT * FROM {table})',
            [str(base/'baseline'/(table+'.parquet'))]).fetchone()[0]
        if conservation[table]['baseline_rows_missing_or_changed']:raise ValueError('Prior rows changed during extension')
    proof=dict(ledger=ledger,conservation=conservation,checks=verification['checks'],counts=table_counts(db),
        historical_main_groups=26,additional_targeted_issuer_dossiers=4,frozen_criteria=True,subagents_used=False)
    save(base/'validation.json',proof)
    if publish and target_db is None:export(db,root/'tables',unchanged={t:base/'baseline'/(t+'.parquet') for t in ('controls','exclusions')},validator=lambda p:snapshot(p,asof))
    return db,proof

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--no-publish',action='store_true');args=parser.parse_args()
    db,proof=apply(Path('.'),publish=not args.no_publish);print(json.dumps(proof,default=str));db.close()
