/**
 * Application-wide timeout and delay constants.
 * Use these instead of hardcoded millisecond values.
 */

// UI interaction delays
export const DEBOUNCE_FAST_MS = 100;
export const DEBOUNCE_DEFAULT_MS = 300;
export const DEBOUNCE_SLOW_MS = 500;

// Animation / transition durations
export const ANIMATION_SHORT_MS = 200;
export const ANIMATION_DEFAULT_MS = 300;
export const TOAST_DURATION_MS = 2000;
export const TOOLTIP_DELAY_MS = 500;

// Network / API timeouts
export const API_TIMEOUT_MS = 30_000;
export const STREAM_TIMEOUT_MS = 300_000; // 5 minutes
export const UPLOAD_TIMEOUT_MS = 120_000; // 2 minutes
export const HEALTH_CHECK_INTERVAL_MS = 30_000;

// Polling intervals
export const AGENT_STATUS_POLL_MS = 1_000;
export const THREAD_REFRESH_POLL_MS = 2_000;
export const SUBSCRIPTION_POLL_MS = 5_000;

// Auto-save
export const AUTO_SAVE_DELAY_MS = 2_000;

// Retry
export const RETRY_DELAY_BASE_MS = 1_000;
export const MAX_RETRY_ATTEMPTS = 3;
