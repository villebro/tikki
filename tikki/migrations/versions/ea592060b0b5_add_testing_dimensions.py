"""add testing dimensions

Revision ID: ea592060b0b5
Revises: d04f2ff5939b
Create Date: 2018-10-13 15:08:33.274605

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea592060b0b5'
down_revision = 'd04f2ff5939b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dim_military_status',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String, nullable=False))

    op.create_table('dim_gender',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String, nullable=False))

    op.create_table('dim_performance',
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String, nullable=False))

    op.create_table('dim_test_limit',
                    sa.Column('record_type_id', sa.Integer, primary_key=True),
                    sa.Column('military_status_id', sa.Integer, primary_key=True),
                    sa.Column('gender_id', sa.Integer, primary_key=True),
                    sa.Column('score', sa.Float, primary_key=True),
                    sa.Column('age_lower_limit', sa.Integer, primary_key=True),
                    sa.Column('age_upper_limit', sa.Integer, nullable=False),
                    sa.Column('lower_limit', sa.Float, nullable=False),
                    sa.Column('upper_limit', sa.Float, nullable=False),
                    sa.Column('performance_id', sa.Integer, nullable=False))


def downgrade():
    op.drop_table('dim_military_status')
    op.drop_table('dim_gender')
    op.drop_table('dim_performance')
    op.drop_table('dim_test_limit')
