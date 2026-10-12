"""SMCI originals and complete 26-group snapshot, with prior archive dependency."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile
from .database import TABLES
from .smci_sources import state,persist
from .dell_package import file_sha,OUTPUT

def verify_previous(root,archive_path):
    prior=json.loads((OUTPUT/'dell_manifest.json').read_text())
    if file_sha(archive_path)!=prior['sha256']:raise ValueError('Prior Dell archive changed')
    manifest=json.loads((state(root)/'baseline/manifest.json').read_text());results={}
    with zipfile.ZipFile(archive_path) as archive:
        for table in TABLES:
            with archive.open('tables/'+table+'.parquet') as f:archive_sha=hashlib.file_digest(f,'sha256').hexdigest()
            results[table]=dict(same_bytes=archive_sha==manifest[table]['sha256'],sha256=archive_sha)
    if not all(v['same_bytes'] for v in results.values()):raise ValueError('25-group baseline differs from delivered Dell model')
    persist(state(root)/'prior_archive_baseline_match.json',results)
    dependency=dict(previous_archive='SEC_Project_2_Dell.zip',previous_archive_sha256=prior['sha256'],previous_archive_bytes=prior['bytes'],earlier_evidence_archive='SEC_Project_2_SoftBank.zip',same_baseline_bytes_verified_in_all_eight_tables=True,current_supplement_contains_full_26_group_table_snapshot=True,historical_archives_unchanged=True)
    persist(state(root)/'delivery_dependency.json',dependency)
    return dependency

def restore(root,archive_path):
    base=state(root);dependency=json.loads((base/'delivery_dependency.json').read_text())
    if file_sha(archive_path)!=dependency['previous_archive_sha256']:raise ValueError('Prior archive hash differs')
    manifest=json.loads((base/'baseline/manifest.json').read_text())
    with zipfile.ZipFile(archive_path) as archive:
        for table in TABLES:
            p=root/manifest[table]['path']
            if p.exists():
                if file_sha(p)!=manifest[table]['sha256']:raise ValueError('Existing baseline differs')
                continue
            p.parent.mkdir(parents=True,exist_ok=True)
            with archive.open('tables/'+table+'.parquet') as f:raw=f.read()
            if hashlib.sha256(raw).hexdigest()!=manifest[table]['sha256']:raise ValueError('Archived baseline differs')
            p.write_bytes(raw)
    return dict(restored_verified_25_group_baseline=True)

def build(root):
    base=state(root);validation=json.loads((base/'validation.json').read_text());replay=json.loads((base/'raw_source_replay_verification.json').read_text())
    assert all(validation['checks'].values()) and replay['all_tables_identical'] and replay['input_manifest_unchanged']
    dependency=json.loads((base/'delivery_dependency.json').read_text())
    instructions='''# Restaurer le modèle SMCI à 26 groupes

Cette archive contient les huit tables complètes courantes, les séries et mesures communes, les originaux SEC SMCI dans un tar.zst, les observations personnelles, les modules, les tests et les preuves de validation/rejeu. L’arrêt reste le 9 octobre 2026. Les archives Dell et SoftBank précédentes sont conservées ; elles contiennent les preuves des 25 groupes antérieurs.

Pour consulter le modèle courant, ouvrir tables/ ou les CSV. Pour rejouer l’ajout SMCI dans un dossier vide, extraire cette archive puis installer requirements.txt. Le point de contrôle antérieur est restauré depuis l’archive Dell vérifiée :

```
python -m secfragility.smci_package restore --previous /chemin/SEC_Project_2_Dell.zip
python -m secfragility.smci_sources restore
python -m secfragility.smci_sources nominate
python -m secfragility.smci_integration native
PYTHONPATH=. python work/smci/author_notes.py
python -m secfragility.smci_integration assemble
```

Les observations sont des entrées rédigées personnellement et conservées. Leur script revalide les citations contre les sources, sans appel de modèle. Le rejeu natif reparse les originaux SMCI puis applique leur delta au point de contrôle immuable de 25 groupes, sans réseau. Il ne prétend pas avoir reparsé à nouveau tous les originaux des anciennes étapes.

Pour une reconstruction complète de toutes les étapes, extraire d’abord SoftBank, puis Dell, puis SMCI dans le même dossier et suivre les instructions de chaque archive. Les sources historiques de work/deepening_data/ supprimées du seul espace de travail après vérification sont présentes dans l’archive SoftBank. Les sources Dell peuvent être rematérialisées avec python -m secfragility.dell_sources restore. Pour exécuter l’ensemble de la suite de tests, les données des archives précédentes sont nécessaires.

Les notes historiques supplémentaires SMCI restent inventoriées hors de la tranche courante. Les onze notes sélectionnées FY2026 sont toutes lues ; les contrats et le proxy ne sont pas annoncés comme intégralement lus. Aucun audit indépendant par un autre exécutant n’a été réalisé.
'''
    (root/'SMCI_REPRODUCTION.md').write_text(instructions)
    files=set()
    for directory in ['secfragility','tests','tables']:
        files.update(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    files.update(p for p in base.glob('*') if p.is_file() and p.suffix in ('.json','.py','.zst') and p.name!='delivery_archive.json')
    files.update((base/'delta_tables').glob('*.parquet'));files.update((base/'baseline').glob('*.json'))
    files.update(p for p in root.glob('smci_*') if p.is_file())
    files.update(root/name for name in ['README.md','SMCI_REPRODUCTION.md','DELL_REPRODUCTION.md','requirements.txt','config.yaml','schema.sql','queries.sql','delivery_summary.json','measures.csv','series.csv','audit/smci_numbers.csv','audit/criteria_manifest.json','work/run.json','work/deprecations.json','work/fact_semantic_quarantines.json','work/idempotency_verification.json','work/reproduction_inputs.json','work/dell/unified_inventory.json','cache/datasets/us-gaap/2026/us-gaap-2026.zip','work/reference/opm_holidays.html'])
    target=OUTPUT/'SEC_Project_2_SMCI.zip';tmp=OUTPUT/'SEC_Project_2_SMCI.partial.zip';OUTPUT.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in sorted(files):archive.write(p,str(p.relative_to(root)))
    with zipfile.ZipFile(tmp) as archive:
        assert archive.testzip() is None;entries=len(archive.infolist())
    manifest=dict(archive=target.name,bytes=tmp.stat().st_size,sha256=file_sha(tmp),entries=entries,repository='https://github.com/jsiaut/codex_test',commit_before_packaging=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),source_cutoff=validation['as_of'],current_main_groups=26,full_current_eight_tables=True,dependency=dependency,every_previous_row_preserved=True,all_eight_tables_identical_on_SMCI_raw_replay=True,subagents_used=False,independent_audit_performed=False)
    tmp.replace(target);persist(base/'delivery_archive.json',manifest);persist(OUTPUT/'smci_manifest.json',manifest)
    for p in root.glob('smci_*'):
        if p.is_file():shutil.copy2(p,OUTPUT/p.name)
    for source,name in [(base/'validation.json','smci_validation.json'),(base/'raw_source_replay_verification.json','smci_raw_source_replay.json'),(root/'audit/smci_numbers.csv','smci_numbers.csv'),(root/'SMCI_REPRODUCTION.md','SMCI_REPRODUCTION.md')]:shutil.copy2(source,OUTPUT/name)
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['verify_previous','restore','build']);p.add_argument('--previous',type=Path);args=p.parse_args();root=Path('.').resolve()
    if args.action=='build':result=build(root)
    elif not args.previous:p.error('--previous archive is required')
    else:result=globals()[args.action](root,args.previous)
    print(json.dumps(result))
