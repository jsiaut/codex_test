from __future__ import annotations
from pathlib import Path
import hashlib
import io
import json
import zipfile
import httpx
import yaml
from lxml import etree


def verify(root: Path):
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    url='https://xbrl.fasb.org/us-gaap/2026/us-gaap-2026.zip'
    cache=root/'cache/datasets/us-gaap/2026';cache.mkdir(parents=True,exist_ok=True)
    p=cache/'us-gaap-2026.zip'
    if not p.exists():
        # The user's SEC contact header is NEVER sent to FASB.
        with httpx.Client(timeout=60,follow_redirects=True) as client:
            response=client.get(url);response.raise_for_status();p.write_bytes(response.content)
    with zipfile.ZipFile(io.BytesIO(p.read_bytes())) as archive:
        names=archive.namelist()
        schema_name=next(n for n in names if n.endswith('/us-gaap-2026.xsd'))
        schema=etree.fromstring(archive.read(schema_name),etree.XMLParser(resolve_entities=False,no_network=True,huge_tree=True))
        concepts={e.get('name'):e.get('type') for e in schema if str(e.tag).endswith('}element')}
        anchors=dict(cfg['concept_anchors'],**cfg['concept_anchors_to_verify'])
        missing=[c for values in anchors.values() for c in values if c not in concepts]
        going='SubstantialDoubtAboutGoingConcernTextBlock'
        result={'url':url,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,
            'taxonomy_package':any(n.endswith('META-INF/taxonomyPackage.xml') for n in names),
            'schema_name':schema_name,'concept_count':len(concepts),'missing_anchors':missing,
            'going_concern_concept_present':going in concepts,'going_concern_type':concepts.get(going),
            'tier':'F','use':'concept_definitions_only_not_financial_evidence'}
        (root/'work/taxonomy_verification.json').write_text(json.dumps(result,indent=2))
        print(json.dumps(result))


if __name__=='__main__':verify(Path('.').resolve())
