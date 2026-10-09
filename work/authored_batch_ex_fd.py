from work.authored_helpers import *
# Each first physical page was served and read before these explicit entries.
for key, end, term in [
('b52b3251470ca2bfca5e17e676e15d3d1be327a69f970c51a9ed994a8f62eb7c',4033,'4.625% due Aug10 2029'),
('6bb8a67b98ff033eef66ea94d76835eb8f525ee78a5f8c55ea15a3397dde0806',4042,'4.875% due Aug15 2031'),
('b6b110b4170d5a8b4aa4f312075590ae8c682dfdab01286050590c02b4ef024a',4036,'5.200% due Aug15 2033')]:
    save(key,[dict(abstention('GLOBAL SECURITY','financial_parties_only: Entire first physical page read. Original new Alphabet global note '+term+', no Item3.03. Cede & Co registered financial nominee and DTC depositary expressly identified, not ultimate beneficial owner proof. 500m form denomination not aggregate actual issuance or cash. Body excluded 11.1.'),model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=end,locator=f'rawbytes:0:{end}')])
