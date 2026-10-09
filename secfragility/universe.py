"""Expected cells from the metric catalogue and dated issuer calendar only."""
from pathlib import Path
from datetime import date,timedelta
import json,yaml
from .database import MEASURE_TERMS

PAIR_MEASURES={'documented_revenue_dependency','documented_backlog_dependency','documented_pair_coverage',
 'consideration_to_customer','noncash_revenue_from_investees','contract_coverage','counterparty_exposure'}
DEPENDENCIES={'fcf_basic','fcf_after_finance_leases','revenue_total','cfo','capex_cash','investment_impairment',
 'sig_material_weakness','sig_going_concern','finance_lease_principal_payments','counterparty_cash_financing_net'}


def build(root:Path):
    cfg=yaml.safe_load((root/'config.yaml').read_text());inv=json.loads((root/'work/inventory.json').read_text())
    run=json.loads((root/'work/run.json').read_text());quarters=[];annuals=[];expected=[]
    for group,g in inv['groups'].items():
        annual_ends=sorted({r['reportDate'] for issuer in g['issuers'].values() for r in issuer['filings']
          if r['form'] in ('10-K','10-KT') and r.get('reportDate')})
        ends=g.get('quarter_boundaries',[])
        for i,end in enumerate(ends):
            if i==0:continue
            prior=ends[i-1];gap=(date.fromisoformat(end)-date.fromisoformat(prior)).days
            start=(date.fromisoformat(prior)+timedelta(days=1)).isoformat()
            if not 65<=gap<=110:continue
            fy_start=next((a for a in reversed(annual_ends) if a<end),None)
            qnumber=sum(1 for q in ends if fy_start and fy_start<q<=end)
            annual_end=next((a for a in annual_ends if a>=end),None)
            quarters.append({'group_id':group,'period_start':start,'period_end':end,
              'fiscal_year_start':(date.fromisoformat(fy_start)+timedelta(days=1)).isoformat() if fy_start else None,
              'quarter_number':qnumber if 1<=qnumber<=4 else None,'fiscal_year_end':annual_end,
              'in_analysis_window':end>=g['analysis_start'],
              'calendar_basis':'submissions_and_structural_dei_period_end','history_left_censored':g.get('history_left_censored',False)})
        for end in annual_ends:
            if end<g['analysis_start']:continue
            prev=next((a for a in reversed(annual_ends) if a<end),None)
            if prev and 340<=(date.fromisoformat(end)-date.fromisoformat(prev)).days<=385:
                annuals.append({'group_id':group,'period_start':(date.fromisoformat(prev)+timedelta(days=1)).isoformat(),'period_end':end,
                    'fiscal_year':int(end[:4]),'calendar_basis':'successive_annual_filing_dates'})
        known_years={int(q['period_end'][:4]) for q in quarters if q['group_id']==group and q.get('in_analysis_window')}
        missing_years=[year for year in range(cfg['window']['start_fiscal_year'],int(run['as_of'][:4])+1) if year not in known_years]
        if missing_years:
            # Unknown dates remain unknown. Calendar quarters are not invented
            # for pre-IPO periods merely because an issuer now uses December 31.
            for year in missing_years:
                quarters.append({'group_id':group,'period_start':'none','period_end':'none',
                    'calendar_basis':'historical_fiscal_dates_not_established','fiscal_year':year,
                    'history_left_censored':True,'breakdown_key':f'unknown_fiscal_dates|FY{year}'})
    catalogue=sorted(set(cfg['tier1'])|DEPENDENCIES)
    for q in quarters:
        if q.get('in_analysis_window') is False:continue
        group=q['group_id'];base={k:q[k] for k in ('group_id','period_start','period_end')}
        for metric in catalogue:
            if metric=='annex_e_outcome':continue
            counterparties=[c for c in list(cfg['groups'])+['LAB:OpenAI','LAB:Anthropic'] if c!=group] if metric in PAIR_MEASURES else ['none']
            for cp in counterparties:
                for term in MEASURE_TERMS[metric]:
                    keys=[q.get('breakdown_key','none')]
                    if metric=='fragility_event':keys=[f'{k}|'+q.get('breakdown_key','none') for k in cfg['annex_f']['events']]
                    if metric=='exposure_matrix':keys=[f'contractual_outflows|purchase_obligation|{bucket}|'+q.get('breakdown_key','none')
                        for bucket in ['FY1','FY2','FY3','FY4','FY5','later']]
                    for view in ('as_known','revised'):
                        for key in keys:expected.append(dict(base,measure=metric,counterparty_id=cp,term=term,view=view,
                            breakdown_key=key,as_of=run['as_of'],expected=True,calendar_basis=q['calendar_basis']))
    for a in annuals:
        for cp in [c for c in list(cfg['groups'])+['LAB:OpenAI','LAB:Anthropic'] if c!=a['group_id']]:
            for view in ('as_known','revised'):
                for statement in ['E1','E2','E3','E4','E5','E6']:
                    grids=cfg['annex_e']['grid'] if statement in ['E2','E3'] else ['none']
                    dates=cfg['annex_e']['E4']['date_bases'] if statement=='E4' else ['none']
                    for grid in grids:
                        for basis in dates:expected.append({'measure':'annex_e_outcome','group_id':a['group_id'],
                            'counterparty_id':cp,'period_start':a['period_start'],'period_end':a['period_end'],
                            'view':view,'as_of':run['as_of'],'term':'none','breakdown_key':f'{statement}|grid={grid}|date_basis={basis}',
                            'expected':True,'calendar_basis':a['calendar_basis']})
    out={'as_of':run['as_of'],'origin':'fixed_metric_catalogue_and_issuer_calendar_no_financial_values',
        'quarters':quarters,'annuals':annuals,'cells':expected}
    (root/'work/expected_universe.json').write_text(json.dumps(out,indent=2,ensure_ascii=False))
    print(json.dumps({'quarters':len(quarters),'annuals':len(annuals),'expected_cells':len(expected)}))
    return out

if __name__=='__main__':build(Path('.').resolve())
