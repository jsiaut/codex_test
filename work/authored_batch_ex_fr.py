from work.authored_helpers import *
for key,series in [
    ('0bb1b6c7ed1cbc7370c7d417be23adb22e7d1db99d08dc526b0c9073c4625ec8','3.200%2030 EUR1.5bn'),
    ('9954d8ab3268109c4ee76a988134ee932af0150219c9ec70bd682ee2670f7b66','3.450%2032 EUR1.75bn'),
    ('964244242a608aa53a92a5a646c402098c2fbccf273006b8ccee512be49f98fa','3.625%2034 EUR1.5bn'),
]:
    save(key,[dict(abstention('GLOBAL SECURITY',
        'Complete physical first page read. Original global note '+series+'; express Euroclear Bank/Clearstream financial depositaries and Bank of New York Depository(Nominees)Limited registered financial nominee of BNY Mellon London. No autonomous amendment and no Item3.03. Body financial_parties_only exclusion; no actual ultimate beneficial holders assumed, no new primary proceeds or actual aggregate cash inferred from global denomination, no EUR-to-USD conversion. AlphabetInc DE stated.'),
        model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=3762,locator='rawbytes:0:3762')])
