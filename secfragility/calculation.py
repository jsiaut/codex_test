from __future__ import annotations
from decimal import Decimal
from pathlib import Path
import json
from .database import sql_literal


def prepare_views(db,root: Path,as_of: str):
    db.execute((root/'queries.sql').read_text())
    db.execute(f'''CREATE VIEW selected_as_known AS SELECT * FROM eligible_facts
        WHERE knowledge_date<=CAST({sql_literal(as_of)} AS TIMESTAMPTZ)::DATE
        QUALIFY row_number() OVER (PARTITION BY semantic_key ORDER BY acceptance_datetime DESC,
          accession DESC,document_rank DESC,occurrence_rank DESC)=1''')
    # An anchor preference is fixed by its order in config BEFORE seeing any
    # control. Ambiguity within a chosen concept remains a conflict.
    import yaml
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    from .mapping import SUPPLEMENTAL_ANCHORS
    replacements=json.loads((root/'work/deprecations.json').read_text())['mapping'] if (root/'work/deprecations.json').exists() else {}
    db.execute('CREATE TEMP TABLE anchor_order (model_quantity VARCHAR,canonical_concept VARCHAR,priority INTEGER)')
    rows=[(q,replacements.get('us-gaap:'+c,'us-gaap:'+c),p) for q,cs in dict(cfg['concept_anchors'],**cfg.get('concept_anchors_to_verify',{}),**SUPPLEMENTAL_ANCHORS).items() for p,c in enumerate(cs)]
    db.executemany('INSERT INTO anchor_order VALUES (?,?,?)',rows)
    for view in ('as_known','revised'):
        db.execute(f'''CREATE VIEW quantities_{view} AS
          SELECT f.* FROM selected_{view} f JOIN anchor_order a USING(model_quantity,canonical_concept)
          WHERE dimensions='{{}}' AND coverage_state IN ('observed','explicit_zero') AND value IS NOT NULL
          QUALIFY row_number() OVER (PARTITION BY group_id,model_quantity,period_start,period_end,unit,
            accounting_framework,reporting_scope ORDER BY priority,acceptance_datetime DESC,accession DESC,
            document_rank DESC,occurrence_rank DESC)=1''')


def ratio_measures(db,as_of: str):
    """Exact SQL ratios on published standalone periods; no fabricated terms."""
    for view in ('as_known','revised'):
        for measure,numerator,denominator,term in [('capex_to_cfo','capex_cash','cfo','without'),
                ('operating_margin','operating_income','revenue_total','none'),
                ('gross_margin','gross_profit','revenue_total','none'),
                ('capex_to_revenue','capex_cash','revenue_total','none')]:
            db.execute(f'''INSERT INTO measures
             (measure,group_id,period_start,period_end,view,as_of,term,value,unit,numerator,denominator,
              status,nd_reason,coverage_state,knowledge_date,evidence_profile,lineage,
              source_perspective,accounting_framework)
             SELECT {sql_literal(measure)},a.group_id,a.period_start,a.period_end,{sql_literal(view)},
              {sql_literal(as_of)}::TIMESTAMPTZ,{sql_literal(term)},
              exact_ratio6(a.value,b.value),'ratio',a.value,b.value,
              CASE WHEN b.value=0 THEN 'not_determinable' ELSE 'computed' END,
              CASE WHEN b.value=0 THEN 'denominator_zero' ELSE NULL END,'observed',
              greatest(a.knowledge_date,b.knowledge_date),
              to_json(map(['numerator','denominator'],[CAST(a.tier AS VARCHAR),CAST(b.tier AS VARCHAR)])),
              to_json([a.fact_id,b.fact_id]),'reporting_entity',a.accounting_framework
             FROM quantities_{view} a JOIN quantities_{view} b ON a.group_id=b.group_id AND
               a.period_start=b.period_start AND a.period_end=b.period_end AND a.currency=b.currency
               AND a.accounting_framework=b.accounting_framework AND a.reporting_scope=b.reporting_scope
             WHERE a.model_quantity={sql_literal(numerator)} AND b.model_quantity={sql_literal(denominator)}
              AND a.period_start IS NOT NULL''')
        db.execute(f'''INSERT INTO measures
          (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,status,coverage_state,
           knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
          SELECT 'fcf_basic',a.group_id,a.period_start,a.period_end,{sql_literal(view)},
           {sql_literal(as_of)}::TIMESTAMPTZ,a.value-b.value,a.unit,a.currency,'computed','observed',
           greatest(a.knowledge_date,b.knowledge_date),to_json([a.tier,b.tier]),
           to_json([a.fact_id,b.fact_id]),'reporting_entity',a.accounting_framework
          FROM quantities_{view} a JOIN quantities_{view} b ON a.group_id=b.group_id AND
           a.period_start=b.period_start AND a.period_end=b.period_end AND a.currency=b.currency
           AND a.accounting_framework=b.accounting_framework AND a.reporting_scope=b.reporting_scope
          WHERE a.model_quantity='cfo' AND b.model_quantity='capex_cash' AND a.period_start IS NOT NULL''')


def controls_not_yet_testable(db,groups: list[str],periods: list[tuple],as_of: str):
    from .database import CONTROL_IDS
    rows=[(c,g,start,end,'as_known',as_of,'not_testable','none','control_not_implemented', '[]')
        for c in CONTROL_IDS for g in groups for start,end in periods]
    db.executemany('''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,status,tolerance_basis,explanation_code,evidence)
      VALUES (?,?,?,?,?,?,?,?,?,?)''',rows)


def core_calibration(db,root: Path,as_of: str):
    # This function is an intermediate calibration, not a publication pipeline.
    prepare_views(db,root,as_of)
    ratio_measures(db,as_of)
