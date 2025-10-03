# Admin Dashboard Implementation Checklist

Quick reference checklist for implementing the admin dashboard.

## 🎯 Overview
- **Backend:** Add CRUD endpoints to lunaxcode-fastapi
- **Frontend:** Build Next.js admin dashboard
- **Timeline:** ~4 weeks (1 week per phase)

---

## ✅ Phase 1: Backend Foundation

### Database Updates
- [ ] Add `status` field to `leads` table (`new`, `contacted`, `qualified`, `converted`, `lost`)
- [ ] Add `assigned_to`, `converted_value`, `lost_reason`, `last_contacted` to `leads`
- [ ] Create `lead_notes` table
- [ ] (Optional) Create `admin_users` table for JWT auth
- [ ] Run migrations: `alembic revision --autogenerate -m "add admin features"`
- [ ] Apply migrations: `alembic upgrade head`

### New Pydantic Schemas
- [ ] Create `PricingPlanCreate`, `PricingPlanUpdate` schemas
- [ ] Create `ServiceCreate`, `ServiceUpdate` schemas
- [ ] Create `FeatureCreate`, `FeatureUpdate` schemas
- [ ] Create `AddonCreate`, `AddonUpdate` schemas
- [ ] Create `LeadUpdate`, `LeadStatusUpdate` schemas
- [ ] Create `LeadNoteCreate` schema
- [ ] Create `CompanyInfoUpdate` schema
- [ ] Create analytics response schemas

### CRUD Endpoints - Pricing Plans
- [ ] `POST /api/v1/pricing` - Create plan
- [ ] `PUT /api/v1/pricing/{id}` - Update plan
- [ ] `DELETE /api/v1/pricing/{id}` - Delete plan

### CRUD Endpoints - Services
- [ ] `POST /api/v1/services` - Create service
- [ ] `PUT /api/v1/services/{id}` - Update service
- [ ] `DELETE /api/v1/services/{id}` - Delete service

### CRUD Endpoints - Features
- [ ] `POST /api/v1/features` - Create feature
- [ ] `PUT /api/v1/features/{id}` - Update feature
- [ ] `DELETE /api/v1/features/{id}` - Delete feature
- [ ] `PATCH /api/v1/features/{id}/reorder` - Reorder features

### CRUD Endpoints - Add-ons
- [ ] `POST /api/v1/addons` - Create addon
- [ ] `PUT /api/v1/addons/{id}` - Update addon
- [ ] `DELETE /api/v1/addons/{id}` - Delete addon

### Lead Management Endpoints
- [ ] `PUT /api/v1/leads/{id}` - Update lead details
- [ ] `PATCH /api/v1/leads/{id}/status` - Update lead status
- [ ] `DELETE /api/v1/leads/{id}` - Delete lead
- [ ] `POST /api/v1/leads/{id}/notes` - Add note to lead
- [ ] `GET /api/v1/leads/{id}/notes` - Get lead notes

### Analytics Endpoints
- [ ] `GET /api/v1/analytics/dashboard` - Overview stats
- [ ] `GET /api/v1/analytics/leads/timeline` - Leads over time
- [ ] `GET /api/v1/analytics/leads/breakdown` - By service/status/budget

### Company Info
- [ ] `PUT /api/v1/company` - Update company info

### Onboarding Questions CRUD
- [ ] `POST /api/v1/onboarding/questions` - Create question
- [ ] `PUT /api/v1/onboarding/questions/{id}` - Update question
- [ ] `DELETE /api/v1/onboarding/questions/{id}` - Delete question

### Authentication (Clerk Integration)
- [ ] **Backend:** Implement Clerk JWT verification in FastAPI
  - [ ] Add `python-jose` for JWT verification
  - [ ] Create `verify_clerk_token()` dependency
  - [ ] Add Clerk environment variables to Vercel
  - [ ] Update all admin endpoints to use Clerk auth

### Testing
- [ ] Test all new endpoints with Postman
- [ ] Write unit tests for new endpoints
- [ ] Update Postman collection
- [ ] Test with invalid API keys
- [ ] Test error cases

---

## ✅ Phase 2: Frontend Setup (TanStack Start + Clerk)

### Project Initialization
- [ ] Create TanStack Start project: `npm create @tanstack/start@latest`
- [ ] Install Clerk: `npm install @clerk/tanstack-start`
- [ ] Install dependencies:
  - [ ] `@tanstack/react-table` - Data tables (built-in)
  - [ ] `@tanstack/react-query` - Data fetching (built-in)
  - [ ] `react-hook-form` - Forms
  - [ ] `@hookform/resolvers` - Form validation
  - [ ] `zod` - Schema validation
  - [ ] `recharts` - Charts
  - [ ] `lucide-react` - Icons
  - [ ] `axios` - HTTP client

### Clerk Setup
- [ ] Create Clerk account at clerk.com
- [ ] Create new application in Clerk dashboard
- [ ] Get API keys (Publishable Key & Secret Key)
- [ ] Configure `.env`:
  - [ ] `VITE_CLERK_PUBLISHABLE_KEY`
  - [ ] `CLERK_SECRET_KEY`
- [ ] Set up user metadata for roles (admin field)
- [ ] Configure Clerk appearance/branding

### Shadcn UI Setup
- [ ] Initialize Shadcn: `npx shadcn@latest init`
- [ ] Add components:
  - [ ] `button`, `card`, `input`, `label`
  - [ ] `table`, `dialog`, `alert-dialog`
  - [ ] `dropdown-menu`, `select`, `checkbox`
  - [ ] `form`, `toast`, `skeleton`
  - [ ] `badge`, `tabs`, `separator`

### Project Structure
- [ ] Create folder structure (see guide)
- [ ] Set up `app/(auth)/` route group
- [ ] Set up `app/(dashboard)/` route group
- [ ] Create `components/` folders
- [ ] Create `lib/` utilities
- [ ] Create `hooks/` directory
- [ ] Create `types/` directory

### Configuration
- [ ] Set up `.env` with API URL and Clerk keys
- [ ] Configure TypeScript paths in `tsconfig.json`
- [ ] Set up Tailwind config
- [ ] Configure TanStack Router file-based routing
- [ ] Set up `app.config.ts` for TanStack Start
- [ ] Add Clerk Provider to root layout

### Type Definitions
- [ ] Copy types from `FRONTEND_INTEGRATION.md`
- [ ] Add admin-specific types
- [ ] Create form schemas with Zod

### API Client
- [ ] Create API service class
- [ ] Add authentication headers
- [ ] Add error handling
- [ ] Add retry logic

---

## ✅ Phase 3: Core Features

### Authentication (Clerk)
- [ ] Create sign-in route (`/sign-in`)
- [ ] Create sign-up route (`/sign-up`)
- [ ] Implement `ClerkProvider` in root layout
- [ ] Create protected route group (`_auth`)
- [ ] Add `beforeLoad` guard for authentication
- [ ] Implement `useAuth()` hook in API calls
- [ ] Add user button/menu to header
- [ ] Configure post-sign-in redirect

### Dashboard Layout
- [ ] Create sidebar component
- [ ] Create header component
- [ ] Create breadcrumb component
- [ ] Add navigation menu
- [ ] Make responsive (mobile menu)

### Dashboard Home (Analytics)
- [ ] Stats cards component
- [ ] Leads timeline chart
- [ ] Service breakdown chart
- [ ] Status distribution chart
- [ ] Recent leads table
- [ ] Fetch analytics data

### Leads Management
- [ ] Leads list page with table
- [ ] Search & filter functionality
- [ ] Status badge component
- [ ] Lead detail page
- [ ] Lead notes component
- [ ] Status update form
- [ ] Export to CSV functionality

---

## ✅ Phase 4: Content Management

### Pricing Plans
- [ ] Pricing plans list page
- [ ] Create plan form
- [ ] Edit plan form
- [ ] Delete confirmation
- [ ] Features array input
- [ ] Preview functionality

### Services
- [ ] Services list page
- [ ] Create service form
- [ ] Edit service form
- [ ] Delete confirmation

### Features
- [ ] Features list page
- [ ] Create feature form
- [ ] Edit feature form
- [ ] Drag-drop reordering
- [ ] Delete confirmation

### Add-ons
- [ ] Add-ons list page
- [ ] Create addon form
- [ ] Edit addon form
- [ ] Delete confirmation

### Company Info
- [ ] Company info form
- [ ] Contact details section
- [ ] Payment terms section
- [ ] Update functionality

### Onboarding Questions
- [ ] Questions list grouped by service
- [ ] Create question form
- [ ] Edit question form
- [ ] Question type selector
- [ ] Options manager (for select/radio)
- [ ] Delete confirmation

---

## ✅ Phase 5: Polish & Deploy

### UX Improvements
- [ ] Loading states for all async operations
- [ ] Error boundaries
- [ ] Toast notifications
- [ ] Skeleton loaders
- [ ] Empty states
- [ ] Form validation messages
- [ ] Confirmation dialogs

### Bulk Operations
- [ ] Select multiple leads
- [ ] Bulk status update
- [ ] Bulk export
- [ ] Bulk delete

### Additional Features
- [ ] Search functionality
- [ ] Sorting on tables
- [ ] Pagination
- [ ] Date range filters
- [ ] Quick actions menu

### Testing
- [ ] Test all CRUD operations
- [ ] Test authentication flow
- [ ] Test on mobile devices
- [ ] Test error scenarios
- [ ] Test with slow network
- [ ] Cross-browser testing

### Performance
- [ ] Optimize images
- [ ] Code splitting
- [ ] Lazy load components
- [ ] Implement caching
- [ ] Minimize bundle size

### Deployment
- [ ] Deploy frontend to Vercel
- [ ] Set up custom domain (e.g., admin.lunaxcode.site)
- [ ] Configure environment variables
- [ ] Set up CORS for admin domain
- [ ] Test production deployment
- [ ] Monitor for errors

---

## 🎯 Quick Commands

### Backend (lunaxcode-fastapi)
```bash
# Database migrations
alembic revision --autogenerate -m "add admin features"
alembic upgrade head

# Run development server
uvicorn api.main:app --reload

# Run tests
pytest tests/ -v

# Deploy to Vercel
git push origin main
```

### Frontend (admin-dashboard with TanStack Start)
```bash
# Initialize project
npm create @tanstack/start@latest admin-dashboard
cd admin-dashboard

# Install Clerk
npm install @clerk/tanstack-start

# Install dependencies
npm install react-hook-form @hookform/resolvers zod
npm install recharts lucide-react axios

# Install Shadcn
npx shadcn@latest init
npx shadcn@latest add button card input table dialog form

# Set up environment variables
cp .env.example .env
# Add your Clerk keys

# Run development
npm run dev

# Build for production
npm run build

# Deploy to Vercel
vercel --prod
```

---

## 📊 Progress Tracking

### Week 1: Backend (0/35)
- [ ] Database (0/5)
- [ ] Schemas (0/8)
- [ ] Pricing CRUD (0/3)
- [ ] Services CRUD (0/3)
- [ ] Features CRUD (0/4)
- [ ] Add-ons CRUD (0/3)
- [ ] Leads Management (0/5)
- [ ] Analytics (0/3)
- [ ] Testing (0/1)

### Week 2: Frontend Setup (0/25)
- [ ] Initialization (0/10)
- [ ] Configuration (0/5)
- [ ] Types & API (0/5)
- [ ] Layout (0/5)

### Week 3: Core Features (0/20)
- [ ] Auth (0/4)
- [ ] Analytics Dashboard (0/6)
- [ ] Leads Management (0/10)

### Week 4: Content Management (0/25)
- [ ] Pricing (0/6)
- [ ] Services (0/4)
- [ ] Features (0/5)
- [ ] Add-ons (0/4)
- [ ] Company (0/3)
- [ ] Onboarding (0/3)

### Week 5: Polish & Deploy (0/15)
- [ ] UX (0/7)
- [ ] Testing (0/6)
- [ ] Deployment (0/2)

---

## 📚 Documentation References

- **Full Guide:** `ADMIN_DASHBOARD_GUIDE.md`
- **API Integration:** `FRONTEND_INTEGRATION.md`
- **Quick Reference:** `API_QUICK_REFERENCE.md`
- **Postman Collection:** `lunaxcode-api.postman_collection.json`

---

## 🎯 Next Actions

1. **Review the full guide** (`ADMIN_DASHBOARD_GUIDE.md`)
2. **Start with Phase 1** - Backend endpoints
3. **Test each endpoint** as you build it
4. **Move to Phase 2** - Frontend setup
5. **Iterate and improve**

---

**Total Estimated Time:** 4-5 weeks for full implementation

**MVP (Minimal Viable Product):**
- Analytics dashboard
- Leads list & detail
- Pricing management
- ~2 weeks

**Full Feature Set:**
- All CRUD operations
- Advanced analytics
- Bulk operations
- ~5 weeks

Good luck! 🚀

