from authored_helpers import save,money as m
periods=[('2018-05-07','2018-08-05'),('2017-05-01','2017-07-30'),('2017-10-30','2018-08-05'),('2016-10-31','2017-07-30')]
rows=[]
header='| | (In millions) | | | | | | | | | | | | | |'
revenue='Total net revenue | | $ | 282 | | | $ | 97 | | | $ | 664 | | | $ | 245 |'
expenses='Total costs and expenses, including inventory purchases | | $ | 25 | | | $ | 28 | | | $ | 92 | | | $ | 93 |'
for n,(start,end) in zip(['282','97','664','245'],periods):
 rows.append(m(header+'\n'+revenue,n,'1000000','director_affiliated_entities',counterparty_evidence='anonymous',period_start=start,period_end=end,receiver='Broadcom',family='commercial',link_type='revenue_recognized',stage='recognized',amount_qualifier='exact',amount_nature='anonymous_related_director_affiliated_entities_net_revenue_not_additive_quarter_and_YTD',model_quantity='related_party_revenue_recognized_total',flag_unknown_reason='individual_customers_and_financing_status_unallocated_related_party_perimeter_changes_unknown'))
for n,(start,end) in zip(['25','28','92','93'],periods):
 rows.append(m(header+'\n'+revenue+'\n'+expenses,n,'1000000','director_affiliated_entities',counterparty_evidence='anonymous',period_start=start,period_end=end,stage='recognized',amount_qualifier='exact',amount_nature='anonymous_related_costs_and_expenses_including_inventory_purchases_not_cash',model_quantity='related_costs_and_expenses_total',flag_unknown_reason='individual_suppliers_unallocated_quarter_and_YTD_not_additive'))
q='| | (In millions) | | | | | |\nTotal receivables | | $ | 79 | | | $ | 31 |\nTotal payables | | $ | 8 | | | $ | 12 |'
for quantity,values in [('related_receivables_total',['79','31']),('related_payables_total',['8','12'])]:
 for n,end in zip(values,['2018-08-05','2017-10-29']):
  rows.append(m(q,n,'1000000','director_affiliated_entities',counterparty_evidence='anonymous',period_end=end,stage='recognized',amount_qualifier='exact',amount_nature='anonymous_related_trade_stock_not_explicit_financing',model_quantity=quantity,flag_unknown_reason='individual_counterparties_terms_and_financing_component_not_disclosed'))
save('d0b27bfdef855efd8c22520779290cb2bdb1bc9cf57f7aa11a6596cb0b99745b',rows)
