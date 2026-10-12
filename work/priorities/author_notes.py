"""Personally selected quotations and inline occurrences for the three priorities.

The program validates selections; it does not discover or author observations.
"""
from pathlib import Path
import json
import duckdb
from secfragility.targeted_priorities import author_record

ROOT = Path('.').resolve()
DB = duckdb.connect()
OUT = []

def note(source, quantity, quote, finding, **kwargs):
    OUT.append(author_record(ROOT, DB, source, quantity, quote, finding, **kwargs))

# The named SOI rows and the exact numerical inline IDs were personally read.
# Native principal tags also occur in the commitment table; column identity,
# not the tag alone, decides whether an amount is funded.
for name, cp, ids, prior in [
    ('helios', 'Galaxy Helios LLC', ['f-310','f-311','f-312','f-2215','f-2216'], ['f-1016','f-1017','f-1018','f-2217','f-2218']),
    ('cw_nest', 'CW Nest Property Owner LLC', ['f-305','f-306','f-307','f-2219','f-2220'], ['f-1011','f-1012','f-1013','f-2221','f-2222']),
    ('ddtl_v', 'Coreweave Financing DDTL V, LLC', ['f-445','f-446','f-447','f-2223','f-2224'], None),
]:
    for period, selected in [('current',ids),('prior',prior)]:
        if selected is None: continue
        for field, inline in zip(['funded_principal','cost','fair_value','total_commitment','unfunded_commitment'],selected):
            note('aci-20260630.htm', f'ares_{name}_{period}_{field}', None,
                 'Holder-side stock at the stated reporting date. SOI principal is funded; commitment-table principal is total commitment, net of paydowns. Cost and fair value are valuation bases, not extra cash advanced.',
                 inline=inline, counterparty=cp,
                 stage='signed' if 'commitment' in field else 'recognized',
                 instrument_key='ARES_'+name, measurement_basis=field)
note('aci-20260630.htm','ares_funded_definition',
     'Principal reflects the funded principal as of June 30, 2026.',
     'Explicit footnote6 resolves the funded-versus-committed ambiguity; preserve the separate note7 unfunded stock.')
note('aci-20260630.htm','ares_nonaccrual_status',
     'As of June 30, 2026 and December 31, 2025, there were no investments on non-accrual status.',
     'Explicit issuer statement for these two dates. No inference of zero future risk or group-wide absence of distress.')
note('aci-20260630.htm','ares_conditional_commitments',
     ('(1) The unfunded debt/delayed draw term loan obligations','Total commitment is net of paydowns for delayed draw term loans.'),
     'Undrawn funding depends on pre-negotiated terms including leverage and borrowing base covenants. It is not cash already received by borrowers.')
for field, inline in [
    ('funded_principal','F_ff7ec004-9e02-4f0f-a140-620ad88e69de'),
    ('cost','F_8e0456ca-b2ee-4b89-ac3c-5357b3a186ca'),
    ('fair_value','F_0ef5af23-0914-4e43-81fb-46db808e69c4'),
    ('unfunded_commitment','F_e8f97915-13d9-43ed-9282-426355145b07'),
]:
    note('ck0001902649-20260630.htm','blackrock_ddtl_v_'+field,None,
         'Fund-specific held amount in USD, not thousands and not total syndicate size. Unfunded balance remains separate. No primary cash origination inferred from a held investment.',
         inline=inline,counterparty='Coreweave Financing DDTL V LLC',
         stage='signed' if field=='unfunded_commitment' else 'recognized',
         instrument_key='BLACKROCK_ddtl_v',measurement_basis=field)
note('ck0001902649-20260630.htm','blackrock_nonaccrual_marker',
     '(G)\nNon-accruing debt investment.',
     'Coreweave row has no G marker; it is not marked non-accruing in this schedule. No explicit borrower-level PIK amount is published on the selected row. Neither absence of a mark nor fair value above cost proves low risk.')

# Vernon identity is named in the filed contract and explicitly incorporated in
# the current 10-K. It is not inferred from capacity or the street address.
note('smci-20240614.htm','vernon_named_sublicensee',
     ('Concurrent with the execution of the MCSA and the Service Order,','directly to the Supplier.'),
     'Lambda, Inc. is the named sublicensee. Original 2024 contract; do not infer latest outstanding cash obligations from its signature.',
     counterparty='Lambda, Inc.',stage='signed',instrument_key='SMCI_VERNON')
note('smci-20240614.htm','vernon_original_estimate',
     'The Company’s aggregate financial obligation for the term of the Service Order is estimated to be $600.0 million, which amount includes the monthly recurring charges, power charges and other anticipated costs.',
     'Original all-in ten-year estimate including power and other anticipated costs. Not current discounted lease debt and not added to USD290.2m lease liability.',
     amount='600000000',amount_qualifier='approximately',stage='signed',instrument_key='SMCI_VERNON')
note('smci-20240614.htm','vernon_acceleration_reimbursement',
     ('The payments owed by the Company under the Service Order','pursuant to the terms of the Sublicense.'),
     'SMCI has contractual reimbursement recourse to Lambda after acceleration by the supplier. It does not release the primary obligation or establish recoverability.',
     counterparty='Lambda, Inc.',counterparty_evidence='derivable',counterparty_method='explicit_cross_reference',
     stage='signed',instrument_key='SMCI_VERNON',recourse='reimbursement_from_sublicensee;SMCI_remains_primary_obligor')
note('sublicense-supermicroxla.htm','vernon_rent_no_setoff',
     'All Rent shall be paid without set off, abatement or deduction.',
     'Sublicense section3.2: contractual protection of collections, subject to the complete contract; not an accounting right to offset SMCI debt.',stage='signed',instrument_key='SMCI_VERNON')
note('sublicense-supermicroxla.htm','vernon_assignment_control',
     'Sublicensee shall not, under any circumstances, assign this Sublicense, sublicense the Premises or permit the use of the Premises by any person other than Sublicensee and its employees without obtaining Sublicensor’s prior written consent which consent may be withheld in Sublicensor’s sole and absolute discretion.',
     'Section11 requires prior consent for assignment. No undocumented successor identity assumed.',stage='signed',instrument_key='SMCI_VERNON')
note('pdcvernon-supermicrolamb.htm','vernon_supplier_security',
     '8. Security a. Security Deposit: None b. Letter of Credit: None. c. Guaranty: None',
     'Service order section8 describes security owed to the supplier under that order. It is not a blanket claim that Lambda has no collateral under every agreement.',stage='signed',instrument_key='SMCI_VERNON')
note('smci-20260630.htm','vernon_current_cross_reference',
     ('Sublicense, dated June 14, 2024, by and between Super Micro Computer, Inc. and Lambda, Inc.', 'on June 21, 2024)'),
     'Current 10-K exhibit10.26 explicitly incorporates the named 2024 sublicense. Documentary identity bridge to note10, reached from note4.',
     counterparty='Lambda, Inc.',tier='C',assurance_level='not_applicable',location='filed_exhibit_index',instrument_key='SMCI_VERNON')
note('smci-20260630.htm','vernon_investment_identity_resolved',
     ('Our non-marketable equity securities include $92.5 million','Please refer to Note 10, “Leases” for further discussion.'),
     'The same filing names Lambda in exhibit10.26 and explicitly connects the investee/sub-licensee to note10. USD92.5m reported invested amount is now attributable by contractual parties and explicit cross-reference. This is an enrichment of the existing observation, not another investment or a new payment.',
     amount='92500000',counterparty='Lambda, Inc.',counterparty_evidence='derivable',counterparty_method='explicit_cross_reference',
     family='financing',measurement_basis='reported_invested_amount_in_measurement_alternative_portfolio',instrument_key='SMCI_VERNON')

# Two filed guarantees: section12 has a letter of credit in ELN02 and is reserved
# in ELN03. A general statement for both would be misleading.
for num in (1,2):
    source=f'apld-springing-{num}.htm'
    note(source,f'apld_eln0{num+1}_springing_scope',
         ('Guarantor / hereby agrees that upon,','the “Obligations”).'),
         'CoreWeave parent guarantee activates only upon a Springing Event and then covers rent, accelerated sums and performance. Lease guarantee, not an unconditional present guarantee of all equipment debt.',
         counterparty=f'APLD ELN-0{num+1} LLC',counterparty_evidence='derivable',counterparty_method='contract_parties',family='credit_support',link_type='guarantee',
         stage='signed',instrument_key=f'CRWV_APLD_ELN0{num+1}',conditionality='conditional',trigger_description='Springing / Events (defined below)',trigger_occurred='unknown')
    note(source,f'apld_eln0{num+1}_rating_redacted',
         'the / receipt by the Equipment Financing of a debt rating that is [***];',
         'The rating trigger threshold is redacted; do not reconstruct it or claim it occurred.',stage='signed',instrument_key=f'CRWV_APLD_ELN0{num+1}')
    note(source,f'apld_eln0{num+1}_customer_contract_trigger',
         ('the / occurrence of (a) the expiration or earlier termination','payments under the Colocation Agreement;'),
         'Colocation contract ending or materially adverse amendment/default can trigger parent lease recourse. Colocation customer remains unnamed in these clauses.',
         stage='signed',instrument_key=f'CRWV_APLD_ELN0{num+1}',trigger_occurred='unknown')
    note(source,f'apld_eln0{num+1}_refinance_trigger',
         ('the full refinancing','material and adverse to the interests of the Landlord;'),
         'Full refinancing (excluding repricing), repayment/satisfaction, maturity or full termination of equipment financing also triggers the guarantee: not only borrower distress.',stage='signed',instrument_key=f'CRWV_APLD_ELN0{num+1}',trigger_occurred='unknown')
note('apld-springing-1.htm','apld_eln02_letter_of_credit',
     ('12.\nLEASE L/C.','Guarantor shall maintain the Lease L/C in the Required L/C Amount\nat all times during the Term.'),
     'Building2 requires a lease letter of credit from the guarantor; required amount/deadline are redacted. It is a requirement, not evidence of actual issuance or a draw.',stage='signed',instrument_key='CRWV_APLD_ELN02')
note('apld-springing-2.htm','apld_eln03_no_section12_lc',
     '12.\n[Reserved].',
     'The parallel Building3 guarantee reserves section12; do not copy the Building2 letter-of-credit requirement to Building3.',stage='signed',instrument_key='CRWV_APLD_ELN03')
note('apld-20260531.htm','apld_bridge_refinanced',
     'On June 16, 2026, APLD ComputeCo 3 LLC refinanced the Bridge Facility with the closing of a $1.59 billion offering (the “2031 7.000% Notes Offering”) of 7.000% senior secured notes due 2031 (the “2031 7.000% Notes”) at an issue price of 100.000% of par.',
     'Confirmed post-May31 closing: bridge is refinanced June16. Do not leave USD300m bridge plus new USD1.59bn both outstanding at the June16 event date.',
     amount='1590000000',event_date='2026-06-16',stage='drawn_or_paid',instrument_key='APLD_COMPUTECO3_2031',tier='C',assurance_level='unaudited',location='subsequent_events')
note('apld-20260531.htm','apld_escrow_release',
     'On June 18, 2026, APLD ComputeCo 2 satisfied the escrow release condition',
     'Release certificate delivered June18 directs escrow funds to ComputeCo2 under specified agreements. This is not unrestricted parent cash and does not retrospectively change May31 restricted cash.',
     event_date='2026-06-18',stage='settled',instrument_key='APLD_COMPUTECO2_2031',tier='C',assurance_level='unaudited',location='subsequent_events')
note('dell-20260731.htm','dfs_us_facility_capacity_dates',
     ('The asset-based financing facility consists of two tranches,','was $4.6 billion.'),
     'US facility tranche dates July7 2027/2028; USD4.6bn capacity, not unconditionally free unused liquidity.',
     amount='4600000000',stage='signed',instrument_key='DFS_US_ABF')
note('dell-20260731.htm','dfs_europe_facility_capacity_date',
     'This facility is effective through December 22, 2026 and had a total debt capacity of $922 million as of July 31, 2026.',
     'European securitization facility date and capacity. Near-term renewal issue, without proof of nonrenewal. Capacity is not current drawn debt.',
     amount='922000000',stage='signed',instrument_key='DFS_EU_SECURITIZATION')
note('dell-20260731.htm','dfs_europe_structural_restrictions',
     ('The securitization facility contains standard structural features','As of July 31, 2026, these criteria were met.'),
     'Same performance-driven funding-stop and delayed excess cash mechanism as the US facility; numerical trigger thresholds unpublished. Confirmation of existing mechanism, not a new default.',stage='signed',instrument_key='DFS_EU_SECURITIZATION',trigger_occurred='no')

(ROOT/'work/priorities/authored_observations.json').write_text(json.dumps(OUT,default=str,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'personally_authored_observations':len(OUT)}))
