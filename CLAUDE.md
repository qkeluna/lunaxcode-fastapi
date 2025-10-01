# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI-based REST API for Lunaxcode website, replacing static TypeScript data with a Postgres-backed API deployed to Vercel as serverless functions.

**Tech Stack:**
- FastAPI (Python 3.13+) with full async support
- SQLAlchemy 2.0 async ORM with asyncpg driver
- Neon Postgres (serverless)
- Pydantic v2 for validation
- Alembic migrations (sync for compatibility)
- Vercel serverless deployment via Mangum

## Commands

### Development
```bash
# Start development server
uvicorn api.main:app --reload --port 8000

# Run single test file
pytest tests/test_pricing.py -v

# Run all tests with coverage
pytest tests/ -v --cov=api

# Watch mode for tests
pytest-watch tests/
```

### Database
```bash
# Create migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# Seed database with initial data
python scripts/seed_data.py
```

### Code Quality
```bash
# Format code
black api/ tests/

# Lint
flake8 api/ tests/

# Type checking
mypy api/
```

### Deployment
```bash
# Deploy to Vercel (production)
vercel --prod

# Deploy preview
vercel
```

## Architecture

### Project Structure
```
api/
├── main.py              # FastAPI app initialization
├── config.py            # Settings via Pydantic BaseSettings
├── database.py          # SQLAlchemy session management
├── index.py             # Vercel serverless entry point (exports FastAPI app)
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic validation schemas
├── routers/             # API route handlers
├── services/            # Business logic layer
└── utils/               # Utilities (logging, exceptions)

alembic/                 # Database migrations
scripts/                 # Utility scripts (seed_data.py)
tests/                   # Unit and integration tests
```

### Layered Architecture
1. **Router Layer** (`routers/`) - Async HTTP request handling, validation
2. **Service Layer** (`services/`) - Async business logic, AI prompt generation
3. **Model Layer** (`models/`) - Database schema via SQLAlchemy
4. **Schema Layer** (`schemas/`) - Request/response validation via Pydantic

**Important:** All routers and service functions use `async/await` with `AsyncSession` from SQLAlchemy.

### Key Business Logic: Dual Data Storage

The `leads` table stores submissions in **two formats simultaneously**:

1. **`answers` (JSONB)** - Structured data for SQL queries and analytics
2. **`ai_prompt` (TEXT)** - Human-readable format auto-generated for AI/LLM processing

**Implementation Location:** `api/services/lead_service.py`

The `format_ai_prompt()` function converts structured lead data into natural language suitable for:
- AI-generated project briefs
- Requirement analysis via Claude/GPT
- Automated client communications

When creating or modifying lead submission logic, always ensure both formats are populated correctly.

### Database Schema

**Core Tables:**
- `pricing_plans` - Service pricing with JSONB features array
- `addons` - Additional services with price ranges
- `services` - Service catalog (FK from pricing_plans)
- `features` - Marketing features with display ordering
- `company_info` - Singleton table for company details
- `onboarding_questions` - Dynamic form schemas per service
- `leads` - Customer submissions with dual storage (JSONB + AI prompt)

**Important Constraints:**
- `company_info.id = 1` (singleton constraint)
- `leads.service_type` FK to `services.id`
- `onboarding_questions.service_type` FK to `services.id`

### API Patterns

**Base URL:** `/api/v1`

**Authentication:**
- Public: All GET endpoints, POST /leads
- Admin: All POST/PUT/DELETE (except POST /leads) - requires `X-API-Key` header

**Response Structure:**
```python
# Success
{"data": [...], "count": 10}  # List endpoints
{"id": 1, "name": "..."}      # Single resource

# Error
{"detail": "Error message"}
```

**Key Endpoints:**
- `GET /pricing` - Public, returns all pricing plans
- `POST /leads` - Public, auto-generates ai_prompt field
- `GET /leads` - Admin only, returns all lead data
- `GET /onboarding/questions/{service_type}` - Public, dynamic form schemas

## Development Patterns

### Adding New Endpoints

1. Create SQLAlchemy model in `api/models/`
2. Create Pydantic schemas in `api/schemas/`
3. Create service layer in `api/services/`
4. Create router in `api/routers/`
5. Register router in `api/main.py`
6. Create Alembic migration
7. Write tests in `tests/`

### Service Layer Pattern

Services contain business logic and should:
- Accept Pydantic models or primitives
- Return ORM models or primitives
- Handle database transactions
- Raise domain-specific exceptions

Example:
```python
# api/services/lead_service.py
async def create_lead(lead_create: LeadCreate, db: AsyncSession) -> Lead:
    # Fetch related data with async
    result = await db.execute(
        select(PricingPlan).filter(PricingPlan.id == lead_create.service_type)
    )
    pricing = result.scalar_one_or_none()

    # Generate AI prompt (business logic)
    ai_prompt = format_ai_prompt(lead_create.dict(), pricing)

    # Create and persist
    lead = Lead(**lead_create.dict(), ai_prompt=ai_prompt)
    db.add(lead)
    await db.commit()
    await db.refresh(lead)
    return lead
```

### Testing Strategy

- **Unit tests** - Service layer logic, utility functions
- **Integration tests** - API endpoints with test database
- **Fixtures** - Defined in `tests/conftest.py`

Use async test client for endpoint testing:
```python
@pytest.mark.asyncio
async def test_create_lead(client: AsyncClient):
    response = await client.post("/api/v1/leads", json=lead_data)
    assert response.status_code == 201
```

## Important Conventions

### Database Sessions
Always use async dependency injection for database sessions:
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.database import get_db

@router.get("/pricing")
async def get_pricing(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PricingPlan))
    return result.scalars().all()
```

**Important Database Notes:**
- Runtime: Uses `asyncpg` driver with `postgresql+asyncpg://` URL format
- Migrations: Uses `psycopg2-binary` with `postgresql://` URL format (Alembic requires sync)
- Both `api/database.py` and `alembic/env.py` auto-convert URL formats appropriately

### Environment Variables
Required in `.env`:
- `DATABASE_URL` - Neon Postgres connection string (standard `postgresql://` format)
  - Example: `postgresql://user:pass@host.neon.tech/dbname?sslmode=require`
  - Note: Remove `channel_binding` parameter if present (not supported by asyncpg)
- `API_KEY` - Admin authentication
- `CORS_ORIGINS` - Comma-separated allowed origins
- `ENVIRONMENT` - development/production
- `LOG_LEVEL` - DEBUG/INFO/WARNING/ERROR

### Vercel Deployment
**IMPORTANT:** Vercel's `@vercel/python` runtime **natively supports ASGI applications**. Do NOT use Mangum or other adapters.

The `api/index.py` simply exports the FastAPI app:
```python
from api.main import app
__all__ = ["app"]
```

**Why no Mangum?**
- Mangum is designed for AWS Lambda, not Vercel
- Using Mangum causes `issubclass() TypeError` in Vercel's runtime wrapper
- Vercel auto-detects and serves ASGI apps directly

`vercel.json` routes all requests to `api/index.py`, which Vercel serves as an ASGI application.

### Migration Guidelines
- Always review auto-generated migrations before applying
- Test migrations on development database first
- Add data migrations separately if needed
- Never skip migrations - run sequentially

### Security Practices
- Use Pydantic validators for input sanitization
- Never expose internal errors in production
- Implement rate limiting on public endpoints (especially POST /leads)
- Use SQLAlchemy ORM exclusively (no raw SQL)
- Validate all JSONB data against schemas

## Common Tasks

### Adding a New Service Type
1. Update `services` table with new entry
2. Create corresponding `pricing_plans` entry
3. Add `onboarding_questions` for the service
4. Update seed script with new data
5. Test lead submission with new service type

### Modifying Lead Prompt Format
1. Edit `format_ai_prompt()` in `api/services/lead_service.py`
2. Test with various service types
3. Verify prompt quality for AI consumption
4. Consider backwards compatibility for existing leads

### Database Schema Changes
1. Modify ORM model in `api/models/`
2. Run `alembic revision --autogenerate -m "description"`
3. Review generated migration in `alembic/versions/`
4. Apply: `alembic upgrade head`
5. Update seed script if needed
6. Update corresponding Pydantic schemas

## Integration with Frontend

The Next.js frontend (lunaxcode-site) consumes this API. When making breaking changes:
1. Version the API if needed (`/api/v2/...`)
2. Update frontend `DataService.ts` accordingly
3. Test CORS configuration
4. Coordinate deployment timing

## Troubleshooting

**Vercel cold starts:** Keep imports lean, use connection pooling
**Database connection errors:** Check Neon connection limits, implement retry logic
**Migration conflicts:** Reset local DB and re-run migrations from scratch
**CORS issues:** Verify `CORS_ORIGINS` includes frontend URL with correct protocol
**Import errors:** Ensure relative imports work with both `uvicorn` and Vercel contexts