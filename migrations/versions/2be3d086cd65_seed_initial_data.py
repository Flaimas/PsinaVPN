"""seed_initial_data

Revision ID: 2be3d086cd65
Revises: 927a72f961df
Create Date: 2026-09-07 23:29:59.743759

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2be3d086cd65"
down_revision: str | Sequence[str] | None = "927a72f961df"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    plans_table = sa.table(
        "tariffs",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("price", sa.Integer),
        sa.column("category", sa.String(20)),
        sa.column("traffic_limit", sa.BigInteger),
        sa.column("is_active", sa.Boolean),
        sa.column("squad_uuids", postgresql.ARRAY(postgresql.UUID)),
        sa.column("device_limit", sa.Integer),
    )

    # Вставляем данные
    op.bulk_insert(
        plans_table,
        [
            {
                "id": 1,
                "name": "Щенок",
                "price": 150,
                "category": "default",
                "traffic_limit": 0,
                "is_active": True,
                "squad_uuids": ["5007c8a9-5395-4bcd-b967-81ef82986b0c"],
                "device_limit": 5,
            },
            {
                "id": 2,
                "name": "Дворняга",
                "price": 150,
                "category": "whitelist",
                "traffic_limit": 50,
                "is_active": True,
                "squad_uuids": ["24801ddd-3db3-4126-a9d3-886edf74414a"],
                "device_limit": 5,
            },
            {
                "id": 3,
                "name": "Псина",
                "price": 150,
                "category": "whitelist",
                "traffic_limit": 75,
                "is_active": True,
                "squad_uuids": ["24801ddd-3db3-4126-a9d3-886edf74414a"],
                "device_limit": 10,
            },
        ],
    )


def downgrade() -> None:
    # При откате миграции чистим эти записи
    op.execute("DELETE FROM plans WHERE id IN (1, 2, 3)")
