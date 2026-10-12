"""Personally read pages and authored evidence; no model/API or agent call."""
from pathlib import Path
import hashlib,json,re
ROOT=Path('.').resolve(); BASE=ROOT/'work/softbank'
SOURCES=json.loads((BASE/'sources.json').read_text())
A=next(s for s in SOURCES if s.get('role')=='latest_full_financial_statements')
Q=next(s for s in SOURCES if 'q1fy2026_01_en.pdf' in s['url'])
def norm(text): return ' '.join(re.sub('[\uFFFD\x08]+',' ',text).split())
ledger=[]; observations=[]
def read(doc,pages,family,finding):
    pp=(ROOT/doc['text_path']).read_text().split('\f')
    for page in pages:
        raw=pp[page-1]
        ledger.append(dict(document_url=doc['url'],source_sha256=doc['sha256'],
            page=page,text_page_sha256=hashlib.sha256(raw.encode()).hexdigest(),
            family=family,finding=finding,state='personally_read',reviewer='sole_executor'))
def add(doc,page,quote,quantity,finding,**fields):
    raw=(ROOT/doc['text_path']).read_text().split('\f')[page-1]
    assert quote in norm(raw),(page,quote)
    observations.append(dict(document_url=doc['url'],source_sha256=doc['sha256'],page=page,
        quote=quote,quantity=quantity,finding=finding,**fields))

read(A,[2,3,4,5,6,7,8,9,10,11,12],'financial_statements',
     'États IFRS en millions JPY ; USD de convenance séparé ; CFO négatif malgré les gains de valorisation ; bilan et tableau de flux ne donnent pas le cash disponible de la holding.')
read(A,[13,14,15,27,28,29,30,31,32,33,34],'investments_and_perimeter',
     'Périmètres, IFRS10/IAS28, SVF consolidés et gains intragroupe éliminés ; tiers SVF en passifs financiers, distincts de dette bancaire ; Arm/Ampere/Graphcore regroupés dans AI Computing depuis T3FY2025 ; comparatifs sectoriels reclassés.')
read(Q,[5,6,39,40,41,42,43,44,45,69,70,71,72], 'current_financials_and_financing',
     'Revue Deloitte limitée aux états et notes Appendix ; OpenAI FVTPL ; tranches et emprunts séparés ; Tsubaki signé avec tirage attendu seulement dans la note ; seconde tranche post-clôture ; frais/fonds intragroupe éliminés.')
add(A,13,'convenience of readers outside of Japan','convenience_translation',
    'Aucune traduction USD des soldes JPY utilisée pour sommer ou comparer des expositions USD contractuelles.')
add(A,14,'On October 28, 2025','openai_legal_successor',
    'OpenAI Group PBC distinct de l’ancien OpenAI Global LLC et de l’ancienne structure ; date de recapitalisation vérifiée.',event_date='2025-10-28',counterparty='OpenAI Group PBC')
add(A,27,'Consolidation of SVF1, SVF2, and LatAm','fund_consolidation',
    'SVF1 et SVF2 contrôlés IFRS10 ; LatAm contrôlé ; aucun double compte du groupe et des fonds.')
add(A,28,'Contributions to SVF1, SVF2, and LatAm from the Company are eliminated in consolidation.',
    'intragroup_elimination','Apports holding-fonds éliminés ; montants de fonds avant tiers ne représentent pas tous la part économique SBG.')
add(A,28,'No cash contributions into SVF2 and LatAm',
    'management_contributions_non_cash','Les receivables de co-investissement de management ne sont pas du cash déjà reçu.')
add(A,30,'the AI Computing segment was newly established','segment_perimeter_break',
    'Arm, Ampere et Graphcore regroupés ; ancienne série Arm et nouvelle AI Computing non substituables sans reclassification publiée.')
add(A,33,'¥6,465,523 million','named_investment_unrealized_gain',
    'Gain OpenAI incluant changements de FV du forward transféré ; non assimilable intégralement à des acquisitions ou du cash.',
    amount='6465523000000',currency='JPY',counterparty='OpenAI Group PBC',stage='recognized',
    period_start='2025-04-01',period_end='2026-03-31',measurement_basis='investment_gain_including_forward_fair_value')
add(A,34,'a 7% rate per annum','svf1_preferred_fixed_distribution',
    'Distribution privilégiée contractuelle de SVF1, non coupon d’une dette SBG ; assiette des apports préférentiels, distincte de tous les actifs du fonds.',amount='0.07',unit='ratio',stage='signed')
add(Q,70,'First tranche','named_investment_acquisitions',
    '10 Md USD versés le 1 avril 2026 ; ne pas additionner à la FV de fin de période.',
    amount='10000000000',currency='USD',stage='drawn_or_paid',event_date='2026-04-01',
    counterparty='OpenAI Group PBC',event_type='funding',instrument_key='OpenAI_2026_follow_on')
add(Q,70,'Second tranche','named_investment_acquisitions',
    '10 Md USD versés le 1 juillet 2026 ; événement post-clôture juin.',
    amount='10000000000',currency='USD',stage='drawn_or_paid',event_date='2026-07-01',
    counterparty='OpenAI Group PBC',event_type='funding',instrument_key='OpenAI_2026_follow_on')
add(Q,71,'FVTPL','openai_accounting','Common et preferred OpenAI en FVTPL ; gain ≠ cash ni nouveau financement.')
add(Q,71,'Borrower','tsubaki_borrower_identity','SVF II TSUBAKI (DE) LLC est la filiale emprunteuse détenue entièrement par SVF2.',counterparty='SVF II TSUBAKI (DE) LLC')
add(Q,71,'Borrowing amount','signed_loan_nominal','10 Md USD contrat 5 août 2026 ; tirage août attendu, réalisé non établi par cette note.',
    amount='10000000000',currency='USD',stage='signed',event_date='2026-08-05',instrument_key='TSUBAKI_2026',
    counterparty='SVF II TSUBAKI (DE) LLC',event_type='signing')
add(Q,71,'Guarantor','parent_guarantee','SBG garant ; montant maximal de garantie non explicitement déterminé.',
    counterparty='SVF II TSUBAKI (DE) LLC',stage='signed',instrument_key='TSUBAKI_2026',family='credit_support',link_type='guarantee')
add(Q,71,'Mandated lead arrangers','arranger_roles',
    'Goldman Sachs Bank USA, JPMorgan Chase N.A., Mizuho Securities USA LLC, Apollo Global Funding LLC, SMBC : rôles d’arrangeur, parts de prêteurs non divulguées ; aucune allocation des 10 Md USD à Apollo.',
    counterparty='Apollo Global Funding LLC',stage='signed',instrument_key='TSUBAKI_2026')
add(Q,71,'Collateral','collateral_cash_account',
    'Cash collateral account de l’emprunteur ; pas de preuve ici d’un nantissement direct des titres OpenAI. Baisse significative de FV OpenAI : apport cash/remboursement obligatoire ; seuil et occurrence non publiés.',
    counterparty='OpenAI Group PBC',instrument_key='TSUBAKI_2026',trigger_occurred='unknown',wrong_way=True)
add(Q,45,'IAS 34','interim_framework','TSE article 5-2 avec omissions IAS34 article5-5 ; ne pas revendiquer IAS34 intégral.')

read(A,[35,36,37,38,39,40,54,55,56,57,58,59,60,61,67,68,69,70,71,72,73,90,91,92,93],
     'funds_debt_leases_and_commitments',
     'Fonds, co-investissement management, Ampere acquis le 25 novembre 2025 ; leases lessee distinctes lessor ; périmètres des filiales ; prêts Arm/SB Corp/Energy Global sans recours SBG, SVF2 recours limité ; covenants par débiteur ; maturités et passifs des tiers distincts ; supplier finance exclu du graphe.')
read(Q,[36,37,38,57,58,64],'current_statements_and_debt',
     'Comptes juin ; dette courante 7,559,173 M JPY et non courante 19,085,685 ; 20 Md USD effectivement tirés en avril par deux emprunteurs distincts ; capex inclut prepaid expenses/prépayments ; investissement SVF OpenAI 1,605,100 M JPY.')
add(A,37,'$8.2 billion','svf1_third_party_uncalled',
    'Capital non appelé de tiers SVF1 ; ni cash disponible SBG ni engagement de financement SBG supplémentaire.',
    amount='8200000000',currency='USD',stage='signed',period_end='2026-03-31',measurement_basis='third_party_uncalled_capital')
add(A,38,'November 25, 2025','ampere_control_acquisition','Ampere wholly owned depuis acquisition via Silver Bands 6 (US) Corp. ; pas une participation OpenAI ni un paiement commercial client.',
    event_date='2025-11-25',counterparty='Ampere Computing Holdings LLC')
add(A,38,'970,680','ampere_acquisition_cash','Paiement acquisition cash 970,680 M JPY ; distinction acquisition entreprise, ancien intérêt 46,899, dette relais 6.5 Md USD et net cash acquis.',
    amount='970680000000',currency='JPY',stage='drawn_or_paid',event_date='2025-11-25',counterparty='Ampere Computing Holdings LLC',event_type='secondary_purchase')
add(A,40,'$6.5 billion','ampere_bridge_drawn','Prêt tiré 25 novembre 2025 ; usage acquisition, dettes et frais ; remboursé avril 2026 dans la même note.',amount='6500000000',currency='USD',stage='drawn_or_paid',event_date='2025-11-25',instrument_key='Ampere_bridge_2025')
add(A,40,'¥292,622 million','bank_cash_reserve','Cash consolidé inclut dépôts Banque du Japon des filiales bancaires ; pas librement disponible à la holding.',amount='292622000000',currency='JPY',stage='recognized',period_end='2026-03-31')
add(A,54,'¥978,450 million','ifrs_lease_liabilities','Dette locative IFRS16 ; maturités jusqu’en 2062 ; non-additive aux deux postes courants/non courants de bilan.',amount='978450000000',currency='JPY',stage='recognized',period_end='2026-03-31')
add(A,57,'40.1% of the voting rights','softbank_corp_control','SoftBank Corp consolidé sous contrôle de fait malgré vote minoritaire ; cash/revenus telecom dans le consolidé ne sont pas seuls ceux de la holding.')
add(A,61,'895,325','unconsolidated_structured_max_loss','Exposition maximale = valeur comptable 837,183 M JPY + engagements 58,142 ; pas perte attendue ni exposition IA attribuée.',amount='895325000000',currency='JPY',stage='recognized',period_end='2026-03-31')
add(A,67,'769,029,000','arm_pledged_shares','Actions Arm nanties chez Kronos ; prêt nominal20 Md USD, comptable3,168,545 M JPY, échéance sept2027 ; sans recours à SBG.',amount='769029000',unit='shares',stage='recognized',counterparty='Arm Holdings plc',instrument_key='Kronos_Arm_margin_loan',period_end='2026-03-31')
add(A,72,'a $20','arm_margin_loan_nominal','20 Md USD effectivement empruntés chez Kronos ; distinct du montant comptable JPY ; sans recours holding, cash collateral et prepay possibles selon FV Arm.',amount='20000000000',currency='USD',stage='drawn_or_paid',counterparty='Kronos I (UK) Limited',instrument_key='Kronos_Arm_margin_loan',period_end='2026-03-31',recourse='non_recourse_to_SBG',wrong_way=True)
add(A,72,'¥814,202 million','svf2_existing_limited_recourse_loan','Prêt SVF2 déjà comptabilisé mars, nantissement intérêts filiales ; recours limité SBG ; ne pas confondre nouveau Tsubaki signé août.',amount='814202000000',currency='JPY',stage='recognized',period_end='2026-03-31',instrument_key='SVF2_existing_facility',recourse='limited_recourse_to_SBG')
add(A,72,'¥1,196,534','telecom_pledge_loan','Prêt garanti par actions SoftBank Corp chez filiale ; sans recours SBG, cash collateral/prepay possibles.',amount='1196534000000',currency='JPY',stage='recognized',period_end='2026-03-31',instrument_key='SoftBank_Corp_share_loan',recourse='non_recourse_to_SBG',wrong_way=True)
add(A,71,'less than 70%','holding_covenant_ratio','Covenant net senior debt / listed shares etc <70%, distinct politique de gestion LTV ; assiettes contractuelles exactes et marge de sécurité non reconstituées.',amount='0.70',unit='ratio',stage='signed',measurement_basis='contractual_threshold_not_observed_LTV')
add(A,71,'¥369.8 billion','holding_net_assets_covenant','Plancher actif net standalone, cadre japonais parent ; ne pas tester avec equity consolidée IFRS.',amount='369800000000',currency='JPY',stage='signed',measurement_basis='parent_standalone_covenant_threshold')
add(A,90,'¥8,147,436 million','credit_facilities_undrawn_reported','Consolidé inclut7,311,390 M JPY sous conditions ; pas intégralement cash mobilisable inconditionnel. Solde historique mars avant tirages/retraits ultérieurs.',amount='8147436000000',currency='JPY',stage='available',period_end='2026-03-31',measurement_basis='consolidated_undrawn_facilities_including_conditional')
add(A,90,'¥7,311,390','credit_facilities_undrawn_conditional','Part sous conditions au tirage ; ne pas retenir comme liquidité assurée.',amount='7311390000000',currency='JPY',stage='available',period_end='2026-03-31',measurement_basis='conditional_facilities_subset')
add(A,93,'¥80,656 million','supplier_finance_arrangement','Passif supplier finance LY inclus payables ; exclu graphe IA, pas dette additionnelle à sommer au bilan.',amount='80656000000',currency='JPY',stage='recognized',period_end='2026-03-31')
add(Q,57,'¥1,452,593 million','bridge_holding_balance','March facility borrower holding :8.9 Md USD convenience et JPY comptable ; distinction finance-sub balance.',amount='1452593000000',currency='JPY',stage='recognized',period_end='2026-06-30',instrument_key='OpenAI_bridge_2026_holding')
add(Q,57,'¥1,119,310 million','bridge_finance_sub_balance','Finance sub OpenAI6.9 Md USD convenience ; ne pas utiliser FX de présentation comme flux.',amount='1119310000000',currency='JPY',stage='recognized',period_end='2026-06-30',instrument_key='OpenAI_bridge_2026_finance_sub')
add(Q,64,'¥1,605,100 million','named_investment_acquisitions','Première tranche10MdUSD en JPY de transaction ; couvre même paiementUSD1avril, pas second montant à sommer.',amount='1605100000000',currency='JPY',stage='drawn_or_paid',event_date='2026-04-01',counterparty='OpenAI Group PBC',instrument_key='OpenAI_2026_follow_on',measurement_basis='JPY_same_cash_payment_as_USD_10bn')
add(Q,64,'includes cash outflows from long-term','capex_scope','Le poste purchase PP&E/intangibles inclut prepaid expenses et prépayments ; FCF correspondant documenté sur cette base, comparaison sectorielle limitée.')

read(A,[82,84,85,97,98,99,100,101,102,103,104,105,123,124,125,129,133,134,140,141,142,143,144,145],
    'valuation_cashflows_contracts',
    'FV niveau3 et risques de valorisation ; warrants Energy Global contrepartie non nommée ; titres non-cash et apport forward ; ventes NVIDIA/Intel ; RPO exclut royalties futures ; commitments OpenAI hors purchases généraux ; prêts shopping/credit card non IA ; acquisitions ABB conditionnelles.')
read(Q,[11,12,13,14,28,29,30,31,51,52,53,54,55,56,59,60,61,62,65,66,67,68],
    'current_perimeter_cash_valuation_related_parties',
    'Cash par entité après éliminations : SBG754752MJPY ; dette holding et financingsubs nonrecourse séparées ; warrants1.050843trJPY liés baux DC anonymes ; gainIntel noncash ; co-investissementsmanagement receivables, garantie personnelleSon et actionsSBGcollatéral.')
add(Q,28,'SBG 2,523,841 754,752','holding_cash',
    'Cash holding après éliminations, non entièrement cash consolidé accessible ; front narratif non inclus automatiquement revue Appendix.',amount='754752000000',currency='JPY',stage='recognized',period_end='2026-06-30',measurement_basis='parent_cash_after_consolidation_eliminations',assurance_override='unaudited',tier_override='C')
add(Q,30,'SBG 12,323,379 12,238,207','holding_debt_and_leases',
    'Dette et leases SBG parent après éliminations, pas holding segment ni dette consolidée totale.',amount='12238207000000',currency='JPY',stage='recognized',period_end='2026-06-30',measurement_basis='parent_debt_and_leases_after_consolidation_eliminations',assurance_override='unaudited',tier_override='C')
add(Q,30,'all interest-bearing debt is nonrecourse to SBG','holding_nonrecourse_boundary','Exception explicite : bridge OpenAI1119310MJPY ; distinct des margin loans Arm/SoftBankCorp et prépaidforwards.',assurance_override='unaudited',tier_override='C')
add(Q,59,'1,050,843','energy_warrant_liability','Warrants Energy Global convertibles nombre variable d’intérêts ; dérivé passif reconnu, non dette cash simplement exigible.',amount='1050843000000',currency='JPY',stage='recognized',period_end='2026-06-30',counterparty='Energy Global, LP',measurement_basis='derivative_warrant_fair_value')
add(A,82,'as lease incentives','energy_warrants_customer_incentive','Warrants attribués en incentive de baux data centers en tant que bailleur ; client non nommé. Impossible d’attribuer automatiquement OpenAI, ou assimilier passif à revenus.',amount='582962000000',currency='JPY',stage='recognized',period_end='2026-03-31',measurement_basis='anonymous_lease_incentive_derivative_liability',counterparty_evidence='anonymous')
add(A,98,'¥20,510,483','svf_level3_assets','SVF FVTPL niveau3 à fin mars, actifs à inputs non observables ; inclus23,495,706MJPYFVTPLtotal.',amount='20510483000000',currency='JPY',stage='recognized',period_end='2026-03-31',measurement_basis='level3_subset_of_SVF_FVTPL')
add(A,103,'¥1,850,108 million','openai_forward_noncash_transfer','Valeur forward à exercice transférée aux titres ; mouvement noncash, distinct22.5MdUSDversés.',amount='1850108000000',currency='JPY',stage='recognized',event_date='2025-12-26',counterparty='OpenAI Group PBC',measurement_basis='non_cash_forward_value_transferred_to_shares')
add(A,129,'¥5,081,443 million','openai_annual_gross_investment_cash','33.5MdUSD cash acquits SVF OpenAI ; comprend8.5+22.5+2.5 ; 1MdUSD ensuite syndiqué, et premierclosing économique7.5MdUSD. Ces assiettes ne sont pas identiques.',amount='5081443000000',currency='JPY',stage='drawn_or_paid',period_start='2025-04-01',period_end='2026-03-31',counterparty='OpenAI Group PBC',measurement_basis='gross_cash_purchases_before_co_investor_syndication')
add(A,144,'$22.5 billion','named_investment_acquisitions','Second closing décembre2025 complété ; montant22.5MdUSDcash distinct34.5MdUSDvaleur comptable incluantforward.',amount='22500000000',currency='USD',stage='drawn_or_paid',event_date='2025-12-26',counterparty='OpenAI Group PBC',instrument_key='OpenAI_2025_second_closing',event_type='funding')
add(A,142,'¥3,244,569 million','purchase_commitments_total','Achats services/biens incluent448741MJPYJV ; excluent engagement30MdUSDOpenAI et ABB soumisapprovals. Échéanciercash détaillé non divulgué.',amount='3244569000000',currency='JPY',stage='signed',period_end='2026-03-31',measurement_basis='purchase_services_goods_including_JV_excluding_OpenAI_ABB')
add(A,142,'¥4,796,400 million','openai_undrawn_investment_commitment','30MdUSDengagementOpenAI31mars ; payé3tranchesultérieures. Ne pas laisser30MdUSDto pay à cutoffOctobre.',amount='4796400000000',currency='JPY',stage='signed',period_end='2026-03-31',counterparty='OpenAI Group PBC',instrument_key='OpenAI_2026_follow_on',measurement_basis='unpaid_investment_commitment_at_March_31')
add(A,142,'$5.375 billion','ABB_acquisition_conditional','Contrat8oct2025 soumisapprovals, closingattendulate2026 ; horsachatsgénéraux et pas paiementétabli.',amount='5375000000',currency='USD',stage='signed',counterparty='ABB Ltd',event_date='2025-10-08',measurement_basis='conditional_company_acquisition_purchase_price')
add(A,140,'¥10,649,038','consumer_lending_commitments','Largement limites cartes de crédit télécom modifiables ; pas investissement IA ferme.',amount='10649038000000',currency='JPY',stage='available',period_end='2026-03-31',measurement_basis='consumer_card_limits_not_AI_funding')
add(A,123,'¥480,487 million','rpo_total','RPOgroupe480487MJPY,331183Arm et149304telecom ; royaltiesfutures excluesArm ; sans attributionOpenAI.',amount='480487000000',currency='JPY',stage='recognized',period_end='2026-03-31',measurement_basis='RPO_excluding_future_Arm_royalties')
add(Q,67,'35,588,400 shares','management_SBG_share_collateral','ActionsSBG déposéescontre receivablesMgmtCo ; actionSBGpeutbaisseravecvaleursfonds : co-mouvementàsurveiller, pascallconstaté.',amount='35588400',unit='shares',stage='recognized',period_end='2026-06-30',counterparty='MASA USA LLC',instrument_key='SVF2_management_receivable',wrong_way=True)
add(Q,5,'cumulative investment totaled $44.6 billion','openai_cumulative_investment_reported',
    'Cumul publié à fin juin avant tranche de juillet, distinct de la juste valeur et des gains cumulés.',amount='44600000000',currency='USD',stage='recognized',period_end='2026-06-30',counterparty='OpenAI Group PBC',measurement_basis='issuer_reported_cumulative_investment',assurance_override='unaudited',tier_override='C')
add(Q,5,'a fair value of $89.6 billion','named_investment_carrying_amount',
    'Juste valeur OpenAI à fin juin, publiée en USD dans le narratif ; pas une trésorerie disponible ni une valorisation actualisée au 9 octobre.',amount='89600000000',currency='USD',stage='recognized',period_end='2026-06-30',counterparty='OpenAI Group PBC',measurement_basis='named_holding_fair_value_June_30',assurance_override='unaudited',tier_override='C')
add(A,125,'Impairment loss on equity method investments','investment_impairment',
    'Dépréciation de participations mises en équivalence : 20,596 M JPY sur l’exercice. Investissement financier ; distinct des 38,386 M JPY d’autres dépréciations. Contreparties non nommées.',amount='20596000000',currency='JPY',stage='recognized',period_start='2025-04-01',period_end='2026-03-31',event_type='impairment')
read(Q,[47],'going_concern_and_segments','La section de doute significatif sur la continuité indique explicitement There are no applicable items ; elle porte seulement sur le dernier trimestre et ne vaut pas absence d’événement dans l’historique.')
add(Q,47,'There are no applicable items.','going_concern_explicit_none',
    'Absence explicitement déclarée de doute significatif dans ce trimestre, dans la section dédiée de l’émetteur ; assurance de cette déclaration séparée de la revue des notes.',amount='0',unit='event',stage='recognized',period_start='2026-04-01',period_end='2026-06-30',assurance_override='unaudited',tier_override='C')

if __name__=='__main__':
    (BASE/'reading_ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
    (BASE/'authored_observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2)+'\n')
    print(dict(pages=len(ledger),observations=len(observations)))
