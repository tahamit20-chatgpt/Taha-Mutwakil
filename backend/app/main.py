import os, json, secrets, hashlib, time
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, Depends, Request, Response, HTTPException, UploadFile, File, Header
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import select
from app.config import DEMO, ROOT, PROVIDER
from app.db import Session, Record, Job, add, serialize, uid, now
from app.auth.service import identity, issue, engineer, DEMO_USERS, hashed, local_demo_client
from app.documents import storage
from app.extraction.service import normalize, FIELDS
from app.rules.engine import evaluate_tag, rollup, PACK, PACK_HASH, digest, power
from app.reports.service import render

app=FastAPI(title='BidFit Phase 1 • synthetic screening',version='0.1.0')
secret_path=ROOT/'.runtime/session-secret';secret_path.parent.mkdir(exist_ok=True)
try:
    with secret_path.open('x') as secret_file: secret_file.write(secrets.token_urlsafe(48))
    secret_path.chmod(0o600)
except FileExistsError: pass
app.add_middleware(SessionMiddleware,secret_key=os.getenv('SESSION_SECRET',secret_path.read_text()),https_only=not DEMO,same_site='lax')
oauth=OAuth()
if os.getenv('OIDC_ISSUER'):
    oauth.register('oidc',client_id=os.environ['OIDC_CLIENT_ID'],client_secret=os.getenv('OIDC_CLIENT_SECRET'),
        server_metadata_url=os.environ['OIDC_ISSUER'].rstrip('/')+'/.well-known/openid-configuration',
        client_kwargs={'scope':'openid email profile','code_challenge_method':'S256'})

class Strict(BaseModel): model_config=ConfigDict(extra='forbid')
class ProjectIn(Strict):
    name: str=Field(min_length=1,max_length=160)
    tags: list[str]=Field(min_length=1,max_length=20)
    synthetic: bool=True
class ReviewIn(Strict):
    expected_version: int
    status: Literal['ACCEPTED','REJECTED']
    value: str
    unit: str=''
    reason: str=Field(min_length=3,max_length=1000)
class EvalIn(Strict): expected_version: int
class NoteIn(Strict):
    expected_version: int
    reason: str=Field(min_length=3,max_length=2000)
class AdjudicationIn(Strict):
    reason: str=Field(min_length=3,max_length=2000)
    evidence: str=Field(min_length=3,max_length=2000)
    disposition: Literal['ACKNOWLEDGED','DECLINED']
class CommercialIn(Strict):
    expected_version: int
    assessment: str=Field(max_length=4000)
class DecisionIn(Strict):
    evaluation_id: str
    decision: Literal['PARTICIPATE','DECLINE','HOLD']
    reason: str=Field(min_length=3,max_length=2000)

def db_session():
    with Session() as db: yield db

def project(db, pid, user, lock=False):
    q=select(Record).where(Record.id==pid,Record.kind=='project',Record.tenant_id==user['tenant'])
    if lock: q=q.with_for_update()
    row=db.scalar(q)
    if not row or user['user'] not in row.data['members']: raise HTTPException(404,'Project not found')
    return row

def object_row(db,rid,user,kind=None):
    row=db.get(Record,rid)
    if not row or row.tenant_id!=user['tenant'] or (kind and row.kind!=kind): raise HTTPException(404,'Object not found')
    project(db,row.project_id,user)
    return row

def audit(db,user,pid,action,rid): add(db,'audit',user['tenant'],pid,action=action,actor=user['user'],object_id=rid)
def check_version(row,expected):
    if row.lock_version!=expected: raise HTTPException(409,'Stale version — reload and review current evidence')

def snapshot_current(db,run,user):
    p=project(db,run.project_id,user,True)
    if p.lock_version!=run.data['snapshot']['project_version']: raise HTTPException(409,'Evaluation stale; create a new run')
    return p

@app.middleware('http')
async def headers(request,call_next):
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['Content-Security-Policy']="default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'"
    response.headers['Cache-Control']='no-store'
    return response

@app.get('/api/v1/health')
def health(): return {'status':'ok','mode':'SYNTHETIC DEMO' if DEMO else 'configured','extraction_provider':PROVIDER}
@app.get('/api/v1/ready')
def ready(db=Depends(db_session)):
    from sqlalchemy import text
    db.execute(text('SELECT 1')); storage.client().head_bucket(Bucket=storage.S3_BUCKET)
    return {'database':'ok','private_object_store':'ok'}
@app.post('/api/v1/auth/demo/{name}')
def demo_login(name:str, request:Request,response:Response,db=Depends(db_session)):
    if not DEMO or not local_demo_client(request.client.host): raise HTTPException(403,'Local demo only')
    if name not in DEMO_USERS: raise HTTPException(404,'Demo user not found')
    if request.headers.get('X-BidFit-Demo')!='local': raise HTTPException(403,'Explicit demo login header required')
    old=request.cookies.get('bidfit_session')
    if old:
        row=db.scalar(select(Record).where(Record.kind=='session',Record.data['token_hash'].as_string()==hashed(old)))
        if row: db.delete(row)
    return issue(db,DEMO_USERS[name],response)
@app.get('/api/v1/auth/login')
async def oidc_login(request:Request):
    if not oauth.create_client('oidc'): raise HTTPException(503,'Managed OIDC not configured; synthetic local demo available')
    return await oauth.oidc.authorize_redirect(request,os.environ['OIDC_REDIRECT_URI'],nonce=secrets.token_urlsafe(24))
@app.get('/api/v1/auth/callback')
async def oidc_callback(request:Request,db=Depends(db_session)):
    if not oauth.create_client('oidc'): raise HTTPException(503,'OIDC not configured')
    token=await oauth.oidc.authorize_access_token(request) # Authlib verifies state, issuer, JWKS signature and nonce.
    info=token['userinfo']
    invites=json.loads(os.getenv('OIDC_INVITES_JSON','{}')) # Bound subject IDs, not domain-based auto-enrolment.
    member=invites.get(info['sub'])
    if not member: raise HTTPException(403,'Invite required')
    response=RedirectResponse('/')
    issue(db,member,response)
    request.session.clear()
    return response
@app.get('/api/v1/session')
def session(user=Depends(identity)): return {k:v for k,v in user.items() if k!='session_id'}
@app.post('/api/v1/auth/logout')
def logout(response:Response,user=Depends(identity),db=Depends(db_session)):
    db.delete(db.get(Record,user['session_id']));db.commit();response.delete_cookie('bidfit_session');return {'ok':True}
@app.get('/api/v1/projects')
def projects(user=Depends(identity),db=Depends(db_session)):
    return [serialize(p) for p in db.scalars(select(Record).where(Record.kind=='project',Record.tenant_id==user['tenant'])).all() if user['user'] in p.data['members']]
@app.post('/api/v1/projects',status_code=201)
def create_project(body:ProjectIn,user=Depends(identity),db=Depends(db_session)):
    engineer(user)
    import re
    if len(set(body.tags))!=len(body.tags) or any(not re.fullmatch(r'[A-Za-z0-9_-]{1,40}',t) for t in body.tags): raise HTTPException(422,'Tags must be unique identifiers')
    if not body.synthetic: raise HTTPException(422,'This prototype accepts synthetic projects only')
    p=add(db,'project',user['tenant'],name=body.name,tags=body.tags,synthetic=True,members=[user['user']],commercial='Not assessed')
    for tag in body.tags: add(db,'tag',user['tenant'],p.id,name=tag)
    audit(db,user,p.id,'PROJECT_CREATED',p.id);db.commit();return serialize(p)
@app.get('/api/v1/projects/{pid}')
def get_project(pid:str,user=Depends(identity),db=Depends(db_session)):
    p=project(db,pid,user)
    rows=db.scalars(select(Record).where(Record.project_id==pid,Record.tenant_id==user['tenant']).order_by(Record.created_at,Record.id)).all()
    records={k:[serialize(r) for r in rows if r.kind==k] for k in ['document','page','fact','review','evaluation','adjudication','audit','commercial','management']}
    # Object keys remain server-side, even in authenticated manifests.
    for d in records['document']: d.pop('object_key',None)
    jobs=db.scalars(select(Job).where(Job.project_id==pid,Job.tenant_id==user['tenant'])).all()
    return {**serialize(p),**records,'jobs':[dict(id=j.id,state=j.state,stage=j.stage,attempt=j.attempt,error=j.error) for j in jobs]}
@app.post('/api/v1/projects/{pid}/documents',status_code=202)
async def upload(pid:str,file:UploadFile=File(...),idempotency_key:str=Header(...,max_length=128),user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True)
    body=await file.read(25*1024*1024+1)
    if len(body)>25*1024*1024: raise HTTPException(413,'25 MiB file limit')
    if not body: raise HTTPException(422,'Empty file')
    sha=hashlib.sha256(body).hexdigest()
    old=db.scalar(select(Job).where(Job.tenant_id==user['tenant'],Job.project_id==pid,Job.key==idempotency_key))
    if old:
        doc=db.get(Record,old.document_id)
        if doc.data['sha256']!=sha or doc.data['filename']!=Path(file.filename or '').name: raise HTTPException(409,'Idempotency key used for different upload')
        return {'document_id':doc.id,'job_id':old.id}
    docs=db.scalars(select(Record).where(Record.kind=='document',Record.project_id==pid)).all()
    if len(docs)>=20: raise HTTPException(422,'20 files/project limit')
    name=Path(file.filename or 'unknown').name[:200]
    allowed=name.lower().endswith(('.txt','.pdf'))
    # Unsupported files are retained as explicit gaps; they are never sent to a provider.
    state='QUARANTINED' if allowed else 'FAILED'
    gap=[] if allowed else ['Unsupported relevant file; replace with text PDF/TXT or resolve coverage']
    if b'EICAR-STANDARD-ANTIVIRUS-TEST-FILE' in body:
        state='FAILED';gap=['Malware test marker detected; quarantined']
    if not DEMO: raise HTTPException(503,'Production ingestion disabled until malware scanner/parser sandbox are configured')
    key=user['tenant']+'/'+pid+'/'+uid()
    storage.put(key,body)
    doc=add(db,'document',user['tenant'],pid,filename=name,object_key=key,sha256=sha,state=state,gaps=gap,page_count=0,
        classification='synthetic RFQ',version=1,scan='DEMO marker check only')
    job=Job(id=uid(),tenant_id=user['tenant'],project_id=pid,document_id=doc.id,key=idempotency_key,state='QUEUED' if state=='QUARANTINED' else 'FAILED',error=gap[0] if gap else None)
    db.add(job);p.lock_version+=1;audit(db,user,pid,'DOCUMENT_UPLOADED',doc.id);db.commit()
    return JSONResponse({'document_id':doc.id,'job_id':job.id,'state':state},status_code=202 if allowed else 415)
@app.get('/api/v1/documents/{rid}/content')
def content(rid:str,user=Depends(identity),db=Depends(db_session)):
    doc=object_row(db,rid,user,'document');audit(db,user,doc.project_id,'DOCUMENT_DOWNLOAD',rid);db.commit()
    # Authenticated proxy: current membership checked for each download; bucket never public.
    return Response(storage.get(doc.data['object_key']),media_type='application/octet-stream',headers={'Content-Disposition':'attachment; filename="source-document"'})
@app.get('/api/v1/jobs/{jid}')
def get_job(jid:str,user=Depends(identity),db=Depends(db_session)):
    job=db.get(Job,jid)
    if not job or job.tenant_id!=user['tenant']: raise HTTPException(404,'Job not found')
    project(db,job.project_id,user)
    return dict(id=job.id,state=job.state,stage=job.stage,attempt=job.attempt,error=job.error)
@app.post('/api/v1/facts/{rid}/reviews')
def review(rid:str,body:ReviewIn,user=Depends(identity),db=Depends(db_session)):
    engineer(user);f=object_row(db,rid,user,'fact');p=project(db,f.project_id,user,True)
    db.refresh(f);check_version(f,body.expected_version)
    value,unit,warnings=normalize(f.data['field'],body.value,body.unit)
    if body.status=='ACCEPTED' and (value is None or warnings): raise HTTPException(422,'Correct invalid value or ambiguous unit before accepting')
    old=serialize(f)
    f.data={**f.data,'normalized_value':value,'normalized_unit':unit,'status':body.status,'reviewed_value':body.value,'reviewed_unit':body.unit,'warnings':warnings}
    f.lock_version+=1;p.lock_version+=1
    add(db,'review',user['tenant'],f.project_id,fact_id=f.id,original=old,accepted=serialize(f),reason=body.reason,actor=user['user'])
    audit(db,user,f.project_id,'FACT_REVIEWED',f.id);db.commit();return serialize(f)
@app.post('/api/v1/projects/{pid}/evaluations',status_code=201)
def evaluate(pid:str,body:EvalIn,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    rows=db.scalars(select(Record).where(Record.project_id==pid).order_by(Record.id)).all()
    facts=[serialize(r) for r in rows if r.kind=='fact'];docs=[serialize(r) for r in rows if r.kind=='document']
    for d in docs:d.pop('object_key',None)
    coverage=bool(docs) and all(d['state'] in ('NEEDS_REVIEW','READY_FOR_EVALUATION') and not d['gaps'] for d in docs)
    tags=[evaluate_tag(t,facts,coverage,p.data['synthetic']) for t in p.data['tags']]
    snapshot=dict(project_id=pid,project_name=p.data['name'],project_version=p.lock_version,tags=tags,outcome=rollup([t['outcome'] for t in tags]),
        facts=facts,documents=docs,human_fact_reviews=[serialize(r) for r in rows if r.kind=='review'],engineer_disposition='Post-run dispositions are append-only in review history, outside this frozen report',rule_pack=PACK,rule_pack_hash=PACK_HASH,namespace='synthetic-demo-v1',
        assumptions=['DEMONSTRATION ONLY — not a genuine AI extraction or validated engineering conclusion','No KSB limits, compatibility, approvals or curves supplied','Complete-package scope; no partial lots in this milestone'],
        versions=dict(parser='pypdf-5.6/text-1',extraction=PROVIDER+'-1',calculation='si-1',code='0.1.0'),commercial=p.data['commercial'])
    snapshot['run_hash']=digest(snapshot)
    run=add(db,'evaluation',user['tenant'],pid,snapshot=snapshot)
    audit(db,user,pid,'EVALUATED',run.id);db.commit();return serialize(run)
@app.get('/api/v1/evaluations/{rid}')
def get_eval(rid:str,user=Depends(identity),db=Depends(db_session)): return serialize(object_row(db,rid,user,'evaluation'))
@app.get('/api/v1/evaluations/{rid}/exports')
def export(rid:str,format:Literal['html','json','csv']='html',user=Depends(identity),db=Depends(db_session)):
    run=object_row(db,rid,user,'evaluation');text,mime=render(run.data['snapshot'],format)
    audit(db,user,run.project_id,'EXPORTED_'+format,rid);db.commit()
    return Response(text,media_type=mime,headers={'Content-Disposition':f'attachment; filename="bidfit-{rid}.{format}"'})
@app.post('/api/v1/evaluations/{rid}/adjudications')
def adjudicate(rid:str,body:AdjudicationIn,user=Depends(identity),db=Depends(db_session)):
    engineer(user);run=object_row(db,rid,user,'evaluation');snapshot_current(db,run,user)
    row=add(db,'adjudication',user['tenant'],run.project_id,evaluation_id=rid,run_hash=run.data['snapshot']['run_hash'],actor=user['user'],**body.model_dump())
    audit(db,user,run.project_id,'ADJUDICATED',row.id);db.commit();return serialize(row)
@app.put('/api/v1/projects/{pid}/commercial-assessment')
def commercial(pid:str,body:CommercialIn,user=Depends(identity),db=Depends(db_session)):
    if user['role'] not in ('Engineer','Commercial'): raise HTTPException(403,'Commercial role required')
    p=project(db,pid,user,True);check_version(p,body.expected_version)
    p.data={**p.data,'commercial':body.assessment};p.lock_version+=1
    add(db,'commercial',user['tenant'],pid,assessment=body.assessment,actor=user['user'],official_GOAL_weights=None)
    db.commit();return serialize(p)
@app.post('/api/v1/projects/{pid}/management-decisions')
def management(pid:str,body:DecisionIn,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);run=object_row(db,body.evaluation_id,user,'evaluation')
    if run.project_id!=pid: raise HTTPException(404,'Evaluation not found')
    snapshot_current(db,run,user)
    if body.decision=='PARTICIPATE' and run.data['snapshot']['outcome'] not in ('GO','CONDITIONAL GO'): raise HTTPException(422,'Technical gate cannot be bypassed')
    row=add(db,'management',user['tenant'],pid,**body.model_dump(),actor=user['user']);db.commit();return serialize(row)
@app.get('/api/v1/rule-pack')
def rule_pack(user=Depends(identity)): return dict(namespace='synthetic-demo-v1',rules=PACK,hash=PACK_HASH,live_rules='PENDING ENGINEERING APPROVAL')

static=ROOT/'frontend/dist'


# API route registration must precede the root static mount.
@app.get('/api/v1/demo-fixture/{scenario}')
def fixture(scenario:str,user=Depends(identity)):
    if scenario not in ('go','conditional','no-go','missing','conflict','multi-tag'): raise HTTPException(404,'Fixture not found')
    return FileResponse(ROOT/'fixtures/synthetic'/f'{scenario}.txt',media_type='text/plain',filename=f'{scenario}.txt')

if static.exists(): app.mount('/',StaticFiles(directory=static,html=True),name='ui')
