from __future__ import annotations
from decimal import Decimal


class InvalidAggregate(ValueError):
    def __init__(self,invariant: str):
        self.invariant=invariant
        super().__init__(invariant)


def guarded_sum(elements: list[dict], relations: list[dict], *, homogeneous_basis: str,
                expected_count: int) -> dict:
    if not homogeneous_basis:
        raise InvalidAggregate('homogeneous_basis_required')
    if any(e.get('tier') not in ('A','B','C','D') for e in elements):
        raise InvalidAggregate('a_inadmissible_evidence')
    if len({e.get('currency') for e in elements})>1:
        raise InvalidAggregate('b_mixed_currency')
    if len({e.get('unit') for e in elements})>1:
        raise InvalidAggregate('incompatible_units')
    ids=[e['amount_id'] for e in elements]
    if len(ids)!=len(set(ids)):
        raise InvalidAggregate('c_nonunique_amount_keys')
    selected=set(ids)
    if any(r.get('amount_a_id') in selected and r.get('amount_b_id') in selected and
           r.get('relation_type') in ('same_measure','component_of','covers','overlaps','eliminated_with','transfers_to')
           for r in relations):
        # A resolved relationship alone does not define an additive allocation.
        # The caller must select its disjoint residuals before invoking the sum.
        return {'status':'blocked_overlap','value':None,'nd_reason':'overlapping_selected_amounts'}
    perspectives={}
    for e in elements:
        perspectives.setdefault(e['node_id'],set()).add(e['source_perspective'])
    if any(len(p)>1 for p in perspectives.values()):
        raise InvalidAggregate('e_mixed_source_perspectives')
    if len({e['accounting_framework'] for e in elements})>1:
        raise InvalidAggregate('f_mixed_accounting_frameworks')
    if any(e.get('entity_status')!='confirmed' or e.get('abstained') for e in elements):
        raise InvalidAggregate('g_pending_entity_or_abstention')
    if any(e.get('measurement_basis')!=homogeneous_basis for e in elements):
        raise InvalidAggregate('heterogeneous_measurement_bases')
    if any(e.get('elimination_status') in ('unresolved','intragroup_not_eliminated') for e in elements):
        raise InvalidAggregate('unresolved_consolidation_elimination')
    if not elements:
        return {'status':'not_determinable','value':None,'nd_reason':'empty_numerator'}
    known=[e for e in elements if e.get('value') is not None]
    if not known:
        return {'status':'not_determinable','value':None,'nd_reason':'missing_terms'}
    return {'status':'computed' if len(known)==expected_count else 'partial',
        'value':sum((Decimal(str(e['value'])) for e in known),Decimal(0)),
        'nd_reason':None if len(known)==expected_count else 'missing_terms'}
