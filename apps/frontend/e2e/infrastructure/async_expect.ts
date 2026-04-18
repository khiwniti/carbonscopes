/**
 * async_expect.ts — Custom async wait utilities for Playwright E2E tests.
 *
 * Supplements Playwright's built-in `expect` with domain-specific waiting
 * patterns.  All helpers throw an `Error` on timeout with a descriptive
 * message pointing to the failing condition.
 *
 * Usage:
 *   import { AsyncExpect } from './async_expect';
 *
 *   await AsyncExpect.waitUntil(
 *     () => page.locator('[data-status="complete"]').isVisible(),
 *     'assessment status to become "complete"',
 *     { timeout: 30_000 }
 *   );
 */

import { Page, Locator } from '@playwright/test';

export interface WaitOptions {
  /** Maximum milliseconds to wait (default: 30_000). */
  timeout?: number;
  /** Milliseconds between polls (default: 500). */
  pollInterval?: number;
}

export class AsyncExpect {

  // ── Core wait ─────────────────────────────────────────────────────────────

  /**
   * Poll a condition until it returns `true` or `timeout` is reached.
   *
   * @param condition    A function returning a `boolean` or `Promise<boolean>`.
   * @param description  Human-readable description for failure messages.
   * @param opts         Timeout and poll interval options.
   */
  static async waitUntil(
    condition: () => boolean | Promise<boolean>,
    description: string,
    opts: WaitOptions = {},
  ): Promise<void> {
    const timeout      = opts.timeout      ?? 30_000;
    const pollInterval = opts.pollInterval ?? 500;
    const deadline     = Date.now() + timeout;

    while (Date.now() < deadline) {
      const result = await condition();
      if (result) return;
      await _sleep(pollInterval);
    }

    throw new Error(`Timed out after ${timeout}ms waiting for: ${description}`);
  }

  // ── Value waits ───────────────────────────────────────────────────────────

  /**
   * Wait until a getter returns the expected value.
   */
  static async waitForValue<T>(
    getter: () => T | Promise<T>,
    expected: T,
    description: string,
    opts: WaitOptions = {},
  ): Promise<void> {
    const timeout      = opts.timeout      ?? 30_000;
    const pollInterval = opts.pollInterval ?? 500;
    const deadline     = Date.now() + timeout;
    let last: T = undefined as unknown as T;

    while (Date.now() < deadline) {
      last = await getter();
      if (last === expected) return;
      await _sleep(pollInterval);
    }

    throw new Error(
      `Timed out after ${timeout}ms waiting for: ${description}\n` +
      `  Expected: ${JSON.stringify(expected)}\n` +
      `  Got:      ${JSON.stringify(last)}`
    );
  }

  // ── Locator waits ─────────────────────────────────────────────────────────

  /**
   * Wait until a Locator's text matches a substring or RegExp.
   */
  static async waitForText(
    locator: Locator,
    text: string | RegExp,
    description: string,
    opts: WaitOptions = {},
  ): Promise<void> {
    const timeout = opts.timeout ?? 30_000;
    await locator.waitFor({ state: 'visible', timeout });

    await AsyncExpect.waitUntil(async () => {
      const content = await locator.textContent();
      if (!content) return false;
      return typeof text === 'string'
        ? content.includes(text)
        : text.test(content);
    }, description, opts);
  }

  /**
   * Wait until a Locator count reaches the expected number.
   */
  static async waitForCount(
    locator: Locator,
    expected: number,
    description: string,
    opts: WaitOptions = {},
  ): Promise<void> {
    await AsyncExpect.waitForValue(
      () => locator.count(),
      expected,
      description,
      opts,
    );
  }

  // ── API polling ───────────────────────────────────────────────────────────

  /**
   * Poll a URL via fetch until the response satisfies a predicate.
   *
   * Useful for waiting on backend state without navigating in the browser.
   */
  static async waitForApiResponse<T = unknown>(
    url: string,
    predicate: (data: T) => boolean,
    description: string,
    opts: WaitOptions & { headers?: Record<string, string> } = {},
  ): Promise<T> {
    const timeout      = opts.timeout      ?? 30_000;
    const pollInterval = opts.pollInterval ?? 1_000;
    const deadline     = Date.now() + timeout;
    let lastData: T | undefined;

    while (Date.now() < deadline) {
      try {
        const resp = await fetch(url, { headers: opts.headers });
        if (resp.ok) {
          lastData = await resp.json() as T;
          if (predicate(lastData)) return lastData;
        }
      } catch {
        // Network error — keep polling
      }
      await _sleep(pollInterval);
    }

    throw new Error(
      `Timed out after ${timeout}ms waiting for: ${description}\n` +
      `  Last response: ${JSON.stringify(lastData)?.slice(0, 200)}`
    );
  }

  // ── Negative assertion ────────────────────────────────────────────────────

  /**
   * Assert a condition never becomes true within `duration` milliseconds.
   */
  static async assertNeverTrue(
    condition: () => boolean | Promise<boolean>,
    description: string,
    opts: { duration?: number; pollInterval?: number } = {},
  ): Promise<void> {
    const duration     = opts.duration     ?? 5_000;
    const pollInterval = opts.pollInterval ?? 250;
    const deadline     = Date.now() + duration;

    while (Date.now() < deadline) {
      if (await condition()) {
        throw new Error(`Condition became true (should never happen): ${description}`);
      }
      await _sleep(pollInterval);
    }
  }
}

function _sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
