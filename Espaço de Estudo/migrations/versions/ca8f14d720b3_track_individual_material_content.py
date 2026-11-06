"""Track completion for individual study material contents.

Revision ID: ca8f14d720b3
Revises: 79d5bd809cb8
"""
from alembic import op
import sqlalchemy as sa


revision = "ca8f14d720b3"
down_revision = "79d5bd809cb8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("study_material", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("content_completed", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
        batch_op.add_column(
            sa.Column("pdf_completed", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
        batch_op.add_column(
            sa.Column("video_completed", sa.Boolean(), server_default=sa.false(), nullable=False)
        )
    with op.batch_alter_table("study_material_resource", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("completed", sa.Boolean(), server_default=sa.false(), nullable=False)
        )

    op.execute(
        sa.text(
            "UPDATE study_material SET content_completed = completed "
            "WHERE TRIM(content) <> ''"
        )
    )
    op.execute(
        sa.text(
            "UPDATE study_material SET pdf_completed = completed "
            "WHERE pdf_storage_name IS NOT NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE study_material SET video_completed = completed "
            "WHERE video_url IS NOT NULL"
        )
    )
    op.execute(
        sa.text(
            "UPDATE study_material_resource SET completed = "
            "(SELECT completed FROM study_material "
            "WHERE study_material.id = study_material_resource.study_material_id)"
        )
    )


def downgrade():
    with op.batch_alter_table("study_material_resource", schema=None) as batch_op:
        batch_op.drop_column("completed")
    with op.batch_alter_table("study_material", schema=None) as batch_op:
        batch_op.drop_column("video_completed")
        batch_op.drop_column("pdf_completed")
        batch_op.drop_column("content_completed")
