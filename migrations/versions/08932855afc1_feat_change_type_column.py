"""feat: change type column

Revision ID: 08932855afc1
Revises: 6b104aaf80a3
Create Date: 2026-09-21 15:22:48.276315

"""

from collections.abc import Sequence

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "08932855afc1"
down_revision: str | Sequence[str] | None = "6b104aaf80a3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "tariffs",
        "external_squad_uuid",
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="external_squad_uuid[1]",
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "tariffs",
        "external_squad_uuid",
        type_=postgresql.ARRAY(postgresql.UUID(as_uuid=True)),
        postgresql_using="ARRAY[external_squad_uuid]",
        existing_nullable=True,
    )
