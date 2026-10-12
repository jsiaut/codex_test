from pathlib import Path
from decimal import Decimal
import json
import pytest
from secfragility.dell_evidence import table_amount
from secfragility.database import create,insert
from secfragility.dell_integration import coherent_controls

ROOT=Path(__file__).resolve().parents[1]

def test_selected_table_cell_preserves_period_column_and_sign():
    quote='July 31, 2026 | January 30, 2026\n(in millions)\nDebt | $ | 100 | $ | 80\nAllocation | (40) | (30)'
    assert table_amount(quote,'Debt',100000000)['column']==0
    assert table_amount(quote,'Allocation',-40000000)['token']=='(40)'
    with pytest.raises(ValueError):table_amount(quote,'Debt',80000000)
    with pytest.raises(ValueError):table_amount(quote,'Allocation',40000000)

@pytest.mark.parametrize('quote',['Debt | $ | 100','(in millions)\nDebt | € | 100','(in billions)\nDebt | $ | 100'])
def test_table_binding_needs_explicit_scale_and_currency(quote):
    with pytest.raises(ValueError):table_amount(quote,'Debt',100000000)

def test_DFS_originations_not_subtracted_twice_and_adjusted_FCF_separate():
    authored=json.loads((ROOT/'work/dell/authored_observations.json').read_text())
    by={o.get('model_quantity'):o for o in authored}
    assert 'cash flows from operations' in by['dfs_cashflow_classification']['quote']
    assert Decimal(by['DFS_financing_receivables_FCF_addback']['amount'])+Decimal(by['DFS_lessor_equipment_FCF_addback']['amount'])+Decimal('986000000')==Decimal(by['adjusted_FCF_reported']['amount'])
    assert by['adjusted_FCF_reported']['tier']=='C'
    assert by['dfs_financing_originations']['counterparty_evidence']=='anonymous'
    assert not by['dfs_financing_originations'].get('family')

def test_available_facility_is_not_drawn_and_MSD_firms_are_distinct():
    authored=json.loads((ROOT/'work/dell/authored_observations.json').read_text());by={o.get('model_quantity'):o for o in authored}
    assert by['undrawn_committed_revolver_actual_availability']['stage']=='available'
    assert by['revolver_zero_draw']['amount']=='0'
    assert by['MSD_personal_affiliates_commercial_scope'].get('amount') is None
    assert 'MSD Investment Corp.' in by['MSD_personal_affiliates_commercial_scope']['issuer_treatment']
    assert by['dfs_vmware_end_customer_financing'].get('family') is None

def test_bond_issuance_is_later_than_July_balance_and_nominal_not_proceeds():
    items=[o for o in json.loads((ROOT/'work/dell/authored_observations.json').read_text()) if o.get('model_quantity','').startswith('September2026_notes_nominal_')]
    assert len(items)==4 and sum(Decimal(o['amount']) for o in items)==Decimal('5000000000')
    assert all(o['event_date']=='2026-09-15' and o['period_end']=='2026-09-15' and 'net cash proceeds' in o['issuer_treatment'] for o in items)

def test_named_lender_commitments_remain_contracts_without_draw_claim():
    entries=json.loads((ROOT/'work/dell/credit_facility_register.json').read_text())
    assert len(entries)==24 and sum(r['committed_amount'] for r in entries)==6000000000
    assert all(r['stage']=='signed' and r['actual_draw_not_inferred'] for r in entries)
    authored={o['observation_id']:o for o in json.loads((ROOT/'work/dell/authored_observations.json').read_text())}
    assert all(authored[r['observation_id']]['tier']=='D' and authored[r['observation_id']].get('family') is None for r in entries)

def test_coherent_controls_never_mix_different_deposits(tmp_path):
    (tmp_path/'schema.sql').write_text((ROOT/'schema.sql').read_text());(tmp_path/'work/dell').mkdir(parents=True)
    db=create(tmp_path);stamp='2026-10-09T10:24:21+00:00'
    def fact(fid,accession,quantity,value):
        insert(db,'facts',dict(fact_id=fid,semantic_key=fid,document_id='doc',accession=accession,entity_id='cik:0001571996',
            group_id='DELL',concept=quantity,canonical_concept=quantity,model_quantity=quantity,period_end='2021-01-29',
            unit='USD',currency='USD',accounting_framework='us_gaap',reporting_scope='consolidated',source_perspective='reporting_entity',
            value=value,is_tagged=True,decimals='-6',locator='test',occurrence_rank=0,acceptance_datetime=stamp,knowledge_date='2021-03-01',
            filing_status='filed',assurance_level='audited',tier='A',location='financial_note',coverage_state='observed',as_of=stamp))
    fact('a','old','operating_lease_payments_undiscounted',10000000);fact('b','old','operating_lease_imputed_interest',1000000)
    fact('c','new','operating_lease_liability_current',2000000);fact('d','new','operating_lease_liability_noncurrent',7000000)
    db.execute('CREATE VIEW eligible_instance_occurrences AS SELECT * FROM facts')
    coherent_controls(db,tmp_path,stamp)
    assert db.execute('SELECT count(*) FROM controls').fetchone()[0]==0
    fact('e','old','operating_lease_liability_current',2000000);fact('f','old','operating_lease_liability_noncurrent',7000000)
    coherent_controls(db,tmp_path,stamp)
    assert db.execute('SELECT status,residual FROM controls').fetchall()==[('ok',Decimal(0))]
    db.close()
