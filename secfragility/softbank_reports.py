"""Human-readable integrated delivery and source-specific audit exports."""
from pathlib import Path
from decimal import Decimal
import csv,json,hashlib,shutil
from .assembly import rows
from .database import TABLES,table_counts,sql_literal
from .softbank_sources import GROUP,VARIANT
from .reports import csv_write

def render(db,root,as_of,validation):
    base=root/'work/softbank';output=Path('/codex/browser/projectless/0001-files-pasted-by-the-user-uploaded-pasted-text-po/output');output.mkdir(parents=True,exist_ok=True)
    data=rows(db,"SELECT * FROM measures WHERE group_id=? ORDER BY measure,period_end,view,variant,breakdown_key",[GROUP])
    evidence=rows(db,"SELECT o.*,d.url,d.sha256 source_sha256 FROM observations o JOIN documents d USING(document_id) WHERE o.group_id=? ORDER BY knowledge_date,event_date,observation_id",[GROUP])
    csv_write(root/'softbank_measures.csv',data);csv_write(root/'softbank_evidence.csv',evidence)
    csv_write(root/'softbank_controls.csv',rows(db,"SELECT * FROM controls WHERE group_id=? ORDER BY control,period_end,breakdown_key",[GROUP]))
    csv_write(root/'softbank_links.csv',rows(db,"SELECT * FROM links WHERE from_group_id=? ORDER BY event_date,link_id",[GROUP]))
    csv_write(root/'softbank_reading_coverage.csv',json.loads((base/'reading_ledger.json').read_text()))
    csv_write(root/'softbank_annex_e.csv',[r for r in data if r['measure']=='annex_e_outcome'])
    csv_write(root/'softbank_events.csv',[r for r in data if r['measure']=='fragility_event'])
    # Keep the central numerical exports current, with their established column
    # ordering. The original evidence index is retained as the SEC index.
    from .softbank_integration import rank1
    for name,condition in [('measures.csv',''),('series.csv',
        ' WHERE measure::VARCHAR IN ('+','.join(sql_literal(x) for x in sorted(rank1()))+')')]:
        path=root/name
        with path.open(newline='') as handle:columns=next(csv.reader(handle))
        fields=','.join('"'+c+'"' for c in columns)
        db.execute('COPY (SELECT '+fields+' FROM measures'+condition+
            ' ORDER BY group_id,period_end,measure,view,term,breakdown_key,counterparty_id,variant) TO '+sql_literal(str(path))+" (FORMAT CSV, HEADER TRUE, NULL '')")
    index=[]
    for m in data:
        if m['variant']!=VARIANT:continue
        for field in ['value','value_lower','value_upper','numerator','denominator']:
            if m[field] is None:continue
            for source_id in json.loads(m['lineage']):
                fact=rows(db,'SELECT document_id,accession,locator,is_tagged,tier,filing_status FROM facts WHERE fact_id=?',[source_id])
                observation=rows(db,'SELECT document_id,accession,locator,tier,filing_status FROM observations WHERE observation_id=?',[source_id]) if not fact else []
                t=(fact or observation)[0]
                index.append(dict(t,measure=m['measure'],period_start=m['period_start'],period_end=m['period_end'],
                    view=m['view'],variant=m['variant'],term=m['term'],breakdown_key=m['breakdown_key'],field=field,
                    published_value=m[field],unit=m['unit'],currency=m['currency'],source_id=source_id,
                    source_kind='fact' if fact else 'observation',is_tagged=False))
    csv_write(root/'audit/softbank_numbers.csv',index)
    sources=json.loads((base/'sources.json').read_text());qualified={s['document_id']:s for s in json.loads((base/'admitted_sources.json').read_text())}
    from .softbank_sources import document_id
    csv_write(root/'softbank_sources.csv',[dict(s,**{k:q.get(k) for k in ['publication_date','publication_date_verified','jurisdiction','source_profile','regulatory_identifier','tier','assurance','eligible_extended']})
        for s in sources for q in [qualified.get(document_id(s),{})]])
    bond_url='https://group.softbank/en/news/press/20260924'
    register=[dict(instrument=f'SBG_2026_09_{currency}_{maturity}',borrower='SoftBank Group Corp.',
        nominal_amount=str(amount),currency=currency,coupon=str(coupon),maturity_date=maturity,
        expected_issue_date='2026-09-29',stage_at_announcement='signed',announcement_date='2026-09-24',
        collateral='none',guarantee='none',recourse='issuer_SBG',source_url=bond_url,
        later_confirmation='2026-10-01 issuer reports use of issuance proceeds; no June balance backdating',
        balance_at_source_cutoff='not independently reconciled')
        for currency,amount,coupon,maturity in [('USD',1000000000,'0.08625','2030-04-01'),
            ('USD',4500000000,'0.0925','2032-04-01'),('USD',4500000000,'0.0975','2034-04-01'),
            ('EUR',500000000,'0.07125','2030-10-01'),('EUR',500000000,'0.08','2032-10-01')]]
    csv_write(root/'softbank_bond_register.csv',register)
    # Source-backed equivalence for the two legacy IDs bearing the identical
    # legal name OpenAI Group PBC. No legal predecessor or unnamed affiliate is
    # collapsed into this equivalence.
    aliases=json.loads((base/'entity_alias_resolutions.json').read_text())
    values=[(old,r['canonical_entity_id']) for r in aliases for old in r['legacy_entity_ids']]
    lookup=' UNION ALL '.join('SELECT '+sql_literal(old)+' legacy_entity_id,'+sql_literal(new)+' canonical_entity_id' for old,new in values)
    prefix='\n-- SoftBank official-source extension: preserved SEC views and explicit alias equivalence\n'
    sql=prefix
    for table in TABLES:
        sql+='CREATE OR REPLACE VIEW legacy_EDGAR_'+table+" AS SELECT * FROM read_parquet('work/softbank/baseline/"+table+".parquet');\n"
    sql+='CREATE OR REPLACE VIEW softbank_exact_legal_aliases AS '+lookup+';\n'
    sql+="CREATE OR REPLACE VIEW softbank_qualified_measures AS SELECT * FROM read_parquet('tables/measures.parquet') WHERE group_id='"+GROUP+"' AND variant='"+VARIANT+"';\n"
    sql+="""CREATE OR REPLACE VIEW integrated_resolved_links AS
      SELECT l.*,COALESCE(a.canonical_entity_id,l.from_entity_id) canonical_from_entity_id,
        COALESCE(b.canonical_entity_id,l.to_entity_id) canonical_to_entity_id
      FROM read_parquet('tables/links.parquet') l
      LEFT JOIN softbank_exact_legal_aliases a ON a.legacy_entity_id=l.from_entity_id
      LEFT JOIN softbank_exact_legal_aliases b ON b.legacy_entity_id=l.to_entity_id;
"""
    (base/'resolved_graph_queries.sql').write_text(sql)
    queries=root/'queries.sql';existing=queries.read_text();existing=existing.split(prefix)[0]
    queries.write_text(existing+sql)
    def value(name,pe,ps='none',breakdown='none'):
        hits=[m for m in data if m['measure']==name and m['view']=='revised' and m['variant']==VARIANT and m['period_start']==ps and m['period_end']==pe and m['breakdown_key']==breakdown]
        return hits[0]['value'] if hits else None
    def yen(v):return 'ND' if v is None else format(v/Decimal(1000000000),'.3f').replace('.',',')
    annual='2026-03-31';latest='2026-06-30'
    cash=value('cash_consolidated',latest);debt=value('debt_interest_bearing',latest);lease=value('ifrs_lease_liabilities',latest)
    cfo=value('cfo',latest,'2026-04-01');capex=value('capex_cash',latest,'2026-04-01');fcf=value('fcf_basic',latest,'2026-04-01')
    acfo=value('cfo',annual,'2025-04-01');ani=next(f['value'] for f in rows(db,"SELECT * FROM facts WHERE group_id=? AND canonical_concept='net_income' AND period_start='2025-04-01' AND period_end='2026-03-31' ORDER BY knowledge_date DESC",[GROUP]))
    ttmcfo=value('cfo',latest,'2025-07-01','TTM');ttmcap=value('capex_cash',latest,'2025-07-01','TTM')
    qurl=next(q['url'] for q in qualified.values() if 'q1fy2026_01_en.pdf' in q['url']);aurl=next(q['url'] for q in qualified.values() if q['source_profile']=='issuer_audited_IFRS_financial_statements');jp=next(q['url'] for q in qualified.values() if q.get('regulatory_identifier')=='S100YGH5')
    counts=table_counts(db);ledger=json.loads((base/'reading_ledger.json').read_text());unique_pages=len({(r['document_url'],r['page']) for r in ledger})
    snapshot=dict(source_cutoff=as_of,integration_status='integrated_with_explicit_public_disclosure_gaps',
        main_groups=24,baseline_main_groups=23,source_profiles=['legacy_EDGAR_only',VARIANT],
        sources_collected=len(sources),sources_qualified=len(qualified),direct_EDINET_annual_originals=sum(s['jurisdiction']=='JP_EDINET' for s in qualified.values()),
        statement_facts=validation['new_statement_facts'],authored_observations=validation['new_authored_observations'],
        personally_read_unique_pages=unique_pages,table_counts=counts,checks=validation['checks'],
        legacy_records_preserved=True,all_historical_notes_exhaustively_read=False,
        exhaustive_EDINET_amendment_inventory=False,complete_contracts_available=False,
        subagents_used=False,independent_audit_performed=False)
    (root/'softbank_summary.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
    report=f'''# SoftBank intégré au modèle

SoftBank Group Corp. rejoint les 23 groupes déjà étudiés. **24 groupes principaux**, huit tables communes, données IFRS en yens, liens juridiques et chronologie des financements. L'arrêt des sources reste le **9 octobre 2026 à 10:24:21 UTC**. La collecte ultérieure des documents conserve sa vraie date ; elle ne déplace pas cet arrêt.

L'extension de sources japonaises a été autorisée par « Ok fais l'intégration complète au mieux ». Les critères des annexes E/F restent inchangés. La méthode admet les originaux EDINET, les états TSE avec leur assurance propre, les états annuels audités de l'émetteur et les communiqués datés pour la chronologie des opérations. Un communiqué reste une déclaration non auditée ; il ne devient ni un bilan audité ni un contrat complet. La vue SEC d'origine et chacun de ses enregistrements sont conservés.

## Les résultats qui apportent le plus de signal

| Mesure, en milliards de yens | Valeur | Périmètre et date |
| --- | ---: | --- |
| Cash consolidé | {yen(cash)} | Groupe IFRS, 30 juin 2026 |
| Cash SBG après éliminations | 754,752 | Holding, 30 juin ; narratif non audité |
| Dette portant intérêt | {yen(debt)} | Groupe, courant + non courant ; leases et intérêts des tiers SVF séparés |
| Passifs locatifs | {yen(lease)} | Groupe IFRS16, 30 juin |
| CFO trimestriel | {yen(cfo)} | Avril–juin 2026 |
| Achats PP&E/intangibles décaissés | {yen(capex)} | Incluent certains prépaiements et frais payés d'avance |
| FCF de base | {yen(fcf)} | CFO moins le poste d'achats précédent ; acquisitions d'entreprises et placements séparés |
| CFO sur douze mois | {yen(ttmcfo)} | Juillet 2025–juin 2026 ; annuel + T1 − comparatif T1 |
| Même poste d'achats sur douze mois | {yen(ttmcap)} | Même période et base |

Les comptes annuels présentent **{yen(Decimal(ani))} Md¥ de bénéfice consolidé**, contre **{yen(acfo)} Md¥ de CFO**. Les gains de valorisation, les mouvements du forward OpenAI et les éliminations des fonds expliquent pourquoi le résultat ne représente pas le cash finançant les investissements. **87,3 % des investissements SVF FVTPL sont classés en niveau 3 à fin mars**, avec des paramètres de valorisation non observables. Les catégories sont conservées séparément, sans total global d'exposition.

Le cash consolidé ne représente pas la liquidité libre de la holding. Il inclut notamment les filiales bancaires, les fonds, la télécom et Arm. La dette de la holding, les prêts des véhicules sans recours à SBG, les prêts à recours limité et la garantie Tsubaki sont identifiés séparément. Le LTV de gestion publié par SBG n'est pas remplacé par dette consolidée / portefeuille consolidé.

## OpenAI et la transformation du financement

La note trimestrielle confirme **10 Md$ investis le 1er avril** et **10 Md$ le 1er juillet**, cette seconde tranche étant postérieure au bilan de juin. Le [communiqué du 1er octobre](https://group.softbank/en/news/press/20261001) confirme la dernière tranche de **10 Md$**, la réalisation des **30 Md$** engagés en février, un cumul publié de **64,6 Md$** et environ **13 %** de participation. Ce cumul est une base d'investissement publiée, pas une juste valeur actualisée du portefeuille. Les titres et les droits antérieurs ne sont pas additionnés une seconde fois aux décaissements.

À fin juin, le narratif publiait une juste valeur OpenAI de **89,6 Md$**, pour **44,6 Md$** d'investissement cumulé. Cette valeur demeure un solde daté de juin ; elle n'est pas augmentée mécaniquement des tranches de juillet et octobre pour fabriquer une juste valeur d'octobre.

La même publication confirme le remboursement de tous les tirages de la facilité relais de mars, dont le plafond était **40 Md$**, et l'annulation du dernier **10 Md$** non tiré le 30 septembre. L'annonce du 9 septembre était une décision de remboursement ; la confirmation du 1er octobre permet de clore cette facilité. Cela ne signifie pas que toute la dette SBG ou Tsubaki a disparu.

La dernière tranche a été financée avec le produit des obligations annoncées le [24 septembre](https://group.softbank/en/news/press/20260924). Leur nominal est **10 Md$ et 1 Md€**, conservés dans leurs devises. Les coupons USD sont **8,625 %, 9,25 % et 9,75 %**, avec échéances 2030, 2032 et 2034. L'équivalent de 11,1 Md$ n'est pas un nominal USD à ajouter au nominal EUR. Le remboursement du relais correspond donc notamment à une transformation du financement, sans preuve d'une disparition de l'exposition économique.

## Collatéral, garanties et véhicules

Le prêt adossé aux actions Arm est porté par **Kronos I (UK) Limited** : nominal **20 Md$**, maturité prolongée à septembre 2027, **769 029 000 actions Arm** nanties, clauses de cash collateral et de remboursement anticipé. La note le décrit explicitement **sans recours à SBG**. Le nominal, la valeur comptable JPY et la traduction USD de convenance restent trois bases distinctes. Aucun appel de marge effectif n'est déduit des seules clauses.

Le contrat Tsubaki de **10 Md$**, signé le 5 août, nomme **SVF II TSUBAKI (DE) LLC** comme emprunteur et SBG comme garant, avec maturité août 2028. Il décrit un compte de cash collatéral et des clauses liées à la valeur des titres OpenAI. Dans cette source, le tirage d'août est attendu : son exécution et son solde actuel ne sont pas établis. Les seuils exacts et le plafond de garantie ne sont pas reconstitués. **Apollo Global Funding LLC est un arrangeur nommé ; aucune part du prêt ne lui est attribuée.**

Chez Energy Global, les warrants accordés en incentive de baux de data centers sont comptabilisés comme dérivés passifs : **582,962 Md¥ en mars**, **1 050,843 Md¥ en juin**. La note ne nomme pas leur bénéficiaire. Ils apportent du signal sur la structure des accords et la sensibilité de leur valeur ; ils ne donnent ni le revenu du client ni un financement OpenAI attribuable.

## Engagements et concentrations

Les engagements d'achats de biens et services atteignent **3 244,569 Md¥ en mars**, avec une composante JV incluse. L'engagement OpenAI de 30 Md$ était publié séparément et a ensuite été exécuté ; l'acquisition ABB de **5,375 Md$**, soumise à conditions, reste une autre base. Les plafonds de cartes de crédit des filiales ne sont pas attribués à l'IA.

Le programme Stargate annoncé à **500 Md$**, les capacités annoncées en GW et la responsabilité financière de SBG ne prouvent pas un engagement cash SBG de ce montant. L'annonce de **3 Md$ annuels de services OpenAI** établit une intention commerciale, sans fournir les paiements réellement exécutés ni le revenu reconnu chez OpenAI. OpenAI Inc., OpenAI Global LLC et OpenAI Group PBC restent des personnes distinctes, avec une recapitalisation datée ; les JV et les véhicules ne sont pas absorbés dans une identité de marque.

Les fonds Vision sont consolidés selon IFRS10 ; leurs transactions internes sont éliminées. Les intérêts des investisseurs externes et les créances sur le management sont distingués du cash déjà reçu. La concentration de revenus par client, les paiements de services OpenAI et les revenus de projets Stargate restent ND lorsque la contrepartie ou le montant n'est pas publié.

## Traçabilité et limites de la livraison

**{len(sources)} sources officielles conservées**, **{len(qualified)} sources qualifiées**, dont six originaux annuels EDINET, **{validation['new_statement_facts']} faits de tableaux** et **{validation['new_authored_observations']} observations** intégrés. **{unique_pages} pages pertinentes ont été lues personnellement**. Les extractions historiques des états à partir de 2021 sont intégrées ; leur extraction automatique ne vaut pas lecture de toutes les notes historiques.

Les contrôles comprennent les équations de bilan/cash, la confrontation des états anglais avec l'original EDINET et la préservation des huit tables SEC. Les sources sont identifiées par URL, empreinte SHA-256, date, page et citation. Les chiffres PDF sont **non balisés XBRL**. Les variantes `legacy_EDGAR_only` et `{VARIANT}` permettent de distinguer la politique initiale et son extension. Les valeurs inconnues ne deviennent pas zéro. Les états japonais standalone ne sont pas mélangés aux IFRS consolidés.

Les lacunes restantes concernent les contrats complets, les seuils de collatéral, le tirage Tsubaki, les revenus privés d'OpenAI, les notes historiques non relues et l'inventaire exhaustif des amendements EDINET. Ce sont des limites de preuve publiées dans `exclusions`, pas une file de pages annoncée comme terminée. Aucun audit indépendant ni score de fragilité n'est revendiqué.

Le dernier bilan disponible dans cette collecte est celui de juin. Les cellules du trimestre clos en septembre portent un motif distinct : **rapport périodique non connu à l'arrêt des sources**. Les communiqués d'octobre ne sont pas employés pour fabriquer ce bilan.

Sources principales : [original EDINET FY2025]({jp}), [états annuels anglais audités]({aurl}), [comptes de juin et notes]({qurl}). Les inventaires, données, liens et contrôles sont joints au dossier et sauvegardés sur [GitHub](https://github.com/jsiaut/codex_test).
'''
    (root/'softbank_integration.md').write_text(report)
    addition='\n\nMise à jour SoftBank : le modèle courant comprend **24 groupes**. Les sources japonaises et la comparaison SEC sont documentées dans [softbank_integration.md](softbank_integration.md). Les chiffres de cette extension ont leur index dans [audit/softbank_numbers.csv](audit/softbank_numbers.csv) ; les résultats SEC antérieurs conservent leur index et leurs critères.\n\n'
    for name in ['synthesis.md','delta.md','series.md','audit/domain_rules.md']:
        path=root/name;text=path.read_text();marker='Mise à jour SoftBank :'
        if marker not in text:
            head,sep,tail=text.partition('\n');path.write_text(head+addition+tail)
    readme=(root/'README.md').read_text();marker='\n## Intégration SoftBank — sources officielles japonaises\n'
    if marker in readme:readme=readme.split(marker)[0]
    readme+=marker+'\nLe modèle courant comprend 24 groupes. Lire [softbank_integration.md](softbank_integration.md). Les huit tables contiennent la base SEC intacte et les données SoftBank qualifiées ; [softbank_summary.json](softbank_summary.json) donne les contrôles et la couverture. `python -m secfragility.softbank_integration` reconstruit cette extension depuis le checkpoint SEC immuable et les sources japonaises conservées. `python -m secfragility.phase3 --reconstruct` conserve la reconstruction complète depuis le cache SEC, puis applique la même extension.\n'
    (root/'README.md').write_text(readme)
    inventory=json.loads((root/'work/inventory.json').read_text());inventory['groups'][GROUP]=dict(name='SoftBank Group Corp.',cik='0001065521',edinet_code='E02778',analysis_start='2021-01-01',source_protocol=VARIANT,legacy_EDGAR_financial_statements=0)
    (base/'unified_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n')
    summary=json.loads((root/'delivery_summary.json').read_text());summary['softbank_integration']=snapshot;summary['current_main_groups']=24
    summary['current_table_counts']=counts
    summary['legacy_table_counts']=summary.get('legacy_table_counts',summary['tables'])
    summary['tables']=counts
    (root/'delivery_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str)+'\n')
    for name in ['softbank_integration.md','softbank_measures.csv','softbank_evidence.csv','softbank_controls.csv','softbank_links.csv','softbank_reading_coverage.csv','softbank_sources.csv','softbank_summary.json','softbank_annex_e.csv','softbank_events.csv','softbank_bond_register.csv']:
        shutil.copy2(root/name,output/name)
    shutil.copy2(base/'validation.json',output/'softbank_validation.json')
    return snapshot
