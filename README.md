**État courant : 26 groupes, avec les trois priorités intégrées.** Lire [les apports ciblés](targeted_priorities.md) : prêteurs, garanties et résolution de l’identité de Vernon — Lambda. Sources arrêtées au 9 octobre 2026 ; huit tables communes et archives antérieures conservées.

# SEC_Project_2

Modèle courant : **26 groupes principaux**, avec SMCI, Dell et SoftBank intégrés dans les huit tables. Lire [le rapport SMCI](smci_integration.md), [sa synthèse](smci_summary.json) et [ses mesures](smci_measures.csv). Les 25 groupes précédents sont conservés ; les sources restent arrêtées au 9 octobre 2026 et les critères E/F sont inchangés.

L’extension ciblée ajoute 56 observations, les positions d’Ares Core Infrastructure Fund et de BlackRock Private Credit Fund, deux garanties conditionnelles CoreWeave/APLD et l’identité documentaire de Lambda à Vernon. Les positions des prêteurs et l’investissement SMCI nouvellement attribué ne sont pas ajoutés aux montants déjà enregistrés. Les sources et tableaux antérieurs sont conservés ; [reproduction du lot ciblé](TARGETED_REPRODUCTION.md).

## Base SEC et étapes précédentes

Les 398 blocs complémentaires sont tous traités, sans sous-agent. L’inventaire des entités ajoutées couvre désormais 465 notes uniques lues sur 465 ; 23 groupes principaux sont suivis. Sources arrêtées au 9 octobre 2026, 10:24:21 UTC, critères inchangés.

Lire [user_brief_398.md](user_brief_398.md), puis [bilan_398_blocs.md](bilan_398_blocs.md). Les conclusions individuelles et les citations figurent dans revue_398_blocs.csv. Les notes historiques et les contrats au-delà de ce lot ne sont pas déclarés entièrement lus. Aucun total d’exposition, score global ou audit indépendant n’est revendiqué.

Les huit tables sont dans tables/, les critères et contrôles dans audit/, les observations dans work/observations/. L’archive de cette livraison est SEC_Project_2_398_blocs.zip ; les archives antérieures sont distinctes.

## Reproduction

Installer requirements.txt. Restaurer les sauvegardes LFS de sources avec leurs manifestes SHA-256, sans écraser les observations et décisions plus récentes. python -m secfragility.phase3 --reconstruct reconstruit depuis le cache, sans requête SEC ni appel de modèle. python -m pytest -q exécute les tests. work/idempotency_verification.json compare les huit tables avec une référence créée après intégration des 398 blocs, toutes colonnes et provenance incluses.

## Intégration SoftBank — sources officielles japonaises

Le modèle courant comprend 24 groupes. Lire [softbank_integration.md](softbank_integration.md). Les huit tables contiennent la base SEC intacte et les données SoftBank qualifiées ; [softbank_summary.json](softbank_summary.json) donne les contrôles et la couverture. `python -m secfragility.softbank_integration` reconstruit cette extension depuis le checkpoint SEC immuable et les sources japonaises conservées. `python -m secfragility.phase3 --reconstruct` conserve la reconstruction complète depuis le cache SEC, puis applique la même extension.
