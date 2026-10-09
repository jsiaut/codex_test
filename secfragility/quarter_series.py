"""Quarter differencing uses compatible dated inputs and excludes future filings."""
from pathlib import Path
import json
from .database import sql_literal


def prepare(db,root:Path,as_of:str):
    universe=json.loads((root/'work/expected_universe.json').read_text())
    db.execute('CREATE TEMP TABLE fiscal_quarters (group_id VARCHAR,start_date DATE,end_date DATE,fy_start DATE,q_number INTEGER)')
    rows=[(q['group_id'],q['period_start'],q['period_end'],q.get('fiscal_year_start'),q.get('quarter_number'))
        for q in universe['quarters'] if q['period_start']!='none' and q['period_end']!='none']
    if rows:db.executemany('INSERT INTO fiscal_quarters VALUES (?,?,?,?,?)',rows)
    db.execute('''CREATE VIEW periodic_occurrences AS
      SELECT f.* FROM eligible_instance_occurrences f JOIN documents d USING(document_id)
       WHERE d.form IN ('10-K','10-K/A','10-KT','10-Q','10-Q/A','10-QT') AND f.dimensions='{}'
        AND f.coverage_state IN ('observed','explicit_zero') AND f.value IS NOT NULL
        AND f.model_quantity IS NOT NULL''')
    # Each quarter has a historical information date: the first periodic filing
    # with its period end. This is a publication snapshot, separately from the
    # annual-deadline cutoffs required for Annex E.
    db.execute('''CREATE VIEW quarter_cutoffs AS SELECT q.group_id,q.start_date,q.end_date,
      min(d.acceptance_datetime) AS public_at FROM fiscal_quarters q JOIN documents d ON d.group_id=q.group_id
      JOIN periodic_occurrences f ON f.document_id=d.document_id AND f.period_end=q.end_date
      WHERE d.form IN ('10-K','10-KT','10-Q','10-QT') AND f.period_start IS NOT NULL GROUP BY ALL''')
    db.execute('''CREATE VIEW quarter_candidates AS
      SELECT q.group_id,q.start_date AS period_start,q.end_date AS period_end,a.model_quantity,
       a.unit,a.currency,a.accounting_framework,a.reporting_scope,a.accession,a.acceptance_datetime,a.knowledge_date,
       a.document_rank,a.occurrence_rank,a.canonical_concept,a.tier,
       CASE WHEN a.period_start=q.start_date THEN a.value ELSE a.value-b.value END AS value,
       CASE WHEN a.period_start=q.start_date THEN to_json([a.fact_id]) ELSE to_json([a.fact_id,b.fact_id]) END AS lineage,
       CASE WHEN a.period_start=q.start_date THEN 'direct_quarter'
        ELSE 'ytd_difference_latest_inputs_known_at_deposit' END AS calculation_basis
      FROM fiscal_quarters q JOIN periodic_occurrences a ON a.group_id=q.group_id AND a.period_end=q.end_date
      LEFT JOIN periodic_occurrences b ON b.group_id=a.group_id AND b.canonical_concept=a.canonical_concept
       AND b.period_start=a.period_start AND b.period_end=q.start_date-INTERVAL 1 DAY AND b.unit=a.unit
       AND b.accounting_framework=a.accounting_framework AND b.reporting_scope=a.reporting_scope
       AND b.acceptance_datetime<=a.acceptance_datetime
      WHERE (a.period_start=q.start_date OR (a.period_start=q.fy_start AND b.value IS NOT NULL))
      QUALIFY row_number() OVER (PARTITION BY a.fact_id,q.start_date,q.end_date ORDER BY
       CASE WHEN b.accession=a.accession THEN 0 ELSE 1 END,b.acceptance_datetime DESC,b.accession DESC,b.occurrence_rank DESC)=1''')
    for view in ['as_known','revised']:
        cutoff='AND a.acceptance_datetime<=k.public_at' if view=='as_known' else ''
        snapshot='k.public_at' if view=='as_known' else sql_literal(as_of)+'::TIMESTAMPTZ'
        db.execute(f'''CREATE VIEW quarter_quantities_{view} AS SELECT a.*,{snapshot} AS snapshot_at FROM quarter_candidates a
          JOIN anchor_order ao USING(model_quantity,canonical_concept)
          LEFT JOIN quarter_cutoffs k ON k.group_id=a.group_id AND k.start_date=a.period_start AND k.end_date=a.period_end
          WHERE a.acceptance_datetime<={sql_literal(as_of)}::TIMESTAMPTZ {cutoff}
          QUALIFY row_number() OVER (PARTITION BY a.group_id,a.model_quantity,a.period_start,a.period_end,a.unit,a.accounting_framework,a.reporting_scope
           ORDER BY CASE WHEN calculation_basis='direct_quarter' THEN 0 ELSE 1 END,ao.priority,
            a.acceptance_datetime DESC,a.accession DESC,a.document_rank DESC,a.occurrence_rank DESC)=1''')


def measures(db,as_of):
    # Initial calibration YTD ratios are not the published quarterly series.
    db.execute("DELETE FROM measures WHERE measure IN ('capex_to_cfo','fcf_basic','capex_to_revenue','gross_margin','operating_margin')")
    stamp=sql_literal(as_of)+'::TIMESTAMPTZ'
    for view in ['as_known','revised']:
        source='quarter_quantities_'+view
        stamp='a.snapshot_at' if view=='as_known' else sql_literal(as_of)+'::TIMESTAMPTZ'
        for quantity in ['revenue_total','cfo','capex_cash','finance_lease_principal_payments']:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,status,coverage_state,
              knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{quantity}',group_id,period_start,period_end,'{view}',{stamp},value,unit,currency,'computed','observed',knowledge_date,
              to_json([tier]),lineage,'reporting_entity',accounting_framework FROM {source} a WHERE model_quantity='{quantity}' ''')
        for measure,a,b,term in [('capex_to_cfo','capex_cash','cfo','without'),('capex_to_revenue','capex_cash','revenue_total','none'),
              ('gross_margin','gross_profit','revenue_total','none'),('operating_margin','operating_income','revenue_total','none')]:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,numerator,denominator,status,nd_reason,
             coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{measure}',a.group_id,a.period_start,a.period_end,'{view}',{stamp},'{term}',exact_ratio6(a.value,b.value),'ratio',a.value,b.value,
              CASE WHEN b.value=0 THEN 'not_determinable' ELSE 'computed' END,CASE WHEN b.value=0 THEN 'denominator_zero' END,'observed',
              greatest(a.knowledge_date,b.knowledge_date),to_json([a.tier,b.tier]),to_json(list_concat(from_json(a.lineage,'["VARCHAR"]'),from_json(b.lineage,'["VARCHAR"]'))),
              'reporting_entity',a.accounting_framework FROM {source} a JOIN {source} b ON a.group_id=b.group_id AND a.period_start=b.period_start
               AND a.period_end=b.period_end AND a.unit=b.unit AND a.accounting_framework=b.accounting_framework AND a.reporting_scope=b.reporting_scope
              WHERE a.model_quantity='{a}' AND b.model_quantity='{b}' ''')
        for measure,subtrahend in [('fcf_basic','capex_cash'),('fcf_after_finance_leases','finance_lease_principal_payments')]:
            minuend='cfo' if measure=='fcf_basic' else 'fcf_basic'
            left=source if measure=='fcf_basic' else 'measures'
            condition=f"a.model_quantity='{minuend}'" if measure=='fcf_basic' else f"a.measure='{minuend}' AND a.view='{view}' AND a.status='computed'"
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,status,coverage_state,
             knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{measure}',a.group_id,a.period_start,a.period_end,'{view}',{'a.as_of' if view=='as_known' else stamp},a.value-b.value,a.unit,a.currency,'computed','observed',
              greatest(a.knowledge_date,b.knowledge_date),to_json([a.evidence_profile,b.tier::VARCHAR]) {'' if measure!='fcf_basic' else ''},
              to_json(list_concat(from_json(a.lineage,'["VARCHAR"]'),from_json(b.lineage,'["VARCHAR"]'))),'reporting_entity',a.accounting_framework
              FROM {left} a JOIN {source} b ON a.group_id=b.group_id AND CAST(a.period_start AS DATE)=b.period_start
               AND CAST(a.period_end AS DATE)=b.period_end AND a.unit=b.unit AND a.accounting_framework=b.accounting_framework
              WHERE {condition} AND b.model_quantity='{subtrahend}' ''') if measure!='fcf_basic' else db.execute(f'''INSERT INTO measures
               (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,status,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
               SELECT 'fcf_basic',a.group_id,a.period_start,a.period_end,'{view}',{stamp},a.value-b.value,a.unit,a.currency,'computed','observed',
                greatest(a.knowledge_date,b.knowledge_date),to_json([a.tier,b.tier]),to_json(list_concat(from_json(a.lineage,'["VARCHAR"]'),from_json(b.lineage,'["VARCHAR"]'))),
                'reporting_entity',a.accounting_framework FROM {source} a JOIN {source} b ON a.group_id=b.group_id AND a.period_start=b.period_start
                AND a.period_end=b.period_end AND a.unit=b.unit AND a.accounting_framework=b.accounting_framework AND a.reporting_scope=b.reporting_scope
                WHERE a.model_quantity='cfo' AND b.model_quantity='capex_cash' ''')
        # Year-over-year comparison must have a comparable period length.
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,numerator,denominator,status,nd_reason,coverage_state,
         knowledge_date,evidence_profile,lineage,unequal_period_length,source_perspective,accounting_framework)
         SELECT 'revenue_growth',a.group_id,a.period_start,a.period_end,'{view}',{stamp},'yoy',exact_ratio6(a.value-b.value,b.value),'ratio',a.value-b.value,b.value,
          CASE WHEN b.value=0 THEN 'not_determinable' ELSE 'computed' END,CASE WHEN b.value=0 THEN 'denominator_zero' END,'observed',a.knowledge_date,
          to_json([a.tier,b.tier]),to_json(list_concat(from_json(a.lineage,'["VARCHAR"]'),from_json(b.lineage,'["VARCHAR"]'))),
          (a.period_end-a.period_start)!=(b.period_end-b.period_start),'reporting_entity',a.accounting_framework
         FROM {source} a JOIN quarter_candidates b ON a.group_id=b.group_id AND a.model_quantity=b.model_quantity AND a.unit=b.unit
          AND a.accounting_framework=b.accounting_framework AND a.reporting_scope=b.reporting_scope
          AND a.period_end-b.period_end BETWEEN 350 AND 380 AND abs((a.period_end-a.period_start)-(b.period_end-b.period_start))<=7
          AND b.acceptance_datetime<=a.acceptance_datetime
         WHERE a.model_quantity='revenue_total'
         QUALIFY row_number() OVER (PARTITION BY a.group_id,a.period_start,a.period_end,a.unit
          ORDER BY CASE WHEN b.accession=a.accession THEN 0 ELSE 1 END,b.acceptance_datetime DESC,b.accession DESC)=1''')
