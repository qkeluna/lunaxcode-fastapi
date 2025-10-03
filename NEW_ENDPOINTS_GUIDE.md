# New API Endpoints - Onboarding & Contact Submissions

Complete guide for the newly implemented onboarding and contact submission endpoints.

## Overview

These endpoints enable:
- **Onboarding Submissions**: Full customer onboarding flow with payment tracking
- **Contact Submissions**: Simple contact form handling
- **Status Tracking**: Public endpoint for customers to check submission status

---

## Onboarding Submission Endpoints

### 1. Submit Onboarding Form

```http
POST /api/v1/onboarding/submit
```

**Authentication:** Public (no auth required)

**Request Body:**
```json
{
  "service_type": "website",
  "answers": {
    "fullName": "John Doe",
    "email": "john@example.com",
    "company": "Acme Inc",
    "phone": "+1234567890",
    "websiteType": "e-commerce",
    "pages": ["Home", "Shop", "About", "Contact"],
    "timeline": "2-4 weeks",
    "budget": "5000-10000"
  },
  "metadata": {
    "timestamp": 1696345678,
    "referrer": "https://google.com",
    "utm_source": "google",
    "utm_campaign": "spring-sale"
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "payment_url": null,
  "message": "Submission received successfully"
}
```

**Notes:**
- Automatically extracts customer info from `answers` object
- Stores full answers as JSONB for flexible querying
- Status set to `pending` by default
- Payment URL will be Stripe checkout link (TODO: implement)

### 2. List All Submissions (Admin)

```http
GET /api/v1/onboarding/submissions?status=pending&skip=0&limit=100
```

**Authentication:** Admin (`X-API-Key` header required)

**Query Parameters:**
- `status` (optional) - Filter by status: `pending`, `paid`, `in-progress`, `completed`, `cancelled`
- `skip` (optional) - Pagination offset (default: 0)
- `limit` (optional) - Results per page (default: 100, max: 100)

**Response (200 OK):**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "service_type": "website",
    "customer_email": "john@example.com",
    "customer_name": "John Doe",
    "customer_company": "Acme Inc",
    "customer_phone": "+1234567890",
    "answers": { /* full answers object */ },
    "status": "pending",
    "payment_status": "unpaid",
    "payment_intent_id": null,
    "created_at": "2025-10-03T10:30:00Z",
    "updated_at": "2025-10-03T10:30:00Z",
    "metadata": { /* tracking data */ }
  }
]
```

### 3. Get Submission Details (Admin)

```http
GET /api/v1/onboarding/submissions/{submission_id}
```

**Authentication:** Admin (`X-API-Key` header required)

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "service_type": "website",
  "customer_email": "john@example.com",
  "customer_name": "John Doe",
  "customer_company": "Acme Inc",
  "customer_phone": "+1234567890",
  "answers": {
    "fullName": "John Doe",
    "email": "john@example.com",
    "websiteType": "e-commerce",
    "pages": ["Home", "Shop", "About"],
    "timeline": "2-4 weeks"
  },
  "status": "pending",
  "payment_status": "unpaid",
  "payment_intent_id": null,
  "created_at": "2025-10-03T10:30:00Z",
  "updated_at": "2025-10-03T10:30:00Z",
  "metadata": {
    "utm_source": "google",
    "referrer": "https://google.com"
  }
}
```

### 4. Update Submission Status (Admin)

```http
PATCH /api/v1/onboarding/submissions/{submission_id}/status
```

**Authentication:** Admin (`X-API-Key` header required)

**Request Body:**
```json
{
  "status": "in-progress",
  "notes": "Started working on homepage design"
}
```

**Valid Status Values:**
- `pending` - Initial state after submission
- `paid` - Payment completed
- `in-progress` - Work has started
- `completed` - Project finished
- `cancelled` - Cancelled by customer or admin

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in-progress",
  "payment_status": "paid",
  "metadata": {
    "admin_notes": [
      {
        "note": "Started working on homepage design",
        "timestamp": "2025-10-03T14:00:00Z"
      }
    ]
  }
}
```

---

## Contact Submission Endpoints

### 1. Submit Contact Form

```http
POST /api/v1/contact/submit
```

**Authentication:** Public (no auth required)

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Project Inquiry",
  "message": "I'm interested in building a web application for my business. Can we schedule a call?",
  "metadata": {
    "source": "homepage",
    "timestamp": 1696345678
  }
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message_id": "650e8400-e29b-41d4-a716-446655440001",
  "message": "Thank you! We'll get back to you soon."
}
```

### 2. List All Contact Submissions (Admin)

```http
GET /api/v1/contact/submissions?status=new&skip=0&limit=100
```

**Authentication:** Admin (`X-API-Key` header required)

**Query Parameters:**
- `status` (optional) - Filter by status: `new`, `read`, `replied`, `archived`
- `skip` (optional) - Pagination offset
- `limit` (optional) - Results per page

**Response (200 OK):**
```json
[
  {
    "id": "650e8400-e29b-41d4-a716-446655440001",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Project Inquiry",
    "message": "I'm interested in building a web application...",
    "status": "new",
    "replied_at": null,
    "created_at": "2025-10-03T11:00:00Z",
    "metadata": {
      "source": "homepage"
    }
  }
]
```

### 3. Get Contact Details (Admin)

```http
GET /api/v1/contact/submissions/{contact_id}
```

**Authentication:** Admin (`X-API-Key` header required)

**Response (200 OK):**
```json
{
  "id": "650e8400-e29b-41d4-a716-446655440001",
  "name": "Jane Smith",
  "email": "jane@example.com",
  "subject": "Project Inquiry",
  "message": "I'm interested in building a web application for my business. Can we schedule a call?",
  "status": "new",
  "replied_at": null,
  "created_at": "2025-10-03T11:00:00Z",
  "metadata": {
    "source": "homepage",
    "timestamp": 1696345678
  }
}
```

### 4. Update Contact Status (Admin)

```http
PATCH /api/v1/contact/submissions/{contact_id}/status?status=replied
```

**Authentication:** Admin (`X-API-Key` header required)

**Query Parameters:**
- `status` - New status value: `new`, `read`, `replied`, `archived`

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Status updated"
}
```

---

## Submission Status Check (Public)

### Check Submission Status

```http
GET /api/v1/submissions/{submission_id}/status
```

**Authentication:** Public (no auth required)

**Purpose:** Allows customers to track their submission without logging in

**Response (200 OK):**
```json
{
  "submission_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "in-progress",
  "payment_status": "paid",
  "created_at": "2025-10-03T10:30:00Z",
  "estimated_completion": null,
  "updates": [
    {
      "timestamp": "2025-10-03T14:00:00Z",
      "status": "in-progress",
      "message": "Started working on homepage design"
    }
  ]
}
```

---

## Database Schema

### onboarding_submissions Table

```sql
CREATE TABLE onboarding_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service_type VARCHAR(50) NOT NULL,
  customer_email VARCHAR(255) NOT NULL,
  customer_name VARCHAR(255) NOT NULL,
  customer_company VARCHAR(255),
  customer_phone VARCHAR(50),
  answers JSONB NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',
  payment_status VARCHAR(20) DEFAULT 'unpaid',
  payment_intent_id VARCHAR(255),
  payment_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

CREATE INDEX idx_onboarding_service_type ON onboarding_submissions(service_type);
CREATE INDEX idx_onboarding_email ON onboarding_submissions(customer_email);
CREATE INDEX idx_onboarding_status ON onboarding_submissions(status);
CREATE INDEX idx_onboarding_created ON onboarding_submissions(created_at DESC);
```

### contact_submissions Table

```sql
CREATE TABLE contact_submissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  subject VARCHAR(255),
  message TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'new',
  replied_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

CREATE INDEX idx_contact_email ON contact_submissions(email);
CREATE INDEX idx_contact_status ON contact_submissions(status);
CREATE INDEX idx_contact_created ON contact_submissions(created_at DESC);
```

---

## Migration Steps

### 1. Run Database Migration

```bash
# Apply new tables migration
alembic upgrade head
```

This creates:
- `onboarding_submissions` table with indexes
- `contact_submissions` table with indexes

### 2. Update Frontend Integration

**Update DataService.ts:**

```typescript
class DataService {
  private apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

  async submitOnboarding(data: OnboardingData) {
    const response = await fetch(`${this.apiUrl}/onboarding/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_type: data.serviceType,
        answers: data.answers,
        metadata: {
          timestamp: Date.now(),
          referrer: document.referrer,
          utm_source: new URLSearchParams(window.location.search).get('utm_source')
        }
      })
    });
    
    if (!response.ok) throw new Error('Submission failed');
    return response.json();
  }

  async submitContact(data: ContactData) {
    const response = await fetch(`${this.apiUrl}/contact/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ...data,
        metadata: {
          source: 'homepage',
          timestamp: Date.now()
        }
      })
    });
    
    return response.json();
  }

  async checkSubmissionStatus(submissionId: string) {
    const response = await fetch(`${this.apiUrl}/submissions/${submissionId}/status`);
    return response.json();
  }
}
```

### 3. Test Endpoints

```bash
# Test onboarding submission (public)
curl -X POST http://localhost:8000/api/v1/onboarding/submit \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "website",
    "answers": {
      "fullName": "Test User",
      "email": "test@example.com",
      "websiteType": "portfolio"
    }
  }'

# List submissions (admin)
curl -X GET http://localhost:8000/api/v1/onboarding/submissions \
  -H "X-API-Key: your-api-key"

# Check status (public)
curl -X GET http://localhost:8000/api/v1/submissions/{submission-id}/status
```

---

## Future Enhancements (TODO)

### Stripe Payment Integration

```python
# In api/services/onboarding_service.py
async def create_stripe_checkout(submission: OnboardingSubmission):
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f'{submission.service_type} - Professional',
                },
                'unit_amount': 99900,  # $999 in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{settings.FRONTEND_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{settings.FRONTEND_URL}/cancelled',
        metadata={
            'submission_id': str(submission.id),
            'service_type': submission.service_type,
        }
    )
    
    return session.url
```

### Email Notifications

```python
# In api/services/email_service.py
async def send_onboarding_confirmation(submission: OnboardingSubmission):
    # Use SendGrid, AWS SES, or Postmark
    pass

async def send_admin_notification(submission: OnboardingSubmission):
    # Alert admin team of new submission
    pass
```

### Stripe Webhook Handler

```python
# In api/routers/webhooks.py
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            submission_id = session['metadata']['submission_id']
            
            # Update payment status
            await update_payment_status(
                UUID(submission_id),
                session['payment_intent'],
                'paid',
                db
            )
            
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## Admin Dashboard Integration

Add new pages to admin dashboard:

### Onboarding Submissions Page
- List all submissions with filters
- View submission details
- Update status
- Export to CSV

### Contact Submissions Page
- List all contact forms
- Mark as read/replied
- Quick reply templates

### Status Dashboard
- Show submission funnel (pending → paid → in-progress → completed)
- Revenue tracking
- Conversion metrics

---

## Security Considerations

1. **Rate Limiting** - Add to public endpoints:
   ```python
   from slowapi import Limiter
   
   @router.post("/onboarding/submit")
   @limiter.limit("5/hour")
   async def submit_onboarding(...):
       ...
   ```

2. **Input Validation** - Already handled by Pydantic schemas

3. **Email Verification** - Consider email verification before status updates

4. **Spam Protection** - Add reCAPTCHA to frontend forms

---

## Support

For questions about implementation:
- Review [CLAUDE.md](./CLAUDE.md) for development guidelines
- Check [ADMIN_API_REFERENCE.md](./ADMIN_API_REFERENCE.md) for existing endpoints
- See [api-requirements.md](./api-requirements.md) for full requirements
