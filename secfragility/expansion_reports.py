"""A dated first review of the added issuers, with explicit reading coverage."""
from collections import Counter
from decimal import Decimal
from pathlib import Path
import json
from .assembly import rows
from .reports import csv_write

def render(db,root,as_of):
    scope=json.loads((root/'work/expansion/reading_scope.json').read_text())
    issuers=json.loads((root/'work/expansion/issuers.json').read_text())
    q=json.loads((root/'work/expansion/queue.json').read_text());active=set(scope['active_keys'])
    evidence=[r for r in rows(db,"SELECT o.*,d.url,d.incorporated_by_reference FROM observations o LEFT JOIN documents d USING(document_id) ORDER BY o.accession,o.observation_id") if r['content_key'] in active]
    csv_write(root/'expansion_evidence.csv',evidence)
    coverage=[];by_key={}
    for r in q:
        b=json.loads((root/r['path']).read_text());by_key[r['content_key']]=b
        coverage.append(dict(group=r['group'],accession=r['accession'],content_key=r['content_key'],
            label=b.get('label'),knowledge_date=r['knowledge_date'],chars=r['chars'],
            state='read' if r['content_key'] in active else 'not_processed',
            original_source_path=b['source_path'],raw_byte_start=b['raw_byte_start'],raw_byte_end=b['raw_byte_end']))
    csv_write(root/'expansion_note_coverage.csv',coverage)
    def source(prefix):
        b=next(b for k,b in by_key.items() if k.startswith(prefix))
        return next(r['url'] for r in evidence if r['content_key']==b['content_key'])
    def note(prefix):return next(b for k,b in by_key.items() if k.startswith(prefix))
    # Bind the major amounts to original, already reviewed cells. The rejected
    # IREN 12m citation is not promoted to an accepted semantic observation.
    assertions=[('cfb175d9d48b','13611035000'),('cfb175d9d48b','13810037000'),
                ('78350f3e9ea7','2169300000'),('012636436f12','1000000000')]
    for prefix,value in assertions:
        assert any(f['value'] is not None and Decimal(str(f['value']))==Decimal(value)
            and f['period_end']=='2026-06-30' for f in note(prefix)['candidates']),(prefix,value)
    cf=note('156dd1043209')['text']
    for exact in ['4,504.1','4,395.0','(8,130.3)','8,042.1','1,056.0']:
        assert exact in cf,exact
    registry=[]
    for cik,item in sorted(issuers.items()):
        parent=rows(db,"""SELECT entity_id,economic_group_id,consolidation_treatment,resolution_rule FROM entities
          WHERE cik=? AND alias_key='none' AND (membership_end IS NULL OR membership_end>?::TIMESTAMPTZ::DATE)
          ORDER BY membership_start DESC NULLS LAST""",[cik,as_of])
        if cik=='0001527469':
            assert parent and parent[0]['economic_group_id']=='external:0001858681','Athene parent membership not established'
        registry.append(dict(cik=cik,name=item['name'],group_id=item['group'],
            main_group=cik!='0001527469',economic_group_id=parent[0]['economic_group_id'] if parent else None,
            consolidation_treatment=parent[0]['consolidation_treatment'] if parent else None,
            periodic_sources_collected=len(item['periodic_filings']),notes_inventory_filings=len(item['text_filings']),
            historical_notes_state='not_processed',latest_annual_accession=item['latest_annual']['accessionNumber']))
    csv_write(root/'expansion_entities.csv',registry)
    groups=[s['group'] for s in issuers.values() if s['group']!='external:0001527469']
    metrics=rows(db,"""SELECT * FROM measures WHERE group_id IN (SELECT unnest(?)) AND view='revised'
        AND measure IN ('revenue_total','cfo','capex_cash','fcf_basic','fcf_after_finance_leases',
        'finance_lease_principal_payments','liq_principal_due_to_cash','liq_cash_to_12m_outflows')
        QUALIFY period_end=max(period_end) OVER(PARTITION BY group_id,measure)
        ORDER BY group_id,measure,period_start,breakdown_key""",[groups])
    csv_write(root/'expansion_financial_metrics.csv',metrics)
    lender=[r for r in evidence if r.get('model_quantity') in ('lender_position_non_accrual_status','lender_position_PIK_terms','lender_non_accrual_schedule_legend','lender_PIK_schedule_legend')]
    csv_write(root/'expansion_lender_classification.csv',lender)
    main_count=len(json.loads((root/'work/inventory.json').read_text())['groups'])
    assert main_count==23 and len(groups)==12
    verification=json.loads((root/'work/delivery_verification.json').read_text())
    mismatches=sum(r['n'] for r in verification['accounting_mismatches'])
    blocked=len(verification['localized_invalid_aggregates'])
    manifest=dict(source_cutoff=as_of,main_groups=main_count,added_main_groups=len(groups),additional_reporter='Athene Holding Ltd.',
        periodic_sources=sum(len(s['periodic_filings']) for s in issuers.values()),
        supplemental_6k_sources=sum(len(s['supplemental_6k']) for s in issuers.values()),
        reading=scope,accepted_expansion_observations=len(evidence),
        delivery_checks=verification['checks'],accounting_mismatch_rows=mismatches,
        localized_invalid_aggregates=blocked,
        all_notes_exhaustively_reviewed=False,complete_contract_review=False,
        source_specific_6k_incorporation_proof=True,independent_audit_performed=False)
    (root/'expansion_summary.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    report=f'''# Entités ajoutées — première analyse

Le périmètre comprend désormais **23 groupes principaux**, contre 11 auparavant. Les 12 nouveaux groupes sont identifiés par leur CIK officiel. Athene est étudiée avec ses propres comptes et rattachée au groupe économique Apollo par une preuve de contrôle. WHCO, les véhicules CTP02/CTP03 et les sociétés de projet Helios restent distincts de leurs gestionnaires ou sociétés mères dans les preuves et les montants.

**Arrêt des sources inchangé : 9 octobre 2026, 10:24:21 UTC.** Ce rapport utilise seulement les dépôts connus avant cet arrêt. Un événement postérieur à la clôture, mais publié avant l'arrêt, reste identifié comme événement ultérieur ; il ne modifie pas le bilan à la clôture.

| Entité / périmètre | Signal établi par cette première lecture | Point à approfondir |
|---|---|---|
| **Core Scientific** | Environ **1 Md$** d'engagements d'achats/construction, essentiellement sur douze mois ; **264 M$** refacturables au client. Dette de projet de **3,3 Md$** et garantie d'achèvement parentale **non plafonnée**. Un client de colocation anonyme représente **83 %** du revenu consolidé au T2 et 77 % au S1. [Notes]({source('012636436f12')}) | Livraison, crédits de revenus différant l'amortissement, trésorerie réellement disponible. Les baux AMD de juillet apportent une nouvelle contrepartie ; son droit de remédier à des défauts d'un neocloud reste facultatif. |
| **Applied Digital** | Amortissement des nouveaux prêts lié au démarrage des baux. Le véhicule TopCo 2 est consolidé ; ses créanciers ont un recours au crédit général du groupe malgré sa qualification bankruptcy-remote. **82,4 M$** tirés et **241 M$** de lettres de crédit sur le revolver de 430 M$. [Dette]({source('92ceeeb2598d')}) | Recours par véhicule, coûts jusqu'à livraison et actions privilégiées rachetables : **60,1 M$** de dividendes PIK sur le trimestre clos en août. Les 35,73 Md$ de loyers contractuels agrégés ne sont pas tous attribuables à CoreWeave. |
| **Apollo / Athene / WHCO** | WHCO porte une obligation d'achat dans une opération de **35 Md$**. Athene garantit **15 % de l'obligation d'achat restant en cours**. Son passif au titre de la garantie est nul parce que le paiement n'est pas jugé probable. [Athene]({source('7f299aba57b5')}) | Solde exact garanti et financement par tranche. Le remboursement par un tiers de 35 % des paiements effectifs reste conditionnel ; aucune exposition nette de 3,41 Md$ n'est calculée à partir du montant nominal de l'opération. |
| **TeraWulf** | Soutien Google aux obligations de Fluidstack activé au commencement de chaque bail ; selon le contrat, paiement de la résiliation ou reprise du bail. **515,5 M$** d'actif différé lié aux warrants remis à Google. Le revolver de 250 M$ est plafonné à **75 M$** avant le premier commencement. [Baux]({source('5922174dfa89')}) | Vérifier séparément les clauses avant/après livraison et les prêts de projet. Le nouveau bail direct Anthropic est distinct des baux Fluidstack soutenus par Google. Les 90 M$ de loyers prépayés par Core42 ont été reçus au S1 2025. |
| **Backblaze** | Contrat CoreWeave de **335,1 M$**, diminué dans les RPO d'environ **21,7 M$** de juste valeur des warrants. Les **4 194 876** warrants doivent réduire les revenus futurs ; aucun revenu lié au contrat ni réduction correspondante n'était reconnu au 30 juin. Revolver de 20 M$ non tiré. [Warrants]({source('3d8f5628e845')}) | Mesurer la dépendance commerciale future et la marge après cette contrepartie au client. Les RPO de 396 M$ comprennent d'autres clients et un changement de périmètre de présentation. |
| **Galaxy Digital / Helios** | Phase I : **133 MW** livrés à CoreWeave sous un bail de 15 ans. Engagements de construction de **1,489 Md$** au 30 juin. Helios I : prêt plafonné à 1,4 Md$, principal de **1,268 Md$** en juin. Helios II : émission ultérieure de **3,507 Md$ à 9,875 %** en juillet, avec garantie d'achèvement **non plafonnée**. [Projet]({source('7aa8c556ad09')}) | Distinguer Helios I et II, les dates de livraison et la trésorerie du segment. Le bénéfice net S1 de Helios inclut 32,45 M$ d'avantage fiscal ; le résultat avant impôt est une perte de 2,842 M$. |
| **Blue Owl Real Estate Net Lease Trust / CTP02–CTP03** | Les véhicules Project Spider/CTP02–CTP03 sont identifiés dans les preuves historiques conservées. Le dépôt de juin publie des JVs agrégées et **1,728 Md$** d'engagements de construction build-to-suit jusqu'en 2029. [Engagements]({source('7d86a80cb0d8')}) | Rapprocher les anciennes désignations de véhicules avec les actifs et participations actuels. Le montant agrégé de juin ne peut être attribué intégralement aux seuls véhicules CoreWeave ; leur absence nominative dans ce dépôt ne prouve pas leur cession. |
| **Great Elm Capital** | Tableau complet de juin et toutes ses légendes lus. Les trois prêts CoreWeave examinés et l'obligation non garantie ne portent ni le marqueur PIK ni celui de non-accrual. Engagement non tiré de **4,836 M$** envers Coreweave Financing V. [Portefeuille]({source('92ae097cc3f5')}) | Le coût et la juste valeur décrivent la position du prêteur, pas la taille de la facilité de l'emprunteur ni un versement primaire. La part d'intérêts PIK réellement encaissés/capitalisés reste non déterminée. |
| **MSD Investment Corp.** | La ligne CoreWeave DDTL de juin présente **26,669 M$ de coût** et **26,950 M$ de juste valeur** ; aucun marqueur de non-accrual ou coupon PIK sur cette ligne. Le seul investissement du fonds marqué non-accrual est identifié ailleurs dans le tableau, pas comme CoreWeave. [Portefeuille]({source('a5d6f1ead7b1')}) | Les positions et l'engagement non tiré publiés en décembre ont changé ; leur disparition ne suffit pas à distinguer remboursement, vente ou reclassement. Le nom commercial ne détermine pas à lui seul la personne juridique emprunteuse. |
| **IREN** | **13,810 Md$** d'engagements de hardware IA/infrastructure, dont **13,611 Md$ à douze mois**. Financement GPU pour Microsoft plafonné à **3,645 Md$**, dont **938 M$** financés en juin ; le solde dépend de conditions de livraison. Avances de loyers reçues : **1,623 Md$**, sans revenu locatif reconnu en juin. [Dette]({source('e7ceb2128e71')}) | Alignement entre paiements aux fournisseurs, acceptation des tranches par Microsoft et déblocage des fonds. La structure annoncée sans recours conserve des garanties parentales spécifiques, dont un mécanisme en cas de terminaison et d'échec du replacement. Le financement d'août allant jusqu'à 2,4 Md$ reste distinct du bilan de juin. |
| **Nebius** | Au S1 : **4,504 Md$ de CFO**, comprenant **4,395 Md$ de variation des revenus différés**, face à **8,130 Md$** d'achats de PPE et d'incorporels. Trésorerie et équivalents **8,042 Md$**, cash restreint **1,056 Md$**. Loyers non commencés : **12,054 Md$** non actualisés. [États de juin]({source('156dd1043209')}) | La croissance absorbe des avances clients, des émissions de titres et de dette. NVIDIA a apporté 2 Md$ ; le contrat Meta de 12 Md$ de capacité dédiée est distinct d'un achat de capacité résiduelle allant jusqu'à 15 Md$. La durée de vie des serveurs passe de quatre à cinq ans : baisse de dépréciation S1 de 86,1 M$, sans économie de cash correspondante. |
| **Cipher Mining, devenu Cipher Digital** | CIK inchangé. **2,169 Md$** d'engagements de construction ; aucun revenu des trois baux HPC au 30 juin. Garantie Google des obligations de Fluidstack rémunérée par warrants : actif initial de **544,5 M$**, avec un plancher de valeur des warrants de **430 M$** pouvant imposer actions supplémentaires ou cash. [Warrants]({source('9f508e6fc48c')}) | Risque de livraison et condition de valeur des warrants. Le revolver de 200 M$ est plafonné à 50 M$ avant livraison ; les lettres de crédit de 33,1 M$ font partie de cette capacité. |

Les points qui apportent le plus de signal sont les **recours parentaux avant livraison**, les **conditions de mobilisation des financements** et le **rôle des avances clients**. Ils relient la construction des actifs à la solvabilité et aux décisions des clients. Les warrants ne suivent pas tous le même traitement : réduction de revenu chez Backblaze, coût d'un soutien de crédit différé chez TeraWulf et Cipher, traitement encore en cours d'évaluation chez Core Scientific.

Il n'existe ici **ni score global de fragilité ni somme d'exposition de la chaîne**. Dette consolidée, dette de projet incluse dans cette consolidation, engagements d'achat, loyers et garanties ne sont pas additionnés. Un ratio de juste valeur supérieur au coût ne prouve pas l'absence de stress ; une absence de non-accrual publié porte seulement sur la ligne et la date examinées.

La lecture de juin Nebius est de **niveau C** : le 6-K incorpore expressément l'annexe 99.2 par référence, mais les états restent non audités et aucune revue d'auditeur n'est supposée. Ses chiffres non balisés sont conservés dans les citations et ce commentaire ; ils ne fabriquent pas une série XBRL ou un TTM. Le dépôt annuel décrit certaines convertibles comme réglées en actions, alors que la note de juin mentionne un choix cash/actions : cette différence est conservée et les contrats restent à vérifier.

Les anciens comptes Yandex en roubles et les comparatifs Nebius publiés en dollars restent distincts. La série scalaire retient la présentation la plus récemment publiée à sa date de connaissance, et s'abstient lorsque cette date laisse plusieurs bases possibles. Les snapshots historiques conservent leur date de première publication ; aucun change ni taux de croissance organique IA entre activités différentes n'est déduit.

Couverture : **{manifest['periodic_sources']} dépôts périodiques collectés** depuis les exercices clos en 2021, plus **{manifest['supplemental_6k_sources']} dépôts 6-K Nebius**. L'inventaire courant contient **{scope['nominated_unique_keys']} blocs uniques** : **{scope['active_unique_keys']} lus**, y compris les preuves déjà lues, et **{scope['deferred_unique_keys']} explicitement non traités**. Les notes historiques et les contrats complets restants ne sont pas déclarés lus. Le tableau expansion_note_coverage.csv conserve cette distinction par source et par bloc.

Les identités sont dans expansion_entities.csv ; les citations et leurs octets sources dans expansion_evidence.csv ; les mesures standard de dernière période dans expansion_financial_metrics.csv ; les classifications de prêteurs dans expansion_lender_classification.csv. Les valeurs ND gardent leurs raisons. Les données et conclusions de la tranche précédente restent accessibles dans l'historique Git et ses archives.

Les **{len(verification['checks'])} vérifications de livraison** passent et les cellules attendues sont présentes. Les rapprochements conservent **{mismatches} lignes de contrôle présentant un écart**, ainsi que **{blocked} agrégat local bloqué**. Ces alertes de précision ou de comparabilité restent dans audit/controls.csv et work/delivery_verification.json ; elles ne constituent pas une opinion d'audit sur les comptes des déposants. Les contrôles de livraison ne signifient pas que tous les rapprochements comptables aboutissent.
'''
    (root/'entites_ajoutees.md').write_text(report)
    (root/'user_brief_expansion.md').write_text(f'''# Ajout des entités — point d'étape

Le périmètre passe de **11 à 23 groupes principaux**. Athene est documentée séparément au sein d'Apollo ; WHCO, CTP02/CTP03 et les véhicules Helios gardent leurs propres identités et bases d'exposition.

Trois constats dominent :

- **Le risque avant livraison remonte vers les sociétés mères.** Core Scientific et Galaxy publient des garanties d'achèvement non plafonnées. Chez IREN, la structure de financement annoncée sans recours conserve des garanties spécifiques en cas de terminaison et d'échec du replacement.
- **La trésorerie dépend du calendrier des clients et des financeurs.** IREN publie 13,611 Md$ d'engagements à douze mois, tandis que certaines ressources dépendent de conditions. Chez Nebius, 4,395 Md$ de variation des revenus différés contribuent aux 4,504 Md$ de trésorerie opérationnelle S1.
- **Les warrants ont des effets différents selon l'opération.** Ceux de Backblaze réduiront ses revenus ; ceux de TeraWulf et Cipher rémunèrent un soutien de crédit. Les prêts CoreWeave examinés chez Great Elm et MSD ne sont pas marqués non-accrual en juin.

Voir [entites_ajoutees.md](entites_ajoutees.md) pour les douze fiches, les sources et les limites. Cette première analyse couvre {scope['active_unique_keys']} blocs naturels lus ; {scope['deferred_unique_keys']} autres blocs collectés restent explicitement non traités. L'historique structuré est collecté depuis 2021. Les critères et l'arrêt des sources du 9 octobre restent inchangés.

Sauvegardes régulières sur [GitHub](https://github.com/jsiaut/codex_test). Travail effectué seul, sans audit indépendant.
''')
    (root/'README.md').write_text(f'''# SEC_Project_2

Le périmètre principal comprend 23 groupes, dont 12 ajoutés dans cette livraison. Lire [user_brief_expansion.md](user_brief_expansion.md), puis [entites_ajoutees.md](entites_ajoutees.md). Les résultats antérieurs restent dans l'historique Git et dans leurs archives distinctes.

Les sources sont arrêtées au 9 octobre 2026, 10:24:21 UTC. La première tranche des entités ajoutées comprend {scope['active_unique_keys']} blocs naturels lus et {scope['deferred_unique_keys']} autres blocs explicitement non traités ; l'inventaire et les originaux sont conservés. La lecture des notes et contrats n'est pas exhaustive. Athene est rattachée économiquement à Apollo par une preuve de contrôle ; les fonds gérés, les JVs et les véhicules de projet gardent leurs identités distinctes. Aucun score global ni total d'exposition n'est calculé. Aucun audit indépendant n'est revendiqué.

Les huit tables sont dans tables/. Les observations sont dans work/observations/, les critères et contrôles dans audit/, et la couverture détaillée dans expansion_note_coverage.csv. Les fichiers expansion_evidence.csv, expansion_entities.csv, expansion_financial_metrics.csv et expansion_lender_classification.csv donnent les citations, identités, mesures et classifications. Les ND conservent leurs raisons.

## Reproduction

Installer requirements.txt et restaurer les sauvegardes de sources LFS avec leurs manifestes SHA-256, sans écraser les observations plus récentes. Les sauvegardes complémentaires contiennent aussi les nouveaux originaux et les notes différées. Depuis la racine, python -m secfragility.phase3 --reconstruct reconstruit depuis le cache, les observations et les décisions versionnées, sans requête SEC ni appel de modèle. python -m pytest -q exécute les tests. Le résultat de la comparaison des huit tables après reconstruction complète figure dans work/idempotency_verification.json.

Les commits intermédiaires enregistrent le travail ; le commit final et ses contrôles établissent la livraison. Les captures d'API sont figées et ne sont pas supposées récupérables à l'identique ultérieurement. L'archive de cette tranche porte le nom SEC_Project_2_entites_ajoutees.zip.
''')
    return manifest
