"""empty message

Revision ID: 39691c9a8487
Revises: a90db4a24faa
Create Date: 2024-11-02 21:28:08.614936

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39691c9a8487'
down_revision = 'a90db4a24faa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('backtest_settings', schema=None) as batch_op:
        batch_op.drop_column('symbol')
        batch_op.drop_column('interval')
        batch_op.drop_column('strategy')
        batch_op.drop_column('algorithm')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('backtest_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('algorithm', sa.INTEGER(), nullable=False))
        batch_op.add_column(sa.Column('strategy', sa.VARCHAR(length=16), nullable=False))
        batch_op.add_column(sa.Column('interval', sa.VARCHAR(length=16), nullable=False))
        batch_op.add_column(sa.Column('symbol', sa.VARCHAR(length=16), nullable=False))

    # ### end Alembic commands ###
