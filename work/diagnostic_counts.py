from pathlib import Path
import duckdb,json
root=Path('.');d=duckdb.connect()
for t in ('facts','measures','controls','exclusions'):
 p=root/'work/phase3_tables'/(t+'.parquet')
 print(t,d.execute('SELECT count(*) FROM read_parquet(?)',[str(p)]).fetchone()[0])
print(d.execute("SELECT group_id,control,count(*) FROM read_parquet('work/phase3_tables/controls.parquet') WHERE status='mismatch' GROUP BY ALL ORDER BY group_id,control").fetchall())
