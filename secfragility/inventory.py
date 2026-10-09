from __future__ import annotations
from collections import Counter
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml
from .network import SecClient, SessionLock, AccessPaused, AccessStopped, ResourceUnavailable, utc_now


def rows(columns: dict) -> list[dict]:
    lengths = {len(v) for v in columns.values() if isinstance(v, list)}
    if len(lengths) > 1:
        raise ValueError('Pagination SEC : colonnes de longueurs incompatibles.')
    return [{k: v[i] for k, v in columns.items() if isinstance(v, list)}
        for i in range(next(iter(lengths), 0))]


def collect_submissions(client: SecClient, cik: str) -> dict:
    base = 'https://data.sec.gov/submissions/'
    submission = client.json(base + 'CIK' + cik.zfill(10) + '.json')
    all_rows = rows(submission['filings']['recent'])
    expected = submission['filings'].get('files', [])
    read, failed = [], []
    for page in expected:  # No date predicate: every page is requested.
        try:
            data = client.json(base + page['name'])
            all_rows.extend(rows(data.get('filings', {}).get('recent', data)))
            read.append(page['name'])
        except ResourceUnavailable as exc:
            failed.append({'page': page['name'], 'reason': str(exc)})
    unique = {}
    for row in all_rows:
        accession = row['accessionNumber']
        if accession in unique and unique[accession] != row:
            raise ValueError(f'Pagination SEC : deux métadonnées contradictoires pour {accession}')
        unique[accession] = row
    return {'metadata': {k: v for k,v in submission.items() if k != 'filings'},
        'filings': sorted(unique.values(), key=lambda x: (x.get('filingDate',''), x['accessionNumber'])),
        'pagination': {'expected': [p['name'] for p in expected], 'read': read, 'failed': failed,
            'history_left_censored': bool(failed)}}


def run(root: Path):
    config = yaml.safe_load((root / 'config.yaml').read_text())
    run_path = root / 'work/run.json'
    if run_path.exists():
        manifest = json.loads(run_path.read_text())
    else:
        manifest = {'as_of': utc_now(), 'phase': 'phase0', 'status': 'in_progress'}
        run_path.write_text(json.dumps(manifest, indent=2))
    as_of = manifest['as_of']
    end = as_of[:10]
    with SessionLock(root, config['session_stale_minutes']) as lock:
        client = SecClient(root, config, as_of, lock)
        output_path = root / 'work/inventory.json'
        output = json.loads(output_path.read_text()) if output_path.exists() else {'as_of': as_of, 'groups': {}, 'exclusions': []}
        try:
            # The ticker URL is the link in the cached official documentation.
            ticker_data = client.json('https://www.sec.gov/files/company_tickers.json')
            tickers = {v['ticker']: str(v['cik_str']).zfill(10) for v in ticker_data.values()}
            for ticker, hint in config['groups'].items():
                if ticker not in tickers:
                    output['groups'][ticker] = {'status': 'unresolved_ticker', 'hint': hint}
                    exclusion = {'group': ticker, 'reason': 'ticker_unresolved'}
                    if exclusion not in output['exclusions']:
                        output['exclusions'].append(exclusion)
                    output_path.write_text(json.dumps(output, indent=2))
                    print(json.dumps({'group': ticker, 'status': 'unresolved_ticker'}), flush=True)
                    continue
                current_cik = tickers[ticker]
                group = output['groups'].setdefault(ticker, {'cik': current_cik, 'issuers': {}})
                group['status'] = 'resolved'
                group['cik'] = current_cik
                cik_names = {current_cik: 'current'}
                cik_names.update({cik: name for name,cik in config.get('predecessors',{}).get(ticker,{}).items()})
                for cik,name in cik_names.items():
                    if cik not in group['issuers']:
                        issuer = collect_submissions(client, cik)
                        issuer['role_hint'] = name
                        group['issuers'][cik] = issuer
                        output_path.write_text(json.dumps(output, indent=2))
                        print(json.dumps({'group': ticker, 'cik': cik, 'filings': len(issuer['filings']),
                            'pages': len(issuer['pagination']['read']),
                            'history_left_censored': issuer['pagination']['history_left_censored']}), flush=True)
                filings = [dict(row, cik=cik) for cik,issuer in group['issuers'].items() for row in issuer['filings']]
                annual = sorted([r for r in filings if r['form'] in ('10-K','10-KT','20-F','40-F') and r.get('reportDate')],
                    key=lambda r:r['reportDate'])
                year = config['window']['start_fiscal_year']
                first = next((r for r in annual if r['reportDate'][:4] == str(year)), None)
                if first:
                    prior = [r for r in annual if r['reportDate'] < first['reportDate']]
                    if prior:
                        start = (date.fromisoformat(prior[-1]['reportDate']) + timedelta(days=1)).isoformat()
                        group['analysis_start_basis'] = 'previous_fiscal_year_end_plus_one_day'
                    else:
                        start = f'{year-1}-01-01'
                        group['analysis_start_basis'] = 'conservative_pending_instance_start'
                else:
                    start = f'{year-1}-01-01'
                    group['analysis_start_basis'] = 'conservative_pending_ipo_annual_periods'
                group['analysis_start'] = start
                # The definitive 52/53-week boundary is refined from the instance.
                sd = date.fromisoformat(start)
                group['read_start_provisional'] = (sd - timedelta(days=3*366)).isoformat()
                group['read_start_basis'] = 'conservative_three_year_floor_pending_fiscal_quarters'
                in_window = [r for r in filings if group['read_start_provisional'] <= r['filingDate'] <= end]
                group['form_counts'] = dict(sorted(Counter(r['form'] for r in in_window).items()))
                group['item_counts'] = dict(sorted(Counter(item.strip() for r in in_window if r['form'] in ('8-K','8-K/A')
                    for item in r.get('items','').split(',') if item.strip()).items()))
                group['submission_bytes'] = sum(int(r.get('size',0) or 0) for r in in_window)
                group['submission_bytes_basis'] = 'complete_submission_not_primary_document'
                group['filings_in_read_window'] = in_window
                output_path.write_text(json.dumps(output, indent=2))
            manifest['status'] = 'inventory_collected_document_checks_pending'
            run_path.write_text(json.dumps(manifest, indent=2))
        except AccessPaused as exc:
            manifest.update(status='sec_cooldown', pause_until=exc.until)
            run_path.write_text(json.dumps(manifest, indent=2))
            print(str(exc), flush=True)
            return 75
        except AccessStopped as exc:
            manifest.update(status='stopped_sec_access', reason=str(exc))
            run_path.write_text(json.dumps(manifest, indent=2))
            print(str(exc), flush=True)
            return 76
        finally:
            client.close()
    return 0


if __name__ == '__main__':
    sys.exit(run(Path('.').resolve()))
