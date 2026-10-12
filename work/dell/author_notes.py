"""Observations personally authored by the executing analyst, never a text scan."""
from pathlib import Path
import json,hashlib
from decimal import Decimal
from secfragility.dell_sources import persist
from secfragility.text import normalize_html
from secfragility.xbrl import digest
from secfragility.observations import validate_semantics

ROOT=Path('.').resolve();BASE=ROOT/'work/dell'
Q=json.loads((BASE/'reading_queue.json').read_text())
REG=json.loads((BASE/'filings.json').read_text())
OUT=[];LEDGER=[];AMOUNT_PROOFS=[]

def block(prefix):
    r=next(r for r in Q if r['key'].startswith(prefix))
    return r,json.loads((ROOT/r['path']).read_text())

def note(prefix,quantity,quote,*,fact=None,amount=None,currency=None,period_start=None,
         period_end=None,finding,**extra):
    r,b=block(prefix)
    # Explicit analyst-chosen sentence/row endpoints, not keyword eligibility.
    if isinstance(quote,tuple):
        a=b['text'].index(quote[0]);z=b['text'].index(quote[1],a)+len(quote[1]);quote=b['text'][a:z]
    raw=(ROOT/b['source_path']).read_bytes()
    row=dict(content_key=b['content_key'],document_id=b['document_id'],accession=b['accession'],
        group_id='DELL',entity_id='cik:0001571996',abstained=False,quote=quote,
        locator=f"rawbytes:{b['raw_byte_start']}:{b['raw_byte_end']};note={b['label']}",
        raw_byte_start=b['raw_byte_start'],raw_byte_end=b['raw_byte_end'],
        model_quantity=quantity,amount_nature=quantity,period_start=period_start,
        period_end=period_end or b['report_date'],issuer_treatment=finding,
        stage='recognized',counterparty_evidence='anonymous')
    row.update(extra)
    if fact:
        f=next(f for f in b['candidates'] if f['fact_id'].startswith(fact))
        row.update(amount=f['value'],unit=f['unit'],currency=f.get('currency'),tagged_fact_id=f['fact_id'],
            amount_origin='tagged_reference',period_start=f.get('period_start'),period_end=f['period_end'])
    elif amount is not None:
        row.update(amount=str(amount),amount_origin='narrative_only',unit=currency,currency=currency)
    validate_semantics(row,b,raw)
    row.update(observation_id=digest(['Dell_authored_v1',r['key'],quantity,quote,fact,period_end]),
        knowledge_date=b['knowledge_date'],filing_status='filed',
        assurance_level='audited' if b['form'].startswith('10-K') else 'reviewed',
        tier='A' if b['form'].startswith('10-K') else 'B',location='financial_statements_and_notes',
        source_perspective='reporting_entity',accounting_framework='us_gaap',as_of=json.loads((BASE/'issuer.json').read_text())['source_cutoff'])
    OUT.append(row)

note('fb9ca6','dfs_financing_originations',
     'New financing originations were $7.5 billion and $2.4 billion for the three months ended July 31, 2026 and August 1, 2025, respectively, and $10.3 billion and $4.0 billion for the six months ended July 31, 2026 and August 1, 2025, respectively.',
     fact='748972',finding='Originations include Dell and complementary third-party technology; no AI/customer allocation.')
note('fb9ca6','dfs_financing_receivables_net','The following table presents the components of the Company’s financing receivables as of the dates indicated:',fact='952ea5',finding='Net portfolio includes lease/loan receivables and residual interest; distinct from trade AR.')
note('fb9ca6','dfs_customer_receivables_gross','The following table presents the components of the Company’s financing receivables as of the dates indicated:',fact='3dbfe0',finding='Gross contractual receivables plus accrued interest, before credit allowance and residual.')
note('fb9ca6','dfs_credit_loss_allowance','The following table presents the changes in allowance for financing receivable losses for the periods indicated:',fact='5d5fde',finding='Allowance for expected credit losses, not incurred losses or immediate cash outflow.')
note('fb9ca6','dfs_credit_loss_provision','The following table presents the changes in allowance for financing receivable losses for the periods indicated:',fact='39f71a',finding='Quarterly expense; distinct from the stock of allowance and gross originations.')
note('fb9ca6','dfs_past_due_31_90','The following table presents the aging of the Company’s customer financing receivables, gross, including accrued interest, as of the dates indicated:',fact='f3247d',finding='Published aging bucket; identities anonymous.')
note('fb9ca6','dfs_past_due_over_90','The following table presents the aging of the Company’s customer financing receivables, gross, including accrued interest, as of the dates indicated:',fact='6b23d8',finding='Over-90-days balance; doubtful accounts may also be in current bucket.')
note('fb9ca6','dfs_lower_credit_quality','The following tables present customer receivables, gross, including accrued interest, by credit quality indicator, as of the dates indicated:',fact='b22c06',finding='Issuer internal relative risk grade; not default probability or external rating.')
note('fb9ca6','dfs_aging_limitations','The receivables identified as doubtful for collectibility may be classified as current for aging purposes.',finding='Current bucket cannot be treated as credit-risk-free.')
note('fb9ca6','dfs_sales_type_lease_revenue','The following table presents amounts included in the Condensed Consolidated Statements of Income related to sales-type lease activity for the periods indicated:',fact='c7f4c7',finding='Product revenue recognized on sales-type lease commencement; not cash collections or all AI sales.')
note('fb9ca6','dfs_operating_lease_assets_net','The following table presents the components of the Company’s operating lease portfolio included in property, plant, and equipment, net as of the dates indicated:',fact='9db422',finding='Lessor equipment asset; not Dell lessee ROU liability and not a financing receivable.')
note('fb9ca6','dfs_debt_recourse',
     'The majority of DFS debt is non-recourse to Dell Technologies and represents borrowings under securitization programs and structured financing programs for which the Company’s risk of loss is limited to transferred lease and loan payments and associated equipment.',
     finding='Nonrecourse applies to the specified securitization/structured debt, not all debt management allocates to DFS.',recourse='majority_nonrecourse_to_Dell;not_all_DFS_related_debt',is_ring_fenced=True)
note('fb9ca6','dfs_funding_trigger',
     'The asset-based financing facility contains standard structural features related to the performance of the funded receivables, which include defined credit losses, delinquencies, average credit scores, and minimum collection requirements. In the event one or more of these criteria are not met and the Company is unable to restructure the facility, no further funding of receivables will be permitted and the timing of the Company’s expected cash flows from over-collateralization will be delayed. As of July 31, 2026, these criteria were met.',
     finding='Funding-stop mechanism documented, thresholds not disclosed in this note; trigger not reported as occurred.',trigger_occurred='no')
note('fb9ca6','dfs_vie_consolidation',
     'The SPEs are bankruptcy-remote legal entities with separate assets and liabilities. The purpose of the SPEs is to facilitate the funding of customer lease and loan payments and associated equipment in the capital markets.',
     finding='Consolidated securitization SPEs remain within Dell exposure; no second addition to consolidated debt.')
note('fb9ca6','dfs_receivables_sales_immaterial',
     'To manage certain concentrations of customer credit exposure, the Company may sell selected fixed-term customer receivables to unrelated third parties on a periodic basis, without recourse. The amounts of customer receivables sold for this purpose were immaterial for both the six months ended July 31, 2026 and August 1, 2025.',
     finding='Immaterial is not zero; factoring is outside the financing graph; servicing retained.')
note('e225e5','investment_upward_adjustment_anonymous',
     'During the six months ended July 31, 2026, net unrealized gains on non-marketable securities were primarily attributable to an upward observable price adjustment of $0.6 billion related to a single investee.',
     fact='1224be',finding='One investee unnamed; no attribution to an AI lab or primary cash funding inference.')
note('e225e5','investment_unrealized_gain_net','The following table presents unrealized gains and losses on marketable and non-marketable equity and other securities for the periods indicated:',fact='b9ad50',finding='Quarterly net valuation gain; noncash nature preserved, distinct from cumulative unrealized stock.')
note('4f67e9','debt_principal','The following table summarizes the Company’s outstanding debt as of the dates indicated:',fact='80cd7c',finding='Total principal includes DFS principal; do not add DFS debt again.')
note('4f67e9','debt_carrying_amount','The following table summarizes the Company’s outstanding debt as of the dates indicated:',fact='e650ab',finding='Carrying amount after issuance costs/discount; distinct from principal.')
note('4f67e9','revolver_zero_draw',
     'As of July 31, 2026, the Company had no outstanding borrowings under the revolving credit facility.',finding='Explicit zero of this instrument only; letters of credit still reduce available capacity.',fact='f0c726',stage='available')
note('4f67e9','commercial_paper_zero_draw',
     'As of July 31, 2026, the Company had no outstanding issuances under the commercial paper program.',finding='Zero outstanding, USD5bn program is capacity rather than additional committed cash.',fact='52e269',stage='available')
note('4f67e9','covenant_compliance',
     'The Company was in compliance with this financial covenant as of July 31, 2026.',finding='Issuer confirms compliance with interest-coverage covenant; not evidence of a waiver or default.',trigger_occurred='no')
note('e819fa','rpo_scope',
     'The Company excludes from remaining performance obligations the revenue under cancelable contracts where there is no substantive termination penalty.',finding='RPO is distinct from orders, shipments and nonbinding AI pipeline; no named-client allocation.')
note('b47ca1','purchase_obligation_scope',
     'Purchase obligations include the non-cancelable portion or the minimum cancellation fee under the contract, and are primarily related to commitments with suppliers, software maintenance, and support services.',finding='Minimum binding amounts/cancellation fee, not all projected component purchases.')
note('b47ca1','contract_manufacturer_guarantee_maximum',
     'As of July 31, 2026, the Company’s maximum potential future payments under the financial guarantees is $8.6 billion, which the Company would have recourse to recover in full from the applicable contract manufacturers.',
     fact='74ecd5',finding='Maximum contingent payments with recourse to unnamed manufacturers; not guaranteed cash already paid.',block='contingent_obligations',category_id='guarantee',measurement_basis='maximum_potential_future_payments',stage='signed',recourse='full_recovery_from_contract_manufacturer')
note('d67f43','customer_concentration_anonymous',
     'One customer accounted for 12% of the Company’s consolidated net revenue for the fiscal year ended January 30, 2026, with substantially all of such net revenue attributable to the sale of ISG offerings.',
     finding='Anonymous annual customer; cannot be identified from media or linked to DFS by growth alone.',fact='c90ade')
note('d67f43','contract_manufacturer_offset',
     'The Company offset its corresponding payables against $13.0 billion and $4.7 billion of such receivables as of January 30, 2026 and January 31, 2025, respectively.',
     finding='Component transfers to manufacturers are not product revenue; gross receivables offset against trade payables.')
note('18990c','supplier_finance_program',
     'As of July 31, 2026 and January 30, 2026, the Company had $3.1 billion and $2.0 billion, respectively, included within accounts payable on the Condensed Consolidated Statements of Financial Position representing invoices due to suppliers confirmed as valid under the SCF Program.',
     fact='118978',finding='Already in AP, no additional debt or named customer financing edge.',block='recognized_liabilities',category_id='supplier_finance_program',measurement_basis='confirmed_invoices_in_accounts_payable')
note('9af485','lessee_scope',
     'As of July 31, 2026 and January 30, 2026, there were no material finance leases in which the Company was a lessee.',finding='Immaterial finance leases are not explicit zero payments; Dell as lessee distinct from DFS lessor.')
note('d0e30b','dfs_upfront_profit',
     'On commencement of sales-type leases, the Company recognizes profit up-front, and amounts due from the customer under the lease contract are recognized as financing receivables on the Consolidated Statements of Financial Position.',finding='Documented accounting route for booked product revenue before collections; no causal customer allocation.')
note('d0e30b','dfs_secured_borrowing',
     'The asset securitizations in the SPEs are accounted for as secured borrowings.',finding='Securitization leaves assets/debt consolidated, distinct from sale without recourse.')
note('b5e0a6','vmware_control_and_related_party_cutoff',
     'Upon Broadcom’s acquisition of VMware, Michael Dell’s ownership interest in VMware and his position as Chairman of the Board of VMware terminated, and the Company determined no related party relationship exists with Broadcom or VMware effective as of November 22, 2023.',finding='Related-party status and economic control change dated; no merger of Dell into Broadcom.',counterparty='VMware',counterparty_evidence='named')
note('b5e0a6','dfs_vmware_end_customer_financing',
     'DFS provided financing to certain VMware end-users, which resulted in the recognition of amounts due to related parties on the Consolidated Statements of Financial Position.',finding='Borrowers are unnamed VMware end users, not VMware itself; cannot classify VMware or Broadcom financed.',counterparty='VMware',counterparty_evidence='named',period_end='2023-11-21')
note('60800c','vmware_embedded_commercial_relation',
     'The Company continues to integrate and embed certain VMware products and services with the Company’s VxRail solution to end-user customers.',finding='Documented sales-channel relationship continues; no direct end-customer revenue attribution.',counterparty='VMware',counterparty_evidence='named',family='commercial',link_type='purchase',sales_channel='integrator')

def excerpt(accession,quantity,quote,*,name=None,finding,table_row=None,**extra):
    filing=REG[accession];m=filing['metadata'];r=filing['resources'][name or m['primaryDocument']]
    raw=(ROOT/r['path']).read_bytes();text=normalize_html(raw)
    if isinstance(quote,tuple):
        a=text.index(quote[0]);z=text.index(quote[1],a)+len(quote[1]);quote=text[a:z]
    b=dict(content_key=digest([text]),text=text,raw_byte_start=0,raw_byte_end=len(raw),candidates=[])
    row=dict(content_key=b['content_key'],document_id=digest([r['url']]),accession=accession,group_id='DELL',entity_id='cik:0001571996',
        abstained=False,quote=quote,raw_byte_start=0,raw_byte_end=len(raw),locator='whole_source_byte_bounds;exact_quote_in_normalized_HTML',
        model_quantity=quantity,amount_nature=quantity,issuer_treatment=finding,knowledge_date=m['filingDate'],
        filing_status='filed',assurance_level='unaudited',tier='C',location='MDandA_or_filed_item',source_perspective='reporting_entity',
        accounting_framework='us_gaap',counterparty_evidence='anonymous',as_of=json.loads((BASE/'issuer.json').read_text())['source_cutoff'])
    row.update(extra)
    if table_row:
        from secfragility.dell_evidence import table_amount
        proof=table_amount(quote,table_row,row['amount'])
        assert row['currency']=='USD' and row['unit']=='USD' and row['amount_origin']=='narrative_only'
        AMOUNT_PROOFS.append(dict(proof,quantity=quantity,document_id=row['document_id'],quote_sha256=digest(quote)))
        # Standard validator still validates content, bytes, identity and quote.
        # This additional structural proof handles USD cells without a repeated
        # currency symbol, which the generic narrative token rule rejects.
        validate_semantics(dict(row,amount=None),b,raw)
    else:validate_semantics(row,b,raw)
    row['observation_id']=digest(['Dell_authored_excerpt_v1',r['url'],quantity,quote]);OUT.append(row)
    LEDGER.append(dict(document_url=r['url'],accession=accession,scope='personally_read_targeted_section',quantity=quantity,quote_sha256=digest(quote)))

excerpt('0001571996-26-000046','dfs_cashflow_classification',
        'For offerings that qualify as sales-type leases, the initial funding of financing receivables is reflected as an impact to cash flows from operations. For offerings that qualify as operating leases, the initial funding is classified as a capital expenditure and reflected as cash flows used in investing activities.',
        finding='Both funding routes already affect CFO minus capex; do not subtract gross DFS originations a second time.',period_end='2026-07-31')
excerpt('0001571996-26-000046','dfs_allocated_debt_management_basis',
        'We approximate the amount of our core debt used to fund the DFS business by applying a 7:1 debt-to-equity ratio to the sum of our financing receivables balance and equipment under operating leases, net, also referred to as DFS owned assets.',
        finding='Management allocation of corporate debt does not become separate nonrecourse securitization debt.',period_end='2026-07-31')
excerpt('0001571996-26-000046','AI_credit_risk_channel',
        'To date, the majority of revenue from our AI‑optimized servers offerings has involved purchases by a relatively small number of large customers and cloud service providers. Such purchases generally involve larger amounts of credit, and could impact our overall credit risk in trade and financing receivables.',
        finding='Direct narrative AI-to-credit link exists, but customers and amounts of credit are not identified.',period_end='2026-07-31')
excerpt('0001571996-26-000046','purchase_commitment_excluded_unknown_prices',
        'The portions of strategic supplier agreements for which certain commodities will be purchased at a price to be mutually agreed upon after the balance sheet date cannot be reasonably estimated and therefore are excluded from purchase obligations.',
        finding='Published purchase commitments omit some future-priced strategic component purchases; no estimate added.',period_end='2026-07-31')
excerpt('0001571996-26-000046','adjusted_FCF_scope',
        'To measure adjusted free cash flow, we exclude the impact of financing receivables and equipment under operating leases from free cash flow, as the initial funding of these DFS offerings at the time of origination is largely subsequently replaced with cash inflows from our DFS related debt.',
        finding='Issuer adjustment removes customer asset funding, with replacement through debt; no equivalence to unadjusted available cash.',period_end='2026-07-31')
excerpt('0001571996-26-000046','quarter_disclosure_controls',
        'Based on that evaluation, our Chief Executive Officer and Chief Financial Officer have concluded that as of July 31, 2026, the Company’s disclosure controls and procedures were effective to accomplish their objectives at the reasonable assurance level.',
        finding='Disclosure controls conclusion only; not an annual ICFR audit or zero material-weakness event by inference.',period_end='2026-07-31')
excerpt('0001571996-26-000008','annual_management_ICFR_effective',
        'As a result of that evaluation, management has concluded that our internal control over financial reporting was effective as of January 30, 2026.',
        finding='Explicit dated management ICFR state.',period_end='2026-01-30',event_date='2026-01-30',event_observable='F5',event_present=False)
excerpt('0001571996-26-000008','annual_auditor_ICFR_effective',
        "Also in our opinion, the Company maintained, in all material respects, effective internal control over financial reporting as of January 30, 2026, based on criteria established in Internal Control - Integrated Framework (2013) issued by the COSO.",
        finding='PwC explicit ICFR opinion; CAM on revenue is not adverse audit opinion.',period_end='2026-01-30',event_date='2026-01-30',event_observable='F5',event_present=False,assurance_level='audited',tier='A',location='auditor_report')
contract=REG['0001193125-26-265877'];ex=next(n for n,r in contract['resources'].items() if r.get('exhibit_type')=='EX-10.1')
excerpt('0001193125-26-265877','revolver_interest_coverage_minimum',
        'Permit the Consolidated Interest Coverage Ratio as of the last day of any fiscal quarter (commencing with the first fiscal quarter of the Company ending after the Closing Date) of the Company to be less than 3.00 to 1.00.',
        name=ex,finding='Negative covenant sets minimum 3.00x using contractual EBITDA/interest definitions, not unadjusted GAAP ratio.',period_end='2026-06-10',stage='signed',assurance_level='not_applicable',tier='D',location='contract_section_7.03')
excerpt('0001193125-26-265877','revolver_covenant_denominator_exclusion',
        ('(iv) commissions, discounts,','(including in respect of any DFS-related financing),'),
        name=ex,finding='Contractual interest denominator excludes DFS-related financing fees/interest; no proxy for headroom calculated.',period_end='2026-06-10',assurance_level='not_applicable',tier='D',location='contract_definitions')
excerpt('0001193125-26-226734','MSD_personal_affiliates_commercial_scope',
        'Entities affiliated with DFO Management LLC, the investment firm that exclusively manages the capital of Mr. Dell and his family, including portfolio companies of MSD Capital, L.P. or its affiliates, portfolio companies of DFO Management, LLC or its affiliates, the Michael & Susan Dell Foundation and other entities affiliated with Mr. Dell, purchase products or services from Dell Technologies on standard commercial terms available to comparable unrelated customers.',
        finding='Personal investment organizations and several portfolio companies; no attribution to MSD Investment Corp. or Dell consolidated finance by surname.',period_end='2026-01-30')
excerpt('0001193125-26-226734','Silver_Lake_portfolio_reciprocal_commercial_scope',
        'Entities affiliated with Silver Lake, including portfolio companies of the SLP stockholders or their affiliates, purchase products or services from Dell Technologies on standard commercial terms available to comparable unrelated customers.',
        finding='Portfolio-company aggregate is not a single consolidated borrower/customer; reciprocal purchases disclosed without company-by-company allocation.',period_end='2026-01-30')

for quantity,amount,label in [('dfs_allocated_corporate_debt',11042000000,'DFS allocated debt'),('dfs_related_debt_management',20660000000,'Total DFS related debt'),('core_debt_management',13983000000,'Total core debt')]:
    excerpt('0001571996-26-000046',quantity,
        ('The following table presents our outstanding debt as of the dates indicated:', 'During the first six months of Fiscal 2027, the outstanding principal amount'),
        finding='Management principal allocation within the same USD34.747bn total debt; not an additional liability or blanket nonrecourse amount.',
        amount=str(amount),amount_origin='narrative_only',unit='USD',currency='USD',period_end='2026-07-31',stage='recognized',table_row=label)
excerpt('0001571996-26-000046','undrawn_committed_revolver_actual_availability',
        ('The following table presents our cash and cash equivalents as well as our available borrowings as of the dates indicated:', 'During the first six months of Fiscal 2027, cash and cash equivalents was flat'),
        finding='Remaining borrowing availability USD5.884bn after letters of credit, less than the USD6bn signed ceiling; commercial paper capacity not added.',
        amount='5884000000',amount_origin='narrative_only',unit='USD',currency='USD',period_end='2026-07-31',stage='available',table_row='Remaining available borrowings under the revolving credit facility')
excerpt('0001571996-26-000046','purchase_obligations_total_reported',
        'As of July 31, 2026, we had purchase obligations of $34.8 billion, of which $24.6 billion is payable within twelve months.',
        finding='Issuer provides total and rolling 12-month outflow; annual-bucket schedule is not interpolated.',
        amount='34800000000',amount_origin='narrative_only',unit='USD',currency='USD',period_end='2026-07-31',stage='signed')
excerpt('0001571996-26-000046','purchase_obligations_rolling_12m_reported',
        'As of July 31, 2026, we had purchase obligations of $34.8 billion, of which $24.6 billion is payable within twelve months.',
        finding='Published rolling-12-month amount, distinct from remainder-of-fiscal-year USD22.4bn.',
        amount='24600000000',amount_origin='narrative_only',unit='USD',currency='USD',period_end='2026-07-31',stage='signed')
for quantity,amount,label in [('adjusted_FCF_reported',8149000000,'Adjusted free cash flow'),('DFS_financing_receivables_FCF_addback',6667000000,'Financing receivables (b)'),('DFS_lessor_equipment_FCF_addback',496000000,'Equipment under operating leases (c)')]:
    excerpt('0001571996-26-000046',quantity,
        ('The following table presents a reconciliation of free cash flow and adjusted free cash flow to cash flow from operations for the periods indicated:', '(a)Capital expenditures and capitalized software development costs, net includes proceeds from sales of facilities, land, and other assets.'),
        finding='Filed unaudited issuer adjustment; does not replace CFO minus capex or quantify named customer cash financing.',
        amount=str(amount),amount_origin='narrative_only',unit='USD',currency='USD',period_start='2026-05-02',period_end='2026-07-31',stage='recognized',table_row=label)
for maturity,amount,coupon in [('2029-09-15',1250000000,'0.051'),('2031-09-15',1250000000,'0.054'),('2033-09-15',1500000000,'0.056'),('2037-04-01',1000000000,'0.059')]:
    excerpt('0001193125-26-391976','September2026_notes_nominal_'+maturity,
        ('On September 15, 2026, two wholly-owned subsidiaries of Dell Technologies Inc.', 'The Notes were sold pursuant to a shelf registration statement on Form S-3ASR (File No. 333-296691).'),
        finding='Completed issuance, nominal principal not net cash proceeds; no retroactive July balance change and no underwriter-to-lender inference.',
        amount=str(amount),amount_origin='narrative_only',unit='USD',currency='USD',event_date='2026-09-15',period_end='2026-09-15',stage='recognized',instrument_key='DELL_September2026_'+maturity)

# Personally read Schedule 2.01. These are contractual commitments, not loans
# drawn. Names and amounts are explicit author inputs; code only binds rows.
LENDERS=[(name,345000000) for name in ['JPMorgan Chase Bank, N.A.','Bank of America, N.A.','Barclays Bank PLC','Citibank, N.A.','Goldman Sachs Bank USA','HSBC Bank USA, National Association','Wells Fargo Bank, N.A.']]
LENDERS += [(name,255000000) for name in ['UBS AG, Stamford Branch','Morgan Stanley Bank, N.A.','Royal Bank of Canada','Deutsche Bank AG New York Branch','Mizuho Bank, Ltd.','BNP Paribas','MUFG Bank, Ltd.','The Bank of Nova Scotia','Société Generale','PNC Bank, National Association','The Toronto-Dominion Bank, New York Branch']]
LENDERS += [(name,130000000) for name in ['Truist Bank','Sumitomo Mitsui Banking Corporation','Standard Chartered Bank','Banco Santander, S.A., New York Branch','ING Bank N.V. - Dublin Branch','The Bank of New York Mellon']]
assert sum(amount for name,amount in LENDERS)==6000000000
contract_text=normalize_html((ROOT/contract['resources'][ex]['path']).read_bytes())
register=[]
for lender,amount in LENDERS:
    quote=next(line for line in contract_text.splitlines() if line.startswith(lender+' |') and f'{amount:,.2f}' in line)
    quantity='revolver_lender_commitment|'+lender
    excerpt('0001193125-26-265877',quantity,quote,name=ex,
        finding='Named committed lender in Schedule2.01; draw and actual creditor exposure are not inferred from commitment.',
        amount=str(amount),amount_origin='narrative_only',unit='USD',currency='USD',period_end='2026-06-10',event_date='2026-06-10',stage='signed',
        counterparty=lender,counterparty_evidence='named',counterparty_method='contract_parties',assurance_level='not_applicable',tier='D',location='contract_Schedule2.01')
    register.append(dict(lender=lender,committed_amount=amount,currency='USD',stage='signed',facility_maturity='2031-06-10',
        joint_borrowers='Dell International L.L.C.;EMC Corporation',actual_draw_not_inferred=True,source_accession='0001193125-26-265877',observation_id=OUT[-1]['observation_id']))
persist(BASE/'credit_facility_register.json',register)

# Every selected current natural note was personally read, using a fully read
# latest note plus exact changes for preceding current filings. No historical
# notes are falsely marked completed by a hash scan.
for r in Q:
    current=r['report_date'] in ('2026-01-30','2026-05-01','2026-07-31')
    LEDGER.append(dict(note_key=r['key'],accession=r['accession'],report_date=r['report_date'],label=r['label'],
        chars=r['chars'],status='completed' if current else 'historical_inventory_outside_current_text_tranche',
        reading_method='personally_read_full_latest_and_exact_reverse_chronological_changes' if current else None))
    if current and not any(o['content_key']==r['content_key'] and o['accession']==r['accession'] for o in OUT):
        # Explicit analyst disposition of the already personally read current
        # blocks. This is an abstention, not automated narrative extraction.
        b=json.loads((ROOT/r['path']).read_text());quote=b['text'].splitlines()[0]
        row=dict(observation_id=digest(['Dell_current_note_abstention_v1',r['key']]),content_key=b['content_key'],
            document_id=b['document_id'],accession=r['accession'],group_id='DELL',entity_id='cik:0001571996',
            abstained=True,abstention_reason='personally_read_current_note;no_additional_admissible_named_financing_edge;numeric_tagged_data_retained',
            quote=quote,locator=f"rawbytes:{b['raw_byte_start']}:{b['raw_byte_end']};whole_current_note_review",
            raw_byte_start=b['raw_byte_start'],raw_byte_end=b['raw_byte_end'],knowledge_date=b['knowledge_date'],
            period_end=r['report_date'],filing_status='filed',assurance_level='audited' if b['form'].startswith('10-K') else 'reviewed',
            tier='A' if b['form'].startswith('10-K') else 'B',location='financial_statements_and_notes',
            source_perspective='reporting_entity',accounting_framework='us_gaap',as_of=json.loads((BASE/'issuer.json').read_text())['source_cutoff'])
        validate_semantics(row,b,(ROOT/b['source_path']).read_bytes());OUT.append(row)
persist(BASE/'authored_observations.json',OUT);persist(BASE/'reading_ledger.json',LEDGER)
persist(BASE/'table_amount_proofs.json',AMOUNT_PROOFS)
print(json.dumps(dict(observations=len(OUT),current_notes_read=sum(x.get('status')=='completed' for x in LEDGER))))
