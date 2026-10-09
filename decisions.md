# Décisions

Les décisions comptables se prendront sur leurs pièces, avant les contrôles, et
resteront consultables ici avec leur accession et leur emplacement.

- D0001 — L’instruction explicite de l’utilisateur interdit tout sous-agent.
  L’audit indépendant prévu au §12.2 n’est donc pas exécuté ; le dossier est
  préparé pour un audit ultérieur. Cette adaptation ne modifie aucun critère E/F.
- D0002 — Les CIK de départ sont des indications ; les onze tickers ont été
  résolus depuis le fichier SEC. Les trois CIK prédécesseurs sont collectés comme
  indications de périmètre ; leurs dates de succession restent à établir sur
  les pièces, avant toute agrégation.
- D0003 — Les limites de lecture provisoires reculent de trois années civiles
  avec une marge conservatrice. Elles servent uniquement à l’inventaire et la
  collecte. Les quatre trimestres de fenêtre allongée et les huit trimestres
  d’historique doivent encore être fixés depuis les périodes fiscales exactes
  avant de servir la file finale de lecture.
- D0004 — Le précontrôle des pages documentaires a reçu un identifiant temporel
  fourni à sa commande ; l’exécution de l’inventaire utilise son propre instant
  UTC effectivement enregistré dans `work/run.json`. Aucun résultat financier
  n’a été calculé pendant le précontrôle documentaire.

- D0005 — Le 424B4 de SpaceX, accession 0001628280-26-042639, note 1 annuelle (octets bruts 7336456–7361893), affirme des regroupements sous contrôle commun, une combinaison rétrospective aux valeurs historiques et des éliminations des transactions entre entités. Les dates juridiques sont enregistrées séparément ; les jours exacts de début du contrôle commun ne sont pas inventés lorsque la pièce ne donne qu’un mois ou la période présentée. La série consolidée révisée est celle publiée après combinaison ; la série historique sans les autres activités reste indéterminable hors de la segmentation documentée.

## D0006 — Correspondances techniques supplémentaires

Avant leurs contrôles, les correspondances supplémentaires sont fixées dans `mapping.py` par le concept standard exact, sa définition documentée et sa présentation par le déposant. La documentation de `DebtInstrumentFaceAmount` définit le montant à l'émission : il n'est pas assimilé au principal restant dû. `RevenueRemainingPerformanceObligationExpectedTimingOfSatisfactionPeriod1` définit une durée ISO 8601 : il n'est pas assimilé à une tranche monétaire. Les durées balisées sont conservées textuellement dans les faits. Les dettes à leur valeur comptable ne remplacent pas le principal sans rapprochement publié. Aucune de ces décisions n'est fondée sur le résultat d'une équation.

## D0007 — Dimensions de composantes et montants parenthétiques

Le contrôle C1 ne doit pas additionner au montant sans dimension d'un concept la part liée du même concept inscrite dans son libellé. L'inclusion d'une composante dimensionnée requiert donc l'absence du montant total du même concept, dans le même dépôt et la même période. Cette correction porte sur la déduplication des composantes ; la correspondance des concepts est conservée. Le cas du bilan de SpaceX a révélé cette erreur d'implémentation. Les différences de précision des taux de CoreWeave et les BPA arrondis proches de zéro restent des résultats de contrôle sous les tolérances d'origine, sans ajustement des faits.

## D0008 — Admission de la série annuelle SpaceX, non balisée

Le rapport PwC du 424B4 (octets 6675682–6704012) couvre les bilans au 31 décembre 2025 et 2024 et les trois exercices clos en 2025. Son opinion mentionne séparément les regroupements sous contrôle commun, le fractionnement des actions et le changement de secteurs, datés du 7 mai 2026 ; l'opinion initiale est du 30 mars 2026. Le parseur a validé les composantes des actifs et des passifs, les trois sections de flux, le résultat au début des flux et les mouvements du déficit accumulé. Les vingt-huit correspondances de postes de bilan retrouvées dans le comparatif balisé de 2025 passent à la tolérance d'arrondi. La série correspondante est admise, `is_tagged=false`, avec son périmètre `as_if_combined` et sa première date publique ; les libellés sans correspondance restent exclus. Les comparaisons historiques en vue `as_known` ne peuvent utiliser ces états avant leur publication.
