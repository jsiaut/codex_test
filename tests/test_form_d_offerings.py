from secfragility.deepening_form_d import offering_key


def test_amendments_are_one_cumulative_offering_but_other_issuers_and_dates_are_distinct():
    assert offering_key('1','2026-01-01','D','totalAmountSold') == offering_key('1','2026-01-01','DA','totalAmountSold')
    assert offering_key('1','2026-01-01','D','totalAmountSold') != offering_key('2','2026-01-01','D','totalAmountSold')
    assert offering_key('1','2026-01-01','D','totalAmountSold') != offering_key('1','2026-02-01','D','totalAmountSold')


def test_missing_first_sale_date_never_merges_different_offerings():
    assert offering_key('1',None,'D','totalAmountSold') != offering_key('1',None,'DA','totalAmountSold')
