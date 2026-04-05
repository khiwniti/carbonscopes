/**
 * BILLING DISABLED - Subscription page shows free access
 */
'use client';

import Link from 'next/link';

export default function SubscriptionPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--carbonscope-background)]">
      <div className="text-center max-w-md mx-auto p-8">
        <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-[var(--carbonscope-primary)]/20 flex items-center justify-center">
          <svg className="w-8 h-8 text-[var(--carbonscope-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h1 className="text-3xl font-bold text-[var(--carbonscope-text-primary)] mb-4">
          Unlimited Access Active
        </h1>
        <p className="text-[var(--carbonscope-text-secondary)] mb-8">
          You have unlimited free access to CarbonScope. No subscription management needed.
        </p>
        <Link 
          href="/dashboard"
          className="inline-flex items-center justify-center px-6 py-3 rounded-lg bg-[var(--carbonscope-primary)] text-white font-medium hover:bg-[var(--carbonscope-primary-dark)] transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
