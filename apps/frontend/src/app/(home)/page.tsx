'use client';

import { Suspense, lazy } from 'react';
import { BackgroundAALChecker } from '@/components/auth/background-aal-checker';
import { HeroSection as NewHeroSection } from '@/components/home/hero-section';
import { ShowCaseSection } from '@/components/home/showcase-section';
import { FooterSection } from '@/components/home/footer-section';

// Lazy load components
const MobileAppInterstitial = lazy(() =>
  import('@/components/announcements/mobile-app-interstitial').then(mod => ({ default: mod.MobileAppInterstitial }))
);

export default function Home() {
  return (
    <BackgroundAALChecker>
      <div style={{ width: '100%', minHeight: '100vh' }}>
        {/* Hero Section - Full viewport height */}
        <NewHeroSection />

        {/* Showcase Section - Worker capabilities */}
        <ShowCaseSection />

        {/* Footer Section */}
        <FooterSection />

        {/* Mobile app banner - shown on mobile devices for logged-in users */}
        <Suspense fallback={null}>
          <MobileAppInterstitial />
        </Suspense>
      </div>
    </BackgroundAALChecker>
  );
}
