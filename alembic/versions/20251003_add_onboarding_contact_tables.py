"""add onboarding and contact submission tables

Revision ID: abc123def456
Revises: ec15a00675f5
Create Date: 2025-10-03

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'abc123def456'
down_revision: Union[str, None] = 'ec15a00675f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create onboarding_submissions table
    op.create_table(
        'onboarding_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('service_type', sa.String(50), nullable=False),
        sa.Column('customer_email', sa.String(255), nullable=False),
        sa.Column('customer_name', sa.String(255), nullable=False),
        sa.Column('customer_company', sa.String(255), nullable=True),
        sa.Column('customer_phone', sa.String(50), nullable=True),
        sa.Column('answers', postgresql.JSONB, nullable=False),
        sa.Column('status', sa.String(20), server_default='pending', nullable=False),
        sa.Column('payment_status', sa.String(20), server_default='unpaid', nullable=False),
        sa.Column('payment_intent_id', sa.String(255), nullable=True),
        sa.Column('payment_url', sa.Text, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('submission_metadata', postgresql.JSONB, nullable=True)
    )
    
    # Create indexes for onboarding_submissions
    op.create_index('idx_onboarding_service_type', 'onboarding_submissions', ['service_type'])
    op.create_index('idx_onboarding_email', 'onboarding_submissions', ['customer_email'])
    op.create_index('idx_onboarding_status', 'onboarding_submissions', ['status'])
    op.create_index('idx_onboarding_created', 'onboarding_submissions', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    
    # Create contact_submissions table
    op.create_table(
        'contact_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('status', sa.String(20), server_default='new', nullable=False),
        sa.Column('replied_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('submission_metadata', postgresql.JSONB, nullable=True)
    )
    
    # Create indexes for contact_submissions
    op.create_index('idx_contact_email', 'contact_submissions', ['email'])
    op.create_index('idx_contact_status', 'contact_submissions', ['status'])
    op.create_index('idx_contact_created', 'contact_submissions', ['created_at'], postgresql_ops={'created_at': 'DESC'})


def downgrade() -> None:
    # Drop contact_submissions indexes
    op.drop_index('idx_contact_created', table_name='contact_submissions')
    op.drop_index('idx_contact_status', table_name='contact_submissions')
    op.drop_index('idx_contact_email', table_name='contact_submissions')
    
    # Drop contact_submissions table
    op.drop_table('contact_submissions')
    
    # Drop onboarding_submissions indexes
    op.drop_index('idx_onboarding_created', table_name='onboarding_submissions')
    op.drop_index('idx_onboarding_status', table_name='onboarding_submissions')
    op.drop_index('idx_onboarding_email', table_name='onboarding_submissions')
    op.drop_index('idx_onboarding_service_type', table_name='onboarding_submissions')
    
    # Drop onboarding_submissions table
    op.drop_table('onboarding_submissions')
