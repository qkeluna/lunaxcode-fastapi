# API Quick Reference

## 🔗 Base URL
```
https://lunaxcode-fastapi.vercel.app/api/v1
```

## 📝 Quick Endpoints

### Public Endpoints

```bash
# Health Check
GET /health
GET /health/db

# Pricing
GET /pricing              # Get all plans
GET /pricing/{id}         # Get specific plan

# Services
GET /services             # Get all services
GET /services/{id}        # Get specific service

# Features
GET /features             # Get all features (ordered)

# Add-ons
GET /addons               # Get all add-ons

# Company Info
GET /company              # Get company details

# Onboarding
GET /onboarding/questions/{service_type}

# Leads (Submit)
POST /leads               # Submit contact/lead form
```

## 🚀 Quick Start Code

### 1. Simple Fetch (Client-Side)

```typescript
// Get pricing plans
const response = await fetch('https://lunaxcode-fastapi.vercel.app/api/v1/pricing');
const plans = await response.json();
```

### 2. Submit Lead Form

```typescript
const leadData = {
  name: "John Doe",
  email: "john@example.com",
  phone: "+63 912 345 6789",
  service_type: "landing_page",
  budget_range: "5000-10000",
  project_description: "Need a landing page",
  answers: {}
};

const response = await fetch('https://lunaxcode-fastapi.vercel.app/api/v1/leads', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(leadData)
});

const result = await response.json();
```

### 3. Next.js Server Component

```typescript
// app/pricing/page.tsx
export const revalidate = 3600; // Revalidate hourly

export default async function PricingPage() {
  const res = await fetch('https://lunaxcode-fastapi.vercel.app/api/v1/pricing');
  const plans = await res.json();
  
  return (
    <div>
      {plans.map(plan => (
        <div key={plan.id}>{plan.name} - ₱{plan.price}</div>
      ))}
    </div>
  );
}
```

## 📊 Response Examples

### Pricing Plan
```json
{
  "id": "landing_page",
  "name": "Landing Page",
  "price": 8000,
  "currency": "PHP",
  "timeline": "48-hour delivery",
  "features": [
    "1 Professional Landing Page",
    "AI Chat Widget Integration",
    "Mobile Responsive Design"
  ],
  "popular": false
}
```

### Service
```json
{
  "id": "landing_page",
  "name": "Landing Page",
  "description": "48-Hour Landing Pages",
  "details": "Professional landing pages in just 48 hours",
  "icon": "⚡",
  "timeline": "48 hours"
}
```

### Company Info
```json
{
  "name": "Lunaxcode",
  "tagline": "Code at the Speed of Light",
  "contact": {
    "email": "hello@lunaxcode.site",
    "phone": "+63 912 345 6789",
    "location": "Antipolo City, Rizal, Philippines"
  },
  "payment_terms": {
    "deposit": "30-50%",
    "balance": "on delivery",
    "methods": ["GCash", "PayMaya", "Bank Transfer"]
  }
}
```

## 🔐 Environment Variables

```env
NEXT_PUBLIC_API_URL=https://lunaxcode-fastapi.vercel.app
NEXT_PUBLIC_API_VERSION=v1
```

## ⚡ Test in Browser Console

```javascript
// Quick test
fetch('https://lunaxcode-fastapi.vercel.app/api/v1/pricing')
  .then(r => r.json())
  .then(console.log);

// Submit test lead
fetch('https://lunaxcode-fastapi.vercel.app/api/v1/leads', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    name: "Test User",
    email: "test@example.com",
    service_type: "landing_page",
    budget_range: "5000-10000",
    answers: {}
  })
}).then(r => r.json()).then(console.log);
```

## 🎯 Service Types (IDs)

- `landing_page` - Landing Page
- `basic_website` - Basic Website  
- `custom_development` - Custom Development
- `mobile_app` - Mobile App
- `ai_integration` - AI Integration

## 💰 Budget Ranges

- `under-5000` - Under ₱5,000
- `5000-10000` - ₱5,000 - ₱10,000
- `10000-25000` - ₱10,000 - ₱25,000
- `25000-50000` - ₱25,000 - ₱50,000
- `50000-plus` - ₱50,000+

## 📖 Full Documentation

**Interactive API Docs:** https://lunaxcode-fastapi.vercel.app/api/v1/docs

**Integration Guide:** See `FRONTEND_INTEGRATION.md`

