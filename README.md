# SEC_Project_2

Premier passage v6.14 livré : lire [delta.md](delta.md), puis [synthesis.md](synthesis.md) et [series.md](series.md). Les huit tables sont dans tables/ ; les observations validées dans work/observations/ ; le dossier de vérification indépendante dans audit/. Aucun audit indépendant n’est revendiqué.

Le périmètre reste first_pass. Les critères engagés avant les requêtes et la date de situation figurent dans audit/criteria_manifest.json et delivery_summary.json. Les valeurs manquantes restent manquantes ; aucun score ou total global d’exposition.

## Reproduire

Installer requirements.txt. Restaurer le cache depuis la sauvegarde LFS et son manifeste, sans écraser les observations plus récentes ni restaurer d’ancien verrou. Depuis la racine, python -m secfragility.phase3 --reconstruct reconstruit depuis le cache et les observations conservées ; python -m secfragility.phase3 utilise les exports document/fait existants. Aucun appel de modèle par API et aucune nouvelle requête SEC pour la reproduction hors ligne.

Le travail est régulièrement commité et poussé. L’exécution finale porte un commit distinct ; les points de sauvegarde intermédiaires ne valent pas livraison. Les sources API sauvegardées ne sont pas supposées reproductibles depuis EDGAR à une date ultérieure.
