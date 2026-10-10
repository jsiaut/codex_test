from extension_authoring import ROOT,tagged
from secfragility.reader import store
k='2370478e74e884d06cb5d0e66993e939e4655b5df8bd136595d394239f5109b1'
row=tagged(k,0,"NVIDIA Corporation invested $2 billion in the Company's Class A common stock",counterparty='NVIDIA Corporation',counterparty_evidence='named',payer='NVIDIA Corporation',receiver='CRWV',source_perspective='reporting_entity',family='financing',link_type='equity_primary',model_quantity='primary_equity_cash_received',stage='drawn_or_paid',event_type='funding',instrument_key='NVDA_CRWV_Jan2026_primary_equity',amount_nature='actual_gross_primary_equity_investment',issuer_treatment='same_January2026_NVIDIA_primary_investment_repeated_in_subsequent_notes_not_incremental_cash',flag_unknown_reason='actual_day_not_disclosed_in_this_note_Jan31_is_context_month_end')
print(store(ROOT,k,[row],schema_retry=True))
