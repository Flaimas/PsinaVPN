"""update_initial_tariffs_data

Revision ID: e990c7daad86
Revises: 54663b08e3a2
Create Date: 2026-09-28 01:45:31.212264

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e990c7daad86"
down_revision: str | Sequence[str] | None = "54663b08e3a2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    plans_table = sa.table(
        "tariffs",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("category", sa.String(20)),
        sa.column("is_promo", sa.Boolean),
        sa.column("traffic_limit", sa.BigInteger),
        sa.column("is_active", sa.Boolean),
        sa.column("internal_squad_uuids", postgresql.ARRAY(postgresql.UUID)),
        sa.column("external_squad_uuid", postgresql.UUID),
        sa.column("device_limit", sa.Integer),
    )
    op.bulk_insert(
        plans_table,
        [
            {
                "id": 4,
                "name": "Тест",
                "category": "whitelist",
                "traffic_limit": 5,
                "is_active": True,
                "internal_squad_uuids": ["62a69885-9c7f-4b37-a976-627d9f0eae9d"],
                "external_squad_uuid": None,
                "is_promo": True,
                "device_limit": 1,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM tariffs WHERE name = 'Тест';")
