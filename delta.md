# Rendement et limites du premier passage

Pas d’arrêt durable. La file de lecture est vide ; la phase d’assemblage livre les tables et le dossier d’audit. Aucun événement n’est sommé ni transformé en score. Les événements datés sont dans synthesis.md et series.csv.

## Rendement

| Statut rang 1 | Cellules |
| --- | ---: |
| computed | 35900 |
| not_determinable | 181401 |
| partial | 5373 |

| Motif | Cellules |
| --- | ---: |
| public_attribution_or_complete_terms_not_established | 95023 |
| empty_numerator | 28488 |
| complete_public_attribution_not_established | 24816 |
| historical_filer_category_or_fiscal_dates_unestablished | 11550 |
| missing_admissible_terms | 10389 |
| fiscal_calendar_not_established | 5868 |
| individual_source_component_not_an_additive_total | 3962 |
| explicit_dated_event_not_established | 2651 |
| named_anonymous_overlap_and_complete_attribution_not_established | 1290 |
| complete_contract_terms_not_established | 1037 |
| dated_explicit_control_or_going_concern_state_not_established | 787 |
| source_not_known_at_information_cutoff | 345 |
| qualified_source_amount | 232 |
| missing_compatible_consecutive_quarters | 194 |
| short_term_principal_not_included | 71 |
| short_term_debt_and_other_components_not_established | 71 |

Les tableaux suivants comptent des cellules et leurs états dans la vue as_known ; ils ne somment ni les événements ni les montants. Toutes les périodes et variantes figurent dans series.csv.

| Observable | Statut | Motif | Cellules temporelles |
| --- | --- | --- | ---: |
| F1 | computed | — | 141 |
| F1 | not_determinable | fiscal_calendar_not_established | 18 |
| F1 | not_determinable | missing_compatible_consecutive_quarters | 68 |
| F1 | not_determinable | source_not_known_at_information_cutoff | 15 |
| F10 | not_determinable | dated_explicit_control_or_going_concern_state_not_established | 224 |
| F10 | not_determinable | fiscal_calendar_not_established | 18 |
| F2 | not_determinable | explicit_dated_event_not_established | 224 |
| F2 | not_determinable | fiscal_calendar_not_established | 18 |
| F3 | not_determinable | explicit_dated_event_not_established | 224 |
| F3 | not_determinable | fiscal_calendar_not_established | 18 |
| F4 | computed | — | 15 |
| F4 | not_determinable | explicit_dated_event_not_established | 209 |
| F4 | not_determinable | fiscal_calendar_not_established | 18 |
| F5 | computed | — | 54 |
| F5 | not_determinable | dated_explicit_control_or_going_concern_state_not_established | 170 |
| F5 | not_determinable | fiscal_calendar_not_established | 18 |
| F6 | computed | — | 2 |
| F6 | not_determinable | explicit_dated_event_not_established | 222 |
| F6 | not_determinable | fiscal_calendar_not_established | 18 |
| F7 | computed | — | 1 |
| F7 | not_determinable | explicit_dated_event_not_established | 223 |
| F7 | not_determinable | fiscal_calendar_not_established | 18 |
| F8 | computed | — | 177 |
| F8 | not_determinable | fiscal_calendar_not_established | 18 |
| F8 | not_determinable | missing_compatible_consecutive_quarters | 31 |
| F8 | not_determinable | source_not_known_at_information_cutoff | 16 |
| F9 | not_determinable | explicit_dated_event_not_established | 224 |
| F9 | not_determinable | fiscal_calendar_not_established | 18 |

| Mesure de relation / couverture | Statut | Motif | Cellules temporelles |
| --- | --- | --- | ---: |
| consideration_to_customer | not_determinable | fiscal_calendar_not_established | 216 |
| consideration_to_customer | not_determinable | public_attribution_or_complete_terms_not_established | 7010 |
| contract_coverage | not_determinable | fiscal_calendar_not_established | 216 |
| contract_coverage | not_determinable | public_attribution_or_complete_terms_not_established | 6500 |
| contract_coverage | partial | complete_contract_terms_not_established | 510 |
| customer_concentration_anonymous | computed | — | 63 |
| customer_concentration_anonymous | not_determinable | fiscal_calendar_not_established | 18 |
| customer_concentration_anonymous | not_determinable | missing_admissible_terms | 203 |
| documented_backlog_dependency | not_determinable | fiscal_calendar_not_established | 432 |
| documented_backlog_dependency | not_determinable | public_attribution_or_complete_terms_not_established | 14020 |
| documented_pair_coverage | computed | — | 14020 |
| documented_pair_coverage | not_determinable | fiscal_calendar_not_established | 432 |
| documented_revenue_dependency | not_determinable | empty_numerator | 14020 |
| documented_revenue_dependency | not_determinable | fiscal_calendar_not_established | 216 |
| investor_customer_revenue_share | not_determinable | empty_numerator | 224 |
| investor_customer_revenue_share | not_determinable | fiscal_calendar_not_established | 18 |
| named_edge_coverage | not_determinable | fiscal_calendar_not_established | 54 |
| named_edge_coverage | not_determinable | named_anonymous_overlap_and_complete_attribution_not_established | 618 |
| named_edge_coverage | not_determinable | source_not_known_at_information_cutoff | 54 |
| noncash_revenue_from_investees | not_determinable | fiscal_calendar_not_established | 216 |
| noncash_revenue_from_investees | not_determinable | public_attribution_or_complete_terms_not_established | 7010 |

Couverture nommée, anonyme et résiduelle par fournisseur, au dernier point fiscal :

| Fournisseur | Dernière période | Part | Ratio | Dénominateur publié | Statut / motif |
| --- | --- | --- | ---: | ---: | --- |
| AMD | 2026-06-27 | anonymous | ND | ND | not_determinable / source_not_known_at_information_cutoff |
| AMD | 2026-06-27 | named | ND | ND | not_determinable / source_not_known_at_information_cutoff |
| AMD | 2026-06-27 | residual | ND | ND | not_determinable / source_not_known_at_information_cutoff |
| AMZN | 2026-06-30 | anonymous | ND | 200606000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMZN | 2026-06-30 | named | ND | 200606000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AMZN | 2026-06-30 | residual | ND | 200606000000.000000 | not_determinable / named_anonymous_overlap_and_complete_attribution_not_established |
| AVGO | 2026-08-02 | anonymous | ND | ND | not_determinable / source_not_known_at_information_cutoff |
| AVGO | 2026-08-02 | named | ND | ND | not_determinable / source_not_known_at_information_cutoff |
| AVGO | 2026-08-02 | residual | ND | ND | not_determinable / source_not_known_at_information_cutoff |
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

Paires à financement de montant documenté : 2. Arêtes de montant : 13. Les couvertures nommée, anonyme et résiduelle restent au niveau du fournisseur dans les séries.

Blocs uniques traités : 3552 ; observations acceptées : 17029. Tentatives rejetées : {"schema": 60, "semantic": 47}. Les essais rejetés restent conservés, même après une correction de schéma autorisée. Répartition des occurrences par classe : {"item404": 166, "related_parties": 31, "going_concern": 220, "controls": 219, "8k_item": 457, "exhibit": 237, "investments_note": 603, "lease_note": 185, "concentration_narrative": 839, "debt_note": 315, "commitments_note": 309} ; items 8-K : {"non renseigné": 457}.

Réseau : {"max_requests_in_rolling_second": 5, "sec_limit_respected": true, "pipeline_rate_respected": true, "requests": 6980, "bytes_received": 2099232340}. Durée calendaire depuis la première requête SEC : 130717.373354 secondes, pauses et interruptions comprises ; aucune durée de travail actif n’est inventée. Les pauses après refus sont vérifiées dans le journal. Les corps arrêtés à leur en-tête sont exclus financial_parties_only et restent identifiables par accession et plage d’octets.

## Exclusions

| Motif d’exclusion | Lignes |
| --- | ---: |
| not_processed | 13689 |
| policy_excluded | 1104 |
| invalid_aggregate | 541 |
| pending_entity | 441 |
| relation_without_admissible_amount | 382 |
| financial_parties_only | 214 |
| direction_not_established | 175 |
| validation_failed | 107 |
| conflicting_tagged_reference | 13 |
| not_public | 11 |
| attribution_interpretation | 8 |
| category_assignment_not_explicit_in_this_contractual_disclosure | 3 |
| event_definition_mismatch | 2 |
| net_proceeds_993_5_vs_independent_offer_price_992_35_unresolved | 1 |
| parse_failed | 1 |
| primary_cash_and_exact_event_date_not_established | 1 |
| same_issue_literal_million_vs_billion_unresolved | 1 |
| source_period_not_established | 1 |

## Modifications et contrôles

Cette extension utilise le même arrêt des sources que le premier passage ; ses changements viennent de la lecture complémentaire et de l’assemblage. Les retraitements entre dépôts se lisent dans C4. Les observations originales restent inchangées ; les corrections de portée et de dépendance numérique passent par exclusions. Les critères E et F ne changent pas.

| Contrôle | ok | mismatch | not_testable | tautological |
| --- | ---: | ---: | ---: | ---: |
| c10_maturity_sums | 419 | 0 | 24 | 0 |
| c11_segments | 312 | 0 | 83 | 0 |
| c12_revenue_disaggregation | 721 | 0 | 620 | 0 |
| c13_rpo | 218 | 0 | 0 | 0 |
| c14_eps_scale | 402 | 9 | 108 | 0 |
| c15_tax_rate | 154 | 13 | 130 | 0 |
| c16_concentration | 1801 | 0 | 6 | 0 |
| c1_balance_components | 1610 | 1 | 93 | 0 |
| c2_cash_flow_components | 1554 | 2 | 28 | 0 |
| c3_cash_reconciliation | 34 | 0 | 350 | 0 |
| c4_restatement_detection | 137268 | 0 | 13 | 0 |
| c5_bilateral | 0 | 0 | 794 | 0 |
| c6_income_articulation | 242 | 0 | 0 | 0 |
| c7_cash_continuity | 289 | 1 | 26 | 0 |
| c8_debt_rollforward | 0 | 0 | 258 | 0 |
| c9_lease_liability | 169 | 0 | 168 | 0 |

Les entités pending figurent dans entities et dans les exclusions. Les tables de correspondance restent établies depuis la définition et la présentation, sans changement destiné à faire passer un contrôle. Les erreurs locales de lignage ou d’agrégat sont écartées avec leur invariant.

## Paires non additives

Registre complet : {"na01": 62, "na02": 16, "na03": 0, "na04": 0, "na05": 0, "na06": 3, "na07": 0, "na08": 0, "na09": 123, "na10": 0, "na11": 0, "na12": 102, "na13": 0, "na14": 0, "na15": 0}. Paires sans candidat dans cette tranche : na03, na04, na05, na07, na08, na10, na11, na13, na14, na15. Une paire muette reste un défaut de couverture possible, pas une preuve d’absence. Les liens candidats non résolus ne fournissent pas d’allocation ni de total.

## Écarts et limites à examiner

Les chiffres indicatifs de l’annexe D ne sont jamais importés. Les divergences de source, notamment montant nominal, coupon, prix net, date juridique et périmètre combiné, restent dans les exclusions ou les observations. Les séries annuelles de SpaceX qui échouent aux contrôles restent exclues. Les bases de liquidité incomplètes portent partial ou ND. Le dossier n’a pas reçu d’audit indépendant.

Les cinq familles de notes autorisées sont traitées ; la découverte, les prêteurs et les autres extensions ne sont pas ouverts. Le dépôt, les observations et la sauvegarde du cache permettent une reprise sans nouvelle lecture des blocs terminés.
