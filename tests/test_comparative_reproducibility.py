from decimal import Decimal
from pathlib import Path
import json
from secfragility.database import create, insert
from secfragility.calculation import prepare_views
from secfragility.quarter_series import prepare, measures
from tests.test_identity_and_guards import fact, instance


def test_published_comparative_wins_over_rounded_ytd_difference_in_either_row_order(tmp_path):
    source = Path(__file__).resolve().parents[1]
    base = fact(instance())
    # The same deposit reports Q2 directly and also rounded Q1/H1 totals.
    # Their difference is one reporting unit lower than the published quarter.
    periods = [('2020-01-01', '2020-03-31', '17000000000'),
               ('2020-01-01', '2020-06-30', '35686000000'),
               ('2020-04-01', '2020-06-30', '18687000000'),
               ('2021-04-01', '2021-06-30', '29077000000')]
    for reverse in (False, True):
        root = tmp_path / str(reverse)
        root.mkdir(); (root / 'work').mkdir()
        for name in ('schema.sql', 'config.yaml', 'queries.sql'):
            (root / name).write_text((source / name).read_text())
        quarters = [dict(group_id='S', period_start=s, period_end=e,
                         fiscal_year_start=s[:4] + '-01-01', quarter_number=1 if e.endswith('03-31') else 2)
                    for s, e in [('2020-01-01', '2020-03-31'), ('2020-04-01', '2020-06-30'), ('2021-04-01', '2021-06-30')]]
        (root / 'work/expected_universe.json').write_text(json.dumps({'quarters': quarters}))
        db = create(root)
        insert(db, 'documents', dict(document_id='d', url='https://www.sec.gov/fixture', group_id='S',
            form='10-Q', acceptance_datetime='2021-07-25T12:00:00Z', cache_path='fixture',
            sha256='fixture', filing_status='filed', as_of='2026-10-09T00:00:00Z'))
        rows = [dict(base, fact_id='f' + str(i), semantic_key='period' + str(i),
                     period_start=s, period_end=e, model_quantity='revenue_total',
                     value=Decimal(v), acceptance_datetime='2021-07-25T12:00:00Z', knowledge_date='2021-07-25')
                for i, (s, e, v) in enumerate(periods)]
        for row in reversed(rows) if reverse else rows:
            insert(db, 'facts', row)
        prepare_views(db, root, '2026-10-09T00:00:00Z')
        prepare(db, root, '2026-10-09T00:00:00Z')
        measures(db, '2026-10-09T00:00:00Z')
        result = db.execute("SELECT denominator,lineage FROM measures WHERE measure='revenue_growth' AND term='yoy' AND view='as_known' AND period_end='2021-06-30'").fetchone()
        assert result is not None
        assert result[0] == Decimal('18687000000')
        assert json.loads(result[1]) == ['f3', 'f2']
        db.close()
