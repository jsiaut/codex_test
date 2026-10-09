from __future__ import annotations
from datetime import date,timedelta
from decimal import Decimal


def dependency_outcome(years: list[dict], threshold: Decimal, criteria: dict) -> dict:
    """E2/E3: strict refutation, adjacent fiscal years, adequate coverage only."""
    evaluable=[y for y in years if y['status'] in ('computed','bounded') and
        y.get('value_lower') is not None and y.get('value_upper') is not None]
    high=sorted(y['fiscal_year'] for y in evaluable if Decimal(str(y['value_lower']))>=threshold)
    consecutive=criteria['min_consecutive_support_years']
    if any(all(year+i in high for i in range(consecutive)) for year in high):
        return {'outcome':'supported','reason':None}
    if len(evaluable)>=criteria['min_evaluable_refutation_years'] and all(
        Decimal(str(y['value_upper']))<threshold/2 for y in evaluable):
        return {'outcome':'refuted','reason':None}
    missing=next((y.get('nd_reason') for y in years if y['status']=='not_determinable' and y.get('nd_reason')),None)
    return {'outcome':'indeterminate','reason':missing or
        ('interval_straddles_threshold' if any(Decimal(str(y['value_lower']))<threshold<=Decimal(str(y['value_upper'])) for y in evaluable)
        else 'precondition_not_met')}


def link_outcome(*, active: bool, linkage_classes: list[str], search_complete: bool) -> dict:
    if not active:
        return {'outcome':'indeterminate','reason':'precondition_not_met'}
    if set(linkage_classes).intersection({'L1','L2','L3','L4','L5'}):
        return {'outcome':'supported','reason':None}
    return {'outcome':'not_supported','reason':None} if search_complete else {
        'outcome':'indeterminate','reason':'search_incomplete'}


def chronology_outcome(financing_date: str | None, purchase_dates: list[str | None], criteria: dict) -> str:
    if not financing_date or not purchase_dates or any(d is None for d in purchase_dates):
        return 'indeterminate'
    origin=date.fromisoformat(financing_date)
    start,end=origin-timedelta(days=criteria['days_before']),origin+timedelta(days=criteria['days_after'])
    return 'compatible' if any(start<=date.fromisoformat(d)<=end for d in purchase_dates) else 'incompatible'


def nondiscrimination(outcomes: list[dict], threshold: Decimal) -> dict:
    eligible=[o for o in outcomes if o['statement'] in ('E1','E2') and o.get('headline',True)]
    if not eligible:
        return {'status':'not_determinable','reason':'no_eligible_pairs'}
    share=Decimal(sum(o['outcome']=='indeterminate' for o in eligible))/Decimal(len(eligible))
    return {'status':'computed','share':share,'publish_statement':share>threshold}
