# Rate Limiting Implementation

## Overview

Rate limiting has been implemented on authentication and sensitive endpoints to prevent brute force attacks and API abuse.

## Protected Endpoints

### 1. Authentication Endpoints
- **Endpoint**: `POST /v1/auth/send-otp`
- **Limit**: 5 requests per 15 minutes per IP address
- **Purpose**: Prevent brute force attacks on magic link/OTP generation

### 2. API Key Management
- **Endpoint**: `POST /v1/api-keys`
- **Limit**: 5 requests per 15 minutes per IP address
- **Purpose**: Prevent abuse of API key creation

## Configuration

Rate limits are configurable via environment variables:

```bash
# Auth endpoints (magic link, OAuth)
AUTH_RATE_LIMIT="5/15minutes"

# API key creation endpoint
API_KEY_RATE_LIMIT="5/15minutes"

# Default rate limit for other endpoints (if applied)
DEFAULT_RATE_LIMIT="100/minute"
```

### Rate Limit Format
The format is `{number}/{period}` where period can be:
- `second`, `seconds`
- `minute`, `minutes`
- `hour`, `hours`
- `day`, `days`

Examples:
- `10/minute` - 10 requests per minute
- `100/hour` - 100 requests per hour
- `5/15minutes` - 5 requests per 15 minutes

## Storage Backend

The rate limiter uses Redis for distributed rate limiting across multiple instances:

- **Production**: Uses Redis URL from `UPSTASH_REDIS_REST_URL` or `REDIS_URL` environment variable
- **Development**: Falls back to in-memory storage if Redis is not available

**Note**: In-memory storage is not suitable for multi-instance deployments as each instance maintains its own counters.

## Response Format

When rate limit is exceeded, the API returns:

**HTTP Status**: `429 Too Many Requests`

**Headers**:
- `Retry-After`: Time in seconds until the rate limit resets
- `X-RateLimit-Limit`: Maximum requests allowed in the time window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Unix timestamp when the rate limit resets

**Response Body**:
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": "15 minutes"
}
```

## Implementation Details

### Library
Uses [slowapi](https://github.com/laurentS/slowapi) - FastAPI rate limiting library based on Flask-Limiter.

### Strategy
Uses **fixed-window** strategy:
- Simple and efficient
- Counts requests in fixed time windows
- Alternative: "moving-window" for more accurate limiting (slightly more overhead)

### Client Identification
Clients are identified by IP address:
1. Checks `X-Forwarded-For` header (for requests behind load balancers/proxies)
2. Falls back to direct connection IP address

### Architecture

```
Request → FastAPI Middleware → slowapi Limiter → Redis/Memory Check
                                    ↓
                           Within Limit?
                           ↓           ↓
                         Yes          No
                          ↓           ↓
                    Process     Return 429
```

## Testing

### Manual Testing
Use the provided test script:

```bash
# Start the API server first
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/backend
python test_rate_limit.py
```

The test script will:
1. Send multiple requests to `/auth/send-otp`
2. Send multiple requests to `/api-keys`
3. Verify that rate limiting triggers after the configured limit
4. Check for proper 429 responses with retry-after information

### Manual curl Testing

#### Test /auth/send-otp endpoint:
```bash
# Send 6 requests quickly
for i in {1..6}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/v1/auth/send-otp \
    -H "Content-Type: application/json" \
    -d '{"email":"test@example.com"}' \
    -w "\nHTTP Status: %{http_code}\n\n"
  sleep 0.5
done
```

Expected: First 5 requests succeed or return 404/500 (email not found), 6th request returns 429.

#### Test /api-keys endpoint:
```bash
# Send 6 requests quickly
for i in {1..6}; do
  echo "Request $i:"
  curl -X POST http://localhost:8000/v1/api-keys \
    -H "Content-Type: application/json" \
    -d '{"title":"Test","description":"Test"}' \
    -w "\nHTTP Status: %{http_code}\n\n"
  sleep 0.5
done
```

Expected: First 5 requests return 401 (unauthorized), 6th request returns 429.

## Files Modified/Created

### Created:
- `core/middleware/__init__.py` - Middleware module initialization
- `core/middleware/rate_limit.py` - Rate limiting configuration and setup
- `test_rate_limit.py` - Testing script
- `RATE_LIMITING.md` - This documentation

### Modified:
- `pyproject.toml` - Added `slowapi>=0.1.9` dependency
- `api.py` - Integrated rate limiter with FastAPI app
- `auth/api.py` - Applied rate limiting to `/send-otp` endpoint
- `core/services/api_keys_api.py` - Applied rate limiting to `/api-keys` endpoint

## Security Considerations

### Current Implementation
✅ IP-based rate limiting prevents brute force attacks
✅ Configurable limits via environment variables
✅ Proper 429 responses with retry-after information
✅ Redis-backed for distributed deployments

### Future Enhancements
- **User-based rate limiting**: Track authenticated users separately from IP
- **Progressive delays**: Increase delays with repeated violations
- **Admin exemptions**: Whitelist certain IPs or users
- **Per-endpoint customization**: Different limits for different sensitivity levels
- **Rate limit analytics**: Track and alert on rate limit violations

## Monitoring

To monitor rate limiting effectiveness:

1. **Check logs** for "Rate limit exceeded" warnings
2. **Monitor 429 responses** in API metrics
3. **Track Redis memory usage** for rate limit storage
4. **Alert on unusual patterns** (e.g., many IPs hitting limits)

Example log entry:
```
WARNING: Rate limit exceeded for 192.168.1.100 on /v1/auth/send-otp
```

## Troubleshooting

### Rate limits not working
1. Check that Redis is properly configured
2. Verify environment variables are set correctly
3. Check that slowapi is installed: `pip list | grep slowapi`
4. Review logs for rate limiter initialization messages

### False positives (legitimate users blocked)
1. Review rate limit configuration - may be too restrictive
2. Check if proxy/load balancer is properly forwarding client IPs
3. Consider implementing user-based rate limiting for authenticated requests

### Redis connection issues
- Rate limiter will fall back to in-memory storage
- Check logs for "Rate limiter using in-memory storage" warning
- Verify REDIS_URL or UPSTASH_REDIS_REST_URL environment variables

## References

- [slowapi Documentation](https://github.com/laurentS/slowapi)
- [FastAPI Middleware](https://fastapi.tiangolo.com/tutorial/middleware/)
- [Redis Rate Limiting Patterns](https://redis.io/docs/manual/patterns/rate-limiting/)
