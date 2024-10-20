"""empty message

Revision ID: adfb3032cc7a
Revises: dd9825aa97b4
Create Date: 2024-10-19 23:01:25.687419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adfb3032cc7a'
down_revision = 'dd9825aa97b4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('timeperiod', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bot_settings', schema=None) as batch_op:
        batch_op.drop_column('timeperiod')

    # ### end Alembic commands ###