# Testing Patterns

**Analysis Date:** 2026-04-09

## Test Framework

**Runner:**
- Pytest 8.3.4 (backend) - Configured in pyproject.toml
- Playwright 1.59.1 (frontend) - From devDependencies in package.json
- Vitest/Jest not detected - Playwright is primary E2E framework

**Assertion Library:**
- Backend: Pytest built-in assertions (assert)
- Frontend: Playwright test assertions (expect)

**Run Commands:**
```bash
# Backend
uv run pytest                          # Run all tests
uv run pytest tests/path/to/test_file.py::test_name  # Run single test
uv run pytest -m unit                  # Run by marker (unit/integration/slow)
uv run pytest -m "not slow"            # Exclude slow tests
uv run pytest --cov=core               # Run with coverage

# Frontend
pnpm dev                               # Dev server (port 3000)
pnpm test                              # Not defined in package.json - Playwright used via scripts
npx playwright test                    # Run Playwright tests (inferred)
```

## Test File Organization

**Location:**
- Backend: Tests co-located with modules in `tests/` directory mirroring source structure
- Frontend: E2E tests in `e2e-testing/` directory (inferred from files like E2E_TESTING_GUIDE.md)
- Shared: Limited testing - primarily consumed by frontend/mobile apps

**Naming:**
- Backend: `test_*.py` or `*_test.py` (mixed convention observed)
- Frontend: `*.test.tsx` or `*.spec.tsx` (Playwright convention)
- E2E: Descriptive names like `test_full_flow.py`

**Structure:**
```
backend/
├── tests/
│   ├── api/                 # API endpoint tests
│   ├── agents/              # Agent-specific tests
│   ├── boq/                 # BOQ parsing tests
│   ├── core/                # Core functionality tests
│   ├── lca/                 # LCA engine tests
│   ├── reports/             # Report generation tests
│   ├── integration/         # Integration tests
│   └── e2e/                 # End-to-end tests
└── conftest.py              # Shared pytest fixtures

apps/frontend/
├── e2e-testing/             # Playwright test files
│   ├── tests/
│   │   ├── login.spec.ts
│   │   └── dashboard.spec.ts
│   ├── utils/
│   └── playwright.config.ts
```

## Test Structure

**Suite Organization:**
```typescript
// Backend example (tests/agents/test_supervisor.py)
import pytest
from unittest.mock import Mock, patch
from core.agents.supervisor import AgentSupervisor

class TestAgentSupervisor:
    def test_supervisor_initialization(self):
        """Test that supervisor initializes correctly"""
        supervisor = AgentSupervisor()
        assert supervisor is not None
        
    @patch('core.agents.supervisor.some_dependency')
    def test_process_request(self, mock_dep):
        """Test request processing with mocked dependency"""
        mock_dep.return_value = "test_result"
        supervisor = AgentSupervisor()
        result = supervisor.process_request("test input")
        assert result == "test_result"
```

**Patterns:**
- Setup: pytest fixtures for mocking external services (database, Redis, LLM)
- Teardown: Automatic via fixture scope or yield cleanup
- Assertion: Direct assertions for values, pytest.raises for exceptions
- Async tests: Marked with `@pytest.mark.asyncio` or using `pytest-asyncio` plugin

## Mocking

**Framework:** 
- Primary: `unittest.mock` (Mock, MagicMock, patch)
- Secondary: Custom mocks in conftest.py for complex services

**Patterns:**
```python
# Service mocking pattern from conftest.py
with patch("boq.cache.get_redis_client") as mock_redis, \
     patch("core.services.supabase.DBConnection") as mock_db, \
     patch("core.agentpress.thread_manager.ThreadManager") as mock_thread_mgr:

    # Configure Redis mock
    mock_redis_client = MagicMock()
    mock_redis.return_value = mock_redis_client

    # Configure Supabase mock
    mock_db_instance = MagicMock()
    mock_db.return_value = mock_db_instance

    # Configure ThreadManager mock
    mock_thread_mgr_instance = MagicMock()
    mock_thread_mgr.return_value = mock_thread_mgr_instance
```

**What to Mock:**
- External services: Supabase, Redis, LLM providers (OpenAI, Anthropic)
- External APIs: Stripe, RevenueCat, Google APIs
- Background tasks: Worker metrics, memory watchdog
- File system operations: When testing file processing

**What NOT to Mock:**
- Pure utility functions (test actual logic)
- Data transformation pipelines (test with real data)
- Authentication logic when testing auth flows
- Database models when testing ORM behavior (use real SQLite in tests)

## Fixtures and Factories

**Test Data:**
```python
# Example from tests/fixtures/boq/create_sample_boq.py
def create_sample_boq():
    """Create a sample BOQ for testing"""
    return {
        "project_name": "Test Project",
        "items": [
            {
                "description": "Concrete",
                "quantity": 10.5,
                "unit": "m³",
                "unit_price": 120.00
            }
        ]
    }
```

**Location:**
- Backend: `tests/fixtures/` directory for reusable test data generators
- Frontend: Test utilities in e2e-testing/utils/ for common operations
- Shared: Minimal test data - relies on consuming apps

## Coverage

**Requirements:** 
- No explicit coverage threshold enforced (pytest-cov used but no fail-under)
- Coverage reports generated via `pytest --cov=core --cov-report=html`

**View Coverage:**
```bash
uv run pytest --cov=core --cov-report=term-missing
uv run pytest --cov=core --cov-report=html  # generates htmlcov/index.html
```

## Test Types

**Unit Tests:**
- Location: `tests/` directory organized by module
- Scope: Individual functions, classes, small components
- Approach: Mock external dependencies, test business logic in isolation
- Markers: `@pytest.mark.unit` (inferred from pytest configuration)

**Integration Tests:**
- Location: `tests/integration/` directory
- Scope: Cross-component interactions, database-involved tests
- Approach: Use real test database (via fixtures), limited external mocking
- Markers: `@pytest.mark.requires_db`, `@pytest.mark.requires_redis`

**E2E Tests:**
- Location: `tests/e2e/` (backend) and `apps/frontend/e2e-testing/` (frontend)
- Scope: Full user workflows, API authentication to UI interactions
- Framework: Playwright for frontend, HTTP client tests for backend
- Example: `tests/e2e/test_full_flow.py` tests complete agent interaction
- Markers: `@pytest.mark.e2e`, `@pytest.mark.slow`

## Common Patterns

**Async Testing:**
```python
# Backend async test pattern
@pytest.mark.asyncio
async def test_async_endpoint(test_client):
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    
    # Or using TestClient with async context
    async with test_client as client:
        response = await client.get("/")
```

**Error Testing:**
```python
# Testing exception handling
def test_validation_error():
    with pytest.raises(ValueError, match="Invalid input"):
        process_invalid_data("bad input")
        
    # Testing HTTP exceptions
    def test_not_found_endpoint(test_client):
        response = test_client.get("/api/v1/nonexistent")
        assert response.status_code == 404
```

**Database Testing:**
```python
# Using test database fixtures
def test_model_creation(db_session):
    # db_session fixture provides transactional test DB
    model = MyModel(name="test")
    db_session.add(model)
    db_session.commit()
    assert model.id is not None
```

**Authentication Testing:**
```python
# Mocking auth dependencies
def test_protected_endpoint(test_client, mock_auth):
    with patch("core.utils.auth_utils.verify_jwt", return_value={"user_id": "123"}):
        response = test_client.get("/api/v1/protected")
        assert response.status_code == 200
```

## CI/CD Practices Related to Testing

**GitHub Actions (inferred):**
- Tests run on pull requests and pushes to main
- Backend: `uv run pytest` with coverage reporting
- Frontend: `npx playwright test` for E2E validation
- Cache: Dependency caching for faster test runs

**Environment:**
- Test environment variables set via conftest.py (ENV_MODE=test, TESTING=true)
- Services mocked to avoid external dependencies during CI
- Database: PostgreSQL test instance or SQLite in-memory
- Redis: Mocked or local test instance

**Artifacts:**
- Test reports: JUnit XML format for CI integration
- Coverage reports: HTML and text formats
- Playwright traces: For failed E2E test debugging
- Test videos: Optional recording of failing tests

## Documentation and Comment Practices

**Test Documentation:**
- Docstrings on test classes and methods explaining purpose
- Comments for complex test setup or non-obvious assertions
- Reference to issue numbers or requirements when applicable
- README files in test directories explaining test scope

**Example:**
```python
def test_agent_handoff_scenario():
    """
    Test agent handoff when specialist agent is needed.
    See: https://github.com/CarbonScope-ai/suna/issues/1234
    """
    # Setup: User asks for carbon calculation (needs specialist)
    # Execute: Send message through supervisor
    # Verify: Carbon calculator agent is invoked and responds
    pass
```