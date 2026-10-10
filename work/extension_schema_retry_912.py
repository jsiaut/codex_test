from extension_authoring import ROOT,tagged
from secfragility.reader import store
k='1cdffe0574b94edfa16912972bcd5b814965e01ac944eb9b5ae66b0d0205cf3e'
r=store(ROOT,k,[tagged(k,22,'the Company agreed to pay the customer $100.0 million in cash over several quarters.',event_type='signing',event_present=True,model_quantity='customer_contract_dispute_settlement',counterparty_evidence='anonymous',issuer_treatment='100m_Q3FY23signedSettlement_NOTproofpaid_ORnewFinancing_ORcustomerIncentive_NOliteralDay')],schema_retry=True)
print({a:b for a,b in r.items() if a!='rejected'})
assert not r['rejected'],r['rejected']
