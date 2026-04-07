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
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://www.googletagmanager.com https://eu.i.posthog.com",
      "style-src 'self' 'unsafe-inline'",
      "img-src 'self' data: https:",
      "font-src 'self' data:",
      "connect-src 'self' https://suna-backend-app.azurewebsites.net https://*.supabase.co wss://*.supabase.co https://www.googletagmanager.com https://eu.i.posthog.com https://eu.posthog.com https://cloud.langfuse.com http://local-backend http://localhost:*",
      "frame-src 'self' https://www.youtube.com https://demo.arcade.software",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'self' https://*.cloudspaces.litng.ai vscode-webview:",
    ].join('; '),
  },
];

const nextConfig: NextConfig = {
  output: 'standalone',
  outputFileTracingRoot: path.join(__dirname, '../../'),
  reactStrictMode: false,
  poweredByHeader: false,
  compress: true,
  allowedDevOrigins: [
    'https://3001-01knh7b1ypcr4dqe973fd266s9.cloudspaces.litng.ai',
    'https://*.cloudspaces.litng.ai',
  ],
  transpilePackages: ['@agentpress/shared'],
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@agentpress/shared': path.resolve(__dirname, '../../packages/shared'),
    };
    if (isServer) {
      config.resolve.alias = {
        ...config.resolve.alias,
        react: path.resolve(__dirname, '../../node_modules/react'),
        'react-dom': path.resolve(__dirname, '../../node_modules/react-dom'),
      };
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
