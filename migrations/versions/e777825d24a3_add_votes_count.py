"""Add votes count

Revision ID: e777825d24a3
Revises: 0cc25e3e3169
Create Date: 2023-12-01 17:32:48.464491

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e777825d24a3"
down_revision: Union[str, None] = "0cc25e3e3169"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "options", sa.Column("votes_count", sa.Integer(), default=0, nullable=False)
    )


def downgrade() -> None:
    op.drop_column("options", "votes_count")
