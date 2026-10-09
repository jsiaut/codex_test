# Modèle SEC — état du chantier

Ce dépôt exécute la spécification v6.14 fournie par l’utilisateur, sans sous-agent.
Les critères E/F et les seuils ont été commités avant toute requête SEC. Le
User-Agent est celui fourni par l’utilisateur. Le réseau est centralisé, plafonné
à cinq requêtes par seconde, journalisé et protégé par un verrou.

Le chantier est en cours. Les tables de faits issues d’une reconstruction
intermédiaire ne constituent pas une livraison comptable validée. La lecture des
blocs, les mesures, les contrôles et l’audit indépendant ne sont pas terminés.
Les faits de l’annexe D ne sont jamais recopiés comme résultats.

## Commandes

Depuis la racine, avec les dépendances de `requirements.txt` :

```sh
python -m pytest -q
python -m secfragility.inventory
python -m secfragility.collect
python -m secfragility.rebuild
```

L’inventaire et la collecte reprennent leurs points de contrôle. La reconstruction
relit le cache local intégralement et écrit huit tables Parquet triées. Elle
n’effectue aucune requête réseau.

Un refus 403 persiste une pause de dix minutes et retourne le code de sortie 75.
Un nouveau refus après cette pause suspend l’exécution (code 76). Le conducteur
ne doit ni changer l’identité ni supprimer cet état pour contourner un refus.

Les observations se soumettent par le module `observations` après lecture
effective d’un bloc. Le module valide le schéma et les citations, contreparties,
faits candidats et unités. Un fichier versionné par clé de contenu conserve
chaque passe et ses rejets. Aucune extraction par API de modèle n’est utilisée.

## Éléments restant à terminer

La vérification détaillée des endpoints de dépôt et des paquets de taxonomie,
les décisions de périmètre SpaceX et des prédécesseurs, le raffinement des bornes
fiscales de lecture, l’univers attendu et les files de blocs doivent être terminés.
La correspondance exhaustive des concepts, les deux vues, les calculs SQL des
mesures et contrôles, la lecture de tous les blocs de la tranche, le graphe et les
rendus finaux restent ensuite à réaliser. Le dossier `audit/AUDITOR.md` prépare
une vérification ultérieure ; aucun audit indépendant n’a été effectué.

Aucune extension du premier passage n’est ouverte. Aucune automatisation n’est
installée tant que le pipeline complet et ses rendus n’ont pas été validés.
