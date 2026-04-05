// Force dynamic rendering to avoid context issues during static generation
export const dynamic = 'force-dynamic';
export const revalidate = 0;

import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="w-full relative overflow-hidden min-h-screen flex items-center justify-center bg-background">
      <div className="relative flex flex-col items-center w-full max-w-md mx-auto px-6 py-8 text-center">
        <h1 className="text-4xl font-bold text-foreground mb-4">
          404
        </h1>
        <h2 className="text-2xl font-semibold text-foreground mb-4">
          Page Not Found
        </h2>
        <p className="text-base text-foreground/60 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
        >
          Return Home
        </Link>
      </div>
    </div>
  );
}
