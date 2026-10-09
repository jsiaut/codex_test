from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json
import sys
import yaml
from .network import SecClient, SessionLock, ResourceUnavailable, AccessPaused, AccessStopped
from .archives import discover,read_xbrl_archive

PERIODIC = {'10-K','10-K/A','10-KT','10-KT/A','10-Q','10-Q/A','10-QT','10-QT/A'}
TEXT_ITEMS = {'1.01','1.02','3.03','8.01'}


def safe_json(path: Path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2))
    temp.replace(path)


def collect(root: Path):
    config=yaml.safe_load((root/'config.yaml').read_text())
    run=json.loads((root/'work/run.json').read_text())
    run['phase']='collection'
    run['status']='collecting'
    run.pop('pause_until',None)
    safe_json(root/'work/run.json',run)
    inventory=json.loads((root/'work/inventory.json').read_text())
    state_path=root/'work/collection.json'
    state=json.loads(state_path.read_text()) if state_path.exists() else {'companyfacts':{},'filings':{},'exclusions':[]}
    with SessionLock(root,config['session_stale_minutes']) as lock:
        client=SecClient(root,config,run['as_of'],lock)
        try:
            # Unbounded companyfacts, including every configured predecessor.
            for group_id,group in inventory['groups'].items():
                for cik in group.get('issuers',{}):
                    if cik in state['companyfacts']:
                        continue
                    url=f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json'
                    try:
                        data=client.json(url)
                        p=root/'work/companyfacts'/f'{cik}.json'
                        safe_json(p,data)
                        state['companyfacts'][cik]={'group':group_id,'path':str(p.relative_to(root)),'url':url,
                            'bytes':len(client.seen[url])}
                        print(json.dumps({'kind':'companyfacts','group':group_id,'cik':cik,'bytes':len(client.seen[url])}),flush=True)
                    except ResourceUnavailable as exc:
                        state['exclusions'].append({'group':group_id,'cik':cik,'element':url,'reason':'not_collected','detail':str(exc)})
                    safe_json(state_path,state)
            queue=[]
            for group_id,group in inventory['groups'].items():
                if group.get('status')!='resolved':
                    continue
                filings=group['filings_in_read_window']
                # Other-form occurrences supplying companyfacts need classification
                # from their own instances before they can enter a measure.
                source_accessions=set()
                for cik in group['issuers']:
                    if cik not in state['companyfacts']:
                        continue
                    data=json.loads((root/state['companyfacts'][cik]['path']).read_text())
                    for namespace,concepts in data.get('facts',{}).items():
                        for details in concepts.values():
                            for series in details.get('units',{}).values():
                                for fact in series:
                                    if group['read_start_provisional']<=fact['end']<=run['as_of'][:10]:
                                        source_accessions.add(fact['accn'])
                for row in filings:
                    form=row['form']
                    items={s.strip() for s in row.get('items','').split(',') if s.strip()}
                    need = form in PERIODIC or form in ('DEF 14A','DEFA14A','424B4') or (
                        form in ('8-K','8-K/A') and bool(items & TEXT_ITEMS)) or row['accessionNumber'] in source_accessions
                    if need:
                        queue.append((-1 if group_id=='SPCX' and form=='424B4' else 0 if form in PERIODIC else 1,group_id,row))
                # Successions are phase-0 pieces, and EX-21 establishes group
                # membership without opening discovery of outside counterparties.
                for cik,issuer in group['issuers'].items():
                    for row in issuer['filings']:
                        if row['form']=='8-K12B':
                            queue.append((-1,group_id,dict(row,cik=cik)))
            queue.sort(key=lambda entry:(entry[0],entry[1],-int(entry[2]['filingDate'].replace('-','')),entry[2]['accessionNumber']))
            state['expected_filings']=[r['accessionNumber'] for _,g,r in queue]
            safe_json(state_path,state)
            for priority,group_id,row in queue:
                accession=row['accessionNumber']
                if accession in state['filings']:
                    saved=state['filings'][accession]
                    if saved.get('discovery_path'):
                        old_disc=json.loads((root/saved['discovery_path']).read_text())
                        legacy_instances=[h['filename'] for h in old_disc['headers'] if h['type']=='EX-101.INS']
                        missing=[n for n in legacy_instances if n not in saved['resources']]
                        if missing:
                            for name in missing:
                                try:
                                    raw=client.get(old_disc['base']+name)
                                    p=root/'work/filings'/accession/name
                                    p.write_bytes(raw)
                                    saved['resources'][name]={'path':str(p.relative_to(root)),'bytes':len(raw),
                                        'url':old_disc['base']+name,'from_archive':False}
                                except ResourceUnavailable as exc:
                                    state['exclusions'].append({'group':group_id,'accession':accession,
                                        'element':name,'reason':'not_collected','detail':str(exc)})
                            old_disc['instances']=sorted(set(old_disc['instances']+legacy_instances))
                            safe_json(root/saved['discovery_path'],old_disc)
                            safe_json(state_path,state)
                    continue
                target=root/'work/filings'/accession
                target.mkdir(parents=True,exist_ok=True)
                result={'group':group_id,'metadata':row,'resources':{},'status':'in_progress'}
                try:
                    disc=discover(client,row['cik'],accession)
                    safe_json(target/'discovery.json',disc)
                    result['discovery_path']=str((target/'discovery.json').relative_to(root))
                    files=read_xbrl_archive(client,disc) if priority==0 or row['form'] not in ('8-K','8-K/A') else {}
                    resources={row.get('primaryDocument','')}
                    if disc['xbrl_archives']:
                        resources.update(disc['instances'])
                        if disc['filing_summary']:
                            resources.add(disc['filing_summary'])
                        if disc['metalinks']:
                            resources.add(disc['metalinks'])
                    if row['form'] in PERIODIC:
                        resources.update(h['filename'] for h in disc['headers'] if h['type'].startswith(('EX-21','EX-99','EX-23')))
                    if row['form'] in ('8-K','8-K/A'):
                        resources.update(h['filename'] for h in disc['headers'] if h['type'].startswith(('EX-10','EX-4','EX-99','EX-23')))
                    resources.update(n for n in files if n.endswith(('.xsd','_pre.xml','_cal.xml','_lab.xml','_def.xml')))
                    # An ordinary primary 8-K is always kept to associate each
                    # exhibit with filed/furnished items; no filename heuristics.
                    for name in sorted(resources):
                        if not name:
                            continue
                        try:
                            raw=files[name] if name in files else client.get(disc['base']+name)
                            (target/name).write_bytes(raw)
                            result['resources'][name]={'path':str((target/name).relative_to(root)),
                                'bytes':len(raw),'url':disc['base']+name,'from_archive':name in files}
                        except ResourceUnavailable as exc:
                            state['exclusions'].append({'group':group_id,'accession':accession,'element':name,
                                'reason':'not_collected','detail':str(exc)})
                    result['status']='collected'
                except ResourceUnavailable as exc:
                    result['status']='not_collected'
                    state['exclusions'].append({'group':group_id,'accession':accession,'element':'filing',
                        'reason':'not_collected','detail':str(exc)})
                state['filings'][accession]=result
                safe_json(state_path,state)
                print(json.dumps({'kind':'filing','group':group_id,'form':row['form'],'accession':accession,
                    'status':result['status'],'resources':len(result['resources']),
                    'done':len(state['filings']),'expected':len(set(state['expected_filings']))}),flush=True)
            run['status']='collection_complete'
            safe_json(root/'work/run.json',run)
        except AccessPaused as exc:
            run.update(status='sec_cooldown',pause_until=exc.until)
            safe_json(root/'work/run.json',run)
            print(str(exc),flush=True)
            return 75
        except AccessStopped as exc:
            run.update(status='stopped_sec_access',reason=str(exc))
            safe_json(root/'work/run.json',run)
            print(str(exc),flush=True)
            return 76
        finally:
            client.close()
    return 0


if __name__=='__main__':
    sys.exit(collect(Path('.').resolve()))
