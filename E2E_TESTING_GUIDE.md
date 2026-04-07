# CarbonScope E2E Testing Guide

This guide explains how to run and maintain end-to-end tests for CarbonScope applications to ensure no console errors occur in production.

## Overview

CarbonScope uses Playwright for end-to-end testing with enhanced console error monitoring to catch JavaScript errors before they reach production.

## Test Structure

- **Frontend E2E Tests**: Located in `apps/frontend/e2e/`
- **Backend E2E Tests**: Located in `backend/tests/e2e/`
- **Enhanced Console Monitoring**: Custom test that captures and reports console errors

## Running Tests

### Frontend E2E Tests

```bash
# Install dependencies (if needed)
cd apps/frontend
npm install

# Run all E2E tests
npx playwright test

# Run specific test file
npx playwright test e2e/console-error-monitor.spec.ts

# Run tests in headed mode (useful for debugging)
npx playwright test e2e/console-error-monitor.spec.ts --headed

# Generate HTML report
npx playwright test --reporter=html
npx playwright show-report
```

### Backend E2E Tests

```bash
cd backend
# Run E2E tests
pytest tests/e2e/ -v
```

## Enhanced Console Error Monitoring

The `console-error-monitor.spec.ts` test includes:

1. Automatic console error capture during test execution
2. Error detection and reporting
3. Warning filtering (ignores development noise)
4. Per-test console error verification
5. Cross-route navigation testing

Key features:
- Captures `console.error` messages and fails test if any are detected
- Filters out common development warnings
- Tests critical user journeys (homepage, auth, pricing, about, support, legal)
- Tests navigation between pages
- Tests responsive views (mobile, tablet, desktop)

## Critical User Journeys Tested

1. Homepage load and interaction
2. Authentication page load
3. Pricing page load
4. About page load
5. Support page load
6. Legal page load
7. Navigation between pages
8. Responsive design verification

## Best Practices

1. **Always run E2E tests before deploying to production**
2. **Check console error output in test results**
3. **Fix any console errors immediately** - they indicate potential production issues
4. **Keep tests updated** when adding new features or pages
5. **Use headed mode** (`--headed`) for debugging visual issues
6. **Review HTML reports** for detailed test execution information

## Troubleshooting

### Common Issues

1. **"Cannot find module '@playwright/test'"**
   - Ensure Playwright is installed: `npm install @playwright/test`
   - May need to run from the frontend directory

2. **Tests timing out**
   - Increase timeout in test configuration if needed
   - Check if development server is running

3. **False positive console errors**
   - Review the warning filtering logic in `console-error-monitor.spec.ts`
   - Adjust filters as needed for your specific case

## Maintenance

### Adding New Tests

1. Create new test files in `apps/frontend/e2e/` with `.spec.ts` extension
2. Follow the pattern in `console-error-monitor.spec.ts` for console error monitoring
3. Add tests for new critical user journeys
4. Update documentation as needed

### Updating Test Infrastructure

1. Playwright configuration is in `apps/frontend/playwright.config.ts`
2. Base URLs are controlled by environment variables:
   - `BASE_URL` for frontend (default: http://localhost:3002)
   - `BACKEND_URL` for backend API (default: http://localhost:8000/v1)

## Contact

For questions about E2E testing, refer to:
- Playwright documentation: https://playwright.dev/
- Internal CarbonScope testing guidelines
- Team lead or QA engineer

Last updated: April 2026