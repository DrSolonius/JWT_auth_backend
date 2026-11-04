"""aprobacion de cuentas por un administrador

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0005'
down_revision: Union[str, Sequence[str], None] = '0004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'usuarios',
        sa.Column('es_admin', sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column('usuarios', 'es_admin', server_default=None)
    # Las cuentas existentes se crearon sin aprobación, incluido el admin con la
    # contraseña que estaba publicada en el repositorio: todas quedan por aprobar.
    # Al arrancar con ADMIN_PASSWORD, el administrador se reactiva con esa contraseña.
    op.execute("UPDATE usuarios SET activo = false")
    op.execute("UPDATE refresh_tokens SET revocado_en = now() WHERE revocado_en IS NULL")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('usuarios', 'es_admin')
