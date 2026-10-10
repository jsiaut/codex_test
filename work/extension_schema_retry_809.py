from extension_authoring import ROOT,tagged
from secfragility.reader import store
k='aedb2f0920c89ab9fcd9c8efd30e96067f8c721ed1832ae922827d0f12be779a'
r=store(ROOT,k,[tagged(k,10,'Prepaid supply and capacity agreements (1) | | | $ | 3,008',block='exposed_assets',component_kind='other',model_quantity='prepaid_supply_capacity_noncurrent',issuer_treatment='3.008bn_LONGheld_EX799mshort_NOTnewCash'),tagged(k,22,'$799 million and $458 million of short-term prepaid supply and capacity agreements',block='exposed_assets',component_kind='other',model_quantity='prepaid_supply_capacity_current',issuer_treatment='799m_SHORTheld_EX3.008long_NOTfutureCommit')],schema_retry=True)
print({a:b for a,b in r.items() if a!='rejected'})
assert not r['rejected'],r['rejected']
