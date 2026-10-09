from __future__ import annotations
from pathlib import Path
import json
import duckdb

# This is the measure-specific term constraint required by §7.5. A term may
# never acquire meaning merely because another measure happened to use it.
MEASURE_TERMS = {
    'capex_to_cfo': ['with','without'], 'fcf_basic': ['none'],
    'fcf_after_finance_leases': ['none'], 'fcf_after_counterparty_financing': ['none'],
    'fcf_after_sbc': ['none'],
    'lease_not_commenced_bridge': ['opening','additions','commenced','closing'],
    'exposure_matrix': ['none'], 'counterparty_exposure': ['none'],
    'receivables_collection_period': ['none'], 'rpo_total': ['none'],
    'rpo_beyond_12m': ['none'], 'revenue_growth': ['yoy','ttm'],
    'depreciation_life_published': ['none'], 'depreciation_life_change_effect': ['published','restated','difference'],
    'investment_gain_loss': ['published','restated','difference'],
    'investment_impairment': ['none'],
    'liq_principal_due_to_cash': ['horizon_12m','horizon_24m'],
    'lev_debt_and_leases_to_operating_income_plus_da': ['debt','leases'],
    'sig_covenant_events': ['none'], 'sig_late_filing': ['none'],
    'sig_distress_8k_items': ['none'], 'sig_auditor_change_or_nonreliance': ['none'],
    'sig_material_weakness': ['none'], 'sig_going_concern': ['none'], 'sig_pledged_assets': ['none'],
    'documented_revenue_dependency': ['none'], 'investor_customer_revenue_share': ['none'],
    'named_edge_coverage': ['named','anonymous','residual'],
    'documented_pair_coverage': ['numerator','denominator'],
    'customer_concentration_anonymous': ['none'], 'supplier_concentration': ['none'],
    'documented_backlog_dependency': ['total','beyond_12m'],
    'consideration_to_customer': ['none'], 'noncash_revenue_from_investees': ['none'],
    'contract_coverage': ['none'], 'annex_e_outcome': ['none'], 'fragility_event': ['none'],
    'revenue_total': ['none'], 'cfo': ['none'], 'capex_cash': ['none'],
    'finance_lease_principal_payments': ['none'], 'counterparty_cash_financing_net': ['none'],
    'gross_margin': ['none'], 'operating_margin': ['none'], 'capex_to_revenue': ['none'],
    'segment_revenue': ['none'], 'segment_profit': ['none'], 'segment_significant_expenses': ['none'],
    'working_capital': ['receivables','inventories','payables','contract_liabilities','net','change'],
    'liq_cash_to_12m_outflows': ['with','without'], 'liq_undrawn_committed_facilities': ['none'],
    'cov_interest_coverage': ['with','without'], 'cov_pik_interest': ['none'],
    'eq_equity_and_accumulated_deficit': ['equity','accumulated_deficit'],
    'eq_diluted_share_count_change': ['none'],
    'earnings_bridge_pretax': ['published','investment_gain_loss','dilution_gain','equity_method_income',
        'investment_impairment','estimate_change_effect','capitalized_interest','bridge_total'],
    'earnings_bridge_share': ['none'], 'implied_useful_life': ['none'], 'cip_share': ['none'],
    'cfo_net_income_gap': ['none'], 'sbc_to_cfo': ['none'], 'customer_advances': ['none'],
    'capitalized_interest': ['none'], 'capex_accrual': ['none'],
    'finance_lease_additions': ['none'], 'vendor_financed_additions': ['none'],
    'stock_paid_additions': ['none'], 'operating_lease_rou_additions': ['none'],
    'relationship_conclusion': ['none'], 'documented_path': ['none'],
    'bdc_fv_to_cost': ['none'], 'bdc_pik_share': ['none'], 'bdc_non_accrual_share': ['none'],
    'form_d_offering_amount': ['none']}

CONTROL_IDS = ['c1_balance_components','c2_cash_flow_components','c3_cash_reconciliation',
    'c4_restatement_detection','c5_bilateral','c6_income_articulation','c7_cash_continuity',
    'c8_debt_rollforward','c9_lease_liability','c10_maturity_sums','c11_segments',
    'c12_revenue_disaggregation','c13_rpo','c14_eps_scale','c15_tax_rate','c16_concentration']
TABLES = ('documents','facts','observations','entities','links','measures','controls','exclusions')


def sql_literal(s: str) -> str:
    return "'" + s.replace("'", "''") + "'"


def create(root: Path):
    db = duckdb.connect()
    db.execute('CREATE TYPE measure_id_t AS ENUM (' + ','.join(map(sql_literal, MEASURE_TERMS)) + ')')
    db.execute('CREATE TYPE control_id_t AS ENUM (' + ','.join(map(sql_literal, CONTROL_IDS)) + ')')
    schema = (root / 'schema.sql').read_text()
    # DuckDB has no ALTER TABLE ADD CHECK. Insert the constraint in CREATE TABLE.
    constraint = 'CHECK (' + ' OR '.join(
        f'(measure = {sql_literal(m)} AND term IN ({",".join(map(sql_literal,ts))}))'
        for m,ts in MEASURE_TERMS.items()) + ')'
    target = "CHECK (status != 'not_determinable' OR nd_reason IS NOT NULL),"
    schema = schema.replace(target, constraint + ',\n  ' + target)
    db.execute(schema)
    # Reader-identified semantic conflicts never alter the deposited facts.
    # This auxiliary view is rebuilt from the versioned evidence decisions;
    # it is not a ninth exported table or a change to candidate identity.
    quarantine_path = root / 'work/fact_semantic_quarantines.json'
    quarantines = json.loads(quarantine_path.read_text()) if quarantine_path.exists() else []
    entries = [(r['fact_id'], r['affected_quantity'], r['reason']) for r in quarantines
               if r['status'] == 'exclude_dependent_numeric_attribution_keep_raw_fact']
    if entries:
        values = ','.join('(' + ','.join(sql_literal(v) for v in row) + ')' for row in entries)
        db.execute('CREATE TEMP VIEW semantic_fact_quarantines AS SELECT * FROM (VALUES '
                   + values + ') AS q(fact_id,affected_quantity,reason)')
    else:
        db.execute('CREATE TEMP VIEW semantic_fact_quarantines AS SELECT '
                   'NULL::VARCHAR AS fact_id,NULL::VARCHAR AS affected_quantity,'
                   'NULL::VARCHAR AS reason WHERE FALSE')
    return db


def insert(db, table: str, row: dict):
    if table not in TABLES:
        raise ValueError(table)
    allowed = {r[1] for r in db.execute(f"PRAGMA table_info('{table}')").fetchall()}
    if set(row) - allowed:
        raise ValueError(f'Colonnes inconnues : {set(row)-allowed}')
    keys = list(row)
    db.execute(f'INSERT INTO {table} ({",".join(keys)}) VALUES ({",".join("?" for _ in keys)})',
        [row[k] for k in keys])


def export(db, destination: Path):
    from tempfile import TemporaryDirectory
    destination.mkdir(parents=True, exist_ok=True)
    # Git checkpoints can run while cached facts are being reconstructed.
    # Keep the prior exports until every new file has finished writing.
    with TemporaryDirectory(prefix='.export-', dir=destination) as staging:
        for table in TABLES:
            info = db.execute(f"PRAGMA table_info('{table}')").fetchall()
            keys = [r[1] for r in info if r[5]]
            target = Path(staging) / (table + '.parquet')
            db.execute(f'COPY (SELECT * FROM {table} ORDER BY {",".join(keys)}) TO {sql_literal(str(target))} (FORMAT PARQUET)')
        for table in TABLES:
            (Path(staging) / (table + '.parquet')).replace(destination / (table + '.parquet'))


def table_counts(db) -> dict:
    return {t: db.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in TABLES}
