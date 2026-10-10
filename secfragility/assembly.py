"""Load immutable reading results and make all scope decisions explicit."""
from pathlib import Path
from collections import defaultdict
import json
from .database import insert, sql_literal
from .xbrl import digest


def exclusion(db,as_of,reason,element_type,element_id,**fields):
    row=dict(exclusion_id=digest([as_of,reason,element_type,element_id,fields]),
             reason=reason,element_type=element_type,element_id=element_id,as_of=as_of,**fields)
    insert(db,'exclusions',row)


def load(db,root,as_of):
    queue=json.loads((root/'work/queue.json').read_text())
    by_key=defaultdict(list)
    for r in queue:by_key[r['content_key']].append(r)
    valid_keys=set(by_key)
    for key in sorted(valid_keys):
        path=root/'work/observations'/(key+'.jsonl')
        if not path.exists():
            exclusion(db,as_of,'not_processed','block',key,content_key=key,coverage_state='not_processed')
            continue
        lines=[json.loads(s) for s in path.read_text().splitlines()]
        stamps=[r['as_of'] for r in lines if r['record_kind']=='pass' and r['as_of']<=as_of]
        if not stamps:continue
        latest=max(stamps)
        for r in lines:
            if r['record_kind']=='observation' and r['as_of']==latest:
                row={k:v for k,v in r.items() if k!='record_kind'}
                # Observation as_of is its reading pass, not a recomputed date.
                insert(db,'observations',row)
        reject=root/'work/observations'/(key+'.rejected.jsonl')
        if reject.exists():
            failures=[json.loads(s) for s in reject.read_text().splitlines()]
            for rank,r in enumerate(failures):
                if r['as_of']!=latest:continue
                # A successful schema-only retry keeps its original failed
                # attempt visible; it does not quarantine its accepted retry.
                exclusion(db,as_of,'validation_failed','rejected_observation',key+':'+str(rank),
                    content_key=key,accession=by_key[key][0]['accession'],
                    detail=r['phase']+': '+r['error'],raw_line=json.dumps(r['raw_line'],ensure_ascii=False),coverage_state='unknown')
    # The collection's structural exclusions are never re-labelled absences.
    for filename in ['work/block_exclusions.json','work/section_exclusions.json']:
        p=root/filename
        if p.exists():
            for rank,r in enumerate(json.loads(p.read_text())):
                exclusion(db,as_of,r.get('reason','not_processed'),'source_scope',filename+':'+str(rank),
                    group_id=r.get('group'),accession=r.get('accession'),content_key=r.get('content_key'),
                    detail=json.dumps(r,ensure_ascii=False),coverage_state='not_processed')
    policies={}
    for filename in ['work/observation_quarantines.json','work/exhibit_body_policy_overrides.json']:
        p=root/filename
        if not p.exists():continue
        for r in json.loads(p.read_text()):
            if 'observation_id' in r:
                policies[r['observation_id']]=r
                exclusion(db,as_of,r['reason'],'observation',r['observation_id'],detail=json.dumps(r,ensure_ascii=False),coverage_state='policy_excluded')
            else:
                exclusion(db,as_of,r['reason'],'exhibit_body',r['content_key'],group_id=r['group'],
                    accession=r['accession'],content_key=r['content_key'],
                    locator=f"rawbytes:{r['raw_byte_start']}:{r['raw_byte_end']}",detail=json.dumps(r,ensure_ascii=False),coverage_state='policy_excluded')
    db.execute('CREATE TEMP TABLE excluded_observations (observation_id VARCHAR PRIMARY KEY,reason VARCHAR)')
    if policies:db.executemany('INSERT INTO excluded_observations VALUES (?,?)',[(k,v['reason']) for k,v in policies.items()])
    db.execute('''CREATE VIEW usable_observations AS SELECT o.* FROM observations o
      WHERE NOT abstained AND tier IN ('A','B','C','D') AND filing_status='filed'
       AND NOT EXISTS (SELECT 1 FROM excluded_observations q WHERE q.observation_id=o.observation_id)
       AND (tagged_fact_id IS NULL OR EXISTS (SELECT 1 FROM eligible_facts f
        WHERE f.fact_id=o.tagged_fact_id AND f.value IS NOT NULL AND f.coverage_state IN ('observed','explicit_zero')))''')
    for o in rows(db,"SELECT * FROM observations WHERE abstained AND model_quantity='exhibit_body_excluded_financial_parties_only'"):
        if any(r.get('content_key')==o['content_key'] for r in json.loads((root/'work/exhibit_body_policy_overrides.json').read_text())):continue
        b=json.loads((root/by_key[o['content_key']][0]['path']).read_text())
        exclusion(db,as_of,'financial_parties_only','exhibit_body',o['content_key'],group_id=o['group_id'],
            document_id=o['document_id'],accession=o['accession'],content_key=o['content_key'],
            locator=f"rawbytes:{o['raw_byte_end']}:{b['raw_byte_end']}",detail=o['abstention_reason'],coverage_state='policy_excluded')
    for row in db.execute('''SELECT o.observation_id,o.group_id,o.accession,o.tagged_fact_id
      FROM observations o LEFT JOIN eligible_facts f ON f.fact_id=o.tagged_fact_id
      WHERE NOT o.abstained AND o.tagged_fact_id IS NOT NULL
       AND (f.fact_id IS NULL OR f.value IS NULL OR f.coverage_state NOT IN ('observed','explicit_zero'))''').fetchall():
        oid,g,acc,fid=row
        exclusion(db,as_of,'conflicting_tagged_reference','observation',oid,group_id=g,accession=acc,
                  detail='Dependent amount, attribution, link and event excluded; deposited fact '+fid+' remains unchanged.',coverage_state='conflicting')
    # Fixed first-pass scope leaves the other note families for the extension.
    for g in sorted(json.loads((root/'work/inventory.json').read_text())['groups']):
        for family in ['investments_note','debt_note','lease_note','commitments_note','concentration_narrative']:
            exclusion(db,as_of,'not_processed','note_family',g+':'+family,group_id=g,
                      detail='First-pass scope; extension not opened.',coverage_state='not_processed')
        exclusion(db,as_of,'not_public','securitization_detail',g,group_id=g,
                  detail='No line-level coverage presumed for the described datacenter securitization layer; SEC staff position is not a financial amount.',coverage_state='unknown')


def rows(db,query,parameters=None):
    result=db.execute(query,parameters or [])
    names=[x[0] for x in result.description]
    return [dict(zip(names,r)) for r in result.fetchall()]
