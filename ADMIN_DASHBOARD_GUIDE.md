# Admin Dashboard Development Guide

## 🎯 Overview

This guide provides a comprehensive plan for building an admin dashboard for the Lunaxcode API, enabling full CRUD operations and analytics for all resources.

**Dashboard Features:**
- 📊 Analytics & Metrics Dashboard
- 👥 Lead Management with Dual Views (Table + Card)
- 💰 Pricing Plan Management - Full CRUD with Dual Views
- 🛠️ Service Management - Full CRUD with Dual Views
- ✨ Feature Management - Full CRUD with Dual Views
- 🔌 Add-on Management - Full CRUD with Dual Views
- 🏢 Company Info Management with Rich Text Editor
- 📋 Onboarding Questions Management
- 🔐 Clerk Authentication (JWT-based)
- 📈 Real-time Statistics
- ✏️ Rich Text Editing (Shadcn-Tiptap Integration)
- 🔄 Dual View System (Table + Card for all list pages)

**Key Technologies:**
- **Framework:** Next.js 15 (App Router)
- **UI:** Shadcn/ui + Tailwind CSS
- **Auth:** Clerk
- **Editor:** Tiptap (Shadcn integration)
- **Forms:** React Hook Form + Zod
- **Data:** TanStack Query + TanStack Table

---

## 📋 Table of Contents

1. [Backend Requirements](#backend-requirements)
2. [Missing API Endpoints](#missing-api-endpoints)
3. [Database Schema Updates](#database-schema-updates)
4. [Authentication System](#authentication-system)
5. [Frontend Architecture](#frontend-architecture)
6. [Dashboard Pages](#dashboard-pages)
7. [Components Library](#components-library)
8. [State Management](#state-management)
9. [Implementation Roadmap](#implementation-roadmap)

---

## Backend Requirements

### Current State ✅

**Already Implemented:**
- ✅ Full CRUD for Pricing Plans (GET, POST, PUT, DELETE)
- ✅ Full CRUD for Services (GET, POST, PUT, DELETE)
- ✅ Full CRUD for Features (GET, POST, PUT, DELETE)
- ✅ Full CRUD for Add-ons (GET, POST, PUT, DELETE)
- ✅ UPDATE for Company Info (PUT /company)
- ✅ Full CRUD for Onboarding Questions (GET, POST, PUT, DELETE)
- ✅ Lead status field and UPDATE endpoint (PUT /leads/{id})
- ✅ Full Leads management (GET, POST, PUT, DELETE with filtering)
- ✅ Basic authentication via `X-API-Key` header

**What's Missing (Optional Enhancements):**
- ❌ Analytics/Statistics endpoints (GET /analytics/dashboard, /analytics/leads/timeline)
- ❌ Advanced admin authentication (JWT/Session-based via Clerk)
- ❌ Role-based access control (RBAC)
- ❌ Lead notes system (separate table for admin notes)
- ❌ Audit logging for admin actions

---

## ✅ All Core CRUD Endpoints Are Implemented!

All essential admin endpoints are already built and ready to use. See [ADMIN_API_REFERENCE.md](./ADMIN_API_REFERENCE.md) for complete API documentation.

### Available Endpoints Summary

| Resource | GET All | GET One | POST | PUT | DELETE |
|----------|---------|---------|------|-----|--------|
| Pricing Plans | ✅ | ✅ | ✅ | ✅ | ✅ |
| Services | ✅ | ✅ | ✅ | ✅ | ✅ |
| Features | ✅ | ✅ | ✅ | ✅ | ✅ |
| Add-ons | ✅ | ✅ | ✅ | ✅ | ✅ |
| Company Info | ✅ | - | - | ✅ | - |
| Onboarding Questions | ✅ | ✅ | ✅ | ✅ | ✅ |
| Leads | ✅ (admin) | ✅ (admin) | ✅ (public) | ✅ (admin) | ✅ (admin) |

**Authentication:** All admin endpoints require `X-API-Key` header (except public GET endpoints and POST /leads).

**Lead Management Features:**
- List leads with filtering by status (`new`, `contacted`, `converted`, `rejected`)
- Pagination support (skip/limit parameters)
- Update lead status via PUT /leads/{id}
- Delete leads
- Lead status field already exists in database

### Optional Analytics Endpoints (Not Yet Implemented)

If you want advanced analytics, consider adding these endpoints:

```python
# api/routers/analytics.py - OPTIONAL NEW ROUTER

@router.get("/analytics/dashboard")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get dashboard overview statistics
    Returns:
    - Total leads count
    - Leads by status breakdown
    - Leads by service type distribution  
    - Conversion rate calculation
    - Recent activity timeline
    """
    pass

@router.get("/analytics/leads/timeline")
async def get_leads_timeline(
    start_date: date,
    end_date: date,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get leads over time for charts"""
    pass
```

---

## Database Schema Updates

### Current Lead Model ✅

The `Lead` model already includes the `status` field:

```python
# api/models/lead.py - CURRENT IMPLEMENTATION

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    service_type = Column(String, ForeignKey("services.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    company = Column(String)
    project_description = Column(Text)
    answers = Column(JSON, nullable=False)  # Structured data
    ai_prompt = Column(Text, nullable=False)  # AI-formatted prompt
    status = Column(String, default="new")  # ✅ Already implemented
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
```

**Valid status values:** `new`, `contacted`, `converted`, `rejected`

### Optional Enhancement: Lead Notes Table

If you want to add admin notes to leads (not yet implemented):

```python
# api/models/lead_note.py - OPTIONAL NEW MODEL

class LeadNote(Base):
    __tablename__ = "lead_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String(100))  # Admin user email
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="notes")
```

### 2. Lead Notes Table

```python
# api/models/lead_note.py - NEW MODEL

class LeadNote(Base):
    __tablename__ = "lead_notes"
    
    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(String(100))  # Admin user
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lead = relationship("Lead", back_populates="notes")
```

### 3. Admin Users Table (Optional - for JWT auth)

```python
# api/models/admin_user.py - NEW MODEL

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="admin")  # admin, super_admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
```

### 4. Create Migrations

```bash
# After adding new models/fields
alembic revision --autogenerate -m "add lead status, notes, and admin users"
alembic upgrade head
```

---

## Authentication System

### Option 1: Keep Simple (API Key) - Recommended for MVP

**Current Setup:**
```python
# api/utils/auth.py - CURRENT
async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
```

**Enhancement - Multiple API Keys:**
```python
# .env
ADMIN_API_KEYS=key1,key2,key3

# api/config.py
class Settings(BaseSettings):
    ADMIN_API_KEYS: str = ""
    
    @property
    def api_keys_list(self) -> List[str]:
        return [k.strip() for k in self.ADMIN_API_KEYS.split(",") if k.strip()]

# api/utils/auth.py
async def verify_api_key(api_key: str = Header(..., alias="X-API-Key")):
    if api_key not in settings.api_keys_list:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key
```

### Option 2: Clerk JWT Verification (Recommended)

**With Clerk, the frontend handles authentication. Backend validates Clerk JWT tokens.**

```python
# api/utils/auth.py - CLERK JWT VERIFICATION

from jose import jwt, JWTError
from fastapi import Header, HTTPException
import httpx

# Clerk configuration
CLERK_JWT_PUBLIC_KEY = settings.CLERK_JWT_PUBLIC_KEY  # From Clerk dashboard
CLERK_ISSUER = settings.CLERK_ISSUER  # e.g., https://clerk.your-app.com

async def verify_clerk_token(authorization: str = Header(...)):
    """
    Verify Clerk JWT token from Authorization header
    Format: "Bearer <token>"
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verify JWT token with Clerk's public key
        payload = jwt.decode(
            token,
            CLERK_JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
        )
        
        # Extract user info from token
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {
            "user_id": user_id,
            "email": email,
            "metadata": payload.get("public_metadata", {})
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

# Alternative: Use Clerk's API to verify session
async def verify_clerk_session(session_token: str = Header(..., alias="Authorization")):
    """Verify session using Clerk's API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.clerk.com/v1/sessions/{session_token}",
            headers={"Authorization": f"Bearer {settings.CLERK_SECRET_KEY}"}
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        return response.json()
```

### Updated Endpoint Protection

```python
# api/routers/pricing.py - WITH CLERK AUTH

@router.post("/pricing", status_code=201)
async def create_pricing_plan(
    plan: PricingPlanCreate,
    db: AsyncSession = Depends(get_db),
    clerk_user: dict = Depends(verify_clerk_token)  # ← Clerk verification
):
    """Create new pricing plan (Admin only)"""
    # clerk_user contains: user_id, email, metadata
    # Check if user has admin role (stored in Clerk metadata)
    
    if not clerk_user.get("metadata", {}).get("role") == "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Create pricing plan...
    pass
```

### Environment Variables for Clerk

```python
# api/config.py - ADD CLERK SETTINGS

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str = ""  # From Clerk Dashboard → API Keys
    CLERK_JWT_PUBLIC_KEY: str = ""  # From Clerk Dashboard → API Keys → JWT Public Key
    CLERK_ISSUER: str = ""  # From Clerk Dashboard (e.g., https://clerk.your-app.com)
```

---

## Frontend Architecture

### Tech Stack Recommendation

**Framework:** Next.js 15 (App Router with Server Components)
**UI Library:** Shadcn/ui + Tailwind CSS
**State Management:** TanStack Query (React Query v5) for server state
**Forms:** React Hook Form + Zod validation
**Rich Text Editor:** [Shadcn-Tiptap](https://github.com/NiazMorshed2007/shadcn-tiptap) (Tiptap with Shadcn/ui integration)
**Charts:** Recharts or Chart.js
**Tables:** TanStack Table v8
**Authentication:** Clerk (Managed authentication with Next.js integration)
**View Modes:** Dual view system (Table + Card) for all list pages

### Where Shadcn-Tiptap Will Be Used

The rich text editor will be essential for:
- **Company Info Editor**: Editing company description, about sections
- **Lead Notes**: Adding formatted notes to leads
- **Service Descriptions**: Rich formatted service details
- **Feature Descriptions**: Detailed feature explanations with formatting
- **Onboarding Questions**: Creating question descriptions with formatting
- **Project Description Templates**: Pre-formatted templates for common projects
- **Email Templates**: Creating rich email responses to leads

### Dual View System (Table + Card)

All list pages will support **two view modes** that users can toggle:

**Table View:**
- Dense information display
- Sortable columns
- Quick actions column
- Best for: Bulk operations, data analysis, filtering

**Card View:**
- Visual, spacious layout
- Preview of content
- Prominent actions
- Best for: Content browsing, visual selection, mobile devices

**Implemented for:**
- ✅ Pricing Plans (compare plans visually)
- ✅ Services (view service cards with icons)
- ✅ Features (visual feature showcase)
- ✅ Add-ons (addon cards with pricing)
- ✅ Leads (lead cards with status badges)
- ✅ Onboarding Questions (question set cards per service)

### Project Structure (Next.js 15 App Router)

```
admin-dashboard/
├── app/
│   ├── layout.tsx                  # Root layout
│   ├── page.tsx                    # Landing/redirect page
│   ├── (auth)/
│   │   ├── sign-in/
│   │   │   └── [[...sign-in]]/
│   │   │       └── page.tsx        # Clerk sign-in
│   │   └── sign-up/
│   │       └── [[...sign-up]]/
│   │           └── page.tsx        # Clerk sign-up
│   └── (dashboard)/
│       ├── layout.tsx              # Dashboard layout (sidebar + header)
│       ├── dashboard/
│       │   └── page.tsx            # Analytics Dashboard
│       ├── leads/
│       │   ├── page.tsx            # Leads List (Table + Card views)
│       │   ├── [id]/
│       │   │   └── page.tsx        # Lead Detail
│       │   └── new/
│       │       └── page.tsx        # Create Lead (optional)
│       ├── pricing/
│       │   ├── page.tsx            # Pricing Plans List (Table + Card views)
│       │   ├── new/
│       │   │   └── page.tsx        # Create Plan
│       │   └── [id]/
│       │       ├── page.tsx        # View Plan
│       │       └── edit/
│       │           └── page.tsx    # Edit Plan
│       ├── services/
│       │   ├── page.tsx            # Services List (Table + Card views)
│       │   ├── new/
│       │   │   └── page.tsx        # Create Service
│       │   └── [id]/
│       │       └── edit/
│       │           └── page.tsx    # Edit Service
│       ├── features/
│       │   ├── page.tsx            # Features List (Table + Card views)
│       │   ├── new/
│       │   │   └── page.tsx        # Create Feature
│       │   └── [id]/
│       │       └── edit/
│       │           └── page.tsx    # Edit Feature
│       ├── addons/
│       │   ├── page.tsx            # Add-ons List (Table + Card views)
│       │   ├── new/
│       │   │   └── page.tsx        # Create Add-on
│       │   └── [id]/
│       │       └── edit/
│       │           └── page.tsx    # Edit Add-on
│       ├── onboarding/
│       │   ├── page.tsx            # Onboarding Questions List (Card view)
│       │   ├── new/
│       │   │   └── page.tsx        # Create Question Set
│       │   └── [serviceType]/
│       │       └── edit/
│       │           └── page.tsx    # Edit Questions
│       ├── company/
│       │   └── page.tsx            # Edit Company Info
│       └── settings/
│           └── page.tsx            # Admin Settings
├── components/
│   ├── ui/                         # Shadcn components
│   ├── dashboard/
│   │   ├── sidebar.tsx
│   │   ├── header.tsx
│   │   ├── stats-card.tsx
│   │   └── recent-activity.tsx
│   ├── shared/
│   │   ├── data-table.tsx          # Reusable table component
│   │   ├── card-view.tsx           # Reusable card grid component
│   │   ├── view-toggle.tsx         # Table/Card view switcher
│   │   ├── rich-text-editor.tsx    # Tiptap editor
│   │   ├── confirm-dialog.tsx
│   │   └── loading-skeleton.tsx
│   ├── leads/
│   │   ├── lead-table.tsx
│   │   ├── lead-card.tsx           # Card view for leads
│   │   ├── lead-form.tsx
│   │   ├── lead-status-badge.tsx
│   │   └── lead-notes.tsx
│   ├── pricing/
│   │   ├── pricing-table.tsx
│   │   ├── pricing-card.tsx        # Card view for pricing
│   │   └── pricing-form.tsx
│   ├── services/
│   │   ├── service-table.tsx
│   │   ├── service-card.tsx        # Card view for services
│   │   └── service-form.tsx
│   ├── features/
│   │   ├── feature-table.tsx
│   │   ├── feature-card.tsx        # Card view for features
│   │   └── feature-form.tsx
│   └── addons/
│       ├── addon-table.tsx
│       ├── addon-card.tsx          # Card view for add-ons
│       └── addon-form.tsx
├── lib/
│   ├── api.ts                      # API client (with Clerk token)
│   ├── utils.ts
│   └── validations.ts              # Zod schemas
├── hooks/
│   ├── use-leads.ts                # TanStack Query hooks
│   ├── use-pricing.ts
│   ├── use-services.ts
│   ├── use-features.ts
│   ├── use-addons.ts
│   ├── use-analytics.ts
│   └── use-view-mode.ts            # Table/Card view state
├── types/
│   └── api.ts                      # TypeScript types
├── middleware.ts                   # Clerk middleware
└── next.config.js
```

---

## Dashboard Pages

### 1. Root Layout with Clerk Provider

```typescript
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Lunaxcode Admin Dashboard',
  description: 'Manage your Lunaxcode business',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body className={inter.className}>
          {children}
        </body>
      </html>
    </ClerkProvider>
  );
}
```

### 2. Protected Dashboard Layout

```typescript
// app/(dashboard)/layout.tsx
import { auth } from '@clerk/nextjs/server';
import { redirect } from 'next/navigation';
import { DashboardSidebar } from '@/components/dashboard/sidebar';
import { DashboardHeader } from '@/components/dashboard/header';

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { userId } = await auth();

  if (!userId) {
    redirect('/sign-in');
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <DashboardSidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <DashboardHeader />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### 3. Sign In Page

```typescript
// app/(auth)/sign-in/[[...sign-in]]/page.tsx
import { SignIn } from '@clerk/nextjs';

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <SignIn
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'shadow-lg',
          },
        }}
        afterSignInUrl="/dashboard"
        signUpUrl="/sign-up"
      />
    </div>
  );
}
```

### 4. Dashboard Home (Analytics)

**URL:** `/dashboard`

**Features:**
- Key metrics cards (Total Leads, Conversion Rate, Revenue, etc.)
- Leads timeline chart
- Leads by status pie chart
- Leads by service type bar chart
- Recent leads table
- Quick actions

```typescript
// app/(dashboard)/dashboard/page.tsx
import { auth } from '@clerk/nextjs/server';
import { StatsCard } from '@/components/dashboard/stats-card';
import { LeadsChart } from '@/components/charts/leads-chart';
import { RecentLeads } from '@/components/dashboard/recent-leads';
import { api } from '@/lib/api';

export default async function DashboardPage() {
  const { getToken } = await auth();
  const token = await getToken();
  
  const stats = await api.getAnalytics(token);
  
  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Leads"
          value={stats.totalLeads}
          change="+12%"
          trend="up"
        />
        <StatsCard
          title="Conversion Rate"
          value={`${stats.conversionRate}%`}
          change="+5%"
          trend="up"
        />
        <StatsCard
          title="Active Services"
          value={stats.activeServices}
          change="+2"
          trend="up"
        />
        <StatsCard
          title="Revenue (MTD)"
          value={`₱${stats.revenue.toLocaleString()}`}
          change="+18%"
          trend="up"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <LeadsChart data={stats.timeline} />
        <ServiceBreakdown data={stats.byService} />
      </div>

      {/* Recent Activity */}
      <RecentLeads leads={stats.recentLeads} />
    </div>
  );
}
```

### 5. View Toggle Component (Shared)

```typescript
// components/shared/view-toggle.tsx
'use client';

import { LayoutGrid, Table as TableIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';

export type ViewMode = 'table' | 'card';

interface ViewToggleProps {
  view: ViewMode;
  onViewChange: (view: ViewMode) => void;
}

export function ViewToggle({ view, onViewChange }: ViewToggleProps) {
  return (
    <div className="flex gap-1 border rounded-md p-1">
      <Button
        variant={view === 'table' ? 'secondary' : 'ghost'}
        size="sm"
        onClick={() => onViewChange('table')}
      >
        <TableIcon className="h-4 w-4" />
        <span className="ml-2 hidden sm:inline">Table</span>
      </Button>
      <Button
        variant={view === 'card' ? 'secondary' : 'ghost'}
        size="sm"
        onClick={() => onViewChange('card')}
      >
        <LayoutGrid className="h-4 w-4" />
        <span className="ml-2 hidden sm:inline">Cards</span>
      </Button>
    </div>
  );
}
```

```typescript
// hooks/use-view-mode.ts
'use client';

import { useState, useEffect } from 'react';

export type ViewMode = 'table' | 'card';

export function useViewMode(key: string, defaultView: ViewMode = 'table') {
  const [view, setView] = useState<ViewMode>(defaultView);

  useEffect(() => {
    const saved = localStorage.getItem(`view-mode-${key}`);
    if (saved === 'table' || saved === 'card') {
      setView(saved);
    }
  }, [key]);

  const setViewMode = (newView: ViewMode) => {
    setView(newView);
    localStorage.setItem(`view-mode-${key}`, newView);
  };

  return [view, setViewMode] as const;
}
```

### 6. Pricing Plans Management (CRUD with Dual Views)

**URL:** `/pricing`

```typescript
// app/(dashboard)/pricing/page.tsx
'use client';

import { useState } from 'react';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ViewToggle } from '@/components/shared/view-toggle';
import { useViewMode } from '@/hooks/use-view-mode';
import { usePricing } from '@/hooks/use-pricing';
import { PricingTable } from '@/components/pricing/pricing-table';
import { PricingCardGrid } from '@/components/pricing/pricing-card-grid';
import Link from 'next/link';

export default function PricingPage() {
  const [view, setView] = useViewMode('pricing', 'card');
  const { plans, loading, deletePlan } = usePricing();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pricing Plans</h1>
          <p className="text-muted-foreground mt-1">
            Manage your service pricing and packages
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ViewToggle view={view} onViewChange={setView} />
          <Button asChild>
            <Link href="/pricing/new">
              <Plus className="h-4 w-4 mr-2" />
              Create Plan
            </Link>
          </Button>
        </div>
      </div>

      {/* Content */}
      {loading ? (
        <div>Loading...</div>
      ) : view === 'table' ? (
        <PricingTable plans={plans} onDelete={deletePlan} />
      ) : (
        <PricingCardGrid plans={plans} onDelete={deletePlan} />
      )}
    </div>
  );
}
```

```typescript
// components/pricing/pricing-table.tsx
import { ColumnDef } from '@tanstack/react-table';
import { DataTable } from '@/components/shared/data-table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Edit, Trash2 } from 'lucide-react';
import Link from 'next/link';

export function PricingTable({ plans, onDelete }: Props) {
  const columns: ColumnDef<PricingPlan>[] = [
    {
      accessorKey: 'name',
      header: 'Plan Name',
    },
    {
      accessorKey: 'price',
      header: 'Price',
      cell: ({ row }) => `₱${row.original.price.toLocaleString()}`,
    },
    {
      accessorKey: 'timeline',
      header: 'Timeline',
    },
    {
      accessorKey: 'features',
      header: 'Features',
      cell: ({ row }) => `${row.original.features.length} features`,
    },
    {
      accessorKey: 'popular',
      header: 'Popular',
      cell: ({ row }) => (
        row.original.popular ? (
          <Badge variant="secondary">Popular</Badge>
        ) : null
      ),
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex gap-2">
          <Button size="sm" variant="ghost" asChild>
            <Link href={`/pricing/${row.original.id}/edit`}>
              <Edit className="h-4 w-4" />
            </Link>
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => onDelete(row.original.id)}
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return <DataTable columns={columns} data={plans} searchKey="name" />;
}
```

```typescript
// components/pricing/pricing-card-grid.tsx
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Edit, Trash2, Check } from 'lucide-react';
import Link from 'next/link';

export function PricingCardGrid({ plans, onDelete }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {plans.map((plan) => (
        <Card key={plan.id} className="relative">
          {plan.popular && (
            <div className="absolute top-4 right-4">
              <Badge variant="secondary">Popular</Badge>
            </div>
          )}
          <CardHeader>
            <CardTitle className="flex items-start justify-between">
              {plan.name}
            </CardTitle>
            <div className="text-3xl font-bold">
              ₱{plan.price.toLocaleString()}
            </div>
            <p className="text-sm text-muted-foreground">{plan.timeline}</p>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {plan.features.slice(0, 4).map((feature, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <Check className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                  <span>{feature}</span>
                </li>
              ))}
              {plan.features.length > 4 && (
                <li className="text-sm text-muted-foreground">
                  +{plan.features.length - 4} more features
                </li>
              )}
            </ul>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button variant="outline" size="sm" asChild className="flex-1">
              <Link href={`/pricing/${plan.id}/edit`}>
                <Edit className="h-4 w-4 mr-2" />
                Edit
              </Link>
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDelete(plan.id)}
            >
              <Trash2 className="h-4 w-4 text-destructive" />
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
```

### 7. Services Management (CRUD with Dual Views)

**URL:** `/services`

```typescript
// app/(dashboard)/services/page.tsx
'use client';

import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ViewToggle } from '@/components/shared/view-toggle';
import { useViewMode } from '@/hooks/use-view-mode';
import { useServices } from '@/hooks/use-services';
import { ServiceTable } from '@/components/services/service-table';
import { ServiceCardGrid } from '@/components/services/service-card-grid';
import Link from 'next/link';

export default function ServicesPage() {
  const [view, setView] = useViewMode('services', 'card');
  const { services, loading, deleteService } = useServices();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Services</h1>
          <p className="text-muted-foreground mt-1">
            Manage your service offerings
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ViewToggle view={view} onViewChange={setView} />
          <Button asChild>
            <Link href="/services/new">
              <Plus className="h-4 w-4 mr-2" />
              Create Service
            </Link>
          </Button>
        </div>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : view === 'table' ? (
        <ServiceTable services={services} onDelete={deleteService} />
      ) : (
        <ServiceCardGrid services={services} onDelete={deleteService} />
      )}
    </div>
  );
}
```

### 8. Features Management (CRUD with Dual Views)

**URL:** `/features`

```typescript
// app/(dashboard)/features/page.tsx
'use client';

import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ViewToggle } from '@/components/shared/view-toggle';
import { useViewMode } from '@/hooks/use-view-mode';
import { useFeatures } from '@/hooks/use-features';
import { FeatureTable } from '@/components/features/feature-table';
import { FeatureCardGrid } from '@/components/features/feature-card-grid';
import Link from 'next/link';

export default function FeaturesPage() {
  const [view, setView] = useViewMode('features', 'card');
  const { features, loading, deleteFeature } = useFeatures();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Features</h1>
          <p className="text-muted-foreground mt-1">
            Manage your marketing features
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ViewToggle view={view} onViewChange={setView} />
          <Button asChild>
            <Link href="/features/new">
              <Plus className="h-4 w-4 mr-2" />
              Create Feature
            </Link>
          </Button>
        </div>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : view === 'table' ? (
        <FeatureTable features={features} onDelete={deleteFeature} />
      ) : (
        <FeatureCardGrid features={features} onDelete={deleteFeature} />
      )}
    </div>
  );
}
```

### 9. Add-ons Management (CRUD with Dual Views)

**URL:** `/addons`

```typescript
// app/(dashboard)/addons/page.tsx
'use client';

import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ViewToggle } from '@/components/shared/view-toggle';
import { useViewMode } from '@/hooks/use-view-mode';
import { useAddons } from '@/hooks/use-addons';
import { AddonTable } from '@/components/addons/addon-table';
import { AddonCardGrid } from '@/components/addons/addon-card-grid';
import Link from 'next/link';

export default function AddonsPage() {
  const [view, setView] = useViewMode('addons', 'card');
  const { addons, loading, deleteAddon } = useAddons();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Add-ons</h1>
          <p className="text-muted-foreground mt-1">
            Manage additional services and packages
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ViewToggle view={view} onViewChange={setView} />
          <Button asChild>
            <Link href="/addons/new">
              <Plus className="h-4 w-4 mr-2" />
              Create Add-on
            </Link>
          </Button>
        </div>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : view === 'table' ? (
        <AddonTable addons={addons} onDelete={deleteAddon} />
      ) : (
        <AddonCardGrid addons={addons} onDelete={deleteAddon} />
      )}
    </div>
  );
}
```

### 10. Leads Management (CRUD with Dual Views)

**URL:** `/leads`

```typescript
// app/(dashboard)/leads/page.tsx
'use client';

import { Download } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ViewToggle } from '@/components/shared/view-toggle';
import { useViewMode } from '@/hooks/use-view-mode';
import { useLeads } from '@/hooks/use-leads';
import { LeadTable } from '@/components/leads/lead-table';
import { LeadCardGrid } from '@/components/leads/lead-card-grid';

export default function LeadsPage() {
  const [view, setView] = useViewMode('leads', 'table');
  const { leads, loading, updateStatus, deleteLead, exportCSV } = useLeads();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Leads</h1>
          <p className="text-muted-foreground mt-1">
            Manage customer inquiries and track conversions
          </p>
        </div>
        <div className="flex items-center gap-3">
          <ViewToggle view={view} onViewChange={setView} />
          <Button variant="outline" onClick={exportCSV}>
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      {loading ? (
        <div>Loading...</div>
      ) : view === 'table' ? (
        <LeadTable
          leads={leads}
          onStatusChange={updateStatus}
          onDelete={deleteLead}
        />
      ) : (
        <LeadCardGrid
          leads={leads}
          onStatusChange={updateStatus}
          onDelete={deleteLead}
        />
      )}
    </div>
  );
}
```

### 11. Create/Edit Forms (Universal Pattern)

All resources follow the same CRUD form pattern. Here's the universal template:

```typescript
// app/(dashboard)/pricing/new/page.tsx - CREATE
'use client';

import { useRouter } from 'next/navigation';
import { PricingForm } from '@/components/pricing/pricing-form';
import { usePricing } from '@/hooks/use-pricing';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function NewPricingPage() {
  const router = useRouter();
  const { createPlan } = usePricing();

  const handleSubmit = async (data: PricingPlanCreate) => {
    await createPlan(data);
    router.push('/pricing');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Create Pricing Plan</h1>
        <p className="text-muted-foreground mt-1">
          Add a new pricing plan to your offerings
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Plan Details</CardTitle>
        </CardHeader>
        <CardContent>
          <PricingForm onSubmit={handleSubmit} />
        </CardContent>
      </Card>
    </div>
  );
}
```

```typescript
// app/(dashboard)/pricing/[id]/edit/page.tsx - EDIT
'use client';

import { useRouter } from 'next/navigation';
import { PricingForm } from '@/components/pricing/pricing-form';
import { usePricing } from '@/hooks/use-pricing';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function EditPricingPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const { plan, loading, updatePlan } = usePricing(params.id);

  const handleSubmit = async (data: PricingPlanUpdate) => {
    await updatePlan(params.id, data);
    router.push('/pricing');
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Edit Pricing Plan</h1>
        <p className="text-muted-foreground mt-1">
          Update pricing plan details
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Plan Details</CardTitle>
        </CardHeader>
        <CardContent>
          <PricingForm plan={plan} onSubmit={handleSubmit} />
        </CardContent>
      </Card>
    </div>
  );
}
```

### 12. Universal CRUD Forms for All Resources

#### Pricing Plan Form

```typescript
// components/pricing/pricing-form.tsx
'use client';

import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Plus, X } from 'lucide-react';

const pricingSchema = z.object({
  id: z.string().min(1, 'ID is required'),
  name: z.string().min(1, 'Name is required'),
  price: z.number().min(0, 'Price must be positive'),
  currency: z.string().default('PHP'),
  timeline: z.string().min(1, 'Timeline is required'),
  features: z.array(z.string()).min(1, 'At least one feature required'),
  popular: z.boolean().default(false),
});

export function PricingForm({ plan, onSubmit }: Props) {
  const form = useForm({
    resolver: zodResolver(pricingSchema),
    defaultValues: plan || {
      id: '',
      name: '',
      price: 0,
      currency: 'PHP',
      timeline: '',
      features: [''],
      popular: false,
    },
  });

  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: 'features',
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Plan ID (only for create) */}
        {!plan && (
          <FormField
            control={form.control}
            name="id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Plan ID</FormLabel>
                <FormControl>
                  <Input placeholder="landing_page" {...field} />
                </FormControl>
                <FormDescription>
                  Unique identifier (lowercase, underscores)
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        {/* Plan Name */}
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plan Name</FormLabel>
              <FormControl>
                <Input placeholder="Landing Page" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Price & Timeline */}
        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="price"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price (PHP)</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="8000"
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="timeline"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Timeline</FormLabel>
                <FormControl>
                  <Input placeholder="48-hour delivery" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Features (Dynamic Array) */}
        <div className="space-y-4">
          <FormLabel>Features</FormLabel>
          {fields.map((field, index) => (
            <div key={field.id} className="flex gap-2">
              <FormField
                control={form.control}
                name={`features.${index}`}
                render={({ field }) => (
                  <FormItem className="flex-1">
                    <FormControl>
                      <Input placeholder="Feature description" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={() => remove(index)}
                disabled={fields.length === 1}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => append('')}
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Feature
          </Button>
        </div>

        {/* Popular */}
        <FormField
          control={form.control}
          name="popular"
          render={({ field }) => (
            <FormItem className="flex items-center space-x-2">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <div className="space-y-1 leading-none">
                <FormLabel>Mark as Popular</FormLabel>
                <FormDescription>
                  Popular plans are highlighted on the website
                </FormDescription>
              </div>
            </FormItem>
          )}
        />

        {/* Submit */}
        <div className="flex gap-3">
          <Button type="submit" className="flex-1">
            {plan ? 'Update Plan' : 'Create Plan'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

#### Service Form

```typescript
// components/services/service-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

const serviceSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  description: z.string().min(1),
  icon: z.string().default('📦'),
});

export function ServiceForm({ service, onSubmit }: Props) {
  const form = useForm({
    resolver: zodResolver(serviceSchema),
    defaultValues: service || { id: '', name: '', description: '', icon: '📦' },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {!service && (
          <FormField
            control={form.control}
            name="id"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Service ID</FormLabel>
                <FormControl>
                  <Input placeholder="web_design" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        )}

        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Service Name</FormLabel>
              <FormControl>
                <Input placeholder="Web Design" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Professional web design services..."
                  rows={4}
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="icon"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Icon (Emoji)</FormLabel>
              <FormControl>
                <Input placeholder="🎨" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex gap-3">
          <Button type="submit" className="flex-1">
            {service ? 'Update Service' : 'Create Service'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

#### Feature Form

```typescript
// components/features/feature-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { RichTextEditor } from '@/components/shared/rich-text-editor';

const featureSchema = z.object({
  title: z.string().min(1),
  description: z.string().min(1),
  icon: z.string().default('✨'),
  display_order: z.number().min(0),
});

export function FeatureForm({ feature, onSubmit }: Props) {
  const form = useForm({
    resolver: zodResolver(featureSchema),
    defaultValues: feature || {
      title: '',
      description: '',
      icon: '✨',
      display_order: 0,
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Feature Title</FormLabel>
              <FormControl>
                <Input placeholder="Fast Delivery" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <RichTextEditor
                  value={field.value}
                  onChange={field.onChange}
                  placeholder="Describe this feature..."
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="icon"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Icon (Emoji)</FormLabel>
                <FormControl>
                  <Input placeholder="⚡" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="display_order"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Display Order</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="flex gap-3">
          <Button type="submit" className="flex-1">
            {feature ? 'Update Feature' : 'Create Feature'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

#### Add-on Form

```typescript
// components/addons/addon-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { RichTextEditor } from '@/components/shared/rich-text-editor';

const addonSchema = z.object({
  name: z.string().min(1),
  description: z.string().min(1),
  price_range: z.string().min(1),
  icon: z.string().default('🔌'),
});

export function AddonForm({ addon, onSubmit }: Props) {
  const form = useForm({
    resolver: zodResolver(addonSchema),
    defaultValues: addon || {
      name: '',
      description: '',
      price_range: '',
      icon: '🔌',
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Add-on Name</FormLabel>
              <FormControl>
                <Input placeholder="SEO Optimization" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Description</FormLabel>
              <FormControl>
                <RichTextEditor
                  value={field.value}
                  onChange={field.onChange}
                  placeholder="Describe this add-on service..."
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="price_range"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price Range</FormLabel>
                <FormControl>
                  <Input placeholder="₱3,000 - ₱5,000" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="icon"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Icon (Emoji)</FormLabel>
                <FormControl>
                  <Input placeholder="🔍" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="flex gap-3">
          <Button type="submit" className="flex-1">
            {addon ? 'Update Add-on' : 'Create Add-on'}
          </Button>
          <Button type="button" variant="outline" onClick={() => router.back()}>
            Cancel
          </Button>
        </div>
      </form>
    </Form>
  );
}
```

### 13. Lead Detail Page

```typescript
// app/(dashboard)/leads/[id]/page.tsx
import { auth } from '@clerk/nextjs/server';
import { api } from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LeadStatusBadge } from '@/components/leads/lead-status-badge';
import { LeadNotes } from '@/components/leads/lead-notes';
import { StatusUpdateForm } from '@/components/leads/status-update';
import { Badge } from '@/components/ui/badge';

export default async function LeadDetailPage({ params }: { params: { id: string } }) {
  const { getToken } = await auth();
  const token = await getToken();
  const lead = await api.getLead(params.id, token);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Main Content */}
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl">{lead.full_name}</CardTitle>
                <p className="text-muted-foreground">{lead.email}</p>
              </div>
              <LeadStatusBadge status={lead.status} />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Phone</p>
                <p>{lead.phone || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Company</p>
                <p>{lead.company || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Service Type</p>
                <Badge variant="secondary">{lead.service_type}</Badge>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Created</p>
                <p>{new Date(lead.created_at).toLocaleDateString()}</p>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Project Description
              </p>
              <p className="text-sm">{lead.project_description}</p>
            </div>

            <div>
              <p className="text-sm font-medium text-muted-foreground mb-2">
                Onboarding Answers
              </p>
              <div className="space-y-2">
                {Object.entries(lead.answers).map(([key, value]) => (
                  <div key={key} className="flex gap-2">
                    <strong className="text-sm">{key}:</strong>
                    <span className="text-sm">{String(value)}</span>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>AI-Generated Prompt</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-md">
              {lead.ai_prompt}
            </pre>
          </CardContent>
        </Card>
      </div>

      {/* Sidebar */}
      <div className="space-y-6">
        <StatusUpdateForm leadId={lead.id} currentStatus={lead.status} />
        <LeadNotes leadId={lead.id} />
      </div>
    </div>
  );
}
```



typescript
// components/pricing/pricing-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const pricingSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  price: z.number().min(0),
  currency: z.string().default('PHP'),
  timeline: z.string(),
  features: z.array(z.string()),
  popular: z.boolean().default(false),
});

export function PricingForm({ plan, onSubmit }: Props) {
  const form = useForm({
    resolver: zodResolver(pricingSchema),
    defaultValues: plan || {
      currency: 'PHP',
      popular: false,
      features: [''],
    },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="id"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plan ID</FormLabel>
              <FormControl>
                <Input {...field} placeholder="landing_page" />
              </FormControl>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Plan Name</FormLabel>
              <FormControl>
                <Input {...field} placeholder="Landing Page" />
              </FormControl>
            </FormItem>
          )}
        />

        <div className="grid grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="price"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Price</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    {...field}
                    onChange={(e) => field.onChange(parseInt(e.target.value))}
                  />
                </FormControl>
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="timeline"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Timeline</FormLabel>
                <FormControl>
                  <Input {...field} placeholder="48 hours" />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        {/* Features - Dynamic Array */}
        <FeaturesList control={form.control} />

        <FormField
          control={form.control}
          name="popular"
          render={({ field }) => (
            <FormItem className="flex items-center space-x-2">
              <FormControl>
                <Checkbox
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              </FormControl>
              <FormLabel>Mark as Popular</FormLabel>
            </FormItem>
          )}
        />

        <Button type="submit">Save Plan</Button>
      </form>
    </Form>
  );
}
```

---

## Components Library

### Key Reusable Components

#### 1. Data Table (with filtering, sorting, pagination)

```typescript
// components/shared/data-table.tsx
import {
  useReactTable,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
} from '@tanstack/react-table';

export function DataTable({ data, columns, searchKey, filters }: Props) {
  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="space-y-4">
      {/* Search & Filters */}
      <div className="flex items-center gap-4">
        <Input
          placeholder={`Search ${searchKey}...`}
          onChange={(e) => table.getColumn(searchKey)?.setFilterValue(e.target.value)}
        />
        {filters?.map((filter) => (
          <FilterDropdown key={filter.key} {...filter} />
        ))}
      </div>

      {/* Table */}
      <Table>
        {/* Header, Body, etc. */}
      </Table>

      {/* Pagination */}
      <DataTablePagination table={table} />
    </div>
  );
}
```

#### 2. Stats Card

```typescript
// components/dashboard/stats-card.tsx
export function StatsCard({ title, value, change, trend, icon }: Props) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className={cn(
          "text-xs",
          trend === 'up' ? 'text-green-600' : 'text-red-600'
        )}>
          {change} from last month
        </p>
      </CardContent>
    </Card>
  );
}
```

#### 3. Confirm Dialog

```typescript
// components/shared/confirm-dialog.tsx
export function ConfirmDialog({ title, description, onConfirm, children }: Props) {
  return (
    <AlertDialog>
      <AlertDialogTrigger asChild>
        {children}
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

#### 4. Rich Text Editor (Shadcn-Tiptap)

```typescript
// components/shared/rich-text-editor.tsx
'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import TextStyle from '@tiptap/extension-text-style';
import Color from '@tiptap/extension-color';
import { Button } from '@/components/ui/button';
import {
  Bold,
  Italic,
  List,
  ListOrdered,
  Link as LinkIcon,
  Heading2,
} from 'lucide-react';

interface RichTextEditorProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
}

export function RichTextEditor({ value, onChange, placeholder }: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({
        placeholder: placeholder || 'Start typing...',
      }),
      Link.configure({
        openOnClick: false,
      }),
      TextStyle,
      Color,
    ],
    content: value,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
  });

  if (!editor) {
    return null;
  }

  return (
    <div className="border rounded-md">
      {/* Toolbar */}
      <div className="border-b p-2 flex gap-1 flex-wrap">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={editor.isActive('bold') ? 'bg-muted' : ''}
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={editor.isActive('italic') ? 'bg-muted' : ''}
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={editor.isActive('heading', { level: 2 }) ? 'bg-muted' : ''}
        >
          <Heading2 className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={editor.isActive('bulletList') ? 'bg-muted' : ''}
        >
          <List className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={editor.isActive('orderedList') ? 'bg-muted' : ''}
        >
          <ListOrdered className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => {
            const url = window.prompt('Enter URL:');
            if (url) {
              editor.chain().focus().setLink({ href: url }).run();
            }
          }}
          className={editor.isActive('link') ? 'bg-muted' : ''}
        >
          <LinkIcon className="h-4 w-4" />
        </Button>
      </div>

      {/* Editor Content */}
      <EditorContent 
        editor={editor} 
        className="prose prose-sm max-w-none p-4 min-h-[200px] focus:outline-none"
      />
    </div>
  );
}
```

**Usage in Forms:**

```typescript
// Example: Company Info Editor with Rich Text
import { RichTextEditor } from '@/components/shared/rich-text-editor';

export function CompanyInfoForm({ company }: Props) {
  const form = useForm({
    defaultValues: {
      name: company?.name || '',
      description: company?.description || '', // Rich text content
      tagline: company?.tagline || '',
    },
  });

  return (
    <Form {...form}>
      <FormField
        control={form.control}
        name="description"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Company Description</FormLabel>
            <FormControl>
              <RichTextEditor
                value={field.value}
                onChange={field.onChange}
                placeholder="Describe your company..."
              />
            </FormControl>
            <FormDescription>
              This will be displayed on your website's about page
            </FormDescription>
          </FormItem>
        )}
      />
    </Form>
  );
}
```

**Use Cases in Admin Dashboard:**

1. **Company Description** - Rich formatted company profile
2. **Lead Notes** - Formatted internal notes with links and lists
3. **Service Descriptions** - Detailed service explanations with formatting
4. **Email Templates** - Pre-formatted email responses to leads
5. **Onboarding Question Descriptions** - Help text with formatting and links

---

## State Management

### Option 1: React Query (Recommended)

```typescript
// hooks/use-leads.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useLeads() {
  const queryClient = useQueryClient();

  const { data: leads, isLoading } = useQuery({
    queryKey: ['leads'],
    queryFn: () => api.getLeads(),
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }: { id: number; status: string }) =>
      api.updateLeadStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  const deleteLeadMutation = useMutation({
    mutationFn: (id: number) => api.deleteLead(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  return {
    leads,
    loading: isLoading,
    updateStatus: updateStatusMutation.mutate,
    deleteLead: deleteLeadMutation.mutate,
  };
}
```

### Option 2: Zustand (for UI state)

```typescript
// store/ui-store.ts
import { create } from 'zustand';

interface UiStore {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  toggleSidebar: () => void;
  setTheme: (theme: 'light' | 'dark') => void;
}

export const useUiStore = create<UiStore>((set) => ({
  sidebarOpen: true,
  theme: 'light',
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setTheme: (theme) => set({ theme }),
}));
```

---

## Implementation Roadmap

### Phase 1: Frontend Setup (Week 1)

**Day 1-2: Project Initialization**
- ✅ Create Next.js 15 project with App Router
- ✅ Install and configure Shadcn/ui + Tailwind CSS
- ✅ Set up Clerk authentication
- ✅ Install Tiptap for rich text editing
- ✅ Configure TypeScript types from backend API
- ✅ Set up folder structure

**Day 3-4: Core Components & Layout**
- ✅ Dashboard layout (sidebar + header)
- ✅ Clerk sign-in/sign-up pages
- ✅ Protected route middleware
- ✅ View toggle component (Table/Card switcher)
- ✅ Rich text editor component
- ✅ Data table component
- ✅ Confirm dialog component
- ✅ Loading skeletons

**Day 5-7: API Client & Data Hooks**
- ✅ API client with Clerk token integration
- ✅ TanStack Query hooks for all resources:
  - `use-pricing.ts`
  - `use-services.ts`
  - `use-features.ts`
  - `use-addons.ts`
  - `use-leads.ts`
  - `use-analytics.ts`
- ✅ Error handling and toast notifications
- ✅ View mode persistence hook (`use-view-mode.ts`)

### Phase 2: CRUD Pages - Pricing & Services (Week 2)

**Day 1-3: Pricing Plans CRUD**
- ✅ List page with Table + Card views
- ✅ Pricing table component
- ✅ Pricing card grid component
- ✅ Create pricing plan page + form
- ✅ Edit pricing plan page
- ✅ Delete confirmation
- ✅ Features dynamic array in form
- ✅ Popular flag toggle

**Day 4-5: Services CRUD**
- ✅ List page with Table + Card views
- ✅ Service table component
- ✅ Service card grid component
- ✅ Create service page + form
- ✅ Edit service page
- ✅ Delete confirmation
- ✅ Rich text description editor

**Day 6-7: Testing & Refinement**
- ✅ Test all CRUD operations
- ✅ Test view switching (Table ↔ Card)
- ✅ Test form validations
- ✅ Polish UI/UX
- ✅ Add loading states

### Phase 3: CRUD Pages - Features & Add-ons (Week 3)

**Day 1-3: Features CRUD**
- ✅ List page with Table + Card views
- ✅ Feature table component
- ✅ Feature card grid component
- ✅ Create feature page + form
- ✅ Edit feature page
- ✅ Delete confirmation
- ✅ Display order management
- ✅ Rich text description editor

**Day 4-5: Add-ons CRUD**
- ✅ List page with Table + Card views
- ✅ Add-on table component
- ✅ Add-on card grid component
- ✅ Create add-on page + form
- ✅ Edit add-on page
- ✅ Delete confirmation
- ✅ Rich text description editor

**Day 6-7: Company Info & Onboarding**
- ✅ Company info editor page
- ✅ Rich text editor for company description
- ✅ Onboarding questions list (Card view)
- ✅ Create/Edit onboarding questions
- ✅ JSON schema editor for questions

### Phase 4: Leads Management (Week 4)

**Day 1-3: Leads List & Detail**
- ✅ List page with Table + Card views
- ✅ Lead table with status filtering
- ✅ Lead card grid with status badges
- ✅ Search and filter functionality
- ✅ Lead detail page
- ✅ Status badges component
- ✅ Lead status update form

**Day 4-5: Lead Actions**
- ✅ Export leads to CSV
- ✅ Bulk status updates
- ✅ Lead notes section
- ✅ View AI-generated prompt
- ✅ Contact history timeline

**Day 6-7: Analytics Dashboard**
- ✅ Stats cards (Total Leads, Conversion Rate, etc.)
- ✅ Leads timeline chart (Recharts)
- ✅ Leads by status pie chart
- ✅ Leads by service bar chart
- ✅ Recent activity feed
- ✅ Quick actions panel

### Phase 5: Polish & Deployment (Week 5)

**Day 1-2: UI/UX Polish**
- ✅ Consistent spacing and typography
- ✅ Mobile responsive design
- ✅ Dark mode support (optional)
- ✅ Toast notifications
- ✅ Error boundaries
- ✅ Loading states everywhere

**Day 3-4: Testing**
- ✅ Manual testing all flows
- ✅ Test CRUD operations for all resources
- ✅ Test dual views (Table + Card)
- ✅ Test authentication flows
- ✅ Test form validations
- ✅ Fix bugs

**Day 5: Deployment**
- ✅ Configure Vercel project
- ✅ Set environment variables
- ✅ Deploy to production
- ✅ Test production deployment
- ✅ Set up custom domain (optional)

**Day 6-7: Documentation & Handoff**
- ✅ Create admin user guide
- ✅ Document API integration
- ✅ Write deployment guide
- ✅ Create video walkthrough (optional)

---

## Quick Start Commands

### Backend Development

```bash
# Create new migration for lead status
alembic revision --autogenerate -m "add lead status and notes"
alembic upgrade head

# Test new endpoints
pytest tests/test_pricing_crud.py -v
pytest tests/test_analytics.py -v
```

### Frontend Development

**Option 1: Create New Project Directory**
```bash
npx create-next-app@latest admin-dashboard --typescript --tailwind --app --no-src-dir
cd admin-dashboard
```

**Option 2: Initialize in Current Directory**
```bash
# Make sure you're in an empty directory first
npx create-next-app@latest . --typescript --tailwind --app --no-src-dir

# Install core dependencies
npm install @tanstack/react-table @tanstack/react-query
npm install react-hook-form @hookform/resolvers zod
npm install recharts lucide-react
npm install date-fns

# Install Clerk for authentication
npm install @clerk/nextjs

# Install Tiptap for rich text editing
npm install @tiptap/react @tiptap/starter-kit @tiptap/extension-placeholder
npm install @tiptap/extension-text-style @tiptap/extension-color @tiptap/extension-link

# Install Shadcn UI
npx shadcn@latest init

# Add required Shadcn components
npx shadcn@latest add button card input table dialog dropdown-menu
npx shadcn@latest add form checkbox textarea badge select
npx shadcn@latest add alert-dialog toast tabs separator
npx shadcn@latest add sheet avatar skeleton

# Run development server
npm run dev
```

**Environment Variables (`.env.local`):**

```bash
# Clerk Authentication
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/dashboard
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/dashboard

# API Configuration
NEXT_PUBLIC_API_URL=https://lunaxcode-fastapi.vercel.app/api/v1
# For local backend testing:
# NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## Security Considerations

1. **API Key Management**
   - Store in environment variables
   - Never expose in frontend code
   - Use server-side API routes if needed

2. **Input Validation**
   - Validate all inputs with Zod
   - Sanitize user inputs
   - Use parameterized queries (SQLAlchemy handles this)

3. **CORS**
   - Add admin dashboard URL to CORS_ORIGINS
   - Example: `https://admin.lunaxcode.site`

4. **Rate Limiting**
   - Implement rate limiting on sensitive endpoints
   - Use SlowAPI (already in requirements)

5. **HTTPS Only**
   - Force HTTPS in production
   - Set secure cookie flags

---

## Deployment

### Backend (Already Deployed)
- Vercel: `https://lunaxcode-fastapi.vercel.app`
- Just need to add new endpoints

### Frontend (New Deployment)

**Option 1: Vercel**
```bash
# Deploy admin dashboard
cd admin-dashboard
vercel --prod

# Set environment variables in Vercel dashboard
NEXT_PUBLIC_API_URL=https://lunaxcode-fastapi.vercel.app
API_KEY=your_admin_api_key
```

**Option 2: Subdomain**
- Deploy to `admin.lunaxcode.site`
- Add DNS record
- Configure in Vercel

---

## Next Steps

1. **Review this guide** and decide on:
   - Authentication method (API Key vs JWT)
   - Which features to prioritize
   - Timeline

2. **Backend work** (lunaxcode-fastapi):
   - Add missing CRUD endpoints
   - Create analytics endpoints
   - Update database schema

3. **Frontend work** (new repo):
   - Set up Next.js project
   - Implement dashboard layout
   - Build CRUD interfaces

4. **Integration**:
   - Connect frontend to new endpoints
   - Test all flows
   - Deploy both

---

**Ready to build the admin dashboard!** 🚀

Let me know which phase you'd like to start with, and I can provide more detailed implementation code.

