from pathlib import Path
import json,hashlib
from secfragility.text import normalize_html

r=Path('.');collection=json.loads((r/'work/collection.json').read_text())
proofs=[]
for acc,end,day,names in [
 ('0001193125-18-107559',17081,'2018-04-04',['Broadcom Inc.','Broadcom Limited']),
 ('0001193125-16-446865',11426,'2016-02-01',['Broadcom Limited','Avago Technologies Limited','Broadcom Corporation'])]:
 f=collection['filings'][acc];res=f['resources'][f['metadata']['primaryDocument']];raw=(r/res['path']).read_bytes()
 proofs.append(dict(accession=acc,document_path=res['path'],url=res['url'],sha256=hashlib.sha256(raw).hexdigest(),
  locator=f'rawbytes:0:{end}',knowledge_date=f['metadata']['filingDate'],legal_date=day,
  names=names,quote=normalize_html(raw[:end]),personally_read=True))
(r/'work/parent_membership_evidence.json').write_text(json.dumps(proofs,ensure_ascii=False,indent=2)+'\n')
with (r/'decisions.md').open('a') as f:f.write('\nD96 — Appartenances Broadcom : introductions des deux 8-K12B lus personnellement dans le cache, plages et SHA conservés. La succession SG→DE est achevée après la clôture du marché le4avril2018, et non lors de l’approbation judiciaire le2avril. SG devient filiale distincte, pas alias deDE. Avago et BroadcomCorporationCA deviennent filiales indirectes de BroadcomLimitedSG le1février2016 ; la date du rapport29janvier ne date pas cette opération. Aucun montant de financement importé de ces introductions de métadonnées. L’identité et la juridiction contradictoires des autres mentions CorporationDE restent distinctes.\n')
