/**
 * Centralized timeout configuration for frontend
 * All values in milliseconds unless otherwise specified
 *
 * Guidelines for adjusting values:
 * - UI_FEEDBACK: Short delays for visual feedback and animations (300-500ms)
 * - USER_INTERACTION: Medium delays for user actions and redirects (1-2s)
 * - POLLING: Regular intervals for status checks and updates (5-30s)
 * - LONG_RUNNING: Extended operations like animations and celebrations (3-5s)
 */

export const TIMEOUTS = {
  // ===== UI Feedback & Animations =====
  /** Delay before showing mobile app banner */
  MOBILE_BANNER_SHOW: 500,

  /** Delay before hiding mobile app banner after close */
  MOBILE_BANNER_HIDE: 300,

  /** Duration for showing toast notifications and messages */
  TOAST_DURATION: 3000,

  /** Debounce delay for loading indicators */
  LOADING_DEBOUNCE: 500,

  /** Focus delay for search inputs and modals */
  FOCUS_DELAY: 50,

  /** Delay for step transitions in multi-step processes */
  STEP_TRANSITION: 500,

  /** Duration for celebration animations (upgrade, success states) */
  CELEBRATION_DURATION: 4000,

  /** Delay for triggering autoplay in carousels */
  AUTOPLAY_DELAY: 2000,

  /** Interval for typing animation effects */
  TYPING_INTERVAL: 100,

  /** Duration for example showcase slide transitions */
  SLIDE_TRANSITION: 3000,

  // ===== Auth & Navigation =====
  /** Interval for checking GitHub OAuth popup status */
  GITHUB_POPUP_CHECK: 1000,

  /** Delay before redirecting after authentication */
  AUTH_REDIRECT_DELAY: 2000,

  /** Delay before closing dialogs after successful operation */
  DIALOG_AUTO_CLOSE: 2000,

  /** Interval for checking popup window status during OAuth */
  POPUP_STATUS_CHECK: 500,

  // ===== Polling & Background Tasks =====
  /** Interval for checking maintenance countdown status */
  MAINTENANCE_CHECK: 30000, // 30 seconds

  /** Debounce delay for search input */
  SEARCH_DEBOUNCE: 300,

  /** Interval for OTP resend countdown timer */
  OTP_COUNTDOWN_INTERVAL: 1000,

  /** Interval for checkout status polling */
  CHECKOUT_POLL_INTERVAL: 1000,

  /** Timeout for checkout completion (5 minutes) */
  CHECKOUT_TIMEOUT: 300000,

  /** Interval for route change tracking */
  ROUTE_CHANGE_DELAY: 2000,

  // ===== State Management =====
  /** Delay for triggering state updates in React components */
  STATE_UPDATE_DELAY: 0,

  /** Delay for triggering schedule changes */
  SCHEDULE_UPDATE_DELAY: 0,
} as const;

/**
 * Backend-specific timeouts that may affect frontend behavior
 * These are reference values - actual values are set in backend config
 */
export const BACKEND_REFERENCE = {
  /** Expected API response timeout (30s) */
  API_TIMEOUT: 30000,

  /** Expected retry delay for failed requests (2s) */
  RETRY_DELAY: 2000,
} as const;

/**
 * Type-safe timeout keys
 */
export type TimeoutKey = keyof typeof TIMEOUTS;

/**
 * Helper function to get timeout value with optional multiplier
 * @param key - The timeout key from TIMEOUTS
 * @param multiplier - Optional multiplier for the timeout value
 * @returns Timeout value in milliseconds
 */
export function getTimeout(key: TimeoutKey, multiplier: number = 1): number {
  return TIMEOUTS[key] * multiplier;
}
