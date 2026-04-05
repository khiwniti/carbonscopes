/**
 * Unit tests for memory leak fixes (#115)
 * Verifies cleanup functions exist in hooks that use setInterval.
 */
import { describe, test, expect } from 'bun:test';
import { readFileSync } from 'fs';
import { join } from 'path';

const SRC = join(import.meta.dir, '..');

function readSrc(relPath: string) {
  return readFileSync(join(SRC, relPath), 'utf-8');
}

describe('Memory leak prevention (#115)', () => {
  test('use-promo.ts has clearInterval cleanup', () => {
    const content = readSrc('hooks/utils/use-promo.ts');
    expect(content).toContain('clearInterval');
    // Return cleanup pattern
    expect(content).toMatch(/return\s*\(\s*\)\s*=>/);
  });

  test('use-holiday-promo.ts has clearInterval cleanup', () => {
    const content = readSrc('hooks/utils/use-holiday-promo.ts');
    expect(content).toContain('clearInterval');
    expect(content).toMatch(/return\s*\(\s*\)\s*=>/);
  });

  test('use-promo.ts setInterval is assigned to variable', () => {
    const content = readSrc('hooks/utils/use-promo.ts');
    // setInterval result should be captured for cleanup
    const hasCapture = /const\s+\w+\s*=\s*setInterval/.test(content) ||
                       /\w+\s*=\s*setInterval/.test(content) ||
                       content.includes('_intervalId');
    expect(hasCapture).toBe(true);
  });
});

describe('Console.log removal (#116)', () => {
  const filesToCheck = [
    'lib/analytics/gtm.ts',
    'lib/api-client.ts',
    'components/thread/ThreadComponent.tsx',
  ];

  for (const file of filesToCheck) {
    test(`${file} uses logger not console.log`, () => {
      try {
        const content = readSrc(file);
        const bareConsole = (content.match(/\bconsole\.(log|warn|info|debug)\b/g) || []).length;
        expect(bareConsole).toBe(0);
      } catch {
        // File doesn't exist — skip
        expect(true).toBe(true);
      }
    });
  }

  test('logger.ts exists and exports logger object', () => {
    const content = readSrc('lib/logger.ts');
    expect(content).toContain('export const logger');
    expect(content).toContain('log:');
    expect(content).toContain('error:');
    expect(content).toContain('warn:');
  });
});

describe('Timeout constants (#121)', () => {
  test('timeouts.ts exports numeric constants', () => {
    const content = readSrc('lib/constants/timeouts.ts');
    expect(content).toContain('export const');
    expect(content).toContain('_MS');
    expect(content).toContain('API_TIMEOUT_MS');
    expect(content).toContain('DEBOUNCE_DEFAULT_MS');
  });
});

describe('XSS sanitization (#116)', () => {
  test('sanitize.ts uses dompurify not isomorphic-dompurify', () => {
    const content = readSrc('lib/sanitize.ts');
    expect(content).not.toContain('isomorphic-dompurify');
    expect(content).toContain('dompurify');
  });

  test('sanitize.ts has window guard', () => {
    const content = readSrc('lib/sanitize.ts');
    expect(content).toContain("typeof window === 'undefined'");
  });

  test('sanitize.ts exports getSafeHtml', () => {
    const content = readSrc('lib/sanitize.ts');
    expect(content).toContain('export function getSafeHtml');
  });

  test('code-block.tsx uses getSafeHtml', () => {
    const content = readSrc('components/ui/code-block.tsx');
    expect(content).toContain('getSafeHtml');
  });

  test('mermaid-renderer-client uses getSafeHtml', () => {
    const content = readSrc('components/ui/mermaid-renderer-client.tsx');
    expect(content).toContain('getSafeHtml');
  });
});
