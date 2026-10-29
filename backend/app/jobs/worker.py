import time, os, subprocess, sys, json, hashlib
from sqlalchemy import select, or_, and_
from app.db import Session, Record, Job, add, uid
from app.documents.storage import get,put
from app.extraction.service import parse, extract, normalize
from app.config import PROVIDER, DEMO
WORKER=uid()

def run_once():
    with Session.begin() as db:
        job=db.scalar(select(Job).where(or_(and_(Job.state=='QUEUED',Job.next_attempt<=time.time()),and_(Job.state=='RUNNING',Job.lease_until<time.time()))).order_by(Job.id).with_for_update(skip_locked=True).limit(1))
        if not job: return False
        if job.attempt>=3:
            job.state='FAILED';job.error='Retry limit after expired worker lease'
            doc=db.get(Record,job.document_id);doc.data={**doc.data,'state':'FAILED','gaps':[job.error]}
            return True
        job.state='RUNNING'; job.attempt+=1; job.lease_owner=WORKER; job.lease_until=time.time()+120; job.stage='PARSING'
        job_id=job.id; document=db.get(Record,job.document_id); data=document.data.copy()
    try:
        # Parser bounded by file/page limits; worker process is additionally resource limited by runner.
        body=get(data['object_key'])
        if data['filename'].lower().endswith('.zip'):
            expand_archive(job_id,body)
            return True
        parsed=subprocess.run([sys.executable,'-m','app.documents.parser',data['filename']],input=body,capture_output=True,timeout=30)
        if parsed.returncode: raise ValueError('Invalid signature, encrypted or malformed document; parser rejected upload')
        parsed_data=json.loads(parsed.stdout);pages=parsed_data['pages']
        with Session.begin() as heartbeat:
            leased=heartbeat.get(Job,job_id)
            if leased.lease_owner!=WORKER: return True
            leased.lease_until=time.time()+120;leased.stage='EXTRACTING'
        proposed=extract(pages,PROVIDER)
        with Session.begin() as db:
            job=db.scalar(select(Job).where(Job.id==job_id).with_for_update())
            if job.state!='RUNNING' or job.lease_owner!=WORKER: return True
            project=db.scalar(select(Record).where(Record.id==job.project_id).with_for_update())
            doc=db.get(Record,job.document_id)
            others=db.scalars(select(Record).where(Record.project_id==project.id,Record.kind=='document',Record.id!=doc.id)).all()
            if sum(d.data.get('page_count',0) for d in others)+len(pages)>500: raise ValueError('500 pages/project limit')
            tags=project.data['tags']; gaps=list(parsed_data.get('gaps',[]))
            for pi,text in enumerate(pages,1):
                add(db,'page',job.tenant_id,job.project_id,document_id=doc.id,index=pi,text=text,source_kind=parsed_data['kinds'][pi-1],worksheet=(parsed_data['locations'][pi-1][0].get('worksheet') if parsed_data['locations'][pi-1] else None),quality='TEXT' if text.strip() else 'UNREADABLE')
                if not text.strip(): gaps.append(f'Page {pi} unreadable; OCR unavailable')
            for p in proposed:
                if p.tag not in tags: gaps.append('Unassigned tag '+p.tag); continue
                value,unit,warnings=normalize(p.field,p.raw_value,p.raw_unit)
                locs=parsed_data['locations'][p.page-1]
                location=locs[p.line-1] if locs and p.line<=len(locs) else {}
                add(db,'fact',job.tenant_id,job.project_id,tag=p.tag,field=p.field,raw_value=p.raw_value,raw_unit=p.raw_unit,
                    normalized_value=value,normalized_unit=unit,warnings=warnings,status='PROPOSED',
                    method='DEMO_PATTERN_NOT_AI' if PROVIDER=='demo' else 'LLM_PROPOSAL_UNVERIFIED',
                    source=dict(document_version_id=doc.id,page=p.page if data['filename'].lower().endswith('.pdf') else None,
                        line_start=p.line,line_end=p.line,quote=p.quote,**location),parser_version='document-v2',extraction_version=PROVIDER+'-1')
            if not proposed: gaps.append('No supported requirements found; manual extraction required')
            doc.data={**doc.data,'state':'PARTIAL' if gaps else 'NEEDS_REVIEW','gaps':gaps,'page_count':len(pages),'provider':PROVIDER,
                'scan':'DEMO marker check only — no certified malware scanner' if DEMO else 'external-scanner-required'}
            project.lock_version+=1
            job.state='DONE';job.stage='NEEDS_REVIEW';job.lease_until=0
            add(db,'audit',job.tenant_id,job.project_id,action='DOCUMENT_PROCESSED',object_id=doc.id)
    except Exception as e:
        transient=not isinstance(e,(ValueError,UnicodeDecodeError))
        with Session.begin() as db:
            job=db.scalar(select(Job).where(Job.id==job_id).with_for_update())
            if job.lease_owner!=WORKER: return True
            job.state='QUEUED' if transient and job.attempt<3 else 'FAILED'
            job.error=str(e)[:400] if isinstance(e,ValueError) else type(e).__name__+': processing failed; inspect configuration'
            job.next_attempt=time.time()+2**job.attempt;job.lease_until=0
            doc=db.get(Record,job.document_id)
            doc.data={**doc.data,'state':job.state,'gaps':[job.error]}
    return True

def expand_archive(job_id,body):
    from app.documents.office import safe_entries
    try: entries=safe_entries(body,max_files=100)
    except Exception as exc:
        if isinstance(exc,ValueError):raise
        raise ValueError('Invalid or unsupported archive') from exc
    if not entries:raise ValueError('Empty archive')
    with Session.begin() as db:
        job=db.scalar(select(Job).where(Job.id==job_id).with_for_update())
        if job.lease_owner!=WORKER or job.state!='RUNNING':return
        p=db.scalar(select(Record).where(Record.id==job.project_id).with_for_update())
        existing=db.scalars(select(Record).where(Record.project_id==p.id,Record.kind=='document')).all()
        if len(existing)+len(entries)>20:raise ValueError('Archive would exceed 20 files/project; split the package')
        parent=db.get(Record,job.document_id);child_ids=[]
        for index,(name,body) in enumerate(entries.items()):
            supported=name.lower().endswith(('.txt','.pdf','.docx','.xlsx'))
            state='QUARANTINED' if supported else 'FAILED'
            gaps=[] if supported else ['Unsupported archive attachment; resolve coverage']
            if b'EICAR-STANDARD-ANTIVIRUS-TEST-FILE' in body:state='FAILED';gaps=['Malware test marker detected']
            key=p.tenant_id+'/'+p.id+'/'+uid();put(key,body)
            doc=add(db,'document',p.tenant_id,p.id,filename=name,object_key=key,sha256=hashlib.sha256(body).hexdigest(),state=state,gaps=gaps,page_count=0,classification='synthetic RFQ',version=1,revision_of=None,revision='',document_number='',category='Other Attachments',category_status='USER_CONFIRMATION_REQUIRED',parent_archive_id=parent.id,scan='DEMO marker check only')
            db.add(Job(id=uid(),tenant_id=p.tenant_id,project_id=p.id,document_id=doc.id,key=parent.id+':'+str(index),state='QUEUED' if state=='QUARANTINED' else 'FAILED',error=gaps[0] if gaps else None))
            child_ids.append(doc.id)
        parent.data={**parent.data,'state':'EXPANDED','is_archive':True,'children':child_ids,'gaps':[]}
        p.lock_version+=1;job.state='DONE';job.stage='ARCHIVE_EXPANDED';job.lease_until=0
        add(db,'audit',p.tenant_id,p.id,action='ARCHIVE_EXPANDED',object_id=parent.id)

if __name__=='__main__':
    while True:
        if not run_once(): time.sleep(.5)
