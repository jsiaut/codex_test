from work.authored_helpers import *
k='64c3a7d79d29cc6e5c0d20672221cdc839923edc845db36e8c2550857248fe59'
rows=repeat_chosen_rows('445b57b3da75194aba04b3fbb3a5595952a34e0984a3e995b68b8052e59a9a34',['consolidation_scope','intercompany_elimination','customer_financing_program_policy','income_tax_standard_adopted'])
def t(fid,q,qty,**fields):rows.append(authored_tagged(k,fid,q,model_quantity=qty,**fields))
q='As of September 30, 2021 and June 30, 2021, other receivables due from suppliers were $854 million and $965 million, respectively,'
for fid in ['f0d9c71f1ab3c18fd438b9ea0ccde515fa17153a6907a95bb0b1499389806d28','b9ed16b79549529128fdeaa57e9a1740276c19e1a3abae26c820adafbc2df362']:t(fid,q,'supplier_other_receivables_stock',stage='recognized',counterparty_evidence='anonymous',amount_nature='supplier_stock_not_customer_financing_or_cash_flow')
q='As of both September 30, 2021 and June 30, 2021, long-term accounts receivable, net of allowance for doubtful accounts, was $3.4 billion'
for fid in ['193793cdd698336f5f4977e2ac089b42376fc4a2f1e2525f6f3e9a511720c33d','6a1c4ee533796ac3e5703f4f71865fd9e6950da6e084f6a7b87a33c3ee2d6486']:t(fid,q,'long_term_trade_receivables_net',stage='recognized',counterparty_evidence='anonymous',amount_nature='stock_not_new_cash',flag_unknown_reason='customer_allocation_unknown_not_OpenAI')
q='As of September 30, 2021 and June 30, 2021, our financing receivables, net were $3.8 billion and $4.4 billion, respectively, for short-term and long-term financing receivables,'
for fid in ['ec1edade86ffe535d8213e80c128ebc071c08e5cb6c9f58a8ec77a72a9fbd121','997efbf3a8d116d8b582682cd0d65bce137f923300dcb7a38598b1647e8b8231']:t(fid,q,'customer_financing_receivables_net',stage='recognized',counterparty_evidence='anonymous',amount_nature='short_and_long_term_stock_not_new_cash',flag_unknown_reason='customer_allocation_unknown_not_OpenAI')
rows.append(abstention('If market, industry, and/or investee conditions deteriorate, we may incur future impairments.','Conditional investment impairment not actual F6. Complete note no substantial doubt, OpenAI commitment or actual life assessment; no later July2022 assessment imported.'))
save(k,rows)
k='3fe45cb0d231b9128bf8f93fe9ee9f4b204dd07681e62e8230c3b138bfca923e'
save(k,[authored_control(k,'the Chief Executive Officer and Chief Financial Officer have concluded that these disclosure controls and procedures are effective.','disclosure_controls_effective',event_present=True),authored_control(k,'There were no changes in our internal control over financial reporting during the quarter ended September 30, 2021','no_material_ICFR_change_quarter',flag_unknown_reason='quarter_nochange_not_F5_absence')])
