"""Issuer-reported chronology, with lower assurance than accounts."""
from pathlib import Path
from lxml import html
import hashlib,json
ROOT=Path('.').resolve();BASE=ROOT/'work/softbank'
sources=json.loads((BASE/'sources.json').read_text());rows=[]
def body(s):
    tree=html.fromstring((ROOT/s['path']).read_bytes())
    for node in tree.xpath('//script|//style|//header|//footer|//nav'):node.drop_tree()
    return ' '.join(tree.text_content().split())
def add(path,quote,quantity,finding,**fields):
    s=next(s for s in sources if s['url']=='https://group.softbank'+path)
    text=body(s);assert quote in text,(path,quote)
    date='-'.join([path.rsplit('/',1)[-1][:4],path.rsplit('/',1)[-1][4:6],path.rsplit('/',1)[-1][6:8]])
    rows.append(dict(document_url=s['url'],source_sha256=s['sha256'],page=None,
        quote=quote,quantity=quantity,finding=finding,publication_date=date,
        source_profile='official_issuer_transaction_chronology',filing_status='issuer_disclosure',
        assurance_override='unaudited',tier_override='C',**fields))

add('/en/news/press/20261001','it executed the third and final tranche','named_investment_acquisitions',
    'Troisième tranche10MdUSDréalisée seloncommuniquédaté ; preuve émetteurunaudited, distinctcompte juin. Recoupée par publicationSGX.',
    amount='10000000000',currency='USD',stage='drawn_or_paid',event_date='2026-10-01',event_type='funding',counterparty='OpenAI Group PBC',instrument_key='OpenAI_2026_follow_on')
add('/en/news/press/20261001','cumulative investment in OpenAI totals USD 64.6 billion','openai_cumulative_investment_reported',
    'Cumul publié inclut investissements historiques et indirects ; pas FV, cash disponible ni somme de toutes lignes du modèle.',
    amount='64600000000',currency='USD',stage='recognized',period_end='2026-10-01',counterparty='OpenAI Group PBC',measurement_basis='issuer_reported_cumulative_investment_not_fair_value')
add('/en/news/press/20261001','ownership interest is approximately 13%','openai_ownership_reported',
    'Pourcentage approximatif publié ; ne prouve pas contrôle IFRS10.',amount='0.13',unit='ratio',stage='recognized',period_end='2026-10-01',counterparty='OpenAI Group PBC')
add('/en/news/press/20261001','all borrowings under the bridge facility agreement have been repaid and no undrawn commitments remain.',
    'march_bridge_outstanding_closed','Toutes les dettes tirées de cette facilité mars40MdUSD sont remboursées ; ne veut pas dire dette totaleSBGzero, ni nouveau prêtTsubaki clôturé.',amount='0',currency='USD',stage='settled',period_end='2026-10-01',instrument_key='OpenAI_bridge_2026',event_type='repayment')
add('/en/news/press/20261001','SBG canceled the remaining USD 10.0 billion of undrawn capacity',
    'march_bridge_undrawn_cancelled','Capacité non tirée10MdUSDannulée30sept ; pas paiement ni montantcash à retrancherdesdettes.',amount='10000000000',currency='USD',stage='terminated',event_date='2026-09-30',event_type='termination',instrument_key='OpenAI_bridge_2026')
add('/en/news/press/20260909','has decided to prepay, on September 15, 2026','march_bridge_prepayment_decision',
    'Décision prépaiement25.9MdUSD et nonpreuve exécution au9sept ; exécutionconfirméecommuniqué1oct.',amount='25900000000',currency='USD',stage='signed',event_date='2026-09-15',instrument_key='OpenAI_bridge_2026')
add('/en/news/press/20260909','USD 30.0 billion has been drawn to date','march_bridge_total_drawn',
    'Cumul tiré30MdUSD de40MdUSD, distinctsolde25.9 et30MdUSDengagementequityOpenAI.',amount='30000000000',currency='USD',stage='drawn_or_paid',period_end='2026-09-09',instrument_key='OpenAI_bridge_2026')
add('/en/news/press/20260924','consisting of USD 10 billion of USD-denominated Senior Notes and EUR 1 billion of EUR-denominated Senior Notes',
    'senior_notes_new_USD_nominal','NominalUSD10Md, séparéEUR1Md ; équivalent11.1MdUSDnonadditionné.',amount='10000000000',currency='USD',stage='signed',instrument_key='SBG_September_2026_notes',event_date='2026-09-29')
add('/en/news/press/20260924','EUR 1 billion of EUR-denominated Senior Notes','senior_notes_new_EUR_nominal',
    'NominalEUR1Md ; pasUSD1Md.',amount='1000000000',currency='EUR',stage='signed',instrument_key='SBG_September_2026_notes',event_date='2026-09-29')
add('/en/news/press/20260924','8.625% per annum9.250% per annum9.750% per annum','USD_bond_coupons',
    'USD1Md8.625%2030,4.5Md9.25%2032,4.5Md9.75%2034 ; nominal/coupon/maturitéspourchaquetranche dansregistre ; dateexpectedpaspreuveémissionauniveaudechaquetranche.')
add('/en/news/press/20250203_0','will spend $3 billion US annually','OpenAI_annual_service_spend_announced',
    'Dépense annuelleannoncée3MdUSD ; pasrevenuOpenAIreconnu ni cash effectivement payé ; contratcomplet/calendrieracceptation/recettesnonpubliés. La partie au communiqué est OpenAI Inc., distincte du PBC créé ultérieurement.',amount='3000000000',currency='USD',stage='intent_non_binding',counterparty='OpenAI, Inc.',family='commercial',link_type='purchase_commitment',instrument_key='Cristal_annual_service_plan_2025',event_date='2025-02-03')
add('/en/news/press/20250203_0','will be 50:50 owned by OpenAI and a company established by SoftBank Group Corp. and SoftBank Corp., will be consolidated to SoftBank Corp.',
    'SB_OpenAI_Japan_control_plan','JVannoncée50/50maisconsolidationSB Corpattendue ; nepasconfondre50%JVavec13%OpenAIGroup ; appartenance effectiveàvérifierdanscomptescourants.',counterparty='SB OpenAI Japan',stage='intent_non_binding')
add('/en/news/press/20250122','$500 billion','Stargate_announced_program_budget',
    'Budgetprogramme500MdUSD sur4ans annoncé ; pascashSBGversé ni engagementcontractuelferme500MdUSDattribué.',amount='500000000000',currency='USD',stage='intent_non_binding',instrument_key='Stargate_program_announced_2025')

if __name__=='__main__':
    (BASE/'chronology_observations.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    print(dict(chronology_observations=len(rows)))
