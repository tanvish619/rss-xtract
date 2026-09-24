"""add max_items to feed_configurations

Revision ID: a1b2c3d4e5f6
Revises: 516aae3f1db3
Create Date: 2026-09-24 13:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '516aae3f1db3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'feed_configurations',
        sa.Column(
            'max_items',
            sa.Integer(),
            nullable=True
        )
    )


def downgrade() -> None:
    op.drop_column('feed_configurations', 'max_items')
