import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine, String, Integer, JSON, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import DATABASE_URL

def uid(): return str(uuid.uuid4())
def now(): return datetime.now(timezone.utc).isoformat()
class Base(DeclarativeBase): pass
class Record(Base):
    """Tenant-scoped versioned domain records; immutable kinds are append-only through service API."""
    __tablename__ = 'records'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False)
    project_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    kind: Mapped[str] = mapped_column(String(40), index=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    lock_version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String(40), default=now)
    __table_args__ = (UniqueConstraint('tenant_id', 'id'), ForeignKeyConstraint(['tenant_id','project_id'], ['records.tenant_id','records.id']))
class Job(Base):
    __tablename__ = 'jobs'
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(String(36))
    project_id: Mapped[str] = mapped_column(String(36))
    document_id: Mapped[str] = mapped_column(String(36))
    state: Mapped[str] = mapped_column(String(30), default='QUEUED')
    key: Mapped[str] = mapped_column(String(128))
    attempt: Mapped[int] = mapped_column(Integer, default=0)
    lease_owner: Mapped[str | None] = mapped_column(String(36))
    lease_until: Mapped[float] = mapped_column(default=0.0)
    next_attempt: Mapped[float] = mapped_column(default=0.0)
    stage: Mapped[str] = mapped_column(String(40), default='QUARANTINED')
    error: Mapped[str | None] = mapped_column(String(500))
    __table_args__ = (UniqueConstraint('tenant_id','project_id','key'), ForeignKeyConstraint(['tenant_id','project_id'], ['records.tenant_id','records.id']), ForeignKeyConstraint(['tenant_id','document_id'], ['records.tenant_id','records.id']))
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(engine, expire_on_commit=False)

def add(db, kind, tenant, project=None, **data):
    row = Record(id=uid(), kind=kind, tenant_id=tenant, project_id=project, data=data)
    db.add(row)
    db.flush()
    return row

def serialize(r):
    return dict(id=r.id, tenant_id=r.tenant_id, project_id=r.project_id, kind=r.kind, lock_version=r.lock_version, created_at=r.created_at, **r.data)
