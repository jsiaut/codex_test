"""Four authorized workstreams, with dated evidence and explicit coverage limits."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import json
from .assembly import rows
from .reports import csv_write

def amount(value):return 'ND' if value is None else format(Decimal(value)/Decimal(1_000_000),',.3f').replace(',',' ').replace('.',',')+' M$'

def render(db,root,as_of,delivery):
    notes=json.loads((root/'work/deepening_reading_queue.json').read_text())
    contracts=json.loads((root/'work/deepening_contract_queue.json').read_text())
    keys={r['content_key'] for r in notes+contracts}
    evidence=[r for r in rows(db,'''SELECT o.*,d.url FROM observations o LEFT JOIN documents d USING(document_id)
        ORDER BY o.accession,o.content_key,o.observation_id''') if r['content_key'] in keys]
    csv_write(root/'deepening_evidence.csv',evidence)
    selected=rows(db,"""SELECT * FROM measures WHERE view='revised' AND
      (group_id LIKE 'external:%' OR (group_id='CRWV' AND measure='liq_principal_due_to_cash' AND status='bounded'))
      ORDER BY group_id,measure,period_end,breakdown_key""")
    csv_write(root/'deepening_measures.csv',selected)
    actual=rows(db,"""SELECT measure,group_id,period_start,period_end,value,status,nd_reason,breakdown_key
      FROM measures WHERE view='revised' AND measure IN
      ('customer_working_capital_loan_received','customer_working_capital_loan_noncash_repayment',
       'customer_working_capital_loan_outstanding','named_customer_revenue','named_investment_acquisitions',
       'named_investment_carrying_amount','named_investment_unrealized_gain','indirect_investment_carrying_amount',
       'capital_solution_contract_size','customer_lease_incentive_asset') ORDER BY group_id,measure,period_end""")
    # Stop publication if the numeric narrative ceases to match the verified
    # export. These expectations bind dates and status, not just amounts.
    expected=[
        ('0002021728','customer_working_capital_loan_received','2026-01-01','2026-06-30',1004571000),
        ('0002021728','customer_working_capital_loan_noncash_repayment','2026-01-01','2026-06-30',86327000),
        ('0002021728','customer_working_capital_loan_outstanding','none','2026-06-30',918244000),
        ('0002021728','named_customer_revenue','2026-01-01','2026-06-30',74400000),
        ('0001585521','named_investment_acquisitions','2026-02-01','2026-07-31',300900000),
        ('0001585521','named_investment_carrying_amount','none','2026-07-31',3134500000),
        ('0001585521','named_investment_unrealized_gain','2026-05-01','2026-07-31',1612700000),
        ('0001108524','named_investment_unrealized_gain','2026-02-01','2026-07-31',3000000000),
        ('0001108524','named_investment_unrealized_gain','2026-05-01','2026-07-31',2700000000),
        ('0001858681','capital_solution_contract_size','2026-04-01','2026-06-30',35000000000),
        ('0001144879','customer_lease_incentive_asset','none','2025-08-28',121200000),
        ('0001892492','indirect_investment_carrying_amount','none','2026-06-30',92600000)]
    for cik,measure,start,end,value in expected:
        matches=[r for r in actual if (r['group_id'],r['measure'],r['period_start'],r['period_end'])==('external:'+cik,measure,start,end)]
        assert len(matches)==1 and matches[0]['status']=='computed' and matches[0]['value']==Decimal(value), ('Narrative/source discrepancy',cik,measure)
    for measure,value in [('cfo',679000000),('capex_cash',6422000000),('fcf_basic',-5743000000)]:
        r=rows(db,"SELECT value,status FROM measures WHERE group_id='CRWV' AND view='revised' AND period_start='2026-04-01' AND period_end='2026-06-30' AND measure=?",[measure])
        assert len(r)==1 and r[0]['status']=='computed' and r[0]['value']==Decimal(value), measure
    numeric_table='| Déposant / CIK | Mesure | Période | Montant publié |\n| --- | --- | --- | ---: |\n'
    for r in actual:numeric_table+=f"| {r['group_id'].split(':')[-1]} | {r['measure']} | {r['period_start']} → {r['period_end']} | {amount(r['value'])} |\n"
    positions=rows(db,'SELECT * FROM targeted_lender_positions ORDER BY group_id,period_end,position_label,accession')
    latest={}
    for r in positions:latest[r['group_id']]=max(latest.get(r['group_id'],r['period_end']),r['period_end'])
    metadata=json.loads((root/'work/deepening_issuer_metadata.json').read_text())
    lender_table='| Déposant | Dernière date vérifiée | Position telle que publiée | Coût | Juste valeur | Juste valeur / coût |\n| --- | --- | --- | ---: | ---: | ---: |\n'
    seen=set()
    # Keep instruments separate and use the latest source for each same
    # end-date/dimensional position; do not add comparative re-publications.
    for r in reversed(positions):
        k=(r['group_id'],r['period_end'],r['dimensions'])
        if r['period_end']!=latest[r['group_id']] or k in seen:continue
        seen.add(k);name=metadata[r['group_id'].split(':')[1]]['metadata']['name']
        lender_table+=f"| {name} | {r['period_end']} | {r['position_label'].replace('|',' / ')} | {amount(r['cost'])} | {amount(r['fair_value'])} | {r['fv_to_cost']} |\n"
    fds=json.loads((root/'work/deepening_form_d_filings.json').read_text())
    summary=dict(source_as_of=as_of,deepening_scope=json.loads((root/'work/deepening_authorization.json').read_text()),
        newly_read_unique_blocks=len(keys),new_observations=len(evidence),original_periodic_filings=len(json.loads((root/'work/deepening_filings.json').read_text())),
        lender_positions=len(positions),lenders_with_qualifying_loan_positions=len(latest),
        form_d_original_filings=len(fds),form_d_issuer_ciks=len({r['source']['ciks'][0] for r in fds.values()}),
        form_d_industry_counts=dict(Counter(r['fields']['industry'] for r in fds.values())),
        form_d_amounts_are_cumulative_and_may_include_noncash_and_mandatory_future_commitments=True,
        previous_financial_mismatch_counts_not_reclassified_to_pass=True,independent_audit_performed=False)
    (root/'work/deepening_results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str)+'\n')
    delivery['deepening_results']=summary
    (root/'delivery_summary.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2,default=str)+'\n')
    brief=f'''# Bilan des quatre approfondissements

Sources arrêtées au **9 octobre 2026**, comme dans la livraison précédente. Le travail est effectué par un seul agent, sans audit indépendant. Les onze groupes du modèle principal restent distincts des déposants supplémentaires examinés pour les prêts, investissements et véhicules.

**La découverte la plus précise est le montage Cerebras–OpenAI : un prêt client, des prestations qui peuvent rembourser ce prêt, et des warrants liés au contrat commercial.** Les pièces établissent ces mécanismes ; elles ne démontrent pas une demande artificielle ni une fragilité attribuable à tout le secteur.

## 1. Séries et dates

Le calcul historique tient désormais compte de la date officielle de publication quand elle suit la réception du dépôt par la SEC. Les dernières périodes AMD (27 juin 2026) et Broadcom (2 août 2026) sont rétablies dans la vue « connue à l’époque ». La synthèse financière utilise la vue révisée ; les deux vues restent disponibles. Le diagnostic ne trouve aucun chiffre publié après son instant de connaissance.

Les divergences comptables préexistantes ne sont pas effacées pour faire passer les contrôles. Le détail actualisé figure dans audit/controls.csv et work/delivery_verification.json.

## 2. CoreWeave : liquidité et prêteurs

Au **30 juin 2026**, CoreWeave publie **5,524 Md$ de trésorerie non restreinte**. Les échéances de principal sont **4,413 Md$ pour le reste de 2026**, **6,184 Md$ en 2027** et **4,416 Md$ en 2028**. Les dates mensuelles ne sont pas publiées.

| Horizon depuis le 30 juin 2026 | Principal exigible : borne basse → haute | Principal / trésorerie : borne basse → haute |
| --- | ---: | ---: |
| 12 mois | 4,413 → 10,597 Md$ | 0,798877 → 1,918357 |
| 24 mois | 10,597 → 15,013 Md$ | 1,918356 → 2,717777 |

Ces fourchettes utilisent uniquement les échéances annuelles publiées ; elles excluent les intérêts, baux et autres obligations de financement. Elles ne mesurent pas une probabilité de défaut. Au deuxième trimestre 2026, le flux de trésorerie opérationnel est de 679 M$, le capex payé de 6,422 Md$ et le FCF de base de −5,743 Md$.

Les dépôts originaux permettent de suivre **{len(positions)} positions de prêts, comparatifs et republications compris, auprès de {len(latest)} prêteurs**. Le fichier lender_positions.csv conserve coût, juste valeur, date, devise, instrument et lignage. Une position à la juste valeur ne mesure ni la taille du crédit syndiqué ni la perte probable. La part des intérêts PIK et le statut non-accrual par position restent non déterminés dans cette tranche ; leur lecture spécifique n’est pas terminée.

## 3. NVIDIA–CoreWeave et AMD–Meta

**NVIDIA–CoreWeave.** Le MSA du 10 avril 2023, déposé le 25 septembre 2025, a été lu intégralement. Il prévoit une interdiction de compensation par le client, une libération des obligations de paiement futures après une résiliation conforme, et la priorité des bons de commande sur le MSA. Le 8-K du 15 septembre 2025 décrit séparément le nouveau bon de commande de **6,3 Md$**, avec achat de capacité résiduelle invendue jusqu’au 13 avril 2032. Sa valeur initiale n’est pas un versement et le MSA ne suffit pas à reconstituer son calendrier ou toutes ses conditions. Le bon de commande complet n’a pas été retrouvé dans cette recherche ciblée.

Les **2 Md$ versés par NVIDIA le 23 janvier 2026** apparaissent dans deux dépôts de CoreWeave : c’est la même opération, à compter une seule fois. Les paiements de NVIDIA à CoreWeave au titre du MSA ne deviennent pas automatiquement du chiffre d’affaires reconnu.

**AMD–Meta.** Le warrant du 23 février 2026 porte sur un maximum de **160 millions d’actions**, à **0,01 $ par action**. Les annexes E et F, relatives à l’acquisition et à l’exercice, sont masquées. La clause fiscale vise une remise ou un rabais commercial ; elle n’établit pas à elle seule le traitement US GAAP ni une remise comptabilisée. Le Master Purchase Agreement et son Amendment Eight sont cités ; leurs textes complets n’ont pas été retrouvés dans le corpus ciblé. Aucun plafond de warrant n’est converti en financement payé.

## 4. Contreparties privées et véhicules

**Cerebras–OpenAI OpCo, LLC.** Le prêt signé le **5 janvier 2026** porte sur **1 004 571 259 $**, avec échéance au plus tard le 31 décembre 2032 et intérêt nominal de 6 %. La note de dette de juin rapporte des encaissements arrondis de **1 004,571 M$**, **86,327 M$ de remboursements non monétaires** et **918,244 M$ de principal restant**. Les fonds reçus sont restreints. Le remboursement peut passer par des services et d’autres crédits ; le plafond de ces remboursements et le calendrier mensuel sont masqués dans le contrat.

Le revenu OpenAI reconnu au premier semestre est de **74,4 M$**, net de **3,3 M$ d’amortissement de l’actif de warrants**. Il est distinct des remboursements non monétaires. Cerebras déclare évaluer ensemble le prêt et le contrat de services, avec une composante de financement significative. Le warrant est présenté comme une incitation aux achats ; une tranche de **4 459 337 actions** est liée au dépôt du prêt. Le calendrier public reste partiellement masqué.

**Anthropic.** Zoom publie **300,9 M$ d’investissements supplémentaires** sur son semestre terminé le 31 juillet 2026, **1 612,7 M$ de gains non réalisés** sur le trimestre et **3 134,5 M$ de valeur comptable** à cette date. Salesforce publie **3 Md$ de gains non réalisés** sur le semestre, dont **2,7 Md$ sur le trimestre** : ce ne sont pas de nouveaux apports de cash démontrés. Ces montants ne s’additionnent pas comme financements reçus par Anthropic.

**Autres véhicules.** Eightco publie **92,6 M$ d’achat d’une participation dans un SPV non consolidé**, exposé indirectement à OpenAI. L’apport primaire à OpenAI n’est pas établi. Applied Digital comptabilise **121,2 M$ d’actif d’incitation locative** lié au warrant Building 4 remis à CoreWeave ; ce warrant a ensuite été cédé à des tiers. Apollo décrit une opération de **35 Md$** avec Broadcom facilitant les infrastructures d’Anthropic : la garantie d’Athene représente **15 % de l’obligation d’achat restante**, avec un accord de remboursement par un tiers portant sur **35 % des paiements éventuels**. L’obligation restante n’étant pas chiffrée dans cette note, aucun montant de garantie n’est calculé en multipliant 35 Md$ par 15 %.

## Couverture et reprise

La recherche a balayé **21 archives BDC** et **12 archives mensuelles de Notes Data Sets**, d’octobre 2025 à septembre 2026. Elle a conservé **95 candidats textuels**, qui servent à trouver les sources et ne valent pas preuves financières. Les dépôts originaux ont été récupérés pour 13 prêteurs nommés et 8 autres déposants ciblés, soit **34 dépôts périodiques**. Le corpus contient **168 Form D / D-A uniques de 118 CIK**, dont 152 formulaires classés « Pooled Investment Fund » : ce sont des dépôts, pas 168 financements des laboratoires.

Un Form D publie des montants cumulatifs d’offres et de titres vendus qui peuvent inclure des contreparties non monétaires et des engagements futurs obligatoires. Les amendements sont rapprochés par CIK et date de première vente ; sans date, le rapprochement reste non établi. Aucun de ces montants n’est attribué automatiquement à OpenAI ou Anthropic. Les archives anciennes non collectées, les candidats non lus et les parties non résolues restent visibles dans les exclusions.

Les sources sont reliées aux citations dans deepening_evidence.csv ; les chiffres et leurs périodes dans deepening_measures.csv, lender_positions.csv et form_d_disclosures.csv. Les observations sont conservées et le code reconstruit les huit tables hors ligne. Les critères des annexes E et F restent inchangés. Les commits intermédiaires et la livraison finale sont sauvegardés sur https://github.com/jsiaut/codex_test.
'''
    concise=f'''# Les quatre approfondissements — point de livraison

Sources arrêtées au **9 octobre 2026**. La découverte principale est le montage **Cerebras–OpenAI**, qui relie un prêt client, son remboursement possible par des services et des warrants incitant aux achats. Les pièces établissent ces liens, sans permettre une conclusion sur la fragilité de tout le secteur.

## 1. Séries et dates

La vue historique respecte désormais la date officielle de publication lorsqu’elle suit la réception du dépôt par la SEC. Les dernières périodes AMD et Broadcom sont rétablies. La synthèse utilise les données révisées et conserve la vue historique. Les contrôles de publication passent ; les **26 divergences comptables localisées** restent visibles et ne sont pas corrigées par hypothèse.

## 2. CoreWeave et ses prêteurs

Au **30 juin 2026**, CoreWeave dispose de **5,524 Md$ de trésorerie non restreinte**. Faute d’échéances mensuelles, le principal exigible est encadré : **4,413 à 10,597 Md$ sur 12 mois**, **10,597 à 15,013 Md$ sur 24 mois**. Les rapports principal / trésorerie sont respectivement **0,799–1,918** et **1,918–2,718**. Ces bornes excluent intérêts, baux et autres obligations de financement.

Au deuxième trimestre, le CFO est de **679 M$**, le capex payé de **6,422 Md$**, soit un FCF de base de **−5,743 Md$**. Les dépôts originaux documentent **{len(positions)} positions auprès de {len(latest)} prêteurs**, comparatifs et republications compris. Ces lignes ne doivent pas être additionnées comme des crédits distincts. La part PIK et le statut non-accrual par position restent à lire.

## 3. NVIDIA–CoreWeave et AMD–Meta

Le MSA NVIDIA–CoreWeave a été lu intégralement : interdiction de compensation, obligations futures libérées après résiliation conforme et priorité des bons de commande. Le 8-K décrit un bon de commande initial de **6,3 Md$** couvrant la capacité résiduelle invendue ; son texte complet n’a pas été retrouvé. Sa valeur contractuelle ne vaut pas encaissement. Les **2 Md$ investis par NVIDIA en janvier 2026**, mentionnés dans deux dépôts, constituent une seule opération.

Le warrant AMD–Meta porte sur **160 millions d’actions au maximum**, à **0,01 $ par action**. Les annexes détaillant acquisition et exercice sont masquées. La clause fiscale vise une remise commerciale ; elle ne démontre pas son traitement comptable. Le contrat d’achat et son amendement sont cités, sans texte complet retrouvé dans cette recherche.

## 4. Contreparties privées et véhicules

**Cerebras–OpenAI.** La note de juin publie **1 004,571 M$ de prêt reçu**, **86,327 M$ de remboursements non monétaires** et **918,244 M$ de principal restant**. Les fonds reçus sont restreints. Le revenu OpenAI reconnu au semestre, **74,4 M$**, est distinct du remboursement. Le warrant constitue une incitation explicite aux achats ; une tranche de **4 459 337 actions** dépend du dépôt du prêt. Les frais, certaines conditions et le calendrier de remboursement restent partiellement masqués.

**Anthropic.** Zoom publie **300,9 M$ d’investissements supplémentaires** au semestre et **3 134,5 M$ de valeur comptable** au 31 juillet. Salesforce publie **3 Md$ de gains non réalisés** au semestre. Ces bases ne permettent pas de sommer les montants comme du cash reçu par Anthropic.

**Véhicules.** Eightco investit **92,6 M$ dans un SPV non consolidé** exposé indirectement à OpenAI ; un apport primaire au laboratoire n’est pas établi. Apollo décrit une opération de **35 Md$** avec Broadcom facilitant les infrastructures d’Anthropic. La garantie d’Athene représente **15 % de l’obligation d’achat restante**, dont le montant n’est pas publié : aucun montant de garantie n’est extrapolé. Applied Digital distingue un warrant client comptabilisé comme incitation locative, puis cédé à des tiers.

## Sources et limites

La tranche comprend **34 dépôts périodiques originaux** et **168 Form D / D-A uniques de 118 CIK**. Les Form D décrivent des offres cumulatives, parfois des fonds : leurs montants peuvent inclure du non-monétaire et des engagements futurs obligatoires. Aucun montant n’est attribué automatiquement à un laboratoire.

Le rapport approfondissements.md contient les sources, les périodes, les positions des prêteurs et les limites de couverture. Les quatre CSV donnent les citations et le lignage des montants. Les huit tables sont reconstructibles hors ligne. Les critères E/F restent inchangés. Travail effectué seul ; aucun audit indépendant revendiqué. Sauvegarde : https://github.com/jsiaut/codex_test.
'''
    (root/'user_brief_deepening.md').write_text(concise)
    full=brief+'\n## Positions de prêteurs à leur dernière date vérifiée\n\n'+lender_table+'\n## Mesures ciblées publiées\n\n'+numeric_table
    full+='\nLes tableaux conservent la base propre à chaque montant. « Dernière date vérifiée » ne garantit pas que la position subsiste au 9 octobre 2026.\n'
    (root/'approfondissements.md').write_text(full)
    # The detailed synthesis stays generated from the main eleven-group model.
    with (root/'synthesis.md').open('a') as f:f.write('\n## Approfondissements autorisés\n\nVoir approfondissements.md et les quatre fichiers CSV de cette tranche pour les prêteurs, contrats et découvertes. Les montants externes sont conservés séparément des agrégats des onze groupes.\n')
    (root/'README.md').write_text('''# SEC_Project_2

Les quatre approfondissements autorisés sont livrés : lire [user_brief_deepening.md](user_brief_deepening.md), puis [approfondissements.md](approfondissements.md). Les citations sont dans deepening_evidence.csv ; les quantités dans deepening_measures.csv, lender_positions.csv et form_d_disclosures.csv. Les huit tables sont dans tables/ et les contrôles dans audit/.

Les onze groupes principaux, l’arrêt des sources du 9 octobre 2026 et les critères E/F restent inchangés. Les prêteurs et autres déposants ciblés sont des sources externes distinctes. Les résultats du premier passage et des notes complémentaires sont conservés dans leurs fichiers et l’historique Git. Aucun score ou total global d’exposition n’est produit. Travail effectué sans sous-agent ; aucun audit indépendant revendiqué.

## Reproduire

Installer requirements.txt. Restaurer le cache initial depuis la sauvegarde LFS, puis les sources supplémentaires depuis la sauvegarde sec-project-2-deepening, sans écraser les observations récentes ni restaurer un ancien verrou. L’archive SEC_Project_2_approfondissements.zip contient aussi les sources supplémentaires, les blocs lus et les exports. Depuis la racine, `python -m secfragility.phase3 --reconstruct` reconstruit les faits et les huit tables hors ligne. Aucun appel de modèle ni nouvelle requête SEC n’est nécessaire. Les décisions, observations et sources originales sont nécessaires à cette reproduction.

`python -m secfragility.reproduce capture`, puis la reconstruction et `python -m secfragility.reproduce compare` vérifient l’égalité intégrale des huit tables, décimales et provenance comprises. Ne pas capturer une nouvelle référence pour masquer une divergence.

Les sauvegardes intermédiaires et la livraison finale sont poussées sur https://github.com/jsiaut/codex_test. Les répertoires de sources ignorés par Git sont conservés dans les sauvegardes LFS avec leur SHA-256.
''')
