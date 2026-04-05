"""
Centralized timeout configuration for backend
All values in seconds unless otherwise specified

Guidelines for adjusting values:
- NETWORK: Short delays for API calls and retries (0.1-2s)
- BACKGROUND: Medium intervals for background tasks and health checks (5-60s)
- POLLING: Regular intervals for status checks and cleanup (30-60s)
- TESTING: Short delays for test scenarios (0.1-1s)

Environment Variables:
- API_TIMEOUT: Override default API timeout
- RETRY_DELAY: Override default retry delay
- CLEANUP_INTERVAL: Override default cleanup interval
"""

import os

# ===== Network & API =====
# Default timeout for API requests (can be overridden per request)
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

# Base delay between retry attempts
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "2"))

# Delay for exponential backoff retries (base multiplier)
EXPONENTIAL_BACKOFF_BASE = 2

# Maximum retry delay (cap for exponential backoff)
MAX_RETRY_DELAY = 60

# Small delay between API calls to avoid rate limits
API_RATE_LIMIT_DELAY = 0.2

# ===== Background Tasks =====
# Interval for running background task checks
BACKGROUND_TASK_INTERVAL = 5

# Interval for background task retry checks
BACKGROUND_TASK_RETRY_INTERVAL = 10

# Interval for health check tasks
HEALTH_CHECK_INTERVAL = 60

# Interval for maintenance countdown checks
MAINTENANCE_CHECK_INTERVAL = int(os.getenv("MAINTENANCE_CHECK_INTERVAL", "60"))

# ===== Polling & Status Checks =====
# Interval for checking sandbox pool status
POOL_CHECK_INTERVAL = 5

# Interval for cleanup operations
CLEANUP_INTERVAL = int(os.getenv("CLEANUP_INTERVAL", "60"))

# Interval for keepalive pings
KEEPALIVE_INTERVAL = 30

# Interval for worker metrics collection
METRICS_COLLECTION_INTERVAL = 60

# Poll interval for file operations
FILE_POLL_INTERVAL = 0.1

# Poll interval for Apify actor runs
APIFY_POLL_INTERVAL = 5

# Poll interval for voice generation status
VOICE_GENERATION_POLL_INTERVAL = 1

# Poll interval for credits balance checks
CREDITS_POLL_INTERVAL = 1  # milliseconds in code, convert as needed

# Poll interval for Reality Defender checks
REALITY_DEFENDER_POLL_INTERVAL = 2

# ===== Execution & Processing =====
# Interval for checking executor stop signals
STOP_CHECK_INTERVAL = 0.1

# Delay before executor shutdown
EXECUTOR_SHUTDOWN_DELAY = 5.0

# Delay for flushing stateless pipeline data
FLUSH_INTERVAL = 1

# Interval for heartbeat updates in ownership tracking
HEARTBEAT_INTERVAL = 10

# Interval for recovery sweep operations
RECOVERY_SWEEP_INTERVAL = 30

# Initial delay before starting analytics worker
ANALYTICS_INITIAL_DELAY = 60

# Interval for processing analytics
ANALYTICS_PROCESSING_INTERVAL = 300  # 5 minutes

# ===== Rate Limiting =====
# Maximum wait time for rate limiter (per iteration)
RATE_LIMITER_MAX_WAIT = 1.0

# Check interval for rate limiter
RATE_LIMITER_CHECK_INTERVAL = 0.1

# Rate limit window duration (15 minutes)
RATE_LIMIT_WINDOW = 900

# ===== Distributed Lock =====
# Delay between lock acquisition attempts
LOCK_ACQUISITION_DELAY = 0.5

# Delay after lock acquisition failure
LOCK_FAILURE_DELAY = 1.0

# Wait time for other process when lock is held
LOCK_WAIT_FOR_OTHER_PROCESS = 3.0

# ===== Database Operations =====
# Delay between database retry attempts
DB_RETRY_DELAY = 1.0

# Delay for database connection retries
DB_CONNECTION_RETRY_DELAY = 0.5

# Short delay for ensuring deletion is processed
DB_DELETION_DELAY = 0.1

# ===== External Services =====
# Delay between voice generation starts
VOICE_GENERATION_START_DELAY = 1.0

# Delay for voice generation processing
VOICE_GENERATION_PROCESS_DELAY = 0.3

# Delay for web search retries
WEB_SEARCH_RETRY_DELAY = 2

# Delay for paper search rate limiting
PAPER_SEARCH_RATE_LIMIT_DELAY = 1.0

# Delay for TGO API calls
TGO_API_DELAY = 2

# Delay for TGO retry attempts
TGO_RETRY_DELAY = 1

# Delay for HTML to PDF conversion retries
PDF_CONVERSION_RETRY_DELAY = 2.0

# ===== Testing & Development =====
# Delay for stress test operations
STRESS_TEST_DELAY = 0.5

# Delay for mock LLM responses
MOCK_LLM_DELAY = 0.1

# Delay for analytics admin operations
ANALYTICS_ADMIN_DELAY = 1.0

# ===== Subscription & Billing =====
# Delay for subscription scheduling operations
SUBSCRIPTION_SCHEDULING_DELAY = 1.0

# Delay for subscription upgrade operations
SUBSCRIPTION_UPGRADE_DELAY = 1.0

# Delay for account state updates
ACCOUNT_STATE_UPDATE_DELAY = 1.0

# ===== Sandbox Operations =====
# Initial delay before starting pool background tasks
POOL_BACKGROUND_INITIAL_DELAY = 5

# Interval for cleanup background tasks
POOL_CLEANUP_INTERVAL = 60

# Interval for keepalive background tasks
POOL_KEEPALIVE_INTERVAL = 30

# Delay for sandbox resolver operations
SANDBOX_RESOLVER_DELAY = 2

# Delay for sandbox container startup
SANDBOX_CONTAINER_STARTUP_DELAY = 1

# Batch delay for pool operations
POOL_BATCH_DELAY = 0.1

# ===== Redis Operations =====
# Delay for Redis connection retries
REDIS_CONNECTION_RETRY_DELAY = 0.5

# Delay for Redis operation retries
REDIS_OPERATION_RETRY_DELAY = 0.1

# ===== Knowledge Base =====
# Delay for knowledge base retry attempts
KB_RETRY_DELAY = 1.0

# Delay for knowledge base operations
KB_OPERATION_DELAY = 0.3

# ===== Shell Operations =====
# Delay for shell command output reading
SHELL_OUTPUT_READ_DELAY = 0.1

# ===== File Operations =====
# Small delay for file operation retries
FILE_OPERATION_RETRY_DELAY = 0.5

# ===== Browser Tool =====
# Base delay for browser tool retries
BROWSER_TOOL_RETRY_BASE_DELAY = 1.0

# Retry delays for browser tool (exponential backoff)
BROWSER_TOOL_RETRY_DELAYS = [1, 2, 4]

# ===== Version Service =====
# Delay for version service retries
VERSION_SERVICE_RETRY_DELAY = 0.1


def get_exponential_backoff_delay(attempt: int, base_delay: float = RETRY_DELAY) -> float:
    """
    Calculate exponential backoff delay for retry attempts

    Args:
        attempt: The retry attempt number (0-indexed)
        base_delay: Base delay in seconds

    Returns:
        Calculated delay in seconds, capped at MAX_RETRY_DELAY
    """
    delay = base_delay * (EXPONENTIAL_BACKOFF_BASE ** attempt)
    return min(delay, MAX_RETRY_DELAY)


def get_timeout_with_multiplier(base_timeout: float, multiplier: float = 1.0) -> float:
    """
    Get timeout value with optional multiplier

    Args:
        base_timeout: Base timeout value in seconds
        multiplier: Multiplier for the timeout

    Returns:
        Timeout value in seconds
    """
    return base_timeout * multiplier
