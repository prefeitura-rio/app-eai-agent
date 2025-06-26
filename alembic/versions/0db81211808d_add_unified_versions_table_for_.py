"""Add unified versions table for centralized versioning

Revision ID: 0db81211808d
Revises: 
Create Date: 2025-06-26 17:21:26.544832

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0db81211808d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Criar tabela unified_versions
    op.create_table(
        'unified_versions',
        sa.Column('version_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('agent_type', sa.String(50), nullable=False, index=True),
        sa.Column('version_number', sa.Integer, nullable=False, index=True),
        sa.Column('change_type', sa.String(20), nullable=False),
        
        # IDs das entidades relacionadas
        sa.Column('prompt_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('config_id', postgresql.UUID(as_uuid=True), nullable=True),
        
        # Metadados da versão
        sa.Column('author', sa.String(100), nullable=True),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        
        # Controle temporal
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.current_timestamp()),
        
        # Metadados adicionais em JSON
        sa.Column('version_metadata', postgresql.JSONB, nullable=True, server_default='{}'),
    )
    
    # Criar índices
    op.create_index('idx_unified_versions_agent_type', 'unified_versions', ['agent_type'])
    op.create_index('idx_unified_versions_version_number', 'unified_versions', ['version_number'])
    op.create_index('idx_unified_versions_created_at', 'unified_versions', ['created_at'])
    
    # Criar constraint unique para agent_type + version_number
    op.create_unique_constraint('uix_agent_type_version', 'unified_versions', ['agent_type', 'version_number'])
    
    # Criar constraint check para change_type
    op.create_check_constraint(
        'check_change_type',
        'unified_versions',
        "change_type IN ('prompt', 'config', 'both')"
    )


def downgrade():
    # Remover constraints
    op.drop_constraint('check_change_type', 'unified_versions')
    op.drop_constraint('uix_agent_type_version', 'unified_versions')
    
    # Remover índices
    op.drop_index('idx_unified_versions_created_at', 'unified_versions')
    op.drop_index('idx_unified_versions_version_number', 'unified_versions')
    op.drop_index('idx_unified_versions_agent_type', 'unified_versions')
    
    # Remover tabela
    op.drop_table('unified_versions') 