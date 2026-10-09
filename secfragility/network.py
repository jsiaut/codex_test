"""Un seul client SEC, journalisé et soumis au verrou de session.

Un 403 persiste une échéance ; le processus rend la main au conducteur pour
qu'il puisse continuer le travail hors réseau pendant la pause réglementaire.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import socket
import time
from urllib.parse import urlparse

import httpx
import zstandard


class AccessPaused(RuntimeError):
    def __init__(self, until: float):
        self.until = until
        super().__init__(f'Accès SEC en pause jusqu’à {datetime.fromtimestamp(until, timezone.utc).isoformat()}')


class AccessStopped(RuntimeError):
    """Refus durable après une pause de dix minutes."""


class ResourceUnavailable(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def atomic_json(path: Path, obj: dict) -> None:
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True) + '\n')
    os.replace(tmp, path)


class SessionLock:
    def __init__(self, root: Path, stale_minutes: int):
        self.path = root / 'work/session.lock'
        self.stale_seconds = stale_minutes * 60
        self.token = f'{socket.gethostname()}:{os.getpid()}:{time.time_ns()}'

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation is the interprocess guard. A stale lock is retired
        # by atomic rename, with a second exclusive creation guarding competitors.
        for _ in range(2):
            try:
                fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
                with os.fdopen(fd, 'w') as f:
                    json.dump({'token': self.token, 'opened_at': utc_now()}, f)
                return self
            except FileExistsError:
                if time.time() - self.path.stat().st_mtime <= self.stale_seconds:
                    raise RuntimeError('Une autre session est encore vivante.')
                retired = self.path.with_name(f'session.stale.{time.time_ns()}.json')
                try:
                    os.rename(self.path, retired)
                except FileNotFoundError:
                    pass
        raise RuntimeError('Impossible d’acquérir le verrou de session.')

    def touch(self):
        if not self.path.exists() or json.loads(self.path.read_text())['token'] != self.token:
            raise RuntimeError('Le verrou de cette session a été perdu.')
        os.utime(self.path, None)

    def __exit__(self, *exc):
        if self.path.exists() and json.loads(self.path.read_text())['token'] == self.token:
            self.path.unlink()


class SecClient:
    def __init__(self, root: Path, config: dict, as_of: str, lock: SessionLock,
                 transport=None, clock=time.time, sleep=time.sleep):
        ua = config.get('user_agent')
        if not ua or not re.fullmatch(r'.+\s+[^\s@]+@[^\s@]+\.[^\s@]+', ua):
            raise ValueError('Le User-Agent réel fourni par l’utilisateur est obligatoire.')
        self.root, self.config, self.as_of, self.lock = root, config, as_of, lock
        self.clock, self.sleep = clock, sleep
        self.state_path = root / 'work/network_state.json'
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state = json.loads(self.state_path.read_text()) if self.state_path.exists() else {}
        self.client = httpx.Client(headers={'User-Agent': ua, 'Accept-Encoding': 'gzip, deflate'},
            timeout=config['network']['timeout_seconds'], follow_redirects=False, transport=transport)
        self.seen = {}

    def close(self):
        self.client.close()

    def _journal(self, url, status, nbytes, start, latency, error=None):
        row = {'as_of': self.as_of, 'timestamp': datetime.fromtimestamp(start, timezone.utc).isoformat(),
            'url': url, 'status': status, 'bytes': nbytes, 'latency_seconds': latency,
            'error': error}
        with (self.root / 'journal.jsonl').open('a') as f:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
        self.lock.touch()

    def _cache_path(self, url: str) -> Path:
        p = urlparse(url)
        parts = p.path.strip('/').split('/')
        if len(parts) >= 5 and parts[:2] == ['Archives', 'edgar'] and parts[2] == 'data':
            return self.root / 'cache/archives' / parts[3] / parts[4] / (parts[-1] + '.zst')
        if p.path.startswith('/Archives/'):
            return self.root / 'cache/archives/reference' / (hashlib.sha256(url.encode()).hexdigest() + '.zst')
        digest = hashlib.sha256(url.encode()).hexdigest()
        version = self.as_of.replace(':', '-').replace('+', '_')
        return self.root / 'cache/api' / digest / (version + '.bin.zst')

    def get(self, url: str) -> bytes:
        parsed = urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in self.config['network']['allowed_hosts']:
            raise ValueError('Hôte hors SEC ou protocole non HTTPS ; aucun User-Agent transmis.')
        if url in self.seen:
            return self.seen[url]
        path = self._cache_path(url)
        if path.exists():
            data = zstandard.ZstdDecompressor().decompress(path.read_bytes())
            self.seen[url] = data
            return data
        until = self.state.get('pause_until', 0)
        if self.clock() < until:
            raise AccessPaused(until)
        if self.state.get('stopped'):
            raise AccessStopped('La SEC refuse durablement l’accès après la pause réglementaire.')
        delays = [0] + self.config['network']['retry_delays_seconds']
        for delay in delays:
            if delay:
                self.sleep(delay)
            # Persist the previous request time across processes, including retries.
            gap = 1 / self.config['network']['requests_per_second']
            wait = gap - (self.clock() - self.state.get('last_request', 0))
            if wait > 0:
                self.sleep(wait)
            start = self.clock()
            self.state['last_request'] = start
            atomic_json(self.state_path, self.state)
            try:
                response = self.client.get(url)
            except httpx.TransportError as exc:
                self._journal(url, None, 0, start, self.clock()-start, type(exc).__name__)
                continue
            self._journal(url, response.status_code, len(response.content), start, self.clock()-start)
            if response.status_code == 403:
                self.state['forbidden_count'] = self.state.get('forbidden_count', 0) + 1
                self.state['pause_until'] = self.clock() + self.config['network']['forbidden_status_pause_seconds']
                self.state['stopped'] = self.state['forbidden_count'] > self.config['network']['max_forbidden_retries']
                atomic_json(self.state_path, self.state)
                if self.state['stopped']:
                    raise AccessStopped('Deux refus SEC, séparés d’une pause d’au moins dix minutes.')
                raise AccessPaused(self.state['pause_until'])
            if response.status_code in (429,) or response.status_code >= 500:
                continue
            if 300 <= response.status_code < 400:
                target = str(response.url.join(response.headers.get('location', '')))
                # Recursing re-checks the host, rate limiter and cooldown.
                return self.get(target)
            if response.status_code != 200:
                raise ResourceUnavailable(f'{response.status_code} : {url}')
            data = response.content
            # SEC may occasionally return a denial page with a successful status.
            if any(marker in data[:10000] for marker in
                   [b'Request Rate Threshold Exceeded', b'Your Request Originates from an Undeclared Automated Tool']):
                self.state['forbidden_count'] = self.state.get('forbidden_count', 0) + 1
                self.state['pause_until'] = self.clock() + self.config['network']['forbidden_status_pause_seconds']
                self.state['stopped'] = self.state['forbidden_count'] > self.config['network']['max_forbidden_retries']
                atomic_json(self.state_path, self.state)
                raise AccessPaused(self.state['pause_until'])
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + '.tmp')
            tmp.write_bytes(zstandard.ZstdCompressor(level=6).compress(data))
            os.replace(tmp, path)
            self.state.pop('pause_until', None)
            self.state['forbidden_count'] = 0
            atomic_json(self.state_path, self.state)
            self.seen[url] = data
            return data
        raise ResourceUnavailable(f'Échec temporaire après tentatives : {url}')

    def json(self, url: str):
        return json.loads(self.get(url))
