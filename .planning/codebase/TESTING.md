# CarbonScopes Testing

> Mapped: 2026-04-18

## Backend Testing

### Framework & Tools
| Tool | Version | Purpose |
|------|---------|---------|
| pytest | 8.3.4 | Test runner |
| pytest-asyncio | 0.24.0 | Async test support |
| pytest-cov | 6.0.0 | Coverage reporting |
| pytest-mock | 3.14.0 | Mocking |
| pytest-xdist | 3.3.0 | Parallel test execution |
| pytest-timeout | 2.3.1 | Test timeout enforcement |
| pytest-randomly | 3.12.0 | Random test ordering |
| pytest-rerunfailures | 10.2.0 | Flaky test reruns |
| pytest-env | 1.1.5 | Environment variable management |

### Test Structure
```
backend/
├── tests/
│   ├── api/                 # API endpoint tests
│   ├── boq/                 # BOQ parsing tests
│   └── utils/               # Utility tests
├── lca/tests/
│   ├── test_deterministic.py     # Deterministic calculation tests
│   ├── test_carbon_calculator.py # Carbon calculator unit tests
│   └── test_brightway_setup.py   # Brightway2 setup validation
├── core/knowledge_graph/versioning/
│   └── test_versioning.py        # Knowledge graph versioning tests
└── core/utils/scripts/
    └── test_redis_connection.py  # Redis connectivity test
```

### Test Patterns
- **Pytest fixtures** for database, auth, and service mocking
- **Async test support** via `pytest-asyncio` (backend is async FastAPI)
- **Parallel execution** with `pytest-xdist` for speed
- **Random ordering** with `pytest-randomly` to catch order-dependent failures
- **Mock mode**: `CarbonCalculatorAgent` supports `mock_mode` for testing without Brightway2

### Running Backend Tests
```bash
cd backend
pytest                          # All tests
pytest -x                       # Stop on first failure
pytest --cov                    # With coverage
pytest -n auto                  # Parallel execution
```

## Frontend Testing

### Unit Tests
| Tool | Purpose |
|------|---------|
| Jest/Vitest | Unit test runner (via Next.js) |
| React Testing Library | Component testing |

### Unit Test Structure
```
apps/frontend/src/__tests__/
├── logger.test.ts               # Logger utility tests
├── error-handler.test.ts        # Error handler tests
├── sanitize.test.ts             # Input sanitization tests
├── api-db-errors.test.ts        # API/DB error handling tests
├── quality-tasks.test.ts        # Quality task tests
├── timeouts.test.ts             # Timeout handling tests
└── compatibility/
    ├── api-routes.test.ts       # API route compatibility
    └── api-contract.test.ts     # API contract tests
```

### E2E Tests (Playwright)
| Tool | Version | Purpose |
|------|---------|---------|
| Playwright | latest | Browser E2E testing |
| Chromium | — | Test browser |

### E2E Test Structure
```
apps/frontend/e2e/
├── infrastructure.spec.ts       # Infrastructure/health checks
├── console-error-monitor.spec.ts # Console error detection
├── chat-debug.spec.ts           # Chat debugging
├── chat-with-auth.spec.ts       # Authenticated chat
├── chat-simple.spec.ts          # Basic chat functionality
├── chat-test.spec.ts            # Chat feature tests
├── chat-full-test.spec.ts       # Comprehensive chat tests
├── chat-carbon-report.spec.ts   # Carbon report generation
├── projects.spec.ts             # Project management
├── dashboard.spec.ts            # Dashboard functionality
├── compatibility.spec.ts        # Browser compatibility
└── infrastructure/
    ├── async_expect.ts          # Async test utilities
    ├── auth.fixture.ts          # Auth test fixtures
    └── page.helpers.ts          # Page object helpers
```

### E2E Configuration
- **Config**: `apps/frontend/playwright.config.ts`
- **Base URL**: `http://localhost:3001` (default)
- **Parallel**: Enabled (`fullyParallel: true`)
- **Retries**: 1 on CI, 0 locally
- **Reporter**: List + HTML (`e2e-report/`)
- **Screenshots**: On failure only
- **Traces**: On first retry
- **Dev server**: Can auto-start or use existing (`reuseExistingServer: true`)

### Running Frontend Tests
```bash
cd apps/frontend
pnpm test                       # Unit tests
pnpm test:e2e                   # E2E tests (Playwright)
pnpm test:prod-readiness        # Production readiness E2E
bash fast-check.sh              # Quick test script
```

## Coverage & Quality

### Observations
- **Backend coverage**: LCA module has dedicated tests; other modules may have limited coverage
- **Frontend coverage**: Unit tests focus on utilities; E2E tests cover critical user flows (chat, carbon report, dashboard)
- **No CI test gate**: CI workflow (`.github/workflows/cloudflare.yml`) only builds and deploys — no test step visible
- **Compatibility tests**: API contract tests ensure frontend-backend compatibility

### Test Data
- **TGO materials**: JSON files for material loading tests
- **Brightway2**: Local LCA database for deterministic carbon calculation tests
- **Mock mode**: Agent tests can run without external dependencies
