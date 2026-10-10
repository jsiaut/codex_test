# Notes complémentaires — investissements, dettes, baux, engagements et clientèle

Sources arrêtées au 2026-10-09T10:24:21.129672+00:00, comme au premier passage. Les critères et seuils restent ceux engagés avant la collecte. La lecture est terminée : 3552 blocs uniques dans la file complète, aucune lecture restante.

| Famille ouverte | Blocs uniques | Blocs lus |
| --- | ---: | ---: |
| Investissements | 602 | 602 |
| Dettes | 315 | 315 |
| Baux | 183 | 183 |
| Engagements | 309 | 309 |
| Concentrations de clientèle | 839 | 839 |

Les comptes ci-dessus sont propres à chaque famille : un même texte peut apparaître dans plusieurs familles. Ils ne s’ajoutent pas au total de blocs uniques.

Les notes permettent de distinguer des montants que les seuls états principaux rapprochent mal : coût et juste valeur d’investissement, dette nominale et valeur comptable nette, passif locatif actualisé et paiements futurs bruts, capacité de crédit disponible et somme effectivement tirée. Le fichier notes_components.csv conserve chaque montant admissible avec son unité, sa période, sa condition, sa citation et son emplacement SEC. Les observations originales restent dans les tables et le journal de lecture, y compris les abstentions.

Les engagements d’achat, les baux non commencés et les garanties conditionnelles restent séparés. Une échéance publiée pour le reste d’un exercice ne constitue pas automatiquement un horizon de douze mois. Un plafond de financement ou un montant signé ne prouve pas un versement. Les composants publiés séparément dans la matrice portent partial lorsqu’une addition ou un rapprochement n’est pas établi ; ils ne forment aucun total global d’exposition.

Le texte de concentration distingue le revenu d’un client du solde de ses créances, et les ventes directes des distributeurs ou des intégrateurs. Les pourcentages anonymes gardent leur période et leur unité : aucune identité de client ni continuité entre exercices n’est déduite de leur ressemblance. Les revenus de marché spécialisé et de cloud conservent leur périmètre publié ; leur classement dans les séries de ventilation ne les transforme pas en secteur opérationnel autonome.

Les remplacements ordinaires de facilité et les résiliations volontaires documentées ne deviennent pas des événements F4. Les pertes cumulées d’investissement ne sont pas attribuées au seul dernier trimestre sans date ou période compatible. Sept décisions d’attribution sont tracées ci-dessous et dans work/extension_interpretation_results.json ; elles corrigent l’interprétation d’assemblage sans réécrire les lectures.

| Décision | Observations concernées | État |
| --- | ---: | --- |
| exclude_vie_unconsolidated_category_attribution_keep_gross_receivable_and_setoff | 1 | applied |
| exclude_F4_ordinary_revolver_replacement_keep_capacity_and_signing | 1 | applied |
| exclude_F4_voluntary_debt_facility_termination_keep_termination_unknown_execution_day | 1 | applied |
| exclude_undrawn_capacity_from_contractual_outflows_keep_available_liquidity | 2 | applied |
| preserve_conditional_right_to_consideration_remove_unconditional_word_from_interpretation | 1 | applied |
| classify_535_as_gross_derivative_liability_use_candidate_375_for_500_balance_sheet_amount | 1 | applied |
| correct_comparator_treatment_to_86_principal_84_net_preserve_693_fair_value | 1 | applied |

La conclusion sur la dépendance financière reste celle enregistrée par paire dans synthesis.md et measures.csv. Une identité juridique non confirmée, un versement non établi ou un revenu client non attribuable laisse le résultat indéterminé. La lecture complète des cinq familles ne ferme pas la recherche dans les autres documents : la découverte, les prêteurs, les documents étrangers et les autres extensions restent hors du périmètre ouvert. Aucun ratio ne démontre à lui seul une demande artificielle.

| Table | Premier passage | Après extension |
| --- | ---: | ---: |
| documents | 6706 | 6706 |
| facts | 616302 | 616302 |
| observations | 6475 | 17029 |
| entities | 408 | 480 |
| links | 715 | 768 |
| measures | 241225 | 264632 |
| controls | 147844 | 147920 |
| exclusions | 18276 | 16695 |

Les huit tables, le contrôle des cellules attendues et les invariants de livraison sont dans le dossier d’audit. Les conflits comptables locaux restent publiés ; aucune absence n’est convertie en zéro. Le travail a été effectué sans sous-agent et aucun audit indépendant n’est revendiqué. Le premier point de contrôle user_brief_2.md et son archive sont conservés séparément.
