# Reproduire l’extension transactionnelle

La livraison contient les huit tables actuelles, les sept petites tables historiques précédentes et une sauvegarde des originaux sélectionnés. Les faits historiques occupent environ 327 Mo : ils sont stockés une seule fois dans la table actuelle. Le module de rejeu restaure la table précédente en retirant les huit identifiants natifs supplémentaires explicitement listés dans `baseline_encoding_proof.json`. Le fichier Parquet ainsi reconstruit a un autre encodage physique que l’ancien ; l’équivalence des lignes dans les deux sens a été certifiée avant publication, et son SHA attendu est enregistré. Les sept autres tables précédentes doivent conserver leur SHA original exact.

Dans un répertoire extrait de l’archive, installer les versions de `requirements.txt`, puis lancer :

```bash
python -m secfragility.operation_replay replay
python -m pytest -q tests/test_operation_dependencies.py
```

Le premier lancement restaure et contrôle les sources, reconstitue les candidats natifs, régénère les observations choisies dans `author_notes.py`, les rôles et contrats dans `author_ledger.py`, puis applique l’extension sur la base historique. Aucun accès réseau n’est nécessaire. La date documentaire demeure celle du modèle, même si les fichiers ont été collectés plus tard. Les réponses originales de métadonnées et les en-têtes disponibles sont également sauvegardés ; les dépôts postérieurs à la limite sont exclus.

Comparer les SHA des huit tables obtenues à ceux enregistrés dans `work/dependencies/replay_verification.json`. Les fichiers d’observations, décisions et opérations régénérés doivent également correspondre. Le manifeste `current.json` associe tous les fichiers à une même génération publiée atomiquement. Un lecteur qui ouvre plusieurs tables doit résoudre le chemin `tables` une seule fois.

Le dossier `work/dependencies` permet de consulter les choix, citations et lacunes sans rejouer. Charger `operation_views.sql` après les tables pour utiliser `effective_links` : les corrections de contrepartie et de classification gardent leurs anciennes lignes historiques et ajoutent une relation de remplacement.

Ce rejeu vérifie la nouvelle extension depuis une base figée ; il ne recalcule pas tous les rapports historiques à partir des documents bruts. Les archives historiques précédentes ou le dépôt GitHub et ses objets LFS restent nécessaires à cette reconstruction complète et à l’ensemble des tests historiques. La suite locale complète et la suite ciblée réellement exécutées sont consignées dans `work/audit_20261012/test_attestation.json` ; les tests isolés de l’extension figurent dans les preuves de rejeu.
