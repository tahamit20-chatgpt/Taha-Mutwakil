"""Populate one synthetic PDF example through the public API; no bypass of review APIs."""
import time
from pathlib import Path
import httpx
with httpx.Client(base_url='http://127.0.0.1:8000',timeout=30) as c:
    r=c.post('/api/v1/auth/demo/alice',headers={'X-BidFit-Demo':'local'});r.raise_for_status()
    c.headers['X-CSRF-Token']=r.json()['csrf']
    name='Example — reviewed synthetic cooling-water RFQ'
    existing=next((p for p in c.get('/api/v1/projects').json() if p['name']==name),None)
    if existing:
        print('Example already exists; open it in the dashboard.');raise SystemExit(0)
    r=c.post('/api/v1/projects',json={'name':name,'tags':['P-101'],'synthetic':True});r.raise_for_status();pid=r.json()['id']
    r=c.post(f'/api/v1/projects/{pid}/documents',headers={'Idempotency-Key':'seed-pdf-v1'},files={'file':('go.pdf',Path('fixtures/synthetic/go.pdf').read_bytes(),'application/pdf')});r.raise_for_status()
    jid=r.json()['job_id']
    for _ in range(100):
        j=c.get('/api/v1/jobs/'+jid).json()
        if j['state']=='FAILED':raise RuntimeError(j['error'])
        if j['state']=='DONE':break
        time.sleep(.2)
    else:raise RuntimeError('Processing timeout')
    p=c.get('/api/v1/projects/'+pid).json()
    for f in p['fact']:
        r=c.post('/api/v1/facts/'+f['id']+'/reviews',json={'expected_version':f['lock_version'],'status':'ACCEPTED','value':f['raw_value'],'unit':f['raw_unit'],'reason':'Seeded demonstration review; synthetic fixture only, not engineering approval'})
        r.raise_for_status()
    p=c.get('/api/v1/projects/'+pid).json()
    r=c.post(f'/api/v1/projects/{pid}/evaluations',json={'expected_version':p['lock_version']});r.raise_for_status()
    assert r.json()['snapshot']['outcome']=='GO'
    print('Seeded synthetic PDF workflow: 10 reviewed facts on physical page 2; fictional demo GO. Open Example in the dashboard.')
