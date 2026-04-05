'use client';

/**
 * HTML Sanitization Utility
 * Protects against XSS attacks by sanitizing HTML content.
 * Browser-only: uses window guard to avoid SSR jsdom dependency.
 * Import only in 'use client' components.
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type DOMPurifyConfig = Record<string, any>;

function getPurify() {
  if (typeof window === 'undefined') return null;
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const mod = require('dompurify');
    return (mod.default ?? mod) as {
      sanitize: (html: string, config?: DOMPurifyConfig) => string;
    };
  } catch {
    return null;
  }
}

/**
 * Sanitize HTML content to prevent XSS attacks.
 * Use this instead of dangerouslySetInnerHTML with raw strings.
 */
export function sanitizeHtml(html: string, options?: DOMPurifyConfig): string {
  const purify = getPurify();
  if (!purify) return '';
  return purify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'img', 'div', 'span',
      'table', 'thead', 'tbody', 'tr', 'th', 'td',
    ],
    ALLOWED_ATTR: ['href', 'title', 'target', 'rel', 'src', 'alt', 'class', 'id'],
    ...options,
  });
}

/**
 * Get sanitized HTML object for dangerouslySetInnerHTML.
 * @example <div dangerouslySetInnerHTML={getSafeHtml(userContent)} />
 */
export function getSafeHtml(html: string, options?: DOMPurifyConfig) {
  return { __html: sanitizeHtml(html, options) };
}
