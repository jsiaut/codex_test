from pathlib import Path
from decimal import Decimal
from secfragility.database import create,bulk_insert


def test_bulk_publication_preserves_decimal_and_missing_value_defaults(tmp_path):
    source=Path(__file__).resolve().parents[1]
    (tmp_path/'schema.sql').write_text((source/'schema.sql').read_text());(tmp_path/'work').mkdir()
    db=create(tmp_path)
    base=dict(measure='cfo',group_id='S',period_start='2026-01-01',period_end='2026-03-31',view='as_known',as_of='2026-04-01T00:00:00+00:00')
    bulk_insert(db,'measures',[dict(base,value=Decimal('9999999999999999.123456'),status='computed',coverage_state='observed'),
      dict(base,view='revised',status='not_determinable',nd_reason='not_processed',coverage_state='not_processed')],tmp_path,'test')
    assert db.execute("SELECT value,entity_id,term,lineage FROM measures WHERE view='as_known'").fetchone()==(Decimal('9999999999999999.123456'),'none','none','[]')
    assert db.execute("SELECT value FROM measures WHERE view='revised'").fetchone()==(None,)
