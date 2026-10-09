from __future__ import annotations


def tier(*, edgar: bool, filing_status: str, document_kind: str,
         assurance_level: str, incorporated_by_reference=False) -> str:
    if not edgar:
        return 'F'
    if (filing_status in ('unclassified','submitted_draft','correspondence') or
        (filing_status == 'furnished' and not incorporated_by_reference) or document_kind == 'marketing'):
        return 'E'
    if document_kind in ('financial_statements','financial_note'):
        return {'audited':'A','reviewed':'B'}.get(assurance_level,'C')
    if document_kind == 'contract':
        return 'D'
    return 'C'


def periodic_assurance(form: str) -> str:
    if form in ('10-K','10-K/A','10-KT','10-KT/A','20-F','20-F/A','40-F','40-F/A'):
        return 'audited'
    if form in ('10-Q','10-Q/A','10-QT','10-QT/A'):
        return 'reviewed'
    return 'unknown'


def filing_status(form: str, item: str | None = None, express: str | None = None) -> str:
    if express in ('filed','furnished'):
        return express
    if form.startswith('DRS'):
        return 'submitted_draft'
    if form in ('CORRESP','UPLOAD','DRSLTR'):
        return 'correspondence'
    if form.startswith('6-K') or (form.startswith('8-K') and item in ('2.02','7.01')):
        return 'furnished'
    if form.startswith('8-K') and item is None:
        return 'unclassified'
    return 'filed'
