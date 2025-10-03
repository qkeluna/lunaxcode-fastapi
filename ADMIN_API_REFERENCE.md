# Admin API Reference

Complete reference for all admin endpoints in the Lunaxcode FastAPI backend.

## Authentication

All admin endpoints require the `X-API-Key` header:

```bash
X-API-Key: your-api-key-here
```

Set `API_KEY` in your `.env` file or Vercel environment variables.

## Base URL

```
Production: https://your-domain.vercel.app/api/v1
Development: http://localhost:8000/api/v1
```

---

## Pricing Plans

### List All Pricing Plans
```http
GET /pricing
```
**Auth:** Public  
**Response:** Array of pricing plans

**Example:**
```bash
curl https://your-domain.vercel.app/api/v1/pricing
```

### Get Single Pricing Plan
```http
GET /pricing/{plan_id}
```
**Auth:** Public  
**Parameters:** `plan_id` (string) - e.g., "landing_page"

### Create Pricing Plan
```http
POST /pricing
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "id": "custom_website",
  "name": "Custom Website",
  "price": 25000,
  "currency": "PHP",
  "timeline": "2-week delivery",
  "features": [
    "Custom design",
    "Responsive layout",
    "SEO optimized"
  ],
  "popular": false
}
```

### Update Pricing Plan
```http
PUT /pricing/{plan_id}
```
**Auth:** Admin (X-API-Key required)  
**Body:** (all fields optional)
```json
{
  "name": "Updated Name",
  "price": 30000,
  "popular": true
}
```

### Delete Pricing Plan
```http
DELETE /pricing/{plan_id}
```
**Auth:** Admin (X-API-Key required)  
**Response:** 204 No Content

---

## Services

### List All Services
```http
GET /services
```
**Auth:** Public  
**Response:** Array of services

### Get Single Service
```http
GET /services/{service_id}
```
**Auth:** Public  
**Parameters:** `service_id` (string) - e.g., "landing_page"

### Create Service
```http
POST /services
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "id": "mobile_app",
  "name": "Mobile App Development",
  "description": "Native iOS and Android apps",
  "icon": "📱"
}
```

### Update Service
```http
PUT /services/{service_id}
```
**Auth:** Admin (X-API-Key required)  
**Body:** (all fields optional)
```json
{
  "name": "Updated Service Name",
  "description": "New description"
}
```

### Delete Service
```http
DELETE /services/{service_id}
```
**Auth:** Admin (X-API-Key required)  
**Response:** 204 No Content

---

## Features

### List All Features
```http
GET /features
```
**Auth:** Public  
**Response:** Array of features ordered by `display_order`

### Get Single Feature
```http
GET /features/{feature_id}
```
**Auth:** Public  
**Parameters:** `feature_id` (integer)

### Create Feature
```http
POST /features
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "title": "Fast Delivery",
  "description": "Get your project delivered in record time",
  "icon": "⚡",
  "display_order": 1
}
```

### Update Feature
```http
PUT /features/{feature_id}
```
**Auth:** Admin (X-API-Key required)  
**Body:** (all fields optional)
```json
{
  "title": "Lightning Fast Delivery",
  "display_order": 2
}
```

### Delete Feature
```http
DELETE /features/{feature_id}
```
**Auth:** Admin (X-API-Key required)  
**Response:** 204 No Content

---

## Add-ons

### List All Add-ons
```http
GET /addons
```
**Auth:** Public  
**Response:** Array of add-ons

### Get Single Add-on
```http
GET /addons/{addon_id}
```
**Auth:** Public  
**Parameters:** `addon_id` (integer)

### Create Add-on
```http
POST /addons
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "name": "SEO Optimization",
  "description": "Complete on-page SEO setup",
  "price_range": "₱3,000 - ₱5,000",
  "icon": "🔍"
}
```

### Update Add-on
```http
PUT /addons/{addon_id}
```
**Auth:** Admin (X-API-Key required)  
**Body:** (all fields optional)
```json
{
  "name": "Advanced SEO",
  "price_range": "₱5,000 - ₱8,000"
}
```

### Delete Add-on
```http
DELETE /addons/{addon_id}
```
**Auth:** Admin (X-API-Key required)  
**Response:** 204 No Content

---

## Company Info

### Get Company Information
```http
GET /company
```
**Auth:** Public  
**Response:** Company information (singleton record)

### Update Company Information
```http
PUT /company
```
**Auth:** Admin (X-API-Key required)  
**Body:** (all fields optional)
```json
{
  "name": "Lunaxcode",
  "tagline": "Build. Ship. Scale.",
  "email": "hello@lunaxcode.site",
  "phone": "+63 917 123 4567",
  "address": "Manila, Philippines",
  "social_links": {
    "github": "https://github.com/lunaxcode",
    "linkedin": "https://linkedin.com/company/lunaxcode"
  }
}
```

**Note:** Company info is a singleton - only one record exists (id=1)

---

## Onboarding Questions

### List All Question Sets
```http
GET /onboarding/questions
```
**Auth:** Public  
**Response:** Array of all onboarding question sets

### Get Questions for Service
```http
GET /onboarding/questions/{service_type}
```
**Auth:** Public  
**Parameters:** `service_type` (string) - e.g., "landing_page"

### Create Question Set
```http
POST /onboarding/questions
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "service_type": "mobile_app",
  "questions": [
    {
      "id": "platform",
      "label": "Which platforms?",
      "type": "checkbox",
      "required": true,
      "options": ["iOS", "Android", "Both"]
    },
    {
      "id": "features",
      "label": "Required features?",
      "type": "textarea",
      "required": true,
      "placeholder": "Describe key features..."
    }
  ]
}
```

### Update Question Set
```http
PUT /onboarding/questions/{service_type}
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "questions": [
    {
      "id": "updated_question",
      "label": "New question",
      "type": "text",
      "required": false
    }
  ]
}
```

### Delete Question Set
```http
DELETE /onboarding/questions/{service_type}
```
**Auth:** Admin (X-API-Key required)  
**Response:** 204 No Content

---

## Leads

### Submit New Lead
```http
POST /leads
```
**Auth:** Public  
**Body:**
```json
{
  "service_type": "landing_page",
  "full_name": "Maria Santos",
  "email": "maria@example.com",
  "phone": "+63 917 123 4567",
  "company": "TechStartup PH",
  "project_description": "Need a landing page for product launch",
  "answers": {
    "landing_type": "Product Launch",
    "design_style": "Modern Tech",
    "sections": ["Hero", "Features", "Pricing"],
    "cta_goal": "Sign up for beta"
  }
}
```

**Response:** Lead object with auto-generated `ai_prompt`

**Note:** This endpoint automatically generates the `ai_prompt` field from the structured data.

### List All Leads
```http
GET /leads?skip=0&limit=100&status=new
```
**Auth:** Admin (X-API-Key required)  
**Query Parameters:**
- `skip` (int, default: 0) - Pagination offset
- `limit` (int, default: 100, max: 100) - Results per page
- `status` (string, optional) - Filter by status: `new`, `contacted`, `converted`, `rejected`

### Get Single Lead
```http
GET /leads/{lead_id}
```
**Auth:** Admin (X-API-Key required)  
**Parameters:** `lead_id` (integer)

### Update Lead Status
```http
PUT /leads/{lead_id}
```
**Auth:** Admin (X-API-Key required)  
**Body:**
```json
{
  "status": "contacted"
}
```

**Valid statuses:** `new`, `contacted`, `converted`, `rejected`

### Delete Lead
```http
DELETE /leads/{lead_id}
```
**Auth:** Admin (X-API-Key required)  
**Response:** 204 No Content

---

## Lead Status Workflow

Recommended lead status progression:

```
new → contacted → converted ✅
                → rejected ❌
```

- **new**: Initial submission
- **contacted**: Admin has reached out
- **converted**: Lead became a client
- **rejected**: Lead declined or not suitable

---

## Error Responses

All endpoints follow standard HTTP error codes:

### 400 Bad Request
```json
{
  "detail": "Pricing plan with this ID already exists"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 404 Not Found
```json
{
  "detail": "Pricing plan not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "price"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error"
    }
  ]
}
```

---

## Postman Collection

Import the included `lunaxcode-api.postman_collection.json` for pre-configured requests.

**Setup:**
1. Import collection into Postman
2. Create environment variable: `API_KEY`
3. Set base URL: `{{base_url}}/api/v1`

---

## Testing Admin Endpoints

### Using cURL

```bash
# Set your API key
export API_KEY="your-api-key-here"

# Create a pricing plan
curl -X POST https://your-domain.vercel.app/api/v1/pricing \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "id": "test_plan",
    "name": "Test Plan",
    "price": 5000,
    "currency": "PHP",
    "timeline": "1 week",
    "features": ["Feature 1", "Feature 2"],
    "popular": false
  }'

# Update lead status
curl -X PUT https://your-domain.vercel.app/api/v1/leads/1 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{"status": "contacted"}'

# List leads with filtering
curl -X GET "https://your-domain.vercel.app/api/v1/leads?status=new&limit=50" \
  -H "X-API-Key: $API_KEY"
```

### Using Python

```python
import httpx

API_KEY = "your-api-key-here"
BASE_URL = "https://your-domain.vercel.app/api/v1"

headers = {"X-API-Key": API_KEY}

# Update lead status
async with httpx.AsyncClient() as client:
    response = await client.put(
        f"{BASE_URL}/leads/1",
        json={"status": "contacted"},
        headers=headers
    )
    print(response.json())
```

---

## Development vs Production

### Development
```bash
# Start local server
uvicorn api.main:app --reload --port 8000

# Base URL
http://localhost:8000/api/v1
```

### Production
```bash
# Deploy to Vercel
vercel --prod

# Base URL
https://your-domain.vercel.app/api/v1
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production admin dashboard:

**Recommended:**
- Implement rate limiting on admin endpoints
- Use session-based authentication instead of API keys
- Add audit logging for all admin actions
- Implement RBAC (Role-Based Access Control)

---

## Next Steps

For building your admin dashboard UI:

1. **Frontend Framework:** Use React/Next.js, Vue, or TanStack Start
2. **API Client:** Create typed API client using the schemas
3. **Authentication:** Store API key securely (environment variables, not in code)
4. **State Management:** Use TanStack Query for data fetching and caching
5. **Forms:** Use React Hook Form or similar for CRUD operations
6. **Tables:** Use TanStack Table for lead management with filtering

**Example Admin Dashboard Features:**
- Dashboard with lead statistics
- Lead management table with status filtering
- Pricing plan editor
- Service/feature/addon management
- Company info editor
- Onboarding question builder

---

## Support

For questions or issues:
- Email: hello@lunaxcode.site
- Review API documentation: `/api/v1/docs` (Swagger UI)
- Check `CLAUDE.md` for development guidelines
