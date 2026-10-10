from extension_authoring import ROOT,tagged
from secfragility.reader import store
k='2da2682d73422befc02fe161b757605cf9a4a8dcbc8c6b2c8b1df1be53450fc5'
print(store(ROOT,k,[tagged(k,35,'range from $13.5 billion to $14.4 billion',amount_qualifier='range',category_id='lease_not_commenced',block='contractual_outflows',issuer_treatment='393MWsite_16yrs_rentCONSTRUCTIONcost_based_LOW13.5HIGH14.4_not_exact13.5_or_sum_overlap39.1unknown'),tagged(k,36,'range from $13.5 billion to $14.4 billion',amount_qualifier='range',model_quantity='construction_based_lease_range_upper',issuer_treatment='393MW_same16yr_range_UPPER14.4_notadditionalcommit')],schema_retry=True))
