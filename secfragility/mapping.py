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
    'restricted_cash_and_equiv_current':['RestrictedCashAndCashEquivalentsAtCarryingValue'],
    'restricted_cash_and_equiv_noncurrent':['RestrictedCashAndCashEquivalentsNoncurrent'],
    'purchase_obligation_total':['UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount'],
    'lease_not_commenced':['UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount'],
    'concentration_risk_percentage':['ConcentrationRiskPercentage1'],
}


def build_mapping(meta: dict, config: dict, group_id: str, accession: str,replacements=None) -> list[dict]:
    inst=next(iter(meta['instance'].values()))
    tags,reports=inst['tag'],inst['report']
    statement_roles={r['role'] for r in reports.values() if r.get('groupType')=='statement'}
    mappings=[]
    replacements=replacements or {}
    anchors=dict(config['concept_anchors'],**config.get('concept_anchors_to_verify',{}),**SUPPLEMENTAL_ANCHORS)
    for quantity,names in anchors.items():
        if quantity in ('vendor_financed_ppe_additions','stock_paid_ppe_additions'):
            # The indicative anchors describe generic noncash acquisitions or
            # stock issuance; neither establishes this payment mode for PPE.
            continue
        for name in names:
            tag_key='us-gaap_'+name
            tag=tags.get(tag_key)
            if not tag:
                continue
            roles=tag.get('presentation',[])
            definition=tag.get('lang',{}).get('en-us',{}).get('role',{}).get('documentation')
            label=tag.get('lang',{}).get('en-us',{}).get('role',{}).get('label')
            selected_quantity=quantity
            issuer_labels=tag.get('lang',{}).get('en-us',{}).get('role',{})
            lease_label=' '.join(str(v) for k,v in issuer_labels.items() if k!='documentation')
            explicit_uncommenced=bool(re.search(r'leases?.{0,100}(?:not yet commenced|not commenced|have not yet commenced)',lease_label,re.I))
            if quantity=='lease_not_commenced' and not explicit_uncommenced:continue
            if quantity=='purchase_obligation_total' and explicit_uncommenced:selected_quantity='lease_not_commenced'
            if not roles or not definition:
                continue
            if quantity in STATEMENT_QUANTITIES and not statement_roles.intersection(roles):
                continue
            mappings.append({'group_id':group_id,'accession':accession,'model_quantity':selected_quantity,
                'concept':replacements.get('us-gaap:'+name,'us-gaap:'+name),'original_concept':'us-gaap:'+name,'definition':definition,'label':label,
                'presentation_roles':roles,'rule':'exact_config_anchor_with_presented_role_and_definition',
                'reference_keys':tag.get('auth_ref',[]),'variant':'original',
                'definition_source':tag.get('definition_source','issuer_MetaLinks'),
                'metadata_origin':meta.get('metadata_origin','issuer_MetaLinks'),
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


def refresh(db,root,collection):
    import yaml
    from .metadata import load
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    replacements=json.loads((root/'work/deprecations.json').read_text())['mapping']
    mappings=[];rows=[]
    for accession,filing in collection['filings'].items():
        metadata=load(root,filing['resources'],accession)
        if metadata is None:continue
        chosen=build_mapping(metadata,cfg,filing['group'],accession,replacements)
        mappings.extend(chosen);lookup={}
        for m in chosen:lookup.setdefault(m['concept'],[]).append(m)
        for concept,entries in lookup.items():
            if len({m['model_quantity'] for m in entries})!=1:continue
            m=entries[0]
            rows.append((accession,concept,m['model_quantity'],m['rule'],json.dumps({'accession':accession,
                'definition':m['definition'],'roles':m['presentation_roles']},ensure_ascii=False)))
    db.execute('CREATE TEMP TABLE refreshed_mappings (accession VARCHAR,canonical_concept VARCHAR,quantity VARCHAR,rule VARCHAR,evidence VARCHAR)')
    db.executemany('INSERT INTO refreshed_mappings VALUES (?,?,?,?,?)',rows)
    db.execute('''UPDATE facts SET model_quantity=m.quantity,mapping_rule=m.rule,mapping_evidence=m.evidence
        FROM refreshed_mappings m WHERE facts.accession=m.accession AND facts.canonical_concept=m.canonical_concept
         AND facts.document_rank>=0 AND facts.is_tagged=true''')
    (root/'work/concept_mappings.json').write_text(json.dumps(mappings,ensure_ascii=False,indent=2))
