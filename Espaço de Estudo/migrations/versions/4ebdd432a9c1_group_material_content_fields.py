"""Group descriptions, PDFs, and links into editable contents.

Revision ID: 4ebdd432a9c1
Revises: ca8f14d720b3
"""
from alembic import op
import sqlalchemy as sa


revision = "4ebdd432a9c1"
down_revision = "ca8f14d720b3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        sa.text(
            "INSERT INTO study_material_resource "
            "(study_material_id, kind, content, video_url, pdf_filename, "
            "pdf_storage_name, completed) "
            "SELECT id, 'content', NULLIF(TRIM(content), ''), "
            "NULLIF(TRIM(video_url), ''), pdf_filename, pdf_storage_name, "
            "CASE WHEN "
            "(NULLIF(TRIM(content), '') IS NULL OR content_completed = 1) "
            "AND (pdf_storage_name IS NULL OR pdf_completed = 1) "
            "AND (NULLIF(TRIM(video_url), '') IS NULL OR video_completed = 1) "
            "THEN 1 ELSE 0 END "
            "FROM study_material "
            "WHERE NULLIF(TRIM(content), '') IS NOT NULL "
            "OR pdf_storage_name IS NOT NULL "
            "OR NULLIF(TRIM(video_url), '') IS NOT NULL"
        )
    )
    op.execute(
        sa.text("UPDATE study_material_resource SET kind = 'content' WHERE kind <> 'content'")
    )
    op.execute(
        sa.text(
            "UPDATE study_material SET completed = CASE "
            "WHEN EXISTS (SELECT 1 FROM study_material_resource "
            "WHERE study_material_resource.study_material_id = study_material.id) "
            "AND NOT EXISTS (SELECT 1 FROM study_material_resource "
            "WHERE study_material_resource.study_material_id = study_material.id "
            "AND study_material_resource.completed = 0) "
            "THEN 1 ELSE 0 END"
        )
    )


def downgrade():
    raise RuntimeError(
        "Esta migração agrupa os campos dos conteúdos e não pode ser revertida sem perda de dados."
    )
