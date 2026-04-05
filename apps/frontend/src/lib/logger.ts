/**
 * Production logger utility.
 * Only emits output in development. Silent in production.
 * Use this instead of console.log throughout the codebase.
 */

const isDev = process.env.NODE_ENV !== 'production';

export const logger = {
  log: (...args: unknown[]) => {
    if (isDev) console.log(...args); // eslint-disable-line no-console
  },
  info: (...args: unknown[]) => {
    if (isDev) console.info(...args); // eslint-disable-line no-console
  },
  warn: (...args: unknown[]) => {
    if (isDev) console.warn(...args); // eslint-disable-line no-console
  },
  debug: (...args: unknown[]) => {
    if (isDev) console.debug(...args); // eslint-disable-line no-console
  },
  /** Always logs errors regardless of environment. */
  error: (...args: unknown[]) => {
    console.error(...args); // eslint-disable-line no-console
  },
};
