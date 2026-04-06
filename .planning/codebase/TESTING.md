# Testing Patterns

**Analysis Date:** 2026-04-06

## Test Framework

**Frontend Runner:**
- **Framework**: Bun Test for unit tests (based on `bun:test` imports)
- **E2E Framework**: Playwright v1.59.1 (`@playwright/test`)
- **Config**: `apps/frontend/playwright.config.ts`

**Backend Runner:**
- **Framework**: pytest v8.3.4
- **Config**: `backend/pytest.ini`

**Run Commands:**
```bash
# Frontend unit tests
cd apps/frontend && bun test

# Frontend E2E tests
cd apps/frontend && pnpm playwright test

# Backend tests
cd backend && pytest                    # All tests
cd backend && pytest --verbose          # Verbose output
cd backend && pytest --cov=core         # With coverage
cd backend && pytest -ra                # Show all test outcomes
```

## Test File Organization

**Frontend Location:**
- **Unit tests**: `apps/frontend/src/__tests__/**/*.test.ts`
- **E2E tests**: `apps/frontend/e2e/**/*.spec.ts`

**Frontend Naming:**
- Unit tests: `*.test.ts` - `logger.test.ts`, `sanitize.test.ts`, `quality-tasks.test.ts`
- E2E tests: `*.spec.ts` - `compatibility.spec.ts`

**Backend Location:**
- **All tests**: `backend/tests/`
- **Structure**:
  ```
  backend/tests/
  ├── agents/          # Agent framework tests
  ├── api/             # API endpoint tests
  ├── boq/             # BOQ parser tests
  ├── core/            # Core functionality tests
  ├── e2e/             # End-to-end tests
  ├── integration/     # Integration tests
  ├── lca/             # LCA calculator tests
  ├── reports/         # Report generation tests
  └── utils/           # Utility tests
  ```

**Backend Naming:**
- Pattern: `test_*.py` - `test_base_agent.py`, `test_carbon_pipeline.py`, `test_validators.py`

## Test Structure

**Frontend Unit Test Suite:**
```typescript
import { describe, test, expect, beforeEach, afterEach, mock } from 'bun:test';

describe('logger', () => {
  const originalEnv = process.env.NODE_ENV;

  beforeEach(() => {
    // Setup before each test
  });

  afterEach(() => {
    // Cleanup after each test
    process.env.NODE_ENV = originalEnv;
  });

  test('logger.error always emits in production', () => {
    // Test implementation
    expect(errorCalls).toHaveLength(1);
  });
});
```

**Frontend E2E Test Suite:**
```typescript
import { test, expect } from '@playwright/test';

const FRONTEND = process.env.BASE_URL ?? 'http://localhost:3002';
const NAV_OPTS = { timeout: 40_000, waitUntil: 'domcontentloaded' as const };

test.describe('Backend reachable from E2E context', () => {
  test('backend health endpoint responds', async ({ request }) => {
    const res = await request.get(`${BACKEND}/v1/health`);
    expect(res.status()).toBeGreaterThan(0);
  });
});

test.describe('Public pages — no backend crash', () => {
  const pages = ['/', '/auth', '/pricing'];
  
  for (const path of pages) {
    test(`${path} loads without error`, async ({ page }) => {
      const res = await page.goto(`${FRONTEND}${path}`, NAV_OPTS);
      expect(res?.status()).toBeLessThan(500);
    });
  }
});
```

**Backend Test Suite:**
```python
import pytest
from core.agents.base import Agent, AgentRegistry
from core.agents.state import AgentState

class MockAgent(Agent):
    """Mock agent for testing."""
    
    def __init__(self, name: str, capabilities: set[str], should_fail: bool = False):
        super().__init__(name, capabilities)
        self.should_fail = should_fail
        self.execute_called = False
    
    async def execute(self, state: AgentState) -> dict[str, any]:
        """Mock execution."""
        self.execute_called = True
        if self.should_fail:
            raise ValueError("Mock agent failure")
        return {"result": "success"}

@pytest.fixture
def mock_state():
    """Fixture providing a mock AgentState."""
    return {
        "user_query": "Test query",
        "current_agent": "test_agent",
    }

@pytest.mark.asyncio
async def test_agent_initialization():
    """Test agent initialization with name and capabilities."""
    agent = MockAgent("test_agent", {"test:capability", "test:another"})
    
    assert agent.name == "test_agent"
    assert agent.capabilities == {"test:capability", "test:another"}
```

**Patterns:**
- **Descriptive test names**: Use clear, action-based names
- **AAA pattern**: Arrange, Act, Assert (implicit in test structure)
- **Fixtures**: Setup shared test data and mocks
- **Async tests**: Use `@pytest.mark.asyncio` for async functions

## Mocking

**Frontend Mocking:**
- **Bun Test mocking**:
  ```typescript
  import { mock } from 'bun:test';
  console.log = (...args: unknown[]) => { logCalls.push(args); };
  ```
- **Module mocking**: Dynamic imports for fresh modules
  ```typescript
  const mod = await import('../lib/logger');
  expect(typeof mod.logger.log).toBe('function');
  ```

**Backend Mocking:**
- **Framework**: `unittest.mock` with `Mock`, `MagicMock`, `patch`
- **Global mocks**: `backend/conftest.py` provides session-wide mocks
  ```python
  @pytest.fixture(scope="session", autouse=True)
  def mock_external_services(request):
      with patch("boq.cache.get_redis_client") as mock_redis, \
           patch("core.services.supabase.DBConnection") as mock_db:
          yield {"redis": mock_redis_client, "db": mock_db_instance}
  ```

**What to Mock:**
- External service connections (Redis, Supabase, GraphDB)
- LLM API calls (OpenAI, Anthropic)
- File system operations
- Network requests
- Time-dependent operations

**What NOT to Mock:**
- Pure functions and utility logic
- Data transformations
- Validation logic
- Business rules

## Fixtures and Factories

**Backend Test Data:**
- **Pytest fixtures** in `conftest.py`:
  ```python
  @pytest.fixture
  def mock_config():
      """Provide a mocked configuration object for tests."""
      config_mock = Mock()
      config_mock.ENV_MODE = EnvMode.LOCAL
      config_mock.TESTING = True
      return config_mock

  @pytest.fixture
  def mock_graphdb_client():
      """Mock GraphDB client for knowledge graph tests."""
      mock_client = MagicMock()
      mock_client.query.return_value = []
      mock_client.is_connected.return_value = True
      return mock_client
  ```

**Frontend Test Data:**
- **Inline test data**: Direct object creation in tests
- **Mock API responses**: Captured via request interception in Playwright

**Location:**
- **Backend**: `backend/conftest.py` (root), `backend/tests/*/conftest.py` (module-specific)
- **Frontend**: Inline in test files

## Coverage

**Backend Requirements:**
- **Tool**: pytest-cov v6.0.0
- **Target**: Not enforced (commented in pytest.ini)
- **Configuration** (commented in `backend/pytest.ini`):
  ```ini
  # --cov=core
  # --cov=agents
  # --cov=api
  # --cov-report=html
  # --cov-report=term-missing
  ```

**Frontend Coverage:**
- **Tool**: Not configured
- **E2E Coverage**: Critical user paths (auth, dashboard, public pages)

**View Coverage:**
```bash
# Backend
cd backend && pytest --cov=core --cov=agents --cov-report=html
# Open htmlcov/index.html in browser

# Backend terminal view
cd backend && pytest --cov=core --cov-report=term-missing
```

## Test Types

**Unit Tests:**
- **Scope**: Individual functions, classes, utilities
- **Location**: `apps/frontend/src/__tests__/`, `backend/tests/`
- **Markers**: `@pytest.mark.unit` (Python)
- **Dependencies**: Mocked
- **Speed**: Fast (<100ms per test)
- **Examples**:
  - `apps/frontend/src/__tests__/logger.test.ts` - Logger utility
  - `backend/tests/agents/test_base_agent.py` - Agent base class

**Integration Tests:**
- **Scope**: Multiple components working together
- **Location**: `backend/tests/integration/`, `backend/tests/api/`
- **Markers**: `@pytest.mark.integration`
- **Dependencies**: Real or test instances (TestClient for APIs)
- **Speed**: Medium (100ms-1s per test)
- **Examples**:
  - `backend/tests/integration/test_boq_api.py` - BOQ API integration
  - `backend/tests/api/test_agents.py` - Agent API endpoints

**E2E Tests:**
- **Scope**: Complete user workflows through browser
- **Location**: `apps/frontend/e2e/`, `backend/tests/e2e/`
- **Dependencies**: Full system (browser + backend + database)
- **Speed**: Slow (5-60s per test)
- **Examples**:
  - `apps/frontend/e2e/compatibility.spec.ts` - Frontend-backend integration
  - `backend/tests/e2e/test_full_flow.py` - Complete agent workflow

**Performance Tests:**
- **Location**: `backend/core/knowledge_graph/*_performance_tests.py`
- **Purpose**: Benchmark critical operations
- **Markers**: `@pytest.mark.slow`

## Common Patterns

**Async Testing (Backend):**
```python
@pytest.mark.asyncio
async def test_execute_with_metrics_success(mock_state):
    """Test execute_with_metrics() wrapper for successful execution."""
    agent = MockAgent("test_agent", {"test:capability"})
    
    result = await agent.execute_with_metrics(mock_state)
    
    assert result["status"] == "success"
    assert "duration_ms" in result
```

**Error Testing (Backend):**
```python
@pytest.mark.asyncio
async def test_agent_abstract_class():
    """Test that Agent is abstract and requires execute() implementation."""
    with pytest.raises(TypeError):
        # Cannot instantiate abstract class
        Agent("test", {"test:capability"})
```

**Frontend Async Testing:**
```typescript
test('logger module exports expected methods', async () => {
  const mod = await import('../lib/logger');
  expect(typeof mod.logger.log).toBe('function');
  expect(typeof mod.logger.error).toBe('function');
});
```

**Playwright Page Testing:**
```typescript
test('renders sign-in form', async ({ page }) => {
  await page.goto(`${FRONTEND}/auth`, NAV_OPTS);
  const emailInput = page.locator('input[type="email"], input[name="email"]');
  await expect(emailInput.first()).toBeVisible({ timeout: 8000 });
});
```

**Request Interception (E2E):**
```typescript
test('frontend makes API calls to backend', async ({ page }) => {
  const apiCalls: string[] = [];
  const backendHost = new URL(BACKEND).host;
  
  page.on('request', req => {
    const url = req.url();
    if (url.includes(backendHost)) {
      apiCalls.push(url);
    }
  });
  
  await page.goto(`${FRONTEND}/dashboard`);
  expect(apiCalls.length).toBeGreaterThan(0);
});
```

## Test Markers and Configuration

**Backend Markers** (defined in `backend/pytest.ini`):
- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may use databases, services)
- `@pytest.mark.slow` - Slow tests (may take >1s)
- `@pytest.mark.requires_graphdb` - Tests requiring GraphDB connection
- `@pytest.mark.requires_redis` - Tests requiring Redis connection
- `@pytest.mark.requires_db` - Tests requiring PostgreSQL connection
- `@pytest.mark.requires_api_keys` - Tests requiring external API keys

**Pytest Configuration:**
```ini
[pytest]
# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Test paths
testpaths = tests

# Output options
addopts =
    --verbose
    --strict-markers
    --disable-warnings
    -ra
    --tb=short

# Asyncio configuration
asyncio_mode = auto

# Environment variables for testing
env =
    ENV_MODE=test
    TESTING=true
```

**Playwright Configuration:**
```typescript
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list'], ['html', { open: 'never', outputFolder: 'e2e-report' }]],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3001',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  webServer: {
    command: 'pnpm dev --port 3002',
    url: 'http://localhost:3001',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
```

## Test Environment Setup

**Backend Test Environment:**
- **Python**: 3.11+ (3.12 recommended)
- **pytest plugins**: asyncio, cov, env, mock, xdist, timeout, randomly, rerunfailures
- **Environment variables**: Set via `conftest.py`
  ```python
  os.environ["ENV_MODE"] = "test"
  os.environ["TESTING"] = "true"
  os.environ["SUPABASE_URL"] = "http://localhost:54321"
  ```

**Frontend Test Environment:**
- **Runtime**: Bun for unit tests, Node.js for Playwright
- **Playwright**: Browsers auto-installed via `pnpm playwright install`
- **Environment variables**: `BASE_URL`, `BACKEND_URL`

## Test Coverage Gaps

**Untested Areas:**
- **Frontend**: Limited unit test coverage (only logger, sanitize, quality-tasks visible)
- **Backend**: Coverage reporting disabled in pytest.ini (needs enablement)
- **Integration**: Some modules have integration tests, others rely on E2E only
- **Risk**: UI components lack unit/integration tests, heavy reliance on E2E

**Testing Priority:**
- **High**: API endpoints, agent execution, data parsers
- **Medium**: UI components (currently E2E only), utilities
- **Low**: Configuration, static content

---

*Testing analysis: 2026-04-06*
