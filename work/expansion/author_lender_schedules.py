"""Position judgments after reading the entire current schedule and every legend."""
from pathlib import Path
import json
from secfragility.expansion_reading import submit
ROOT=Path(__file__).resolve().parents[2]
GECC=[
 ('Coreweave Compute Acquisition Co. II, LLC','Coreweave Compute Acquisition Co. II, LLC | | Technology | | 1st Lien, Secured Loan | | 2, 6, 14 | | 3M SOFR + 9.62% (13.29%) | | 08/21/2023 | | 07/31/2028 | | | 9,888 | | | | 9,866 | | | | 10,234 | | |'),
 ('Coreweave Compute Acquisition Co. IV, LLC','Coreweave Compute Acquisition Co. IV, LLC | | Technology | | 1st Lien, Secured Loan | | 2, 6, 14 | | 3M SOFR + 6.00% (9.68%) | | 05/29/2024 | | 05/16/2030 | | | 2,093 | | | | 2,070 | | | | 2,145 | | |'),
 ('CoreWeave Financing DDTL V, LLC','CoreWeave Financing DDTL V, LLC | | Technology | | 1st Lien, Delayed Draw Term Loan | | 2, 10, 14 | | 1M SOFR + 4.50% (8.12%) | | 05/06/2026 | | 11/14/2031 | | | 2,664 | | | | 2,590 | | | | 2,812 | | |'),
 ('Coreweave, Inc.','Coreweave, Inc. | | Technology | | Unsecured Bond | | 10 | | 9.63% | | 06/11/2026 | | 07/15/2032 | | | 2,000 | | | | 2,000 | | | | 1,973 | | |'),
]
AUTHORED={
 '92ae097cc3f5':[
  dict(quote='Investment was on non-accrual status as of period end.',model_quantity='lender_non_accrual_schedule_legend',stage='recognized',measurement_basis='footnote_9_is_non_accrual_marker'),
  dict(quote='Security pays, or has the option to pay, some or all of its interest in kind.',model_quantity='lender_PIK_schedule_legend',stage='recognized',measurement_basis='footnote_7_is_PIK_terms_marker'),
  *[dict(quote=q,model_quantity=metric,stage='recognized',period_end='2026-06-30',instrument_key=name,
      counterparty=name,counterparty_evidence='named',event_present=False,
      measurement_basis=basis) for name,q in GECC for metric,basis in [
        ('lender_position_non_accrual_status','current_schedule_row_has_no_footnote_9;no_reported_non_accrual'),
        ('lender_position_PIK_terms','current_schedule_row_has_no_footnote_7_or_PIK_coupon;not_position_PIK_income_ratio')]],
 ],
 'a5d6f1ead7b1':[
  dict(quote='Investment was on non-accrual status as of June 30, 2026, meaning that the Company has ceased recognizing interest income on these investments.',model_quantity='lender_non_accrual_schedule_legend',stage='recognized',measurement_basis='footnote_12_is_non_accrual_marker'),
  dict(quote='Security may be an obligation of one or more entities affiliated with the named portfolio company.',model_quantity='lender_named_brand_not_legal_borrower',stage='recognized'),
  dict(quote='CoreWeave - Delayed Draw Term Loan | (6) | | S + 6.00% | | 0.00% | | 9.61% | | 8/26/2030 | | | 26,950 | | | | 26,669 | | | | 26,950 | | | | 0.77 |',model_quantity='lender_position_non_accrual_status',stage='recognized',period_end='2026-06-30',instrument_key='CoreWeave - Delayed Draw Term Loan',counterparty='CoreWeave',counterparty_evidence='named',event_present=False,measurement_basis='current_schedule_row_has_no_footnote_12;no_reported_non_accrual;affiliated_legal_obligor_not_resolved'),
  dict(quote='CoreWeave - Delayed Draw Term Loan | (6) | | S + 6.00% | | 0.00% | | 9.61% | | 8/26/2030 | | | 26,950 | | | | 26,669 | | | | 26,950 | | | | 0.77 |',model_quantity='lender_position_PIK_terms',stage='recognized',period_end='2026-06-30',instrument_key='CoreWeave - Delayed Draw Term Loan',counterparty='CoreWeave',counterparty_evidence='named',event_present=False,measurement_basis='no_PIK_coupon_stated_on_this_row;not_position_PIK_income_ratio'),
 ],
}
if __name__=='__main__':
 for key,rows in AUTHORED.items():print(json.dumps(dict(prefix=key,result=submit(ROOT,key,rows)),default=str),flush=True)
