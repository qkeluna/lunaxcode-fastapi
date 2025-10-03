# Frontend API Integration Guide

## 🎯 Overview

This guide helps you integrate the **lunaxcode-fastapi** backend with your **lunaxcode-site** Next.js frontend.

**API Base URL:** `https://lunaxcode-fastapi.vercel.app`

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Endpoints](#api-endpoints)
3. [TypeScript Types](#typescript-types)
4. [API Service Implementation](#api-service-implementation)
5. [React Hooks](#react-hooks)
6. [Usage Examples](#usage-examples)
7. [Error Handling](#error-handling)
8. [CORS Configuration](#cors-configuration)

---

## Quick Start

### 1. Environment Variables

Create/update `.env.local` in your Next.js project:

```env
# API Configuration
NEXT_PUBLIC_API_URL=https://lunaxcode-fastapi.vercel.app
NEXT_PUBLIC_API_VERSION=v1

# For admin operations (optional - use server-side only)
API_KEY=your_admin_api_key_here
```

### 2. Install Dependencies (if needed)

```bash
npm install axios
# or
npm install swr  # For data fetching with caching
```

---

## API Endpoints

### Public Endpoints (No Authentication)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| `GET` | `/api/v1/health` | API health check | Health status |
| `GET` | `/api/v1/pricing` | Get all pricing plans | Array of pricing plans |
| `GET` | `/api/v1/services` | Get all services | Array of services |
| `GET` | `/api/v1/features` | Get all features | Array of features |
| `GET` | `/api/v1/company` | Get company info | Company details |
| `GET` | `/api/v1/addons` | Get all add-ons | Array of add-ons |
| `GET` | `/api/v1/onboarding/questions/{service_type}` | Get onboarding questions | Dynamic form schema |
| `POST` | `/api/v1/leads` | Submit lead/contact form | Created lead |

### Admin Endpoints (Require `X-API-Key` header)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/leads` | Get all leads |
| `GET` | `/api/v1/leads/{id}` | Get specific lead |

---

## TypeScript Types

### Create `types/api.ts` in your Next.js project:

```typescript
// Base Types
export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  timeline: string;
  features: string[];
  popular: boolean;
  created_at: string;
  updated_at: string;
}

export interface Service {
  id: string;
  name: string;
  description: string;
  details: string;
  icon: string;
  timeline: string;
  created_at: string;
  updated_at: string;
}

export interface Feature {
  id: number;
  icon: string;
  title: string;
  description: string;
  display_order: number;
  created_at: string;
  updated_at: string;
}

export interface Addon {
  id: number;
  name: string;
  description: string;
  price_range: string;
  icon: string;
  created_at: string;
  updated_at: string;
}

export interface CompanyInfo {
  id: number;
  name: string;
  tagline: string;
  description: string;
  contact: {
    email: string;
    phone: string;
    location: string;
  };
  payment_terms: {
    deposit: string;
    balance: string;
    methods: string[];
  };
  updated_at: string;
}

export interface OnboardingQuestion {
  id: string;
  type: 'text' | 'textarea' | 'select' | 'radio' | 'checkbox' | 'number' | 'date';
  label: string;
  placeholder?: string;
  required: boolean;
  options?: string[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
  };
  display_order: number;
}

export interface OnboardingSchema {
  service_type: string;
  questions: OnboardingQuestion[];
}

// Lead Submission
export interface LeadCreate {
  name: string;
  email: string;
  phone?: string;
  company?: string;
  service_type: string;
  budget_range: string;
  timeline?: string;
  project_description?: string;
  answers: Record<string, any>;
  source?: string;
}

export interface Lead extends LeadCreate {
  id: number;
  ai_prompt: string;
  status: string;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  service: string;
  version: string;
}

export interface DatabaseHealthResponse {
  status: 'healthy' | 'unhealthy';
  database: 'connected' | 'disconnected';
  error?: string;
}

export interface ApiError {
  detail: string;
}
```

---

## API Service Implementation

### Create `lib/api.ts`:

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  PricingPlan,
  Service,
  Feature,
  Addon,
  CompanyInfo,
  OnboardingSchema,
  LeadCreate,
  Lead,
  HealthResponse,
  DatabaseHealthResponse,
  ApiError,
} from '@/types/api';

class ApiService {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'https://lunaxcode-fastapi.vercel.app';
    
    this.client = axios.create({
      baseURL: `${this.baseUrl}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 10000, // 10 seconds
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response) {
          // Server responded with error
          console.error('API Error:', error.response.data);
          throw new Error(error.response.data.detail || 'An error occurred');
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
          throw new Error('Network error. Please check your connection.');
        } else {
          // Something else happened
          console.error('Error:', error.message);
          throw error;
        }
      }
    );
  }

  // Health Checks
  async healthCheck(): Promise<HealthResponse> {
    const { data } = await this.client.get<HealthResponse>('/health');
    return data;
  }

  async databaseHealth(): Promise<DatabaseHealthResponse> {
    const { data } = await this.client.get<DatabaseHealthResponse>('/health/db');
    return data;
  }

  // Pricing Plans
  async getPricingPlans(): Promise<PricingPlan[]> {
    const { data } = await this.client.get<PricingPlan[]>('/pricing');
    return data;
  }

  async getPricingPlan(id: string): Promise<PricingPlan> {
    const { data } = await this.client.get<PricingPlan>(`/pricing/${id}`);
    return data;
  }

  // Services
  async getServices(): Promise<Service[]> {
    const { data } = await this.client.get<Service[]>('/services');
    return data;
  }

  async getService(id: string): Promise<Service> {
    const { data } = await this.client.get<Service>(`/services/${id}`);
    return data;
  }

  // Features
  async getFeatures(): Promise<Feature[]> {
    const { data } = await this.client.get<Feature[]>('/features');
    return data;
  }

  // Add-ons
  async getAddons(): Promise<Addon[]> {
    const { data } = await this.client.get<Addon[]>('/addons');
    return data;
  }

  // Company Info
  async getCompanyInfo(): Promise<CompanyInfo> {
    const { data } = await this.client.get<CompanyInfo>('/company');
    return data;
  }

  // Onboarding Questions
  async getOnboardingQuestions(serviceType: string): Promise<OnboardingSchema> {
    const { data } = await this.client.get<OnboardingSchema>(
      `/onboarding/questions/${serviceType}`
    );
    return data;
  }

  // Leads
  async createLead(lead: LeadCreate): Promise<Lead> {
    const { data } = await this.client.post<Lead>('/leads', lead);
    return data;
  }

  // Admin endpoints (require API key)
  async getLeads(apiKey: string): Promise<Lead[]> {
    const { data } = await this.client.get<Lead[]>('/leads', {
      headers: { 'X-API-Key': apiKey },
    });
    return data;
  }

  async getLead(id: number, apiKey: string): Promise<Lead> {
    const { data } = await this.client.get<Lead>(`/leads/${id}`, {
      headers: { 'X-API-Key': apiKey },
    });
    return data;
  }
}

// Export singleton instance
export const api = new ApiService();

// Export class for testing or custom instances
export default ApiService;
```

---

## React Hooks

### Create `hooks/useApi.ts`:

```typescript
import { useState, useEffect } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useApi<T>(
  fetchFunction: () => Promise<T>,
  dependencies: any[] = []
): UseApiState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await fetchFunction();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('An error occurred'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, dependencies);

  return { data, loading, error, refetch: fetchData };
}
```

### Using SWR (Alternative - Recommended)

```typescript
// hooks/useApi.ts (SWR version)
import useSWR from 'swr';
import { api } from '@/lib/api';

export function usePricingPlans() {
  const { data, error, isLoading, mutate } = useSWR(
    'pricing-plans',
    () => api.getPricingPlans(),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000, // 1 minute
    }
  );

  return {
    plans: data,
    loading: isLoading,
    error,
    refetch: mutate,
  };
}

export function useServices() {
  const { data, error, isLoading, mutate } = useSWR(
    'services',
    () => api.getServices(),
    { revalidateOnFocus: false }
  );

  return {
    services: data,
    loading: isLoading,
    error,
    refetch: mutate,
  };
}

export function useFeatures() {
  const { data, error, isLoading } = useSWR(
    'features',
    () => api.getFeatures(),
    { revalidateOnFocus: false }
  );

  return {
    features: data,
    loading: isLoading,
    error,
  };
}

export function useCompanyInfo() {
  const { data, error, isLoading } = useSWR(
    'company-info',
    () => api.getCompanyInfo(),
    { revalidateOnFocus: false }
  );

  return {
    company: data,
    loading: isLoading,
    error,
  };
}

export function useOnboardingQuestions(serviceType: string | null) {
  const { data, error, isLoading } = useSWR(
    serviceType ? `onboarding-${serviceType}` : null,
    () => serviceType ? api.getOnboardingQuestions(serviceType) : null,
    { revalidateOnFocus: false }
  );

  return {
    schema: data,
    loading: isLoading,
    error,
  };
}
```

---

## Usage Examples

### 1. Pricing Page Component

```typescript
// app/pricing/page.tsx
'use client';

import { usePricingPlans } from '@/hooks/useApi';
import PricingCard from '@/components/PricingCard';
import LoadingSpinner from '@/components/LoadingSpinner';

export default function PricingPage() {
  const { plans, loading, error } = usePricingPlans();

  if (loading) return <LoadingSpinner />;
  if (error) return <div>Error loading pricing: {error.message}</div>;
  if (!plans) return null;

  return (
    <div className="pricing-grid">
      {plans.map((plan) => (
        <PricingCard key={plan.id} plan={plan} />
      ))}
    </div>
  );
}
```

### 2. Services Section

```typescript
// components/ServicesSection.tsx
'use client';

import { useServices } from '@/hooks/useApi';

export default function ServicesSection() {
  const { services, loading, error } = useServices();

  if (loading) return <div>Loading services...</div>;
  if (error) return null; // Fail silently or show error

  return (
    <section className="services">
      <h2>Our Services</h2>
      <div className="services-grid">
        {services?.map((service) => (
          <div key={service.id} className="service-card">
            <span className="icon">{service.icon}</span>
            <h3>{service.name}</h3>
            <p>{service.description}</p>
            <span className="timeline">{service.timeline}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
```

### 3. Contact/Lead Form

```typescript
// components/LeadForm.tsx
'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { LeadCreate } from '@/types/api';

export default function LeadForm() {
  const [formData, setFormData] = useState<LeadCreate>({
    name: '',
    email: '',
    phone: '',
    company: '',
    service_type: 'landing_page',
    budget_range: '5000-10000',
    timeline: '',
    project_description: '',
    answers: {},
  });

  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await api.createLead(formData);
      setSuccess(true);
      // Reset form or redirect
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit');
    } finally {
      setSubmitting(false);
    }
  };

  if (success) {
    return (
      <div className="success-message">
        <h3>Thank you! We'll get back to you soon.</h3>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Your Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
        required
      />
      
      <input
        type="email"
        placeholder="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />

      <textarea
        placeholder="Project Description"
        value={formData.project_description}
        onChange={(e) => setFormData({ ...formData, project_description: e.target.value })}
      />

      {error && <div className="error">{error}</div>}

      <button type="submit" disabled={submitting}>
        {submitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

### 4. Server-Side Rendering (SSR/SSG)

```typescript
// app/pricing/page.tsx (Server Component)
import { api } from '@/lib/api';
import PricingCard from '@/components/PricingCard';

export const revalidate = 3600; // Revalidate every hour

export default async function PricingPage() {
  const plans = await api.getPricingPlans();

  return (
    <div className="pricing-grid">
      {plans.map((plan) => (
        <PricingCard key={plan.id} plan={plan} />
      ))}
    </div>
  );
}
```

### 5. Dynamic Onboarding Form

```typescript
// components/OnboardingForm.tsx
'use client';

import { useState } from 'react';
import { useOnboardingQuestions } from '@/hooks/useApi';

interface Props {
  serviceType: string;
}

export default function OnboardingForm({ serviceType }: Props) {
  const { schema, loading } = useOnboardingQuestions(serviceType);
  const [answers, setAnswers] = useState<Record<string, any>>({});

  if (loading) return <div>Loading form...</div>;
  if (!schema) return null;

  return (
    <form>
      <h2>Tell us about your {schema.service_type} project</h2>
      
      {schema.questions.map((question) => (
        <div key={question.id} className="form-field">
          <label>
            {question.label}
            {question.required && <span className="required">*</span>}
          </label>

          {question.type === 'text' && (
            <input
              type="text"
              placeholder={question.placeholder}
              required={question.required}
              onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
            />
          )}

          {question.type === 'textarea' && (
            <textarea
              placeholder={question.placeholder}
              required={question.required}
              onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
            />
          )}

          {question.type === 'select' && (
            <select
              required={question.required}
              onChange={(e) => setAnswers({ ...answers, [question.id]: e.target.value })}
            >
              <option value="">Select...</option>
              {question.options?.map((opt) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          )}
        </div>
      ))}

      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## Error Handling

### Global Error Boundary

```typescript
// components/ErrorBoundary.tsx
'use client';

import { Component, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service (e.g., Sentry)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### API Error Toast

```typescript
// lib/errorHandler.ts
import { toast } from 'react-hot-toast'; // or your toast library

export function handleApiError(error: unknown) {
  if (error instanceof Error) {
    toast.error(error.message);
    console.error('API Error:', error);
  } else {
    toast.error('An unexpected error occurred');
    console.error('Unknown error:', error);
  }
}

// Usage
try {
  await api.createLead(formData);
} catch (error) {
  handleApiError(error);
}
```

---

## CORS Configuration

The API is configured to accept requests from your frontend. If you encounter CORS issues:

### 1. Verify CORS Origins in Vercel

The backend's `CORS_ORIGINS` environment variable should include your frontend URL:

```
CORS_ORIGINS=https://lunaxcode.site,https://www.lunaxcode.site,http://localhost:3000
```

### 2. For Local Development

Add `http://localhost:3000` to the backend's CORS configuration.

### 3. Debugging CORS

```typescript
// Test CORS from browser console
fetch('https://lunaxcode-fastapi.vercel.app/api/v1/health')
  .then(res => res.json())
  .then(data => console.log('CORS working:', data))
  .catch(err => console.error('CORS error:', err));
```

---

## Performance Optimization

### 1. Use SWR for Automatic Caching

```bash
npm install swr
```

```typescript
// app/providers.tsx
'use client';

import { SWRConfig } from 'swr';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SWRConfig
      value={{
        refreshInterval: 0,
        revalidateOnFocus: false,
        revalidateOnReconnect: true,
        dedupingInterval: 2000,
      }}
    >
      {children}
    </SWRConfig>
  );
}
```

### 2. Static Generation for Pricing/Services

```typescript
// app/pricing/page.tsx
export const revalidate = 3600; // ISR: Revalidate every hour

export default async function PricingPage() {
  const plans = await api.getPricingPlans();
  return <PricingGrid plans={plans} />;
}
```

### 3. Parallel Data Fetching

```typescript
// Fetch multiple endpoints in parallel
const [plans, services, features] = await Promise.all([
  api.getPricingPlans(),
  api.getServices(),
  api.getFeatures(),
]);
```

---

## Testing

### Mock API for Testing

```typescript
// __mocks__/api.ts
export const api = {
  getPricingPlans: jest.fn(() => Promise.resolve([
    {
      id: 'test-plan',
      name: 'Test Plan',
      price: 1000,
      // ... other fields
    },
  ])),
  // ... other mocked methods
};
```

---

## Migration Checklist

- [ ] Install dependencies (`axios` or `swr`)
- [ ] Set up environment variables
- [ ] Copy TypeScript types to your project
- [ ] Implement API service class
- [ ] Create React hooks for data fetching
- [ ] Update existing components to use new API
- [ ] Test all endpoints in development
- [ ] Configure CORS properly
- [ ] Add error handling and loading states
- [ ] Deploy and verify in production

---

## Support

**API Documentation:** https://lunaxcode-fastapi.vercel.app/api/v1/docs

**Backend Repository:** lunaxcode-fastapi

For issues or questions, check the API health endpoint:
```bash
curl https://lunaxcode-fastapi.vercel.app/api/v1/health
```

---

**Happy coding! 🚀**

