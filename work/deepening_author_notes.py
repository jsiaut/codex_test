"""Human-authored, source-bound rows. No lexical discovery logic lives here."""
from pathlib import Path
import json
from secfragility.reader import block_for,store
root=Path(__file__).resolve().parents[1]
q=json.loads((root/'work/deepening_reading_queue.json').read_text())
def submit(prefix,authored):
    key=next(r['content_key'] for r in q if r['content_key'].startswith(prefix))
    if (root/'work/observations'/(key+'.jsonl')).exists():return
    b=block_for(root,key);out=[]
    for item in authored:
        item=dict(item);idx=item.pop('candidate_index',None)
        if idx is not None:
            f=b['candidates'][idx]
            item.update(tagged_fact_id=f['fact_id'],amount=str(f['value']),unit=f['unit'],currency=f['currency'],
                period_start=f.get('period_start'),period_end=f['period_end'],amount_origin='tagged_reference')
        if item['quote'] not in b['text']:raise ValueError('Authored quotation not present')
        out.append(item)
    result=store(root,key,out)
    print(json.dumps(dict(key=prefix,**result),default=str),flush=True)
    if result.get('rejected'):raise ValueError('Rejected authored observation')

if __name__=='__main__':
    cp=dict(counterparty='OpenAI OpCo, LLC',counterparty_evidence='derivable',counterparty_method='explicit_cross_reference')
    submit('abe162186e9c',[
        dict(cp,candidate_index=6,quote='Principal amount received in January 2026 | | | | | | $ | 1,004,571 |',
            model_quantity='customer_working_capital_loan_received',stage='drawn_or_paid',event_type='funding',
            amount_nature='cash_flow',amount_qualifier='exact',measurement_basis='principal_cash_received_in_January',
            family='financing',link_type='loan_or_facility',payer='OpenAI OpCo, LLC',receiver='Cerebras Systems Inc.',
            instrument_key='CBRS_OpenAI_WorkingCapitalLoan_2026-01-05'),
        dict(cp,candidate_index=7,quote='Less: non-cash repayments through services and other permitted credits | | | | | | (86,327) | |',
            model_quantity='customer_working_capital_loan_noncash_repayment',stage='settled',event_type='repayment',
            amount_nature='noncash_repayment',amount_qualifier='exact',measurement_basis='noncash_principal_repayment',
            instrument_key='CBRS_OpenAI_WorkingCapitalLoan_2026-01-05'),
        dict(cp,candidate_index=8,quote='Principal balance outstanding as of June 30, 2026 | | | | | | 918,244 | |',
            model_quantity='customer_working_capital_loan_outstanding',stage='recognized',amount_nature='stock',
            amount_qualifier='exact',measurement_basis='principal_outstanding',
            instrument_key='CBRS_OpenAI_WorkingCapitalLoan_2026-01-05'),
        dict(cp,quote='The MRA and Working Capital Loan are evaluated together in accounting for the overall OpenAI customer arrangement. The timing of OpenAI’s funding and the expected repayment of the Working Capital Loan through service fees and other permitted non-cash credits under the MRA result in a significant financing component in the MRA services arrangement.',
            model_quantity='customer_financing_component',stage='recognized',judgment_sensitive=True,
            issuer_treatment='Significant financing component; interest expense increases deferred revenue, subsequently recognized as performance obligations are satisfied.'),
        dict(cp,quote='The Working Capital Loan may be repaid in cash or, subject to the terms of the MRA and the secured promissory note, through service fees, compute capacity, hardware, other services, pass-through monthly recurring charges, applicable asset transfers, or other permitted non-cash credits under the MRA.',
            model_quantity='customer_loan_noncash_repayment_terms',stage='signed'),
        dict(cp,quote='Upon receipt, the proceeds were recorded as restricted cash. Amounts held as restricted cash are subject to contractual use restrictions and are available to fund permitted uses related to the build-out of infrastructure and related capabilities required to deliver services under the MRA.',
            model_quantity='customer_loan_restricted_cash',stage='recognized',is_ring_fenced=True)
    ])
    submit('46d207b28370',[
        dict(counterparty='OpenAI OpCo, LLC',counterparty_evidence='named',
            quote='In December 2025, the Company entered into a Master Relationship Agreement (the “MRA”) with OpenAI OpCo, LLC (“OpenAI”) to provide 750MW of AI inference compute capacity that OpenAI is contractually committed to purchase (the “Committed Capacity”) and related services over a multi-year term.',
            model_quantity='customer_relationship_agreement',stage='signed'),
        dict(cp,candidate_index=38,quote='For the three and six months ended June 30, 2026, the Company recognized revenue of $56.8 million and $74.4 million, respectively, under the arrangement, which is net of amortization of the customer warrant asset of $2.5 million and $3.3 million, respectively.',
            model_quantity='named_customer_revenue',stage='recognized',event_type='recognition',amount_nature='revenue',
            amount_qualifier='approximately',measurement_basis='recognized_revenue_net_of_customer_warrant_amortization',
            family='commercial',link_type='revenue_recognized',payer='OpenAI OpCo, LLC',receiver='Cerebras Systems Inc.',
            instrument_key='CBRS_OpenAI_MRA_2025-12-24')
    ])
    submit('7a4a4f238ce3',[
        dict(cp,candidate_index=2,quote='In July 2026, the OpenAI Warrant was partially exercised to purchase 10,033,508 shares of the Company’s Class N common stock.',
            model_quantity='customer_warrant_exercised_shares',stage='settled',event_type='warrant_vesting',
            amount_nature='shares',amount_qualifier='exact'),
        dict(cp,quote='The OpenAI Warrant vests in multiple tranches upon achievement of specified milestones associated with the MRA, including funding of the Working Capital Loan, delivery of the Committed Capacity and Additional Capacity in tranches, and certain market capitalization or customer payment thresholds.',
            model_quantity='customer_warrant_vesting_terms',stage='signed',conditionality='conditional',
            trigger_description='funding of the Working Capital Loan, delivery of the Committed Capacity and Additional Capacity in tranches, and certain market capitalization or customer payment thresholds',trigger_occurred='unknown')
    ])
    submit('1dcadfc0d843',[
        dict(candidate_index=16,quote='OpenAI (indirect investment) | | | 92,600,000 | | | | - |',counterparty='OpenAI',
            counterparty_evidence='named',model_quantity='indirect_investment_carrying_amount',stage='recognized',
            amount_nature='stock',amount_qualifier='exact',measurement_basis='ASC321_measurement_alternative_SPV_position',
            vehicle_level=True,judgment_sensitive=True,
            issuer_treatment='Passive minority SPV interest; SPV not consolidated under ASC 810; underlying OpenAI securities not held directly.'),
        dict(quote='the Company acquired an indirect interest in OpenAI through a structured investment vehicle (the\n“SPV”) sponsored by an unaffiliated third party, for total cash consideration of $92,600,000.',
            counterparty='OpenAI',counterparty_evidence='named',model_quantity='indirect_investment_cash_to_SPV',stage='drawn_or_paid',
            vehicle_level=True,amount_nature='cash_to_unidentified_SPV',measurement_basis='cash_consideration_for_SPV_interest'),
        dict(quote='the SPV is not consolidated, as the Company holds\na passive, non-controlling investor interest, has no power to direct the activities of the SPV that most significantly affect its economic\nperformance, and is not the primary beneficiary.',model_quantity='investment_SPV_consolidation',stage='recognized',
            judgment_sensitive=True,vehicle_level=True)
    ])
    submit('074012c62719',[
        dict(candidate_index=72,quote='During the six months ended July 31, 2026, we made an additional $300.9 million investment in preferred stock of Anthropic, PBC (“Anthropic”).',
            counterparty='Anthropic, PBC',counterparty_evidence='named',model_quantity='named_investment_acquisitions',
            stage='recognized',amount_nature='investment_acquisition',amount_qualifier='exact',
            measurement_basis='investment_in_preferred_stock_primary_cash_not_established'),
        dict(candidate_index=73,quote='During the three months ended July 31, 2026, we recorded unrealized gains of $1,612.7 million on our investment in Anthropic, based on valuation adjustments using information including Anthropic’s financing round announced on May 28, 2026.',
            counterparty='Anthropic, PBC',counterparty_evidence='derivable',counterparty_method='explicit_cross_reference',
            model_quantity='named_investment_unrealized_gain',stage='recognized',event_type='observable_price_adjustment',
            amount_nature='valuation_gain',amount_qualifier='exact',measurement_basis='ASC321_measurement_alternative_upward_adjustment'),
        dict(candidate_index=74,quote='As of July 31, 2026, the carrying value of our preferred stock of Anthropic was $3,134.5 million.',
            counterparty='Anthropic, PBC',counterparty_evidence='derivable',counterparty_method='explicit_cross_reference',
            model_quantity='named_investment_carrying_amount',stage='recognized',amount_nature='stock',
            amount_qualifier='exact',measurement_basis='ASC321_measurement_alternative'),
        dict(quote='we determined that we do not have a controlling interest or the ability to exercise significant influence over the operating and financial policies of the investees. Therefore, these investments are accounted for under the measurement alternative method.',
            model_quantity='investment_consolidation_treatment',stage='recognized',judgment_sensitive=True)
    ])
    submit('b7ad99b47cb8',[
        dict(candidate_index=132,quote='Upward adjustments for the three and six months ended July 31, 2026 include unrealized gains of $2.7 billion and $3.0 billion, respectively, related to the Company’s investment in Anthropic.',
            counterparty='Anthropic',counterparty_evidence='named',model_quantity='named_investment_unrealized_gain',
            stage='recognized',event_type='observable_price_adjustment',amount_nature='valuation_gain',amount_qualifier='approximately',
            measurement_basis='ASC321_measurement_alternative_upward_adjustment'),
        dict(candidate_index=133,quote='Upward adjustments for the three and six months ended July 31, 2026 include unrealized gains of $2.7 billion and $3.0 billion, respectively, related to the Company’s investment in Anthropic.',
            counterparty='Anthropic',counterparty_evidence='named',model_quantity='named_investment_unrealized_gain',
            stage='recognized',event_type='observable_price_adjustment',amount_nature='valuation_gain',amount_qualifier='approximately',
            measurement_basis='ASC321_measurement_alternative_upward_adjustment')
    ])
    submit('7c03a55bd999',[
        dict(cp,candidate_index=22,quote='The Company recorded customer warrant assets of $457.2 million and $822.9 million for the three and six months ended June 30, 2026.',
            model_quantity='customer_warrant_assets_capitalized',stage='recognized',amount_nature='customer_consideration_asset',
            amount_qualifier='exact',measurement_basis='customer_warrant_asset_capitalized_in_period'),
        dict(cp,quote='The customer warrant asset will be recognized as a reduction of revenue in proportion to the related revenue recognized.',
            model_quantity='customer_warrant_revenue_reduction',stage='recognized',issuer_treatment='Reduction of revenue in proportion to related revenue recognized.'),
        dict(counterparty='Amazon.com NV Investment Holdings LLC',counterparty_evidence='named',
            quote='the remaining 2,427,010 AWS Warrant Shares vest in tranches upon the attainment of specified payment thresholds prior to the fifth anniversary of issuance, based on aggregate payments by Amazon Web Services to us pursuant to certain commercial arrangements between the parties.',
            model_quantity='customer_warrant_vesting_terms',stage='signed',conditionality='conditional',
            trigger_description='attainment of specified payment thresholds',trigger_occurred='unknown')
    ])
    submit('3407c1609083',[
        dict(candidate_index=45,quote='In the second quarter of 2026, Apollo-managed funds and affiliates, including Athene, in partnership with certain third parties, entered into a $35 billion capital solution agreement with Broadcom Inc., which facilitates Anthropic, PBC’s compute infrastructure expansion beginning in mid-2026.',
            counterparty='Broadcom Inc.',counterparty_evidence='named',model_quantity='capital_solution_contract_size',
            stage='signed',amount_nature='transaction_structure_not_cash_flow',amount_qualifier='exact',
            measurement_basis='nominal_capital_solution_agreement'),
        dict(candidate_index=46,quote='AHL’s guarantee represents 15% of the outstanding purchase obligation, which is expected to be satisfied as fundings occur and no later than 2028.',
            counterparty='WarehouseCo Intermediate Holdings LP',counterparty_evidence='named',
            model_quantity='purchase_obligation_guarantee_percentage',stage='signed',amount_nature='percentage',
            amount_qualifier='exact',measurement_basis='percentage_of_outstanding_purchase_obligation_not_total_contract'),
        dict(candidate_index=47,quote='AHL’s guarantee is not probable of payment as the funding obligations are expected to be satisfied by the committed financing arrangements established as part of the transaction structure; therefore, there is no liability on the Company’s condensed consolidated financial statements.',
            counterparty='WarehouseCo Intermediate Holdings LP',counterparty_evidence='named',model_quantity='purchase_obligation_guarantee_carrying_amount',
            stage='recognized',amount_nature='stock',amount_qualifier='exact',measurement_basis='recognized_guarantee_liability',judgment_sensitive=True),
        dict(candidate_index=48,quote='Separately, AHL has an agreement with a third party under which AHL would be reimbursed for 35% of any amounts paid by AHL under its guarantee.',
            counterparty_evidence='anonymous',model_quantity='guarantee_reimbursement_percentage',stage='signed',
            amount_nature='percentage',amount_qualifier='exact',measurement_basis='percentage_of_guarantee_payments')
    ])
    submit('783eee3f3afe',[
        dict(candidate_index=41,quote='The resulting fair value of the Building 4 Warrant was $14.44 per share, totaling $121.2 million, which was recorded to lease incentive asset and additional paid in capital on the Company\'s consolidated balance sheets, and will be amortized over the life of the Building 4 Lease once it commences.',
            counterparty='CoreWeave',counterparty_evidence='named',model_quantity='customer_lease_incentive_asset',
            stage='recognized',amount_nature='customer_consideration_asset',amount_qualifier='exact',measurement_basis='lease_incentive_asset_grant_date_fair_value'),
        dict(quote='On October 31, 2025, CoreWeave assigned the Building 4 Warrant and its rights under the CoreWeave Registration Rights Agreement to Jane Street and on or around May 15, 2026, Jane Street assigned all of its right, title and interest in and to the Building 4 Warrant to WFBNA.',
            counterparty='CoreWeave',counterparty_evidence='named',model_quantity='customer_warrant_assignment',stage='settled')
    ])
    submit('48ca5ceddfd3',[
        dict(quote='a new data center lease with CoreWeave Compute Acquisition Co. VIII, LLC (“CoreWeave SPV”), a wholly owned subsidiary of CoreWeave, for those same two data halls on substantially the same terms as the ELN-02 Parent Lease',
            counterparty='CoreWeave Compute Acquisition Co. VIII, LLC',counterparty_evidence='named',
            model_quantity='lease_obligor_subsidiary_and_parent_guarantee',stage='signed',vehicle_level=True),
        dict(candidate_index=4,quote='CoreWeave is obligated to provide a letter of credit in the amount of $50 million to secure obligations under the ELN-02 Parent Lease within 30 days of March 30, 2026.',
            counterparty='CoreWeave',counterparty_evidence='named',model_quantity='lease_letter_of_credit_requirement',
            stage='signed',amount_nature='contractual_credit_support',amount_qualifier='exact',measurement_basis='required_letter_of_credit_not_proven_issued')
    ])
    submit('96070be0dd0f',[
        dict(quote='Subsequent to June 30, 2026, the Company entered into a long-term datacenter lease agreement with Anthropic to support its HPC operations at the Justified Data Campus (see Note 18).',
            counterparty='Anthropic',counterparty_evidence='named',model_quantity='named_customer_future_lease',stage='signed')
    ])
    submit('95234894ed1e',[
        dict(quote='In July 2026, the Company entered into a long-term datacenter lease agreement (the “Anthropic HPC Lease”) with Anthropic PBC (“Anthropic”) for specified datacenter infrastructure at the Justified Data Campus to support Anthropic’s HPC operations.',
            counterparty='Anthropic PBC',counterparty_evidence='named',model_quantity='named_customer_future_lease',stage='signed'),
        dict(quote='The Anthropic HPC Lease had not commenced as of the date these condensed consolidated financial statements were issued.',
            counterparty='Anthropic PBC',counterparty_evidence='named',model_quantity='named_customer_future_lease_uncommenced',stage='signed')
    ])
    submit('b756995bee13',[
        dict(quote='a private philanthropic organization focused on funding and participating in social, health, environmental, and sustainability programs.',
            abstained=True,abstention_reason='False lexical nomination: philanthropic is not the legal name Anthropic. No target financing relationship in this natural note.')
    ])
    submit('76bdaac072b0',[
        dict(candidate_index=8,quote='the Company estimates that it will contribute an additional $5,410 and $13,671 to CoreWeave CTP-02 JV and CoreWeave CTP-03 JV, respectively, to fund the future commitments to complete the construction of the build-to-suit assets.',
            counterparty='CoreWeave CTP-02 JV',counterparty_evidence='named',model_quantity='vehicle_construction_remaining_contribution',
            stage='signed',amount_nature='estimate',amount_qualifier='approximately',measurement_basis='estimated_investor_contribution',vehicle_level=True),
        dict(candidate_index=9,quote='the Company estimates that it will contribute an additional $5,410 and $13,671 to CoreWeave CTP-02 JV and CoreWeave CTP-03 JV, respectively, to fund the future commitments to complete the construction of the build-to-suit assets.',
            counterparty='CoreWeave CTP-03 JV',counterparty_evidence='named',model_quantity='vehicle_construction_remaining_contribution',
            stage='signed',amount_nature='estimate',amount_qualifier='approximately',measurement_basis='estimated_investor_contribution',vehicle_level=True)
    ])
    submit('9ef31b315bbd',[
        dict(candidate_index=98,quote='CoreWeave JVs (4) | | | 14.0 | | % | | | | 14.3 | | % | | | | 32,617 | | | | | | 8,820 | |',
            counterparty='CoreWeave',counterparty_evidence='named',model_quantity='indirect_property_investment_carrying_amount',
            stage='recognized',amount_nature='stock',amount_qualifier='exact',measurement_basis='ASC825_FVO_unconsolidated_JV_position',vehicle_level=True),
        dict(quote='CoreWeave CTP-02 JV was formed to facilitate the investment of BOREC Spider Member LLC and AREP Chirisa CTP2 JV LLC to fund the development of a single-story data center leased to CoreWeave, Inc. in a build-to-suit arrangement.',
            counterparty='CoreWeave, Inc.',counterparty_evidence='named',model_quantity='property_vehicle_tenant_relationship',stage='signed',vehicle_level=True)
    ])
