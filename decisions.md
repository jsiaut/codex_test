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

## D0009 — Correction de D0007 par emplacement dans le tableau

La règle de D0007, qui écartait une composante dimensionnée dès que le même concept existait sans dimension, est trop large : AMD affiche aussi des lignes distinctes pour des composantes liées. Le critère est désormais l'emplacement physique, défini indépendamment des valeurs : un fait inséré dans la cellule du libellé est parenthétique ; un fait dans une cellule de montant est une composante affichée. C1 exclut les montants parenthétiques et conserve les lignes distinctes. Les concepts et valeurs sont inchangés. Cette correction d'implémentation est documentée séparément des décisions de correspondance.

## D0010 — Trésorerie restreinte et équivalents

Les concepts `RestrictedCashAndCashEquivalentsAtCarryingValue` (courant selon sa définition) et `RestrictedCashAndCashEquivalentsNoncurrent`, présentés notamment par CoreWeave, deviennent deux correspondances supplémentaires distinctes. Le rapprochement C3 préfère leur montant combiné aux seuls espèces restreintes quand les deux sont publiés, selon une priorité fixée avant le calcul ; il ne les additionne pas. Les composantes absentes restent inconnues. La pièce nouvelle utilisée est la définition et la présentation dans le dernier 10-Q de CoreWeave ; aucun échec C3 n'avait été corrigé par ces correspondances.

## D0011 — Dépréciations et espaces de noms

Le paquet FASB US GAAP 2026 épinglé contient une linkbase `depcon-def`. Seuls les remplacements univoques de concepts entiers (`dep-concept-deprecatedConcept` ou `essence-alias`, du concept courant vers le concept déprécié) sont aplatis ; les remplacements conditionnés par une dimension, partiels, mutuellement exclusifs ou ambigus restent séparés. Les relations retenues, écartées et l'empreinte du paquet sont conservées dans `work/deprecations.json`. Les dates des espaces de noms d'extensions sont retirées de l'identité canonique, y compris lorsqu'elles précèdent `/taxonomy` ; les unités et espaces de noms XBRL standard ne sont pas altérés. Les valeurs et occurrences source sont conservées.

## D0012 — Rapports classiques et notes annuelles CoreWeave

Lorsque MetaLinks est absent, les rôles et catégories proviennent de FilingSummary et les présentations, libellés et types de ses linkbases et schémas effectivement déposés. Les types et définitions standards sont documentés séparément par le paquet FASB épinglé. La sélection des notes ne repose jamais sur leur suffixe. Les faits candidats classiques doivent être présentés dans le rôle de la note, en plus de leur compatibilité de période ; une égalité de montant ne permet aucune attribution de contrepartie. Le prospectus CoreWeave 0001193125-25-067651 porte les opinions Deloitte des états 2024/2023 (octets 2532867–2538111) et RSM des états 2022, hors bilan 2022 (2538111–2542753). Sa note 14 annuelle (3463351–3477806) est donc lue comme une note auditée. L'absence d'opinion d'audit sur le contrôle interne ne devient pas une faiblesse significative.

## D0013 — Tirets annuels non balisés ; réexamen de D0008

Le parseur avait assimilé les tirets nus des états annuels SpaceX à zéro. Cette erreur contredit §7.3 et ne peut être justifiée par un rapprochement. Les tirets deviennent inconnus, les équations qui en dépendent `not_testable` ; le bilan comparatif reste rapproché pour ses nombres explicites. D0008 est suspendue et seule la nouvelle validation D1 décide l'admission de la série entière. Les notes textuelles auditées restent dans la tranche. Cette correction ne change ni les concepts, ni les seuils, ni les critères E/F.

## D0014 — Présentations de concepts historiques sans définition moderne

Une composante présentée dans une linkbase ancienne ne disparaît pas de C1/C2 au motif que son concept n'existe plus dans le schéma 2026. Son rôle effectivement déposé est conservé ; son type et sa définition restent inconnus et ne permettent aucune correspondance de grandeur. Cette correction complète les termes de l'équation sans modifier les valeurs, les poids déposés, les correspondances ou la tolérance. Les parts dimensionnées sans emplacement primaire établi ne sont pas assimilées à des lignes physiques distinctes.

## D0015 — Obligation non comptabilisée et bail non commencé

Le concept standard UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount couvre explicitement plusieurs catégories dans sa définition, dont les baux non commencés. Lorsque le libellé propre du déposant affirme ces baux, sa grandeur est lease_not_commenced ; sinon elle reste une obligation d'achat non comptabilisée à périmètre large, chevauchement possible. Aucun bail n'est déduit du seul nom standard. La clôture et, lorsqu'elle est disponible, l'ouverture du pont sont publiées ; additions et commencements ne sont pas reconstitués par solde. Les concepts d'extensions sans paragraphe ASC attesté restent non résolus.

## D0016 — Ancres vides et sous-sections d'Item 404

L'ancre de table des matières d'Alphabet précède un bandeau de navigation ; son absence de taille typographique avait provoqué une borne au premier sous-titre. Le départ est résolu vers le titre réel, et les liens de sous-sections de transactions/politique de parties liées restent dans l'Item 404. La borne finale suit le prochain sujet de la table des matières, sans comparaison de tailles entre pages. Les blocs imbriqués déjà entièrement couverts sont écartés comme doublons de découpage. Les anciennes et nouvelles clés sont conservées dans section_boundary_changes ; aucune observation de l'ancien faux bloc d'Alphabet n'avait été écrite. Les sections de gouvernance, de contrôle et des 8-K ne prennent pas le niveau d'assurance des états financiers seulement parce qu'elles figurent dans le même formulaire.

## D0017 — Quarantaine de classification contractuelle

Trois observations de paiements contractuels sur la durée des équipements Valor, dans l'Item 404 du prospectus SpaceX, avaient été classées comme échéancier de dette par rapprochement avec la note financière. La qualification de chaque contrat ordinal n'est pas explicitement établie dans cet extrait. Les citations et montants restent conservés, mais observation_quarantines exclut leurs arêtes de montant et les mesures dépendant de cette catégorie jusqu'à résolution. Aucun total de ces engagements avec la dette comptabilisée ni aucun principal de dette n'est publié par hypothèse. Le fichier d'observations original n'est pas modifié.

## D0018 — Titres non liés et niveaux des proxies

Le proxy CoreWeave contient une table des matières sans liens et des sous-titres en caractères gras de même taille que le titre principal. Une entrée terminée par un numéro de page n'est pas une borne de section. Pour un titre principal entièrement en majuscules, les sous-titres de casse différente ne terminent pas la section. Chez Amazon, les titres principaux de grande taille ne sont pas gras : leur taille explicite permet de retrouver le prochain titre. Une distance arbitraire de 500 octets ne doit pas empêcher cette borne dans une courte section. Les régressions sont testées sur ces structures ; elles n'autorisent aucun filtrage des opérations.

## D0019 — Deuxième tentative de schéma et citations de continuations

Le premier enregistrement d'Alphabet comportait quatre erreurs de noms de champs (`approximate` au lieu de `approximately`, `event_kind` au lieu de `event_type`). Le code avait écrit trop tôt le marqueur de première tentative. La seconde tentative du même passage est ajoutée, sans écrasement, sous un marqueur `schema_retry` ; les quatre lignes brutes refusées restent dans le fichier de rejets. Les quatre corrections passent. Ce mécanisme ne constitue pas une nouvelle lecture et n'autorise pas un troisième essai ni la reprise d'un rejet sémantique. Les nouvelles passes de lecture requièrent toujours un nouvel `as_of`.

Quatre lignes de la note annuelle CoreWeave traversaient un pied de page présent dans la plage brute englobante mais exclu des continuations iXBRL de la note. Elles ont été rejetées au contrôle sémantique. La validation assemble désormais uniquement les plages sources déclarées, vérifiées incluses dans la plage englobante. Les quatre rejets déjà écrits restent exclus pour cette exécution ; aucune retouche du fichier original ne les réadmet. Les observations suivantes passent cette vérification corrigée.

## D0020 — Dates de contexte et nature des montants

La note trimestrielle CoreWeave donne au montant de dépôt historiquement classé au 31 décembre 2024 un contexte balisé de mars ou juin 2025. L'attribution numérique de ce montant à son ancien solde est écartée et le conflit de dates documenté. Chez Microsoft, la borne de 10 % concerne les participations d'autres investisseurs à la signature de mars 2024 ; les contextes plus récents ne créent ni une détention actuelle certaine, ni un investissement de Microsoft. Les paiements de clients ne deviennent jamais des revenus reconnus ; les offres secondaires ne deviennent jamais une levée de fonds de l'émetteur ; une annonce d'acquisition ne date pas sa clôture.

## D0021 — Plafond complet du paquet servi

Le paquet sérialisé, et pas seulement le texte, est borné à 80 000 caractères. Les coupures restent naturelles avec recouvrement. À partir de cette correction, read_packets consigne la clé, la partie, le nombre de parties, l'en-tête de pièce éventuel, les caractères servis et l'empreinte du paquet. Les compteurs antérieurs ne sont pas inventés rétroactivement. Une émission de paquet par le code ne prouve pas à elle seule une lecture complète ; la passe d'observations validées en est le résultat conservé.
