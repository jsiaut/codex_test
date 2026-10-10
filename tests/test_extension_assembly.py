from decimal import Decimal
from pathlib import Path
import json
from secfragility.database import create,insert
from secfragility.extension_assembly import components,interpretations


def environment(tmp_path):
    source=Path(__file__).resolve().parents[1]
    (tmp_path/'work').mkdir()
    (tmp_path/'schema.sql').write_text((source/'schema.sql').read_text())
    (tmp_path/'work/extension_authorization.json').write_text(json.dumps({'components':['lease_note']}))
    db=create(tmp_path)
    db.execute('CREATE TEMP TABLE quarter_cutoffs (group_id VARCHAR, period_start DATE, period_end DATE, cutoff TIMESTAMPTZ)')
    db.execute("INSERT INTO quarter_cutoffs VALUES ('S','2026-01-01','2026-03-31','2026-04-30T12:00:00Z')")
    return db


def observation(oid,amount,basis,known='2026-04-30'):
    return dict(observation_id=oid,content_key='k',document_id='d',accession='a',group_id='S',entity_id='s',
        abstained=False,quote='Source amount retained',locator='rawbytes:0:30',raw_byte_start=0,raw_byte_end=30,
        amount=Decimal(amount),unit='http://www.xbrl.org/2003/iso4217:USD',currency='USD',
        amount_origin='narrative_only',amount_qualifier='exact',model_quantity='lease_amount',
        period_end='2026-03-31',block='contractual_outflows',measurement_basis=basis,
        filing_status='filed',assurance_level='reviewed',tier='B',location='notes',knowledge_date=known,
        source_perspective='reporting_entity',accounting_framework='us_gaap',as_of='2026-10-09T00:00:00Z')


def test_present_value_and_gross_schedule_remain_separate_with_publication_cutoff(tmp_path):
    db=environment(tmp_path)
    for o in [observation('pv','100','present_value'),observation('gross','130','undiscounted'),
              observation('later','140','undiscounted','2026-05-01')]:
        insert(db,'observations',o)
    db.execute('CREATE VIEW usable_observations AS SELECT * FROM observations')
    components(db,tmp_path,'2026-10-09T00:00:00Z')
    known=db.execute("SELECT value,lineage,status,overlap_possible FROM measures WHERE view='as_known' ORDER BY value").fetchall()
    assert known==[(Decimal(100),'["pv"]','partial',True),(Decimal(130),'["gross"]','partial',True)]
    assert db.execute("SELECT count(*) FROM measures WHERE view='revised'").fetchone()[0]==3
    assert db.execute('SELECT count(*) FROM measures WHERE value=230').fetchone()[0]==0


def test_attribution_correction_preserves_original_reading(tmp_path):
    db=environment(tmp_path)
    o=observation('capacity','50','capacity_available')
    insert(db,'observations',o)
    (tmp_path/'work/extension_attribution_reviews.json').write_text(json.dumps([
        dict(content_key='k',affected_quantity='lease_amount',decision='exclude_undrawn_capacity_from_contractual_outflows_keep_available_liquidity')]))
    interpretations(db,tmp_path,'2026-10-09T00:00:00Z')
    assert db.execute('SELECT block,amount FROM observations').fetchone()==('contractual_outflows',Decimal(50))
    assert db.execute('SELECT block,amount FROM interpreted_observations').fetchone()==(None,Decimal(50))
