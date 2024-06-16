"""from_copyright_video_id field

Revision ID: 2e68bb962c0c
Revises: 4b23f1912e9c
Create Date: 2024-06-16 17:05:30.428763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e68bb962c0c'
down_revision: Union[str, None] = '4b23f1912e9c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('copyright_video_parts', sa.Column('from_copyright_video_id', sa.Uuid(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('copyright_video_parts', 'from_copyright_video_id')
    # ### end Alembic commands ###