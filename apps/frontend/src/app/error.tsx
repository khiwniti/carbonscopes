'use client';

// Force dynamic rendering to avoid context issues during static generation
export const dynamic = 'force-dynamic';
export const revalidate = 0;

import { useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-background px-4">
      <div className="text-center max-w-md">
        <div className="mb-4 flex justify-center">
          <div className="rounded-full bg-destructive/10 p-3">
            <AlertTriangle className="h-10 w-10 text-destructive" />
          </div>
        </div>
        
        <h1 className="text-2xl font-semibold mb-2 text-foreground">
          Something went wrong
        </h1>
        
        <p className="text-muted-foreground mb-6">
          We encountered an unexpected error. Don't worry, your data is safe.
        </p>

        {process.env.NODE_ENV === 'development' && (
          <details className="mb-6 text-left">
            <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground mb-2">
              Error details (dev only)
            </summary>
            <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-40">
              {error.message}
              {error.digest && `\n\nDigest: ${error.digest}`}
            </pre>
          </details>
        )}
        
        <div className="flex gap-3 justify-center">
          <button
            onClick={reset}
            className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            Try again
          </button>
          
          <Link
            href="/"
            className="px-6 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/90 transition-colors font-medium"
          >
            Go home
          </Link>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          If this problem persists, please contact support.
        </p>
      </div>
    </div>
  );
}
