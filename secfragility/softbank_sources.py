"""Explicit Japan source protocol; never promotes arbitrary non-EDGAR material."""
from pathlib import Path
from datetime import date
from decimal import Decimal
import calendar,hashlib,json,re,unicodedata

GROUP='external:0001065521'
VARIANT='extended_official_JP_sources'
def norm(t):return ' '.join(re.sub('[\uFFFD\x08]+',' ',t).split())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pages(root,s):return (root/s['text_path']).read_text().split('\f')[:-1]
def document_id(s):return hashlib.sha256(('JP|'+s['url']).encode()).hexdigest()

def qualify(root):
    sources=json.loads((root/'work/softbank/sources.json').read_text())
    byurl={s['url']:s for s in sources}; result=[]
    for s in sources:
        assert sha(root/s['path'])==s['sha256']
        if '/financial_reports/financial-report_' in s['url'] and s['url'].endswith('_en.pdf'):
            pp=pages(root,s);m=re.search(r'Tokyo,\s+([A-Za-z]+)\s+(\d{1,2}),\s+(20\d\d)',pp[0])
            if not m:raise ValueError('No dated cover: '+s['url'])
            month=list(calendar.month_name).index(m[1]);published=date(int(m[3]),month,int(m[2]))
            original=byurl.get(s['url'].replace('_en.pdf','_ja.pdf'))
            if not original:raise ValueError('Japanese original missing')
            jp=unicodedata.normalize('NFKC',norm(pages(root,original)[0]))
            pattern=rf'{published.year}年\s*0?{published.month}月\s*0?{published.day}日'
            if not re.search(pattern,jp):raise ValueError('Cover dates differ: '+s['url'])
            match=re.search(r'q([1-4])fy(20\d\d)',s['url']);q,fy=map(int,match.groups())
            end=date(fy if q<4 else fy+1,[0,6,9,12,3][q],[0,30,30,31,31][q])
            start=date(fy,4,1)
            review=[i+1 for i,p in enumerate(pp) if 'We have reviewed' in p]
            # Original historical earnings releases expressly say unaudited;
            # a separately filed statutory report is not silently imported.
            result.append(dict(s,document_id=document_id(s),publication_date=str(published),
                publication_proof='English dated cover and matching Japanese dated cover',
                original_document_id=document_id(original),original_url=original['url'],
                original_sha256=original['sha256'],original_path=original['path'],
                period_start=str(start),period_end=str(end),fiscal_year=fy,quarter=q,
                jurisdiction='JP_TSE',regulatory_identifier=None,
                source_profile='TSE_issuer_translation_original_matched',
                filing_status='published_regulated',tier='B' if review else 'C',
                assurance='reviewed' if review else 'unaudited',review_pages=review,
                assurance_rule='Review confined to identified financial statements and notes; front management narrative is unaudited',
                eligible_extended=True,eligible_legacy=False))
        elif s.get('role')=='latest_full_financial_statements':
            # Back cover PDF149 states the publication date. Auditor report
            # PDF146-148 inspected visually, source page images retained.
            result.append(dict(s,document_id=document_id(s),publication_date='2026-07-27',
                publication_proof='Own back cover PDF149: Published on July 27, 2026; rendered page retained',
                original_document_id=None,original_url=None,original_sha256=None,original_path=None,
                period_start='2025-04-01',period_end='2026-03-31',fiscal_year=2025,quarter=4,
                jurisdiction='JP_issuer_audited_financial_statements',regulatory_identifier=None,
                source_profile='issuer_audited_IFRS_financial_statements',filing_status='published_regulated',
                tier='B',assurance='audited',review_pages=[146,147,148],
                assurance_rule='Consolidated financial statements and notes, excluding expressly unaudited pro forma; convenience USD translations excluded from JPY metrics',
                eligible_extended=True,eligible_legacy=False))
        elif s.get('role')=='EDINET_direct_annual_original':
            pp=pages(root,s);cover=unicodedata.normalize('NFKC',norm(pp[0]))
            assert 'E02778' in cover and 'SoftBank Group Corp.' in cover
            dates=re.findall(r'(20\d\d)年\s*(\d+)月\s*(\d+)日',cover)
            published=date(*map(int,dates[0]));start=date(*map(int,dates[1]));end=date(*map(int,dates[2]))
            if end.year<2021:continue
            docid=s['url'].rsplit('/',1)[-1].replace('.pdf','')
            result.append(dict(s,document_id=document_id(s),publication_date=str(published),
                publication_proof='Original EDINET dated cover PDF1, identity E02778 and fiscal dates',
                original_document_id=None,original_url=s['url'],original_sha256=s['sha256'],original_path=None,
                period_start=str(start),period_end=str(end),fiscal_year=start.year,quarter=4,
                jurisdiction='JP_EDINET',regulatory_identifier=docid,
                source_profile='EDINET_original_annual_consolidated_IFRS',filing_status='filed',
                tier='A',assurance='audited',review_pages=[i+1 for i,p in enumerate(pp) if '独立監査人の監査報告書' in p],
                assurance_rule='Only consolidated IFRS statements and notes; standalone Japanese GAAP and management sections not assigned this assurance',
                eligible_extended=True,eligible_legacy=False))
    for record in result:record['publication_date_verified']=True
    (root/'work/softbank/source_qualifications.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

LABELS={
 'Cash and cash equivalents':'cash', 'Total assets':'assets',
 'Total current assets':'current_assets','Total current liabilities':'current_liabilities',
 'Total liabilities':'liabilities','Total equity':'equity',
 'Total equity attributable to owners of the parent':'parent_equity',
 'Non-controlling interests':'non_controlling_interests',
 'Interest-bearing debt':'debt','Lease liabilities':'leases',
 'Third-party interests in SVF':'third_party_fund_interests',
 'Investments of SVF (FVTPL)':'svf_fvtpl','Investments from SVF (FVTPL)':'svf_fvtpl',
 'Investments accounted for using the equity method':'equity_method_assets',
 'Investment securities':'investment_securities',
 'Trade and other receivables':'receivables','Inventories':'inventories',
 'Trade and other payables':'payables','Net sales':'revenue',
 'Gross profit':'gross_profit','Income before income tax':'pretax_income',
 'Net income':'net_income','Depreciation and amortization':'da',
 'Finance cost':'finance_cost',
 'Total gain on investments':'investment_gains',
 'Net cash provided by (used in) operating activities':'cfo',
 'Net cash (used in) provided by operating activities':'cfo',
 'Net cash provided by operating activities':'cfo',
 'Net cash used in operating activities':'cfo',
 'Net cash provided by (used in) investing activities':'cfi',
 'Net cash (used in) provided by investing activities':'cfi',
 'Net cash used in investing activities':'cfi','Net cash provided by investing activities':'cfi',
 'Net cash provided by (used in) financing activities':'cff',
 'Net cash (used in) provided by financing activities':'cff',
 'Net cash provided by financing activities':'cff','Net cash used in financing activities':'cff',
 'Purchase of property, plant and equipment, and intangible assets':'capex_signed',
 'Repayment of lease liabilities':'lease_payments_signed',
 'Proceeds from interest-bearing debt':'debt_proceeds',
 'Repayment of interest-bearing debt':'debt_repayments_signed',
 'Payments for acquisition of investments by SVF':'svf_purchases_signed',
 'Proceeds from sales of investments by SVF':'svf_sales',
 'Payments for acquisition of investments':'investment_purchases_signed',
 'Proceeds from sales/redemption of investments':'investment_sales',
 'Payments (net) for acquisition of control over subsidiaries':'business_acquisitions_signed',
 'Cash and cash equivalents at the beginning of the period':'cash_opening',
 'Cash and cash equivalents at the beginning of the year':'cash_opening',
 'Cash and cash equivalents at the end of the period':'cash_closing',
 'Cash and cash equivalents at the end of the year':'cash_closing',
 'Effect of exchange rate changes on cash and cash equivalents':'cash_fx',
 'Increase (decrease) in cash and cash equivalents':'cash_change',
 '(Decrease) increase in cash and cash equivalents':'cash_change',
 'Increase in cash and cash equivalents':'cash_change',
 'Decrease in cash and cash equivalents':'cash_change',
 'Increase in cash and cash equivalents relating to transfer of assets classified as held for sale':'cash_held_for_sale_transfer',
 'Decrease in cash and cash equivalents relating to transfer of assets classified as held for sale':'cash_held_for_sale_transfer',
 '(Decrease) increase in cash and cash equivalents relating to transfer of assets classified as held for sale':'cash_held_for_sale_transfer',
}
NUMBER=r'(?:[¥$]\s*)?(?:\(?-?\d[\d,]*\)?|[–−-])'
TAIL=re.compile(r'('+NUMBER+r'(?:\s+'+NUMBER+r')+)\s*$')
def row_values(line,n=2):
    m=TAIL.search(line)
    if not m:return None
    tokens=re.findall(NUMBER,m[1]);tokens=tokens[-n:]
    if len(tokens)!=n:return None
    def parse(t):
        t=re.sub(r'[¥$\s]','',t)
        if t in ('–','−','-'):return None # dash is not asserted to be zero
        negative=t.startswith('(');return Decimal(t.strip('()').replace(',',''))*(-1 if negative else 1)*1000000
    return [parse(t) for t in tokens]

def extract(root,s):
    pp=pages(root,s); n=3 if s['source_profile']=='issuer_audited_IFRS_financial_statements' else 2
    original_text=''
    if s.get('original_path'):
        original=next(x for x in json.loads((root/'work/softbank/sources.json').read_text()) if x['path']==s['original_path'])
        original_text=unicodedata.normalize('NFKC',''.join(pages(root,original)))
    state=None;section='';out=[];started=False; prior=''
    for page,p in enumerate(pp,1):
        if page<2:continue
        clean=re.sub('[\uFFFD\x08]+',' ',p)
        if not started:
            if 'Current assets' in clean and ('Statement of Financial Position' in clean or 'ASSETS' in clean) and 'Cash and cash equivalents' in clean:
                started=True;state='balance'
            else:continue
        if re.search(r'(Notes to (?:Condensed Interim )?Consolidated|Basis of Presentation|Significant Doubt about Going Concern)',clean):break
        if re.search(r'(?:Consolidated )Statement of Cash Flows',clean):state='cashflow'
        elif 'Statement of Changes in Equity' in clean:state='changes'
        elif 'Statement of Profit or Loss' in clean or 'Statement of Income' in clean:state='income'
        elif 'Statement of Comprehensive Income' in clean:state='comprehensive'
        rawlines=clean.splitlines();logical=[];i=0
        while i<len(rawlines):
            line=rawlines[i];snippet=line
            if i+1<len(rawlines) and re.fullmatch(r'\s*'+NUMBER+r'(?:\s+'+NUMBER+r')+\s*',rawlines[i+1]):
                label=line.strip();numeric=rawlines[i+1];snippet+='\n'+numeric
                if i+2<len(rawlines) and re.match(r'\s*[a-z]',rawlines[i+2]) and not row_values(rawlines[i+2],n):
                    label+=' '+rawlines[i+2].strip();snippet+='\n'+rawlines[i+2];consumed=3
                else:consumed=2
                logical.append((i+1,label+' '+numeric,snippet));i+=consumed
            else:logical.append((i+1,line,snippet));i+=1
        for lineno,line,snippet in logical:
            text=' '.join(line.split())
            if text in ('Current assets','Current liabilities','Non-current assets','Non-current liabilities'):section=text.lower().replace(' ','_')
            combined=prior+' '+text
            for label,concept in sorted(LABELS.items(),key=lambda item:-len(item[0])):
                matchtext=text if text.startswith(label+' ') else combined if combined.startswith(label+' ') else None
                if not matchtext:continue
                tail=TAIL.search(matchtext)
                if not tail or re.sub(r'[0-9,\s*]','',matchtext[len(label):tail.start()]):continue
                values=row_values(matchtext,n)
                if values is None:continue
                if state in ('changes','comprehensive'):continue
                if concept=='cash' and state!='balance':continue
                if concept in ('non_controlling_interests','parent_equity','equity') and state!='balance':continue
                if state=='balance' and concept in ('revenue','net_income','pretax_income','finance_cost'):continue
                if concept=='net_income' and ('attributable' in matchtext.lower()):continue
                if state=='cashflow' and concept in ('net_income','finance_cost'):concept+='__cf'
                if state=='balance' and concept in ('debt','leases'):concept+='__'+section
                end=date.fromisoformat(s['period_end']); start=date.fromisoformat(s['period_start'])
                for column,value in enumerate(values[:2]):
                    if value is None:continue
                    if state=='balance':pe=date(s['fiscal_year'],3,31) if column==0 else end;ps=None
                    else:pe=end.replace(year=end.year-1) if column==0 else end;ps=start.replace(year=start.year-1) if column==0 else start
                    quote=snippet.strip()
                    original=s.get('original_path')
                    original_match=None
                    if original:
                        amount=format(abs(value)/1000000,',.0f')
                        original_match=amount in original_text
                        if not original_match:raise ValueError('Translation value absent in original '+amount+' '+s['url'])
                    out.append(dict(document_id=s['document_id'],source_url=s['url'],concept=concept,
                        period_start=str(ps) if ps else None,period_end=str(pe),value=str(value),currency='JPY',unit='JPY',
                        page=page,line=lineno,column=column,quote=quote,statement=state,
                        knowledge_date=s['publication_date'],assurance=s['assurance'],tier=s['tier'],
                        original_value_match=original_match,precision_decimals='-6'))
                break
            prior=text if not row_values(text,n) else ''
    keys=set();unique=[]
    for r in out:
        key=(r['concept'],r['period_start'],r['period_end'])
        if key in keys:continue
        keys.add(key);unique.append(r)
    return unique

def prepare(root):
    qualified=qualify(root);facts=[f for s in qualified for f in
        (extract_japanese(root,s) if s['jurisdiction']=='JP_EDINET' else extract(root,s))]
    (root/'work/softbank/statement_facts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n')
    return dict(qualified_sources=len(qualified),facts=len(facts))

JP_LABELS={
 '現金及び現金同等物':'cash','流動資産合計':'current_assets','資産合計':'assets',
 '流動負債合計':'current_liabilities','負債合計':'liabilities','資本合計':'equity',
 '親会社の所有者に帰属する持分合計':'parent_equity','非支配持分':'non_controlling_interests',
 '有利子負債':'debt','リース負債':'leases','SVFにおける外部投資家持分':'third_party_fund_interests',
 'SVFの投資(FVTPL)':'svf_fvtpl','SVFからの投資(FVTPL)':'svf_fvtpl','SVFの外部投資家持分':'third_party_fund_interests',
 '持分法で会計処理されている投資':'equity_method_assets','投資有価証券':'investment_securities',
 '営業債権及びその他の債権':'receivables','棚卸資産':'inventories',
 '営業債務及びその他の債務':'payables','売上高':'revenue','売上総利益':'gross_profit',
 '税引前利益':'pretax_income','純利益':'net_income','減価償却費及び償却費':'da','財務費用':'finance_cost',
 '投資損益合計':'investment_gains',
 '営業活動によるキャッシュ・フロー':'cfo','投資活動によるキャッシュ・フロー':'cfi',
 '財務活動によるキャッシュ・フロー':'cff',
 '有形固定資産及び無形資産の取得による支出':'capex_signed',
 'リース負債の返済による支出':'lease_payments_signed',
 '有利子負債の収入':'debt_proceeds','有利子負債の支出':'debt_repayments_signed',
 '有利子負債の返済による支出':'debt_repayments_signed',
 'SVFの投資の取得による支出':'svf_purchases_signed','SVFによる投資の取得による支出':'svf_purchases_signed',
 'SVFの投資の売却による収入':'svf_sales','SVFによる投資の売却による収入':'svf_sales',
 '投資の取得による支出':'investment_purchases_signed','投資の売却または償還による収入':'investment_sales',
 '現金及び現金同等物の期首残高':'cash_opening','現金及び現金同等物の期末残高':'cash_closing',
 '現金及び現金同等物に係る換算差額':'cash_fx','現金及び現金同等物の増減額(-は減少額)':'cash_change',
 '売却目的保有に分類された資産からの振替に伴う現金及び現金同等物の増加額':'cash_held_for_sale_transfer',
 '売却目的保有に分類された資産への振替に伴う現金及び現金同等物の減少額':'cash_held_for_sale_transfer',
 '売却目的保有に分類された資産への振替に伴う現金及び現金同等物の増減額(-は減少)':'cash_held_for_sale_transfer',
}
def extract_japanese(root,s):
    state=None;section='';out=[];seen=set();start=date.fromisoformat(s['period_start']);end=date.fromisoformat(s['period_end'])
    for page,p in enumerate(pages(root,s),1):
        clean=unicodedata.normalize('NFKC',p).replace('△','-')
        if re.search(r'【連結財政状態計算書】',clean):state='balance'
        if not state:continue
        if '【連結財務諸表注記】' in clean or '1.報告企業' in re.sub(r'\s','',clean):break
        if '【連結キャッシュ・フロー計算書】' in clean:state='cashflow'
        elif '【連結持分変動計算書】' in clean:state='changes'
        elif '【連結損益計算書】' in clean:state='income'
        elif '【連結包括利益計算書】' in clean:state='comprehensive'
        if state not in ('balance','income','cashflow'):continue
        original_lines=clean.splitlines();joined=[];idx=0
        while idx<len(original_lines):
            line=original_lines[idx]
            if '売却目的保有' in line and row_values(line,2) and idx+1<len(original_lines):
                m=TAIL.search(line);joined.append((idx+1,line[:m.start()].strip()+original_lines[idx+1].strip()+' '+m[1]));idx+=2
            elif '売却目的保有' in line and idx+2<len(original_lines) and row_values(original_lines[idx+1],2):
                joined.append((idx+1,line.strip()+original_lines[idx+2].strip()+' '+original_lines[idx+1].strip()));idx+=3
            else:joined.append((idx+1,line));idx+=1
        for lineno,line in joined:
            text=' '.join(line.split());compact=re.sub(r'\s','',text)
            if compact in ['流動資産','非流動資産','流動負債','非流動負債']:
                section={'流動資産':'current_assets','非流動資産':'non-current_assets','流動負債':'current_liabilities','非流動負債':'non-current_liabilities'}[compact]
            for label,concept in sorted(JP_LABELS.items(),key=lambda x:-len(x[0])):
                if not compact.startswith(label):continue
                values=row_values(text,2)
                if not values:continue
                prefix=compact[len(label):];tail=TAIL.search(text)
                if not tail or re.sub(r'[0-9,\s*]','',text.replace(' ','')[len(label):len(text[:tail.start()].replace(' ',''))]):continue
                if concept in ('non_controlling_interests','equity','parent_equity') and state!='balance':continue
                if state=='cashflow' and concept in ('net_income','finance_cost'):concept+='__cf'
                if state=='balance' and concept in ('debt','leases'):concept+='__'+section
                for column,value in enumerate(values):
                    if value is None:continue
                    pe=end.replace(year=end.year-1) if column==0 else end
                    ps=None if state=='balance' else start.replace(year=start.year-1) if column==0 else start
                    key=(concept,str(ps),str(pe))
                    if key in seen:continue
                    seen.add(key)
                    out.append(dict(document_id=s['document_id'],source_url=s['url'],concept=concept,
                        period_start=str(ps) if ps else None,period_end=str(pe),value=str(value),currency='JPY',unit='JPY',
                        page=page,line=lineno,column=column,quote=line.strip(),statement=state,
                        knowledge_date=s['publication_date'],assurance='audited',tier='A',
                        original_value_match=True,precision_decimals='-6'))
                break
    return out

if __name__=='__main__':print(prepare(Path('.').resolve()))
