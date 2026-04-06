/**
 * Safe PostHog wrapper that prevents errors when the API key is not configured.
 * Use this instead of importing posthog-js directly.
 */

import posthogJs from 'posthog-js';

const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY;
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://eu.i.posthog.com';

// Track if PostHog has been initialized
let isInitialized = false;

/**
 * Initialize PostHog if the API key is configured.
 * Safe to call multiple times - will only initialize once.
 */
export function initPostHog() {
  if (typeof window === 'undefined') return;
  if (isInitialized) return;
  if (!POSTHOG_KEY) return;

  try {
    posthogJs.init(POSTHOG_KEY, {
      api_host: POSTHOG_HOST,
      capture_pageview: false, // We handle this manually
      capture_pageleave: true,
      persistence: 'localStorage',
    });
    isInitialized = true;
  } catch (error) {
    console.warn('[PostHog] Failed to initialize:', error);
  }
}

/**
 * Check if PostHog is available and initialized.
 */
export function isPostHogAvailable(): boolean {
  return isInitialized && !!POSTHOG_KEY;
}

/**
 * Safe PostHog capture - only captures if PostHog is initialized.
 */
export function capture(event: string, properties?: Record<string, unknown>) {
  if (!isPostHogAvailable()) return;
  try {
    posthogJs.capture(event, properties);
  } catch (error) {
    // Silently fail - analytics should not break the app
  }
}

/**
 * Safe PostHog identify - only identifies if PostHog is initialized.
 */
export function identify(userId: string, properties?: Record<string, unknown>) {
  if (!isPostHogAvailable()) return;
  try {
    posthogJs.identify(userId, properties);
  } catch (error) {
    // Silently fail
  }
}

/**
 * Safe PostHog reset - only resets if PostHog is initialized.
 */
export function reset() {
  if (!isPostHogAvailable()) return;
  try {
    posthogJs.reset();
  } catch (error) {
    // Silently fail
  }
}

/**
 * Export the raw posthog instance for advanced usage.
 * Use with caution - prefer the safe wrapper functions above.
 */
export const posthog = posthogJs;
