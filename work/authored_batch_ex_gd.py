from work.authored_helpers import *
for key,end,series,proof in [
 ('64f230f32f894ee6f58c66ac4fb3a12b0248d5d5ff4c9f28da32f069de28fb3e',3761,'5.875%2058 GBP1.25bn','Euroclear/Clearstream financialdepositaries andBNYfinancialnominee'),
 ('26af4bf4df065b0032859d53673b9f987a584eb4d762a4fffb6b2363b24ce908',5036,'6.125%2126 GBP1bn','Euroclear/Clearstream financialdepositaries andBNYfinancialnominee'),
 ('8bdc53e5d5ca05bc1a0dff45b7357e1572c6b20f5c7f714c666633817f9c13b9',4040,'3.700%2029 USD500m certificate','DTCfinancialdepositary andCedeCo registeredfinancialnominee'),
]:
 save(key,[dict(abstention('GLOBAL SECURITY','Complete physical first page personally read. Original global note '+series+'; express '+proof+'. AlphabetIncDE. No autonomousamendment or Item3.03; body financial_parties_only. Beneficialholders unknown; denomination notactualissuerproceeds or aggregateissuance/newcustomerfinancing; noGBPUSDconversion.'),model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=end,locator=f'rawbytes:0:{end}')])
