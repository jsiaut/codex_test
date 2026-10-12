# Reproduire les trois priorités

La date de coupure reste `2026-10-09T10:24:21.129672+00:00`. Aucun accès réseau ni extraction par modèle n’est nécessaire.

1. Installer `requirements.txt` et extraire `SEC_Project_2_priorites.zip` dans un dossier vide. L’archive contient les huit tables actuelles, les sept tables du snapshot antérieur, le code et la sauvegarde des originaux ciblés. Les faits inchangés sont stockés une seule fois ; `prepare_baseline` les relie au snapshot antérieur après vérification SHA.
2. Exécuter `python -m secfragility.targeted_priorities`. Le programme vérifie les SHA des huit tables de référence, restaure les originaux manquants depuis `work/priorities/originals.tar.zst`, vérifie les citations et les montants inline puis applique les seules additions. Les sources déjà présentes ne sont pas remplacées.
3. Pour refaire aussi la validation de la sélection personnelle : `python -c 'from pathlib import Path; from secfragility.targeted_priorities import prepare_baseline,restore_sources; r=Path(".").resolve(); prepare_baseline(r); restore_sources(r)'`, puis `PYTHONPATH=. python work/priorities/author_notes.py`, puis l’étape 2.
4. Exécuter `python -m pytest -q tests/test_targeted_priorities.py`. Comparer les résultats à `work/priorities/validation.json` et à la preuve de restauration indépendante du dossier de travail `work/priorities/replay_verification.json`.

Le GitHub `jsiaut/codex_test` contient aussi le snapshot de référence via Git LFS. La reproduction globale historique, décrite dans les livraisons précédentes, dépend de leurs sauvegardes d’originaux. L’archive de ce lot suffit à la reproduction de l’extension ciblée et à la consultation des huit tables actuelles ; elle ne remplace pas tous les originaux historiques SoftBank/Dell/SMCI.

Les anciennes observations de Vernon ont été conservées. L’observation `vernon_investment_identity_resolved` et l’exhibit 10.26 du 10-K actuel donnent la résolution. Ne pas ajouter l’ancien montant anonyme et le montant nouvellement attribué : c’est le même investissement de 92,5 M$.
