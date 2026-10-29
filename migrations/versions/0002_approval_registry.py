"""Add tenant-scoped approval identities, evidence and many-to-many mappings.

No existing domain table or RFQ is changed. Data are imported idempotently by
the approval service on first authorized lookup, not by destructive migration.
"""
from alembic import op
from app.approvals.store import TABLES
revision='0002'
down_revision='0001'

def upgrade():
    for model in TABLES:model.__table__.create(op.get_bind(),checkfirst=True)

def downgrade():
    for model in reversed(TABLES):model.__table__.drop(op.get_bind(),checkfirst=True)
