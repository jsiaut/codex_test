"""Dated pair outputs. Empty and incompletely attributed numerators stay ND."""
import json
from collections import defaultdict
from datetime import date,timedelta
from decimal import Decimal, ROUND_HALF_EVEN
from .assembly import rows
from .database import insert,bulk_insert
from .xbrl import digest


def number(a,b):
    return (Decimal(a)/Decimal(b)).quantize(Decimal('0.000001'),rounding=ROUND_HALF_EVEN) if b else None


def financed(edges,s,c,q,quarters,cutoff,policy='exposure_outstanding'):
    eligible=[e for e in edges if e.get('from_group_id')==s and e.get('to_group_id')==c
              and e.get('knowledge_date') and str(e['knowledge_date'])<=cutoff[:10]
              and e.get('elimination_status')=='external']
    dates=[x['period_end'] for x in quarters if x['group_id']==s and x['period_end']!='none' and x['period_end']<=q['period_end']]
    dates=sorted(set(dates));left=dates[-9] if len(dates)>8 else min(
        (x['period_start'] for x in quarters if x['group_id']==s and x['period_start']!='none'
         and x['period_end']!='none' and x['period_end']<=q['period_end']),default=None)
    if left and len(dates)<=8:left=str(date.fromisoformat(left)-timedelta(days=1))
    for e in eligible:
        d=str(e.get('event_date') or e.get('period_end') or '')
        qualifies=(e.get('edge_kind')=='amount' and e.get('family')=='financing' and e.get('stage')=='drawn_or_paid'
          and e.get('event_type') in ('funding','drawdown') and e.get('currency')
          and e.get('unit') in (e.get('currency'),'http://www.xbrl.org/2003/iso4217:'+e.get('currency',''))
          and e.get('type')!='noncash_investment' and e.get('amount') is not None and e['amount']>0)
        # Recognized consideration needs the issuer's actual GAAP recognition;
        # a signed maximum warrant grant does not qualify.
        qualifies=qualifies or (e.get('edge_kind')=='amount' and e.get('family')=='customer_consideration' and e.get('stage')=='recognized'
             and e.get('event_type')=='recognition' and e.get('tier') in ('A','B','C'))
        if qualifies and not e.get('event_date') and e.get('period_start') and left and str(e['period_start'])<=left:
            qualifies=False  # Do not assign a straddling annual flow to its closing day.
        if qualifies and d and d<=q['period_end'] and (policy=='ever_financed' or left and d>left):return 'active'
    # An incomplete or unconfirmed financing history cannot establish absence.
    return 'unknown'


def run(db,root,as_of,entities,observations,resolve):
    from .extension_assembly import opened
    completed=bool(opened(root))
    missing='public_attribution_or_complete_terms_not_established' if completed else 'not_processed'
    missing_state='unknown' if completed else 'not_processed'
    pending=[]
    def emit(db,table,row):pending.append(row)
    u=json.loads((root/'work/expected_universe.json').read_text());inv=json.loads((root/'work/inventory.json').read_text())
    edges=rows(db,"SELECT * FROM links WHERE family IS NOT NULL")
    cp=defaultdict(set);cpnames={}
    for g in inv['groups']:cp[g].update(set(inv['groups'])-set([g]));cp[g].update(['LAB:OpenAI','LAB:Anthropic'])
    for o in observations:
        if o.get('counterparty') and o.get('family'):
            e=resolve(o['counterparty'],o)
            if e and e.get('economic_group_id')!=o['group_id']:
                k=e['economic_group_id'];cp[o['group_id']].add(k);cpnames[k]=e['legal_name']
    rev={(m['group_id'],m['period_start'],m['period_end'],m['view']):m for m in rows(db,"SELECT * FROM measures WHERE measure='revenue_total' AND status='computed'")}
    stocks={(m['group_id'],m['period_start'],m['period_end'],m['view']):m for m in rows(db,"SELECT * FROM measures WHERE measure='rpo_total' AND status='computed'")}
    public={(g,str(s),str(e)):str(t) for g,s,e,t in db.execute('SELECT * FROM quarter_cutoffs').fetchall()}
    entities_by_id={e['entity_id']:e for e in entities}
    def row(metric,g,c,q,view,**extra):
        base=dict(measure=metric,group_id=g,counterparty_id=c,period_start=q['period_start'],period_end=q['period_end'],
             view=view,as_of=as_of,information_cutoff=public.get((g,q['period_start'],q['period_end']),as_of) if view=='as_known' else as_of,
             status='not_determinable',nd_reason=missing,coverage_state=missing_state,
             source_perspective='reporting_entity',accounting_framework='us_gaap',**extra)
        return base
    for q in u['quarters']:
        if not q.get('in_analysis_window') or (q['period_start']=='none' or q['period_end']=='none'):continue
        g=q['group_id']
        for view in ('as_known','revised'):
            r=rev.get((g,q['period_start'],q['period_end'],view));cutoff=public.get((g,q['period_start'],q['period_end']),as_of) if view=='as_known' else as_of
            visible=[e for e in edges if str(e.get('knowledge_date') or '9999')<=cutoff[:10]
                     and str(e.get('event_date') or e.get('period_end') or '9999')<=q['period_end']
                     and g in (e.get('from_group_id'),e.get('to_group_id'))]
            for c in sorted(cp[g]):
                pe=[e for e in visible if {e.get('from_group_id'),e.get('to_group_id')}=={g,c}]
                commercial=[e for e in pe if e['family']=='commercial'];fund=[e for e in pe if e['family']=='financing' and e['edge_kind']=='amount' and e['event_type'] in ('funding','drawdown')]
                reciprocal=bool(any(e['from_group_id']==g for e in commercial) and any(e['to_group_id']==g for e in commercial))
                structure='reciprocal_commercial' if reciprocal else 'commercial_and_financing' if commercial and fund else 'commercial_only' if commercial else 'financing_only' if fund else 'none'
                linked=bool(any(e.get('linkage_class') and e['linkage_evidence']=='documented_link' for e in pe))
                conclusion='documented_dependency' if linked else 'commercial_with_financing' if commercial and fund else 'reciprocal_commercial_only' if reciprocal else 'causality_not_established'
                for policy in ('exposure_outstanding','ever_financed'):
                    state=financed(edges,g,c,q,u['quarters'],cutoff,policy)
                    m=row('relationship_conclusion',g,c,q,view,financing_policy=policy,financing_state=state,
                          edge_structure=structure,linkage_evidence='documented_link' if linked else 'search_incomplete',relationship_conclusion=conclusion)
                    if pe:m.update(status='computed',nd_reason=None,coverage_state='observed',lineage=json.dumps([e['link_id'] for e in pe]),knowledge_date=max(e['knowledge_date'] for e in pe))
                    emit(db,'measures',m)
                    candidates=[e for e in commercial if e['to_group_id']==g and e['from_group_id']==c and e['type']=='revenue_recognized'
                         and e['stage']=='recognized' and e['edge_kind']=='amount' and e['source_perspective']=='reporting_entity'
                         and e.get('sales_channel')=='direct' and str(e.get('period_start'))==q['period_start'] and str(e.get('period_end'))==q['period_end']
                         and any(o['observation_id']==e['observation_id'] and o['group_id']==g for o in observations)]
                    m=row('documented_revenue_dependency',g,c,q,view,financing_policy=policy,financing_state=state,
                          numerator_coverage='absent',denominator_coverage='complete' if r else 'absent')
                    if not candidates:m.update(nd_reason='empty_numerator',coverage_state=missing_state)
                    elif not r:m['nd_reason']='missing_revenue_denominator'
                    elif state!='active':m['nd_reason']='financing_state_unknown'
                    elif len(candidates)!=1:m.update(status='blocked_overlap',coverage_state='unknown',nd_reason='attribution_overlap_not_resolved')
                    else:
                        e=candidates[0]
                        if e['unit']==r['unit'] and e['accounting_framework']==r['accounting_framework'] and r['value']!=0:
                            v=number(e['amount'],r['value']);m.update(value=v,value_lower=v,value_upper=v,numerator=e['amount'],denominator=r['value'],unit='ratio',status='computed',nd_reason=None,coverage_state='observed',numerator_coverage='complete',knowledge_date=max(e['knowledge_date'],r['knowledge_date']),lineage=json.dumps([e['link_id']]+json.loads(r['lineage'])))
                    emit(db,'measures',m)
                for term in ('numerator','denominator'):
                    m=row('documented_pair_coverage',g,c,q,view,term=term,numerator_coverage='complete' if candidates else 'absent',denominator_coverage='complete' if r else 'absent')
                    m.update(status='computed',nd_reason=None,coverage_state='observed',lineage=json.dumps([e['link_id'] for e in candidates]+(json.loads(r['lineage']) if r else [])))
                    emit(db,'measures',m)
                m=row('contract_coverage',g,c,q,view)
                if pe:m.update(status='partial',nd_reason='complete_contract_terms_not_established' if completed else 'not_processed',coverage_state='observed',lineage=json.dumps([e['link_id'] for e in pe]),knowledge_date=max(e['knowledge_date'] for e in pe))
                emit(db,'measures',m)
                for metric in ['counterparty_exposure','consideration_to_customer','noncash_revenue_from_investees']:
                    m=row(metric,g,c,q,view,wrong_way=bool(commercial and fund))
                    emit(db,'measures',m)
                for term in ['total','beyond_12m']:
                    m=row('documented_backlog_dependency',g,c,q,view,term=term,financing_policy='exposure_outstanding',financing_state=financed(edges,g,c,q,u['quarters'],cutoff))
                    emit(db,'measures',m)
            for term in ['named','anonymous','residual']:
                m=row('named_edge_coverage',g,'none',q,view,term=term,overlap_possible=True,visible_pairs_count=len({e.get('from_group_id') if e.get('to_group_id')==g else e.get('to_group_id') for e in visible}),denominator=r['value'] if r else None)
                m['nd_reason']='named_anonymous_overlap_and_complete_attribution_not_established'
                if r:m.update(lineage=r['lineage'],knowledge_date=r['knowledge_date'],evidence_profile=r['evidence_profile'],unit='ratio')
                emit(db,'measures',m)
            emit(db,'measures',dict(row('investor_customer_revenue_share',g,'none',q,view,financing_policy='exposure_outstanding'),nd_reason='empty_numerator'))
    (root/'work/pair_registry.json').write_text(json.dumps({'pairs':{g:sorted(v) for g,v in cp.items()},'names':cpnames},ensure_ascii=False,indent=2)+'\n')
    # Individual exposures remain separate by deposited basis and instrument.
    for e in edges:
        if e['edge_kind']!='amount' or e.get('elimination_status')!='external':continue
        o=next(o for o in observations if o['observation_id']==e['observation_id'])
        if not o.get('block') or not o.get('measurement_basis'):continue
        for view in ['as_known','revised']:
            emit(db,'measures',dict(measure='counterparty_exposure',group_id=o['group_id'],counterparty_id=e['to_entity_id'] if e['from_group_id']==o['group_id'] else e['from_entity_id'],
                period_start=str(o['period_start'] or o['period_end'] or o['event_date']),period_end=str(o['period_end'] or o['event_date']),view=view,as_of=as_of,
                breakdown_key='|'.join([o['block'],o.get('category_id') or 'unspecified',o['measurement_basis'],o.get('instrument_key') or e['link_id']]),
                variant=e['link_id'],value=e['amount'],unit=e['unit'],currency=e['currency'],status='partial',nd_reason='complete_contract_terms_not_established' if completed else 'not_processed',coverage_state='observed',
                knowledge_date=e['knowledge_date'],lineage=json.dumps([e['link_id']]),evidence_profile=json.dumps([e['tier']]),wrong_way=None,
                source_perspective=o['source_perspective'],accounting_framework=o['accounting_framework']))

    bulk_insert(db,'measures',pending,root,'pairs')
