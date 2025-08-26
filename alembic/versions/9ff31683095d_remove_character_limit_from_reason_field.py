"""Remove character limit from reason field in unified_versions table

Revision ID: 9ff31683095d
Revises: 0db81211808d
Create Date: 2025-08-26 17:54:17.305680

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9ff31683095d'
down_revision = '0db81211808d'
branch_labels = None
depends_on = None


def upgrade():
    # Alterar coluna reason de String(255) para Text
    op.alter_column('unified_versions', 'reason',
                    existing_type=sa.String(255),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade():
    # Reverter coluna reason de Text para String(255)
    op.alter_column('unified_versions', 'reason',
                    existing_type=sa.Text(),
                    type_=sa.String(255),
                    existing_nullable=True)
