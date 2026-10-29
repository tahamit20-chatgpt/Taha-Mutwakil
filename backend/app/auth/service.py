import os, secrets, hashlib, ipaddress
from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, Request
from sqlalchemy import select
from app.db import Record, add, Session
from app.config import DEMO
DEMO_USERS={
 'alice':dict(user='alice',tenant='demo-tenant-a',role='Engineer',permissions=['configuration','engineering_approval','approval_verification']),
 'bob':dict(user='bob',tenant='demo-tenant-a',role='Engineer'),
 'viewer':dict(user='viewer',tenant='demo-tenant-a',role='Viewer'),
 'outsider':dict(user='outsider',tenant='demo-tenant-b',role='Engineer')}

def hashed(value): return hashlib.sha256(value.encode()).hexdigest()
def issue(db, identity, response):
    token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(32)
    row=add(db,'session',identity['tenant'],token_hash=hashed(token),identity=identity,csrf=csrf,
        expires=(datetime.now(timezone.utc)+timedelta(hours=8)).isoformat())
    db.commit()
    response.set_cookie('bidfit_session',token,httponly=True,samesite='strict',secure=not DEMO,max_age=28800)
    return dict(**identity,csrf=csrf,demo=DEMO)

def identity(request: Request):
    token=request.cookies.get('bidfit_session','')
    with Session() as db:
        row=db.scalar(select(Record).where(Record.kind=='session',Record.data['token_hash'].as_string()==hashed(token)))
        if not row or datetime.fromisoformat(row.data['expires'])<datetime.now(timezone.utc): raise HTTPException(401,'Sign in required')
        if request.method not in ('GET','HEAD','OPTIONS') and not secrets.compare_digest(request.headers.get('X-CSRF-Token',''),row.data['csrf']):
            raise HTTPException(403,'CSRF token required')
        return dict(**row.data['identity'],csrf=row.data['csrf'],session_id=row.id,demo=DEMO)

def engineer(user):
    if user['role']!='Engineer': raise HTTPException(403,'Engineer role required')


def local_demo_client(host):
    """Local profile only: private Docker bridge peers when explicitly enabled.

    The Docker Compose profile publishes API only on host loopback. This is not
    a production authentication mechanism. Header-supplied IPs are not consulted.
    """
    if host in ('127.0.0.1','::1','testclient'): return True
    if not DEMO: return False
    try:
        peer=ipaddress.ip_address(host)
        return any(peer in ipaddress.ip_network(c.strip()) for c in os.getenv('BIDFIT_DEMO_NETWORKS','').split(',') if c.strip())
    except ValueError: return False


def require_permission(user, permission):
    if permission not in user.get("permissions",[]): raise HTTPException(403,"Designated "+permission+" permission required")
