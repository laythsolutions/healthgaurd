/**
 * HealthGuard Service Worker
 *
 * Strategies:
 *   - restaurant grade pages (/restaurants/*) — cache-first for offline browsing
 *   - advisory/recall pages              — stale-while-revalidate (fresh data preferred)
 *   - QR code pages (/qr/*)             — cache-first (quick scan in low-connectivity)
 *   - API calls                          — network-only (never serve stale API data)
 *   - static assets (_next/static/*)    — cache-first with long TTL
 *
 * Cache names are versioned so old caches are pruned on activation.
 */

const CACHE_VERSION = 'v1';
const STATIC_CACHE  = `static-${CACHE_VERSION}`;
const PAGE_CACHE    = `pages-${CACHE_VERSION}`;

const STATIC_EXTENSIONS = ['.js', '.css', '.woff2', '.woff', '.ttf', '.png', '.svg', '.ico'];

// -----------------------------------------------------------------
// Install — pre-cache the shell
// -----------------------------------------------------------------
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) =>
      cache.addAll([
        '/',
        '/restaurants',
        '/advisories',
        '/recalls',
        '/offline',
      ]).catch(() => { /* offline page may not exist yet */ })
    )
  );
  self.skipWaiting();
});

// -----------------------------------------------------------------
// Activate — prune stale caches
// -----------------------------------------------------------------
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== STATIC_CACHE && k !== PAGE_CACHE)
          .map((k) => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// -----------------------------------------------------------------
// Fetch — route to the right strategy
// -----------------------------------------------------------------
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET and cross-origin requests
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  // API calls — always network-only
  if (url.pathname.startsWith('/api/')) return;

  // Next.js HMR / dev tools — skip
  if (url.pathname.startsWith('/_next/webpack-hmr')) return;

  // Static assets — cache-first
  if (
    url.pathname.startsWith('/_next/static/') ||
    STATIC_EXTENSIONS.some((ext) => url.pathname.endsWith(ext))
  ) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // Restaurant grade pages and QR scans — cache-first (offline friendly)
  if (
    url.pathname.startsWith('/restaurants/') ||
    url.pathname.startsWith('/qr/')
  ) {
    event.respondWith(cacheFirst(request, PAGE_CACHE));
    return;
  }

  // Advisory and recall pages — stale-while-revalidate
  if (
    url.pathname.startsWith('/advisories') ||
    url.pathname.startsWith('/recalls')
  ) {
    event.respondWith(staleWhileRevalidate(request, PAGE_CACHE));
    return;
  }

  // Everything else — network with offline fallback
  event.respondWith(networkWithOfflineFallback(request));
});

// -----------------------------------------------------------------
// Strategy helpers
// -----------------------------------------------------------------

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return offlineFallback(request);
  }
}

async function staleWhileRevalidate(request, cacheName) {
  const cache  = await caches.open(cacheName);
  const cached = await cache.match(request);

  const networkPromise = fetch(request).then((response) => {
    if (response.ok) cache.put(request, response.clone());
    return response;
  }).catch(() => null);

  return cached || (await networkPromise) || offlineFallback(request);
}

async function networkWithOfflineFallback(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(PAGE_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    return cached || offlineFallback(request);
  }
}

function offlineFallback(request) {
  if (request.headers.get('accept')?.includes('text/html')) {
    return caches.match('/offline') || new Response(
      '<h1>You are offline</h1><p>Check your connection and try again.</p>',
      { headers: { 'Content-Type': 'text/html' } }
    );
  }
  return new Response('Offline', { status: 503 });
}
