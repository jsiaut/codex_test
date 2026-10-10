from decimal import Decimal
from pathlib import Path
from secfragility.database import create, insert
from tests.test_identity_and_guards import fact, instance


def test_rounded_comparative_does_not_quarantine_more_precise_statement(tmp_path):
    source = Path(__file__).resolve().parents[1]
    (tmp_path/'schema.sql').write_text((source/'schema.sql').read_text())
    db = create(tmp_path)
    precise = fact(instance().replace(b'decimals="-6">1000000', b'decimals="-6">50486000000'))
    rounded = dict(precise, fact_id='rounded', occurrence_rank=2,
                   value=Decimal('50500000000'), decimals='-8')
    insert(db,'facts',precise); insert(db,'facts',rounded)
    db.execute((source/'queries.sql').read_text())
    assert db.execute('SELECT count(*) FROM eligible_facts WHERE value IS NOT NULL').fetchone()[0] == 2
    assert db.execute('SELECT fact_id FROM eligible_instance_occurrences').fetchone()[0] == precise['fact_id']
    assert db.execute('SELECT value FROM facts WHERE fact_id=?',[rounded['fact_id']]).fetchone()[0] == rounded['value']


def test_disjoint_rounding_intervals_block_both_occurrences(tmp_path):
    source = Path(__file__).resolve().parents[1]
    (tmp_path/'schema.sql').write_text((source/'schema.sql').read_text())
    db=create(tmp_path)
    original=fact(instance())
    incompatible=dict(original,fact_id='incompatible',occurrence_rank=2,value=Decimal('2000000'))
    insert(db,'facts',original);insert(db,'facts',incompatible)
    db.execute((source/'queries.sql').read_text())
    assert db.execute('SELECT count(*) FROM eligible_facts WHERE value IS NOT NULL').fetchone()[0] == 0
    assert db.execute('SELECT count(*) FROM facts WHERE value IS NOT NULL').fetchone()[0] == 2


def test_exact_value_at_excluded_upper_boundary_conflicts(tmp_path):
    source=Path(__file__).resolve().parents[1]
    (tmp_path/'schema.sql').write_text((source/'schema.sql').read_text())
    db=create(tmp_path);a=fact(instance())
    b=dict(a,fact_id='upper-bound',occurrence_rank=2,value=Decimal('1500000'),decimals='INF')
    insert(db,'facts',a);insert(db,'facts',b);db.execute((source/'queries.sql').read_text())
    assert db.execute('SELECT count(*) FROM eligible_facts WHERE value IS NOT NULL').fetchone()[0]==0


def test_exact_value_at_included_lower_boundary_remains_eligible(tmp_path):
    source=Path(__file__).resolve().parents[1]
    (tmp_path/'schema.sql').write_text((source/'schema.sql').read_text())
    db=create(tmp_path);a=fact(instance())
    b=dict(a,fact_id='lower-bound',occurrence_rank=2,value=Decimal('500000'),decimals='INF')
    insert(db,'facts',a);insert(db,'facts',b);db.execute((source/'queries.sql').read_text())
    assert db.execute('SELECT count(*) FROM eligible_facts WHERE value IS NOT NULL').fetchone()[0]==2
