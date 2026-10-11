"""Keep scalar series on a dated reporting basis without currency conversion."""
import json
from .assembly import exclusion,rows


def select(db,source,target,as_of,identity=('group_id','model_quantity','period_start','period_end')):
    # Callers have already selected anchors within each unit/framework/scope
    # and applied their historical information cutoff. A later presentation
    # can supersede an old currency; simultaneous alternative bases cannot
    # be resolved by an arbitrary currency or framework preference.
    key=','.join(identity)
    match=' AND '.join(f't.{k} IS NOT DISTINCT FROM s.{k}' for k in identity)
    db.execute(f'''CREATE TEMP TABLE {target} AS
      WITH latest AS (SELECT *,dense_rank() OVER (PARTITION BY {key}
        ORDER BY acceptance_datetime DESC) AS basis_rank FROM {source})
      SELECT * EXCLUDE (basis_rank) FROM latest WHERE basis_rank=1
      QUALIFY count(*) OVER (PARTITION BY {key})=1''')
    omitted=rows(db,f'''SELECT s.*, EXISTS (SELECT 1 FROM {target} t
      WHERE {match}) AS resolved
      FROM {source} s WHERE NOT EXISTS (SELECT 1 FROM {target} t WHERE t.fact_id=s.fact_id AND {match})''')
    for row in omitted:
        exclusion(db,as_of,'superseded_reporting_basis' if row['resolved'] else 'conflicting_reporting_bases',
            'scalar_quantity_candidate',target+':'+row['fact_id']+':'+json.dumps([row.get(k) for k in identity],default=str),group_id=row['group_id'],
            detail=json.dumps({k:row.get(k) for k in set(identity)|{'fact_id','accession','model_quantity','period_start',
                'period_end','unit','currency','accounting_framework','reporting_scope','acceptance_datetime'}},default=str,sort_keys=True),
            invariant='no_currency_conversion_or_arbitrary_basis_tiebreak',
            coverage_state='policy_excluded' if row['resolved'] else 'conflicting')
