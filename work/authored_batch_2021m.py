from work.authored_helpers import *
k='0eadd720171975f1d02ca9d96fa2cecc7706b55885237976425dfdf81a55ce55'
rows=repeat_chosen_rows('9298b59432bb09b775bd45e4ffaafcd003dd319b22c2c3e6925171f131d36975',['consolidation_scope','intercompany_elimination'])
rows += [dict(quote='On January 1, 2021, we adopted Accounting Standards Update No. 2020-01,',model_quantity='ASU2020_01_adopted',event_date='2021-01-01',recast_cause='accounting_change',flag_unknown_reason='no_material_impact_not_zero'),abstention('There have been no material changes to our significant accounting policies','Complete note no substantial doubt, actual investment impairment or actual life change. ASU2020-06 pending here; no later life-change or Meta rename imported.')]
save(k,rows)
k='f086f9479c6c2d5c2def787ef46390b66b7b01adfa78785fa50740406e5db235'
save(k,[authored_control(k,'our disclosure controls and procedures are designed at a reasonable assurance level and are effective','disclosure_controls_effective',event_present=True),authored_control(k,'There were no changes in our internal control over financial reporting identified in management\'s evaluation','no_material_ICFR_change_quarter',flag_unknown_reason='generic_inherent_limits_not_MW_quarter_nochange_not_F5_absence')])
