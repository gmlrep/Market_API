"""Rename create_at -> created_at and add timestamps to all tables.

Revision ID: timestamps_basemodel
Revises: create_user_table
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "timestamps_basemodel"
down_revision: Union[str, None] = "04193d6abe9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLES_WITHOUT_TIMESTAMPS = (
    "sellers",
    "admins",
    "category",
    "company",
    "orders",
    "products",
    "parameters",
    "photos",
    "photo_review",
    "contacts",
)


def upgrade() -> None:
    # Rename legacy create_at columns
    with op.batch_alter_table("users") as batch:
        batch.alter_column("create_at", new_column_name="created_at")
        batch.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=True,
            )
        )
    with op.batch_alter_table("reviews") as batch:
        batch.alter_column("create_at", new_column_name="created_at")
        batch.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                nullable=True,
            )
        )

    for table in TABLES_WITHOUT_TIMESTAMPS:
        with op.batch_alter_table(table) as batch:
            batch.add_column(
                sa.Column(
                    "created_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=True,
                )
            )
            batch.add_column(
                sa.Column(
                    "updated_at",
                    sa.DateTime(timezone=True),
                    server_default=sa.func.now(),
                    nullable=True,
                )
            )


def downgrade() -> None:
    for table in TABLES_WITHOUT_TIMESTAMPS:
        with op.batch_alter_table(table) as batch:
            batch.drop_column("updated_at")
            batch.drop_column("created_at")

    with op.batch_alter_table("reviews") as batch:
        batch.drop_column("updated_at")
        batch.alter_column("created_at", new_column_name="create_at")
    with op.batch_alter_table("users") as batch:
        batch.drop_column("updated_at")
        batch.alter_column("created_at", new_column_name="create_at")
