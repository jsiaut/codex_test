import json
from pathlib import Path
s='Fin 2025 : FV groupe386,597 Md$, level3 152,115 et NAV23,92 Md$ distincts ; retirement378,105 déjà inclut Athene après éliminations. Tables FV AM excluent performance allocations235 M$, rollforward AM exclut due related15 M$, retraite exclut MRBassets214 M$ : expliquer périmètre sans forcer rapprochement incomplet. IPO d’un émetteur anonyme déclenche impairment257 M$ au T2 et valeur101 M$, sans preuve cash ni identité IA. Validation externe limitée aux procédures demandées par management, pas audit indépendant de toutes valorisations.'
A=[dict(index=281,classification='material',summary=s,rows=[dict(quote='the Company recognized an impairment loss of $257 million during the second quarter of 2025',model_quantity='ipo_observable_price_impairment_not_cash_or_named_ai',stage='recognized',issuer_treatment=s,counterparty_evidence='anonymous',measurement_basis='Q2_2025_impairment257m;Dec_group_Level3_152_115bn_scope_specific',judgment_sensitive=True)])]
Path(__file__).with_suffix('.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n')
M=json.loads(Path('work/continuation398/scope.json').read_text())['rows']
assert A[0]['rows'][0]['quote'] in json.loads(Path(M[281]['path']).read_text())['text']
