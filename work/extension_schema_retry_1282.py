from extension_authoring import ROOT,tagged
from secfragility.reader import store
k='59645b6c34ebb280ababceddb3ab1cef4abdaf9c95dfb624e0cf0416234a029e'
r=store(ROOT,k,[tagged(k,26,'14,809',family='commercial',link_type='revenue_recognized',stage='recognized',model_quantity='segment_revenue',issuer_treatment='14.809bnQ2CY21_NotAllAI_AWS'),tagged(k,34,'4,193',model_quantity='segment_operating_profit',issuer_treatment='AWS_Q2CY21')],schema_retry=True)
print({a:b for a,b in r.items() if a!='rejected'})
assert not r['rejected'],r['rejected']
