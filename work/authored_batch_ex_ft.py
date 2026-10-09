from work.authored_helpers import *
for key,end,series in [
    ('c6172f42370347301407cdb79b7f7235803a0c9282e259599486a302d69d642a',4281,'3.650%2031 CAD1.5bn'),
    ('2c677df00e9153a923ec31614990181762bdb5c2f1f80450543e93f2ca91e0c3',4296,'4.000%2033 CAD2bn'),
    ('2419449876a1f73e3aae93b0fcbb6a6632c2c4ce5cc8392833780e1356f0dd34',4282,'4.350%2036 CAD2.25bn'),
]:
    save(key,[dict(abstention('GLOBAL SECURITY',
        'Complete physical first page read. Original Canadian global note '+series+'; express CDS Clearing and Depository ServicesInc financial depositary and registered CDS&Co nominee. No autonomous amendment and no Item3.03. Body financial_parties_only exclusion; actual ultimate beneficial holders unknown, denomination not new aggregate actual primary cash or proceeds, no CAD-to-USD conversion. AlphabetInc DE stated; future maturity and Canadian resale restriction not actual termination.'),
        model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=end,locator=f'rawbytes:0:{end}')])
