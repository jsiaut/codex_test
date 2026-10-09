from authored_helpers import save,money as m,repeat_chosen_rows
cp='GLOBALFOUNDRIES Inc.'
rows=[]
q='The Company’s total purchases from GF related to wafer manufacturing, research and development activities and other for the quarters ended June 30, 2018 and July 1, 2017 were $383 million and $266 million, respectively.'
for n,start,end in [('383','2018-04-01','2018-06-30'),('266','2017-04-02','2017-07-01')]:
 rows.append(m(q,n,'1000000',cp,period_start=start,period_end=end,payer='AMD',receiver=cp,family='commercial',link_type='purchase',stage='delivered',amount_qualifier='exact',amount_nature='related_supplier_purchases_including_other_foundry_volume_fees_not_explicit_cash_or_supplier_GAAP_revenue',model_quantity='related_supplier_purchases',instrument_key='AMD_GF_WSA'))
q='The Company’s total purchases from GF related to wafer manufacturing, research and development activities and other for the six months ended June 30, 2018 and July 1, 2017 were $781 million and $442 million, respectively.'
for n,start,end in [('781','2017-12-31','2018-06-30'),('442','2017-01-01','2017-07-01')]:
 rows.append(m(q,n,'1000000',cp,period_start=start,period_end=end,payer='AMD',receiver=cp,family='commercial',link_type='purchase',stage='delivered',amount_qualifier='exact',amount_nature='related_supplier_YTD_purchases_not_additive_with_quarter_components_not_explicit_cash',model_quantity='related_supplier_purchases',instrument_key='AMD_GF_WSA'))
for n,end in [('8','2018-06-30'),('27','2017-12-30')]:
 rows.append(m('As of June 30, 2018 and December 30, 2017, the amount of prepayment and other receivables related to GF was $8 million and $27 million, respectively, included in Prepayment and other receivables—related parties on the Company’s condensed consolidated balance sheets.',n,'1000000',cp,period_end=end,stage='recognized',amount_qualifier='exact',amount_nature='combined_prepayment_and_other_receivables_asset_stock_not_pure_advance_or_financing_component',model_quantity='related_prepayment_and_other_receivables',instrument_key='AMD_GF_WSA',flag_unknown_reason='prepayment_and_receivables_not_split_maturity_and_financing_component_not_disclosed'))
for n,end in [('269','2018-06-30'),('241','2017-12-30')]:
 rows.append(m('As of June 30, 2018 and December 30, 2017, the amount of payable to GF was $269 million and $241 million, respectively, included in Payables to related parties on the Company’s condensed consolidated balance sheets.',n,'1000000',cp,period_end=end,stage='recognized',amount_qualifier='exact',amount_nature='related_supplier_payable_stock_not_explicit_borrowing_or_financing_program',model_quantity='related_supplier_payables',instrument_key='AMD_GF_WSA',flag_unknown_reason='payment_terms_and_financing_component_not_disclosed'))
# These six clauses were read again, word for word, in the current full block.
rows += repeat_chosen_rows('ee17f90e2625fbf498b28afe12b42e978262893aabbeff1eda72bbea8e339f62',[
 'supplier_waiver_rights_cash_payments','other_foundry_volume_fee_commitment',
 'conditional_wafer_purchase_shortfall_payment','supplier_rights_warrant_exercise_terms',
 'entity_identity_and_control_evidence','economic_group_control_evidence'])
rows.append(dict(quote='As of June 30, 2018, the Company expects to meet its 2018 wafer purchase target.',counterparty=cp,counterparty_evidence='named',instrument_key='AMD_GF_WSA_sixth_amendment_2016',model_quantity='wafer_purchase_target_expectation',flag_unknown_reason='expectation_does_not_establish_trigger_absence_for_completed_2018'))
save('a8904b962beaeb7c1ce5246d0388f9d7d6818b8996b8f080b26c2233dbdadea0',rows)
