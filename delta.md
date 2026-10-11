# Rendement, changements et limites

Exclusions locales de calcul après contrôle du lignage : {"source_not_known_at_information_cutoff": 1}. Les valeurs concernées sont retirées avec un motif explicite ; la vue révisée conserve les sources admissibles à l’arrêt de l’exécution. Les dates de disponibilité de l’information et l’arrêt des sources restent distincts.

Pas d’arrêt durable. La file de lecture est vide ; la phase d’assemblage livre les tables et le dossier d’audit. Aucun événement n’est sommé ni transformé en score. Les événements datés sont dans synthesis.md et series.csv.

## Rendement

| Statut rang 1 | Cellules |
| --- | ---: |
| bounded | 4 |
| computed | 69184 |
| not_determinable | 390720 |
| partial | 5505 |

| Motif | Cellules |
| --- | ---: |
| public_attribution_or_complete_terms_not_established | 215517 |
| empty_numerator | 57940 |
| fiscal_calendar_not_established | 36034 |
| complete_public_attribution_not_established | 34416 |
| missing_admissible_terms | 21405 |
| historical_filer_category_or_fiscal_dates_unestablished | 15774 |
| explicit_dated_event_not_established | 4927 |
| individual_source_component_not_an_additive_total | 4076 |
| named_anonymous_overlap_and_complete_attribution_not_established | 2484 |
| dated_explicit_control_or_going_concern_state_not_established | 1546 |
| complete_contract_terms_not_established | 1041 |
| missing_compatible_consecutive_quarters | 676 |
| qualified_source_amount | 232 |
| short_term_principal_not_included | 82 |
| short_term_debt_and_other_components_not_established | 74 |
| source_not_known_at_information_cutoff | 1 |

Les tableaux suivants comptent des cellules et leurs états dans la vue as_known ; ils ne somment ni les événements ni les montants. Toutes les périodes et variantes figurent dans series.csv.

| Observable | Statut | Motif | Cellules temporelles |
| --- | --- | --- | ---: |
| F1 | computed | — | 228 |
| F1 | not_determinable | fiscal_calendar_not_established | 47 |
| F1 | not_determinable | missing_compatible_consecutive_quarters | 185 |
| F1 | not_determinable | source_not_known_at_information_cutoff | 1 |
| F10 | not_determinable | dated_explicit_control_or_going_concern_state_not_established | 414 |
| F10 | not_determinable | fiscal_calendar_not_established | 47 |
| F2 | not_determinable | explicit_dated_event_not_established | 414 |
| F2 | not_determinable | fiscal_calendar_not_established | 47 |
| F3 | not_determinable | explicit_dated_event_not_established | 414 |
| F3 | not_determinable | fiscal_calendar_not_established | 47 |
| F4 | computed | — | 15 |
| F4 | not_determinable | explicit_dated_event_not_established | 399 |
| F4 | not_determinable | fiscal_calendar_not_established | 47 |
| F5 | computed | — | 55 |
| F5 | not_determinable | dated_explicit_control_or_going_concern_state_not_established | 359 |
| F5 | not_determinable | fiscal_calendar_not_established | 47 |
| F6 | computed | — | 4 |
| F6 | not_determinable | explicit_dated_event_not_established | 410 |
| F6 | not_determinable | fiscal_calendar_not_established | 47 |
| F7 | computed | — | 1 |
| F7 | not_determinable | explicit_dated_event_not_established | 413 |
| F7 | not_determinable | fiscal_calendar_not_established | 47 |
| F8 | computed | — | 259 |
| F8 | not_determinable | fiscal_calendar_not_established | 47 |
| F8 | not_determinable | missing_compatible_consecutive_quarters | 155 |
| F9 | not_determinable | explicit_dated_event_not_established | 414 |
| F9 | not_determinable | fiscal_calendar_not_established | 47 |

| Mesure de relation / couverture | Statut | Motif | Cellules temporelles |
| --- | --- | --- | ---: |
| consideration_to_customer | not_determinable | fiscal_calendar_not_established | 1128 |
| consideration_to_customer | not_determinable | public_attribution_or_complete_terms_not_established | 14278 |
| contract_coverage | not_determinable | fiscal_calendar_not_established | 1128 |
| contract_coverage | not_determinable | public_attribution_or_complete_terms_not_established | 13766 |
| contract_coverage | partial | complete_contract_terms_not_established | 512 |
| customer_concentration_anonymous | computed | — | 128 |
| customer_concentration_anonymous | not_determinable | fiscal_calendar_not_established | 47 |
| customer_concentration_anonymous | not_determinable | missing_admissible_terms | 374 |
| documented_backlog_dependency | not_determinable | fiscal_calendar_not_established | 2256 |
| documented_backlog_dependency | not_determinable | public_attribution_or_complete_terms_not_established | 28556 |
| documented_pair_coverage | computed | — | 28556 |
| documented_pair_coverage | not_determinable | fiscal_calendar_not_established | 2256 |
| documented_revenue_dependency | not_determinable | empty_numerator | 28556 |
| documented_revenue_dependency | not_determinable | fiscal_calendar_not_established | 1128 |
| investor_customer_revenue_share | not_determinable | empty_numerator | 414 |
| investor_customer_revenue_share | not_determinable | fiscal_calendar_not_established | 47 |
| named_edge_coverage | not_determinable | fiscal_calendar_not_established | 141 |
| named_edge_coverage | not_determinable | named_anonymous_overlap_and_complete_attribution_not_established | 1242 |
| noncash_revenue_from_investees | not_determinable | fiscal_calendar_not_established | 1128 |
| noncash_revenue_from_investees | not_determinable | public_attribution_or_complete_terms_not_established | 14278 |

Couverture nommée, anonyme et résiduelle par fournisseur, au dernier point fiscal :

| Fournisseur | Dernière période | Part | Ratio | Dénominateur publié | Statut / motif |
| --- | --- | --- | ---: | ---: | --- |
| AMD | 2026-06-27 | anonymous | ND | 11536000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMD | 2026-06-27 | named | ND | 11536000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMD | 2026-06-27 | residual | ND | 11536000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMZN | 2026-06-30 | anonymous | ND | 200606000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMZN | 2026-06-30 | named | ND | 200606000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMZN | 2026-06-30 | residual | ND | 200606000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AVGO | 2026-08-02 | anonymous | ND | 29591000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AVGO | 2026-08-02 | named | ND | 29591000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AVGO | 2026-08-02 | residual | ND | 29591000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| CRWV | 2026-06-30 | anonymous | ND | 2575000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| CRWV | 2026-06-30 | named | ND | 2575000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| CRWV | 2026-06-30 | residual | ND | 2575000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| GOOGL | 2026-06-30 | anonymous | ND | 119796000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| GOOGL | 2026-06-30 | named | ND | 119796000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| GOOGL | 2026-06-30 | residual | ND | 119796000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| META | 2026-06-30 | anonymous | ND | 60801000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| META | 2026-06-30 | named | ND | 60801000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| META | 2026-06-30 | residual | ND | 60801000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| MRVL | 2026-08-01 | anonymous | ND | 2739300000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| MRVL | 2026-08-01 | named | ND | 2739300000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| MRVL | 2026-08-01 | residual | ND | 2739300000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| MSFT | 2026-06-30 | anonymous | ND | 90007000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| MSFT | 2026-06-30 | named | ND | 90007000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| MSFT | 2026-06-30 | residual | ND | 90007000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| NVDA | 2026-07-26 | anonymous | ND | 96221000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| NVDA | 2026-07-26 | named | ND | 96221000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| NVDA | 2026-07-26 | residual | ND | 96221000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| ORCL | 2026-08-31 | anonymous | ND | 19345000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| ORCL | 2026-08-31 | named | ND | 19345000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| ORCL | 2026-08-31 | residual | ND | 19345000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| SPCX | 2026-06-30 | anonymous | ND | 7814000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| SPCX | 2026-06-30 | named | ND | 7814000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| SPCX | 2026-06-30 | residual | ND | 7814000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001083301 | 2026-06-30 | anonymous | ND | 44767000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001083301 | 2026-06-30 | named | ND | 44767000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001083301 | 2026-06-30 | residual | ND | 44767000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001144879 | 2026-08-31 | anonymous | ND | 341875000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001144879 | 2026-08-31 | named | ND | 341875000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001144879 | 2026-08-31 | residual | ND | 341875000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001462056 | 2026-06-30 | anonymous | ND | 42713000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001462056 | 2026-06-30 | named | ND | 42713000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001462056 | 2026-06-30 | residual | ND | 42713000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001513845 | 2025-12-31 | anonymous | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001513845 | 2025-12-31 | named | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001513845 | 2025-12-31 | residual | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001675033 | 2026-06-30 | anonymous | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001675033 | 2026-06-30 | named | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001675033 | 2026-06-30 | residual | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001819989 | 2026-06-30 | anonymous | ND | 24837000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001819989 | 2026-06-30 | named | ND | 24837000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001819989 | 2026-06-30 | residual | ND | 24837000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001839341 | 2026-06-30 | anonymous | ND | 164201000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001839341 | 2026-06-30 | named | ND | 164201000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001839341 | 2026-06-30 | residual | ND | 164201000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001849894 | 2026-06-30 | anonymous | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001849894 | 2026-06-30 | named | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001849894 | 2026-06-30 | residual | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001858681 | 2026-06-30 | anonymous | ND | 11153000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001858681 | 2026-06-30 | named | ND | 11153000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001858681 | 2026-06-30 | residual | ND | 11153000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001859392 | 2026-06-30 | anonymous | ND | 8557336000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001859392 | 2026-06-30 | named | ND | 8557336000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001859392 | 2026-06-30 | residual | ND | 8557336000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001878848 | 2026-06-30 | anonymous | ND | 137225000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001878848 | 2026-06-30 | named | ND | 137225000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001878848 | 2026-06-30 | residual | ND | 137225000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001944366 | 2026-06-30 | anonymous | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001944366 | 2026-06-30 | named | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| external:0001944366 | 2026-06-30 | residual | ND | ND | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |

Paires à financement de montant documenté : 2. Arêtes de montant : 13. Les couvertures nommée, anonyme et résiduelle restent au niveau du fournisseur dans les séries.

Blocs uniques traités : 4034 ; observations acceptées : 17637. Tentatives rejetées : {"semantic": 48, "schema": 60}. Les essais rejetés restent conservés, même après une correction de schéma autorisée. Répartition des occurrences par classe : {"item404": 166, "related_parties": 31, "going_concern": 220, "controls": 219, "8k_item": 457, "exhibit": 245, "investments_note": 867, "lease_note": 210, "concentration_narrative": 937, "debt_note": 369, "commitments_note": 346, "section": 1} ; items 8-K : {"non renseigné": 457}.

Réseau : {"max_requests_in_rolling_second": 5, "sec_limit_respected": true, "pipeline_rate_respected": true, "requests": 9251, "bytes_received": 7461730535}. Durée calendaire depuis la première requête SEC : 187905.427058 secondes, pauses et interruptions comprises ; aucune durée de travail actif n’est inventée. Les pauses après refus sont vérifiées dans le journal. Les corps arrêtés à leur en-tête sont exclus financial_parties_only et restent identifiables par accession et plage d’octets.

## Exclusions

| Motif d’exclusion | Lignes |
| --- | ---: |
| not_processed | 13761 |
| policy_excluded | 1113 |
| pending_entity | 471 |
| relation_without_admissible_amount | 384 |
| superseded_reporting_basis | 244 |
| financial_parties_only | 214 |
| direction_not_established | 175 |
| conflicting_reporting_bases | 140 |
| validation_failed | 108 |
| not_collected | 67 |
| not_public | 23 |
| conflicting_tagged_reference | 13 |
| recast_boundary | 13 |
| attribution_interpretation | 9 |
| category_assignment_not_explicit_in_this_contractual_disclosure | 3 |
| event_definition_mismatch | 2 |
| invalid_aggregate | 1 |
| net_proceeds_993_5_vs_independent_offer_price_992_35_unresolved | 1 |
| parse_failed | 1 |
| primary_cash_and_exact_event_date_not_established | 1 |
| same_issue_literal_million_vs_billion_unresolved | 1 |
| source_period_not_established | 1 |

## Modifications et contrôles

Cette extension utilise le même arrêt des sources que le premier passage ; ses changements viennent de la lecture complémentaire et de l’assemblage. Les retraitements entre dépôts se lisent dans C4. Les observations originales restent inchangées ; les corrections de portée et de dépendance numérique passent par exclusions. Les critères E et F ne changent pas.

| Contrôle | ok | mismatch | not_testable | tautological |
| --- | ---: | ---: | ---: | ---: |
| c10_maturity_sums | 618 | 0 | 34 | 0 |
| c11_segments | 358 | 0 | 152 | 0 |
| c12_revenue_disaggregation | 847 | 0 | 840 | 0 |
| c13_rpo | 240 | 0 | 0 | 0 |
| c14_eps_scale | 615 | 66 | 154 | 0 |
| c15_tax_rate | 279 | 62 | 165 | 0 |
| c16_concentration | 4095 | 0 | 8 | 0 |
| c1_balance_components | 2302 | 50 | 256 | 6 |
| c2_cash_flow_components | 2114 | 19 | 159 | 6 |
| c3_cash_reconciliation | 54 | 1 | 569 | 0 |
| c4_restatement_detection | 281926 | 0 | 81 | 0 |
| c5_bilateral | 0 | 0 | 796 | 0 |
| c6_income_articulation | 364 | 0 | 0 | 0 |
| c7_cash_continuity | 462 | 8 | 41 | 0 |
| c8_debt_rollforward | 0 | 0 | 347 | 0 |
| c9_lease_liability | 299 | 9 | 230 | 0 |

Les entités pending figurent dans entities et dans les exclusions. Les tables de correspondance restent établies depuis la définition et la présentation, sans changement destiné à faire passer un contrôle. Les erreurs locales de lignage ou d’agrégat sont écartées avec leur invariant.

## Paires non additives

Registre complet : {"na01": 66, "na02": 16, "na03": 0, "na04": 0, "na05": 0, "na06": 3, "na07": 0, "na08": 0, "na09": 144, "na10": 0, "na11": 0, "na12": 153, "na13": 0, "na14": 0, "na15": 0}. Paires sans candidat dans cette tranche : na03, na04, na05, na07, na08, na10, na11, na13, na14, na15. Une paire muette reste un défaut de couverture possible, pas une preuve d’absence. Les liens candidats non résolus ne fournissent pas d’allocation ni de total.

## Écarts et limites à examiner

Les chiffres indicatifs de l’annexe D ne sont jamais importés. Les divergences de source, notamment montant nominal, coupon, prix net, date juridique et périmètre combiné, restent dans les exclusions ou les observations. Les séries annuelles de SpaceX qui échouent aux contrôles restent exclues. Les bases de liquidité incomplètes portent partial ou ND. Le dossier n’a pas reçu d’audit indépendant.

Les cinq familles de notes et les quatre approfondissements autorisés sont traités dans une tranche bornée ; voir approfondissements.md pour les sources, résultats et limites. Douze groupes sont maintenant ajoutés aux onze groupes initiaux. Leur première lecture, ses sources et ses notes non traitées figurent dans entites_ajoutees.md et expansion_note_coverage.csv. Le dépôt, les observations et la sauvegarde du cache permettent une reprise sans nouvelle lecture des blocs terminés.
