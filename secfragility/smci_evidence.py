"""Validate an explicit analyst-selected inline occurrence against its instance."""
from decimal import Decimal
from lxml import html

def inline_bridge(raw,fact):
    locator=fact['locator']
    if not locator.startswith('id:'):raise ValueError('An exact inline ID is required')
    nodes=html.fromstring(raw).xpath('//*[@id=$identity]',identity=locator[3:])
    if len(nodes)!=1:raise ValueError('Inline ID absent or ambiguous')
    node=nodes[0]
    if node.get('name')!=fact['canonical_concept']:raise ValueError('Inline concept differs')
    token=node.text_content().strip().replace(',','')
    value=Decimal(token)*Decimal(10)**int(node.get('scale','0'))
    if node.get('sign')=='-':value=-value
    if value!=Decimal(str(fact['value'])):raise ValueError('Inline amount differs')
    return dict(inline_id=locator[3:],concept=node.get('name'),token=token,scale=node.get('scale','0'),value=str(value),context_ref=node.get('contextref'))
