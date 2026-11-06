"""Add users and private study spaces

Revision ID: d9269380be8c
Revises: 8e9b0a2e0a06
Create Date: 2026-11-04 19:01:02.692634

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9269380be8c'
down_revision = '8e9b0a2e0a06'
branch_labels = None
depends_on = None


def upgrade():
    existing_spaces = op.get_bind().execute(
        sa.text("SELECT COUNT(*) FROM study_space")
    ).scalar_one()
    if existing_spaces:
        raise RuntimeError(
            "Cannot add private study spaces: study_space contains records without an owner. "
            "Assign each existing space to a user before applying this migration."
        )

    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=254), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)

    op.add_column('study_space', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_study_space_owner_id'), 'study_space', ['owner_id'], unique=False)
    op.create_foreign_key(
        'fk_study_space_owner_id_user',
        'study_space',
        'user',
        ['owner_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade():
    op.drop_constraint('fk_study_space_owner_id_user', 'study_space', type_='foreignkey')
    op.drop_index(op.f('ix_study_space_owner_id'), table_name='study_space')
    op.drop_column('study_space', 'owner_id')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
