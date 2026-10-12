# Restaurer le modèle SMCI à 26 groupes

Cette archive contient les huit tables complètes courantes, les séries et mesures communes, les originaux SEC SMCI dans un tar.zst, les observations personnelles, les modules, les tests et les preuves de validation/rejeu. L’arrêt reste le 9 octobre 2026. Les archives Dell et SoftBank précédentes sont conservées ; elles contiennent les preuves des 25 groupes antérieurs.

Pour consulter le modèle courant, ouvrir tables/ ou les CSV. Pour rejouer l’ajout SMCI dans un dossier vide, extraire cette archive puis installer requirements.txt. Le point de contrôle antérieur est restauré depuis l’archive Dell vérifiée :

```
python -m secfragility.smci_package restore --previous /chemin/SEC_Project_2_Dell.zip
python -m secfragility.smci_sources restore
python -m secfragility.smci_sources nominate
python -m secfragility.smci_integration native
PYTHONPATH=. python work/smci/author_notes.py
python -m secfragility.smci_integration assemble
```

Les observations sont des entrées rédigées personnellement et conservées. Leur script revalide les citations contre les sources, sans appel de modèle. Le rejeu natif reparse les originaux SMCI puis applique leur delta au point de contrôle immuable de 25 groupes, sans réseau. Il ne prétend pas avoir reparsé à nouveau tous les originaux des anciennes étapes.

Pour une reconstruction complète de toutes les étapes, extraire d’abord SoftBank, puis Dell, puis SMCI dans le même dossier et suivre les instructions de chaque archive. Les sources historiques de work/deepening_data/ supprimées du seul espace de travail après vérification sont présentes dans l’archive SoftBank. Les sources Dell peuvent être rematérialisées avec python -m secfragility.dell_sources restore. Pour exécuter l’ensemble de la suite de tests, les données des archives précédentes sont nécessaires.

Les notes historiques supplémentaires SMCI restent inventoriées hors de la tranche courante. Les onze notes sélectionnées FY2026 sont toutes lues ; les contrats et le proxy ne sont pas annoncés comme intégralement lus. Aucun audit indépendant par un autre exécutant n’a été réalisé.
