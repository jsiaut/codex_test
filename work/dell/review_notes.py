"""Serve exact normalized paragraphs; no observation or amount extraction."""
from pathlib import Path
from collections import defaultdict
import json,re,difflib,argparse
base=Path('work/dell')
def compact(text):
 out=[]
 for line in text.splitlines():
  if '|' in line:line=' | '.join(x.strip() for x in line.split('|') if x.strip())
  out.append(line)
 return out
p=argparse.ArgumentParser();p.add_argument('pattern');p.add_argument('--since',default='2018-01-01');p.add_argument('--before',default='9999');p.add_argument('--diff',action='store_true');a=p.parse_args()
q=json.loads((base/'reading_queue.json').read_text());groups=defaultdict(list)
for r in q:
 if re.search(a.pattern,r['label'],re.I) and a.since<=r['report_date']<a.before:groups[r['label']].append(r)
for label,rs in sorted(groups.items()):
 previous=None
 for r in sorted(rs,key=lambda r:(r['report_date'],r['accession']),reverse=True):
  b=json.loads(Path(r['path']).read_text());lines=compact(b['text']);print('\nBLOCK',r['key'],r['report_date'],label)
  if a.diff and previous:
   dif=list(difflib.unified_diff(previous[1],lines,fromfile=previous[0],tofile=r['key'],n=1))
   print('\n'.join(dif) if dif else 'EXACT UNCHANGED TEXT: '+previous[0])
  else:print('\n'.join(lines))
  previous=(r['key'],lines)
