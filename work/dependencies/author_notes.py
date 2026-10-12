"""Quotations, quantities and clause interpretations selected by the sole analyst.

The called program verifies literal quotations and selected native IDs; it does
not select or author observations. Source coverage remains transaction-bounded.
"""
from pathlib import Path
from secfragility.operation_dependencies import author_record
from secfragility.operation_sources import save

ROOT=Path('.').resolve(); OUT=[]; FACTS={}; PROOFS={}; CASES={}

def note(case,source,quantity,quote,finding,**kwargs):
    row,fact,proof=author_record(ROOT,source,quantity,quote,finding,**kwargs)
    OUT.append(row);CASES.setdefault(case,[]).append(row['observation_id'])
    if fact:FACTS[fact['fact_id']]=fact
    if proof:PROOFS[row['observation_id']]=proof
    return row['observation_id']

SB='sbenergy-sx1a2.htm'; GUAR='sbenergy-ex1031xformofport.htm'
note('SB_PORTS',SB,'sb_energy_cash_forward_received_and_contributed',
     ('On August 17, 2026, Energy Global, LP entered into a prepaid forward contract with NVIDIA Corporation',
      'immediately contributed to the Company.'),
     'Nvidia paid Energy Global on August 17; Energy Global immediately contributed the same cash to the reporting company. One USD1.5bn economic funding with two legal hops, not USD3bn cash and not a June30 balance.',
     amount='1500000000',stage='drawn_or_paid',period_end='2026-08-17',event_date='2026-08-17',event_type='funding',
     counterparty='Energy Global, LP',counterparty_evidence='named',payer='NVIDIA Corporation',receiver='Energy Global, LP',
     instrument_key='SB_PORTS_PREPAID_FORWARD',measurement_basis='cash_paid_and_passed_through_once')
note('SB_PORTS',SB,'sb_energy_issuance_or_cash_settlement_obligation',
     ('On August 17, 2026, in connection with the prepaid forward contract, SB Energy entered into an issuance',
      'settlement obligations under the prepaid forward contract.'),
     'Issuer unconditionally undertakes to deliver shares or make applicable cash payments to satisfy the parent’s prepaid-forward obligation. Settlement terms and liquidity events remain separate from the paid cash.',
     period_end='2026-08-17',event_date='2026-08-17',counterparty='Energy Global, LP',counterparty_evidence='named',stage='signed')
note('SB_PORTS',SB,'sb_energy_additional_nvidia_subscription_conditional',
     ('On August 17, 2026, the Company entered into a share purchase agreement with NVIDIA Corporation',
      'The shares will be restricted securities with customary registration rights.'),
     'Separate USD1.5bn primary share subscription, conditioned on the IPO closing. It is not a second paid receipt at the frozen cutoff.',
     amount='1500000000',stage='signed',period_end='2026-08-17',event_date='2026-08-17',event_type='commitment',
     counterparty='NVIDIA Corporation',counterparty_evidence='named',measurement_basis='conditional_primary_subscription_not_paid',
     family='financing',link_type='equity_primary',payer='NVIDIA Corporation',receiver='SB Energy, Inc.')
note('SB_PORTS',SB,'sb_energy_transaction_accounting_pending',
     'The Company is currently in the process of evaluating the accounting for the above transactions and the\nrelated impacts on its financial statements.',
     'Cash receipt is explicitly published; final accounting classification of the prepaid-forward and share arrangements was still being evaluated. Do not manufacture a recognized equity/debt balance.')
note('SB_PORTS',SB,'ports_signed_leases_and_delivery_conditions',
     ('NVIDIA has provided residual value guaranties of the OpenAI tenant’s lease obligations at PORTS-Pike',
      'such compensation is provided separately by OpenAI under a separate agreement.'),
     'Guarantee covers the first approximately4.25GW, with an optional further3.78GW. It is triggered by specified insolvency/uncured monetary default; the minimum value declines, with assumption, re-letting and sale options. No current call or all-phase effectiveness is established.',
     amount='105000000000',amount_qualifier='up_to',stage='signed',period_end='2026-08-17',event_date='2026-08-17',
     measurement_basis='aggregate_declining_conditional_remedy_cap',instrument_key='SB_PORTS_NVIDIA_RVG',
     family='credit_support',link_type='residual_value_guarantee',trigger_occurred='unknown')
note('SB_PORTS',GUAR,'ports_guaranty_named_guarantor_redacted_parties',
     ('entered into by NVIDIA Corporation, a Delaware corporation',
      'by and between [***], a [***], and Guarantor.'),
     'Filed form names Nvidia but leaves landlord, tenant, tenant parent and letter-agreement counterparty blank/redacted. Do not assign the USD105bn to a guessed individual lessee or landlord.',
     stage='signed',counterparty='NVIDIA Corporation',counterparty_evidence='named')
note('SB_PORTS',GUAR,'ports_guarantee_cost_scope_and_aggregate_cap',
     ('The parties acknowledge and agree that the total cap on liability for this Guaranty',
      'any additional Related Guaranties entered into after the Effective Date.'),
     'USD105bn is one aggregate cap for related guaranties and encompasses data-center, power and transmission costs. It is not an insurance valuation of GPUs, a funded debt amount or a separate cap for every building.',
     amount='105000000000',amount_qualifier='up_to',period_end='2026-08-17',stage='signed',
     measurement_basis='same_aggregate_cap_as_S1_not_additive',instrument_key='SB_PORTS_NVIDIA_RVG')
note('SB_PORTS',GUAR,'ports_guarantee_commencement_and_RFS',
     ('(a)Subject to the terms and conditions set forth herein, this Guaranty shall be effective as of the Commencement Date',
      'this Guaranty shall be terminated upon such mutual determination.'),
     'Form section2(a): effectiveness is tied to lease commencement and loss payment to ready-for-service conditions. Additional conditions and dispute parameters are redacted. Construction protection cannot be assumed from the headline cap.',stage='signed')
note('SB_PORTS',GUAR,'ports_reserves_before_guarantor_payment',
     ('(c)Except during a Deferral Period pursuant to Section 12(a)(vi)',
      'Landlord shall use commercially reasonable efforts to mitigate any Project Agreement Costs.'),
     'Security deposits and debt-service-reserve funds are applied first for specified costs; timing and cap adjustments contain redactions. Their balances and sufficiency are not publicly established by this form.',stage='signed')
note('SB_PORTS',GUAR,'ports_insurance_and_parent_recourse',
     ('8.Limitation of Liability.',
      'turned over to Guarantor promptly after the collection thereof.'),
     'Section8 requires concurrent good-faith insurance collection and commercially reasonable tenant-parent remedies, subject to provisos. Recovery reduces the cap dollar-for-dollar; recovery from the same distressed tenant group is not an independent protection.',stage='signed')
note('SB_PORTS',GUAR,'ports_trigger_notice_and_cure',
     ('12.Guarantor Remedies; Right to Cure Lease.',
      'a “Guarantor Trigger Event”'),
     'Insolvency or uncured monetary default, notice/cure and landlord termination intent matter. Nvidia has a cure right rather than a general obligation to cure every breach.',stage='signed')
note('SB_PORTS',GUAR,'ports_loss_formula_and_discount_redacted',
     ('(b)“Covered Loss Amount” means, in respect of the Premises',
      '(c)“Discount Rate” shall mean [***]%.'),
     'The covered-loss formula and discount rate are redacted. No expected loss, quarterly liquidity call or recovery value is calculated.',stage='signed')
note('SB_PORTS',SB,'ports_power_external_to_reporting_group',
     ('The U.S.–Japan Partnership has been publicly announced with funding associated with the development',
      'The facilities are being developed by an affiliate of SoftBank that is not our\nsubsidiary, and we do not expect to own or operate them.'),
     'Associated gas generation is developed outside the SB Energy reporting company. Public/government funding announcements and operational dependencies are not a completed financing or a sovereign guarantee.',stage='signed')
note('SB_PORTS',SB,'ports_power_funding_political_conditions',
     ('The gas-fired power generation supporting the PORTS-Pike Technology Campus depends in part',
      'amounts, or at all.'),
     'Generation funding remains conditional on governmental/institutional processes. Treat unavailable power as a delivery dependency, without inventing construction-payment dates or public guarantees.',stage='signed')
note('SB_PORTS','exhibit1027-prepaidforward.htm','sb_prepaid_forward_legal_party_and_payment',
     ('THIS CERTIFIES THAT in exchange for the prepayment by NVIDIA Corporation',
      'subject to the terms described below.'),
     'Executed prepaid-forward contract names Energy Global, LP as receiving issuer of the instrument and obliges delivery/cause delivery of IPO Entity securities. Contract alone proves terms; the later S1 separately proves August17 payment.',
     amount='1500000000',counterparty='Energy Global, LP',counterparty_evidence='named',period_end='2026-08-17',stage='signed',measurement_basis='contract_principal_same_funding_not_additive')
note('SB_PORTS','exhibit1027-prepaidforward.htm','sb_prepaid_liquidation_priority',
     ('(e) Liquidation Priority.', '(f) Payment of Investment Amount.'),
     'Prepaid-forward cash-out is junior to outstanding indebtedness/creditor claims and also junior to the specified existing Ares securities; equity settlement and cash-out rank differently. Recoverability is not the purchase amount.',stage='signed')
note('SB_PORTS','exhibit1028-sharepurchasea.htm','sb_subscription_closing_condition',
     ('1. Purchase and Sale of Shares.', '2. Representations, Warranties and Covenants of the Company.'),
     'Executed share agreement separately conditions the subscription payment on IPO closing and delivery. It is not evidence that the second USD1.5bn was paid.',stage='signed')
note('SB_PORTS',SB,'sb_openai_warrants_issued_total',
     ('“OpenAI Warrants” means the 3,991,809 warrants issued by us to OpenAI',
      'See\n“Certain Relationships and Related Party Transactions—Transactions with OpenAI—Warrants.”'),
     'Total issued warrants differ from vested, IPO-vesting and unvested quantities; cashless exercise is possible. Shares are not dollars and the count is not a cash investment.',
     amount='3991809',unit='shares',currency=None,stage='signed',period_end='2026-09-21',measurement_basis='issued_warrants_including_unvested')

note('SB_PORTS',SB,'sb_ares_preferred_original_investment_and_preference',
     ('Across 2022, 2024, and 2025, SBE Global issued $800 million of preferred equity interests',
      'equal to the then-expected fair market value.'),
     'USD800m of original preferred equity differs from approximatelyUSD996m liquidation preference and related warrants. This is SBE Global’s security, not another USD800m cash balance of SB Energy.',
     amount='800000000',period_end='2025-12-31',stage='recognized',measurement_basis='historical_preferred_issue_amount_not_current_fair_value')
note('SB_PORTS',SB,'sb_ares_cash_out_before_ipo',
     ('Ares Redemption Mechanics\nWe currently expect',
      'or warrant position in SBE Global or any of its subsidiaries.'),
     'Expected redemption before or around IPO consumes intercompany-note repayment, Energy Global cash and/or new credit. Not a completed redemption or a new project inflow; the roughlyUSD40m warrant cash-out is funded above SB Energy, with exact final timing/amount unknown.',stage='signed')
note('SB_PORTS',SB,'sb_new_credit_future_commitment_split',
     ('The Credit Facility is expected to provide for (i) a senior secured revolving credit facility',
      'of credit facility up to its commitments.'),
     'ExpectedUSD3bn total includes a USD1.875bn cash/LC revolver and a USD1.125bn LC-only facility. Do not treat allUSD3bn as available cash or count revolver LCs twice. The facility is expected, not executed/drawn.',
     amount='3000000000',stage='intent_non_binding',period_end='2026-09-21',measurement_basis='expected_cash_and_LC_total_not_available_cash')
note('SB_PORTS',SB,'sb_credit_project_assets_not_blanket_recourse',
     ('Guarantees and Security. The Credit Facility is expected',
      'limited portion of our consolidated assets.'),
     'Expected corporate collateral and guarantors exclude specified project/tax-equity vehicles and assets. The proposed corporate lender does not have a blanket claim over consolidated project assets.',stage='intent_non_binding')
note('SB_PORTS',SB,'sb_future_liquidity_covenant_definition',
     ('In addition, the Credit Facility is expected to require us to maintain minimum liquidity',
      'within a specified period.'),
     'Prospective minimum liquidityUSD600m, stepping toUSD400m after a definedUSD1bn contract cash-flow test. Liquidity includes undrawn revolving commitments; this is neither present cash nor calculated covenant headroom.',stage='intent_non_binding')
note('SB_PORTS',SB,'sb_openai_warrants_lease_incentive_non_cash',
     ('The corresponding initial cost of $3,646,246 thousand was accounted for as a lease incentive provided to',
      'Company\'s lessor arrangements.'),
     'June30 historical warrant-related lease incentiveUSD3.646246bn is noncash and reduces future revenue from lease commencement. It is not a cash outflow, current recognized revenue or a second cash investment; later August warrant amendments are separate.',
     amount='3646246000',period_end='2026-06-30',stage='recognized',measurement_basis='noncash_customer_lease_incentive_before_August_amendment')

NS='ck0002110365-20260918.htm'; DFS='ck0002110365-ex10_20.htm'; WC='ck0002110365-ex10_23.htm'; AN='ck0002110365-ex10_25.htm'
note('NSCALE',NS,'nscale_microsoft_aggregate_contract_upper_value',
     ('Between September 2025 and April 2026, we entered into statements of work with Microsoft',
      'delivery and availability of service requirements.'),
     'Up toUSD43.8bn throughDecember2033, excluding options and subject to delivery/availability. Aggregate multiple contracts, not recognized revenue, cash, or the amount of a single Norway/US template.',
     amount='43800000000',amount_qualifier='up_to',counterparty='Microsoft',counterparty_evidence='named',stage='signed',period_end='2026-09-18',measurement_basis='multi_contract_future_upper_value_excluding_options')
note('NSCALE',NS,'nscale_anthropic_aggregate_contract_upper_value',
     ('In addition, on August 25, 2026, we entered into the Anthropic Services Agreements',
      'each between Anthropic and a wholly owned subsidiary of Nscale Limited.'),
     'Up toUSD44.6bn across four separately financed subsidiaries. Not current RPO cash, a funded loan, or an amount allocated to the one filed template.',
     amount='44600000000',amount_qualifier='up_to',counterparty='Anthropic',counterparty_evidence='named',stage='signed',period_end='2026-08-25',event_date='2026-08-25',measurement_basis='four_contract_conditional_upper_value')
note('NSCALE',NS,'nscale_anthropic_binding_finance_not_obtained',
     ('The Anthropic Services Agreements require us to use best efforts to obtain qualifying financing',
      'There can be no assurance that we will obtain any of the required financings on acceptable terms or at all.'),
     'At the prospectus date no binding financing commitments had been obtained for this Anthropic performance obligation. Other facilities for other sites cannot be assumed to fill this gap.',stage='signed')
note('NSCALE',NS,'nscale_nvidia_subscription_future_close',
     ('On September 15, 2026, we entered into a Subscription Agreement for subscriptions',
      'The NVIDIA Sale will close on or around November 16, 2026.'),
     'Signed minimumUSD3.1bn includes a separateUSD1bn Nvidia transaction with future November closing; it is not an already received USD1bn investment or an additional amount on top of theUSD3.1bn.',
     amount='1000000000',counterparty='NVIDIA',counterparty_evidence='named',period_end='2026-09-15',event_date='2026-09-15',stage='signed',measurement_basis='signed_future_nvidia_subscription_component')
note('NSCALE',NS,'nscale_dfs_executed_schedule_rent',
     ('In April 2026, we entered into two Global Framework Agreements',
      'including combined financing charges of approximately $34.8 million.'),
     'Forty executed payment schedules atSeptember4 imply approximatelyUSD2.54bn gross initial-term rent, including financing charges. This is not drawn cash, principal outstanding, fair value or a Ward County-only amount.',
     amount='2540000000',amount_qualifier='approximately',counterparty='Dell Financial Services L.L.C.',counterparty_evidence='named',stage='signed',period_end='2026-09-04',measurement_basis='gross_initial_term_equipment_lease_rent_including_finance_charges')
note('NSCALE',DFS,'nscale_dfs_schedules_non_cancellable',
     ('1.\nENTITIES.', '3.\nPAYMENTS, TAXES AND PAYMENT OBLIGATION.'),
     'Each executed schedule is a separate non-cancellable agreement. Product acceptance, delivery responsibilities and deemed acceptance precede schedules; the public framework alone does not establish payments or allocations to vendors.',stage='signed')
note('NSCALE',DFS,'nscale_dfs_payments_absolute',
     ('Your obligation to pay all amounts when due', 'or the bankruptcy of any person.'),
     'Payments remain absolute/unconditional under the framework despite supplier claims, loss of use or bankruptcy. The actual schedule can override framework provisions.',stage='signed')
note('NSCALE',DFS,'nscale_dfs_security_assignment_and_schedule_control',
     ('9.\nASSIGNMENT.', 'Page 3 of 3'),
     'Funder assignment, product/proceeds security interest and schedule priority are published. Appendix entities and the actual schedules are omitted; they are necessary for exact legal exposure and proceeds reconciliation.',stage='signed')
note('NSCALE',NS,'nscale_ward_county_signed_gpu_facility',
     ('In August 2026, Nscale Ward County Borrower SPV, LLC entered into a $1.85 billion',
      'The Ward County GPU Facility matures in February 2033.'),
     'Ward CountyUSD1.85bn delayed-draw commitment hasUSD630m fixed andUSD1.22bn floating tranches. Signed capacity is not a disclosed drawn balance; it finances this site, not all Anthropic commitments.',
     amount='1850000000',counterparty='Nscale Ward County Borrower SPV, LLC',counterparty_evidence='named',period_end='2026-08-27',event_date='2026-08-27',stage='signed',measurement_basis='delayed_draw_commitment_not_actual_draw')
note('NSCALE',NS,'nscale_north_carolina_signed_gpu_facility',
     ('In August 2026, Nscale NC Borrower SPV, LLC entered into a $1.2 billion',
      'The North Carolina GPU Facility matures in December 2031.'),
     'SeparateNorthCarolinaUSD1.2bn delayed-draw commitment withUSD370m fixed/830m floating tranches. Do not assign all bank risk to its joint arrangers or treat all commitments as funded.',
     amount='1200000000',counterparty='Nscale NC Borrower SPV, LLC',counterparty_evidence='named',period_end='2026-08-27',event_date='2026-08-27',stage='signed',measurement_basis='separate_site_delayed_draw_commitment_not_actual_draw')
note('NSCALE',WC,'nscale_ward_legal_roles',
     ('CREDIT AGREEMENT\ndated as of August 27, 2026', 'as Mandated Lead Arrangers'),
     'Borrower, affiliate guarantor, administrative/collateral agent and joint arrangers are different legal roles. Lender allocations are not inferred from the title page.',stage='signed')
note('NSCALE',WC,'nscale_ward_cash_trap_threshold',
     ('“Cash Trap Event” shall mean the Historical DSCR', 'from the relevant Cash Trap Determination Date.'),
     'Cash trap starts belowHistoricalDSCR1.10 and six consecutive months triggers cash-trap prepayment. The threshold differs from the1.05 default covenant; no current compliance ratio/headroom is calculated.',stage='signed')
note('NSCALE',WC,'nscale_ward_financial_covenant',
     'Section 6.12. Financial Covenant. The Borrower will not permit the Historical DSCR to be less than 1.05:1.00, as of any Payment Date (the “Financial Covenant”), subject to the right of the Borrower to exercise the Cure Right.',
     'Published1.05contractDSCR covenant, subject to cure. It is not a GAAP interest-coverage ratio, a reported current ratio or evidence of a breach.',stage='signed')
note('NSCALE',WC,'nscale_ward_cure_draw_standstill',
     ('Section 7.03. Right to Equity Cure.', 'Section 7.04. Application of Funds.'),
     'Cure equity can cure specified cash shortfalls/covenant events, while credit extensions remain suspended during a continuing shortfall/breach. Cure frequency and cash-trap treatment matter; no actual cure is asserted.',stage='signed')
note('NSCALE',WC,'nscale_ward_nonacceptance_recovery_waterfall',
     ('“RVG Triggering Event” shall mean,', 'the sixty (60) day anniversary of the Tranche Termination Date.'),
     'Following customer nonacceptance/termination, options include sale, reallocation or approved redeployment. Sale proceeds pay tranche debt/hedges first, then related customer prepayments. Parent has an offer right, not an unconditional obligation to buy every asset at cost; deadlines are10/5/30businessdays within a60day period.',stage='signed')
note('NSCALE',AN,'nscale_anthropic_legal_provider',
     ('This Order for GPU Services (“Order”) is governed', 'Contact: | | Alice Takhtajan'),
     'Body namesAnthropicPBC andNscale GPU MCC B1.1 LLC. The exhibit index usesMMC; retain the body’s legal name and report the index/body discrepancy rather than merging different names without proof.',stage='signed')
note('NSCALE',AN,'nscale_anthropic_no_fees_before_acceptance',
     ('To avoid doubt, no fees will be payable for a Tranche', 'other adjustments and amounts required to be credited to Anthropic under the Agreement).'),
     'Payment begins only after written acceptance, and credits/late-delivery adjustments reduce billings. A headline contract value does not remove pre-acceptance funding risk.',stage='signed')
note('NSCALE',AN,'nscale_anthropic_financing_longstop_and_termination',
     ('9.\nFinancing', 'except for obligations that expressly survive termination.'),
     'Financing must cover GPUs and data-center/credit support. Both parties can terminate if qualifying financing is not obtained by a redacted longstop, without further obligations except survivors. Capacity cannot be allocated elsewhere while financing is sought.',stage='signed')
note('NSCALE',AN,'nscale_anthropic_direct_agreements_require_consent',
     ('At Provider’s request, Anthropic will negotiate in good faith',
      'mutually agreed by Anthropic, Provider and the applicable Provider Financing Party.'),
     'Future lender direct agreements may include notice, cure, standstill, step-in and payment direction only as mutually agreed. Their actual execution is not established by this promise to negotiate.',stage='signed')
note('NSCALE',AN,'nscale_anthropic_four_tranche_coordination',
     ('Provider agrees and acknowledges that, at Provider’s request to facilitate',
      'Provider must remain an Affiliate Controlled by Parent throughout the Tranche Term.'),
     'Four separately financed provider contracts must operate the entire site together, with aligned lender/step-in rights. Legal diversification acrossSPVs does not remove common operational/customer dependence.',stage='signed')
note('NSCALE',NS,'nscale_equipment_purchase_commitments',
     'As of June 30, 2026, we had commitments to purchase technology equipment which had not yet been delivered of $24.0 billion across our sites.',
     'June30group-wide undelivered equipment commitments. No allocation to the laterAnthropic contracts or subtraction from unrelated financing capacities is made.',amount='24000000000',period_end='2026-06-30',stage='signed',measurement_basis='group_wide_undelivered_equipment_commitment')
note('NSCALE',NS,'nscale_cash_excluding_restricted_cash',
     ('CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS\n(In millions)',
      'The accompanying notes are an integral part of these condensed consolidated financial statements.'),
     'June30reportedcashUSD1.4784bn, excluding restricted cash. Selected cash row, not a financing receipt or the cash of any particular project.',
     amount='1478400000',stage='recognized',period_start=None,period_end='2026-06-30',measurement_basis='consolidated_cash_excluding_restricted_cash')
note('NSCALE',NS,'nscale_total_cash_including_restricted_cash',
     ('CONDENSED CONSOLIDATED STATEMENTS OF CASH FLOWS\n(In millions)',
      'The accompanying notes are an integral part of these condensed consolidated financial statements.'),
     'June30totalcashincludingrestrictedUSD2.0931bn. This contains the freecash row; the two quantities are not additive. Restricted components areUSD44.4mcurrent andUSD570.3mnoncurrent in the same table.',
     amount='2093100000',stage='recognized',period_start=None,period_end='2026-06-30',measurement_basis='consolidated_cash_including_restricted_cash_not_free_cash')

IO='ioni-20260630.htm'
note('IONIC_WARD',IO,'ionic_named_nscale_tenant_and_actual_rent_start',
     ('In October 2025, we announced our inaugural participation in the HPC/AI sector',
      'increasing to a potential $2.6 billion under the provisions of the amendment.'),
     'The later10Q namesNscaleWardCountyLLC, records first paymentNovember2025 and confirms monthly fixed payments commencedAugust2026. The prospectus’s future start is superseded; contract lifetime revenue is not recognized current cash.',stage='delivered',period_end='2026-08-31')
note('IONIC_WARD',IO,'ionic_nvidia_first_five_year_guarantee_cap',
     ('In connection with the Nscale Agreement, Nscale provided a guarantee from',
      'step-into the Nscale Agreement for the remainder of the term.'),
     'Nvidia rent guarantee up toUSD860.3m for years1–5; Nscale parent covers rents fromyear6. Anchor customer has an optional30day insolvency step-in right. This does not guarantee Nscale GPU loan principal or establish an actual call.',
     amount='860300000',amount_qualifier='up_to',counterparty='NVIDIA Corporation',counterparty_evidence='named',stage='signed',period_end='2026-08-31',measurement_basis='first_five_lease_year_rent_guarantee_not_GPU_debt',trigger_occurred='unknown')
note('IONIC_WARD',IO,'ionic_expansion_power_condition',
     ('In addition to the 234 MW currently leased to Nscale',
      'is subject to regulatory approval;'),
     'Additional89MW lease obligation is conditional on capacity availability and regulatory approval. Broader700MW expansion is an objective, not assured delivered capacity.',stage='signed')
note('IONIC_WARD',IO,'ionic_no_debt_and_capex_cash_strategy',
     ('We incurred no debt during the six months ended June 30, 2026',
      'over the next twelve months.'),
     'Issuer statement about debt incurred and financing strategy, not a guarantee of future self-funding or absence of all contractual liabilities. Do not turn the Nvidia guarantee into existing issuer debt.',stage='recognized',period_end='2026-06-30')
note('IONIC_WARD',IO,'ionic_consolidated_cash',None,
     'June30cashUSD415.738m at the reporting company, not a balance of Nscale or cash guaranteed byNvidia.',
     inline='f-31',stage='recognized',measurement_basis='consolidated_cash')
note('IONIC_WARD',IO,'ionic_operating_cash_flow',None,
     'First-halfCFOminusUSD25.935m covers the consolidated business, including cryptocurrency mining; no AI-only attribution.',
     inline='f-316',stage='recognized',measurement_basis='consolidated_operating_cash_flow')
note('IONIC_WARD',IO,'ionic_financing_cash_flow',None,
     'First-halfnetfinancingcashUSD400m is a financing inflow, distinct from operating cash and prospective lifetime lease revenues.',
     inline='f-332',stage='recognized',measurement_basis='net_financing_cash_flow_not_revenue')

HUT='hut-20260630x10q.htm'
note('HUT_RIVER',HUT,'hut_river_bend_funded_gross_proceeds',
     ('Gross proceeds from the issuance were $3.25 billion', 'expenses of the offering.'),
     'ActualApril30gross issue proceedsUSD3.25bn, allocated to construction, reimbursement of prior sponsor equity, reserves and fees. They are not freely available parent cash and are not another exposure on top ofJune30principal.',
     inline='Narr_dJL7JjNKr0GvZYY-Bh_8CQ',stage='drawn_or_paid',event_date='2026-04-30',event_type='funding',measurement_basis='gross_funded_note_proceeds_before_uses')
note('HUT_RIVER',HUT,'hut_river_bend_principal_outstanding',
     ('As of June 30, 2026, the aggregate principal balance of the River Bend Notes',
      'effective interest method.'),
     'June30faceprincipalUSD3.25bn, distinct from approximatelyUSD3.20bn net carrying amount after issuance costs. The native concept sayscarryingamount but the explicit prose identifies principal; column/paragraph role controls.',
     inline='Narr_363KCdWpEUm5W9h7HQuxRA',stage='recognized',measurement_basis='face_principal_outstanding_not_net_book_value')
note('HUT_RIVER',HUT,'hut_river_google_lease_support_not_bond_guarantee',
     ('The data center is leased in its entirety to Fluidstack USA IV Inc.',
      'or the lease guarantor.'),
     'FluidstackUSAIV rents are the principal debt-service source. GoogleLLC supports rent and certain lease obligations; note creditors have project/equity liens. The Notes are solelyHut8DC obligations and are not guaranteed by parent, tenant or lease guarantor.',stage='signed',counterparty='Google LLC',counterparty_evidence='named')
note('HUT_RIVER',HUT,'hut_river_restricted_accounts_and_reserves',
     ('The indenture governing the River Bend Notes contains customary restrictive covenants',
      'Unaudited Condensed Consolidated Balance Sheets.'),
     'Construction and debt-service accounts are restricted. They are not equivalent to general liquidity at the sponsor or transferable cash in a differentSPV.',stage='recognized')
note('HUT_RIVER',HUT,'hut_river_amortization_and_maturity',
     ('Interest on the River Bend Notes is payable semi-annually',
      'continue semi-annually through maturity.'),
     'First couponNovember15,2026; principal startsMay15,2028, with final maturity2042. Preserve real calendar dates without synthesizing an undisclosed monthly construction budget.',stage='signed')
note('HUT_BEACON',HUT,'hut_beacon_point_principal_outstanding',
     ('As of June 30, 2026, the aggregate principal balance of the Beacon Point Notes',
      'effective interest method.'),
     'SeparateJune30faceprincipalUSD4.25bn ofBeaconPointDC, with net carrying value reported separately. Do not transposeRiverBend guarantors, debtor or amortization dates to this vehicle.',
     inline='Narr_7Z1HyauKeUekz58iRrQtgQ',stage='recognized',measurement_basis='separate_vehicle_face_principal_outstanding')
note('HUT_BEACON',HUT,'hut_beacon_payment_calendar',
     ('Interest on the Beacon Point Notes is payable semi-annually',
      'continue semi-annually through maturity.'),
     'First couponNovember30,2026 and principal startsMay30,2030; final maturity2042. Distinct fromRiverBend’s2028principal start.',stage='signed')
note('HUT_BEACON',HUT,'hut_beacon_unnamed_high_grade_tenant_and_nonrecourse',
     ('The data center is leased in its entirety to a high-investment-grade company',
      'any of their respective subsidiaries or affiliates.'),
     'Beacon Point has a tenant described by credit quality but unnamed. Its Notes have project/account/equity liens and no guarantee from parent, tenant or their affiliates. Do not infer Google or Fluidstack from the separate River Bend structure.',stage='signed')
note('HUT_RIVER',HUT,'hut_parent_cash_unrestricted_reported',None,
     'ConsolidatedJune30cashUSD233.579m. This is a reporting-company amount, not a cash balance attributed entirely to either AI project.',
     inline='Tc_-ymN9smOY0OpkF7OHO4tow_6_3',stage='recognized',measurement_basis='consolidated_cash_excluding_restricted_cash')
note('HUT_RIVER',HUT,'hut_cash_restricted_consolidated',None,
     'ConsolidatedrestrictedcashUSD6.787147bn mainly comprises construction/debt-service proceeds forRiverBend/BeaconPoint andLCsupport. No allocation of this whole balance to oneSPV.',
     inline='Tc_9TXLDwaYd0ak85dXfiTzng_7_3',stage='recognized',measurement_basis='consolidated_restricted_cash_not_free_cash')

META='meta-20260630.htm'
note('HYPERION',META,'meta_louisiana_venture_ownership_and_cost_scope',
     ('Our non-marketable equity method investments include an arrangement, entered into in October 2025',
      'approximately $27 billion in total estimated development costs.'),
     'SEC financial note documents20%membership and pro-rata funding of estimatedUSD27bn development costs at theLouisianaVenture. Cost budget is not spentcash, Beignet debt principal or a newly recognized Meta loan.',stage='signed')
note('HYPERION',META,'meta_louisiana_initial_lease_commitment',
     ('Our lease agreements with the Venture, which cover the right to use properties on the data center campus',
      'a total lease period of up to 20 years.'),
     'InitialleasecommitmentUSD12.31bn, with2029commencement, four-year initial terms and renewal options up to20years. Native context identifies the initial commitment atOctober31,2025; publication remainsJuly2026.',
     inline='f-649',stage='signed',measurement_basis='initial_lease_commitment_not_current_cash_or_20_year_firm_rent')
note('HYPERION',META,'meta_louisiana_RVG_threshold',
     ('In addition, we have provided residual value guarantees (RVG)',
      'approximately $28 billion that decreases over time.'),
     'InitialRVGthresholdapproximatelyUSD28bn declines over time. Payment is the shortfall to fairvalue after specified nonrenewal/termination conditions. Zero recognized liability is not zero contingent exposure.',
     inline='f-652',stage='signed',measurement_basis='initial_declining_RVG_threshold_not_expected_loss',trigger_occurred='unknown')
note('HYPERION',META,'meta_louisiana_RVG_formula_and_no_recognized_liability',
     ('any shortfall between the fair value at that time and the RVG threshold for that property.',
      'no liability has been recorded to date.'),
     'Continuation of the preceding RVG paragraph: payment depends on the fair-value shortfall, and no liability is recorded because payments are not probable. This is an accounting recognition statement rather than a loss forecast.',stage='signed')
note('HYPERION',META,'meta_louisiana_nonconsolidation_reason',
     ('Significant judgment is required to identify the activities that most significantly impact the Venture',
      'providing construction management, administrative and property management services to the Venture.'),
     'Meta does not control the most significant remarketing decisions and is not the primary beneficiary; theVIE is not consolidated. Legal and economic guarantees remain despite nonconsolidation.',stage='recognized')
note('HYPERION',META,'meta_louisiana_equity_method_carrying_value',
     ('As of June 30, 2026 and December 31, 2025, the carrying value of our equity investment',
      'the maximum RVG threshold.'),
     'June30equity-methodbookvalueUSD2.92bn, not investmentcash or marketvalue. It is included in the issuer’s maximum exposure measure, not an additional amount to add to that measure.',
     inline='f-653',stage='recognized',measurement_basis='equity_method_carrying_value')
note('HYPERION',META,'meta_louisiana_issuer_maximum_exposure',
     ('As of June 30, 2026 and December 31, 2025, the carrying value of our equity investment',
      'the maximum RVG threshold.'),
     'Issuer’sJune30maximumexposureUSD46.03bn already comprises equity bookvalue, lease commitments, future funding and maximumRVGthreshold. It is not debt outstanding, an expected loss or an amount to add to those components or toBeignet’s debt.',
     inline='f-655',stage='recognized',measurement_basis='issuer_published_composite_maximum_exposure_nonadditive')
note('HYPERION','hyperion_meta','hyperion_project_name_and_ownership_external',
     ('Meta announces joint venture with funds managed by Blue Owl Capital',
      'in total development costs for the buildings and long-lived power, cooling, and connectivity infrastructure at the campus.'),
     'IssuerIR identifies theHyperioncampus, funds-managed80%interest andMeta20%. This source corroborates project identity; it does not identify every fund or establish their individual retained positions. ExternaltierE, no core numeric amount.',stage='signed',accounting_framework='unknown')
note('HYPERION','hyperion_meta','hyperion_RVG_window_and_bond_investors_external',
     ('Meta entered into operating lease agreements with the joint venture',
      'through a private securities offering.'),
     'IssuerIR reports initialfour-yearleases, anRVGcovering thefirst16operatingyears, and debt funding involvingPIMCOand other investors. Preciseamortization/guarantee-expiry alignment and individual allocations require contracts;PIMCOmanager is not the same entity as a named fund.',stage='signed',accounting_framework='unknown')
note('HYPERION','primary_doc.xml','nport_beignet_held_principal',
     ('BEIGNET INVESTOR LLC','BENCHMARK Mortgage Trust'),
     'PIMCO Extended Duration Fund, seriesS000013233, holdsUSD1.517mprincipal ofCUSIP076912AA2 atJune30,2026. XML unitsPA meanprincipalamount; this is notUSD1.517bn, PIMCO’s total allocation, a new origination orBeignet’s total debt.',
     amount='1517000',counterparty='Beignet Investor LLC',counterparty_evidence='named',stage='recognized',period_end='2026-06-30',
     source_perspective='counterparty',measurement_basis='fund_series_held_bond_principal_USD_units_PA')
note('HYPERION','primary_doc.xml','nport_beignet_held_market_value',
     ('BEIGNET INVESTOR LLC','BENCHMARK Mortgage Trust'),
     'SamepositionreportedUSD1,548,323.70marketvalue, Level2. Notanotherloan or a cost basis; noFV/cost ratio is calculated without cost.',
     amount='1548323.7',counterparty='Beignet Investor LLC',counterparty_evidence='named',stage='recognized',period_end='2026-06-30',
     source_perspective='counterparty',measurement_basis='fund_series_reported_market_value_not_additional_principal')
note('HYPERION','primary_doc.xml','nport_beignet_security_terms_and_flags',
     ('BEIGNET INVESTOR LLC','BENCHMARK Mortgage Trust'),
     'CUSIP076912AA2, USDprincipalunits, fixed6.58%coupon, May30,2049maturity; default, arrears andPIKfields areN for thisrecord. These flags are not proof of lowrisk, a verified interestcashreceipt or a corporateguarantee.',stage='recognized',period_end='2026-06-30',source_perspective='counterparty')
note('HYPERION','beignet_sp_search_excerpt','beignet_agency_holding_structure_excerpt',
     ('Blue Owl Capital Inc. (Blue Owl; BBB/Stable)', 'one for each building--with Landlord.'),
     'Explicitly labelled search-index excerpt of the October2025 preliminary rating, not publisher original or contract: Beignet holding finances80%JV, JV ownsLaidleylandlord andMeta subsidiaryPelicanLeap is tenant. Names and proposedUSD27.3bndebtremain exploratoryE evidence.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')
note('HYPERION','beignet_sp_search_excerpt','beignet_agency_risk_transfer_and_weak_asset_security_excerpt',
     ('Typical construction risks, including cost overruns and construction delays', 'Meta will pay the GMV.'),
     'Agency excerpt describes construction-risk transfer toMeta, lack of directJV/landlordassetsecurity for holding creditors andGMVpayment before completedsale. These are credit-analysis assertions requiring the private contracts for legal confirmation.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')

note('LAMBDA_COMPUTE_I','lambda_issuer','lambda_closed_delayed_draw_facility_external',
     ('SAN FRANCISCO, CA, October 1, 2026',
      'across multiple data centers.'),
     'Issuer announcesclosing of a delayed-drawfacility, not funding of everycommitment. Twoinvestmentgradeofftakers remainunnamed. ExternaltierE; no USD1bnamountentersthecorefinancialtables.',stage='signed',accounting_framework='unknown')
note('LAMBDA_COMPUTE_I','lambda_issuer','lambda_financing_milestones_security_and_terms_external',
     ('Facility highlights',
      'contracted cash flows'),
     'Issuer reportsUSD1.008bnfacility,6.78%fixedcoupon, May30,2033finalmaturity, fullyamortizingprofile, GPU/infrastructure andcontractedcashflowsecurity. Reportedcontracttermsare retained separately from admissibleSECcash/encours.',stage='signed',accounting_framework='unknown')
note('LAMBDA_COMPUTE_I','lambda_issuer','lambda_arranger_not_retained_lender_external',
     'J.P. Morgan acted as sole coordinating lead arranger, structuring agent, and bookrunner.',
     'Arranger/structuring/bookrunnerroleisdisclosed; retainedloanallocationandidentityofinsuranceholdersarenot. No allocationoftheentirefacilitytoJPMorgan.',stage='signed',accounting_framework='unknown')
note('LAMBDA_COMPUTE_I','lambda_dbrs','lambda_compute_borrower_identity_and_GPU_sites_external',
     ('DBRS Limited (Morningstar DBRS) assigned an Issuer Rating',
      'Kansas City, and Dallas (the Project).'),
     'Ratingagency identifiesLambdaComputeILLCasborrower andGB300/VR200deployments atthreecities. Ratinganalysisisnotafiledequivalentorareplacementfortheloancontract.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')
note('LAMBDA_COMPUTE_I','lambda_dbrs','lambda_amortization_and_customer_dependence_external',
     ('The credit ratings reflect (1) highly stable cash flows',
      'a maturity date that is approximately six years from the close of financing.'),
     'Agency describes take-or-paycustomerflows, stageddrawconditions andamortizationaftereachGPUtranchestabilizes, with1.20xDSCR. It alsodisclosesinstallation,acceptanceandindirectparentcreditrisks. ThisdoesnotestablishacurrentreportedDSCR.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')
note('LAMBDA_COMPUTE_I','lambda_dbrs','lambda_reserve_weakness_external',
     ('Morningstar DBRS notes that the debt service reserve is weaker',
      'a half notch downward adjustment for this weakness.'),
     'Specificcounterweighttotheinvestmentgraderating:debtservicereserveweakerthanusualandbelowmethodologylevel,withhalfnotchadjustment. Reservebalanceandcashsufficiencyremainunknown.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')
note('LAMBDA_COMPUTE_I','lambda_dbrs','lambda_dell_supply_and_equity_installation_risk_external',
     ('During the installation process, the Project is exposed to risk',
      'artificial intelligence space.'),
     'Agency describesfixedpriceDellMarketingInc supplycontract,drawconditions,equityduringinstallationandlimitedcustomercancellationprovisions. No assignmentofthewholefacilitytoDellFS ordirectproofthatfinancingproceedsboughtSMCIequipment.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')
note('LAMBDA_COMPUTE_I','lambda_dbrs','lambda_lender_stepin_external',
     'Finally, Morningstar DBRS notes that step-in rights allow enforcement by the lenders to ensure continuity of delivery under the offtake agreements, in adverse circumstances.',
     'Agencyassertionofstep-inrights; fullcounterpartyconsents,transferrestrictionsandcontractscopeareunavailableinthepublishedanalysis. Notaninferreduniversalabilitytosell/redeployGPUs.',stage='signed',accounting_framework='unknown',source_perspective='counterparty')

note('CEREBRAS_OPENAI','exhibit1012-sx1.htm','cerebras_loan_named_legal_parties_and_MRA',
     ('THIS SECURED PROMISSORY NOTE, dated as of January 5, 2026',
      'evidencing the Working Capital Loan.'),
     'Executed note names Cerebras Systems Inc. and OpenAI OpCo, LLC, including Delaware jurisdictions, and explicitly refers to the December24MRA. This binds the source loan to its legal parties; contract principal differs from financial-statement rounding.',stage='signed',counterparty='OpenAI OpCo, LLC',counterparty_evidence='named')
note('CEREBRAS_OPENAI','exhibit1012-sx1.htm','cerebras_ringfenced_loan_purpose',
     ('1. Use of Proceeds.', '2. Interest.'),
     'Loan proceeds go to a lockbox and are dedicated to services development, software and hardware manufacturing under the MRA. They are not general unrestricted operating cash.',stage='signed')
note('CEREBRAS_OPENAI','exhibit1012-sx1.htm','cerebras_noncash_repayment_and_interest',
     ('2. Interest.', '3. Payments; Repayment.'),
     'The note bears6%interest, but accrued interest can be deemed paid when principal is repaid through specified services or asset transfers. Actual cash interest cannot be inferred from the contractual rate.',stage='signed')
note('CEREBRAS_OPENAI','cbrs-20260630.htm','cerebras_contractual_bundle_and_named_revenue_binding',
     ('In December 2025, the Company entered into a Master Relationship Agreement',
      'Refer to Note 10 - Debt and Note 12 - Common Stock for further discussion.'),
     'The financial note directly names OpenAI OpCo, LLC and identifies services, funded working-capital loan and ClassNwarrant in the same MRA. Existing revenue and financing observations are attributed to this named bundle, with no dollar-by-dollar recycling claim.',stage='recognized',counterparty='OpenAI OpCo, LLC',counterparty_evidence='named')
note('CEREBRAS_OPENAI','cbrs-20260630.htm','cerebras_H1_total_revenue_denominator',None,
     'Primary income-statement H1 revenue USD373.516m on the sameJanuary–June2026 period and USD basis as the OpenAI revenue. This denominator supports a descriptive named-customer share, not tracing the source of customer cash.',
     inline='f-147',stage='recognized',measurement_basis='same_period_primary_statement_revenue_denominator')
note('WHCO_CAPITAL_SOLUTION','ahl-20260630.htm','whco_named_broadcom_anthropic_purchase_and_guarantee',
     ('Purchase Obligation Guarantee—In the second quarter of 2026',
      '35% of any amounts paid by AHL under its guarantee.'),
     'Athene names Broadcom, Anthropic and WHCO in theUSD35bncapital arrangement. Athene supports15%of WHCO outstanding purchase obligations, with35%reimbursement from an unnamed third party. Purchase-base guarantee differs from Broadcom’s lease-base backstop; do not calculate15%of the entireUSD35bn or a complete loss waterfall.',stage='signed')
note('WHCO_CAPITAL_SOLUTION','avgo-20260802.htm','broadcom_current_backstop_formula_and_no_payment',
     ('During the fiscal quarter ended August 2, 2026, we arranged for a financial partner',
      'No amounts have been paid under the Backstop.'),
     'LatestBroadcomnote: liability aftercustomerlease default equals85%of outstandingbackstop amounts less equipment sale value, subject to remedies. MaximumUSD29bnonly atfull deployment; currentfairvalue notmaterial and no payment reported. Partner/customer are not named in this note; exactallocation toWHCOrequires further binding.',
     amount='29000000000',amount_qualifier='up_to',stage='signed',period_end='2026-08-02',measurement_basis='full_deployment_conditional_lease_backstop_maximum_not_current_encours')
note('WHCO_CAPITAL_SOLUTION','avgo-20260802.htm','broadcom_conditional_convertible_notes_unissued',
     ('In connection with lease agreements that enable access to compute capacity',
      'no notes have been issued to us.'),
     'Customer may issue up toUSD42bnconvertiblenotes underconditions solelyforleaseobligations; noneissued atAugust2. Capacity for contingent support is not an actual loan or another current exposure to add to theUSD29bnbackstop.',
     amount='42000000000',amount_qualifier='up_to',stage='signed',period_end='2026-08-02',measurement_basis='conditional_unissued_note_capacity_not_outstanding_financing')
note('TERAWULF_FLUIDSTACK','wulf-20260630.htm','wulf_named_fluidstack_google_lease_backstop',
     ('In connection with the Fluidstack HPC Leases the Company entered into recognition agreements',
      'assume the Fluidstack HPC Lease as the tenant thereunder.'),
     'NamesFluidstackUSA I Inc.andGoogleLLC. Backstop starts at eachleasecommencement, with termination-fee orrent/assumption options after specifieddefault/insolvency. This is not a blanketguarantee of TeraWulf debt.',stage='signed')
note('TERAWULF_FLUIDSTACK','wulf-20260630.htm','wulf_precommencement_warrants_pledged_to_lenders',
     ('As a condition to receiving the Google Warrants prior to the effective date applicable to the Google Backstop',
      'the Company’s $3,200.0 million 2030 Secured Notes financing in October 2025 (see Note 10).'),
     'Before the backstop becomes effective, Googlewarrants are pledged for constructionlenders under a separate agreement. Warrants/pledge/leasebackstop are distinct protections at different phases; theUSD3.2bnnotes are not the warrantvalue or aGoogleloan.',stage='signed')
note('TERAWULF_FLUIDSTACK','wulf-20260630.htm','wulf_partial_commencement_and_remaining_delivery',
     ('As of June 30, 2026, all of the Core42 HPC Leases have commenced',
      'in early 2027.'),
     'Only oneFluidstackleasepartiallycommenced atJune30; remainingleases expectedlater2026/early2027. Do not treat all leasebackstops as fullyeffective or currentrent.',stage='delivered',period_end='2026-06-30')

# Existing monetary observations are reused without changing their raw values.

if __name__=='__main__':
    base=ROOT/'work/dependencies'
    save(base/'authored_observations.json',OUT)
    save(base/'selected_native_facts.json',list(FACTS.values()))
    save(base/'attribution_proofs.json',PROOFS)
    save(base/'case_evidence.json',CASES)
    print('Personally authored observations:',len(OUT),'selected native facts:',len(FACTS))
