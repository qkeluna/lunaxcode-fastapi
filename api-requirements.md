# API Requirements for LunaxCode Site

**Document Purpose**: Backend API specification for FastAPI endpoints development  
**Created**: 2025-10-03  
**Status**: Planning - Ready for implementation

---

## Overview

The Next.js frontend is architected with a `DataService` abstraction layer that currently uses localStorage. This document specifies the FastAPI endpoints needed to replace localStorage with persistent backend storage.

## Current Architecture

**Frontend Data Layer**: `src/lib/data-service.ts`  
**Storage**: localStorage (temporary, browser-dependent)  
**State Management**: Zustand stores  
**Email**: EmailJS configured but needs backend trigger

---

## Required API Endpoints

### 1. Onboarding Submission

**Purpose**: Persist customer onboarding data and trigger notification workflow

#### Endpoint
```
POST /api/v1/onboarding/submit
```

#### Request Body
```typescript
{
  serviceType: string;           // e.g., "website", "webapp", "mobile-app"
  answers: {
    // Basic Information
    fullName: string;
    email: string;
    company?: string;
    phone?: string;
    
    // Service-Specific Answers (dynamic based on serviceType)
    [key: string]: any;          // Question IDs from onboarding-questions.ts
  };
  metadata?: {
    timestamp: number;
    userAgent?: string;
    referrer?: string;
  };
}
```

#### Response (Success)
```typescript
{
  success: true;
  submissionId: string;          // UUID for tracking
  paymentUrl?: string;           // Redirect URL for payment
  message: string;
}
```

#### Response (Error)
```typescript
{
  success: false;
  error: {
    code: string;                // "VALIDATION_ERROR", "SERVER_ERROR"
    message: string;
    fields?: string[];           // Invalid field names
  }
}
```

#### Backend Logic
1. **Validate** submission data against service type schema
2. **Save** to database with status: `pending`
3. **Generate** unique submission ID
4. **Trigger** email notifications (admin + customer)
5. **Create** payment intent (Stripe) and return checkout URL
6. **Return** submission ID and payment URL

#### Database Schema
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
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB
);

CREATE INDEX idx_submissions_email ON onboarding_submissions(customer_email);
CREATE INDEX idx_submissions_status ON onboarding_submissions(status);
CREATE INDEX idx_submissions_created ON onboarding_submissions(created_at DESC);
```

---

### 2. Contact Form Submission

**Purpose**: Handle simple contact form submissions from homepage

#### Endpoint
```
POST /api/v1/contact/submit
```

#### Request Body
```typescript
{
  name: string;
  email: string;
  message: string;
  subject?: string;
  metadata?: {
    timestamp: number;
    source?: string;            // "homepage", "footer", etc.
  };
}
```

#### Response (Success)
```typescript
{
  success: true;
  messageId: string;
  message: "Thank you! We'll get back to you soon."
}
```

#### Backend Logic
1. **Validate** email and required fields
2. **Save** to contacts database
3. **Send** email notification to admin
4. **Send** auto-reply to customer
5. **Return** confirmation

#### Database Schema
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

CREATE INDEX idx_contacts_email ON contact_submissions(email);
CREATE INDEX idx_contacts_status ON contact_submissions(status);
CREATE INDEX idx_contacts_created ON contact_submissions(created_at DESC);
```

---

### 3. Submission Status Check

**Purpose**: Allow customers to check their submission status

#### Endpoint
```
GET /api/v1/submissions/{submissionId}/status
```

#### Response
```typescript
{
  submissionId: string;
  status: "pending" | "paid" | "in-progress" | "completed" | "cancelled";
  paymentStatus: "unpaid" | "paid" | "refunded";
  createdAt: string;           // ISO 8601
  estimatedCompletion?: string; // ISO 8601
  updates: Array<{
    timestamp: string;
    status: string;
    message: string;
  }>;
}
```

---

### 4. Payment Webhook

**Purpose**: Handle Stripe payment confirmation webhooks

#### Endpoint
```
POST /api/v1/webhooks/stripe
```

#### Request Body
Stripe webhook event payload (signature verification required)

#### Backend Logic
1. **Verify** Stripe signature
2. **Update** submission payment_status to `paid`
3. **Update** submission status to `in-progress`
4. **Trigger** email confirmation to customer
5. **Notify** admin team of new paid project

---

### 5. Admin Dashboard Endpoints

**Purpose**: Internal admin panel to manage submissions

#### List Submissions
```
GET /api/v1/admin/submissions?status={status}&page={page}&limit={limit}
Authorization: Bearer {admin_token}
```

#### Response
```typescript
{
  submissions: Array<{
    id: string;
    serviceType: string;
    customerName: string;
    customerEmail: string;
    status: string;
    paymentStatus: string;
    createdAt: string;
  }>;
  pagination: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}
```

#### Get Submission Details
```
GET /api/v1/admin/submissions/{submissionId}
Authorization: Bearer {admin_token}
```

#### Update Submission Status
```
PATCH /api/v1/admin/submissions/{submissionId}/status
Authorization: Bearer {admin_token}

{
  status: "in-progress" | "completed" | "cancelled";
  notes?: string;
}
```

---

## Email Notification Requirements

### 1. Customer Onboarding Confirmation
**Trigger**: POST /api/v1/onboarding/submit success  
**To**: Customer email  
**Subject**: "Thanks for choosing LunaxCode - Next Steps"  
**Content**:
- Submission confirmation
- Payment link
- What happens next
- Contact information

### 2. Admin New Submission Alert
**Trigger**: POST /api/v1/onboarding/submit success  
**To**: Admin team  
**Subject**: "New {serviceType} Project Submission - {customerName}"  
**Content**:
- Customer details
- Service type
- Key answers summary
- Link to admin dashboard

### 3. Payment Confirmation
**Trigger**: Stripe webhook payment success  
**To**: Customer + Admin  
**Subject**: "Payment Confirmed - Project Starting Soon"  
**Content**:
- Payment receipt
- Project timeline
- Next steps
- Admin notification

### 4. Contact Form Auto-Reply
**Trigger**: POST /api/v1/contact/submit success  
**To**: Customer email  
**Subject**: "We received your message"  
**Content**:
- Confirmation message
- Expected response time
- Contact options

---

## Payment Integration Requirements

### Stripe Integration

#### Products to Create
```typescript
const products = [
  {
    name: "Starter Website",
    price: 99900,              // $999 in cents
    currency: "usd",
    metadata: { serviceType: "website", tier: "starter" }
  },
  {
    name: "Professional Website",
    price: 249900,             // $2,499 in cents
    currency: "usd",
    metadata: { serviceType: "website", tier: "professional" }
  },
  {
    name: "Enterprise Website",
    price: 499900,             // $4,999 in cents
    currency: "usd",
    metadata: { serviceType: "website", tier: "enterprise" }
  }
  // Add other service types...
];
```

#### Payment Flow
1. Customer completes onboarding
2. Backend creates Stripe Checkout Session
3. Customer redirected to Stripe hosted checkout
4. Payment success → Webhook updates database
5. Customer redirected back to success page with submission ID

#### Checkout Session Configuration
```python
stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': f'{service_type} - {tier}',
                'description': 'LunaxCode Project',
            },
            'unit_amount': price_in_cents,
        },
        'quantity': 1,
    }],
    mode='payment',
    success_url=f'{frontend_url}/onboarding/success?session_id={{CHECKOUT_SESSION_ID}}',
    cancel_url=f'{frontend_url}/onboarding/cancelled',
    metadata={
        'submission_id': submission_id,
        'service_type': service_type,
    }
)
```

---

## Security Requirements

### Authentication
- **Admin Endpoints**: JWT bearer token authentication
- **Public Endpoints**: Rate limiting (10 req/min per IP)
- **Webhook Endpoints**: Stripe signature verification

### Data Validation
- Email format validation
- Phone number sanitization
- XSS prevention (sanitize text inputs)
- SQL injection prevention (parameterized queries)

### CORS Configuration
```python
allowed_origins = [
    "https://lunaxcode.com",
    "https://www.lunaxcode.com",
    "http://localhost:3000",      # Development
]
```

### Rate Limiting
```python
rate_limits = {
    "/api/v1/onboarding/submit": "5/hour",
    "/api/v1/contact/submit": "10/hour",
    "/api/v1/submissions/*/status": "60/hour",
}
```

---

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/lunaxcode

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PUBLISHABLE_KEY=pk_live_...

# Email (SendGrid/AWS SES)
EMAIL_SERVICE=sendgrid
EMAIL_API_KEY=SG.xxx
EMAIL_FROM=notifications@lunaxcode.com
ADMIN_EMAIL=team@lunaxcode.com

# Frontend
FRONTEND_URL=https://lunaxcode.com

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION=24h

# Rate Limiting
REDIS_URL=redis://localhost:6379
```

---

## Frontend Integration Changes

### Update DataService
**File**: `src/lib/data-service.ts`

Replace localStorage methods with API calls:

```typescript
class DataService {
  private apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  async submitOnboarding(data: OnboardingSubmission) {
    const response = await fetch(`${this.apiUrl}/api/v1/onboarding/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error.message);
    }
    
    return response.json();
  }

  async submitContact(data: ContactFormData) {
    const response = await fetch(`${this.apiUrl}/api/v1/contact/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    return response.json();
  }

  async getSubmissionStatus(submissionId: string) {
    const response = await fetch(
      `${this.apiUrl}/api/v1/submissions/${submissionId}/status`
    );
    return response.json();
  }
}
```

### Add Environment Variable
**File**: `.env.local`

```env
NEXT_PUBLIC_API_URL=https://api.lunaxcode.com
```

---

## Testing Requirements

### API Tests
- ✅ Onboarding submission with valid data
- ✅ Onboarding submission with invalid data (validation)
- ✅ Contact form submission
- ✅ Duplicate email handling
- ✅ Rate limiting enforcement
- ✅ Stripe webhook signature validation
- ✅ Admin authentication
- ✅ CORS policy enforcement

### Integration Tests
- ✅ End-to-end onboarding → payment → confirmation flow
- ✅ Email delivery (staging environment)
- ✅ Database persistence and retrieval
- ✅ Status updates via admin panel

---

## Deployment Checklist

- [ ] FastAPI app deployed (e.g., AWS ECS, Railway, Render)
- [ ] PostgreSQL database provisioned
- [ ] Redis for rate limiting (optional but recommended)
- [ ] Stripe account configured with products
- [ ] Webhook endpoint registered in Stripe dashboard
- [ ] Email service configured (SendGrid/AWS SES)
- [ ] Environment variables set in production
- [ ] SSL certificate for API domain
- [ ] CORS configured for production frontend domain
- [ ] Rate limiting configured
- [ ] Database migrations run
- [ ] Admin JWT tokens generated
- [ ] Frontend `.env.production` updated with API URL

---

## Migration Steps

1. **Phase 1: Backend Setup**
   - Deploy FastAPI with database
   - Implement onboarding and contact endpoints
   - Configure email service

2. **Phase 2: Payment Integration**
   - Setup Stripe products
   - Implement checkout session creation
   - Configure webhook handling

3. **Phase 3: Frontend Integration**
   - Update DataService to use API
   - Add error handling and loading states
   - Test full onboarding flow

4. **Phase 4: Admin Panel**
   - Implement admin endpoints
   - Build simple admin dashboard (optional)
   - Configure authentication

5. **Phase 5: Production Launch**
   - Deploy to production
   - Test payment flow end-to-end
   - Monitor email delivery
   - Set up error tracking (Sentry)

---

## API Response Standards

### Success Response Pattern
```typescript
{
  success: true,
  data: { /* actual response data */ },
  message?: string
}
```

### Error Response Pattern
```typescript
{
  success: false,
  error: {
    code: string,              // Machine-readable error code
    message: string,           // Human-readable message
    fields?: string[],         // Validation errors
    details?: any              // Additional context
  }
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created (onboarding submission)
- `400` - Validation error
- `401` - Unauthorized (admin endpoints)
- `404` - Not found
- `429` - Rate limit exceeded
- `500` - Internal server error

---

## Additional Considerations

### Analytics & Tracking
Consider adding tracking fields to submissions:
- UTM parameters (source, medium, campaign)
- Referrer URL
- User agent
- Session ID

### Future Enhancements
- **File Uploads**: Allow customers to upload mockups, logos, assets
- **Real-time Updates**: WebSocket for submission status updates
- **Chat Integration**: Add live chat for pre-sales questions
- **Project Portal**: Customer dashboard to track project progress
- **Invoicing**: Automated invoice generation after payment

---

## Questions for Backend Team

1. **Preferred Email Service**: SendGrid, AWS SES, or Postmark?
2. **Database Preference**: PostgreSQL version? RDS or self-hosted?
3. **Deployment Platform**: AWS, Railway, Render, or other?
4. **Admin Panel**: Build custom or use existing admin framework?
5. **File Storage**: Need S3 for file uploads in future?
6. **Monitoring**: Preferred error tracking (Sentry, Rollbar)?

---

**Next Steps**: Share this document with backend team and schedule API contract review meeting.
