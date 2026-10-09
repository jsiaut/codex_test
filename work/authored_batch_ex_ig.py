from work.authored_helpers import *

# Each complete physical header personally read, independent Item8.01 reread.
for key,end,description in [
 ('af44d751e5bb0bcfcefdad40ccf4bbddeb682485354b267c8739c5da71f6d67c',4400,'2027series1bn independent issuance vs500m global-form denomination.'),
 ('5224ca91c5790aa01ba8fc5ed2592c92b98687a0252463f741483e602c4eed32',4387,'2030series2.25bn independent issuance; form alternative500/250m denominations not aggregate or additional funds.'),
 ('21c5ca7340bac920b83524008ea987ba364c2e9ccb5dfaad9fe03bf2719dc03d',4381,'2040series1.25bn independent issuance; alternative500/250m denominations not aggregate or additional funds.')
]:
 save(key,[dict(abstention('GLOBAL SECURITY','Header explicitly financial CedeCo registered payee, BNYTrustNA financial trustee from full same Itemdfcad3f2. '+description+f' No identified outside nonfinancial financing counterparty. Entire body{end}:rawend excluded unread, including any scope reading; no body amount, covenant, link, F4 or entity alias admitted. Original notes and historical2016indenture not actual amendment/default. Sustainability proceeds intended allocation not actual project funding.'),model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=end,locator=f'rawbytes:0:{end}')])
