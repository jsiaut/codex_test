"""Contract observations authored after reading complete exhibits and natural clauses."""
from pathlib import Path
import json
from secfragility.reader import block_for,store
root=Path(__file__).resolve().parents[1]
q=json.loads((root/'work/deepening_contract_queue.json').read_text())
def submit(prefix,authored):
    k=next(r['content_key'] for r in q if r['content_key'].startswith(prefix))
    if (root/'work/observations'/(k+'.jsonl')).exists():return
    b=block_for(root,k)
    for r in authored:
        if r['quote'] not in b['text']:raise ValueError('Authored quote not present: '+prefix)
    result=store(root,k,authored);print(json.dumps(dict(key=prefix,**result),default=str),flush=True)
    if result.get('rejected'):raise ValueError('Rejected authored contract observation')

if __name__=='__main__':
    cp=dict(counterparty='NVIDIA CORPORATION',counterparty_evidence='derivable',counterparty_method='contract_parties')
    submit('029e8673b992',[
        dict(cp,quote='Any amounts due under this Agreement shall not be withheld or offset by / Customer against amounts due to Customer for any reason.',
            model_quantity='contract_no_customer_setoff',stage='signed'),
        dict(cp,quote='If this Agreement or an Order Form is terminated by either party in accordance with the “Termination” section above, Customer is released of payment obligations for / Services that would have been provided after the effective date of termination.',
            model_quantity='contract_post_termination_payment_release',stage='signed'),
        dict(cp,quote='In the event of any conflict or inconsistency among the following documents, the order of / precedence shall be: (i) the applicable Order Form, (ii) any exhibit, schedule or addendum to this Agreement (including to the extent incorporated by reference), (iii) the body of this Agreement, and (iv) the Documentation.',
            model_quantity='contract_order_form_precedence',stage='signed'),
        dict(cp,quote='CoreWeave must not, at any point in time, dedicate more than [*] of available customer capacity to NVIDIA',
            model_quantity='contract_capacity_allocation_cap_redacted',stage='signed')
    ])
    cp=dict(counterparty='OpenAI OpCo, LLC',counterparty_evidence='derivable',counterparty_method='contract_parties')
    submit('d5914126788f',[
        dict(counterparty='OpenAI OpCo, LLC',counterparty_evidence='named',
            quote='Cerebras Systems Inc., a Delaware corporation (the “Borrower”), and OpenAI OpCo, LLC, a Delaware limited liability company',
            model_quantity='contract_party_legal_identity',stage='signed'),
        dict(cp,quote='the Borrower hereby unconditionally promises to pay to the Holder the principal amount of $1,004,571,259, together with any accrued but unpaid interest, on December 31, 2032',
            model_quantity='customer_loan_contract_principal',stage='signed',amount='1004571259',unit='USD',currency='USD',
            amount_origin='narrative_only',amount_qualifier='exact',amount_nature='contract_principal',event_date='2026-01-05',
            instrument_key='CBRS_OpenAI_WorkingCapitalLoan_2026-01-05'),
        dict(cp,quote='The Borrower may satisfy all or any of portion of its repayment obligations hereof either (i) in cash or (ii) through the delivery of Services to the Holder under the MRA in accordance with Exhibit B §2 of the MRA and Section 7.h.ii of the MRA.',
            model_quantity='contract_loan_service_repayment',stage='signed'),
        dict(cp,quote='Notwithstanding anything to the contrary, no more than $[***] of principal amount of this Note may be repaid through delivery of Services or the assignment or transfer to the Holder of applicable assets [***].',
            model_quantity='contract_noncash_repayment_cap_redacted',stage='signed'),
        dict(cp,quote='the outstanding principal balance under this Note shall be amortized in [***] equal monthly installments over a [***] period, commencing on [***]',
            model_quantity='contract_loan_amortization_redacted',stage='signed'),
        dict(cp,quote='Upon the occurrence of the (i) termination of the MRA for any reason other than the Holder’s material uncured breach under Section 7.b thereof or (ii) [***], the outstanding principal amount of this Note and all accrued but unpaid interest thereon shall automatically and immediately become due and payable in full',
            model_quantity='contract_customer_loan_acceleration',stage='signed',conditionality='conditional',
            trigger_description='termination of the MRA for any reason other than the Holder’s material uncured breach under Section 7.b thereof',trigger_occurred='unknown')
    ])
    submit('5e012e564321',[
        dict(cp,quote='Subject to the terms and conditions of this Agreement, Cerebras shall make available to OpenAI, and OpenAI commits to purchase the following Capacity, in accordance with the schedule in Exhibit A',
            model_quantity='contract_committed_compute_capacity',stage='signed'),
        dict(cp,quote='OpenAI will have the option to procure additional Capacity',model_quantity='contract_optional_additional_capacity',stage='signed',conditionality='optional'),
        dict(cp,quote='Any amounts remitted to OpenAI from the Lockbox Account and the amount paid from the Lockbox Account for any assets or rights assigned under the foregoing clause (B) will reduce, dollar-for-dollar, the amounts payable under clause (A).',
            model_quantity='contract_loan_assets_cash_not_additive',stage='signed'),
        dict(cp,quote='Exhibit B\nFEES AND PAYMENT\n[****]',model_quantity='contract_fees_and_payment_redacted',stage='signed')
    ])
    # Party definitions and explicit commercial inducement occur in one continuous
    # opening block. The long quotation retains that cross-reference exactly.
    b=block_for(root,next(r['content_key'] for r in q if r['content_key'].startswith('b3290d22f2cc')))
    start=b['text'].index('Company: Cerebras Systems Inc.');end=b['text'].index('Section 1. EXERCISE.')
    opening=b['text'][start:end].rstrip()
    submit('b3290d22f2cc',[
        dict(cp,quote=opening,model_quantity='customer_warrant_commercial_link',stage='signed',
            family='customer_consideration',link_type='equity_or_warrants_to_customer',
            payer='Cerebras Systems Inc.',receiver='OpenAI OpCo, LLC',linkage_class='L2',linkage_quote=opening,
            event_date='2025-12-24',instrument_key='CBRS_OpenAI_Warrant_2025-12-24'),
        dict(cp,quote='Deposit of the Working Capital Loan into the Lockbox | | | — | | | [***] | | | 4,459,337 | | | [***] | |',
            model_quantity='customer_warrant_funding_trigger',stage='signed',conditionality='conditional',
            trigger_description='Deposit of the Working Capital Loan into the Lockbox',trigger_occurred='unknown'),
        dict(cp,quote='treat this Warrant as entered into pursuant to the terms of the Commercial Agreement as giving rise to a sales discount or allowance in respect of the provision of services under the Commercial Agreement.',
            model_quantity='customer_warrant_tax_intent_only',stage='signed')
    ])
    submit('950e63e45218',[
        dict(quote='The Warrantholder and the Company agree that they intend, for U.S. federal and applicable state and local income tax purposes, to:',
            abstained=True,abstention_reason='Typeset paragraph continues on the next page; complete natural §15 is recorded separately. This fragment alone does not establish the tax clause.')
    ])
    submit('3b0e325849d0',[
        dict(quote='treat this Warrant as giving rise to a sales discount, allowance, or rebate in connection with the purchase or lease of the applicable products described in Exhibit E.',
            counterparty='Meta Platforms, Inc.',counterparty_evidence='derivable',counterparty_method='contract_parties',
            model_quantity='customer_warrant_tax_intent_only',stage='signed',
            issuer_treatment='Stated income-tax intent only; not evidence of current US GAAP recognition.')
    ])
    submit('a9b24054e76e',[
        dict(quote='EXHIBIT E\nVESTING SCHEDULE\n[***]',model_quantity='contract_warrant_vesting_schedule_redacted',stage='signed')
    ])
    submit('a171384cc60d',[
        dict(quote='EXHIBIT F\nEXERCISE CONDITIONS SCHEDULE\n[***]',model_quantity='contract_warrant_exercise_schedule_redacted',stage='signed')
    ])
