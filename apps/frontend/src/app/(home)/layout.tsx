'use client';

import { Navbar } from '@/components/home/navbar';
import { usePathname } from 'next/navigation';

export default function HomeLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const pathname = usePathname();
  const isHomePage = pathname === '/';

  return (
    <div style={{ width: '100%', minHeight: '100dvh', position: 'relative' }}>
      {/* Navbar is absolute on home page to not take up space, sticky on other pages */}
      <div style={isHomePage ? { position: 'absolute', top: 0, left: 0, right: 0, zIndex: 50 } : {}}>
        <Navbar isAbsolute={isHomePage} />
      </div>
      {children}
    </div>
  );
}
