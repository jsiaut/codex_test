from pathlib import Path
from decimal import Decimal
import json,re
import duckdb
from .spacex_annual import label_key
from .text import parse_html,normalize_space,render


def validate(root:Path):
    s=json.loads((root/'work/spcx_annual_candidates.json').read_text());d=duckdb.connect()
    d.execute('CREATE TABLE native (kind VARCHAR,rank INTEGER,label VARCHAR,year VARCHAR,value DECIMAL(38,6))')
    records=[(r['kind'],i,r['label_key'],y,v) for i,r in enumerate(s['native_rows']) for y,v in r['display_values'].items()]
    d.executemany('INSERT INTO native VALUES (?,?,?,?,?)',records)
    equations=[]
    def eq(control,kind,opening,closing,*,plus_opening=False):
        for year, in d.execute('SELECT DISTINCT year FROM native WHERE kind=? ORDER BY year',[kind]).fetchall():
            bounds=d.execute('SELECT min(rank) FILTER (WHERE label=?),min(rank) FILTER (WHERE label=?) FROM native WHERE kind=? AND year=?',[label_key(opening),label_key(closing),kind,year]).fetchone()
            if None in bounds:equations.append({'control':control,'year':year,'status':'not_testable','reason':'native_boundary_label_missing','labels':[opening,closing]});continue
            start,end=bounds
            lhs,rhs,terms=d.execute('SELECT sum(value) FILTER (WHERE rank>=? AND rank<?),max(value) FILTER (WHERE rank=?),count(*) FILTER (WHERE rank>=? AND rank<?) FROM native WHERE kind=? AND year=?',[start if plus_opening else start+1,end,end,start if plus_opening else start+1,end,kind,year]).fetchone()
            residual=lhs-rhs if lhs is not None and rhs is not None else None
            tolerance=Decimal('0.5')*(terms+1)
            equations.append({'control':control,'kind':kind,'year':year,'labels':[opening,closing],
                'lhs_million':str(lhs),'rhs_million':str(rhs),'residual_million':str(residual),'tolerance_million':str(tolerance),
                'status':'ok' if residual is not None and abs(residual)<=tolerance else 'mismatch'})
    # Ranges use printed statement headings/subtotals, and all native rows,
    # including those without an admissible concept correspondence.
    eq('C1','balance_sheet','Cash and cash equivalents','Total current assets',plus_opening=True)
    eq('C1','balance_sheet','Total current assets','Total assets',plus_opening=True)
    eq('C1','balance_sheet','Accounts payable','Total current liabilities',plus_opening=True)
    eq('C1','balance_sheet','Total current liabilities','Total liabilities',plus_opening=True)
    # CFF continues on the next physical page; the native sequence joins pages.
    eq('C2','cash_flow','Net income (loss)','Net cash provided by operating activities',plus_opening=True)
    eq('C2','cash_flow','Net cash provided by operating activities','Net cash used in investing activities')
    eq('C2','cash_flow','Net cash used in investing activities','Net cash provided by financing activities')
    d.execute("CREATE TABLE mapped AS SELECT * FROM read_json(?)",[str(root/'work/spcx_annual_candidates.json')]) if False else None
    for year in ['2023','2024','2025']:
        q=d.execute("SELECT i.value,c.value,i.value-c.value FROM native i JOIN native c USING(year,label) WHERE i.kind='income_statement' AND c.kind='cash_flow' AND i.year=? AND i.label=?",[year,label_key('Net income (loss)')]).fetchone()
        equations.append({'control':'C6_income_to_cash_flow','year':year,'status':'ok' if q and abs(q[2])<=1 else 'not_testable' if not q else 'mismatch',
            'lhs_million':str(q[0]) if q else None,'rhs_million':str(q[1]) if q else None,'residual_million':str(q[2]) if q else None,'tolerance_million':'1'})
    collection=json.loads((root/'work/collection.json').read_text())['filings'];f=collection[s['source_accession']]
    raw=(root/f['resources'][f['metadata']['primaryDocument']]['path']).read_bytes()
    lo=raw.find(b'Consolidated Statements of Redeemable',6824776);hi=7158566
    equity=[]
    for table in parse_html(raw[lo:hi]).iter('table'):
        trs=table.xpath('./tr|./tbody/tr|./thead/tr');index=None
        for tr in trs:
            cells=[normalize_space(render(c)) for c in tr.xpath('./td|./th')]
            header=next((i for i,v in enumerate(cells) if label_key(v)=='accumulated deficit'),None)
            if header is not None:index=header;continue
            if index is None or len(cells)<=index:continue
            label=next((x for x in cells if x),'');v=cells[index].replace('$','').replace(',','').strip()
            if v in ('-','–','—'):value='0'
            elif re.fullmatch(r'\(?-?\d+(?:\.\d+)?\)?',v):value=('-' if v.startswith('(') else '')+v.strip('()')
            else:continue
            equity.append((len(equity),label_key(label),value))
    d.execute('CREATE TABLE equity (rank INTEGER,label VARCHAR,value DECIMAL(38,6))')
    if equity:d.executemany('INSERT INTO equity VALUES (?,?,?)',equity)
    for year in ['2023','2024','2025']:
        opening='balances at december 31 '+str(int(year)-1);closing='balances at december 31 '+year
        bounds=d.execute('SELECT min(rank) FILTER (WHERE label=?),min(rank) FILTER (WHERE label=?) FROM equity',[opening,closing]).fetchone()
        if None in bounds:equations.append({'control':'C6_retained_earnings','year':year,'status':'not_testable','reason':'retained_earnings_column_unresolved'});continue
        lhs,rhs,count=d.execute('SELECT sum(value) FILTER(WHERE rank>=? AND rank<?),max(value) FILTER(WHERE rank=?),count(*) FILTER(WHERE rank>=? AND rank<?) FROM equity',[bounds[0],bounds[1],bounds[1],bounds[0],bounds[1]]).fetchone()
        residual=lhs-rhs;tolerance=Decimal('0.5')*(count+1)
        equations.append({'control':'C6_retained_earnings','year':year,'lhs_million':str(lhs),'rhs_million':str(rhs),'residual_million':str(residual),
            'tolerance_million':str(tolerance),'status':'ok' if abs(residual)<=tolerance else 'mismatch'})
    d.execute("CREATE TABLE facts AS SELECT * FROM read_parquet(?)",[str(root/'tables/facts.parquet')])
    comparisons=[]
    for r in s['rows']:
        if r['statement_kind']!='balance_sheet' or r['period_end']!='2025-12-31':continue
        matches=d.execute("SELECT value,decimals,fact_id FROM facts WHERE accession='0001628280-26-052535' AND canonical_concept=? AND dimensions='{}' AND period_start IS NULL AND period_end='2025-12-31' AND value IS NOT NULL ORDER BY primary_statement_occurrence DESC NULLS LAST,occurrence_rank DESC LIMIT 1",[r['concept']]).fetchone()
        if not matches:comparisons.append({'concept':r['concept'],'status':'not_testable','reason':'quarter_comparative_concept_missing'});continue
        tol=Decimal(500000)+Decimal('0.5')*(Decimal(10)**-int(matches[1]));residual=Decimal(r['value'])-matches[0]
        comparisons.append({'concept':r['concept'],'annual_value':r['value'],'quarter_value':str(matches[0]),'fact_id':matches[2],
            'residual':str(residual),'tolerance':str(tol),'status':'ok' if abs(residual)<=tol else 'mismatch'})
    s['internal_equations']=equations;s['comparative_reconciliation']=comparisons
    s['annual_series_admitted']=all(q['status']=='ok' for q in equations+comparisons) and len(comparisons)>=20
    s['status']='admitted_untagged_audited_html' if s['annual_series_admitted'] else 'excluded_internal_or_comparative_validation_incomplete'
    (root/'work/spcx_annual_validation.json').write_text(json.dumps(s,ensure_ascii=False,indent=2))
    print(json.dumps({'annual_series_admitted':s['annual_series_admitted'],'equation_statuses':[(q['control'],q['year'],q['status'],q.get('reason')) for q in equations],
       'comparative_statuses':{status:sum(q['status']==status for q in comparisons) for status in ['ok','mismatch','not_testable']}}))
    return s

if __name__=='__main__':validate(Path('.').resolve())
