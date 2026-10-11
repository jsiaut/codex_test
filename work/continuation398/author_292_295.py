import json
from pathlib import Path
A=[]
def add(i,s,q,m,**kw):
 A.append(dict(index=i,classification='material',summary=s,rows=[dict(quote=q,model_quantity=m,stage='recognized',issuer_treatment=s,**kw)]))
add(292,'Mars affiliés : créances 861 M$, dettes 1,296 Md$ dont TRA 778 M$, clawback GP 334 M$ et employés 145 M$ hypothétiques ; pas cash déjà réglé. Athora/PIC acquisition clôturée T1 : stock 3,150 Md$ comprend conversion noncash de 266 M$ préférentiel et achats nouveaux. Engagements fin mars AM57 M$/Athene136 M$ remplacent montants conditionnels fin2025, sans addition. Atlas AFS affiliés6,1 Md$/commit1,3 Md$ distinct concentration émetteur3,325. ARI ~9 Md$ clôturé 24 avril, post-mars. ADIP126 M$ apports/254 distributions déjà inclus Athene.','The transaction closed on April 24, 2026.','ari_closed_post_march_athora_cash_and_conversion_stock',judgment_sensitive=True)
add(293,'Etats intermédiaires non audités, intragroupe éliminé, AAM/AHL présentés séparément. Les 79 M$ de revenu issu du stock différé au 1 janvier ne sont pas un nouvel encaissement T1. ASU2025-04/07 encore en évaluation et non adoptées : ne pas appliquer rétroactivement aux warrants clients.','There was $79 million of revenue recognized','deferred_opening_contract_liability_revenue_not_new_cash',judgment_sensitive=True)
add(294,'SBC T1 232 M$ noncash ; RSU non reconnu 1,3 Md$ sur2,4 ans. Attribution service6,6 millions/FV847 M$ non apport financier externe. Métriques performance FRE/SRE conditionnent rémunération, pas contrats clients IA.','equity-based compensation expense of $232 million','employee_sbc_non_cash_dilution_not_ai_funding')
add(295,'T1 rachats ouverts632 M$ et taxes net share225 M$ effectivement payés, distinct plafond discrétionnaire4 Md$. Dividendes communs295 M$+équivalents17. Préférentielles1,4 Md$ doivent se convertir en actions juillet, sans remboursement principal cash obligatoire ; coupons cumulatifs cash ou actions. Warrants cashless ne donnent pas de produit d’exercice. AOCI -3,144 Md$ non sortie cash.','The Company paid $632 million and $193 million','actual_buybacks_cash_vs_authorization_and_mandatory_stock_conversion')
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
