"""Add LangGraph memory tables

Revision ID: langgraph_memory_tables
Revises: 0db81211808d
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'langgraph_memory_tables'
down_revision = '0db81211808d'
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension if not already enabled
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create langgraph_memory_short_term table
    op.create_table('langgraph_memory_short_term',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('content_raw', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False, server_default='history'),
        sa.Column('embedding', sa.dialects.postgresql.VECTOR(768), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_user_session', 'langgraph_memory_short_term', ['user_id', 'session_id'])
    op.create_index('idx_created_at', 'langgraph_memory_short_term', ['created_at'])
    op.create_index('idx_embedding_hnsw', 'langgraph_memory_short_term', ['embedding'], 
                   postgresql_using='hnsw')
    
    # Create memory_retrieval_logs table
    op.create_table('memory_retrieval_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('query_text', sa.Text(), nullable=False),
        sa.Column('retrieved_memories', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for logs table
    op.create_index('idx_user_session_log', 'memory_retrieval_logs', ['user_id', 'session_id'])
    op.create_index('idx_created_at_log', 'memory_retrieval_logs', ['created_at'])


def downgrade():
    # Drop tables in reverse order
    op.drop_table('memory_retrieval_logs')
    op.drop_table('langgraph_memory_short_term') 