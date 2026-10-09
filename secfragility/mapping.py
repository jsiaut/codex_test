from __future__ import annotations
import json
from pathlib import Path
import re

STATEMENT_QUANTITIES = {'revenue_total','net_income','operating_income','pretax_income_continuing',
    'total_assets','current_assets','total_liabilities','current_liabilities','temporary_equity',
    'equity_including_nci','cash_and_equivalents','cfo','cfi','cff','capex_cash',
    'gross_profit','cost_of_revenue','receivables','inventories','accounts_payable',
    'contract_liabilities_current','eps_diluted','diluted_shares_weighted'}

# Technical mappings fixed by definitions and presentation, before running
# their controls. In particular FaceAmount (at issuance) is not outstanding
# debt principal, and RPO Period1 is a duration, not a monetary tranche.
SUPPLEMENTAL_ANCHORS = {
    'income_tax_expense':['IncomeTaxExpenseBenefit'],
    'effective_tax_rate':['EffectiveIncomeTaxRateContinuingOperations'],
    'retained_earnings':['RetainedEarningsAccumulatedDeficit'],
    'fx_effect_on_cash':['EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsIncludingDisposalGroupAndDiscontinuedOperations',
        'EffectOfExchangeRateOnCashAndCashEquivalents'],
    'depreciation_amortization':['DepreciationDepletionAndAmortization'],
    'depreciation_expense':['Depreciation'],
    'gross_depreciable_ppe':['PropertyPlantAndEquipmentGross'],
    'land':['Land'], 'construction_in_progress':['ConstructionInProgressGross'],
    'contract_assets':['ContractWithCustomerAssetNet','ContractWithCustomerAssetNetCurrent'],
    'sbc_expense':['ShareBasedCompensation'],
    'debt_carrying_current':['LongTermDebtCurrent'],
    'debt_carrying_noncurrent':['LongTermDebtNoncurrent'],
    'debt_principal_due_next_fiscal_year':['LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths'],
    'debt_principal_due_second_fiscal_year':['LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo'],
    'depreciation_life_published':['PropertyPlantAndEquipmentUsefulLife'],
}


def build_mapping(meta: dict, config: dict, group_id: str, accession: str) -> list[dict]:
    inst=next(iter(meta['instance'].values()))
    tags,reports=inst['tag'],inst['report']
    statement_roles={r['role'] for r in reports.values() if r.get('groupType')=='statement'}
    mappings=[]
    anchors=dict(config['concept_anchors'],**config.get('concept_anchors_to_verify',{}),**SUPPLEMENTAL_ANCHORS)
    for quantity,names in anchors.items():
        for name in names:
            tag_key='us-gaap_'+name
            tag=tags.get(tag_key)
            if not tag:
                continue
            roles=tag.get('presentation',[])
            definition=tag.get('lang',{}).get('en-us',{}).get('role',{}).get('documentation')
            label=tag.get('lang',{}).get('en-us',{}).get('role',{}).get('label')
            if not roles or not definition:
                continue
            if quantity in STATEMENT_QUANTITIES and not statement_roles.intersection(roles):
                continue
            mappings.append({'group_id':group_id,'accession':accession,'model_quantity':quantity,
                'concept':'us-gaap:'+name,'definition':definition,'label':label,
                'presentation_roles':roles,'rule':'exact_config_anchor_with_presented_role_and_definition',
                'reference_keys':tag.get('auth_ref',[]),'variant':'original',
                'after_mismatch_change':False})
    return mappings


def apply_mapping(facts: list[dict], mappings: list[dict]):
    lookup={}
    for m in mappings:
        lookup.setdefault(m['concept'],[]).append(m)
    for fact in facts:
        candidates=lookup.get(fact['canonical_concept'],[])
        quantities={m['model_quantity'] for m in candidates}
        if len(quantities)==1:
            m=candidates[0]
            fact['model_quantity']=m['model_quantity']
            fact['mapping_rule']=m['rule']
            fact['mapping_evidence']=json.dumps({'accession':m['accession'],
                'definition':m['definition'],'roles':m['presentation_roles']},ensure_ascii=False)
        # An ambiguous concept is retained as a fact, never selected to make a
        # control balance. Supplemental mappings require a documented decision.


def candidate_unanchored(meta: dict, config: dict) -> list[dict]:
    inst=next(iter(meta['instance'].values()))
    labels=re.compile(r'(interest|debt|depreciation|construction|tax rate|income tax|retained earnings|stock.based|contract asset)',re.I)
    output=[]
    for name,tag in inst['tag'].items():
        lang=tag.get('lang',{}).get('en-us',{}).get('role',{})
        label=lang.get('label','')
        if labels.search(label) and tag.get('xbrltype')!='textBlockItemType' and tag.get('presentation'):
            output.append({'concept':name.replace('_',':',1),'label':label,
                'definition':lang.get('documentation'), 'presentation_roles':tag['presentation'],
                'reference_keys':tag.get('auth_ref',[])})
    return output
