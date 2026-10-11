# Bilan des quatre approfondissements

Sources arrêtées au **9 octobre 2026**, comme dans la livraison précédente. Le travail est effectué par un seul agent, sans audit indépendant. Les quatre approfondissements décrivent les onze groupes initiaux et leurs contreparties. Les douze nouveaux groupes font l’objet de la première analyse distincte dans entites_ajoutees.md.

**La découverte la plus précise est le montage Cerebras–OpenAI : un prêt client, des prestations qui peuvent rembourser ce prêt, et des warrants liés au contrat commercial.** Les pièces établissent ces mécanismes ; elles ne démontrent pas une demande artificielle ni une fragilité attribuable à tout le secteur.

## 1. Séries et dates

Le calcul historique tient désormais compte de la date officielle de publication quand elle suit la réception du dépôt par la SEC. Les dernières périodes AMD (27 juin 2026) et Broadcom (2 août 2026) sont rétablies dans la vue « connue à l’époque ». La synthèse financière utilise la vue révisée ; les deux vues restent disponibles. Le diagnostic ne trouve aucun chiffre publié après son instant de connaissance.

Les divergences comptables préexistantes ne sont pas effacées pour faire passer les contrôles. Le détail actualisé figure dans audit/controls.csv et work/delivery_verification.json.

## 2. CoreWeave : liquidité et prêteurs

Au **30 juin 2026**, CoreWeave publie **5,524 Md$ de trésorerie non restreinte**. Les échéances de principal sont **4,413 Md$ pour le reste de 2026**, **6,184 Md$ en 2027** et **4,416 Md$ en 2028**. Les dates mensuelles ne sont pas publiées.

| Horizon depuis le 30 juin 2026 | Principal exigible : borne basse → haute | Principal / trésorerie : borne basse → haute |
| --- | ---: | ---: |
| 12 mois | 4,413 → 10,597 Md$ | 0,798877 → 1,918357 |
| 24 mois | 10,597 → 15,013 Md$ | 1,918356 → 2,717777 |

Ces fourchettes utilisent uniquement les échéances annuelles publiées ; elles excluent les intérêts, baux et autres obligations de financement. Elles ne mesurent pas une probabilité de défaut. Au deuxième trimestre 2026, le flux de trésorerie opérationnel est de 679 M$, le capex payé de 6,422 Md$ et le FCF de base de −5,743 Md$.

Les dépôts originaux permettent de suivre **87 positions de prêts, comparatifs et republications compris, auprès de 11 prêteurs**. Le fichier lender_positions.csv conserve coût, juste valeur, date, devise, instrument et lignage. Une position à la juste valeur ne mesure ni la taille du crédit syndiqué ni la perte probable. La part des intérêts PIK et le statut non-accrual par position restent non déterminés dans cette tranche ; leur lecture spécifique n’est pas terminée.

## 3. NVIDIA–CoreWeave et AMD–Meta

**NVIDIA–CoreWeave.** Le MSA du 10 avril 2023, déposé le 25 septembre 2025, a été lu intégralement. Il prévoit une interdiction de compensation par le client, une libération des obligations de paiement futures après une résiliation conforme, et la priorité des bons de commande sur le MSA. Le 8-K du 15 septembre 2025 décrit séparément le nouveau bon de commande de **6,3 Md$**, avec achat de capacité résiduelle invendue jusqu’au 13 avril 2032. Sa valeur initiale n’est pas un versement et le MSA ne suffit pas à reconstituer son calendrier ou toutes ses conditions. Le bon de commande complet n’a pas été retrouvé dans cette recherche ciblée.

Les **2 Md$ versés par NVIDIA le 23 janvier 2026** apparaissent dans deux dépôts de CoreWeave : c’est la même opération, à compter une seule fois. Les paiements de NVIDIA à CoreWeave au titre du MSA ne deviennent pas automatiquement du chiffre d’affaires reconnu.

**AMD–Meta.** Le warrant du 23 février 2026 porte sur un maximum de **160 millions d’actions**, à **0,01 $ par action**. Les annexes E et F, relatives à l’acquisition et à l’exercice, sont masquées. La clause fiscale vise une remise ou un rabais commercial ; elle n’établit pas à elle seule le traitement US GAAP ni une remise comptabilisée. Le Master Purchase Agreement et son Amendment Eight sont cités ; leurs textes complets n’ont pas été retrouvés dans le corpus ciblé. Aucun plafond de warrant n’est converti en financement payé.

## 4. Contreparties privées et véhicules

**Cerebras–OpenAI OpCo, LLC.** Le prêt signé le **5 janvier 2026** porte sur **1 004 571 259 $**, avec échéance au plus tard le 31 décembre 2032 et intérêt nominal de 6 %. La note de dette de juin rapporte des encaissements arrondis de **1 004,571 M$**, **86,327 M$ de remboursements non monétaires** et **918,244 M$ de principal restant**. Les fonds reçus sont restreints. Le remboursement peut passer par des services et d’autres crédits ; le plafond de ces remboursements et le calendrier mensuel sont masqués dans le contrat.

Le revenu OpenAI reconnu au premier semestre est de **74,4 M$**, net de **3,3 M$ d’amortissement de l’actif de warrants**. Il est distinct des remboursements non monétaires. Cerebras déclare évaluer ensemble le prêt et le contrat de services, avec une composante de financement significative. Le warrant est présenté comme une incitation aux achats ; une tranche de **4 459 337 actions** est liée au dépôt du prêt. Le calendrier public reste partiellement masqué.

**Anthropic.** Zoom publie **300,9 M$ d’investissements supplémentaires** sur son semestre terminé le 31 juillet 2026, **1 612,7 M$ de gains non réalisés** sur le trimestre et **3 134,5 M$ de valeur comptable** à cette date. Salesforce publie **3 Md$ de gains non réalisés** sur le semestre, dont **2,7 Md$ sur le trimestre** : ce ne sont pas de nouveaux apports de cash démontrés. Ces montants ne s’additionnent pas comme financements reçus par Anthropic.

**Autres véhicules.** Eightco publie **92,6 M$ d’achat d’une participation dans un SPV non consolidé**, exposé indirectement à OpenAI. L’apport primaire à OpenAI n’est pas établi. Applied Digital comptabilise **121,2 M$ d’actif d’incitation locative** lié au warrant Building 4 remis à CoreWeave ; ce warrant a ensuite été cédé à des tiers. Apollo décrit une opération de **35 Md$** avec Broadcom facilitant les infrastructures d’Anthropic : la garantie d’Athene représente **15 % de l’obligation d’achat restante**, avec un accord de remboursement par un tiers portant sur **35 % des paiements éventuels**. L’obligation restante n’étant pas chiffrée dans cette note, aucun montant de garantie n’est calculé en multipliant 35 Md$ par 15 %.

## Couverture et reprise

La recherche a balayé **21 archives BDC** et **12 archives mensuelles de Notes Data Sets**, d’octobre 2025 à septembre 2026. Elle a conservé **95 candidats textuels**, qui servent à trouver les sources et ne valent pas preuves financières. Les dépôts originaux ont été récupérés pour 13 prêteurs nommés et 8 autres déposants ciblés, soit **34 dépôts périodiques**. Le corpus contient **168 Form D / D-A uniques de 118 CIK**, dont 152 formulaires classés « Pooled Investment Fund » : ce sont des dépôts, pas 168 financements des laboratoires.

Un Form D publie des montants cumulatifs d’offres et de titres vendus qui peuvent inclure des contreparties non monétaires et des engagements futurs obligatoires. Les amendements sont rapprochés par CIK et date de première vente ; sans date, le rapprochement reste non établi. form_d_series.csv conserve le dernier dépôt connu à chaque fin de trimestre : les montants sont cumulatifs, pas des flux trimestriels de cash. Une modification publiée ensuite ne remplace pas une ancienne valeur historique. Aucun de ces montants n’est attribué automatiquement à OpenAI ou Anthropic. Les archives anciennes non collectées, les candidats non lus et les parties non résolues restent visibles dans les exclusions.

Les sources sont reliées aux citations dans deepening_evidence.csv ; les chiffres et leurs périodes dans deepening_measures.csv, lender_positions.csv et form_d_disclosures.csv. Les observations sont conservées et le code reconstruit les huit tables hors ligne. Les critères des annexes E et F restent inchangés. Les commits intermédiaires et la livraison finale sont sauvegardés sur https://github.com/jsiaut/codex_test.

## Positions de prêteurs à leur dernière date vérifiée

| Déposant | Dernière date vérifiée | Position telle que publiée | Coût | Juste valeur | Juste valeur / coût |
| --- | --- | --- | ---: | ---: | ---: |
| Ares Core Infrastructure Fund | 2026-06-30 | Coreweave Financing DDTL V, LLC, First lien senior secured loans | 5,571 M$ | 5,616 M$ | 1.008078 |
| AB Private Lending Fund | 2026-06-30 | US Corporate Debt  /  1st Lien/Senior Secured Debt  /  CoreWeave Financing DDTL V, LLC  /  IT Services  /  Term Loan  /  8.15% (S + 4.50%)  /  11/15/2031 | 0,041 M$ | 0,045 M$ | 1.086313 |
| Nuveen Churchill Private Capital Income Fund | 2026-06-30 | Coreweave Financing DDTL V, LLC  /  First Lien Debt | 0,092 M$ | 0,101 M$ | 1.097826 |
| PIMCO Capital Solutions BDC Corp. | 2026-06-30 | Debt Investments  /  First Lien Senior Secured  /  Technology  /  CoreWeave Compute Acquisition Co. IV, LLC Initial Term Loan  /  SOFR + 6.000% /  9.700 %  /  05/16/2029 | 2,093 M$ | 2,158 M$ | 1.031056 |
| BlackRock Private Credit Fund | 2026-06-30 | Debt Investments IT Services Coreweave Financing DDTL V LLC Instrument First Lien Delayed Draw Term Loan Ref SOFR(M) Spread 4.50% Total Coupon 8.12% Maturity 11/6/2031 | 0,784 M$ | 0,855 M$ | 1.090587 |
| Carlyle Secured Lending III | 2024-09-30 | First Lien Debt, CoreWeave Compute Acquisition Co. II, LLC, High Tech Industries 1 | 1,562 M$ | 1,552 M$ | 0.993598 |
| Carlyle Secured Lending III | 2024-09-30 | First Lien Debt, CoreWeave Compute Acquisition Co. II, LLC, High Tech Industries | 1,139 M$ | 1,167 M$ | 1.024583 |
| MSD Investment Corp. | 2026-06-30 | Investments Investments - non-controlled/non-affiliated First Lien Debt Software & Services CoreWeave - Delayed Draw Term Loan Reference Rate and Spread S + 6.00% Interest Rate Floor 0.00% Interest Rate 9.61% Maturity Date 8/26/2030 | 26,669 M$ | 26,950 M$ | 1.010537 |
| Palmer Square Capital BDC Inc. | 2026-06-30 | Portfolio Company Debt Investments Semiconductors and Semiconductor Equipment CoreWeave Financing DDTL V LLC Investment First Lien Senior Secured Delayed Draw Loan Interest Rate 8.12% (S + 4.50%) Maturity Date 11/15/2031 | 1,776 M$ | 1,883 M$ | 1.060494 |
| Carlyle Credit Solutions, Inc. | 2026-06-30 | Investment  /  Non-Affiliated Issuer  /  First Lien Debt  /  CoreWeave Compute Acquisition Co. IV, LLC  /  High Tech Industries | 12,429 M$ | 12,432 M$ | 1.000241 |
| Carlyle Credit Solutions, Inc. | 2026-06-30 | Investment  /  Non-Affiliated Issuer  /  First Lien Debt  /  CoreWeave Compute Acquisition Co. II, LLC  /  High Tech Industries | 1,136 M$ | 1,157 M$ | 1.018486 |
| Great Elm Capital Corp. | 2026-06-30 | Coreweave Compute Acquisition Co. IV, LLC Industry Technology Security 1st Lien, Secured Loan Interest Rate 3M SOFR + 6.00% (9.68%) Initial Acquisition Date 5/29/2024 Maturity 5/16/2030 | 2,070 M$ | 2,145 M$ | 1.036232 |
| Great Elm Capital Corp. | 2026-06-30 | Coreweave Compute Acquisition Co. II, LLC Industry Technology Security 1st Lien, Secured Loan Interest Rate 3M SOFR + 9.62% (13.29%) Initial Acquisition Date 8/21/2023 Maturity 7/31/2028 | 9,866 M$ | 10,234 M$ | 1.037300 |
| Great Elm Capital Corp. | 2026-06-30 | CoreWeave Financing DDTL V, LLC Industry Technology Security 1st Lien, Delayed Draw Term Loan Interest Rate 1M SOFR + 4.50% (8.12%) Initial Acquisition Date 5/6/2026 Maturity 11/14/2031 | 2,590 M$ | 2,812 M$ | 1.085714 |
| Carlyle Secured Lending, Inc. | 2026-06-30 | Investment  /  Non-Affiliated Issuer  /  First Lien Debt  /  CoreWeave Compute Acquisition Co. IV, LLC  /  High Tech Industries | 16,576 M$ | 16,575 M$ | 0.999940 |
| Carlyle Secured Lending, Inc. | 2026-06-30 | Investment  /  Non-Affiliated Issuer  /  First Lien Debt  /  CoreWeave Compute Acquisition Co. II, LLC  /  High Tech Industries | 1,829 M$ | 1,851 M$ | 1.012028 |

## Mesures ciblées publiées

| Déposant / CIK | Mesure | Période | Montant publié |
| --- | --- | --- | ---: |
| 0001108524 | named_investment_unrealized_gain | 2026-05-01 → 2026-07-31 | 2 700,000 M$ |
| 0001108524 | named_investment_unrealized_gain | 2026-02-01 → 2026-07-31 | 3 000,000 M$ |
| 0001144879 | customer_lease_incentive_asset | none → 2025-08-28 | 121,200 M$ |
| 0001585521 | named_investment_acquisitions | 2026-02-01 → 2026-07-31 | 300,900 M$ |
| 0001585521 | named_investment_unrealized_gain | 2026-05-01 → 2026-07-31 | 1 612,700 M$ |
| 0001585521 | named_investment_carrying_amount | none → 2026-07-31 | 3 134,500 M$ |
| 0001858681 | capital_solution_contract_size | 2026-04-01 → 2026-06-30 | 35 000,000 M$ |
| 0001892492 | indirect_investment_carrying_amount | none → 2026-06-30 | 92,600 M$ |
| 0002021728 | customer_working_capital_loan_received | 2026-01-01 → 2026-06-30 | 1 004,571 M$ |
| 0002021728 | customer_working_capital_loan_noncash_repayment | 2026-01-01 → 2026-06-30 | 86,327 M$ |
| 0002021728 | customer_working_capital_loan_outstanding | none → 2026-06-30 | 918,244 M$ |
| 0002021728 | named_customer_revenue | 2026-01-01 → 2026-06-30 | 74,400 M$ |

Les tableaux conservent la base propre à chaque montant. « Dernière date vérifiée » ne garantit pas que la position subsiste au 9 octobre 2026.

## Pièces SEC directement consultées

- [TERAWULF INC. — 10-Q, 0001083301-22-000023](https://www.sec.gov/Archives/edgar/data/1083301/000108330122000023/wulf-20220630x10q.htm)
- [TERAWULF INC. — 10-Q, 0001083301-22-000048](https://www.sec.gov/Archives/edgar/data/1083301/000108330122000048/wulf-20220930x10q.htm)
- [TERAWULF INC. — 10-Q, 0001083301-23-000054](https://www.sec.gov/Archives/edgar/data/1083301/000108330123000054/wulf-20230930.htm)
- [TERAWULF INC. — 10-Q/A, 0001083301-23-000060](https://www.sec.gov/Archives/edgar/data/1083301/000108330123000060/wulf-20230930.htm)
- [TERAWULF INC. — 10-K, 0001083301-24-000072](https://www.sec.gov/Archives/edgar/data/1083301/000108330124000072/wulf-20231231.htm)
- [TERAWULF INC. — 10-Q, 0001083301-24-000103](https://www.sec.gov/Archives/edgar/data/1083301/000108330124000103/wulf-20240331.htm)
- [TERAWULF INC. — 10-Q, 0001083301-24-000124](https://www.sec.gov/Archives/edgar/data/1083301/000108330124000124/wulf-20240630.htm)
- [TERAWULF INC. — 10-Q, 0001083301-24-000147](https://www.sec.gov/Archives/edgar/data/1083301/000108330124000147/wulf-20240930.htm)
- [TERAWULF INC. — 10-K, 0001083301-25-000018](https://www.sec.gov/Archives/edgar/data/1083301/000108330125000018/wulf-20241231.htm)
- [TERAWULF INC. — 10-Q, 0001083301-25-000038](https://www.sec.gov/Archives/edgar/data/1083301/000108330125000038/wulf-20250331.htm)
- [TERAWULF INC. — 10-K/A, 0001083301-25-000052](https://www.sec.gov/Archives/edgar/data/1083301/000108330125000052/terawulf-form10xkxafy2024p.htm)
- [TERAWULF INC. — 10-Q/A, 0001083301-25-000053](https://www.sec.gov/Archives/edgar/data/1083301/000108330125000053/terawulf-form10xqxaq12025p.htm)
- [TERAWULF INC. — 10-Q, 0001083301-25-000061](https://www.sec.gov/Archives/edgar/data/1083301/000108330125000061/wulf-20250630.htm)
- [TERAWULF INC. — 10-Q, 0001083301-25-000099](https://www.sec.gov/Archives/edgar/data/1083301/000108330125000099/wulf-20250930.htm)
- [TERAWULF INC. — 10-K, 0001083301-26-000031](https://www.sec.gov/Archives/edgar/data/1083301/000108330126000031/wulf-20251231.htm)
- [TERAWULF INC. — 10-Q, 0001083301-26-000092](https://www.sec.gov/Archives/edgar/data/1083301/000108330126000092/wulf-20260331.htm)
- [TERAWULF INC. — 10-Q, 0001083301-26-000166](https://www.sec.gov/Archives/edgar/data/1083301/000108330126000166/wulf-20260630.htm)
- [TERAWULF INC. — 10-K, 0001104659-22-041168](https://www.sec.gov/Archives/edgar/data/1083301/000110465922041168/wulf-20211231x10k.htm)
- [TERAWULF INC. — 10-K/A, 0001140361-23-023223](https://www.sec.gov/Archives/edgar/data/1083301/000114036123023223/brhc20052547_10ka.htm)
- [TERAWULF INC. — 10-Q, 0001437749-21-011912](https://www.sec.gov/Archives/edgar/data/1083301/000143774921011912/ikon20210331_10q.htm)
- [TERAWULF INC. — 10-Q, 0001437749-21-019685](https://www.sec.gov/Archives/edgar/data/1083301/000143774921019685/ikon20210630_10q.htm)
- [TERAWULF INC. — 10-Q, 0001437749-21-026741](https://www.sec.gov/Archives/edgar/data/1083301/000143774921026741/ikon20210930_10q.htm)
- [TERAWULF INC. — 10-Q, 0001558370-22-008985](https://www.sec.gov/Archives/edgar/data/1083301/000155837022008985/wulf-20220331x10q.htm)
- [TERAWULF INC. — 10-K, 0001558370-23-005301](https://www.sec.gov/Archives/edgar/data/1083301/000155837023005301/wulf-20221231x10k.htm)
- [TERAWULF INC. — 10-Q, 0001558370-23-009915](https://www.sec.gov/Archives/edgar/data/1083301/000155837023009915/wulf-20230331x10q.htm)
- [TERAWULF INC. — 10-Q, 0001558370-23-014682](https://www.sec.gov/Archives/edgar/data/1083301/000155837023014682/wulf-20230630x10q.htm)
- [Salesforce, Inc. — 10-Q, 0001108524-26-000190](https://www.sec.gov/Archives/edgar/data/1108524/000110852426000190/crm-20260731.htm)
- [Applied Digital Corp. — 10-K/A, 0001144879-22-000043](https://www.sec.gov/Archives/edgar/data/1144879/000114487922000043/apld-20220531.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-22-000052](https://www.sec.gov/Archives/edgar/data/1144879/000114487922000052/apld-20220831.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-23-000028](https://www.sec.gov/Archives/edgar/data/1144879/000114487923000028/apld-20221130.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-23-000101](https://www.sec.gov/Archives/edgar/data/1144879/000114487923000101/apld-20230228.htm)
- [Applied Digital Corp. — 10-K, 0001144879-23-000176](https://www.sec.gov/Archives/edgar/data/1144879/000114487923000176/apld-20230531.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-24-000010](https://www.sec.gov/Archives/edgar/data/1144879/000114487924000010/apld-20231130.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-24-000078](https://www.sec.gov/Archives/edgar/data/1144879/000114487924000078/apld-20240229.htm)
- [Applied Digital Corp. — 10-K, 0001144879-24-000216](https://www.sec.gov/Archives/edgar/data/1144879/000114487924000216/apld-20240531.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-24-000253](https://www.sec.gov/Archives/edgar/data/1144879/000114487924000253/apld-20240831.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-25-000006](https://www.sec.gov/Archives/edgar/data/1144879/000114487925000006/apld-20241130.htm)
- [Applied Digital Corp. — 10-K, 0001144879-25-000021](https://www.sec.gov/Archives/edgar/data/1144879/000114487925000021/apld-20250531.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-25-000069](https://www.sec.gov/Archives/edgar/data/1144879/000114487925000069/apld-20250831.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-26-000006](https://www.sec.gov/Archives/edgar/data/1144879/000114487926000006/apld-20251130.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-26-000030](https://www.sec.gov/Archives/edgar/data/1144879/000114487926000030/apld-20260228.htm)
- [Applied Digital Corp. — 10-K, 0001144879-26-000048](https://www.sec.gov/Archives/edgar/data/1144879/000114487926000048/apld-20260531.htm)
- [Applied Digital Corp. — 10-Q, 0001144879-26-000059](https://www.sec.gov/Archives/edgar/data/1144879/000114487926000059/apld-20260831.htm)
- [Applied Digital Corp. — 10-Q, 0001628280-22-014389](https://www.sec.gov/Archives/edgar/data/1144879/000162828022014389/apld-20220228.htm)
- [Applied Digital Corp. — 10-K, 0001628280-22-023816](https://www.sec.gov/Archives/edgar/data/1144879/000162828022023816/apld-20220531.htm)
- [Applied Digital Corp. — 10-Q, 0001628280-25-017684](https://www.sec.gov/Archives/edgar/data/1144879/000162828025017684/apld-20250228.htm)
- [Applied Digital Corp. — 10-Q, 0001898844-23-000006](https://www.sec.gov/Archives/edgar/data/1144879/000189884423000006/apld-20230831.htm)
- [Applied Digital Corp. — 10-K/A, 0001898844-23-000012](https://www.sec.gov/Archives/edgar/data/1144879/000189884423000012/apld-20230531.htm)
- [Zoom Communications, Inc. — 10-Q, 0001585521-26-000121](https://www.sec.gov/Archives/edgar/data/1585521/000158552126000121/zm-20260731.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-22-000029](https://www.sec.gov/Archives/edgar/data/1858681/000185868122000029/apo-20220331.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-22-000045](https://www.sec.gov/Archives/edgar/data/1858681/000185868122000045/apo-20220630.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-22-000053](https://www.sec.gov/Archives/edgar/data/1858681/000185868122000053/apo-20220930.htm)
- [Apollo Global Management, Inc. — 10-K, 0001858681-23-000007](https://www.sec.gov/Archives/edgar/data/1858681/000185868123000007/apo-20221231.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-23-000017](https://www.sec.gov/Archives/edgar/data/1858681/000185868123000017/apo-20230331.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-23-000026](https://www.sec.gov/Archives/edgar/data/1858681/000185868123000026/apo-20230630.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-23-000042](https://www.sec.gov/Archives/edgar/data/1858681/000185868123000042/apo-20230930.htm)
- [Apollo Global Management, Inc. — 10-K, 0001858681-24-000031](https://www.sec.gov/Archives/edgar/data/1858681/000185868124000031/apo-20231231.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-24-000048](https://www.sec.gov/Archives/edgar/data/1858681/000185868124000048/apo-20240331.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-24-000096](https://www.sec.gov/Archives/edgar/data/1858681/000185868124000096/apo-20240630.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-24-000120](https://www.sec.gov/Archives/edgar/data/1858681/000185868124000120/apo-20240930.htm)
- [Apollo Global Management, Inc. — 10-K, 0001858681-25-000034](https://www.sec.gov/Archives/edgar/data/1858681/000185868125000034/apo-20241231.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-25-000049](https://www.sec.gov/Archives/edgar/data/1858681/000185868125000049/apo-20250331.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-25-000117](https://www.sec.gov/Archives/edgar/data/1858681/000185868125000117/apo-20250630.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-25-000139](https://www.sec.gov/Archives/edgar/data/1858681/000185868125000139/apo-20250930.htm)
- [Apollo Global Management, Inc. — 10-K, 0001858681-26-000013](https://www.sec.gov/Archives/edgar/data/1858681/000185868126000013/apo-20251231.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-26-000026](https://www.sec.gov/Archives/edgar/data/1858681/000185868126000026/apo-20260331.htm)
- [Apollo Global Management, Inc. — 10-Q, 0001858681-26-000040](https://www.sec.gov/Archives/edgar/data/1858681/000185868126000040/apo-20260630.htm)
- [Eightco Holdings Inc. — 10-Q, 0001493152-26-036637](https://www.sec.gov/Archives/edgar/data/1892492/000149315226036637/form10-q.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-23-000023](https://www.sec.gov/Archives/edgar/data/1944366/000194436623000023/osnl-20230630.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-23-000056](https://www.sec.gov/Archives/edgar/data/1944366/000194436623000056/osnl-20230930.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-K, 0001944366-24-000031](https://www.sec.gov/Archives/edgar/data/1944366/000194436624000031/osnl-20231231.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-24-000053](https://www.sec.gov/Archives/edgar/data/1944366/000194436624000053/osnl-20240331.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-24-000076](https://www.sec.gov/Archives/edgar/data/1944366/000194436624000076/osnl-20240630.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-24-000098](https://www.sec.gov/Archives/edgar/data/1944366/000194436624000098/osnl-20240930.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-K, 0001944366-25-000041](https://www.sec.gov/Archives/edgar/data/1944366/000194436625000041/osnl-20241231.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-25-000066](https://www.sec.gov/Archives/edgar/data/1944366/000194436625000066/osnl-20250331.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-25-000100](https://www.sec.gov/Archives/edgar/data/1944366/000194436625000100/osnl-20250630.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-25-000126](https://www.sec.gov/Archives/edgar/data/1944366/000194436625000126/osnl-20250930.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-K, 0001944366-26-000020](https://www.sec.gov/Archives/edgar/data/1944366/000194436626000020/osnl-20251231.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-26-000034](https://www.sec.gov/Archives/edgar/data/1944366/000194436626000034/osnl-20260331.htm)
- [Blue Owl Real Estate Net Lease Trust — 10-Q, 0001944366-26-000066](https://www.sec.gov/Archives/edgar/data/1944366/000194436626000066/osnl-20260630.htm)
- [Cerebras Systems Inc. — 10-Q, 0001628280-26-056357](https://www.sec.gov/Archives/edgar/data/2021728/000162828026056357/cbrs-20260630.htm)
- [CRWV — EX-10.31, 0001140361-25-036118](https://www.sec.gov/Archives/edgar/data/1769628/000114036125036118/ny20053122x6_ex10-31.htm)
- [external:0002021728 — EX-10.11, 0001628280-26-025762](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/exhibit1011-sx1.htm)
- [external:0002021728 — EX-10.12, 0001628280-26-025762](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/exhibit1012-sx1.htm)
- [external:0002021728 — EX-10.13, 0001628280-26-025762](https://www.sec.gov/Archives/edgar/data/2021728/000162828026025762/exhibit1013-sx1.htm)
- [AMD–Meta — warrant du 23 février 2026](https://www.sec.gov/Archives/edgar/data/2488/000000248826000045/a41commonstockwarrantagree.htm)
- [Form D officiel — instructions de l’Item 13](https://www.sec.gov/files/formd.pdf)

Les liens de chaque position de prêteur figurent aussi dans lender_positions.csv. Les citations exactes et leurs repères sont conservés dans deepening_evidence.csv.
