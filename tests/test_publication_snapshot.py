import json
from pathlib import Path
from decimal import Decimal

from secfragility.database import create, insert
from secfragility.calculation import prepare_views
from secfragility.quarter_series import prepare
from tests.test_identity_and_guards import fact, instance


def test_evening_acceptance_uses_official_publication_date_without_future_comparative(tmp_path):
    source = Path(__file__).resolve().parents[1]
    (tmp_path / 'work').mkdir()
    for name in ('schema.sql', 'config.yaml', 'queries.sql'):
        (tmp_path / name).write_text((source / name).read_text())
    (tmp_path / 'work/expected_universe.json').write_text(json.dumps({'quarters': [
        dict(group_id='S', period_start='2024-10-01', period_end='2024-12-31',
             fiscal_year_start='2024-01-01', quarter_number=4)]}))
    db = create(tmp_path)
    for docid, acc, accepted, public, value in (
        ('original', 'first', '2025-02-04T23:00:00Z', '2025-02-05', '1000000'),
        ('later', 'second', '2025-05-05T12:00:00Z', '2025-05-05', '2000000')):
        f = dict(fact(instance(), document_id=docid), accession=acc,
                 period_start='2024-10-01', acceptance_datetime=accepted,
                 knowledge_date=public, model_quantity='revenue_total', value=Decimal(value))
        insert(db, 'facts', f)
        insert(db, 'documents', dict(document_id=docid, group_id='S', accession=acc,
               url='https://www.sec.gov/' + docid, cache_path=docid, sha256=docid,
               form='10-K', filing_status='filed', acceptance_datetime=accepted,
               knowledge_date=public, as_of='2026-10-09T00:00:00Z'))
    prepare_views(db, tmp_path, '2026-10-09T00:00:00Z')
    prepare(db, tmp_path, '2026-10-09T00:00:00Z')
    assert str(db.execute('SELECT public_at::DATE FROM quarter_cutoffs').fetchone()[0]) == '2025-02-05'
    assert db.execute('SELECT value FROM quarter_quantities_as_known').fetchone()[0] == Decimal('1000000')
    assert db.execute('SELECT value FROM quarter_quantities_revised').fetchone()[0] == Decimal('2000000')
