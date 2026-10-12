/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async redirects() {
    // Request, Missions, Network and Control are combined into the Console.
    // Mission briefs (/missions/[id]), jobs and share links keep their routes.
    return ["/plan", "/missions", "/network", "/dashboard"].map((source) => ({
      source,
      destination: "/console",
      permanent: false
    }));
  },
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
