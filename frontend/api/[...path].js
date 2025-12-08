// Vercel Serverless Function - API Proxy
// /api/* 요청을 AWS EB로 프록시

export const config = {
  runtime: 'edge',
};

const BACKEND_URL = 'http://pjt-env.eba-jnmm8j7x.ap-northeast-2.elasticbeanstalk.com';

export default async function handler(request) {
  const url = new URL(request.url);
  const path = url.pathname; // /api/auth/check-username/ 등

  const targetUrl = `${BACKEND_URL}${path}${url.search}`;

  // 요청 헤더 복사 (host 제외)
  const headers = new Headers();
  for (const [key, value] of request.headers.entries()) {
    if (key.toLowerCase() !== 'host') {
      headers.set(key, value);
    }
  }

  try {
    const response = await fetch(targetUrl, {
      method: request.method,
      headers: headers,
      body: request.method !== 'GET' && request.method !== 'HEAD'
        ? await request.text()
        : undefined,
    });

    // 응답 헤더 복사
    const responseHeaders = new Headers();
    for (const [key, value] of response.headers.entries()) {
      responseHeaders.set(key, value);
    }

    // CORS 헤더 추가
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    return new Response(await response.text(), {
      status: response.status,
      headers: responseHeaders,
    });
  } catch (error) {
    return new Response(JSON.stringify({ error: 'Proxy error', details: error.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' },
    });
  }
}