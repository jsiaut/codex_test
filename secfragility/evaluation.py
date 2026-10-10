"""Frozen Annex E evaluated at annual deadlines, including empty results."""
import json
from collections import defaultdict
from decimal import Decimal
import yaml
from .assembly import rows
from .annexes import dependency_outcome,link_outcome,chronology_outcome
from .database import insert,bulk_insert
from .pairs import financed


def run(db,root,as_of):
    cfg=yaml.safe_load((root/'config.yaml').read_text());criteria=cfg['annex_e']
    cutoffs=json.loads((root/'work/annual_cutoffs.json').read_text())['annuals']
    registry=json.loads((root/'work/pair_registry.json').read_text())['pairs']
    u=json.loads((root/'work/expected_universe.json').read_text());edges=rows(db,'SELECT * FROM links WHERE family IS NOT NULL')
    # Every potential path remains uncomputed until the text/discovery extension.
    results=[]
    dependency_rows=defaultdict(list)
    for m in rows(db,"SELECT * FROM measures WHERE measure IN ('documented_revenue_dependency','documented_backlog_dependency') AND financing_policy='exposure_outstanding'"):
        dependency_rows[(m['measure'],m['group_id'],m['counterparty_id'],m['view'])].append(m)
    for a in cutoffs:
        g=a['group_id'];q=dict(group_id=g,period_start=a['period_start'],period_end=a['period_end'])
        for view in ('as_known','revised'):
            dated=a['period_start']!='none' and a['period_end']!='none'
            known=(a['as_known_cutoff'] if view=='as_known' else as_of) if dated and not a.get('cutoff_reason') else None
            cutoff=known or as_of
            for c in registry[g]:
                pe=[e for e in edges if {e.get('from_group_id'),e.get('to_group_id')}=={g,c} and str(e.get('knowledge_date') or '9999')<=cutoff[:10]
                    and str(e.get('event_date') or e.get('period_end') or '9999')<=a['period_end']] if known else []
                active=known and financed(edges,g,c,q,u['quarters'],cutoff)=='active'
                linked=[e['linkage_class'] for e in pe if e['linkage_evidence']=='documented_link']
                for statement in ['E1','E2','E3','E4','E5','E6']:
                    grids=criteria['grid'] if statement in ('E2','E3') else ['none']
                    bases=criteria['E4']['date_bases'] if statement=='E4' else ['none']
                    for grid in grids:
                        for basis in bases:
                            key=f'{statement}|grid={grid}|date_basis={basis}'
                            if not dated:key+='|unknown_fiscal_dates|FY'+str(a['fiscal_year'])
                            reason=a.get('cutoff_reason') if not known else 'not_processed'
                            outcome='indeterminate';status='not_determinable';value=None;lineage=[]
                            if known and statement=='E1':
                                outcome=link_outcome(active=bool(active),linkage_classes=linked,search_complete=False)['outcome']
                                if outcome=='supported':status='computed';reason=None;lineage=[e['link_id'] for e in pe]
                            elif known and statement in ('E2','E3'):
                                # Annual power needs full-year same-basis coverage.
                                metric='documented_revenue_dependency' if statement=='E2' else 'documented_backlog_dependency'
                                annual_years={v['period_end']:v['fiscal_year'] for v in cutoffs if v['group_id']==g and v['period_end']!='none'}
                                annual_periods={(v['period_start'],v['period_end']) for v in cutoffs if v['group_id']==g and v['period_end']!='none'}
                                years=[dict(y) for y in dependency_rows[(metric,g,c,view)] if y['period_end'] in annual_years
                                   and y['period_end']<=a['period_end'] and (y['knowledge_date'] is None or str(y['knowledge_date'])<=cutoff[:10])
                                   and ((y['period_start'],y['period_end']) in annual_periods if statement=='E2' else y['term']=='total')]
                                for y in years:y['fiscal_year']=annual_years[y['period_end']]
                                # First-pass annual numerators are unfilled rather
                                # than composed from selected, high-only quarters.
                                answer=dependency_outcome(years,Decimal(grid),criteria['E2'])
                                outcome=answer['outcome'];reason=(answer['reason'] or reason) if years else 'not_processed'
                            elif known and statement=='E4':
                                fs=[e for e in pe if e['family']=='financing' and e['from_group_id']==g and (e['event_type'] in ('funding','drawdown') if basis=='payment' else e['stage'] in ('signed','available'))]
                                ps=[e for e in pe if e['family']=='commercial' and e['from_group_id']==c and (e['event_type'] in ('payment','purchase') and e['stage']=='drawn_or_paid' if basis=='payment' else e['type']=='purchase_commitment')]
                                if fs and ps:
                                    answers=[chronology_outcome(str(f['event_date']) if f['event_date'] else None,[str(p['event_date']) if p['event_date'] else None for p in ps],criteria['E4']) for f in fs]
                                    outcome='compatible' if 'compatible' in answers else 'indeterminate' if 'indeterminate' in answers else 'incompatible'
                                    if outcome!='indeterminate':status='computed';reason=None;lineage=[e['link_id'] for e in fs+ps]
                                    else:reason='date_missing'
                            elif known and statement=='E5':
                                eligible=[e for e in pe if e['family']=='customer_consideration' and e['from_group_id']==g and e['stage']=='recognized' and e['event_type']=='recognition' and e['tier'] in ('A','B','C') and e.get('linkage_class')=='L3']
                                if eligible:outcome='supported';status='computed';reason=None;lineage=[e['link_id'] for e in eligible]
                            elif statement=='E6':outcome='descriptive'
                            m=dict(measure='annex_e_outcome',group_id=g,counterparty_id=c,period_start=a['period_start'],period_end=a['period_end'],
                                view=view,as_of=cutoff,information_cutoff=known,variant='original' if known else 'cutoff_unresolved',breakdown_key=key,
                                status=status,nd_reason=reason or 'not_processed' if status=='not_determinable' else None,
                                coverage_state='not_processed' if status=='not_determinable' else 'observed',outcome=outcome,value=value,
                                lineage=json.dumps(lineage),financing_policy='exposure_outstanding',financing_state='active' if active else 'unknown')
                            if lineage:m['knowledge_date']=max(e['knowledge_date'] for e in pe if e['link_id'] in lineage)
                            results.append(m)
    # E7/E8: one outcome for each pair over its observed annual window, not one
    # vote per quarter or repeated annual cell.
    collapsed=defaultdict(list)
    for r in results:
        statement=r['breakdown_key'].split('|')[0]
        if statement not in ('E1','E2') or statement=='E2' and 'grid='+criteria['headline']+'|' not in r['breakdown_key']:continue
        if r['view']!='as_known':continue
        collapsed[(r['group_id'],r['counterparty_id'],statement)].append(r)
    e7=[]
    for (g,c,s),rs in collapsed.items():
        outcome='supported' if any(r['outcome']=='supported' for r in rs) else 'refuted' if s=='E2' and all(r['outcome']=='refuted' for r in rs) else 'indeterminate'
        e7.append(dict(group_id=g,counterparty_id=c,statement=s,outcome=outcome,reason='not_processed' if outcome=='indeterminate' else None))
    (root/'work/annex_e_pair_outcomes.json').write_text(json.dumps(e7,indent=2)+'\n')

    bulk_insert(db,'measures',results,root,'evaluation')
