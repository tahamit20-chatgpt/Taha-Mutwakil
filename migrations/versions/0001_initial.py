"""Initial tenant-scoped domain store and durable document queue."""
from alembic import op
from app.db import Base
revision = '0001'
down_revision = None

def upgrade(): Base.metadata.create_all(op.get_bind())
def downgrade(): Base.metadata.drop_all(op.get_bind())
