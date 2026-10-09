from work.authored_helpers import *
k='f7ac4141fcd6aff0bc3014bdc30dde67f2eb7f9cd9294a0da65d6aeee05e6ab9'
rows=repeat_chosen_rows('9c5557c7abc861577a9184ef63bec2d39530b1cdb4b7d726236b172858abe129',['issuer_legal_name_jurisdiction_consolidation_scope','intercompany_elimination','current_prior_fiscal_years_52weeks','presentation_reclassification'])
rows += [abstention('Basis of Presentation','Full first note no substantial doubt, actual investment impairment or life change. No later Inphi merger agreement or US parent imported. Separate policies note not processed here.')]
save(k,rows)
k='a102a5d03771206fb25c8e6773d077fcc079a648460a55cca2a6f2c747d1a098'
save(k,[authored_control(k,'our disclosure controls and procedures were effective.','disclosure_controls_effective',event_present=True),authored_control(k,'There have been no changes in our internal control over financial reporting during the three months ended May 2, 2020','no_material_ICFR_change_quarter',flag_unknown_reason='generic_limits_not_MW_quarter_nochange_not_F5_absence')])
k='ce4e481480326d13b41ee9f32b60389d5ba50f9238df99b0cde81a13d0d0748a'
rows=repeat_chosen_rows('b50cb1cb6daea5d61c4281ae226ff399e51742b10503b507f5ec71e686aaa2a2',['consolidation_scope','intercompany_elimination','presentation_reclassification','current53_prior52_week_basis'])
rows += [dict(quote='The first quarters of fiscal years 2021 and 2020 were both 13-week quarters.',model_quantity='quarter_13_week_basis'),dict(quote="The Company adopted the standard in the first quarter of fiscal year 2021 and the impact of the adoption was not material to the Company's consolidated financial statements.",model_quantity='expected_credit_loss_standard_adopted',recast_cause='accounting_change',flag_unknown_reason='Q1FY2021_no_exact_day_not_material_not_zero'),abstention('Actual results could differ materially from our estimates.','Complete note no substantial doubt, actual investment impairment or life change. No Mellanox consolidation clause in this April26 reporting-period note; later April27 consolidation not imported.')]
save(k,rows)
