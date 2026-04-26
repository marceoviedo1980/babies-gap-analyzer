const CACHE = 'babies-pwa-v3';

const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png'
];

// INSTALL
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

// ACTIVATE
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE)
            .map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// FETCH (estrategia: stale-while-revalidate)
self.addEventListener('fetch', e => {

  if (e.request.method !== 'GET') return;

  // Ignorar Supabase
  if (e.request.url.includes('supabase')) return;

  e.respondWith(
    caches.match(e.request).then(cached => {

      const fetchPromise = fetch(e.request)
        .then(networkResponse => {
          // Guardar copia actualizada en caché
          return caches.open(CACHE).then(cache => {
            cache.put(e.request, networkResponse.clone());
            return networkResponse;
          });
        })
        .catch(() => cached); // fallback offline

      // Si hay caché → mostrar rápido
      return cached || fetchPromise;
    })
  );
});
