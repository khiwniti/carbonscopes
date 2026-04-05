# Backend Timeout Configuration

## Overview

All timeout values have been centralized in `core/config/timeouts.py` for better maintainability and environment-specific tuning.

## Configuration File

**Location**: `core/config/timeouts.py`

### Timeout Categories

#### 1. Network & API (seconds)
- `API_TIMEOUT`: 30s - Default timeout for API requests
- `RETRY_DELAY`: 2s - Base delay between retry attempts
- `EXPONENTIAL_BACKOFF_BASE`: 2 - Base multiplier for exponential backoff
- `MAX_RETRY_DELAY`: 60s - Maximum retry delay (cap for exponential backoff)
- `API_RATE_LIMIT_DELAY`: 0.2s - Small delay between API calls to avoid rate limits

#### 2. Background Tasks (seconds)
- `BACKGROUND_TASK_INTERVAL`: 5s - Interval for running background task checks
- `BACKGROUND_TASK_RETRY_INTERVAL`: 10s - Interval for background task retry checks
- `HEALTH_CHECK_INTERVAL`: 60s - Interval for health check tasks
- `MAINTENANCE_CHECK_INTERVAL`: 60s - Interval for maintenance countdown checks

#### 3. Polling & Status Checks (seconds)
- `POOL_CHECK_INTERVAL`: 5s - Interval for checking sandbox pool status
- `CLEANUP_INTERVAL`: 60s - Interval for cleanup operations
- `KEEPALIVE_INTERVAL`: 30s - Interval for keepalive pings
- `METRICS_COLLECTION_INTERVAL`: 60s - Interval for worker metrics collection
- `FILE_POLL_INTERVAL`: 0.1s - Poll interval for file operations
- `APIFY_POLL_INTERVAL`: 5s - Poll interval for Apify actor runs
- `VOICE_GENERATION_POLL_INTERVAL`: 1s - Poll interval for voice generation status
- `CREDITS_POLL_INTERVAL`: 1s - Poll interval for credits balance checks
- `REALITY_DEFENDER_POLL_INTERVAL`: 2s - Poll interval for Reality Defender checks

#### 4. Execution & Processing (seconds)
- `STOP_CHECK_INTERVAL`: 0.1s - Interval for checking executor stop signals
- `EXECUTOR_SHUTDOWN_DELAY`: 5.0s - Delay before executor shutdown
- `FLUSH_INTERVAL`: 1s - Delay for flushing stateless pipeline data
- `HEARTBEAT_INTERVAL`: 10s - Interval for heartbeat updates in ownership tracking
- `RECOVERY_SWEEP_INTERVAL`: 30s - Interval for recovery sweep operations
- `ANALYTICS_INITIAL_DELAY`: 60s - Initial delay before starting analytics worker
- `ANALYTICS_PROCESSING_INTERVAL`: 300s - Interval for processing analytics (5 minutes)

#### 5. Rate Limiting (seconds)
- `RATE_LIMITER_MAX_WAIT`: 1.0s - Maximum wait time for rate limiter (per iteration)
- `RATE_LIMITER_CHECK_INTERVAL`: 0.1s - Check interval for rate limiter
- `RATE_LIMIT_WINDOW`: 900s - Rate limit window duration (15 minutes)

#### 6. Database Operations (seconds)
- `DB_RETRY_DELAY`: 1.0s - Delay between database retry attempts
- `DB_CONNECTION_RETRY_DELAY`: 0.5s - Delay for database connection retries
- `DB_DELETION_DELAY`: 0.1s - Short delay for ensuring deletion is processed

#### 7. External Services (seconds)
- `VOICE_GENERATION_START_DELAY`: 1.0s - Delay between voice generation starts
- `VOICE_GENERATION_PROCESS_DELAY`: 0.3s - Delay for voice generation processing
- `WEB_SEARCH_RETRY_DELAY`: 2s - Delay for web search retries
- `PAPER_SEARCH_RATE_LIMIT_DELAY`: 1.0s - Delay for paper search rate limiting
- `TGO_API_DELAY`: 2s - Delay for TGO API calls
- `TGO_RETRY_DELAY`: 1s - Delay for TGO retry attempts
- `PDF_CONVERSION_RETRY_DELAY`: 2.0s - Delay for HTML to PDF conversion retries

#### 8. Testing & Development (seconds)
- `STRESS_TEST_DELAY`: 0.5s - Delay for stress test operations
- `MOCK_LLM_DELAY`: 0.1s - Delay for mock LLM responses
- `ANALYTICS_ADMIN_DELAY`: 1.0s - Delay for analytics admin operations

## Usage

### Importing

```python
from core.config import timeouts
```

### Basic Usage

```python
# Instead of:
await asyncio.sleep(2)

# Use:
await asyncio.sleep(timeouts.RETRY_DELAY)
```

### Exponential Backoff

```python
from core.config import timeouts

# Calculate exponential backoff delay
delay = timeouts.get_exponential_backoff_delay(attempt=2)  # Returns: 2 * (2 ** 2) = 8s
await asyncio.sleep(delay)
```

### With Multiplier

```python
from core.config import timeouts

# Get timeout with multiplier
extended_timeout = timeouts.get_timeout_with_multiplier(
    timeouts.API_TIMEOUT, 
    multiplier=2.0
)  # Returns: 60s
```

## Files Updated

### Updated Files (21 files)
1. `core/utils/distributed_lock.py` - Lock acquisition delays
2. `core/knowledge_graph/tgo_poc.py` - TGO API delays
3. `core/services/redis.py` - Redis connection retries
4. `core/services/voice_generation.py` - Voice generation delays
5. `core/agents/api.py` - API rate limiting
6. `core/sandbox/resolver.py` - Sandbox preview retry
7. `core/sandbox/pool_background.py` - Pool background tasks
8. `core/sandbox/sandbox.py` - Container startup delays
9. `core/tools/sb_kb_tool.py` - Knowledge base operations
10. `core/tools/sb_shell_tool.py` - Shell command delays
11. `core/tools/sb_files_tool.py` - File operation delays
12. `core/admin/analytics_admin_api.py` - Analytics delays
13. `core/admin/stress_test_admin_api.py` - Stress test delays
14. `core/utils/scripts/verify_subscription_sync.py` - Subscription sync delays
15. `core/agents/runner/executor.py` - Executor shutdown delays
16. `core/agents/pipeline/stateless/resilience/rate_limiter.py` - Rate limiter delays
17. `core/agents/pipeline/stateless/coordinator/background_tasks.py` - Coordinator background tasks
18. `core/agents/pipeline/stateless/coordinator/stateless.py` - Stateless coordinator delays
19. `core/billing/subscriptions/handlers/scheduling.py` - Subscription scheduling
20. `core/billing/subscriptions/services/subscription_upgrade_service.py` - Subscription upgrades
21. `core/billing/subscriptions/services/scheduling_service.py` - Scheduling service

### Total Replacements
- **Backend**: 33 timeout replacements across 21 files
- **Files with imports**: 21 files

## Environment Configuration

Many timeouts can be configured via environment variables:

```bash
# .env
API_TIMEOUT=30
RETRY_DELAY=2
CLEANUP_INTERVAL=60
MAINTENANCE_CHECK_INTERVAL=60
```

Update values in `core/config/timeouts.py` or use environment variables directly.

## Helper Functions

### get_exponential_backoff_delay(attempt, base_delay)

Calculates exponential backoff delay for retry attempts.

**Parameters**:
- `attempt` (int): The retry attempt number (0-indexed)
- `base_delay` (float): Base delay in seconds (default: `RETRY_DELAY`)

**Returns**: Calculated delay in seconds, capped at `MAX_RETRY_DELAY`

**Example**:
```python
from core.config import timeouts

for attempt in range(5):
    delay = timeouts.get_exponential_backoff_delay(attempt)
    print(f"Attempt {attempt}: wait {delay}s")
    await asyncio.sleep(delay)

# Output:
# Attempt 0: wait 2s
# Attempt 1: wait 4s
# Attempt 2: wait 8s
# Attempt 3: wait 16s
# Attempt 4: wait 32s
```

### get_timeout_with_multiplier(base_timeout, multiplier)

Gets timeout value with optional multiplier.

**Parameters**:
- `base_timeout` (float): Base timeout value in seconds
- `multiplier` (float): Multiplier for the timeout (default: 1.0)

**Returns**: Timeout value in seconds

**Example**:
```python
from core.config import timeouts

# Double the standard API timeout
extended = timeouts.get_timeout_with_multiplier(timeouts.API_TIMEOUT, 2.0)
await asyncio.wait_for(slow_operation(), timeout=extended)
```

## Testing

Timeout values are validated through:
- Unit tests for helper functions
- Integration tests for retry mechanisms
- System tests for background task intervals
- Load tests for rate limiting behavior

## Maintenance

### Adding New Timeouts

1. Add constant to `core/config/timeouts.py`:
```python
# New feature timeout
FEATURE_TIMEOUT = int(os.getenv("FEATURE_TIMEOUT", "10"))
```

2. Import and use in your module:
```python
from core.config import timeouts

await asyncio.sleep(timeouts.FEATURE_TIMEOUT)
```

3. Document in this file under appropriate category.

### Adjusting Values

Edit values in `core/config/timeouts.py`. Consider:
- **Network Latency**: Increase timeouts for slow networks
- **Resource Constraints**: Adjust intervals based on system load
- **User Experience**: Balance responsiveness with resource usage
- **External Services**: Account for third-party API rate limits

## Migration Notes

### Before (Hardcoded)
```python
await asyncio.sleep(2)
await asyncio.sleep(60)
time.sleep(1)
```

### After (Configured)
```python
from core.config import timeouts

await asyncio.sleep(timeouts.RETRY_DELAY)
await asyncio.sleep(timeouts.CLEANUP_INTERVAL)
time.sleep(timeouts.TGO_RETRY_DELAY)
```

## Benefits

1. **Centralized Management**: All timeouts in one place
2. **Semantic Naming**: Clear purpose for each timeout
3. **Environment-Configurable**: Override via environment variables
4. **Helper Functions**: Exponential backoff and multiplier support
5. **Type Safety**: Python type hints for all functions
6. **Documentation**: Comprehensive docstrings and comments
7. **Maintainability**: Easy to tune for different environments (dev, staging, production)
