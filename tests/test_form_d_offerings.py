from secfragility.deepening_form_d import offering_key


def test_amendments_are_one_cumulative_offering_but_other_issuers_and_dates_are_distinct():
    assert offering_key('1','2026-01-01','D','totalAmountSold') == offering_key('1','2026-01-01','DA','totalAmountSold')
    assert offering_key('1','2026-01-01','D','totalAmountSold') != offering_key('2','2026-01-01','D','totalAmountSold')
    assert offering_key('1','2026-01-01','D','totalAmountSold') != offering_key('1','2026-02-01','D','totalAmountSold')


def test_missing_first_sale_date_never_merges_different_offerings():
    assert offering_key('1',None,'D','totalAmountSold') != offering_key('1',None,'DA','totalAmountSold')


def test_quarter_snapshot_ignores_later_amendments_and_next_day_publication():
    import duckdb
    from secfragility.deepening_form_d import make_snapshot
    db=duckdb.connect()
    db.execute('CREATE TABLE facts(entity_id VARCHAR,semantic_key VARCHAR,canonical_concept VARCHAR,knowledge_date DATE,acceptance_datetime TIMESTAMPTZ,accession VARCHAR,value INTEGER)')
    db.executemany('INSERT INTO facts VALUES (?,?,?,?,?,?,?)',[
        ('issuer1','offering1','secFormD:totalAmountSold','2026-03-20','2026-03-20T12:00:00Z','D',100),
        ('issuer1','offering1','secFormD:totalAmountSold','2026-04-20','2026-04-20T12:00:00Z','DA',180),
        ('issuer2','offering2','secFormD:totalAmountSold','2026-04-01','2026-03-31T23:50:00Z','D2',50)])
    make_snapshot(db,'2026-03-31T23:59:59Z')
    assert db.execute('SELECT accession,value FROM form_d_snapshot WHERE offering_version=1').fetchall()==[('D',100)]
    make_snapshot(db,'2026-06-30T23:59:59Z')
    assert set(db.execute('SELECT accession,value FROM form_d_snapshot WHERE offering_version=1').fetchall())=={('DA',180),('D2',50)}
