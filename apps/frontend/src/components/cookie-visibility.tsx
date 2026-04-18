'use client';

import { usePathname } from 'next/navigation';
import { useEffect } from 'react';

export function CookieVisibility() {
  const pathname = usePathname();

  // Only show cookie button on homepage and dashboard
  const showOnPaths = ['/', '/dashboard'];
  const shouldShow = showOnPaths.some(path => pathname === path);

  useEffect(() => {
    if (shouldShow) {
      const style = document.createElement('style');
      style.textContent = '.cky-btn-revisit-wrapper { display: none !important; }';
      document.head.appendChild(style);
      return () => {
        document.head.removeChild(style);
      };
    }
  }, [shouldShow]);

  return null;
}
