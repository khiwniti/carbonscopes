'use client';

import { ReactNode } from 'react';
import { ProvidersClient } from './ProvidersClient';

/**
 * Providers must wrap the tree on the first client paint. Deferring with
 * useState+useEffect returned null first and allowed children (e.g. hooks
 * using TanStack Query) to run without QueryClient — "No QueryClient set".
 * Root layout is already force-dynamic for SSR/provider alignment.
 */
export function ClientProvidersWrapper({ children }: { children: ReactNode }) {
  return <ProvidersClient>{children}</ProvidersClient>;
}
