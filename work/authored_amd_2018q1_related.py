from authored_helpers import save,money as m,repeat_chosen_rows
cp='GLOBALFOUNDRIES Inc.'
rows=[]
q='The Company’s total purchases from GF related to wafer manufacturing, research and development activities and other for the quarters ended March 31, 2018 and April 1, 2017 were $398 million and $176 million, respectively.'
for n,start,end in [('398','2017-12-31','2018-03-31'),('176','2017-01-01','2017-04-01')]:
 rows.append(m(q,n,'1000000',cp,period_start=start,period_end=end,payer='AMD',receiver=cp,family='commercial',link_type='purchase',stage='delivered',amount_qualifier='exact',amount_nature='related_supplier_purchases_including_other_foundry_volume_fees_not_explicit_cash_or_supplier_GAAP_revenue',model_quantity='related_supplier_purchases',instrument_key='AMD_GF_WSA'))
for n,end in [('10','2018-03-31'),('27','2017-12-30')]:
 rows.append(m('As of March 31, 2018 and December 30, 2017, the amount of prepayment and other receivables related to GF was $10 million and $27 million, respectively, included in Prepayment and other receivables - related parties on the Company’s condensed consolidated balance sheets.',n,'1000000',cp,period_end=end,stage='recognized',amount_qualifier='exact',amount_nature='combined_prepayment_and_other_receivables_asset_stock_not_pure_advance_or_financing_component',model_quantity='related_prepayment_and_other_receivables',instrument_key='AMD_GF_WSA',flag_unknown_reason='prepayment_and_receivables_not_split_maturity_and_financing_component_not_disclosed'))
for n,end in [('197','2018-03-31'),('241','2017-12-30')]:
 rows.append(m('As of March 31, 2018 and December 30, 2017, the amount of payable to GF was $197 million and $241 million, respectively, included in Payables to related parties on the Company’s condensed consolidated balance sheets.',n,'1000000',cp,period_end=end,stage='recognized',amount_qualifier='exact',amount_nature='related_supplier_payable_stock_not_explicit_borrowing_or_financing_program',model_quantity='related_supplier_payables',instrument_key='AMD_GF_WSA',flag_unknown_reason='payment_terms_and_financing_component_not_disclosed'))
# Each selected unchanged clause was read in this current block before reuse.
rows += repeat_chosen_rows('ee17f90e2625fbf498b28afe12b42e978262893aabbeff1eda72bbea8e339f62',[
 'supplier_waiver_rights_cash_payments','other_foundry_volume_fee_commitment',
 'conditional_wafer_purchase_shortfall_payment','supplier_rights_warrant_exercise_terms',
 'entity_identity_and_control_evidence','economic_group_control_evidence'])
rows.append(dict(quote='As of March 31, 2018, the Company expects to meet its 2018 wafer purchase target.',counterparty=cp,counterparty_evidence='named',instrument_key='AMD_GF_WSA_sixth_amendment_2016',model_quantity='wafer_purchase_target_expectation',flag_unknown_reason='expectation_does_not_establish_trigger_absence_for_completed_2018'))
save('78ccc35701c3142e3908ea5e921933f1757f5d2042231fd10a3030fe09e4996a',rows)
