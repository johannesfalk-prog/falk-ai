const CACHE_NAME = 'falk-v6';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon.svg',
  'https://cdn.jsdelivr.net/npm/dompurify@3.0.8/dist/purify.min.js',
  'https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js',
  'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) return caches.delete(key);
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  // Ignorera favicon-förfrågningar om de saknas
  if (event.request.url.includes('favicon.ico')) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        return cached || new Response('', { status: 200, headers: { 'Content-Type': 'image/x-icon' } });
      })
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) return cachedResponse;

      return fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseToCache));
        }
        return networkResponse;
      }).catch(() => {
        if (event.request.mode === 'navigate') {
          return caches.match('/index.html');
        }
        return new Response(JSON.stringify({ error: "Offline" }), {
          status: 503,
          headers: new Headers({ 'Content-Type': 'application/json' })
        });
      });
    })
  );
});
