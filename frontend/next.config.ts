import type { NextConfig } from "next";

const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.trim() || "";
const isSameOriginApi =
  configuredApiUrl === "/api" || configuredApiUrl === "/api/";
const localBackendOrigin = "http://localhost:8000";
const apiOrigin = isSameOriginApi
  ? localBackendOrigin
  : configuredApiUrl.replace(/\/$/, "");

const nextConfig: NextConfig = {
  async rewrites() {
    if (
      process.env.NODE_ENV === "production" &&
      (!configuredApiUrl || isSameOriginApi)
    ) {
      return [];
    }

    const destinationOrigin =
      !configuredApiUrl && process.env.NODE_ENV !== "production"
        ? localBackendOrigin
        : apiOrigin;

    return [
      {
        source: "/api/:path*",
        destination: `${destinationOrigin}/:path*`,
      },
      {
        source: "/health",
        destination: `${destinationOrigin}/health`,
      },
    ];
  },
};

export default nextConfig;
