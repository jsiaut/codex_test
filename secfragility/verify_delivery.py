"""Publication checks: local omissions are quarantined; systematic defects stop."""
import json,hashlib
from .assembly import rows,exclusion
from .database import TABLES


def run(db,root,as_of):
    # Enrichment rows use their snapshot timestamp as as_of. Keep it as the
    # information cutoff before normalizing the delivery's run timestamp.
    db.execute('UPDATE measures SET information_cutoff=COALESCE(information_cutoff,as_of),as_of=?',[as_of])
    checks={}
    checks['eight_tables']=len(TABLES)==8
    checks['no_value_for_ND']=db.execute("SELECT count(*) FROM measures WHERE status IN ('not_determinable','blocked_overlap','not_applicable') AND value IS NOT NULL").fetchone()[0]==0
    checks['ND_reason']=db.execute("SELECT count(*) FROM measures WHERE status='not_determinable' AND nd_reason IS NULL").fetchone()[0]==0
    checks['amount_edge_admissible']=db.execute("SELECT count(*) FROM links WHERE edge_kind='amount' AND (tier NOT IN ('A','B','C','D') OR counterparty_evidence NOT IN ('named','derivable') OR amount IS NULL OR period_end IS NULL)").fetchone()[0]==0
    checks['no_pending_amount_edges']=db.execute("SELECT count(*) FROM links l WHERE edge_kind='amount' AND (NOT EXISTS (SELECT 1 FROM entities e WHERE e.entity_id=l.from_entity_id AND e.entity_status='confirmed') OR NOT EXISTS (SELECT 1 FROM entities e WHERE e.entity_id=l.to_entity_id AND e.entity_status='confirmed'))").fetchone()[0]==0
    checks['no_guarantee_only_financed']=db.execute("SELECT count(*) FROM measures WHERE financing_state='active' AND measure='relationship_conclusion' AND edge_structure='none'").fetchone()[0]==0
    checks['control_reasons']=db.execute("SELECT count(*) FROM controls WHERE status IN ('mismatch','not_testable') AND explanation_code IS NULL").fetchone()[0]==0
    checks['not_supported_search_incomplete']=db.execute("SELECT count(*) FROM measures WHERE measure='annex_e_outcome' AND starts_with(breakdown_key,'E1|') AND outcome='not_supported'").fetchone()[0]==0
    checks['no_nonfinancial_F6']=db.execute("SELECT count(*) FROM measures m JOIN json_each(m.lineage) j ON true JOIN observations o ON j.value::VARCHAR=to_json(o.observation_id)::VARCHAR WHERE m.measure='fragility_event' AND m.breakdown_key='F6' AND o.model_quantity IS DISTINCT FROM 'investment_impairment'").fetchone()[0]==0
    # Numeric lineage resolves to immutable facts, authored observations, links
    # or official metadata documents; bad evidence is localized, never set 0.
    facts={r['fact_id']:r for r in rows(db,'SELECT fact_id,document_id,accession,locator,is_tagged,tier,filing_status,currency,unit,accounting_framework,source_perspective,entity_id,reporting_scope,knowledge_date FROM facts')}
    obs={r['observation_id']:r for r in rows(db,'SELECT observation_id,document_id,accession,locator,tier,filing_status,currency,unit,accounting_framework,source_perspective,entity_id,abstained,tagged_fact_id,knowledge_date FROM observations')}
    links={r['link_id']:r for r in rows(db,'SELECT * FROM links')}
    docs={r['document_id']:r for r in rows(db,'SELECT * FROM documents')}
    blocked={r[0] for r in db.execute('SELECT observation_id FROM excluded_observations').fetchall()}
    ineligible={r[0] for r in db.execute("SELECT fact_id FROM eligible_facts WHERE coverage_state='conflicting'").fetchall()}
    def source(k,seen=None):
        seen=seen or set()
        if k in seen:return []
        seen.add(k)
        if k in facts:return [dict(facts[k],source_id=k,source_kind='fact')]
        if k in obs:
            o=obs[k];f=facts.get(o.get('tagged_fact_id'))
            return [dict(o,source_id=k,source_kind='observation',is_tagged=bool(f and f['is_tagged']))]
        if k in links:
            l=links[k]
            if l.get('observation_id'):return source(l['observation_id'],seen)
            return source(l.get('fact_id'),seen) if l.get('fact_id') else []
        if k in docs:return [dict(docs[k],source_id=k,source_kind='document',is_tagged=False,locator='submission_metadata or document header')]
        return []
    measures=rows(db,'SELECT * FROM measures');invalid=[]
    for m in measures:
        if all(m[k] is None for k in ['value','value_lower','value_upper','numerator','denominator']):continue
        keys=json.loads(m['lineage']);terms=[t for k in keys for t in source(k)]
        reason=None
        if any(not source(k) for k in keys):reason='unresolved_numeric_lineage'
        elif not keys:reason='missing_numeric_lineage'
        elif any(t.get('tier') in ('E','F') or t.get('filing_status')!='filed' for t in terms):reason='inadmissible_numeric_evidence'
        elif any(t['source_id'] in blocked or t['source_id'] in ineligible or t.get('abstained') for t in terms):reason='quarantined_numeric_dependency'
        elif m['view']=='as_known' and (not m['information_cutoff'] or any(
            t.get('knowledge_date') and str(t['knowledge_date'])>str(m['information_cutoff'])[:10] for t in terms)):
            reason='source_not_known_at_information_cutoff'
        # Ratios and cash sums operate on one currency, framework and scope;
        # event/logical descriptions combine evidence without adding amounts.
        if m.get('unit')!='event' and m['measure'] not in ('depreciation_life_published','customer_concentration_anonymous','investment_gain_loss'):
            if len({t.get('currency') for t in terms if t.get('currency')})>1:reason='mixed_currency_terms'
            if len({t.get('accounting_framework') for t in terms if t.get('accounting_framework')})>1:reason='mixed_framework_terms'
            if len({t.get('reporting_scope') for t in terms if t.get('reporting_scope')})>1:reason='mixed_presentation_scope_terms'
        if reason:
            where=" AND ".join(k+'=?' for k in ['measure','group_id','entity_id','counterparty_id','period_start','period_end','view','as_of','term','breakdown_key','financing_policy','constant_perimeter','variant'])
            values=[m[k] for k in ['measure','group_id','entity_id','counterparty_id','period_start','period_end','view','as_of','term','breakdown_key','financing_policy','constant_perimeter','variant']]
            db.execute("UPDATE measures SET status='not_determinable',value=NULL,value_lower=NULL,value_upper=NULL,numerator=NULL,denominator=NULL,nd_reason=?,coverage_state='conflicting' WHERE "+where,[reason]+values)
            exclusion(db,as_of,'invalid_aggregate','measure',hashlib.sha256(json.dumps(values,default=str).encode()).hexdigest(),group_id=m['group_id'],detail=reason,invariant=reason,coverage_state='conflicting')
            invalid.append(dict(group_id=m['group_id'],measure=m['measure'],period_end=m['period_end'],reason=reason))
    coverage=db.execute('''SELECT count(*) FROM expected_cells e WHERE NOT EXISTS (
      SELECT 1 FROM measures m WHERE m.measure::VARCHAR=e.measure AND m.group_id=e.group_id AND m.counterparty_id=e.counterparty_id
       AND m.period_start=e.period_start AND m.period_end=e.period_end AND m.view::VARCHAR=e.view AND m.term=e.term)''').fetchone()[0]
    checks['expected_cells_present']=coverage==0
    checks['no_future_numeric_as_known']=db.execute("SELECT count(*) FROM measures WHERE view='as_known' AND value IS NOT NULL AND (information_cutoff IS NULL OR knowledge_date>information_cutoff::DATE)").fetchone()[0]==0
    # Failures are not generalized on most groups and most periods.
    mismatches=rows(db,"SELECT control,group_id,count(*) n FROM controls WHERE status='mismatch' AND tolerance_basis!='inferred' GROUP BY ALL")
    generalized=db.execute("""WITH gp AS (SELECT group_id,period_start,period_end,bool_or(status='mismatch') failed
      FROM controls WHERE control IN ('c1_balance_components','c2_cash_flow_components','c3_cash_reconciliation',
       'c6_income_articulation','c7_cash_continuity') AND status IN ('ok','mismatch') AND tolerance_basis!='inferred' GROUP BY ALL),
      g AS (SELECT group_id,sum(failed::INTEGER) failures,count(*) periods FROM gp GROUP BY ALL)
      SELECT count(*) FROM g WHERE failures*2>periods""").fetchone()[0]
    checks['no_generalized_accounting_failure']=generalized<6
    checks['criteria_frozen']=json.loads((root/'audit/criteria_manifest.json').read_text())['criteria_unchanged']
    result=dict(as_of=as_of,checks=checks,localized_invalid_aggregates=invalid,accounting_mismatches=mismatches,missing_expected_cells=coverage,independent_audit_performed=False)
    (root/'work/delivery_verification.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    if not all(checks.values()):raise RuntimeError('Delivery invariant failed: '+str([k for k,v in checks.items() if not v]))
    return source,result
