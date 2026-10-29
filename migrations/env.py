from alembic import context
from app.db import Base, engine
from app.approvals import store  # Register additive approval tables for metadata.
with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction(): context.run_migrations()
