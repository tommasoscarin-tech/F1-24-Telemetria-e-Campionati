const CACHE_NAME = 'f124-pwa-cache-v2';
const STATIC_ASSETS = [
  '/static/styles.css',
  '/static/app.js',
  '/manifest.json'
];
const OFFLINE_URL = '/';

self.addEventListener('install', event => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
  const request = event.request;
  const url = new URL(request.url);

  if (request.method !== 'GET') return;

  // HTML Requests (Network-First, fallback to Offline/Cache)
  if (request.mode === 'navigate' || request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .catch(() => caches.match(OFFLINE_URL))
    );
    return;
  }

  // Static Assets (Cache-First)
  if (STATIC_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(request).then(response => {
        return response || fetch(request).then(netResponse => {
          return caches.open(CACHE_NAME).then(cache => {
            cache.put(request, netResponse.clone());
            return netResponse;
          });
        });
      })
    );
    return;
  }
});

// Background Sync
self.addEventListener('sync', event => {
  if (event.tag === 'sync-telemetry') {
    event.waitUntil(
      // Implement background sync logic here (e.g. read IndexedDB and fetch POST)
      Promise.resolve()
    );
  }
});

// Push Notifications
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : { title: 'F1 Telemetry', body: 'Nuovo aggiornamento.' };
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body,
      icon: '/static/images/icon-192.png'
    })
  );
});

// Notification Click
self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow('/')
  );
});
