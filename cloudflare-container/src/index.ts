/**
 * Cloudflare Worker entrypoint for CarbonScopes backend.
 *
 * This Worker sits in front of the Cloudflare Container running the
 * FastAPI backend and proxies matching requests to it.  It also handles
 * CORS pre-flight requests and provides a small grace period while the
 * container is still booting.
 */

interface Env {
  /** The container binding injected by Cloudflare Containers runtime. */
  BACKEND: Fetcher;
}

/** Paths that should be forwarded to the backend container. */
const BACKEND_PATH_PREFIXES = ['/v1/', '/health', '/healthz', '/docs', '/openapi.json', '/redoc'];

/** Allowed origins for CORS. Adjust as needed. */
const ALLOWED_ORIGINS = [
  'https://carbonscope.ensimu.space',
  'https://carbonscope-frontend.pages.dev',
  'http://localhost:3000',
];

function corsHeaders(origin: string | null): Record<string, string> {
  const allowedOrigin =
    origin && ALLOWED_ORIGINS.some((o) => origin.startsWith(o)) ? origin : ALLOWED_ORIGINS[0];

  return {
    'Access-Control-Allow-Origin': allowedOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Max-Age': '86400',
  };
}

function shouldProxy(pathname: string): boolean {
  return BACKEND_PATH_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const origin = request.headers.get('Origin');

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: 204,
        headers: corsHeaders(origin),
      });
    }

    // Only proxy paths that belong to the backend API
    if (!shouldProxy(url.pathname)) {
      return new Response(JSON.stringify({ error: 'Not Found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json', ...corsHeaders(origin) },
      });
    }

    try {
      // Forward the request to the backend container
      const backendUrl = new URL(request.url);
      backendUrl.hostname = 'localhost';
      backendUrl.port = '8080';
      backendUrl.protocol = 'http:';

      const backendRequest = new Request(backendUrl.toString(), {
        method: request.method,
        headers: request.headers,
        body: request.body,
      });

      const response = await env.BACKEND.fetch(backendRequest);

      // Clone the response so we can add CORS headers
      const newHeaders = new Headers(response.headers);
      for (const [key, value] of Object.entries(corsHeaders(origin))) {
        newHeaders.set(key, value);
      }

      return new Response(response.body, {
        status: response.status,
        statusText: response.statusText,
        headers: newHeaders,
      });
    } catch (err) {
      // The container may still be starting up -- return 503
      console.error('Backend container error:', err);
      return new Response(
        JSON.stringify({
          error: 'Service Unavailable',
          message: 'The backend container is starting up. Please retry in a few seconds.',
        }),
        {
          status: 503,
          headers: {
            'Content-Type': 'application/json',
            'Retry-After': '5',
            ...corsHeaders(origin),
          },
        },
      );
    }
  },
};
