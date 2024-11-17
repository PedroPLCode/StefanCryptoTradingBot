"""empty message

Revision ID: c7cf39b1d184
Revises: 6173c3355ec5
Create Date: 2024-11-17 20:47:41.978481

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7cf39b1d184'
down_revision = '6173c3355ec5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trades_history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trade_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('trades_history', schema=None) as batch_op:
        batch_op.drop_column('trade_id')

    # ### end Alembic commands ###
