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

## D0022 — Retours à la ligne dans les citations et les noms

Les citations rédigées après lecture sont alignées sur les seuls espaces et retours à la ligne du texte effectivement servi avant leur soumission : les mots et la ponctuation ne changent pas et le validateur exige toujours le fragment source exact. L'outil ne sélectionne aucun passage et ne qualifie aucune opération. Six citations du proxy Alphabet 2024 avaient été refusées parce que des retours avaient été aplatis ; l'indemnisation y a aussi échoué au second essai de schéma, puis en sémantique. Ces refus restent conservés, sans réadmission dans cette exécution. La seconde tentative NVIDIA 2024 ajoute le déclencheur omis et passe.

La raison sociale BCH San Jose LLC est coupée par une ligne dans le proxy Alphabet 2021, accession 0001308179-21-000256. La vérification d'un nom admet désormais uniquement cette variation des espaces : chaque mot, la casse et la ponctuation restent littéraux, sans correction typographique ni rapprochement flou. Les treize contrôles de validation et d'invariants ciblés passent. Le rejet antérieur de cette observation reste exclu pour ce passage.

## D0023 — Portée des montants historiques et des mentions accessoires

L'achat Oracle d'une participation Ampere à un autre investisseur (proxy 2022, accession 0001193125-22-250158) est secondaire, distinct de l'investissement en dette convertible du même exercice. Les montants appliqués à une commande prépayée sont des composantes des achats, jamais de nouveaux paiements. Les fonds engagés et les placements personnels des fondateurs d'Alphabet ne se confondent pas avec des versements du groupe. Les mois publiés deviennent des plages mensuelles explicites, sans jour d'événement inventé ; ils ne prouvent pas une détention actuelle. Les mentions de parties liées dans les thèmes de surveillance du comité d'audit sont des abstentions de portée, pas des opérations, et les déclarations d'absence Item 404 ne deviennent jamais une absence de financement client.

## D0024 — Fragments de phrases et classifications datées

Deux fins de phrases de rapports Broadcom, démarrant en minuscule, avaient été assimilées à des titres de parties liées. Leur lecture et les abstentions originales restent archivées ; elles quittent la file active après correction du découpage. La régression du parseur passe. Le proxy Alphabet 2020 décrit la levée Viz d’août 2019 par un montant arrondi et une plage plus courte que les proxies suivants : les pièces restent distinctes, sans addition de deux levées présumées. La cessation de la qualification de partie liée de GLOBALFOUNDRIES chez AMD en mai 2019 ne constate pas une sortie de participation.

## D0025 — Sauvegardes distantes intermédiaires

L’utilisateur demande des sauvegardes régulières et choisit explicitement le dépôt GitHub jsiaut/codex_test. L’historique initial est conservé ; les tables volumineuses utilisent Git LFS, et une archive distincte conserve le cache non versionné et les fichiers de reprise. Le lecteur pousse un point de sauvegarde toutes les dix clés terminées ou toutes les dix minutes de travail. Ces commits ne remplacent ni le commit de livraison en fin d’exécution, ni les preuves de lecture, ni un audit indépendant. Un échec réseau de GitHub laisse les observations et le commit local intacts et est signalé au conducteur.

L’API GitHub accepte les commits, Git LFS et la création de release, mais le serveur uploads.github.com refuse même le petit manifeste avec HTTP 401. Aucun jeton n’est modifié ni aucune connexion détournée. L’archive de reprise passe donc par Git LFS sous backup/, avec son manifeste ; son empreinte est vérifiée à la restauration, qui ne remplace pas les fichiers déjà suivis par Git.

## D0026 — Ancre interne à un titre et données historiques AMD

L’ancre vide du proxy AMD 2019 est placée à l’intérieur du titre. La recherche du titre vers l’avant avait sélectionné sa répétition sur la page de continuation et omis la première page. L’ancre dont un parent porte exactement le titre est désormais reconnue comme départ ; la correction modifie une seule clé de la file entière. Le faux bloc garde une abstention archivée et le bloc complet est relu. Le test de régression passe.

Le proxy date le septième amendement WSA du 29 janvier 2019, tandis que la note trimestrielle le date du 28 janvier : conflit conservé, pas de date choisie par hypothèse. Les noms Mubadala Investment Company PJSC et Mubadala Development Company PJSC ne sont pas fusionnés sans pièce d’identité. Une participation passant sous le seuil de désignation d’un administrateur n’est pas une sortie complète de capital. Les frais de waiver d’un contrat fournisseur ne deviennent pas un événement de covenant financier.

## D0027 — HTML historique, tableaux répétés et portée des paiements

Le proxy Amazon 2018 emploie des tailles ordinales FONT sans taille CSS. La borne compare les seules tailles ordinales publiées de titres principaux en majuscules, sans les convertir en points. La correction change une seule clé de la file ; le fragment antérieur reste archivé, le nouveau bloc est entièrement lu et son test de régression passe.

Un montant de tableau sans suffixe monétaire peut utiliser l’échelle explicite « In millions », uniquement quand sa cellule est précédée du signe dollar. Une année ou un pourcentage ne peut fournir un montant en dollars. Les sous-tableaux déjà lus dans leur note parente sont néanmoins servis et relus ; une abstention de doublon de présentation évite une seconde attribution des mêmes flux. Un tiret isolé reste inconnu, jamais zéro.

Un prix d’acquisition, un remboursement brut avant séquestre et une participation achetée ne prouvent ni une levée primaire ni un encaissement. Les montants et leur nature restent distincts. Les contrôles de la phase 2 portent la date de rapport réellement publiée dans submissions, distincte de la date de connaissance ; une conclusion sur les disclosure controls ne devient pas une affirmation d’absence de material weakness de l’ICFR.

## D0028 — Fermetures des éléments inline imbriqués

Dans la Note 1 Broadcom du trimestre clos le 2 août 2026, une continuation contient une autre continuation. La première fermeture rencontrée avait tronqué sa plage brute, alors que le texte servi comportait la fin du parent. Le validateur a refusé l’abstention dont la citation se trouvait après cette fausse borne. Ce rejet sémantique reste exclu au même as_of, sans correction rétroactive. Les deux autres observations admises du bloc restent conservées.

Les fins de nonNumeric et de continuation correspondent désormais à leur propre ouverture, en comptant les éléments imbriqués de même nom. Les tests vérifient que le texte après l’élément enfant reste dans le bloc et sa plage brute, tandis que le texte extérieur reste exclu. La file est régénérée depuis le cache ; les éventuelles nouvelles clés exigent une lecture complète et ne réutilisent pas une ancienne passe par hypothèse.

## D0029 — Type exact des pièces et première page physique

Le préfixe EX-10 admettait à tort les ressources EX-101 de taxonomie. La file contractuelle accepte désormais uniquement les types EX-10 et EX-4 suivis éventuellement de leur numéro de pièce ; les EX-101 restent des ressources structurées de phase 1. Aucune observation n’avait été écrite sur ces faux blocs contractuels.

L’en-tête servi d’un contrat suit la première rupture de page explicite du fichier, avec ses bornes brutes, même si les parties figurent après 6 000 caractères. Une rupture avant le premier texte est ignorée ; une rupture après un parent suit sa vraie fermeture. Sans pagination explicite, le document entier est servi et se lit avant toute exclusion fondée sur les parties. Les tests vérifient ces trois cas et la séparation EX-10/EX-101. Aucun classement financier n’est automatisé sur ces marqueurs.

## D0030 — Note Amazon et fragments d’affichage

La Note 1 Amazon du trimestre clos le 30 juin 2026 contient 135 faits candidats. Le premier affichage a été tronqué par l’outil ; son texte complet et tous les candidats ont été effectivement relus avant la soumission, par fragments explicitement bornés. Le lecteur sert désormais au plus 30 000 caractères sérialisés, sous le plafond autorisé de 80 000 ; un grand en-tête se présente en fragments de candidats avant les morceaux naturels de texte. Tous gardent la même clé du bloc et aucune observation n’est rendue avant sa lecture complète. Le test vérifie l’absence d’omission de candidats.

Les ajustements de prix d’investissements privés et les gains de reclassement AOCI sont des gains comptables, jamais des fonds versés à Anthropic. « Primarily » n’en attribue pas la totalité à cette contrepartie. Les engagements AWS annoncés envers OpenAI et Anthropic ne sont ni du chiffre d’affaires ni des encaissements ; « more than » demeure une borne stricte, même quand le fait balisé ne contient que son seuil. Leur addition au RPO total courant serait un double compte sans rapprochement de mesure et de dates. Les valeurs précises du tableau et leurs versions narratives arrondies ne créent pas deux transactions.

## D0031 — Note 1 financière et rubriques réglementaires

FilingSummary classe aussi les rubriques ECD et CYD de gouvernance dans MenuCategory=Notes. Le premier rôle de cette catégorie n’est donc pas nécessairement la Note 1 financière. Dans le 10-K Microsoft 2026, les rubriques de rémunération, de transactions d’initiés et de cybersécurité précèdent ACCOUNTING POLICIES ; dans le 10-Q Oracle d’août 2026, deux rubriques ECD précèdent BASIS OF PRESENTATION. Le repli vers la Note 1 ignorait ces notes comptables sans en avoir lu le texte.

L’ordre publié se choisit désormais parmi les rôles de notes représentés par des textBlockItemType financiers, en écartant les types des taxonomies réglementaires ECD/CYD/DEI. Aucun nom de concept comptable n’est imposé. Le test reproduit ces rubriques réglementaires antérieures à deux vraies notes. La file est régénérée ; tout bloc ajouté doit être intégralement lu, et la couverture est confrontée à l’inventaire indépendant des rapports, jamais à la seule file déjà traitée.

## D0032 — Ordre physique des documents

La reconstruction affectait implicitement le rang zéro aux documents et faits d’instances. Le rang vient désormais de l’ordre des DOCUMENT réellement publié dans l’en-tête SGML. Pour une instance dérivée non présente dans cet en-tête, un fait n’hérite du rang de son document inline que si son identifiant et son concept y ont une origine unique ; deux documents portant le même identifiant ne sont pas départagés par hypothèse. Le document source et la règle sont conservés dans les tables.

Le rang −1 désigne l’API companyfacts ; −2 désigne un rang physique non établi et exclut le fait de la sélection admissible. Les métadonnées et instances dérivées ne se voient pas inventer un rang de soumission. Le test vérifie un rang physique non nul, l’ambiguïté d’identifiant, un concept divergent et une instance classique. Les tables intermédiaires seront reconstruites avec cette règle avant les contrôles de livraison.

## D0033 — MetaLinks ancien et date de la fenêtre comptable

Les MetaLinks de 2022 et antérieurs ne donnent ni menuCat ni order. Leur présence empêchait le recours à FilingSummary, et tous leurs blocs naturels de notes étaient ignorés. Les rôles sont désormais enrichis par jointure exacte avec les Role/RoleURI du FilingSummary réellement déposé, qui donne catégorie et ordre ; l’ordre des clés JSON n’est jamais utilisé comme ordre des notes. Le test reproduit le format ancien et vérifie la réadmission de la première note financière. Les blocs ajoutés, notamment les anciennes notes de parties liées, sont entièrement à lire.

Les blocs de contrôle et de continuité se bornent sur reportDate, fin de la période comptable, et non sur filingDate. Un rapport annuel de l’exercice précédent déposé après le début du premier exercice analysé ne doit pas entrer dans cette tranche. La date de connaissance reste distincte et inchangée.

## D0034 — Conflits balisés et deuxième essai de schéma

La note annuelle Oracle 2026 nomme les 605 et 417 millions comme placements négociables en dette et actions, alors que leur concept balisé vise des actions sans juste valeur facilement déterminable. Ils ne deviennent pas des stocks privés par le nom du concept. Les 9,4 et 9,3 milliards de revenus issus de revenus différés portent aussi des contextes annuels décalés par rapport au texte. Les faits bruts restent intacts ; fact_semantic_quarantines exclut les attributions numériques concernées.

Une ligne de la note trimestrielle Oracle utilisait standard_application comme cause de retraitement au lieu du nom d’énumération accounting_change. Son unique deuxième essai de schéma corrige ce nom et passe ; le premier rejet reste conservé.

Le montant Microsoft OpenAI de 11,9 milliards est un financement cumulé, pas un flux de l’exercice et pas une preuve de composition exclusivement en numéraire. Les revenus de 24,1 milliards incluent les paiements de partage de revenus ; ils ne deviennent pas tous du revenu Azure. La cession Ampere Oracle donne des encaissements de 4,3 milliards pour un ensemble actions, dette et option, sans allocation arbitraire au principal remboursé.


## D0035 — Conflits de contexte et écriture des exports

La Note 1 annuelle CoreWeave 2025 a été intégralement lue, avec les 55 candidats et les trois morceaux de texte. Un premier affichage groupé avait tronqué le début de l’en-tête ; cet en-tête a été resservi seul et intégralement relu avant l’unique soumission. Les deux balises de 500 millions portent une date de clôture de décembre alors que le texte décrit le séquestre de l’IPO et sa libération en avril 2025. Trois membres Customer B/C contredisent les lignes du tableau ; une lettre ne prouve par ailleurs aucune continuité d’identité d’un exercice à l’autre. Des zéros balisés correspondent à « not material » dans le texte. Ces conflits restent explicites sans réécriture des faits ni attribution par égalité de montant.

Dans la note Oracle de février 2026, les trois dates de départ typées du RPO sont décalées par rapport aux fenêtres futures décrites à la clôture. Le RPO total reste distinct et utilisable ; ses allocations contestées restent inconnues. Les décisions D0034/D0035 alimentent maintenant une vue de conflits dans la sélection numérique. Les occurrences de même identité sémantique du même dépôt, y compris companyfacts, ne peuvent contourner une exclusion ; un dépôt corrigé ultérieur n’est pas exclu par cette règle. Le test vérifie la conservation brute, le blocage de la copie API et l’admission d’un autre concept dimensionné ou d’un dépôt ultérieur.

Les huit exports Parquet sont entièrement écrits dans un répertoire temporaire avant remplacement de chaque fichier. Une sauvegarde intermédiaire ne peut donc prendre un fichier en cours d’écriture. Cette protection garantit l’intégrité de chaque fichier, sans prétendre rendre atomique le remplacement simultané des huit fichiers. La reconstruction des rangs physiques depuis le cache est terminée.


## D0036 — Durées de vie, gains et absence de matérialité

La note annuelle Amazon 2025 est entièrement lue avec ses 168 candidats et cinq fragments. La réduction de six à cinq ans est limitée à une partie des serveurs et équipements réseau et prend effet le 1er janvier 2025. Son effet de 1,4 milliard est une hausse de charge avant impôt ; la baisse de résultat net de 1,0 milliard est après impôt et ne s’additionne pas au même pont. Le changement d’estimation prospectif ne devient pas un retraitement d’erreur. Les dépréciations de 1,3 milliard, dont 610 millions au quatrième trimestre, portent principalement sur des biens et locations de magasins physiques ; elles ne deviennent pas des pertes sur les participations IA.

Les 5,3 milliards investis en notes Anthropic de Q3 2023 à Q4 2024 ne sont pas répartis arbitrairement entre les exercices. Les stocks à la juste valeur, les gains AOCI reclassés, les hausses de prix et les nouveaux investissements restent distincts. Les gains Q1 2026 annoncés dans la note annuelle restent prévisionnels dans cette source, même si une pièce ultérieure les confirme ou les révise. Le signe des balises de valorisation des warrants est celui d’une charge : il se renverse pour un effet sur le résultat. Le total des warrants décrit comme Level 2 et 3 ne se voit pas entièrement attribuer à Level 2 sur la seule dimension du candidat.

La note annuelle Alphabet 2025 dit que les pertes sur goodwill ne sont pas matérielles, et non qu’elles sont nulles. Ses trois zéros balisés restent bruts mais exclus de l’attribution numérique exacte. L’ASU 2023-09 est effectivement adopté avec comparatifs mis à jour ; la mention d’ASU encore évalués ne devient pas une adoption. Le rapport ICFR de l’auditeur Amazon est intégralement contenu dans le bloc de contrôle lu ; les simples renvois à des opinions situées ailleurs chez NVIDIA et Alphabet ne sont pas extraits comme si ces opinions avaient été lues.


## D0037 — Contextes historiques IPO et précision des chiffres

La Note 1 CoreWeave de septembre 2025 est entièrement lue. Le fait de séquestre portant le membre IPO et une date de septembre contredit la libération d’avril ; le fait distinct portant la DDTL et une date de mars n’est pas exclu. Les frais différés de l’IPO déjà reclassés en capitaux propres ne deviennent pas un actif différé de clôture en septembre. Deux nouvelles quarantaines conservent leurs faits bruts.

Les 36 590 000 actions IPO précisément publiées dans le trimestre sont compatibles avec les 37 millions arrondis publiés plus tard. La vérification d’une multiplication entre chiffres arrondis doit utiliser leurs intervalles de précision ; un écart de produit nominal ne prouve pas à lui seul une contradiction. Les flags historiques restent immuables et leur éventuelle résolution appartient aux contrôles de phase 3, avec preuve de précision, sans modification des observations ni fabrication de nombre exact.

L’accélération de l’échéance de la dette au closing de l’IPO est un déclencheur contractuel documenté ; elle ne prouve ni défaut ni waiver de covenant financier. L’efficacité des swaps comme couverture ne désigne pas l’efficacité de l’ICFR. Les material weaknesses publiées dans le bloc de contrôle de septembre sont déjà existantes ; elles ne reçoivent pas une nouvelle date d’apparition à chaque rapport.


### D0038 — Contextes historiques IPO CoreWeave dans le dépôt Q2 2025

La note 1 lue intégralement annonce la libération de 500 millions USD au cours d’avril 2025 et le reclassement des frais IPO de 31 millions USD en capitaux propres. Les contextes de restricted cash IPO au 30 juin et DDTL au 30 avril, ainsi que celui de deferred offering costs au 30 juin, contredisent cette chronologie. Les trois faits bruts restent intacts ; leurs valeurs sont exclues des calculs dépendants par la quarantaine sémantique. La mention de maturité accélérée par l’IPO décrit un déclencheur contractuel et ne prouve pas un défaut financier.


### D0039 — Concepts contradictoires des placements cotés Oracle FY2025

Lecture complète de la note 1 : les montants de 417 millions USD au 31 mai 2025 et 207 millions au 31 mai 2024 correspondent à des titres de dette et actions marketable. Leur concept balisé without readily determinable fair value contredit ce périmètre. Les deux faits restent bruts et sont exclus des calculs dépendant de ce concept. Les soldes non-marketable combinés de 2,1 et 2,0 milliards restent distincts et ne sont pas entièrement attribués à Ampere.


### D0040 — Chronologie Q1 CoreWeave et précision des actions au client

Note 1 Q1 2025 lue intégralement : 500 millions USD d’escrow constituent bien le solde restricted cash au 31 mars, contrairement aux contextes postérieurs à la libération d’avril. Le fait deferred offering costs de 31 millions au 31 mars contredit le reclassement en capitaux propres lors de l’IPO achevée et reste exclu des calculs. Les 8 750 000 actions exactes au client stratégique, émises le 31 mars à 40 USD, expliquent 350 millions ; une présentation ultérieure à 9 millions arrondis ne prouve donc pas une contradiction. Préserver les anciens flags immuables et résoudre cette différence par la précision dans la phase 3. Le client demeure anonyme dans cette note ; le renvoi à Note 2 ne prouve pas à lui seul un nom ou un traitement contra-revenue.


### D0041 — Contexte RPO FY2025 Oracle et essai de schéma Q3

La confrontation à la note de février 2025 a permis de repérer un conflit supplémentaire dans la note annuelle FY2025 déjà lue : le membre typé du taux de 23 % porte le 1er juin 2027 alors que « month 37 to month 60 » après le 31 mai 2025 commence le 1er juin 2028. Le fait et l’observation historique restent immuables ; une quarantaine exclut leur utilisation numérique dépendante. Le total RPO et les tranches correctes ne sont pas exclus.

La ligne des 48,4 milliards de leases non commencés de février 2025 employait category au lieu de la colonne category_id. Son unique deuxième essai de schéma corrige ce nom ; le rejet initial est conservé et les 36 lignes acceptées au premier essai ne sont pas resoumises.


### D0042 — Prévisions operating income Amazon et dimension des warrants

La note annuelle 2024 est lue intégralement avec 168 candidats et cinq fragments ; deux affichages tronqués sont resservis seuls avant soumission. Les effets prévus 2025 de +900, −700 et −600 millions portent le concept NetIncomeLoss alors que les trois phrases nomment operating income. Ils ne deviennent ni du résultat net ni des effets réalisés. Cinq faits restent bruts mais exclus des calculs dépendants, dont les deux totaux de warrants décrits comme Level 2 et 3 alors que leur dimension désigne seulement Level 2.

Le raccourcissement de six à cinq ans d’un sous-ensemble des serveurs et réseaux prend effet le 1er janvier 2025, connu dans le dépôt du 7 février : l’événement F7 est distinct de l’effet financier encore prévu. Les 920 millions de Q4 2024 sont une charge réalisée de dépréciation accélérée et charges liées ; le total ne devient pas exclusivement une perte sur placement. L’allongement antérieur et son effet net après impôt restent distincts.


### D0043 — Goodwill Alphabet FY2024

La note annuelle 2024, lue intégralement, qualifie les pertes sur goodwill de non matérielles pour les périodes présentées. Les trois zéros balisés pour 2022–2024 ne prouvent pas un zéro exact et restent bruts, exclus des calculs dépendants dans ce dépôt. La quarantaine d’un dépôt ultérieur ne remplace pas cette preuve propre à l’accession. L’adoption ASU2023-07 en 2024 et la mise à jour des comparatifs concernent les disclosures ; la mention des placements et arrangements commerciaux contemporains reste anonyme et sans allocation de montant.


### D0044 — Périmètre combiné des placements Oracle et vie des équipements

La note de novembre 2024 est intégralement lue, avec ses 68 candidats. Ses stocks non-marketable réunissent dette, actions et instruments liés, y compris le total des placements Ampere après la description de dette convertible ; ils ne prouvent pas des stocks exclusivement en actions comme le concept EquitySecuritiesFvNiAndWithoutReadilyDeterminableFairValue. Les trois faits sont exclus de l’attribution dépendante. Deux candidats de durée relatifs aux serveurs et réseaux portent un concept de vie d’actifs incorporels ; leurs faits bruts et durées restent conservés sans attribution d’une vie incorporelle.

La confrontation explicite des dix faits déjà choisis dans les notes entièrement lues de février, mai et août 2025 confirme le même conflit de périmètre. Leurs observations historiques ne sont ni remplacées ni resoumises : dix quarantaines supplémentaires excluent les calculs dépendants. Les montants d’investissements convertibles de la période et les parts de propriété restent distincts de ces soldes combinés. Cette revue n’est pas une nouvelle passe de lecture.

D0045 — Oracle FY2025 Q1: après lecture intégrale de la note et de ses 42 candidats, cinq références sont mises en quarantaine. Deux durées de serveurs sont balisées comme immobilisations incorporelles et trois stocks combinent dette et actions sous une balise actions seule. Les faits bruts et observations historiques restent conservés.

D0046 — Oracle FY2024: lecture intégrale des 68 candidats et de la note. Neuf références en quarantaine : deux durées tangibles balisées incorporelles, deux stocks négociables balisés non négociables, quatre stocks dette/actions balisés actions seules et une date de début RPO mois37–60 décalée de douze mois. Faits bruts et observations conservés.

D0047 — Oracle FY2024 Q3 : après lecture intégrale des 57 candidats et de la note, trois stocks mixtes dette/actions sont mis en quarantaine pour leur balise actions seules. L’amendement du 5 mars est un événement postérieur au 29 février connu au dépôt, sans preuve de waiver de covenant financier. L’unique nouvelle tentative de schéma de D0046 retire le type non prévu equity_secondary sans changer le sens secondaire ni les lignes acceptées.

D0048 — NVIDIA FY2024 : après lecture intégrale des 14 candidats et des deux parties, six effets annuels de durée de vie (coût des ventes, charges, résultat opérationnel, résultat net après impôt et BPA) sont balisés seulement au quatrième trimestre. Mise en quarantaine sans remplacement narratif des montants ni altération des faits. Les durées augmentent, sans événement F7.

D0049 — Amazon FY2023 : après lecture intégrale des 170 candidats et de la note, les deux stocks totaux de warrants Level2 et Level3 sont mis en quarantaine pour leur dimension Level2 seule. La prévision de résultat opérationnel 2024 de 3,1 milliards est correctement balisée OperatingIncomeLoss et reste une prévision. L’investissement Anthropic de Q3 et l’engagement supplémentaire optionnel sont séparés ; pas de paiement explicite ni de revenu AWS attribuable.

D0050 — Alphabet FY2023 : note et 17 candidats intégralement lus. Trois zéros goodwill restent bruts et sont exclus des calculs : le texte dit non matériel, pas aucune perte. L’allongement serveurs/réseau de janvier 2023 et ses effets annuels avant et après impôt sont distincts. Aucun investissement ou contrat commercial anonyme n’est attribué à une entité nommée.

D0051 — Oracle FY2024 Q2 : note et 52 candidats entièrement lus. Deux stocks combinés dette/actions/instruments restent bruts, exclus de leur balise actions seules. La majorité attribuée à une partie liée reste anonyme dans ce bloc et ne devient pas Ampere par proximité avec des dépôts ultérieurs. Les options jusqu’à juin 2025 ne prouvent ni exercice ni contrôle réalisé.

D0052 — Oracle FY2024 Q1 : après lecture intégrale de la note et des 30 candidats, deux revenus reconnus trimestriels portent une période annuelle antérieure, et deux stocks combinés dette/actions portent un concept actions seules. Quatre quarantaines sans remplacement narratif. RPO et pourcentages ont leurs dates correctes ; partie liée des placements reste anonyme et options conditionnelles.

D0053 — Oracle FY2023 : note et 61 candidats intégralement lus. Deux durées de serveurs tangibles portent un concept incorporel et deux stocks mixtes dette/actions portent un concept actions seules : quatre quarantaines, faits bruts conservés. Cerner est consolidé prospectivement dès le 8 juin 2022 ; les options de la partie liée anonyme ne prouvent aucun exercice. Goodwill explicitement sans impairment, contrairement aux formulations non matérielles.

D0054 — Oracle FY2023 Q3 : lecture complète des 59 candidats et de la note. Deux durées tangibles sous concept incorporel et deux stocks dette/actions sous concept actions seules mis en quarantaine, faits bruts conservés. RPO correctement datés ; Cerner consolidé prospectivement. La tentative unique de schéma D0053 ajoute le déclencheur conditionnel explicite à la seule ligne rejetée, sans resoumettre les lignes acceptées.

D0055 — Amazon FY2022 : 166 candidats et note entièrement lus. Prévision vidéo 2023 de résultat opérationnel balisée résultat net, et deux stocks totaux de warrants seulement principalement Level2 sous dimension Level2 seule : trois quarantaines. Les allongements équipement et vidéo sont séparés, avant/après impôt distincts, aucun paiement Anthropic importé.

D0056 — Alphabet FY2022 : note et 19 candidats entièrement lus. Trois zéros goodwill exclus car non matériel ne prouve pas absence. Les liens investissement/contrat commercial restent anonymes. Allongement de janvier 2023 postérieur à la clôture 2022 ; approbation du split et effet au 15 juillet distingués.

D0057 — Oracle FY2023 Q2 : lecture complète des 60 candidats et de la note. Deux durées de serveurs sous concept incorporel et deux stocks dette/actions sous concept actions seules mis en quarantaine, sans altérer les données brutes. RPO correctement datés, effets de durée avant impôt et stocks non assimilés à des paiements.

D0058 — Oracle FY2023 Q1 : lecture complète des 35 candidats et de la note. Quatre conflits balise/texte supplémentaires mis en quarantaine, faits bruts inchangés. Les options évoquées vont ici jusqu’à décembre 2023, sans importer la date juin 2025 des dépôts ultérieurs ; l’investie reste anonyme dans ce bloc.

D0059 — Amazon Q2 2022 : lecture complète des 141 candidats et de la note. Six effets résultat net/BPA portent un signe négatif alors que le texte décrit une réduction de perte, donc un bénéfice pour le résultat. Ils sont mis en quarantaine sans inversion des faits bruts ni remplacement narratif ; les effets de charge d’amortissement restent distincts et avant impôt. La participation Rivian passe ici à 18 % du capital contre 17 % dans la note de septembre, sans assimiler cette variation à un nouveau paiement.

D0060 — Meta Q2 2022 : lecture complète des cinq candidats et de la note. Le texte indique une réduction de charge de 252 millions et une hausse du résultat net de 206 millions, mais les signes balisés sont inverses ; deux faits mis en quarantaine, sans correction quantitative. ASU 2022-03 est encore présenté comme non adopté dans ce dépôt et la date du dépôt suivant n’est pas importée.

D0061 — Oracle FY2022 : lecture complète des 59 candidats et des deux parties de la note. Deux stocks mixtes dette/actions sous balise actions seules mis en quarantaine. Aucun changement de durée de serveur ni clause de clôture Cerner dans ce bloc ; les clauses des dépôts ultérieurs ne sont pas importées. Les zéros goodwill sont ici explicitement confirmés par le texte, contrairement aux clauses « non significatif ».

D62 — Lecture intégrale de la première note Oracle au 28 février 2022 : les deux stocks de placements privés mêlent dette, titres de capital et instruments associés ; leurs balises de titres de capital seuls ne justifient pas cette attribution. Deux faits exclus des calculs dépendants, données brutes conservées.

D63 — Amazon FY2021 : trois en-têtes, 152 candidats et deux parties de texte intégralement lus. Les stocks totaux de warrants de 2020 et 2021 sont seulement principalement Level2 ; les deux balises exclusivement Level2 sont exclues des calculs dépendants sans remplacement narratif ni modification brute.

D64 — Alphabet FY2021 : note entière et 21 candidats lus. Trois valeurs zéro de goodwill (2019–2021) balisent une absence de pertes matérielles, qui ne prouve pas une perte exactement nulle. Quarantaine sans remplacement numérique ni modification brute.

D65 — Marvell juillet 2021 : cinq candidats et première note entière lus. Innovium est une intention d’acquisition annoncée après clôture, avec prix brut en actions de 1,1 milliard, cash et exercices attendus mêlés de 145 millions et coût net de 955 millions. Les deux dernières balises isolent à tort du cash acquis seul et une contrepartie en capital ; quarantaine sans remplacement. Aucune clôture effective d’octobre importée.

D0066 — Oracle FY2021 : lecture complète des 61 candidats et des deux parties de la note. Deux totaux actions et instruments associés ne permettent pas une attribution aux seules actions et sont mis en quarantaine, sans inventer leur ventilation. Les dates RPO et les périodes de reprise du passif contractuel sont cohérentes. Les reclassements sont explicitement sans effet sur revenus, résultat opérationnel et résultat net. Le gain de 193 millions des placements pour avantages au personnel est compensé par une charge opérationnelle ; pas de double comptage.

D0067 — Marvell FY2021 : lecture intégrale des 15 candidats et de la première note. Trois stocks de frais différés explicitement au 30 janvier 2021 sont balisés au 29 octobre 2020 et mis en quarantaine. Le projet Inphi reste signé et soumis aux approbations dans ce dépôt : les engagements de prêts ne sont pas du principal tiré, les frais de rupture restent conditionnels, aucune clôture ultérieure ni domiciliation américaine effective n’est importée.

D0068 — Marvell octobre 2020 : lecture intégrale des 15 candidats et de la note. Trois stocks de frais de financement au 31 octobre sont balisés au 29 octobre et mis en quarantaine. Les engagements de 4 milliards (2,5 + 0,75 + 0,75) demeurent conditionnels et ne sont pas additionnés à leurs montants actualisés dans le dépôt annuel ultérieur. Aucun financement tiré ou frais de rupture payé n’est inféré.

D0069 — Amazon 8-K du 14 septembre 2026 : six observations numériques en livres sterling rejetées par le validateur qui ne reconnaissait pas le symbole £. Défaut corrigé pour les passes futures avec test de devise, sans réadmission ni seconde passe sémantique du bloc existant. Les six lignes originales restent rejetées et la couverture numérique reste incomplète, sans équivalent USD inventé.

D0070 — Amazon 8-K du 12 juin 2026 : livres canadiennes conservées en CAD, sans taux de change inventé. Validation étendue à C$ avant la première passe de ce bloc ; un test prouve que C$ ne justifie pas USD. Les rejets GBP déjà écrits restent intacts. Prix public, principal et estimation nette non additionnables.

D0071 — Alphabet 8-K du 21 mai 2026 : principal en JPY conservé sans conversion USD ; la description littérale « Japanese yen-denominated » établit la devise. Validateur étendu avant la première passe et test distinguant le symbole ¥ seul, insuffisant pour identifier la devise. Principal agrégé et sept séries non additionnables.

D0072 — CoreWeave 8-K du 14 avril 2026 : le texte indique littéralement 1 750 000 dollars de notes 9,750%2031, contre 1 750 000 000 pour cette même émission dans le dépôt du 21 avril. Les deux sources restent inchangées, conflit de montant signalé pour exclusion des agrégats dépendants, sans correction de faute présumée. Les convertibles distincts4bn et leurs produits/derivés ne sont pas affectés par ce conflit.

D0073 — Marvell 8-K du 15 avril 2026 : Item8.01 indique prix de vente aux souscripteurs99,235% et prix public99,885% du principal1bn. Le prix aux souscripteurs implique992,35m, incompatible avec993,5m de produit net après discount et avant autres frais déclaré dans Item1.01. Observation initiale conservée ; calculs de cash dépendants à bloquer jusqu’à résolution explicite, sans modifier ni inventer de montant source.

D0074 — CoreWeave 8-K/A du 7 juillet 2025 : première clause dit que Merger Sub fusionnera dans Core Scientific (« Company »), puis que « Miami » survivra. Contradiction textuelle conservée ; aucun choix automatique du survivant ni consolidation actuelle. Prix d’échange0,1235 et frais270m conditionnels ne sont pas des flux actuels ; future modification d’indentures liée à la fusion n’est pas un F4effectif.

D75 — La ligne narrative agrégée de 1,5 milliard USD du contrat AMD signé le 10 mars 2025 a été rejetée SEM : la citation rédigée ne contenait pas le montant, même si la linkage_quote le contenait. Le rejet reste immuable pour cet as_of, sans réadmission. Les deux composantes 875/625 millions explicitement citées ont été admises ; aucune nouvelle observation agrégée ni preuve de trésorerie ne doit contourner ce rejet.

D76 — L’échange Microsoft/Activision du 6 novembre 2023 nomme les nouvelles notes 2047 à 4,500 % puis leur attribue 3,400 % dans la liste des taux et échéances. Les deux formulations sont conservées ; le coupon 2047 et les intérêts calculés qui en dépendent restent indéterminés sans résolution documentaire. Les faces échangées/annulées, nouvelles faces et anciens soldes distincts ne sont pas des encaissements. Les suppressions de clauses ont été exécutées le 27 octobre mais sont devenues opérantes le 6 novembre : F4 daté du 6 novembre sans inférer un manquement.

D77 — AMD notes 2052 : le texte fixe l’échéance au 1er juin 2052 mais la date de par call au 1er décembre 2052, dite six mois avant l’échéance. Ces indications sont incompatibles ; aucune correction implicite vers décembre 2051. L’échéance littérale et le conflit de par call restent tracés, tout calcul de fenêtre de remboursement 2052 dépendant de la date contradictoire est indéterminé. Aucun remboursement effectif n’est publié ici.
