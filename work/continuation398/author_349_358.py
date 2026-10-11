import json
from pathlib import Path
A=[]
def add(i,s,q,m,c='material',**kw):
 A.append(dict(index=i,classification=c,summary=s,rows=[dict(quote=q,model_quantity=m,stage='recognized',issuer_treatment=s,**kw)]))
add(349,'GECC basefee1,5% actifsinclleverage, FY4,987 M$/payable1,183. Incentive20% aprèshurdle7%/catchup8,75 inclPIK/OID revenuaccrual MAISpaiementfeePIKdifféréparsecurityjusqu’àcash reçu, mitigant liquidité. Totalreturntest reporteautresfees : stock2,267 M$Decmais0immédiatementexigible. Reset2022retire163,2 M$historicaloss calculfees pasrecouvrementcash. Waiver2022 4,9nonrecapturehistorique.','becomes payable only if, as, when and to the extent cash is received','incentive_pik_fees_deferred_until_cash_received',judgment_sensitive=True)
add(350,'PostFYdistributionT10,30$cashprévue ; févrierwaiverstock2,3 M$fees augmenteNII nonencaissement. GECCO20 M$redemptionnotice27février pour31mars intentionexécuter pasencorepaidauDec.','expects to recognize the reversal','incentive_fee_waiver_non_cash_and_planned_note_redemption',judgment_sensitive=True)
add(351,'GECCBDCexternallymanagednondiversified, GECMfilialeGEG. RelationgestionpaspreuvepartenaireclientIA ouconsoloperatinginvestments.','externally managed, non-diversified','bdc_organization_manager_parent_scope','context_only')
add(352,'Mars NAV7,74 vs8,07Déc, netassets107,477 M$ ; NII0,36/distrib0,30 inclreversalfees àisoler pourcouverturecash, perteslatent0,60. RatioNII11,77annualisé pascashquarter11,77.','Annualized for periods less than one year.','march_nav_income_waiver_adjustment_and_annualized_ratios',judgment_sensitive=True)
add(353,'T2distributionréduite0,25$cashprévue30juin ; avrilnoticeGECCO18,6 M$pour27mai rembourserremainder. Waiverfeesétenduejusqu’à30juin, réduitdettefee sanscashinvestisseur.','redeem $18.6 million','remaining_gecco_redemption_notice_and_fee_waiver_extension',judgment_sensitive=True)
add(354,'Mars ASC946/PIK reporting inchangés : accrualnoncash etCLOeffectiveyieldpasdistributions. RIC90%ICTIinclPIK peutforcerdistributions avantréceptioncash, maisfeePIKreportéejusqu’àcash note3. DDTLnegcost/negFV possiblesfeesunfundedpasperte/principalnégatif. ValuationGECM/tierssubjective, petitespositionssansvaluationexterne.','including PIK interest','march_pik_tax_distribution_and_deferred_draw_accounting',judgment_sensitive=True)
add(355,'Mandate originationETsecondaire, CLOwarehouse ; nopreuvenouveaufinancementCWsurmandategénéral.','directly with issuers and in the secondary markets','march_investment_mandate_no_primary_cash_proof','context_only')
add(356,'MarsFV276,763 M$dontL3164,787/NAV43,857horsL3, versusDec331,071 ; L3purchases16,914inclPIK/exchange, noncashintégral. Teninvest21,937L2→L3pricingmoinsvisible nonpreuveuniquedéfaut. DeuxNAVretraits≤annuelrestrictifs nonliquiditéinstantanée.','capitalized PIK income','march_level3_transparency_and_nav_redemption_restrictions',judgment_sensitive=True)
add(357,'T1rachat106123actions×4,98$~528492$calculé, distinct10 M$plafond. ATM cumul13 M$net inchangéDec→mars doncpasnewcash13 M$T1. PoorRichard14,3 M$placement2025 pasT1collecte.','As of March 31, 2026, the Company has sold 1,163,753 shares','cumulative_atm_unchanged_not_new_quarter_funding',judgment_sensitive=True)
add(358,'Marswaiverfees2,810 M$=2,267ancien+543kquarter, NONRECAPTURE ; stockpayable0. ReversalboostNII/NAVnoncash, n’estpasPIKrecouvrementouCoreWeavedistribution. Basefee1,072/admin420kpayables cashfutures distincts. AvrilwaiverT2àsuivrejuin. PIKincentivefee demeure cashonlyreceivedrule.','The incentive fee waiver is not subject to recapture.','2_810m_fee_waiver_non_cash_nii_nav_support',judgment_sensitive=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
