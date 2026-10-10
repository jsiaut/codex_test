from decimal import Decimal
from secfragility.pairs import financed

Q=[dict(group_id='S',period_start='2026-01-01',period_end='2026-03-31')]
BASE=dict(from_group_id='S',to_group_id='C',knowledge_date='2026-02-01',elimination_status='external',edge_kind='amount',
          family='financing',stage='drawn_or_paid',event_type='funding',event_date='2026-01-20',currency='USD',unit='USD',
          type='equity_primary',amount=Decimal(10),tier='C')

def state(edge,cutoff='2026-04-01'):
    return financed([edge],'S','C',Q[0],Q,cutoff)

def test_paid_cash_during_first_known_quarter_is_active_without_inventing_history():
    assert state(BASE)=='active'

def test_signed_cap_and_guarantee_do_not_establish_financing():
    assert state(dict(BASE,stage='signed'))=='unknown'
    assert state(dict(BASE,family='credit_support',type='guarantee'))=='unknown'

def test_future_publication_noncash_and_zero_do_not_establish_cash_financing():
    assert state(dict(BASE,knowledge_date='2026-05-01'))=='unknown'
    assert state(dict(BASE,type='noncash_investment'))=='unknown'
    assert state(dict(BASE,amount=Decimal(0)))=='unknown'

def test_pending_relation_and_repayment_are_not_new_financing():
    assert state(dict(BASE,edge_kind='relation'))=='unknown'
    assert state(dict(BASE,event_type='repayment'))=='unknown'


def test_xbrl_currency_unit_establishes_the_same_cash_financing():
    assert state(dict(BASE,unit='http://www.xbrl.org/2003/iso4217:USD'))=='active'
    assert state(dict(BASE,unit='http://www.xbrl.org/2003/instance:shares'))=='unknown'


def test_cumulative_flow_crossing_lookback_is_not_dated_to_its_closing_day():
    assert state(dict(BASE,event_date=None,period_start='2025-01-01',period_end='2026-03-31'))=='unknown'
