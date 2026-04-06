import { siteMetadata } from '@/lib/site-metadata';
import type { Metadata, Viewport } from 'next';
import './globals.css';
import { ClientProvidersWrapper } from '@/components/ClientProvidersWrapper';
import { Toaster } from '@/components/ui/sonner';
import '@/lib/polyfills';
import { instrumentSerif } from './fonts/instrument-serif';
import { plusJakarta } from './fonts/plus-jakarta';
import { ibmPlexMono } from './fonts/ibm-plex-mono';
import { Suspense, lazy } from 'react';
import { featureFlags } from '@/lib/feature-flags';

// Lazy load non-critical analytics and global components
// Note: Vercel Analytics & Speed Insights disabled for Azure deployment
// const Analytics = lazy(() => import('@vercel/analytics/react').then(mod => ({ default: mod.Analytics })));
// const SpeedInsights = lazy(() => import('@vercel/speed-insights/next').then(mod => ({ default: mod.SpeedInsights })));
const GoogleTagManager = lazy(() => import('@next/third-parties/google').then(mod => ({ default: mod.GoogleTagManager })));
const PostHogIdentify = lazy(() => import('@/components/posthog-identify').then(mod => ({ default: mod.PostHogIdentify })));
const PlanSelectionModal = lazy(() => import('@/components/billing/pricing/plan-selection-modal').then(mod => ({ default: mod.PlanSelectionModal })));
const AnnouncementDialog = lazy(() => import('@/components/announcements/announcement-dialog').then(mod => ({ default: mod.AnnouncementDialog })));
const RouteChangeTracker = lazy(() => import('@/components/analytics/route-change-tracker').then(mod => ({ default: mod.RouteChangeTracker })));
const AuthEventTracker = lazy(() => import('@/components/analytics/auth-event-tracker').then(mod => ({ default: mod.AuthEventTracker })));
const CookieVisibility = lazy(() => import('@/components/cookie-visibility').then(mod => ({ default: mod.CookieVisibility })));


export const viewport: Viewport = {
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' }
  ],
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
};

// Force dynamic rendering to prevent static generation of error pages
// which causes useContext errors with client providers
export const dynamic = 'force-dynamic';
export const revalidate = 0;

export const metadata: Metadata = {
  metadataBase: new URL(siteMetadata.url),
  title: {
    default: siteMetadata.title,
    template: `%s | ${siteMetadata.name}`,
  },
  description: siteMetadata.description,
  keywords: siteMetadata.keywords,
  authors: [{ name: 'BKS - CarbonScope Team', url: 'https://www.carbonscope.ai' }],
  creator: 'BKS - CarbonScope',
  publisher: 'BKS - CarbonScope',
  applicationName: siteMetadata.name,
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  openGraph: {
    type: 'website',
    title: siteMetadata.title,
    description: siteMetadata.description,
    url: siteMetadata.url,
    siteName: siteMetadata.name,
    locale: 'en_US',
    images: [
      {
        url: '/banner.png',
        width: 1200,
        height: 630,
        alt: `${siteMetadata.title} – ${siteMetadata.description}`,
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: siteMetadata.title,
    description: siteMetadata.description,
    creator: '@carbonscope',
    site: '@carbonscope',
    images: ['/banner.png'],
  },
  icons: {
    icon: [
      { url: '/favicon-dark.svg', type: 'image/svg+xml', media: '(prefers-color-scheme: light)' },
      { url: '/favicon-light.svg', type: 'image/svg+xml', media: '(prefers-color-scheme: dark)' },
    ],
    shortcut: '/favicon-dark.svg',
    apple: [{ url: '/apple-touch-icon.png', sizes: '180x180' }],
  },
  manifest: '/manifest.json',
  alternates: {
    canonical: siteMetadata.url,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" suppressHydrationWarning data-scroll-behavior="smooth" className={`${instrumentSerif.variable} ${plusJakarta.variable} ${ibmPlexMono.variable}`}>
      <head>
        {/* DNS prefetch for analytics (loaded later but resolve DNS early) */}
        <link rel="dns-prefetch" href="https://www.googletagmanager.com" />
        <link rel="dns-prefetch" href="https://eu.i.posthog.com" />
        
        {/* Container Load - Initialize dataLayer with page context BEFORE GTM loads */}
        <script
          dangerouslySetInnerHTML={{ __html: `
              (function() {
                window.dataLayer = window.dataLayer || [];
                var pathname = window.location.pathname;

                // Get language from localStorage, cookie, or default to 'en'
                var lang = 'en';
                try {
                  // Check localStorage first
                  var stored = localStorage.getItem('locale');
                  if (stored) {
                    lang = stored;
                  } else {
                    // Check cookie
                    var cookies = document.cookie.split(';');
                    for (var i = 0; i < cookies.length; i++) {
                      var cookie = cookies[i].trim();
                      if (cookie.indexOf('locale=') === 0) {
                        lang = cookie.substring(7);
                        break;
                      }
                    }
                  }
                } catch (e) {}

                var context = { master_group: 'General', content_group: 'Other', page_type: 'other', language: lang };

                if (pathname === '/' || pathname === '') {
                  context = { master_group: 'General', content_group: 'Other', page_type: 'home', language: lang };
                } else if (pathname.indexOf('/auth') === 0) {
                  context = { master_group: 'General', content_group: 'User', page_type: 'auth', language: lang };
                } else if (pathname === '/dashboard') {
                  context = { master_group: 'Platform', content_group: 'Dashboard', page_type: 'home', language: lang };
                } else if (pathname.indexOf('/projects') === 0 || pathname.indexOf('/thread') === 0) {
                  context = { master_group: 'Platform', content_group: 'Dashboard', page_type: 'thread', language: lang };
                } else if (pathname.indexOf('/settings') === 0) {
                  context = { master_group: 'Platform', content_group: 'User', page_type: 'settings', language: lang };
                }

                window.dataLayer.push(context);
              })();
            ` }}
        />
        
        {/* Static SEO meta tags - rendered in initial HTML */}
        <title>CarbonScope: Embodied Carbon Intelligence Platform</title>
        <meta name="description" content="Professional carbon footprint analysis for the built environment. EN 15978 compliant lifecycle assessment, TGO database integration, and TREES/EDGE certification guidance." />
        <meta name="keywords" content="CarbonScope, BKS, Embodied Carbon, Carbon Footprint, LCA, Life Cycle Assessment, EN 15978, Building Carbon, TREES, EDGE, Green Building, Sustainable Construction, Carbon Intelligence" />
        <meta property="og:title" content="CarbonScope: Embodied Carbon Intelligence Platform" />
        <meta property="og:description" content="Professional carbon footprint analysis for the built environment. EN 15978 compliant lifecycle assessment, TGO database integration, and TREES/EDGE certification guidance." />
        <meta property="og:image" content="https://www.carbonscope.ai/banner.png" />
        <meta property="og:url" content="https://www.carbonscope.ai" />
        <meta property="og:type" content="website" />
        <meta property="og:site_name" content="CarbonScope" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="CarbonScope: Embodied Carbon Intelligence Platform" />
        <meta name="twitter:description" content="Professional carbon footprint analysis for the built environment. EN 15978 compliant lifecycle assessment, TGO database integration, and TREES/EDGE certification guidance." />
        <meta name="twitter:image" content="https://www.carbonscope.ai/banner.png" />
        <meta name="twitter:site" content="@carbonscope" />
        <link rel="canonical" href="https://www.carbonscope.ai" />
        
        {/* iOS Smart App Banner - shows native install banner in Safari */}
        {!featureFlags.disableMobileAdvertising ? (
          <meta name="apple-itunes-app" content="app-id=6754448524, app-argument=carbonscope://" />
        ) : null}



        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'Organization',
              name: siteMetadata.name,
              alternateName: ['CarbonScope', 'BKS CarbonScope', 'CarbonScope: Embodied Carbon Intelligence Platform'],
              url: siteMetadata.url,
              logo: `${siteMetadata.url}/Logomark-Black.png`,
              description: siteMetadata.description,
              foundingDate: '2024',
              sameAs: [
                'https://github.com/BKS-ai/CarbonScope',
                'https://x.com/carbonscope',
                'https://linkedin.com/company/carbonscope',
              ],
              contactPoint: {
                '@type': 'ContactPoint',
                contactType: 'Customer Support',
                url: siteMetadata.url,
              },
            }) }}
        />

        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'SoftwareApplication',
              name: siteMetadata.title,
              alternateName: [siteMetadata.name, 'CarbonScope'],
              applicationCategory: 'BusinessApplication',
              operatingSystem: 'Web, macOS, Windows, Linux',
              description: siteMetadata.description,
              offers: {
                '@type': 'Offer',
                price: '0',
                priceCurrency: 'USD',
              },
              aggregateRating: {
                '@type': 'AggregateRating',
                ratingValue: '4.8',
                ratingCount: '1000',
              },
            }) }}
        />
      </head>

      <body
        className="antialiased font-sans"
        style={{
          background: 'var(--carbonscope-background)',
          color: 'var(--carbonscope-text-primary)',
          fontFamily: 'var(--font-jakarta), sans-serif'
        }}
      >
        <ClientProvidersWrapper>
          {children}
          <Toaster />
          <Suspense fallback={null}>
            <PlanSelectionModal />
          </Suspense>
          <Suspense fallback={null}>
            <AnnouncementDialog />
          </Suspense>
          {/* Analytics components need auth context - must be inside providers */}
          <Suspense fallback={null}>
            <PostHogIdentify />
          </Suspense>
          <Suspense fallback={null}>
            <RouteChangeTracker />
          </Suspense>
          <Suspense fallback={null}>
            <AuthEventTracker />
          </Suspense>
          <Suspense fallback={null}>
            <CookieVisibility />
          </Suspense>
        </ClientProvidersWrapper>
        {/* Third-party analytics - independent of auth context */}
        {/* Vercel Analytics & Speed Insights disabled for Azure deployment */}
        {/* <Suspense fallback={null}>
          <Analytics />
        </Suspense> */}
        {process.env.NEXT_PUBLIC_GTM_ID && (
        <Suspense fallback={null}>
            <GoogleTagManager gtmId={process.env.NEXT_PUBLIC_GTM_ID} />
        </Suspense>
        )}
        {/* <Suspense fallback={null}>
          <SpeedInsights />
        </Suspense> */}
      </body>
    </html>
  );
}
