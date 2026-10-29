import hashlib
from datetime import date
from fastapi import APIRouter,Depends,HTTPException,UploadFile,File,Response
from sqlalchemy import select
from app.api.access import db_session,project,audit,check_version
from app.auth.service import identity,engineer,require_permission
from app.config import DEMO
from app.db import add,serialize,now,uid
from app.documents import storage
from . import service as svc
from .store import ApprovalProfile,ApprovalEvidence,ApprovalCommodity,ProductSeries,ProductApprovalMapping,ApprovalVerification,encode,insert
from .models import EvidenceInput,CommodityInput,SeriesInput,MappingInput,VerificationInput,AssignmentInput,PolicyInput

router=APIRouter(prefix='/api/v1')

def admin(user):engineer(user);require_permission(user,'configuration')

def revise(db,row,user,payload,reason,expected):
    if expected is None or row.version!=expected:raise HTTPException(409,'Reload the current registry revision before updating')
    before=encode(row);row.data={**row.data,**payload,'updated_at':now()};row.version+=1;db.flush()
    svc.event(db,user['tenant'],user['user'],'REFERENCE_REVISED',row.id,before,encode(row),reason)

@router.get('/approvals/registry')
def registry(product_category:str='',pump_classification:str='',code:str='',product_series:str='',status:str='',user=Depends(identity),db=Depends(db_session)):
    c=svc.catalog(db,user['tenant'])
    for commodity in c['commodities']:
        commodity['verification']=svc.current_status(commodity,c['verifications'],c['evidence'])
        commodity['product_series']=[p for p in c['products'] if any(m['commodity_id']==commodity['id'] and m['product_series_id']==p['id'] for m in c['mappings'])]
    c['commodities']=[x for x in c['commodities'] if (not product_category or x['product_category']==product_category)
        and (not code or code in x['commodity_code']) and (not status or x['verification']['status']==status)
        and (not product_series or any(product_series.casefold() in p['name'].casefold() for p in x['product_series']))
        and (not pump_classification or any(pump_classification.casefold() in p['classification'].casefold() for p in x['product_series']))]
    db.commit();return c

@router.get('/approvals/products')
def products(user=Depends(identity),db=Depends(db_session)):
    c=svc.catalog(db,user['tenant']);db.commit();return c['products']

@router.get('/approvals/evidence/{rid}')
def evidence(rid:str,user=Depends(identity),db=Depends(db_session)):
    r=svc.get(db,ApprovalEvidence,rid,user['tenant']);return svc.public_evidence(r)

@router.post('/approvals/evidence',status_code=201)
def new_evidence(body:EvidenceInput,user=Depends(identity),db=Depends(db_session)):
    admin(user);svc.ensure_registry(db,user['tenant'])
    r=insert(db,ApprovalEvidence,user['tenant'],data={**body.model_dump(mode='json'),'attachment_status':'PENDING','object_key':None,
        'sha256':None,'document_inspected':False,'authorized_current_source':False,'synthetic':body.source_type=='SYNTHETIC_TEST','created_by':user['user']})
    svc.event(db,user['tenant'],user['user'],'EVIDENCE_REFERENCE_ADDED',r.id,after=svc.public_evidence(r),reason=body.notes);db.commit();return svc.public_evidence(r)

@router.post('/approvals/evidence/{rid}/attachment')
async def attach_evidence(rid:str,file:UploadFile=File(...),user=Depends(identity),db=Depends(db_session)):
    admin(user);r=svc.get(db,ApprovalEvidence,rid,user['tenant'],True)
    if r.data.get('object_key'):raise HTTPException(409,'Evidence bytes are immutable; add a new source revision')
    # Real evidence ingestion remains closed with the existing prototype scanner
    # boundary. A synthetic text attachment exercises private storage and history
    # without processing protected company documents or faking customer authority.
    if not DEMO or r.data['source_type']!='SYNTHETIC_TEST':raise HTTPException(422,'Live approval-document ingestion requires the approved scanner and authority integration. Use only a synthetic test source here.')
    body=await file.read(2*1024*1024+1)
    if len(body)>2*1024*1024:raise HTTPException(413,'Evidence attachment limit: 2 MiB')
    try:
        content=body.decode('utf-8')
        if not file.filename.lower().endswith('.txt') or '\x00' in content or 'SYNTHETIC DEMO' not in content:raise ValueError()
    except Exception:raise HTTPException(415,'Use a UTF-8 .txt fixture labelled SYNTHETIC DEMO')
    key=f"{user['tenant']}/approvals/{r.id}/{uid()}";storage.put(key,body)
    r.data={**r.data,'object_key':key,'sha256':hashlib.sha256(body).hexdigest(),'attachment_status':'ATTACHED_SYNTHETIC','filename':file.filename[:250],'document_inspected':False}
    r.version+=1;svc.event(db,user['tenant'],user['user'],'SYNTHETIC_EVIDENCE_ATTACHED',r.id,after=svc.public_evidence(r));db.commit();return svc.public_evidence(r)

@router.get('/approvals/evidence/{rid}/content')
def evidence_content(rid:str,user=Depends(identity),db=Depends(db_session)):
    r=svc.get(db,ApprovalEvidence,rid,user['tenant'])
    if not r.data.get('object_key'):raise HTTPException(404,'Supporting source attachment is pending')
    body=storage.get(r.data['object_key'])
    if hashlib.sha256(body).hexdigest()!=r.data['sha256']:raise HTTPException(409,'Evidence content hash mismatch')
    svc.event(db,user['tenant'],user['user'],'EVIDENCE_DOWNLOADED',r.id);db.commit()
    return Response(body,media_type='text/plain',headers={'Content-Disposition':f'attachment; filename="approval-evidence-{rid}.txt"','Cache-Control':'no-store'})

@router.post('/approvals/commodities',status_code=201)
def commodity(body:CommodityInput,user=Depends(identity),db=Depends(db_session)):
    admin(user);svc.ensure_registry(db,user['tenant']);profile=svc.get(db,ApprovalProfile,body.profile_id,user['tenant'],True)
    svc.get(db,ApprovalEvidence,body.evidence_id,user['tenant'])
    old=db.scalar(select(ApprovalCommodity).where(ApprovalCommodity.tenant_id==user['tenant'],ApprovalCommodity.profile_id==profile.id,ApprovalCommodity.commodity_code==body.commodity_code))
    payload=body.model_dump(mode='json',exclude={'profile_id','commodity_code','evidence_id','expected_version','reason'})
    if old:
        if old.data['product_category']!=body.product_category and any(m.commodity_id==old.id for m in svc.entries(db,user['tenant'],ProductApprovalMapping)):raise HTTPException(422,'Mapped commodity category cannot be changed; add a controlled new classification')
        if old.data.get('historical_original_listing') and (body.original_approval_date.isoformat() if body.original_approval_date else None)!=old.data['original_approval_date']:raise HTTPException(422,'Keep the original historical approval date; new verification dates belong in appended review records')
        # Include source relationship in the immutable event before changing it.
        before=encode(old);revise(db,old,user,payload,body.reason,body.expected_version);old.evidence_id=body.evidence_id
        svc.event(db,user['tenant'],user['user'],'COMMODITY_SOURCE_REVISED',old.id,before,encode(old),body.reason);r=old
    else:
        r=insert(db,ApprovalCommodity,user['tenant'],profile_id=profile.id,commodity_code=body.commodity_code,evidence_id=body.evidence_id,
            data={**payload,'historical_evidence_status':'OWNER_REFERENCE_ATTACHMENT_PENDING','current_status':'REQUIRES_VERIFICATION','verification_required':True,'updated_at':now()})
        svc.event(db,user['tenant'],user['user'],'COMMODITY_ADDED',r.id,after=encode(r),reason=body.reason)
    db.commit();return encode(r)

@router.post('/approvals/products',status_code=201)
def product(body:SeriesInput,user=Depends(identity),db=Depends(db_session)):
    admin(user);svc.ensure_registry(db,user['tenant']);root=svc.entries(db,user['tenant'],ApprovalProfile)[0];db.refresh(root,with_for_update=True)
    old=next((r for r in svc.entries(db,user['tenant'],ProductSeries) if r.name.casefold()==body.name.casefold()),None)
    payload=body.model_dump(exclude={'name','expected_version','reason'})
    if old:
        if old.data['product_category']!=body.product_category and any(m.product_series_id==old.id for m in svc.entries(db,user['tenant'],ProductApprovalMapping)):raise HTTPException(422,'Mapped series category cannot be changed')
        if old.name=='Omega' and ('API 610' in body.design_standards or 'deviation' not in body.engineering_notes.casefold()):raise HTTPException(422,'Retain Omega API 610 deviation warning; full compliance cannot be published through reference metadata')
        revise(db,old,user,payload,body.reason,body.expected_version);r=old
    else:
        r=insert(db,ProductSeries,user['tenant'],name=body.name,data={**payload,'engineering_verification_status':'NOT_VERIFIED'})
        svc.event(db,user['tenant'],user['user'],'PRODUCT_REFERENCE_ADDED',r.id,after=encode(r),reason=body.reason)
    db.commit();return encode(r)

@router.post('/approvals/mappings',status_code=201)
def mapping(body:MappingInput,user=Depends(identity),db=Depends(db_session)):
    admin(user);s=svc.get(db,ProductSeries,body.product_series_id,user['tenant']);c=svc.get(db,ApprovalCommodity,body.commodity_id,user['tenant'])
    profile=svc.get(db,ApprovalProfile,c.profile_id,user['tenant'],True);svc.get(db,ApprovalEvidence,body.evidence_id,user['tenant'])
    if s.data['product_category']!=c.data['product_category']:raise HTTPException(422,'Product and commodity categories must match')
    old=db.scalar(select(ProductApprovalMapping).where(ProductApprovalMapping.tenant_id==user['tenant'],ProductApprovalMapping.product_series_id==s.id,ProductApprovalMapping.commodity_id==c.id))
    payload=dict(slide=body.slide,applicable_plant_id=profile.plant_id,engineering_notes=body.engineering_notes,mapping_verification_status='OWNER_REFERENCE_REQUIRES_VERIFICATION')
    if old:
        before=encode(old);revise(db,old,user,payload,body.reason,body.expected_version);old.evidence_id=body.evidence_id
        svc.event(db,user['tenant'],user['user'],'MAPPING_SOURCE_REVISED',old.id,before,encode(old),body.reason);r=old
    else:
        r=insert(db,ProductApprovalMapping,user['tenant'],product_series_id=s.id,commodity_id=c.id,profile_id=profile.id,evidence_id=body.evidence_id,data=payload)
        svc.event(db,user['tenant'],user['user'],'PRODUCT_MAPPING_ADDED',r.id,after=encode(r),reason=body.reason)
    db.commit();return encode(r)

@router.post('/approvals/commodities/{rid}/verifications',status_code=201)
def verification(rid:str,body:VerificationInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);require_permission(user,'approval_verification');c=svc.get(db,ApprovalCommodity,rid,user['tenant'],True)
    e=svc.get(db,ApprovalEvidence,body.evidence_id,user['tenant'])
    previous=[r for r in svc.entries(db,user['tenant'],ApprovalVerification) if r.commodity_id==rid]
    last=previous[-1] if previous else None
    if (last.id if last else None)!=body.supersedes_verification_id:raise HTTPException(409,'Supersede the latest verification explicitly; reload history')
    if last and body.verification_date.isoformat()<last.data['verification_date']:raise HTTPException(422,'A new current verification cannot predate the previous one')
    if body.status in ('VERIFIED','CONDITIONAL','REVOKED','SUSPENDED'):
        if not body.authorized_current_source:raise HTTPException(422,'This status requires an explicitly authorized current source')
        if e.data.get('source_type') not in ('CURRENT_CUSTOMER_SOURCE','SYNTHETIC_TEST'):raise HTTPException(422,'A historical letter or internal portfolio cannot establish current approval status')
        if not e.data.get('object_key'):raise HTTPException(422,'Attach source evidence; metadata alone cannot verify approval')
    # The only permitted attachment path is synthetic today. Recording a claimed
    # status is useful for testing/history but it never becomes live verification.
    effective=bool(not DEMO and e.data.get('authorized_current_source') and e.data.get('document_inspected') and not e.data.get('synthetic'))
    r=insert(db,ApprovalVerification,user['tenant'],commodity_id=rid,evidence_id=e.id,supersedes_verification_id=body.supersedes_verification_id,
        data={**body.model_dump(mode='json',exclude={'evidence_id','supersedes_verification_id'}),'reviewed_by':user['user'],
            'effective_authorized':effective,'evidence_hash':e.data.get('sha256'),'source_snapshot':svc.public_evidence(e),'mode':'LIVE_AUTHORIZED' if effective else 'UNVERIFIED_REVIEW_OR_SIMULATED_TEST'})
    svc.event(db,user['tenant'],user['user'],'VERIFICATION_RECORDED',r.id,after=encode(r),reason=body.reviewer_notes);db.commit();return encode(r)

@router.get('/approvals/history')
def history(user=Depends(identity),db=Depends(db_session)):
    from app.workflow.service import rows
    require_permission(user,'configuration');return [serialize(r) for r in rows(db,user['tenant'],'approval_event')]

@router.put('/approvals/policy')
def policy(body:PolicyInput,user=Depends(identity),db=Depends(db_session)):
    engineer(user);require_permission(user,'engineering_approval');svc.ensure_registry(db,user['tenant'])
    root=svc.entries(db,user['tenant'],ApprovalProfile)[0];db.refresh(root,with_for_update=True);r=svc.policy(db,user['tenant'])
    if r.data['policy_version']!=body.expected_version:raise HTTPException(409,'Reload the current evidence policy')
    p=add(db,'approval_policy',user['tenant'],**{**r.data,'policy_version':r.data['policy_version']+1,'unresolved_design_deviation':body.unresolved_design_deviation,'rationale':body.rationale,'actor':user['user']})
    svc.event(db,user['tenant'],user['user'],'EVIDENCE_POLICY_REVISED',p.id,before=r.data,after=p.data,reason=body.rationale);db.commit();return serialize(p)

@router.get('/projects/{pid}/approvals')
def rfq_approvals(pid:str,user=Depends(identity),db=Depends(db_session)):
    p=project(db,pid,user);result=svc.assessments(db,p);db.commit();return result

@router.put('/projects/{pid}/approvals/assignment')
def assignment(pid:str,body:AssignmentInput,user=Depends(identity),db=Depends(db_session)):
    from app.workflow.service import equipment
    engineer(user);p=project(db,pid,user,True);check_version(p,body.expected_version)
    if not svc.applicable(p):raise HTTPException(422,'Saudi Aramco approvals are not applicable to this customer')
    item=next((e for e in equipment(p) if e['tag']==body.tag),None)
    if not item:raise HTTPException(422,'Unknown equipment tag')
    if body.product_series_id:
        s=svc.get(db,ProductSeries,body.product_series_id,user['tenant'])
        if s.data['product_category']!=item['product_category']:raise HTTPException(422,'Choose a product series matching this equipment category')
    r=add(db,'approval_assignment',user['tenant'],pid,**body.model_dump(exclude={'expected_version'}),actor=user['user'])
    p.lock_version+=1;audit(db,user,pid,'APPROVAL_CANDIDATE_REVIEWED',r.id);db.commit();return serialize(r)
