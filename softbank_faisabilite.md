# SoftBank — faisabilité de l’intégration

**Oui : les sources disponibles permettent une analyse utile de SoftBank Group, de son financement et de ses investissements IA.** Cette première étape a récupéré 43 PDF officiels, principalement les rapports financiers trimestriels en anglais et les rapports réglementaires japonais depuis FY2021. Elle a aussi produit un inventaire SEC et un pilote de 11 observations avec pages, citations et empreintes de fichiers.

Il s’agit d’une préparation à l’intégration. Les 43 PDF ne sont pas déclarés entièrement lus et SoftBank n’est pas encore ajouté aux calculs principaux. Le lot des 398 blocs terminé précédemment reste terminé.

## La modification méthodologique à expliciter

La spécification v6.14, §2.2 et §2.6, réserve les calculs aux pièces EDGAR admissibles ; les documents hors EDGAR sont des pointeurs de niveau F. Notre inventaire des soumissions de SoftBank Group, CIK 0001065521, trouve des dépôts depuis 2021, notamment des 13F et déclarations de participations, mais aucun 10-K, 10-Q, 20-F ou 6-K dans la fenêtre examinée. Les 13F ne fournissent pas son bilan, sa dette et toute son exposition aux sociétés privées.

L’intégration substantielle demande donc une extension aux sources japonaises. Le contrat préparé dans work/softbank/integration_contract.json distingue une vue **EDGAR d’origine** et une vue **sources officielles japonaises étendues**. Les seuils de l’annexe E, les événements de l’annexe F et les interdictions de double compte restent inchangés. Le pilote n’a modifié aucune des huit tables de la livraison précédente.

L’arrêt des informations retenues reste celui du modèle : **9 octobre 2026, 12 h 24 à Paris**. Les nouvelles captures ont été réalisées le 12 octobre : leur date de récupération est conservée séparément. Une publication antérieure ne garantit pas que la version actuellement disponible était identique à cette date ; les versions et corrections doivent être vérifiées avant une utilisation historique `as_known`.

## Sources et apport attendu

| Source | Ce qu’elle peut apporter | Point de contrôle |
|---|---|---|
| Rapports annuels réglementaires japonais | Comptes, dettes, échéances, participations, garanties, engagements, parties liées et risques | Vérifier les identifiants EDINET, dépôts et amendements ; distinguer les comptes consolidés des comptes de la société mère |
| Rapports financiers annuels détaillés en anglais | Lecture des notes IFRS et tableaux de financements | Rapprocher les traductions des originaux japonais et vérifier la date de publication |
| Rapports intérimaires | Actualisation des soldes, mouvements et événements ultérieurs | Limiter l’assurance au périmètre effectivement revu |
| Présentations finance, feuilles de données et conférences | NAV, LTV de la holding, portefeuille des fonds, stratégie de financement | Définitions propres à SoftBank ; ne pas traiter un indicateur ajusté comme le bilan consolidé |
| Communiqués et conditions d’émissions | Chronologie des contrats annoncés, tranches exécutées, refinancements et annulations | Différencier déclaration de l’émetteur, contrat complet et preuve comptable du paiement |
| SEC : SoftBank, Arm et contreparties du modèle | Identités, participations publiques et confirmations provenant de l’autre côté d’une relation | Une contrepartie anonyme ne devient pas SoftBank par supposition |

Le rapport annuel japonais FY2025 décrit un exercice du 1er avril 2025 au 31 mars 2026 et un dépôt du 22 juin 2026. Son préambule le présente comme une impression des données déposées via EDINET, avec rapports d’audit annexés. La copie archivée provient du site de l’émetteur ; la comparaison indépendante avec les octets du régulateur reste à effectuer. [Rapport réglementaire japonais](https://group.softbank/media/Project/sbg/sbg/pdf/ir/financials/security_reports/securities_report_q4fy2025_01_ja.pdf).

Le rapport de juin contient une revue de Deloitte sur les états et notes de l’Appendix. Il précise que certaines informations IAS34 sont omises selon les règles TSE : cette assurance ne doit pas être étendue automatiquement au narratif entier ou aux présentations investisseurs. [Rapport financier de juin, pages PDF 45 et 72](https://group.softbank/media/Project/sbg/sbg/pdf/ir/financials/financial_reports/financial-report_q1fy2026_01_en.pdf).

## Les quatre priorités qui apporteraient le plus de signal

**1. Reconstituer l’investissement dans OpenAI et son financement, opération par opération.** Séparer l’engagement global, chaque tranche effectivement exécutée, les tirages bancaires, les remboursements et les valeurs comptables. Le communiqué du 1er octobre indique que la dernière tranche a été exécutée, les emprunts du bridge remboursés et la capacité non tirée annulée. Une lecture arrêtée aux annonces de mars ou aux soldes de juin donnerait une image différente. Cette déclaration doit garder son statut de communiqué et être rapprochée des pièces financières et des émissions qui remplacent les crédits. [Déclaration du 1er octobre](https://group.softbank/en/news/press/20261001).

**2. Distinguer les prêts adossés à Arm des financements faisant référence à OpenAI.** La note annuelle décrit un emprunt de Kronos I (UK), avec actions Arm nanties, cash collateral et remboursement anticipé possibles ; elle le qualifie sans recours à SoftBank Group. Le rapport de juin décrit séparément SVF II TSUBAKI (DE) LLC, SoftBank Group comme garant et des clauses liées à une baisse de valeur des actions privilégiées OpenAI. Le tirage y est encore attendu ; son exécution et son solde actuel restent à confirmer. Ce sont des structures de recours différentes. [Note annuelle de dette, page PDF 67](https://group.softbank/media/Project/sbg/sbg/pdf/ir/financials/annual_reports/financial-report_fy2026_en.pdf), [note intérimaire, page PDF 71](https://group.softbank/media/Project/sbg/sbg/pdf/ir/financials/financial_reports/financial-report_q1fy2026_01_en.pdf).

**3. Séparer les ressources de la holding de celles des filiales et des fonds.** SoftBank Group et SoftBank Corp. sont deux entités différentes. Les notes expliquent la consolidation de SVF1, SVF2 et LatAm et l’élimination des transactions internes. Les droits des investisseurs externes, les contributions non cash, les créances sur co-investisseurs et les fonds affectés peuvent limiter ce qui est mobilisable par la mère. Le LTV présenté par la direction doit être rapproché de son propre périmètre, pas assimilé au levier comptable de tout le groupe. [Politiques de consolidation, pages PDF 15 et 27](https://group.softbank/media/Project/sbg/sbg/pdf/ir/financials/annual_reports/financial-report_fy2026_en.pdf).

**4. Relier les investissements aux projets et fournisseurs effectivement documentés.** OpenAI, Arm, Ampere et les projets d’infrastructure sont des pistes prioritaires. Stargate doit être suivi par société de projet, contrat, engagement et paiement : son budget annoncé ne mesure pas automatiquement l’engagement financé de SoftBank. Le prêt de SVF2 nomme notamment Apollo Global Funding parmi les chefs de file ; cette fonction ne révèle pas à elle seule la part prêtée par Apollo. [Projet Stargate](https://group.softbank/en/news/press/20250122), [table du financement SVF2, page PDF 71](https://group.softbank/media/Project/sbg/sbg/pdf/ir/financials/financial_reports/financial-report_q1fy2026_01_en.pdf).

## Limites à conserver dans le modèle

Les documents publics ne garantissent pas l’accès aux contrats complets, aux seuils chiffrés d’appels de collatéral, aux valorisations retenues par les banques, à tous les accords confidentiels avec OpenAI ou aux expositions par prêteur. Ces champs doivent rester non déterminés lorsqu’ils ne sont pas publiés. Une variation de juste valeur n’est pas un encaissement et une présentation en dollars de convenance n’est pas une deuxième exposition à ajouter aux montants en yens.

Le financement et la trésorerie sont les axes les plus prometteurs. La collecte publique est déjà substantielle ; le travail délicat sera de qualifier chaque source, résoudre les périmètres et reconstituer les opérations sans double compte.

## Fichiers préparés

- softbank_sources.csv : inventaire des sources, chemins, tailles, empreintes et état de lecture.
- softbank_pilote.csv : 11 observations contrôlées, avec source et page PDF.
- work/softbank/sec_inventory.json : soumissions SEC et distribution des formulaires dans la fenêtre.
- work/softbank/integration_contract.json : extension proposée et règles de comparaison.
- work/softbank/feasibility.json : contrôles du pilote et limites restantes.

Travail effectué par l’assistant unique, sans sous-agent. Les sources et le code de collecte sont conservés dans le dépôt ; aucun audit indépendant n’est revendiqué.
