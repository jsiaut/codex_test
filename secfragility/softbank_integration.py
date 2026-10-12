"""Additive, deterministic eight-table Japanese extension and legacy SEC view.

The baseline is an immutable checkpoint of the fully verified SEC reconstruction.
Source qualification is explicit and local. No foreign document is SEC-filed by
inference, no claim of an audited contract, and no source cutoff is advanced.
"""
from pathlib import Path
from collections import defaultdict
from datetime import date,datetime,timedelta,timezone
from decimal import Decimal
import argparse,csv,hashlib,json,shutil
import duckdb,yaml
from functools import lru_cache
from .database import create,insert,bulk_insert,export,TABLES,MEASURE_TERMS
from .softbank_sources import GROUP,VARIANT,document_id,norm,sha,pages,prepare
from .assembly import rows
from .xbrl import digest

PRIMARY='legal:b3afd4bdbaaa7b3c7d19197e9d9a10cd89160358d2d53e8d23f80a33332056df'
SCOPE='SoftBank_Group_IFRS_consolidated'
BASELINE_VARIANT='legacy_EDGAR_only'

def stamp(day):return day+'T14:59:59.999999+00:00' # end of publication day in Japan
def j(value):return json.dumps(value,ensure_ascii=False,default=str)
@lru_cache(maxsize=1)
def rank1():
    from .universe import DEPENDENCIES
    return set(yaml.safe_load((Path('.').resolve()/'config.yaml').read_text())['tier1'])|DEPENDENCIES

def approved_source(root,doc,qualifications,variant):
    q=qualifications.get(doc['document_id'])
    return bool(variant==VARIANT and q and q['eligible_extended'] and
        sha(root/doc['cache_path'])==q['sha256'] and q['publication_date']<=doc['as_of'][:10])

def load_sources(db,root,as_of):
    source_records=json.loads((root/'work/softbank/sources.json').read_text())
    qualified=json.loads((root/'work/softbank/source_qualifications.json').read_text())
    qmap={r['document_id']:r for r in qualified}
    authored=json.loads((root/'work/softbank/authored_observations.json').read_text())
    chrono=json.loads((root/'work/softbank/chronology_observations.json').read_text())
    for o in chrono:
        s=next(s for s in source_records if s['url']==o['document_url'])
        qmap[document_id(s)]=dict(s,document_id=document_id(s),publication_date=o['publication_date'],
            publication_proof='Explicit dated original issuer transaction announcement',
            source_profile=o['source_profile'],jurisdiction='JP_issuer_official_announcement',
            regulatory_identifier=None,filing_status='issuer_disclosure',assurance='unaudited',tier='C',
            publication_date_verified=True,
            eligible_extended=True,eligible_legacy=False,
            assurance_rule='Issuer transaction claim only; no independent assurance and no complete contract; not used as June financial balances')
    # Originals used to validate translations remain distinct physical documents.
    original_ids={q.get('original_document_id'):q for q in qualified if q.get('original_document_id')}
    for s in source_records:
        did=document_id(s);q=qmap.get(did);original=original_ids.get(did)
        pub=q['publication_date'] if q else original['publication_date'] if original else None
        if pub and pub>as_of[:10]:raise ValueError('Future qualified source')
        insert(db,'documents',dict(document_id=did,group_id=GROUP,entity_id=PRIMARY,cik='0001065521',
            accession='JP:'+q['regulatory_identifier'] if q and q.get('regulatory_identifier') else 'JP:'+did[:24],
            url=s['url'],cache_path=s['path'],sha256=s['sha256'],form=q['source_profile'] if q else s['role'],
            filing_status=q['filing_status'] if q else 'unclassified',
            assurance_level=q['assurance'] if q else 'unknown',incorporated_by_reference=False,
            location='PDF_native_text' if s.get('text_path') else 'issuer_HTML',document_kind='foreign_official_source',
            tier=q['tier'] if q else 'F',acceptance_datetime=stamp(pub) if pub else None,
            filing_date=pub if q and q['filing_status']=='filed' else None,knowledge_date=pub,
            period_start=q.get('period_start') if q else None,period_end=q.get('period_end') if q else None,
            byte_count=s['bytes'],parse_status='observed' if s.get('text_path') or q else 'not_processed',
            normalizer_version='pdftotext_layout_native_v1;NFKC_JP_negative_triangle;no_XBRL_tag_claim',as_of=as_of))
    (root/'work/softbank/admitted_sources.json').write_text(json.dumps(list(qmap.values()),ensure_ascii=False,indent=2)+'\n')
    return qmap,source_records,authored+chrono

def load_facts(db,root,as_of,qmap):
    data=json.loads((root/'work/softbank/statement_facts.json').read_text());result=[]
    for r in data:
        q=qmap[r['document_id']];key=[r['concept'],r['period_start'],r['period_end'],r['currency'],SCOPE]
        fid=digest(['SoftBank_statement_v1',r['document_id'],key,r['page'],r['column']])
        dims=j(dict(statement=r['statement'],column=r['column'],source_basis='extended_JP',quote=r['quote'],
                    source_language='ja' if q['jurisdiction']=='JP_EDINET' else 'en',original_value_match=r['original_value_match']))
        record=dict(fact_id=fid,semantic_key=digest(key),document_id=r['document_id'],
            accession='JP:'+q['regulatory_identifier'] if q.get('regulatory_identifier') else 'JP:'+r['document_id'][:24],
            entity_id=PRIMARY,group_id=GROUP,concept='JP_IFRS:'+r['concept'],taxonomy_namespace='native_PDF_untagged',
            canonical_concept=r['concept'],model_quantity=r['concept'],period_start=r['period_start'],period_end=r['period_end'],
            unit='JPY',currency='JPY',dimensions=dims,accounting_framework='ifrs',reporting_scope=SCOPE,
            source_perspective='reporting_entity',value=r['value'],is_tagged=False,is_nil=False,
            explicit_zero=Decimal(r['value'])==0,decimals='-6',locator=f"PDF_PAGE:{r['page']};TEXT_LINE:{r['line']};COLUMN:{r['column']};quote_in_dimensions",
            primary_statement_occurrence=True,primary_statement_role=r['statement'],primary_statement_parenthetical=False,
            occurrence_rank=r['page']*10000+r['line']*10+r['column'],document_rank=0,document_rank_source='one_original_PDF',
            acceptance_datetime=stamp(r['knowledge_date']),knowledge_date=r['knowledge_date'],
            filing_status=q['filing_status'],assurance_level=r['assurance'],location='primary_statement',tier=r['tier'],
            stage='recognized',coverage_state='explicit_zero' if Decimal(r['value'])==0 else 'observed',
            mapping_rule='reviewed_closed_native_statement_label_dictionary',mapping_evidence=r['quote'],as_of=as_of)
        result.append(record)
    bulk_insert(db,'facts',result,root,'softbank_facts')
    return result

def entity_map(db,root,as_of,qmap):
    known=defaultdict(set)
    for r in rows(db,"SELECT entity_id,legal_name FROM entities WHERE alias_key='none'"):
        known[r['legal_name'].casefold()].add(r['entity_id'])
    annual=next(q for q in qmap.values() if q['source_profile']=='issuer_audited_IFRS_financial_statements')
    ids={}
    def entity(name,group=None,treatment='undetermined',page=56,cik=None,membership_start=None):
        existing=known.get(name.casefold(),set())
        if name=='SoftBank Group Corp.':eid=PRIMARY
        elif len(existing)==1:eid=next(iter(existing))
        elif len(existing)>1:
            # Explicit alias decision references all existing equivalents; keep
            # their original rows/edges unchanged in the legacy view.
            eid=sorted(existing)[0]
        else:eid='legal:'+digest(name)
        ids[name]=eid
        insert(db,'entities',dict(entity_id=eid,membership_id=digest(['SoftBank_extension_membership',eid,group,page]),
            legal_name=name,normalized_name=name.casefold(),cik=cik,jurisdiction='JP' if name in ('SoftBank Group Corp.','SoftBank Corp.') else None,
            entity_status='confirmed',group_id=group or eid,economic_group_id=group or eid,
            consolidation_treatment=treatment,membership_start=membership_start or '2026-03-31',knowledge_date=annual['publication_date'],
            resolution_rule='personally_read_consolidated_note;dated_snapshot_not_full_legal_history',
            evidence_document_id=annual['document_id'],evidence_locator=f'PDF_PAGE:{page}',source_perspective='reporting_entity',as_of=as_of))
        if len(existing)>1:
            alias_decisions.append(dict(legal_name=name,canonical_entity_id=eid,legacy_entity_ids=sorted(existing),
                proof=annual['url'],rule='exact_identical_legal_name;old_rows_retained;resolved_view_only'))
        return eid
    alias_decisions=[]
    entity('SoftBank Group Corp.',GROUP,'parent',14,'0001065521')
    for name in ['SoftBank Corp.','SoftBank Group Capital Limited','SoftBank Group Japan Corporation',
        'SoftBank Group Overseas GK','SoftBank Vision Fund L.P.','SoftBank Vision Fund II-2 L.P.',
        'SBLA Latin America Fund LLC','SB Investment Advisers (UK) Limited','SB Global Advisers Limited',
        'Arm Holdings plc','Graphcore Limited','Energy Global, LP','Silver Bands 4 (US) Corp.',
        'SB Northstar LP','Delaware Project 1 L.L.C.','Delaware Project 2 L.L.C.','Delaware Project 3 L.L.C.']:
        entity(name,GROUP,'consolidated_subsidiary',57 if name=='Energy Global, LP' else 56)
    entity('Ampere Computing Holdings LLC',GROUP,'consolidated_subsidiary',38,membership_start='2025-11-25')
    entity('Kronos I (UK) Limited',GROUP,'consolidated_subsidiary',67)
    entity('SVF II TSUBAKI (DE) LLC',GROUP,'consolidated_subsidiary',page=14,membership_start='2026-08-05')
    entity('OpenAI Group PBC',None,'investment_only',14,membership_start='2025-10-28')
    entity('OpenAI, Inc.',None,'undetermined',14,membership_start='2025-02-03')
    entity('MASA USA LLC',None,'undetermined',133)
    entity('ABB Ltd',None,'undetermined',142)
    entity('Apollo Global Funding LLC',None,'undetermined',14,membership_start='2026-08-05')
    entity('SB OpenAI Japan',None,'undetermined',14,membership_start='2025-02-03')
    # Correct proof for identities that were established by Q1 rather than the
    # annual note; prospective JV control is never asserted as completed.
    current=next(q for q in qmap.values() if 'q1fy2026_01_en.pdf' in q['url'])
    for name in ('SVF II TSUBAKI (DE) LLC','Apollo Global Funding LLC'):
        db.execute("UPDATE entities SET evidence_document_id=?,evidence_locator='PDF_PAGE:71',knowledge_date=? WHERE entity_id=? AND starts_with(membership_id,'') AND membership_start='2026-08-05'",
            [current['document_id'],current['publication_date'],ids[name]])
    # The JV plan's dated announcement is the identity proof, not the annual.
    release=next(q for q in qmap.values() if q['url'].endswith('/20250203_0'))
    db.execute("UPDATE entities SET evidence_document_id=?,evidence_locator='dated_issuer_announcement;prospective_control_only',knowledge_date=? WHERE entity_id=? AND membership_start='2025-02-03'",
        [release['document_id'],release['publication_date'],ids['SB OpenAI Japan']])
    (root/'work/softbank/entity_alias_resolutions.json').write_text(json.dumps(alias_decisions,indent=2)+'\n')
    return ids

def load_observations(db,root,as_of,qmap,sources,authored,ids):
    out=[];byurl={s['url']:s for s in sources}
    for number,r in enumerate(authored):
        s=byurl[r['document_url']];q=qmap[document_id(s)]
        if r['page']:
            raw=pages(root,s)[r['page']-1];assert r['quote'] in norm(raw)
            locator=f"PDF_PAGE:{r['page']};quote_in_observation;container_byte_bounds;page_sha256={hashlib.sha256(raw.encode()).hexdigest()}"
        else:
            from lxml import html
            tree=html.fromstring((root/s['path']).read_bytes())
            for node in tree.xpath('//script|//style|//header|//footer|//nav'):node.drop_tree()
            assert r['quote'] in ' '.join(tree.text_content().split())
            locator='issuer_HTML_dated_body;quote_in_observation;container_byte_bounds'
        amount=r.get('amount');currency=r.get('currency');unit=r.get('unit') or currency
        event=r.get('event_date');pe=r.get('period_end') or event or q.get('period_end') or q['publication_date']
        # No retroactive fiscal assignment for post-closing funding.
        ps=r.get('period_start') or event if event else r.get('period_start')
        oid=digest(['SoftBank_authored_v1',q['document_id'],r['page'],r['quantity'],r['quote'],event,pe])
        record=dict(observation_id=oid,content_key=digest([q['document_id'],r['page'] or 'issuer_body']),
            document_id=q['document_id'],accession='JP:'+q['document_id'][:24],group_id=GROUP,entity_id=PRIMARY,
            abstained=False,quote=r['quote'],locator=locator,raw_byte_start=0,raw_byte_end=s['bytes'],
            counterparty=r.get('counterparty'),counterparty_entity_id=ids.get(r.get('counterparty')),
            counterparty_evidence=r.get('counterparty_evidence') or ('named' if r.get('counterparty') else 'anonymous'),
            counterparty_method='exact_named_amount_same_filing' if r.get('counterparty') else None,
            amount=amount,unit=unit,currency=currency,amount_origin='narrative_only' if amount is not None else None,
            amount_qualifier='approximately' if r['quantity']=='openai_ownership_reported' else 'exact' if amount is not None else None,
            amount_nature=r['quantity'],model_quantity=r['quantity'],period_start=ps,period_end=pe,
            event_date=event,event_type=r.get('event_type'),stage=r.get('stage'),instrument_key=r.get('instrument_key'),
            family=r.get('family'),link_type=r.get('link_type'),measurement_basis=r.get('measurement_basis',r['quantity']),
            trigger_occurred=r.get('trigger_occurred'),recourse=r.get('recourse'),vehicle_level=r['quantity'].startswith(('svf','arm','energy')),
            judgment_sensitive='valuation' in r['quantity'] or 'level3' in r['quantity'],issuer_treatment=r['finding'],
            filing_status=q['filing_status'],assurance_level=r.get('assurance_override',q['assurance']),
            tier=r.get('tier_override',q['tier']),location='PDF_financial_note' if r['page'] else 'issuer_transaction_announcement',
            knowledge_date=q['publication_date'],source_perspective='reporting_entity',accounting_framework='ifrs' if r['page'] else 'unknown',
            linkage_class='L1' if r.get('family')=='commercial' else None,
            standard_application='IFRS10;IAS28;IFRS9;IFRS16;IFRS13;source-specific scope',as_of=as_of)
        out.append(record)
    bulk_insert(db,'observations',out,root,'softbank_observations')
    return out

def build_links(db,root,as_of,observations,ids):
    result=[]
    for o in observations:
        if not o['counterparty_entity_id']:continue
        quantity=o['model_quantity'];amount=o['amount'];stage=o['stage']
        primary=quantity=='named_investment_acquisitions' and o['currency']=='USD'
        guarantee=quantity=='parent_guarantee'
        commercial=o['family']=='commercial'
        if not (primary or guarantee or commercial):continue
        from_id=ids['SoftBank Vision Fund II-2 L.P.'] if primary else PRIMARY
        family='financing' if primary else 'commercial' if commercial else 'credit_support'
        linktype='equity_primary' if primary else o['link_type'] if o['link_type'] else 'guarantee' if guarantee else 'credit_enhancement'
        # Arranging, prospective cash collateral and identity information never
        # masquerade as funded loan amounts or as a funded Apollo exposure.
        funded=primary and amount is not None and stage=='drawn_or_paid'
        # links has no edge_structure column; conclusion belongs to measures.
        row=dict(link_id=digest(['SoftBank_link_v1',o['observation_id']]),edge_kind='amount' if funded else 'relation',
            family=family,type=linktype,from_entity_id=from_id,to_entity_id=o['counterparty_entity_id'],
            from_group_id=GROUP,to_group_id=o['counterparty_entity_id'],amount=amount if funded else None,
            unit=o['unit'],currency=o['currency'],period_start=o['period_start'],period_end=o['period_end'],event_date=o['event_date'],
            knowledge_date=o['knowledge_date'],stage=stage,event_type=o['event_type'],instrument_key=o['instrument_key'],
            observation_id=o['observation_id'],document_id=o['document_id'],locator=o['locator'],filing_status=o['filing_status'],
            assurance_level=o['assurance_level'],tier=o['tier'],counterparty_evidence=o['counterparty_evidence'],
            accounting_framework=o['accounting_framework'],source_perspective='reporting_entity',
            financing_state='active' if funded else 'unknown',financing_policy='ever_financed' if funded else 'none',
            linkage_class=o['linkage_class'],linkage_evidence='documented_link' if commercial else 'search_incomplete',
            resolution_evidence=o['issuer_treatment'],wrong_way=quantity in ('collateral_cash_account','management_SBG_share_collateral'),
            vehicle_level=primary or guarantee,as_of=as_of)
        result.append(row)
    # Holdings and cash flows are separate observations/measure bases; the JPY
    # cash translation of April's USD10bn is deliberately not another edge.
    bulk_insert(db,'links',result,root,'softbank_links')
    return result

def measure(db,as_of,name,view,ps,pe,value=None,lineage=(),reason=None,**fields):
    record=dict(measure=name,group_id=GROUP,entity_id=PRIMARY,period_start=ps or 'none',period_end=pe or 'none',
        view=view,as_of=as_of,variant=VARIANT,value=value,status='computed' if value is not None else 'not_determinable',
        nd_reason=reason or 'not_disclosed_or_compatible_basis_not_established' if value is None else None,
        coverage_state='observed' if value is not None else 'not_disclosed',lineage=j(list(lineage)),
        evidence_profile='authorized_JP_official_source_protocol;native_untagged_PDF;assurance_per_source',
        information_cutoff=as_of,accounting_framework='ifrs',source_perspective='reporting_entity',tier=2)
    record.update(fields)
    record['tier']=1 if name in rank1() else 2
    insert(db,'measures',record);return record

def financial_measures(db,root,as_of,facts):
    bycell=defaultdict(list)
    for f in facts:bycell[(f['canonical_concept'],f['period_start'],f['period_end'])].append(f)
    allperiods=sorted({(f['period_start'],f['period_end']) for f in facts if f['period_start'] and f['period_end']>='2021-01-01'})
    snapshots={pe:min(f['knowledge_date'] for f in facts if f['period_end']==pe and f['period_start'] and f['knowledge_date']>=pe) for _,pe in allperiods}
    # Annual as_known is bounded by the normal FIEA three-month deadline.
    # Actual timely submissions are proved by EDINET originals. Deadline
    # exceptions/amendment inventory remain explicit coverage limitations.
    def cutoff(view,pe):return (pe[:4]+'-06-30T14:59:59.999999+00:00' if pe.endswith('03-31') else stamp(snapshots[pe])) if view=='as_known' else as_of
    decisions=[]
    def select(concept,ps,pe,view,reference_cutoff=None):
        options=[f for f in bycell.get((concept,ps,pe),[]) if stamp(f['knowledge_date'])<=(reference_cutoff or cutoff(view,pe))]
        if not options:return None
        # Latest same-period published facts; for ties regulator original before
        # translation. Both originals stay in facts and comparisons stay visible.
        options.sort(key=lambda f:(f['knowledge_date'],f['tier']=='A',f['assurance_level']=='audited',f['fact_id']))
        picked=options[-1]
        if len({f['value'] for f in options if f['knowledge_date']==picked['knowledge_date']})>1:
            decisions.append(dict(concept=concept,period_start=ps,period_end=pe,view=view,reason='same_publication_conflict'))
            return None
        return picked
    published=[]
    direct={'revenue':'revenue_total','cfo':'cfo','capex_signed':'capex_cash','investment_gains':'investment_gain_loss',
            'lease_payments_signed':'ifrs_lease_liability_payments'}
    for view in ('as_known','revised'):
        for ps,pe in allperiods:
            terms={k:select(k,ps,pe,view) for k in ['revenue','cfo','capex_signed','gross_profit','net_income','lease_payments_signed','investment_gains']}
            cut=cutoff(view,pe)
            def emit(name,val=None,deps=(),reason=None,**fields):
                record=measure(db,as_of,name,view,ps,pe,val,[f['fact_id'] for f in deps if f],reason,
                    knowledge_date=max((f['knowledge_date'] for f in deps if f),default=None),**fields)
                db.execute("UPDATE measures SET information_cutoff=? WHERE group_id=? AND measure=? AND view=? AND period_start=? AND period_end=? AND variant=? AND breakdown_key=? AND term=?",
                    [cut,GROUP,name,view,ps,pe,VARIANT,fields.get('breakdown_key','none'),fields.get('term','none')])
                published.append(record)
            for c,name in direct.items():
                f=terms[c];v=Decimal(f['value']) if f else None
                if c in ('capex_signed','lease_payments_signed') and v is not None:v=-v
                emit(name,v,[f],term='published' if name=='investment_gain_loss' else 'none',unit='JPY',currency='JPY')
            cfo=terms['cfo'];capex=terms['capex_signed'];lease=terms['lease_payments_signed'];rev=terms['revenue'];ni=terms['net_income']
            if cfo and capex:
                cv=Decimal(cfo['value']);cx=-Decimal(capex['value'])
                emit('fcf_basic',cv-cx,[cfo,capex],unit='JPY',currency='JPY')
                emit('capex_to_cfo',cx/cv if cv!=0 else None,[cfo,capex],reason='zero_denominator' if cv==0 else None,term='without',unit='ratio',currency='JPY',numerator=cx,denominator=cv)
                emit('capex_to_cfo',reason='US_GAAP_finance_lease_additions_not_equivalent_to_IFRS16_lease_additions',term='with',unit='ratio')
                emit('fcf_after_ifrs_lease_payments',cv-cx+Decimal(lease['value']) if lease else None,[cfo,capex,lease],unit='JPY',currency='JPY')
            if cfo and ni:emit('cfo_net_income_gap',Decimal(cfo['value'])-Decimal(ni['value']),[cfo,ni],unit='JPY',currency='JPY')
            if rev and terms['gross_profit'] and Decimal(rev['value'])!=0:
                emit('gross_margin',Decimal(terms['gross_profit']['value'])/Decimal(rev['value']),[terms['gross_profit'],rev],unit='ratio',currency='JPY')
            if rev and capex and Decimal(rev['value'])!=0:emit('capex_to_revenue',-Decimal(capex['value'])/Decimal(rev['value']),[capex,rev],unit='ratio',currency='JPY')
            prior_end=str(date.fromisoformat(pe).replace(year=int(pe[:4])-1));prior_start=str(date.fromisoformat(ps).replace(year=int(ps[:4])-1))
            prior=select('revenue',prior_start,prior_end,view,cut)
            # A comparable from the very same statement is preferred, since it
            # embodies that statement's published restatement/presentation.
            same=[f for f in bycell.get(('revenue',prior_start,prior_end),[]) if rev and f['document_id']==rev['document_id']]
            if same:prior=same[0]
            if rev and prior and Decimal(prior['value'])!=0:
                emit('revenue_growth',Decimal(rev['value'])/Decimal(prior['value'])-1,[rev,prior],term='yoy',unit='ratio',currency='JPY',basis_break=False)
            else:emit('revenue_growth',reason='same_basis_prior_year_revenue_missing',term='yoy',unit='ratio')
            for name,term,why in [('fcf_after_counterparty_financing','none','complete_net_counterparty_financing_not_public'),
                ('fcf_after_finance_leases','none','IFRS16_lease_payments_not_US_GAAP_finance_lease_principal'),
                ('finance_lease_principal_payments','none','IFRS16_no_US_GAAP_lease_class_split'),
                ('liq_principal_due_to_cash','horizon_12m','principal_cash_only_schedule_and_parent_available_cash_not_established'),
                ('liq_principal_due_to_cash','horizon_24m','principal_cash_only_schedule_and_parent_available_cash_not_established'),
                ('lev_debt_and_leases_to_operating_income_plus_da','debt','no_comparable_operating_income_subtotal_published'),
                ('lev_debt_and_leases_to_operating_income_plus_da','leases','no_comparable_operating_income_subtotal_published')]:
                emit(name,reason=why,term=term)
        for pe in sorted(snapshots):
            fs={c:select(c,None,pe,view) for c in ['cash','debt__current_liabilities','debt__non-current_liabilities','leases__current_liabilities','leases__non-current_liabilities','equity']}
            for name,cs in [('cash_consolidated',['cash']),('debt_interest_bearing',['debt__current_liabilities','debt__non-current_liabilities']),('ifrs_lease_liabilities',['leases__current_liabilities','leases__non-current_liabilities']),('eq_equity_and_accumulated_deficit',['equity'])]:
                deps=[fs[c] for c in cs];v=sum(Decimal(f['value']) for f in deps) if all(deps) else None
                measure(db,as_of,name,view,None,pe,v,[f['fact_id'] for f in deps if f],unit='JPY',currency='JPY',
                    knowledge_date=max((f['knowledge_date'] for f in deps if f),default=None),information_cutoff=cutoff(view,pe),term='equity' if name=='eq_equity_and_accumulated_deficit' else 'none')
            cash=fs['cash'];dc=fs['debt__current_liabilities']
            measure(db,as_of,'debt_current_to_consolidated_cash',view,None,pe,
                Decimal(dc['value'])/Decimal(cash['value']) if cash and dc and Decimal(cash['value']) else None,
                [f['fact_id'] for f in [cash,dc] if f],unit='ratio',currency='JPY',
                information_cutoff=cutoff(view,pe),
                basis_break_reason='Book current debt / consolidated cash proxy; not cash-only contractual principal coverage or parent LTV')
        # TTM is annual + current YTD - the comparator in the current statement.
        # Latest annual/Q1 policies defining cash capex have been read personally.
        end='2026-06-30';year_start='2026-04-01';annual_ps='2025-04-01';annual_pe='2026-03-31'
        for concept,name in [('revenue','revenue_total'),('cfo','cfo'),('capex_signed','capex_cash'),('lease_payments_signed','ifrs_lease_liability_payments')]:
            now=select(concept,year_start,end,view);annual=select(concept,annual_ps,annual_pe,view)
            previous=[f for f in facts if now and f['document_id']==now['document_id'] and f['canonical_concept']==concept and f['period_start']=='2025-04-01' and f['period_end']=='2025-06-30']
            if now and annual and previous:
                old=previous[0];v=Decimal(annual['value'])+Decimal(now['value'])-Decimal(old['value'])
                if concept in ('capex_signed','lease_payments_signed'):v=-v
                measure(db,as_of,name,view,'2025-07-01',end,v,[annual['fact_id'],now['fact_id'],old['fact_id']],
                    unit='JPY',currency='JPY',breakdown_key='TTM',knowledge_date=max(f['knowledge_date'] for f in [annual,now,old]))
    (root/'work/softbank/fact_selection_decisions.json').write_text(json.dumps(decisions,indent=2)+'\n')
    return published

def quarter_measures(db,root,as_of,facts):
    def choose(concept,ps,pe,cut):
        candidates=[f for f in facts if f['canonical_concept']==concept and f['period_start']==ps and f['period_end']==pe and stamp(f['knowledge_date'])<=cut]
        candidates.sort(key=lambda f:(f['knowledge_date'],f['tier']=='A',f['fact_id']))
        if not candidates:return None
        last=candidates[-1]
        if len({f['value'] for f in candidates if f['knowledge_date']==last['knowledge_date']})>1:return None
        return last
    periods=[];quarter_terms={}
    for fy in range(2021,2027):
        annual_start=f'{fy}-04-01'
        ends=[f'{fy}-06-30',f'{fy}-09-30',f'{fy}-12-31',f'{fy+1}-03-31']
        for q,end in enumerate(ends,1):
            if end>'2026-06-30':continue
            start=annual_start if q==1 else str(date.fromisoformat(ends[q-2])+timedelta(days=1))
            publications=[f['knowledge_date'] for f in facts if f['period_start']==annual_start and f['period_end']==end and f['knowledge_date']>=end]
            if not publications:continue
            periods.append(dict(period_start=start,period_end=end,fiscal_year_start=annual_start,quarter=q,
                first_publication=min(publications),annual_deadline=end[:4]+'-06-30' if q==4 else None))
            for view in ('as_known','revised'):
                cut=as_of if view=='revised' else stamp(end[:4]+'-06-30' if q==4 else min(publications))
                terms={}
                for concept in ['cfo','capex_signed','revenue','gross_profit','net_income','lease_payments_signed']:
                    current=choose(concept,annual_start,end,cut)
                    prior=choose(concept,annual_start,ends[q-2],cut) if q>1 else None
                    if not current or (q>1 and not prior):terms[concept]=(None,[]);continue
                    # IFRS scope/unit/concept and YTD origin coincide; retain
                    # the exact subtraction and both dated source terms.
                    value=Decimal(current['value'])-(Decimal(prior['value']) if prior else 0)
                    terms[concept]=(value,[current]+([prior] if prior else []))
                quarter_terms[(view,end)]=terms
                if q==1:continue # already directly published by financial_measures
                def emit(name,value=None,deps=(),reason=None,**fields):
                    return measure(db,as_of,name,view,start,end,value,[f['fact_id'] for f in deps],reason,
                        information_cutoff=cut,knowledge_date=max((f['knowledge_date'] for f in deps),default=None),
                        evidence_profile='same_consolidated_IFRS_JPY_YTD_subtraction;two_exact_source_terms;current_reported_perimeter',**fields)
                for concept,name in [('cfo','cfo'),('capex_signed','capex_cash'),('revenue','revenue_total'),('lease_payments_signed','ifrs_lease_liability_payments')]:
                    v,deps=terms[concept]
                    emit(name,-v if v is not None and concept in ('capex_signed','lease_payments_signed') else v,deps,unit='JPY',currency='JPY')
                cv,cd=terms['cfo'];cx,xd=terms['capex_signed'];lp,ld=terms['lease_payments_signed']
                if cv is not None and cx is not None:
                    emit('fcf_basic',cv+cx,cd+xd,unit='JPY',currency='JPY')
                    emit('capex_to_cfo',-cx/cv if cv else None,cd+xd,reason='zero_denominator' if cv==0 else None,
                        term='without',unit='ratio',currency='JPY',numerator=-cx,denominator=cv)
                    if lp is not None:emit('fcf_after_ifrs_lease_payments',cv+cx+lp,cd+xd+ld,unit='JPY',currency='JPY')
    # Latest TTM cash sensitivity, preserving every source term rather than
    # using a rounded published ratio as an arithmetic input.
    for view in ('as_known','revised'):
        ttm=rows(db,"SELECT * FROM measures WHERE group_id=? AND view=? AND variant=? AND breakdown_key='TTM'",[GROUP,view,VARIANT]);byname={r['measure']:r for r in ttm}
        cfo=byname.get('cfo');capex=byname.get('capex_cash');lp=byname.get('ifrs_lease_liability_payments')
        if cfo and capex:
            deps=json.loads(cfo['lineage'])+json.loads(capex['lineage'])
            measure(db,as_of,'fcf_basic',view,'2025-07-01','2026-06-30',cfo['value']-capex['value'],deps,unit='JPY',currency='JPY',breakdown_key='TTM')
            if lp:measure(db,as_of,'fcf_after_ifrs_lease_payments',view,'2025-07-01','2026-06-30',cfo['value']-capex['value']-lp['value'],deps+json.loads(lp['lineage']),unit='JPY',currency='JPY',breakdown_key='TTM')
    periods.append(dict(period_start='2026-07-01',period_end='2026-09-30',fiscal_year_start='2026-04-01',quarter=2,
        first_publication=None,annual_deadline=None,publication_status='periodic_report_not_known_at_frozen_source_cutoff'))
    (root/'work/softbank/fiscal_calendar.json').write_text(json.dumps(periods,indent=2)+'\n')
    return periods,quarter_terms

def expected_coverage(db,root,as_of,periods,quarter_terms,observations,ids):
    cfg=yaml.safe_load((root/'config.yaml').read_text());catalog=set(cfg['tier1'])|rank1()
    for view in ('as_known','revised'):
        for p in periods:
            ps,pe=p['period_start'],p['period_end']
            for name in sorted(catalog-{'annex_e_outcome','fragility_event'}):
                for term in MEASURE_TERMS[name]:
                    existing=db.execute("SELECT count(*) FROM measures WHERE group_id=? AND variant=? AND measure=? AND view=? AND period_start=? AND period_end=? AND term=?",[GROUP,VARIANT,name,view,ps,pe,term]).fetchone()[0]
                    if not existing:measure(db,as_of,name,view,ps,pe,reason='periodic_report_not_known_at_frozen_source_cutoff' if not p['first_publication'] else 'source_not_disclosed_or_complete_attribution_not_established',term=term)
            for code in [f'F{i}' for i in range(1,11)]:
                value=None;deps=[];why='event_source_or_precondition_not_fully_established'
                if code=='F10' and pe=='2026-06-30':
                    stated=next(o for o in observations if o['model_quantity']=='going_concern_explicit_none')
                    value=0;deps=[stated['observation_id']]
                elif code=='F1' and (view,pe) in quarter_terms:
                    ends=sorted(end for v,end in quarter_terms if v==view and end<=pe)
                    if len(ends)>=2:
                        now,prior=[quarter_terms[(view,e)] for e in ends[-2:]]
                        if all(t[c][0] is not None for t in [now,prior] for c in ['cfo','capex_signed']):
                            value=int(all(-t['capex_signed'][0]>t['cfo'][0] for t in [now,prior]))
                            deps=[f['fact_id'] for t in [now,prior] for c in ['cfo','capex_signed'] for f in t[c][1]]
                cut=as_of if view=='revised' or not p['first_publication'] else stamp(pe[:4]+'-06-30' if p['quarter']==4 else p['first_publication'])
                measure(db,as_of,'fragility_event',view,ps,pe,value,deps,reason=why,breakdown_key=code,unit='event',information_cutoff=cut,
                    outcome='supported' if value==1 else 'descriptive' if value==0 else 'indeterminate')
    # Same original E2/E3 threshold grid; private revenue denominators and
    # contract linkage are not invented to manufacture statistical power.
    criteria=cfg['annex_e']
    annuals=[p for p in periods if p['quarter']==4]
    for view in ('as_known','revised'):
        for p in annuals:
            ps,pe=p['fiscal_year_start'],p['period_end']
            for cp in [ids['OpenAI Group PBC'],ids['OpenAI, Inc.']]:
                for code in ['E1','E2','E3','E4','E5','E6']:
                    grid=criteria['grid'] if code in ('E2','E3') else ['none']
                    for point in grid:
                        for basis in criteria['E4']['date_bases'] if code=='E4' else ['payment']:
                            measure(db,as_of,'annex_e_outcome',view,ps,pe,reason='complete_same_legal_pair_revenue_contract_or_cash_chronology_not_established',
                                counterparty_id=cp,breakdown_key=f'{code}|grid={point}|date_basis={basis}',outcome='descriptive' if code=='E6' else 'indeterminate',
                                information_cutoff=as_of if view=='revised' else stamp(pe[:4]+'-06-30'))
    # Scope-specific quoted RPO is a stock. It is not allocated to OpenAI.
    for o in observations:
        if o['model_quantity']=='rpo_total':
            measure(db,as_of,'rpo_total','revised',None,str(o['period_end']),o['amount'],[o['observation_id']],unit='JPY',currency='JPY',knowledge_date=o['knowledge_date'],breakdown_key='published_group_RPO_excluding_royalties')
        if o['model_quantity']=='investment_impairment':
            measure(db,as_of,'investment_impairment','revised',str(o['period_start']),str(o['period_end']),o['amount'],[o['observation_id']],unit='JPY',currency='JPY',knowledge_date=o['knowledge_date'],breakdown_key='equity_method_investments_annual')
            measure(db,as_of,'fragility_event','revised',str(o['period_start']),str(o['period_end']),1,[o['observation_id']],unit='event',knowledge_date=o['knowledge_date'],breakdown_key='F6',outcome='supported')

def controls(db,root,as_of,facts):
    frames=defaultdict(dict)
    for f in facts:frames[(f['document_id'],f['period_start'],f['period_end'])][f['canonical_concept']]=f
    out=[]
    equations=[('c1_balance_components','assets',['liabilities','equity'],[1,1]),
               ('c3_cash_reconciliation','cash_closing',['cash_opening','cash_change'],[1,1]),
               ('c2_cash_flow_components','cash_change',['cfo','cfi','cff','cash_fx'],[1,1,1,1])]
    for (doc,ps,pe),frame in frames.items():
        for cid,lhs,rhs,signs in equations:
            rhs=list(rhs);signs=list(signs)
            if cid=='c2_cash_flow_components' and 'cash_held_for_sale_transfer' in frame:
                rhs.append('cash_held_for_sale_transfer');signs.append(1)
            if lhs not in frame or any(c not in frame for c in rhs):continue
            terms=[frame[lhs]]+[frame[c] for c in rhs]
            lv=Decimal(terms[0]['value']);rv=sum(Decimal(f['value'])*s for f,s in zip(terms[1:],signs));res=lv-rv
            tolerance=Decimal(500000)*len(terms)
            status='ok' if abs(res)<=tolerance else 'mismatch'
            out.append(dict(control=cid,group_id=GROUP,period_start=ps or 'none',period_end=pe,view='revised',as_of=as_of,
                breakdown_key=doc,variant=VARIANT,status=status,lhs=lv,rhs=rv,residual=res,tolerance=tolerance,
                tolerance_basis='notes_dcml',explanation_code=None if status=='ok' else 'other_cash_bridge_component_or_parse_conflict',
                evidence=j([f['fact_id'] for f in terms])))
    # Independent Japanese original / English audited statement comparisons.
    source_map={s['document_id']:s for s in json.loads((root/'work/softbank/source_qualifications.json').read_text())}
    original={ (f['canonical_concept'],f['period_start'],f['period_end']):f for f in facts if source_map[f['document_id']].get('regulatory_identifier')=='S100YGH5'}
    full=[f for f in facts if source_map[f['document_id']]['source_profile']=='issuer_audited_IFRS_financial_statements']
    for f in full:
        k=(f['canonical_concept'],f['period_start'],f['period_end']);g=original.get(k)
        if not g:continue
        res=Decimal(f['value'])-Decimal(g['value'])
        out.append(dict(control='c4_restatement_detection',group_id=GROUP,period_start=f['period_start'] or 'none',period_end=f['period_end'],view='revised',as_of=as_of,
            breakdown_key='JP_original_EN_translation|'+f['canonical_concept'],variant=VARIANT,status='ok' if res==0 else 'mismatch',
            lhs=f['value'],rhs=g['value'],residual=res,tolerance=0,tolerance_basis='notes_dcml',
            explanation_code=None if res==0 else 'regulatory_original_translation_conflict',evidence=j([f['fact_id'],g['fact_id']])))
    bulk_insert(db,'controls',out,root,'softbank_controls')
    return out

def note_measures(db,root,as_of,observations):
    for o in observations:
        if o['amount'] is None:continue
        for view in ('as_known','revised'):
            # Chronology is a dated issuer claim, not an audited fiscal balance.
            measure(db,as_of,'foreign_source_reported_quantity',view,str(o['period_start']) if o['period_start'] else None,str(o['period_end']),o['amount'],[o['observation_id']],
                breakdown_key=o['model_quantity']+'|'+o['observation_id'][:16],unit=o['unit'],currency=o['currency'],
                knowledge_date=o['knowledge_date'],counterparty_id=o['counterparty_entity_id'] or 'none',
                evidence_profile=o['tier']+';'+o['filing_status']+';'+o['assurance_level']+';'+o['measurement_basis'])
        if o['model_quantity'] in ('named_investment_carrying_amount','openai_undrawn_investment_commitment'):
            block='exposed_assets' if o['stage']=='recognized' else 'contractual_outflows'
            for name in ['counterparty_exposure','exposure_matrix']:
                measure(db,as_of,name,'revised',None,str(o['period_end']),o['amount'],[o['observation_id']],
                    counterparty_id=o['counterparty_entity_id'] or 'none',unit=o['unit'],currency=o['currency'],
                    breakdown_key=block+'|'+o['measurement_basis'],overlap_possible=True,
                    knowledge_date=o['knowledge_date'])
        if o['model_quantity']=='svf_level3_assets':
            fact=rows(db,"SELECT fact_id,value FROM facts WHERE group_id=? AND document_id=? AND canonical_concept='svf_fvtpl' AND period_end='2026-03-31' AND period_start IS NULL",[GROUP,o['document_id']])[0]
            measure(db,as_of,'svf_level3_share','revised',None,'2026-03-31',Decimal(o['amount'])/fact['value'],[o['observation_id'],fact['fact_id']],
                unit='ratio',currency='JPY',numerator=o['amount'],denominator=fact['value'],knowledge_date=o['knowledge_date'])
    guarantee=next(o for o in observations if o['model_quantity']=='parent_guarantee')
    measure(db,as_of,'counterparty_exposure','revised',None,str(guarantee['period_end']),reason='guarantee_maximum_scope_not_disclosed',
        counterparty_id=guarantee['counterparty_entity_id'],breakdown_key='contingent_obligations|TSUBAKI_parent_guarantee',
        lineage=[guarantee['observation_id']],unit='USD',currency='USD')

def verify(db,root,as_of,qmap,facts,observations,control_rows):
    checks={};checks['eight_tables']=len(TABLES)==8
    baseline=json.loads((root/'work/softbank/baseline/manifest.json').read_text()); preservation={}
    def bag(value):return json.dumps(sorted(json.loads(value),key=lambda x:json.dumps(x,sort_keys=True)),separators=(',',':'))
    db.create_function('softbank_source_bag',bag,['VARCHAR'],'VARCHAR')
    for table in TABLES:
        reference=root/baseline[table]['path'];assert sha(reference)==baseline[table]['sha256']
        columns=[r[1] for r in db.execute(f"PRAGMA table_info('{table}')").fetchall()]
        fields=','.join('softbank_source_bag("'+c+'") AS "'+c+'"' if c in ('lineage','evidence') else '"'+c+'"' for c in columns)
        old=db.execute(f"SELECT count(*) FROM (SELECT {fields} FROM read_parquet('{reference}') EXCEPT ALL SELECT {fields} FROM {table})").fetchone()[0]
        preservation[table]=dict(missing_or_changed_original_rows=old,original_sha256=baseline[table]['sha256'])
    checks['every_legacy_row_preserved']=all(r['missing_or_changed_original_rows']==0 for r in preservation.values())
    prior_criteria=json.loads((root/'work/softbank/baseline/criteria_manifest.json').read_text())
    current_criteria=json.loads((root/'audit/criteria_manifest.json').read_text())
    checks['frozen_annex_criteria']=all(prior_criteria[k]==current_criteria[k] for k in
        ['original_commit','original_commit_date','first_sec_request','original_criteria','current_criteria','criteria_unchanged'])
    checks['foreign_source_hashes']=all(sha(root/q['path'])==q['sha256'] for q in qmap.values())
    checks['no_future_source']=all(q['publication_date']<=as_of[:10] for q in qmap.values())
    checks['untagged_PDF_facts']=all(not f['is_tagged'] and f['currency']=='JPY' and f['accounting_framework']=='ifrs' and f['reporting_scope']==SCOPE for f in facts)
    checks['legacy_no_foreign_numeric']=db.execute("SELECT count(*) FROM measures WHERE group_id=? AND variant=? AND value IS NOT NULL",[GROUP,BASELINE_VARIANT]).fetchone()[0]==0
    checks['ND_not_zero']=db.execute("SELECT count(*) FROM measures WHERE status='not_determinable' AND (value IS NOT NULL OR nd_reason IS NULL)").fetchone()[0]==0
    checks['no_signed_only_financing_amount_edge']=db.execute("SELECT count(*) FROM links WHERE from_group_id=? AND edge_kind='amount' AND family='financing' AND stage NOT IN ('drawn_or_paid','recognized')",[GROUP]).fetchone()[0]==0
    checks['no_Apollo_amount_allocation']=db.execute("SELECT count(*) FROM links l JOIN entities e ON l.to_entity_id=e.entity_id WHERE l.from_group_id=? AND l.amount IS NOT NULL AND e.legal_name='Apollo Global Funding LLC'",[GROUP]).fetchone()[0]==0
    checks['JP_EN_original_amounts_agree']=all(r['status']=='ok' for r in control_rows if r['control']=='c4_restatement_detection')
    obsmap={o['observation_id']:o for o in observations};factmap={f['fact_id']:f for f in facts}
    invalid=[]
    for m in rows(db,"SELECT * FROM measures WHERE group_id=? AND variant=? AND value IS NOT NULL",[GROUP,VARIANT]):
        evidence=[factmap.get(k) or obsmap.get(k) for k in json.loads(m['lineage'])]
        if not evidence or any(e is None for e in evidence):invalid.append('unresolved_lineage');continue
        if any(e['document_id'] not in qmap for e in evidence):invalid.append('unqualified_source')
        if any(e['knowledge_date']>str(m['information_cutoff'])[:10] for e in evidence):invalid.append('future_as_known_source')
        if len({e.get('currency') for e in evidence if e.get('currency')})>1:invalid.append('mixed_currency')
    checks['all_numeric_lineage_qualified_and_known']=not invalid
    result=dict(as_of=as_of,checks=checks,baseline_preservation=preservation,
        invalid_numeric_dependencies=invalid,qualified_sources=len(qmap),new_statement_facts=len(facts),
        new_authored_observations=len(observations),new_controls=len(control_rows),
        accounting_mismatches=[r for r in control_rows if r['status']=='mismatch'],
        independent_audit_performed=False,subagents_used=False)
    (root/'work/softbank/validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,default=str)+'\n')
    if not all(checks.values()):raise RuntimeError('SoftBank checks failed: '+str([k for k,v in checks.items() if not v]))
    return result

def apply(db,root,as_of):
    qmap,sources,authored=load_sources(db,root,as_of)
    facts=load_facts(db,root,as_of,qmap);ids=entity_map(db,root,as_of,qmap)
    observations=load_observations(db,root,as_of,qmap,sources,authored,ids)
    links=build_links(db,root,as_of,observations,ids)
    financial_measures(db,root,as_of,facts)
    periods,quarter_terms=quarter_measures(db,root,as_of,facts)
    expected_coverage(db,root,as_of,periods,quarter_terms,observations,ids)
    control_rows=controls(db,root,as_of,facts)
    note_measures(db,root,as_of,observations)
    for pe in sorted({f['period_end'] for f in facts}):
        for name in ['cash_consolidated','debt_interest_bearing','cfo','capex_cash','revenue_total']:
            insert(db,'measures',dict(measure=name,group_id=GROUP,entity_id=PRIMARY,period_end=pe,
                view='as_known',as_of=as_of,variant=BASELINE_VARIANT,status='not_determinable',
                nd_reason='no_SEC_periodic_financial_statement_in_frozen_window',coverage_state='policy_excluded',
                evidence_profile='EDGAR_only_original_policy;JP_evidence_excluded',lineage='[]',tier=2))
    for reason,detail in [
        ('historical_notes_not_processed','Historical primary statements 2021 onward integrated; earlier narrative notes not declared fully read.'),
        ('EDINET_amendment_search_incomplete','Six direct annual originals and their IDs verified; exhaustive statutory amendments/extraordinary-report search unavailable without authenticated listing API.'),
        ('complete_contracts_not_public','Tsubaki, margin-loan and project contracts are financial-note summaries; exact margin thresholds and lender allocations not disclosed.'),
        ('Tsubaki_actual_draw_not_established','August expected draw differs from actual; no numerical outstanding balance inferred from signed USD10bn.'),
        ('anonymous_data_center_warrant_recipient','Energy Global lease incentive warrants do not name the recipient; no OpenAI attribution.'),
        ('Stargate_funded_budget_not_established','USD500bn announced program, GW project capacity and issuer financial responsibility are not proof of SBG cash-funded commitments.'),
        ('JP_GAAP_parent_statements_not_mixed','Japanese parent standalone statements not mixed with consolidated IFRS or holding narrative after eliminations.'),
        ('no_private_counterparty_revenue_denominator','OpenAI annual customer revenue numerator/denominator and actual USD3bn service payments not publicly reconciled.')]:
        insert(db,'exclusions',dict(exclusion_id=digest(['SoftBank_gap',reason]),group_id=GROUP,entity_id=PRIMARY,
            element_type='foreign_source_coverage',element_id=GROUP+':'+reason,reason=reason,detail=detail,
            coverage_state='not_processed' if 'not_processed' in reason else 'not_disclosed',as_of=as_of))
    validation=verify(db,root,as_of,qmap,facts,observations,control_rows)
    from .softbank_reports import render
    render(db,root,as_of,validation)
    return validation

def run(root,from_current_legacy=False):
    as_of=json.loads((root/'work/run.json').read_text())['as_of']
    assert as_of==json.loads((root/'work/softbank/integration_contract.json').read_text())['core_source_cutoff']
    db=create(root)
    source='tables' if from_current_legacy else 'work/softbank/baseline'
    if from_current_legacy:
        existing=duckdb.connect().execute("SELECT count(*) FROM read_parquet('tables/documents.parquet') WHERE group_id=?",[GROUP]).fetchone()[0]
        if existing:raise ValueError('Current exports already contain foreign integration; use immutable baseline mode')
    for table in TABLES:
        db.execute(f"INSERT INTO {table} BY NAME SELECT * FROM read_parquet('{source}/{table}.parquet')")
    result=apply(db,root,as_of);export(db,root/'tables');db.close();return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--from-current-legacy',action='store_true');args=parser.parse_args()
    print(json.dumps(run(Path('.').resolve(),args.from_current_legacy),ensure_ascii=False,default=str))
