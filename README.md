# Lunaxcode FastAPI Backend

FastAPI-based REST API for Lunaxcode website with dual data storage pattern, replacing static TypeScript data with a Postgres-backed API deployed to Vercel.

## Tech Stack

- **Framework:** FastAPI (Python 3.11+)
- **Database:** Neon Postgres (serverless)
- **ORM:** SQLAlchemy 2.0 with Alembic migrations
- **Validation:** Pydantic v2
- **Deployment:** Vercel Serverless (via Mangum)

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update with your values:

```bash
cp .env.example .env
```

Required variables:
- `DATABASE_URL` - Neon Postgres connection string
- `API_KEY` - Admin authentication key
- `CORS_ORIGINS` - Comma-separated allowed origins

### 3. Database Setup

```bash
# Run migrations to create schema
alembic upgrade head

# Seed database with initial data
python scripts/seed_data.py
```

### 4. Run Development Server

```bash
# Start FastAPI server
uvicorn api.main:app --reload --port 8000
```

API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## Development Commands

### Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=api

# Run specific test file
pytest tests/test_pricing.py -v
```

### Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1
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

## API Architecture

### Dual Data Storage Pattern

The leads table implements a unique dual storage strategy:

1. **`answers` (JSONB)** - Structured data for SQL queries and analytics
2. **`ai_prompt` (TEXT)** - Auto-generated natural language format for AI/LLM processing

When a lead is submitted via `POST /api/v1/leads`, the API automatically:
- Validates structured answers against service question schema
- Generates human-readable AI prompt with all context
- Stores both formats in a single transaction

**Use Cases:**
- Query leads by specific requirements using JSONB operators
- Feed AI prompt directly to Claude/GPT for project briefs
- Analytics and reporting on structured data
- Automated client communication generation

### Endpoints

**Base URL:** `/api/v1`

**Public Endpoints:**
- `GET /pricing` - Get all pricing plans
- `GET /services` - Get all services
- `GET /features` - Get marketing features
- `GET /addons` - Get add-on services
- `GET /company` - Get company information
- `GET /onboarding/questions/{service_type}` - Get onboarding questions
- `POST /leads` - Submit new lead (generates AI prompt automatically)
- `GET /health` - Health check
- `GET /health/db` - Database health check

**Admin Endpoints** (require `X-API-Key` header):
- All POST/PUT/DELETE operations except lead submission
- `GET /leads` - Get all leads with filtering

## Project Structure

```
api/
├── main.py              # FastAPI app
├── config.py            # Settings
├── database.py          # DB session
├── index.py             # Vercel handler
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── routers/             # API endpoints
├── services/            # Business logic (AI prompt generation)
└── utils/               # Auth, exceptions

alembic/                 # Migrations
scripts/                 # Seed script
tests/                   # Test suite
```

## Deployment

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Set environment variables in Vercel dashboard:
   - `DATABASE_URL`
   - `API_KEY`
   - `CORS_ORIGINS`
   - `ENVIRONMENT=production`

3. Deploy:
```bash
vercel --prod
```

### Database Migrations on Production

```bash
# Run migrations against production database
DATABASE_URL="your-production-url" alembic upgrade head
```

## Key Features

### AI Prompt Generation

Located in `api/services/lead_service.py`, the `format_ai_prompt()` function converts structured lead data into natural language optimized for AI consumption.

Example output:
```
Project: Landing Page for Maria Santos (TechStartup PH)
Service Type: Landing Page
Email: maria@techstartup.ph
Phone: +63 917 123 4567

Project Description:
Product launch for new SaaS platform

Requirements:
- What type of landing page?: Product Launch
- Preferred design style: Tech/Startup
- Required sections: Hero Section, Features/Benefits, Pricing
- Primary call-to-action goal: Sign up for beta access

Timeline: 48-hour delivery
Price: ₱8,000
```

### Authentication

Admin endpoints use API key authentication via `X-API-Key` header. Implemented in `api/utils/auth.py`.

### Error Handling

- Development: Detailed error messages
- Production: Generic error messages for security
- Custom exceptions in `api/utils/exceptions.py`

## Testing

Test coverage includes:
- Health checks
- Pricing plan CRUD
- Lead submission with AI prompt generation
- Authentication
- Input validation

Run tests before committing:
```bash
pytest tests/ -v
```

## Contributing

1. Create feature branch from `main`
2. Make changes
3. Run tests and code quality checks
4. Create pull request

## License

Proprietary - Lunaxcode

## Support

For questions or issues, contact: hello@lunaxcode.site