from extension_authoring import ROOT
from secfragility.reader import store
k='62e5cfc29b545cf1ff49ab355db94a220a163feab1bd6932859ce5f2de68a73a'
r=store(ROOT,k,[dict(quote='On June 15, 2023, we repaid the 0.309% Notes Due 2023.',event_type='repayment',event_date='2023-06-15',model_quantity='debt_repayment_event',issuer_treatment='ACTUALJun15_23_DATEresolvesPriorAnnual_NOtransactionAmtUsePriorStock_NOTAIprimary')],schema_retry=True)
print({a:b for a,b in r.items() if a!='rejected'})
assert not r['rejected'],r['rejected']
