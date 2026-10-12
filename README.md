## Extension transactionnelle actuelle

Lire [le bilan des onze dossiers](operation_dependencies.md), [les règles de cette extension](DEPENDENCY_SPEC.md) et [sa reproduction](OPERATION_REPRODUCTION.md). Les 26 groupes historiques sont conservés ; quatre dossiers ciblés supplémentaires portent sur SB Energy, Nscale, Ionic Digital et Hut 8. La couche ajoute 97 observations et huit faits natifs, sans total agrégé de risque. Utiliser `operation_views.sql` pour la lecture actuelle des arêtes remplacées.

**État courant : 26 groupes, avec les corrections de l’audit du 12 octobre.** Lire [les apports ciblés](targeted_priorities.md) : prêteurs, garanties et résolution de l’identité de Vernon — Lambda. Sources arrêtées au 9 octobre 2026 ; huit tables communes et archives antérieures conservées.

# SEC_Project_2

Modèle courant : **26 groupes principaux**, avec SMCI, Dell et SoftBank intégrés dans les huit tables. Lire [le rapport SMCI](smci_integration.md), [sa synthèse](smci_summary.json) et [ses mesures](smci_measures.csv). Les 25 groupes précédents sont conservés ; les sources restent arrêtées au 9 octobre 2026 et les critères E/F sont inchangés.

L’extension ciblée ajoute 56 observations, les positions d’Ares Core Infrastructure Fund et de BlackRock Private Credit Fund, deux garanties conditionnelles CoreWeave/APLD et l’identité documentaire de Lambda à Vernon. Les positions des prêteurs et l’investissement SMCI nouvellement attribué ne sont pas ajoutés aux montants déjà enregistrés. Les sources et tableaux antérieurs sont conservés ; [reproduction du lot ciblé](TARGETED_REPRODUCTION.md).

## Résultat actuel et relance locale

Utiliser **current.json** comme point d’entrée : il désigne une génération complète, validée, de huit tables. `tables/` est un lien vers ce même dossier. Pour lire plusieurs tables pendant une autre exécution, résoudre ce lien une fois et conserver le chemin du dossier immuable. Les générations précédentes sont conservées dans `work/table_generations/`. La coupure reste le 9 octobre 2026, 10:24:21 UTC ; 26 groupes principaux, hors identifiants auxiliaires et paires.

L’audit reçu et le traitement des douze constats figurent dans [AUDIT_RESPONSE.md](AUDIT_RESPONSE.md). Le dossier `audit/` et les anciennes archives conservent des instantanés historiques ; leurs tables ne remplacent pas la génération courante. Les preuves courantes sont `work/audit_20261012/final_invariants.json`, `source_preflight.json` et `test_attestation.json`. [Le protocole actuel](AUDITOR_CURRENT.md) précise leur périmètre.

Installation testée : **Python 3.12.14, Linux**, `python -m pip install -r requirements.txt`, puis `python -m pytest -q`. Chaque connexion de calcul utilise UTC. Les paquets acceptent `--output /dossier/choisi` ; le défaut est `output/` du projet. Le changement atomique d’un dossier préexistant utilise `renameat2` sous Linux ; sur un système qui ne le permet pas, l’opération échoue en conservant le résultat précédent.

Avant une reconstruction historique complète, restaurer les sauvegardes d’originaux et exécuter `python -m secfragility.source_registry`. Ce contrôle vérifie les SHA à partir des fichiers et archives disponibles, sans requête SEC. Les 44 réponses submissions exactes sont sauvegardées dans `work/audit_20261012/submission_metadata.tar.zst`. Les fichiers portant les mêmes SHA sous un autre emplacement sont enregistrés et peuvent être rematérialisés par le résolveur. Le contrôle de disponibilité ne signifie pas que tous les originaux ont déjà été décompressés sur le disque.

Les étapes intermédiaires de `phase3` ne sélectionnent pas un nouveau résultat courant. Seul le jeu complet, après toutes les extensions et la validation globale, est publié. Une reprise refuse un checkpoint si le code, les entrées déclarées ou les dépendances ont changé. Les archives qui se présentent comme testées exigent une attestation fraîche liée au code, aux entrées et aux tables réellement testés.

## Base SEC et étapes précédentes

Les 398 blocs complémentaires sont tous traités, sans sous-agent. L’inventaire des entités ajoutées couvre désormais 465 notes uniques lues sur 465 ; 23 groupes principaux sont suivis. Sources arrêtées au 9 octobre 2026, 10:24:21 UTC, critères inchangés.

Lire [user_brief_398.md](user_brief_398.md), puis [bilan_398_blocs.md](bilan_398_blocs.md). Les conclusions individuelles et les citations figurent dans revue_398_blocs.csv. Les notes historiques et les contrats au-delà de ce lot ne sont pas déclarés entièrement lus. Aucun total d’exposition, score global ou audit indépendant n’est revendiqué.

Les huit tables sont dans tables/, les critères et contrôles dans audit/, les observations dans work/observations/. L’archive de cette livraison est SEC_Project_2_398_blocs.zip ; les archives antérieures sont distinctes.

## Reproduction

Installer requirements.txt. Restaurer les sauvegardes LFS de sources avec leurs manifestes SHA-256, sans écraser les observations et décisions plus récentes. python -m secfragility.phase3 --reconstruct reconstruit depuis le cache, sans requête SEC ni appel de modèle. python -m pytest -q exécute les tests. work/idempotency_verification.json compare les huit tables avec une référence créée après intégration des 398 blocs, toutes colonnes et provenance incluses.

## Intégration SoftBank — sources officielles japonaises

Cette livraison historique correspondait au modèle à 24 groupes. Lire [softbank_integration.md](softbank_integration.md). Les huit tables contiennent la base SEC intacte et les données SoftBank qualifiées ; [softbank_summary.json](softbank_summary.json) donne les contrôles et la couverture. `python -m secfragility.softbank_integration` reconstruit cette extension depuis le checkpoint SEC immuable et les sources japonaises conservées. `python -m secfragility.phase3 --reconstruct` conserve la reconstruction complète depuis le cache SEC, puis applique la même extension.
