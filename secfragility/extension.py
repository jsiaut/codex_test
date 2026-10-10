"""Inventory the authorized notes using filed presentation roles, not names in prose.

The serving/validation path remains reader; this module never authors observations.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse, json, re
import yaml
from .metadata import load as load_metadata
from .text import extract_inline_blocks, extract_classic_blocks, normalize_html, content_key
from .xbrl import parse_instance, digest
from .evidence import periodic_assurance

PATTERNS = {
    'investments_note': r'investment|\bsecurit|financial instruments|fair value|joint venture|variable interest|unconsolidated|subsequent event',
    'debt_note': r'\bdebt\b|borrow|notes payable|revolving|liabilities|financial instruments',
    'lease_note': r'lease',
    'commitments_note': r'commitment|contingen|guarantee|joint venture|variable interest|unconsolidated|subsequent event',
    'concentration_narrative': r'concentration|credit.*risk|revenue|segment|geograph|accounting polic|supplemental financial|supplemental balance|balance sheet.*component|consolidated balance sheets components',
}

def families(label):
    return [family for family, pattern in PATTERNS.items() if re.search(pattern, label, re.I)]

def contains(parent, child):
    return all(any(a <= c and d <= z for a, z in parent['source_ranges'])
               for c, d in child['source_ranges'])

def bounded_html_notes(root, cfg, run, collection):
    """Rebuild explicitly bounded, untagged IPO notes from immutable sources."""
    registry = root/'work/extension_html_bounds.json'
    if not registry.exists():return []
    output=[]
    for bound in json.loads(registry.read_text()):
        filing=collection['filings'][bound['accession']];meta=filing['metadata']
        resource=filing['resources'][meta['primaryDocument']]
        raw=(root/resource['path']).read_bytes()
        start,end=bound['raw_byte_start'],bound['raw_byte_end']
        if not 0<=start<end<=len(raw):raise ValueError('Invalid explicit IPO note bounds')
        selected=[f for f in PATTERNS if f in families(bound['label']) and f in cfg['text_components']]
        if not selected:continue
        text=normalize_html(raw[start:end]);key=content_key(text,[],cfg['normalizer_version'])
        document_id=digest([resource['url']]);occurrence=digest([key,document_id,start])
        block=dict(content_key=key,occurrence_id=occurrence,text=text,candidates=[],
            label=bound['label'],concept='untagged_annual_note' if bound['assurance_level']=='audited' else 'untagged_unaudited_note',
            raw_byte_start=start,raw_byte_end=end,source_ranges=[[start,end]],
            group=bound['group'],accession=bound['accession'],entity_id='cik:'+meta['cik'],
            form=meta['form'],knowledge_date=meta['filingDate'],acceptance_datetime=meta['acceptanceDateTime'],
            source_path=resource['path'],document_id=document_id,as_of=run['as_of'],
            assurance_level=bound['assurance_level'],
            location='annual_audited_notes_in_424B4' if bound['assurance_level']=='audited' else 'unaudited_notes_in_424B4',
            block_class=selected[0],priority=list(PATTERNS).index(selected[0]),
            financial_note=True,note_families=selected,report_period_end=bound['report_period_end'])
        path=root/'work/blocks'/(occurrence+'.json')
        if not path.exists():path.write_text(json.dumps(block,ensure_ascii=False))
        output.append(dict(content_key=key,occurrence_id=occurrence,path=str(path.relative_to(root)),
            group=bound['group'],accession=bound['accession'],block_class=selected[0],note_families=selected,
            chars=len(text),candidates=0,knowledge_date=meta['filingDate']))
    return output

def save_inventory(root, records, exclusions, report_inventory=None):
    run=json.loads((root/'work/run.json').read_text())
    # Newest reports first across the five authorized note families.
    records.sort(key=lambda r:(-int(r['knowledge_date'].replace('-','')),
        list(PATTERNS).index(r['block_class']),r['group'],r['accession'],r['occurrence_id']))
    first=json.loads((root/'work/first_pass_queue.json').read_text())
    first_occurrences={r['occurrence_id'] for r in first}
    combined=first+[r for r in records if r['occurrence_id'] not in first_occurrences]
    seen=set()
    for row in combined:row['duplicate']=row['content_key'] in seen;seen.add(row['content_key'])
    for name,value in [('extension_queue',records),('queue',combined),('extension_exclusions',exclusions)]:
        (root/('work/'+name+'.json')).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    if report_inventory is not None:
        (root/'work/extension_note_reports.json').write_text(json.dumps(report_inventory,ensure_ascii=False,indent=2)+'\n')
    unique={r['content_key']:r for r in records}
    reused={k for k in unique if (root/'work/observations'/(k+'.jsonl')).exists()}
    new=[r for k,r in unique.items() if k not in reused]
    volume=dict(as_of=run['as_of'],measured_at=datetime.now(timezone.utc).isoformat(),
        occurrences=len(records),unique_blocks=len(unique),reused_blocks=len(reused),
        remaining_blocks=len(new),remaining_text_chars=sum(r['chars'] for r in new),
        remaining_candidates=sum(r['candidates'] for r in new),
        remaining_by_group=dict(Counter(r['group'] for r in new)),
        remaining_by_primary_family=dict(Counter(r['block_class'] for r in new)),
        extraction_exclusions=exclusions,additional_sec_requests=0,
        reading_duration_estimate='not_established_before_extension_reading',
        criteria_changed=False,independent_audit_performed=False)
    (root/'work/extension_volume.json').write_text(json.dumps(volume,ensure_ascii=False,indent=2)+'\n')
    run.update(phase='extension_reading',status='in_progress')
    (root/'work/run.json').write_text(json.dumps(run,indent=2)+'\n')
    return volume

def refresh(root):
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    run=json.loads((root/'work/run.json').read_text())
    collection=json.loads((root/'work/collection.json').read_text())
    records=json.loads((root/'work/extension_queue.json').read_text())
    by_occurrence={r['occurrence_id']:r for r in records}
    for row in bounded_html_notes(root,cfg,run,collection):by_occurrence.setdefault(row['occurrence_id'],row)
    exclusions=json.loads((root/'work/extension_exclusions.json').read_text())
    recovered={b['accession'] for b in json.loads((root/'work/extension_html_bounds.json').read_text())}
    for row in exclusions:
        if row['accession'] in recovered:row['detail']='No XBRL note presentation metadata; explicitly bounded HTML notes recovered separately.'
    return save_inventory(root,list(by_occurrence.values()),exclusions)

def inventory(root):
    cfg = yaml.safe_load((root/'config.yaml').read_text())
    assert 'text' in cfg['scope']
    opened = set(cfg['text_components'])
    run = json.loads((root/'work/run.json').read_text())
    collection = json.loads((root/'work/collection.json').read_text())
    issuers = json.loads((root/'work/inventory.json').read_text())['groups']
    replacements = json.loads((root/'work/deprecations.json').read_text())['mapping']
    records, exclusions, report_inventory = [], [], []
    directory = root/'work/blocks'; directory.mkdir(exist_ok=True)
    for accession, filing in collection['filings'].items():
        meta = filing['metadata']; group = filing['group']
        if meta['form'] not in ('10-K', '10-K/A', '10-Q', '10-Q/A', '424B4'):
            continue
        floor = issuers[group].get('read_start', issuers[group]['read_start_provisional'])
        if (meta.get('reportDate') or meta['filingDate']) < floor:
            continue
        if filing['status'] != 'collected':
            exclusions.append(dict(group=group,accession=accession,reason='not_collected'))
            continue
        resources = filing['resources']
        metadata = load_metadata(root, resources, accession)
        if not metadata:
            exclusions.append(dict(group=group,accession=accession,reason='parse_failed',
                detail='No XBRL note presentation metadata; HTML notes require explicit bounds.'))
            continue
        instance = next(iter(metadata['instance'].values()))
        role_families = {}
        for report in instance['report'].values():
            if report.get('menuCat') != 'Notes' or report.get('groupType') != 'disclosure':
                continue
            label = report.get('shortName') or report.get('longName') or ''
            found = sorted(set(families(label)) & opened)
            report_inventory.append(dict(group=group,accession=accession,label=label,
                role=report['role'],families=found))
            if found:role_families[report['role']] = found
        if not role_families:continue
        resource = resources.get(meta['primaryDocument'])
        if not resource:
            exclusions.append(dict(group=group,accession=accession,reason='not_collected',detail='primary document missing'))
            continue
        disc = json.loads((root/filing['discovery_path']).read_text()) if filing.get('discovery_path') else {}
        candidates = []
        for name, res in resources.items():
            if name not in disc.get('instances', []) and not name.endswith('_htm.xml'):continue
            candidates.extend(parse_instance((root/res['path']).read_bytes(),
                entity_id='cik:'+meta['cik'],reporting_identity='reporter:'+group,group_id=group,
                document_id=digest([res['url']]),accession=accession,
                acceptance_datetime=meta['acceptanceDateTime'],knowledge_date=meta['filingDate'],
                assurance_level=periodic_assurance(meta['form']),as_of=run['as_of'],
                taxonomy_replacements=replacements,
                reporting_scope='as_if_combined' if group=='SPCX' else 'consolidated'))
        raw = (root/resource['path']).read_bytes()
        try:
            if b'ix:nonnumeric' in raw.lower():
                natural = extract_inline_blocks(raw,metadata,candidates,normalizer_version=cfg['normalizer_version'])
            else:
                name = next((n for n in disc.get('instances',[]) if n in resources),None)
                if not name:raise ValueError('no classic note instance')
                resource = resources[name]
                natural = extract_classic_blocks((root/resource['path']).read_bytes(),metadata,candidates,
                    normalizer_version=cfg['normalizer_version'])
        except Exception as exc:
            exclusions.append(dict(group=group,accession=accession,reason='parse_failed',detail=str(exc)))
            continue
        selected = []
        for block in natural:
            found = sorted({family for role in block['note_roles'] for family in role_families.get(role,[])})
            if found:selected.append(dict(block,note_families=found))
        # A full note contains its separately tagged tables/policies. Read the
        # enclosing natural note once with ALL numeric candidates, without
        # lexical filtering inside it. Disjoint ranges remain separate blocks.
        selected = [b for i,b in enumerate(selected) if not any(
            i != j and contains(p,b) and (len(p['text']) > len(b['text']) or
              len(p['text']) == len(b['text']) and j < i)
            for j,p in enumerate(selected))]
        for block in selected:
            primary = next(f for f in PATTERNS if f in block['note_families'])
            block.update(group=group,accession=accession,entity_id='cik:'+meta['cik'],
                form=meta['form'],knowledge_date=meta['filingDate'],
                acceptance_datetime=meta['acceptanceDateTime'],source_path=resource['path'],
                document_id=digest([resource['url']]),as_of=run['as_of'],
                assurance_level=periodic_assurance(meta['form']),
                location='financial_statements_or_notes',block_class=primary,
                priority=list(PATTERNS).index(primary),financial_note=True)
            occurrence = digest([block['content_key'],block['document_id'],block['raw_byte_start']])
            block['occurrence_id'] = occurrence
            path = directory/(occurrence+'.json')
            # Existing first-pass block metadata/assurance must not be mutated.
            if not path.exists():path.write_text(json.dumps(block,ensure_ascii=False,default=str))
            records.append(dict(content_key=block['content_key'],occurrence_id=occurrence,
                path=str(path.relative_to(root)),group=group,accession=accession,
                block_class=primary,note_families=block['note_families'],chars=len(block['text']),
                knowledge_date=meta['filingDate'],candidates=len(block['candidates'])))
        print(json.dumps(dict(stage='note_inventory',group=group,accession=accession,
            selected=len(selected))),flush=True)
    records.extend(bounded_html_notes(root,cfg,run,collection))
    volume=save_inventory(root,records,exclusions,report_inventory)
    print(json.dumps(dict(stage='volume',**volume),ensure_ascii=False),flush=True)
    return volume

if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['inventory','refresh'])
    args=parser.parse_args();print(json.dumps((inventory if args.action=='inventory' else refresh)(Path('.').resolve())))
