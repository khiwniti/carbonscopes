import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.INTERNAL_BACKEND_URL || 'http://localhost:8000';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function PUT(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await params);
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, await params);
}

async function proxyRequest(
  request: NextRequest,
  params: { path: string[] }
) {
  const path = params.path.join('/');
  const url = new URL(request.url);
  const targetUrl = `${BACKEND_URL}/v1/${path}${url.search}`;

  console.log(`[API Proxy] ${request.method} ${targetUrl}`);

  try {
    const headers: Record<string, string> = {};
    request.headers.forEach((value, key) => {
      // Skip headers that shouldn't be forwarded
      if (!['host', 'connection', 'content-length'].includes(key.toLowerCase())) {
        headers[key] = value;
      }
    });

    const fetchOptions: RequestInit = {
      method: request.method,
      headers,
    };

    // Forward body for non-GET requests
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      const contentType = request.headers.get('content-type') || '';
      if (contentType.includes('application/json')) {
        fetchOptions.body = await request.text();
      } else if (contentType.includes('multipart/form-data')) {
        fetchOptions.body = await request.arrayBuffer();
      } else {
        fetchOptions.body = await request.text();
      }
    }

    const response = await fetch(targetUrl, fetchOptions);

    // Forward response headers
    const responseHeaders = new Headers();
    response.headers.forEach((value, key) => {
      if (!['transfer-encoding', 'content-encoding'].includes(key.toLowerCase())) {
        responseHeaders.set(key, value);
      }
    });

    const data = await response.arrayBuffer();
    
    return new NextResponse(data, {
      status: response.status,
      statusText: response.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error(`[API Proxy] Error:`, error);
    return NextResponse.json(
      { error: 'Backend unavailable', details: String(error) },
      { status: 502 }
    );
  }
}
