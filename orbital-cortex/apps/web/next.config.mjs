/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    // Same-origin proxy so HttpOnly session cookies work in local dev
    // (browser localhost:3000 → API localhost:8000 is cross-origin).
    const apiTarget =
      process.env.API_PROXY_TARGET ??
      process.env.NEXT_PUBLIC_API_BASE_URL ??
      "http://127.0.0.1:8000";
    return [
      {
        source: "/api/oc/:path*",
        destination: `${apiTarget.replace(/\/$/, "")}/:path*`
      }
    ];
  }
};

export default nextConfig;
