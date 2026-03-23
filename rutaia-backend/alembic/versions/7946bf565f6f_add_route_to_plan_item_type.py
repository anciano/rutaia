"""add_route_to_plan_item_type

Revision ID: 7946bf565f6f
Revises: 0e1e46211e89
Create Date: 2026-02-28 16:55:26.921063

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7946bf565f6f'
down_revision: Union[str, Sequence[str], None] = '0e1e46211e89'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Postgres doesn't allow ALTER TYPE ... ADD VALUE inside a transaction block in older versions,
    # but in SQLAlchemy/Alembic we can use op.execute.
    # Note: This might fail if run in a multi-command transaction depending on PG version.
    op.execute("ALTER TYPE plan_item_type ADD VALUE 'route'")


def downgrade() -> None:
    """Downgrade schema."""
    # Removing a value from an enum is complex in Postgres. We'll leave it for now.
    pass
