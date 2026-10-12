"""Publish a manually authored feasibility pilot, outside legacy SEC metrics."""
from pathlib import Path
from datetime import datetime,timezone
from decimal import Decimal
import csv,hashlib,json,re,subprocess

ROOT=Path('.').resolve();BASE=ROOT/'work/softbank'
sources=json.loads((BASE/'sources.json').read_text())
Q=next(r for r in sources if 'q1fy2026' in r['url'])
A=next(r for r in sources if r['role']=='latest_full_financial_statements')
J=next(r for r in sources if 'securities_report_q4fy2025' in r['url'])
def norm(t):return ' '.join(re.sub('[\uFFFD\x08]+',' ',t).split())
rows=[]
def add(doc,page,quote,quantity,conclusion,amount=None,currency=None,stage=None,event_date=None):
    pages=(ROOT/doc['text_path']).read_text().split('\f');raw=pages[page-1]
    assert quote in norm(raw),(page,quote)
    if amount is not None:Decimal(str(amount))
    rows.append(dict(source_url=doc['url'],source_path=doc['path'],source_sha256=doc['sha256'],
        page_pdf_1based=page,text_page_sha256=hashlib.sha256(raw.encode()).hexdigest(),quote=quote,
        quantity=quantity,amount=amount,currency=currency,stage=stage,event_date=event_date,
        conclusion=conclusion,legacy_sec_tier='F',eligible_for_legacy_sec_core=False,
        protocol_status='foreign_extension_pilot_not_integrated',reviewer='sole_executor',subagents_used=False))

add(Q,71,'Borrowing amount','svf2_tsubaki_loan_nominal',
 'Contrat du 5 août 2026 de 10 Md$ ; emprunteur SVF II TSUBAKI (DE) LLC, filiale de SVF2 ; maturité août 2028. Tirage seulement attendu en août dans cette note : tirage effectif non établi ici.',
 '10000000000','USD','signed','2026-08-05')
add(Q,71,'Guarantor','svf2_parent_guarantee',
 'SoftBank Group est nommé garant. Collatéral indiqué : compte de cash de l’emprunteur ; la baisse de FV des actions privilégiées OpenAI sert de référence aux clauses de cash collateral et remboursement obligatoire. Ne pas requalifier sans preuve en nantissement direct des actions. Étendue précise de la garantie et seuils de déclenchement non déterminés.',stage='signed',event_date='2026-08-05')
add(Q,71,'Mandated lead arrangers','svf2_bank_roles',
 'Goldman Sachs Bank USA, JPMorgan Chase Bank N.A., Mizuho Securities USA LLC, Apollo Global Funding LLC et Sumitomo Mitsui Banking Corporation sont nommés chefs de file. Ce rôle ne prouve pas la part financée ou l’exposition de chaque banque ; ne pas attribuer les 10 Md$ à Apollo.',stage='signed')
add(Q,70,'First tranche','openai_first_tranche_cash',
 'La note rapporte la première tranche exécutée le 1er avril. Flux distinct de l’engagement global, du tirage bancaire et de la FV du portefeuille.',
 '10000000000','USD','drawn_or_paid','2026-04-01')
add(Q,70,'Second tranche','openai_second_tranche_cash',
 'La seconde tranche exécutée le 1er juillet est un événement postérieur au bilan de juin ; elle ne modifie pas rétroactivement les soldes de juin.',
 '10000000000','USD','drawn_or_paid','2026-07-01')
add(Q,71,'FVTPL','openai_non_cash_valuation',
 'Actions privilégiées et ordinaires OpenAI à juste valeur par résultat ; une variation de FV n’est ni apport de cash nouveau ni trésorerie disponible.',stage='recognized')
add(Q,45,'IAS 34','interim_reporting_framework',
 'Cadre TSE Article 5-2, avec certaines informations IAS34 omises selon Article 5-5. Ne pas déclarer un jeu complet d’informations IAS34.')
add(Q,72,'We have reviewed','interim_assurance_scope',
 'Deloitte a revu les états intérimaires et leurs notes inclus dans l’Appendix. La revue ne s’étend pas automatiquement à tout le narratif et aux présentations investisseurs.')
add(A,27,'Consolidation of SVF1, SVF2, and LatAm','vision_fund_consolidation',
 'SVF1 et SVF2 consolidés selon le pouvoir et les rendements IFRS10 ; LatAm consolidé selon les droits de vote. Frais et transactions intragroupe éliminés ; fonds et groupe ne s’additionnent pas comme expositions indépendantes.')
add(A,67,'non-recourse debt','arm_margin_loan_terms',
 'Emprunteur Kronos I (UK) Limited, filiale détenue en totalité ; prêt historique 8,5 Md$ et 11,5 Md$ supplémentaires effectivement empruntés. Le nominal de 20 Md$ est un calcul explicitement 8,5+11,5, distinct de la valeur comptable JPY et de la conversion USD de présentation. Maturité septembre 2027 après extension ; sans recours à SBG selon la note, mais cash collateral et remboursement anticipé possibles si baisse de FV des actions Arm nanties. Aucun seuil chiffré de déclenchement extrait ici.',
 '20000000000','USD','drawn_or_paid')
add(J,4,'2026年６月22日','japanese_filing_cover',
 'Couverture japonaise : rapport annuel FY2025, exercice 1 avril 2025–31 mars 2026, soumis le 22 juin 2026. Le préambule le décrit comme impression des données déposées via EDINET, avec rapports d’audit annexés. Il s’agit de la copie publiée par l’émetteur : récupération indépendante des octets EDINET et DocID à réaliser.')
with (BASE/'pilot_evidence.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(BASE/'pilot_evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')

inventory=[]
for s in sources:
    assert hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest()==s['sha256']
    row=dict(s);row['reading_state']='targeted_pages_reviewed' if s['url'] in {r['source_url'] for r in rows} else 'collected_not_reviewed'
    row['pages_reviewed']=json.dumps(sorted({r['page_pdf_1based'] for r in rows if r['source_url']==s['url']}))
    inventory.append(row)
fields=sorted(set().union(*(r.keys() for r in inventory)))
with (BASE/'source_inventory.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(inventory)
baseline=json.loads((ROOT/'work/idempotency_verification.json').read_text())
core_unchanged=all(hashlib.sha256((ROOT/'tables'/(t+'.parquet')).read_bytes()).hexdigest()==r['replay_sha256'] for t,r in baseline['tables'].items())
assert core_unchanged
assert subprocess.check_output(['git','show','64a3ba8324d1db1eab6ea8625d9949e2cf44e0a0:audit/criteria_manifest.json'])==(ROOT/'audit/criteria_manifest.json').read_bytes()
sec=json.loads((BASE/'sec_inventory.json').read_text())
assert sec['cik']=='0001065521' and sec['sec_financial_reports_in_window']==0
result=dict(created_at=datetime.now(timezone.utc).isoformat(),core_source_cutoff=baseline['as_of'],
    status='feasibility_verified_foreign_extension_prepared_not_integrated',issuer='SoftBank Group Corp.',cik=sec['cik'],
    official_issuer_sources=len(sources),pdfs=sum(s['path'].endswith('.pdf') for s in sources),
    source_bytes=sum(s['bytes'] for s in sources),pilot_observations=len(rows),source_hashes_verified=True,
    pilot_quotes_verified=True,legacy_eight_tables_unchanged=core_unchanged,legacy_criteria_unchanged=True,
    original_source_policy='EDGAR_only; non_EDGAR_tier_F_discovery_only',
    proposed_extension='JP_regulatory_filings_and_scope_verified_reviewed_interim_statements_in_separate_IFRS_layer',
    changes_required=['source_jurisdiction_and_regulatory_filing_identifier','per_section_assurance_scope',
      'JPY_USD_and_convenience_translation_separation','Japan_fiscal_year_and_annual_filing_deadline',
      'consolidated_group_versus_holding_company_LTV','dated_legal_entity_and_control_memberships',
      'nominal_carrying_fair_value_and_cash_flow_separation','baseline_EDGAR_and_extended_source_sensitivity'],
    unresolved=['direct_EDINET_bytes_DocIDs_and_regulatory_amendments',
      'complete_contracts_and_numeric_margin_call_triggers','actual_TSUBAKI_drawdown_and_current_balance',
      'complete_historical_note_reading','Stargate_financed_projects_versus_announced_budget'],
    all_sources_exhaustively_reviewed=False,subagents_used=False,independent_audit_performed=False)
(BASE/'feasibility.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False))
