"""Current Dell findings, preserved prior stages and numerical evidence index."""
from pathlib import Path
from decimal import Decimal
import csv,json,shutil
from .assembly import rows
from .database import sql_literal,table_counts
from .dell_sources import state,persist

def csv_write(path,data):
    if not data:path.write_text('');return
    columns=list(dict.fromkeys(k for r in data for k in r))
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=columns);w.writeheader();w.writerows(data)

def render(db,root,asof,validation):
    base=state(root);data=rows(db,"SELECT * FROM measures WHERE group_id='DELL' ORDER BY period_end,period_start,measure,view,term,breakdown_key,counterparty_id,variant")
    evidence=rows(db,"SELECT o.*,d.url FROM observations o JOIN documents d USING(document_id) WHERE o.group_id='DELL' ORDER BY knowledge_date,observation_id")
    controls=rows(db,"SELECT * FROM controls WHERE group_id='DELL' ORDER BY control,period_end,breakdown_key")
    csv_write(root/'dell_measures.csv',data);csv_write(root/'dell_evidence.csv',evidence);csv_write(root/'dell_controls.csv',controls)
    csv_write(root/'dell_links.csv',rows(db,"SELECT * FROM links WHERE 'DELL' IN (from_group_id,to_group_id) ORDER BY link_id"))
    csv_write(root/'dell_reading_coverage.csv',json.loads((base/'reading_ledger.json').read_text()))
    csv_write(root/'dell_events.csv',[m for m in data if m['measure']=='fragility_event'])
    csv_write(root/'dell_annex_e.csv',[m for m in data if m['measure']=='annex_e_outcome'])
    csv_write(root/'dell_sources.csv',rows(db,"SELECT * FROM documents WHERE group_id='DELL' ORDER BY acceptance_datetime,url"))
    csv_write(root/'dell_credit_facility_register.csv',json.loads((base/'credit_facility_register.json').read_text()))
    explanations=json.loads((base/'control_explanations.json').read_text())
    csv_write(root/'dell_control_explanations.csv',explanations)
    index=[]
    for m in data:
        for sid in json.loads(m['lineage']):
            f=rows(db,'SELECT document_id,accession,locator,tier,filing_status,is_tagged FROM facts WHERE fact_id=?',[sid])
            o=rows(db,'SELECT document_id,accession,locator,tier,filing_status,false AS is_tagged FROM observations WHERE observation_id=?',[sid]) if not f else []
            d=rows(db,'SELECT document_id,accession,cache_path AS locator,tier,filing_status,false AS is_tagged FROM documents WHERE document_id=?',[sid]) if not f and not o else []
            if not (f or o or d):continue
            for field in ['value','value_lower','value_upper','numerator','denominator']:
                if m[field] is not None:index.append(dict((f or o or d)[0],measure=m['measure'],period_start=m['period_start'],period_end=m['period_end'],
                    view=m['view'],variant=m['variant'],term=m['term'],breakdown_key=m['breakdown_key'],field=field,published_value=m[field],
                    source_id=sid,unit=m['unit'],currency=m['currency']))
    csv_write(root/'audit/dell_numbers.csv',index)
    # Stable complete-PK order, so tied periods in different variants do not
    # create CSV-only differences between two identical offline assemblies.
    from .softbank_integration import rank1
    for name,condition in [('measures.csv',''),('series.csv',' WHERE measure::VARCHAR IN ('+','.join(sql_literal(x) for x in sorted(rank1()))+')')]:
        path=root/name
        with path.open(newline='') as f:columns=next(csv.reader(f))
        fields=','.join('"'+c+'"' for c in columns)
        keys=[r[1] for r in db.execute("PRAGMA table_info('measures')").fetchall() if r[5]]
        db.execute('COPY (SELECT '+fields+' FROM measures'+condition+' ORDER BY '+','.join(keys)+') TO '+sql_literal(str(path))+" (FORMAT CSV, HEADER TRUE, NULL '')")
    inventory=json.loads((root/'work/softbank/unified_inventory.json').read_text())
    inv=json.loads((base/'assembly/work/inventory.json').read_text());inventory['groups']['DELL']=inv['groups']['DELL']
    persist(base/'unified_inventory.json',inventory)
    snapshot=dict(source_cutoff=asof,main_groups=len(inventory['groups']),SEC_identity='0001571996',
        issuer='Dell Technologies Inc.',latest_report_period='2026-07-31',latest_fiscal_label='Q2_FY2027',
        fiscal_year_end='Friday_nearest_January31',periodic_reports_collected=len(json.loads((base/'issuer.json').read_text())['periodic']),
        current_selected_notes_personally_read=32,historical_notes_exhaustively_read=False,
        observations=len(evidence),subagents_used=False,checks=validation['checks'],table_counts=table_counts(db),
        new_Dell_accounting_mismatches=len(validation['Dell_accounting_mismatches']),
        private_customer_allocation_complete=False,independent_audit_performed=False)
    persist(root/'dell_summary.json',snapshot)
    summary=json.loads((root/'delivery_summary.json').read_text());summary.update(dell_integration=snapshot,current_main_groups=len(inventory['groups']),current_table_counts=table_counts(db))
    # Prior cohort summaries remain reviewable; current aggregate counts cover
    # the same 25-group table exports the reader actually opens.
    summary.setdefault('before_Dell_aggregate_counts',{k:summary.get(k) for k in ['tables','rank1_by_status','rank1_by_reason','controls_by_status','controls_by_id','exclusions_by_reason']})
    summary['tables']=table_counts(db)
    summary['rank1_by_status']=rows(db,'SELECT status,count(*) AS count FROM measures WHERE tier=1 GROUP BY status ORDER BY status')
    summary['rank1_by_reason']=rows(db,'SELECT nd_reason,count(*) AS count FROM measures WHERE tier=1 AND nd_reason IS NOT NULL GROUP BY nd_reason ORDER BY count(*) DESC')
    summary['controls_by_status']=rows(db,'SELECT status,count(*) AS count FROM controls GROUP BY status ORDER BY status')
    summary['controls_by_id']=rows(db,'SELECT control,status,count(*) AS count FROM controls GROUP BY control,status ORDER BY control,status')
    summary['exclusions_by_reason']=rows(db,'SELECT reason,count(*) AS count FROM exclusions GROUP BY reason ORDER BY count(*) DESC')
    persist(root/'delivery_summary.json',summary)
    cstatus=rows(db,"SELECT status,count(*) AS count FROM controls GROUP BY status ORDER BY status")
    summary['controls_by_status_current']=cstatus;persist(root/'delivery_summary.json',summary)
    bonds=[dict(issuer='Dell International L.L.C. and EMC Corporation',guarantors='Dell Technologies Inc.;Denali Intermediate Inc.;Dell Inc.',
        event_date='2026-09-15',stage='recognized',nominal_principal=amount,currency='USD',coupon=coupon,maturity_date=maturity,
        status='completed_issuance;net_proceeds_not_established;not_July_balance',source_accession='0001193125-26-391976')
        for maturity,amount,coupon in [('2029-09-15',1250000000,'0.051'),('2031-09-15',1250000000,'0.054'),('2033-09-15',1500000000,'0.056'),('2037-04-01',1000000000,'0.059')]]
    csv_write(root/'dell_bond_register.csv',bonds)
    latest=next(f for f in json.loads((base/'filings.json').read_text()).values() if f['metadata']['accessionNumber']=='0001571996-26-000046')
    annual=next(f for f in json.loads((base/'filings.json').read_text()).values() if f['metadata']['accessionNumber']=='0001571996-26-000008')
    qurl=latest['resources'][latest['metadata']['primaryDocument']]['url'];aurl=annual['resources'][annual['metadata']['primaryDocument']]['url']
    report=f'''# Dell intégré au modèle

**25 groupes principaux**, huit tables communes, sources arrêtées au **9 octobre 2026, 10:24:21 UTC**, critères E/F inchangés. Dell Technologies Inc. (CIK 0001571996) est consolidé en US GAAP, en dollars. Le dernier bilan connu à cette date est celui du **31 juillet 2026, T2 de l’exercice fiscal 2027**. Les exercices Dell se terminent le vendredi proche du 31 janvier ; FY2026 se clôture le 30 janvier 2026.

Le travail est réalisé par l’exécutant seul. Les 24 groupes précédents et toutes leurs lignes sont conservés. Dell Financial Services, Dell Bank, les emprunteurs obligataires et les véhicules de titrisation sont rattachés au groupe sur des preuves juridiques datées. Les sociétés personnelles de Michael Dell restent distinctes de Dell Technologies.

## Ce que Dell apporte

Les [comptes trimestriels déposés]({qurl}) documentent un mécanisme précis : DFS finance des achats de produits, les locations-ventes peuvent produire un résultat dès leur commencement, les encaissements clients suivent ensuite, et une partie des créances est financée par des titrisations. Le narratif déposé relie explicitement la croissance de l’IA à des volumes de crédit plus élevés chez un nombre restreint de clients. **La ventilation du portefeuille DFS entre clients IA n’est pas publiée.**

| Montant en milliards de dollars, sauf indication | Valeur | Base |
| --- | ---: | --- |
| Revenu des serveurs IA | 16,401 | T2 FY2027, catégorie désormais distincte d’ISG |
| Revenu consolidé | 46,971 | Même trimestre ; part IA calculée ≈ 34,9 % |
| Créances DFS nettes | 20,430 | 31 juillet ; 14,280 au 30 janvier |
| Équipements loués par DFS, nets | 3,182 | Actifs du bailleur ; distincts des créances et des baux de Dell preneur |
| Nouvelles opérations de financement DFS | 10,3 | Semestre ; 4,0 sur le semestre comparable, montant brut |
| Revenu produit de locations-ventes | 3,711 | Trimestre ; 0,181 sur le trimestre comparable, non attribué à l’IA |
| Provision de pertes de crédit passée en résultat | 0,122 | Trimestre ; stock d’allowance : 0,314 |
| Créances classées « Lower » | 4,424 | 21,5 % des créances brutes de 20,542 ; classement interne, pas une probabilité de défaut |
| Créances en retard de plus de 90 jours | 0,106 | 0,52 % des créances brutes ; certaines créances douteuses peuvent être classées courantes |
| Dette DFS définie dans la note | 9,618 | Principal ; majoritairement sans recours, périmètre précisé |
| Dette corporate allouée à DFS par la direction | 11,042 | Allocation de gestion, déjà incluse dans la dette corporate |
| Dette « DFS related » publiée par la direction | 20,660 | 9,618 + 11,042 ; **ne se rajoute pas** à la dette consolidée |
| Dette consolidée | 34,747 / 34,466 | Principal / valeur comptable ; baux preneur séparés |
| Cash et équivalents | 11,569 | Cash restreint de 0,168 séparé |
| Disponibilité réelle du revolver | 5,884 | Plafond signé de 6,0, aucun prêt tiré ; lettres de crédit réduisent la disponibilité |
| RPO | 132 | Tous produits et services ; pas un carnet IA exclusivement, environ 77 % à reconnaître sous 12 mois |
| Engagements d’achat | 34,8 | 24,6 sous 12 mois, selon le narratif ; certaines commandes à prix futur indéterminé sont exclues |
| Garanties aux fournisseurs pour les fabricants sous contrat | 8,6 | Maximum contingent, droit de recours contre les fabricants ; pas un paiement effectué |

Ces lignes décrivent des bases différentes et comportent des chevauchements. Elles ne forment pas un total d’exposition. Le SCF de 3,1 Md$ est déjà inclus dans les dettes fournisseurs ; la titrisation consolidée n’est pas assimilée à une cession de créances sortie du bilan.

## La trésorerie et le risque de double comptage

Au trimestre, le CFO est de **2,225 Md$** et les investissements décaissés publiés, comprenant le développement logiciel capitalisé, de **1,239 Md$** : **FCF de base = 0,986 Md$**. Dell publie aussi un **FCF ajusté de 8,149 Md$**, qui rajoute **6,667 Md$** liés aux créances de financement et **0,496 Md$** liés aux équipements en location. Les valeurs et la réconciliation sont conservées séparément.

Le financement initial des locations-ventes passe déjà dans le CFO ; celui des locations opérationnelles passe dans les investissements. Retirer une nouvelle fois les 10,3 Md$ d’originations DFS du CFO moins investissements compterait deux fois une partie du financement. Le FCF après financement net de contreparties nommées reste indéterminé, faute de ventilation complète. Le FCF ajusté représente une définition de gestion qui neutralise ces actifs, avec une substitution annoncée par la dette ; il n’est pas remplacé par le FCF de base.

## Qui porte le risque

Les véhicules DFS sont consolidés et juridiquement distincts, avec surcollatéralisation. Les programmes exposent Dell à un arrêt du financement de nouvelles créances si certains critères de pertes, retards, scores et collecte ne sont plus respectés. Dell déclare ces critères respectés au 31 juillet. Les seuils précis de ces programmes ne sont pas établis par les pièces lues.

L’accord de crédit du 10 juin 2026 donne, lui, le seuil de couverture des intérêts : **3,00x**, sur quatre trimestres, avec un EBITDA et des charges d’intérêts définis par le contrat. Les intérêts de financements DFS sont notamment exclus de son dénominateur. Aucun ratio GAAP simplifié n’est présenté comme une marge disponible sous ce covenant. Les **24 banques** de l’annexe 2.01 et leurs engagements, qui totalisent **6 Md$**, sont publiées dans dell_credit_facility_register.csv. Ce registre prouve leurs engagements, pas des prêts effectivement tirés ; il ne crée aucune arête de financement en montant.

Les émissions du **15 septembre 2026** représentent **5 Md$ de principal nominal** sur quatre échéances. Elles sont enregistrées comme une opération achevée après le bilan de juillet, sans fabriquer une dette ou une trésorerie d’octobre. Les garanties des sociétés Dell sont internes au groupe et ne doublent pas la dette consolidée.

## Clients, investissements et liens avec le reste du modèle

Les [comptes annuels]({aurl}) déclarent un client représentant **12 %** du revenu FY2026, surtout dans ISG, **sans nommer ce client**. Aucun rapprochement avec xAI, CoreWeave, OpenAI ou un autre client n’est retenu sur cette seule base. Les gains de valorisation comprennent une hausse de prix observable de **0,6 Md$** liée à une participation également anonyme ; elle n’est attribuée à aucun laboratoire IA.

Une relation commerciale avec VMware, contrôlé par Broadcom depuis le 22 novembre 2023, est ajoutée comme relation de canal de vente. Le financement par DFS de certains clients finaux de VMware ne démontre pas un prêt à VMware ou à Broadcom. Les ventes agrégées à des sociétés affiliées aux organisations personnelles de Michael Dell ou aux portefeuilles Silver Lake ne sont pas ventilées entre sociétés. Elles ne sont pas attribuées à MSD Investment Corp. par proximité de nom.

**Annexe E : résultats indéterminés** pour les dépendances financières non attribuables, avec les trois seuils inchangés et les dates limites annuelles. L’absence de montant nommé reste une donnée manquante. L’annexe F conserve ses définitions : le nouveau revolver n’est pas, à lui seul, une dérogation de covenant ; le CAM de PwC sur le revenu n’est pas une opinion défavorable. L’opinion ICFR annuelle est explicitement favorable.

## Couverture, vérification et limites

Les séries structurées sont reconstruites depuis les instances SEC et l’API companyfacts non bornée, puis filtrées sur leurs vraies dates de publication. **35 rapports périodiques sont archivés**, avec les trimestres antérieurs servant aux comparaisons et à l’historique. La lecture personnelle complète des familles de notes ouvertes porte sur le dernier 10-K et les deux 10-Q suivants : **32 notes**, plus l’Item 404 du dernier proxy et les sections ciblées des contrats actuels. Les archives de notes historiques ne sont pas déclarées intégralement lues ; l’historique de financement demeure donc `search_incomplete`, jamais `never`.

Les contrôles hérités appliqués à Dell signalent **{len(validation['Dell_accounting_mismatches'])} rapprochements**, conservés dans dell_controls.csv avec leurs sources. Ils mélangent des composantes issues de dépôts différents : des passifs locatifs comparatifs après la séparation VMware avec un ancien échéancier, ou des montants d’impôt révisés avec un ancien taux. Le contrôle supplémentaire **Dell_same_deposit** teste les équations complètes dans chaque dépôt : **93 équations cohérentes** ; les explications et les empreintes des composantes sont dans dell_control_explanations.csv. La cause exacte de la révision des montants d’impôt n’est pas présumée. Les anciens écarts du modèle sont également conservés. Les tests et le rejeu portent sur le code et la reproduction des données ; aucun audit indépendant n’est revendiqué.

Fichiers : dell_measures.csv, dell_evidence.csv, dell_reading_coverage.csv, dell_sources.csv, dell_controls.csv, dell_events.csv, dell_annex_e.csv, dell_bond_register.csv. Le nouvel export commun des huit tables contient Dell et les 24 groupes précédents. L’archive Dell est un complément à l’archive SoftBank déjà livrée ; sa dépendance et les empreintes des deux archives sont explicites.
'''
    (root/'dell_integration.md').write_text(report)
    readme=root/'README.md';text=readme.read_text();start=text.index('Modèle courant :');end=text.index('\n\n',start)
    text=text[:start]+'Modèle courant : **25 groupes principaux**, avec Dell et SoftBank intégrés dans les huit tables. Lire [dell_integration.md](dell_integration.md), [dell_summary.json](dell_summary.json) et [dell_measures.csv](dell_measures.csv), puis les étapes précédentes ci-dessous. Les sources restent arrêtées au 9 octobre 2026 ; les critères E/F et les lignes des 24 groupes précédents sont conservés.'+text[end:]
    readme.write_text(text)
