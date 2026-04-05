'use client';

// Force dynamic rendering to avoid context issues during static generation
export const dynamic = 'force-dynamic';
export const revalidate = 0;

import { useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

export default function AuthError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Auth error:', error);
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
          Authentication Error
        </h1>
        
        <p className="text-muted-foreground mb-6">
          We encountered an issue with the authentication process. This is usually temporary.
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
        
        <div className="flex gap-3 justify-center flex-wrap">
          <button
            onClick={reset}
            className="inline-flex items-center gap-2 px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors font-medium"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </button>
          
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-6 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/90 transition-colors font-medium"
          >
            <Home className="h-4 w-4" />
            Go home
          </Link>
        </div>

        <div className="mt-6 p-4 bg-muted/50 rounded-lg text-left">
          <p className="text-sm text-muted-foreground font-medium mb-2">
            Common causes:
          </p>
          <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
            <li>Network connection interrupted</li>
            <li>Browser cookies disabled</li>
            <li>Third-party authentication service temporarily unavailable</li>
            <li>Browser extension blocking authentication</li>
          </ul>
        </div>

        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-left">
          <p className="text-sm text-blue-600 dark:text-blue-400">
            <strong>Alternative:</strong> Try signing in with a different method (Google, Email, etc.)
          </p>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          If this problem persists, please contact support at support@carbonscope.com
        </p>
      </div>
    </div>
  );
}
