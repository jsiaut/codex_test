from __future__ import annotations
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import re
from .database import insert
from .text import normalize_html, normalize_space, parse_html, render
from .xbrl import digest


class ObservationRejected(ValueError):
    pass


def validate_semantics(row: dict, block: dict, raw: bytes):
    if row['content_key'] != block['content_key']:
        raise ObservationRejected('Clé de contenu différente du bloc servi.')
    start,end=row['raw_byte_start'],row['raw_byte_end']
    if not (0<=start<end<=len(raw)):
        raise ObservationRejected('Plage d’octets hors du document brut.')
    quote=row['quote']
    if not quote or quote not in block['text']:
        raise ObservationRejected('Citation non retrouvée mot pour mot dans le bloc normalisé.')
    normalized_raw=normalize_space(render(parse_html(raw[start:end])))
    if block.get('source_ranges') and len(block['source_ranges'])>1:
        pieces=[]
        for a,z in block['source_ranges']:
            if not start<=a<z<=end:
                raise ObservationRejected('Continuation hors de la plage brute déclarée.')
            pieces.append(normalize_space(render(parse_html(raw[a:z]))))
        normalized_raw='\n'.join(pieces)
    if block.get('source_format')=='escaped_html_instance':
        normalized_raw=normalize_space(render(parse_html(normalized_raw.encode())))
    # Multi-part blocks retain the enclosing raw-byte range, including their
    # continuation fragments. Quotes still have to exist in this range.
    if quote not in normalized_raw:
        raise ObservationRejected('Citation absente de son emplacement brut.')
    cp=row.get('counterparty')
    if row.get('counterparty_evidence')=='named' and (not cp or cp not in block['text']):
        raise ObservationRejected('Contrepartie nommée absente du bloc.')
    if row.get('linkage_class'):
        lq=row.get('linkage_quote')
        if not lq or lq not in block['text']:
            raise ObservationRejected('La pièce de lien exige sa citation exacte.')
        if not row.get('payer') or not row.get('receiver') or not all(p in lq for p in (row['payer'],row['receiver'])):
            raise ObservationRejected('La citation de lien doit nommer les deux parties.')
    if row.get('amount_origin')=='tagged_reference':
        fact=next((f for f in block['candidates'] if f['fact_id']==row.get('tagged_fact_id')),None)
        if fact is None:
            raise ObservationRejected('Fait candidat absent du bloc.')
        if fact.get('is_nil') or fact.get('value') is None:
            raise ObservationRejected('Un fait nil ne fournit pas de montant.')
        if Decimal(str(row['amount']))!=Decimal(str(fact['value'])):
            raise ObservationRejected('Montant différent du fait candidat.')
        if (row.get('unit')!=fact['unit'] or row.get('currency')!=fact.get('currency')):
            raise ObservationRejected('Unité ou devise différente du fait candidat.')
        for field in ('period_start','period_end'):
            if row.get(field)!=fact.get(field):
                raise ObservationRejected('Période différente du fait candidat.')
    elif row.get('amount_origin')=='narrative_only' and row.get('amount') is not None:
        # Numeric narrative must be tied to the quote and an explicit scale,
        # never accepted merely because the same number occurs elsewhere.
        tokens=re.finditer(r'(?<![\w.])([+-]?\d[\d,]*(?:\.\d+)?)\s*(billion|million|thousand)?',quote,re.I)
        matched=False
        for token in tokens:
            value=Decimal(token.group(1).replace(',',''))
            factor={None:1,'thousand':1000,'million':1000000,'billion':1000000000}[token.group(2).lower() if token.group(2) else None]
            if value*factor==Decimal(str(row['amount'])):
                matched=True
        if not matched:
            raise ObservationRejected('Montant narratif non retrouvé avec son échelle explicite dans la citation.')
        if any(f.get('value') is not None and Decimal(str(f['value']))==Decimal(str(row['amount']))
               and f.get('unit')==row.get('unit') and f.get('currency')==row.get('currency') for f in block['candidates']):
            raise ObservationRejected('Montant disponible en XBRL : tagged_reference requis.')
        if row.get('currency') and not any(s in quote for s in
                ({'USD':['$','USD','U.S. dollar','US dollar'],'EUR':['€','EUR','euro']}.get(row['currency'],[row['currency']]))):
            raise ObservationRejected('Devise narrative non démontrée par la citation.')
    if row.get('abstained') and row.get('amount') is not None:
        raise ObservationRejected('Une abstention ne peut pas porter de montant.')
    if row.get('conditionality')=='conditional':
        trigger=row.get('trigger_description')
        if not trigger or trigger not in block['text']:
            raise ObservationRejected('Déclencheur conditionnel non cité mot pour mot.')


def submit(db, root: Path, block: dict, raw: bytes, rows: list[dict], as_of: str, *, schema_retry=False) -> dict:
    if not rows:
        raise ValueError('Au moins une observation ou une abstention est requise par bloc.')
    folder=root/'work/observations'
    folder.mkdir(parents=True,exist_ok=True)
    accepted,rejected=[],[]
    for rank,original in enumerate(rows):
        row=dict(original,as_of=as_of)
        row.setdefault('observation_id',digest([block['content_key'],as_of,rank,original]))
        phase='schema'
        db.execute('BEGIN TRANSACTION')
        try:
            insert(db,'observations',row)
            phase='semantic'
            validate_semantics(row,block,raw)
            db.execute('ROLLBACK')
            accepted.append(row)
        except Exception as exc:
            db.execute('ROLLBACK')
            rejected.append({'as_of':as_of,'content_key':block['content_key'],'phase':phase,
                'raw_line':original,'error':str(exc)})
    path=folder/(block['content_key']+'.jsonl')
    reject_path=folder/(block['content_key']+'.rejected.jsonl')
    if path.exists():
        existing=[json.loads(line) for line in path.read_text().splitlines()]
        if any(r['as_of']==as_of for r in existing):
            failures=[json.loads(line) for line in reject_path.read_text().splitlines()] if reject_path.exists() else []
            retry_done=any(r['record_kind']=='schema_retry' and r['as_of']==as_of for r in existing)
            if not schema_retry or retry_done or not any(r['as_of']==as_of and r['phase']=='schema' for r in failures):
                raise ValueError('Une passe déjà écrite ne se remplace pas ; nouvel as_of requis.')
            # Complete the second schema attempt of the SAME reading pass.
            # Preserve the premature first-attempt marker and original rejects.
            # This is append-only and is never used for a new reading pass.
            kind='schema_retry'
        else:kind='pass'
    else:
        if schema_retry:raise ValueError('Aucune première tentative au schéma.')
        kind='pass'
    # The pass marker persists even when every row was rejected (§7.4).
    with path.open('a') as f:
        f.write(json.dumps({'record_kind':kind,'as_of':as_of,'content_key':block['content_key'],
            'accepted_count':len(accepted)},ensure_ascii=False)+'\n')
        for row in accepted:
            f.write(json.dumps(dict(record_kind='observation',**row),ensure_ascii=False,default=str)+'\n')
    if rejected:
        with reject_path.open('a') as f:
            for row in rejected:
                f.write(json.dumps(row,ensure_ascii=False,default=str)+'\n')
    return {'accepted':len(accepted),'rejected':rejected,'path':str(path)}


def latest_pass(path: Path, current_keys: set[str], as_of: str) -> list[dict]:
    records=[json.loads(line) for line in path.read_text().splitlines()]
    dates=[r['as_of'] for r in records if r['record_kind']=='pass' and
        r['content_key'] in current_keys and datetime.fromisoformat(r['as_of'])<=datetime.fromisoformat(as_of)]
    if not dates:
        return []
    latest=max(dates,key=datetime.fromisoformat)
    return [{k:v for k,v in r.items() if k!='record_kind'} for r in records
        if r['record_kind']=='observation' and r['as_of']==latest and r['content_key'] in current_keys]
