# Séries temporelles

Mise à jour SoftBank : le modèle courant comprend **24 groupes**. Les sources japonaises et la comparaison SEC sont documentées dans [softbank_integration.md](softbank_integration.md). Les chiffres de cette extension ont leur index dans [audit/softbank_numbers.csv](audit/softbank_numbers.csv) ; les résultats SEC antérieurs conservent leur index et leurs critères.


La feuille series.csv publie toutes les mesures de rang 1, les dépendances requises et les événements, par groupe, contrepartie, période fiscale, vue, terme et variante. Le champ value vide est ND ; status et nd_reason donnent le motif. knowledge_date indique la publicité de la pièce et information_cutoff l’information disponible pour la vue. Les ruptures et périmètres restent en colonnes. Aucun montant manquant n’est remplacé par zéro.

Lire delta.md d’abord, puis synthesis.md. Les références et les termes de chaque chiffre figurent dans audit/numbers.csv. Les tables Parquet conservent les décimales exactes.
