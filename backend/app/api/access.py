from fastapi import HTTPException
from sqlalchemy import select
from app.db import Session, Record, add

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
    if run.data['snapshot'].get('registry_hash'):
        from app.workflow.service import registry_hash
        if registry_hash(db,p.tenant_id)!=run.data['snapshot']['registry_hash']:raise HTTPException(409,'Approved rule registry changed; reprocess RFQ')
    return p

