"""Explicitly authored observations from complete natural notes served to the reader."""
from pathlib import Path
from secfragility.expansion_reading import submit
ROOT=Path(__file__).resolve().parents[2]

AUTHORED={
 'cfb175d9d48b':[
  dict(candidate_index=2,quote='Amounts payable within 12 months of balance date:',model_quantity='construction_commitment_12m',stage='signed',block='contractual_outflows',category_id='construction_commitment',measurement_basis='AI_hardware_and_infrastructure_purchase_commitments;not_debt_principal'),
  dict(candidate_index=6,quote='Total commitments',model_quantity='construction_commitment',stage='signed',block='contractual_outflows',category_id='construction_commitment',measurement_basis='AI_hardware_and_infrastructure_purchase_commitments'),
 ],
 'e7ceb2128e71':[
  dict(quote='The proceeds of the GPU Financing are used to finance a portion of the acquisition cost of GPUs and related infrastructure deployed by the Financing SPV in support of the Group’s agreement with Microsoft Corporation (“Microsoft”) announced in November 2025 (the “Microsoft Agreement”).',model_quantity='project_financing_customer_dependency',stage='signed',counterparty='Microsoft Corporation',counterparty_evidence='named',vehicle_level=True),
  dict(quote='As at June 30, 2026, $413 million of the DDTL had been funded and $1,132 million of unfunded commitment remained available subject to the conditions precedent.',model_quantity='project_facility_funding_status',stage='recognized',vehicle_level=True),
  dict(quote='As at June 30, 2026, $525 million of USPP Senior Notes had been issued and $1,575 million of unfunded commitment remained available subject to the conditions precedent.',model_quantity='project_facility_funding_status',stage='recognized',vehicle_level=True),
  dict(quote='If Microsoft validly terminates a funded tranche of the Microsoft Agreement and a replacement qualified customer is not secured during the ensuing remarketing period, the Parent has guaranteed that (i) the debt and notes allocated to that tranche, net of any disposition proceeds realized from the sale of the GPUs associated with such terminated tranche and applied to prepayment, payable within five business days of demand, and (ii) any upfront amount owed to Microsoft on termination, payable when due (subject to a carve-out where the Collateral Agent enforces against the collateral during the remarketing period).',model_quantity='customer_termination_parent_guarantee',stage='signed',counterparty='Microsoft Corporation',counterparty_evidence='named',vehicle_level=True,block='contingent_obligations',category_id='guarantee'),
  dict(quote='This is a performance guarantee and not a guarantee of the Financing SPV\'s borrowings.',model_quantity='managed_services_guarantee_scope',stage='signed',vehicle_level=True),
  dict(quote='As at June 30, 2026, the Group was in compliance with all financial and operational covenants.',model_quantity='sig_covenant_events',stage='recognized',event_present=False),
 ],
 '2fe539fa2185':[
  dict(quote='No lease revenue was recognized during the periods presented in the Consolidated Statements of Operations and Comprehensive Income (Loss).',model_quantity='uncommenced_customer_lease_revenue',stage='recognized'),
  dict(candidate_index=20,quote='Deferred lease revenue — operating leases',model_quantity='customer_lease_advance_stock',stage='recognized',measurement_basis='advance_payments_received_on_uncommenced_tranches;not_ASC606_RPO_or_period_cash_receipts'),
  dict(quote='As of June 30, 2026, the Group had $5.1 billion of unsatisfied RPO, of which $0.9 billion is expected to be recognized over the initial 12 months ending June 30, 2027, $1.3 billion between months 13 and 24, and the remaining balance recognized between months 25 and 60.',model_quantity='RPO_recognition_schedule',stage='signed'),
  dict(quote='As of June 30, 2026, the aggregate contracted value of lease arrangements was approximately $11.4 billion.',model_quantity='lease_contract_value',stage='signed',measurement_basis='ASC842_lease_contracts_separate_from_ASC606_RPO'),
 ],
 'c7ad26bea7a9':[
  dict(quote='Financing cash flows — principal repaid',model_quantity='finance_lease_principal_cash_flow_classification',stage='recognized',measurement_basis='finance_lease_principal_is_financing_cash_flow;not_in_CFO'),
 ],
 '732a9388e287':[
  dict(quote='Borrowings under the MFSA and issuances of Notes will be made in stages and mature 30 months after the relevant funding date.',model_quantity='subsequent_GPU_financing_draw_conditions',stage='signed',event_date='2026-08-25',measurement_basis='up_to_2.4bn_agreement;not_June30_drawn_debt'),
 ],
 'd5dbe328cfb2':[
  dict(quote='Following the completion of the Divestment, the Group continues to have no exposure to the risks and uncertainties associated with the operations of the Divested Businesses.',model_quantity='historical_reporting_scope_break',stage='recognized',basis_break=True,recast_cause='discontinued_operations'),
 ],
 'eb0ee8277258':[
  dict(quote='Upon conversion, the Notes are settled entirely in shares.',model_quantity='convertible_debt_settlement_terms',stage='signed',measurement_basis='share_settlement_on_conversion;not_automatic_cash_maturity_acceleration'),
  dict(quote='The June 2025 Notes and September 2025 Notes are carried at amortized cost, with an unamortized balance of $4,103.2 million as of December 31, 2025.',model_quantity='convertible_debt_carrying_amount',stage='recognized',measurement_basis='amortized_cost;distinct_from_4836.8m_accreted_maturity_principal'),
 ],
 'b76ee8bf20ff':[
  dict(quote='Toloka operating segment previously reported was reclassified into the results of discontinued operations.',model_quantity='segment_reporting_scope_break',stage='recognized',basis_break=True,recast_cause='discontinued_operations'),
 ],
 '80a0b7b849bb':[
  dict(quote='On March 11, 2026, the Group entered into a securities purchase agreement with NVIDIA Corporation (“NVIDIA”), pursuant to which the Group agreed to sell, in a private placement, a pre-funded warrant (the “Warrant”) to purchase an aggregate of 21,065,396 Class A shares, par value €0.01 per share (the “Warrant Shares”), for aggregate gross proceeds of approximately $2.0 billion.',model_quantity='strategic_equity_financing',stage='signed',counterparty='NVIDIA Corporation',counterparty_evidence='named',event_date='2026-03-11',family='financing',link_type='equity_primary',payer='NVIDIA Corporation',receiver='external:0001513845'),
  dict(quote='Under the five-year agreement, the Group will provide approximately $12 billion of dedicated compute capacity across multiple locations, based on large-scale deployments of the NVIDIA Vera Rubin platform, with delivery expected to commence in early 2027.',model_quantity='dedicated_compute_contract',stage='signed',counterparty='Meta',counterparty_evidence='named',event_date='2026-03-16',measurement_basis='dedicated_capacity_contract;not_recognized_revenue_or_cash'),
  dict(quote='The Group currently intends to sell such capacity to third-party customers of its AI cloud business, with any remaining capacity to be purchased by Meta.',model_quantity='residual_compute_capacity_purchase_backstop',stage='signed',counterparty='Meta',counterparty_evidence='named',measurement_basis='up_to_15bn_residual_capacity;not_27bn_unconditional_dedicated_compute'),
  dict(quote='The option to purchase an additional $337.5 aggregate principal amount of the 2031 Notes was exercised, increasing the total aggregate principal amount of the Notes to approximately $4.34 billion.',model_quantity='subsequent_convertible_financing',stage='signed',event_date='2026-03-20',measurement_basis='post_Dec31_financing;excluded_from_Dec31_balance'),
 ],
 '47b8716dc85e':[
  dict(quote='Subsequent to the deconsolidation, the Group retained significant influence over Toloka Group.',model_quantity='investee_control_change',stage='recognized',counterparty='Toloka Group',counterparty_evidence='named'),
 ],
 '2899fd0d1e43':[
  dict(quote='These leases have not commenced and no revenue has been recognized as of June 30, 2026.',model_quantity='uncommenced_customer_lease_revenue',stage='recognized'),
  dict(quote='As of June 30, 2026, the Company recorded $25.5 million of Deferred revenue on its condensed consolidated balance sheet, representing amounts billed to, or received from HPC tenants for tenant-requested change orders.',model_quantity='customer_lease_advance_stock',stage='recognized',counterparty_evidence='anonymous',measurement_basis='billed_or_received_change_orders;not_all_received_cash'),
 ],
 '78350f3e9ea7':[
  dict(candidate_index=0,quote='In the normal course of business, the Company enters into contracts with suppliers, primarily related to construction, and has commitments of approximately $2,169.3 million as of June 30, 2026.',model_quantity='construction_commitment',stage='signed',block='contractual_outflows',category_id='construction_commitment'),
 ],
 'f8776f3c4045':[
  dict(quote='During the period prior to the first to occur of the commencement of operations at the Barber Lake Facility and the Black Pearl Facility (the “Pre-Completion Availability Period”), aggregate borrowings under the Revolving Credit Facility are limited to $50.0 million (the “Pre-Completion Availability Cap”).',model_quantity='facility_pre_completion_availability_cap',stage='available',measurement_basis='conditional_50m_cap;not_200m_unrestricted_capacity'),
  dict(quote='As of June 30, 2026, there were $33.1 million of letters of credit outstanding under the Revolving Credit Facility and no revolving borrowings outstanding.',model_quantity='facility_drawings_and_letters_of_credit',stage='recognized'),
  dict(quote='Each borrowing under the Revolving Credit Facility is also conditioned upon, among other things, the Company’s market capitalization meeting a specified minimum as of the trading day immediately preceding such borrowing.',model_quantity='facility_market_capitalization_condition',stage='signed',judgment_sensitive=True),
  dict(quote='As of June 30, 2026, the Company was in compliance with all covenants under the Revolving Credit Facility.',model_quantity='sig_covenant_events',stage='recognized',event_present=False),
  dict(quote='No amortization will be payable prior to the completion of the Barber Lake Facility.',model_quantity='project_debt_amortization_trigger',stage='signed',vehicle_level=True),
 ],
 '9f508e6fc48c':[
  dict(quote='On September 24, 2025, as consideration for Google agreeing to backstop certain obligations of Fluidstack in connection with the Barber Lake Facility lease, the Company entered into the Google Warrant Agreement, pursuant to which the Company issued to Google warrants to purchase 24,178,576 shares (the “Warrant Shares”) of the Company’s Common Stock for an exercise price of $0.01 per share of Common Stock (the “Google Warrants”).',model_quantity='credit_support_warrant_terms',stage='signed',counterparty='Google',counterparty_evidence='named',event_date='2025-09-24'),
  dict(quote='Additionally, if, on the business day prior to the beginning of the exercise period under the Google Warrant Agreement, the value of the Warrant Shares does not equal or exceed $430.0 million, the Company shall be obligated to issue additional Warrant Shares and/or make a cash payment equal in the aggregate to such shortfall amount on the terms set forth in the Warrant Agreement.',model_quantity='credit_support_warrant_value_floor',stage='signed',block='contingent_obligations',category_id='guarantee',judgment_sensitive=True),
  dict(quote='The Company recorded an asset of $544.5 million in Other noncurrent assets on the condensed consolidated balance sheets at the initial fair value of the Google Warrants at issuance to represent the value of Google agreeing to make the lease payments from Fluidstack in the event of Fluidstack not fulfilling its obligations under the lease.',model_quantity='credit_support_warrant_accounting',stage='recognized',measurement_basis='noncash_deferred_credit_support_asset;not_cash_financing'),
 ],
 '7c942204e003':[
  dict(quote='During the six months ended June 30, 2026, the Company received proceeds of $129.2 million, net of issuance costs, from the sale of 5,496,993 shares of common stock, with an average net selling price of $23.50 per share.',model_quantity='equity_ATM_cash_proceeds',stage='drawn_or_paid'),
 ],
 'ac57d7781bee':[
  dict(quote='On July 24, 2026, the Company amended the HPC lease at the Black Pearl Facility, which accelerated delivery of the first capacity to early August.',model_quantity='subsequent_customer_lease_delivery_change',stage='signed',event_date='2026-07-24'),
 ],
 'edc66ffd3e03':[
  dict(candidate_index=2,quote='Coreweave Financing V, LLC - DDTL',model_quantity='lender_unfunded_commitment',stage='signed',counterparty='Coreweave Financing V, LLC',counterparty_evidence='named',vehicle_level=True,measurement_basis='GECC_undrawn_commitment;not_total_borrower_facility'),
 ],
 '37453e49b09e':[
  dict(quote='In the event that the borrower can settle in kind or via cash payment, the income is not included as PIK until the borrower elects to pay in kind and the payment is received by the Company.',model_quantity='lender_PIK_recognition_policy',stage='recognized',measurement_basis='fund_policy;does_not_establish_CoreWeave_position_PIK_income'),
  dict(quote='Interest income in CLO subordinated note investments are recorded on an accrual basis utilizing an effective interest methodology based upon an effective yield to maturity of projected cash flows.',model_quantity='lender_interest_income_policy',stage='recognized'),
 ],
 '319400ca0143':[
  dict(quote='Gross additions include increases resulting from new or additional portfolio investments, capitalized PIK income, accretion of discounts and the exchange of one or more existing securities for one or more new securities.',model_quantity='lender_portfolio_rollforward_scope',stage='recognized',measurement_basis='additions_are_not_all_cash_advanced'),
 ],
 '8a0473f1c07f':[
  dict(quote='As of June 30, 2026, the Company held one investment in the portfolio on non-accrual status.',model_quantity='lender_portfolio_non_accrual_count',stage='recognized',measurement_basis='fund_total;borrower_identity_not_established_by_this_note'),
  dict(quote='Beginning with the period ended June 30, 2026, the Company is transitioning to the Global Industry Classification Standard ("GICS") to align its portfolio composition reporting with the convention more broadly used across the financial markets.',model_quantity='lender_industry_reporting_scope_change',stage='recognized',basis_break=True,recast_cause='presentation_reclassification'),
 ],
 'ac48837ed85a':[
  dict(quote='Since these commitments and the associated amounts may expire without being drawn upon, the total commitment amount does not necessarily represent a future cash requirement.',model_quantity='lender_unfunded_commitment_recognition_policy',stage='signed'),
  dict(quote='CoreWeave Compute Acquisition Co., IV, LLC',model_quantity='lender_prior_period_unfunded_commitment',stage='signed',period_end='2025-12-31',counterparty='CoreWeave Compute Acquisition Co., IV, LLC',counterparty_evidence='named',vehicle_level=True,measurement_basis='December31_commitment_10.168m;not_present_in_June30_table;reason_not_established'),
 ],
 '22563f72eca5':[
  dict(quote='Debt investments are generally placed on non-accrual status when interest payments are at least 90 days past due or there is reasonable doubt that principal or interest will be collected.',model_quantity='lender_non_accrual_policy',stage='recognized',measurement_basis='policy;not_position_specific_default_evidence'),
  dict(quote='If at any point the Company believes PIK is not expected to be realized, the investment generating PIK will be placed on non-accrual status.',model_quantity='lender_PIK_recognition_policy',stage='recognized'),
 ],
}

if __name__=='__main__':
 import json
 for key,rows in AUTHORED.items():print(json.dumps(dict(prefix=key,result=submit(ROOT,key,rows)),default=str),flush=True)
