-- Migration: Add onboarding and contact submission tables
-- Run this directly in Neon SQL Editor

-- Create onboarding_submissions table
CREATE TABLE IF NOT EXISTS onboarding_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_type VARCHAR(50) NOT NULL,
    customer_email VARCHAR(255) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    customer_company VARCHAR(255),
    customer_phone VARCHAR(50),
    answers JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'unpaid' NOT NULL,
    payment_intent_id VARCHAR(255),
    payment_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    submission_metadata JSONB
);

-- Create indexes for onboarding_submissions
CREATE INDEX IF NOT EXISTS idx_onboarding_service_type ON onboarding_submissions(service_type);
CREATE INDEX IF NOT EXISTS idx_onboarding_email ON onboarding_submissions(customer_email);
CREATE INDEX IF NOT EXISTS idx_onboarding_status ON onboarding_submissions(status);
CREATE INDEX IF NOT EXISTS idx_onboarding_created ON onboarding_submissions(created_at DESC);

-- Create contact_submissions table
CREATE TABLE IF NOT EXISTS contact_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    subject VARCHAR(255),
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'new' NOT NULL,
    replied_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    submission_metadata JSONB
);

-- Create indexes for contact_submissions
CREATE INDEX IF NOT EXISTS idx_contact_email ON contact_submissions(email);
CREATE INDEX IF NOT EXISTS idx_contact_status ON contact_submissions(status);
CREATE INDEX IF NOT EXISTS idx_contact_created ON contact_submissions(created_at DESC);

-- Update alembic version table (if using Alembic)
-- Note: Only run this if you're using Alembic for version tracking
INSERT INTO alembic_version (version_num) 
VALUES ('abc123def456')
ON CONFLICT (version_num) DO NOTHING;

-- Verify tables were created
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name IN ('onboarding_submissions', 'contact_submissions')
ORDER BY table_name, ordinal_position;

-- Verify indexes were created
SELECT 
    tablename, 
    indexname 
FROM pg_indexes 
WHERE tablename IN ('onboarding_submissions', 'contact_submissions')
ORDER BY tablename, indexname;
