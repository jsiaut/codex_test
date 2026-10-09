from pathlib import Path
from .database import create,export,table_counts
from .calculation import core_calibration
from .controls import component_controls,concentration_controls,lease_controls,eps_controls
from .controls_extended import run as extended
import json
if __name__=='__main__':
 r=Path('.').resolve();db=create(r);run=json.loads((r/'work/run.json').read_text());collection=json.loads((r/'work/collection.json').read_text())
 for t in ['documents','facts']:db.execute(f"INSERT INTO {t} BY NAME SELECT * FROM read_parquet('tables/{t}.parquet')")
 core_calibration(db,r,run['as_of']);component_controls(db,r,collection,run['as_of']);concentration_controls(db,run['as_of'])
 lease_controls(db,run['as_of']);eps_controls(db,run['as_of'],'0.10');extended(db,r,collection,run['as_of'])
 export(db,r/'work/calibration_tables');print(table_counts(db));print(db.execute('SELECT control,status,count(*) FROM controls GROUP BY ALL ORDER BY 1,2').fetchall())
 from .quarter_series import prepare,measures
 prepare(db,r,run['as_of']);measures(db,run['as_of']);export(db,r/'work/quarter_calibration_tables')
 print(db.execute('SELECT measure,view,count(*) FROM measures GROUP BY ALL ORDER BY 1,2').fetchall())
