# Development Authentication Bypass

## Overview

The backend provides a development authentication bypass mode for local testing and E2E tests. This allows you to bypass the full Supabase authentication flow (magic links, email delivery) and use a fixed test user.

**⚠️ SECURITY WARNING**: This bypass is ONLY for local development. Never enable this in production!

## Configuration

Add these environment variables to your `.env` file:

```env
DEV_AUTH_BYPASS=true
DEV_TEST_USER_ID=00000000-0000-0000-0000-000000000001
DEV_TEST_EMAIL=test@dev.local
```

## Test User Credentials

- **User ID**: `00000000-0000-0000-0000-000000000001`
- **Email**: `test@dev.local`

## Usage Methods

The bypass supports two authentication methods:

### Method 1: Using x-dev-test-user Header

Send the special header `x-dev-test-user: true` with any request:

```bash
curl -X GET http://localhost:8000/api/protected-endpoint \
  -H "x-dev-test-user: true"
```

### Method 2: Using Bearer Token with Test Email

Send a Bearer token with format `dev:test@dev.local`:

```bash
curl -X GET http://localhost:8000/api/protected-endpoint \
  -H "Authorization: Bearer dev:test@dev.local"
```

## Testing Examples

### Test Health Check with Auth Bypass
```bash
curl -X GET http://localhost:8000/health \
  -H "x-dev-test-user: true" \
  -v
```

### Test Protected Endpoint
```bash
# Using header method
curl -X GET http://localhost:8000/api/v1/threads \
  -H "x-dev-test-user: true" \
  -H "Content-Type: application/json"

# Using Bearer token method
curl -X GET http://localhost:8000/api/v1/threads \
  -H "Authorization: Bearer dev:test@dev.local" \
  -H "Content-Type: application/json"
```

### Test with Python Requests
```python
import requests

# Method 1: Header
response = requests.get(
    "http://localhost:8000/api/v1/threads",
    headers={"x-dev-test-user": "true"}
)

# Method 2: Bearer token
response = requests.get(
    "http://localhost:8000/api/v1/threads",
    headers={"Authorization": "Bearer dev:test@dev.local"}
)
```

### Test with JavaScript/Playwright
```javascript
// Method 1: Header
await page.setExtraHTTPHeaders({
  'x-dev-test-user': 'true'
});

// Method 2: Bearer token
await page.setExtraHTTPHeaders({
  'Authorization': 'Bearer dev:test@dev.local'
});
```

## How It Works

When `DEV_AUTH_BYPASS=true` is set, the `verify_and_get_user_id_from_jwt()` function in `core/utils/auth_utils.py`:

1. Checks for the `x-dev-test-user: true` header
2. OR checks for Bearer token starting with `dev:` containing the test email
3. Returns the configured `DEV_TEST_USER_ID` immediately
4. Bypasses all JWT verification and Supabase checks
5. Logs a warning message with 🚨 emoji for visibility

## Security Notes

- **Never commit**: Ensure `.env` is in `.gitignore`
- **Local only**: Only use this in local development environments
- **Visible warnings**: All bypass authentications log prominent warnings
- **Production check**: Deployment pipelines should never set `DEV_AUTH_BYPASS=true`

## Disabling the Bypass

To disable the bypass and use real authentication:

```env
# Comment out or remove
# DEV_AUTH_BYPASS=true

# Or explicitly set to false
DEV_AUTH_BYPASS=false
```

## Troubleshooting

### Bypass not working
1. Check `.env` file has `DEV_AUTH_BYPASS=true`
2. Restart the backend server to reload environment variables
3. Check logs for "🚨 DEV_AUTH_BYPASS" messages
4. Verify you're sending one of the two supported authentication methods

### Getting 401 Unauthorized
1. Ensure you're using the correct header or Bearer token format
2. Check that the backend server is running
3. Verify `.env` is loaded (check server startup logs)

### Need to test real authentication
1. Set `DEV_AUTH_BYPASS=false` or remove the variable
2. Restart the backend server
3. Use real Supabase JWT tokens

## Related Files

- **Auth implementation**: `suna-init/backend/core/utils/auth_utils.py` (lines 399-424)
- **Environment config**: `suna-init/backend/.env`
- **Config loader**: `suna-init/backend/core/utils/config.py`
