# CarbonScopes - Product Requirements Document

## Product Overview
CarbonScopes is a comprehensive carbon accounting platform for tracking, analyzing, and managing carbon footprints for businesses and individuals.

## Key Features

### Backend API (FastAPI on port 5002)
1. **Health Check** - GET /healthz and /v1/health return server status
2. **Authentication** - OTP-based magic link authentication, Google OAuth
3. **CSRF Protection** - Double-submit cookie pattern with GET /v1/csrf-token endpoint
4. **Rate Limiting** - slowapi-based rate limiting on auth, API key, and webhook endpoints
5. **API Key Management** - Create, list, and revoke API keys
6. **Carbon Data Management** - CRUD operations for carbon footprint data
7. **Google Integration** - Google Slides and Google Docs API integration
8. **Account Setup** - Anonymous account initialization and setup flows
9. **Webhook Support** - Webhook endpoints for external integrations

### Frontend (Next.js on port 3001)
1. **Dashboard** - Real-time carbon tracking dashboard with data visualization
2. **Authentication** - Login/logout with magic link OTP flow
3. **Carbon Tracking** - Input and track carbon emissions data
4. **User Management** - User profile and settings screens
5. **Data Visualization** - Charts and graphs for carbon data analysis

## User Stories
- As a business user, I want to track my organization's carbon footprint
- As a user, I want to authenticate via magic link email
- As a user, I want to generate API keys for programmatic access
- As a user, I want to view carbon data in visual dashboards
- As an admin, I want rate limiting to protect against abuse
- As a user, I want CSRF protection on state-changing operations

## Technical Stack
- Backend: Python/FastAPI with slowapi rate limiting and CSRF middleware
- Frontend: Next.js 15 with React
- Auth: Supabase (OTP, Google OAuth)
- Database: PostgreSQL via Supabase