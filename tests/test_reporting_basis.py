from decimal import Decimal
from pathlib import Path
import json
from secfragility.database import create,insert
from secfragility.calculation import prepare_views
from secfragility.quarter_series import prepare,measures
from tests.test_identity_and_guards import fact,instance


def fixture(root,simultaneous=False):
    src=Path(__file__).resolve().parents[1];(root/'work').mkdir()
    for name in ['schema.sql','queries.sql','config.yaml']:(root/name).write_text((src/name).read_text())
    (root/'work/expected_universe.json').write_text(json.dumps({'quarters':[dict(group_id='S',
        period_start='2024-01-01',period_end='2024-12-31',fiscal_year_start='2024-01-01',quarter_number=4)]}))
    db=create(root)
    for i,(currency,value) in enumerate([('RUB','1000000'),('USD','2000000')]):
        date='2025-02-01' if i==0 or simultaneous else '2026-02-01';accepted=date+'T12:00:00Z';doc='d'+str(i)
        insert(db,'documents',dict(document_id=doc,group_id='S',accession=doc,url='https://www.sec.gov/'+doc,
            cache_path=doc,sha256=doc,form='20-F',filing_status='filed',acceptance_datetime=accepted,
            knowledge_date=date,as_of='2026-10-09T00:00:00Z'))
        insert(db,'facts',dict(fact(instance()),fact_id=doc,semantic_key=doc,document_id=doc,accession=doc,
            currency=currency,unit='http://www.xbrl.org/2003/iso4217:'+currency,value=Decimal(value),
            model_quantity='revenue_total',acceptance_datetime=accepted,knowledge_date=date))
    prepare_views(db,root,'2026-10-09T00:00:00Z');prepare(db,root,'2026-10-09T00:00:00Z')
    return db


def test_later_currency_presentation_preserves_historical_publication_snapshot(tmp_path):
    db=fixture(tmp_path)
    assert db.execute('SELECT currency,value FROM quantities_revised').fetchall()==[('USD',Decimal('2000000'))]
    assert db.execute('SELECT currency,value FROM quarter_quantities_as_known').fetchall()==[('RUB',Decimal('1000000'))]
    assert db.execute('SELECT currency,value FROM quarter_quantities_revised').fetchall()==[('USD',Decimal('2000000'))]
    measures(db,'2026-10-09T00:00:00Z')
    assert db.execute("SELECT currency FROM measures WHERE measure='revenue_total' AND view='revised'").fetchall()==[('USD',)]
    assert db.execute('SELECT count(*) FROM facts').fetchone()[0]==2


def test_simultaneous_alternative_bases_abstain_and_keep_original_facts(tmp_path):
    db=fixture(tmp_path,simultaneous=True)
    assert db.execute('SELECT count(*) FROM quantities_revised').fetchone()[0]==0
    assert db.execute('SELECT count(*) FROM quarter_quantities_revised').fetchone()[0]==0
    assert db.execute("SELECT count(*) FROM exclusions WHERE reason='conflicting_reporting_bases'").fetchone()[0]>0
    assert db.execute('SELECT count(*) FROM facts').fetchone()[0]==2
