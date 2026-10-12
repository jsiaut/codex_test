"""Publish one immutable table generation with a single atomic pointer switch.

Readers doing several operations should resolve ``root/tables`` once. The
current.json symlink follows the same table pointer, not an independent update.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import ctypes,errno,hashlib,json,os,shutil,uuid

_DEFERRED=ContextVar('deferred_table_publication',default=None)

def sha(path):
    with Path(path).open('rb') as file:return hashlib.file_digest(file,'sha256').hexdigest()

def deferred(destination):
    active=_DEFERRED.get()
    return active is not None and Path(destination).absolute()==active

@contextmanager
def defer(root):
    token=_DEFERRED.set((Path(root)/'tables').absolute())
    try:yield
    finally:_DEFERRED.reset(token)

def _exchange(a,b):
    # Linux renameat2 can atomically exchange a pre-existing directory and a
    # symlink. Unsupported filesystems fail before touching the old directory.
    libc=ctypes.CDLL(None,use_errno=True)
    function=getattr(libc,'renameat2',None)
    if function is None:raise OSError(errno.ENOSYS,'Atomic directory exchange unavailable; prior generation retained')
    function.argtypes=[ctypes.c_int,ctypes.c_char_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_uint]
    function.restype=ctypes.c_int
    if function(-100,os.fsencode(a),-100,os.fsencode(b),2)!=0:
        error=ctypes.get_errno();raise OSError(error,os.strerror(error))

def select(candidate,destination):
    destination=Path(destination);candidate=Path(candidate)
    temporary=destination.parent/('.'+destination.name+'-pointer-'+uuid.uuid4().hex)
    temporary.symlink_to(os.path.relpath(candidate,destination.parent),target_is_directory=True)
    if destination.name=='tables':
        current=destination.parent/'current.json'
        if current.exists() and not current.is_symlink():
            # A ZIP extraction has a regular flattened manifest. Turn it into
            # the same pointer before switching the table generation.
            if destination.is_dir() and not (destination/'current.json').exists():
                shutil.copy2(current,destination/'current.json')
            link=current.with_name('.current-pointer-'+uuid.uuid4().hex)
            link.symlink_to('tables/current.json');os.replace(link,current)
    try:
        if destination.is_dir() and not destination.is_symlink():
            _exchange(temporary,destination)
            # The old directory survives the switch, including interrupted
            # selection cleanup. It is never deleted as part of publication.
            legacy=candidate.parent/('legacy-'+uuid.uuid4().hex)
            temporary.rename(legacy)
        else:os.replace(temporary,destination)
    finally:
        if temporary.is_symlink():temporary.unlink()
    if destination.name=='tables':
        current=destination.parent/'current.json'
        if not current.exists() and not current.is_symlink():
            link=current.with_name('.current-pointer-'+uuid.uuid4().hex)
            link.symlink_to('tables/current.json');os.replace(link,current)

def write(db,destination,tables,sql_literal,*,unchanged=None,validator=None):
    destination=Path(destination).absolute();destination.parent.mkdir(parents=True,exist_ok=True)
    generations=(destination.parent/'work/table_generations' if destination.name=='tables'
                 else destination.parent/('.'+destination.name+'-generations'))
    generations.mkdir(parents=True,exist_ok=True)
    candidate=generations/uuid.uuid4().hex;candidate.mkdir()
    try:
        for table in tables:
            p=candidate/(table+'.parquet')
            if unchanged and table in unchanged:
                p.hardlink_to(Path(unchanged[table]).resolve())
            else:
                info=db.execute(f"PRAGMA table_info('{table}')").fetchall()
                keys=[r[1] for r in info if r[5]]
                order=','.join(keys) if keys else 'ALL'
                db.execute(f'COPY (SELECT * FROM {table} ORDER BY {order}) TO {sql_literal(str(p))} (FORMAT PARQUET)')
        verification=validator(candidate) if validator else None
        manifest=dict(generation=candidate.name,dataset_path=os.path.relpath(candidate,destination.parent),
            status='validated' if validator else 'intermediate',
            tables={t:dict(file=t+'.parquet',sha256=sha(candidate/(t+'.parquet'))) for t in tables},
            validation=verification)
        (candidate/'current.json').write_text(json.dumps(manifest,default=str,indent=2)+'\n')
        for p in candidate.iterdir():
            with p.open('rb') as file:os.fsync(file.fileno())
        select(candidate,destination)
        return manifest
    except BaseException:
        # A failed calculation or validation never selects this directory.
        if destination.is_symlink() and destination.resolve()==candidate:raise
        shutil.rmtree(candidate,ignore_errors=True)
        raise
