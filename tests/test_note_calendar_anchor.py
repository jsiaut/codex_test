from secfragility.extension_assembly import note_anchor_map


def test_stock_uses_published_quarter_instead_of_acquisition_context_in_any_order():
    universe={'quarters':[
        {'group_id':'MRVL','period_start':'2021-05-02','period_end':'2021-07-31','quarter_number':2},
        {'group_id':'MRVL','period_start':'2021-04-20','period_end':'2021-07-31','quarter_number':None}]}
    rows=[('MRVL','2021-05-02','2021-07-31','2021-08-27T12:00:00Z'),
          ('MRVL','2021-04-20','2021-07-31','2021-08-27T12:00:00Z')]
    expected={('MRVL','2021-07-31'):('2021-05-02','2021-08-27T12:00:00Z')}
    assert note_anchor_map(universe,rows)==expected
    assert note_anchor_map(universe,list(reversed(rows)))==expected


def test_ambiguous_unnumbered_starts_are_not_assigned_arbitrarily():
    universe={'quarters':[]}
    rows=[('X','2026-04-01','2026-06-30','2026-08-01T12:00:00Z'),
          ('X','2026-04-20','2026-06-30','2026-08-02T12:00:00Z')]
    assert note_anchor_map(universe,rows)=={('X','2026-06-30'):('none','2026-08-01T12:00:00Z')}
