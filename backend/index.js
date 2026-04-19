// CarbonScope Backend Worker - Routes requests to Container
import { Container, getContainer } from "@cloudflare/containers";

// Container class definition
export class CarbonScopeBackend extends Container {
  async fetch(request) {
    // Forward request to the container
    return await super.fetch(request);
  }
}

// Legacy stubs - satisfy existing Durable Object bindings from previous deployments
// Can be removed after delete-class migrations in a future deploy
export class NotificationsDurableObject {
  constructor(state, env) {}
  async fetch(request) {
    return new Response("Deprecated - use CarbonScopeBackend", { status: 410 });
  }
  async alarm() {}
}

export class BackendContainer {
  constructor(state, env) {}
  async fetch(request) {
    return new Response("Deprecated - use CarbonScopeBackend", { status: 410 });
  }
  async alarm() {}
}

export class RateLimiter {
  constructor(state, env) {}
  async fetch(request) {
    return new Response("Deprecated", { status: 410 });
  }
  async alarm() {}
}

// Main Worker handler
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Health check endpoint (handled by Worker)
    if (url.pathname === "/health") {
      return new Response(JSON.stringify({ 
        status: "ok", 
        service: "carbonscope-backend",
        timestamp: new Date().toISOString()
      }), {
        headers: { "Content-Type": "application/json" }
      });
    }

    // Get container instance
    const container = await getContainer(env.CARBONSCOPE_BACKEND, url.pathname);
    
    // Forward request to container
    return await container.fetch(request);
  }
};
