"""Presentation metadata for classic filings without MetaLinks.json."""
from pathlib import Path
from lxml import etree
from functools import lru_cache
import zipfile,json

L='{http://www.xbrl.org/2003/linkbase}';X='{http://www.w3.org/1999/xlink}'
P=etree.XMLParser(resolve_entities=False,no_network=True,huge_tree=True)


def first_financial_note_role(instance: dict):
    """Issuer report order among financial notes, excluding SEC governance tags.

    ECD and CYD disclosures also use MenuCategory=Notes. They do not become
    the financial statements' Note 1 merely by preceding it in FilingSummary.
    """
    roles={r['role']:int(r.get('order',999999)) for r in instance['report'].values()
        if r.get('menuCat')=='Notes' and r.get('groupType')=='disclosure'
        and not r['role'].startswith('http://xbrl.sec.gov/ecd/')}
    financial={role:order for role,order in roles.items() if any(
        tag.get('xbrltype')=='textBlockItemType'
        and name.split('_',1)[0] not in {'ecd','cyd','dei'}
        and role in (tag.get('presentation') or [])
        for name,tag in instance['tag'].items())}
    return min(financial,key=financial.get) if financial else None


def enrich_report_order(metadata: dict, summary_raw: bytes, summary_path: str):
    """Join native MetaLinks reports to actual FilingSummary roles exactly.

    Older MetaLinks has neither MenuCategory nor report order. Its dictionary
    order is not the issuer's presentation order.
    """
    summary=etree.fromstring(summary_raw,P)
    by_role={}
    for order,report in enumerate(summary.findall('.//Report')):
        role=report.findtext('Role') or report.findtext('RoleURI')
        if role and role not in by_role:
            by_role[role]={'menuCat':report.findtext('MenuCategory') or '',
                'order':str(order),'metadata_source':summary_path}
    for instance in metadata['instance'].values():
        for report in instance['report'].values():
            if report['role'] in by_role:report.update(by_role[report['role']])
    return metadata


@lru_cache(maxsize=1)
def standard(root_string):
    z=zipfile.ZipFile(Path(root_string)/'cache/datasets/us-gaap/2026/us-gaap-2026.zip')
    schema=etree.fromstring(z.read('us-gaap-2026/elts/us-gaap-2026.xsd'),P)
    tags={'us-gaap_'+n.get('name'):{'xbrltype':n.get('type','').split(':')[-1],
      'lang':{'en-us':{'role':{}}},'presentation':[], 'auth_ref':[],
      'definition_source':'pinned_FASB_2026_documentation'} for n in schema if str(n.tag).endswith('}element')}
    for filename in ['us-gaap-lab-2026.xml','us-gaap-doc-2026.xml']:
        tree=etree.fromstring(z.read('us-gaap-2026/elts/'+filename),P)
        for link in tree.iter(L+'labelLink'):
            loc={n.get(X+'label'):n.get(X+'href').split('#')[-1] for n in link if n.tag==L+'loc'}
            labels={n.get(X+'label'):n for n in link if n.tag==L+'label'}
            for arc in link:
                if arc.tag!=L+'labelArc':continue
                concept=loc.get(arc.get(X+'from'));lab=labels.get(arc.get(X+'to'))
                if concept not in tags or lab is None:continue
                tags[concept]['lang']['en-us']['role'][lab.get(X+'role','').split('/')[-1]]=lab.text or ''
    return tags


def load(root:Path,resources:dict,accession:str):
    if 'MetaLinks.json' in resources:
        metadata=json.loads((root/resources['MetaLinks.json']['path']).read_text())
        if 'FilingSummary.xml' in resources:
            metadata=enrich_report_order(metadata,(root/resources['FilingSummary.xml']['path']).read_bytes(),resources['FilingSummary.xml']['path'])
        return metadata
    if 'FilingSummary.xml' not in resources:return None
    reports={};tags={};fallback=standard(str(root));schema_tags={}
    for name,res in resources.items():
        if not name.endswith('.xsd'):continue
        schema=etree.fromstring((root/res['path']).read_bytes(),P)
        for n in schema:
            if str(n.tag).endswith('}element') and n.get('id'):
                schema_tags[n.get('id')]={'xbrltype':n.get('type','').split(':')[-1],
                  'lang':{'en-us':{'role':{}}},'presentation':[],'auth_ref':[],'definition_source':res['path']}
    summary=etree.fromstring((root/resources['FilingSummary.xml']['path']).read_bytes(),P)
    for i,r in enumerate(summary.findall('.//Report')):
        role=r.findtext('Role') or r.findtext('RoleURI');short=r.findtext('ShortName') or ''
        long=r.findtext('LongName') or '';cat=r.findtext('MenuCategory') or ''
        if not role:continue
        group='statement' if cat=='Statements' or 'Statement -' in long else 'disclosure'
        reports['R'+str(i)]={'role':role,'shortName':short,'longName':long,'menuCat':cat,
          'groupType':group,'order':str(i),'metadata_source':resources['FilingSummary.xml']['path']}
    for name,res in resources.items():
        if not name.endswith('_pre.xml'):continue
        tree=etree.fromstring((root/res['path']).read_bytes(),P)
        for link in tree.iter(L+'presentationLink'):
            role=link.get(X+'role')
            for n in link:
                if n.tag!=L+'loc':continue
                key=n.get(X+'href').split('#')[-1]
                if key not in tags:
                    original=schema_tags.get(key) or fallback.get(key)
                    if not original:
                        # A historical standard concept can have disappeared
                        # from the pinned modern schema. Its actual filed
                        # presentation remains evidence for component controls;
                        # absence of its type/definition cannot erase an arc.
                        original={'xbrltype':'unknown','lang':{'en-us':{'role':{}}},
                            'presentation':[],'auth_ref':[],
                            'definition_source':'unresolved_historical_type_and_definition'}
                    tags[key]=json.loads(json.dumps(original))
                if role not in tags[key]['presentation']:tags[key]['presentation'].append(role)
    for name,res in resources.items():
        if not name.endswith('_lab.xml'):continue
        tree=etree.fromstring((root/res['path']).read_bytes(),P)
        for link in tree.iter(L+'labelLink'):
            loc={n.get(X+'label'):n.get(X+'href').split('#')[-1] for n in link if n.tag==L+'loc'}
            labs={n.get(X+'label'):n for n in link if n.tag==L+'label'}
            for a in link:
                if a.tag!=L+'labelArc':continue
                key=loc.get(a.get(X+'from'));lab=labs.get(a.get(X+'to'))
                if key in tags and lab is not None:tags[key]['lang']['en-us']['role'][lab.get(X+'role','').split('/')[-1]]=lab.text or ''
    result={'instance':{accession:{'report':reports,'tag':tags}},'metadata_origin':'issuer_FilingSummary_and_linkbases_with_pinned_standard_types_and_definitions'}
    dest=root/'work/compiled_metadata';dest.mkdir(parents=True,exist_ok=True)
    (dest/(accession+'.json')).write_text(json.dumps(result,ensure_ascii=False))
    return result
