from pathlib import Path
from .database import sql_literal


def stocks(db,as_of:str):
    for view in ['as_known','revised']:
        timestamp='q.public_at' if view=='as_known' else sql_literal(as_of)+'::TIMESTAMPTZ'
        db.execute(f'''CREATE VIEW snapshot_stocks_{view} AS SELECT f.*,q.start_date AS quarter_start,q.end_date AS quarter_end,
          {timestamp} AS snapshot_at FROM eligible_instance_occurrences f
          JOIN quarter_cutoffs q ON q.group_id=f.group_id AND f.period_start IS NULL
           AND (f.period_end=q.end_date OR f.period_end=q.start_date-INTERVAL 1 DAY)
          JOIN anchor_order ao USING(model_quantity,canonical_concept)
          WHERE f.dimensions='{{}}' AND f.value IS NOT NULL AND f.coverage_state IN ('observed','explicit_zero')
           AND f.acceptance_datetime<={timestamp}
          QUALIFY row_number() OVER (PARTITION BY f.group_id,q.start_date,q.end_date,f.model_quantity,f.period_end,f.unit,
            f.accounting_framework,f.reporting_scope ORDER BY ao.priority,f.acceptance_datetime DESC,f.accession DESC,f.document_rank DESC,f.occurrence_rank DESC)=1''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,status,coverage_state,
          knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework,constant_perimeter)
         SELECT 'rpo_total',group_id,quarter_start,quarter_end,'{view}',snapshot_at,value,unit,currency,'computed','observed',
          knowledge_date,to_json([tier]),to_json([fact_id]),'reporting_entity',accounting_framework,
          CASE WHEN reporting_scope='as_if_combined' THEN 'as_if_combined' ELSE 'current' END
          FROM snapshot_stocks_{view} WHERE model_quantity='rpo_total' AND period_end=quarter_end''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,variant,value,unit,status,coverage_state,
          knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'receivables_collection_period',r.group_id,r.period_start,r.period_end,'{view}',r.snapshot_at,'receivables_only',
          exact_ratio6((opening.value+closing.value)*(r.period_end-r.period_start+1),r.value*2),'days',
          CASE WHEN r.value=0 THEN 'not_determinable' ELSE 'computed' END,'observed',r.knowledge_date,
          to_json([opening.tier,closing.tier,r.tier]),to_json([opening.fact_id,closing.fact_id]||from_json(r.lineage,'["VARCHAR"]')),
          'reporting_entity',r.accounting_framework FROM quarter_quantities_{view} r
          JOIN snapshot_stocks_{view} closing ON closing.group_id=r.group_id AND closing.quarter_start=r.period_start
           AND closing.quarter_end=r.period_end AND closing.model_quantity='receivables' AND closing.period_end=r.period_end AND closing.unit=r.unit
          JOIN snapshot_stocks_{view} opening ON opening.group_id=r.group_id AND opening.quarter_start=r.period_start
           AND opening.quarter_end=r.period_end AND opening.model_quantity='receivables' AND opening.period_end=r.period_start-INTERVAL 1 DAY AND opening.unit=r.unit
          WHERE r.model_quantity='revenue_total' AND r.value!=0 AND opening.accounting_framework=r.accounting_framework
           AND closing.accounting_framework=r.accounting_framework AND opening.reporting_scope=r.reporting_scope AND closing.reporting_scope=r.reporting_scope''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,status,coverage_state,
          knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'receivables_collection_period',r.group_id,r.period_start,r.period_end,'{view}',r.snapshot_at,
          exact_ratio6((ar_open.value+ar_close.value+ca_open.value+ca_close.value)*(r.period_end-r.period_start+1),r.value*2),'days','computed','observed',r.knowledge_date,
          to_json([ar_open.tier,ar_close.tier,ca_open.tier,ca_close.tier,r.tier]),
          to_json([ar_open.fact_id,ar_close.fact_id,ca_open.fact_id,ca_close.fact_id]||from_json(r.lineage,'["VARCHAR"]')),
          'reporting_entity',r.accounting_framework FROM quarter_quantities_{view} r
          JOIN snapshot_stocks_{view} ar_close ON ar_close.group_id=r.group_id AND ar_close.quarter_start=r.period_start AND ar_close.quarter_end=r.period_end
           AND ar_close.model_quantity='receivables' AND ar_close.period_end=r.period_end AND ar_close.unit=r.unit AND ar_close.reporting_scope=r.reporting_scope
          JOIN snapshot_stocks_{view} ar_open ON ar_open.group_id=r.group_id AND ar_open.quarter_start=r.period_start AND ar_open.quarter_end=r.period_end
           AND ar_open.model_quantity='receivables' AND ar_open.period_end=r.period_start-INTERVAL 1 DAY AND ar_open.unit=r.unit AND ar_open.reporting_scope=r.reporting_scope
          JOIN snapshot_stocks_{view} ca_close ON ca_close.group_id=r.group_id AND ca_close.quarter_start=r.period_start AND ca_close.quarter_end=r.period_end
           AND ca_close.model_quantity='contract_assets' AND ca_close.period_end=r.period_end AND ca_close.unit=r.unit AND ca_close.reporting_scope=r.reporting_scope
          JOIN snapshot_stocks_{view} ca_open ON ca_open.group_id=r.group_id AND ca_open.quarter_start=r.period_start AND ca_open.quarter_end=r.period_end
           AND ca_open.model_quantity='contract_assets' AND ca_open.period_end=r.period_start-INTERVAL 1 DAY AND ca_open.unit=r.unit AND ca_open.reporting_scope=r.reporting_scope
          WHERE r.model_quantity='revenue_total' AND r.value!=0 AND ar_open.accounting_framework=r.accounting_framework
           AND ar_close.accounting_framework=r.accounting_framework AND ca_open.accounting_framework=r.accounting_framework AND ca_close.accounting_framework=r.accounting_framework''')
        # Each investment component is published on its own, with its concept
        # and dimensions. Up/down adjustments never masquerade as a net total.
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,breakdown_key,value,unit,currency,status,coverage_state,
          knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'investment_gain_loss',f.group_id,f.period_start,f.period_end,'{view}',q.snapshot_at,'published',f.canonical_concept||'|'||f.dimensions,
          f.value,f.unit,f.currency,'computed','observed',f.knowledge_date,to_json([f.tier]),to_json([f.fact_id]),'reporting_entity',f.accounting_framework
          FROM eligible_instance_occurrences f JOIN quarter_quantities_{view} q ON q.group_id=f.group_id AND q.model_quantity='revenue_total'
           AND q.period_start=f.period_start AND q.period_end=f.period_end AND f.acceptance_datetime<=q.snapshot_at
          WHERE f.model_quantity='investment_gain_loss' AND f.value IS NOT NULL
          QUALIFY row_number() OVER (PARTITION BY f.group_id,f.period_start,f.period_end,f.canonical_concept,f.dimensions,f.unit
           ORDER BY f.acceptance_datetime DESC,f.accession DESC,f.document_rank DESC,f.occurrence_rank DESC)=1''')
        for term,endpoint in [('opening','quarter_start-INTERVAL 1 DAY'),('closing','quarter_end')]:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,currency,
              status,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework,overlap_possible)
             SELECT 'lease_not_commenced_bridge',group_id,quarter_start,quarter_end,'{view}',snapshot_at,'{term}',value,unit,currency,
              'computed',coverage_state,knowledge_date,to_json([tier]),to_json([fact_id]),'reporting_entity',accounting_framework,true
              FROM snapshot_stocks_{view} WHERE model_quantity='lease_not_commenced' AND period_end={endpoint}''')


def tagged_components(db,as_of):
    buckets={
      'UnrecordedUnconditionalPurchaseObligationToBePaidInRemainderOfFiscalYear':'FY_remainder',
      'UnrecordedUnconditionalPurchaseObligationBalanceOnFirstAnniversary':'FY1',
      'UnrecordedUnconditionalPurchaseObligationBalanceOnSecondAnniversary':'FY2',
      'UnrecordedUnconditionalPurchaseObligationBalanceOnThirdAnniversary':'FY3',
      'UnrecordedUnconditionalPurchaseObligationBalanceOnFourthAnniversary':'FY4',
      'UnrecordedUnconditionalPurchaseObligationBalanceOnFifthAnniversary':'FY5',
      'UnrecordedUnconditionalPurchaseObligationDueAfterFiveYears':'later'}
    db.execute('CREATE TEMP TABLE purchase_buckets (canonical_concept VARCHAR,bucket VARCHAR)')
    db.executemany('INSERT INTO purchase_buckets VALUES (?,?)',[('us-gaap:'+c,b) for c,b in buckets.items()])
    for view in ('as_known','revised'):
        stamp='q.public_at' if view=='as_known' else sql_literal(as_of)+'::TIMESTAMPTZ'
        db.execute(f'''INSERT INTO measures
          (measure,group_id,period_start,period_end,view,as_of,breakdown_key,value,unit,currency,status,coverage_state,
           knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework,overlap_possible)
          SELECT 'exposure_matrix',f.group_id,q.start_date,q.end_date,'{view}',{stamp},
           'contractual_outflows|'||CASE WHEN EXISTS (SELECT 1 FROM eligible_instance_occurrences parent
             WHERE parent.accession=f.accession AND parent.model_quantity='lease_not_commenced')
            THEN 'lease_not_commenced' ELSE 'purchase_obligation' END||'|undiscounted|'||b.bucket||'|'||f.dimensions,
           f.value,f.unit,f.currency,'computed',f.coverage_state,f.knowledge_date,to_json([f.tier]),to_json([f.fact_id]),
           'reporting_entity',f.accounting_framework,true FROM eligible_instance_occurrences f
          JOIN quarter_cutoffs q ON f.group_id=q.group_id AND f.period_end=q.end_date AND f.period_start IS NULL
          JOIN purchase_buckets b USING(canonical_concept)
          WHERE f.value IS NOT NULL AND f.acceptance_datetime<={stamp}
          QUALIFY row_number() OVER (PARTITION BY f.group_id,q.start_date,q.end_date,b.bucket,f.dimensions,f.unit,
           f.accounting_framework,f.reporting_scope ORDER BY f.acceptance_datetime DESC,f.accession DESC,f.document_rank DESC,f.occurrence_rank DESC)=1''')
        for measure,quantity in [('customer_concentration_anonymous','concentration_risk_percentage'),('investment_impairment','investment_impairment')]:
            additional="""AND json_extract_string(f.dimensions,'$.\"us-gaap:ConcentrationRiskByTypeAxis\"')='us-gaap:CustomerConcentrationRiskMember'
                AND json_extract_string(f.dimensions,'$.\"us-gaap:ConcentrationRiskByBenchmarkAxis\"') IN
                  ('us-gaap:SalesRevenueNetMember','us-gaap:RevenuesMember','us-gaap:RevenueFromContractWithCustomerExcludingAssessedTaxMember','us-gaap:RevenueFromContractWithCustomerMember')
                AND regexp_matches(json_extract_string(f.dimensions,'$.\"srt:MajorCustomersAxis\"'),':(?:Customer|Distributor)[A-Z0-9]+Member$')""" if measure=='customer_concentration_anonymous' else ''
            db.execute(f'''INSERT INTO measures
             (measure,group_id,period_start,period_end,view,as_of,breakdown_key,value,unit,currency,status,coverage_state,
              knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{measure}',f.group_id,f.period_start,f.period_end,'{view}',{stamp},f.canonical_concept||'|'||f.dimensions,
              f.value,f.unit,f.currency,'computed',f.coverage_state,f.knowledge_date,to_json([f.tier]),to_json([f.fact_id]),
              'reporting_entity',f.accounting_framework FROM eligible_instance_occurrences f
             JOIN quarter_cutoffs q ON q.group_id=f.group_id AND q.start_date=f.period_start AND q.end_date=f.period_end
             WHERE f.model_quantity='{quantity}' AND f.value IS NOT NULL AND f.acceptance_datetime<={stamp} {additional}
              QUALIFY row_number() OVER (PARTITION BY f.group_id,f.period_start,f.period_end,f.canonical_concept,f.dimensions,f.unit
               ORDER BY f.acceptance_datetime DESC,f.accession DESC,f.document_rank DESC,f.occurrence_rank DESC)=1''')
        # ISO durations are preserved in facts. Months can be calculated exactly
        # when no day/time component is published; PnD is not estimated in years.
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,breakdown_key,value,unit,status,coverage_state,
          knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'depreciation_life_published',f.group_id,q.start_date,q.end_date,'{view}',{stamp},f.dimensions,
          coalesce(try_cast(regexp_extract(f.text_value,'([0-9]+)Y',1) AS DECIMAL(38,6)),0)*12+
          coalesce(try_cast(regexp_extract(f.text_value,'([0-9]+)M',1) AS DECIMAL(38,6)),0),'months','computed','observed',
          f.knowledge_date,to_json([f.tier]),to_json([f.fact_id]),'reporting_entity',f.accounting_framework
          FROM eligible_facts f JOIN quarter_cutoffs q ON q.group_id=f.group_id AND f.period_end=q.end_date
          WHERE f.model_quantity='depreciation_life_published' AND regexp_full_match(f.text_value,'P([0-9]+Y([0-9]+M)?|[0-9]+M)')
           AND f.acceptance_datetime<={stamp}
          QUALIFY row_number() OVER (PARTITION BY f.group_id,q.start_date,q.end_date,f.dimensions
           ORDER BY f.acceptance_datetime DESC,f.accession DESC,f.document_rank DESC,f.occurrence_rank DESC)=1''')


def liquidity_and_leases(db,as_of):
    for view in ('as_known','revised'):
        source='snapshot_stocks_'+view
        db.execute(f'''INSERT INTO measures
         (measure,group_id,period_start,period_end,view,as_of,term,variant,value,unit,numerator,denominator,status,nd_reason,
          coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'liq_principal_due_to_cash',debt.group_id,debt.quarter_start,debt.quarter_end,'{view}',debt.snapshot_at,
          'horizon_12m','cash_only_long_term_principal',exact_ratio6(debt.value,cash.value),'ratio',debt.value,cash.value,
          CASE WHEN cash.value=0 THEN 'not_determinable' ELSE 'partial' END,
          CASE WHEN cash.value=0 THEN 'denominator_zero' ELSE 'short_term_principal_not_included' END,
          'observed',greatest(debt.knowledge_date,cash.knowledge_date),to_json([debt.tier,cash.tier]),to_json([debt.fact_id,cash.fact_id]),
          'reporting_entity',debt.accounting_framework FROM {source} debt JOIN {source} cash ON debt.group_id=cash.group_id
           AND debt.quarter_start=cash.quarter_start AND debt.quarter_end=cash.quarter_end AND debt.period_end=cash.period_end
           AND debt.unit=cash.unit AND debt.reporting_scope=cash.reporting_scope AND debt.accounting_framework=cash.accounting_framework
          JOIN fiscal_quarters fiscal ON debt.group_id=fiscal.group_id AND debt.quarter_start=fiscal.start_date AND debt.quarter_end=fiscal.end_date
          WHERE debt.model_quantity='debt_principal_due_next_fiscal_year' AND debt.period_end=debt.quarter_end
           AND cash.model_quantity='cash_and_equivalents' AND debt.quarter_end IN
            (SELECT max(end_date) FROM fiscal_quarters samefy WHERE samefy.group_id=debt.group_id
              AND samefy.fy_start=fiscal.fy_start GROUP BY samefy.fy_start)
           AND fiscal.q_number=4''')
        db.execute(f'''INSERT INTO measures
         (measure,group_id,period_start,period_end,view,as_of,term,value,unit,numerator,denominator,status,nd_reason,
          coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         WITH lease AS (SELECT group_id,quarter_start,quarter_end,snapshot_at,unit,accounting_framework,reporting_scope,
           sum(value) AS value,count(DISTINCT model_quantity) AS terms,max(knowledge_date) AS knowledge_date,
           list(fact_id) AS lineage,list(tier) AS tiers FROM {source}
          WHERE period_end=quarter_end AND model_quantity IN ('operating_lease_liability_current','operating_lease_liability_noncurrent',
           'finance_lease_liability_current','finance_lease_liability_noncurrent') GROUP BY ALL)
         SELECT 'lev_debt_and_leases_to_operating_income_plus_da',lease.group_id,lease.quarter_start,lease.quarter_end,'{view}',lease.snapshot_at,
          'leases',exact_ratio6(lease.value,op.value+da.value),'ratio',lease.value,op.value+da.value,
          CASE WHEN op.value+da.value=0 THEN 'not_determinable' ELSE 'computed' END,
          CASE WHEN op.value+da.value=0 THEN 'denominator_zero' END,'observed',greatest(lease.knowledge_date,op.knowledge_date,da.knowledge_date),
          to_json([lease.tiers,from_json(op.evidence_profile,'["VARCHAR"]'),from_json(da.evidence_profile,'["VARCHAR"]')]),
          to_json(lease.lineage||from_json(op.lineage,'["VARCHAR"]')||from_json(da.lineage,'["VARCHAR"]')),'reporting_entity',lease.accounting_framework
          FROM lease JOIN ttm_quantities_{view} op ON lease.group_id=op.group_id AND lease.quarter_start=op.anchor_start
           AND lease.quarter_end=op.anchor_end AND op.window_rank=0 AND op.model_quantity='operating_income' AND lease.unit=op.unit
           AND lease.reporting_scope=op.reporting_scope AND lease.accounting_framework=op.accounting_framework
          JOIN ttm_quantities_{view} da ON da.group_id=op.group_id AND da.anchor_start=op.anchor_start AND da.anchor_end=op.anchor_end
           AND da.model_quantity='depreciation_amortization' AND da.window_rank=0 AND da.unit=op.unit
           AND da.reporting_scope=op.reporting_scope AND da.accounting_framework=op.accounting_framework
          WHERE lease.terms=4''')
