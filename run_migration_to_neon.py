#!/usr/bin/env python3
"""
Script to manually run migration to Neon database
Usage: python run_migration_to_neon.py
"""

import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Migration SQL
MIGRATION_SQL = """
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

-- Update alembic version (if using Alembic)
INSERT INTO alembic_version (version_num) 
VALUES ('abc123def456')
ON CONFLICT (version_num) DO NOTHING;
"""

VERIFY_SQL = """
-- Verify tables
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('onboarding_submissions', 'contact_submissions')
ORDER BY table_name;
"""

def main():
    print("=" * 60)
    print("Migrating New Tables to Neon Database")
    print("=" * 60)
    
    if not DATABASE_URL:
        print("❌ ERROR: DATABASE_URL not found in environment variables")
        print("Please check your .env file")
        return 1
    
    # Convert DATABASE_URL for psycopg2 (remove channel_binding if present)
    db_url = DATABASE_URL.replace('?channel_binding=prefer', '')
    
    print(f"✓ Database URL loaded")
    print(f"  Host: {db_url.split('@')[1].split('/')[0] if '@' in db_url else 'unknown'}")
    
    try:
        print("\n📡 Connecting to Neon database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("✓ Connected successfully")
        
        print("\n🔨 Running migration SQL...")
        cursor.execute(MIGRATION_SQL)
        print("✓ Migration executed successfully")
        
        print("\n🔍 Verifying tables were created...")
        cursor.execute(VERIFY_SQL)
        tables = cursor.fetchall()
        
        if tables:
            print("✓ Tables created successfully:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("❌ No tables found! Migration may have failed.")
            return 1
        
        print("\n📊 Checking table structures...")
        
        # Check onboarding_submissions columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'onboarding_submissions'
            ORDER BY ordinal_position
        """)
        print("\n✓ onboarding_submissions columns:")
        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]}")
        
        # Check contact_submissions columns
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'contact_submissions'
            ORDER BY ordinal_position
        """)
        print("\n✓ contact_submissions columns:")
        for col in cursor.fetchall():
            print(f"  - {col[0]}: {col[1]}")
        
        # Check indexes
        cursor.execute("""
            SELECT tablename, indexname 
            FROM pg_indexes 
            WHERE tablename IN ('onboarding_submissions', 'contact_submissions')
            ORDER BY tablename, indexname
        """)
        print("\n✓ Indexes created:")
        for idx in cursor.fetchall():
            print(f"  - {idx[0]}.{idx[1]}")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the API server: uvicorn api.main:app --reload")
        print("2. Test endpoints: python test_new_endpoints.py")
        print("3. Check API docs: http://localhost:8000/api/v1/docs")
        
        return 0
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
