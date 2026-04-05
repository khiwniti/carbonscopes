'use client';

import { ReactNode } from 'react';
import { ThemeProvider } from '@/components/home/theme-provider';
import { AuthProvider } from '@/components/AuthProvider';
import { PresenceProvider } from '@/components/presence-provider';
import { ReactQueryProvider } from '@/app/react-query-provider';
import { I18nProvider } from '@/components/i18n-provider';

/**
 * All context-using providers wrapped together.
 * This file is ONLY imported in browser environment (not during SSG).
 */
export function ProvidersClient({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <AuthProvider>
        <I18nProvider>
          <PresenceProvider>
            <ReactQueryProvider>
              {children}
            </ReactQueryProvider>
          </PresenceProvider>
        </I18nProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}
