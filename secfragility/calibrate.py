from pathlib import Path
import json
from .rebuild import rebuild
from .calculation import core_calibration
from .database import export,table_counts
from .controls import component_controls,concentration_controls,lease_controls,eps_controls

if __name__=='__main__':
    root=Path('.').resolve()
    db=rebuild(root)
    run=json.loads((root/'work/run.json').read_text())
    core_calibration(db,root,run['as_of'])
    collection=json.loads((root/'work/collection.json').read_text())
    component_controls(db,root,collection,run['as_of'])
    concentration_controls(db,run['as_of'])
    lease_controls(db,run['as_of'])
    eps_controls(db,run['as_of'],'0.10')
    from .controls_extended import run as extended_controls
    extended_controls(db,root,collection,run['as_of'])
    export(db,root/'work/calibration_tables')
    print(json.dumps(table_counts(db)))
    print(db.execute('SELECT control,status,count(*) FROM controls GROUP BY ALL ORDER BY 1,2').fetchall())
