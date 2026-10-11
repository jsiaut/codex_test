import json
from pathlib import Path
A=[]
def add(i,s,q,m,**kw):
 A.append(dict(index=i,classification='material',summary=s,rows=[dict(quote=q,model_quantity=m,stage='recognized',issuer_treatment=s,**kw)]))
add(282,'Apollo conserve en consolidation la comptabilité spécialisée à la juste valeur des fonds : un portefeuille de fonds ne devient donc pas automatiquement une filiale opérationnelle consolidée. Contrôle VIE exige pouvoir et intérêt variable significatif. Performance allocations sous equity method, hors ASC606 ; incentive fees différées tant que risque de reprise. Profit sharing peut être payé en nature après réalisation ; clawback hypothétique distinct d’une dette cash exigible. Repo demeure financement ; fonds retenus légalement chez cédant. Offsets de commissions différés et parfois remboursables : éviter double comptage des revenus et encaissements. Les 99 M$ de revenu issu du stock différé initial ne sont pas du cash neuf.','The Company has retained this specialized accounting for investment companies in consolidation.','investment_company_fair_value_retained_in_consolidation',judgment_sensitive=True)
add(283,'Engagements AM non financés 553 M$, distincts des 35,2 Md$ Athene déjà inclus dans les totaux VIE/affiliés et appelables à tout moment. Reprise théorique de 6 Md$ de performance allocations si tous fonds sans valeur, sans exigibilité cash actuelle. Capital Markets Partnership : 2,5 Md$ de capacité revolving contre 1,4 Md$ d’opérations financées ; aucun apport parent à date, non-recours sous réserve comfort letter. Bridge : prêts garantis par clauses contingentes de 758 M$ de nominal, sans perte maximale quantifiée. Garantie Atlas 2,5 Md$ avec non-probabilité estimée, non absence de garantie. Stone Tower 72 M$ FV contingent ; Griffin déjà réglé/expiré en 2024. Litiges 1,9 Md$ et paiements TRA contestés 570 M$ ne constituent pas des provisions nouvelles de mêmes montants.','Apollo Capital Markets Partnership','capital_markets_vie_capacity_drawn_parent_funding_distinguished',judgment_sensitive=True)
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
