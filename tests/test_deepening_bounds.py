import json
from decimal import Decimal
from pathlib import Path
from secfragility.database import create, insert
from secfragility.calculation import prepare_views
from secfragility.deepening_assembly import horizon_bounds
from tests.test_identity_and_guards import fact, instance


def fixture(root, missing_year_two=False):
    source=Path(__file__).resolve().parents[1];(root/'work').mkdir()
    for name in ('schema.sql','queries.sql','config.yaml'):
        (root/name).write_text((source/name).read_text())
    concepts=dict(cash='us-gaap:CashAndCashEquivalentsAtCarryingValue',
        remainder='us-gaap:LongTermDebtMaturitiesRepaymentsOfPrincipalRemainderOfFiscalYear',
        next_year='us-gaap:LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths',
        year_two='us-gaap:LongTermDebtMaturitiesRepaymentsOfPrincipalInYearTwo')
    quote='As of June 30, 2026, future principal payments for total debt: remaining 2026, 2027, 2028.'
    (root/'work/block.json').write_text(json.dumps(dict(text=quote)))
    (root/'work/deepening_numeric_rules.json').write_text(json.dumps([dict(group_id='S',
        accession='acc',period_end='2026-06-30',block_path='work/block.json',source_quote=quote,concepts=concepts)]))
    db=create(root)
    for key,value in dict(cash='5524000000',remainder='4413000000',next_year='6184000000',year_two='4416000000').items():
        if key=='year_two' and missing_year_two:continue
        f=dict(fact(instance()),fact_id=key,semantic_key=key,accession='acc',concept=concepts[key],
            canonical_concept=concepts[key],period_start=None,period_end='2026-06-30',value=Decimal(value),
            acceptance_datetime='2026-08-12T12:00:00Z',knowledge_date='2026-08-12')
        insert(db,'facts',f)
    prepare_views(db,root,'2026-10-09T10:24:21Z')
    db.execute("CREATE TEMP TABLE quarter_cutoffs AS SELECT 'S' group_id, DATE '2026-04-01' start_date, DATE '2026-06-30' end_date, TIMESTAMPTZ '2026-08-12T12:00:00Z' public_at")
    horizon_bounds(db,root,'2026-10-09T10:24:21Z')
    return db


def test_annual_buckets_produce_rolling_intervals_not_a_false_exact_maturity(tmp_path):
    db=fixture(tmp_path)
    r=db.execute("SELECT term,value_lower,value_upper,value FROM measures WHERE view='revised' ORDER BY term").fetchall()
    assert r==[('horizon_12m',Decimal('0.798877'),Decimal('1.918357'),None),
               ('horizon_24m',Decimal('1.918356'),Decimal('2.717777'),None)]
    # Every permissible allocation of an annual bucket remains inside the
    # outward-rounded bounds, including schedules at both extreme endpoints.
    cash=Decimal('5524000000')
    for within_2027 in (0,Decimal('3092000000'),Decimal('6184000000')):
        ratio=(Decimal('4413000000')+within_2027)/cash
        assert r[0][1]<=ratio<=r[0][2]


def test_missing_2028_amount_never_becomes_zero_for_24_month_bound(tmp_path):
    db=fixture(tmp_path,missing_year_two=True)
    assert db.execute("SELECT DISTINCT term FROM measures").fetchall()==[('horizon_12m',)]
