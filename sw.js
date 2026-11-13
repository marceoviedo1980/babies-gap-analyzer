const CACHE_NAME = 'babies-pwa-v12';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Firebase / Firestore: siempre red primero
  if (event.request.url.includes('firestore.googleapis.com') ||
      event.request.url.includes('firebase') ||
      event.request.url.includes('gstatic.com/firebasejs')) {
    event.respondWith(fetch(event.request).catch(() => new Response('', {status:503})));
    return;
  }
  // CDN scripts: red primero, caché como fallback
  if (event.request.url.includes('cdn.jsdelivr.net') ||
      event.request.url.includes('cdnjs.cloudflare.com')) {
    event.respondWith(
      fetch(event.request)
        .then(res => { const cl = res.clone(); caches.open(CACHE_NAME).then(c => c.put(event.request,cl)); return res; })
        .catch(() => caches.match(event.request))
    );
    return;
  }
  // Assets locales: caché primero
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
