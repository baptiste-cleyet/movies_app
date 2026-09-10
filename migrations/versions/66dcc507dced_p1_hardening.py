"""p1 hardening

Revision ID: 66dcc507dced
Revises: a109d0ae1db1
Create Date: 2026-09-10 13:36:16.160247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66dcc507dced'
down_revision = 'a109d0ae1db1'
branch_labels = None
depends_on = None


def upgrade():
    # ### P1 hardening: new check constraints and watchlist year nullable ###
    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.create_check_constraint("ck_movies_year", "year IS NULL OR (year >= 1888 AND year <= 2100)")
        batch_op.create_check_constraint("ck_movies_avg_rating", "average_rating IS NULL OR (average_rating >= 0 AND average_rating <= 100)")

    with op.batch_alter_table('watchlist', schema=None) as batch_op:
        batch_op.alter_column('year',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.create_check_constraint("ck_watchlist_rating", "rating >= 0 AND rating <= 100")
        batch_op.create_check_constraint("ck_watchlist_year", "year IS NULL OR (year >= 1888 AND year <= 2100)")

    # ### end Alembic commands ###


def downgrade():
    # ### downgrade P1 hardening ###
    with op.batch_alter_table('watchlist', schema=None) as batch_op:
        batch_op.drop_constraint("ck_watchlist_year", type_="check")
        batch_op.drop_constraint("ck_watchlist_rating", type_="check")
        batch_op.alter_column('year',
               existing_type=sa.INTEGER(),
               nullable=False)

    with op.batch_alter_table('movies', schema=None) as batch_op:
        batch_op.drop_constraint("ck_movies_avg_rating", type_="check")
        batch_op.drop_constraint("ck_movies_year", type_="check")

    # ### end Alembic commands ###
