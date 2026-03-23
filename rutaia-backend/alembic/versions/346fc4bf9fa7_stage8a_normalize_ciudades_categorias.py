"""stage8a_normalize_ciudades_categorias

Revision ID: 346fc4bf9fa7
Revises: a6ac0426d58f
Create Date: 2026-02-17 23:30:46.925703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '346fc4bf9fa7'
down_revision: Union[str, Sequence[str], None] = 'a6ac0426d58f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Create categorias table
    op.create_table('categorias',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nombre', sa.String(), nullable=False),
        sa.Column('icono', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nombre')
    )

    # 2. Add pais column to ciudades (server_default to satisfy NOT NULL)
    op.add_column('ciudades', sa.Column('pais', sa.String(), nullable=False, server_default='Chile'))

    # 3. Make origen_id nullable temporarily so we can set it to NULL
    op.execute("ALTER TABLE user_plans ALTER COLUMN origen_id DROP NOT NULL")

    # 4. Nullify all FK columns pointing to ciudades.id before type change
    op.execute("UPDATE lugares SET ciudad_id = NULL")
    op.execute("UPDATE user_plans SET origen_id = NULL")
    op.execute("UPDATE actividades SET ciudad_id = NULL")

    # 5. Drop all FK constraints referencing ciudades.id
    op.drop_constraint('lugares_ciudad_id_fkey', 'lugares', type_='foreignkey')
    op.drop_constraint('user_plans_origen_id_fkey', 'user_plans', type_='foreignkey')
    op.drop_constraint('actividades_ciudad_id_fkey', 'actividades', type_='foreignkey')

    # 6. Drop unique constraint on ciudades.nombre
    op.execute("ALTER TABLE ciudades DROP CONSTRAINT IF EXISTS ciudades_nombre_key")

    # 7. Clear existing ciudades data (slugs can't become integers)
    op.execute("DELETE FROM ciudades")

    # 8. Change ciudades.id from VARCHAR to SERIAL (Integer)
    op.execute("ALTER TABLE ciudades ALTER COLUMN id DROP DEFAULT")
    op.execute("ALTER TABLE ciudades ALTER COLUMN id TYPE INTEGER USING 0")
    op.execute("CREATE SEQUENCE IF NOT EXISTS ciudades_id_seq")
    op.execute("ALTER TABLE ciudades ALTER COLUMN id SET DEFAULT nextval('ciudades_id_seq')")
    op.execute("SELECT setval('ciudades_id_seq', 1, false)")

    # 9. Change lugares.ciudad_id from VARCHAR to INTEGER
    op.execute("ALTER TABLE lugares ALTER COLUMN ciudad_id TYPE INTEGER USING NULL")

    # 10. Change actividades.ciudad_id from VARCHAR to INTEGER
    op.execute("ALTER TABLE actividades ALTER COLUMN ciudad_id TYPE INTEGER USING NULL")

    # 11. Change user_plans.origen_id from VARCHAR to INTEGER
    op.execute("ALTER TABLE user_plans ALTER COLUMN origen_id TYPE INTEGER USING NULL")

    # 12. Add categoria_id column to lugares
    op.add_column('lugares', sa.Column('categoria_id', sa.Integer(), nullable=True))

    # 13. Re-add FK constraints
    op.create_foreign_key('lugares_ciudad_id_fkey', 'lugares', 'ciudades', ['ciudad_id'], ['id'])
    op.create_foreign_key('user_plans_origen_id_fkey', 'user_plans', 'ciudades', ['origen_id'], ['id'])
    op.create_foreign_key('actividades_ciudad_id_fkey', 'actividades', 'ciudades', ['ciudad_id'], ['id'])
    op.create_foreign_key('lugares_categoria_id_fkey', 'lugares', 'categorias', ['categoria_id'], ['id'])

    # 14. Make ciudades.region nullable
    op.alter_column('ciudades', 'region', existing_type=sa.VARCHAR(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Simplified downgrade - not fully reversible due to data loss
    op.drop_constraint('lugares_categoria_id_fkey', 'lugares', type_='foreignkey')
    op.drop_column('lugares', 'categoria_id')
    op.drop_column('ciudades', 'pais')
    op.drop_table('categorias')
