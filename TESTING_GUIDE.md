# Testing Guide - New Endpoints

Complete guide for testing the new onboarding and contact submission endpoints.

## Prerequisites

1. **Database Migration:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Run migration
   alembic upgrade head
   ```

2. **Start API Server:**
   ```bash
   # Make sure you're in the virtual environment
   source venv/bin/activate
   
   # Start the server
   uvicorn api.main:app --reload --port 8000
   ```

3. **Set Environment Variables:**
   ```bash
   # In .env file
   DATABASE_URL=postgresql://...  # Your Neon database URL
   API_KEY=your-admin-key-here
   ```

---

## Automated Testing

### Option 1: Python Test Script (Recommended)

```bash
# Install dependencies (if needed)
pip install httpx python-dotenv

# Run tests
python test_new_endpoints.py
```

**What it tests:**
- ✅ Onboarding submission (public)
- ✅ Contact submission (public)
- ✅ Status check (public)
- ✅ List submissions (admin)
- ✅ Get submission details (admin)
- ✅ Update submission status (admin)
- ✅ List contacts (admin)
- ✅ Get contact details (admin)
- ✅ Update contact status (admin)
- ✅ Filter by status (admin)

### Option 2: Bash Test Script

```bash
# Install jq for JSON parsing (if needed)
brew install jq  # macOS
# or
sudo apt install jq  # Linux

# Update API key in script
# Edit test_new_endpoints.sh and set API_KEY

# Run tests
./test_new_endpoints.sh
```

---

## Manual Testing with cURL

### 1. Submit Onboarding Form (Public)

```bash
curl -X POST http://localhost:8000/api/v1/onboarding/submit \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "website",
    "answers": {
      "fullName": "John Doe",
      "email": "john@example.com",
      "company": "Acme Inc",
      "phone": "+1234567890",
      "websiteType": "e-commerce",
      "pages": ["Home", "Shop", "About"],
      "timeline": "2-4 weeks"
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_url": null,
  "message": "Submission received successfully"
}
```

**Save the submission_id for next tests!**

### 2. Check Submission Status (Public)

```bash
# Replace {submission_id} with actual ID from step 1
curl http://localhost:8000/api/v1/submissions/{submission_id}/status
```

**Expected Response:**
```json
{
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "payment_status": "unpaid",
  "created_at": "2025-10-03T10:30:00Z",
  "estimated_completion": null,
  "updates": []
}
```

### 3. Submit Contact Form (Public)

```bash
curl -X POST http://localhost:8000/api/v1/contact/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Project Inquiry",
    "message": "I am interested in your services"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message_id": "650e8400-e29b-41d4-a716-446655440001",
  "message": "Thank you! We'll get back to you soon."
}
```

### 4. List All Onboarding Submissions (Admin)

```bash
# Replace YOUR_API_KEY with actual key from .env
curl http://localhost:8000/api/v1/onboarding/submissions \
  -H "X-API-Key: YOUR_API_KEY"
```

**Expected Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "service_type": "website",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "status": "pending",
    "payment_status": "unpaid",
    ...
  }
]
```

### 5. Update Submission Status (Admin)

```bash
curl -X PATCH http://localhost:8000/api/v1/onboarding/submissions/{submission_id}/status \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{
    "status": "in-progress",
    "notes": "Started working on design"
  }'
```

**Expected Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in-progress",
  "payment_status": "unpaid",
  "metadata": {
    "admin_notes": [
      {
        "note": "Started working on design",
        "timestamp": "2025-10-03T14:00:00Z"
      }
    ]
  }
}
```

### 6. Filter Submissions by Status (Admin)

```bash
curl "http://localhost:8000/api/v1/onboarding/submissions?status=in-progress&limit=10" \
  -H "X-API-Key: YOUR_API_KEY"
```

### 7. List Contact Submissions (Admin)

```bash
curl http://localhost:8000/api/v1/contact/submissions \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## Testing with Swagger UI

1. **Open Interactive Docs:**
   ```
   http://localhost:8000/api/v1/docs
   ```

2. **Test Public Endpoints:**
   - Find `POST /onboarding/submit`
   - Click "Try it out"
   - Edit request body
   - Click "Execute"

3. **Test Admin Endpoints:**
   - Click "Authorize" button (top right)
   - Enter API key in `X-API-Key` field
   - Click "Authorize"
   - Now you can test admin endpoints

---

## Verification Checklist

### Database Verification

Connect to your Neon database and verify:

```sql
-- Check onboarding_submissions table
SELECT * FROM onboarding_submissions ORDER BY created_at DESC LIMIT 5;

-- Check contact_submissions table
SELECT * FROM contact_submissions ORDER BY created_at DESC LIMIT 5;

-- Count submissions by status
SELECT status, COUNT(*) 
FROM onboarding_submissions 
GROUP BY status;

-- Check metadata fields
SELECT 
  id, 
  customer_name, 
  status, 
  metadata->'admin_notes' as notes
FROM onboarding_submissions
WHERE metadata IS NOT NULL;
```

### API Response Verification

✅ **Public Endpoints Work Without Auth:**
- POST /onboarding/submit
- POST /contact/submit
- GET /submissions/{id}/status

✅ **Admin Endpoints Require API Key:**
- GET /onboarding/submissions
- PATCH /onboarding/submissions/{id}/status
- GET /contact/submissions
- PATCH /contact/submissions/{id}/status

✅ **Data Validation:**
- UUID primary keys generated correctly
- JSONB fields store complex objects
- Timestamps auto-generated
- Status enums enforced
- Indexes created for performance

✅ **Status Flow:**
- Onboarding: pending → paid → in-progress → completed
- Contact: new → read → replied → archived

---

## Common Issues & Solutions

### Issue 1: Migration Fails

```bash
# Error: Table already exists
# Solution: Drop tables manually or use downgrade
alembic downgrade -1
alembic upgrade head
```

### Issue 2: API Key Authentication Fails

```bash
# Check .env file has API_KEY set
cat .env | grep API_KEY

# Make sure to use X-API-Key header (not Authorization)
curl ... -H "X-API-Key: your-key"
```

### Issue 3: UUID Parse Error

```bash
# Make sure to use full UUID, not shortened version
# Correct: 550e8400-e29b-41d4-a716-446655440000
# Wrong: 550e8400
```

### Issue 4: JSONB Query Issues

```sql
-- Access JSONB fields with ->
SELECT answers->'fullName' FROM onboarding_submissions;

-- Query within JSONB
SELECT * FROM onboarding_submissions 
WHERE answers->>'websiteType' = 'e-commerce';
```

---

## Performance Testing

### Load Test (Optional)

```bash
# Install hey (HTTP load generator)
brew install hey

# Test onboarding endpoint
hey -n 100 -c 10 \
  -m POST \
  -H "Content-Type: application/json" \
  -d '{"service_type":"website","answers":{"fullName":"Load Test","email":"test@example.com"}}' \
  http://localhost:8000/api/v1/onboarding/submit
```

**Expected Performance:**
- Response time: < 200ms (avg)
- Throughput: > 50 req/sec
- Error rate: 0%

---

## Next Steps After Testing

1. ✅ Verify all tests pass
2. ✅ Check database for correct data
3. ✅ Test with Postman collection
4. ✅ Deploy to Vercel staging
5. ✅ Test production endpoints
6. ✅ Integrate with frontend
7. ✅ Add Stripe payment (TODO)
8. ✅ Add email notifications (TODO)

---

## Support

If tests fail, check:
1. Server is running: `curl http://localhost:8000/api/v1/health`
2. Database is accessible: `psql $DATABASE_URL -c "SELECT 1"`
3. Migration ran: `alembic current`
4. API key is correct: Check `.env` file
5. Logs for errors: Check terminal where server is running
