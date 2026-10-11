# SEC_Project_2

Les quatre approfondissements autorisés sont livrés : lire [user_brief_deepening.md](user_brief_deepening.md), puis [approfondissements.md](approfondissements.md). Les citations sont dans deepening_evidence.csv ; les quantités dans deepening_measures.csv, lender_positions.csv et form_d_disclosures.csv. form_d_series.csv contient les dernières déclarations cumulatives connues à chaque fin de trimestre. Les huit tables sont dans tables/ et les contrôles dans audit/.

Les onze groupes principaux, l’arrêt des sources du 9 octobre 2026 et les critères E/F restent inchangés. Les prêteurs et autres déposants ciblés sont des sources externes distinctes. Les résultats du premier passage et des notes complémentaires sont conservés dans leurs fichiers et l’historique Git. Aucun score ou total global d’exposition n’est produit. Travail effectué sans sous-agent ; aucun audit indépendant revendiqué.

## Reproduire

Installer requirements.txt. Restaurer le cache initial depuis la sauvegarde LFS, puis les sources supplémentaires depuis la sauvegarde sec-project-2-deepening, sans écraser les observations récentes ni restaurer un ancien verrou. L’archive SEC_Project_2_approfondissements.zip contient aussi les sources supplémentaires, les blocs lus et les exports. Depuis la racine, `python -m secfragility.phase3 --reconstruct` reconstruit les faits et les huit tables hors ligne. Aucun appel de modèle ni nouvelle requête SEC n’est nécessaire. Les décisions, observations et sources originales sont nécessaires à cette reproduction.

`python -m secfragility.reproduce capture`, puis la reconstruction et `python -m secfragility.reproduce compare` vérifient l’égalité intégrale des huit tables, décimales et provenance comprises. Ne pas capturer une nouvelle référence pour masquer une divergence.

Les sauvegardes intermédiaires et la livraison finale sont poussées sur https://github.com/jsiaut/codex_test. Les répertoires de sources ignorés par Git sont conservés dans les sauvegardes LFS avec leur SHA-256.
