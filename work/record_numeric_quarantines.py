from pathlib import Path
import json
r=Path('.');p=r/'work/observation_quarantines.json';data=json.loads(p.read_text())
for oid,decision,reason in [
 ('686f6175c4be935801d3193ec768598b2183b6a84843df19855407c7e45fbd88','D72','same_issue_literal_million_vs_billion_unresolved'),
 ('b91882ba658f18c39fa7caf22b24b0d76118470e2794b25472ad7285cd284005','D73','net_proceeds_993_5_vs_independent_offer_price_992_35_unresolved'),
 ('0617b927c580811d94a6508460452e71b70fa0a5b1b5130b9fbcf446f8af09e2','D97','private_primary_round_amount_and_date_source_discrepancy')]:
 if not any(x.get('observation_id')==oid for x in data):
  data.append(dict(observation_id=oid,decision=decision,reason=reason,scope='all_dependent_numeric_attributions',
   detail='Immutable original observation and independent source discrepancy retained; no averaged amount or silent correction.'))
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
