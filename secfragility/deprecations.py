from pathlib import Path
from lxml import etree
import json,zipfile,hashlib

L='{http://www.xbrl.org/2003/linkbase}';X='{http://www.w3.org/1999/xlink}'


def build(root:Path):
    package=root/'cache/datasets/us-gaap/2026/us-gaap-2026.zip';z=zipfile.ZipFile(package)
    name='us-gaap-2026/elts/us-gaap-depcon-def-2026.xml';t=etree.fromstring(z.read(name))
    candidates={};excluded=[]
    for link in t.iter(L+'definitionLink'):
        loc={n.get(X+'label'):n.get(X+'href').split('#')[-1].replace('_',':',1) for n in link if n.tag==L+'loc'}
        for a in link:
            if a.tag!=L+'definitionArc':continue
            role=a.get(X+'arcrole');current,old=loc.get(a.get(X+'from')),loc.get(a.get(X+'to'))
            if not old or not current:continue
            if role in ('http://www.xbrl.org/2009/arcrole/dep-concept-deprecatedConcept','http://www.xbrl.org/2003/arcrole/essence-alias'):
                candidates.setdefault(old,set()).add(current)
            else:excluded.append({'old':old,'replacement':current,'reason':'dimensional_partial_or_mutually_exclusive_deprecation','arcrole':role})
    mapping={old:next(iter(values)) for old,values in candidates.items() if len(values)==1}
    # Flatten only acyclic chains of whole-concept replacements.
    for old in list(mapping):
        current=mapping[old];seen={old}
        while current in mapping:
            if current in seen:raise ValueError('Cycle in official deprecation map')
            seen.add(current);current=mapping[current]
        mapping[old]=current
    out={'package_url':'https://xbrl.fasb.org/us-gaap/2026/us-gaap-2026.zip',
         'package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'source_member':name,
         'mapping':mapping,'excluded_non_whole_concept':excluded,
         'ambiguous':[old for old,v in candidates.items() if len(v)!=1]}
    (root/'work/deprecations.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({'whole_concept_replacements':len(mapping),'not_flattened':len(excluded),'ambiguous':len(out['ambiguous'])}))
    return mapping

if __name__=='__main__':build(Path('.').resolve())
