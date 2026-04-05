'use client';

// Force dynamic rendering to avoid context issues during static generation
export const dynamic = 'force-dynamic';
export const revalidate = 0;

import { useEffect } from 'react';

export default function GlobalError({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <html>
      <body style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        fontFamily: 'system-ui, sans-serif',
        backgroundColor: '#000',
        color: '#fff',
        margin: 0
      }}>
        <div style={{ textAlign: 'center', maxWidth: '600px', padding: '2rem' }}>
          <h1 style={{ fontSize: '2rem', marginBottom: '1rem', fontWeight: 600 }}>
            Application Error
          </h1>
          <p style={{ color: '#888', marginBottom: '2rem', lineHeight: 1.6 }}>
            A global error occurred. Please try refreshing the page or contact support if the problem persists.
          </p>
          {process.env.NODE_ENV === 'development' && error && (
            <details style={{ textAlign: 'left', marginTop: '2rem' }}>
              <summary style={{
                cursor: 'pointer',
                marginBottom: '1rem',
                color: '#aaa'
              }}>
                Error Details (Development Only)
              </summary>
              <pre style={{
                background: '#111',
                padding: '1rem',
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '0.875rem',
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word'
              }}>
                {error.message}
                {error.digest && `\n\nDigest: ${error.digest}`}
              </pre>
            </details>
          )}
        </div>
      </body>
    </html>
  );
}
