"""Further manual reading judgments; no automatic passage extraction."""
from pathlib import Path
import json
from secfragility.expansion_reading import submit
ROOT=Path(__file__).resolve().parents[2]
AUTHORED={
 '3d8f5628e845':[
  dict(quote='In June 2026, the Company entered into a multi-year Master Strategic Agreement with CoreWeave, Inc. (“CoreWeave”) under which the Company will provide committed B2 Cloud Storage capacity and managed storage services on CoreWeave’s infrastructure (the “CoreWeave Agreement”).',model_quantity='named_storage_contract',stage='signed',counterparty='CoreWeave, Inc.',counterparty_evidence='named',family='commercial',link_type='purchase',payer='CoreWeave, Inc.',receiver='external:0001462056'),
  dict(quote='In connection with the CoreWeave Agreement, the Company issued CoreWeave two equity-classified warrants to purchase an aggregate of 4,194,876 shares of the Company’s Class A common stock, consisting of an initial warrant to purchase 3,053,314 shares (the “Initial Warrant”) and an additional warrant to purchase 1,141,562 shares (the “Additional Warrant”).',model_quantity='customer_warrant_terms',stage='signed',counterparty='CoreWeave',counterparty_evidence='named',family='customer_consideration',link_type='equity_or_warrants_to_customer',payer='external:0001462056',receiver='CoreWeave'),
  dict(quote='The grant-date fair value of the warrants expected or probable to vest is recognized as a reduction of revenue in the same pattern as the related revenue.',model_quantity='customer_warrant_revenue_reduction_policy',stage='signed'),
  dict(quote='Because recognition of the related revenue had not commenced as of June 30, 2026, no revenue reduction related to the warrants was recognized during the three and six months ended June 30, 2026.',model_quantity='customer_warrant_revenue_recognition_status',stage='recognized'),
 ],
 '9949640ffc63':[
  dict(quote="This temporary equity presentation is the result of the redeemable noncontrolling interest being subject to certain redemption rights that are not entirely within the Company's control.",model_quantity='redeemable_noncontrolling_equity_classification',stage='recognized',vehicle_level=True),
  dict(quote='The change in redeemable noncontrolling interest consists of $60.1 million of preferred stock dividends paid in-kind, $1.3 million of contributions from noncontrolling interest, net of costs and $6.8 million in current year net loss attributable to non-controlling interest.',model_quantity='redeemable_noncontrolling_equity_PIK_dividends',stage='recognized',measurement_basis='preferred_dividends;not_BDC_loan_PIK_income;quarter_ended_Aug31'),
 ],
 '5922174dfa89':[
  dict(quote='The Google Backstop under each Google Recognition Agreement becomes effective as of the commencement date under the corresponding Fluidstack HPC Lease.',model_quantity='customer_credit_backstop_effective_date',stage='signed',counterparty='Google LLC',counterparty_evidence='named'),
  dict(quote='In the event of a payment default under a Fluidstack HPC Lease, or if Fluidstack becomes subject to an insolvency event, following notice from the Company, Google will have the option to either (i) pay the termination fee under such Fluidstack HPC Lease (the “Termination Fee”) or (ii) pay all rent currently due under the Fluidstack HPC Lease and assume the Fluidstack HPC Lease as the tenant thereunder.',model_quantity='customer_credit_backstop_alternative_remedies',stage='signed',counterparty='Google LLC',counterparty_evidence='named'),
  dict(quote='The Company recorded an asset of $515.5 million based on the fair value of the Google Warrants at issuance, which is in deferred charges in the condensed consolidated balance sheets as of June 30, 2026 and December 31, 2025.',model_quantity='credit_support_warrant_accounting',stage='recognized',measurement_basis='deferred_credit_support_asset;not_revenue_reduction_or_cash_financing'),
  dict(quote='During the six months ended June 30, 2025, the Company received the $90.0 million of Prepaid Rent from the customer and as of June 30, 2026 recorded $49.7 million and $0.9 million in current portion of deferred rent liability and deferred rent liability, net of current portion, respectively, in the condensed consolidated balance sheet.',model_quantity='customer_rent_prepayment_timing',stage='recognized',measurement_basis='cash_received_H1_2025;remaining_stock_50.6m_at_June2026'),
 ],
 '670475832c3b':[
  dict(quote='The Company has provided customary completion guarantees with respect to the HPC buildout at the Lake Mariner Data Campus under which it will fund Wulf Compute as necessary to ensure the timely completion of the HPC data center buildings.',model_quantity='completion_guarantee_scope',stage='signed',vehicle_level=True),
  dict(quote='In connection with the 2030 Secured Notes, an affiliate of Google unconditionally agreed with the collateral agent for the benefit of the lenders that it shall (or shall cause Google to) pay the Termination Fee in accordance with the timing requirements set forth in the respective Google Recognition Agreements.',model_quantity='project_lender_credit_support',stage='signed',counterparty='Google',counterparty_evidence='named',vehicle_level=True),
  dict(quote='As the First Commencement Date had not occurred as of June 30, 2026, the Company’s borrowing and letter of credit capacity under the Revolving Credit Facility was limited to $75.0 million in the aggregate as of June 30, 2026.',model_quantity='facility_pre_completion_availability_cap',stage='available',measurement_basis='75m_total_cap;not_250m_available_cash'),
  dict(quote='As of June 30, 2026, no borrowings were outstanding and the Company had $74.8 million of remaining available letter of credit capacity.',model_quantity='facility_remaining_capacity',stage='available',measurement_basis='reported_remaining_LC_capacity;not_unrestricted_cash'),
 ],
 'd80df4ff6912':[
  dict(quote='The Company is expected to pay a net $11.2 million in the aggregate by the first quarter of 2027, which is net of a $0.6 million credit related to the sale of electrical equipment and is being credited against the costs of the transmission system modification.',model_quantity='grid_infrastructure_reimbursement_commitment',stage='signed',counterparty_evidence='anonymous'),
 ],
 '940cf1934071':[
  dict(quote='As of June 30, 2026 and December 31, 2025, the Company had an outstanding commitment for the construction of improvements at its Helios facility totaling $1,489.2 million and $529.8 million, respectively.',model_quantity='construction_commitment',stage='signed',block='contractual_outflows',category_id='construction_commitment',vehicle_level=True),
 ],
 'f8dced0a86ca':[
  dict(quote='On August 15, 2025, Galaxy Helios I LLC (“Galaxy Helios I”), a wholly owned subsidiary of GDH LP, entered into a credit agreement (the “Credit Agreement”) with Deutsche Bank AG providing for a senior secured term loan facility in an aggregate principal amount of up to $1.4 billion.',model_quantity='project_facility_commitment',stage='signed',vehicle_level=True,counterparty='Deutsche Bank AG',counterparty_evidence='named',measurement_basis='facility_limit;not_drawn_balance'),
  dict(quote='The Credit Agreement also contains a financial maintenance covenant, requiring Galaxy Helios I to maintain a minimum debt service coverage ratio of 1.40 beginning with the first full quarter after Stabilization (as defined in the Credit Agreement) and a maximum loan to cost ratio of 80% on the closing date and each fiscal quarter thereafter until Stabilization (as defined in the Credit Agreement).',model_quantity='project_debt_covenant_timing',stage='signed',vehicle_level=True),
  dict(quote='Total interest cost incurred was $28.4 million and $49.5 million for the three and six months ended June 30, 2026 respectively, of which $21.1 million and $42.1 million, respectively, was capitalized to construction in progress related to the development of the Helios data center campus.',model_quantity='project_capitalized_interest',stage='recognized',vehicle_level=True),
 ],
 '45e825c6ff75':[
  dict(quote='On July 28, 2026, Galaxy, through its wholly-owned subsidiary, Galaxy Helios Data Centers II LLC (“Galaxy Data Centers”), completed the issuance and sale of $3.507 billion aggregate principal amount of 9.875% Senior Secured Notes due in 2031 (the “Notes”) in a private offering exempt from registration under Rule 144A and Regulation S of the Securities Act.',model_quantity='subsequent_project_debt_issuance',stage='drawn_or_paid',event_date='2026-07-28',vehicle_level=True,measurement_basis='post_June30_bond_issue;separate_Helios_II_obligor'),
  dict(quote='In connection with the Notes, GDH LP provided a customary, uncapped completion guarantee with respect to the Project.',model_quantity='completion_guarantee_uncapped',stage='signed',vehicle_level=True,block='contingent_obligations',category_id='guarantee',flag_unknown_reason='uncapped_guarantee_no_finite_amount'),
 ],
 '460722d57f36':[
  dict(quote='The Data Centers segment comprises the Helios infrastructure assets.',model_quantity='segment_AI_infrastructure_scope',stage='recognized',measurement_basis='Helios_segment;exclude_parent_crypto_trading_revenues'),
  dict(quote='Net income / (loss) for the period, before taxes',model_quantity='project_segment_income_tax_scope',stage='recognized',measurement_basis='H1_Helios_pre_tax_loss_2.842m;net_income_29.608m_includes_32.450m_tax_benefit'),
 ],
 '08225d504183':[
  dict(quote='The proceeds from these loans are utilized for trading activities.',model_quantity='short_term_borrowing_activity_scope',stage='recognized',measurement_basis='digital_asset_trading;not_all_Helios_project_debt'),
 ],
 '0d1a09bb0432':[
  dict(quote='Deferred lease revenue represents payments received in advance of the Company’s performance obligation under the lease agreements in its Data Centers segment.',model_quantity='customer_lease_advance_stock',stage='recognized',measurement_basis='150m_at_Mar31;not_new_quarter_receipts'),
 ],
 '2e9ee9281c3e':[
  dict(quote='Deferred lease revenue represents payments received in advance of the Company’s performance obligation under the lease agreements in its Data Centers segment.',model_quantity='customer_lease_advance_stock',stage='recognized',measurement_basis='150m_at_June30;no_H1_new_prepayment_in_rollforward'),
 ],
 '7aa8c556ad09':[
  dict(quote='Galaxy’s Helios data center campus, located in the panhandle region of West Texas, has developed the first 133 megawatts (“MW”) of critical IT load, utilizing approximately 200 MW of gross power capacity, for CoreWeave, Inc. (“CoreWeave”) under a 15-year lease agreement (the “Lease Agreement”) entered into in April 2025.',model_quantity='named_capacity_lease',stage='delivered',counterparty='CoreWeave, Inc.',counterparty_evidence='named',family='commercial',link_type='capacity_lease',payer='CoreWeave, Inc.',receiver='external:0001859392'),
  dict(quote='The remaining 830 MW of approved power capacity remains available to be contracted.',model_quantity='approved_uncontracted_capacity',stage='available',measurement_basis='power_approval;not_firm_customer_order'),
 ],
 '4f875ba46c2a':[
  dict(quote='The accompanying unaudited condensed consolidated financial statements have been prepared in accordance with accounting principles generally accepted in the United States of America (“U.S. GAAP”) and applicable rules and regulations of the Securities and Exchange Commission regarding interim financial reporting.',model_quantity='financial_reporting_framework',stage='recognized',accounting_framework='us_gaap'),
  dict(quote='In January 2026, the Company completed an assessment of the useful lives of servers and network equipment based on updated information and usage patterns obtained and concluded that the estimated useful lives of such assets should be extended from four to five years.',model_quantity='GPU_useful_life_estimate_change',stage='recognized',basis_break=True,recast_cause='accounting_change',measurement_basis='prospective_estimate;H1_depreciation_reduction_86.1m;not_cash_savings'),
 ],
 'a735ab1723dd':[
  dict(quote='The Group has contractual obligations arising from contracts with remaining terms greater than one year, primarily consisting of energy and power supply agreements, related to the co-location arrangements and the development of greenfield data center facilities.',model_quantity='power_purchase_agreement',stage='signed',block='contractual_outflows',category_id='power_purchase_agreement',measurement_basis='energy_commitments;not_GPU_construction_commitments'),
 ],
 '99c904ce3dc0':[
  dict(quote='The convertible notes are carried at amortized cost, with a carrying amount of $8,499.0 as of June 30, 2026.',model_quantity='convertible_debt_carrying_amount',stage='recognized',measurement_basis='millions_USD;distinct_from_10041.8m_accreted_maturity_principal_or_20823.7m_fair_value'),
  dict(quote='Upon conversion, notes are settled in cash, shares or a combination of cash and shares, at the Company’s election.',model_quantity='convertible_debt_settlement_terms',stage='signed',measurement_basis='June_2025_and_September_2025_series;June2026_disclosure_differs_from_annual_share_only_description;contract_verification_pending'),
 ],
 'a1d17660d8bb':[
  dict(quote='As of June 30, 2026, the Company had executed additional lease agreements, primarily for data center facilities, as well as equipment, that had not yet commenced.',model_quantity='lease_not_commenced',stage='signed',block='contractual_outflows',category_id='lease_not_commenced',measurement_basis='12054.1m_undiscounted_future_payments;612.4m_prepaid;not_recognized_lease_liability'),
 ],
 '8ceb3daf67cb':[
  dict(quote='On July 10, 2026, the Group entered into its first senior secured debt facility in an aggregate principal amount of approximately $775.',model_quantity='subsequent_project_facility',stage='signed',event_date='2026-07-10',measurement_basis='775m_USD_post_June30_commitment;drawn_status_not_proven'),
 ],
 'a100a31f28f2':[
  dict(quote='Cash and cash equivalents | | 4 | | 3,678.1 | ​ | 8,042.1',model_quantity='cash_and_cash_equivalents',stage='recognized',measurement_basis='millions_USD;June30_8042.1m;not_combined_cash_and_restricted_cash'),
  dict(quote='Deferred revenue, non-current | ​ | ​ | ​ | 1,302.0 | ​ | 4,995.8',model_quantity='customer_advances',stage='recognized',measurement_basis='millions_USD;noncurrent_stock_4995.8m;current_stock_979.4m;counterparty_not_attributed'),
 ],
 '156dd1043209':[
  dict(quote='Deferred revenue | ​ | ​ | | 3.0 | ​ | 4,395.0',model_quantity='customer_advance_cash_flow_driver',stage='recognized',measurement_basis='millions_USD;H1_CFO_driver_4395.0m;CFO_total_4504.1m;not_recurring_margin_cash'),
  dict(quote='Purchases of property and equipment and intangible assets | ​ | ​ | | (1,054.5) | | (8,130.3)',model_quantity='capital_expenditure_combined_cash_outflow',stage='drawn_or_paid',measurement_basis='millions_USD;H1_PPE_plus_intangible_purchases;do_not_automatically_map_combined_caption_to_PPE_only'),
  dict(quote='Proceeds from issuance of pre-funded warrants | ​ | ​ | ​ | — | ​ | 2,000.0',model_quantity='strategic_equity_financing_cash_received',stage='drawn_or_paid',measurement_basis='millions_USD;H1_cash_received;annual_note_names_NVIDIA'),
  dict(quote='Restricted cash and cash equivalents, end of period | ​ | ​ | ​ | 74.5 | ​ | 1,056.0',model_quantity='restricted_cash',stage='recognized',is_ring_fenced=True,measurement_basis='millions_USD;1056.0m_excluded_from_8042.1m_unrestricted_cash'),
 ],
}

if __name__=='__main__':
 for key,rows in AUTHORED.items():print(json.dumps(dict(prefix=key,result=submit(ROOT,key,rows)),default=str),flush=True)
