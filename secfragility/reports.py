"""Generated deliverables; all financial numbers come from exported records."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime,timezone
from collections import Counter,defaultdict
import csv,json,hashlib,subprocess,shutil,zipfile
import yaml
from .assembly import rows
from .database import TABLES,export,table_counts
from .provenance import freeze_manifest,network_review
from .xbrl import digest


def csv_write(path,data,fields=None):
    fields=fields or sorted({k for row in data for k in row})
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in data:w.writerow({k:json.dumps(v,ensure_ascii=False,default=str) if isinstance(v,(dict,list)) else v for k,v in r.items() if k in fields})


def fnum(value):
    return 'ND' if value is None else format(value,'f') if isinstance(value,Decimal) else str(value)


def number_id(value):
    return digest(json.loads(json.dumps(value,default=str)))


def render(db,root,as_of,source,verification):
    export(db,root/'tables')
    freeze_manifest(root);network=network_review(root)
    cfg=yaml.safe_load((root/'config.yaml').read_text());audit=root/'audit';audit.mkdir(exist_ok=True)
    measures=rows(db,'SELECT * FROM measures ORDER BY group_id,period_end,measure,view,term,breakdown_key,counterparty_id')
    controls=rows(db,'SELECT * FROM controls ORDER BY control,group_id,period_end,breakdown_key')
    exclusions=rows(db,'SELECT * FROM exclusions ORDER BY reason,group_id,element_id')
    obs=rows(db,'SELECT * FROM observations ORDER BY observation_id')
    mapping=json.loads((root/'work/concept_mappings.json').read_text())
    inv=json.loads((root/'work/inventory.json').read_text())
    progress=json.loads((root/'work/reading_progress.json').read_text())
    ranks=set(cfg['tier1']);from .universe import DEPENDENCIES
    ranks|=DEPENDENCIES
    series=[r for r in measures if r['measure'] in ranks]
    csv_write(root/'series.csv',series)
    csv_write(root/'measures.csv',measures)
    csv_write(audit/'exclusions.csv',exclusions)
    csv_write(audit/'concepts.csv',mapping)
    admitted={r[0] for r in db.execute("SELECT observation_id FROM links WHERE edge_kind='amount'").fetchall()}
    blocked={r[0]:r[1] for r in db.execute('SELECT observation_id,reason FROM excluded_observations').fetchall()}
    attrs=[dict(observation_id=o['observation_id'],accession=o['accession'],document_id=o['document_id'],counterparty=o['counterparty'],
                evidence=o['counterparty_evidence'],amount=o['amount'],unit=o['unit'],currency=o['currency'],stage=o['stage'],
                model_quantity=o['model_quantity'],quote=o['quote'],locator=o['locator'],tagged_fact_id=o['tagged_fact_id'],
                amount_origin=o['amount_origin'],is_tagged=bool(o['tagged_fact_id']),numeric_edge_admitted=o['observation_id'] in admitted,
                exclusion_reason=blocked.get(o['observation_id'])) for o in obs if o['counterparty'] and o['amount'] is not None]
    csv_write(audit/'attributions.csv',attrs)
    # One row per published numeric field and deposited term. Reused terms are
    # kept with the measure key; this is an audit trail, not an additive ledger.
    fields=['number_id','record_kind','measure','group_id','counterparty_id','period_start','period_end','view','as_of','term','breakdown_key',
       'variant','field','published_value','unit','source_id','source_kind','accession','document_id','locator','is_tagged','tier','filing_status']
    with (audit/'numbers.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for m in measures:
            terms=[s for k in json.loads(m['lineage']) for s in source(k)]
            for field in ['value','value_lower','value_upper','numerator','denominator']:
                if m[field] is None:continue
                key={k:m[k] for k in ['measure','group_id','counterparty_id','period_start','period_end','view','as_of','term','breakdown_key','variant']}
                for t in terms:
                    if t['source_kind']=='document' and m['basis_break_reason']:
                        t=dict(t,locator=m['basis_break_reason'],accession=m['breakdown_key'].split('|')[0])
                    w.writerow(dict(key,number_id=number_id([key,field]),record_kind='measure',field=field,published_value=fnum(m[field]),unit=m['unit'],
                       **{k:t.get(k) for k in ['source_id','source_kind','accession','document_id','locator','is_tagged','tier','filing_status']}))
        # The control table itself carries every equation and original terms.
        # Index its numeric terms here for the independent audit as well.
        for c in controls:
            for field in ['lhs','rhs','residual','tolerance']:
                if c[field] is None:continue
                for k in json.loads(c['evidence']):
                    for t in source(k):
                        key={k:c[k] for k in ['group_id','period_start','period_end','view','as_of','breakdown_key','variant']}
                        w.writerow(dict(key,measure=c['control'],term='none',number_id=number_id([key,c['control'],field]),record_kind='control',field=field,
                           published_value=fnum(c[field]),unit='equation_unit',**{k:t.get(k) for k in ['source_id','source_kind','accession','document_id','locator','is_tagged','tier','filing_status']}))
    shutil.copy2(root/'tables/measures.parquet',audit/'measures.parquet');shutil.copy2(root/'tables/controls.parquet',audit/'controls.parquet')
    # Domain rules contain only normative rules, no production reasoning.
    (audit/'domain_rules.md').write_text('''# Règles du domaine appliquées

Seuls les documents SEC déposés alimentent les mesures. Une pièce furnished, une correspondance ou un projet n’est pas une preuve de montant : Reg S-T ; instructions des formulaires 8-K et S-1. Les attributs formulaire, item, emplacement, assurance et niveau de preuve restent distincts.

Les dates et dimensions définissent les faits ; fy et fp ne définissent pas une période. L’instance est déjà à l’échelle ; decimals donne une précision. Une absence n’est jamais un zéro. Les comparaisons et contrôles n’emploient que les précisions publiées. Aucun change ni mélange de cadres comptables. Les comparatifs retirés ou retraités ne sont pas soustraits à une base incompatible.

Le groupe économique et les entités juridiques ont des appartenances datées : ASC 810, ASC 805, ASC 323. Les successeurs restent des personnes distinctes. Une identité non établie reste pending. Un fonds n’est pas fusionné avec son gestionnaire. Les opérations internes au périmètre sont éliminées.

Un financement exige un versement ou une reconnaissance comptable admissible ; un plafond signé et une garantie ne sont pas un versement. Les contreparties au client, financements significatifs, revenus non monétaires et contrats combinés suivent ASC 606-10-32 et 606-10-25. Un achat du client ne devient pas le revenu de son fournisseur sans rapprochement publié.

Dette, échéances, passifs locatifs, engagements et garanties restent séparés par base : ASC 470, 842, 440, 460, 810. Les programmes de financement fournisseurs et transferts de créances suivent ASC 405-50 et 860 et restent hors du graphe. Aucun total unique d’exposition. Tout chevauchement non résolu bloque une addition.

Les parts de revenu et les secteurs suivent ASC 280 ; la complétude des grands clients au seuil normatif est annuelle. Aucun client anonyme n’est prolongé d’un exercice à l’autre sans preuve. Les états intermédiaires suivent Reg S-X article 10 et ASC 270. Les changements d’estimation et de principe suivent ASC 250 ; les investissements ASC 321 et 323. La continuité suit ASC 205-40.

Les horizons de dépôt suivent les instructions du 10-K et Exchange Act Rule 0-3, avec calendrier vérifié ; une date limite non établie reste indéterminée. Les critères E et la liste F sont ceux engagés avant les requêtes. Aucun score, corrélation, extrapolation sectorielle ni prédiction. L’extension de découverte n’est pas ouverte.
''')
    statuses=Counter(c['status'] for c in controls)
    ct=defaultdict(Counter)
    for c in controls:ct[c['control']][c['status']]+=1
    control_md='| Contrôle | ok | mismatch | not_testable | tautological |\n| --- | ---: | ---: | ---: | ---: |\n'+'\n'.join('| '+k+' | '+' | '.join(str(v[s]) for s in ['ok','mismatch','not_testable','tautological'])+' |' for k,v in sorted(ct.items()))
    rank_status=Counter(m['status'] for m in series)
    rank_reasons=Counter(m['nd_reason'] for m in series if m['nd_reason'])
    exclusion_reasons=Counter(e['reason'] for e in exclusions)
    ef=json.loads((root/'work/annex_e_pair_outcomes.json').read_text());efstats=Counter(e['outcome'] for e in ef)
    e7ratio=Decimal(efstats['indeterminate'])/Decimal(len(ef)) if ef else None
    e7motifs=Counter(e['reason'] for e in ef if e.get('reason'))
    e7motif_md='| Motif principal E7 | Issues de paire |\n| --- | ---: |\n'+'\n'.join(f'| {k} | {v} |' for k,v in sorted(e7motifs.items()))
    coverage_flags=dict(anonymous_observations=sum(o['counterparty_evidence']=='anonymous' for o in obs),
       sales_channels=dict(Counter(o['sales_channel'] for o in obs if o['sales_channel'])),
       redacted_exclusions=sum(e['coverage_state']=='redacted' for e in exclusions),
       not_processed_exclusions=sum(e['coverage_state']=='not_processed' for e in exclusions),
       parse_failed_exclusions=sum(e['coverage_state']=='parse_failed' for e in exclusions),
       non_filer='not_determinable: annual-reporting status not established for each external legal identity')
    efmd='| Issue de paire | Nombre |\n| --- | ---: |\n'+'\n'.join(f'| {k} | {v} |' for k,v in sorted(efstats.items()))
    events=[m for m in measures if m['measure']=='fragility_event' and m['view']=='as_known' and m['value']==1]
    def refs(m):
        terms=[s for k in json.loads(m['lineage']) for s in source(k)]
        return '; '.join(sorted({str(t.get('accession') or 'métadonnées SEC')+' / '+str(t.get('locator')) for t in terms}))
    event_md='| Groupe | Période | Observable | Public le | Pièce et emplacement |\n| --- | --- | --- | --- | --- |\n'+'\n'.join(f"| {m['group_id']} | {m['period_end']} | {m['breakdown_key']} | {m['knowledge_date']} | {refs(m)} |" for m in events)
    if not events:event_md+='\nAucun événement affirmatif calculable ; les cellules non calculables et leurs motifs figurent dans les séries.'
    manifest=json.loads((audit/'criteria_manifest.json').read_text())
    configcommit=subprocess.check_output(['git','log','-1','--format=%H','--','config.yaml'],cwd=root,text=True).strip()
    header=f'''# Premier passage — fragilité financière et relations documentées

Situation des sources arrêtée au {as_of}. Périmètre : `first_pass` ; aucune extension de texte ou découverte ouverte.

Les critères E, la liste F et les seuils n’ont pas changé. Commit d’origine : `{manifest['original_commit']}` ; commit courant de config.yaml : `{configcommit}`. Le manifeste et les annexes du dossier d’audit portent les empreintes et l’horodatage de la première requête.

Les pièces déposées ne permettent pas de discriminer entre les deux lectures. La part indéterminée des issues de paire E1 et E2 au point de tête vaut {fnum(e7ratio)} ; le périmètre borné et les numérateurs non attribuables en sont les premières limites. Cette proportion porte sur les paires publiées dans le registre, sans pondérer les montants. Les échéances non établies restent explicitement indéterminées. La sensibilité revised et les autres points de grille sont publiés dans les tables.

Aucun arrêt durable d’accès SEC ni échec comptable généralisé. Les échecs et conflits locaux restent exclus. L’audit indépendant n’a pas été effectué, conformément à la demande de travailler sans sous-agent ; le dossier permet de le faire ultérieurement.

## Contrôles

{control_md}

Les écarts sont conservés avec leurs deux termes, leur précision et leur explication. Un contrôle non testable ne devient pas un succès.

## Événements

{event_md}

## Fragilité par groupe

'''
    group_sections=[]
    health=['revenue_total','revenue_growth','capex_to_cfo','fcf_basic','fcf_after_counterparty_financing','receivables_collection_period',
            'rpo_total','liq_principal_due_to_cash','lev_debt_and_leases_to_operating_income_plus_da','lease_not_commenced_bridge']
    for g in sorted(inv['groups']):
        gr=[m for m in measures if m['group_id']==g and m['view']=='as_known' and m['counterparty_id']=='none' and m['period_end']!='none']
        latest=max((m['period_end'] for m in gr if m['measure']=='revenue_total' and m['status']=='computed'),default=max((m['period_end'] for m in gr),default='non établi'))
        lines=[f'### {g}',f'Dernière période de revenu exploitable : {latest}. Les séries complètes sont dans series.csv ; les périodes fiscales et dates de publicité y sont distinctes.',
             '| Mesure | Terme / variante | Valeur | Unité | Statut / motif | Source |','| --- | --- | ---: | --- | --- | --- |']
        for metric in health:
            items=[m for m in gr if m['measure']==metric and m['period_end']==latest]
            if not items:lines.append(f'| {metric} | — | ND | — | missing_admissible_terms | — |')
            for m in items:
                lines.append(f"| {metric} | {m['term']} / {m['variant']} | {fnum(m['value'])} | {m['unit'] or '—'} | {m['status']} / {m['nd_reason'] or '—'} | {refs(m) or '—'} |")
        lines.append('La matrice conserve séparément les bases, échéances et composants ; aucune somme unique. Les additions et ponts non établis restent manquants. La qualité du résultat, les changements de durée et les gains ou pertes d’investissement gardent leur pièce et leur rupture de base dans les tables. Les engagements non lus ne sont pas tenus pour nuls.')
        if g=='SPCX':lines.append('La présentation combinée de l’émetteur reste distincte du périmètre historique. Les tableaux annuels non balisés dont les contrôles n’ont pas abouti sont exclus ; aucune série annuelle de flux n’en est reconstruite. La série legacy_only hors ventilation sectorielle reste non déterminable.')
        group_sections.append('\n\n'.join(lines))
    circular=f'''## Circularité par paire

{efmd}

Les cellules de documented_revenue_dependency, documented_backlog_dependency, consideration_to_customer et noncash_revenue_from_investees gardent leur contrepartie et leur motif. Un numérateur vide reste ND. La couverture du numérateur et celle du dénominateur sont séparées ; named_edge_coverage ne répartit pas artificiellement le revenu entre parts nommée, anonyme et résiduelle quand leur chevauchement n’est pas résolu.

Les plafonds et garanties publiés rendent certaines relations visibles sans prouver un financement versé. Le statut financé est daté, avec la sensibilité ever_financed à côté. La conclusion de chaque paire figure dans relationship_conclusion. Aucun ratio ni cycle ne démontre à lui seul une demande artificielle.

{e7motif_md}

Les conditions de couverture enregistrées, non exclusives et distinctes des issues de paire, sont : {json.dumps(coverage_flags,ensure_ascii=False)}. Les comptes de zéro portent sur les exclusions classées, jamais sur l’absence universelle d’une difficulté. La concentration anonyme reste provisoire tant que son texte environnant n’est pas traité ; les non-déposants ne sont pas dénombrés par supposition.

Les critères E sont confrontés aux paires et aux exercices dans measures.parquet, même pour les cellules vides. Les chemins de l’extension restent non déterminables, motif not_processed ; ils ne sont pas comptés comme inexistants.

## Exclusions et évolution

Les motifs principaux sont publiés dans delta.md et audit/exclusions.csv. Les notes d’investissements, de dette, de baux, d’engagements et le texte de concentration hors tranche restent not_processed. Les dates limites, identités, précisions et bases non établies restent visibles. Aucun comparatif exclu ni contrat signé ne remplit un versement ou un revenu manquant.

Ce premier rendu ne compare pas à une livraison antérieure : les valeurs nouvelles sont une base initiale. Les changements internes entre dépôts sont conservés par le contrôle de retraitement, avec leur cause connue ou inconnue. Les lectures et leur validation sont conservées pour les reprises.
'''
    synthesis=header+'\n\n'.join(group_sections)+'\n\n'+circular
    (root/'synthesis.md').write_text(synthesis);(audit/'synthesis.md').write_text(synthesis)
    data=dict(as_of=as_of,tables=table_counts(db),rank1_by_status=dict(rank_status),rank1_by_reason=dict(rank_reasons),
      controls_by_status=dict(statuses),controls_by_id={k:dict(v) for k,v in ct.items()},exclusions_by_reason=dict(exclusion_reasons),
      reading=progress,network=network,annex_e_pair_outcomes=dict(efstats),annex_e7_ratio=str(e7ratio),invariants=verification['checks'],
      amount_edges=db.execute("SELECT count(*) FROM links WHERE edge_kind='amount'").fetchone()[0],
      documented_financing_pairs=db.execute("SELECT count(DISTINCT from_group_id||'|'||to_group_id) FROM links WHERE edge_kind='amount' AND family='financing'").fetchone()[0])
    data['annex_e7_primary_reasons']=dict(e7motifs)
    data['recorded_coverage_conditions']=coverage_flags
    data['elapsed_wall_seconds_since_first_sec_request']=str(Decimal(str((datetime.now(timezone.utc)-datetime.fromisoformat(manifest['first_sec_request'])).total_seconds())).quantize(Decimal('0.000001')))
    (root/'delivery_summary.json').write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str)+'\n')
    table_status='| Statut rang 1 | Cellules |\n| --- | ---: |\n'+'\n'.join(f'| {k} | {v} |' for k,v in sorted(rank_status.items()))
    reason_status='| Motif | Cellules |\n| --- | ---: |\n'+'\n'.join(f'| {k} | {v} |' for k,v in rank_reasons.most_common())
    exclusion_md='| Motif d’exclusion | Lignes |\n| --- | ---: |\n'+'\n'.join(f'| {k} | {v} |' for k,v in exclusion_reasons.most_common())
    queue=json.loads((root/'work/queue.json').read_text());classes=Counter(r['block_class'] for r in queue);items=Counter(r.get('item') or 'non renseigné' for r in queue if r['block_class']=='8k_item')
    maskednetwork={k:v for k,v in network.items() if k!='pause_violations'}
    na=json.loads((root/'work/nonadditive_counts.json').read_text());silent=[k for k,v in na.items() if not v]
    delta=f'''# Rendement et limites du premier passage

Pas d’arrêt durable. La file de lecture est vide ; la phase d’assemblage livre les tables et le dossier d’audit. Aucun événement n’est sommé ni transformé en score. Les événements datés sont dans synthesis.md et series.csv.

## Rendement

{table_status}

{reason_status}

Paires à financement de montant documenté : {data['documented_financing_pairs']}. Arêtes de montant : {data['amount_edges']}. Les couvertures nommée, anonyme et résiduelle restent au niveau du fournisseur dans les séries.

Blocs uniques traités : {progress['completed_unique_keys']} ; observations acceptées : {progress['accepted_observations']}. Tentatives rejetées : {json.dumps(progress['validation_rejected_attempts_by_phase'],ensure_ascii=False)}. Les essais rejetés restent conservés, même après une correction de schéma autorisée. Répartition des occurrences par classe : {json.dumps(dict(classes),ensure_ascii=False)} ; items 8-K : {json.dumps(dict(items),ensure_ascii=False)}.

Réseau : {json.dumps(maskednetwork,ensure_ascii=False)}. Durée calendaire depuis la première requête SEC : {data['elapsed_wall_seconds_since_first_sec_request']} secondes, pauses et interruptions comprises ; aucune durée de travail actif n’est inventée. Les pauses après refus sont vérifiées dans le journal. Les corps arrêtés à leur en-tête sont exclus financial_parties_only et restent identifiables par accession et plage d’octets.

## Exclusions

{exclusion_md}

## Modifications et contrôles

Aucune livraison antérieure validée n’existe : aucun changement inter-exécutions n’est imputé à tort à une nouvelle information. Les retraitements entre dépôts se lisent dans C4. Les observations originales restent inchangées ; les corrections de portée et de dépendance numérique passent par exclusions. Les critères E et F ne changent pas.

{control_md}

Les entités pending figurent dans entities et dans les exclusions. Les tables de correspondance restent établies depuis la définition et la présentation, sans changement destiné à faire passer un contrôle. Les erreurs locales de lignage ou d’agrégat sont écartées avec leur invariant.

## Paires non additives

Registre complet : {json.dumps(na,ensure_ascii=False)}. Paires sans candidat dans cette tranche : {', '.join(silent) or 'aucune'}. Une paire muette reste un défaut de couverture possible, pas une preuve d’absence. Les liens candidats non résolus ne fournissent pas d’allocation ni de total.

## Écarts et limites à examiner

Les chiffres indicatifs de l’annexe D ne sont jamais importés. Les divergences de source, notamment montant nominal, coupon, prix net, date juridique et périmètre combiné, restent dans les exclusions ou les observations. Les séries annuelles de SpaceX qui échouent aux contrôles restent exclues. Les bases de liquidité incomplètes portent partial ou ND. Le dossier n’a pas reçu d’audit indépendant.

Le texte hors tranche reste non traité ; l’extension ne s’ouvre que sur décision explicite après cette livraison. Le dépôt, les observations et la sauvegarde du cache permettent une reprise sans nouvelle lecture des blocs terminés.
'''
    (root/'delta.md').write_text(delta)
    (root/'series.md').write_text('''# Séries temporelles

La feuille series.csv publie toutes les mesures de rang 1, les dépendances requises et les événements, par groupe, contrepartie, période fiscale, vue, terme et variante. Le champ value vide est ND ; status et nd_reason donnent le motif. knowledge_date indique la publicité de la pièce et information_cutoff l’information disponible pour la vue. Les ruptures et périmètres restent en colonnes. Aucun montant manquant n’est remplacé par zéro.

Lire delta.md d’abord, puis synthesis.md. Les références et les termes de chaque chiffre figurent dans audit/numbers.csv. Les tables Parquet conservent les décimales exactes.
''')
    (root/'user_brief_2.md').write_text(f'''# Second point de contrôle

Le premier passage est livré. La file contient {progress['completed_unique_keys']} blocs uniques traités et aucune lecture restante. Le dépôt conserve les observations, les huit tables et le cache sauvegardé ; les rendus sont générés depuis les tables.

Les comptes balisés permettent de publier des séries de revenu, flux, investissement et certains composants d’exposition. Les conditions des contrats ne donnent souvent pas le financement effectif ou le revenu par client. La part indéterminée des issues E1 et E2 au point de tête est {fnum(e7ratio)}. Ce résultat tient d’abord à la tranche bornée et aux bases non attribuables ; il ne démontre aucune des deux lectures.

{table_status}

Les événements sont datés et documentés, sans score. Les contradictions et éléments hors tranche restent visibles. L’audit indépendant n’est pas effectué puisque le travail a été réalisé sans sous-agent.

Une extension pourrait surtout résoudre les motifs not_processed : notes courantes d’investissements, de dette, de baux et d’engagements, puis texte de concentration. Elle ne rendrait pas publics les montants caviardés ou les comptes des non-déposants. Aucune extension n’est ouverte à ce stade ; votre décision explicite est requise par §11.1.
''')
    (root/'README.md').write_text('''# SEC_Project_2

Premier passage v6.14 livré : lire [delta.md](delta.md), puis [synthesis.md](synthesis.md) et [series.md](series.md). Les huit tables sont dans tables/ ; les observations validées dans work/observations/ ; le dossier de vérification indépendante dans audit/. Aucun audit indépendant n’est revendiqué.

Le périmètre reste first_pass. Les critères engagés avant les requêtes et la date de situation figurent dans audit/criteria_manifest.json et delivery_summary.json. Les valeurs manquantes restent manquantes ; aucun score ou total global d’exposition.

## Reproduire

Installer requirements.txt. Restaurer le cache depuis la sauvegarde LFS et son manifeste, sans écraser les observations plus récentes ni restaurer d’ancien verrou. Depuis la racine, python -m secfragility.phase3 --reconstruct reconstruit depuis le cache et les observations conservées ; python -m secfragility.phase3 utilise les exports document/fait existants. Aucun appel de modèle par API et aucune nouvelle requête SEC pour la reproduction hors ligne.

Le travail est régulièrement commité et poussé. L’exécution finale porte un commit distinct ; les points de sauvegarde intermédiaires ne valent pas livraison. Les sources API sauvegardées ne sont pas supposées reproductibles depuis EDGAR à une date ultérieure.
''')
    return data


def package(root,as_of):
    output=Path('/codex/browser/projectless/0001-files-pasted-by-the-user-uploaded-pasted-text-po/output');output.mkdir(parents=True,exist_ok=True)
    for name in ['synthesis.md','delta.md','user_brief_2.md','delivery_summary.json']:
        shutil.copy2(root/name,output/name)
    target=output/'SEC_Project_2_premier_passage.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(root.rglob('*')):
            rel=path.relative_to(root);parts=rel.parts
            if not path.is_file():continue
            include=parts[0] in ['audit','tables','secfragility','tests'] and '__pycache__' not in parts
            include=include or len(parts)==1 and path.suffix in ['.md','.yaml','.sql','.csv','.json','.txt']
            include=include or parts[:2]==('work','observations')
            include=include or str(rel) in ['work/expected_universe.json','work/annual_cutoffs.json','work/reading_progress.json','work/delivery_verification.json','work/pair_registry.json','work/annex_e_pair_outcomes.json','work/nonadditive_counts.json','backup/sec-project-2-20261009T150746Z.tar.zst.json','backup/sec-project-2-20261009T150746Z.tar.zst.sha256','work/observation_quarantines.json','work/fact_semantic_quarantines.json','work/exhibit_body_policy_overrides.json','work/parent_membership_evidence.json','work/entity_decisions.json','work/queue.json','work/run.json','work/inventory.json','work/collection.json','work/spcx_annual_validation.json','work/deprecations.json','work/concept_mappings.json']
            if include:z.write(path,rel)
    manifest=dict(as_of=as_of,archive=target.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size,
       repository='https://github.com/jsiaut/codex_test',independent_audit_performed=False)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest
