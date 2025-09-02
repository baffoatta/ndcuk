/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'ymzukmntpwohcqiddaqo.supabase.co'],
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**.supabase.co',
        port: '',
        pathname: '/storage/v1/object/public/**',
      },
    ],
  },
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8001/api/v1/:path*',
      },
    ];
  },
};

module.exports = nextConfig;