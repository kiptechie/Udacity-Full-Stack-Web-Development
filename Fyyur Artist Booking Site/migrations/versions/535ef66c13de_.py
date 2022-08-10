"""empty message

Revision ID: 535ef66c13de
Revises: 1aaf5c4dff1d
Create Date: 2022-08-11 00:42:30.825359

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '535ef66c13de'
down_revision = '1aaf5c4dff1d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('num_upcoming_shows', sa.Integer(), nullable=False))
    op.add_column('Show', sa.Column('name', sa.String(length=120), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'name')
    op.drop_column('Show', 'num_upcoming_shows')
    # ### end Alembic commands ###