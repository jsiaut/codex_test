"""Additional rank-one quantities, with missing terms left missing."""
from .database import sql_literal


def run(db,as_of):
    for view in ['as_known','revised']:
        q='quarter_quantities_'+view;s='snapshot_stocks_'+view
        # Standalone quarterly expense and cash measures.
        for measure,quantity in [('capitalized_interest','capitalized_interest'),('cov_pik_interest','pik_interest'),
             ('finance_lease_additions','rou_obtained_finance_lease'),('operating_lease_rou_additions','rou_obtained_operating_lease')]:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,
              status,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{measure}',group_id,period_start,period_end,'{view}',snapshot_at,value,unit,currency,'computed','observed',
              knowledge_date,to_json([tier]),lineage,'reporting_entity',accounting_framework FROM {q} WHERE model_quantity='{quantity}' ''')
        for metric,quantity,term in [('eq_equity_and_accumulated_deficit','equity_including_nci','equity'),
            ('eq_equity_and_accumulated_deficit','retained_earnings','accumulated_deficit'),
            ('working_capital','receivables','receivables'),('working_capital','inventories','inventories'),
            ('working_capital','accounts_payable','payables'),('working_capital','contract_liabilities_current','contract_liabilities'),
            ]:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,currency,
             status,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{metric}',group_id,quarter_start,quarter_end,'{view}',snapshot_at,'{term}',value,unit,currency,
              'computed','observed',knowledge_date,to_json([tier]),to_json([fact_id]),'reporting_entity',accounting_framework
              FROM {s} WHERE model_quantity='{quantity}' AND period_end=quarter_end''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,currency,
          status,nd_reason,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'working_capital',group_id,period_start,period_end,'{view}',as_of,'net',
          sum(CASE WHEN term IN ('receivables','inventories') THEN value ELSE -value END),unit,currency,
          CASE WHEN count(DISTINCT term)=4 THEN 'computed' ELSE 'partial' END,
          CASE WHEN count(DISTINCT term)<4 THEN 'missing_working_capital_terms' END,'observed',max(knowledge_date),
          to_json(list(evidence_profile)),to_json(flatten(list(from_json(lineage,'["VARCHAR"]')))),'reporting_entity',accounting_framework
          FROM measures WHERE measure='working_capital' AND view='{view}' AND term IN ('receivables','inventories','payables','contract_liabilities') GROUP BY ALL''')
        db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,value,unit,currency,status,
          coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
         SELECT 'fcf_after_sbc',a.group_id,a.period_start,a.period_end,'{view}',a.snapshot_at,a.value-b.value-c.value,a.unit,a.currency,
          'computed','observed',greatest(a.knowledge_date,b.knowledge_date,c.knowledge_date),to_json([a.tier,b.tier,c.tier]),
          to_json(from_json(a.lineage,'["VARCHAR"]')||from_json(b.lineage,'["VARCHAR"]')||from_json(c.lineage,'["VARCHAR"]')),
          'reporting_entity',a.accounting_framework FROM {q} a JOIN {q} b ON a.group_id=b.group_id AND a.period_start=b.period_start
           AND a.period_end=b.period_end AND a.unit=b.unit AND a.reporting_scope=b.reporting_scope AND a.accounting_framework=b.accounting_framework
          JOIN {q} c ON c.group_id=a.group_id AND c.period_start=a.period_start AND c.period_end=a.period_end AND c.unit=a.unit
           AND c.reporting_scope=a.reporting_scope AND c.accounting_framework=a.accounting_framework
          WHERE a.model_quantity='cfo' AND b.model_quantity='capex_cash' AND c.model_quantity='sbc_expense' ''')
        for metric,a,b,term,subtract in [('sbc_to_cfo','sbc_expense','cfo','none',False),
            ('cov_interest_coverage','operating_income','interest_expense','without',False),
            ('cfo_net_income_gap','cfo','net_income','none',True)]:
            db.execute(f'''INSERT INTO measures (measure,group_id,period_start,period_end,view,as_of,term,value,unit,currency,numerator,denominator,
              status,nd_reason,coverage_state,knowledge_date,evidence_profile,lineage,source_perspective,accounting_framework)
             SELECT '{metric}',a.group_id,a.period_start,a.period_end,'{view}',a.snapshot_at,'{term}',
              {'a.value-b.value' if subtract else 'exact_ratio6(a.value,b.value)'},
              {'a.unit' if subtract else "'ratio'"},{'a.currency' if subtract else 'NULL'},a.value,b.value,
              CASE WHEN {'false' if subtract else 'b.value=0'} THEN 'not_determinable' ELSE 'computed' END,
              CASE WHEN {'false' if subtract else 'b.value=0'} THEN 'denominator_zero' END,'observed',greatest(a.knowledge_date,b.knowledge_date),
              to_json([a.tier,b.tier]),to_json(from_json(a.lineage,'["VARCHAR"]')||from_json(b.lineage,'["VARCHAR"]')),
              'reporting_entity',a.accounting_framework FROM {q} a JOIN {q} b ON a.group_id=b.group_id AND a.period_start=b.period_start
               AND a.period_end=b.period_end AND a.unit=b.unit AND a.reporting_scope=b.reporting_scope AND a.accounting_framework=b.accounting_framework
              WHERE a.model_quantity='{a}' AND b.model_quantity='{b}' ''')
