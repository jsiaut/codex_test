# SEC_Project_2

Les 398 blocs complémentaires sont tous traités, sans sous-agent. L’inventaire des entités ajoutées couvre désormais 465 notes uniques lues sur 465 ; 23 groupes principaux sont suivis. Sources arrêtées au 9 octobre 2026, 10:24:21 UTC, critères inchangés.

Lire [user_brief_398.md](user_brief_398.md), puis [bilan_398_blocs.md](bilan_398_blocs.md). Les conclusions individuelles et les citations figurent dans revue_398_blocs.csv. Les notes historiques et les contrats au-delà de ce lot ne sont pas déclarés entièrement lus. Aucun total d’exposition, score global ou audit indépendant n’est revendiqué.

Les huit tables sont dans tables/, les critères et contrôles dans audit/, les observations dans work/observations/. L’archive de cette livraison est SEC_Project_2_398_blocs.zip ; les archives antérieures sont distinctes.

## Reproduction

Installer requirements.txt. Restaurer les sauvegardes LFS de sources avec leurs manifestes SHA-256, sans écraser les observations et décisions plus récentes. python -m secfragility.phase3 --reconstruct reconstruit depuis le cache, sans requête SEC ni appel de modèle. python -m pytest -q exécute les tests. work/idempotency_verification.json compare les huit tables avec une référence créée après intégration des 398 blocs, toutes colonnes et provenance incluses.

La validation de cette continuation est dans work/continuation398/validation.json. work/expansion/validation.json conserve la première tranche datée, avec son ancien périmètre de lecture.

## SoftBank — extension préparée

[softbank_faisabilite.md](softbank_faisabilite.md) présente les sources japonaises et le pilote. Les 43 PDF sont collectés ; la lecture exhaustive et l’intégration aux calculs principaux restent à effectuer. Les huit tables de la livraison des 398 blocs sont inchangées.

## Intégration SoftBank — sources officielles japonaises

Le modèle courant comprend 24 groupes. Lire [softbank_integration.md](softbank_integration.md). Les huit tables contiennent la base SEC intacte et les données SoftBank qualifiées ; [softbank_summary.json](softbank_summary.json) donne les contrôles et la couverture. `python -m secfragility.softbank_integration` reconstruit cette extension depuis le checkpoint SEC immuable et les sources japonaises conservées. `python -m secfragility.phase3 --reconstruct` conserve la reconstruction complète depuis le cache SEC, puis applique la même extension.
