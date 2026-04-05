import type { NextConfig } from 'next';

/**
 * Next.js Production Configuration for Azure Deployment
 *
 * Optimized for containerized deployment with standalone output.
 * This config is used by the Dockerfile.production build.
 */
const nextConfig: NextConfig = {
  // Standalone output for Docker deployment (70% smaller)
  output: 'standalone',

  // Security and performance
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
    // Use default loader for Azure deployment
    unoptimized: false,
  },

  // Disable telemetry in production
  typescript: {
    // Build will fail on type errors (good for CI/CD)
    ignoreBuildErrors: false,
  },

  eslint: {
    // Build will fail on lint errors
    ignoreDuringBuilds: false,
  },

  // Experimental features
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['@/components', '@/lib'],
  },
};

export default nextConfig;
