const CACHE = 'babies-pwa-v6';
const ASSETS = [
  './',
  './index.html',
  './manifest.json'
];
 
// INSTALL
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});
 
// ACTIVATE — elimina caches viejos
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
 
// FETCH — cache-first para assets locales, network-first para Supabase
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  if (e.request.url.includes('supabase')) return;
  if (e.request.url.includes('cdn.jsdelivr.net')) return; // CDN siempre desde red
  e.respondWith(
    caches.match(e.request).then(cached => cached || fetch(e.request))
  );
});
