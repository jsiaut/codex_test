"""Manually authored after all 84 candidates and complete Note 1 were read."""
from work.authored_helpers import *

k='85a78e933c3d76e312a926fee4799a615a2b21da059ff86756d56ef16836d356'
rows=repeat_chosen_rows('8bf9fec8af82638c58833ada3890a507d8c3d1dcd35ec7bd03494577582bd757',[
    'server_network_life_extension_not_F7',
    'customer_long_term_payment_contract_nonrecourse_sale_policy'])
q='this change in accounting estimate decreased our total operating expenses by $181 million and increased our net income by $136 million,'
q9='decreased our total operating expenses by $567 million and increased our net income by $442 million,'
for fid,quote,quantity,nature in [
('a1c957c9ff33f64cf21e576b0593c59831f218c40cf7d958b407cd228f2740c0',q,'depreciation_life_change_expense_effect','negative_expense_change_positive_pretax_effect_invert_sign'),
('5e6e0e3c57ac5c39c87ebb8df7e0788f65f69458e58d2a7239b4c63c0addca9c',q,'depreciation_life_change_net_income_effect','positive_after_tax_effect_not_pretax_bridge'),
('b7576c6b9364676489ffa6cfc902a75a22da9fd74535e589a30563e29ad115d5',q9,'depreciation_life_change_expense_effect','negative_expense_change_positive_pretax_effect_invert_sign'),
('55d11c11efecb99f92cf5c1b608ed65a732578f1ba2bf30545454e52efe7cbca',q9,'depreciation_life_change_net_income_effect','positive_after_tax_effect_not_pretax_bridge')]:
    rows.append(authored_tagged(k,fid,quote,model_quantity=quantity,amount_nature=nature))
q='The revenues recognized during the nine months ended February 28, 2025 and February 29, 2024 that were included in the opening deferred revenues balances as of May 31, 2024 and 2023 were approximately $8.6 billion and $8.5 billion, respectively.'
for fid in ['02e8e0169bdf28d26acd5724cc09c6e799167180f647a5af4e9763bf2c0325b6','a7753793ddedd1a231a495a72bdfaa4534cd33447ce444ed9cf10fb18b99901c']:
    rows.append(authored_tagged(k,fid,q,model_quantity='revenue_recognized_from_opening_deferred_revenue',stage='recognized',amount_nature='opening_contract_liability_recognition_not_cash',amount_qualifier='approximately'))
q='were $130.2 billion as of February 28, 2025, of which we expect to recognize approximately 31% as revenues over the next twelve months, 40% over the subsequent month 13 to month 36, 25% over the subsequent month 37 to month 60 and the remainder thereafter.'
for fid,quantity in [
('25ba037ff3ee4822208127cd4cc821aa0ee9d7fc656bd86854c7d1f364281c0c','rpo_total'),
('9ab54adbbecfa6f88ed7a273326563528bc47f3f5c6f2b7615608dced522a877','rpo_next_12m_share'),
('2dd39d6ef0cad91772e8c01ebd317dea2866faedf02214b3145dbf1dfd96e5e3','rpo_months13_36_share'),
('856e1204029ad51e980a8de878587a5ed662fd79926eb712e53146e61dd7557e','rpo_months37_60_share')]:
    rows.append(authored_tagged(k,fid,q,model_quantity=quantity,amount_qualifier='approximately',flag_unknown_reason='RPO_not_cash_no_named_customer_no_exact_24m_bucket'))
q='Financing receivables sold to financial institutions were $306 million and $1.2 billion for the three and nine months ended February 28, 2025, respectively, and $269 million and $1.1 billion for the three and nine months ended February 29, 2024, respectively.'
for fid in ['60e1fd4c3c6beb25ceaaab47078f469cba900b9f40c39fe318dadc1489d78f38','0b0bdbd49c635858de0a0b8947e6b369f2469ae8165ee9def9d75b8200273e62','cc8839d83ed4e95e11bd2c870185aa2af92852abf764a36929847920ad493a98','e03ac660e512a9b55dda8d351ea65ffd6a3f649c7b58bcd95a7ba98db36ad7ea']:
    rows.append(authored_tagged(k,fid,q,model_quantity='financing_receivables_sold',stage='recognized',amount_nature='receivables_transferred_not_explicit_narrative_cash_receipts',flag_unknown_reason='anonymous_customer_and_financial_institution_quarter_YTD_not_additive'))
q='As of each of February 28, 2025 and May 31, 2024, our non-marketable debt investments and equity securities and related instruments totaled $2.0 billion,'
for fid in ['5ac86e1ce99e8680805c741e1acc54018d0f0edf56cee487c8041a86ff7f219b','a43edcff0e2d784732bc81b05f1e43db23623b8ef46ad252a31619c409902196']:
    rows.append(authored_tagged(k,fid,q,model_quantity='nonmarketable_investments_combined_carrying_value',stage='recognized',amount_nature='combined_debt_equity_related_instruments_stock_not_new_cash',flag_unknown_reason='majority_Ampere_not_entire_allocation'))
rows.append(dict(quote='We follow the equity method of accounting for our investment in Ampere',model_quantity='Ampere_equity_method_not_consolidated',counterparty='Ampere',counterparty_evidence='named'))
rows.append(authored_tagged(k,'134a0f93dc53bb8b19c9864aa7c2b3cfe97a559d95d94bd309e87cfebff2f209','a related party entity in which we have an ownership interest of approximately 29% as of February 28, 2025.',model_quantity='Ampere_equity_method_ownership',counterparty='Ampere',counterparty_evidence='named',amount_qualifier='approximately'))
rows.append(authored_tagged(k,'c0356b983a62d121617da7da13f83e27df520bddaad109374356dd9ae0d88daa','During the nine months ended February 28, 2025, we invested an aggregate of $225 million in convertible debt instruments issued by Ampere.',model_quantity='Ampere_convertible_investment_recognized',counterparty='Ampere',counterparty_evidence='named',family='financing',link_type='convertible_or_safe',stage='recognized',flag_unknown_reason='cash_payment_not_explicit_not_primary_equity_round'))
rows.append(authored_tagged(k,'0be59ef04de5d8697304c27025edb05a904b3be6afe92192f8590a2b7bef6f80','The total carrying value of our investments in Ampere after accounting for losses under the equity method of accounting was $1.5 billion as of February 28, 2025.',model_quantity='Ampere_combined_investment_carrying_value',counterparty='Ampere',counterparty_evidence='named',amount_nature='combined_equity_debt_options_stock_not_cash_or_pure_principal'))
rows.append(dict(quote='We also have convertible debt investments in Ampere which, under the terms of an agreement with Ampere and other co-investors, will mature in June 2026 and are convertible into equity securities at the holder’s option under certain circumstances.',model_quantity='Ampere_convertible_maturity_and_optional_conversion',counterparty='Ampere',counterparty_evidence='named',flag_unknown_reason='month_only_day_not_assumed'))
rows.append(dict(quote='we are also a counterparty to certain put (exercisable by a co-investor) and call (exercisable by Oracle) options at prices of approximately $450 million to $1.5 billion, respectively, to acquire additional equity interests in Ampere from our co-investors through January 2027.',model_quantity='Ampere_secondary_put_call_options',counterparty='Ampere',counterparty_evidence='named',conditionality='optional',event_type='secondary_purchase',flag_unknown_reason='secondary_from_coinvestors_not_primary_cash_to_Ampere_no_exercise_proved'))
rows.append(dict(quote='If either of such options is exercised by us or our co-investors, we would obtain control of Ampere and consolidate its results with our results of operations.',model_quantity='Ampere_future_conditional_control',conditionality='conditional',trigger_description='If either of such options is exercised by us or our co-investors,',flag_unknown_reason='not_current_control_no_exercise_proved'))
q='Total operating lease liabilities were $12.0 billion and $7.5 billion as of February 28, 2025 and May 31, 2024, respectively, and total finance lease liabilities were $900 million as of February 28, 2025 (and none as of May 31, 2024).'
for fid,quantity in [
('8df3c4812f7c3f4e070fc487f0c213fb14e24b40ec5ef7dd0d0c2eaa1bd70ae3','operating_lease_liability'),
('695e73d7639acdf1f045cf915c859bda3bdfe7348a1771d4b5acdc9f0f12f82e','operating_lease_liability'),
('aef0d4206f1f3acb16e40b8a6ebacdbc24ba1bf64ef4130a579de9aaf4c9f444','finance_lease_liability'),
('ca014f4b2a4439bd8668a434e3c58ef58a0848401dcd161216d5ab4fc88f23ab','finance_lease_liability')]:
    rows.append(authored_tagged(k,fid,q,model_quantity=quantity,stage='recognized',amount_nature='discounted_lease_liability_stock_not_principal_cash_payments'))
q='Operating lease payments and interest payments on finance leases were $1.2 billion and $839 million for the nine months ended February 28, 2025 and February 29, 2024, respectively.'
for fid in ['9a877fdb95c8f724b949ffa6ebbe80f6b718346b2ffe369bdf1100db191fa0ec','b09d3f06e9e69ca75c511b1e3cd5cc957a58d5b4bd329eb33921fd471c89ae05']:
    rows.append(authored_tagged(k,fid,q,model_quantity='operating_lease_and_finance_interest_payments',stage='drawn_or_paid',amount_nature='mixed_operating_lease_cash_and_finance_interest_excludes_finance_principal'))
q='As of February 28, 2025, we had $48.4 billion of additional lease commitments, primarily for data centers, that are generally expected to commence between fiscal 2025 and fiscal 2027 and for terms of ten to fifteen years that were not reflected on our condensed consolidated balance sheets as of February 28, 2025.'
rows.append(authored_tagged(k,'563381c8f30f72ad63f910cde6fef40a2ea2d0231220b09852632b67e002a86f',q,model_quantity='lease_not_commenced',block='contractual_outflows',category_id='lease_not_commenced',component_kind='lease_payment',amount_nature='undiscounted_not_commenced_commitment_stock_not_cash_or_recognized_lease',flag_unknown_reason='no_exact_24m_schedule_or_operating_vs_finance_allocation'))
q='Losses from marketable and non-marketable investments, net | | | (59 | ) | | | (94 | ) | | | (236 | ) | | | (290 | )'
for fid in ['148d2e33492418bc04dbec572ba0a81ecc576306077f03b66811a6fc39644810','77c7dc54c2052e3d095579c84c741c1d6e9dcfbeb68f733367ae9cd42cc661ac','e2034265a8eae09e57a2a54c9784fed1774d71faf69792f3b2570581cee46d83','f8e1587d42e123d9e5679b1dea1ac7316a89d04ec6641e5c98b361750635046f']:
    rows.append(authored_tagged(k,fid,q,model_quantity='investment_gain_loss',stage='recognized',amount_nature='aggregate_net_investment_equity_method_loss_not_all_impairment',flag_unknown_reason='primarily_Ampere_not_entire_allocation'))
rows.append(abstention('was immaterial.','Immaterial restricted cash is not zero. Complete note contains no explicit substantial-doubt warning. Pending ASUs are not adopted; life extension is not F7.'))
if __name__=='__main__': save(k,rows)
