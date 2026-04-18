import type { NextConfig } from 'next';
import path from 'path';

const securityHeaders = [
  { key: 'X-Frame-Options',          value: 'SAMEORIGIN' },
  { key: 'X-Content-Type-Options',   value: 'nosniff' },
  { key: 'X-XSS-Protection',         value: '1; mode=block' },
  { key: 'Referrer-Policy',          value: 'origin-when-cross-origin' },
  { key: 'Permissions-Policy',       value: 'camera=(), microphone=(), geolocation=()' },
  { key: 'Strict-Transport-Security',value: 'max-age=63072000; includeSubDomains; preload' },
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://eu.i.posthog.com https://js.stripe.com",
      "script-src-elem 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://eu.i.posthog.com https://js.stripe.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' https://vplbjxijbrgwskgxiukd.supabase.co wss://*.supabase.co https://*.supabase.co https://integrate.api.nvidia.com https://carbonscope.simu.space https://*.workers.dev https://www.googletagmanager.com https://eu.i.posthog.com https://eu.posthog.com https://cloud.langfuse.com https://js.stripe.com http://localhost:*",
      "frame-src 'self' https://www.youtube.com https://demo.arcade.software https://js.stripe.com",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'self'",
    ].join('; '),
  },
];

const nextConfig: NextConfig = {
  output: 'standalone',
  // outputFileTracingRoot: path.join(__dirname, '../../'), // Disabled - causing module resolution issues
  reactStrictMode: false,
  poweredByHeader: false,
  compress: true,
  productionBrowserSourceMaps: false,

  experimental: {
    reactCompiler: false,
  },
  allowedDevOrigins: [
    'https://3000-01kjj6zms0r5qvm5pxcmq9dx3t.cloudspaces.litng.ai',
    'https://*.cloudspaces.litng.ai',
    'https://*.trycloudflare.com',
  ],
  transpilePackages: ['@agentpress/shared'],
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  images: {
    qualities: [75, 85, 100],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  webpack: (config, { isServer }) => {
    // Monorepo paths for shared code only. Do not alias `react` / `react-dom` on the
    // server bundle: Next 15 RSC relies on the `react-server` entry; forcing the
    // root `react` package into server chunks can yield a null dispatcher and
    // `Cannot read properties of null (reading 'useState')` at runtime.
    config.resolve.alias = {
      ...config.resolve.alias,
      '@agentpress/shared': path.resolve(__dirname, '../../packages/shared'),
      'lodash-es': path.resolve(__dirname, './node_modules/lodash-es'),
    };
    // Removed custom react aliases to fix monorepo resolution issues
    if (isServer) {
      config.externals = [...(config.externals || []), 'mermaid'];
    }
    return config;
  },
  async redirects() {
    return [
      { source: '/login', destination: '/auth', permanent: false },
      { source: '/signup', destination: '/auth', permanent: false },
      { source: '/projects', destination: '/dashboard', permanent: false },
      { source: '/settings', destination: '/settings/api-keys', permanent: false },
      { source: '/home', destination: '/', permanent: false },
    ];
  },
  async headers() {
    return [{ source: '/:path*', headers: securityHeaders }];
  },
  async rewrites() {
    // In production, API calls go directly to backend Worker
    // For local development, use the environment variable NEXT_PUBLIC_API_URL
    return [];
  },
};

export default nextConfig;
