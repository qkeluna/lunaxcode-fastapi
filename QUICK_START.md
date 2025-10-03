# Quick Start - New Endpoints

## ✅ What Was Fixed

**Issue:** SQLAlchemy reserved word conflict with `metadata` column name  
**Solution:** Renamed to `submission_metadata` in all files

## 🚀 Quick Test Steps

### 1. Run Migration
```bash
source venv/bin/activate
alembic upgrade head
```

### 2. Start Server
```bash
uvicorn api.main:app --reload --port 8000
```

### 3. Test Public Endpoints

**Test Onboarding Submission:**
```bash
curl -X POST http://localhost:8000/api/v1/onboarding/submit \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "website",
    "answers": {
      "fullName": "John Doe",
      "email": "john@example.com",
      "company": "Test Co"
    }
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "submission_id": "550e8400-e29b-...",
  "message": "Submission received successfully"
}
```

**Test Contact Form:**
```bash
curl -X POST http://localhost:8000/api/v1/contact/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "message": "Test message"
  }'
```

### 4. Run Automated Tests (Optional)

```bash
# Python test script
python test_new_endpoints.py

# Or bash script
./test_new_endpoints.sh
```

## 📋 New Endpoints Summary

### Public (No Auth)
- `POST /api/v1/onboarding/submit` - Submit onboarding form
- `POST /api/v1/contact/submit` - Submit contact form
- `GET /api/v1/submissions/{id}/status` - Check submission status

### Admin (API Key Required)
- `GET /api/v1/onboarding/submissions` - List all submissions
- `GET /api/v1/onboarding/submissions/{id}` - Get details
- `PATCH /api/v1/onboarding/submissions/{id}/status` - Update status
- `GET /api/v1/contact/submissions` - List contacts
- `GET /api/v1/contact/submissions/{id}` - Get contact details
- `PATCH /api/v1/contact/submissions/{id}/status` - Update status

## 📊 Verify Database

```sql
-- Check tables exist
\dt onboarding_submissions
\dt contact_submissions

-- View data
SELECT * FROM onboarding_submissions ORDER BY created_at DESC LIMIT 5;
SELECT * FROM contact_submissions ORDER BY created_at DESC LIMIT 5;
```

## 📚 Full Documentation

- **[NEW_ENDPOINTS_GUIDE.md](./NEW_ENDPOINTS_GUIDE.md)** - Complete API reference
- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Full testing guide
- **[CLAUDE.md](./CLAUDE.md)** - Development guidelines

## ⚡ Key Features

✅ UUID primary keys for secure public IDs  
✅ JSONB storage for flexible data  
✅ Payment tracking ready (Stripe integration TODO)  
✅ Admin notes with timestamps  
✅ Status workflow management  
✅ Public status checking (no auth)  
✅ Full filtering and pagination  

## 🔧 Next Steps

1. ✅ Migration complete
2. ✅ Server starts without errors
3. ⏳ Test endpoints (use scripts above)
4. ⏳ Integrate with frontend
5. ⏳ Add Stripe payment (optional)
6. ⏳ Add email notifications (optional)
