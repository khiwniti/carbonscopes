/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    // Disable ESLint during production builds
    ignoreDuringBuilds: true,
  },
  typescript: {
    // Keep TypeScript checking enabled
    ignoreBuildErrors: false,
  },
  experimental: {
    reactCompiler: false,
    turbo: {
      root: '../../',
    },
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
  // Optimize for production
  productionBrowserSourceMaps: false,
  // Output configuration
  output: 'standalone',
  
  // Webpack config to exclude problematic packages from SSR
  webpack: (config, { isServer }) => {
    if (isServer) {
      config.externals = [...(config.externals || []), 'mermaid'];
    }
    return config;
  },
};

export default nextConfig;
