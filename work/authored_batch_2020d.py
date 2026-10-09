from work.authored_helpers import *
k='33f4806e0e9ba86b3fda289aa6ebd47251891a50fbe673743a76a94f8f7e2ccc'
rows=repeat_chosen_rows('5563727191e172c54f12457fd8d1836f37198b62870dbe9d5271986597400541',['named_majority_owned_subsidiaries','trade_receivable_deferred_revenue_netting_policy'])
rows += [dict(quote='we adopted Accounting Standards Update (ASU) 2016-13,',model_quantity='credit_loss_and_equity_standard_adopted',recast_cause='accounting_change',flag_unknown_reason='ASU2016_13_and2020_01_Q1FY2021_no_exact_day_no_material_impact_not_zero'),abstention('was nominal.','Restricted cash nominal not exact zero; receivable impairment immaterial not zero and not investment F6. Complete note no substantial doubt, life change or nonmarketable stock clause. Reference-rate reform and income-tax standard pending; no covenant waiver or later tax realignment imported.')]
def t(fid,q,qty,**fields):rows.append(authored_tagged(k,fid,q,model_quantity=qty,**fields))
q='were approximately $3.4 billion and $3.5 billion, respectively.'
for fid in ['1a7247de39570f02864078ae01e8ea2eeae333cb7be0983c1ccd34f3e93bb50e','afe39bda89466ff20462f7a7be3e6ee89dc01fb50c99b0efa510bdc7c9b76aa8']:t(fid,q,'revenue_recognized_from_opening_deferred_revenue',stage='recognized',amount_nature='opening_contract_liability_recognition_not_current_cash')
q='were $35.5 billion as of August 31, 2020, approximately 61% of which we expect to recognize as revenues over the next twelve months and the remainder thereafter.'
for fid,qty in [('9c5e56a702b339f9ff74331f73f11d423e32333dd2e65681982199f0255958e5','rpo_total'),('333c4a0e82edc012e7fcb7e380e7c92cccfa6af46dca511e01622bf8a1d64fd2','rpo_next_12m_share')]:t(fid,q,qty,flag_unknown_reason='not_cash_no_named_customer_no_exact24m_bucket')
q='Financing receivables sold to financial institutions were $677 million and $705 million for each of the three months ended August 31, 2020 and 2019, respectively.'
for fid in ['231c83949d1f888330735b91a5b2d725a466b2610bb3485ea4b759f57deeed27','e08d7876acd619926abf57df671db2cebafc9436778fefb606c17658aba3acaa']:t(fid,q,'financing_receivables_sold',stage='recognized',amount_nature='receivables_transferred_not_explicit_narrative_cash_receipts',flag_unknown_reason='anonymous_parties_nonrecourse_generally90days')
save(k,rows)
k='117b92a55b5d27db86eaf6833ae7ddade118d6bcb93281141043f17b9a5b796f'
save(k,[authored_control(k,'were effective to provide reasonable assurance that the information required to be disclosed by us','disclosure_controls_effective',event_present=True),authored_control(k,'There were no changes in our internal control over financial reporting that occurred during our last fiscal quarter','no_material_ICFR_change_quarter',flag_unknown_reason='generic_limits_not_MW_quarter_nochange_not_F5_absence')])
k='9c5557c7abc861577a9184ef63bec2d39530b1cdb4b7d726236b172858abe129'
rows=repeat_chosen_rows('e734e067d8a513d105e512eaf96252bdfc73cadacc980d56d5f7be0630f9f7e2',['issuer_legal_name_jurisdiction_consolidation_scope','intercompany_elimination','current_prior_fiscal_years_52weeks','presentation_reclassification'])
rows += [abstention('Actual results could differ from these estimates','Full note no substantial doubt, actual investment impairment or life change. No later Inphi merger agreement, US parent or Innovium announcement imported.')]
save(k,rows)
