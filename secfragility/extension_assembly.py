"""Interpret versioned readings without changing their immutable observations.

The component ledger publishes source amounts individually. It is deliberately
not an aggregate: bases, conditions and overlapping representations stay apart.
"""
import json
from collections import defaultdict
from pathlib import Path
from .assembly import rows, exclusion
from .database import bulk_insert, sql_literal
from .reader import block_for

FAMILIES = ('investments_note', 'debt_note', 'lease_note',
            'commitments_note', 'concentration_narrative')

# Fixed before calculation; values and successful observations do not select
# expected cells. The unopened lender/discovery catalogues stay outside scope.
NOTE_MEASURES = {
    'investment_gain_loss', 'investment_impairment', 'rpo_total', 'rpo_beyond_12m',
    'lease_not_commenced_bridge', 'exposure_matrix', 'customer_concentration_anonymous',
    'supplier_concentration', 'segment_revenue', 'segment_profit', 'segment_significant_expenses',
    'liq_cash_to_12m_outflows', 'liq_undrawn_committed_facilities', 'cov_interest_coverage',
    'cov_pik_interest', 'customer_advances', 'capitalized_interest', 'capex_accrual',
    'finance_lease_additions', 'vendor_financed_additions', 'stock_paid_additions',
    'operating_lease_rou_additions', 'sig_covenant_events', 'sig_pledged_assets',
}


def extend_universe(root):
    if not opened(root):
        return
    from .database import MEASURE_TERMS
    path=root/'work/expected_universe.json'
    universe=json.loads(path.read_text())
    cells=universe['cells']
    def key(c):
        return tuple(c[k] for k in ('measure','group_id','counterparty_id','period_start',
                                    'period_end','view','term','breakdown_key'))
    present={key(c) for c in cells}
    for q in universe['quarters']:
        if q.get('in_analysis_window') is False:
            continue
        for name in sorted(NOTE_MEASURES):
            for term in MEASURE_TERMS[name]:
                for view in ('as_known','revised'):
                    c=dict(measure=name,group_id=q['group_id'],counterparty_id='none',
                           period_start=q['period_start'],period_end=q['period_end'],view=view,
                           term=term,breakdown_key=q.get('breakdown_key','none'),
                           as_of=universe['as_of'],expected=True,calendar_basis=q['calendar_basis'])
                    if key(c) not in present:
                        cells.append(c);present.add(key(c))
    universe['extension_expected_catalogue']=sorted(NOTE_MEASURES)
    path.write_text(json.dumps(universe,indent=2,ensure_ascii=False)+'\n')


def opened(root):
    p = root / 'work/extension_authorization.json'
    return set(json.loads(p.read_text())['components']) if p.exists() else set()


def interpretations(db, root, as_of):
    """Apply named, already documented attribution decisions in a SQL view."""
    p = root / 'work/extension_attribution_reviews.json'
    reviews = json.loads(p.read_text()) if p.exists() else []
    changes = defaultdict(dict)
    output = []
    for review in reviews:
        key = review['content_key']
        candidates = rows(db, 'SELECT * FROM observations WHERE content_key=?', [key])
        indexes = review.get('tagged_candidate_indexes',
                             [review['tagged_candidate_index']] if 'tagged_candidate_index' in review else [])
        fids = set()
        if indexes:
            block = block_for(root, key)
            fids = {block['candidates'][i]['fact_id'] for i in indexes}
        selected = [o for o in candidates if
                    (o.get('tagged_fact_id') in fids if indexes else
                     review.get('quote', '') in o['quote'] if review.get('quote') else
                     o.get('model_quantity') == review['affected_quantity'])]
        if review['decision'].startswith('exclude_F4_'):
            selected = [o for o in selected if o.get('event_observable') == 'F4' or
                        o.get('model_quantity') == 'sig_covenant_events']
        for o in selected:
            change = changes[o['observation_id']]
            decision = review['decision']
            if decision.startswith('exclude_vie_'):
                change['category_id'] = None
            elif decision.startswith('exclude_F4_'):
                change.update(event_observable=None, event_present=None,
                              model_quantity='ordinary_facility_change',
                              event_type='termination' if 'termination' in decision else 'signing')
            elif decision.startswith('exclude_undrawn_'):
                change['block'] = None
            elif decision.startswith('preserve_conditional_'):
                change['issuer_treatment'] = 'Conditional right to consideration; not an unconditional receivable.'
            elif decision.startswith('classify_535_'):
                change.update(model_quantity='derivative_gross_liability',
                              issuer_treatment='535m gross; 500m presented after 35m balance-sheet offset. Neither is cash collateral.')
            elif decision.startswith('correct_comparator_'):
                change['issuer_treatment'] = '693m own convertible debt fair value; 86m principal and 84m net carrying amount.'
            else:
                raise ValueError('Undocumented interpretation decision: ' + decision)
            exclusion(db, as_of, 'attribution_interpretation', 'observation_interpretation',
                      o['observation_id'] + ':' + decision, group_id=o['group_id'],
                      accession=o['accession'], content_key=key,
                      detail=json.dumps(review, ensure_ascii=False), coverage_state='observed')
        output.append(dict(review, matched_observations=[o['observation_id'] for o in selected],
                           assembly_status='applied' if selected else 'not_matched'))
    fields = sorted({field for change in changes.values() for field in change})
    replacements = []
    for field in fields:
        cases = ' '.join('WHEN observation_id=' + sql_literal(oid) + ' THEN ' +
                         ('NULL' if change[field] is None else sql_literal(str(change[field])))
                         for oid, change in changes.items() if field in change)
        replacements.append(f'CASE {cases} ELSE {field} END AS {field}')
    replace = ' REPLACE (' + ','.join(replacements) + ')' if replacements else ''
    db.execute('CREATE TEMP VIEW interpreted_observations AS SELECT *' + replace + ' FROM observations')
    (root / 'work/extension_interpretation_results.json').write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + '\n')


DIRECT = {
    'remaining_performance_obligations': ('rpo_total', 'none'),
    'rpo': ('rpo_total', 'none'), 'RPO_total': ('rpo_total', 'none'),
    'rpo_total': ('rpo_total', 'none'),
    'investment_impairment': ('investment_impairment', 'none'),
    'investment_gain_loss': ('investment_gain_loss', 'published'),
    'commercial_cloud_revenue': ('segment_revenue', 'none'),
    'cloud_and_onpremise_management_revenue': ('segment_revenue', 'none'),
    'cloud_and_onpremise_segment_margin': ('segment_profit', 'none'),
    'data_center_market_revenue': ('segment_revenue', 'none'),
    'data_center_end_market_revenue': ('segment_revenue', 'none'),
    'specialized_market_revenue': ('segment_revenue', 'none'),
    'customer_revenue_concentration': ('customer_concentration_anonymous', 'none'),
    'revenue_customer_concentration': ('customer_concentration_anonymous', 'none'),
    'customer_advances': ('customer_advances', 'none'),
    'capitalized_interest': ('capitalized_interest', 'none'),
}


def metric(quantity):
    # These are authored quantity names, never words searched in source text.
    if quantity in DIRECT:
        return DIRECT[quantity]
    if quantity and quantity.endswith('_segment_revenue'):
        return 'segment_revenue', 'none'
    if quantity and quantity.endswith(('_segment_operating_income', '_segment_operating_profit')):
        return 'segment_profit', 'none'
    return None


def components(db, root, as_of):
    """Publish all monetary note components and mapped metrics, without sums."""
    if not opened(root):
        return
    result = []
    selections = rows(db, 'SELECT * FROM usable_observations WHERE amount IS NOT NULL')
    cutoffs = {(g, str(e)): (str(s),str(t)) for g, s, e, t in
               db.execute('SELECT * FROM quarter_cutoffs').fetchall()}
    quantities = defaultdict(int)
    for o in selections:
        end = str(o.get('period_end') or o.get('event_date') or '')
        if not end:
            continue
        quantity = o.get('model_quantity') or 'unclassified_authored_amount'
        quantities[quantity] += 1
        money = o.get('currency') and o.get('unit') in (
            o['currency'], 'http://www.xbrl.org/2003/iso4217:' + o['currency'])
        direct = metric(quantity)
        for view in ('as_known', 'revised'):
            anchor=cutoffs.get((o['group_id'], end))
            cutoff = (anchor[1] if anchor else None) if view == 'as_known' else as_of
            if not cutoff or str(o['knowledge_date']) > cutoff[:10]:
                continue
            base = dict(group_id=o['group_id'], period_start=str(o.get('period_start') or (anchor[0] if anchor else 'none')),
                        period_end=end, view=view, as_of=as_of, information_cutoff=cutoff,
                        variant='text:' + o['observation_id'], unit=o['unit'], currency=o.get('currency'),
                        value=o['amount'], status='partial', coverage_state='observed',
                        nd_reason='individual_source_component_not_an_additive_total',
                        knowledge_date=o['knowledge_date'], lineage=json.dumps([o['observation_id']]),
                        evidence_profile=json.dumps([o['tier']]), source_perspective=o['source_perspective'],
                        accounting_framework=o['accounting_framework'], overlap_possible=True,
                        basis_break=o.get('basis_break'), recast_cause=o.get('recast_cause'))
            if money and o.get('block'):
                basis = o.get('measurement_basis') or 'basis_not_classified'
                key = '|'.join([o['block'], o.get('category_id') or 'unclassified', basis, quantity])
                result.append(dict(base, measure='exposure_matrix', breakdown_key=key))
            if direct:
                name, term = direct
                exact=o.get('amount_qualifier')=='exact'
                result.append(dict(base, measure=name, term=term, breakdown_key=quantity,
                                   status='computed' if exact else 'partial',
                                   nd_reason=None if exact else 'qualified_source_amount'))
    bulk_insert(db, 'measures', result, root, 'extension_components')
    (root / 'work/extension_component_loading.json').write_text(json.dumps(
        dict(accepted_amount_observations=len(selections), published_component_rows=len(result),
             quantities=dict(sorted(quantities.items())), amounts_aggregated=False), indent=2) + '\n')
