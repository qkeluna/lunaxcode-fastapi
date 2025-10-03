# TanStack Start + Clerk Quick Start Guide

Complete guide for setting up the admin dashboard with TanStack Start and Clerk authentication.

---

## 🚀 Quick Start

### 1. Create TanStack Start Project

```bash
# Create new project
npm create @tanstack/start@latest admin-dashboard

# Navigate to project
cd admin-dashboard

# Install dependencies
npm install
```

### 2. Install Clerk

```bash
npm install @clerk/tanstack-start
```

### 3. Install Additional Dependencies

```bash
# UI and Forms
npm install react-hook-form @hookform/resolvers zod

# Charts and Icons
npm install recharts lucide-react

# HTTP Client
npm install axios

# Shadcn UI (optional but recommended)
npx shadcn@latest init
npx shadcn@latest add button card input table dialog form toast badge
```

---

## 🔐 Clerk Setup

### Step 1: Create Clerk Account

1. Go to https://clerk.com
2. Sign up for free account
3. Create new application
4. Choose "TanStack Start" as framework

### Step 2: Get API Keys

From Clerk Dashboard → API Keys:
- **Publishable Key**: Starts with `pk_test_...` or `pk_live_...`
- **Secret Key**: Starts with `sk_test_...` or `sk_live_...`

### Step 3: Configure Environment Variables

Create `.env` file in project root:

```env
# Clerk Keys
VITE_CLERK_PUBLISHABLE_KEY=pk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CLERK_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# API Configuration
VITE_API_URL=https://lunaxcode-fastapi.vercel.app
```

### Step 4: Configure User Metadata for Roles

In Clerk Dashboard → **User & Authentication** → **Metadata**:

Add custom metadata field:
```json
{
  "public_metadata": {
    "role": "admin"
  }
}
```

This will be used to check admin access in your backend.

---

## 📁 Project Structure

```
admin-dashboard/
├── app/
│   ├── routes/
│   │   ├── __root.tsx           # Root layout with Clerk
│   │   ├── index.tsx            # Landing page
│   │   ├── sign-in.tsx          # Clerk sign-in
│   │   ├── sign-up.tsx          # Clerk sign-up
│   │   └── _auth/               # Protected routes
│   │       ├── route.tsx        # Auth layout (sidebar + header)
│   │       └── dashboard/
│   │           ├── index.tsx    # Dashboard home
│   │           ├── leads/
│   │           ├── pricing/
│   │           └── ...
│   ├── client.tsx
│   └── ssr.tsx
├── components/
│   ├── ui/                      # Shadcn components
│   ├── dashboard/               # Dashboard components
│   └── shared/                  # Reusable components
├── lib/
│   ├── api.ts                   # API client with Clerk token
│   └── utils.ts
├── hooks/
│   └── use-*.ts                 # Custom hooks
├── types/
│   └── api.ts
├── app.config.ts                # TanStack Start config
└── .env                         # Environment variables
```

---

## 🔧 Implementation Steps

### 1. Root Layout with Clerk Provider

```typescript
// app/routes/__root.tsx
import { ClerkProvider } from '@clerk/tanstack-start';
import { Outlet, ScrollRestoration, createRootRoute } from '@tanstack/react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TanStackRouterDevtools } from '@tanstack/router-devtools';

const queryClient = new QueryClient();

export const Route = createRootRoute({
  component: RootComponent,
});

function RootComponent() {
  return (
    <ClerkProvider
      publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}
    >
      <QueryClientProvider client={queryClient}>
        <html lang="en">
          <head>
            <meta charSet="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Lunaxcode Admin</title>
          </head>
          <body>
            <Outlet />
            <ScrollRestoration />
            {process.env.NODE_ENV === 'development' && (
              <TanStackRouterDevtools position="bottom-right" />
            )}
          </body>
        </html>
      </QueryClientProvider>
    </ClerkProvider>
  );
}
```

### 2. Sign In Page

```typescript
// app/routes/sign-in.tsx
import { createFileRoute } from '@tanstack/react-router';
import { SignIn } from '@clerk/tanstack-start';

export const Route = createFileRoute('/sign-in')({
  component: SignInPage,
});

function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <SignIn
        routing="path"
        path="/sign-in"
        signUpUrl="/sign-up"
        afterSignInUrl="/dashboard"
        appearance={{
          elements: {
            rootBox: 'mx-auto',
            card: 'shadow-xl',
          },
        }}
      />
    </div>
  );
}
```

### 3. Sign Up Page

```typescript
// app/routes/sign-up.tsx
import { createFileRoute } from '@tanstack/react-router';
import { SignUp } from '@clerk/tanstack-start';

export const Route = createFileRoute('/sign-up')({
  component: SignUpPage,
});

function SignUpPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <SignUp
        routing="path"
        path="/sign-up"
        signInUrl="/sign-in"
        afterSignUpUrl="/dashboard"
      />
    </div>
  );
}
```

### 4. Protected Routes Layout

```typescript
// app/routes/_auth/route.tsx
import { createFileRoute, redirect, Outlet } from '@tanstack/react-router';
import { useAuth } from '@clerk/tanstack-start';
import { DashboardLayout } from '@/components/dashboard/layout';

export const Route = createFileRoute('/_auth')({
  beforeLoad: async () => {
    const { isSignedIn } = useAuth();
    
    if (!isSignedIn) {
      throw redirect({
        to: '/sign-in',
        search: {
          redirect: location.href,
        },
      });
    }
  },
  component: AuthLayout,
});

function AuthLayout() {
  return (
    <DashboardLayout>
      <Outlet />
    </DashboardLayout>
  );
}
```

### 5. Dashboard Layout Component

```typescript
// components/dashboard/layout.tsx
import { useAuth, UserButton } from '@clerk/tanstack-start';
import { Link } from '@tanstack/react-router';
import { 
  LayoutDashboard, 
  Users, 
  DollarSign, 
  Settings 
} from 'lucide-react';

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();

  return (
    <div className="flex h-screen">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-gray-50">
        <div className="p-4">
          <h1 className="text-xl font-bold">Lunaxcode Admin</h1>
        </div>
        
        <nav className="px-2 space-y-1">
          <Link
            to="/dashboard"
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-200"
          >
            <LayoutDashboard size={20} />
            Dashboard
          </Link>
          
          <Link
            to="/dashboard/leads"
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-200"
          >
            <Users size={20} />
            Leads
          </Link>
          
          <Link
            to="/dashboard/pricing"
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-200"
          >
            <DollarSign size={20} />
            Pricing
          </Link>
          
          <Link
            to="/dashboard/settings"
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-gray-200"
          >
            <Settings size={20} />
            Settings
          </Link>
        </nav>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="border-b bg-white px-6 py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Welcome, {user?.firstName}!</h2>
            <UserButton afterSignOutUrl="/sign-in" />
          </div>
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
```

### 6. API Client with Clerk Token

```typescript
// lib/api.ts
import axios, { AxiosInstance } from 'axios';
import { useAuth } from '@clerk/tanstack-start';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: `${import.meta.env.VITE_API_URL}/api/v1`,
      timeout: 10000,
    });
  }

  // Helper to get token and make authenticated request
  private async makeAuthRequest<T>(
    method: 'get' | 'post' | 'put' | 'delete' | 'patch',
    url: string,
    token: string,
    data?: any
  ): Promise<T> {
    const response = await this.client.request<T>({
      method,
      url,
      data,
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }

  // Analytics
  async getAnalytics(token: string) {
    return this.makeAuthRequest('get', '/analytics/dashboard', token);
  }

  // Leads
  async getLeads(token: string) {
    return this.makeAuthRequest('get', '/leads', token);
  }

  async getLead(id: number, token: string) {
    return this.makeAuthRequest('get', `/leads/${id}`, token);
  }

  async updateLeadStatus(id: number, status: string, token: string) {
    return this.makeAuthRequest('patch', `/leads/${id}/status`, token, { status });
  }

  // Pricing Plans
  async getPricingPlans() {
    const response = await this.client.get('/pricing');
    return response.data;
  }

  async createPricingPlan(plan: any, token: string) {
    return this.makeAuthRequest('post', '/pricing', token, plan);
  }

  async updatePricingPlan(id: string, plan: any, token: string) {
    return this.makeAuthRequest('put', `/pricing/${id}`, token, plan);
  }

  async deletePricingPlan(id: string, token: string) {
    return this.makeAuthRequest('delete', `/pricing/${id}`, token);
  }
}

export const api = new ApiClient();
```

### 7. Custom Hook for Data Fetching

```typescript
// hooks/use-leads.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '@clerk/tanstack-start';
import { api } from '@/lib/api';

export function useLeads() {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const { data: leads, isLoading, error } = useQuery({
    queryKey: ['leads'],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Not authenticated');
      return api.getLeads(token);
    },
  });

  const updateStatusMutation = useMutation({
    mutationFn: async ({ id, status }: { id: number; status: string }) => {
      const token = await getToken();
      if (!token) throw new Error('Not authenticated');
      return api.updateLeadStatus(id, status, token);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['leads'] });
    },
  });

  return {
    leads,
    loading: isLoading,
    error,
    updateStatus: updateStatusMutation.mutate,
  };
}
```

### 8. Dashboard Page Example

```typescript
// app/routes/_auth/dashboard/index.tsx
import { createFileRoute } from '@tanstack/react-router';
import { useQuery } from '@tanstack/react-query';
import { useAuth } from '@clerk/tanstack-start';
import { api } from '@/lib/api';
import { StatsCard } from '@/components/dashboard/stats-card';

export const Route = createFileRoute('/_auth/dashboard/')({
  component: DashboardPage,
});

function DashboardPage() {
  const { getToken } = useAuth();

  const { data: stats, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new Error('Not authenticated');
      return api.getAnalytics(token);
    },
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatsCard
          title="Total Leads"
          value={stats?.totalLeads || 0}
          change="+12%"
          trend="up"
        />
        <StatsCard
          title="Conversion Rate"
          value={`${stats?.conversionRate || 0}%`}
          change="+5%"
          trend="up"
        />
        {/* More stats... */}
      </div>
    </div>
  );
}
```

---

## 🔒 Backend Integration (FastAPI)

### 1. Install Required Package

```bash
pip install python-jose[cryptography]
```

### 2. Update `requirements.txt`

```txt
# Add to existing requirements
python-jose[cryptography]==3.3.0
```

### 3. Add Clerk Settings

```python
# api/config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_PUBLIC_KEY: str = ""  # Get from Clerk Dashboard → API Keys → Advanced → JWT Public Key
    CLERK_ISSUER: str = ""  # e.g., https://clerk.your-domain.com
```

### 4. Create Clerk Auth Dependency

```python
# api/utils/clerk_auth.py
from jose import jwt, JWTError
from fastapi import Header, HTTPException
from api.config import settings

async def verify_clerk_token(authorization: str = Header(...)):
    """
    Verify Clerk JWT token from Authorization header
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(
            token,
            settings.CLERK_JWT_PUBLIC_KEY,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
        )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        metadata = payload.get("public_metadata", {})
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check for admin role
        if metadata.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return {
            "user_id": user_id,
            "email": email,
            "metadata": metadata
        }
        
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}"
        )
```

### 5. Update Endpoints to Use Clerk Auth

```python
# api/routers/pricing.py
from api.utils.clerk_auth import verify_clerk_token

@router.post("/pricing", status_code=201)
async def create_pricing_plan(
    plan: PricingPlanCreate,
    db: AsyncSession = Depends(get_db),
    clerk_user: dict = Depends(verify_clerk_token)
):
    """Create new pricing plan (Admin only)"""
    # clerk_user contains user_id, email, metadata
    # User is already verified as admin
    # ... implementation ...
    pass
```

### 6. Set Vercel Environment Variables

In Vercel Dashboard → Project → Settings → Environment Variables:

```
CLERK_SECRET_KEY=sk_live_xxxxx
CLERK_JWT_PUBLIC_KEY=-----BEGIN PUBLIC KEY-----\nMII...\n-----END PUBLIC KEY-----
CLERK_ISSUER=https://clerk.your-domain.com
```

**Note:** Get JWT Public Key from Clerk Dashboard → API Keys → Show JWT public key

---

## 🎨 Styling with Tailwind

TanStack Start comes with Tailwind CSS pre-configured. Customize in `tailwind.config.ts`:

```typescript
import type { Config } from 'tailwindcss';

export default {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          // Your brand colors
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
```

---

## 🧪 Testing Authentication Flow

### 1. Sign Up Test User

1. Go to `http://localhost:3000/sign-up`
2. Create account with email
3. Verify email
4. You should redirect to `/dashboard`

### 2. Set Admin Role in Clerk

1. Go to Clerk Dashboard → Users
2. Click on your test user
3. Go to **Metadata** tab
4. Add to **Public metadata**:
```json
{
  "role": "admin"
}
```
5. Save

### 3. Test Protected Route

1. Try accessing `/dashboard` without signing in
2. Should redirect to `/sign-in`
3. Sign in with test user
4. Should access dashboard successfully

### 4. Test API Calls

```typescript
// Test in browser console after signing in
const token = await window.Clerk.session.getToken();
console.log('Token:', token);

// Make API call
fetch('https://lunaxcode-fastapi.vercel.app/api/v1/leads', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(r => r.json())
.then(console.log);
```

---

## 🚢 Deployment

### Deploy Frontend to Vercel

```bash
# Connect to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin your-repo-url
git push -u origin main

# Deploy to Vercel
vercel --prod

# Or use Vercel dashboard to connect GitHub repo
```

### Environment Variables in Vercel

Set these in Vercel Dashboard:
- `VITE_CLERK_PUBLISHABLE_KEY`
- `VITE_API_URL`

---

## 📚 Additional Resources

- **TanStack Start Docs:** https://tanstack.com/start
- **TanStack Router:** https://tanstack.com/router
- **TanStack Query:** https://tanstack.com/query
- **Clerk Docs:** https://clerk.com/docs
- **Clerk + TanStack Start:** https://clerk.com/docs/references/tanstack-start

---

## 🎯 Next Steps

1. ✅ Complete backend CRUD endpoints (see `ADMIN_DASHBOARD_GUIDE.md`)
2. ✅ Build dashboard pages (Analytics, Leads, Pricing, etc.)
3. ✅ Add charts with Recharts
4. ✅ Implement data tables with TanStack Table
5. ✅ Add forms with React Hook Form + Zod
6. ✅ Deploy to production

---

**You're ready to build a modern, type-safe admin dashboard with TanStack Start and Clerk!** 🚀

