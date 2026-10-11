import json
from pathlib import Path
A=[]
def add(i,s,q,m,c='material',**kw):
 A.append(dict(index=i,classification=c,summary=s,rows=[dict(quote=q,model_quantity=m,stage='recognized',issuer_treatment=s,**kw)]))
add(332,'JuinHTM17,454 M$coût/net vs17,435FV,19klatentnoncash, toutes≤1an. MMF14,051 déjàcashéquivalentNAV ; pasplacementIAprimaireidentifié.','Within one year','june_short_marketables_cost_fv_cash_equivalent_overlap','context_only')
add(333,'Programmeachat10 M$ terminé1août2026 ; disponibilité6,6 M$àjuin n’est pasprogrammeencoreactifaprèsaoût ni dépense. Financementréeloptions/ESPP mentionné, sansCWcash.','on which date the plan terminated','buyback_program_terminated_august_not_current_capacity')
add(334,'Juin servicesnoncancelables1,5reste2026+3,6/2,2/1 jusqu’à2029=8,3 M$, nouveauxstocknepasajouter5,1mars. Indemnitésinestimablesnonprovisionnées restentcontingentes.','not possible to reasonably estimate the maximum potential amount','june_nonlease_8_3m_commitment_stock_and_unquantified_indemnities',judgment_sensitive=True)
add(335,'H1 revenu81,379 M$ inclT242,713/T138,666 ; pertes11,236 inclT25,089, segmentunique nonisoléIA. AdjustedexclutDA7,783/AM5,702/SBC15,471/restruct3,512 ; SBCrestruct0,6 ailleurs donc pasdoubler. Pas revenucommittedstorage avantT3 selonpolicy.','one operating and reportable segment','halfyear_segment_single_scope_no_ai_cash_inference','context_only')
add(336,'Juin NOrevenucommittedcapacity/managedstorage H1, commencementrevenuattenduT3 uniquementcapacitédisponible/déployée. Actionsaccordéesclient réduisenttransactionprice selonmêmerythmerevenu ; ASU2025-04 adoptéanticipationjan2026, pas cashprimaire. Duréeéquipement6ans réduitDAH11,7 M$(inclT20,8), noncash. DeuxclientsAR27%anonymes nepeuventêtrenommésCW, fournisseurcash14%idem.','Therefore, no related revenue was recognized during the three and six months ended June 30, 2026.','committed_capacity_revenue_zero_predeployment_customer_equity_contrarevenue',judgment_sensitive=True)
add(337,'JuinFV31,486 M$ dontMMF14,051 déjàcash+HTM17,435 ; NAVhorshiérarchie, aucunL3récurentidentifié. AucuneimpairmentnonrécurrentematérielleH1, sanspreuveabsencefuturrisqueIA.','There were no material assets or liabilities that were measured at fair value on a non-recurring basis','june_generic_liquidity_investments_not_ai_or_new_impairment','context_only')
add(338,'Juin financebaux46,713 M$bilan vs55,723brut ; operating35,724 vs44,191+services11,767 horsbilan. CashH1intérêts2,292/rent3,747 distinct19,108equipment/13,082ROUnoncash. NouveaujuinDC3,8 M$noncommencéT3 etexpansionjuillet1,5 M$T4 horsjuin/table, total5,3 futur sans mélangerdates. Ancien17,5 M$expansion prévuT2 nonrépété ; ne pasconclureannulationniadditionautomaticauxstocksjuin sansrapprochement.','not included in the lease obligations presented in the table above','june_july_uncommenced_5_3m_and_operating_nonlease_off_balance',judgment_sensitive=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
