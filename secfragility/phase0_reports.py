from __future__ import annotations
from pathlib import Path
import json
import subprocess
from collections import Counter
import yaml


def generate(root: Path):
    config=yaml.safe_load((root/'config.yaml').read_text())
    inv=json.loads((root/'work/inventory.json').read_text())
    progress=json.loads((root/'work/collection.json').read_text())
    journal=[json.loads(l) for l in (root/'journal.jsonl').read_text().splitlines()]
    initial_commit=subprocess.check_output(['git','rev-list','--max-parents=0','HEAD'],cwd=root,text=True).strip()
    items=Counter()
    total_filings=0
    total_submission_bytes=0
    groups=[]
    for name,g in inv['groups'].items():
        total_filings+=sum(g.get('form_counts',{}).values())
        total_submission_bytes+=g.get('submission_bytes',0)
        items.update(g.get('item_counts',{}))
        periodic=sum(n for f,n in g.get('form_counts',{}).items() if f.startswith(('10-K','10-Q')))
        groups.append(f'| {name} | {g.get("analysis_start","non établi")} | {g.get("read_start_provisional","non établi")} | {periodic} | {g.get("form_counts",{}).get("8-K",0)} |')
    latencies=sorted(j['latency_seconds'] for j in journal if j.get('status')==200)
    network_bytes=sum(j['bytes'] for j in journal)
    cf_bytes=sum(v['bytes'] for v in progress['companyfacts'].values())
    requests=len(journal)
    plan=f'''# Plan du premier passage

État : inventaire complet ; vérifications de périmètre et collecte des documents en cours.
Les bornes de lecture provisoires sont conservatrices et seront resserrées depuis les contextes fiscaux des instances. Aucun chiffre comptable n’est publié à ce stade.

Le dépôt et le cache résident dans `{root}` et `{root / 'cache'}`. Le cache n’est pas versionné ; les observations le seront. Les critères sont ceux du commit `{initial_commit}`.

## Volumes mesurés

L’inventaire de la fenêtre provisoire contient {total_filings} dépôts, tous formulaires confondus. Les soumissions complètes représentent {total_submission_bytes} octets ; ce volume ne mesure pas les documents principaux. Les données structurées de sociétés téléchargées représentent {cf_bytes} octets.

La file de collecte contient {len(set(progress.get('expected_filings',[])))} accessions distinctes. Elle inclut les formulaires nécessaires aux parties liées, aux contrôles et aux autres sources des faits structurés, ainsi que les pièces de succession.

| Groupe | Début d’analyse | Début de lecture provisoire | Rapports périodiques | 8-K |
| --- | --- | --- | --- | --- |
{chr(10).join(groups)}

Les {requests} requêtes déjà journalisées ont reçu {network_bytes} octets. La latence médiane mesurée sur les réponses réussies vaut {latencies[len(latencies)//2] if latencies else 'non mesurable'} seconde. Ces statistiques distinguent le débit plafonné du téléchargement effectif.

## Ordre et estimation restante

Après les vérifications de phase initiale : correspondances de concepts fixées avant les contrôles ; faits et deux vues ; puis notes de parties liées et informations de gouvernance, contrôle interne et continuité ; ensuite sections ciblées des 8-K et contrats. Le calcul, la confrontation aux critères, les rendus et le dossier d’audit terminent le passage.

Le nombre précis de blocs et de requêtes restantes dépend des ressources découvertes dans chaque dépôt. L’estimation d’heures de lecture reste non déterminable tant que la file normalisée n’est pas mesurée : aucun débit de lecture artificiel n’est appliqué au modèle. Les normes et les faits de l’annexe D restent des indications à vérifier ; ils ne sont pas recopiés comme données.

Aucune extension n’est ouverte. L’audit indépendant n’est pas exécuté, conformément à l’instruction de l’utilisateur de ne pas employer de sous-agent. Un dossier sera préparé pour une vérification ultérieure.
'''
    (root/'plan.md').write_text(plan)
    (root/'user_brief_1.md').write_text(f'''# Premier point de contrôle

Les historiques des onze groupes et des trois sociétés prédécesseures configurées ont été reçus. Toutes les pages annoncées par la SEC ont été lues. L’inventaire provisoire compte {total_filings} dépôts ; la sélection en cours porte sur {len(set(progress.get('expected_filings',[])))} accessions.

Le travail porte sur les comptes publiés depuis le premier exercice clos en 2021, avec un recul supplémentaire pour rechercher les financements antérieurs. Les dates exactes des exercices restent propres à chaque groupe. Les tailles fournies par l’inventaire SEC représentent des soumissions complètes et ne permettent pas de déduire le volume de texte à lire.

La collecte des documents et la mesure de la file de lecture sont en cours. Une durée de lecture fiable n’est pas encore disponible ; le temps réseau sera mesuré séparément. Aucun résultat comptable ni absence d’événement n’est déduit de cet inventaire.

Le dépôt est conservé dans `{root}` ; le cache est dans son sous-dossier `cache`. L’empreinte du commit des critères, communiquée avant l’accès SEC, est `{initial_commit}`. Les critères n’ont pas changé depuis.

Les recherches étendues restent fermées. Je réalise le travail seul et prépare un dossier de vérification, sans revendiquer un audit indépendant.
''')


if __name__=='__main__':
    generate(Path('.').resolve())
