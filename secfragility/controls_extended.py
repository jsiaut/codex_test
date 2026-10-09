from pathlib import Path
from .database import sql_literal
from .controls import calculation_arcs
import json


def run(db,root:Path,collection:dict,as_of:str):
    stamp=sql_literal(as_of)+'::TIMESTAMPTZ'
    # Ratios are cross-multiplied. DECIMAL arithmetic never performs a FLOAT
    # division to decide whether an accounting equation is within precision.
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      WITH q AS (
       SELECT f.group_id,f.accession,f.period_end,f.unit,f.accounting_framework,
        max(value) FILTER (WHERE model_quantity='cash_and_restricted_cash_total') AS cf_cash,
        sum(value) FILTER (WHERE model_quantity IN ('cash_and_equivalents','restricted_cash_current','restricted_cash_noncurrent')) AS bs_cash,
        count(DISTINCT model_quantity) AS terms,count(p.half_unit) AS precisions,sum(p.half_unit) AS tolerance,
        to_json(list(f.fact_id)) AS evidence,max(f.acceptance_datetime) AS accepted
       FROM eligible_instance_occurrences f LEFT JOIN precision_units p USING(decimals)
       WHERE dimensions='{{}}' AND period_start IS NULL AND value IS NOT NULL
        AND model_quantity IN ('cash_and_restricted_cash_total','cash_and_equivalents','restricted_cash_current','restricted_cash_noncurrent')
       GROUP BY ALL
      ) SELECT 'c3_cash_reconciliation',group_id,period_end,period_end,'as_known',{stamp},unit,
       CASE WHEN terms<4 OR precisions<terms THEN 'not_testable' WHEN abs(cf_cash-bs_cash)<=tolerance THEN 'ok' ELSE 'mismatch' END,
       bs_cash,cf_cash,bs_cash-cf_cash,tolerance,'instance',
       CASE WHEN terms<4 THEN 'restricted_cash_component_not_explicitly_disclosed' WHEN precisions<terms THEN 'precision_missing'
        WHEN abs(cf_cash-bs_cash)>tolerance THEN 'cash_definition_residual' END,evidence
       FROM q QUALIFY row_number() OVER (PARTITION BY group_id,period_end,unit ORDER BY accepted DESC,accession DESC)=1''')
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      WITH distinct_deposits AS (
       SELECT f.*,p.half_unit FROM eligible_instance_occurrences f LEFT JOIN precision_units p USING(decimals)
       WHERE value IS NOT NULL AND knowledge_date<={stamp}::DATE
      ), comparisons AS (
       SELECT *,lag(value) OVER w AS prior_value,lag(half_unit) OVER w AS prior_precision,
        lag(fact_id) OVER w AS prior_fact,lag(accession) OVER w AS prior_accession FROM distinct_deposits
       WINDOW w AS (PARTITION BY semantic_key ORDER BY acceptance_datetime,accession,document_rank,occurrence_rank)
      ) SELECT 'c4_restatement_detection',group_id,coalesce(period_start,period_end),period_end,'as_known',{stamp},semantic_key||'|'||accession,
       CASE WHEN half_unit IS NULL OR prior_precision IS NULL THEN 'not_testable' ELSE 'ok' END,
       value,prior_value,value-prior_value,half_unit+prior_precision,'instance',
       CASE WHEN half_unit IS NULL OR prior_precision IS NULL THEN 'precision_missing'
        WHEN abs(value-prior_value)>half_unit+prior_precision THEN 'changed_value_'||recast_cause::VARCHAR ELSE 'unchanged_within_precision' END,
       to_json([prior_fact,fact_id]) FROM comparisons WHERE prior_accession IS NOT NULL AND prior_accession!=accession''')
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      WITH pairs AS (
       SELECT a.group_id,a.accession,a.period_start,a.period_end,a.unit,a.canonical_concept,a.value AS income,b.value AS cf_start,
        ap.half_unit+bp.half_unit AS tolerance,to_json([a.fact_id,b.fact_id]) AS evidence,a.acceptance_datetime
       FROM facts a JOIN facts b ON a.accession=b.accession AND a.canonical_concept=b.canonical_concept
        AND a.period_start=b.period_start AND a.period_end=b.period_end AND a.unit=b.unit
        AND a.dimensions='{{}}' AND b.dimensions='{{}}' AND a.accounting_framework=b.accounting_framework
       LEFT JOIN precision_units ap ON ap.decimals=a.decimals LEFT JOIN precision_units bp ON bp.decimals=b.decimals
       WHERE a.canonical_concept IN ('us-gaap:ProfitLoss','us-gaap:NetIncomeLoss') AND a.value IS NOT NULL AND b.value IS NOT NULL
        AND a.primary_statement_role='income_statement' AND b.primary_statement_role='cash_flow'
        AND a.primary_statement_occurrence AND b.primary_statement_occurrence AND a.tier IN ('A','B') AND b.tier IN ('A','B')
       QUALIFY row_number() OVER (PARTITION BY a.group_id,a.period_start,a.period_end,a.canonical_concept
        ORDER BY a.acceptance_datetime DESC,a.accession DESC,a.occurrence_rank DESC,b.occurrence_rank DESC)=1
      ) SELECT 'c6_income_articulation',group_id,period_start,period_end,'as_known',{stamp},'income_to_cash_flow|'||canonical_concept||'|'||unit,
       CASE WHEN tolerance IS NULL THEN 'not_testable' WHEN abs(income-cf_start)<=tolerance THEN 'ok' ELSE 'mismatch' END,
       income,cf_start,income-cf_start,tolerance,'instance',CASE WHEN tolerance IS NULL THEN 'precision_missing'
        WHEN abs(income-cf_start)>tolerance THEN 'cash_flow_income_start_differs' END,evidence FROM pairs''')
    # Opening cash is read in P; the closing comparison must be a different,
    # earlier filing. The latest comparative inside P cannot verify itself.
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      WITH periods AS (SELECT DISTINCT accession,group_id,period_start,period_end,acceptance_datetime FROM eligible_instance_occurrences
       WHERE model_quantity='cfo' AND period_start IS NOT NULL), comparisons AS (
       SELECT p.*,opening.unit,opening.value AS opening_cash,prior.value AS prior_cash,
        op.half_unit+pp.half_unit AS tolerance,to_json([opening.fact_id,prior.fact_id]) AS evidence
       FROM periods p JOIN eligible_instance_occurrences opening ON opening.accession=p.accession AND opening.group_id=p.group_id
        AND opening.period_start IS NULL AND opening.period_end=p.period_start-INTERVAL 1 DAY
        AND opening.model_quantity='cash_and_restricted_cash_total' AND opening.dimensions='{{}}'
       LEFT JOIN eligible_instance_occurrences prior ON prior.group_id=p.group_id AND prior.period_start IS NULL
        AND prior.period_end=opening.period_end AND prior.model_quantity=opening.model_quantity AND prior.unit=opening.unit
        AND prior.dimensions=opening.dimensions AND prior.accession!=p.accession AND prior.acceptance_datetime<p.acceptance_datetime
       LEFT JOIN precision_units op ON op.decimals=opening.decimals LEFT JOIN precision_units pp ON pp.decimals=prior.decimals
       QUALIFY row_number() OVER (PARTITION BY p.group_id,p.period_start,p.period_end,opening.unit
        ORDER BY p.acceptance_datetime DESC,p.accession DESC,prior.acceptance_datetime DESC,prior.accession DESC)=1
      ) SELECT 'c7_cash_continuity',group_id,period_start,period_end,'as_known',{stamp},unit,
       CASE WHEN prior_cash IS NULL OR tolerance IS NULL THEN 'not_testable' WHEN abs(opening_cash-prior_cash)<=tolerance THEN 'ok' ELSE 'mismatch' END,
       opening_cash,prior_cash,opening_cash-prior_cash,tolerance,'instance',CASE WHEN prior_cash IS NULL THEN 'prior_deposit_cash_missing'
        WHEN tolerance IS NULL THEN 'precision_missing' WHEN abs(opening_cash-prior_cash)>tolerance THEN 'cross_deposit_cash_recast' END,evidence FROM comparisons''')
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      WITH terms AS (
       SELECT group_id,period_start,period_end,unit,
        max(value) FILTER (WHERE model_quantity='debt_proceeds') AS proceeds,max(value) FILTER (WHERE model_quantity='debt_repayments') AS repayments,
        sum(p.half_unit) AS tolerance,count(p.half_unit) AS precision_count,count(*) AS term_count,
        list(f.fact_id) AS evidence
       FROM quantities_as_known f LEFT JOIN precision_units p USING(decimals)
       WHERE model_quantity IN ('debt_proceeds','debt_repayments') AND period_start IS NOT NULL GROUP BY ALL
      ), equation AS (
       SELECT t.*,closing.value-opening.value AS principal_change,op.half_unit+cp.half_unit+t.tolerance AS total_tolerance,
        to_json(t.evidence||[opening.fact_id,closing.fact_id]) AS all_evidence
       FROM terms t LEFT JOIN quantities_as_known closing ON closing.group_id=t.group_id
        AND closing.model_quantity='debt_principal' AND closing.period_start IS NULL AND closing.period_end=t.period_end AND closing.unit=t.unit
       LEFT JOIN quantities_as_known opening ON opening.group_id=t.group_id AND opening.model_quantity='debt_principal'
        AND opening.period_start IS NULL AND opening.period_end=t.period_start-INTERVAL 1 DAY AND opening.unit=t.unit
       LEFT JOIN precision_units op ON op.decimals=opening.decimals LEFT JOIN precision_units cp ON cp.decimals=closing.decimals
      ) SELECT 'c8_debt_rollforward',group_id,period_start,period_end,'as_known',{stamp},unit,
       CASE WHEN principal_change IS NULL OR proceeds IS NULL OR repayments IS NULL OR total_tolerance IS NULL OR precision_count!=term_count THEN 'not_testable'
        WHEN abs(principal_change-proceeds+repayments)<=total_tolerance THEN 'ok' ELSE 'mismatch' END,
       principal_change,proceeds-repayments,principal_change-proceeds+repayments,total_tolerance,'instance',
       CASE WHEN principal_change IS NULL THEN 'outstanding_principal_unresolved' WHEN proceeds IS NULL OR repayments IS NULL THEN 'debt_cash_terms_missing'
        WHEN total_tolerance IS NULL OR precision_count!=term_count THEN 'precision_missing'
        WHEN abs(principal_change-proceeds+repayments)>total_tolerance THEN 'nonmonetary_debt_rollforward_residual' END,all_evidence FROM equation''')
    # Calculation networks also enumerate issuer extensions in maturities and
    # RPO. They are equations in the issued statement, not quantity mappings.
    db.execute('CREATE TEMP TABLE disclosure_rules (accession VARCHAR,role VARCHAR,parent VARCHAR,child VARCHAR,weight DECIMAL(38,6),control VARCHAR)')
    rows=[]
    for acc,f in collection['filings'].items():
        res=f['resources']
        if 'MetaLinks.json' not in res:continue
        m=next(iter(json.loads((root/res['MetaLinks.json']['path']).read_text())['instance'].values()))
        roles={r['role']:r for r in m['report'].values() if r.get('groupType')=='disclosure'}
        for name,r in res.items():
            if not name.endswith('_cal.xml'):continue
            for a in calculation_arcs((root/r['path']).read_bytes()):
                role=roles.get(a['role']);child=m['tag'].get(a['child'].replace(':','_',1),{})
                if not role or a['role'] not in child.get('presentation',[]):continue
                if a['parent'].endswith((':LesseeOperatingLeaseLiabilityPaymentsDue',':FinanceLeaseLiabilityPaymentsDue',':UnrecordedUnconditionalPurchaseObligationBalanceOnBalanceSheetDate')):
                    c='c10_maturity_sums'
                elif a['parent']=='us-gaap:RevenueRemainingPerformanceObligation':c='c13_rpo'
                else:continue
                rows.append((acc,a['role'],a['parent'],a['child'],a['weight'],c))
    if rows:db.executemany('INSERT INTO disclosure_rules VALUES (?,?,?,?,?,?)',rows)
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      WITH q AS (SELECT r.control,p.group_id,p.period_start,p.period_end,p.accession,r.parent,r.role,p.unit,p.value AS rhs,
       sum(r.weight*c.value) AS lhs,count(*) AS terms,count(c.value) AS found,count(cp.half_unit) AS known_precision,
       max(pp.half_unit) AS parent_precision,sum(abs(r.weight)*cp.half_unit)+max(pp.half_unit) AS tolerance,
       to_json(list(c.fact_id)||[any_value(p.fact_id)]) AS evidence,p.acceptance_datetime
       FROM disclosure_rules r JOIN eligible_instance_occurrences p ON p.accession=r.accession AND p.canonical_concept=r.parent
       LEFT JOIN eligible_instance_occurrences c ON c.accession=p.accession AND c.canonical_concept=r.child AND c.dimensions=p.dimensions
        AND c.period_start IS NOT DISTINCT FROM p.period_start AND c.period_end=p.period_end AND c.unit=p.unit
       LEFT JOIN precision_units pp ON pp.decimals=p.decimals LEFT JOIN precision_units cp ON cp.decimals=c.decimals
       WHERE p.value IS NOT NULL GROUP BY ALL
      ) SELECT control,group_id,coalesce(period_start,period_end),period_end,'as_known',{stamp},parent||'|'||role||'|'||unit,
       CASE WHEN terms<2 THEN 'tautological' WHEN terms!=found OR known_precision!=terms OR parent_precision IS NULL THEN 'not_testable'
        WHEN abs(lhs-rhs)<=tolerance THEN 'ok' ELSE 'mismatch' END,lhs,rhs,lhs-rhs,tolerance,'instance',
       CASE WHEN terms!=found THEN 'missing_maturity_components' WHEN known_precision!=terms OR parent_precision IS NULL THEN 'precision_missing'
        WHEN abs(lhs-rhs)>tolerance THEN 'maturity_residual_unexplained' END,evidence FROM q
       QUALIFY row_number() OVER (PARTITION BY control,group_id,period_start,period_end,parent,role,unit ORDER BY acceptance_datetime DESC,accession DESC)=1''')
    dimension_controls(db,as_of)
    tax_controls(db,as_of)


def dimension_controls(db,as_of):
    stamp=sql_literal(as_of)+'::TIMESTAMPTZ'
    for control,segment in [('c11_segments',True),('c12_revenue_disaggregation',False)]:
        condition="axis LIKE '%:StatementBusinessSegmentsAxis'" if segment else "axis NOT LIKE '%:StatementBusinessSegmentsAxis'"
        # One axis at a time. Nested product×geography cells are not summed
        # alongside their one-axis totals. Negative reconciliation is retained.
        db.execute(f'''INSERT INTO controls
         (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
         WITH components AS (
          SELECT f.*,json_keys(dimensions)[1] AS axis FROM eligible_instance_occurrences f
          WHERE canonical_concept IN ('us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax','us-gaap:Revenues','us-gaap:SalesRevenueNet')
           AND array_length(json_keys(dimensions))=1 AND value IS NOT NULL
         ), q AS (
          SELECT c.group_id,c.accession,c.period_start,c.period_end,c.axis,c.unit,c.canonical_concept,
           sum(c.value) AS lhs,max(total.value) AS rhs,count(*) AS terms,
           count(cp.half_unit) AS known_precision,max(tp.half_unit) AS parent_precision,
           sum(cp.half_unit)+max(tp.half_unit) AS tolerance,
           to_json(list(c.fact_id)||[any_value(total.fact_id)]) AS evidence,max(c.acceptance_datetime) AS accepted
          FROM components c LEFT JOIN eligible_instance_occurrences total ON total.accession=c.accession AND total.group_id=c.group_id
           AND total.canonical_concept=c.canonical_concept AND total.dimensions='{{}}' AND total.period_start=c.period_start
           AND total.period_end=c.period_end AND total.unit=c.unit
          LEFT JOIN precision_units cp ON cp.decimals=c.decimals LEFT JOIN precision_units tp ON tp.decimals=total.decimals
          WHERE {condition} GROUP BY ALL
         ) SELECT '{control}',group_id,period_start,period_end,'as_known',{stamp},axis||'|'||canonical_concept||'|'||unit,
          CASE WHEN terms<2 OR rhs IS NULL OR known_precision<terms OR parent_precision IS NULL THEN 'not_testable'
           WHEN abs(lhs-rhs)<=tolerance THEN 'ok' ELSE 'not_testable' END,
          lhs,rhs,lhs-rhs,tolerance,'instance',CASE WHEN terms<2 THEN 'insufficient_dimension_members' WHEN rhs IS NULL THEN 'consolidated_total_missing'
           WHEN known_precision<terms OR parent_precision IS NULL THEN 'precision_missing'
           WHEN abs(lhs-rhs)>tolerance THEN 'dimension_partition_or_reconciliation_not_established' END,evidence FROM q
          QUALIFY row_number() OVER (PARTITION BY group_id,period_start,period_end,axis,canonical_concept,unit ORDER BY accepted DESC,accession DESC)=1''')


def tax_controls(db,as_of):
    stamp=sql_literal(as_of)+'::TIMESTAMPTZ'
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,tolerance,tolerance_basis,explanation_code,evidence)
      SELECT 'c15_tax_rate',r.group_id,r.period_start,r.period_end,'as_known',{stamp},'continuing_operations|'||r.unit,
       CASE WHEN i.value IS NULL OR pretax.value IS NULL OR pretax.value=0 OR rp.half_unit IS NULL OR ip.half_unit IS NULL OR pp.half_unit IS NULL THEN 'not_testable'
        WHEN abs(r.value*pretax.value-i.value)<=abs(pretax.value)*rp.half_unit+ip.half_unit+abs(r.value)*pp.half_unit THEN 'ok' ELSE 'mismatch' END,
       r.value*pretax.value,i.value,r.value*pretax.value-i.value,
       abs(pretax.value)*rp.half_unit+ip.half_unit+abs(r.value)*pp.half_unit,'instance',
       CASE WHEN i.value IS NULL OR pretax.value IS NULL THEN 'tax_terms_missing' WHEN pretax.value=0 THEN 'denominator_zero'
        WHEN rp.half_unit IS NULL OR ip.half_unit IS NULL OR pp.half_unit IS NULL THEN 'precision_missing'
        WHEN abs(r.value*pretax.value-i.value)>abs(pretax.value)*rp.half_unit+ip.half_unit+abs(r.value)*pp.half_unit THEN 'tax_rate_definition_residual' END,
       to_json([r.fact_id,i.fact_id,pretax.fact_id]) FROM quantities_as_known r
       LEFT JOIN quantities_as_known i ON i.group_id=r.group_id AND i.model_quantity='income_tax_expense'
        AND i.period_start=r.period_start AND i.period_end=r.period_end
       LEFT JOIN quantities_as_known pretax ON pretax.group_id=r.group_id AND pretax.model_quantity='pretax_income_continuing'
        AND pretax.period_start=r.period_start AND pretax.period_end=r.period_end
       LEFT JOIN precision_units rp ON rp.decimals=r.decimals LEFT JOIN precision_units ip ON ip.decimals=i.decimals
       LEFT JOIN precision_units pp ON pp.decimals=pretax.decimals WHERE r.model_quantity='effective_tax_rate' AND r.period_start IS NOT NULL''')
