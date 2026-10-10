"""Cache-only health and exposure components, never a global exposure sum."""
from .database import sql_literal


def run(db,as_of):
    db.execute('''UPDATE measures m SET lineage=r.lineage,knowledge_date=r.knowledge_date,evidence_profile=r.evidence_profile,unit='ratio'
      FROM measures r WHERE m.measure='named_edge_coverage' AND m.lineage='[]' AND m.denominator=r.value
       AND r.measure='revenue_total' AND r.status='computed' AND m.group_id=r.group_id
       AND m.period_start=r.period_start AND m.period_end=r.period_end AND m.view=r.view''')
    for view in ['as_known','revised']:
        s='snapshot_stocks_'+view;q='quarter_quantities_'+view
        for quantity,category in [('debt_carrying_current','debt'),('debt_carrying_noncurrent','debt'),
           ('operating_lease_liability_current','lease_liability'),('operating_lease_liability_noncurrent','lease_liability'),
           ('finance_lease_liability_current','lease_liability'),('finance_lease_liability_noncurrent','lease_liability')]:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,breakdown_key,value,unit,currency,
             status,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT 'exposure_matrix',group_id,quarter_start,quarter_end,'{view}',snapshot_at,
              'recognized_liabilities|{category}|carrying_amount|{quantity}',value,unit,currency,'computed',coverage_state,
              knowledge_date,to_json([tier]),to_json([fact_id]),source_perspective,accounting_framework
              FROM {s} WHERE model_quantity='{quantity}' AND period_end=quarter_end''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,
          status,coverage_state,knowledge_date,lineage,evidence_profile,source_perspective,accounting_framework)
          SELECT 'liq_undrawn_committed_facilities',group_id,quarter_start,quarter_end,'{view}',snapshot_at,value,unit,currency,
           'computed',coverage_state,knowledge_date,to_json([fact_id]),to_json([tier]),source_perspective,accounting_framework
           FROM {s} WHERE model_quantity='undrawn_committed_facilities' AND period_end=quarter_end''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,variant,value,unit,numerator,denominator,
           status,nd_reason,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         WITH debt AS (SELECT group_id,quarter_start,quarter_end,snapshot_at,unit,accounting_framework,reporting_scope,
           sum(value) AS value,count(DISTINCT model_quantity) AS terms,max(knowledge_date) AS knowledge_date,
           list(fact_id) AS lineage,list(tier) AS tiers FROM {s} WHERE period_end=quarter_end
           AND model_quantity IN ('debt_carrying_current','debt_carrying_noncurrent') GROUP BY ALL)
          SELECT 'lev_debt_and_leases_to_operating_income_plus_da',d.group_id,d.quarter_start,d.quarter_end,'{view}',d.snapshot_at,
           'debt','long_term_carrying_only',exact_ratio6(d.value,op.value+da.value),'ratio',d.value,op.value+da.value,
           CASE WHEN op.value+da.value=0 THEN 'not_determinable' ELSE 'partial' END,
           CASE WHEN op.value+da.value=0 THEN 'denominator_zero' ELSE 'short_term_debt_and_other_components_not_established' END,
           'observed',greatest(d.knowledge_date,op.knowledge_date,da.knowledge_date),to_json(d.tiers),
           to_json(d.lineage||from_json(op.lineage,'["VARCHAR"]')||from_json(da.lineage,'["VARCHAR"]')),'reporting_entity',d.accounting_framework
           FROM debt d JOIN ttm_quantities_{view} op ON d.group_id=op.group_id AND d.quarter_start=op.anchor_start
            AND d.quarter_end=op.anchor_end AND op.model_quantity='operating_income' AND op.window_rank=0 AND d.unit=op.unit
            AND d.reporting_scope=op.reporting_scope AND d.accounting_framework=op.accounting_framework
           JOIN ttm_quantities_{view} da ON op.group_id=da.group_id AND op.anchor_start=da.anchor_start AND op.anchor_end=da.anchor_end
            AND op.unit=da.unit AND op.reporting_scope=da.reporting_scope AND op.accounting_framework=da.accounting_framework
            AND da.model_quantity='depreciation_amortization' AND da.window_rank=0 WHERE d.terms=2''')
        # No proxy for the counterparty-cash financing total: current investment
        # and debt notes were not read, even where an isolated flow is known.
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,currency,status,
           coverage_state,knowledge_date,lineage,source_perspective,accounting_framework)
          WITH opening AS (SELECT group_id,quarter_start,quarter_end,unit,accounting_framework,
             sum(CASE WHEN model_quantity IN ('receivables','inventories') THEN value ELSE -value END) AS value,
             count(DISTINCT model_quantity) AS terms,max(knowledge_date) AS knowledge_date,to_json(list(fact_id)) AS lineage
             FROM {s} WHERE period_end=quarter_start-INTERVAL 1 DAY
              AND model_quantity IN ('receivables','inventories','accounts_payable','contract_liabilities_current') GROUP BY ALL)
          SELECT 'working_capital',a.group_id,a.period_start,a.period_end,'{view}',a.as_of,'change',a.value-b.value,a.unit,a.currency,
           'computed','observed',greatest(a.knowledge_date,b.knowledge_date),
           to_json(from_json(a.lineage,'["VARCHAR"]')||from_json(b.lineage,'["VARCHAR"]')),
           'reporting_entity',a.accounting_framework FROM measures a JOIN opening b ON a.group_id=b.group_id
            AND a.unit=b.unit AND a.accounting_framework=b.accounting_framework AND a.period_start=b.quarter_start::VARCHAR
            AND a.period_end=b.quarter_end::VARCHAR WHERE a.measure='working_capital' AND a.term='net'
             AND a.view='{view}' AND a.status='computed' AND b.terms=4''')
    db.execute("UPDATE links SET resolved=true,relation_type='same_measure',resolution_evidence='Identical immutable amount key; no additional amount.' WHERE amount_a_id=amount_b_id AND amount_a_id IS NOT NULL")
    db.execute("UPDATE measures SET constant_perimeter='as_if_combined' WHERE group_id='SPCX' AND status IN ('computed','partial','bounded') AND unit IS DISTINCT FROM 'event'")
    # Published precise concentration bounds. Anonymous identities stay tied to
    # this particular filing/period, never stitched into a client history.
    db.execute('''UPDATE measures m SET value_lower=m.value-precision_radius(f.decimals),
      value_upper=m.value+precision_radius(f.decimals),bound_basis='deposited_decimal_rounding_half_open_upper'
      FROM facts f WHERE m.measure='customer_concentration_anonymous' AND json_extract_string(m.lineage,'$[0]')=f.fact_id
       AND precision_radius(f.decimals) IS NOT NULL''')
    db.execute('''CREATE TEMP TABLE changed_fact_ids AS SELECT DISTINCT json_extract_string(j.value,'$') AS fact_id
      FROM controls c,json_each(c.evidence) j WHERE c.control='c4_restatement_detection' AND starts_with(c.explanation_code,'changed_value_')''')
    db.execute('''UPDATE measures m SET basis_break=true,basis_break_reason='Selected deposited amount follows a changed comparative; cause unresolved.',recast_cause='unknown'
      WHERE m.measure NOT IN ('fragility_event','annex_e_outcome') AND EXISTS (
       SELECT 1 FROM json_each(m.lineage) a JOIN changed_fact_ids b ON json_extract_string(a.value,'$')=b.fact_id)''')
