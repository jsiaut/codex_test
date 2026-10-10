from extension_authoring import ROOT,tagged
from secfragility.reader import store,block_for
k='988644fbf2827c1a295861bae50c115269815085d06cacbfa0e11e3978aa86dc'
rows=[tagged(k,19,'1,220',block='contractual_outflows',category_id='purchase_obligation',component_kind='purchase',model_quantity='firm_purchase_commitments',issuer_treatment='1.220bnFIRMprimInventory_INCancelableCampusCONSTRcostToCancel_TABLEMATERIALLYCHANGEDcategoriesOnly_NotAll'),tagged(k,22,'standby letters of credit of $59 million',block='contingent_obligations',category_id='standby_lc',component_kind='guarantee_cap',model_quantity='standby_letters_of_credit',conditionality='conditional',trigger_description='If the guarantees are called, we must reimburse the provider of the guarantees.',trigger_occurred='unknown',issuer_treatment='59mOUTSTANDINGMay2_21_Not500mFacilityLCcap_ProviderReimbursementConditional')]
assert all(r['quote'] in block_for(ROOT,k)['text'] for r in rows)
result=store(ROOT,k,rows,schema_retry=True)
print({a:b for a,b in result.items() if a!='rejected'}|{'rejected':result['rejected']})
assert not result['rejected']
