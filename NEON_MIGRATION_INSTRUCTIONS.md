# Neon Database Migration Instructions

## Option 1: Neon SQL Editor (Recommended)

Since automated migration is timing out, you can run the migration manually in the Neon Console.

### Steps:

1. **Go to Neon Console:**
   - Visit: https://console.neon.tech
   - Log in to your account
   - Select your project

2. **Open SQL Editor:**
   - Click on "SQL Editor" in the left sidebar
   - Or navigate to: Tables → SQL Editor

3. **Copy and Run Migration SQL:**

```sql
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

-- Update alembic version (optional - only if you're tracking migrations with Alembic)
INSERT INTO alembic_version (version_num) 
VALUES ('abc123def456')
ON CONFLICT (version_num) DO NOTHING;
```

4. **Click "Run" button**

5. **Verify tables were created:**

```sql
-- Check tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_name IN ('onboarding_submissions', 'contact_submissions')
ORDER BY table_name;

-- Check columns
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name IN ('onboarding_submissions', 'contact_submissions')
ORDER BY table_name, ordinal_position;

-- Check indexes
SELECT tablename, indexname 
FROM pg_indexes 
WHERE tablename IN ('onboarding_submissions', 'contact_submissions')
ORDER BY tablename, indexname;
```

**Expected output:**
- 2 tables created: `contact_submissions`, `onboarding_submissions`
- 7 indexes created total
- All columns with correct data types

---

## Option 2: Using psql (If you have PostgreSQL client)

```bash
# Set password as environment variable
export PGPASSWORD='npg_gVT0Anbpx7DE'

# Connect and run migration file
psql -h ep-noisy-unit-a1hoa9fb-pooler.ap-southeast-1.aws.neon.tech \
     -U neondb_owner \
     -d neondb \
     -f migrate_to_neon.sql
```

---

## Option 3: Python Script (If psycopg2 is working)

```bash
# Install psycopg2 if not already installed
pip install psycopg2-binary

# Run migration script
python run_migration_to_neon.py
```

---

## Verification After Migration

### 1. Check tables in Neon Console

Navigate to: Tables → View Tables
You should see:
- `onboarding_submissions` (14 columns)
- `contact_submissions` (8 columns)

### 2. Test with API

```bash
# Start server
uvicorn api.main:app --reload --port 8000

# Test onboarding submission
curl -X POST http://localhost:8000/api/v1/onboarding/submit \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "website",
    "answers": {
      "fullName": "Test User",
      "email": "test@example.com"
    }
  }'

# Should return success with submission_id
```

### 3. Check data in Neon Console

```sql
-- View submitted data
SELECT * FROM onboarding_submissions ORDER BY created_at DESC LIMIT 5;
SELECT * FROM contact_submissions ORDER BY created_at DESC LIMIT 5;

-- Count records
SELECT 
    'onboarding_submissions' as table_name, 
    COUNT(*) as count 
FROM onboarding_submissions
UNION ALL
SELECT 
    'contact_submissions' as table_name, 
    COUNT(*) as count 
FROM contact_submissions;
```

---

## Troubleshooting

### Issue: "relation already exists"
**Solution:** Tables already created, migration successful! Just verify with SELECT queries above.

### Issue: "permission denied"
**Solution:** Make sure you're using the correct database credentials from .env file.

### Issue: Connection timeout
**Solution:** 
- Check Neon project is active (not hibernated)
- Try running migration directly in Neon SQL Editor (Option 1)

### Issue: Alembic version error
**Solution:** The `INSERT INTO alembic_version` line is optional. You can skip it if you're not using Alembic for version tracking.

---

## After Successful Migration

✅ **Checklist:**
- [ ] Tables created successfully
- [ ] Indexes created (7 total)
- [ ] Test onboarding endpoint works
- [ ] Test contact endpoint works  
- [ ] Data appears in Neon console
- [ ] Status check endpoint works

✅ **Next Steps:**
1. Start using the new endpoints
2. Integrate with frontend
3. Add Stripe payment (optional)
4. Add email notifications (optional)

---

## Files Available

- `migrate_to_neon.sql` - Raw SQL migration script
- `run_migration_to_neon.py` - Python migration script
- `QUICK_START.md` - Quick testing guide
- `TESTING_GUIDE.md` - Complete testing documentation
- `NEW_ENDPOINTS_GUIDE.md` - Full API reference

---

## Support

If migration still fails:
1. Share the error message
2. Check Neon console logs
3. Verify database connection string in .env
4. Try running SQL directly in Neon SQL Editor (most reliable method)
