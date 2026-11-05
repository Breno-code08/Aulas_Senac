"""Add written study material content

Revision ID: bf8bdef191b0
Revises: b0b83654c4af
Create Date: 2026-11-03 21:19:57.069080

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bf8bdef191b0'
down_revision = 'b0b83654c4af'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "study_material",
        sa.Column("content", sa.Text(), nullable=True),
    )
    op.execute(
        sa.text("UPDATE study_material SET content = '' WHERE content IS NULL")
    )
    op.alter_column(
        "study_material",
        "content",
        existing_type=sa.Text(),
        nullable=False,
    )


def downgrade():
    op.drop_column("study_material", "content")
