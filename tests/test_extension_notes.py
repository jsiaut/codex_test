from secfragility.extension import families, contains
from secfragility.reader import financial_note


def test_note_role_selection_includes_risk_and_combined_disclosures():
    assert 'concentration_narrative' in families('Concentrations of Credit and Operation Risk')
    assert {'lease_note', 'commitments_note'} <= set(families('LEASES, OTHER COMMITMENTS AND CERTAIN CONTINGENCIES'))
    assert 'investments_note' in families('Non-marketable Equity Securities')
    assert 'debt_note' in families('NOTES PAYABLE AND OTHER BORROWINGS')
    assert families('Income Taxes') == []


def test_continuation_gaps_do_not_hide_separate_notes():
    parent = {'source_ranges': [[100, 200], [500, 600]]}
    assert contains(parent, {'source_ranges': [[120, 150], [550, 580]]})
    assert not contains(parent, {'source_ranges': [[250, 350]]})


def test_extension_notes_keep_financial_assurance():
    for family in ('investments_note', 'debt_note', 'lease_note',
                   'commitments_note', 'concentration_narrative'):
        assert financial_note({'block_class': family})
    assert not financial_note({'block_class': '8k_item'})
