"""Publish every expected cell, distinguishing coverage from a numeric value."""
import json
from .database import MEASURE_TERMS,sql_literal


def run(db,root,as_of):
    u=json.loads((root/'work/expected_universe.json').read_text())
    cells=u['cells']
    path=root/'work/expected_cells.ndjson'
    path.write_text(''.join(json.dumps(c)+'\n' for c in cells))
    db.execute('''CREATE TEMP TABLE expected_cells AS SELECT measure,group_id,counterparty_id,period_start,period_end,
                  view,term,breakdown_key FROM read_json_auto('''+sql_literal(str(path))+''',format='newline_delimited')''')
    db.execute('''INSERT INTO measures (measure,group_id,counterparty_id,period_start,period_end,view,as_of,term,breakdown_key,
      status,nd_reason,coverage_state,financing_policy,financing_state,outcome)
      SELECT e.measure::measure_id_t,e.group_id,e.counterparty_id,e.period_start,e.period_end,e.view::view_t,?,e.term,e.breakdown_key,
       'not_determinable',CASE WHEN e.period_end='none' THEN 'fiscal_calendar_not_established'
         WHEN e.measure IN ('fcf_after_counterparty_financing','counterparty_cash_financing_net','counterparty_exposure',
          'lease_not_commenced_bridge','documented_backlog_dependency','consideration_to_customer','noncash_revenue_from_investees','contract_coverage','documented_path','annex_e_outcome') THEN 'not_processed'
         WHEN e.measure IN ('documented_revenue_dependency','investor_customer_revenue_share') THEN 'empty_numerator'
         WHEN e.measure='fragility_event' THEN 'source_not_collected_or_period_not_established' ELSE 'missing_admissible_terms' END,
       CASE WHEN e.period_end='none' THEN 'unknown'
         WHEN e.measure IN ('fcf_after_counterparty_financing','counterparty_cash_financing_net','counterparty_exposure','lease_not_commenced_bridge',
          'documented_backlog_dependency','consideration_to_customer','noncash_revenue_from_investees','contract_coverage','documented_path','annex_e_outcome') THEN 'not_processed'
         WHEN e.measure='fragility_event' THEN 'not_collected' ELSE 'not_disclosed' END,
       CASE WHEN e.measure IN ('documented_revenue_dependency','documented_backlog_dependency','investor_customer_revenue_share') THEN 'exposure_outstanding' ELSE 'none' END,
       CASE WHEN e.measure IN ('documented_revenue_dependency','documented_backlog_dependency','investor_customer_revenue_share') THEN 'unknown' END,
       CASE WHEN e.measure='annex_e_outcome' THEN CASE WHEN starts_with(e.breakdown_key,'E6|') THEN 'descriptive' ELSE 'indeterminate' END END
      FROM expected_cells e WHERE NOT EXISTS (SELECT 1 FROM measures m WHERE m.measure::VARCHAR=e.measure AND m.group_id=e.group_id
        AND m.counterparty_id=e.counterparty_id AND m.period_start=e.period_start AND m.period_end=e.period_end AND m.view::VARCHAR=e.view
        AND m.term=e.term AND (m.breakdown_key=e.breakdown_key OR e.breakdown_key='none' AND m.breakdown_key!='none'
         OR e.measure='fragility_event' AND m.breakdown_key=split_part(e.breakdown_key,'|',1)
         OR e.measure='exposure_matrix' AND m.breakdown_key LIKE split_part(e.breakdown_key,'|',1)||'|'||split_part(e.breakdown_key,'|',2)||'|%'||split_part(e.breakdown_key,'|',3)||'|%'
         OR e.measure='annex_e_outcome' AND starts_with(m.breakdown_key,split_part(e.breakdown_key,'|',1)||'|'||split_part(e.breakdown_key,'|',2)||'|'||split_part(e.breakdown_key,'|',3))))''',[as_of])
    # Every observed recast boundary remains an explicit excluded calculation,
    # not an invisible hole in the growth/difference series.
    db.execute('''INSERT INTO exclusions (exclusion_id,group_id,accession,element_type,element_id,reason,detail,coverage_state,period_start,period_end,as_of)
      SELECT DISTINCT sha256(accession||model_quantity||period_start::VARCHAR||period_end::VARCHAR),group_id,accession,'quarter_difference',
       model_quantity||'|'||period_start::VARCHAR||'|'||period_end::VARCHAR,'recast_boundary',
       'Comparative values differ beyond published precision across candidate filings; no mixed-basis subtraction.',
       'conflicting',period_start,period_end,? FROM quarter_candidates WHERE recast_boundary''',[as_of])
    db.execute('''UPDATE measures m SET coverage_state='conflicting',nd_reason='conflicting_tagged_fact'
      WHERE m.status='not_determinable' AND m.lineage='[]' AND EXISTS (
       SELECT 1 FROM eligible_facts f WHERE f.group_id=m.group_id AND f.period_end::VARCHAR=m.period_end
        AND f.model_quantity=m.measure::VARCHAR AND f.coverage_state='conflicting')''')
    db.execute('''UPDATE measures m SET basis_break=true,basis_break_reason='No subtraction across incompatible comparative presentations.',
      nd_reason='recast_boundary',coverage_state='conflicting',recast_cause='unknown'
      WHERE m.status='not_determinable' AND m.lineage='[]' AND m.measure IN ('revenue_growth','revenue_total','cfo','capex_cash')
       AND EXISTS (SELECT 1 FROM quarter_candidates q WHERE q.group_id=m.group_id AND q.period_start::VARCHAR=m.period_start
        AND q.period_end::VARCHAR=m.period_end AND q.recast_boundary AND (q.model_quantity=m.measure::VARCHAR
         OR m.measure='revenue_growth' AND q.model_quantity='revenue_total'))''')
