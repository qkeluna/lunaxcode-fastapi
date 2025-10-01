# Vercel Deployment Checklist

## ✅ Pre-Deployment Requirements

### Environment Variables (Set in Vercel Dashboard)
- [ ] `DATABASE_URL` - Neon Postgres connection string
  - Format: `postgresql://user:pass@host.neon.tech/dbname`
  - **IMPORTANT:** Do NOT include `?sslmode=require` - the code auto-converts it to `ssl=require` for asyncpg
  - Note: `channel_binding` and `sslmode` parameters are automatically removed/converted
- [ ] `API_KEY` - Admin authentication key
- [ ] `CORS_ORIGINS` - Comma-separated allowed origins (e.g., `https://lunaxcode.com,https://www.lunaxcode.com`)
- [ ] `ENVIRONMENT` - Set to `production`
- [ ] `LOG_LEVEL` - Set to `INFO` or `WARNING`

### Database Migrations
```bash
# Ensure migrations are up to date
alembic upgrade head

# Seed initial data if needed
python scripts/seed_data.py
```

## 🔧 Fixed Issues (Oct 1, 2025)

### 1. Handler Export Pattern - Vercel Runtime Compatibility
**Problem:** `issubclass() arg 1 must be a class` TypeError in Vercel's `vc__handler__python.py`
- Root cause: Mangum adapter was incompatible with Vercel's Python runtime auto-detection
- The error occurred when Vercel tried to wrap the handler in its runtime layer
- Triggered by all requests including `/`, `/favicon.ico`, `/favicon.png`

**THE REAL SOLUTION:**

**Fix 1: Remove Mangum - Use Native ASGI (`api/index.py`)**
```python
# ❌ BEFORE (Mangum caused issubclass errors with Vercel)
from mangum import Mangum
from api.main import app
handler = Mangum(app, lifespan="off")

# ✅ AFTER (Direct FastAPI export - Vercel handles ASGI natively)
from api.main import app
__all__ = ["app"]
```
**Key Insight:** Vercel's `@vercel/python` runtime **natively supports ASGI applications** like FastAPI. Using Mangum (designed for AWS Lambda) causes conflicts with Vercel's handler detection.

**Fix 1b: Removed Mangum Dependency (`requirements.txt`)**
- Mangum is not needed for Vercel deployment
- Vercel's Python runtime auto-detects and serves ASGI apps directly

**Fix 2: Added Favicon Handlers (`api/main.py`)**
```python
@app.get("/favicon.ico")
@app.get("/favicon.png")
async def favicon():
    """Return 204 No Content for favicon requests"""
    from fastapi import Response
    return Response(status_code=204)
```
**Key:** Prevents 404 errors on favicon requests that were triggering handler detection issues

**Fix 3: Cleaned Vercel Configuration (`vercel.json`)**
- Removed `env.ENVIRONMENT` from vercel.json (set via dashboard instead)
- Kept `maxLambdaSize: 15mb` for dependencies

### 2. Database URL Handling - asyncpg SSL Configuration
**Problem:** `connect() got an unexpected keyword argument 'sslmode'`
- Root cause: asyncpg doesn't support `sslmode` parameter (PostgreSQL native format)
- asyncpg requires `ssl=require` instead of `sslmode=require`

**Fix:** Auto-convert SSL parameters in `api/database.py`
```python
# Remove sslmode parameter
database_url = re.sub(r'[?&]sslmode=[^&]*', '', database_url)

# Add asyncpg-compatible SSL
if '?' in database_url:
    database_url += '&ssl=require'
else:
    database_url += '?ssl=require'
```

**Additional improvements:**
- Auto-convert `postgres://` and `postgresql://` to `postgresql+asyncpg://`
- Remove `channel_binding` parameter (not supported by asyncpg)
- Use `NullPool` for serverless (no connection pooling)

### 3. Vercel Configuration
- Added `maxLambdaSize: 15mb` to handle dependencies
- Set `ENVIRONMENT: production` in vercel.json

## 🚀 Deployment Steps

### Option 1: Vercel CLI (Recommended)
```bash
# Install Vercel CLI globally
npm i -g vercel

# Deploy to production
vercel --prod

# Or deploy preview
vercel
```

### Option 2: Git Push (Auto-deploy)
```bash
git add .
git commit -m "fix: serverless handler export pattern for Vercel"
git push origin main
```

## 🧪 Post-Deployment Testing

### 1. Health Check
```bash
curl https://your-domain.vercel.app/api/v1/health
# Expected: {"status": "healthy"}
```

### 2. Test Public Endpoints
```bash
# Get pricing
curl https://your-domain.vercel.app/api/v1/pricing

# Get services
curl https://your-domain.vercel.app/api/v1/services
```

### 3. Test Admin Endpoints
```bash
# List leads (requires API key)
curl -H "X-API-Key: YOUR_API_KEY" https://your-domain.vercel.app/api/v1/leads
```

### 4. Test Lead Submission
```bash
curl -X POST https://your-domain.vercel.app/api/v1/leads \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "company": "Test Co",
    "service_type": 1,
    "budget_range": "5000-10000",
    "answers": {"question1": "answer1"}
  }'
```

## 🔍 Troubleshooting

### Cold Start Issues
- **Symptom:** First request slow or times out
- **Solution:** Use `NullPool` (already configured for production)
- **Mitigation:** Implement Vercel cron for warming

### Database Connection Errors
```bash
# Check Vercel logs
vercel logs

# Common issues:
# 1. DATABASE_URL not set → Add in Vercel dashboard
# 2. channel_binding error → Remove from URL
# 3. Connection timeout → Check Neon pooling settings
```

### CORS Errors
- Verify `CORS_ORIGINS` includes your frontend domain
- Check protocol (https vs http)
- Ensure no trailing slashes in origins

### Import Errors
- Ensure all dependencies in `requirements.txt`
- Check `maxLambdaSize` if bundle too large
- Review Vercel build logs for missing packages

## 📊 Monitoring

### Vercel Dashboard Metrics
- Function execution count
- Error rate
- Cold start frequency
- Response time (P50, P95, P99)

### Neon Postgres Metrics
- Active connections
- Query performance
- Database size
- Connection pooling stats

## 🔐 Security Checklist
- [ ] API_KEY is strong and unique
- [ ] DATABASE_URL uses SSL (`sslmode=require`)
- [ ] CORS_ORIGINS restricted to known domains
- [ ] Environment variables not committed to git
- [ ] Rate limiting configured (via SlowAPI)
- [ ] Global exception handler hides internal errors in production

## 📝 Notes
- Vercel serverless functions have 10-second timeout (Hobby) / 60s (Pro)
- Neon Postgres free tier: 10GB storage, 1GB RAM
- Cold starts: ~1-3 seconds with NullPool
- Max Lambda size: 50MB (increase if needed via config)

