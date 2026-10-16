"""Lightweight SQLite column/table upgrades for the local demo (not a migration framework)."""
from sqlalchemy import inspect, text
from app.database import engine


def ensure_demo_schema() -> None:
    """Add columns introduced after v0.3 when the existing SQLite file is reused."""
    if engine.dialect.name != 'sqlite':
        return
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    with engine.begin() as conn:
        if 'organization_setups' in tables:
            cols = {c['name'] for c in inspector.get_columns('organization_setups')}
            if 'version' not in cols:
                conn.execute(text('ALTER TABLE organization_setups ADD COLUMN version INTEGER DEFAULT 1'))
        # New submission table is created by metadata.create_all.
