"""Physical SGML document order and proven origins of derived inline facts."""
from pathlib import Path
import json
from functools import lru_cache
from .text import parse_html,local_tag
from .xbrl import digest


@lru_cache(maxsize=2048)
def provenance(root_string: str, accession: str):
    root=Path(root_string)
    filing=json.loads((root/'work/collection.json').read_text())['filings'][accession]
    resources=filing['resources']
    discovery=json.loads((root/filing['discovery_path']).read_text()) if filing.get('discovery_path') else {}
    names={};inline={}
    for header in discovery.get('headers',[]):
        name=header['filename'];rank=header['document_rank']
        names.setdefault(name,set()).add(rank)
        if name not in resources:continue
        raw=(root/resources[name]['path']).read_bytes()
        if b'ix:nonfraction' not in raw.lower() and b'ix:fraction' not in raw.lower():continue
        document_id=digest([resources[name]['url']])
        for node in parse_html(raw).iter():
            if local_tag(node) not in ('ix:nonfraction','ix:fraction') or not node.get('id'):continue
            inline.setdefault(node.get('id'),set()).add((rank,document_id,node.get('name')))
    return {'physical':{name:next(iter(ranks)) for name,ranks in names.items() if len(ranks)==1},
        'inline':inline}


def fact_order(name: str, fact: dict, source: dict):
    if name in source['physical']:
        return source['physical'][name],'SGML_DOCUMENT_order',fact['document_id']
    locator=fact['locator']
    choices=source['inline'].get(locator[3:],set()) if locator.startswith('id:') else set()
    if len(choices)==1:
        rank,document_id,concept=next(iter(choices))
        if concept==fact['concept']:
            return rank,'exact_inline_fact_id_and_concept',document_id
    # -1 is reserved for the unbounded companyfacts API; -2 means unknown.
    return -2,'unresolved_physical_document_order',None
