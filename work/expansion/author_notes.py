"""Rows authored after reading complete original financial notes."""
from pathlib import Path
from secfragility.expansion_reading import submit
ROOT=Path(__file__).resolve().parents[2]

AUTHORED={
 '012636436f12':[
  dict(candidate_index=0,quote='As of June 30, 2026, the Company had approximately $1.0 billion of expected future cash expenditures under its outstanding purchase and construction commitments, primarily related to infrastructure development costs, power utility deposits, equipment procurement, and labor.',model_quantity='construction_commitment',stage='signed',amount_qualifier='approximately',amount_nature='expected_future_cash_expenditures',block='contractual_outflows',category_id='construction_commitment',measurement_basis='outstanding_purchase_and_construction_commitments'),
  dict(candidate_index=1,quote='Of this amount, $264 million will be passed through to the Company’s customer as invoiced.',model_quantity='customer_pass_through_construction_commitment',stage='signed',amount_nature='customer_reimbursement_component',measurement_basis='component_of_gross_construction_commitments;not_cash_received',counterparty_evidence='anonymous'),
  dict(quote='Substantially all of these expenditures are expected to occur within the next 12 months.',model_quantity='construction_commitment_timing',stage='signed'),
 ],
 '268c12e85586':[
  dict(candidate_index=59,quote='On May 6, 2026, Core Scientific Finance, an indirect wholly-owned subsidiary of the Company, completed a private offering of $3.30 billion aggregate principal amount of 7.75% Senior Secured Notes due 2031 at an issue price of 99.25% of the principal amount.',model_quantity='project_debt_face_amount',stage='signed',amount_nature='principal_face_not_net_cash_proceeds',measurement_basis='senior_secured_notes_principal',vehicle_level=True),
  dict(quote='Amortization of principal will commence on the First Installment Payment Date, defined in the indenture as the first semi-annual payment date to occur at least 15 days after the later of (i) rent commencement under the related datacenter leases and (ii) the abatement of all revenue credits provided by the Company or its affiliates to the tenant under the related datacenter leases.',model_quantity='project_debt_amortization_trigger',stage='signed',judgment_sensitive=True),
  dict(quote='In addition, the Company provided an uncapped completion guarantee for the benefit of the holders with respect to the completion of specified data center development projects.',model_quantity='completion_guarantee_uncapped',stage='signed',block='contingent_obligations',category_id='guarantee',flag_unknown_reason='uncapped_guarantee_no_finite_amount'),
  dict(quote='The remaining net proceeds were used to fund a debt service reserve account, of which $344.8 million remained on deposit as of June 30, 2026, and are included in Restricted cash on the condensed consolidated balance sheets.',model_quantity='project_debt_service_reserve_cash',stage='recognized',is_ring_fenced=True),
 ],
 'b79af9f36344':[
  dict(candidate_index=202,quote='For the three months ended June 30, 2026 and 2025, 83% and 13%, respectively, of the Company’s total revenue was generated from one customer in the Colocation segment.',model_quantity='customer_concentration_anonymous',stage='recognized',counterparty_evidence='anonymous',measurement_basis='share_of_consolidated_revenue;customer_in_colocation_segment;identity_not_established'),
  dict(candidate_index=204,quote='For the six months ended June 30, 2026 and 2025, 77% and 12%, respectively, of the Company’s total revenue was generated from one customer in the Colocation segment.',model_quantity='customer_concentration_anonymous',stage='recognized',counterparty_evidence='anonymous',measurement_basis='share_of_consolidated_revenue;customer_in_colocation_segment;identity_not_established'),
 ],
 '855b548df7e2':[
  dict(quote='On July 27, 2026, the Company entered into Lease Agreements (collectively, the “AMD Leases”) with Advanced Micro Devices, Inc. (“AMD”) for an aggregate of 377 MW of critical IT capacity at the Company’s Pecos, TX; Muskogee, OK; and Hunt County, TX sites;',counterparty='Advanced Micro Devices, Inc.',counterparty_evidence='named',model_quantity='named_capacity_lease',stage='signed',event_date='2026-07-27',family='commercial',link_type='capacity_lease',payer='Advanced Micro Devices, Inc.',receiver='Core Scientific, Inc.'),
  dict(quote='(ii) providing AMD the right, but not the obligation, to cure certain defaults of Neocloud under the applicable Neocloud Lease,',model_quantity='optional_customer_credit_support',stage='signed',counterparty='AMD',counterparty_evidence='named',conditionality='optional',issuer_treatment='Right to cure is not an unconditional payment guarantee.'),
  dict(quote='In addition, the Company issued to AMD a warrant (the “Warrant”) to purchase up to 30 million shares (the “Warrant Shares”) of the Company’s common stock, par value $0.00001 per share (“Common Stock”) at an exercise price of $23.47 per share,',model_quantity='customer_warrant_terms',stage='signed',counterparty='AMD',counterparty_evidence='named',family='customer_consideration',link_type='equity_or_warrants_to_customer',payer='Core Scientific, Inc.',receiver='AMD'),
  dict(quote='The Company is evaluating the accounting treatment, including measurement and classification.',model_quantity='customer_warrant_accounting_not_yet_determined',stage='signed',judgment_sensitive=True),
 ],
 '1c4a9f0c4ec2':[
  dict(quote='Restricted cash as of June 30, 2026, consisted of (i) funds held in the debt service reserve account established under the indenture governing the Company’s $3.3 billion aggregate principal amount of 7.75% Senior Secured Notes due 2031 (the “Senior Secured Notes”), (ii) funds held in escrow in connection with the pending acquisition of Polaris DS LLC, which will be applied to the purchase price at closing, and (iii) funds held in escrow in connection with certain construction and development activities.',model_quantity='restricted_cash_uses',stage='recognized',is_ring_fenced=True),
 ],
 '08476e003238':[
  dict(quote='As of August 31, 2026 and May 31, 2026, the Company recorded $39.3 million and $4.7 million, respectively, of deferred revenue primarily related to advance billings for tenant fit-out services and the delivery of power.',model_quantity='customer_advances',stage='recognized',counterparty_evidence='anonymous',measurement_basis='deferred_revenue_stock_not_period_cash_receipts'),
  dict(quote='The contract\nassets balance was $103.1 million and $43.1 million as of August 31, 2026 and May 31, 2026, respectively, and is included in “accounts receivable, net” and “other assets” in the unaudited condensed consolidated balance sheet.',model_quantity='contract_assets',stage='recognized',counterparty_evidence='anonymous'),
 ],
 '92ceeeb2598d':[
  dict(quote='The principal amount of the 2031 7.000% Notes will amortize on a semi-annual basis beginning after the final commencement date of the applicable data center leases in effect on the issue date.',model_quantity='project_debt_amortization_trigger',stage='signed',vehicle_level=True),
  dict(quote='Upon receipt of certain termination fees under an applicable data center lease, APLD ComputeCo 3 generally will be required to apply the proceeds to redeem the 2031 7.000% Notes at 100% of the principal amount, plus accrued and unpaid interest, to, but excluding, the redemption date, subject to the permitted deferral and replacement tenant provisions set forth in the 2031 7.000% Notes Indenture.',model_quantity='lease_termination_debt_repayment_waterfall',stage='signed',vehicle_level=True),
  dict(quote='In connection with the 2031 7.000% Notes, the Company provides a customary completion guarantee with respect to the construction and completion of the ELN-04 data center project. Other than the completion guarantee, the Company is not a guarantor of any obligations under the 2031 7.000% Notes.',model_quantity='completion_guarantee_scope',stage='signed',vehicle_level=True),
  dict(quote='As of August 31, 2026, approximately $82.4 million was drawn under the 2026 Revolving Credit Facility and approximately $241.0 million of standby letters of credit were outstanding under the 2026 Revolving Credit Facility.',model_quantity='facility_drawings_and_letters_of_credit',stage='recognized',measurement_basis='drawings_and_LCs_reduce_remaining_capacity;not_full_430m_available_cash'),
  dict(quote='The Company was in compliance with the applicable financial covenants under all outstanding debt arrangements as of August 31, 2026.',model_quantity='sig_covenant_events',stage='recognized',event_present=False),
 ],
 'e1391303ab76':[
  dict(quote='On June 5, 2026, the Company entered into an approximately 15-year lease (with three five-year renewal options) with a high investment-grade hyperscaler at its Delta Forge 2 210 MW critical IT load campus located in its southern region, comprising a single building under construction.',model_quantity='anonymous_capacity_lease',stage='signed',counterparty_evidence='anonymous'),
  dict(quote='Following the signing of this lease, our aggregate contracted critical IT load is 1,410 MW.',model_quantity='contracted_capacity_scope',stage='signed',issuer_treatment='Includes anonymous counterparties; no automatic attribution to CoreWeave.'),
 ],
 '2d9c3383237c':[
  dict(quote='The Company has determined that it is the primary beneficiary of one VIE, APLD HPC TopCo 2 LLC (“TopCo 2”), as it has both the power to direct the activities that most significantly impact the entity’s economic performance and the obligation to absorb losses or the right to receive benefits that could potentially be significant to the VIE.',model_quantity='VIE_consolidation_treatment',stage='recognized',counterparty='APLD HPC TopCo 2 LLC',counterparty_evidence='named',vehicle_level=True),
  dict(quote='TopCo 2 is a bankruptcy-remote legal entity with separate assets and liabilities. The creditors of TopCo 2 have recourse to the Company’s general\ncredit.',model_quantity='VIE_creditor_recourse',stage='signed',vehicle_level=True,recourse='creditors_have_recourse_to_company_general_credit'),
  dict(quote='Accordingly, the Company does not consolidate Base Electron because ASC 810 requires both power and economics for consolidation.',model_quantity='VIE_consolidation_treatment',stage='recognized',counterparty='Base Electron',counterparty_evidence='named',vehicle_level=True),
 ],
 '06bf7b5f7084':[
  dict(quote='As of August 31, 2026, the Company had a minimum commitment of approximately $12.1 million related to the energy services agreement for its Jamestown, North Dakota co-hosting facility payable over, approximately, the next 0.4 years.',model_quantity='power_purchase_agreement',stage='signed',counterparty_evidence='anonymous',block='contractual_outflows',category_id='power_purchase_agreement'),
 ],
 '87233ead7d6f':[
  dict(quote='On October 4, 2026, the Company entered into a Power Purchase Agreement with Base Electron, for the purchase of capacity and energy from an approximately 1,200 MW natural gas-fired generation facility to be developed by Base Electron in North Dakota, which is intended to provide dedicated generation for the Company’s Polaris Forge 3 campus expansion.',model_quantity='named_power_purchase_agreement',stage='signed',counterparty='Base Electron',counterparty_evidence='named',event_date='2026-10-04'),
 ],
 '7f299aba57b5':[
  dict(candidate_index=35,quote='AHL’s guarantee represents 15% of the outstanding purchase obligation, which is expected to be satisfied as fundings occur and no later than 2028.',model_quantity='purchase_obligation_guarantee_percentage',stage='signed',counterparty='WarehouseCo Intermediate Holdings LP',counterparty_evidence='named',amount_nature='guarantee_percentage_of_remaining_purchase_obligation',measurement_basis='not_15_percent_of_35bn_contract_size'),
  dict(candidate_index=36,quote='AHL’s guarantee is not probable of payment as the funding obligations are expected to be satisfied by the committed financing arrangements established as part of the transaction structure; therefore, there is no liability on our condensed consolidated financial statements.',model_quantity='purchase_obligation_guarantee_carrying_amount',stage='recognized',measurement_basis='recognized_guarantee_liability;not_zero_contingent_exposure'),
  dict(quote='Separately, AHL has an agreement with a third party under which AHL would be reimbursed for 35% of any amounts paid by AHL under its guarantee.',model_quantity='guarantee_reimbursement_terms',stage='signed',counterparty_evidence='anonymous',measurement_basis='reimbursement_of_actual_payment;not_automatic_guarantee_netting'),
  dict(quote='As part of the agreement, an Apollo-managed fund, WarehouseCo Intermediate Holdings LP (WHCO), has a purchase obligation for the compute infrastructure produced under the agreement.',model_quantity='managed_fund_purchase_obligor',stage='signed',counterparty='WarehouseCo Intermediate Holdings LP',counterparty_evidence='named',vehicle_level=True,issuer_treatment='Management relationship alone does not establish consolidation.'),
 ],
 '2b1ce43f7cb1':[
  dict(quote='We are a direct subsidiary of Apollo Global Management, Inc. (AGM, and together with its subsidiaries other than us or our subsidiaries, Apollo).',model_quantity='parent_control_membership',stage='recognized',counterparty='Apollo Global Management, Inc.',counterparty_evidence='named'),
 ],
 'ad11d6b222a5':[
  dict(quote='The Company owns interests in unconsolidated real estate investments with third parties which are primarily accounted for under the FVO.',model_quantity='joint_venture_investment_measurement',stage='recognized',vehicle_level=True,issuer_treatment='Fund holding value is not underlying project debt.'),
 ],
 '7d86a80cb0d8':[
  dict(quote='As of June 30, 2026, the estimated future commitments of the Company to complete the construction of the build-to-suit assets are $1,728,198, which is to be funded through 2029.',model_quantity='joint_venture_construction_commitments_scope',stage='signed',vehicle_level=True,issuer_treatment='Aggregate commitments across build-to-suit JVs; cannot attribute full amount to CTP02/CTP03.'),
 ],
 '46466ad49ee2':[
  dict(quote='(1) The increase in RPOs as of June 30, 2026 was primarily attributable to the CoreWeave Agreement entered into on June 16, 2026, with an aggregate contract value of approximately $335.1 million, less approximately $21.7 million attributable to the fair value of warrants issued to the customer.',model_quantity='customer_contract_and_warrant_RPO_bridge',stage='signed',counterparty='CoreWeave',counterparty_evidence='named',measurement_basis='nominal_contract_less_customer_warrant_fair_value;not_recognized_revenue_or_cash'),
  dict(quote='(2) Effective January 1, 2026, the Company has included contracts with an original duration of one year or less in the above RPOs disclosure. To conform to current period disclosure, the Company has similarly included short-term contracts in the comparative disclosure as of December 31, 2025 resulting in an increase of $4.0 million from amounts previously disclosed.',model_quantity='rpo_reporting_scope_change',stage='recognized',basis_break=True,recast_cause='presentation_reclassification'),
 ],
 '3dad2db95043':[
  dict(quote='As of June 30, 2026, the Company had no outstanding borrowings and no letters of credit under the Revolving Credit Facility and $20.0 million remained available for borrowing.',model_quantity='undrawn_facility',stage='available'),
  dict(quote='As of June 30, 2026, the Company was in compliance with the covenants under the Credit Agreement.',model_quantity='sig_covenant_events',stage='recognized',event_present=False),
  dict(quote='On June 30, 2026, the Company entered into an amendment to the Credit Agreement that modified a negative covenant to increase the permitted indebtedness for capital leases to $150.0 million outstanding.',model_quantity='capital_lease_indebtedness_covenant_cap',stage='signed',measurement_basis='permitted_debt_limit;not_actual_drawn_debt'),
 ],
}

if __name__=='__main__':
 import json
 for key,rows in AUTHORED.items():print(json.dumps(dict(prefix=key,result=submit(ROOT,key,rows)),default=str),flush=True)
