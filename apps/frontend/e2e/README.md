# CarbonScope Frontend E2E Test Infrastructure

Playwright-based end-to-end tests for the CarbonScope Next.js frontend.

---

## Quick Start

```typescript
// Import from the auth fixture instead of @playwright/test
import { test, expect } from './infrastructure/auth.fixture';
import { PageHelpers } from './infrastructure/page.helpers';
import { AsyncExpect } from './infrastructure/async_expect';

test('dashboard shows project list', async ({ authenticatedPage }) => {
  const helpers = new PageHelpers(authenticatedPage);

  // Given
  await helpers.navigateToDashboard();

  // When
  await helpers.waitForPageLoad();

  // Then
  const count = await helpers.getProjectCount();
  expect(count).toBeGreaterThanOrEqual(0);
});
```

---

## Running Tests

```bash
cd apps/frontend

# Run all E2E tests
pnpm exec playwright test

# Run only infrastructure verification
pnpm exec playwright test e2e/infrastructure.spec.ts

# Run against a specific URL
BASE_URL=http://staging.example.com pnpm exec playwright test

# Show report
pnpm exec playwright show-report e2e-report
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `BASE_URL` | Frontend base URL | `http://localhost:3001` |
| `BACKEND_URL` | Backend base URL | `http://localhost:8000` |
| `TEST_USER_EMAIL` | Login email | `e2e-test@carbonscopes.dev` |
| `TEST_USER_PASSWORD` | Login password | `test_password_e2e_12345` |

---

## Infrastructure Components

### `auth.fixture.ts`

Provides a pre-authenticated `Page` via `authenticatedPage` fixture.
Sessions are cached in `e2e/.auth/user.json` and reused across tests.

```typescript
import { test, expect } from './infrastructure/auth.fixture';

test('needs auth', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
  // Already logged in
});
```

### `PageHelpers`

Domain page interactions:

```typescript
const helpers = new PageHelpers(page);
await helpers.navigateToDashboard();
await helpers.navigateToProjects();
await helpers.sendChatMessage("Calculate carbon for 100kg steel");
await helpers.waitForPageLoad();
const greeting = helpers.getGreeting();
```

### `AsyncExpect`

Wait utilities for async UI states:

```typescript
// Wait for a condition
await AsyncExpect.waitUntil(
  () => page.locator('[data-status="complete"]').isVisible(),
  'status to reach complete',
  { timeout: 30_000 },
);

// Wait for element count
await AsyncExpect.waitForCount(
  page.locator('[data-testid="project-card"]'),
  3,
  '3 project cards to appear',
);

// Assert something never happens
await AsyncExpect.assertNeverTrue(
  () => page.locator('[data-testid="error"]').isVisible(),
  'error banner should never appear',
  { duration: 5_000 },
);
```

---

## Directory Structure

```
apps/frontend/e2e/
├── infrastructure/
│   ├── auth.fixture.ts      # Playwright auth fixture (authenticated page)
│   ├── page.helpers.ts      # Domain page interaction helpers
│   └── async_expect.ts      # Custom wait/assertion utilities
├── infrastructure.spec.ts   # Scaffold verification tests (run first)
├── dashboard.spec.ts        # Dashboard feature tests
├── projects.spec.ts         # Projects feature tests
├── .auth/                   # Cached auth state (git-ignored)
└── README.md                # This file
```

---

## Best Practices

1. **Use `authenticatedPage` for tests that require login.**
2. **Add `data-testid` attributes** to components for stable selectors.
3. **Prefer `AsyncExpect.waitUntil()` over `page.waitForTimeout()`.**
4. **Use `PageHelpers`** for repeated interactions to keep tests DRY.
5. **Capture screenshots on failure** — Playwright does this automatically with `screenshot: 'only-on-failure'`.

---

## Extension Guide

### Adding PageHelpers methods

```typescript
// In page.helpers.ts:
async clickUploadBoQ(): Promise<void> {
  await this.page
    .locator('button', { hasText: /upload|import/i })
    .first()
    .click();
}
```

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| All tests skip with "redirected to auth" | No auth state | Set `TEST_USER_EMAIL` / `TEST_USER_PASSWORD` and run `playwright test --headed` |
| `Timeout 40000ms exceeded` | Frontend not running | Run `pnpm dev` first |
| Auth state expired | Old `e2e/.auth/user.json` | Delete the file and re-run |
| Flaky selectors | Using text-based selectors | Add `data-testid` attrs to components |
