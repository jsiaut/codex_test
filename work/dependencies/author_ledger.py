"""Manual role, edge, timeline and coverage decisions for eleven operations."""
from pathlib import Path
import json,re
from secfragility.database import connect,sql_literal
from secfragility.xbrl import digest
from secfragility.operation_sources import read,save,BASE

ROOT=Path('.').resolve(); B=ROOT/BASE; SCOPE=read(B/'scope.json'); ASOF=SCOPE['source_cutoff']
DB=connect()
for table in ('entities','observations','links'):
    DB.execute('CREATE VIEW '+table+' AS SELECT * FROM read_parquet('+sql_literal(str(B/'baseline'/(table+'.parquet')))+')')
OLD={r[0]:r for r in DB.execute('SELECT observation_id,model_quantity,document_id,knowledge_date,locator FROM observations').fetchall()}
NEW=read(B/'authored_observations.json'); NOTES={r['model_quantity']:r for r in NEW}
ALL={**{k:dict(zip(('observation_id','model_quantity','document_id','knowledge_date','locator'),v)) for k,v in OLD.items()},**{r['observation_id']:r for r in NEW}}
ENTITIES=[]; EDGES=[]; MEASURES=[]; OPERATIONS=[]

def evidence(quantity):return NOTES[quantity]['observation_id']
def norm(name):return re.sub(r'[^a-z0-9]','',name.casefold())
PREFERRED={
 'OpenAI OpCo, LLC':'legal:1f25e8f4d4adb8aba613e06de49ef13a00312daa9add8387b1312678a4e5b1fa',
 'Google LLC':'legal:71832df416b50795d06c6167834cb68943d344815496b4b751428e701411af1b',
 'NVIDIA Corporation':'cik:0001045810','Cerebras Systems Inc.':'cik:0002021728',
 'CoreWeave, Inc.':'cik:0001769628','Athene Holding Ltd.':'cik:0001527469',
 'TeraWulf Inc.':'cik:0001083301','Broadcom Inc.':'cik:0001730168',
 'Meta Platforms, Inc.':'cik:0001326801','SB Energy, Inc.':'cik:0002133037',
 'Nscale Limited':'cik:0002110365','Ionic Digital Inc.':'cik:0002007691','Hut 8 Corp.':'cik:0001964789',
 'PIMCO Extended Duration Fund':'series:S000013233'}
GROUPS={'cik:0001045810':'NVDA','cik:0002021728':'external:0002021728','cik:0001769628':'CRWV',
 'cik:0001083301':'external:0001083301','cik:0001730168':'AVGO','cik:0001326801':'META',
 'cik:0002133037':'external:0002133037','cik:0002110365':'external:0002110365',
 'cik:0002007691':'external:0002007691','cik:0001964789':'external:0001964789','series:S000013233':'fund_series:S000013233'}

def legal(name,ref,*,jurisdiction=None,status='confirmed'):
    oid=evidence(ref) if ref in NOTES else ref;o=ALL[oid]
    matches={r[0] for r in DB.execute('SELECT entity_id,legal_name FROM entities').fetchall() if norm(r[1])==norm(name)}
    eid=PREFERRED.get(name)
    if not eid:
        if len(matches)>1:raise ValueError('Manual identity choice required: '+name)
        eid=next(iter(matches)) if matches else 'legal:'+digest(['dependencies_legal_name',name])
    current=DB.execute("SELECT min(knowledge_date) FROM entities WHERE entity_id=? AND entity_status='confirmed'",[eid]).fetchone()[0]
    if current is not None and str(current)<=str(o['knowledge_date']):return eid
    if any(e['entity_id']==eid and e['knowledge_date']<=str(o['knowledge_date']) for e in ENTITIES):return eid
    if eid in GROUPS:group=GROUPS[eid];treatment='parent'
    else:group=None;treatment='undetermined'
    ENTITIES.append(dict(entity_id=eid,membership_id=digest(['dependency_identity',eid,oid]),legal_name=name,
        normalized_name=name.casefold(),cik=eid[4:] if eid.startswith('cik:') else None,jurisdiction=jurisdiction,
        entity_status=status,group_id=group,economic_group_id=group or eid,consolidation_treatment=treatment,
        knowledge_date=str(o['knowledge_date']),resolution_rule='manually_selected_exact_named_filed_party_or_registered_issuer;no_group_inference',
        evidence_document_id=o['document_id'],evidence_locator=o['locator'],source_perspective='counterparty'))
    return eid

def role(name,kind,ref=None,*,eid=None,unknown=None):
    if eid is None and ref:eid=legal(name,ref)
    row=dict(name=name,role=kind,entity_id=eid)
    if unknown:row['unknown_reason']=unknown
    return row

def edge(case,oid,a,b,family,kind,*,amount=False,replaces=None,proof=None):
    oid=evidence(oid) if oid in NOTES else oid
    row=dict(operation_id=case,observation_id=oid,from_entity_id=a,to_entity_id=b,from_group_id=GROUPS.get(a),
        to_group_id=GROUPS.get(b),family=family,type=kind,edge_kind='amount' if amount else 'relation',
        counterparty_evidence='derivable',vehicle_level=case in ('IONIC_WARD','HUT_RIVER','HUT_BEACON','HYPERION'))
    if replaces:row['replaces_link_id']=replaces
    if proof:row['identity_binding_evidence']=[evidence(p) if p in NOTES else p for p in proof]
    EDGES.append(row)

QUESTIONS=('entities','asset_or_service','engaged_or_paid_amount','revenue_payer','interruption_conditions','loss_allocation','cash_calendar','missing_pieces')
def operation(case,title,roles,refs,answers,*,phases=(),clauses=(),flows=(),extra=None):
    refs=[evidence(x) if x in NOTES else x for x in refs]
    quantity_refs=[o['observation_id'] for o in NEW if o['observation_id'] in refs and o.get('amount') is not None]
    row=dict(operation_id=case,title=title,source_cutoff=ASOF,roles=roles,evidence=refs,amount_references=quantity_refs,
        phases=list(phases),contract_features=list(clauses),cash_or_resource_paths=list(flows),
        closure_state='documented_contract_segments;economic_cycle_or_full_loss_waterfall_not_established',
        no_global_sum=True,questions=[dict(question=q,state=state,answer=answer,**({'gap':gap} if gap else {}))
            for q,(state,answer,gap) in zip(QUESTIONS,answers)])
    if extra:row.update(extra)
    OPERATIONS.append(row)
    for oid in quantity_refs:
        MEASURES.append(dict(operation_id=case,observation_id=oid))

def answers(entities,asset,money,payer,conditions,losses,calendar,gaps):
    return [('partial',entities,gaps[0]),('documented',asset,None),('partial',money,gaps[1]),('partial',payer,gaps[2]),
            ('partial',conditions,gaps[3]),('partial',losses,gaps[4]),('partial',calendar,gaps[5]),('documented','Pièces et lacunes recensées dans le périmètre explicite de cette opération.',None)]

# 1. Existing contract bundles, using the previously preserved amounts.
OA=legal('OpenAI OpCo, LLC','cerebras_loan_named_legal_parties_and_MRA',jurisdiction='DE')
CB=legal('Cerebras Systems Inc.','cerebras_loan_named_legal_parties_and_MRA',jurisdiction='DE')
CB_REVENUE='cf94d1eafccc932992e129d6f453bb97a081c976f6e2af50eed20ce73a0d7f5b'
CB_LOAN='eb5f30716782e81ebba368862c428f3d066c395c838568488f819bf37a4e9fb1'
CB_OUT='ec75b90973927c21717fb50ad1afcde42d68e33498f841413e701c11d4523619'
CB_NONCASH='a8cdce81399b0fd60118df41049e11553d0de74f4cc92460bebc1f62da9e62a3'
CB_WARRANT='1e638688de886bc0ffc49303319ecc10937833e5cf64458c5aa68919ab5aaa3f'
edge('CEREBRAS_OPENAI',CB_LOAN,OA,CB,'financing','loan_or_facility',amount=True,replaces='f187effcea1229a80d7ea63e6fb018737ebf884b1c3edff6c2328234f616ec0d',proof=['cerebras_loan_named_legal_parties_and_MRA'])
edge('CEREBRAS_OPENAI',CB_REVENUE,OA,CB,'commercial','revenue_recognized',amount=True,replaces='892f9a71f0b7aec6350d98654a067c497d8cf55327c50429b4e7a92a96f6a26e',proof=['cerebras_contractual_bundle_and_named_revenue_binding'])
edge('CEREBRAS_OPENAI',CB_WARRANT,CB,OA,'customer_consideration','equity_or_warrants_to_customer',amount=True,proof=['cerebras_contractual_bundle_and_named_revenue_binding'])
operation('CEREBRAS_OPENAI','Cerebras–OpenAI : prêt client, services et warrants',
 [role('OpenAI OpCo, LLC','client_et_prêteur',eid=OA),role('Cerebras Systems Inc.','fournisseur_et_emprunteur',eid=CB)],
 list(read(B/'case_evidence.json')['CEREBRAS_OPENAI'])+[CB_LOAN,CB_REVENUE,CB_OUT,CB_NONCASH,CB_WARRANT],
 answers('Deux parties juridiques nommées dans le prêt et le MRA.','Services de calcul, logiciels et fabrication matérielle financés par le prêt affecté.',
 'Prêt reçu 1,004571 Md$ ; encours 918,244 M$ à juin ; remboursement non monétaire 86,327 M$ ; revenu OpenAI 74,4 M$ au semestre.',
 'OpenAI est client et prêteur. Les recettes propres du laboratoire ne sont pas ventilées publiquement.',
 'Utilisation via lockbox, remboursements possibles par services et transferts autorisés ; intérêts pouvant être réputés payés.',
 'Warrants et prêt créent des obligations différentes ; récupération et pertes finales ne sont pas publiées.',
 'Prêt reçu en janvier 2026 ; données au 30 juin ; échéance contractuelle du prêt fin 2032.',
 ['Contrôle/consolidation de toutes les sociétés OpenAI non établi.','Ventilation des crédits non monétaires et paiements futurs incomplète.',
  'Origine ultime de la trésorerie OpenAI non publiée.','MRA complet et certains paramètres expurgés.',
  'Valeur récupérable et priorité des autres créanciers non reconstituées.','Échéancier détaillé des services/remboursements absent.']),
 phases=[dict(event='loan_signature',date='2026-01-05'),dict(event='cash_receipt',month='2026-01'),dict(event='reported_snapshot',date='2026-06-30'),dict(event='contract_maturity',date='2032-12-31')],
 flows=[dict(provider=OA,receiver=CB,kind='cash_loan',evidence=CB_LOAN),dict(provider=CB,receiver=OA,kind='services_or_permitted_noncash_repayment',evidence=CB_NONCASH),dict(provider=CB,receiver=OA,kind='customer_warrants_noncash',evidence=CB_WARRANT)])
MEASURES += [dict(operation_id='CEREBRAS_OPENAI',observation_id=CB_REVENUE,measure='named_customer_revenue',counterparty_id=OA),
             dict(operation_id='CEREBRAS_OPENAI',observation_id=CB_LOAN),dict(operation_id='CEREBRAS_OPENAI',observation_id=CB_OUT),dict(operation_id='CEREBRAS_OPENAI',observation_id=CB_NONCASH),dict(operation_id='CEREBRAS_OPENAI',observation_id=CB_WARRANT)]
DERIVED=[dict(operation_id='CEREBRAS_OPENAI',quantity='named_customer_revenue_share_H1_not_funding_causality',counterparty_id=OA,
              numerator_observation_id=CB_REVENUE,denominator_observation_id=evidence('cerebras_H1_total_revenue_denominator'))]

AHL=legal('Athene Holding Ltd.','whco_named_broadcom_anthropic_purchase_and_guarantee')
WHCO=legal('WarehouseCo Intermediate Holdings LP','whco_named_broadcom_anthropic_purchase_and_guarantee')
AVGO=legal('Broadcom Inc.','whco_named_broadcom_anthropic_purchase_and_guarantee')
ANTH=legal('Anthropic PBC','nscale_anthropic_legal_provider',jurisdiction='DE')
edge('WHCO_CAPITAL_SOLUTION','whco_named_broadcom_anthropic_purchase_and_guarantee',AHL,WHCO,'credit_support','guarantee')
edge('WHCO_CAPITAL_SOLUTION','whco_named_broadcom_anthropic_purchase_and_guarantee',WHCO,AVGO,'commercial','purchase_commitment')
wh_refs=read(B/'case_evidence.json')['WHCO_CAPITAL_SOLUTION']+['2a76673619f299b2730a1dee5ed92be6beb77e3aeb640bb407a885aadecdc9ad','5e42dd582c83281b0ff7eeea3825093d4c980e479605a79e15d19d81e68c9e80','f28211fefb7c99d65f79498e1311cdba0f2e7463ade1d226aab39ced77f4f9f3']
operation('WHCO_CAPITAL_SOLUTION','WHCO–Broadcom–Anthropic : achats, baux et soutien Athene',
 [role('WarehouseCo Intermediate Holdings LP','obligé_à_acheter',eid=WHCO),role('Athene Holding Ltd.','garant_limité',eid=AHL),
  role('Broadcom Inc.','fournisseur_et_soutien_de_baux',eid=AVGO),role('Anthropic PBC','bénéficiaire_de_capacité_nommé',eid=ANTH),
  role('Tiers remboursant Athene','contre_garant',unknown='Identité et indépendance du tiers non publiées.')],wh_refs,
 answers('Athene nomme WHCO, Broadcom et Anthropic ; Apollo gère le fonds.', 'Infrastructure de calcul et racks à accélérateurs spécifiques.',
 '35 Md$ décrit la solution de capital ; 15 % porte sur l’obligation d’achat encore en cours ; plafond Broadcom de 29 Md$ à plein déploiement.',
 'Anthropic est bénéficiaire nommé de capacité ; les personnes signant chaque bail ne sont pas publiées dans ces notes.',
 'Défaut d’achat WHCO et défaut de bail client déclenchent des garanties sur des bases différentes.',
 'Recours Athene sur un tiers à hauteur de 35 % de ses paiements ; récupération des racks pour Broadcom.',
 'Déploiement à partir de mi-2026 ; obligation d’achat attendue satisfaite au plus tard en 2028 ; baux Broadcom de cinq ans.',
 ['Véhicules, prêteurs retenus et locataires juridiques incomplets.','Encours précis par obligation et affectation des financements manquants.',
  'Payeurs juridiques des baux non identifiés.','Contrats de soutien complets non collectés dans les pièces ouvertes.',
  'Les 15 % achat et 85 % bail ne prouvent pas une couverture commune de 100 %.','Calendrier des décaissements et extinction des garanties incomplet.']),
      clauses=[dict(kind='purchase_support_percentage',value='15',unit='percent'),dict(kind='reimbursement_percentage_of_paid_guarantee',value='35',unit='percent'),dict(kind='Broadcom_lease_support_formula',description='85 % du solde de soutien de bail, diminué de la valeur de cession des racks ; attribution précise à WHCO non confirmée.')])
for oid in ('2a76673619f299b2730a1dee5ed92be6beb77e3aeb640bb407a885aadecdc9ad','5e42dd582c83281b0ff7eeea3825093d4c980e479605a79e15d19d81e68c9e80','f28211fefb7c99d65f79498e1311cdba0f2e7463ade1d226aab39ced77f4f9f3'):
    MEASURES.append(dict(operation_id='WHCO_CAPITAL_SOLUTION',observation_id=oid))

NV=legal('NVIDIA Corporation','732e4b6c2c269e416fbb5d6f02755e08dd2b304fca94e8b0974eb5f9b08b4a7a');CW=legal('CoreWeave, Inc.','732e4b6c2c269e416fbb5d6f02755e08dd2b304fca94e8b0974eb5f9b08b4a7a')
CW_EQ='dae661544725ab2791bc06918b06add2cf2c4b34705d560ce7d639b8759a64aa';CW_PAY='db38ace62d06bdcb55c51c9a0af3d7c01fa90e31a5b12035dbb30ce7fc05f833';CW_CAP='732e4b6c2c269e416fbb5d6f02755e08dd2b304fca94e8b0974eb5f9b08b4a7a'
edge('NVIDIA_CRWV',CW_EQ,NV,CW,'financing','equity_primary',amount=True)
edge('NVIDIA_CRWV',CW_PAY,NV,CW,'commercial','purchase',amount=True)
edge('NVIDIA_CRWV',CW_CAP,NV,CW,'commercial','purchase_commitment',replaces='d311556f39a2859f9a7dc7be8aeb7db762b87df817e04b250f6c4c2c77cd5d67')
operation('NVIDIA_CRWV','Nvidia–CoreWeave : capital, paiements de services et capacité résiduelle',
 [role('NVIDIA Corporation','investisseur_client_et_fournisseur',eid=NV),role('CoreWeave, Inc.','émetteur_fournisseur_et_acheteur',eid=CW)],
 [CW_EQ,CW_PAY,CW_CAP,'cab90b26d8dcc112b02a4ca780288418adef1529621ded240eeb1afec3160e6b','c19dab61da4fccc06a7e2a627a1700e8c4b90e12b94370f2227de00ad81d1936'],
 answers('Deux groupes cotés identifiés ; intégrateurs et acheteurs finaux restent distincts.', 'Capacité de calcul et matériel Nvidia, avec relations commerciales dans les deux sens.',
 '2 Md$ de souscription primaire payée en janvier ; 59,6 M$ de paiements de services au T1 ; 6,3 Md$ est la valeur initiale de l’arrangement de capacité, sans preuve d’une somme payée.',
 'Nvidia peut acheter la capacité résiduelle non vendue ; des tiers achètent aussi de la capacité.',
 'Livraison, disponibilité du service et résiliation conditionnent les obligations.',
 'Nvidia porte capital et certaines obligations d’achat ; prêteurs et valeurs récupérables ne sont pas attribués ici.',
 'Souscription 23 janvier 2026 ; paiements T1 ; mécanisme de capacité jusqu’au 13 avril 2032.',
 ['Achats via intégrateurs et contrats de chaque client non raccordés.','Valeur Nvidia des achats de matériel et capacité résiduelle effectivement utilisée inconnues.',
  'Répartition de tous les paiements finaux entre tiers et Nvidia incomplète.','Ordres et paramètres expurgés restent nécessaires.',
  'Recours, collatéraux et pertes finales par véhicule non reconstitués.','Budgets de livraison et renouvellement détaillés inconnus.']),
 phases=[dict(event='primary_equity_paid',date='2026-01-23'),dict(event='service_payments_period_end',date='2026-03-31'),dict(event='residual_capacity_contract_end',date='2032-04-13')],
 extra=dict(legacy_edge_correction='La valeur initiale de 6,3 Md$ devient une relation commerciale conditionnelle ; l’ancienne arête de soutien monétaire est marquée remplacée dans la vue effective.'))
for oid in (CW_EQ,CW_PAY,CW_CAP):MEASURES.append(dict(operation_id='NVIDIA_CRWV',observation_id=oid))

GOOGLE=legal('Google LLC','hut_river_google_lease_support_not_bond_guarantee')
WULF=legal('TeraWulf Inc.','wulf_named_fluidstack_google_lease_backstop')
FSI=legal('Fluidstack USA I Inc.','wulf_named_fluidstack_google_lease_backstop')
edge('TERAWULF_FLUIDSTACK','wulf_named_fluidstack_google_lease_backstop',GOOGLE,FSI,'credit_support','backstop')
edge('TERAWULF_FLUIDSTACK','wulf_named_fluidstack_google_lease_backstop',FSI,WULF,'commercial','capacity_lease')
operation('TERAWULF_FLUIDSTACK','TeraWulf–Fluidstack USA I–Google : protections avant et après commencement',
 [role('TeraWulf Inc.','sponsor_et_bailleur_déclarant',eid=WULF),role('Fluidstack USA I Inc.','locataire',eid=FSI),role('Google LLC','soutien_des_obligations_de_bail',eid=GOOGLE),role('Porteurs des notes et agent de sûreté','financeurs',unknown='Allocations finales des porteurs non recensées.')],
 read(B/'case_evidence.json')['TERAWULF_FLUIDSTACK'],
 answers('Le locataire USA I et Google sont nommés ; société propriétaire de chaque bâtiment à préciser.', 'Bâtiments HPC de Lake Mariner et raccordement électrique.',
 'Notes de 3,2 Md$ mentionnées dans l’accord de nantissement ; montant par garantie de bail non établi ici.',
 'Fluidstack paie les loyers ; Google peut payer la terminaison ou reprendre le bail après déclenchement.',
 'Soutien effectif au commencement de chaque bail ; nantissement des warrants avant ce moment.',
 'Garanties de bail, warrants nantis et dettes du sponsor sont des protections différentes.',
 'Une location partiellement commencée à juin ; autres mises en service prévues fin 2026/début 2027.',
 ['Bailleurs de chaque bâtiment et contrôle de toutes les filiales non établis.','Plafonds effectifs et comptes de réserve par bâtiment manquants.',
  'Client ultime et origine des recettes Fluidstack non attribués.','Paramètres de terminaison et accords de nantissement complets à rapprocher.',
  'Rang exact de toutes les sûretés et droits en difficulté incomplet.','Dates effectives et flux de chaque bâtiment non publiés.']),
 clauses=[dict(kind='backstop_effective_date',description='Commencement du bail correspondant.'),dict(kind='precommencement_protection',description='Warrants Google nantis au bénéfice des financeurs de construction.')])

# 2. SB Energy: trace one paid investment through the parent, then keep future
# subscription, contingent protection and prospective facilities separate.
SB=legal('SB Energy, Inc.','sb_energy_cash_forward_received_and_contributed')
EG=legal('Energy Global, LP','sb_energy_cash_forward_received_and_contributed')
OINFRA=legal('OpenAI Infra Holdings, LLC','sb_openai_warrants_issued_total')
edge('SB_PORTS','sb_energy_additional_nvidia_subscription_conditional',NV,SB,'financing','equity_primary')
sbrefs=read(B/'case_evidence.json')['SB_PORTS']
operation('SB_PORTS','SB Energy–Energy Global–OpenAI–Nvidia : PORTS et financement de la société',
 [role('SB Energy, Inc.','émetteur_et_groupe_de_développement',eid=SB),role('Energy Global, LP','receveur_du_prépaiement_et_apporteur',eid=EG),role('NVIDIA Corporation','investisseur_et_garant_conditionnel',eid=NV),
  role('OpenAI Infra Holdings, LLC','bénéficiaire_des_warrants',eid=OINFRA),role('Locataires et bailleurs PORTS','parties_aux_baux',unknown='Noms propres expurgés ou laissés en blanc dans les formulaires.')],sbrefs,
 answers('CIK SB Energy et Energy Global identifiés ; OpenAI Infra nommé dans le warrant, mais certaines parties aux baux restent expurgées.', 'PORTS-Pike : centres de données, électricité et transmission.',
 '1,5 Md$ payé le 17 août à Energy Global puis apporté à la société ; 1,5 Md$ supplémentaire conditionné à l’IPO ; plafond de garantie 105 Md$.',
 'Affiliés OpenAI locataires ; Nvidia peut reprendre certains baux après déclenchement.',
 'Commencement/RFS, défaut monétaire non remédié ou insolvabilité, notification, réserves, options et libération.',
 'Réserves, assurance et recours au parent du locataire précèdent ou réduisent certains paiements ; formule et paramètres expurgés.',
 'Cash reçu 17 août ; engagements futurs liés à IPO et mise en service ; échéancier des paiements de garantie inconnu.',
 ['Noms du locataire, bailleur et parent garant de chaque phase manquants.','Allocation du cash à PORTS et solde disponible après refinancement/remboursements non établis.',
  'Origine des recettes OpenAI et opérateur électrique définitif non établis.','Formule de perte, taux d’actualisation et paramètres RFS expurgés.',
  'Montants des réserves, indépendance des recours et valeur des actifs inconnus.','Dates de mise en service et montants d’appels simultanés non calculables.']),
 phases=[dict(event='cash_forward_paid_and_contributed',date='2026-08-17'),dict(event='IPO_subscription',date=None,condition='IPO closing'),dict(event='guarantee_effectiveness',date=None,condition='Lease commencement and RFS provisions')],
 flows=[dict(provider=NV,receiver=EG,kind='cash_prepaid_forward',amount_reference=evidence('sb_energy_cash_forward_received_and_contributed'),economic_flow_id='SB_NVIDIA_1_5BN_PAID'),
        dict(provider=EG,receiver=SB,kind='same_cash_contribution',amount_reference=evidence('sb_energy_cash_forward_received_and_contributed'),economic_flow_id='SB_NVIDIA_1_5BN_PAID')],
 clauses=[dict(kind='legal_receipt_vs_equity_settlement',description='Paiement confirmé ; règlement en titres et classement comptable encore à préciser.'),dict(kind='optional_guaranty_scope',description='4,25 GW initiaux ; extension 3,78 GW facultative pour Nvidia.')])

# 3. Nscale and Ionic: the lessee and GPU borrower are separate people.
NS=legal('Nscale Limited','nscale_ward_legal_roles',jurisdiction='GB')
WC_B=legal('Nscale Ward County Borrower SPV, LLC','nscale_ward_legal_roles')
NC_B=legal('Nscale NC Borrower SPV, LLC','nscale_north_carolina_signed_gpu_facility')
WC_T=legal('Nscale Ward County LLC','ionic_named_nscale_tenant_and_actual_rent_start')
DFS_ID=legal('Dell Financial Services L.L.C.','nscale_dfs_executed_schedule_rent')
MCC=legal('Nscale GPU MCC B1.1 LLC','nscale_anthropic_legal_provider')
edge('NSCALE','nscale_dfs_executed_schedule_rent',DFS_ID,NS,'financing','lease_financing')
edge('NSCALE','nscale_anthropic_legal_provider',ANTH,MCC,'commercial','purchase_commitment')
nsrefs=read(B/'case_evidence.json')['NSCALE']
operation('NSCALE','Nscale : commandes, matériel, Dell et prêts par site',
 [role('Nscale Limited','holding_déclarante',eid=NS),role('Nscale Ward County Borrower SPV, LLC','emprunteur_GPU_Ward',eid=WC_B),role('Nscale NC Borrower SPV, LLC','emprunteur_GPU_NC',eid=NC_B),role('Nscale GPU MCC B1.1 LLC','fournisseur_Anthropic',eid=MCC),role('Anthropic PBC','client',eid=ANTH),role('Dell Financial Services L.L.C.','financeur_d’équipements',eid=DFS_ID),role('Microsoft, plusieurs contrats','clients',unknown='Le formulaire déposé nomme Microsoft Ireland Operations Limited ; index et corps divergent, sans allocation de 43,8 Md$ à une personne unique.')],nsrefs,
 answers('Holding, SPV GPU et un fournisseur Anthropic nommés ; index Microsoft/Anthropic et corps des formulaires diffèrent.', 'GPU, équipements, sites et capacités de calcul dans plusieurs pays.',
 'Commandes conditionnelles 43,8 et 44,6 Md$ ; rent DFS 2,54 Md$ ; engagements GPU Ward 1,85 Md$ et NC 1,2 Md$ ; cash juin hors restreint 1,4784 Md$.',
 'Microsoft et Anthropic selon contrats ; aucun paiement Anthropic avant acceptation écrite.',
 'Financement qualifiant à obtenir, résiliation au longstop expurgé, livraison/acceptation, disponibilité et crédits de service.',
 'Prêt Ward : seuil contractuel DSCR 1,05 ; cash trap 1,10 ; equity cure avec suspension des crédits et règles de vente/remboursement.',
 'Achats non livrés 24 Md$ à juin ; prêt NC décembre 2031, Ward février 2033 ; vente Nvidia prévue novembre 2026.',
 ['Allocations et identités de tous les contrats Microsoft et quatre fournisseurs Anthropic incomplètes.',
  'Soldes effectivement tirés, affectation des 24 Md$ et disponibilité par SPV inconnus.',
  'Direct agreements et personnes signant tous les contrats non collectés.',
  'Dates, prix, critères d’acceptation, SLA et schedules expurgés/omis.',
  'Recours parent limité et sûretés détaillées à compléter avec annexes omises.',
  'Longstop exact et budgets de cash par tranche manquants.']),
 clauses=[dict(kind='financial_covenant',metric='Historical DSCR',threshold='1.05',source=evidence('nscale_ward_financial_covenant'),current_value=None),dict(kind='cash_trap',metric='Historical DSCR',threshold='1.10',source=evidence('nscale_ward_cash_trap_threshold'),current_value=None),dict(kind='financing_status_Anthropic',state='no_binding_commitment_at_prospectus',source=evidence('nscale_anthropic_binding_finance_not_obtained'))])
IO_ID=legal('Ionic Digital Inc.','ionic_named_nscale_tenant_and_actual_rent_start')
edge('IONIC_WARD','ionic_nvidia_first_five_year_guarantee_cap',NV,WC_T,'credit_support','guarantee',amount=True,proof=['ionic_named_nscale_tenant_and_actual_rent_start'])
edge('IONIC_WARD','ionic_named_nscale_tenant_and_actual_rent_start',WC_T,IO_ID,'commercial','capacity_lease')
operation('IONIC_WARD','Ionic–Nscale Ward County : loyers, garantie Nvidia puis parent Nscale',
 [role('Ionic Digital Inc.','bailleur',eid=IO_ID),role('Nscale Ward County LLC','locataire',eid=WC_T),role('NVIDIA Corporation','garant_années_1_à_5',eid=NV),role('Parent Nscale','garant_à_partir_de_l’année_6',unknown='Personne garantissant les années suivantes non nommée dans cette clause.'),role('Client principal','repreneur_possible',unknown='L’identité et toutes les obligations de reprise ne sont pas établies par cette clause.')],read(B/'case_evidence.json')['IONIC_WARD'],
 answers('Ionic et locataire Ward County nommés ; locataire distinct du Borrower SPV de dette GPU.', 'Site alimenté, propriété immobilière et capacité électrique ; pas la valeur de revente de tous les GPU.',
 'Nvidia couvre jusqu’à 860,3 M$ de loyers sur cinq années ; cash Ionic 415,738 M$ à juin ; net financement H1 400 M$.',
 'Nscale locataire ; parent reprend la garantie dès année 6 ; client principal peut reprendre le bail sous conditions.',
 'Défaut/insolvabilité, dates de bail et disponibilité électrique ; expansion 89 MW conditionnelle.',
 'Le garant et sa qualité changent avant la fin du bail ; aucun appel ni couverture intégrale de dette GPU démontrés.',
 'Premier paiement novembre 2025 ; loyers fixes commencés août 2026 ; passage du garant en sixième année.',
 ['Nom juridique du parent garant et accord direct de reprise incomplets.','Solde garanti actuel et relation aux agrégats Nvidia non réconciliés.',
  'Paiements du client principal et obligations reprises non ventilés.','Garanties signées complètes, montants et effets des extensions à obtenir.',
  'Recours et rang après changement de garant non établis.','Calendrier exact des cinq/sixième années et des extensions non publié.']),
 phases=[dict(event='first_lease_payment',month='2025-11'),dict(event='monthly_fixed_rent_commenced',month='2026-08'),dict(event='guarantor_transition',lease_year=6)],
 clauses=[dict(kind='Nvidia_coverage_window',first_lease_year=1,last_lease_year=5,cap_observation=evidence('ionic_nvidia_first_five_year_guarantee_cap')),dict(kind='anchor_stepin_option',deadline_days=30,trigger='tenant_insolvency')])

# 4. Hut8: preserve separate debtors and distinct repayment calendars.
HUT_ID=legal('Hut 8 Corp.','hut_river_google_lease_support_not_bond_guarantee')
FSIV=legal('Fluidstack USA IV Inc.','hut_river_google_lease_support_not_bond_guarantee')
RIVER=legal('Hut 8 DC LLC','hut_river_bend_principal_outstanding');BEACON=legal('Beacon Point DC LLC','hut_beacon_point_principal_outstanding')
edge('HUT_RIVER','hut_river_google_lease_support_not_bond_guarantee',GOOGLE,FSIV,'credit_support','backstop')
edge('HUT_RIVER','hut_river_google_lease_support_not_bond_guarantee',FSIV,RIVER,'commercial','capacity_lease')
for case,title,borrower,principal,first_principal,refs in [
 ('HUT_RIVER','Hut 8 : River Bend',RIVER,'3,25 Md$','2028-05-15',read(B/'case_evidence.json')['HUT_RIVER']),
 ('HUT_BEACON','Hut 8 : Beacon Point',BEACON,'4,25 Md$','2030-05-30',read(B/'case_evidence.json')['HUT_BEACON'])]:
    operation(case,title,[role('Hut 8 Corp.','sponsor',eid=HUT_ID),role('Hut 8 DC LLC' if case=='HUT_RIVER' else 'Beacon Point DC LLC','émetteur_des_notes',eid=borrower),role('Porteurs de notes','créanciers',unknown='Identités et allocations finales non recensées.')]+([role('Fluidstack USA IV Inc.','locataire',eid=FSIV),role('Google LLC','soutien_du_bail',eid=GOOGLE)] if case=='HUT_RIVER' else []),refs,
      answers('Émetteur propre à chaque projet et société sponsor nommés.','Centre de données, sous-station, actifs et comptes du véhicule.',
      principal+' de principal émis et restant à juin ; dette différente des comptes restreints et de la valeur comptable nette.',
      'River Bend : loyers Fluidstack USA IV ; Beacon Point : locataire non nommé, décrit comme high-investment-grade.',
      'Dette du SPV, covenants et comptes réservés ; soutien Google du bail River Bend, sans garantie de ses notes.',
      'Créanciers ont des sûretés sur projet/comptes/actions ; aucune garantie générale du sponsor, locataire ou garant de bail pour River Bend.',
      'Premier principal '+first_principal+' ; maturité 2042 ; coupons à partir de novembre 2026.',
      ['Porteurs et rôle du client de Beacon Point non recensés.','Répartition des réserves et besoins de chantier par SPV non reconstituée.',
       'Modalités du payeur Beacon Point à confirmer ; revenus des clients ultimes inconnus.',
       'Annexes de bail/backstop et accords de reprise manquants.','Waterfall intégrale et recours de chaque créancier à compléter.',
       'Budget de construction et encaissements trimestriels détaillés inconnus.']),
      phases=[dict(event='first_principal_payment',date=first_principal),dict(event='final_maturity',year=2042)],
      clauses=[dict(kind='cash_restriction',description='Produit de dette réservé à construction, service de dette et usages contractuels.'),dict(kind='parent_or_tenant_bond_guarantee',present=False,scope='Separate explicit issuer statements for each vehicle.')])

# 5. Hyperion: financial amounts are attributed to Meta’s published Louisiana
# venture; no legal allocation of the whole balance to Beignet is invented.
META_ID=legal('Meta Platforms, Inc.','meta_louisiana_nonconsolidation_reason')
PIMCO=legal('PIMCO Extended Duration Fund','nport_beignet_held_principal');BEIGNET=legal('Beignet Investor LLC','nport_beignet_held_principal')
edge('HYPERION','nport_beignet_held_principal',PIMCO,BEIGNET,'financing','loan_or_facility',amount=True)
operation('HYPERION','Meta–Hyperion–Beignet : VIE, garantie résiduelle et une position PIMCO',
 [role('Meta Platforms, Inc.','investisseur_locataire_et_garant',eid=META_ID),role('Beignet Investor LLC','émetteur_des_obligations_identifiées',eid=BEIGNET),role('PIMCO Extended Duration Fund','porteur_identifié',eid=PIMCO),role('Fonds Blue Owl et véhicules de projet','investisseurs_et_propriétaires',unknown='Leur identification juridique et le raccordement complet à Beignet ne sont pas établis par les pièces SEC ouvertes.')],read(B/'case_evidence.json')['HYPERION'],
 answers('Meta, Beignet et série PIMCO identifiés ; lien juridique complet de Beignet à la VIE à confirmer.', 'Campus Louisiana/Hyperion, bâtiments et infrastructure de longue durée ; holding et propriétaire d’actifs distincts.',
 'Meta publie 46,03 Md$ d’exposition maximale composée, 28 Md$ de seuil RVG initial, 12,31 Md$ de baux et 2,92 Md$ de participation ; PIMCO détient 1,517 M$ nominal.',
 'Engagements de Meta envers la VIE ; distributions du projet vers la holding obligataire à reconstituer.',
 'Non-renouvellement/résiliation et valeur à la date considérée pour RVG ; clauses complètes non collectées.',
 'Non-consolidation comptable n’efface pas baux/RVG ; la dette Beignet ne s’ajoute pas à l’exposition composée Meta.',
 'Baux prévus en 2029, initialement quatre ans, options jusqu’à vingt ; obligation PIMCO échéance mai 2049.',
 ['JVCo, bailleur, locataire et fonds Blue Owl réels non confirmés par contrats SEC ouverts.',
  '27,3 Md$ cité par S&P : analyse d’agence non admise comme dette SEC directement constatée.',
  'Waterfall de distribution et accords directs non collectés.','Garantie RVG complète, schedules et indenture private placement manquants.',
  'Rang des créanciers de holding et sûretés directes à confirmer.','Amortissement détaillé et articulation fin de garantie/maturité inconnus.']),
 phases=[dict(event='reported_lease_commencement',year=2029),dict(event='initial_lease_term',years=4),dict(event='renewal_options_total',years=20),dict(event='identified_bond_maturity',date='2049-05-30')],
 clauses=[dict(kind='Meta_reporting_scope',state='unconsolidated_VIE'),dict(kind='bond_holding_scope',CUSIP='076912AA2',series='S000013233',reported_not_default=True,reported_not_PIK=True),dict(kind='agency_legal_chain',source='beignet_sp_search_excerpt',qualified_contract=False,holding='Beignet Investor LLC',asset_owner='Laidley LLC',Meta_member='Iris Crossing LLC',Meta_tenant='Pelican Leap LLC',description='Noms publiés dans un extrait indexé S&P ; contrats et chaîne de contrôle non vérifiés.')],
 extra=dict(legal_chain_state='SEC financial quantities plus issuer IR project attribution and NPORT holding; no blanket allocation to Beignet or Blue Owl manager'))

# 6. Lambda: agency and issuer statements stay explicitly outside ABCD numbers.
LAMBDA=legal('Lambda, Inc.','lambda_closed_delayed_draw_facility_external')
operation('LAMBDA_COMPUTE_I','Lambda Compute I : prêts différés et contrats clients',
 [role('Lambda, Inc.','sponsor_déclarant',eid=LAMBDA),role('Lambda Compute I LLC','emprunteur_nommé_par_l’agence',unknown='Contrat, CIK et contrôle juridique complet non confirmés dans les sources qualifiées.'),role('Deux offtakers','payeurs',unknown='Noms non publiés dans ces déclarations.'),role('Assureurs et investisseurs obligataires','financeurs',unknown='Identités et allocations détenues non publiées.')],read(B/'case_evidence.json')['LAMBDA_COMPUTE_I'],
 answers('Lambda et emprunteur nommés dans des sources externes ; parties contractuelles non vérifiées par pièces ABCD.', 'Serveurs GPU GB300/VR200 et contrats de capacité à Seattle, Kansas City et Dallas selon l’agence.',
 'Facilité annoncée 1,008 Md$, à tirages différés ; montant effectivement tiré inconnu.',
 'Deux offtakers de qualité investment grade selon agence, non nommés.',
 'Acceptation des GPU, achèvement des sites, SLA et conditions de tirage ; historique technologique court.',
 'Sûretés sur matériels et cash-flows selon issuer/agence ; réserve moins forte que la pratique selon DBRS ; équité sponsor en construction.',
 'Amortissement après stabilisation des tranches ; maturité annoncée 30 mai 2033, taux fixe annoncé 6,78 %.',
 ['Source externe et contrats sous-jacents non publiés dans les recherches bornées.',
  'Tirages, encours et réserves non publiés ; chiffres externes exclus des mesures core.',
  'Identité des clients et clauses de paiement non vérifiées.','Contrats de prêt, SLA, offtake et accords directs absents.',
  'Recours, rang, collatéral et prix de récupération non vérifiés dans contrats.',
  'Calendrier précis de tranche, réserve et remboursements non disponible.']),
 phases=[dict(event='facility_closing_announced',date='2026-10-01'),dict(event='amortization_start',condition='Each GPU tranche stabilization'),dict(event='final_maturity_reported',date='2033-05-30')],
 extra=dict(reported_unadmitted_quantities=[dict(source_key='lambda_issuer',quantity='facility_commitment',value='1008000000',currency='USD',admitted_to_core=False),dict(source_key='lambda_issuer',quantity='fixed_coupon_percent',value='6.78',admitted_to_core=False),dict(source_key='lambda_dbrs',quantity='agency_DSCR_case',value='1.20',admitted_to_core=False,current_value_not_reported=True)]))

# Personally assessed gap types; a bounded dossier is not an exhaustive search.
GAP_STATES={
 'CEREBRAS_OPENAI':('partial','partial','not_collected','redacted','not_collected','partial'),
 'WHCO_CAPITAL_SOLUTION':('identity_unresolved','amount_unattributable','identity_unresolved','not_collected','partial','partial'),
 'NVIDIA_CRWV':('partial','partial','partial','redacted','not_collected','partial'),
 'TERAWULF_FLUIDSTACK':('identity_unresolved','amount_unattributable','identity_unresolved','partial','not_collected','partial'),
 'SB_PORTS':('redacted','amount_unattributable','identity_unresolved','redacted','partial','partial'),
 'NSCALE':('partial','partial','partial','redacted','partial','partial'),
 'IONIC_WARD':('identity_unresolved','partial','identity_unresolved','not_collected','not_collected','partial'),
 'HUT_RIVER':('partial','partial','partial','partial','partial','partial'),
 'HUT_BEACON':('identity_unresolved','partial','identity_unresolved','not_collected','partial','partial'),
 'HYPERION':('partial','amount_unattributable','not_collected','not_collected','partial','partial'),
 'LAMBDA_COMPUTE_I':('identity_unresolved','amount_unattributable','identity_unresolved','not_collected','not_collected','partial'),
}
for case in OPERATIONS:
    for index,state in zip((0,2,3,4,5,6),GAP_STATES[case['operation_id']]):case['questions'][index]['state']=state

if __name__=='__main__':
    save(B/'entity_decisions.json',ENTITIES);save(B/'edge_decisions.json',EDGES)
    save(B/'measure_decisions.json',MEASURES);save(B/'derived_decisions.json',DERIVED);save(B/'operations.json',OPERATIONS)
    save(B/'negative_search_certificates.json',[])
    print('Manual operation ledger:',len(OPERATIONS),'cases;',len(ENTITIES),'identity versions;',len(EDGES),'edges')
