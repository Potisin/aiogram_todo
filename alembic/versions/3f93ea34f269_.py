"""empty message

Revision ID: 3f93ea34f269
Revises: 
Create Date: 2023-08-23 15:16:37.653291

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f93ea34f269'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tg_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
    op.create_table('catalog',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('user_tg_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_tg_id'], ['user.tg_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('deadline', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('catalog_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['catalog_id'], ['catalog.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    op.drop_table('catalog')
    op.drop_table('user')
    # ### end Alembic commands ###
