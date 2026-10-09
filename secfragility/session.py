"""Foreground logical-session ownership; no artificial heartbeat."""
from pathlib import Path
import argparse,json
from .network import SessionLock

def command(root,action):
    owner=root/'work/foreground_owner.json'
    lock=SessionLock(root,120)
    if action=='open':
        lock.__enter__()
        owner.write_text(json.dumps({'token':lock.token}))
    else:
        lock.token=json.loads(owner.read_text())['token']
        if action=='touch':lock.touch()
        elif action=='close':
            lock.__exit__()
            owner.unlink()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['open','touch','close'])
    command(Path('.').resolve(),p.parse_args().action)
