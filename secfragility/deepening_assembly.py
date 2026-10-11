"""Targeted, source-bounded calculations. No inferred cash dates or additive exposure total."""
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from pathlib import Path
import json
from .database import bulk_insert, sql_literal
from .assembly import rows


def horizon_bounds(db, root, as_of):
    registry = root / 'work/deepening_numeric_rules.json'
    if not registry.exists(): return
    rules = json.loads(registry.read_text())
    def ratio_outward(a, b, up):
        if not b: return None
        with localcontext() as ctx:
            ctx.prec = 60
            return (Decimal(a) / Decimal(b)).quantize(Decimal('.000001'),
                rounding=ROUND_CEILING if up else ROUND_FLOOR)
    db.create_function('ratio_lower6', lambda a,b:ratio_outward(a,b,False),
        ['DECIMAL(38,6)','DECIMAL(38,6)'], 'DECIMAL(38,6)', null_handling='special')
    db.create_function('ratio_upper6', lambda a,b:ratio_outward(a,b,True),
        ['DECIMAL(38,6)','DECIMAL(38,6)'], 'DECIMAL(38,6)', null_handling='special')
    for rule in rules:
        block = json.loads((root / rule['block_path']).read_text())
        if rule['source_quote'] not in block['text']:
            raise ValueError('Maturity calendar evidence no longer matches source block')
        group, period, accession = rule['group_id'], rule['period_end'], rule['accession']
        names = rule['concepts']
        db.execute('''CREATE OR REPLACE TEMP TABLE targeted_debt_terms AS
          SELECT * FROM eligible_instance_occurrences WHERE group_id=? AND accession=?
            AND period_end=?::DATE AND period_start IS NULL AND dimensions='{}'
            AND value IS NOT NULL AND coverage_state IN ('observed','explicit_zero')
          QUALIFY row_number() OVER (PARTITION BY canonical_concept,unit,accounting_framework,reporting_scope
            ORDER BY document_rank DESC,numeric_precision DESC,occurrence_rank DESC,fact_id)=1''',
            [group,accession,period])
        for view in ('as_known','revised'):
            stamp = db.execute('SELECT public_at FROM quarter_cutoffs WHERE group_id=? AND end_date=?::DATE',
                [group,period]).fetchone()
            cutoff = str(stamp[0]) if view == 'as_known' and stamp else as_of
            for months, lower_terms, upper_terms in (
                (12,['remainder'],['remainder','next_year']),
                (24,['remainder','next_year'],['remainder','next_year','year_two'])):
                term = 'horizon_' + str(months) + 'm'
                # Annual buckets supply an interval, not an invented monthly
                # payment schedule. The note expressly covers total debt.
                lower = '+'.join('t' + str(i) + '.value' for i in range(len(lower_terms)))
                upper = '+'.join('t' + str(i) + '.value' for i in range(len(upper_terms)))
                aliases = ['cash'] + ['t'+str(i) for i in range(len(upper_terms))]
                join = ' CROSS JOIN '.join('targeted_debt_terms '+a for a in aliases)
                constraints = ['cash.canonical_concept='+sql_literal(names['cash'])]
                for i, name in enumerate(upper_terms):
                    constraints.extend(['t'+str(i)+'.canonical_concept='+sql_literal(names[name]),
                        't'+str(i)+'.unit=cash.unit','t'+str(i)+'.accounting_framework=cash.accounting_framework',
                        't'+str(i)+'.reporting_scope=cash.reporting_scope'])
                constraints += [a+'.knowledge_date<='+sql_literal(cutoff)+'::TIMESTAMPTZ::DATE' for a in aliases]
                where = ' AND '.join(constraints)
                valid = db.execute('SELECT count(*) FROM '+join+' WHERE '+where).fetchone()[0]
                if valid != 1: continue
                db.execute('''DELETE FROM measures WHERE measure='liq_principal_due_to_cash'
                  AND group_id=? AND period_end=? AND term=? AND view=? AND variant='original'
                  AND status='not_determinable' ''',[group,period,term,view])
                tiers='to_json(['+','.join(a+'.tier' for a in aliases)+'])'
                lineage='to_json(['+','.join(a+'.fact_id' for a in aliases)+'])'
                public='greatest('+','.join(a+'.knowledge_date' for a in aliases)+')'
                db.execute(f'''INSERT INTO measures
                  (measure,group_id,period_start,period_end,view,as_of,information_cutoff,term,variant,
                   value_lower,value_upper,denominator,unit,currency,status,nd_reason,coverage_state,
                   knowledge_date,lineage,evidence_profile,source_perspective,accounting_framework,constant_perimeter,
                   bound_basis)
                  SELECT 'liq_principal_due_to_cash',cash.group_id,
                    (SELECT start_date::VARCHAR FROM quarter_cutoffs WHERE group_id=cash.group_id AND end_date=cash.period_end),
                    cash.period_end::VARCHAR,{sql_literal(view)},{sql_literal(as_of)}::TIMESTAMPTZ,
                    {sql_literal(cutoff)}::TIMESTAMPTZ,{sql_literal(term)},'original',
                    ratio_lower6({lower},cash.value),ratio_upper6({upper},cash.value),cash.value,
                    'ratio',cash.currency,CASE WHEN cash.value=0 THEN 'not_determinable' ELSE 'bounded' END,
                    CASE WHEN cash.value=0 THEN 'denominator_zero' END,'observed',
                    {public},{lineage},{tiers},'reporting_entity',cash.accounting_framework,'current',
                    'annual_debt_buckets_bound_rolling_horizon_no_monthly_timing;principal_only;published_rounded_amounts'
                  FROM {join} WHERE {where}''')
    (root / 'work/deepening_liquidity_bounds.json').write_text(json.dumps(rows(db,
        "SELECT group_id,period_end,view,term,value_lower,value_upper,denominator,status,bound_basis,lineage "
        "FROM measures WHERE measure='liq_principal_due_to_cash' AND status='bounded' ORDER BY ALL"),
        default=str,indent=2)+'\n')
