# Rate Limiting Implementation Documentation

## Overview

Rate limiting has been implemented on authentication and sensitive endpoints to prevent brute force attacks and API abuse. The implementation uses **slowapi** (FastAPI wrapper for flask-limiter) with Redis backend for distributed rate limiting.

## Implementation Status

✅ **COMPLETED** - All requirements met

### Components Implemented

1. **Rate Limiting Library**: slowapi v0.1.9 (already in pyproject.toml)
2. **Middleware**: `core/middleware/rate_limit.py`
3. **Protected Endpoints**:
   - `/auth/send-otp` - 5 requests per 15 minutes per IP ✅
   - `/api/api-keys` - 5 requests per 15 minutes per IP ✅
4. **Error Handling**: Returns HTTP 429 with Retry-After header ✅
5. **IP-based Limiting**: Uses X-Forwarded-For header when behind proxy ✅

## Architecture

### Storage Backend

The rate limiter uses Redis for distributed rate limiting across multiple instances:

```python
# From core/middleware/rate_limit.py
REDIS_URL = os.getenv("UPSTASH_REDIS_REST_URL") or os.getenv("REDIS_URL")

def get_storage_uri() -> str:
    if REDIS_URL:
        return REDIS_URL  # Redis for production
    else:
        return "memory://"  # In-memory for development
```

### Rate Limit Configuration

Rate limits are configurable via environment variables:

```bash
# .env
AUTH_RATE_LIMIT=5/15minutes       # Auth endpoints (default)
API_KEY_RATE_LIMIT=5/15minutes    # API key management (default)
DEFAULT_RATE_LIMIT=100/minute     # Other endpoints (default)
```

### Client Identification

The limiter identifies clients by IP address, supporting proxy headers:

```python
def get_client_identifier(request: Request) -> str:
    # Check X-Forwarded-For header (behind load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    # Fallback to direct remote address
    return get_remote_address(request)
```

## Protected Endpoints

### 1. `/auth/send-otp` (POST)

**Purpose**: Send OTP verification email for magic link authentication

**Rate Limit**: 5 requests per 15 minutes per IP

**Implementation**:
```python
# auth/api.py
@router.post("/send-otp", response_model=SendOtpResponse)
@limiter.limit(AUTH_RATE_LIMIT)
async def send_otp_email(http_request: Request, request: SendOtpRequest):
    ...
```

**Test**:
```bash
./test_auth_rate_limit.sh
```

### 2. `/api/api-keys` (POST)

**Purpose**: Create new API key for authenticated user

**Rate Limit**: 5 requests per 15 minutes per IP

**Implementation**:
```python
# core/services/api_keys_api.py
@router.post("/api-keys", response_model=APIKeyCreateResponse)
@limiter.limit(API_KEY_RATE_LIMIT)
async def create_api_key(
    http_request: Request,
    request: APIKeyCreateRequest,
    ...
):
    ...
```

**Test**:
```bash
export TEST_JWT_TOKEN='your-jwt-token'
./test_api_keys_rate_limit.sh
```

## Error Response Format

When rate limit is exceeded, the API returns:

**HTTP Status**: 429 Too Many Requests

**Headers**:
- `Retry-After`: Seconds until rate limit resets (e.g., "900" for 15 minutes)
- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Timestamp when limit resets

**Body**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": "15 minutes"
}
```

**Example**:
```bash
curl -X POST http://localhost:3000/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# After 5 requests:
# HTTP/1.1 429 Too Many Requests
# Retry-After: 900
# {
#   "error": "rate_limit_exceeded",
#   "message": "Too many requests. Please try again later.",
#   "retry_after": "15 minutes"
# }
```

## FastAPI Integration

The rate limiter is integrated into the main FastAPI application:

```python
# api.py
from core.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter  # Register limiter

# Add exception handler for 429 responses
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
```

## Testing

### Manual Testing

**Test Script 1**: `/auth/send-otp` endpoint
```bash
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init/backend
./test_auth_rate_limit.sh
```

Expected output:
- Requests 1-5: 200 OK or 404 (user not found)
- Request 6: 429 Too Many Requests with Retry-After header

**Test Script 2**: `/api/api-keys` endpoint
```bash
export TEST_JWT_TOKEN='your-valid-jwt'
./test_api_keys_rate_limit.sh
```

Expected output:
- Requests 1-5: 200 OK (API key created)
- Request 6: 429 Too Many Requests with Retry-After header

### Automated Testing

Create a pytest test:

```python
# tests/test_rate_limiting.py
import pytest
from fastapi.testclient import TestClient

def test_auth_rate_limit(client: TestClient):
    """Test that /auth/send-otp enforces rate limiting"""
    endpoint = "/auth/send-otp"
    payload = {"email": "test@example.com"}
    
    # First 5 requests should succeed or fail normally (not rate limited)
    for i in range(5):
        response = client.post(endpoint, json=payload)
        assert response.status_code != 429
    
    # 6th request should be rate limited
    response = client.post(endpoint, json=payload)
    assert response.status_code == 429
    assert "retry_after" in response.json()
    assert "Retry-After" in response.headers
```

## Configuration Options

### Environment Variables

```bash
# Required for distributed rate limiting
UPSTASH_REDIS_REST_URL=redis://...
# or
REDIS_URL=redis://...

# Optional: Override default rate limits
AUTH_RATE_LIMIT=5/15minutes
API_KEY_RATE_LIMIT=5/15minutes
DEFAULT_RATE_LIMIT=100/minute
```

### Rate Limit Format

Slowapi supports various time windows:

```python
"5/15minutes"   # 5 requests per 15 minutes
"10/hour"       # 10 requests per hour
"100/day"       # 100 requests per day
"1/second"      # 1 request per second
```

### Strategy Options

Currently using **fixed-window** strategy:

```python
# core/middleware/rate_limit.py
limiter = Limiter(
    key_func=get_client_identifier,
    storage_uri=get_storage_uri(),
    strategy="fixed-window",  # Simple, performant
    headers_enabled=True,
)
```

Alternative: **moving-window** for more accurate limiting (higher Redis load)

## Security Considerations

### IP Spoofing Protection

When behind a proxy/load balancer:
- Uses first IP in X-Forwarded-For chain (original client)
- Configure load balancer to sanitize X-Forwarded-For header
- In production, validate proxy headers are from trusted sources

### Distributed Deployments

- **With Redis**: Rate limits shared across all instances ✅
- **Without Redis**: Each instance has independent limits ⚠️
  - Not recommended for production
  - Set REDIS_URL or UPSTASH_REDIS_REST_URL

### Bypass Mechanisms

For legitimate high-volume users:
- Use API key authentication (separate rate limit tier)
- Implement user-based rate limiting (not just IP)
- Create exemption list for trusted IPs/users

## Monitoring

### Logs

Rate limit exceeded events are logged:

```python
logger.warning(
    f"Rate limit exceeded for {client_ip} on {request.url.path}"
)
```

### Metrics

Monitor these metrics:
- 429 response rate per endpoint
- Rate limit hit rate per IP
- Average retry-after time
- Redis connection health

### Redis Keys

Rate limit data is stored in Redis with keys:
```
slowapi:<strategy>:<endpoint>:<ip_address>
```

Example:
```
slowapi:fixed-window:/auth/send-otp:192.168.1.100
```

## Troubleshooting

### Rate limit not working

1. **Check Redis connection**:
   ```bash
   echo $UPSTASH_REDIS_REST_URL
   # Should be set in production
   ```

2. **Verify limiter is registered**:
   ```python
   # api.py should have:
   app.state.limiter = limiter
   ```

3. **Check endpoint decorator**:
   ```python
   @limiter.limit(AUTH_RATE_LIMIT)  # Must be present
   async def endpoint(...):
   ```

### 429 errors in development

- Rate limits apply in all environments
- Wait 15 minutes for limit reset
- Or restart server (in-memory storage clears)
- Or flush Redis: `redis-cli FLUSHDB`

### Production deployment

1. Ensure Redis is configured:
   ```bash
   export UPSTASH_REDIS_REST_URL='your-redis-url'
   ```

2. Test distributed limiting:
   - Deploy multiple instances
   - Send 5 requests across instances
   - 6th request should be rate limited regardless of instance

## Future Enhancements

### User-based Rate Limiting

Instead of IP-only, limit by user ID:

```python
def get_user_identifier(request: Request) -> str:
    # Try to get user ID from auth
    user_id = getattr(request.state, 'user_id', None)
    if user_id:
        return f"user:{user_id}"
    
    # Fallback to IP
    return get_client_identifier(request)
```

### Tiered Rate Limits

Different limits for different subscription tiers:

```python
# Free tier: 5/15minutes
# Pro tier: 20/15minutes
# Enterprise: 100/15minutes

async def get_user_tier_limit(request: Request) -> str:
    user = getattr(request.state, 'user', None)
    if user:
        tier = await get_user_subscription_tier(user['id'])
        return TIER_LIMITS.get(tier, AUTH_RATE_LIMIT)
    return AUTH_RATE_LIMIT
```

### Dynamic Rate Limits

Adjust limits based on system load:

```python
async def get_dynamic_limit(request: Request) -> str:
    system_load = await get_system_load()
    if system_load > 0.8:
        return "2/15minutes"  # Stricter during high load
    return AUTH_RATE_LIMIT
```

## References

- **slowapi Documentation**: https://github.com/laurentS/slowapi
- **Flask-Limiter**: https://flask-limiter.readthedocs.io/
- **Rate Limiting Best Practices**: https://blog.logrocket.com/rate-limiting-node-js/
- **Redis Rate Limiting**: https://redis.io/docs/manual/patterns/rate-limiter/

## Related Files

- `core/middleware/rate_limit.py` - Main middleware implementation
- `auth/api.py` - Auth endpoint with rate limiting
- `core/services/api_keys_api.py` - API keys endpoint with rate limiting
- `api.py` - FastAPI app integration
- `test_auth_rate_limit.sh` - Auth endpoint test script
- `test_api_keys_rate_limit.sh` - API keys endpoint test script

## Changelog

- **2026-04-01**: Initial implementation with slowapi
  - Added rate limiting middleware
  - Protected /auth/send-otp endpoint (5/15min)
  - Protected /api/api-keys endpoint (5/15min)
  - Implemented 429 error handling with Retry-After header
  - Created test scripts for manual verification
