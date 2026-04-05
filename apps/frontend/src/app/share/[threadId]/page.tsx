'use client';

import dynamic from 'next/dynamic';
import Link from 'next/link';
import { SharePageWrapper } from './_components/SharePageWrapper';
import React, { Suspense } from 'react';
import {
  ThreadParams,
} from '@/components/thread/types';

// Dynamic import to avoid SSR issues with browser-only dependencies
const ThreadComponent = dynamic(
  () => import('@/components/thread/ThreadComponent').then(mod => ({ default: mod.ThreadComponent })),
  { 
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading shared thread...</p>
        </div>
      </div>
    )
  }
);

export default function ShareThreadPage({
  params,
}: {
  params: Promise<ThreadParams>;
}) {
  const unwrappedParams = React.use(params);
  const threadId = unwrappedParams.threadId;

  // Validate threadId format (basic validation)
  if (!threadId || threadId.length < 10) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center max-w-md px-4">
          <h1 className="text-2xl font-semibold mb-2">Thread Not Found</h1>
          <p className="text-muted-foreground mb-4">
            The shared thread you're looking for doesn't exist or has been removed.
          </p>
          <Link
            href="/"
            className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            Go to Homepage
          </Link>
        </div>
      </div>
    );
  }

  // For shared pages, projectId will be fetched from the thread data
  // Pass empty string - useThreadData will handle it via thread->project relationship
  const projectId = '';

  return (
    <SharePageWrapper>
      <Suspense fallback={
        <div className="flex items-center justify-center h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading thread...</p>
          </div>
        </div>
      }>
        <ThreadComponent
          projectId={projectId}
          threadId={threadId}
          isShared={true}
        />
      </Suspense>
    </SharePageWrapper>
  );
}
