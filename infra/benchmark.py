"""Synthetic rule execution only; deliberately excludes parsing, DB, HTTP and LLM latency."""
import time,statistics,platform,json
from app.rules.engine import RULES,evaluate_tag
from app.extraction.service import extract,normalize
from pathlib import Path
facts=[]
for p in extract([(Path('fixtures/synthetic/go.txt')).read_text()]):
    n,u,w=normalize(p.field,p.raw_value,p.raw_unit)
    facts.append(dict(id=p.field,tag='P-101',field=p.field,normalized_value=n,status='ACCEPTED'))
rules=[r.model_copy(update={'criterion_id':f'D{i*8+j+1:02}'}) for i in range(5) for j,r in enumerate(RULES)]
timings=[]
for _ in range(100):
    t=time.perf_counter()
    result=[evaluate_tag('P-101',facts,True,True,rules) for _ in range(20)]
    assert sum(len(r['results']) for r in result)==800 and all(r['outcome']=='GO' for r in result)
    timings.append(time.perf_counter()-t)
print(json.dumps(dict(host=platform.platform(),python=platform.python_version(),iterations=100,tags=20,rules_per_tag=40,p95_seconds=sorted(timings)[94],median_seconds=statistics.median(timings),scope='in-process deterministic synthetic engine; excludes database/network/parsing'),indent=2))
