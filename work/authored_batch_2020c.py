from work.authored_helpers import *
k='e19f90ad8a908bf20937cdac74107b29e60f071bad2bcdd415bbab2e389690b2'
rows=repeat_chosen_rows('7d75dfa0f2a8b53d33d80fe1b4f7a395c97bc518ec44987d77c5119182de6cc8',['consolidation_scope','intercompany_elimination','customer_financing_program_policy','server_network_life_extension_not_F7','life_change_existing_cohort_basis','credit_loss_standard_adopted'])
def t(fid,q,qty,**fields):rows.append(authored_tagged(k,fid,q,model_quantity=qty,**fields))
t('9272f44c052707e51b418e8ffb5f49feddc32bf8425e9f0b5230334953b3e738','an increase in operating income of $927 million','life_change_operating_income_effect',amount_nature='existing_June2020_cohort_effect_not_cash')
t('b0dbf25395fdae954a856c087de97a797f7d4c859fd3832bf5a7cffdd61ba1bd','net income of $763 million','life_change_net_income_effect',amount_nature='after_tax_existing_June2020_cohort_effect_not_cash')
q='As of September 30, 2020 and June 30, 2020, other receivables due from suppliers were $1.1 billion and $442 million, respectively,'
for fid in ['e0ea15043934205f35ea07e25b288c0f2b14dd21860768f17eb21af9a10cc021','58fec51c3de6a639a510a5c1d05137594f1c3ecb87b387ad3ad0edb4b6f7470a']:t(fid,q,'supplier_other_receivables_stock',stage='recognized',counterparty_evidence='anonymous',amount_nature='supplier_stock_not_customer_financing_or_cash_flow')
q='As of both September 30, 2020 and June 30, 2020, long-term accounts receivable, net of allowance for doubtful accounts was $2.7 billion'
for fid in ['a24df6159f01812330584b21ce3d106e067892491e65244475cb4b82ba8bf8a8','626dd89da21c082495459338571d8d591921653a3c2848fdf903069e6aa054a3']:t(fid,q,'long_term_trade_receivables_net',stage='recognized',counterparty_evidence='anonymous',amount_nature='stock_not_new_cash',flag_unknown_reason='customer_allocation_unknown_not_OpenAI')
q='As of September 30, 2020 and June 30, 2020, financing receivables, net were $4.8 billion and $5.2 billion, respectively, for short-term and long-term financing receivables,'
for fid in ['e6a9df3a2090703b3f0ec00ef92ecf94efb3f0364bbd1d1a2fba1993f9329e12','11ba7f703ab2b1a7f4dc5462ebfaf5deaadb61a4b450b69ccb5e04e60ce43551']:t(fid,q,'customer_financing_receivables_net',stage='recognized',counterparty_evidence='anonymous',amount_nature='short_and_long_term_stock_not_new_cash',flag_unknown_reason='customer_allocation_unknown_not_OpenAI')
rows += [abstention('If market, industry, and/or investee conditions deteriorate, we may incur future impairments.','Conditional investment impairment not actual F6. Complete note no substantial doubt or OpenAI commitment. Income-tax standard still under evaluation here; no later assessment or adoption imported.')]
save(k,rows)
k='f208a588226c667714c64208d4e7794842c113cceb753617a27ffaa7d260325e'
save(k,[authored_control(k,'the Chief Executive Officer and Chief Financial Officer have concluded that these disclosure controls and procedures are effective.','disclosure_controls_effective',event_present=True),authored_control(k,'There were no changes in our internal control over financial reporting during the quarter ended September 30, 2020','no_material_ICFR_change_quarter',flag_unknown_reason='quarter_nochange_not_F5_absence')])
