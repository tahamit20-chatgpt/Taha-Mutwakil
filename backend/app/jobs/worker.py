import time, os, subprocess, sys, json
from sqlalchemy import select, or_, and_
from app.db import Session, Record, Job, add, uid
from app.documents.storage import get
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
        parsed=subprocess.run([sys.executable,'-m','app.documents.parser',data['filename']],input=body,capture_output=True,timeout=30)
        if parsed.returncode: raise ValueError('Invalid signature, encrypted or malformed document; parser rejected upload')
        pages=json.loads(parsed.stdout)['pages']
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
            tags=project.data['tags']; gaps=[]
            for pi,text in enumerate(pages,1):
                add(db,'page',job.tenant_id,job.project_id,document_id=doc.id,index=pi,text=text,quality='TEXT' if text.strip() else 'UNREADABLE')
                if not text.strip(): gaps.append(f'Page {pi} unreadable; OCR unavailable')
            for p in proposed:
                if p.tag not in tags: gaps.append('Unassigned tag '+p.tag); continue
                value,unit,warnings=normalize(p.field,p.raw_value,p.raw_unit)
                add(db,'fact',job.tenant_id,job.project_id,tag=p.tag,field=p.field,raw_value=p.raw_value,raw_unit=p.raw_unit,
                    normalized_value=value,normalized_unit=unit,warnings=warnings,status='PROPOSED',
                    method='DEMO_PATTERN_NOT_AI' if PROVIDER=='demo' else 'LLM_PROPOSAL_UNVERIFIED',
                    source=dict(document_version_id=doc.id,page=p.page if data['filename'].lower().endswith('.pdf') else None,
                        line_start=p.line,line_end=p.line,quote=p.quote),parser_version='pypdf-5.6/text-1',extraction_version=PROVIDER+'-1')
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

if __name__=='__main__':
    while True:
        if not run_once(): time.sleep(.5)
