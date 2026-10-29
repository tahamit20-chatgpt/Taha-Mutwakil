"""Repeatable synthetic examples via the public API. No private files or paid AI."""
import time
from pathlib import Path
import httpx

def checked(response):response.raise_for_status();return response.json()
def fill(c,pid,filename):
    data=checked(c.post(f'/api/v1/projects/{pid}/documents',headers={'Idempotency-Key':'synthetic-seed-v2'},files={'file':(filename,Path('fixtures/synthetic',filename).read_bytes())}))
    for _ in range(150):
        job=checked(c.get('/api/v1/jobs/'+data['job_id']))
        if job['state']=='FAILED':raise RuntimeError(job['error'])
        if job['state']=='DONE':break
        time.sleep(.2)
    else:raise RuntimeError('Synthetic processing timeout')
    p=checked(c.get('/api/v1/projects/'+pid))
    for f in p['fact']:
        if f['status']!='PROPOSED':continue
        checked(c.post('/api/v1/facts/'+f['id']+'/reviews',json=dict(expected_version=f['lock_version'],status='ACCEPTED',value=f['raw_value'],unit=f['raw_unit'],reason='Seeded synthetic demonstration review only; not company engineering approval')))
    return checked(c.get('/api/v1/projects/'+pid))
with httpx.Client(base_url='http://127.0.0.1:8000',timeout=30) as c:
    auth=checked(c.post('/api/v1/auth/demo/alice',headers={'X-BidFit-Demo':'local'}));c.headers['X-CSRF-Token']=auth['csrf']
    existing={p['name'] for p in checked(c.get('/api/v1/projects'))}
    old='Example — reviewed synthetic cooling-water RFQ'
    if old not in existing:
        p=checked(c.post('/api/v1/projects',json=dict(name=old,tags=['P-101'],synthetic=True)))
        p=fill(c,p['id'],'go.pdf')
        checked(c.post(f"/api/v1/projects/{p['id']}/evaluations",json={'expected_version':p['lock_version']}))
        print('Created original synthetic PDF example; historical workflow retained.')
    for name,filename in [('BidFit 2.0 — synthetic pump screening','v2-pump.txt'),('BidFit 2.0 — standards review required','v2-standards.xlsx')]:
        if name in existing:print('Preserved existing example: '+name);continue
        p=checked(c.post('/api/v1/rfqs',json=dict(name=name,classification=dict(product_category='Pump / Pump Set',market_area='Water',application='Water Supply',customer='Synthetic demo customer',rfq_reference='SYNTHETIC-ONLY',assigned_engineer='Demo Alice'),equipment=[dict(tag='P-101',product_category='Pump / Pump Set',quantity=2)])))
        p=fill(c,p['id'],filename);s=checked(c.get(f"/api/v1/projects/{p['id']}/summary"))
        checked(c.post(f"/api/v1/projects/{p['id']}/summary/reviews",json=dict(expected_version=p['lock_version'],summary_hash=s['summary_hash'],reason='Seeded example reviewed for demonstration only; actual engineer must verify all gaps')))
        run=checked(c.post(f"/api/v1/projects/{p['id']}/process-rfq",json={'expected_version':p['lock_version']}))
        print('Created '+name+': '+run['snapshot']['outcome']+' (fictional preliminary screening only)')
    print('BidFit examples are ready. No real engineering conclusion or company approval was generated.')
