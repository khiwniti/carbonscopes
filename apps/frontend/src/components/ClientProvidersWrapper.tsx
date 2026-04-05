'use client';

import { ReactNode, useEffect, useState } from 'react';
import { ProvidersClient } from './ProvidersClient';

export function ClientProvidersWrapper({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Don't render children until providers are mounted (prevents useContext errors)
  if (!mounted) {
    return null;
  }

  return <ProvidersClient>{children}</ProvidersClient>;
}
