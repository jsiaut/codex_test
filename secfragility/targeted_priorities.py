"""Small evidence overlay on the immutable 26-group snapshot.

No global ratios or frozen E/F conclusions are recomputed by a lender-side
position. Reproduction validates literal quotes, inline scale and column identity.
"""
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timezone
import argparse, csv, hashlib, json, os, re, tarfile
import duckdb, zstandard
from lxml import html
from .database import create, insert, TABLES, sql_literal
from .xbrl import digest
from .text import normalize_html
from .observations import validate_semantics

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p, obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,default=str,indent=2)+'\n')
def sources(root): return json.loads((root/'work/priorities/source_manifest.json').read_text())
def scope(root): return json.loads((root/'work/priorities/scope.json').read_text())

def restore_sources(root):
    """Restore preserved originals offline; never replace present evidence."""
    missing=any(not (root/s['path']).is_file() for s in sources(root))
    if not missing:return
    b=root/'work/priorities';meta=json.loads((b/'source_backup.json').read_text());archive=root/meta['path']
    if sha(archive)!=meta['sha256']:raise ValueError('Source archive SHA differs')
    with archive.open('rb') as file,zstandard.ZstdDecompressor().stream_reader(file) as z,tarfile.open(fileobj=z,mode='r|') as tar:
        for m in tar:
            p=Path(m.name)
            if not m.isfile() or p.is_absolute() or '..' in p.parts or len(p.parts)<4 or p.parts[:2]!=('work','priorities') or p.parts[2] not in ('sources','text'):
                raise ValueError('Unsafe source archive member')
            target=root/p
            if not target.exists():
                target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(tar.extractfile(m).read())

def prepare_baseline(root):
    # The facts are unchanged by this overlay. A portable package stores them
    # once, and links the identical immutable facts into the preceding snapshot.
    p=root/'work/priorities/baseline/facts.parquet'
    if not p.exists():
        source=root/'tables/facts.parquet'
        if sha(source)!=scope(root)['baseline_tables']['facts']['sha256']:raise ValueError('Baseline fact SHA differs')
        p.hardlink_to(source)

def author_record(root, db, source, quantity, quote, finding, inline=None, **extra):
    s=next(s for s in sources(root) if Path(s['path']).name==source)
    raw=(root/s['path']).read_bytes()
    if sha(root/s['path'])!=s['sha256']: raise ValueError('Source SHA differs')
    text=normalize_html(raw)
    fact=None
    if inline:
        node=html.fromstring(raw).xpath('//*[@id=$ident]',ident=inline)
        if len(node)!=1: raise ValueError('Inline ID absent or ambiguous')
        node=node[0]
        ancestors=node.xpath('ancestor::tr')
        if not ancestors: raise ValueError('Numeric choice is not a table row')
        quote=normalize_html(b'<table>'+html.tostring(ancestors[-1])+b'</table>')
        rows=db.execute("SELECT * FROM read_parquet(?) WHERE accession=? AND locator=?",
                        [str(root/'work/priorities/baseline/facts.parquet'),s['accession'],'id:'+inline]).fetchdf().to_dict('records')
        if len(rows)!=1: raise ValueError('Native occurrence absent or ambiguous')
        fact=rows[0]
        # Namespaces are checked as well as the local concept. Custom taxonomy
        # normalization need not retain the lexical prefix of the HTML.
        lexical=node.get('name');prefix,local=lexical.split(':',1)
        namespace=re.search(rb'xmlns:'+re.escape(prefix.encode())+rb'=["\']([^"\']+)["\']',raw)
        if not namespace or namespace.group(1).decode()!=fact['taxonomy_namespace']:
            raise ValueError('Inline namespace differs from native fact')
        if local!=fact['canonical_concept'].rsplit(':',1)[-1]: raise ValueError('Concept differs')
        token=node.text_content().strip().replace(',','')
        value=Decimal(token)*Decimal(10)**int(node.get('scale','0'))
        if node.get('sign')=='-': value=-value
        if value!=fact['value']: raise ValueError('Inline amount or scale differs')
        for k in ('period_start','period_end'):
            fact[k]=None if str(fact[k])=='NaT' else str(fact[k])[:10]
        tree=node.getroottree()
        units=tree.xpath('//*[@id=$ident]',ident=node.get('unitref'))
        if len(units)!=1:raise ValueError('Inline unit absent or ambiguous')
        measures=[e.text.strip() for e in units[0].iter() if e.tag.endswith('measure') and e.text]
        if measures!=['iso4217:USD'] or fact['currency']!='USD':raise ValueError('Currency/unit differs')
        contexts=tree.xpath('//*[@id=$ident]',ident=node.get('contextref'))
        if len(contexts)!=1:raise ValueError('Inline context absent or ambiguous')
        dates={e.tag.rsplit(':',1)[-1]:e.text.strip() for e in contexts[0].iter()
               if e.tag.rsplit(':',1)[-1] in ('instant','startdate','enddate') and e.text}
        if dates.get('instant',dates.get('enddate'))!=fact['period_end'] or dates.get('startdate')!=fact['period_start']:
            raise ValueError('Inline period differs')
    elif isinstance(quote,tuple):
        a=text.index(quote[0]);z=text.index(quote[1],a)+len(quote[1]);quote=text[a:z]
    if not quote or quote not in text: raise ValueError('Selected quote absent: '+quantity)
    row=dict(observation_id=digest(['targeted_v1',s['document_id'] if s.get('document_id') else s['url'],quantity]),
        content_key=hashlib.sha256(text.encode()).hexdigest(),document_id=s.get('document_id') or digest([s['url']]),
        accession=s['accession'],group_id=s['group_id'],entity_id='cik:'+s['cik'],abstained=False,
        quote=quote,locator='rawbytes:0:'+str(len(raw))+';selection='+quantity,
        raw_byte_start=0,raw_byte_end=len(raw),model_quantity=quantity,amount_nature=quantity,
        issuer_treatment=finding,stage='recognized',counterparty_evidence='anonymous',
        period_end=s['period_end'] if s.get('period_end') not in ('None','NaT','') else None,
        knowledge_date=s['knowledge_date'][:10],filing_status='filed',
        assurance_level=s['assurance_level'] if s['assurance_level']!='contract' else 'not_applicable',tier=s['tier'],
        location='contract' if s['tier']=='D' else 'financial_statements_and_notes',
        source_perspective='counterparty' if source.startswith(('aci-','ck0001902649-')) else 'reporting_entity',
        accounting_framework='us_gaap',as_of=scope(root)['source_cutoff'])
    if extra.get('counterparty') and 'counterparty_evidence' not in extra:row['counterparty_evidence']='named'
    row.update(extra)
    if fact:
        row.update(amount=str(fact['value']),unit=fact['unit'],currency=fact['currency'],amount_origin='tagged_reference',
                   tagged_fact_id=fact['fact_id'],period_start=fact['period_start'],period_end=fact['period_end'])
    elif row.get('amount') is not None:
        row.update(amount_origin='narrative_only',unit='USD',currency='USD')
    block=dict(content_key=row['content_key'],text=text,candidates=[fact] if fact else [])
    validate_semantics(row,block,raw)
    if row.get('currency')=='USD':row['unit']='USD'
    return row

def validate_evidence(root, observations):
    db=duckdb.connect()
    for s in sources(root):
        if sha(root/s['path'])!=s['sha256']:raise ValueError('Original SHA changed: '+s['url'])
        if s.get('acceptance_datetime') and datetime.fromisoformat(s['acceptance_datetime'].replace('Z','+00:00'))>datetime.fromisoformat(scope(root)['source_cutoff']):raise ValueError('Source after cutoff')
    for o in observations:
        s=next(s for s in sources(root) if (s.get('document_id') or digest([s['url']]))==o['document_id'])
        raw=(root/s['path']).read_bytes();text=normalize_html(raw)
        if o['quote'] not in text:raise ValueError('Literal quote changed')
        if o.get('tagged_fact_id'):
            f=db.execute('SELECT * FROM read_parquet(?) WHERE fact_id=?',[str(root/'work/priorities/baseline/facts.parquet'),o['tagged_fact_id']]).fetchdf().to_dict('records')[0]
            native=author_record(root,db,Path(s['path']).name,o['model_quantity'],None,o['issuer_treatment'],inline=f['locator'][3:])
            if Decimal(native['amount'])!=Decimal(o['amount']):raise ValueError('Native scale changed')
        elif o.get('amount'):
            # Validate actual narrative scale and raw-byte citation again.
            validate_semantics(o,dict(content_key=o['content_key'],text=text,candidates=[]),raw)
    db.close()

def entity(db,name,o,root):
    # Only punctuation/case variants of an exact legal name are aliases. Group
    # membership is never inferred from a branded borrower name.
    normalized=re.sub(r'[^a-z0-9]','',name.casefold())
    matches=[r for r in db.execute('SELECT entity_id,legal_name FROM entities').fetchall()
             if re.sub(r'[^a-z0-9]','',r[1].casefold())==normalized]
    if len(set(r[0] for r in matches))>1: raise ValueError('Ambiguous entity')
    if matches:return matches[0][0]
    eid='legal:'+digest([name.casefold()])
    insert(db,'entities',dict(entity_id=eid,membership_id=digest(['targeted_entity',eid]),legal_name=name,
        normalized_name=name.casefold(),entity_status='confirmed',consolidation_treatment='undetermined',
        knowledge_date=o['knowledge_date'],legal_date=o.get('event_date'),resolution_rule='exact_named_contract_party_or_SOI_borrower;no_control_inference',
        evidence_document_id=o['document_id'],evidence_locator=o['locator'],source_perspective=o['source_perspective'],as_of=scope(root)['source_cutoff']))
    return eid

def measure(db,o,value=None,name='targeted_reported_quantity',lineage=None,**extra):
    for view in ('as_known','revised'):
        insert(db,'measures',dict(measure=name,group_id=o['group_id'],entity_id=o['entity_id'],
            counterparty_id=o.get('counterparty_entity_id') or 'none',period_start=o.get('period_start') or 'none',
            period_end=o['period_end'] or 'none',view=view,as_of=o['as_of'],breakdown_key=o['model_quantity'],
            variant='targeted_priorities_v1',knowledge_date=o['knowledge_date'],information_cutoff=o['as_of'],
            value=str(value if value is not None else o['amount']),unit=o.get('unit'),currency=o.get('currency'),
            status='computed',coverage_state='observed',lineage=json.dumps(lineage or [o['observation_id']]),
            evidence_profile=json.dumps([o['document_id']]),tier=2,source_perspective=o['source_perspective'],
            accounting_framework=o['accounting_framework'],**extra))

def apply(root,target_db=None):
    root=Path(root);b=root/'work/priorities';sc=scope(root)
    prepare_baseline(root);restore_sources(root)
    for table,s in sc['baseline_tables'].items():
        if sha(b/'baseline'/(table+'.parquet'))!=s['sha256']:raise ValueError('26-group baseline changed')
    obs=json.loads((b/'authored_observations.json').read_text());validate_evidence(root,obs)
    db=target_db or create(root)
    def bag(v):
        return json.dumps(sorted(json.loads(v),key=lambda x:json.dumps(x,sort_keys=True)),separators=(',',':'))
    db.create_function('priority_source_bag',bag,['VARCHAR'],'VARCHAR')
    # An optional full reconstruction supplies a completed SMCI database. The
    # frozen 26-group stage must compare exactly before this overlay is applied.
    for table in TABLES:
        file=b/'baseline'/(table+'.parquet')
        if target_db:
            columns=[r[1] for r in db.execute(f"PRAGMA table_info('{table}')").fetchall()]
            fields=','.join('priority_source_bag("'+c+'") AS "'+c+'"' if c in ('lineage','evidence') else '"'+c+'"' for c in columns)
            diffs=db.execute(f'SELECT count(*) FROM ((SELECT {fields} FROM {table} EXCEPT ALL SELECT {fields} FROM read_parquet(?)) UNION ALL (SELECT {fields} FROM read_parquet(?) EXCEPT ALL SELECT {fields} FROM {table}))',[str(file),str(file)]).fetchone()[0]
            if diffs:raise ValueError('Reconstructed baseline differs: '+table)
        elif table!='facts':db.execute(f'INSERT INTO {table} BY NAME SELECT * FROM read_parquet(?)',[str(file)])
    new_docs=[]
    for s in sources(root):
        did=s.get('document_id') or digest([s['url']])
        if db.execute('SELECT count(*) FROM documents WHERE document_id=?',[did]).fetchone()[0]:continue
        insert(db,'documents',dict(document_id=did,group_id=s['group_id'],entity_id='cik:'+s['cik'],cik=s['cik'],
            accession=s['accession'],document_rank=s['document_rank'],document_rank_source='original_SEC_exhibit_sequence_header',
            url=s['url'],cache_path=s['path'],sha256=s['sha256'],form=s['form'],exhibit_type='EX-10.'+str(s['document_rank']),
            filing_status='filed',assurance_level='not_applicable',location='contract',document_kind='exhibit',tier='D',
            acceptance_datetime=s['acceptance_datetime'],filing_date=s['filing_date'],knowledge_date=s['knowledge_date'],
            period_end=s['period_end'],byte_count=(root/s['path']).stat().st_size,parse_status='observed',as_of=sc['source_cutoff']))
        new_docs.append(did)
    for o in obs:
        if o.get('counterparty'):o['counterparty_entity_id']=entity(db,o['counterparty'],o,root)
        insert(db,'observations',o)
        if o.get('amount') is not None:measure(db,o)
        if o['model_quantity'].endswith('funded_principal'):
            insert(db,'links',dict(link_id=digest(['targeted_held',o['observation_id']]),edge_kind='amount',family='financing',type='loan_or_facility',
                from_entity_id=o['entity_id'],to_entity_id=o['counterparty_entity_id'],from_group_id=o['group_id'],amount=o['amount'],
                unit=o['unit'],currency=o['currency'],period_end=o['period_end'],knowledge_date=o['knowledge_date'],stage='recognized',
                instrument_key=o['instrument_key'],fact_id=o['tagged_fact_id'],observation_id=o['observation_id'],document_id=o['document_id'],locator=o['locator'],
                filing_status='filed',assurance_level=o['assurance_level'],tier=o['tier'],counterparty_evidence='named',source_perspective='counterparty',
                accounting_framework='us_gaap',financing_state='active',financing_policy='exposure_outstanding',as_of=sc['source_cutoff']))
        elif o.get('link_type')=='guarantee':
            insert(db,'links',dict(link_id=digest(['targeted_springing',o['observation_id']]),edge_kind='relation',family='credit_support',type='guarantee',
                from_entity_id='cik:0001769628',from_group_id='CRWV',to_entity_id=o['counterparty_entity_id'],to_group_id=o['group_id'],
                period_end=o['period_end'],event_date='2026-03-30',knowledge_date=o['knowledge_date'],stage='signed',instrument_key=o['instrument_key'],
                observation_id=o['observation_id'],document_id=o['document_id'],locator=o['locator'],filing_status='filed',assurance_level='not_applicable',tier='D',
                counterparty_evidence='derivable',source_perspective='counterparty',accounting_framework='us_gaap',conditionality='conditional',
                trigger_description=o['trigger_description'],trigger_occurred='unknown',financing_state='unknown',as_of=sc['source_cutoff']))
        elif o['model_quantity']=='vernon_named_sublicensee':
            insert(db,'links',dict(link_id=digest(['targeted_vernon',o['observation_id']]),edge_kind='relation',family='commercial',type='capacity_lease',
                from_entity_id='cik:0001375365',from_group_id='SMCI',to_entity_id=o['counterparty_entity_id'],period_end=o['period_end'],
                event_date='2024-06-14',knowledge_date=o['knowledge_date'],stage='signed',instrument_key='SMCI_VERNON',
                observation_id=o['observation_id'],document_id=o['document_id'],locator=o['locator'],filing_status='filed',tier=o['tier'],
                assurance_level=o['assurance_level'],counterparty_evidence='named',source_perspective='reporting_entity',accounting_framework='us_gaap',as_of=sc['source_cutoff']))
    idx={o['model_quantity']:o for o in obs}
    for prefix in ('ares_helios_current','ares_cw_nest_current','ares_ddtl_v_current','ares_helios_prior','ares_cw_nest_prior','blackrock_ddtl_v'):
        f,c=idx[prefix+'_fair_value'],idx[prefix+'_cost'];ratio=Decimal(f['amount'])/Decimal(c['amount'])
        measure(db,dict(f,unit='ratio',currency=None),value=ratio,name='bdc_fv_to_cost',lineage=[f['observation_id'],c['observation_id']],numerator=f['amount'],denominator=c['amount'])
        if prefix.startswith('ares'):
            p,u,t=(idx[prefix+'_'+field] for field in ('funded_principal','unfunded_commitment','total_commitment'))
            residual=Decimal(p['amount'])+Decimal(u['amount'])-Decimal(t['amount'])
            if residual!=0:raise ValueError('Commitment/funded/unfunded mismatch')
            for view in ('as_known','revised'):
                insert(db,'controls',dict(control='targeted_commitment_reconciliation',group_id=p['group_id'],period_end=p['period_end'],view=view,as_of=sc['source_cutoff'],
                    breakdown_key=prefix,variant='targeted_priorities_v1',status='ok',lhs=str(Decimal(p['amount'])+Decimal(u['amount'])),rhs=t['amount'],
                    residual='0',tolerance='1500',tolerance_basis='notes_dcml',explanation_code='independent_SOI_funded_plus_note7_unfunded_equals_note7_total',
                    evidence=json.dumps([p['observation_id'],u['observation_id'],t['observation_id']])))
    for reason,group,state,detail in [
        ('Tsubaki_draw_and_private_terms_not_established','external:0001065521','not_disclosed','Bounded official-source search adds no confirmed draw or threshold. Retain signed USD10bn; no arranger allocation.'),
        ('DFS_private_contracts_and_numeric_triggers_not_established','DELL','not_disclosed','Published note supplies capacities and criteria, not lender shares, exact performance thresholds or named AI receivables.'),
        ('Vernon_investment_not_new_payment_and_revenue_ND','SMCI','not_disclosed','Identity resolved by explicit current filing incorporation; no amount of Lambda product revenue, private creditworthiness, or proof of current cash recovery.'),
        ('lender_PIK_and_borrower_full_control_outside_tranche','CRWV','not_disclosed','Selected positions are fund-specific, no borrower-level PIK amount or full creditor coverage. No branded-name consolidation inference.'),
        ('APLD_springing_threshold_and_call_not_established','external:0001144879','redacted','Rating trigger and Building2 LC amount/deadlines redacted. Activation not established. Building3 section12 reserved.'),
    ]:
        insert(db,'exclusions',dict(exclusion_id=digest(['targeted_gap',reason]),group_id=group,element_type='targeted_scope',element_id=reason,reason=reason,
            detail=detail,coverage_state=state,as_of=sc['source_cutoff']))
    # Export only changed tables; the 1.4m existing facts remain byte identical.
    changed=[t for t in TABLES if t!='facts'];staging=b/'staging';staging.mkdir(exist_ok=True)
    for t in changed:db.execute(f'COPY (SELECT * FROM {t} ORDER BY ALL) TO {sql_literal(str(staging/(t+".parquet")))} (FORMAT PARQUET)')
    conservation={}
    for t in changed:
        columns=[r[1] for r in db.execute(f"PRAGMA table_info('{t}')").fetchall()]
        fields=','.join('priority_source_bag("'+c+'") AS "'+c+'"' if c in ('lineage','evidence') else '"'+c+'"' for c in columns)
        n=db.execute(f'SELECT count(*) FROM (SELECT {fields} FROM read_parquet(?) EXCEPT ALL SELECT {fields} FROM {t})',[str(b/'baseline'/(t+'.parquet'))]).fetchone()[0]
        if n:raise ValueError('Baseline row changed: '+t)
        conservation[t]={'baseline_rows_missing_or_changed':n,'rows':db.execute(f'SELECT count(*) FROM {t}').fetchone()[0]}
    if sha(root/'tables/facts.parquet')!=sc['baseline_tables']['facts']['sha256']:raise ValueError('Existing native facts changed')
    for t in changed:(staging/(t+'.parquet')).replace(root/'tables'/(t+'.parquet'))
    conservation['facts']={'byte_identical':True,'rows':1435879}
    csv_path=root/'targeted_evidence.csv'
    keys=['observation_id','group_id','model_quantity','counterparty','counterparty_evidence','amount','currency','measurement_basis','stage','period_end','knowledge_date','document_id','locator','tagged_fact_id','issuer_treatment','quote']
    with csv_path.open('w') as file:
        writer=csv.DictWriter(file,keys,extrasaction='ignore');writer.writeheader();writer.writerows(obs)
    summary=dict(status='integrated_targeted_overlay',source_cutoff=sc['source_cutoff'],main_groups=26,subagents_used=False,
        observations=len(obs),new_documents=len(new_docs),added_links=9,amounts_are_not_additive=True,conservation=conservation,
        lender_rows=6,independent_commitment_controls=10,vernon_identity='Lambda, Inc.',remaining_gaps=5,
        validation_time=datetime.now(timezone.utc).isoformat())
    save(root/'targeted_summary.json',summary);save(b/'validation.json',summary)
    save(b/'integration_contract.json',dict(status='integrated_targeted_overlay',source_cutoff=sc['source_cutoff'],authorization=sc['authorization']))
    report=root/'smci_integration.md'
    if report.exists():
        t=report.read_text()
        t=t.replace('L’identité manque : aucune arête de financement chiffrée vers un nom supposé n’est produite.',
            'L’identité est désormais résolue comme Lambda, Inc. par le contrat et son incorporation dans le 10-K actuel. Le type d’émission primaire n’étant pas établi, aucune nouvelle arête monétaire d’émission primaire n’est produite : voir [l’extension ciblée](targeted_priorities.md).')
        if 'Mise à jour ciblée de Vernon' not in t:
            t='**Mise à jour ciblée de Vernon : Lambda, Inc. est identifiée par les contrats déposés ; voir [les preuves nouvelles](targeted_priorities.md).**\n\n'+t
        report.write_text(t)
    if not target_db:db.close()
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser();p.parse_args();print(json.dumps(apply(Path('.').resolve()),ensure_ascii=False))
