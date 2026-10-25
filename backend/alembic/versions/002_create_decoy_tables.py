"""Create decoy asset and event tables for PS 03 blockchain-verified deception

Revision ID: 002
Revises: 001
Create Date: 2026-10-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create decoy_assets table
    op.create_table('decoy_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('decoy_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('endpoint_location', sa.String(), nullable=False),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('interaction_count', sa.Integer(), nullable=False),
        sa.Column('last_interaction_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decoy_assets_name'), 'decoy_assets', ['name'], unique=True)
    op.create_index(op.f('ix_decoy_assets_decoy_type'), 'decoy_assets', ['decoy_type'], unique=False)
    op.create_index(op.f('ix_decoy_assets_severity'), 'decoy_assets', ['severity'], unique=False)
    op.create_index(op.f('ix_decoy_assets_enabled'), 'decoy_assets', ['enabled'], unique=False)

    # Create decoy_events table with blockchain fields
    op.create_table('decoy_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('decoy_id', sa.Integer(), nullable=False),
        sa.Column('event_hash', sa.String(), nullable=False),
        sa.Column('previous_hash', sa.String(), nullable=True),
        sa.Column('source_ip', sa.String(), nullable=False),
        sa.Column('source_endpoint', sa.String(), nullable=False),
        sa.Column('interaction_type', sa.String(), nullable=False),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('incident_id', sa.String(), nullable=True),
        sa.Column('alert_created', sa.Boolean(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['decoy_id'], ['decoy_assets.id'], ),
        sa.ForeignKeyConstraint(['incident_id'], ['investigations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decoy_events_decoy_id'), 'decoy_events', ['decoy_id'], unique=False)
    op.create_index(op.f('ix_decoy_events_event_hash'), 'decoy_events', ['event_hash'], unique=True)
    op.create_index(op.f('ix_decoy_events_previous_hash'), 'decoy_events', ['previous_hash'], unique=False)
    op.create_index(op.f('ix_decoy_events_source_ip'), 'decoy_events', ['source_ip'], unique=False)
    op.create_index(op.f('ix_decoy_events_interaction_type'), 'decoy_events', ['interaction_type'], unique=False)
    op.create_index(op.f('ix_decoy_events_session_id'), 'decoy_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_decoy_events_incident_id'), 'decoy_events', ['incident_id'], unique=False)
    op.create_index(op.f('ix_decoy_events_severity'), 'decoy_events', ['severity'], unique=False)
    op.create_index(op.f('ix_decoy_events_timestamp'), 'decoy_events', ['timestamp'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_decoy_events_timestamp'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_severity'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_incident_id'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_session_id'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_interaction_type'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_source_ip'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_previous_hash'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_event_hash'), table_name='decoy_events')
    op.drop_index(op.f('ix_decoy_events_decoy_id'), table_name='decoy_events')
    op.drop_table('decoy_events')
    
    op.drop_index(op.f('ix_decoy_assets_enabled'), table_name='decoy_assets')
    op.drop_index(op.f('ix_decoy_assets_severity'), table_name='decoy_assets')
    op.drop_index(op.f('ix_decoy_assets_decoy_type'), table_name='decoy_assets')
    op.drop_index(op.f('ix_decoy_assets_name'), table_name='decoy_assets')
    op.drop_table('decoy_assets')
