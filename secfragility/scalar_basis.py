"""Keep scalar series on a dated reporting basis without currency conversion."""
import json
from .assembly import exclusion,rows


def select(db,source,target,as_of):
    # Callers have already selected anchors within each unit/framework/scope
    # and applied their historical information cutoff. A later presentation
    # can supersede an old currency; simultaneous alternative bases cannot
    # be resolved by an arbitrary currency or framework preference.
    key='group_id,model_quantity,period_start,period_end'
    db.execute(f'''CREATE TEMP TABLE {target} AS
      WITH latest AS (SELECT *,dense_rank() OVER (PARTITION BY {key}
        ORDER BY acceptance_datetime DESC) AS basis_rank FROM {source})
      SELECT * EXCLUDE (basis_rank) FROM latest WHERE basis_rank=1
      QUALIFY count(*) OVER (PARTITION BY {key})=1''')
    omitted=rows(db,f'''SELECT s.*, EXISTS (SELECT 1 FROM {target} t
      WHERE t.group_id=s.group_id AND t.model_quantity=s.model_quantity
       AND t.period_start IS NOT DISTINCT FROM s.period_start AND t.period_end=s.period_end) AS resolved
      FROM {source} s WHERE NOT EXISTS (SELECT 1 FROM {target} t WHERE t.fact_id=s.fact_id)''')
    for row in omitted:
        exclusion(db,as_of,'superseded_reporting_basis' if row['resolved'] else 'conflicting_reporting_bases',
            'scalar_quantity_candidate',target+':'+row['fact_id'],group_id=row['group_id'],
            detail=json.dumps({k:row.get(k) for k in ['fact_id','accession','model_quantity','period_start',
                'period_end','unit','currency','accounting_framework','reporting_scope','acceptance_datetime']},default=str),
            invariant='no_currency_conversion_or_arbitrary_basis_tiebreak',
            coverage_state='policy_excluded' if row['resolved'] else 'conflicting')
