'use client';

// Force dynamic rendering to avoid context issues during static generation
export const dynamic = 'force-dynamic';
export const revalidate = 0;

import { useEffect } from 'react';
import { AlertTriangle, Home, RefreshCw } from 'lucide-react';

export default function DashboardError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Dashboard error:', error);
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
          Dashboard Error
        </h1>
        
        <p className="text-muted-foreground mb-6">
          We encountered an issue loading the dashboard. Your data is safe and this is likely temporary.
        </p>

        {process.env.NODE_ENV === 'development' && (
          <details className="mb-6 text-left">
            <summary className="cursor-pointer text-sm text-muted-foreground hover:text-foreground mb-2">
              Error details (dev only)
            </summary>
            <pre className="text-xs bg-muted p-4 rounded-lg overflow-auto max-h-40">
              {error.message}
              {error.stack && `\n\n${error.stack}`}
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
          
          <a
            href="/dashboard"
            className="inline-flex items-center gap-2 px-6 py-2 bg-secondary text-secondary-foreground rounded-lg hover:bg-secondary/90 transition-colors font-medium"
          >
            <Home className="h-4 w-4" />
            Dashboard home
          </a>
        </div>

        <div className="mt-6 p-4 bg-muted/50 rounded-lg text-left">
          <p className="text-sm text-muted-foreground font-medium mb-2">
            Quick fixes to try:
          </p>
          <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
            <li>Refresh the page</li>
            <li>Clear your browser cache</li>
            <li>Check your internet connection</li>
            <li>Try a different browser</li>
          </ul>
        </div>

        <p className="text-xs text-muted-foreground mt-6">
          If this problem persists, please contact support at support@carbonscope.com
        </p>
      </div>
    </div>
  );
}
