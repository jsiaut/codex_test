"""C5 never equates a client commitment with an unrelated supplier total."""
import json
from collections import defaultdict
from datetime import date
from .assembly import rows
from .database import insert
from .xbrl import digest


def run(db,as_of):
    os=rows(db,'SELECT * FROM usable_observations WHERE family IS NOT NULL AND amount IS NOT NULL')
    by=defaultdict(list)
    for o in os:
        if o.get('instrument_key'):by[o['instrument_key']].append(o)
    pairs=[]
    for key,observations in by.items():
        for i,a in enumerate(observations):
            for b in observations[i+1:]:
                if a['group_id']==b['group_id']:continue
                da=a.get('period_end') or a.get('event_date');dbdate=b.get('period_end') or b.get('event_date')
                comparable=bool(da and dbdate and abs((da-dbdate).days)<=45 and a['unit']==b['unit'] and a['accounting_framework']==b['accounting_framework'])
                bases=(a.get('model_quantity'),b.get('model_quantity'))
                kind='prepayment' if a['link_type']==b['link_type']=='prepayment' else 'financing' if a['family']==b['family']=='financing' and a['event_type']==b['event_type']=='funding' else None
                # The commercial gross/net basis and RPO agreement attribution
                # are required explicit author fields, not guessed by name.
                comparable=comparable and kind is not None and bool(a['measurement_basis'] and a['measurement_basis']==b['measurement_basis'])
                tol=None
                if comparable and a.get('tagged_fact_id') and b.get('tagged_fact_id'):
                    r=db.execute('SELECT sum(precision_radius(decimals)),count(precision_radius(decimals)) FROM eligible_facts WHERE fact_id IN (?,?)',[a['tagged_fact_id'],b['tagged_fact_id']]).fetchone()
                    if r[1]==2:tol=r[0]
                status='not_testable' if tol is None else 'ok' if abs(a['amount']-b['amount'])<=tol else 'mismatch'
                for view in ('as_known','revised'):
                    insert(db,'controls',dict(control='c5_bilateral',group_id=a['group_id'],period_start=str(a['period_start'] or da or 'none'),period_end=str(da or 'none'),view=view,as_of=as_of,
                        breakdown_key=digest([a['observation_id'],b['observation_id']]),status=status,lhs=a['amount'] if comparable else None,rhs=b['amount'] if comparable else None,
                        residual=a['amount']-b['amount'] if tol is not None else None,tolerance=tol,tolerance_basis='instance' if tol is not None else 'none',
                        explanation_code='documented_bilateral_difference' if status=='mismatch' else 'comparable_basis_date_identity_or_precision_not_established' if status=='not_testable' else None,
                        evidence=json.dumps([a['observation_id'],b['observation_id']])))
                pairs.append((a['group_id'],key))
    # Visible commercial relations for which the other filing's matching
    # amount is unavailable remain explicit untestable controls.
    for o in os:
        if o['family']!='commercial':continue
        for view in ('as_known','revised'):
            insert(db,'controls',dict(control='c5_bilateral',group_id=o['group_id'],period_start=str(o['period_start'] or o['period_end'] or o['event_date'] or 'none'),
              period_end=str(o['period_end'] or o['event_date'] or 'none'),view=view,as_of=as_of,breakdown_key='unpaired|'+o['observation_id'],
              status='not_testable',tolerance_basis='none',explanation_code='matching_counterparty_filing_amount_same_agreement_not_established',evidence=json.dumps([o['observation_id']])))
    for o in os:
        if o['link_type']!='revenue_recognized' or o['counterparty_evidence'] not in ('named','derivable'):continue
        for view in ('as_known','revised'):
            insert(db,'controls',dict(control='c16_concentration',group_id=o['group_id'],period_start=str(o['period_start'] or o['period_end'] or 'none'),period_end=str(o['period_end'] or 'none'),view=view,as_of=as_of,
               breakdown_key='named|'+o['observation_id'],status='not_testable',tolerance_basis='none',explanation_code='explicit_named_percentage_same_benchmark_not_established',evidence=json.dumps([o['observation_id']])))
