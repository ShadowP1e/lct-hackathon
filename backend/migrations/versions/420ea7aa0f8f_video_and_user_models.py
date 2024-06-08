"""video and user models

Revision ID: 420ea7aa0f8f
Revises: 
Create Date: 2024-06-06 11:12:07.951276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '420ea7aa0f8f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('copyright_videos',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('filename', sa.String(length=250), nullable=True),
    sa.Column('user_ip', sa.String(length=60), nullable=True),
    sa.Column('url', sa.String(length=250), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('finished', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=False),
    sa.Column('password_updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('videos',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('filename', sa.String(length=250), nullable=True),
    sa.Column('user_ip', sa.String(length=60), nullable=True),
    sa.Column('url', sa.String(length=250), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('finished', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('copyright_video_parts',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('video_id', sa.Uuid(), nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('start', sa.Integer(), nullable=False),
    sa.Column('end', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('copyright_video_parts')
    op.drop_table('videos')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('copyright_videos')
    # ### end Alembic commands ###