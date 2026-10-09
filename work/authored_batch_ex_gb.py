from work.authored_helpers import *
import json
from datetime import datetime, timezone

key='c9d59afc458e567fa1f9c7a3be5d0ebfe6067f81c6e8704da7f2510572e7c586'
legal='REGISTRATION RIGHTS AGREEMENT dated as of February 23, 2026 (this “Agreement”) between Advanced Micro Devices, Inc., a Delaware corporation (the “Company”), and Meta Platforms, Inc., a Delaware corporation (the “Investor”).'

with Path('decisions.md').open('a') as f:
    f.write('\nD90 — Amazon/OpenAI EX10.1 du 27 février2026 : la proposition JCA nomme AWS et OpenAI OpCo, mais ne précisait pas les champs payer/receiver alors que le déposant est Amazon.com. Le validateur de lien a donc rejeté cette ligne SEM_CHECK. Rejet immuable à cet as_of, sans nouvelle soumission ni utilisation dérivée de cette proposition. Les huit autres observations admises et les lectures intégrales restent intactes. Ne pas transformer OpCo en alias de Group PBC ni exploiter la proposition rejetée comme preuve de relation commerciale ; seuls des blocs indépendamment admissibles peuvent établir leurs propres relations.\n')
with Path('journal.jsonl').open('a') as f:
    f.write(json.dumps(dict(as_of=json.loads(Path('work/run.json').read_text())['as_of'],timestamp=datetime.now(timezone.utc).isoformat(),event='immutable_semantic_rejection_documented',decision='D90',content_key='a11f1af4fb71dba2c556d94cbd5c616c1d424f4db13d9c3d75477ab299c5bd85',rejected_quantity='AWS_OpenAI_OpCo_named_JCA_commercial_reference',retry=False,final_delivery=False))+'\n')

save(key,[
    dict(quote=legal,linkage_quote=legal,linkage_class='L1',counterparty='Meta Platforms, Inc.',counterparty_evidence='named',payer='Advanced Micro Devices, Inc.',receiver='Meta Platforms, Inc.',model_quantity='AMD_Meta_registration_rights_full_legal_parties',stage='signed',event_date='2026-02-23',flag_unknown_reason='AMD_DE_Meta_DE_separatelegalproof;registrationrights_samewarrant_not_newprimaryfunding_or_commonshareexercise'),
    dict(quote='“RRA Expiration Date” means February 23, 2036.',counterparty='Meta Platforms, Inc.',counterparty_evidence='named',model_quantity='AMD_Meta_registration_rights_conditional_expiry',flag_unknown_reason='6k_earlier_RRAexpiry_orHolderceasesRegistrableSecurities_notactualtermination;3_4_5liabilitysurvives;notwarrantexpiry2031'),
    dict(quote='aggregate gross cash proceeds (without regard to any underwriting discount or commission) of at least $100,000,000',model_quantity='AMD_Meta_registration_demand_holder_resale_threshold',flag_unknown_reason='2b_holdersecondaryresale_demandeligibilitythreshold_notcashAMDreceived_orcommittedprimaryequity;Companyownofferingpossibleallocationpermission_notactualsale'),
    abstention('Signature Page to Registration Rights Agreement','Complete header and both body packets personally read through executedAMDJeanHu/MetaRajSingh signatures. Piggyback/demand/blocktrade rights are future holder resale permissions; no actualregistration,sale,exercise,payment or newfinancialguarantee. 160m warrant underlying references sameFebruary23warrant notadditionalshares. 30m transferminimum and1percentterminationcondition notactualownership. AmendmentEightMPA definition notfullcommercialcontract; ordinary6b amendmentpermission not actualF4. Expense/indemnity allocations do not establish financialguaranteecall oramount. RegistrableSecurities initially includesfutureissuable shares; 2036RRA vs2031warrant distinctdates.')
])
