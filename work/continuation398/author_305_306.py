import json
from pathlib import Path
A=[]
def add(i,s,q,m,c='material'):
 A.append(dict(index=i,classification=c,summary=s,rows=[dict(quote=q,model_quantity=m,stage='recognized',issuer_treatment=s)]))
add(305,'Dette juin13,727 Md$ bilan=AM5,895 dont warehouse nonrecours133 M$ anonyme+Athene7,832. Notes500 M$2026 principal et intérêts remboursés27mai, retirer des échéances futures. Notes AGM750 M$ émisesmars ; Athene1 Md$6,15% émises7août post-juin ne pas ajouter à cash/dette juin. Refinancement26juin AHLcap1,75 Md$2031 cov40%/networth22,1 ; liquidité2,6 Md$2027 AAReNW26,2, remplace facilités anciennes. Toutes non tirées juin. Intérêts H1369 M$ inclT2190 ne sont pas tous coupons cash.','AMH repaid in full the principal and accrued interest','500m_may_notes_repaid_june_facilities_refinanced_august_postperiod')
add(306,'Périmètre Apollo inclut retraite Athene ; Bridge transaction en actions consolidée depuis2sept2025. Ne pas fusionner fonds gérés et filiales opérationnelles sur la seule relation de gestion.','in an all-stock transaction','organization_repeated_group_scope','context_only')
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
for a in A:
 t=json.loads(Path(M[a['index']]['path']).read_text())['text']
 for r in a['rows']:assert r['quote'] in t,(a['index'],r['quote'])
