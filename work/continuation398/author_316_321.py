import json
from pathlib import Path
A=[]
def add(i,s,q,m,c='material',**kw):
 A.append(dict(index=i,classification=c,summary=s,rows=[dict(quote=q,model_quantity=m,stage='recognized',issuer_treatment=s,**kw)]))
add(316,'Segment unique revenu145,835 M$/perte25,612 FY2025, pas segment IA isolable. Coûts adjusted excluent amortissements,SBC,restructuring ; absence revenus IA détaillés ne signifie pas absence future contrat. SBCsegment26,425 vsnote26,436 k$ différence11k liée présentation nominalrestruct, ne pas doubler.','excluding stock-based compensation expense, depreciation and amortization','single_segment_adjusted_costs_not_cash_margin',judgment_sensitive=True)
add(317,'FV fin2025 30,946 M$ inclut MMF8,729 classés cashéquivalentsNAV et investissements22,217, pas totalité cash bancaire. Pas L3 récurrent rapporté ; L3nonrécurrent ROU siège impairment2024/25 noncash.','the only significant assets measured at fair value on a non-recurring basis','treasury_cash_equivalent_overlap_and_headquarters_rou_impairment','context_only')
add(318,'SBC26,436 M$ FY plus2,6 capitalisés, noncash ; bonus2025 finalement entièrementRSU4,1 M$ émisfévrier2026, pas bonus cash4,1. RSUunrecognized26,9 sur2,02ans +ESPP2,8 distinct, octroi postpériode8,9 à reconnaître3ans. Valeur intrinsèque options5,4 n’est pas produit d’exercice.','bonus awards for the period would be settled entirely in RSUs','bonus_settled_in_rsus_not_cash_and_sbc_capitalization')
add(319,'B279,897/Backup65,938 M$ FY ; revenuusage77,187 et subscription68,236 mêmes145,835 non àadditionner. Deferred35,897 M$ inclus RPO66,2 (35,5≤1an/30,7après) et openingrecognized30,640 non nouveaucash. HausseRPO contratmultiannuel T42025 anonyme, aucune preuve CW dans note ; ne pas ajouter à contrat2026 sanspérimètre.','a new multi-year customer contract executed during the fourth quarter of 2025.','annual_rpo_66_2m_includes_deferred_unnamed_contract',counterparty_evidence='anonymous',judgment_sensitive=True)
add(320,'RachatsFY2 M$ effectifs vs10 M$autorisation/8 M$restants jusqu’àaoût2026 ; financement attendu options/ESPP ne prouve aucun apport CoreWeave. ConversionclasseB2023nombreidentique noncash historique ; réserves17,194 millionsactions non émissioncollecte.','repurchased a total of 256,549 shares','actual_2m_buyback_vs_10m_authorization')
add(321,'TitresHTM fin2025 coût22,201 M$/portagenet22,199/FV22,217 toutes≤1an ; MMF8,729 déjàcashéquivalent. Perteslatentes0 n’est pas absencecrédit (allowance2k corporate). TrésoreriePLACEE générique non investissementprimaireIA.','Within one year','held_to_maturity_cost_vs_fair_value_short_maturity','context_only')
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
