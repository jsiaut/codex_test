"""Publish the sole executor's completed, frozen 398-note review and synthesis."""
from collections import Counter
from pathlib import Path
import hashlib,json,math
from .assembly import rows
from .reports import csv_write

def verify_scope(root):
    base=root/'work/continuation398'
    frozen=json.loads((base/'scope.json').read_text())
    reviews=[json.loads(x) for x in (base/'reviews.jsonl').read_text().splitlines()]
    assert len(frozen['rows'])==len(reviews)==398
    assert {r['index'] for r in reviews}==set(range(398))
    assert len({r['content_key'] for r in reviews})==398
    packets=[json.loads(x) for x in (root/'work/expansion/read_packets.jsonl').read_text().splitlines()]
    served={}
    for p in packets:served.setdefault(p['content_key'],set()).add((p['part'],p['text_sha256']))
    for r in reviews:
        f=frozen['rows'][r['index']]
        assert all(r[k]==f[k] for k in ('content_key','group','accession'))
        assert r['reviewer']=='sole_executor' and r['subagents_used'] is False
        block=json.loads((root/f['path']).read_text())
        for p in range(math.ceil(len(block['text'])/24000)):
            expected=hashlib.sha256(block['text'][p*24000:(p+1)*24000].encode()).hexdigest()
            assert (p,expected) in served[r['content_key']]
        obs=[json.loads(x) for x in (root/'work/observations'/(r['content_key']+'.jsonl')).read_text().splitlines()]
        assert obs[0]['accepted_count']==r['accepted_observations']>0
    scope=json.loads((root/'work/expansion/reading_scope.json').read_text())
    assert scope['nominated_unique_keys']==scope['active_unique_keys']==465
    assert scope['deferred_unique_keys']==0 and scope['all_nominated_notes_read']
    return frozen,reviews,scope

def render(db,root,as_of):
    frozen,reviews,scope=verify_scope(root)
    base=root/'work/continuation398'
    corrections={r['index']:r for r in json.loads((base/'editorial_corrections.json').read_text())}
    authored=json.loads((base/'entity_synthesis.json').read_text())
    assert len(authored)==13 and sum(x['blocks'] for x in authored)==398
    urls={r['document_id']:r['url'] for r in rows(db,'SELECT document_id,url FROM documents')}
    sources={};ledger=[]
    for r in sorted(reviews,key=lambda x:x['index']):
        f=frozen['rows'][r['index']];b=json.loads((root/f['path']).read_text())
        observations=[json.loads(x) for x in (root/'work/observations'/(r['content_key']+'.jsonl')).read_text().splitlines() if json.loads(x).get('observation_id')]
        assert observations and all(o['quote'] in b['text'] for o in observations)
        source=urls[b['document_id']];sources[r['index']]=source
        ledger.append(dict(index=r['index'],group=r['group'],accession=r['accession'],
            content_key=r['content_key'],label=b.get('label'),source_url=source,
            knowledge_date=b['knowledge_date'],original_source_path=b['source_path'],
            raw_byte_start=b['raw_byte_start'],raw_byte_end=b['raw_byte_end'],
            classification=r['classification'],reviewer=r['reviewer'],subagents_used=False,
            summary=corrections.get(r['index'],r)['summary'],editorial_correction=r['index'] in corrections,
            accepted_observations=r['accepted_observations'],
            observation_ids=json.dumps([o['observation_id'] for o in observations]),
            exact_quotes=json.dumps([o['quote'] for o in observations],ensure_ascii=False)))
    csv_write(root/'revue_398_blocs.csv',ledger)
    verification=json.loads((root/'work/delivery_verification.json').read_text())
    result=dict(source_cutoff=as_of,requested_blocks=398,completed_blocks=398,remaining_blocks=0,
        nominated_unique_notes=465,previously_reviewed_notes=67,all_nominated_notes_read=True,
        reviewed_by_entity=dict(Counter(r['group'] for r in reviews)),
        accepted_observations=sum(r['accepted_observations'] for r in reviews),
        reviewer='sole_executor',subagents_used=False,
        full_text_parts_verified=True,immutable_review_ledger=True,editorial_corrections=len(corrections),
        historical_notes_complete=False,complete_contract_review=False,
        independent_audit_performed=False,delivery_checks=verification['checks'],
        accounting_mismatch_rows=sum(r['n'] for r in verification['accounting_mismatches']),
        localized_invalid_aggregates=len(verification['localized_invalid_aggregates']))
    (root/'continuation398_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    intro='''# Analyse des 398 blocs complémentaires

**398 blocs sur 398 ont été lus et analysés par l’assistant unique, sans sous-agent. Aucun bloc de ce lot ne reste non traité.** Les 67 blocs de la première tranche et les 398 de cette continuation portent la couverture de l’inventaire des entités ajoutées à **465 notes uniques sur 465**. Le périmètre conserve 23 groupes principaux ; Athene est étudiée séparément au sein d’Apollo.

Les sources restent arrêtées au **9 octobre 2026, 10:24:21 UTC**. Les événements postérieurs aux bilans sont pris en compte lorsqu’ils ont été publiés avant cet arrêt, sans les réinjecter dans les soldes de clôture. « 0 restant » porte sur ce lot figé : cela ne signifie pas que toutes les notes historiques depuis 2021 ou tous les contrats ont été lus intégralement.

La lecture renforce quatre axes : recours parentaux et conditions de livraison ; distinction entre cash libre, avances et cash restreint ; consolidation et transferts entre véhicules ; qualité du revenu et risque de refinancement chez les prêteurs. Les stocks, flux, plafonds, garanties et valeurs comptables restent distincts. Aucun total d’exposition de la chaîne ni score global n’est calculé.

## Ce qui change le plus l’analyse

- **Les échéances doivent être actualisées.** Les bridges Core Scientific, Applied Digital et TeraWulf ont été remboursés ou refinancés. Great Elm a remboursé ses notes 2026 en mai et renouvelé son revolver en juin. MSD a prolongé son revolver en juillet. Ces dettes historiques ne restent pas toutes à traiter comme un mur de maturités courant.
- **La vente d’un véhicule ne suffit pas à démontrer la fin du recours.** TeraWulf a vendu sa participation Abernathy en juillet contre une contrepartie échelonnée ; la libération de tout soutien parental n’est pas établie. Chez Great Elm, une cession à GESF peut remplacer une exposition directe par une exposition indirecte conservée.
- **Les besoins avant livraison restent importants.** IREN publie 13,611 Md$ d’engagements à douze mois. Nebius utilise notamment des avances clients pour financer ses investissements. Les capacités de crédit et loyers futurs ne sont pas du cash disponible aujourd’hui.
- **Le revenu comptable ne mesure pas seul le cash.** PIK et amortissement de décotes chez les BDC, renonciations à frais chez Great Elm, allongements de vie des serveurs et variations de juste valeur des warrants demandent des lectures séparées. Les notes ne permettent pas d’attribuer tous ces effets à l’IA.

## Résultats par entité

'''
    sections=[]
    for item in authored:
        links=' · '.join(f"[Bloc {i+1}]({sources[i]})" for i in item['source_indices'])
        sections.append('### '+item['name']+' — '+str(item['blocks'])+' blocs\n\n'+
                        '\n\n'.join(item['paragraphs'])+'\n\nSources : '+links+'\n')
    footer=f'''## Traçabilité et validation

Le fichier [revue_398_blocs.csv](revue_398_blocs.csv) donne une ligne par bloc : accession, URL originale, emplacement en octets, citations exactes, observations acceptées et conclusion. Les notes apparaissant dans plusieurs contextes sont dédupliquées par contenu. Le registre original work/continuation398/reviews.jsonl reste immuable ; deux corrections éditoriales sont appliquées séparément, sans modifier les preuves originales.

Les {len(verification['checks'])} contrôles de livraison passent. Les rapprochements conservent {result['accounting_mismatch_rows']} lignes avec écart et {result['localized_invalid_aggregates']} agrégat local bloqué, disponibles dans audit/controls.csv et work/delivery_verification.json. Les incohérences de source relevées dans les lectures sont conservées dans le registre ; elles ne sont pas toutes transformées en rapprochements numériques. La reproduction hors ligne compare les huit tables, toutes leurs colonnes et les listes de provenance comme multiensembles ; son résultat est dans work/idempotency_verification.json. Une validation technique n’est pas une opinion d’audit indépendante sur les comptes.

Les tableaux standard restent dans tables/, les observations dans work/observations/, les critères figés dans audit/. L’archive SEC_Project_2_398_blocs.zip contient les résultats, le code, les observations et les manifestes nécessaires ; les sauvegardes LFS des sources historiques restent dans le dépôt [GitHub](https://github.com/jsiaut/codex_test). L’archive de la première tranche est conservée sous son nom distinct.
'''
    report=intro+'\n'.join(sections)+'\n'+footer
    (root/'bilan_398_blocs.md').write_text(report)
    (root/'entites_ajoutees.md').write_text(report)
    brief='''# Les 398 blocs restants sont traités

**398/398 terminés, 0 restant, sans sous-agent.** Avec la première tranche, les 465 notes uniques de l’inventaire des entités ajoutées sont maintenant couvertes. Les critères et l’arrêt des sources du 9 octobre 2026 restent inchangés.

Les principaux apports sont :

- L’actualisation des dettes refinancées ou remboursées, des échéances et des lignes de crédit.
- La distinction entre exposition directe, transfert affilié, participation à un véhicule et garantie parentale.
- La séparation des avances clients, du cash restreint, des engagements non tirés et des revenus non cash.
- La mise en évidence du PIK, des renonciations à frais et des changements de valorisation, sans attribution automatique à l’IA.

Lire [bilan_398_blocs.md](bilan_398_blocs.md) pour les 13 fiches, les sources et les implications. [revue_398_blocs.csv](revue_398_blocs.csv) contient les 398 conclusions individuelles et leurs citations. Les tableaux et contrôles sont dans SEC_Project_2_398_blocs.zip.

Cette clôture concerne le lot demandé. La lecture de toutes les notes historiques et de tous les contrats n’est pas déclarée exhaustive. Les inconnues et écarts restent signalés ; aucun audit indépendant n’est revendiqué.
'''
    (root/'user_brief_398.md').write_text(brief)
    (root/'user_brief_expansion.md').write_text(brief)
    (root/'README.md').write_text('''# SEC_Project_2

Les 398 blocs complémentaires sont tous traités, sans sous-agent. L’inventaire des entités ajoutées couvre désormais 465 notes uniques lues sur 465 ; 23 groupes principaux sont suivis. Sources arrêtées au 9 octobre 2026, 10:24:21 UTC, critères inchangés.

Lire [user_brief_398.md](user_brief_398.md), puis [bilan_398_blocs.md](bilan_398_blocs.md). Les conclusions individuelles et les citations figurent dans revue_398_blocs.csv. Les notes historiques et les contrats au-delà de ce lot ne sont pas déclarés entièrement lus. Aucun total d’exposition, score global ou audit indépendant n’est revendiqué.

Les huit tables sont dans tables/, les critères et contrôles dans audit/, les observations dans work/observations/. L’archive de cette livraison est SEC_Project_2_398_blocs.zip ; les archives antérieures sont distinctes.

## Reproduction

Installer requirements.txt. Restaurer les sauvegardes LFS de sources avec leurs manifestes SHA-256, sans écraser les observations et décisions plus récentes. python -m secfragility.phase3 --reconstruct reconstruit depuis le cache, sans requête SEC ni appel de modèle. python -m pytest -q exécute les tests. work/idempotency_verification.json compare les huit tables avec une référence créée après intégration des 398 blocs, toutes colonnes et provenance incluses.
''')
    return result
