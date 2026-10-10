"""Oriented evidence edges; commitments never become cash financing."""
import json
from collections import defaultdict
from .database import insert
from .assembly import rows,exclusion
from .xbrl import digest


def assemble(db,root,as_of,entities,observations,resolve):
    evidence=[]
    for o in observations:
        if not o.get('family') or not o.get('link_type') or o.get('counterparty_evidence') not in ('named','derivable'):continue
        payer=o.get('payer');receiver=o.get('receiver')
        if o['family']=='credit_support':
            if o.get('ultimate_obligor'):
                receiver=o['ultimate_obligor']
            elif receiver and any(word in receiver.lower().split() for word in ['trust','bank','securities']):
                receiver=None  # Beneficiary/trustee is not the supported obligor.
        if not payer or not receiver:
            exclusion(db,as_of,'direction_not_established','amount_edge',o['observation_id'],group_id=o['group_id'],
                      detail='Resource provider and receiver must both be established; no orientation guessed.',coverage_state='unknown')
            continue
        a,b=resolve(payer,o),resolve(receiver,o)
        if not a or not b:continue
        same=a.get('economic_group_id')==b.get('economic_group_id')
        date=o.get('event_date') or o.get('period_end')
        date=str(date) if date else None
        def member_at(e):
            return date is not None and (not e.get('membership_start') or str(e['membership_start'])<=date) and (
                not e.get('membership_end') or date<str(e['membership_end']))
        elimination='intragroup_not_eliminated' if same and not (member_at(a) and member_at(b)) else 'eliminated' if same else 'external'
        confirmed=a['entity_status']==b['entity_status']=='confirmed'
        numeric=confirmed and o.get('amount') is not None and date is not None and elimination=='external'
        if o['family']=='financing':numeric=numeric and o['tier'] in ('A','B','C') and o['stage'] in ('drawn_or_paid','recognized')
        lid=digest(['evidence_edge',o['observation_id']])
        row=dict(link_id=lid,edge_kind='amount' if numeric else 'relation',family=o['family'],type=o['link_type'],
           from_entity_id=a['entity_id'],to_entity_id=b['entity_id'],from_group_id=a.get('economic_group_id'),to_group_id=b.get('economic_group_id'),
           amount=o['amount'] if numeric else None,unit=o.get('unit'),currency=o.get('currency'),period_start=o.get('period_start'),
           period_end=o.get('period_end') or o.get('event_date'),event_date=o.get('event_date'),knowledge_date=o['knowledge_date'],
           stage=o['stage'],event_type=o.get('event_type'),instrument_key=o.get('instrument_key'),fact_id=o.get('tagged_fact_id'),
           observation_id=o['observation_id'],document_id=o['document_id'],locator=o['locator'],filing_status=o['filing_status'],
           assurance_level=o['assurance_level'],tier=o['tier'],counterparty_evidence=o['counterparty_evidence'],
           accounting_framework=o['accounting_framework'],source_perspective=o['source_perspective'],sales_channel=o.get('sales_channel'),
           financing_state='unknown',financing_policy='exposure_outstanding',linkage_class=o.get('linkage_class'),
           linkage_evidence='documented_link' if o.get('linkage_class') and o.get('linkage_quote') else 'search_incomplete',
           relationship_conclusion='causality_not_established',elimination_status=elimination,conditionality=o.get('conditionality'),
           trigger_description=o.get('trigger_description'),trigger_occurred=o.get('trigger_occurred'),
           vehicle_level=o.get('vehicle_level'),as_of=as_of)
        insert(db,'links',row);evidence.append((row,o))
        if not numeric and o.get('amount') is not None:
            exclusion(db,as_of,'relation_without_admissible_amount','amount_edge',lid,group_id=o['group_id'],
                detail='Unconfirmed identity, undated amount, intragroup elimination or financing evidence/stage requirement; amount retained in observations.',coverage_state='unknown')
    # Duplicate descriptions of the same tagged amount are related explicitly.
    db.execute('''INSERT INTO links (link_id,edge_kind,relation_type,amount_a_id,amount_b_id,resolved,resolution_evidence,as_of)
      SELECT sha256(a.link_id||b.link_id||'same_tagged_fact'),'relation','same_measure',a.link_id,b.link_id,true,
       'Same admissible tagged_fact_id; retained descriptions are not additive.',a.as_of
      FROM links a JOIN links b ON a.fact_id=b.fact_id AND a.fact_id IS NOT NULL AND a.link_id<b.link_id
       AND a.edge_kind='amount' AND b.edge_kind='amount' ''')
    return evidence


def nonadditive(db,root,as_of):
    import yaml
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    aliases={'rpo':['rpo_total'],'debt_principal':['debt_principal'],
      'debt_carrying_amount':['debt_carrying_current','debt_carrying_noncurrent'],
      'debt':['debt_carrying_current','debt_carrying_noncurrent'],
      'consolidated_debt':['debt_carrying_current','debt_carrying_noncurrent'],
      'lease_liability':['operating_lease_liability_current','operating_lease_liability_noncurrent','finance_lease_liability_current','finance_lease_liability_noncurrent'],
      'accounts_payable':['accounts_payable'],'contract_liabilities':['contract_liabilities_current'],
      'purchase_obligation':['purchase_obligation_total'],'supplier_finance_program':['supplier_finance_obligation'],
      'unpaid_capex':['unpaid_capex'],'lease_not_commenced':['lease_not_commenced']}
    db.execute('CREATE TEMP TABLE nonadditive_selectors (pair_id VARCHAR,side VARCHAR,quantity VARCHAR)')
    selectors=[]
    for p in cfg['non_additive_pairs']:
        for side in ['a','b']:
            q=p['selector_'+side]['model_quantity']
            selectors.extend((p['id'],side,x) for x in aliases.get(q,[q]))
    db.executemany('INSERT INTO nonadditive_selectors VALUES (?,?,?)',selectors)
    # One deposited amount may be classified twice; the self relation is itself
    # useful evidence that no additional amount exists.
    db.execute('''CREATE TEMP VIEW nonadditive_amounts AS SELECT fact_id AS amount_id,group_id,period_end,unit,
      model_quantity AS quantity,dimensions,NULL::VARCHAR AS instrument_key,value FROM selected_revised WHERE value IS NOT NULL
      UNION ALL SELECT observation_id,group_id,coalesce(period_end,event_date),unit,model_quantity,'{}',instrument_key,amount
       FROM usable_observations WHERE amount IS NOT NULL''')
    db.execute('''INSERT INTO links (link_id,edge_kind,pair_id,relation_type,amount_a_id,amount_b_id,resolved,resolution_evidence,as_of)
      SELECT DISTINCT sha256(sa.pair_id||a.amount_id||b.amount_id),'relation',sa.pair_id,'overlaps',a.amount_id,b.amount_id,false,
       'Candidate by fixed register and group/date or explicit instrument. Allocation or comparable bases not established.',?
      FROM nonadditive_selectors sa JOIN nonadditive_selectors sb ON sa.pair_id=sb.pair_id AND sa.side='a' AND sb.side='b'
      JOIN nonadditive_amounts a ON a.quantity=sa.quantity JOIN nonadditive_amounts b ON b.quantity=sb.quantity
       AND a.unit=b.unit AND ((a.group_id=b.group_id AND a.period_end=b.period_end AND a.dimensions=b.dimensions)
        OR (a.instrument_key IS NOT NULL AND a.instrument_key=b.instrument_key))''',[as_of])
    counts={p['id']:db.execute('SELECT count(*) FROM links WHERE pair_id=?',[p['id']]).fetchone()[0] for p in cfg['non_additive_pairs']}
    (root/'work/nonadditive_counts.json').write_text(json.dumps(counts,indent=2)+'\n')
