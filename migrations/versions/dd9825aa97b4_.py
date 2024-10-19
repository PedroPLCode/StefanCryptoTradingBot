"""empty message

Revision ID: dd9825aa97b4
Revises: 18f1c4dea986
Create Date: 2024-10-19 22:45:47.490200

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd9825aa97b4'
down_revision = '18f1c4dea986'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cci_buy', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('cci_sell', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rsi_buy', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rsi_sell', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('mfi_buy', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('mfi_sell', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('signals_extended', sa.Boolean(), nullable=True))
        batch_op.drop_column('sell_signal_extended')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sell_signal_extended', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('signals_extended')
        batch_op.drop_column('mfi_sell')
        batch_op.drop_column('mfi_buy')
        batch_op.drop_column('rsi_sell')
        batch_op.drop_column('rsi_buy')
        batch_op.drop_column('cci_sell')
        batch_op.drop_column('cci_buy')

    # ### end Alembic commands ###
