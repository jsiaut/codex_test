# SEC_Project_2

Le périmètre principal comprend 23 groupes, dont 12 ajoutés dans cette livraison. Lire [user_brief_expansion.md](user_brief_expansion.md), puis [entites_ajoutees.md](entites_ajoutees.md). Les résultats antérieurs restent dans l'historique Git et dans leurs archives distinctes.

Les sources sont arrêtées au 9 octobre 2026, 10:24:21 UTC. La première tranche des entités ajoutées comprend 67 blocs naturels lus et 398 autres blocs explicitement non traités ; l'inventaire et les originaux sont conservés. La lecture des notes et contrats n'est pas exhaustive. Athene est rattachée économiquement à Apollo par une preuve de contrôle ; les fonds gérés, les JVs et les véhicules de projet gardent leurs identités distinctes. Aucun score global ni total d'exposition n'est calculé. Aucun audit indépendant n'est revendiqué.

Les huit tables sont dans tables/. Les observations sont dans work/observations/, les critères et contrôles dans audit/, et la couverture détaillée dans expansion_note_coverage.csv. Les fichiers expansion_evidence.csv, expansion_entities.csv, expansion_financial_metrics.csv et expansion_lender_classification.csv donnent les citations, identités, mesures et classifications. Les ND conservent leurs raisons.

## Reproduction

Installer requirements.txt et restaurer les sauvegardes de sources LFS avec leurs manifestes SHA-256, sans écraser les observations plus récentes. Les sauvegardes complémentaires contiennent aussi les nouveaux originaux et les notes différées. Depuis la racine, python -m secfragility.phase3 --reconstruct reconstruit depuis le cache, les observations et les décisions versionnées, sans requête SEC ni appel de modèle. python -m pytest -q exécute les tests. Le résultat de la comparaison des huit tables après reconstruction complète figure dans work/idempotency_verification.json.

Les commits intermédiaires enregistrent le travail ; le commit final et ses contrôles établissent la livraison. Les captures d'API sont figées et ne sont pas supposées récupérables à l'identique ultérieurement. L'archive de cette tranche porte le nom SEC_Project_2_entites_ajoutees.zip.
