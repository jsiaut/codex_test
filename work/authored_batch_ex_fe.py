from work.authored_helpers import *
for key, end, term in [
('fafd2e648dd264a8274b22a77b2362972d2801fec20a8456f60210f63212c0bc',4048,'5.450% due Aug15 2036'),
('98e87b7bd8cf2f165adc7b6e373a1dc64b110ceca1b9280dc9e67852add9a910',4040,'6.250% due Aug15 2046'),
('6a5890698d64d2e40a7419b82c9200e41e1e544bf08296a24835bf153b619f4a',4054,'6.375% due Aug15 2056')]:
    save(key,[dict(abstention('GLOBAL SECURITY','financial_parties_only: Entire first physical page personally read. Original new Alphabet global note '+term+', no Item3.03. Cede & Co registered financial nominee and DTC depositary expressly identified, not ultimate beneficial owner proof. 500m form denomination not aggregate actual issuance or cash. Body excluded 11.1.'),model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=end,locator=f'rawbytes:0:{end}')])
