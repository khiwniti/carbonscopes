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
      "connect-src 'self' https://api.carbonscope.simu.space https://*.supabase.co wss://*.supabase.co https://www.googletagmanager.com https://eu.i.posthog.com https://eu.posthog.com https://cloud.langfuse.com https://js.stripe.com http://localhost:*",
      "frame-src 'self' https://www.youtube.com https://demo.arcade.software https://js.stripe.com",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'self' https://*.cloudspaces.litng.ai vscode-webview:",
    ].join('; '),
  },
];

const isDev = process.env.NODE_ENV !== 'production';

const nextConfig: NextConfig = {
  // `standalone` output only applies to production builds; enabling it in dev
  // causes routes-manifest.json lookups to fail on this constrained environment.
  ...(isDev ? {} : { output: 'standalone' as const }),
  // outputFileTracingRoot: path.join(__dirname, '../../'), // Disabled - causing module resolution issues
  reactStrictMode: false,
  poweredByHeader: false,
  compress: true,
  productionBrowserSourceMaps: false,

 experimental: {
 reactCompiler: false,
 optimizeCss: !isDev,
 },
  allowedDevOrigins: [
    'https://3001-01knh7b1ypcr4dqe973fd266s9.cloudspaces.litng.ai',
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
 modularizeImports: {
 'lodash-es': {
 transform: 'lodash-es/{{ member }}',
 },
 },
 images: {
 qualities: [75, 85, 100],
 remotePatterns: [
 {
 protocol: 'https',
 hostname: 'carbonscope.simu.space',
 },
 {
 protocol: 'https',
 hostname: '*.supabase.co',
 },
 {
 protocol: 'https',
 hostname: '*.googleusercontent.com',
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
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://localhost:8000/v1/:path*',
      },
    ];
  },
};

export default nextConfig;
