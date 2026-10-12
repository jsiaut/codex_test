"""Render personally authored decisions, without inferring financial claims."""
from pathlib import Path
from datetime import datetime,timezone
import csv,json
from .operation_sources import BASE,read,save

def csv_file(path,keys,rows):
    with Path(path).open('w',newline='') as f:
        writer=csv.DictWriter(f,keys,extrasaction='ignore');writer.writeheader();writer.writerows(rows)

def report(root):
    root=Path(root);base=root/BASE;cases=read(base/'operations.json');notes=read(base/'authored_observations.json');sources=read(base/'source_manifest.json')
    indexed={s['document_id']:s for s in sources};proof=read(base/'validation.json')
    evidence=[dict(n,source_url=indexed[n['document_id']]['url'],source_sha256=indexed[n['document_id']]['sha256']) for n in notes]
    csv_file(root/'operation_evidence.csv',['observation_id','group_id','model_quantity','amount','unit','currency','measurement_basis','stage','period_start','period_end','event_date','knowledge_date','tier','document_id','tagged_fact_id','locator','source_url','source_sha256','issuer_treatment','quote'],evidence)
    coverage=[dict(operation_id=c['operation_id'],title=c['title'],**q) for c in cases for q in c['questions']]
    csv_file(root/'operation_coverage.csv',['operation_id','title','question','state','answer','gap'],coverage)
    roles=[dict(operation_id=c['operation_id'],**r) for c in cases for r in c['roles']]
    csv_file(root/'operation_roles.csv',['operation_id','name','role','entity_id','unknown_reason'],roles)
    clauses=[dict(operation_id=c['operation_id'],kind=f['kind'],features=json.dumps(f,ensure_ascii=False)) for c in cases for f in c['contract_features']]
    csv_file(root/'operation_clauses.csv',['operation_id','kind','features'],clauses)
    paths=[dict(operation_id=c['operation_id'],**f) for c in cases for f in c['cash_or_resource_paths']]
    csv_file(root/'operation_paths.csv',['operation_id','provider','receiver','kind','economic_flow_id','amount_reference','evidence'],paths)
    shared=[
        dict(guarantor='NVIDIA Corporation',operation='SB_PORTS',scope='Garantie de valeur résiduelle et coûts des phases initiales PORTS',window='Commencement du bail et conditions RFS',amount_basis='Plafond global conditionnel 105 Md$, décroissant ; formulaires expurgés'),
        dict(guarantor='NVIDIA Corporation',operation='IONIC_WARD',scope='Loyers du locataire Nscale Ward County',window='Années 1 à 5 du bail',amount_basis='Plafond 860,3 M$ ; dette GPU distincte'),
        dict(guarantor='Google LLC',operation='TERAWULF_FLUIDSTACK',scope='Loyers/terminaison de Fluidstack USA I',window='Commencement de chaque bail ; warrants nantis avant',amount_basis='Plafonds et risques par bâtiment incomplets'),
        dict(guarantor='Google LLC',operation='HUT_RIVER',scope='Certaines obligations de bail de Fluidstack USA IV',window='Bail River Bend',amount_basis='Obligations de bail ; aucune garantie Google des notes de Hut 8 DC'),
        dict(guarantor='Athene Holding Ltd.',operation='WHCO_CAPITAL_SOLUTION',scope='Obligation d’achat WHCO',window='Solde de l’obligation, financement prévu au plus tard en 2028',amount_basis='15 % du solde d’achat ; tiers rembourse 35 % des paiements effectués, non une réduction certaine du risque'),
        dict(guarantor='Meta, périmètre de publication',operation='HYPERION',scope='Valeur résiduelle de la VIE Louisiana',window='Non-renouvellement/résiliation ; baux commençant en 2029',amount_basis='28 Md$ de seuil initial, inclus dans 46,03 Md$ d’exposition composée'),
    ]
    csv_file(root/'operation_guarantors.csv',['guarantor','operation','scope','window','amount_basis'],shared)
    summary=dict(status='integrated_transaction_overlay',source_cutoff=cases[0]['source_cutoff'],historical_main_groups=26,
        additional_targeted_issuer_dossiers=4,operations=len(cases),authored_observations=len(notes),additional_native_facts=8,
        additional_documents=34,additional_identity_versions=23,additional_links_including_replacements=21,additional_measures=96,
        coverage_questions=len(coverage),verification=proof,amounts_not_additive=True,full_historical_reconstruction=False,
        private_contract_coverage_complete=False,negative_search_certificates=0,subagents_used=False,
        completed_at=datetime.now(timezone.utc).isoformat())
    save(root/'operation_summary.json',summary)
    body='''# Chaînes financières IA : onze dossiers transactionnels

Les six priorités retenues sont intégrées à une couche exploratoire distincte. **97 observations nouvelles, huit faits natifs supplémentaires et 88 réponses de couverture** documentent onze opérations. Les 26 groupes historiques sont conservés ; SB Energy, Nscale, Ionic Digital et Hut 8 ajoutent quatre dossiers ciblés, sans prétention de série historique exhaustive. La date limite reste le 9 octobre 2026 à 10:24:21 UTC. Travail effectué sans sous-agent.

## Les résultats qui changent la lecture du risque

**SB Energy : un paiement réel et des protections futures très différentes.** Nvidia a payé 1,5 Md$ à Energy Global le 17 août 2026 ; cette société a immédiatement apporté la même trésorerie à SB Energy. Ces deux étapes constituent un seul flux économique. Une souscription supplémentaire de 1,5 Md$ reste conditionnée à l’IPO. Le classement comptable des transactions était encore en cours d’évaluation dans le prospectus. Les formulaires de garantie PORTS confirment un plafond global de 105 Md$ pour les phases initiales et certains coûts de centre de données, d’électricité et de transmission. Ce plafond ne mesure ni une dette tirée ni une perte attendue. Commencement du bail, conditions de mise à disposition, défaut, réserves, assurance et recours au parent du locataire affectent les paiements. Plusieurs identités et paramètres sont expurgés. Le financement électrique porté hors des filiales SB Energy et les financements publics envisagés ne constituent pas une garantie souveraine constatée.

**Nscale/Ionic : le passage de l’engagement au revenu reste conditionnel.** Les contrats Anthropic annoncés jusqu’à 44,6 Md$ exigent acceptation écrite avant paiement. Le formulaire prévoit une condition de financement avec date limite expurgée et résiliation possible ; le prospectus n’annonce pas encore d’engagements de financement contraignants pour ces contrats. Les 2,54 Md$ de loyers initiaux associés aux 40 échéanciers DFS exécutés constituent des loyers bruts, incluant 34,8 M$ de charges financières, et ne mesurent pas un principal prêté. Chez Ward County, le covenant DSCR est 1,05 ; le blocage de trésorerie commence sous 1,10, avec un mécanisme après six mois et des limites aux cures. Aucun ratio réel ni marge disponible n’est calculé. Ionic confirme que les loyers fixes ont commencé en août 2026. Sa garantie Nvidia de 860,3 M$ porte sur les cinq premières années de loyers ; l’emprunteur GPU est une société distincte. Les clauses de reprise et les protections des années ultérieures demandent encore des contrats complémentaires.

**Hut 8 : les protections de bail ne garantissent pas les obligations.** Les notes River Bend de Hut 8 DC ont un principal de 3,25 Md$, celles de Beacon Point DC de 4,25 Md$. Les deux véhicules déclarent expressément que le parent et les locataires ne garantissent pas leurs notes. Le soutien Google du bail de Fluidstack USA IV à River Bend ne devient donc pas une garantie Google de cette dette. Le locataire de Beacon Point reste non nommé dans la pièce ouverte. Les premières échéances de principal interviennent en mai 2028 et mai 2030 respectivement, avec des maturités finales en 2042. Les 6,787 Md$ de trésorerie restreinte publiés au niveau du groupe sont principalement liés aux comptes de projets et lettres de crédit ; ils ne représentent pas une liquidité libre du parent ni une allocation intégrale à un seul projet.

**Cerebras/OpenAI : le contrat relie prêt, services et warrants.** Le prêt reçu de 1,004571 Md$ est affecté à la fourniture des services et matériels prévus par le MRA. Au 30 juin, l’encours est 918,244 M$ et les remboursements non monétaires cumulés sont 86,327 M$. Le revenu OpenAI du semestre est 74,4 M$ sur 373,516 M$ de revenu total, soit **19,9188 %**. Le ratio décrit une concentration de recettes. Les remboursements non monétaires, le revenu et les actifs liés aux warrants restent des grandeurs différentes. Les 822,9 M$ d’actifs liés aux warrants capitalisés sur le semestre ne sont pas un paiement de trésorerie de ce montant.

**WHCO/Broadcom/Athene : les bases des garanties ne coïncident pas.** La note d’Athene nomme Broadcom, Anthropic et WHCO dans la solution de capital de 35 Md$. Athene couvre 15 % du solde de l’obligation d’achat ; un tiers non nommé rembourse 35 % de ses paiements réalisés. La formule Broadcom est exprimée comme 85 % d’un solde de soutien de bail, diminué de la valeur de vente des racks. Ces bases différentes ne permettent pas une addition donnant « 100 % couvert ». Le maximum de 29 Md$ publié par Broadcom suppose le déploiement complet ; l’attribution juridique de chaque composante à WHCO reste partielle. Jusqu’à 42 Md$ de notes convertibles peuvent servir aux obligations de bail, mais aucune n’était émise au 2 août 2026.

**Nvidia/CoreWeave : capital, achats et soutien de capacité sont séparés.** Les 2 Md$ de souscription primaire payés en janvier et les 59,6 M$ de paiements de services au premier trimestre sont des flux constatés. Les 6,3 Md$ décrivent la valeur initiale de l’arrangement de capacité, avec achat éventuel du solde non vendu sous conditions. L’ancienne arête monétaire de backstop est conservée pour l’historique et remplacée dans la vue effective par un engagement commercial qualitatif. Les 17 % d’achats fournisseur ne sont pas un montant de revenu Nvidia attribuable à CoreWeave.

**TeraWulf/Fluidstack : la protection change au commencement.** Google peut payer une indemnité ou reprendre le bail après les événements prévus ; le soutien devient effectif au commencement de chaque location. Avant ce moment, le nantissement des warrants Google protège les financeurs de construction selon le dispositif publié. Une location était partiellement commencée à juin ; les autres étaient prévues fin 2026/début 2027. Fluidstack USA I chez TeraWulf et USA IV chez Hut 8 demeurent des personnes juridiques distinctes.

**Hyperion/Beignet : non-consolidation et absence de dette consolidée ne suppriment pas le risque.** Meta publie 46,03 Md$ d’exposition maximale composée à la VIE Louisiana : le seuil RVG initial de 28 Md$, les baux de 12,31 Md$, la participation comptable de 2,92 Md$ et les autres éléments ne s’y ajoutent pas une seconde fois. Le N-PORT ouvert identifie une seule position du PIMCO Extended Duration Fund : 1,517 M$ de nominal Beignet au 30 juin 2026, valorisés 1,5483237 M$. Cela ne mesure pas l’allocation totale de PIMCO. L’extrait S&P conservé nomme Beignet, Laidley, Iris Crossing et Pelican Leap et décrit une dette de holding sans sûreté directe sur tous les actifs de projet. Cet extrait indexé est une source d’agence qualitative, pas le contrat ni le texte intégral récupéré auprès de l’éditeur ; le montant annoncé de 27,3 Md$ n’entre pas comme nouvelle dette constatée dans le noyau.

**Lambda Compute I : dossier qualitatif, tirages inconnus.** La clôture annoncée d’une facilité de 1,008 Md$ à tirages différés ne prouve pas le décaissement de toute la somme. L’agence décrit deux clients de qualité investment grade non nommés, un financement par tranches, une stabilisation avant amortissement et des réserves plus faibles que la pratique habituelle. Le DSCR de 1,20 cité dans son analyse n’est pas un ratio observé. L’identité et l’allocation des prêteurs, les contrats clients et les recours restent manquants. Ces sources externes ne créent pas d’arête monétaire admise.

## Ce que les fichiers permettent de vérifier

`operation_evidence.csv` relie chaque observation à sa citation, son URL, son SHA, sa date, sa nature monétaire et, le cas échéant, au fait natif choisi. `operation_coverage.csv` détaille les 88 questions avec leurs limites. Les fichiers `operation_roles.csv`, `operation_clauses.csv`, `operation_paths.csv` et `operation_guarantors.csv` séparent personnes juridiques, mécanismes, étapes du cash et soutiens communs. Le registre des garants rapproche les dossiers sans addition de plafonds incompatibles. Les choix complets restent dans `work/dependencies/operations.json`.

Toutes les anciennes lignes des huit tables sont conservées ; les 19 invariants globaux passent. Les mesures ajoutées sont descriptives, de niveau 2, avec la variante `operation_dependencies_v1`. Les critères historiques E/F restent figés. Utiliser `operation_views.sql` pour écarter les anciennes arêtes explicitement remplacées dans une lecture actuelle.

Les recherches sont bornées aux opérations et pièces sélectionnées. La collecte d’un contrat ne garantit pas que toutes ses annexes ont été lues et structurées. Les parties expurgées, sous-contrats privés, allocations aux financeurs et valeurs récupérables empêchent encore de calculer une cascade complète de pertes. Aucun score agrégé, total de risque ou circuit causal de trésorerie n’est établi.

La notice `OPERATION_REPRODUCTION.md` décrit le rejeu hors ligne de cette extension et la différence entre vérification des lignes historiques conservées et reconstruction complète de l’histoire. Les preuves de tests et de rejeu sont livrées séparément ; le travail n’a pas fait l’objet d’un audit indépendant.
'''
    (root/'operation_dependencies.md').write_text(body)
    return summary

if __name__=='__main__':report(Path('.'))
