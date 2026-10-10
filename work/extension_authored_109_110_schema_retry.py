import json
from extension_authoring import ROOT
from secfragility.reader import store
for k in ['914a3dca3fd1b25a9d229508202b5c923722cf04afd354c23551e1d9772e4b93','038a6653fd05a1c71f526b158b2757a854cb938011d88a3c408dde35606b4f28']:
    rows=[]
    for line in (ROOT/'work/observations'/(k+'.rejected.jsonl')).read_text().splitlines():
        r=json.loads(line)
        if r['phase']!='schema':continue
        row=r['raw_line']
        if 'counterparty_name' in row:
            row['counterparty']=row.pop('counterparty_name')
            row['counterparty_evidence']='named'
        if 'recast_kind' in row:
            row.pop('recast_kind');row['recast_cause']='presentation_reclassification'
        rows.append(row)
    result=store(ROOT,k,rows,schema_retry=True)
    print(dict(content_key=k,accepted=result['accepted'],rejected=result['rejected']))
    assert not result['rejected']
