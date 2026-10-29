import io,json,secrets,hashlib
from datetime import date
from pathlib import Path
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Response
from fastapi.responses import FileResponse
from pydantic import Field
from sqlalchemy import select
from app.api.access import db_session,project,object_row,audit,check_version,snapshot_current
from app.auth.service import identity,engineer,require_permission
from app.db import Record,add,serialize,now,uid
from app.config import ROOT
from app.rules.engine import digest,rollup
from .models import *
from . import service as svc
router=APIRouter(prefix='/api/v1')

def global_row(db,rid,user,kind):
    r=db.get(Record,rid)
    if not r or r.tenant_id!=user['tenant'] or r.kind!=kind or r.project_id:raise HTTPException(404,'Reference not found')
    return r

@router.get('/configuration')
def configuration(user=Depends(identity),db=Depends(db_session)):
    from app.extraction.service import FIELDS
    r=svc.master(db,user['tenant']);db.commit();return {**serialize(r),'field_contract':{key:dict(numeric=spec is not None,unit=spec[1] if spec else '') for key,spec in FIELDS.items()}}
class MasterUpdate(Strict):
    expected_version:int
    customers:list[str]=Field(min_length=1,max_length=100)
    markets:dict[str,list[str]]
@router.put('/configuration')
def configure(body:MasterUpdate,user=Depends(identity),db=Depends(db_session)):
    require_permission(user,'configuration');r=svc.master(db,user['tenant']);db.refresh(r,with_for_update=True);check_version(r,body.expected_version)
    if set(body.markets)!=set(svc.BASE_MASTER['markets']):raise HTTPException(422,'Preserve the approved six market areas')
    for market,apps in svc.BASE_MASTER['markets'].items():
        if not set(apps)<=set(body.markets[market]) or len(body.markets[market])>100 or any(not x.strip() or len(x)>100 for x in body.markets[market]):raise HTTPException(422,'Preserve approved applications; add new choices without deleting them')
    if any(not x.strip() or len(x)>160 for x in body.customers):raise HTTPException(422,'Invalid customer profile')
    add(db,'configuration_history',user['tenant'],original=serialize(r),actor=user['user'])
    r.data={**r.data,'customers':list(dict.fromkeys(body.customers)),'markets':body.markets,'version':r.data['version']+1};r.lock_version+=1;db.commit();return serialize(r)

@router.post('/rfqs',status_code=201)
def new_rfq(body:CreateRFQ,user=Depends(identity),db=Depends(db_session)):
    engineer(user);svc.validate_classification(db,user['tenant'],body.classification,body.equipment)
    eq=[e.model_dump() for e in body.equipment]
    p=add(db,'project',user['tenant'],name=body.name,tags=[e['tag'] for e in eq],equipment=eq,classification=body.classification.model_dump(mode='json'),workflow_version='2.0',synthetic=True,members=[user['user']],commercial='Not assessed',updated_at=now(),summary_notes='')
    for item in eq:add(db,'tag',user['tenant'],p.id,name=item['tag'],product_category=item['product_category'],quantity=item['quantity'])
    audit(db,user,p.id,'RFQ_CLASSIFIED',p.id);db.commit();return serialize(p)
@router.put('/projects/{pid}/classification')
def classify(pid:str,body:EditClassification,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    svc.validate_classification(db,user['tenant'],body.classification,body.equipment)
    if set(p.data['tags'])!={e.tag for e in body.equipment}:raise HTTPException(422,'Keep existing equipment tags; adding/removing tags requires a separate controlled revision')
    add(db,'classification_review',user['tenant'],pid,original=p.data.get('classification'),actor=user['user'])
    p.data={**p.data,'name':body.name,'classification':body.classification.model_dump(mode='json'),'workflow_version':'2.0','equipment':[e.model_dump() for e in body.equipment],'updated_at':now()};p.lock_version+=1;audit(db,user,pid,'CLASSIFICATION_CHANGED',pid);db.commit();return serialize(p)
@router.get('/projects/{pid}/summary')
def get_summary(pid:str,user=Depends(identity),db=Depends(db_session)):
    s=svc.summary(db,project(db,pid,user));db.commit();return s
class SummaryNote(Strict):
    expected_version:int
    notes:str=Field(max_length=3000)
@router.put('/projects/{pid}/summary')
def summary_notes(pid:str,body:SummaryNote,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    p.data={**p.data,'summary_notes':body.notes,'updated_at':now()};p.lock_version+=1;audit(db,user,pid,'SUMMARY_EDITED',pid);db.commit();return svc.summary(db,p)
@router.post('/projects/{pid}/summary/reviews')
def summary_review(pid:str,body:ReviewSummary,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version);s=svc.summary(db,p)
    if s['summary_hash']!=body.summary_hash:raise HTTPException(409,'Summary changed; reload it before reviewing')
    if s['unreviewed_count']:raise HTTPException(409,'Accept/correct or reject proposed facts before reviewing the summary')
    if not s['documents']:raise HTTPException(409,'Upload source documents before reviewing the summary')
    r=add(db,'summary_review',user['tenant'],pid,summary_hash=s['summary_hash'],reason=body.reason,actor=user['user'],known_missing=s['missing'],known_conflicts=s['conflicts']);audit(db,user,pid,'SUMMARY_REVIEWED',r.id);db.commit();return serialize(r)

@router.get('/projects/{pid}/standards')
def standards(pid:str,user=Depends(identity),db=Depends(db_session)):
    r=svc.standards(db,project(db,pid,user));db.commit();return r
@router.post('/projects/{pid}/standards/reviews')
def confirm_standard(pid:str,body:Applicability,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    if body.tag not in p.data['tags']:raise HTTPException(422,'Unknown equipment tag')
    s=svc.standards(db,p)
    if not any(x['tag']==body.tag and x['code']==body.code and x['edition']==body.edition for x in s['explicit']+s['suggested']):raise HTTPException(422,'Standard is not referenced by this RFQ/registry')
    r=add(db,'standard_review',user['tenant'],pid,**body.model_dump(exclude={'expected_version'}),actor=user['user']);p.lock_version+=1;audit(db,user,pid,'STANDARD_APPLICABILITY_REVIEWED',r.id);db.commit();return serialize(r)
@router.get('/registry/standards')
def registry_standards(user=Depends(identity),db=Depends(db_session)):
    svc.ensure_registry(db,user['tenant']);data=[serialize(r) for r in svc.rows(db,user['tenant'],'standard_ref')];db.commit();return data
@router.post('/registry/standards',status_code=201)
def add_standard(body:StandardInput,user=Depends(identity),db=Depends(db_session)):
    require_permission(user,'configuration');svc.ensure_registry(db,user['tenant'])
    r=add(db,'standard_ref',user['tenant'],**body.model_dump(),version=1,availability='REFERENCE NOT AVAILABLE / REQUIRES REVIEW',approval_status='UNVERIFIED');db.commit();return serialize(r)
@router.get('/registry/rules')
def registry_rules(user=Depends(identity),db=Depends(db_session)):
    svc.ensure_registry(db,user['tenant']);data=[serialize(r) for r in svc.rows(db,user['tenant'],'engineering_rule')];db.commit();return dict(rules=data,registry_hash=svc.registry_hash(db,user['tenant']),live_rules='Pending approved KSB engineering data')
@router.post('/registry/rules',status_code=201)
def submit_rule(body:RuleInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);svc.ensure_registry(db,user['tenant'])
    if body.standard_id:global_row(db,body.standard_id,user,'standard_ref')
    # Lock the tenant's configuration to allocate versions without concurrent collisions.
    root=svc.master(db,user['tenant']);db.refresh(root,with_for_update=True)
    previous=[r for r in svc.rows(db,user['tenant'],'engineering_rule') if r.data['criterion_id']==body.criterion_id]
    payload=body.model_dump(mode='json')
    r=add(db,'engineering_rule',user['tenant'],**payload,version=max([r.data['version'] for r in previous],default=0)+1,approval_status='DRAFT',content_hash=digest(payload),synthetic_only=True,submitted_by=user['user'],approved_by=None,approved_at=None)
    db.commit();return serialize(r)
@router.post('/registry/rules/{rid}/approve')
def approve_rule(rid:str,body:Reason,user=Depends(identity),db=Depends(db_session)):
    require_permission(user,'engineering_approval');r=global_row(db,rid,user,'engineering_rule');db.refresh(r,with_for_update=True)
    if r.data['approval_status']!='DRAFT':raise HTTPException(409,'Rule version already reviewed; submit a new version')
    fields=RuleInput.model_fields
    model=RuleInput.model_validate({k:r.data[k] for k in fields if k in r.data})
    if digest(model.model_dump(mode='json'))!=r.data['content_hash']:raise HTTPException(409,'Rule content hash mismatch')
    if model.effective_date>date.today():raise HTTPException(422,'Future rules cannot be activated early')
    r.data={**r.data,'approval_status':'APPROVED','approved_by':user['user'],'approved_at':now(),'approval_reason':body.reason};r.lock_version+=1
    add(db,'rule_approval',user['tenant'],rule_id=rid,content_hash=r.data['content_hash'],actor=user['user'],reason=body.reason,namespace='SYNTHETIC ONLY');db.commit();return serialize(r)

class ProcessInput(Strict):expected_version:int
@router.post('/projects/{pid}/process-rfq',status_code=201)
def process_rfq(pid:str,body:ProcessInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    if p.data.get('workflow_version')!='2.0':raise HTTPException(422,'Legacy RFQ: use its existing technical evaluation workflow')
    s,tags,std,rs=svc.compliance(db,p)
    facts,documents=svc.source_rows(db,p)
    snapshot=dict(project_id=p.id,project_name=p.data['name'],project_version=p.lock_version,classification=p.data['classification'],equipment=svc.equipment(p),summary=s,standards=std,tags=tags,outcome=rollup([t['outcome'] for t in tags]),compliance_matrix=[f for t in tags for f in t['results']],facts=facts,documents=documents,rule_pack=[serialize(r) for r in rs],rule_pack_hash=svc.registry_hash(db,p.tenant_id),registry_hash=svc.registry_hash(db,p.tenant_id),namespace='synthetic-demo-v2',human_fact_reviews=[serialize(r) for r in svc.rows(db,p.tenant_id,'review',pid)],engineer_disposition='Preliminary; post-run review history is append-only',commercial=p.data['commercial'],versions=dict(workflow='2.0',parser='document-v2',code='2.0.0',report='2.0'),assumptions=['Synthetic-only preliminary screening — not KSB certification','No complete portfolio exclusion, licensed standard clauses, performance curves or validated hydraulic selection supplied','Standards suggestions alone never create mandatory obligations','Commercial attractiveness cannot change technical eligibility'])
    if s.get('customer_approvals'):
        snapshot['customer_approvals']=s['customer_approvals']
        snapshot['approval_registry_hash']=s['customer_approvals']['registry_hash']
        snapshot['versions']['approvals']='aramco-evidence-v1'
        snapshot['assumptions'].append('Aramco historical commodity and portfolio records are owner-supplied structured references; named source attachments and current verification are pending')
    snapshot['run_hash']=digest(snapshot);r=add(db,'evaluation',user['tenant'],pid,snapshot=snapshot);audit(db,user,pid,'RFQ_PROCESSED',r.id);db.commit();return serialize(r)

@router.patch('/documents/{rid}/metadata')
def metadata(rid:str,body:DocumentMetadata,user=Depends(identity),db=Depends(db_session)):
    engineer(user);doc=object_row(db,rid,user,'document');p=project(db,doc.project_id,user,True);db.refresh(doc);check_version(doc,body.expected_version)
    m=svc.master(db,user['tenant']).data
    if body.category not in m['document_categories']:raise HTTPException(422,'Choose a configured document category')
    add(db,'document_review',user['tenant'],p.id,document_id=rid,original=serialize(doc),reason=body.reason,actor=user['user'])
    doc.data={**doc.data,**body.model_dump(exclude={'expected_version','reason'}),'metadata_confirmed_by':user['user'],'category_status':'CONFIRMED'};doc.lock_version+=1;p.lock_version+=1;audit(db,user,p.id,'DOCUMENT_METADATA_CHANGED',rid);db.commit();result=serialize(doc);result.pop('object_key',None);return result

@router.get('/library/product-families')
def families(user=Depends(identity),db=Depends(db_session)):return [serialize(r) for r in svc.rows(db,user['tenant'],'product_family')]
@router.post('/library/product-families',status_code=201)
def family(body:FamilyInput,user=Depends(identity),db=Depends(db_session)):
    require_permission(user,'configuration');r=add(db,'product_family',user['tenant'],**body.model_dump(),version=1,approval_status='UNVERIFIED',namespace='synthetic-only',created_by=user['user']);db.commit();return serialize(r)
@router.get('/projects/{pid}/studios')
def studios(pid:str,user=Depends(identity),db=Depends(db_session)):
    p=project(db,pid,user);svc.ensure_registry(db,user['tenant']);s=svc.summary(db,p)
    result=dict(inputs=s['equipment'],candidates=[serialize(r) for r in svc.rows(db,user['tenant'],'selection_candidate',pid)],prices=[serialize(r) for r in svc.rows(db,user['tenant'],'price_reference',pid)],quotations=[serialize(r) for r in svc.rows(db,user['tenant'],'quotation',pid)],templates=[serialize(r) for r in svc.rows(db,user['tenant'],'quote_template')],selection_status='PENDING ENGINEERING DATA — no approved curves/compatibility data',icap_status='REQUIRES CONFIGURATION — no approved cost integration or automatic pricing',easyselect_status='NOT AVAILABLE YET — authorized reference adapter only')
    for candidate in result['candidates']:
        candidate['reference_reviews']=[serialize(r) for r in svc.rows(db,user['tenant'],'selection_review',pid) if r.data['candidate_id']==candidate['id']]
        candidate['inputs_stale']=candidate['input_hash']!=s['summary_hash']
    db.commit();return result
@router.post('/projects/{pid}/selection/candidates',status_code=201)
def candidate(pid:str,body:CandidateInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version);family=global_row(db,body.family_id,user,'product_family')
    item=next((e for e in svc.equipment(p) if e['tag']==body.tag),None)
    if not item or family.data['product_category']!=item['product_category']:raise HTTPException(422,'Choose a product family matching this equipment category')
    r=add(db,'selection_candidate',user['tenant'],pid,**body.model_dump(exclude={'expected_version'}),family_snapshot=serialize(family),source_project_version=p.lock_version,input_hash=svc.summary(db,p)['summary_hash'],status='UNVERIFIED',engineering_review='PENDING',actor=user['user']);audit(db,user,pid,'CANDIDATE_REFERENCED',r.id);db.commit();return serialize(r)
class CandidateReview(Reason):disposition:Literal['REFERENCE_REVIEWED','REJECTED','NEEDS_DATA']
@router.post('/selection/candidates/{rid}/reviews')
def candidate_review(rid:str,body:CandidateReview,user=Depends(identity),db=Depends(db_session)):
    engineer(user);r=object_row(db,rid,user,'selection_candidate');p=project(db,r.project_id,user,True)
    if r.data['input_hash']!=svc.summary(db,p)['summary_hash']:raise HTTPException(409,'Candidate inputs stale; create a new reference')
    review=add(db,'selection_review',user['tenant'],p.id,candidate_id=rid,**body.model_dump(),actor=user['user'],performance_validation='UNVERIFIED');db.commit();return serialize(review)
@router.post('/projects/{pid}/pricing/references',status_code=201)
def price(pid:str,body:PriceInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    if body.tag not in p.data['tags']:raise HTTPException(422,'Unknown equipment tag')
    if body.price_kind=='Approved Selling Price':raise HTTPException(422,'Approved selling prices require a configured approval workflow; store a target/reference instead')
    r=add(db,'price_reference',user['tenant'],pid,**body.model_dump(mode='json',exclude={'expected_version'}),approval_status='DRAFT_UNAPPROVED',version=1,actor=user['user'],source_project_version=p.lock_version);audit(db,user,pid,'PRICE_REFERENCE_RECORDED',r.id);db.commit();return serialize(r)
@router.post('/projects/{pid}/quotations',status_code=201)
def quotation(pid:str,body:QuoteInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version);run=object_row(db,body.evaluation_id,user,'evaluation')
    if run.project_id!=pid:raise HTTPException(404,'Evaluation not found')
    snapshot_current(db,run,user);template=global_row(db,body.template_id,user,'quote_template')
    prior=svc.rows(db,user['tenant'],'quotation',pid)
    snap=dict(project_name=p.data['name'],evaluation_id=run.id,evaluation_hash=run.data['snapshot']['run_hash'],technical_outcome=run.data['snapshot']['outcome'],requirements=run.data['snapshot']['facts'],classification=p.data.get('classification'),template=serialize(template),notes=body.notes,selection_status='UNVERIFIED',prices=None,commercial_terms=None,unavailable=['Approved product configuration','Approved current pricing','Company commercial terms','Authorized submission approval'],status='DRAFT — NOT FOR SUBMISSION',version=len(prior)+1)
    snap['content_hash']=digest(snap);r=add(db,'quotation',user['tenant'],pid,snapshot=snap,actor=user['user']);audit(db,user,pid,'QUOTATION_DRAFTED',r.id);db.commit();return serialize(r)
@router.get('/quotations/{rid}/export')
def quote_export(rid:str,user=Depends(identity),db=Depends(db_session)):
    import html
    r=object_row(db,rid,user,'quotation');s=r.data['snapshot'];audit(db,user,r.project_id,'QUOTATION_DRAFT_EXPORTED',rid);db.commit()
    body='<!doctype html><html><head><meta charset="utf-8"><title>BidFit draft</title></head><body><h1>DRAFT — NOT FOR SUBMISSION</h1><p>No product guarantee or approved price. Preliminary synthetic evidence only.</p><pre>'+html.escape(json.dumps(s,sort_keys=True,indent=2))+'</pre></body></html>'
    return Response(body,media_type='text/html',headers={'Content-Disposition':f'attachment; filename="bidfit-draft-{rid}.html"'})

@router.get('/branding/status')
def branding_status():return {'configured':(ROOT/'.runtime/branding-logo.png').exists() or (ROOT/'frontend/public/branding/ksb-logo.png').exists() or (ROOT/'frontend/dist/branding/ksb-logo.png').exists(),'message':'Upload the original logo PNG unchanged in Settings; inline chat images are not byte assets in this workspace'}
@router.get('/branding/logo')
def logo():
    for path in [ROOT/'.runtime/branding-logo.png',ROOT/'frontend/public/branding/ksb-logo.png',ROOT/'frontend/dist/branding/ksb-logo.png']:
        if path.exists():return FileResponse(path,media_type='image/png')
    raise HTTPException(404,'Original logo file not configured')
@router.post('/branding/logo')
async def upload_logo(file:UploadFile=File(...),user=Depends(identity),db=Depends(db_session)):
    from PIL import Image
    require_permission(user,'configuration');body=await file.read(2*1024*1024+1)
    if len(body)>2*1024*1024:raise HTTPException(413,'Logo limit: 2 MiB')
    try:
        image=Image.open(io.BytesIO(body))
        if image.format!='PNG' or image.width*image.height>10000000:raise ValueError()
        image.verify()
    except Exception:raise HTTPException(415,'Use the original PNG logo file; invalid or oversized image')
    path=ROOT/'.runtime/branding-logo.png';temp=path.with_suffix('.'+secrets.token_hex(4)+'.tmp');temp.write_bytes(body);temp.replace(path)
    add(db,'branding_audit',user['tenant'],actor=user['user'],sha256=hashlib.sha256(body).hexdigest(),action='ORIGINAL_LOGO_UPLOADED_UNCHANGED');db.commit();return dict(configured=True,sha256=hashlib.sha256(body).hexdigest())

@router.get('/knowledge')
def knowledge(user=Depends(identity),db=Depends(db_session)):
    allowed={p.id:p.data['name'] for p in svc.rows(db,user['tenant'],'project') if user['user'] in p.data['members']}
    return [dict(document_id=d.id,project_id=d.project_id,project_name=allowed[d.project_id],filename=d.data['filename'],sha256=d.data['sha256'],revision=d.data.get('revision',''),status=d.data['state']) for d in svc.rows(db,user['tenant'],'document') if d.project_id in allowed]

@router.get('/analytics')
def analytics(user=Depends(identity),db=Depends(db_session)):
    projects=[p for p in svc.rows(db,user['tenant'],'project') if user['user'] in p.data['members']]
    counts={k:0 for k in ('GO','CONDITIONAL GO','INSUFFICIENT DATA','NO-GO','NOT EVALUATED')}
    for p in projects:
        runs=svc.rows(db,user['tenant'],'evaluation',p.id)
        counts[runs[-1].data['snapshot']['outcome'] if runs else 'NOT EVALUATED']+=1
    return dict(accessible_rfqs=len(projects),outcomes=counts,notice='Latest historical computed outcomes only; current approvals can be stale. No commercial weights are invented.')
