from __future__ import annotations
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
import json
from lxml import etree
from .database import sql_literal
from .xbrl import half_unit,canonical_qname,filing_namespaces
from .metadata import load as load_metadata

XLINK='http://www.w3.org/1999/xlink'
LINK='http://www.xbrl.org/2003/linkbase'


def calculation_arcs(raw: bytes,namespace_map=None,replacements=None) -> list[dict]:
    tree=etree.fromstring(raw,etree.XMLParser(resolve_entities=False,no_network=True,huge_tree=True))
    result=[]
    for link in tree.iter(f'{{{LINK}}}calculationLink'):
        loc={n.get(f'{{{XLINK}}}label'):n.get(f'{{{XLINK}}}href').split('#')[-1].replace('_',':',1)
             for n in link if n.tag==f'{{{LINK}}}loc'}
        role=link.get(f'{{{XLINK}}}role')
        for arc in link:
            if arc.tag!=f'{{{LINK}}}calculationArc':continue
            source,target=loc.get(arc.get(f'{{{XLINK}}}from')),loc.get(arc.get(f'{{{XLINK}}}to'))
            if source and target:
                canonical_parent=canonical_qname(source,namespace_map) if namespace_map and source.split(':',1)[0] in namespace_map else source
                canonical_child=canonical_qname(target,namespace_map) if namespace_map and target.split(':',1)[0] in namespace_map else target
                result.append({'role':role,
                    'parent':(replacements or {}).get(canonical_parent,canonical_parent),
                    'child':(replacements or {}).get(canonical_child,canonical_child),
                    'parent_lexical':source,'child_lexical':target,'weight':arc.get('weight','1')})
    return result


def component_controls(db,root: Path,collection: dict,as_of: str):
    # A component is included only if it is in the issuer's presentation role
    # and has a fixed mapping, or is an explicitly presented child of the total.
    db.execute('CREATE TEMP TABLE component_rules (accession VARCHAR, role VARCHAR,parent VARCHAR,child VARCHAR,weight DECIMAL(38,6),control VARCHAR)')
    rows=[]
    for accession,filing in collection['filings'].items():
        resources=filing['resources']
        metadata=load_metadata(root,resources,accession)
        if metadata is None:continue
        meta=next(iter(metadata['instance'].values()))
        roles={r['role']:r for r in meta['report'].values() if r.get('groupType')=='statement'}
        tags=meta['tag']
        namespaces=filing_namespaces(root,resources)
        for name,res in resources.items():
            if not name.endswith('_cal.xml'):continue
            replacements=json.loads((root/'work/deprecations.json').read_text())['mapping'] if (root/'work/deprecations.json').exists() else {}
            for arc in calculation_arcs((root/res['path']).read_bytes(),namespaces,replacements):
                report=roles.get(arc['role'])
                child=tags.get(arc['child_lexical'].replace(':','_',1),{})
                if not report or arc['role'] not in child.get('presentation',[]):continue
                if arc['parent'] in {'us-gaap:AssetsCurrent','us-gaap:Assets','us-gaap:LiabilitiesCurrent',
                    'us-gaap:Liabilities','us-gaap:StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest',
                    'us-gaap:TemporaryEquityCarryingAmountAttributableToParent'}:
                    control='c1_balance_components'
                elif arc['parent'] in {'us-gaap:NetCashProvidedByUsedInOperatingActivities',
                    'us-gaap:NetCashProvidedByUsedInInvestingActivities','us-gaap:NetCashProvidedByUsedInFinancingActivities'}:
                    control='c2_cash_flow_components'
                else:continue
                rows.append((accession,arc['role'],arc['parent'],arc['child'],arc['weight'],control))
    if rows:db.executemany('INSERT INTO component_rules VALUES (?,?,?,?,?,?)',rows)
    precisions=[(str(d),str(half_unit(d))) for d in range(-18,7)]+[('INF','0')]
    db.execute('CREATE TEMP TABLE precision_units (decimals VARCHAR,half_unit DECIMAL(38,12))')
    db.executemany('INSERT INTO precision_units VALUES (?,?)',precisions)
    db.execute('''CREATE TEMP VIEW eligible_component_occurrences AS SELECT * FROM eligible_instance_occurrences
      WHERE dimensions='{}' OR primary_statement_parenthetical=false''')
    # Every equation is checked WITHIN its deposit. A later comparative cannot
    # fill a component missing from the statement under examination.
    db.execute(f'''INSERT INTO controls
     (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,
       tolerance,tolerance_basis,explanation_code,evidence)
     WITH eq AS (
      SELECT rule.control,p.group_id,coalesce(p.period_start,p.period_end) AS period_start,p.period_end,
       p.accession,p.canonical_concept,rule.role,p.value AS rhs,
       sum(rule.weight*c.value) AS lhs,
       sum(cp.half_unit*abs(rule.weight))+max(pp.half_unit) AS tolerance,
       count(*) AS expected_terms,count(c.value) AS observed_terms,
       count(cp.half_unit) AS known_precision,max(pp.half_unit) AS parent_precision,
       to_json(list(c.fact_id)||[any_value(p.fact_id)]) AS evidence,
       p.acceptance_datetime,p.document_rank,p.occurrence_rank
      FROM component_rules rule JOIN eligible_instance_occurrences p ON p.accession=rule.accession
       AND p.canonical_concept=rule.parent AND p.dimensions='{{}}' AND p.value IS NOT NULL
      LEFT JOIN eligible_component_occurrences c ON c.accession=rule.accession AND c.canonical_concept=rule.child
       AND (c.dimensions=p.dimensions OR (c.primary_statement_occurrence=true AND
           c.primary_statement_role=p.primary_statement_role AND p.primary_statement_role IS NOT NULL)) AND c.period_end=p.period_end
       AND c.period_start IS NOT DISTINCT FROM p.period_start AND c.unit=p.unit AND c.value IS NOT NULL
      LEFT JOIN precision_units cp ON cp.decimals=c.decimals
      LEFT JOIN precision_units pp ON pp.decimals=p.decimals
      WHERE p.knowledge_date<=CAST({sql_literal(as_of)} AS TIMESTAMPTZ)::DATE
      GROUP BY ALL
     ), latest AS (SELECT * FROM eq QUALIFY row_number() OVER
      (PARTITION BY control,group_id,period_start,period_end,canonical_concept,role
       ORDER BY acceptance_datetime DESC,accession DESC,document_rank DESC,occurrence_rank DESC)=1)
     SELECT control,group_id,period_start,period_end,'as_known',{sql_literal(as_of)}::TIMESTAMPTZ,
      canonical_concept||'|'||role,
      CASE WHEN expected_terms<2 THEN 'tautological'
       WHEN expected_terms!=observed_terms OR known_precision!=observed_terms OR parent_precision IS NULL THEN 'not_testable'
       WHEN abs(lhs-rhs)<=tolerance THEN 'ok' ELSE 'mismatch' END,
      lhs,rhs,lhs-rhs,tolerance,'instance',
      CASE WHEN expected_terms!=observed_terms THEN 'missing_components'
       WHEN known_precision!=observed_terms OR parent_precision IS NULL THEN 'precision_missing'
       WHEN abs(lhs-rhs)>tolerance THEN 'component_residual_unexplained' END,evidence FROM latest''')


def concentration_controls(db,as_of: str):
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,
       tolerance,tolerance_basis,explanation_code,evidence)
      SELECT 'c16_concentration',group_id,coalesce(period_start,period_end),period_end,
       'as_known',{sql_literal(as_of)}::TIMESTAMPTZ,dimensions,
       CASE WHEN value BETWEEN 0 AND 1 THEN 'ok' ELSE 'mismatch' END,value,1,
       CASE WHEN value>1 THEN value-1 WHEN value<0 THEN value ELSE 0 END,0,'instance',
       CASE WHEN value NOT BETWEEN 0 AND 1 THEN 'percentage_outside_unit_interval' END,to_json([fact_id])
      FROM selected_as_known WHERE canonical_concept='us-gaap:ConcentrationRiskPercentage1'
       AND value IS NOT NULL AND dimensions!='{{}}' AND coverage_state!='conflicting' ''')


def lease_controls(db,as_of: str):
    for lease_type in ('operating','finance'):
        q={k:f'{lease_type}_lease_{k}' for k in ('liability_current','liability_noncurrent','payments_undiscounted','imputed_interest')}
        db.execute(f'''INSERT INTO controls
          (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,
           tolerance,tolerance_basis,explanation_code,evidence)
          WITH terms AS (
           SELECT group_id,period_end,unit,accounting_framework,
            max(value) FILTER (WHERE model_quantity='{q['payments_undiscounted']}') AS payments,
            max(value) FILTER (WHERE model_quantity='{q['imputed_interest']}') AS interest,
            max(value) FILTER (WHERE model_quantity='{q['liability_current']}') AS current_liability,
            max(value) FILTER (WHERE model_quantity='{q['liability_noncurrent']}') AS noncurrent_liability,
            count(DISTINCT model_quantity) AS term_count,
            count(DISTINCT CASE WHEN p.half_unit IS NOT NULL THEN model_quantity END) AS precise_terms,
            sum(p.half_unit) AS tolerance,to_json(list(f.fact_id)) AS evidence
           FROM quantities_as_known f LEFT JOIN precision_units p USING(decimals)
           WHERE model_quantity IN ('{q['payments_undiscounted']}','{q['imputed_interest']}',
             '{q['liability_current']}','{q['liability_noncurrent']}') AND period_start IS NULL
           GROUP BY group_id,period_end,unit,accounting_framework
          ) SELECT 'c9_lease_liability',group_id,period_end,period_end,'as_known',
           {sql_literal(as_of)}::TIMESTAMPTZ,'{lease_type}'||'|'||unit,
           CASE WHEN term_count!=4 OR precise_terms!=4 THEN 'not_testable'
            WHEN abs(payments-interest-current_liability-noncurrent_liability)<=tolerance THEN 'ok' ELSE 'mismatch' END,
           payments-interest,current_liability+noncurrent_liability,
           payments-interest-current_liability-noncurrent_liability,tolerance,'instance',
           CASE WHEN term_count!=4 THEN 'missing_lease_terms' WHEN precise_terms!=4 THEN 'precision_missing'
            WHEN abs(payments-interest-current_liability-noncurrent_liability)>tolerance THEN 'lease_residual_unexplained' END,evidence
           FROM terms''')


def eps_controls(db,as_of: str,relative_tolerance: str):
    db.execute(f'''INSERT INTO controls
      (control,group_id,period_start,period_end,view,as_of,breakdown_key,status,lhs,rhs,residual,
       tolerance,tolerance_basis,explanation_code,evidence)
      SELECT 'c14_eps_scale',eps.group_id,eps.period_start,eps.period_end,'as_known',
       {sql_literal(as_of)}::TIMESTAMPTZ,'consolidated_diluted',
       CASE WHEN EXISTS (SELECT 1 FROM selected_as_known classes WHERE classes.group_id=eps.group_id
         AND classes.canonical_concept=eps.canonical_concept AND classes.period_start=eps.period_start AND classes.period_end=eps.period_end
         AND classes.dimensions LIKE '%:StatementClassOfStockAxis%' GROUP BY classes.group_id HAVING count(DISTINCT classes.value)>1)
         OR eps.value*shares.value IS NULL OR income.value IS NULL OR (direct.value IS NOT NULL AND
         (p_income.half_unit IS NULL OR p_eps.half_unit IS NULL OR p_shares.half_unit IS NULL)) THEN 'not_testable'
        WHEN abs(income.value-eps.value*shares.value)<=
          CASE WHEN direct.value IS NOT NULL THEN p_income.half_unit+
           abs(shares.value)*p_eps.half_unit+abs(eps.value)*p_shares.half_unit+p_eps.half_unit*p_shares.half_unit
           ELSE abs(income.value)*{relative_tolerance}::DECIMAL(38,6) END THEN 'ok' ELSE 'mismatch' END,
       eps.value*shares.value,income.value,eps.value*shares.value-income.value,
       CASE WHEN direct.value IS NOT NULL THEN p_income.half_unit+
        abs(shares.value)*p_eps.half_unit+abs(eps.value)*p_shares.half_unit+p_eps.half_unit*p_shares.half_unit
        ELSE abs(income.value)*{relative_tolerance}::DECIMAL(38,6) END,
       'instance',CASE WHEN EXISTS (SELECT 1 FROM selected_as_known classes WHERE classes.group_id=eps.group_id
         AND classes.canonical_concept=eps.canonical_concept AND classes.period_start=eps.period_start AND classes.period_end=eps.period_end
         AND classes.dimensions LIKE '%:StatementClassOfStockAxis%' GROUP BY classes.group_id HAVING count(DISTINCT classes.value)>1)
         THEN 'multiple_share_classes_with_different_eps'
        WHEN eps.value*shares.value IS NULL OR income.value IS NULL THEN 'missing_eps_terms'
        WHEN direct.value IS NOT NULL AND (p_income.half_unit IS NULL OR p_eps.half_unit IS NULL OR p_shares.half_unit IS NULL) THEN 'precision_missing'
        WHEN abs(income.value-eps.value*shares.value)>abs(income.value)*{relative_tolerance}::DECIMAL(38,6)
         THEN 'eps_scale_residual' WHEN direct.value IS NULL THEN 'net_income_proxy_relative_tolerance' END,
       to_json([eps.fact_id,shares.fact_id,income.fact_id])
      FROM quantities_as_known eps
      LEFT JOIN quantities_as_known shares ON shares.group_id=eps.group_id AND shares.model_quantity='diluted_shares_weighted'
       AND shares.period_start=eps.period_start AND shares.period_end=eps.period_end
      LEFT JOIN quantities_as_known direct ON direct.group_id=eps.group_id AND direct.model_quantity='net_income_to_common_diluted'
       AND direct.period_start=eps.period_start AND direct.period_end=eps.period_end
      LEFT JOIN quantities_as_known income ON income.group_id=eps.group_id AND
       income.model_quantity=CASE WHEN direct.value IS NOT NULL THEN 'net_income_to_common_diluted' ELSE 'net_income' END
       AND income.period_start=eps.period_start AND income.period_end=eps.period_end
      LEFT JOIN precision_units p_eps ON p_eps.decimals=eps.decimals
      LEFT JOIN precision_units p_shares ON p_shares.decimals=shares.decimals
      LEFT JOIN precision_units p_income ON p_income.decimals=income.decimals
      WHERE eps.model_quantity='eps_diluted' AND eps.period_start IS NOT NULL''')
