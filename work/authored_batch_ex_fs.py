from work.authored_helpers import *
for key,series in [
    ('7230ae749e211deb615210660410ccc9485f70020e4369c38148c05161437cf0','4.100%2039 EUR1.75bn'),
    ('feebd845c9b40c22ff00496a9877e5d57fd21c7b1e363f849db67e6504b0e451','4.500%2045 EUR1.25bn'),
    ('c7b5d867453789567d06ec8edf9b858d20ef437a78406901eba4fd56b0c11d2c','4.800%2063 EUR1.25bn'),
]:
    save(key,[dict(abstention('GLOBAL SECURITY',
        'Complete physical first page read. Original global note '+series+'; express Euroclear Bank/Clearstream financial depositaries and Bank of New York Depository(Nominees)Limited registered financial nominee of BNY Mellon London. No autonomous amendment and no Item3.03. Body financial_parties_only exclusion; no actual ultimate beneficial holders assumed, no new primary proceeds or actual aggregate cash inferred from global denomination, no EUR-to-USD conversion. AlphabetInc DE stated.'),
        model_quantity='exhibit_body_excluded_financial_parties_only',raw_byte_start=0,raw_byte_end=3762,locator='rawbytes:0:3762')])
