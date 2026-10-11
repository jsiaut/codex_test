"""Targeted, source-bounded calculations. No inferred cash dates or additive exposure total."""
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from pathlib import Path
import json
from .database import bulk_insert, sql_literal
from .assembly import rows
from .database import insert
from .xbrl import parse_instance, digest
from .text import parse_html, local_tag
from .document_order import fact_order
from .evidence import periodic_assurance, filing_status


def lender_positions(db, root, as_of):
    """FV/cost is measured on each reported loan position, outside group totals."""
    import re
    from lxml import etree
    from .reports import csv_write
    def label(dimensions):
        pieces=[]
        for axis,member in json.loads(dimensions).items():
            if member.startswith('<'):
                node=etree.fromstring(member.encode(),etree.XMLParser(resolve_entities=False,no_network=True))
                pieces.append(' '.join(node.itertext()))
            else:pieces.append(member)
        return ' | '.join(pieces)
    db.create_function('investment_position_label',label,['VARCHAR'],'VARCHAR')
    db.execute('''CREATE OR REPLACE TEMP TABLE targeted_lender_positions AS
      SELECT cost.group_id,cost.entity_id,cost.accession,cost.period_end,cost.unit,cost.currency,
        cost.dimensions,investment_position_label(cost.dimensions) AS position_label,
        cost.value AS cost,fv.value AS fair_value,cost.accounting_framework,cost.tier,
        greatest(cost.knowledge_date,fv.knowledge_date) AS knowledge_date,
        to_json([cost.fact_id,fv.fact_id]) AS lineage,
        CASE WHEN cost.value>0 THEN exact_ratio6(fv.value,cost.value) END AS fv_to_cost
      FROM eligible_instance_occurrences cost JOIN eligible_instance_occurrences fv
        ON cost.accession=fv.accession AND cost.dimensions=fv.dimensions AND cost.period_end=fv.period_end
        AND cost.unit=fv.unit AND cost.reporting_scope=fv.reporting_scope
        AND cost.accounting_framework=fv.accounting_framework
      WHERE cost.canonical_concept='us-gaap:InvestmentOwnedAtCost'
        AND fv.canonical_concept='us-gaap:InvestmentOwnedAtFairValue'
        AND cost.value IS NOT NULL AND fv.value IS NOT NULL AND cost.group_id LIKE 'external:%'
        AND cost.dimensions ILIKE '%coreweave%'
        AND regexp_matches(investment_position_label(cost.dimensions),'(?i)loan|debt|lien')
        AND NOT regexp_matches(investment_position_label(cost.dimensions),'(?i)unfunded|uncommitted')''')
    for view in ('as_known','revised'):
        db.execute(f'''INSERT INTO measures
          (measure,group_id,entity_id,period_start,period_end,view,as_of,information_cutoff,breakdown_key,
           value,numerator,denominator,unit,status,nd_reason,coverage_state,knowledge_date,lineage,
           evidence_profile,tier,source_perspective,accounting_framework)
          SELECT 'bdc_fv_to_cost',group_id,entity_id,'none',period_end::VARCHAR,'{view}',?::TIMESTAMPTZ,
            ?::TIMESTAMPTZ,accession||'|'||dimensions,fv_to_cost,fair_value,cost,'ratio',
            CASE WHEN cost<=0 THEN 'not_determinable' ELSE 'computed' END,
            CASE WHEN cost<=0 THEN 'non_positive_cost' END,'observed',knowledge_date,lineage,to_json([tier]),
            2,'reporting_entity',accounting_framework FROM targeted_lender_positions WHERE knowledge_date<=?::DATE''',
            [as_of,as_of,as_of[:10]])
        for metric,reason in [('bdc_pik_share','position_pik_income_and_total_interest_income_not_established'),
                              ('bdc_non_accrual_share','position_non_accrual_classification_not_established')]:
            db.execute(f'''INSERT INTO measures
              (measure,group_id,entity_id,period_start,period_end,view,as_of,information_cutoff,breakdown_key,
               unit,status,nd_reason,coverage_state,knowledge_date,lineage,evidence_profile,tier,
               source_perspective,accounting_framework)
              SELECT '{metric}',group_id,entity_id,'none',period_end::VARCHAR,'{view}',?::TIMESTAMPTZ,
                ?::TIMESTAMPTZ,accession||'|'||dimensions,'ratio','not_determinable','{reason}',
                'not_processed',knowledge_date,lineage,to_json([tier]),2,'reporting_entity',accounting_framework
                FROM targeted_lender_positions WHERE knowledge_date<=?::DATE''',[as_of,as_of,as_of[:10]])
    positions=rows(db,'SELECT * FROM targeted_lender_positions ORDER BY group_id,period_end,position_label')
    csv_write(root/'lender_positions.csv',positions)
    (root/'work/deepening_lender_summary.json').write_text(json.dumps(dict(positions=len(positions),
        lenders=len({r['group_id'] for r in positions}),costs_and_fair_values_are_positions_not_facility_sizes=True,
        pii_or_model_api_calls=False,earlier_missing_data_not_zero=True),indent=2)+'\n')


def load_sources(db, root, as_of):
    """Add original filings, never financial amounts read from an SEC dataset scan."""
    registry=root/'work/deepening_filings.json'
    if not registry.exists():return
    import hashlib
    contracts=root/'work/deepening_contract_sources.json'
    if contracts.exists():
        manifest=json.loads((root/'work/deepening_source_manifest.json').read_text())
        for url,r in sorted(json.loads(contracts.read_text()).items()):
            meta=r['metadata'];res=r['resource'];raw=(root/res['path']).read_bytes();did=digest([url])
            if hashlib.sha256(raw).hexdigest()!=manifest[url]['sha256']:raise ValueError('Contract bytes changed')
            if db.execute('SELECT count(*) FROM documents WHERE document_id=?',[did]).fetchone()[0]:continue
            insert(db,'documents',dict(document_id=did,group_id=r['group'],entity_id='cik:'+str(meta['cik']).zfill(10),cik=str(meta['cik']).zfill(10),
                accession=meta['accessionNumber'],document_rank=r['header']['document_rank'],document_rank_source='SGML_DOCUMENT_order',
                url=url,cache_path=res['path'],sha256=manifest[url]['sha256'],form=meta['form'],exhibit_type=r['header']['type'],
                filing_status='filed',assurance_level='not_applicable',location='contract_exhibit',document_kind='contract',tier='D',
                acceptance_datetime=meta['acceptanceDateTime'],filing_date=meta['filingDate'],knowledge_date=meta['filingDate'],
                byte_count=len(raw),parse_status='observed',as_of=as_of))
    from .deepening_form_d import load as load_form_d
    load_form_d(db,root,as_of)
    for accession,filing in sorted(json.loads(registry.read_text()).items()):
        meta=filing['metadata'];resources=filing['resources'];group=filing['group']
        assurance=periodic_assurance(meta['form'])
        status=filing_status(meta['form'])
        physical={h['filename']:h['document_rank'] for h in filing['discovery']['headers']}
        inline={}
        for name,res in resources.items():
            raw=(root/res['path']).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=res['sha256']:raise ValueError('Official filing bytes changed')
            did=digest([res['url']])
            if not db.execute('SELECT count(*) FROM documents WHERE document_id=?',[did]).fetchone()[0]:
                insert(db,'documents',dict(document_id=did,group_id=group,entity_id='cik:'+meta['cik'],cik=meta['cik'],
                    accession=accession,document_rank=physical.get(name,-2),document_rank_source='SGML_DOCUMENT_order',
                    url=res['url'],cache_path=res['path'],sha256=res['sha256'],form=meta['form'],filing_status=status,
                    assurance_level=assurance,location='financial_statements_and_notes',document_kind='financial_source',
                    tier='E' if status=='furnished' else 'A' if assurance=='audited' else 'B' if assurance=='reviewed' else 'C',
                    acceptance_datetime=meta['acceptanceDateTime'],filing_date=meta['filingDate'],knowledge_date=meta['filingDate'],
                    byte_count=len(raw),parse_status='observed',as_of=as_of))
            if name not in physical or b'ix:nonfraction' not in raw.lower():continue
            for node in parse_html(raw).iter():
                if local_tag(node) not in ('ix:nonfraction','ix:fraction') or not node.get('id'):continue
                inline.setdefault(node.get('id'),set()).add((physical[name],did,node.get('name')))
        source=dict(physical=physical,inline=inline)
        for name,res in resources.items():
            if name not in filing['discovery']['instances']:continue
            facts=parse_instance((root/res['path']).read_bytes(),entity_id='cik:'+meta['cik'],
                reporting_identity='reporter:'+group,group_id=group,document_id=digest([res['url']]),accession=accession,
                acceptance_datetime=meta['acceptanceDateTime'],knowledge_date=meta['filingDate'],assurance_level=assurance,
                as_of=as_of)
            for f in facts:
                rank,rule,did=fact_order(name,f,source)
                f.update(document_rank=rank,document_rank_source=rule,source_document_id=did)
                if rank==-2:f['coverage_state']='unknown'
                if status=='furnished':f.update(filing_status='furnished',tier='E',coverage_state='not_processed')
            existing={x[0] for x in db.execute('SELECT fact_id FROM facts WHERE accession=?',[accession]).fetchall()}
            facts=[f for f in facts if f['fact_id'] not in existing]
            bulk_insert(db,'facts',facts,root,'deepening_facts')


def targeted_note_measures(db,root,as_of):
    """Report source-specific quantities without treating valuations as primary cash."""
    allowed=['customer_working_capital_loan_received','customer_working_capital_loan_noncash_repayment',
        'customer_working_capital_loan_outstanding','named_customer_revenue','customer_warrant_assets_capitalized',
        'indirect_investment_carrying_amount','named_investment_acquisitions','named_investment_unrealized_gain',
        'named_investment_carrying_amount','capital_solution_contract_size','purchase_obligation_guarantee_percentage',
        'purchase_obligation_guarantee_carrying_amount','guarantee_reimbursement_percentage','customer_lease_incentive_asset',
        'lease_letter_of_credit_requirement','vehicle_construction_remaining_contribution','indirect_property_investment_carrying_amount']
    for view in ('as_known','revised'):
        db.execute(f'''INSERT INTO measures
          (measure,group_id,entity_id,period_start,period_end,view,as_of,information_cutoff,breakdown_key,value,unit,
           status,coverage_state,knowledge_date,lineage,evidence_profile,tier,source_perspective,accounting_framework)
          SELECT model_quantity,group_id,entity_id,COALESCE(period_start::VARCHAR,'none'),period_end::VARCHAR,'{view}',
            ?::TIMESTAMPTZ,?::TIMESTAMPTZ,observation_id||'|'||COALESCE(measurement_basis,'unknown_basis'),amount,unit,
            'computed',CASE WHEN amount=0 THEN 'explicit_zero' ELSE 'observed' END,knowledge_date,
            to_json([observation_id,tagged_fact_id]),to_json([tier]),2,source_perspective,accounting_framework
          FROM usable_observations WHERE model_quantity IN ({','.join(sql_literal(x) for x in allowed)})
            AND amount IS NOT NULL AND period_end IS NOT NULL AND knowledge_date<=?::DATE''',[as_of,as_of,as_of[:10]])


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
