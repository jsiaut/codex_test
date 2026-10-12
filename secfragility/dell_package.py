"""Dell evidence supplement with the full current eight-table model snapshot."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,zipfile
from .database import TABLES
from .dell_sources import persist,state

OUTPUT=Path('output')

def file_sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def restore_checkpoint(root,previous_archive):
    base=state(root);dependency=json.loads((base/'delivery_dependency.json').read_text())
    if file_sha(previous_archive)!=dependency['previous_archive_sha256']:raise ValueError('Previous delivered archive hash mismatch')
    manifest=json.loads((base/'baseline/manifest.json').read_text())
    with zipfile.ZipFile(previous_archive) as archive:
        for table in TABLES:
            destination=root/manifest[table]['path']
            if destination.exists():
                if file_sha(destination)!=manifest[table]['sha256']:raise ValueError('Existing baseline changed')
                continue
            destination.parent.mkdir(parents=True,exist_ok=True)
            with archive.open('tables/'+table+'.parquet') as f:raw=f.read()
            if hashlib.sha256(raw).hexdigest()!=manifest[table]['sha256']:raise ValueError('Delivered baseline differs')
            destination.write_bytes(raw)
    return dict(restored_checkpoint='24_groups_as_delivered_with_SoftBank',previous_archive_verified=True)

def run(root,output=None):
    output=Path(output) if output is not None else Path(root)/'output'
    base=state(root);validation=json.loads((base/'validation.json').read_text())
    replay=json.loads((root/'work/idempotency_verification.json').read_text())
    assert all(validation['checks'].values()) and replay['all_tables_identical'] and replay['input_manifest_unchanged']
    assert all(r['same_bytes'] for r in json.loads((base/'prior_archive_baseline_match.json').read_text()).values())
    prior=json.loads((root/'work/softbank/delivery_archive.json').read_text())
    dependency=dict(previous_archive='SEC_Project_2_SoftBank.zip',previous_archive_sha256=prior['sha256'],
        previous_archive_bytes=prior['bytes'],previous_archive_contains='All older SEC and Japanese evidence plus the verified 24-group snapshot',
        same_baseline_bytes_verified_in_all_eight_tables=True,current_supplement_contains_full_25_group_table_snapshot=True,
        historical_archives_unchanged=True)
    persist(base/'delivery_dependency.json',dependency)
    instructions='''# Restaurer le modèle Dell à 25 groupes

Cette archive contient les **huit tables courantes complètes à 25 groupes**, les séries et mesures communes, les sources Dell originales, les observations, le code, les tests et les preuves de validation. Elle complète SEC_Project_2_SoftBank.zip, qui contient les preuves des 24 groupes antérieurs. Les empreintes et la dépendance sont dans work/dell/delivery_dependency.json.

Pour consulter les données courantes, ouvrir tables/ et les CSV. Pour rejouer sans réseau, extraire d’abord l’archive SoftBank dans un dossier vide, puis cette archive Dell dans le même dossier. Installer requirements.txt. Restaurer le point de contrôle précédent depuis le ZIP conservé :

```
python -m secfragility.dell_package restore --previous /chemin/SEC_Project_2_SoftBank.zip
python -m secfragility.dell_sources restore
python -m secfragility.dell_sources nominate
python -m secfragility.dell_integration native
python -m secfragility.dell_integration assemble
python -m pytest -q
```

Les observations personnelles sont des entrées conservées, pas une extraction à refaire par un modèle. author_notes.py et la nomination permettent de revalider leurs citations contre les originaux. Le rejeu Dell reparse les états SEC puis applique l’extension au point de contrôle vérifié des 24 groupes, sans requête SEC ni appel de modèle. Le rejeu SEC complet de l’étape précédente dispose de sa preuve propre dans l’archive SoftBank.

Les archives antérieures restent intactes. Le 9 octobre 2026 reste l’arrêt des sources. Les notes détaillées des derniers comptes sont entièrement lues dans le périmètre annoncé ; les notes historiques supplémentaires et la ventilation privée du portefeuille DFS ne sont pas déclarées exhaustives.
'''
    (root/'DELL_REPRODUCTION.md').write_text(instructions)
    files=set()
    for directory in ['secfragility','tests','tables']:
        files.update(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    files.update(p for p in base.glob('*') if p.is_file() and p.suffix in ('.json','.py','.zst')
        and p.name!='delivery_archive.json')
    files.update(p for p in (base/'delta_tables').glob('*.parquet'))
    files.update(p for p in (base/'baseline').glob('*.json'))
    files.update(p for p in root.glob('dell_*') if p.is_file())
    files.update(root/name for name in ['README.md','DELL_REPRODUCTION.md','requirements.txt','config.yaml','schema.sql','queries.sql',
        'delivery_summary.json','measures.csv','series.csv','audit/dell_numbers.csv','audit/criteria_manifest.json',
        'work/run.json','work/deprecations.json','work/fact_semantic_quarantines.json','work/idempotency_verification.json',
        'work/reproduction_inputs.json','cache/datasets/us-gaap/2026/us-gaap-2026.zip','work/reference/opm_holidays.html'])
    # Quantitative mappings for current reconstruction are packaged; the
    # bulky historical evidence remains in its already delivered archive.
    target=output/'SEC_Project_2_Dell.zip';temporary=output/'SEC_Project_2_Dell.partial.zip'
    output.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for p in sorted(files):archive.write(p,str(p.relative_to(root)))
    with zipfile.ZipFile(temporary) as archive:
        assert archive.testzip() is None
        entries=len(archive.infolist())
    manifest=dict(archive=target.name,bytes=temporary.stat().st_size,sha256=file_sha(temporary),entries=entries,
        repository='https://github.com/jsiaut/codex_test',commit_before_packaging=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        source_cutoff=validation['as_of'],current_main_groups=25,full_current_eight_tables=True,dependency=dependency,
        every_previous_row_preserved=True,all_eight_tables_identical_on_replay=True,subagents_used=False,independent_audit_performed=False)
    temporary.replace(target);persist(base/'delivery_archive.json',manifest);persist(output/'dell_manifest.json',manifest)
    for p in sorted(root.glob('dell_*')):
        if p.is_file():shutil.copy2(p,output/p.name)
    shutil.copy2(root/'DELL_REPRODUCTION.md',output/'DELL_REPRODUCTION.md')
    shutil.copy2(base/'validation.json',output/'dell_validation.json')
    shutil.copy2(root/'work/idempotency_verification.json',output/'dell_idempotency.json')
    shutil.copy2(root/'audit/dell_numbers.csv',output/'dell_numbers.csv')
    return manifest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','restore']);p.add_argument('--previous',type=Path);p.add_argument('--output',type=Path);args=p.parse_args()
    if args.action=='restore':
        if not args.previous:p.error('--previous archive is required')
        result=restore_checkpoint(Path('.').resolve(),args.previous)
    else:result=run(Path('.').resolve(),args.output)
    print(json.dumps(result))
