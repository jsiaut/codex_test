# Restaurer le modèle Dell à 25 groupes

Cette archive contient les **huit tables courantes complètes à 25 groupes**, les séries et mesures communes, les sources Dell originales, les observations, le code, les tests et les preuves de validation. Elle complète SEC_Project_2_SoftBank.zip, qui contient les preuves des 24 groupes antérieurs. Les empreintes et la dépendance sont dans work/dell/delivery_dependency.json.

Pour consulter les données courantes, ouvrir tables/ et les CSV. Pour rejouer sans réseau, extraire d’abord l’archive SoftBank dans un dossier vide, puis cette archive Dell dans le même dossier. Installer requirements.txt. Restaurer le point de contrôle précédent depuis le ZIP conservé :

```
python -m secfragility.dell_package restore --previous /chemin/SEC_Project_2_SoftBank.zip
python -m secfragility.dell_sources restore
python -m secfragility.dell_sources nominate
python -m secfragility.dell_integration native
python -m secfragility.dell_integration assemble
python -m pytest -q
```

Les observations personnelles sont des entrées conservées, pas une extraction à refaire par un modèle. author_notes.py et la nomination permettent de revalider leurs citations contre les originaux. Le rejeu Dell reparse les états SEC puis applique l’extension au point de contrôle vérifié des 24 groupes, sans requête SEC ni appel de modèle. Le rejeu SEC complet de l’étape précédente dispose de sa preuve propre dans l’archive SoftBank.

Les archives antérieures restent intactes. Le 9 octobre 2026 reste l’arrêt des sources. Les notes détaillées des derniers comptes sont entièrement lues dans le périmètre annoncé ; les notes historiques supplémentaires et la ventilation privée du portefeuille DFS ne sont pas déclarées exhaustives.
