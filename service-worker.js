const CACHE_VERSION = '8.5.2';
const CACHE_NAME = `btc-cycle-compass-${CACHE_VERSION}`;
const STABLE_ASSETS = [
  './bitcoin-compass-base.png',
  './bitcoin-compass-needle.png'
];

function isNetworkFirst(url) {
  return (
    url.pathname.endsWith('/index.html') ||
    url.pathname === '/' ||
    url.pathname.endsWith('/data/live.json') ||
    url.pathname.endsWith('/manifest.json')
  );
}

function isStableImage(url) {
  return (
    STABLE_ASSETS.some((asset) => url.pathname.endsWith(asset.replace('./', '/'))) ||
    url.pathname.endsWith('.png')
  );
}

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STABLE_ASSETS))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.map((key) => caches.delete(key)));
      await clients.claim();
    })()
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) {
    return;
  }

  if (isNetworkFirst(url)) {
    event.respondWith(
      (async () => {
        try {
          const networkResponse = await fetch(request, { cache: 'no-store' });
          const cache = await caches.open(CACHE_NAME);
          cache.put(request, networkResponse.clone());
          return networkResponse;
        } catch (error) {
          const cachedResponse = await caches.match(request, { ignoreSearch: false });
          if (cachedResponse) {
            return cachedResponse;
          }
          throw error;
        }
      })()
    );
    return;
  }

  if (isStableImage(url)) {
    event.respondWith(
      (async () => {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
          return cachedResponse;
        }
        const networkResponse = await fetch(request);
        const cache = await caches.open(CACHE_NAME);
        cache.put(request, networkResponse.clone());
        return networkResponse;
      })()
    );
    return;
  }

  event.respondWith(
    (async () => {
      try {
        return await fetch(request);
      } catch (error) {
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
          return cachedResponse;
        }
        throw error;
      }
    })()
  );
});
