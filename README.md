# SEC_Project_2

Extension des cinq familles de notes v6.14 livrée. Lire [user_brief_extension.md](user_brief_extension.md), [notes_complementaires.md](notes_complementaires.md), puis [synthesis.md](synthesis.md). Les montants individuels et leurs sources figurent dans notes_components.csv ; les huit tables sont dans tables/ et les vérifications dans audit/. Le premier passage reste conservé dans user_brief_2.md et l’historique Git.

Les critères et l’arrêt des sources restent inchangés. Les autres extensions et la découverte ne sont pas ouverts. Aucun montant absent n’est remplacé par zéro, aucun total global d’exposition ni score n’est produit. Aucun audit indépendant n’est revendiqué.

Installer requirements.txt et restaurer le cache LFS. python -m secfragility.phase3 assemble depuis les documents, faits et observations conservés ; --reconstruct reconstruit les faits depuis le cache. Ces commandes ne demandent aucune nouvelle requête SEC ni appel de modèle. Les observations et les décisions d’attribution sont nécessaires à la reproduction. Les sauvegardes intermédiaires sont distinctes du commit de livraison.
