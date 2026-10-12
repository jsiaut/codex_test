"""French SMCI evidence report and complete current common exports."""
from pathlib import Path
import csv,json
from .assembly import rows
from .database import TABLES,table_counts,sql_literal
from .smci_sources import state,persist
from .dell_reports import csv_write

def render(db,root,asof,validation):
    base=state(root)
    for suffix,query in {
        'measures':"SELECT * FROM measures WHERE group_id='SMCI' ORDER BY period_end,period_start,measure,view,breakdown_key,term,variant",
        'evidence':"SELECT o.*,d.url FROM observations o JOIN documents d USING(document_id) WHERE o.group_id='SMCI' ORDER BY knowledge_date,observation_id",
        'controls':"SELECT * FROM controls WHERE group_id='SMCI' ORDER BY control,period_end,breakdown_key",
        'sources':"SELECT * FROM documents WHERE group_id='SMCI' ORDER BY acceptance_datetime,url",
        'links':"SELECT * FROM links WHERE 'SMCI' IN (from_group_id,to_group_id) ORDER BY link_id",
        'events':"SELECT * FROM measures WHERE group_id='SMCI' AND measure='fragility_event' ORDER BY period_end,view,breakdown_key",
        'annex_e':"SELECT * FROM measures WHERE group_id='SMCI' AND measure='annex_e_outcome' ORDER BY period_end,view,breakdown_key",
    }.items():csv_write(root/('smci_'+suffix+'.csv'),rows(db,query))
    ledger=json.loads((base/'reading_ledger.json').read_text());csv_write(root/'smci_reading_coverage.csv',ledger)
    audit=rows(db,"""SELECT m.measure,m.period_start,m.period_end,m.view,m.variant,m.term,m.breakdown_key,m.value,m.numerator,m.denominator,
        json_extract_string(j.value,'$') AS source_id,COALESCE(f.document_id,o.document_id,d.document_id) AS document_id,
        COALESCE(f.accession,o.accession,d.accession) AS accession,COALESCE(f.locator,o.locator,d.cache_path) AS locator,
        m.unit,m.currency FROM measures m,json_each(m.lineage) j
        LEFT JOIN facts f ON f.fact_id=json_extract_string(j.value,'$')
        LEFT JOIN observations o ON o.observation_id=json_extract_string(j.value,'$')
        LEFT JOIN documents d ON d.document_id=json_extract_string(j.value,'$')
        WHERE m.group_id='SMCI' AND m.value IS NOT NULL ORDER BY m.period_end,m.period_start,m.measure,m.view,m.breakdown_key,source_id""")
    csv_write(root/'audit/smci_numbers.csv',audit)
    from .softbank_integration import rank1
    for name,condition in [('measures.csv',''),('series.csv',' WHERE measure::VARCHAR IN ('+','.join(sql_literal(x) for x in sorted(rank1()))+')')]:
        path=root/name
        with path.open(newline='') as f:columns=next(csv.reader(f))
        keys=[r[1] for r in db.execute("PRAGMA table_info('measures')").fetchall() if r[5]]
        db.execute('COPY (SELECT '+','.join('"'+c+'"' for c in columns)+' FROM measures'+condition+' ORDER BY '+','.join(keys)+') TO '+sql_literal(str(path))+" (FORMAT CSV, HEADER TRUE, NULL '')")
    inv=json.loads((root/'work/dell/unified_inventory.json').read_text());new=json.loads((base/'assembly/work/inventory.json').read_text());inv['groups']['SMCI']=new['groups']['SMCI'];persist(base/'unified_inventory.json',inv)
    assert len(inv['groups'])==26
    observation_count=db.execute("SELECT count(*) FROM observations WHERE group_id='SMCI'").fetchone()[0]
    snapshot=dict(source_cutoff=asof,main_groups=26,issuer='Super Micro Computer, Inc.',CIK='0001375365',latest_report_period='2026-06-30',fiscal_label='FY2026',fiscal_year_end='June30',current_complete_notes_personally_read=11,historical_notes_exhaustively_read=False,historical_notes_inventoried=len([r for r in ledger if r.get('status')=='historical_inventory_outside_current_text_tranche']),active_current_notes_unprocessed=0,observations=observation_count,table_counts=table_counts(db),checks=validation['checks'],subagents_used=False,independent_audit_performed=False)
    persist(root/'smci_summary.json',snapshot)
    summary=json.loads((root/'delivery_summary.json').read_text());summary.update(smci_integration=snapshot,current_main_groups=26,current_table_counts=table_counts(db),tables=table_counts(db))
    for name,query in {'rank1_by_status':'SELECT status,count(*) AS count FROM measures WHERE tier=1 GROUP BY status ORDER BY status','rank1_by_reason':'SELECT nd_reason,count(*) AS count FROM measures WHERE tier=1 AND nd_reason IS NOT NULL GROUP BY nd_reason ORDER BY count(*) DESC','controls_by_status':'SELECT status,count(*) AS count FROM controls GROUP BY status ORDER BY status','controls_by_id':'SELECT control,status,count(*) AS count FROM controls GROUP BY control,status ORDER BY control,status','exclusions_by_reason':'SELECT reason,count(*) AS count FROM exclusions GROUP BY reason ORDER BY count(*) DESC'}.items():summary[name]=rows(db,query)
    summary['controls_by_status_current']=summary['controls_by_status'];persist(root/'delivery_summary.json',summary)
    reg=json.loads((base/'filings.json').read_text());f=reg['0001375365-26-000022'];url=f['resources'][f['metadata']['primaryDocument']]['url']
    report=f'''# SMCI intégré au modèle

Le modèle contient **26 groupes principaux**, avec les huit tables communes. Les sources restent arrêtées au **9 octobre 2026, 10:24:21 UTC**. Super Micro Computer, Inc. (SMCI, CIK 0001375365) est intégré en US GAAP et en USD. Son dernier exercice connu est **FY2026, clos le 30 juin 2026**, déposé le 31 août 2026. Les exercices commencent le 1er juillet.

Les **25 groupes précédents sont conservés ligne par ligne**, y compris les sources, montants, contrôles et listes de provenance. Le travail a été réalisé seul, sans sous-agent ; il ne constitue pas un audit indépendant du modèle.

## Ce que SMCI apporte

Le signal principal est le financement du besoin en fonds de roulement : les ventes augmentent fortement, mais la constitution des stocks et les créances absorbent du cash. SMCI ajoute aussi un cas explicite de faiblesse matérielle du contrôle interne et de dérogation sur des ratios financiers. Ces constats ne prouvent pas une insolvabilité ou un financement circulaire avec un laboratoire IA.

| Donnée | FY2026 / 30 juin 2026 | Traitement |
|---|---:|---|
| Chiffre d’affaires | 39,063072 Md$ | Consolidé ; un seul segment, aucune ventilation auditée de tous les postes en IA |
| Résultat net | 2,230453 Md$ | Distinct du cash opérationnel |
| CFO | **−6,809886 Md$** | Créances et stocks déjà inclus dans ce flux |
| Capex décaissés | 0,161999 Md$ | Les engagements non décaissés restent séparés |
| FCF simple, CFO − capex | **−6,971885 Md$** | Calcul traçable ; pas de seconde soustraction des stocks ou créances |
| Flux de financement | **+9,478755 Md$** | Comprend dettes bancaires et levées d’actions ; explique la hausse du cash |
| Trésorerie | 7,521474 Md$ | Cash restreint de 0,110062 Md$ présenté séparément |
| Créances courantes nettes | 6,125414 Md$ | 2,203942 Md$ un an auparavant ; créances non courantes 0,004846 Md$ séparées |
| Stocks nets | **12,895949 Md$** | 4,680375 Md$ un an auparavant ; produits finis 10,275998 Md$ inclus |
| Dépréciations de stocks | ≈0,1881 Md$ | Arrondi de la note ; charge détaillée 0,188110 Md$ au tableau des flux. Hors F6 |
| Fournisseurs | 2,247003 Md$ | Crédit commercial ; pas une dette financière ajoutée |
| Dettes bancaires comptabilisées | 4,056148 Md$ | Dont 2,039774 Md$ à court terme au bilan |
| Convertibles, valeur comptable précise | 4,664139 Md$ | Nominal total 4,725 Md$ ; les montants arrondis par tranche ne remplacent pas ce total |
| Dette financière comptable, hors baux | **8,720287 Md$** | Somme des deux postes précédents, sans ajouter les lignes disponibles |
| Engagements d’achat non annulables | **34,2 Md$** | Principalement sous douze mois ; futurs achats, pas dette déjà comptabilisée |
| Baux, dette actualisée | 0,539600 Md$ | Paiements futurs non actualisés 0,716115 Md$ ; pas de double addition |

Les données viennent des [comptes annuels SEC]({url}). Les observations et les CSV donnent les citations, faits XBRL, périodes et sources de chaque montant.

## Concentrations et dépendances

Un client représente **28,1 % des ventes annuelles**. Trois clients représentent **23,0 %, 17,1 % et 12,5 %** des créances. Un fournisseur représente **63,1 % des achats**. Ces contreparties ne sont pas identifiées dans ces disclosures : aucun nom, ni rapprochement entre le client des ventes et les clients des créances, n’est déduit.

Ablecom et Compuware sont des parties liées et fournisseurs identifiés, conservés comme entités distinctes du groupe consolidé. Ablecom fabrique 95,3 % des châssis achetés et Compuware 94,4 % des alimentations ; ce sont des pourcentages de composants précis. Les engagements envers elles, 59,8 M$ et 182,2 M$, restent des achats futurs. Le plafond de crédit commercial Compuware de 200 M$ n’est pas un prêt tiré de ce montant ; la créance commerciale de clôture est 0,620 M$.

La vente de créances à MUFG/Crédit Agricole représente **831,674 M$ sur l’exercice**, avec 5,737 M$ de coût. Le programme de 1,790 Md$ est **non engagé**, à la discrétion des acheteurs. Sa non-utilisation à la clôture n’efface pas le flux annuel vendu. Le factoring reste hors du graphe de financement des contreparties.

## Investissement, client et sous-location de Vernon

Une société anonyme, non qualifiée de partie liée par SMCI, est à la fois cliente, bénéficiaire d’un investissement de **92,5 M$** et sous-locataire de l’intégralité du site de Vernon, de **21 MW**. SMCI conserve sa dette de bail de **290,2 M$**, incluse dans les baux consolidés. La sous-location ne libère pas SMCI de son obligation et ne justifie aucun netting automatique. Le revenu de sous-location de 39,705 M$ est reconnu linéairement ; les recettes minimales futures de 401,968 M$ ne sont pas du cash déjà encaissé.

L’investissement et cette double relation commerciale sont conservés avec leur citation. L’identité manque : aucune arête de financement chiffrée vers un nom supposé n’est produite. Le portefeuille non coté sous méthode alternative vaut 139,230 M$. Une dépréciation d’investissement de **12 M$** et un gain réalisé de **13,3 M$** sont distincts ; leur solde ne masque pas la perte brute. L’information annuelle ne date pas cette perte à un trimestre précis pour F6.

## Financements et clauses

Le revolver américain de **2 Md$ est entièrement tiré** au 30 juin ; JPMorgan est agent d’un syndicat, sans allocation automatique de tout le risque à cette banque. Le contrat prévoit un levier maximal de **4,00x**, puis **3,50x**, puis **3,00x**, et une couverture des intérêts minimale de **2,50x** pendant la période hors catégorie investissement. Les définitions contractuelles utilisent la dette financée nette et l’EBITDA ajusté sur quatre trimestres : aucun headroom issu d’un simple ratio GAAP n’est publié ici.

Le syndicat taïwanais mené par CTBC a **1,763533 Md$ tiré**. La société mère garantit la filiale taïwanaise, avec sûretés sur créances, dépôts et certains actifs. Les participations E.SUN et Mega mentionnées sont déjà comprises dans ce syndicat. La date de remboursement de l’utilisation initiale a été prolongée le 23 juillet 2026 jusqu’au 22 janvier 2027 ; cela ne reclassifie pas rétroactivement le bilan de juin.

Le **26 juin 2026**, E.SUN a accordé une dérogation ponctuelle à la vérification de ratios dette/fonds propres et couverture des intérêts pour le test du 31 octobre 2026 : **F4 est documenté**. SMCI déclare respecter les covenants à la clôture ; ni cette dérogation ni cette déclaration ne prouvent un défaut ou une marge de sécurité non modifiée. Le contrat intégral de cette dérogation n’est pas identifié dans les pièces déposées collectées ; la preuve est la note financière auditée.

La clause taïwanaise sur la qualification de l’audit vise les **états financiers annuels** ; l’opinion défavorable sur le contrôle interne ne la déclenche pas automatiquement. Une clause distincte vise la radiation ou une suspension Nasdaq dépassant dix jours de négociation, sous exceptions.

En février 2025, les convertibles 2029 ont été modifiés : coupon passé de 0 % à 3,5 %, conversion ajustée et waiver assorti d’une exception de dépôt avant le 22 mai 2025. Ce waiver général et de reporting n’est pas codé comme F4 sur ratios financiers. U.S. Bank est trustee, sans attribution du nominal à cette banque.

Les levées d’actions ordinaires et préférentielles apparaissent dans les flux réellement reçus : **1,406953 Md$ et 4,231640 Md$**, nets des décotes de placement. Les actions préférentielles sont classées en capitaux propres, avec dividende cumulatif de 7 % pouvant être payé en cash ou en actions et conversion obligatoire attendue en juin 2029. Le programme ATM de 1,25 Md$ n’avait pas été utilisé au 30 juin : son plafond n’est pas un financement reçu.

## Dépôts et audit : chronologie conservée

| Date / période | Fait établi | Portée |
|---|---|---|
| 24 octobre 2024 | Démission d’EY, invoquant l’impossibilité de s’appuyer sur certaines représentations | Lettre et disclosure conservés ; EY n’a pas signé l’audit FY2024 |
| 18 novembre 2024 | Nomination de BDO | Nomination distincte de la certification ultérieure |
| 2 décembre 2024 | Conclusions rassurantes annoncées du comité spécial | Enquête mandatée par le conseil ; portée distincte de l’audit des comptes |
| 25 février 2025 | Dépôt des rapports retardés et clôture de la non-conformité Nasdaq de reporting | N’efface pas les faiblesses matérielles |
| 30 juin 2024 / 2025 | Faiblesses matérielles explicitement publiées | Connaissance datée au dépôt effectif ; aucune information rétroactivement connue |
| **30 juin 2026** | **Une faiblesse ITGC non corrigée ; opinion BDO défavorable sur ICFR** | **F5 documenté** ; trois autres faiblesses déclarées corrigées |
| 31 août 2026 | Opinion BDO sans réserve sur les états financiers FY2026 | Distincte de l’opinion défavorable sur ICFR |

Les emprunts américains auprès de Bank of America et Cathay ont été remboursés et résiliés en novembre 2024 ; HSBC a été résilié en décembre après remboursement en septembre. Les dépôts ne suffisent pas à en déduire un remboursement forcé ou un défaut. Les litiges et enquêtes sont conservés comme risques à perte non estimable, sans amende inventée.

## Couverture et limites

Les **32 rapports périodiques** archivés fournissent les séries structurées, avec données d’analyse FY2021–FY2026 et comparatifs antérieurs. Les **11 notes naturelles sélectionnées des derniers comptes annuels ont toutes été personnellement lues**, ainsi que les passages ciblés de contrôles FY2024/FY2025, les changements d’auditeur, le proxy Item404 et les clauses de crédit/convertibles citées. Les métadonnées des rapports courants sont inspectées ; leur collecte ne vaut pas lecture exhaustive de chaque communiqué ou contrat.

Il ne reste **aucune note de la tranche courante à traiter**. Les notes narratives historiques supplémentaires sont inventoriées et explicitement hors de cette tranche ; elles ne sont pas annoncées comme intégralement lues. Les clients anonymes, leur ventilation IA, les contrats privés, les tirages par banque et les bilans après juin restent incomplets quand les sources ne les publient pas.

Les critères des annexes E/F sont inchangés, les ND restent distincts de zéro, aucun score ni total global d’expositions n’est créé. Le contrôle EPS historique signalé en décembre 2017, hors de la fenêtre d’analyse, est conservé pour révision ; aucun nouveau écart comptable n’apparaît dans la fenêtre FY2021–FY2026. Le rejeu de l’ajout SMCI reparse ses originaux puis les applique au point de contrôle vérifié des 25 groupes ; les preuves des étapes antérieures restent dans leurs archives respectives.
'''
    (root/'smci_integration.md').write_text(report)
    readme=root/'README.md';old=readme.read_text();lead='**État courant : 26 groupes, SMCI inclus.** Sources arrêtées au 9 octobre 2026 ; [rapport SMCI](smci_integration.md), huit tables communes et archives antérieures conservées.\n\n'
    if lead not in old:readme.write_text(lead+old)
    run=json.loads((root/'work/run.json').read_text());run.update(phase='smci_integration_completed',status='completed',current_main_groups=26);persist(root/'work/run.json',run)
