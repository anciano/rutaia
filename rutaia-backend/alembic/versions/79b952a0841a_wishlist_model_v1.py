"""wishlist_model_v1

Revision ID: 79b952a0841a
Revises: 7946bf565f6f
Create Date: 2026-03-01 00:12:12.883216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79b952a0841a'
down_revision: Union[str, Sequence[str], None] = '7946bf565f6f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Add plan_id as nullable initially
    op.add_column('plan_items', sa.Column('plan_id', sa.String(), nullable=True))
    
    # 2. Migrate data: Link plan_items to their parent plan via plan_days
    op.execute("""
        UPDATE plan_items
        SET plan_id = plan_days.plan_id
        FROM plan_days
        WHERE plan_items.day_id = plan_days.id
    """)
    
    # 3. Now make it non-nullable
    op.alter_column('plan_items', 'plan_id', nullable=False)
    
    # 4. Make day_id nullable (Wishlist support)
    op.alter_column('plan_items', 'day_id',
               existing_type=sa.UUID(),
               nullable=True)
    
    # 5. Add indices and FKs
    op.create_index('idx_plan_items_plan', 'plan_items', ['plan_id'], unique=False)
    op.create_foreign_key('fk_plan_items_plan_id', 'plan_items', 'user_plans', ['plan_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_plan_items_plan_id', 'plan_items', type_='foreignkey')
    op.drop_index('idx_plan_items_plan', table_name='plan_items')
    op.alter_column('plan_items', 'day_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.drop_column('plan_items', 'plan_id')
    # ### end Alembic commands ###
