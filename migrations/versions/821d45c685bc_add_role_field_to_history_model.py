"""Add role field to History model

Revision ID: 821d45c685bc
Revises: 7370b9a98c6c
Create Date: 2024-11-13 16:19:28.991373

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '821d45c685bc'
down_revision = '7370b9a98c6c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.add_column(sa.Column('response', sa.Text(), nullable=True))
        batch_op.alter_column('role',
               existing_type=sa.VARCHAR(length=50),
               type_=sa.String(length=20),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('history', schema=None) as batch_op:
        batch_op.alter_column('role',
               existing_type=sa.String(length=20),
               type_=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.drop_column('response')

    # ### end Alembic commands ###
