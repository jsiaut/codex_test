"""Resumable SMCI SEC collection and complete natural-note nomination.

No observations are authored by this module. Every nominated note is served to
the executing analyst, including notes with no AI keywords.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re,tarfile
import zstandard
import yaml
from .network import SecClient, SessionLock, atomic_json
from .inventory import collect_submissions
from .archives import discover, read_xbrl_archive
from .metadata import load
from .xbrl import parse_instance, digest
from .text import extract_inline_blocks, extract_classic_blocks, normalize_html
from .extension import contains

CIK='0001375365'
GROUP='SMCI'
PERIODIC={'10-K','10-K/A','10-Q','10-Q/A'}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def state(root):return root/'work/smci'
def persist(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,sort_keys=True,default=str)+'\n')
    tmp.replace(path)

def inventory(root,sec):
    base=state(root);path=base/'issuer.json'
    if path.exists():return json.loads(path.read_text())
    issuer=collect_submissions(sec,CIK)
    if str(issuer['metadata']['cik']).zfill(10)!=CIK or 'SMCI' not in issuer['metadata']['tickers']:
        raise ValueError('SMCI official identity mismatch')
    cutoff=datetime.fromisoformat(sec.as_of)
    def eligible(f):
        accept=f.get('acceptanceDateTime')
        return bool(accept and datetime.fromisoformat(accept.replace('Z','+00:00'))<=cutoff)
    all_known=[dict(f,cik=CIK) for f in issuer['filings'] if eligible(f)]
    periodic=[f for f in all_known if f['form'] in PERIODIC and f.get('reportDate','')>='2018-07-01']
    current=[f for f in all_known if f['form'] in ('8-K','8-K/A','NT 10-K','NT 10-Q') and f['filingDate']>='2023-07-01']
    result=dict(official=issuer,periodic=periodic,current_reports=current,
        source_cutoff=sec.as_of,identity_verified=True,history_pages_complete=not issuer['pagination']['failed'])
    persist(path,result)
    raw=sec.get('https://data.sec.gov/api/xbrl/companyfacts/CIK'+CIK+'.json')
    (base/'companyfacts.json').write_bytes(raw)
    print(json.dumps(dict(stage='SMCI_identity',name=issuer['metadata']['name'],periodic=len(periodic),
        current_reports=len(current),pages=issuer['pagination'])),flush=True)
    return result

def collect_one(root,sec,f,registry):
    f=dict(f,cik=CIK)
    accession=f['accessionNumber']
    if accession in registry:return
    d=discover(sec,CIK,accession)
    archive=read_xbrl_archive(sec,d) if f['form'] in PERIODIC else {}
    names=set(d['instances'])|{f['primaryDocument']}|{n for n in (d['filing_summary'],d['metalinks']) if n}
    # Presentation/definition/calculation/labels support admissibility and controls.
    names|={n for n in archive if n.endswith(('.xml','.xsd')) and not re.fullmatch(r'R\d+\.xml',n)}
    # Keep EX21/EX23 original legal/auditor evidence. Contract selection is
    # recorded separately from an exhibit's incorporation-by-reference pointer.
    names|={h['filename'] for h in d['headers'] if h['type'].startswith(('EX-21','EX-23'))}
    if f['form'] in ('8-K','8-K/A'):
        names|={h['filename'] for h in d['headers'] if re.match(r'^EX-(?:10|4|16|99)(?:\.|$)',h['type'])}
    directory=state(root)/'sources'/accession;directory.mkdir(parents=True,exist_ok=True)
    resources={}
    for name in sorted(names):
        raw=archive.get(name)
        if raw is None:raw=sec.get(d['base']+name)
        p=directory/name;p.write_bytes(raw)
        header=next((h for h in d['headers'] if h['filename']==name),None)
        resources[name]=dict(path=str(p.relative_to(root)),url=d['base']+name,sha256=sha(p),bytes=len(raw),
            document_rank=header['document_rank'] if header else -2,exhibit_type=header.get('type') if header else None)
    registry[accession]=dict(metadata=f,group=GROUP,resources=resources,discovery=d,status='collected',
        retrieved_at=datetime.now(timezone.utc).isoformat())
    persist(state(root)/'filings.json',registry)
    print(json.dumps(dict(stage='SMCI_filing',form=f['form'],accession=accession,files=len(resources))),flush=True)

def collect(root):
    base=state(root);base.mkdir(parents=True,exist_ok=True)
    cfg=yaml.safe_load((root/'config.yaml').read_text());asof=json.loads((root/'work/run.json').read_text())['as_of']
    with SessionLock(root,cfg['session_stale_minutes']) as lock:
        sec=SecClient(root,cfg,asof,lock)
        try:
            inv=inventory(root,sec)
            path=base/'filings.json';registry=json.loads(path.read_text()) if path.exists() else {}
            for f in sorted(inv['periodic'],key=lambda f:(f['filingDate'],f['accessionNumber']),reverse=True):
                collect_one(root,sec,f,registry)
            # Complete metadata inspection of all 8-Ks; collect material
            # contract/termination/rights reports and auditor/distress signals.
            items={'1.01','1.02','3.03','3.01','8.01','2.04','4.01','4.02','1.03','2.02'}
            proxies=[f for f in inv['official']['filings'] if f['form']=='DEF 14A' and f.get('acceptanceDateTime') and datetime.fromisoformat(f['acceptanceDateTime'].replace('Z','+00:00'))<=datetime.fromisoformat(asof)]
            if proxies:collect_one(root,sec,max(proxies,key=lambda f:f['filingDate']),registry)
            for f in inv['current_reports']:
                if f['form'].startswith('NT ') or items.intersection(x.strip() for x in f.get('items','').split(',')):
                    collect_one(root,sec,f,registry)
        finally:sec.close()

def nominate(root):
    base=state(root);cfg=yaml.safe_load((root/'config.yaml').read_text())
    registry=json.loads((base/'filings.json').read_text());blocks=[];coverage=[]
    for accession,filing in sorted(registry.items()):
        m=filing['metadata'];res=filing['resources'];primary=res[m['primaryDocument']]
        if m['form'] not in PERIODIC:
            text=normalize_html((root/primary['path']).read_bytes())
            p=base/'text'/(accession+'.txt');p.parent.mkdir(exist_ok=True);p.write_text(text)
            for name,r in res.items():
                if r.get('exhibit_type','') and re.match(r'^EX-(?:10|4|16|99)(?:\.|$)',r['exhibit_type']):
                    q=base/'text'/(accession+'_'+name+'.txt');q.write_text(normalize_html((root/r['path']).read_bytes()))
            continue
        meta=load(root,res,accession)
        if not meta:raise ValueError('Missing natural-note metadata '+accession)
        facts=[]
        for name in filing['discovery']['instances']:
            r=res[name]
            facts+=parse_instance((root/r['path']).read_bytes(),entity_id='cik:'+CIK,reporting_identity='reporter:SMCI',
                group_id=GROUP,document_id=digest([r['url']]),accession=accession,
                acceptance_datetime=m['acceptanceDateTime'],knowledge_date=m['filingDate'],
                assurance_level='audited' if m['form'].startswith('10-K') else 'reviewed',as_of=json.loads((root/'work/run.json').read_text())['as_of'])
        raw=(root/primary['path']).read_bytes()
        bs=extract_inline_blocks(raw,meta,facts,normalizer_version=cfg['normalizer_version'])
        if not bs:
            for name in filing['discovery']['instances']:
                r=res[name]
                for b in extract_classic_blocks((root/r['path']).read_bytes(),meta,facts,normalizer_version=cfg['normalizer_version']):
                    b['resource_override']=r;bs.append(b)
        roles={r['role'] for inst in meta['instance'].values() for r in inst['report'].values()
            if r.get('menuCat')=='Notes' and r.get('groupType')=='disclosure' and not r['role'].startswith('http://xbrl.sec.gov/ecd/')}
        selected=[]
        for b in bs:
            if not roles.intersection(b.get('note_roles',[])):continue
            label=b.get('label','')+' '+b.get('concept','')+' '+' '.join(b.get('note_roles',[]))
            include=bool(re.search(r'financ|credit|receiv|invest|related.?part|debt|lease|commit|contingen|concentr|revenue|segment|subsequent|fair.?value|significant.?account|accounting.?polic|balance.?sheet.?component|stockholders.?equity',label,re.I))
            if re.search(r'cybersecurity',label,re.I):include=False
            if m['reportDate']<'2020-07-01':include=bool(re.search(r'invest|related.?part',label,re.I))
            if include:selected.append(b)
        parents=[b for b in selected if not any(o is not b and contains(o,b) and
            (len(o['text'])>len(b['text']) or o['raw_byte_start']<b['raw_byte_start']) for o in selected)]
        for b in parents:
            r=b.pop('resource_override',primary)
            b.update(accession=accession,form=m['form'],report_date=m['reportDate'],knowledge_date=m['filingDate'],
                document_url=r['url'],source_path=r['path'],document_id=digest([r['url']]))
            key=digest([accession,b['content_key'],b['raw_byte_start']]);p=base/'blocks'/(key+'.json');p.parent.mkdir(exist_ok=True)
            persist(p,b)
            blocks.append(dict(key=key,content_key=b['content_key'],accession=accession,form=m['form'],
                report_date=m['reportDate'],label=b.get('label'),chars=len(b['text']),path=str(p.relative_to(root))))
        coverage.append(dict(accession=accession,form=m['form'],report_date=m['reportDate'],notes=len(parents),
            scope='all_selected_note_families' if m['reportDate']>='2020-07-01' else 'prior_relationship_history'))
        p=base/'text'/(accession+'.txt');p.parent.mkdir(exist_ok=True);p.write_text(normalize_html(raw))
    persist(base/'reading_queue.json',blocks);persist(base/'note_coverage.json',coverage)
    print(json.dumps(dict(notes=len(blocks),chars=sum(x['chars'] for x in blocks),reports=len(coverage))),flush=True)

def backup(root):
    base=state(root);path=base/'SEC_SMCI_originals.tar.zst';temporary=path.with_suffix('.partial')
    with temporary.open('wb') as out,zstandard.ZstdCompressor(level=8).stream_writer(out,closefd=False) as z:
        with tarfile.open(fileobj=z,mode='w|') as tar:
            for p in sorted((base/'sources').rglob('*')):
                if p.is_file():tar.add(p,arcname=str(p.relative_to(root)),recursive=False)
            for name in ['companyfacts.json','issuer.json','filings.json']:tar.add(base/name,arcname='work/smci/'+name)
    temporary.replace(path)
    persist(base/'source_backup.json',dict(path=str(path.relative_to(root)),sha256=sha(path),bytes=path.stat().st_size,
        contains='All collected SEC original bytes, complete source registry and unbounded companyfacts',
        source_cutoff=json.loads((base/'issuer.json').read_text())['source_cutoff']))
    print(json.dumps(dict(stage='SMCI_raw_source_backup',bytes=path.stat().st_size,sha256=sha(path))),flush=True)

def restore(root):
    base=state(root);manifest=json.loads((base/'source_backup.json').read_text());archive=root/manifest['path']
    if sha(archive)!=manifest['sha256']:raise ValueError('SMCI source archive hash mismatch')
    count=0
    with archive.open('rb') as handle,zstandard.ZstdDecompressor().stream_reader(handle) as stream:
        with tarfile.open(fileobj=stream,mode='r|') as tar:
            for member in tar:
                path=Path(member.name)
                if path.is_absolute() or '..' in path.parts or path.parts[:2]!=('work','smci') or not member.isfile():
                    raise ValueError('Unexpected archive member')
                # Never overwrite later versioned analysis or inventory files.
                target=root/path
                if target.exists():continue
                target.parent.mkdir(parents=True,exist_ok=True)
                with tar.extractfile(member) as source:target.write_bytes(source.read())
                count+=1
    print(json.dumps(dict(stage='SMCI_source_restore',restored_files=count)),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['collect','nominate','backup','restore']);a=p.parse_args()
    globals()[a.action](Path('.').resolve())
