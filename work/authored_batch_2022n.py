from work.authored_helpers import *
k='4755359ee07a9eb85e139a39364c4ddba0b45e3e2952d9fc0f9f5d7ac13f8c39'
rows=repeat_chosen_rows('7acf692e16f68389cac29d1364e8bd38e8d6b971abc37f96a28a8f4256d1bd68',['consolidation_scope','intercompany_elimination','ASU2021_08_adopted'])
rows.append(abstention('Actual results could differ materially from those estimates.','Complete note no explicit substantial doubt or life extension clause; no future Q2 server change or July fair-value adoption imported. Government-assistance guidance pending.'))
save(k,rows)
k='f9aeb2f57522c03e34ee35236996ec61bc7e183f063e6c50fb76ad9660474549'
save(k,[authored_control(k,'our CEO and CFO have concluded that as of March 31, 2022, our disclosure controls and procedures are designed at a reasonable assurance level and are effective','disclosure_controls_effective',event_present=True),authored_control(k,'There were no changes in our internal control over financial reporting identified in management\'s evaluation','no_material_ICFR_change_quarter',flag_unknown_reason='quarter_nochange_and_generic_limits_not_F5_absence')])
k='d65e0437a17a382cb2bc93214c15581090b4dcc9800e06bfada9b9432aaaa031'
rows=repeat_chosen_rows('9aca7ea4d35ac06442aa416cc93afe576d87a0cf5d83f6b5d3a010f3e216fc0b',['Alphabet_successor_issuer_year','consolidation_scope','intercompany_elimination'])
rows.append(abstention('Actual results could differ materially from these estimates.','Complete note no explicit substantial doubt, life assessment or stock-split clause; no clause imported from later notes.'))
save(k,rows)
