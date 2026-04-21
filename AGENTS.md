# CarbonScopes Project Documentation

This document provides an overview of the CarbonScopes project structure and key information for contributors.

## Repository Overview

This repository contains the CarbonScopes project, which is a comprehensive carbon accounting platform for tracking, analyzing, and managing carbon footprints for businesses and individuals.

## Key Components

### Backend API
- Built with Python/FastAPI
- REST API endpoints for carbon data management
- Authentication and user management systems
- Database schemas and relationships

### Frontend Application
- Next.js application for the user interface
- Real-time carbon tracking dashboard
- Data visualization components
- User management screens

### Infrastructure
- Docker configurations for deployment
- Environment configurations
- Database schemas and migrations

## Security Architecture

### Rate Limiting (SEC-04 / Task #114)
- **Middleware**: `core/middleware/rate_limit.py` (slowapi with Redis/in-memory backend)
- **Configuration**: `AUTH_RATE_LIMIT="5/15minutes"`, `API_KEY_RATE_LIMIT="5/15minutes"`, `DEFAULT_RATE_LIMIT="100/minute"`
- **Protected endpoints**: OTP send/verify, Google OAuth auth-url/callback, account setup/initialize-anonymous, API key creation, webhooks
- **Auth API**: `backend/auth/api.py` — OTP endpoints for expired magic links
- **Important**: slowapi requires `Request` as first parameter on decorated endpoints

### CSRF Protection (SEC-05 / Task #111)
- **Middleware**: `core/middleware/csrf.py` (double-submit cookie pattern)
- **Cookie**: `csrf_token`, **Header**: `X-CSRF-Token`
- **Token endpoint**: `GET /v1/csrf-token`
- **Exemptions**: Bearer token auth, API key auth (`X-API-Key`), webhook paths, safe methods (GET/HEAD/OPTIONS/TRACE), health checks
- **Configuration**: `CSRF_ENABLED` env var (default: true), `CSRF_COOKIE_SECURE` (default: true)

## Key File Locations

- **Main API**: `backend/api.py` — FastAPI app, all routers, middleware registration
- **Auth module**: `backend/auth/api.py` — OTP endpoints
- **Core auth**: `backend/core/auth/auth.py` — JWT validation, RBAC
- **Rate limiting**: `backend/core/middleware/rate_limit.py`
- **CSRF**: `backend/core/middleware/csrf.py`
- **Google OAuth**: `backend/core/google/google_slides_api.py`, `google_docs_api.py`
- **Account setup**: `backend/core/setup/api.py`
- **API keys**: `backend/core/services/api_keys_api.py`
- **Email service**: `backend/core/services/email.py` (Mailtrap integration)
- **Config**: `backend/core/utils/config.py`

## Testing

- **Test directory**: `backend/tests/`
- **Auth tests**: `test_auth_edge_cases.py`
- **Security tests**: `test_security_middleware.py` (37 tests for rate limiting + CSRF)
- **Carbon pipeline**: `test_carbon_pipeline.py`
- **Note**: Some tests require Supabase config (set env vars or they skip)
- **Dependencies**: `pip install pytest pytest-asyncio slowapi starlette fastapi redis`