"""Relational approval identities and associations over the existing domain store.

Metadata is extensible JSON, but identity, uniqueness and all associations are
tenant-scoped relational keys. Revisions are retained in immutable events and
verification records; evaluations embed their exact input snapshot.
"""
from sqlalchemy import String, Integer, JSON, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base, uid, now

class Entity:
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uid)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[str] = mapped_column(String(40), default=now)

class ApprovalProfile(Entity, Base):
    __tablename__='approval_profiles'
    customer_key: Mapped[str] = mapped_column(String(100))
    vendor_code: Mapped[str] = mapped_column(String(40))
    plant_id: Mapped[str] = mapped_column(String(40))
    __table_args__=(UniqueConstraint('tenant_id','id'),UniqueConstraint('tenant_id','customer_key','vendor_code','plant_id'))

class ApprovalEvidence(Entity, Base):
    __tablename__='approval_evidence'
    __table_args__=(UniqueConstraint('tenant_id','id'),)

class ApprovalCommodity(Entity, Base):
    __tablename__='approval_commodities'
    profile_id: Mapped[str] = mapped_column(String(36))
    commodity_code: Mapped[str] = mapped_column(String(10))
    evidence_id: Mapped[str] = mapped_column(String(36))
    __table_args__=(UniqueConstraint('tenant_id','id'),UniqueConstraint('tenant_id','profile_id','commodity_code'),
        ForeignKeyConstraint(['tenant_id','profile_id'],['approval_profiles.tenant_id','approval_profiles.id']),
        ForeignKeyConstraint(['tenant_id','evidence_id'],['approval_evidence.tenant_id','approval_evidence.id']))

class ProductSeries(Entity, Base):
    __tablename__='approval_product_series'
    name: Mapped[str] = mapped_column(String(100))
    __table_args__=(UniqueConstraint('tenant_id','id'),UniqueConstraint('tenant_id','name'))

class ProductApprovalMapping(Entity, Base):
    __tablename__='approval_product_mappings'
    product_series_id: Mapped[str] = mapped_column(String(36))
    commodity_id: Mapped[str] = mapped_column(String(36))
    profile_id: Mapped[str] = mapped_column(String(36))
    evidence_id: Mapped[str] = mapped_column(String(36))
    __table_args__=(UniqueConstraint('tenant_id','id'),UniqueConstraint('tenant_id','product_series_id','commodity_id'),
        ForeignKeyConstraint(['tenant_id','product_series_id'],['approval_product_series.tenant_id','approval_product_series.id']),
        ForeignKeyConstraint(['tenant_id','commodity_id'],['approval_commodities.tenant_id','approval_commodities.id']),
        ForeignKeyConstraint(['tenant_id','profile_id'],['approval_profiles.tenant_id','approval_profiles.id']),
        ForeignKeyConstraint(['tenant_id','evidence_id'],['approval_evidence.tenant_id','approval_evidence.id']))

class ApprovalVerification(Entity, Base):
    __tablename__='approval_verifications'
    commodity_id: Mapped[str] = mapped_column(String(36))
    evidence_id: Mapped[str] = mapped_column(String(36))
    supersedes_verification_id: Mapped[str | None] = mapped_column(String(36),nullable=True)
    __table_args__=(UniqueConstraint('tenant_id','id'),
        ForeignKeyConstraint(['tenant_id','commodity_id'],['approval_commodities.tenant_id','approval_commodities.id']),
        ForeignKeyConstraint(['tenant_id','evidence_id'],['approval_evidence.tenant_id','approval_evidence.id']),
        ForeignKeyConstraint(['tenant_id','supersedes_verification_id'],['approval_verifications.tenant_id','approval_verifications.id']))

TABLES=[ApprovalProfile,ApprovalEvidence,ApprovalCommodity,ProductSeries,ProductApprovalMapping,ApprovalVerification]

def encode(row):
    return {**row.data,**{col.name:getattr(row,col.name) for col in row.__table__.columns if col.name!='data'}}

def insert(db,model,tenant,**kw):
    r=model(id=uid(),tenant_id=tenant,version=1,**kw);db.add(r);db.flush();return r
