"""Source-backed expansion scope, incorporation proof and reported parent control."""
from pathlib import Path
import hashlib,json
from .text import normalize_html
from .xbrl import digest
from .network import atomic_json

def qualifies_source(root,record):
    raw=(root/record['proof_path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=record['proof_sha256']:
        raise ValueError('Incorporation proof bytes changed')
    if record['quote'] not in normalize_html(raw):
        raise ValueError('Incorporation statement missing from original report')
    return True

def qualify_documents(db,root):
    path=root/'work/expansion/source_qualifications.json'
    if not path.exists():return
    for r in json.loads(path.read_text()):
        qualifies_source(root,r)
        for url in r['qualified_urls']:
            db.execute("""UPDATE documents SET incorporated_by_reference=true,
                incorporation_evidence=?,tier='C',assurance_level='unknown'
                WHERE document_id=? AND accession=? AND filing_status='furnished'""",
                [r['proof_url']+'; '+r['quote'],digest([url]),r['accession']])

def reported_control(records,index,observations):
    # A manager/fund relationship never enters this rule. The observation is
    # explicitly authored from the controlled reporter's own financial note.
    for o in observations:
        if o.get('model_quantity')!='parent_control_membership':continue
        from .entities import normalize
        parents=[r for r in index.get(normalize(o.get('counterparty','')),[]) if r.get('cik')]
        children=[r for r in records if r['entity_id']==o['entity_id'] and not r.get('alias_key')]
        if len({r['entity_id'] for r in parents})!=1 or len(children)!=1:continue
        parent=parents[0];child=children[0]
        if child['entity_id']==parent['entity_id']:raise ValueError('Self control is invalid')
        child.update(economic_group_id=parent['economic_group_id'],
            consolidation_treatment='consolidated_subsidiary',
            evidence_document_id=o['document_id'],evidence_locator=o['locator'],
            knowledge_date=o['knowledge_date'],membership_start=o['knowledge_date'],legal_date=None,
            membership_id=digest([child['entity_id'],parent['economic_group_id'],str(o['knowledge_date'])]),
            resolution_rule='own_financial_note_reports_direct_parent;historical_start_not_established')

def stage_scope(root,selected_prefixes):
    nominated=json.loads((root/'work/expansion/queue.json').read_text())
    keys={r['content_key'] for r in nominated}
    selected={k for k in keys if any(k.startswith(p) for p in selected_prefixes)}
    if len(selected)!=len(set(selected_prefixes)):raise ValueError('Missing or ambiguous selection')
    pending=[k for k in selected if not (root/'work/observations'/(k+'.jsonl')).exists()]
    if pending:raise ValueError('Selected natural notes have not been completed: '+str(pending))
    old=json.loads((root/'work/queue.json').read_text())
    untouched=[r for r in old if r['content_key'] not in keys]
    if any(not (root/'work/observations'/(r['content_key']+'.jsonl')).exists() for r in untouched):
        raise ValueError('An earlier active reading pass is incomplete')
    reused={r['content_key'] for r in nominated if (root/'work/observations'/(r['content_key']+'.jsonl')).exists()}
    active=selected|reused
    deferred=[dict(r,reason='not_processed',content_key=r['content_key'],
        detail='Collected natural note; explicitly deferred beyond first financing/construction/customer-support review tranche.')
        for r in nominated if r['content_key'] not in active]
    atomic_json(root/'work/expansion/scope_exclusions.json',deferred)
    atomic_json(root/'work/expansion/reading_scope.json',dict(
        source_cutoff=json.loads((root/'work/run.json').read_text())['as_of'],
        nominated_unique_keys=len(keys),active_unique_keys=len(active),deferred_unique_keys=len(keys-active),
        active_keys=sorted(active),deferred_keys=sorted(keys-active),
        historical_notes_complete=False,all_nominated_notes_read=not deferred,
        rule=('All nominated natural notes have been individually reviewed; historical notes and complete contracts beyond this frozen inventory are not declared reviewed.' if not deferred else
              'First review of construction commitments, project financing, guarantees, customer support and lender positions; all other nominated notes remain explicitly not_processed.')))
    atomic_json(root/'work/queue.json',untouched+[r for r in nominated if r['content_key'] in active])
    return dict(active=len(active),deferred=len(keys-active))
