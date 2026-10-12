# Audit du résultat actuel — 26 groupes

Le point d’entrée est `current.json`, également visible dans `tables/current.json`. Résoudre `tables/` une fois : ce chemin immuable contient les huit fichiers Parquet et leur manifeste de validation. Les identifiants de fonds, véhicules et paires ne sont pas des groupes principaux supplémentaires.

Les huit tables courantes sont documents, facts, observations, entities, links, measures, controls et exclusions. Leurs champs de provenance renvoient aux faits, observations personnelles, pièces originales ou sources publiques de métadonnées. La coupure reste `2026-10-09T10:24:21.129672+00:00`, avec une convention UTC explicite. Les annexes E/F et leurs empreintes d’origine restent inchangées.

Les tableaux `audit/measures.parquet` et `audit/controls.parquet` sont le snapshot historique SEC à 23 groupes ; `audit/AUDITOR.md` conserve le protocole initial à onze groupes. Les compléments SoftBank, Dell, SMCI et priorities ont leurs propres rapports, sources, preuves et limites. Pour des contrôles globaux, utiliser les huit tables du manifeste courant. Pour une vérification financière, revenir aux pièces originales et aux citations, pas seulement aux tableaux calculés.

SoftBank utilise une variante distincte de sources officielles japonaises qualifiées. Vérifier publication, traduction/original, niveau d’assurance, IFRS, périmètre et devise ; ne pas mélanger cette variante avec la base EDGAR historique. Les arêtes de prêteurs décrivent leurs positions détenues, pas un supplément aux dettes des emprunteurs. Une identité juridique confirmée ne prouve pas une consolidation au groupe. Les contreparties anonymes et les recettes privées non publiées restent non déterminables.

Les vérifications présentes sont celles d’un producteur unique, sans sous-agent. L’audit externe transmis par l’utilisateur est conservé dans `work/audit_20261012/audit_input.pdf` ; il porte sur le commit 5c8d484. La réponse aux constats ne vaut pas un nouvel audit financier indépendant ni une reconstruction intégrale de toutes les sources historiques.

Pour auditer le code de reprise et de livraison, les cas de régression sont dans `tests/test_audit_regressions.py` : frontière de publication, échec d’export, validation tardive, changement de code après checkpoint/test, attribution entre contreparties, verrou perdu et chemins explicites. Les commandes réellement exécutées et leurs empreintes figurent dans `work/audit_20261012/test_attestation.json`. L’inventaire SHA complet des sources est `source_preflight.json`.
