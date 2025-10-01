# Vercel Deployment Checklist

## ✅ Pre-Deployment Requirements

### Environment Variables (Set in Vercel Dashboard)
- [ ] `DATABASE_URL` - Neon Postgres connection string
  - Format: `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`
  - Note: Remove `channel_binding` parameter if present
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
- Root cause: Vercel's Python runtime couldn't recognize the handler as a proper ASGI callable
- The error occurred during auto-detection when Vercel tried to determine handler type
- Triggered by requests to `/`, `/favicon.ico`, `/favicon.png`

**Fixes Applied:**

**Fix 1: Simplified Mangum Handler (`api/index.py`)**
```python
# ❌ BEFORE (with wrapper - caused detection issues)
_handler = Mangum(app, lifespan="off")
def handler(event, context):
    return _handler(event, context)

# ✅ AFTER (direct export - proper ASGI callable)
handler = Mangum(app, lifespan="off")
```
**Key:** Removed `api_gateway_base_path` parameter and wrapper function for clean ASGI export

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

### 2. Database URL Handling
- Improved URL conversion for `postgres://` and `postgresql://` formats
- Removed problematic `channel_binding` parameter for asyncpg compatibility
- Using `NullPool` for serverless (no connection pooling)

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

