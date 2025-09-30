# Lunaxcode API Development Plan

## Executive Summary

This document outlines the development plan for a FastAPI-based REST API that will replace the current static data layer in the Lunaxcode website. The API will be deployed to Vercel as serverless functions, using Neon Postgres as the database backend.

**Current State:** Static TypeScript data files (`src/data/`)
**Target State:** Production-ready REST API with Postgres persistence
**Timeline:** Estimated 2-3 weeks for full implementation and testing

---

## Technical Architecture

### Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **API Framework** | FastAPI | Async support, automatic OpenAPI docs, Pydantic validation |
| **Database** | Neon Postgres | Serverless, auto-scaling, Vercel-compatible |
| **ORM** | SQLAlchemy 2.0 | Mature, async support, type-safe |
| **Migrations** | Alembic | Industry standard for SQLAlchemy |
| **Validation** | Pydantic v2 | Built into FastAPI, powerful validation |
| **Deployment** | Vercel Serverless | Zero-config, auto-scaling, global CDN |
| **Language** | Python 3.11+ | Modern async features, type hints |

### Architecture Diagram

```
┌─────────────────┐
│  Next.js Frontend│
│  (lunaxcode-site)│
└────────┬────────┘
         │ HTTPS/REST
         ▼
┌─────────────────┐
│  Vercel Edge    │
│  (API Gateway)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐      ┌──────────────┐
│  FastAPI        │─────▶│ Neon Postgres│
│  Serverless     │      │  Database    │
│  Functions      │      └──────────────┘
└─────────────────┘
```

---

## Database Schema

### Tables Overview

| Table | Purpose | Records | Key Feature |
|-------|---------|---------|-------------|
| `pricing_plans` | Service pricing tiers | 5 plans | JSONB features array |
| `addons` | Additional services | 3 addons | Price ranges |
| `services` | Service catalog | 5 services | Linked to pricing |
| `features` | Marketing features | 6 features | Display ordering |
| `company_info` | Company details (singleton) | 1 record | JSONB contact/terms |
| `onboarding_questions` | Dynamic form questions | 5 question sets | JSONB question schemas |
| `leads` | Customer submissions | Dynamic | **Dual storage: JSONB + AI prompt** |

### Detailed Schema

#### 1. pricing_plans
```sql
CREATE TABLE pricing_plans (
    id TEXT PRIMARY KEY,                    -- 'landing_page', 'basic_website', etc.
    name TEXT NOT NULL,
    price INTEGER NOT NULL,                 -- In PHP
    currency TEXT NOT NULL DEFAULT 'PHP',
    timeline TEXT NOT NULL,                 -- '48-hour delivery'
    features JSONB NOT NULL,                -- Array of feature strings
    popular BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Sample Data:**
```json
{
    "id": "landing_page",
    "name": "Landing Page",
    "price": 8000,
    "currency": "PHP",
    "timeline": "48-hour delivery",
    "features": ["1 Professional Landing Page", "AI Chat Widget Integration", ...],
    "popular": false
}
```

#### 2. addons
```sql
CREATE TABLE addons (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    price_range TEXT NOT NULL,              -- '1500-2000'
    currency TEXT NOT NULL DEFAULT 'PHP',
    unit TEXT NOT NULL,                     -- 'each', 'project', 'monthly'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 3. services
```sql
CREATE TABLE services (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    details TEXT NOT NULL,
    icon TEXT NOT NULL,                     -- Emoji or icon identifier
    timeline TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 4. features
```sql
CREATE TABLE features (
    id SERIAL PRIMARY KEY,
    icon TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    display_order INTEGER,                  -- For ordering
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### 5. company_info
```sql
CREATE TABLE company_info (
    id INTEGER PRIMARY KEY DEFAULT 1,       -- Singleton table
    name TEXT NOT NULL,
    tagline TEXT NOT NULL,
    description TEXT NOT NULL,
    contact JSONB NOT NULL,                 -- {email, phone, location}
    payment_terms JSONB NOT NULL,           -- {deposit, balance, methods[]}
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT single_row CHECK (id = 1)    -- Ensure only one row
);
```

#### 6. onboarding_questions
```sql
CREATE TABLE onboarding_questions (
    id SERIAL PRIMARY KEY,
    service_type TEXT NOT NULL UNIQUE,      -- FK to services.id
    title TEXT NOT NULL,
    questions JSONB NOT NULL,               -- Array of question objects
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_service FOREIGN KEY (service_type) REFERENCES services(id)
);
```

**Questions JSON Structure:**
```json
[
    {
        "id": "pageType",
        "label": "What type of landing page?",
        "type": "select",
        "options": ["Product Launch", "Lead Generation", ...],
        "required": true
    }
]
```

#### 7. leads
```sql
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    service_type TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    company TEXT,
    project_description TEXT,
    answers JSONB NOT NULL,                 -- Service-specific answers (structured data)
    ai_prompt TEXT NOT NULL,                -- AI-formatted prompt from answers
    status TEXT DEFAULT 'new',              -- 'new', 'contacted', 'converted', 'rejected'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT fk_service FOREIGN KEY (service_type) REFERENCES services(id)
);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_created_at ON leads(created_at DESC);
CREATE INDEX idx_leads_email ON leads(email);
```

**Business Logic - Dual Data Storage:**

The `leads` table stores data in two formats for different purposes:

1. **`answers` (JSONB)** - Structured data for querying and reporting
   - Allows SQL queries on specific answers
   - Easy to filter leads by requirements
   - Machine-readable format for analytics

2. **`ai_prompt` (TEXT)** - Human-readable prompt for AI/LLM processing
   - Natural language description of project requirements
   - Ready for AI content generation or project scoping
   - Can be used directly in LLM context

**Example Data Structure:**

```json
// answers field (structured)
{
    "pageType": "Product Launch",
    "designStyle": "Modern/Minimalist",
    "sections": ["Hero Section", "Features/Benefits", "Pricing"],
    "ctaGoal": "Sign up for free trial"
}

// ai_prompt field (formatted for AI)
"Project: Landing Page for Juan Dela Cruz (ABC Corp)
Service Type: Landing Page
Email: juan@example.com
Phone: +63 912 345 6789

Project Description:
Need landing page for product launch

Requirements:
- Page Type: Product Launch
- Design Style: Modern/Minimalist
- Required Sections: Hero Section, Features/Benefits, Pricing
- Primary CTA Goal: Sign up for free trial

Timeline: 48-hour delivery
Price: ₱8,000"
```

---

## API Endpoints

### Base URL
- **Development:** `http://localhost:8000/api/v1`
- **Production:** `https://api.lunaxcode.site/api/v1`

### Endpoint Specification

#### 1. Pricing Plans
```
GET    /api/v1/pricing              # List all pricing plans
GET    /api/v1/pricing/{id}         # Get specific plan
POST   /api/v1/pricing              # Create plan (admin)
PUT    /api/v1/pricing/{id}         # Update plan (admin)
DELETE /api/v1/pricing/{id}         # Delete plan (admin)
```

**Response Example:**
```json
[
    {
        "id": "landing_page",
        "name": "Landing Page",
        "price": 8000,
        "currency": "PHP",
        "timeline": "48-hour delivery",
        "features": ["1 Professional Landing Page", ...],
        "popular": false
    }
]
```

#### 2. Add-ons
```
GET    /api/v1/addons               # List all addons
GET    /api/v1/addons/{id}          # Get specific addon
POST   /api/v1/addons               # Create addon (admin)
PUT    /api/v1/addons/{id}          # Update addon (admin)
DELETE /api/v1/addons/{id}          # Delete addon (admin)
```

#### 3. Services
```
GET    /api/v1/services             # List all services
GET    /api/v1/services/{id}        # Get specific service
POST   /api/v1/services             # Create service (admin)
PUT    /api/v1/services/{id}        # Update service (admin)
DELETE /api/v1/services/{id}        # Delete service (admin)
```

#### 4. Features
```
GET    /api/v1/features             # List all features (ordered)
GET    /api/v1/features/{id}        # Get specific feature
POST   /api/v1/features             # Create feature (admin)
PUT    /api/v1/features/{id}        # Update feature (admin)
DELETE /api/v1/features/{id}        # Delete feature (admin)
```

#### 5. Company Info
```
GET    /api/v1/company              # Get company information
PUT    /api/v1/company              # Update company info (admin)
```

#### 6. Onboarding Questions
```
GET    /api/v1/onboarding/questions                    # List all question sets
GET    /api/v1/onboarding/questions/{service_type}     # Get questions for service
POST   /api/v1/onboarding/questions                    # Create question set (admin)
PUT    /api/v1/onboarding/questions/{service_type}     # Update questions (admin)
```

**Response Example:**
```json
{
    "service_type": "landing_page",
    "title": "Landing Page Requirements",
    "questions": [
        {
            "id": "pageType",
            "label": "What type of landing page?",
            "type": "select",
            "options": ["Product Launch", "Lead Generation", ...],
            "required": true
        }
    ]
}
```

#### 7. Leads
```
GET    /api/v1/leads                # List all leads (admin)
GET    /api/v1/leads/{id}           # Get specific lead (admin)
POST   /api/v1/leads                # Submit new lead (public)
PUT    /api/v1/leads/{id}           # Update lead status (admin)
DELETE /api/v1/leads/{id}           # Delete lead (admin)
```

**POST Request Example:**
```json
{
    "service_type": "landing_page",
    "full_name": "Juan Dela Cruz",
    "email": "juan@example.com",
    "phone": "+63 912 345 6789",
    "company": "ABC Corp",
    "project_description": "Need landing page for product launch",
    "answers": {
        "pageType": "Product Launch",
        "designStyle": "Modern/Minimalist",
        "sections": ["Hero Section", "Features/Benefits", "Pricing"],
        "ctaGoal": "Sign up for free trial"
    }
}
```

**POST Response Example:**
```json
{
    "id": 123,
    "service_type": "landing_page",
    "full_name": "Juan Dela Cruz",
    "email": "juan@example.com",
    "phone": "+63 912 345 6789",
    "company": "ABC Corp",
    "project_description": "Need landing page for product launch",
    "answers": {
        "pageType": "Product Launch",
        "designStyle": "Modern/Minimalist",
        "sections": ["Hero Section", "Features/Benefits", "Pricing"],
        "ctaGoal": "Sign up for free trial"
    },
    "ai_prompt": "Project: Landing Page for Juan Dela Cruz (ABC Corp)...",
    "status": "new",
    "created_at": "2025-09-30T10:30:00Z"
}
```

**GET Response Example (Admin):**
```json
{
    "id": 123,
    "service_type": "landing_page",
    "full_name": "Juan Dela Cruz",
    "email": "juan@example.com",
    "phone": "+63 912 345 6789",
    "company": "ABC Corp",
    "project_description": "Need landing page for product launch",
    "answers": {
        "pageType": "Product Launch",
        "designStyle": "Modern/Minimalist",
        "sections": ["Hero Section", "Features/Benefits", "Pricing"],
        "ctaGoal": "Sign up for free trial"
    },
    "ai_prompt": "Project: Landing Page for Juan Dela Cruz (ABC Corp)\nService Type: Landing Page\nEmail: juan@example.com\nPhone: +63 912 345 6789\n\nProject Description:\nNeed landing page for product launch\n\nRequirements:\n- Page Type: Product Launch\n- Design Style: Modern/Minimalist\n- Required Sections: Hero Section, Features/Benefits, Pricing\n- Primary CTA Goal: Sign up for free trial\n\nTimeline: 48-hour delivery\nPrice: ₱8,000",
    "status": "new",
    "created_at": "2025-09-30T10:30:00Z",
    "updated_at": "2025-09-30T10:30:00Z"
}
```

**Business Logic Implementation:**

The API automatically generates the `ai_prompt` field when a lead is submitted. The service layer includes a prompt formatter:

```python
# api/services/lead_service.py

def format_ai_prompt(lead_data: dict, pricing_info: dict) -> str:
    """
    Convert structured lead data into AI-friendly prompt format.

    Args:
        lead_data: The lead submission data
        pricing_info: Pricing and timeline information for the service

    Returns:
        Formatted prompt string ready for AI processing
    """
    service_type = lead_data['service_type']
    answers = lead_data['answers']

    # Build header
    prompt_parts = [
        f"Project: {pricing_info['name']} for {lead_data['full_name']}",
    ]

    if lead_data.get('company'):
        prompt_parts[0] += f" ({lead_data['company']})"

    prompt_parts.extend([
        f"Service Type: {pricing_info['name']}",
        f"Email: {lead_data['email']}",
    ])

    if lead_data.get('phone'):
        prompt_parts.append(f"Phone: {lead_data['phone']}")

    # Project description
    prompt_parts.extend([
        "",
        "Project Description:",
        lead_data.get('project_description', 'Not provided'),
        "",
        "Requirements:"
    ])

    # Format answers based on question labels
    questions = get_questions_for_service(service_type)
    for question in questions:
        q_id = question['id']
        if q_id in answers:
            label = question['label']
            value = answers[q_id]

            # Format arrays nicely
            if isinstance(value, list):
                value = ", ".join(value)

            prompt_parts.append(f"- {label}: {value}")

    # Add pricing and timeline
    prompt_parts.extend([
        "",
        f"Timeline: {pricing_info['timeline']}",
        f"Price: ₱{pricing_info['price']:,}"
    ])

    return "\n".join(prompt_parts)


async def create_lead(lead_create: LeadCreate, db: Session) -> Lead:
    """
    Create a new lead with both structured answers and AI prompt.
    """
    # Get pricing information
    pricing = db.query(PricingPlan).filter(
        PricingPlan.id == lead_create.service_type
    ).first()

    if not pricing:
        raise ValueError(f"Invalid service type: {lead_create.service_type}")

    # Generate AI prompt
    ai_prompt = format_ai_prompt(
        lead_data=lead_create.dict(),
        pricing_info={
            'name': pricing.name,
            'timeline': pricing.timeline,
            'price': pricing.price
        }
    )

    # Create lead with both formats
    lead = Lead(
        **lead_create.dict(),
        ai_prompt=ai_prompt
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Optional: Send email notification with ai_prompt
    await send_lead_notification(lead)

    return lead
```

#### 8. Health Check
```
GET    /api/v1/health               # API health status
GET    /api/v1/health/db            # Database connection status
```

---

## Project Structure

```
lunaxcode-api/
├── api/
│   ├── __init__.py
│   ├── index.py                    # Vercel serverless handler
│   ├── main.py                     # FastAPI application
│   ├── config.py                   # Configuration and settings
│   ├── database.py                 # Database connection and session
│   │
│   ├── models/                     # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── pricing.py
│   │   ├── addon.py
│   │   ├── service.py
│   │   ├── feature.py
│   │   ├── company.py
│   │   ├── onboarding.py
│   │   └── lead.py
│   │
│   ├── schemas/                    # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── pricing.py
│   │   ├── addon.py
│   │   ├── service.py
│   │   ├── feature.py
│   │   ├── company.py
│   │   ├── onboarding.py
│   │   └── lead.py
│   │
│   ├── routers/                    # API route handlers
│   │   ├── __init__.py
│   │   ├── pricing.py
│   │   ├── addons.py
│   │   ├── services.py
│   │   ├── features.py
│   │   ├── company.py
│   │   ├── onboarding.py
│   │   ├── leads.py
│   │   └── health.py
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── pricing_service.py
│   │   ├── addon_service.py
│   │   ├── service_service.py
│   │   ├── feature_service.py
│   │   ├── company_service.py
│   │   ├── onboarding_service.py
│   │   └── lead_service.py
│   │
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       ├── logging.py
│       └── exceptions.py
│
├── alembic/                        # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── scripts/                        # Utility scripts
│   ├── seed_data.py                # Seed initial data from TS files
│   └── convert_ts_to_json.py      # Convert TS data to JSON
│
├── tests/                          # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_pricing.py
│   ├── test_addons.py
│   ├── test_services.py
│   ├── test_features.py
│   ├── test_company.py
│   ├── test_onboarding.py
│   └── test_leads.py
│
├── .env.example                    # Environment variable template
├── .gitignore
├── alembic.ini                     # Alembic configuration
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment config
└── README.md                       # Project documentation
```

---

## Implementation Phases

### Phase 1: Project Initialization (Day 1-2)

**Tasks:**
1. Create new Git repository for API project
2. Initialize Python project structure
3. Setup virtual environment
4. Install dependencies
5. Configure Neon Postgres database
6. Setup Alembic for migrations
7. Create basic FastAPI application
8. Test local development server

**Deliverables:**
- Working FastAPI skeleton
- Database connection established
- Health check endpoint functional

---

### Phase 2: Database Schema & Models (Day 3-5)

**Tasks:**
1. Create SQLAlchemy models for all tables
2. Write Alembic migration scripts
3. Create Pydantic schemas for validation
4. Setup database session management
5. Run migrations on development database
6. Write seed data script
7. Convert TypeScript data to JSON format
8. Populate database with initial data

**Deliverables:**
- Complete database schema created
- All tables populated with existing data
- Migration scripts version-controlled

---

### Phase 3: API Development - Read Operations (Day 6-8)

**Tasks:**
1. Implement GET endpoints for all resources
2. Create service layer for business logic
3. Add pagination for list endpoints
4. Implement filtering and sorting
5. Add comprehensive error handling
6. Write unit tests for read operations
7. Generate OpenAPI documentation
8. Test all endpoints with Postman/Thunder Client

**Deliverables:**
- All read endpoints functional
- API documentation auto-generated
- Unit tests passing

---

### Phase 4: API Development - Write Operations (Day 9-11)

**Tasks:**
1. Implement POST endpoint for lead submissions
2. **Build AI prompt formatter** for dual data storage
3. Add email notification on new lead (EmailJS integration)
4. Implement admin endpoints (POST, PUT, DELETE)
5. Add API key authentication for admin routes
6. Add request validation
7. Write unit tests for write operations
8. Test lead submission flow end-to-end
9. **Test AI prompt generation** with various service types

**Deliverables:**
- Lead submission working with dual format storage
- AI prompt generation functional
- Admin CRUD operations functional
- Authentication in place

**Key Implementation Note:**

The lead submission endpoint must automatically generate both formats:
- Store raw `answers` JSONB for querying/filtering
- Generate formatted `ai_prompt` TEXT for AI/LLM usage

Example use cases:
- **Analytics**: Query leads by specific requirements using JSONB queries
  ```sql
  SELECT * FROM leads
  WHERE answers->>'designStyle' = 'Modern/Minimalist';
  ```
- **AI Processing**: Use `ai_prompt` directly in Claude/GPT context for:
  - Generating project proposals
  - Creating initial project briefs
  - Estimating detailed requirements
  - Auto-generating client communications

---

### Phase 5: Integration & Testing (Day 12-14)

**Tasks:**
1. Setup CORS for frontend integration
2. Test API with frontend application
3. Performance testing and optimization
4. Add rate limiting
5. Setup structured logging
6. Write integration tests
7. Security audit
8. Load testing

**Deliverables:**
- Frontend successfully consuming API
- Performance benchmarks met
- Security vulnerabilities addressed

---

### Phase 6: Deployment to Vercel (Day 15-17)

**Tasks:**
1. Configure `vercel.json` for serverless deployment
2. Setup environment variables in Vercel
3. Deploy to Vercel preview environment
4. Test preview deployment
5. Configure custom domain (api.lunaxcode.site)
6. Deploy to production
7. Update frontend to use production API
8. Monitor logs and errors

**Deliverables:**
- API live on Vercel
- Frontend using production API
- Monitoring in place

---

## Business Logic: Dual Data Storage

### Overview

The Lunaxcode API implements a dual data storage strategy for lead submissions, maintaining both structured and AI-ready formats. This approach optimizes for both operational efficiency and AI/LLM integration.

### Storage Strategy

#### 1. Structured Data (`answers` field - JSONB)

**Purpose:** Machine-readable format for queries, analytics, and reporting

**Use Cases:**
- **Lead Filtering**: Find leads by specific requirements
  ```sql
  -- Find all leads wanting e-commerce features
  SELECT * FROM leads
  WHERE answers @> '{"features": ["E-commerce"]}';

  -- Find mobile app leads for iOS
  SELECT * FROM leads
  WHERE service_type = 'basic_mobile_app'
    AND answers @> '{"platforms": ["iOS (iPhone/iPad)"]}';
  ```

- **Analytics & Reporting**:
  ```sql
  -- Most popular design styles
  SELECT answers->>'designStyle' as style, COUNT(*) as count
  FROM leads
  WHERE service_type = 'landing_page'
  GROUP BY style
  ORDER BY count DESC;

  -- Average features requested per service
  SELECT service_type,
         AVG(jsonb_array_length(answers->'features')) as avg_features
  FROM leads
  GROUP BY service_type;
  ```

- **Lead Qualification**: Programmatically assess lead complexity
- **CRM Integration**: Export structured data to external systems
- **Automated Workflows**: Trigger actions based on specific answers

#### 2. AI-Formatted Prompt (`ai_prompt` field - TEXT)

**Purpose:** Human-readable format optimized for AI/LLM processing

**Use Cases:**

1. **Project Brief Generation**
   ```
   Use ai_prompt directly in Claude/GPT to generate:
   - Detailed project proposals
   - Statement of work documents
   - Client presentations
   ```

2. **Requirement Analysis**
   ```
   Feed ai_prompt to LLM to:
   - Identify missing requirements
   - Suggest additional features
   - Estimate accurate timelines
   - Flag potential challenges
   ```

3. **Client Communication**
   ```
   Generate personalized responses:
   - Quote confirmations
   - Project kickoff emails
   - Technical feasibility assessments
   ```

4. **AI-Assisted Development**
   ```
   Use as context for:
   - Generating initial code scaffolding
   - Creating design mockups prompts
   - Writing user stories
   ```

### Implementation Details

#### Automatic Generation

When a lead is submitted via `POST /api/v1/leads`, the API:

1. **Validates** the structured `answers` against the service's question schema
2. **Fetches** pricing and timeline information
3. **Generates** the `ai_prompt` by formatting:
   - Contact information
   - Service details
   - All answered questions with labels
   - Pricing and timeline context
4. **Stores** both formats in a single database transaction

#### Prompt Format Template

```text
Project: [Service Name] for [Client Name] ([Company])
Service Type: [Service Name]
Email: [Email]
Phone: [Phone]

Project Description:
[Project Description]

Requirements:
- [Question Label 1]: [Answer 1]
- [Question Label 2]: [Answer 2]
- [Question Label 3]: [Answer 3]
...

Timeline: [Delivery Timeline]
Price: ₱[Price]
```

### Example Workflow

#### Scenario: New Landing Page Lead

**Input (Frontend Submission):**
```json
{
  "service_type": "landing_page",
  "full_name": "Maria Santos",
  "email": "maria@techstartup.ph",
  "phone": "+63 917 123 4567",
  "company": "TechStartup PH",
  "project_description": "Product launch for new SaaS platform",
  "answers": {
    "pageType": "Product Launch",
    "designStyle": "Tech/Startup",
    "sections": ["Hero Section", "Features/Benefits", "Pricing", "FAQ"],
    "ctaGoal": "Sign up for beta access"
  }
}
```

**Stored in Database:**

1. **Structured Format (`answers`):**
   ```json
   {
     "pageType": "Product Launch",
     "designStyle": "Tech/Startup",
     "sections": ["Hero Section", "Features/Benefits", "Pricing", "FAQ"],
     "ctaGoal": "Sign up for beta access"
   }
   ```

2. **AI Format (`ai_prompt`):**
   ```text
   Project: Landing Page for Maria Santos (TechStartup PH)
   Service Type: Landing Page
   Email: maria@techstartup.ph
   Phone: +63 917 123 4567

   Project Description:
   Product launch for new SaaS platform

   Requirements:
   - What type of landing page?: Product Launch
   - Preferred design style: Tech/Startup
   - Required sections: Hero Section, Features/Benefits, Pricing, FAQ
   - Primary call-to-action goal: Sign up for beta access

   Timeline: 48-hour delivery
   Price: ₱8,000
   ```

**Business Operations:**

1. **Admin Dashboard**: Query by design style to batch similar projects
   ```sql
   SELECT * FROM leads
   WHERE answers->>'designStyle' = 'Tech/Startup'
   AND status = 'new'
   ORDER BY created_at DESC;
   ```

2. **AI Project Brief**: Feed `ai_prompt` to Claude
   ```
   Based on this project request, create a detailed proposal:

   [ai_prompt content]

   Include: technical approach, design recommendations, content structure, and timeline breakdown.
   ```

3. **Email Notification**: Include both formats
   - Human reads the `ai_prompt`
   - System processes the `answers` for workflow automation

### Benefits

| Aspect | Structured (`answers`) | AI Prompt (`ai_prompt`) |
|--------|----------------------|------------------------|
| **Querying** | ✅ Fast JSONB queries | ❌ Full-text search only |
| **Analytics** | ✅ Aggregations, reports | ❌ Not suitable |
| **AI Processing** | ⚠️ Requires formatting | ✅ Ready to use |
| **Human Readability** | ❌ Technical | ✅ Natural language |
| **API Integrations** | ✅ Standard JSON | ⚠️ Needs parsing |
| **Storage Size** | ✅ Compact | ⚠️ Larger |

### Future Enhancements

1. **AI Prompt Templates**: Customizable per service type
2. **Multi-language Support**: Generate prompts in different languages
3. **Prompt Versioning**: Track format changes over time
4. **Automated AI Analysis**: Run AI analysis on submission and store results
5. **Smart Lead Scoring**: Use AI to score lead quality based on prompt content

---

## Deployment Strategy

### Vercel Configuration

#### vercel.json
```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    }
  ],
  "env": {
    "PYTHON_VERSION": "3.11"
  }
}
```

#### api/index.py (Vercel Handler)
```python
from api.main import app
from mangum import Mangum

# Vercel serverless handler
handler = Mangum(app)
```

### Environment Variables

**Required Variables:**
```bash
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/lunaxcode
CORS_ORIGINS=https://lunaxcode.site,http://localhost:3000
API_KEY=your-secure-admin-api-key-here
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Vercel Setup:**
1. Go to Vercel Dashboard → Project → Settings → Environment Variables
2. Add all required variables
3. Separate values for Development, Preview, Production

### Database Setup (Neon)

1. **Create Neon Project:**
   - Go to https://neon.tech
   - Create new project: "lunaxcode-api"
   - Copy connection string

2. **Configure Connection:**
   - Add `?sslmode=require` to connection string
   - Enable connection pooling
   - Set idle timeout to 300s

3. **Run Migrations:**
   ```bash
   # From local machine
   alembic upgrade head
   ```

4. **Seed Initial Data:**
   ```bash
   python scripts/seed_data.py
   ```

---

## Security & Best Practices

### Authentication Strategy

**Public Endpoints (No Auth):**
- GET `/api/v1/pricing`
- GET `/api/v1/addons`
- GET `/api/v1/services`
- GET `/api/v1/features`
- GET `/api/v1/company`
- GET `/api/v1/onboarding/questions/{service_type}`
- POST `/api/v1/leads`
- GET `/api/v1/health`

**Admin Endpoints (API Key Auth):**
- All POST, PUT, DELETE operations except lead submissions
- GET `/api/v1/leads`

**API Key Implementation:**
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### Input Validation

**Pydantic Models:**
- Email validation for leads
- Phone number format validation
- Required field enforcement
- Type coercion and validation
- Custom validators for business rules

**Example:**
```python
from pydantic import BaseModel, EmailStr, validator

class LeadCreate(BaseModel):
    service_type: str
    full_name: str
    email: EmailStr
    phone: Optional[str]
    project_description: str
    answers: dict

    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.startswith('+63'):
            raise ValueError('Phone must be Philippine number')
        return v
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/leads")
@limiter.limit("5/minute")  # 5 submissions per minute
async def create_lead(lead: LeadCreate):
    ...
```

### SQL Injection Prevention

- Use SQLAlchemy ORM exclusively (no raw SQL)
- Parameterized queries automatically
- Input validation via Pydantic

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### Error Handling

```python
from fastapi import HTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

---

## Data Migration Plan

### Step 1: Convert TypeScript to JSON

**Script: `scripts/convert_ts_to_json.py`**
```python
import json
import re

def extract_ts_data(file_path):
    """Extract data from TypeScript export files"""
    with open(file_path, 'r') as f:
        content = f.read()

    # Remove TypeScript syntax
    content = re.sub(r'export const \w+ = ', '', content)
    content = re.sub(r' as const;', '', content)

    # Convert to valid JSON
    data = eval(content)  # Careful: only use with trusted data
    return data

# Convert each file
pricing_data = extract_ts_data('../src/data/pricing.ts')
with open('seed_data/pricing.json', 'w') as f:
    json.dump(pricing_data, f, indent=2)

# Repeat for all data files
```

### Step 2: Seed Database

**Script: `scripts/seed_data.py`**
```python
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from api.models import PricingPlan, Addon, Service, Feature, CompanyInfo, OnboardingQuestion

def seed_database():
    engine = create_engine(DATABASE_URL)
    session = Session(engine)

    # Load JSON data
    with open('seed_data/pricing.json') as f:
        pricing_data = json.load(f)

    # Insert pricing plans
    for item in pricing_data:
        plan = PricingPlan(**item)
        session.add(plan)

    # Repeat for all tables
    session.commit()
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
```

### Step 3: Verification

```python
def verify_data():
    """Verify all data migrated correctly"""
    session = Session(engine)

    assert session.query(PricingPlan).count() == 5
    assert session.query(Addon).count() == 3
    assert session.query(Service).count() == 5
    assert session.query(Feature).count() == 6
    assert session.query(CompanyInfo).count() == 1
    assert session.query(OnboardingQuestion).count() == 5

    print("✅ All data verified!")
```

---

## Testing Strategy

### Unit Tests

**Test Coverage Goals:**
- Models: 100%
- Routers: 90%
- Services: 90%
- Overall: 85%+

**Example Test:**
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_pricing_plans(client: AsyncClient):
    response = await client.get("/api/v1/pricing")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["id"] == "landing_page"

@pytest.mark.asyncio
async def test_create_lead(client: AsyncClient):
    lead_data = {
        "service_type": "landing_page",
        "full_name": "Test User",
        "email": "test@example.com",
        "project_description": "Test project",
        "answers": {"pageType": "Product Launch"}
    }
    response = await client.post("/api/v1/leads", json=lead_data)
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
```

### Integration Tests

- Test database transactions
- Test email notifications
- Test error scenarios
- Test authentication flow

### Load Testing

```bash
# Using Apache Bench
ab -n 1000 -c 10 https://api.lunaxcode.site/api/v1/pricing

# Using wrk
wrk -t4 -c100 -d30s https://api.lunaxcode.site/api/v1/pricing
```

**Performance Targets:**
- Response time: <200ms (p95)
- Throughput: >100 req/sec
- Error rate: <0.1%

---

## Dependencies

### requirements.txt
```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic[email]==2.5.0
python-dotenv==1.0.0

# Database
sqlalchemy==2.0.25
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.9

# Vercel Deployment
mangum==0.17.0

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
slowapi==0.1.9

# Utilities
python-multipart==0.0.6
email-validator==2.1.0

# Development
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
black==23.12.1
flake8==7.0.0
mypy==1.8.0

# Monitoring (Optional)
sentry-sdk==1.39.1
```

---

## Seed Data Reference

This section contains the complete seed data from the current website that will populate the database tables.

### 1. Pricing Plans Data

```json
[
  {
    "id": "landing_page",
    "name": "Landing Page",
    "price": 8000,
    "currency": "PHP",
    "timeline": "48-hour delivery",
    "features": [
      "1 Professional Landing Page",
      "AI Chat Widget Integration",
      "Mobile Responsive Design",
      "Basic SEO Optimization",
      "Google Analytics Setup",
      "1 Round of Revisions"
    ],
    "popular": false
  },
  {
    "id": "basic_website",
    "name": "Basic Website",
    "price": 18000,
    "currency": "PHP",
    "timeline": "5-7 days delivery",
    "features": [
      "3-5 Static Pages",
      "AI Chat Widget",
      "Mobile Responsive Design",
      "SEO Optimization",
      "Analytics Integration",
      "Contact Forms",
      "2 Rounds of Revisions"
    ],
    "popular": false
  },
  {
    "id": "advanced_website",
    "name": "Advanced Website",
    "price": 40000,
    "currency": "PHP",
    "timeline": "2-3 weeks delivery",
    "features": [
      "8-12 Pages",
      "Content Management System",
      "Advanced AI Features",
      "Advanced SEO & Analytics",
      "Blog Setup",
      "E-commerce Ready",
      "3 Rounds of Revisions"
    ],
    "popular": false
  },
  {
    "id": "basic_mobile_app",
    "name": "Basic Mobile App",
    "price": 80000,
    "currency": "PHP",
    "timeline": "4-6 weeks delivery",
    "features": [
      "iOS + Android (Cross-platform)",
      "Basic UI/UX Design",
      "Core Functionality",
      "AI Integration",
      "App Store Submission",
      "Basic Analytics",
      "3 Months Support"
    ],
    "popular": false
  },
  {
    "id": "advanced_mobile_app",
    "name": "Advanced Mobile App",
    "price": 150000,
    "currency": "PHP",
    "timeline": "8-12 weeks delivery",
    "features": [
      "iOS + Android (Cross-platform)",
      "Custom UI/UX Design",
      "Backend Integration",
      "Push Notifications",
      "Advanced AI Features",
      "Payment Integration",
      "6 Months Support"
    ],
    "popular": false
  }
]
```

### 2. Add-ons Data

```json
[
  {
    "name": "Additional Pages",
    "price_range": "1500-2000",
    "currency": "PHP",
    "unit": "each"
  },
  {
    "name": "AI Content Generation",
    "price_range": "3000-5000",
    "currency": "PHP",
    "unit": "project"
  },
  {
    "name": "Monthly Maintenance",
    "price_range": "3000-5000",
    "currency": "PHP",
    "unit": "monthly"
  }
]
```

### 3. Services Data

```json
[
  {
    "id": "landing_page",
    "name": "Landing Page",
    "description": "48-Hour Landing Pages",
    "details": "While competitors take 3-5 days minimum, we deliver professional landing pages in just 48 hours. No compromises on quality.",
    "icon": "⚡",
    "timeline": "48 hours"
  },
  {
    "id": "basic_website",
    "name": "Basic Website",
    "description": "Full Website Development",
    "details": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
    "icon": "🌐",
    "timeline": "5-7 days"
  },
  {
    "id": "advanced_website",
    "name": "Advanced Website",
    "description": "Full Website Development",
    "details": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
    "icon": "🌐",
    "timeline": "2-3 weeks"
  },
  {
    "id": "basic_mobile_app",
    "name": "Basic Mobile App",
    "description": "Mobile App Development",
    "details": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
    "icon": "📱",
    "timeline": "4-6 weeks"
  },
  {
    "id": "advanced_mobile_app",
    "name": "Advanced Mobile App",
    "description": "Mobile App Development",
    "details": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
    "icon": "📱",
    "timeline": "8-12 weeks"
  }
]
```

### 4. Features Data

```json
[
  {
    "icon": "⚡",
    "title": "48-Hour Landing Pages",
    "description": "While competitors take 3-5 days minimum, we deliver professional landing pages in just 48 hours. No compromises on quality.",
    "display_order": 1
  },
  {
    "icon": "🌐",
    "title": "Full Website Development",
    "description": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
    "display_order": 2
  },
  {
    "icon": "📱",
    "title": "Mobile App Development",
    "description": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
    "display_order": 3
  },
  {
    "icon": "🤖",
    "title": "AI Integration Included",
    "description": "Every project comes with intelligent AI features - chat widgets for websites, smart features for mobile apps.",
    "display_order": 4
  },
  {
    "icon": "💰",
    "title": "SME-Friendly Pricing",
    "description": "Starting at just ₱8,000 for landing pages, ₱18,000 for websites, and ₱80,000 for mobile apps. Affordable for all business sizes.",
    "display_order": 5
  },
  {
    "icon": "🔧",
    "title": "AI-Powered Development",
    "description": "Using cutting-edge AI tools to accelerate development while maintaining high quality and modern design standards across all services.",
    "display_order": 6
  }
]
```

### 5. Company Info Data

```json
{
  "id": 1,
  "name": "Lunaxcode",
  "tagline": "Code at the Speed of Light",
  "description": "Professional websites and mobile apps for Filipino SMEs",
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

### 6. Onboarding Questions Data

#### Landing Page Questions
```json
{
  "service_type": "landing_page",
  "title": "Landing Page Requirements",
  "questions": [
    {
      "id": "pageType",
      "label": "What type of landing page?",
      "type": "select",
      "options": [
        "Product Launch",
        "Lead Generation",
        "Event Registration",
        "App Download",
        "Service Promotion",
        "Newsletter Signup"
      ],
      "required": true
    },
    {
      "id": "designStyle",
      "label": "Preferred design style",
      "type": "select",
      "options": [
        "Modern/Minimalist",
        "Bold/Colorful",
        "Professional/Corporate",
        "Creative/Artistic",
        "Tech/Startup"
      ],
      "required": true
    },
    {
      "id": "sections",
      "label": "Required sections",
      "type": "checkbox",
      "options": [
        "Hero Section",
        "Features/Benefits",
        "Testimonials",
        "Pricing",
        "FAQ",
        "Contact Form",
        "About Us",
        "Gallery/Portfolio"
      ],
      "required": true
    },
    {
      "id": "ctaGoal",
      "label": "Primary call-to-action goal",
      "type": "text",
      "placeholder": "e.g., Sign up for free trial, Download app, Contact sales...",
      "required": true
    }
  ]
}
```

#### Basic Website Questions
```json
{
  "service_type": "basic_website",
  "title": "Website Requirements",
  "questions": [
    {
      "id": "websiteType",
      "label": "Website type",
      "type": "select",
      "options": [
        "Corporate Website",
        "Portfolio",
        "Blog/News",
        "E-commerce",
        "Directory/Listing",
        "Educational",
        "Non-profit"
      ],
      "required": true
    },
    {
      "id": "pageCount",
      "label": "Approximate number of pages",
      "type": "select",
      "options": [
        "3-5 pages",
        "6-10 pages",
        "11-20 pages",
        "20+ pages"
      ],
      "required": true
    },
    {
      "id": "features",
      "label": "Required features",
      "type": "checkbox",
      "options": [
        "Contact Forms",
        "Blog/News Section",
        "Image Gallery",
        "Video Integration",
        "Social Media Integration",
        "Newsletter Signup",
        "Online Booking",
        "User Accounts"
      ],
      "required": true
    },
    {
      "id": "contentSource",
      "label": "Content source",
      "type": "select",
      "options": [
        "I will provide all content",
        "I need help with copywriting",
        "Mix of both"
      ],
      "required": true
    }
  ]
}
```

#### Advanced Website Questions
```json
{
  "service_type": "advanced_website",
  "title": "Advanced Website Requirements",
  "questions": [
    {
      "id": "websiteType",
      "label": "Website type",
      "type": "select",
      "options": [
        "Corporate Website",
        "Portfolio",
        "Blog/News",
        "E-commerce",
        "Directory/Listing",
        "Educational",
        "Non-profit"
      ],
      "required": true
    },
    {
      "id": "pageCount",
      "label": "Approximate number of pages",
      "type": "select",
      "options": [
        "3-5 pages",
        "6-10 pages",
        "11-20 pages",
        "20+ pages"
      ],
      "required": true
    },
    {
      "id": "features",
      "label": "Required features",
      "type": "checkbox",
      "options": [
        "Contact Forms",
        "Blog/News Section",
        "Image Gallery",
        "Video Integration",
        "Social Media Integration",
        "Newsletter Signup",
        "Online Booking",
        "User Accounts",
        "CMS",
        "E-commerce",
        "Multi-language"
      ],
      "required": true
    },
    {
      "id": "contentSource",
      "label": "Content source",
      "type": "select",
      "options": [
        "I will provide all content",
        "I need help with copywriting",
        "Mix of both"
      ],
      "required": true
    }
  ]
}
```

#### Basic Mobile App Questions
```json
{
  "service_type": "basic_mobile_app",
  "title": "Mobile App Requirements",
  "questions": [
    {
      "id": "appCategory",
      "label": "App category",
      "type": "select",
      "options": [
        "Business/Productivity",
        "Social Networking",
        "E-commerce/Shopping",
        "Health/Fitness",
        "Education",
        "Entertainment",
        "Finance",
        "Food & Drink"
      ],
      "required": true
    },
    {
      "id": "platforms",
      "label": "Target platforms",
      "type": "checkbox",
      "options": [
        "iOS (iPhone/iPad)",
        "Android",
        "Both Platforms"
      ],
      "required": true
    },
    {
      "id": "coreFeatures",
      "label": "Core features needed",
      "type": "checkbox",
      "options": [
        "User Registration/Login",
        "Push Notifications",
        "Offline Mode",
        "Camera/Photos",
        "GPS/Location",
        "Social Sharing",
        "In-app Purchases",
        "Real-time Chat"
      ],
      "required": true
    },
    {
      "id": "backend",
      "label": "Backend requirements",
      "type": "checkbox",
      "options": [
        "User Management",
        "Data Storage",
        "Push Notifications",
        "Analytics",
        "Payment Processing",
        "File Storage",
        "API Integration"
      ],
      "required": true
    }
  ]
}
```

#### Advanced Mobile App Questions
```json
{
  "service_type": "advanced_mobile_app",
  "title": "Advanced Mobile App Requirements",
  "questions": [
    {
      "id": "appCategory",
      "label": "App category",
      "type": "select",
      "options": [
        "Business/Productivity",
        "Social Networking",
        "E-commerce/Shopping",
        "Health/Fitness",
        "Education",
        "Entertainment",
        "Finance",
        "Food & Drink"
      ],
      "required": true
    },
    {
      "id": "platforms",
      "label": "Target platforms",
      "type": "checkbox",
      "options": [
        "iOS (iPhone/iPad)",
        "Android",
        "Both Platforms"
      ],
      "required": true
    },
    {
      "id": "coreFeatures",
      "label": "Core features needed",
      "type": "checkbox",
      "options": [
        "User Registration/Login",
        "Push Notifications",
        "Offline Mode",
        "Camera/Photos",
        "GPS/Location",
        "Social Sharing",
        "In-app Purchases",
        "Real-time Chat",
        "Advanced Analytics",
        "Custom Integrations"
      ],
      "required": true
    },
    {
      "id": "backend",
      "label": "Backend requirements",
      "type": "checkbox",
      "options": [
        "User Management",
        "Data Storage",
        "Push Notifications",
        "Analytics",
        "Payment Processing",
        "File Storage",
        "API Integration",
        "Real-time Features",
        "Advanced Security"
      ],
      "required": true
    }
  ]
}
```

### Complete Seed Script

**File: `scripts/seed_data.py`**

```python
"""
Seed script to populate the Lunaxcode API database with initial data.
Run this after creating the database schema with Alembic migrations.

Usage: python scripts/seed_data.py
"""

import json
import sys
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

# Add parent directory to path to import api modules
sys.path.append(str(Path(__file__).parent.parent))

from api.models import (
    PricingPlan, Addon, Service, Feature,
    CompanyInfo, OnboardingQuestion
)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable not set")

# Seed data
PRICING_PLANS = [
    {
        "id": "landing_page",
        "name": "Landing Page",
        "price": 8000,
        "currency": "PHP",
        "timeline": "48-hour delivery",
        "features": [
            "1 Professional Landing Page",
            "AI Chat Widget Integration",
            "Mobile Responsive Design",
            "Basic SEO Optimization",
            "Google Analytics Setup",
            "1 Round of Revisions"
        ],
        "popular": False
    },
    {
        "id": "basic_website",
        "name": "Basic Website",
        "price": 18000,
        "currency": "PHP",
        "timeline": "5-7 days delivery",
        "features": [
            "3-5 Static Pages",
            "AI Chat Widget",
            "Mobile Responsive Design",
            "SEO Optimization",
            "Analytics Integration",
            "Contact Forms",
            "2 Rounds of Revisions"
        ],
        "popular": False
    },
    {
        "id": "advanced_website",
        "name": "Advanced Website",
        "price": 40000,
        "currency": "PHP",
        "timeline": "2-3 weeks delivery",
        "features": [
            "8-12 Pages",
            "Content Management System",
            "Advanced AI Features",
            "Advanced SEO & Analytics",
            "Blog Setup",
            "E-commerce Ready",
            "3 Rounds of Revisions"
        ],
        "popular": False
    },
    {
        "id": "basic_mobile_app",
        "name": "Basic Mobile App",
        "price": 80000,
        "currency": "PHP",
        "timeline": "4-6 weeks delivery",
        "features": [
            "iOS + Android (Cross-platform)",
            "Basic UI/UX Design",
            "Core Functionality",
            "AI Integration",
            "App Store Submission",
            "Basic Analytics",
            "3 Months Support"
        ],
        "popular": False
    },
    {
        "id": "advanced_mobile_app",
        "name": "Advanced Mobile App",
        "price": 150000,
        "currency": "PHP",
        "timeline": "8-12 weeks delivery",
        "features": [
            "iOS + Android (Cross-platform)",
            "Custom UI/UX Design",
            "Backend Integration",
            "Push Notifications",
            "Advanced AI Features",
            "Payment Integration",
            "6 Months Support"
        ],
        "popular": False
    }
]

ADDONS = [
    {
        "name": "Additional Pages",
        "price_range": "1500-2000",
        "currency": "PHP",
        "unit": "each"
    },
    {
        "name": "AI Content Generation",
        "price_range": "3000-5000",
        "currency": "PHP",
        "unit": "project"
    },
    {
        "name": "Monthly Maintenance",
        "price_range": "3000-5000",
        "currency": "PHP",
        "unit": "monthly"
    }
]

SERVICES = [
    {
        "id": "landing_page",
        "name": "Landing Page",
        "description": "48-Hour Landing Pages",
        "details": "While competitors take 3-5 days minimum, we deliver professional landing pages in just 48 hours. No compromises on quality.",
        "icon": "⚡",
        "timeline": "48 hours"
    },
    {
        "id": "basic_website",
        "name": "Basic Website",
        "description": "Full Website Development",
        "details": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
        "icon": "🌐",
        "timeline": "5-7 days"
    },
    {
        "id": "advanced_website",
        "name": "Advanced Website",
        "description": "Full Website Development",
        "details": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
        "icon": "🌐",
        "timeline": "2-3 weeks"
    },
    {
        "id": "basic_mobile_app",
        "name": "Basic Mobile App",
        "description": "Mobile App Development",
        "details": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
        "icon": "📱",
        "timeline": "4-6 weeks"
    },
    {
        "id": "advanced_mobile_app",
        "name": "Advanced Mobile App",
        "description": "Mobile App Development",
        "details": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
        "icon": "📱",
        "timeline": "8-12 weeks"
    }
]

FEATURES = [
    {
        "icon": "⚡",
        "title": "48-Hour Landing Pages",
        "description": "While competitors take 3-5 days minimum, we deliver professional landing pages in just 48 hours. No compromises on quality.",
        "display_order": 1
    },
    {
        "icon": "🌐",
        "title": "Full Website Development",
        "description": "Complete websites with CMS, advanced SEO, and multi-page functionality delivered in 5 days to 3 weeks depending on complexity.",
        "display_order": 2
    },
    {
        "icon": "📱",
        "title": "Mobile App Development",
        "description": "Cross-platform iOS and Android apps with modern UI/UX, backend integration, and push notifications in 4-12 weeks.",
        "display_order": 3
    },
    {
        "icon": "🤖",
        "title": "AI Integration Included",
        "description": "Every project comes with intelligent AI features - chat widgets for websites, smart features for mobile apps.",
        "display_order": 4
    },
    {
        "icon": "💰",
        "title": "SME-Friendly Pricing",
        "description": "Starting at just ₱8,000 for landing pages, ₱18,000 for websites, and ₱80,000 for mobile apps. Affordable for all business sizes.",
        "display_order": 5
    },
    {
        "icon": "🔧",
        "title": "AI-Powered Development",
        "description": "Using cutting-edge AI tools to accelerate development while maintaining high quality and modern design standards across all services.",
        "display_order": 6
    }
]

COMPANY_INFO = {
    "id": 1,
    "name": "Lunaxcode",
    "tagline": "Code at the Speed of Light",
    "description": "Professional websites and mobile apps for Filipino SMEs",
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

ONBOARDING_QUESTIONS = [
    {
        "service_type": "landing_page",
        "title": "Landing Page Requirements",
        "questions": [
            {
                "id": "pageType",
                "label": "What type of landing page?",
                "type": "select",
                "options": ["Product Launch", "Lead Generation", "Event Registration", "App Download", "Service Promotion", "Newsletter Signup"],
                "required": True
            },
            {
                "id": "designStyle",
                "label": "Preferred design style",
                "type": "select",
                "options": ["Modern/Minimalist", "Bold/Colorful", "Professional/Corporate", "Creative/Artistic", "Tech/Startup"],
                "required": True
            },
            {
                "id": "sections",
                "label": "Required sections",
                "type": "checkbox",
                "options": ["Hero Section", "Features/Benefits", "Testimonials", "Pricing", "FAQ", "Contact Form", "About Us", "Gallery/Portfolio"],
                "required": True
            },
            {
                "id": "ctaGoal",
                "label": "Primary call-to-action goal",
                "type": "text",
                "placeholder": "e.g., Sign up for free trial, Download app, Contact sales...",
                "required": True
            }
        ]
    },
    {
        "service_type": "basic_website",
        "title": "Website Requirements",
        "questions": [
            {
                "id": "websiteType",
                "label": "Website type",
                "type": "select",
                "options": ["Corporate Website", "Portfolio", "Blog/News", "E-commerce", "Directory/Listing", "Educational", "Non-profit"],
                "required": True
            },
            {
                "id": "pageCount",
                "label": "Approximate number of pages",
                "type": "select",
                "options": ["3-5 pages", "6-10 pages", "11-20 pages", "20+ pages"],
                "required": True
            },
            {
                "id": "features",
                "label": "Required features",
                "type": "checkbox",
                "options": ["Contact Forms", "Blog/News Section", "Image Gallery", "Video Integration", "Social Media Integration", "Newsletter Signup", "Online Booking", "User Accounts"],
                "required": True
            },
            {
                "id": "contentSource",
                "label": "Content source",
                "type": "select",
                "options": ["I will provide all content", "I need help with copywriting", "Mix of both"],
                "required": True
            }
        ]
    },
    {
        "service_type": "advanced_website",
        "title": "Advanced Website Requirements",
        "questions": [
            {
                "id": "websiteType",
                "label": "Website type",
                "type": "select",
                "options": ["Corporate Website", "Portfolio", "Blog/News", "E-commerce", "Directory/Listing", "Educational", "Non-profit"],
                "required": True
            },
            {
                "id": "pageCount",
                "label": "Approximate number of pages",
                "type": "select",
                "options": ["3-5 pages", "6-10 pages", "11-20 pages", "20+ pages"],
                "required": True
            },
            {
                "id": "features",
                "label": "Required features",
                "type": "checkbox",
                "options": ["Contact Forms", "Blog/News Section", "Image Gallery", "Video Integration", "Social Media Integration", "Newsletter Signup", "Online Booking", "User Accounts", "CMS", "E-commerce", "Multi-language"],
                "required": True
            },
            {
                "id": "contentSource",
                "label": "Content source",
                "type": "select",
                "options": ["I will provide all content", "I need help with copywriting", "Mix of both"],
                "required": True
            }
        ]
    },
    {
        "service_type": "basic_mobile_app",
        "title": "Mobile App Requirements",
        "questions": [
            {
                "id": "appCategory",
                "label": "App category",
                "type": "select",
                "options": ["Business/Productivity", "Social Networking", "E-commerce/Shopping", "Health/Fitness", "Education", "Entertainment", "Finance", "Food & Drink"],
                "required": True
            },
            {
                "id": "platforms",
                "label": "Target platforms",
                "type": "checkbox",
                "options": ["iOS (iPhone/iPad)", "Android", "Both Platforms"],
                "required": True
            },
            {
                "id": "coreFeatures",
                "label": "Core features needed",
                "type": "checkbox",
                "options": ["User Registration/Login", "Push Notifications", "Offline Mode", "Camera/Photos", "GPS/Location", "Social Sharing", "In-app Purchases", "Real-time Chat"],
                "required": True
            },
            {
                "id": "backend",
                "label": "Backend requirements",
                "type": "checkbox",
                "options": ["User Management", "Data Storage", "Push Notifications", "Analytics", "Payment Processing", "File Storage", "API Integration"],
                "required": True
            }
        ]
    },
    {
        "service_type": "advanced_mobile_app",
        "title": "Advanced Mobile App Requirements",
        "questions": [
            {
                "id": "appCategory",
                "label": "App category",
                "type": "select",
                "options": ["Business/Productivity", "Social Networking", "E-commerce/Shopping", "Health/Fitness", "Education", "Entertainment", "Finance", "Food & Drink"],
                "required": True
            },
            {
                "id": "platforms",
                "label": "Target platforms",
                "type": "checkbox",
                "options": ["iOS (iPhone/iPad)", "Android", "Both Platforms"],
                "required": True
            },
            {
                "id": "coreFeatures",
                "label": "Core features needed",
                "type": "checkbox",
                "options": ["User Registration/Login", "Push Notifications", "Offline Mode", "Camera/Photos", "GPS/Location", "Social Sharing", "In-app Purchases", "Real-time Chat", "Advanced Analytics", "Custom Integrations"],
                "required": True
            },
            {
                "id": "backend",
                "label": "Backend requirements",
                "type": "checkbox",
                "options": ["User Management", "Data Storage", "Push Notifications", "Analytics", "Payment Processing", "File Storage", "API Integration", "Real-time Features", "Advanced Security"],
                "required": True
            }
        ]
    }
]


def seed_database():
    """Populate database with initial data"""
    print("🌱 Starting database seeding...")

    engine = create_engine(DATABASE_URL)
    session = Session(engine)

    try:
        # Clear existing data (optional - comment out for production)
        print("🗑️  Clearing existing data...")
        session.query(OnboardingQuestion).delete()
        session.query(CompanyInfo).delete()
        session.query(Feature).delete()
        session.query(Service).delete()
        session.query(Addon).delete()
        session.query(PricingPlan).delete()
        session.commit()

        # Insert Services first (referenced by other tables)
        print("📦 Inserting services...")
        for service_data in SERVICES:
            service = Service(**service_data)
            session.add(service)
        session.commit()
        print(f"✅ Inserted {len(SERVICES)} services")

        # Insert Pricing Plans
        print("💰 Inserting pricing plans...")
        for plan_data in PRICING_PLANS:
            plan = PricingPlan(**plan_data)
            session.add(plan)
        session.commit()
        print(f"✅ Inserted {len(PRICING_PLANS)} pricing plans")

        # Insert Add-ons
        print("🔧 Inserting add-ons...")
        for addon_data in ADDONS:
            addon = Addon(**addon_data)
            session.add(addon)
        session.commit()
        print(f"✅ Inserted {len(ADDONS)} add-ons")

        # Insert Features
        print("⭐ Inserting features...")
        for feature_data in FEATURES:
            feature = Feature(**feature_data)
            session.add(feature)
        session.commit()
        print(f"✅ Inserted {len(FEATURES)} features")

        # Insert Company Info
        print("🏢 Inserting company info...")
        company = CompanyInfo(**COMPANY_INFO)
        session.add(company)
        session.commit()
        print("✅ Inserted company info")

        # Insert Onboarding Questions
        print("📝 Inserting onboarding questions...")
        for question_data in ONBOARDING_QUESTIONS:
            question = OnboardingQuestion(**question_data)
            session.add(question)
        session.commit()
        print(f"✅ Inserted {len(ONBOARDING_QUESTIONS)} question sets")

        print("\n🎉 Database seeding completed successfully!")

        # Verify counts
        print("\n📊 Verification:")
        print(f"  - Services: {session.query(Service).count()}")
        print(f"  - Pricing Plans: {session.query(PricingPlan).count()}")
        print(f"  - Add-ons: {session.query(Addon).count()}")
        print(f"  - Features: {session.query(Feature).count()}")
        print(f"  - Company Info: {session.query(CompanyInfo).count()}")
        print(f"  - Onboarding Questions: {session.query(OnboardingQuestion).count()}")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
```

### Usage Instructions

1. **After creating database schema:**
   ```bash
   # Run migrations
   alembic upgrade head

   # Seed the database
   python scripts/seed_data.py
   ```

2. **To re-seed (development only):**
   ```bash
   # The script includes deletion of existing data
   # Uncomment the deletion section in seed_data.py
   python scripts/seed_data.py
   ```

3. **Verify data:**
   ```bash
   # Connect to Neon database
   psql $DATABASE_URL

   # Check table counts
   SELECT 'pricing_plans' as table, COUNT(*) FROM pricing_plans
   UNION ALL
   SELECT 'addons', COUNT(*) FROM addons
   UNION ALL
   SELECT 'services', COUNT(*) FROM services
   UNION ALL
   SELECT 'features', COUNT(*) FROM features
   UNION ALL
   SELECT 'company_info', COUNT(*) FROM company_info
   UNION ALL
   SELECT 'onboarding_questions', COUNT(*) FROM onboarding_questions;
   ```

---

## Next Steps

### Immediate Actions

1. **Create Repository**
   ```bash
   mkdir lunaxcode-api
   cd lunaxcode-api
   git init
   git remote add origin <repository-url>
   ```

2. **Setup Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create Neon Database**
   - Sign up at https://neon.tech
   - Create project: "lunaxcode-api"
   - Copy DATABASE_URL

4. **Initialize Alembic**
   ```bash
   alembic init alembic
   # Edit alembic.ini with DATABASE_URL
   ```

5. **Create First Migration**
   ```bash
   alembic revision --autogenerate -m "Initial schema"
   alembic upgrade head
   ```

### Development Workflow

1. **Local Development**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

2. **Run Tests**
   ```bash
   pytest tests/ -v --cov=api
   ```

3. **Check Code Quality**
   ```bash
   black api/
   flake8 api/
   mypy api/
   ```

4. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

### Frontend Integration

**Update DataService.ts:**
```typescript
// src/lib/data-service.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class DataService {
  static async getPricingPlans() {
    const response = await fetch(`${API_BASE_URL}/pricing`);
    return response.json();
  }

  static async submitLead(leadData: LeadSubmission) {
    const response = await fetch(`${API_BASE_URL}/leads`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leadData)
    });
    return response.json();
  }
}
```

---

## Success Criteria

### Technical Metrics
- ✅ All endpoints functional and documented
- ✅ Test coverage >85%
- ✅ API response time <200ms (p95)
- ✅ Zero SQL injection vulnerabilities
- ✅ Successful Vercel deployment

### Business Metrics
- ✅ Lead submissions working end-to-end
- ✅ Frontend successfully migrated from static data
- ✅ Admin can manage content via API
- ✅ Email notifications on new leads
- ✅ System scalable to 1000+ requests/hour

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Vercel cold starts | Performance | Use connection pooling, optimize imports |
| Database connection limits | Availability | Use Neon's connection pooling, implement retry logic |
| API rate limiting | User experience | Implement graceful degradation, caching |
| Data migration errors | Data integrity | Thorough testing, backup before migration |
| CORS issues | Integration failure | Test cross-origin requests early |

---

## Maintenance Plan

### Regular Tasks
- **Daily:** Monitor error logs, check API health
- **Weekly:** Review lead submissions, database performance
- **Monthly:** Security updates, dependency updates
- **Quarterly:** Performance audit, cost optimization

### Backup Strategy
- Neon automatic daily backups
- Manual backup before schema migrations
- Export critical data weekly to S3/storage

---

## Resources & References

### Documentation
- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy 2.0: https://docs.sqlalchemy.org/
- Neon Postgres: https://neon.tech/docs
- Vercel Python: https://vercel.com/docs/functions/runtimes/python

### Tools
- API Testing: Postman / Thunder Client
- Database GUI: pgAdmin / DBeaver
- Monitoring: Vercel Analytics / Sentry

---

## Appendix

### Sample Configuration Files

#### .env.example
```bash
# Database
DATABASE_URL=postgresql://user:password@ep-xxx.neon.tech/lunaxcode?sslmode=require

# API
API_KEY=your-secure-api-key-here
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# CORS
CORS_ORIGINS=http://localhost:3000,https://lunaxcode.site

# Email (Optional)
EMAILJS_SERVICE_ID=your_service_id
EMAILJS_TEMPLATE_ID=your_template_id
EMAILJS_PUBLIC_KEY=your_public_key
```

#### api/config.py
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    API_KEY: str
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Conclusion

This plan provides a comprehensive roadmap for developing and deploying the Lunaxcode API. The phased approach ensures systematic progress while maintaining quality and security standards. With proper execution, the API will be production-ready within 2-3 weeks and provide a solid foundation for future enhancements.

**Estimated Total Effort:** 17 development days (3-4 weeks with testing and deployment)

**Next Immediate Step:** Create the Git repository and initialize the project structure.