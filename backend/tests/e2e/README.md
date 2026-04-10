# CarbonScope Backend E2E Test Infrastructure

End-to-end tests validate complete API journeys — from authentication through
carbon calculations and agent runs — against a running backend instance.

---

## Quick Start

```python
from tests.e2e.infrastructure import E2EFixture, ScenarioBuilder, AsyncAssert

@pytest.mark.e2e
class TestCarbonWorkflow(E2EFixture):
    async def test_calculate_carbon_for_project(self):
        # Given: a project with a material
        state = await (
            ScenarioBuilder(self.client)
            .with_project("Office Tower")
            .with_material("Concrete C30", quantity=250.0, unit="m3")
            .build()
        )
        project_id = state["project"]["id"]
        self.track_resource("project", project_id)

        # When: we run a carbon calculation
        result = await self.api.calculate_carbon("Concrete C30/37", 250.0, "m3")

        # Then: result contains carbon factors
        assert "co2e" in result or "total_carbon" in result
```

---

## Running Tests

```bash
# Run all E2E tests
cd backend
uv run pytest tests/e2e/ -v -m e2e

# Run only infrastructure verification
uv run pytest tests/e2e/test_infrastructure.py -v

# Run with a specific backend URL
TEST_API_URL=http://staging.example.com/v1 uv run pytest tests/e2e/ -m e2e
```

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_API_URL` | Backend base URL | `http://localhost:8000/v1` |
| `SUPABASE_URL` | Supabase project URL | — |
| `SUPABASE_SERVICE_ROLE_KEY` | Admin key for test user creation | — |
| `SUPABASE_JWT_SECRET` | For minting test JWTs | — |
| `TEST_REQUEST_TIMEOUT` | HTTP timeout in seconds | `30.0` |

---

## Infrastructure Components

### `E2EFixture` (base class)

Inherit from `E2EFixture` to get:
- `self.client` — authenticated `httpx.AsyncClient`
- `self.api` — `CarbonScopeAPIClient` domain helpers
- `self.user_info` — test user dict (`user_id`, `email`)
- `self.track_resource(type, id)` — register for auto-cleanup
- `setup()` / `teardown()` — override hooks

### `ScenarioBuilder`

Fluent API for setting up test state:

```python
state = await (
    ScenarioBuilder(self.client)
    .with_project("My Project")
    .with_material("Steel", 100.0, "kg")
    .with_boq_from_file("backend/tests/sample_data/sample_boq.csv")
    .with_carbon_assessment("Concrete C30", 250.0, "m3")
    .build()
)
```

### `CarbonScopeAPIClient` (`self.api`)

Domain-specific API methods:

```python
health = await self.api.get_health()
project = await self.api.create_project("My Project")
projects = await self.api.list_projects()
result = await self.api.calculate_carbon("Concrete C30", 100.0, "m3")
events = await self.api.stream_agent_run(run_id, max_events=10)
```

### `AsyncAssert`

Wait-for-condition utilities:

```python
# Wait for a condition
await AsyncAssert.wait_until(
    lambda: check_status() == "complete",
    "status to reach complete",
    timeout=60.0,
)

# Wait for a specific value
await AsyncAssert.wait_for_value(
    lambda: get_count(),
    expected=5,
    description="thread count",
)

# Assert something never happens
await AsyncAssert.assert_never_true(
    lambda: error_count > 0,
    "errors should never appear",
    duration=5.0,
)
```

---

## Directory Structure

```
backend/tests/e2e/
├── infrastructure/
│   ├── __init__.py          # Public API
│   ├── e2e_fixture.py       # Base test class (auth, cleanup)
│   ├── scenario_builder.py  # Fluent state builder
│   ├── api_client.py        # Domain API helpers
│   └── async_assert.py      # Wait/assertion utilities
├── test_infrastructure.py   # Scaffold verification tests (run first)
├── test_full_flow.py        # Original monolithic E2E test
├── conftest.py             # Session-scoped fixtures
├── config.py               # E2ETestConfig dataclass
└── README.md               # This file
```

---

## Best Practices

1. **Wait for conditions, not time.** Use `AsyncAssert.wait_until()` instead of `asyncio.sleep()`.
2. **One journey per test class.** Keep tests focused on a single user flow.
3. **Track resources.** Call `self.track_resource()` for everything created, or use `ScenarioBuilder` (which tracks automatically in future versions).
4. **Use descriptive assertions.** `CarbonScopeAPIClient.assert_status()` includes context in failure messages.
5. **Skip billing tests in CI.** Use `@pytest.mark.billing` and `self.api.skip_if_billing_error()`.

---

## Extension Guide

### Adding ScenarioBuilder methods

```python
# In scenario_builder.py, add a new with_* method:
def with_lca_report(self, project_id: str) -> "ScenarioBuilder":
    async def _action() -> None:
        response = await self._client.post("/lca/reports", json={"project_id": project_id})
        self._state["lca_report"] = response.json()
    self._actions.append(_action)
    return self
```

### Adding API client helpers

```python
# In api_client.py, add a new method:
async def get_lca_report(self, report_id: str) -> Dict[str, Any]:
    response = await self._client.get(f"/lca/reports/{report_id}")
    self.assert_status(response, 200, f"get LCA report {report_id}")
    return response.json()
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `SUPABASE_JWT_SECRET not set` | Missing env var | Add to `backend/.env` |
| `HTTP 401` on all requests | JWT expired or wrong secret | Check `SUPABASE_JWT_SECRET` |
| `Connection refused` | Backend not running | Run `uv run uvicorn api:app --port 8000` |
| `HTTP 402` billing error | Test user has no credits | Use `skip_if_billing_error()` |
| Test leaks resources | Forgot `track_resource()` | Add tracking call after each creation |
