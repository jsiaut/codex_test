import json
from pathlib import Path
A=[]
def add(i,s,q,m,stage='recognized',**kw):
 A.append(dict(index=i,classification='material',summary=s,rows=[dict(quote=q,model_quantity=m,stage=stage,issuer_treatment=s,**kw)]))
add(301,'SBC H1 478 M$ inclut T2246 et T1232, noncash ; unrecognized1,1 Md$ sur2,2 ans. Grant FV service883 M$ et performance30 M$ rémunération, pas financement client.','equity-based compensation expense of $478 million','halfyear_employee_non_cash_compensation')
add(302,'Commun0,5625$ déclaré4août pour31août, post-juin ; aucune preuve de paiement réalisé fournie dans cette courte note.','which will be paid on August 31, 2026','post_june_common_dividend_declared','signed')
add(303,'Juin VIE AM investissements3,713 Md$, lignes subscription1,381 Md$ à6,25%, maturité0,08 an ; autres dettes501 M$ à11%, maturité0,38 an, emprunteur non nommé : risque renouvellement sans attribution WHCO/IA. Cash escrow68 M$ attendu12mois indisponible. AM maxVIE409 M$. Retraite139,108/148,068 Md$ portage/max déjà engagements inclus, fonds sous VIE consolidées, non additif. Non-recours annoncé ne supprime pas engagements distincts des autres notes.','Other debt obligations','june_vie_501m_11percent_short_debt_unidentified',counterparty_evidence='anonymous',judgment_sensitive=True)
add(304,'H1 Segment Income3,200 Md$=T11,522+T21,678, hors HoldCo98 M$ financement et autres ajustements. FRE1,513/SRE1,596/PII91 non cash-flow. Frais AM1,953 Md$ incluent785 M$ Athene déjà T1399+T2386, à éliminer. Revenus segments11,033 vs GAAP16,212 ; actifs477,285→494,048 Md$ après VIE/éliminations. Effets FV et revenus noncash ne prouvent pas encaissements IA.','not as a measure of liquidity','halfyear_segment_intercompany_785m_and_gaap_perimeter',judgment_sensitive=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
