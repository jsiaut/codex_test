"""Four contiguous quarters selected together at a single information date."""
from .database import sql_literal

def run(db,as_of):
    for view in ('as_known','revised'):
        stamp='k.public_at' if view=='as_known' else sql_literal(as_of)+'::TIMESTAMPTZ'
        db.execute(f'''CREATE VIEW ttm_terms_{view} AS
          SELECT a.*,k.start_date AS anchor_start,k.end_date AS anchor_end,{stamp} AS snapshot_at
          FROM quarter_cutoffs k JOIN quarter_candidates a ON k.group_id=a.group_id
           AND a.period_end<=k.end_date AND a.period_end>k.end_date-INTERVAL 800 DAY
           AND a.acceptance_datetime<={stamp} AND a.value IS NOT NULL AND NOT a.recast_boundary
           JOIN anchor_order ao USING(model_quantity,canonical_concept)
          QUALIFY row_number() OVER (PARTITION BY k.group_id,k.start_date,k.end_date,a.model_quantity,a.period_start,a.period_end,a.unit,
           a.accounting_framework,a.reporting_scope ORDER BY CASE WHEN calculation_basis='direct_quarter' THEN 0 ELSE 1 END,
            ao.priority,a.acceptance_datetime DESC,a.accession DESC,a.document_rank DESC,a.occurrence_rank DESC)=1''')
        db.execute(f'''CREATE VIEW ttm_quantities_{view} AS
          WITH ranked AS (SELECT *,row_number() OVER (PARTITION BY group_id,anchor_start,anchor_end,model_quantity,unit,
           accounting_framework,reporting_scope ORDER BY period_end DESC) AS quarter_rank FROM ttm_terms_{view}),
          ordered AS (SELECT *,lag(period_start) OVER (PARTITION BY group_id,anchor_start,anchor_end,model_quantity,unit,
           accounting_framework,reporting_scope ORDER BY quarter_rank) AS newer_start FROM ranked),
          totals AS (SELECT group_id,anchor_start,anchor_end,model_quantity,unit,currency,accounting_framework,reporting_scope,snapshot_at,
           (quarter_rank-1)//4 AS window_rank,
           sum(value) AS value,min(period_start) AS start_date,max(period_end) AS end_date,count(*) AS terms,
           sum(period_end-period_start+1) AS duration_days,max(knowledge_date) AS knowledge_date,
           bool_and(quarter_rank%4=1 OR period_end+INTERVAL 1 DAY=newer_start) AS contiguous,
           to_json(flatten(list(from_json(lineage,'["VARCHAR"]')))) AS lineage,to_json(list(tier)) AS evidence_profile
           FROM ordered a WHERE quarter_rank<=8 AND NOT EXISTS (
            SELECT 1 FROM ranked b JOIN filing_recast_differences x ON x.accession_a=a.accession
             AND x.accession_b=b.accession AND x.model_quantity=a.model_quantity
            WHERE b.group_id=a.group_id AND b.anchor_start=a.anchor_start AND b.anchor_end=a.anchor_end
             AND b.model_quantity=a.model_quantity AND (b.quarter_rank-1)//4=(a.quarter_rank-1)//4) GROUP BY ALL)
          SELECT * FROM totals WHERE terms=4 AND contiguous AND duration_days=end_date-start_date+1
           AND duration_days BETWEEN 340 AND 385''')
        db.execute(f'''INSERT INTO measures
         (measure,group_id,period_start,period_end,view,as_of,term,value,unit,numerator,denominator,status,nd_reason,coverage_state,
          knowledge_date,evidence_profile,lineage,unequal_period_length,source_perspective,accounting_framework)
         SELECT 'revenue_growth',a.group_id,a.anchor_start,a.anchor_end,'{view}',a.snapshot_at,'ttm',
          exact_ratio6(a.value-b.value,b.value),'ratio',a.value-b.value,b.value,
          CASE WHEN b.value=0 THEN 'not_determinable' ELSE 'computed' END,
          CASE WHEN b.value=0 THEN 'denominator_zero' END,'observed',greatest(a.knowledge_date,b.knowledge_date),
          to_json([a.evidence_profile,b.evidence_profile]),to_json(from_json(a.lineage,'["VARCHAR"]')||from_json(b.lineage,'["VARCHAR"]')),
          a.duration_days!=b.duration_days,'reporting_entity',a.accounting_framework FROM ttm_quantities_{view} a
          JOIN ttm_quantities_{view} b ON a.group_id=b.group_id AND a.model_quantity=b.model_quantity AND a.unit=b.unit
           AND a.accounting_framework=b.accounting_framework AND a.reporting_scope=b.reporting_scope
           AND a.anchor_start=b.anchor_start AND a.anchor_end=b.anchor_end AND b.window_rank=1
           AND abs(date_diff('day',b.end_date,a.end_date)-365)<=7
          WHERE a.model_quantity='revenue_total' AND a.window_rank=0 AND a.end_date=a.anchor_end
          QUALIFY row_number() OVER (PARTITION BY a.group_id,a.anchor_start,a.anchor_end,a.unit,a.accounting_framework,a.reporting_scope
           ORDER BY b.end_date DESC)=1''')
