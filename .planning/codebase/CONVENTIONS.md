# Coding Conventions

**Analysis Date:** 2026-04-09

## Naming Patterns

**Files:**
- Backend: Python snake_case for modules (`api.py`, `conftest.py`, `test_simple.py`)
- Frontend: TypeScript with PascalCase for components and camelCase for utility files
- Shared package: TypeScript with camelCase for utility functions and PascalCase for types/interfaces
- Test files: Suffix with `_test.py` (backend) or `.test.tsx` (frontend)

**Functions:**
- Backend: snake_case (`def health_check():`, `def prewarm_user_caches():`)
- Frontend: camelCase (`function handleSubmit()`, `const processData = () =>`)
- Async functions often prefixed with `handle` or named as verbs

**Variables:**
- Backend: snake_case (`instance_id`, `is_shutting_down`, `allowed_origins`)
- Frontend: camelCase (`isLoading`, `userData`, `apiResponse`)
- Constants: UPPERCASE_WITH_UNDERSCORES (`MAX_CONCURRENT_IPS`, `METRICS_LOG_INTERVAL_SECONDS`)

**Types/Interfaces:**
- Backend: CamelCase with descriptive names (`EnvMode`, `TestClient`, `UnifiedMessage`)
- Frontend TypeScript: PascalCase for interfaces (`interface UnifiedMessage`, `type AgentStatus`)
- Generic types use single letters (`T`, `K`, `V`) or descriptive names

## Code Style

**Formatting:**
- Backend: Ruff for linting (inferred from `.ruff_cache` directory)
- Frontend: Prettier with ESLint (`.prettierrc` and `eslint.config.mjs` present)
- Prettier settings: semi-colons, single quotes, trailing commas, 2-space tabs, 80 print width

**Linting:**
- Backend: Ruff (evidenced by `.ruff_cache` and pyproject.toml pytest configuration)
- Frontend: ESLint with Next.js plugin (`eslint.config.mjs` extends `next/core-web-vitals`, `next/typescript`)
- Key ESLint rules: 
  - `@typescript-eslint/no-unused-vars`: off
  - `@typescript-eslint/no-explicit-any`: off
  - `react-hooks/exhaustive-deps`: warn
  - `@next/next/no-img-element`: warn
  - `prefer-const`: warn

## Import Organization

**Backend (Python):**
1. Standard library imports (dotenv, fastapi, uuid, etc.)
2. Third-party imports (psycopg, redis, supabase, etc.)
3. Local application imports (core.services, api, etc.)
4. Relative imports within same module when needed

**Frontend (TypeScript):**
1. External libraries (@radix-ui, @tiptap, zod, etc.)
2. Internal workspace imports (@agentpress/shared, @usebasejump/shared)
3. Local component/utils imports (relative paths)
4. Type imports separated when beneficial

**Path Aliases:**
- Frontend: Uses `@/` alias for `src/` directory (Next.js convention)
- Shared package: Uses relative imports or workspace aliases (`@agentpress/shared`)

## Error Handling

**Patterns:**
- Backend: 
  - Try/except blocks with specific exception catching
  - HTTPException for API errors with appropriate status codes
  - Logging errors with structlog before raising exceptions
  - Custom exception classes in `core/billing/shared/exceptions.py`
  - Circuit breaker pattern wraps external service calls (mentioned in CLAUDE.md)
  
- Frontend:
  - Try/catch for async operations
  - Error boundaries for React components (inferred from usage patterns)
  - Toast notifications for user-facing errors (sonner library used)
  - Form validation with react-hook-form and zod/yup

## Logging

**Framework:** structlog (backend) and console (frontend)

**Patterns:**
- Backend:
  - Structured logging with `structlog.get_logger(__name__)`
  - Different log levels: debug, info, warning, error
  - Context variables binding for request tracking (`structlog.contextvars.bind_contextvars`)
  - Consistent format: `[Emoji] Message: {key}={value}` (e.g., `🚨 CRITICAL: Worker memory {mem_mb:.0f}MB`)
  - Request/response logging middleware captures method, path, status, timing
  
- Frontend:
  - Console.log for development debugging
  - Limited production logging (inferred from absence of extensive logging patterns)
  - Error reporting via posthog and sentry integrations

## Comments

**When to Comment:**
- Backend: Docstrings for all public functions and classes (PEP 257 style)
- Complex logic blocks with explanation of why (not what)
- Configuration sections and environment variable usage
- TODO/FIXME comments for technical debt tracking (present in codebase)

**JSDoc/TSDoc:**
- Frontend/TS: JSDoc comments for exported functions and complex types
- Examples: `/** @description Formats credit values */` in shared utils
- Component props documented with JSDoc

## Function Design

**Size:** 
- Functions should be small and focused (typically <50 lines)
- Longer functions broken into private helper functions
- Backend API endpoints follow pattern: validation → business logic → response

**Parameters:** 
- Backend: Explicit typing with Python 3.11+ type hints
- Common patterns: dependency injection for services (Depends in FastAPI)
- Pydantic models for request/validation bodies
- Frontend: Strict TypeScript typing for all parameters
- Callback functions properly typed (React event handlers)

**Return Values:** 
- Backend: Consistent JSON responses for API endpoints
- Pydantic models for response serialization
- Clear success/error indicators in return values
- Frontend: 
  - React components return JSX elements
  - Hooks return arrays or objects with clear semantics
  - Async functions return Promise<T> with proper error handling

## Module Design

**Exports:** 
- Backend: `__all__` lists when appropriate, explicit imports preferred
- Frontend: Named exports for utilities, default exports for components
- Barrel exports (`index.ts`) used in shared package for clean imports

**Barrel Files:** 
- Used extensively in shared package (`packages/shared/src/index.ts`)
- Frontend: Limited use, prefer explicit relative paths
- Backend: `__init__.py` files for package organization and selective exports

## Configuration

**Environment Variables:**
- Backend: Loaded via python-dotenv and pydantic BaseSettings (inferred from core.utils.config)
- Frontend: NEXT_PUBLIC_ prefix for client-side env vars
- Required variables documented in ENV_CONFIGURATION_REFERENCE.md

**Files:**
- Backend: Configuration in `core/utils/config.py` with EnvMode enum
- Separation of concerns: secrets in .env, non-secrets in code
- Feature flags for enabling/disabling functionality (ACTIVATE_MCPS_TRIG, etc.)
