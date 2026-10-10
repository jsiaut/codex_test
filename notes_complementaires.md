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

Les remplacements ordinaires de facilité et les résiliations volontaires documentées ne deviennent pas des événements F4. Les pertes cumulées d’investissement ne sont pas attribuées au seul dernier trimestre sans date ou période compatible. 8 décisions d’attribution sont tracées ci-dessous et dans work/extension_interpretation_results.json ; elles corrigent l’interprétation d’assemblage sans réécrire les lectures.

| Décision | Observations concernées | État |
| --- | ---: | --- |
| Créance de financement conservée ; attribution à une VIE retirée. | 1 | applied |
| Remplacement ordinaire de facilité conservé ; événement F4 retiré. | 1 | applied |
| Résiliation volontaire conservée ; événement F4 retiré. | 1 | applied |
| Capacité non tirée retirée des sorties contractuelles. | 2 | applied |
| Actif de contrat conservé comme droit conditionnel. | 1 | applied |
| Montant brut de dérivé distingué du montant présenté après compensation. | 1 | applied |
| Juste valeur de dette conservée ; comparateurs de nominal et de valeur nette corrigés. | 1 | applied |
| Plafond de warrant conservé comme droit signé ; reconnaissance comptable retirée. | 1 | applied |

La conclusion sur la dépendance financière reste celle enregistrée par paire dans synthesis.md et measures.csv. Une identité juridique non confirmée, un versement non établi ou un revenu client non attribuable laisse le résultat indéterminé. La lecture complète des cinq familles ne ferme pas la recherche dans les autres documents : la découverte, les prêteurs, les documents étrangers et les autres extensions restent hors du périmètre ouvert. Aucun ratio ne démontre à lui seul une demande artificielle.

| Table | Premier passage | Après extension |
| --- | ---: | ---: |
| documents | 6706 | 6706 |
| facts | 616302 | 616302 |
| observations | 6475 | 17029 |
| entities | 408 | 480 |
| links | 715 | 768 |
| measures | 241225 | 264630 |
| controls | 147844 | 147920 |
| exclusions | 18276 | 16696 |

Les huit tables, le contrôle des cellules attendues et les invariants de livraison sont dans le dossier d’audit. Les conflits comptables locaux restent publiés ; aucune absence n’est convertie en zéro. Le travail a été effectué sans sous-agent et aucun audit indépendant n’est revendiqué. Le premier point de contrôle user_brief_2.md et son archive sont conservés séparément.
