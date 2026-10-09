from work.authored_helpers import *
k='880237b75dddf47bdccb20263d3c23a6ce1d83e36cc484977aaaac2aec6335f7'
rows=[dict(quote='On September 30, 2021, Broadcom Inc. (the “Company”) completed the early settlement',event_date='2021-09-30',stage='settled',model_quantity='notes_exchange_2035_2036_early_settlement',flag_unknown_reason='new_2035_2036_faces_not_disclosed_old_canceled_faces_not_new_cash')]
# Every coupon, maturity, issuer, canceled face and remaining face was chosen
# after reading the whole item; formatting only reconstructs its exact quote.
for coupon,year,issuer,canceled,remaining,series in [
('3.125',2025,'Broadcom Corporation',90528000,494541000,'BRCM_2025'),
('4.700',2025,'Broadcom Inc.',227633000,1019714000,'parent_4_700_2025'),
('3.150',2025,'Broadcom Inc.',517730000,899856000,'parent_3_150_2025'),
('4.250',2026,'Broadcom Inc.',238348000,944488000,'parent_4_250_2026'),
('3.459',2026,'Broadcom Inc.',943002000,752318000,'parent_3_459_2026'),
('3.875',2027,'Broadcom Corporation',890672000,2922282000,'BRCM_2027'),
('4.700',2027,'CA, Inc.',84898000,265102000,'CA_2027'),
('4.110',2028,'Broadcom Inc.',257173000,1965176000,'parent_2028'),
('3.500',2028,'Broadcom Corporation',472973000,777027000,'BRCM_2028'),
('5.000',2030,'Broadcom Inc.',1164086000,1085914000,'parent_5_000_2030'),
('4.750',2029,'Broadcom Inc.',1041999000,1958001000,'parent_2029'),
('4.150',2030,'Broadcom Inc.',70942000,2679058000,'parent_4_150_2030')]:
 for num,suffix,nature in [(canceled,'canceled','old_principal_canceled_in_exchange_not_cash_payment'),(remaining,'remaining','old_principal_outstanding_stock_not_new_funding')]:
  rows.append(money(f'${num:,} aggregate principal amount of {coupon}% Senior Notes due {year}',str(num),'1',issuer,event_date='2021-09-30',period_end='2021-09-30',stage='recognized',amount_qualifier='exact',model_quantity=series+'_old_principal_'+suffix,amount_nature=nature,flag_unknown_reason='issuer_not_cash_payer_old_retired_remaining_new_face_nonadditive_not_as_of2026_stock'))
rows.extend([dict(quote='Broadcom Corporation, a California corporation',counterparty='Broadcom Corporation',counterparty_evidence='named',model_quantity='Broadcom_Corporation_note_issuer_California',flag_unknown_reason='distinct_from_Broadcom_Inc_not_alias_merge'),dict(quote='CA, Inc., a Delaware corporation',counterparty='CA, Inc.',counterparty_evidence='named',model_quantity='CA_Inc_note_issuer_Delaware'),abstention('If the Company fail to satisfy this obligation with respect to a series of the New Notes','Full item: actual early exchange, all12old canceled faces/issuers and12old outstanding faces/issuers, new2035/2036series not faces, original indenture/private classes/interestdates, all optional makewhole/parcall/tax/changeofcontrolput, complete ranking/restrictive/defaultclauses, registrationrights/three dealer managers/Sept30,2026deadline/shelf/conditionalintereststeps/cure/cashinterest and exhibit renvois read. No new face/cash/actual redemption, registration default or invoked penalty; expired date at as_of not proof default. Original new indenture not F4; trustees/managers not funding payers.')])
save(k,rows)
save('0c266d95cd4047b0e5bae88e7a670da2ececa8b55e1a07f56f83a491da4240e2',[dict(quote='its waiver of the Pool 1 Sub-Caps and Pool 2 Sub-Cap',event_date='2021-09-27',model_quantity='exchange_offer_subcaps_waived_caps_upsized',flag_unknown_reason='discretionary_tender_offer_acceptance_limits_not_existing_financial_covenant_waiver_no_automatic_F4'),abstention('its increase in the 2035 Notes Cap, 2036 Notes Cap and New Notes Cap','Full item:Sept27early participation/waivedoffer-subcaps/upsizedoffer-caps/earlysettlement election, pricing/both releases/privateclasses/no-offer, entire forward-looking statement/fullpandemic/customer/supplier/global/trade/debt/people/acquisition/legal/demand/design/manufacturing/software/privacy/tax risk list/finaldisclosure read. No amounts, actual settlement or cash, debt financial-covenant waiver/default/call; offer limits not breached credit covenants. LaterSept30settlement not imported.')])
save('cf04190b8015e54a0f8ce31733e7a97b79cda25f6ebcdd39c176c6621d5d36b4',[abstention('On September 23, 2021, Marvell Technology, Inc. (the “Company”) announced','Full item read:declared0.06per-share futureOct27/recordOct11, furnished release and every future-policy factor. No actual aggregate cash payout, primary financing or distress event.')])
