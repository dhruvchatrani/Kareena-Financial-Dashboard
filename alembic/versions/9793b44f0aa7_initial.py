"""initial

Revision ID: 9793b44f0aa7
Revises: 
Create Date: 2026-05-30 00:41:22.576340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9793b44f0aa7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite does not support ALTER COLUMN; batch mode recreates tables safely.
    # Create all tables that may not exist yet (safe for fresh and existing DBs).
    import models
    from sqlalchemy import MetaData

    bind = op.get_bind()
    meta = MetaData()
    meta.reflect(bind=bind)

    for table in models.Base.metadata.sorted_tables:
        if table.name not in meta.tables:
            table.create(bind=bind)

    # The original auto-generated alter_column (TEXT -> String) is a no-op in
    # SQLite since both types map to TEXT. New tables are created with the
    # correct String type above, so the alter is unnecessary.


def downgrade() -> None:
    # Drop all application tables.
    import models
    bind = op.get_bind()
    for table in reversed(models.Base.metadata.sorted_tables):
        if bind.dialect.has_table(bind, table.name):
            table.drop(bind=bind)
