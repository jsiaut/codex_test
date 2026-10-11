from pathlib import Path
from decimal import Decimal
import pytest
from secfragility.database import create,insert
from secfragility.controls import eps_controls
from tests.test_identity_and_guards import fact,instance


@pytest.mark.parametrize('income_currency,status,reason',[
    ('USD','mismatch','eps_scale_residual'),('EUR','not_testable','missing_eps_terms')])
def test_eps_control_explains_small_precise_residual_and_rejects_other_currency(tmp_path,income_currency,status,reason):
    src=Path(__file__).resolve().parents[1];(tmp_path/'schema.sql').write_text((src/'schema.sql').read_text())
    db=create(tmp_path);usd='http://www.xbrl.org/2003/iso4217:USD';shares='http://www.xbrl.org/2003/instance:shares'
    terms=[('eps_diluted','1',usd+'/'+shares,'-2'),('diluted_shares_weighted','1000',shares,'INF'),
        ('net_income_to_common_diluted','1010','http://www.xbrl.org/2003/iso4217:'+income_currency,'0')]
    for i,(quantity,value,unit,decimals) in enumerate(terms):
        insert(db,'facts',dict(fact(instance()),fact_id=str(i),semantic_key=str(i),model_quantity=quantity,
            value=Decimal(value),unit=unit,decimals=decimals))
    db.execute('CREATE TEMP TABLE quantities_as_known AS SELECT * FROM facts')
    db.execute('CREATE TEMP TABLE selected_as_known AS SELECT * FROM facts')
    db.execute("CREATE TEMP TABLE precision_units AS SELECT * FROM (VALUES ('-2',0.005),('INF',0),('0',0.5)) v(decimals,half_unit)")
    eps_controls(db,'2026-10-09T00:00:00Z','0.10')
    assert db.execute('SELECT status,explanation_code FROM controls').fetchall()==[(status,reason)]
    if status=='mismatch':
        residual,tolerance=db.execute('SELECT residual,tolerance FROM controls').fetchone()
        assert abs(residual)>tolerance and abs(residual)<Decimal('101')
