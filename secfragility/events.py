"""Annex F uses its frozen list; no score and no asset-charge proxy for F6."""
import json
from collections import defaultdict
from .assembly import rows,exclusion
from .database import insert


def run(db,root,as_of):
    u=json.loads((root/'work/expected_universe.json').read_text())
    quarters=[q for q in u['quarters'] if q.get('in_analysis_window') and q['period_start']!='none' and q['period_end']!='none']
    collection=json.loads((root/'work/collection.json').read_text())
    obs=rows(db,'SELECT * FROM usable_observations');evidence=defaultdict(list)
    for o in obs:
        f=o.get('event_observable')
        if not f and o.get('event_present') is False and o.get('model_quantity') in (
             'annual_management_ICFR_effective','annual_management_ICFR_effectiveness','management_ICFR_effective',
             'auditor_ICFR_effective','auditor_ICFR_effectiveness','annual_auditor_ICFR_effective'):
            f='F5'
        if not f and o.get('trigger_occurred')=='yes' and o.get('family')=='credit_support':f='F3'
        if not f and o.get('event_type')=='amendment' and o.get('family') in ('financing','credit_support'):f='F4'
        if not f:continue
        if f=='F6' and o['model_quantity']!='investment_impairment':
            exclusion(db,as_of,'event_definition_mismatch','event',o['observation_id'],group_id=o['group_id'],
                accession=o['accession'],detail='F6 requires investment impairment; PPE and operating-lease impairments are preserved separately.',coverage_state='policy_excluded')
            continue
        d=str(o.get('event_date') or o.get('period_end') or '')
        if not d:continue
        if f in ('F5','F10'):
            report=collection.get('filings',{}).get(o['accession'],{}).get('metadata',{}).get('reportDate')
            if not report or report!=d:
                exclusion(db,as_of,'source_period_not_established','event',o['observation_id'],group_id=o['group_id'],accession=o['accession'],
                   detail='A shared controls content key does not establish the state for another reporting date.',coverage_state='unknown')
                continue
        q=next((q for q in quarters if q['group_id']==o['group_id'] and q['period_start']<=d<=q['period_end']),None)
        if q:evidence[(q['group_id'],q['period_start'],q['period_end'],f)].append(o)
    public={(g,str(s),str(e)):str(t) for g,s,e,t in db.execute('SELECT * FROM quarter_cutoffs').fetchall()}
    ms=rows(db,"SELECT * FROM measures WHERE measure IN ('capex_to_cfo','revenue_growth','investment_impairment','fcf_after_counterparty_financing')")
    by=defaultdict(list)
    for m in ms:by[(m['group_id'],m['period_start'],m['period_end'],m['view'],m['measure'],m['term'])].append(m)
    for view in ('as_known','revised'):
        for q in quarters:
            g,s,e=q['group_id'],q['period_start'],q['period_end'];cutoff=public.get((g,s,e)) if view=='as_known' else as_of
            for f in ['F'+str(i) for i in range(1,11)]:
                key=(g,s,e,f);valid=[o for o in evidence[key] if cutoff and str(o['knowledge_date'])<=cutoff[:10]]
                base=dict(measure='fragility_event',group_id=g,period_start=s,period_end=e,view=view,as_of=as_of,
                    information_cutoff=cutoff,breakdown_key=f,status='not_determinable',nd_reason='not_processed',coverage_state='not_processed',unit='event')
                if valid:
                    affirmative=[o for o in valid if o.get('event_present') or f in ('F3','F4')]
                    base.update(value=1 if affirmative else 0,status='computed',nd_reason=None,coverage_state='observed' if affirmative else 'explicit_zero',
                        knowledge_date=max(o['knowledge_date'] for o in valid),lineage=json.dumps([o['observation_id'] for o in valid]),evidence_profile=json.dumps(sorted({o['tier'] for o in valid})))
                elif f in ('F1','F8'):
                    prior=next((p for p in quarters if p['group_id']==g and str(__import__('datetime').date.fromisoformat(p['period_end'])+__import__('datetime').timedelta(days=1))==s),None)
                    metric,term=('capex_to_cfo','without') if f=='F1' else ('revenue_growth','yoy')
                    a=by[(g,s,e,view,metric,term)]
                    b=by[(g,prior['period_start'],prior['period_end'],view,metric,term)] if prior else []
                    if len(a)==len(b)==1 and a[0]['status']==b[0]['status']=='computed':
                        present=(a[0]['numerator']>a[0]['denominator'] and b[0]['numerator']>b[0]['denominator']) if f=='F1' else a[0]['numerator']*a[0]['denominator']<0 and b[0]['numerator']*b[0]['denominator']>=0
                        base.update(value=int(present),status='computed',nd_reason=None,coverage_state='observed' if present else 'explicit_zero',
                            knowledge_date=max(a[0]['knowledge_date'],b[0]['knowledge_date']),lineage=json.dumps(json.loads(a[0]['lineage'])+json.loads(b[0]['lineage'])))
                    else:base.update(nd_reason='missing_compatible_consecutive_quarters',coverage_state='unknown')
                elif f=='F6':
                    a=by[(g,s,e,view,'investment_impairment','none')]
                    if a and all(m['status']=='computed' for m in a):
                        present=any(m['value']>0 for m in a)
                        base.update(value=int(present),status='computed',nd_reason=None,coverage_state='observed' if present else 'explicit_zero',
                          knowledge_date=max(m['knowledge_date'] for m in a),lineage=json.dumps([i for m in a for i in json.loads(m['lineage'])]))
                elif f in ('F5','F10'):
                    base.update(nd_reason='dated_explicit_control_or_going_concern_state_not_established',coverage_state='not_disclosed')
                insert(db,'measures',base)
                if f in ('F4','F5','F10') and valid:
                    signal={'F4':'sig_covenant_events','F5':'sig_material_weakness','F10':'sig_going_concern'}[f]
                    insert(db,'measures',dict(base,measure=signal,breakdown_key='none'))
