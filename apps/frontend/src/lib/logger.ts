/**
 * Production logger utility.
 * Only emits output in development when NEXT_PUBLIC_VERBOSE_LOGGING is enabled.
 * Silent in production.
 * Use this instead of console.log throughout the codebase.
 */

const isDev = process.env.NODE_ENV !== 'production';
const isVerbose = process.env.NEXT_PUBLIC_VERBOSE_LOGGING === 'true';

export const logger = {
  log: (...args: unknown[]) => {
    if (isDev && isVerbose) console.log(...args); // eslint-disable-line no-console
  },
  info: (...args: unknown[]) => {
    if (isDev && isVerbose) console.info(...args); // eslint-disable-line no-console
  },
  warn: (...args: unknown[]) => {
    if (isDev && isVerbose) console.warn(...args); // eslint-disable-line no-console
  },
  debug: (...args: unknown[]) => {
    if (isDev && isVerbose) console.debug(...args); // eslint-disable-line no-console
  },
  /** Always logs errors regardless of environment. */
  error: (...args: unknown[]) => {
    console.error(...args); // eslint-disable-line no-console
  },
};
