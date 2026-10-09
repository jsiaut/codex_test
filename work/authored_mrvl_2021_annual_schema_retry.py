from work.authored_mrvl_2021_annual import rows,k
from work.authored_helpers import ROOT
from secfragility.reader import store
quantities={'Inphi_acquisition_closing_conditions_pending','acquisition_financing_commitments_total','acquisition_bridge_loan_commitment','acquisition_3year_term_loan_commitment','acquisition_5year_term_loan_commitment'}
retry=[]
for original in rows:
 if original.get('model_quantity') not in quantities:continue
 row=dict(original)
 if 'provider' in row:row['payer']=row.pop('provider')
 if row['model_quantity']=='Inphi_acquisition_closing_conditions_pending':row['trigger_description']="pending approval by Inphi's and the Company's stockholders, as well as regulatory approval and satisfaction of other customary closing conditions."
 retry.append(row)
print(store(ROOT,k,retry,schema_retry=True))
