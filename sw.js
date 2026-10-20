const CACHE_NAME = "falk-v25";
const STATIC_ASSETS = [
  "/",
  "/index.html",
  "/manifest.json",
  "/icon.svg",
  "/js/purify.min.js",
  "/js/marked.min.js",
  "/js/supabase.js"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(async (cache) => {
      for (const asset of STATIC_ASSETS) {
        try {
          await cache.add(asset);
        } catch (err) {
          console.warn("Asset-varning vid install:", asset, err);
        }
      }
    })
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(
      keys.map((key) => key !== CACHE_NAME && caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener("message", (event) => {
  if (event.data && event.data.type === "SKIP_WAITING") {
    self.skipWaiting();
  }
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  event.respondWith(
    (async () => {
      try {
        // Nätverk först för index.html/roten för att alltid garantera nyaste UI-koden
        if (event.request.mode === "navigate" || event.request.url.endsWith("/index.html")) {
          const networkResponse = await fetch(event.request);
          if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(event.request, networkResponse.clone());
            return networkResponse;
          }
        }
      } catch (e) {
        // Fallback till cache om offline
      }

      const cachedResponse = await caches.match(event.request);
      if (cachedResponse) return cachedResponse;

      try {
        const networkResponse = await fetch(event.request);
        if (networkResponse && networkResponse.status === 200 && networkResponse.type === "basic") {
          const cache = await caches.open(CACHE_NAME);
          cache.put(event.request, networkResponse.clone());
        }
        return networkResponse;
      } catch (networkError) {
        if (event.request.mode === "navigate") {
          const fallbackIndex = await caches.match("/index.html") || await caches.match("/");
          if (fallbackIndex) return fallbackIndex;
        }

        return new Response(
          "<html><body><h2>FALK Offline Mode</h2><p>Applikationen laddades utan sparad cache.</p></body></html>",
          {
            status: 503,
            statusText: "Service Unavailable",
            headers: { "Content-Type": "text/html; charset=utf-8" }
          }
        );
      }
    })()
  );
});
