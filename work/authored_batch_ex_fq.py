from work.authored_helpers import *

# The header and all four body packets were personally read. These selected
# clauses match the later, independently read DDTL V-V instrument; names and
# dates below are those of this original DDTL V instrument.
rows = repeat_chosen_rows('027e226503f3796601816a2268d3aac068d4d6beb77ae71f2ff3d288b19d8236', [
    'DDTL5_5_parent_full_payment_guarantee',
    'DDTL5_5_Holdco_owns_entire_Borrower',
    'DDTL5_5_Holdco_borrower_equity_and_debt_pledge',
    'DDTL5_5_original_minimum_contracted_revenue_covenant_threshold',
    'DDTL5_5_original_parent_financial_covenant_and_acquisition_stepup',
    'DDTL5_5_equity_cure_permission',
    'DDTL5_5_conditional_swap_keepwell',
])
for row in rows:
    row['model_quantity'] = row['model_quantity'].replace('DDTL5_5_', 'DDTL5_')
    if row.get('event_date'):
        row['event_date'] = '2026-05-15'
    if row.get('counterparty'):
        row['counterparty'] = row['counterparty'].replace('DDTL V-V', 'DDTL V')
    if row.get('flag_unknown_reason'):
        row['flag_unknown_reason'] = row['flag_unknown_reason'].replace('currentAug7', 'currentMay15').replace('2.6b_facility_same_underlying_not_add_', 'same_underlying_facility_not_add_')
rows.append(abstention(
    'IN WITNESS WHEREOF, the Guarantor, Pledgor and the Collateral Agent have executed this Agreement',
    'Header and all four body packets personally read. May15 original executed full payment/performance parent guarantee, fraudulent-transfer legal cap unquantified; no actual call, default, cure, draw or foreclosure. Current DE Holdco owns100% DE Borrower under5.6c; Parent100%Holdco change-of-control definition alone not actual consolidation evidence. Collateral is Borrower equity/debt/proceeds, not all Parent assets. Covenants minimum1bn weighted projected contracted revenue and6x leverage, conditional7x acquisition stepup; no current recognized revenue or actual ratio inferred. Swap keepwell10m total-assets eligibility threshold not guarantee cap. Release on PaymentInFull not actual termination. Exhibits A/B/C absent, no invented private schedules or amendments; original rights and permissions not F4 event.'
))
save('801806a08b7a8aac1f2345bcb041b5a6089d9ac9483f54a165fb209eb79fdc6c', rows)
