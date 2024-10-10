"""empty message

Revision ID: 4ae14b9d450b
Revises: 413e6a045163
Create Date: 2024-10-10 20:02:03.648251

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ae14b9d450b'
down_revision = '413e6a045163'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lookback_period', sa.String(length=16), nullable=True))
        batch_op.drop_column('lookback_days')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('lookback_days', sa.VARCHAR(length=16), nullable=True))
        batch_op.drop_column('lookback_period')

    # ### end Alembic commands ###