from extension_authoring import ROOT
from secfragility.reader import store
k='0d3b6bb441fb7d221dc0cdb5ebef1f2d60928202f6ff468e3741e356713cffaf'
rows=[dict(quote='Broadcom Inc. (“Broadcom”), a Delaware corporation',abstained=True,abstention_reason='ExplicitFullLegalNameAndJurisdiction_NotBRCMOrBTI;IndependentAccessionFromAnnual1507_1574')]
r=store(ROOT,k,rows,schema_retry=True)
print({a:b for a,b in r.items() if a!='rejected'}|{'rejected':r['rejected']})
assert not r['rejected']
