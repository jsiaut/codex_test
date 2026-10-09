# Modèle SEC — état du chantier

Ce dépôt exécute la spécification v6.14 fournie par l’utilisateur, sans sous-agent.
Les critères E/F et les seuils ont été commités avant toute requête SEC. Le
User-Agent est celui fourni par l’utilisateur. Le réseau est centralisé, plafonné
à cinq requêtes par seconde, journalisé et protégé par un verrou.

Le chantier est en cours. Les tables de faits issues d’une reconstruction
intermédiaire ne constituent pas une livraison comptable validée. La lecture des
blocs, les mesures, les contrôles et l’audit indépendant ne sont pas terminés.
Les faits de l’annexe D ne sont jamais recopiés comme résultats. L’audit
indépendant n’est pas réalisé, conformément à la demande de travailler sans
sous-agent.

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

## Reprise et sauvegarde

La collecte est conservée dans le cache. La phase 2 poursuit la lecture directe
des blocs ; son avancement est généré dans `work/reading_progress.json`. Les
tables intermédiaires et les calibrations ne constituent pas le résultat final.
L’assemblage du graphe, les contrôles finaux et les rendus restent à terminer.

Une tâche quotidienne reprend l’exécution ou surveille les nouveaux dépôts,
sous le verrou de session. Aucune extension du premier passage n’est ouverte.

À la demande de l’utilisateur, les commits sont poussés vers
`https://github.com/jsiaut/codex_test`. Les tables Parquet utilisent Git LFS.
La lecture crée un point de sauvegarde toutes les dix clés terminées ou après
dix minutes de travail. Ces commits intermédiaires ne déclarent pas l’exécution
terminée. Le cache est exclu de Git et conservé dans une archive de reprise
sous `backup/`, transférée avec Git LFS et accompagnée de son empreinte SHA-256.

Pour reprendre sur une nouvelle machine, cloner le dépôt, exécuter `git lfs
pull`, installer les dépendances, puis lancer `python -m secfragility.backup
--restore backup/sec-project-2-20261009T150746Z.tar.zst --manifest
backup/sec-project-2-20261009T150746Z.tar.zst.json`. Cette commande vérifie
l’empreinte et conserve les fichiers versionnés les plus récents. Ne pas
restaurer le verrou ni le propriétaire de
session : la nouvelle session doit acquérir son propre verrou. Le fichier
`work/run.json` conserve l’instant logique de l’exécution inachevée.

Le dossier `audit/AUDITOR.md` prépare une vérification ultérieure ; aucun audit
indépendant n’a été effectué.
