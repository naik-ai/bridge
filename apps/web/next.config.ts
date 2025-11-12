import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy API requests to backend
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"}/:path*`,
      },
    ];
  },

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "**",
      },
    ],
  },

  // Enable React strict mode
  reactStrictMode: true,

  // TypeScript strict mode
  typescript: {
    ignoreBuildErrors: false,
  },

  // ESLint
  eslint: {
    ignoreDuringBuilds: false,
  },

  // Experimental features
  experimental: {
    // Enable optimistic UI updates
    optimisticClientCache: true,
  },
};

export default nextConfig;
