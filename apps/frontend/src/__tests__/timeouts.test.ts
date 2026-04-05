/**
 * Unit tests for timeouts constants (#121 — centralized timeouts)
 */
import { describe, test, expect } from 'bun:test';
import {
  DEBOUNCE_FAST_MS,
  DEBOUNCE_DEFAULT_MS,
  DEBOUNCE_SLOW_MS,
  ANIMATION_SHORT_MS,
  ANIMATION_DEFAULT_MS,
  TOAST_DURATION_MS,
  API_TIMEOUT_MS,
  STREAM_TIMEOUT_MS,
  UPLOAD_TIMEOUT_MS,
  HEALTH_CHECK_INTERVAL_MS,
  AGENT_STATUS_POLL_MS,
  THREAD_REFRESH_POLL_MS,
  AUTO_SAVE_DELAY_MS,
  RETRY_DELAY_BASE_MS,
  MAX_RETRY_ATTEMPTS,
} from '../lib/constants/timeouts';

describe('timeout constants', () => {
  test('all constants are positive numbers', () => {
    const constants = [
      DEBOUNCE_FAST_MS, DEBOUNCE_DEFAULT_MS, DEBOUNCE_SLOW_MS,
      ANIMATION_SHORT_MS, ANIMATION_DEFAULT_MS, TOAST_DURATION_MS,
      API_TIMEOUT_MS, STREAM_TIMEOUT_MS, UPLOAD_TIMEOUT_MS,
      HEALTH_CHECK_INTERVAL_MS, AGENT_STATUS_POLL_MS, THREAD_REFRESH_POLL_MS,
      AUTO_SAVE_DELAY_MS, RETRY_DELAY_BASE_MS,
    ];
    constants.forEach(c => {
      expect(typeof c).toBe('number');
      expect(c).toBeGreaterThan(0);
    });
  });

  test('debounce values increase correctly', () => {
    expect(DEBOUNCE_FAST_MS).toBeLessThan(DEBOUNCE_DEFAULT_MS);
    expect(DEBOUNCE_DEFAULT_MS).toBeLessThan(DEBOUNCE_SLOW_MS);
  });

  test('API timeout is reasonable (5s–5min)', () => {
    expect(API_TIMEOUT_MS).toBeGreaterThanOrEqual(5_000);
    expect(API_TIMEOUT_MS).toBeLessThanOrEqual(300_000);
  });

  test('stream timeout is longer than API timeout', () => {
    expect(STREAM_TIMEOUT_MS).toBeGreaterThan(API_TIMEOUT_MS);
  });

  test('MAX_RETRY_ATTEMPTS is a small positive integer', () => {
    expect(Number.isInteger(MAX_RETRY_ATTEMPTS)).toBe(true);
    expect(MAX_RETRY_ATTEMPTS).toBeGreaterThanOrEqual(1);
    expect(MAX_RETRY_ATTEMPTS).toBeLessThanOrEqual(10);
  });

  test('poll intervals are sensible (100ms–60s)', () => {
    expect(AGENT_STATUS_POLL_MS).toBeGreaterThanOrEqual(100);
    expect(THREAD_REFRESH_POLL_MS).toBeGreaterThanOrEqual(100);
    expect(HEALTH_CHECK_INTERVAL_MS).toBeLessThanOrEqual(60_000);
  });
});
