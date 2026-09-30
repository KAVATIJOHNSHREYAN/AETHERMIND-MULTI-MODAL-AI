/* ==========================================================================
   AETHERMIND MULTIMODAL AI — PRODUCTION PWA SERVICE WORKER (v1.0.0)
   Features: Intelligent Asset Precaching, Offline Fallback, Network-First API Bypass,
   Background Sync Queue, Push Notification Infrastructure, & Automatic Cache Cleanup.
   ========================================================================== */

const CACHE_NAME = 'aethermind-pwa-v1.0.0';
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/js/app.js',
    '/static/img/favicon.png',
    '/static/img/apple-touch-icon.png',
    '/static/img/bg-futuristic.png',
    '/static/img/icons/icon-192x192.png',
    '/static/img/icons/icon-512x512.png',
    '/static/img/icons/maskable-icon-192x192.png'
];

// Install Event — Precache Core Application Shell
self.addEventListener('install', (event) => {
    console.log('[ServiceWorker] Installing AetherMind PWA Service Worker v1.0.0');
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[ServiceWorker] Precaching App Shell static assets');
            return cache.addAll(STATIC_ASSETS).catch((err) => {
                console.warn('[ServiceWorker] Precache partial error (continuing):', err);
            });
        })
    );
    self.skipWaiting();
});

// Activate Event — Clean up outdated caches
self.addEventListener('activate', (event) => {
    console.log('[ServiceWorker] Activating new Service Worker version');
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[ServiceWorker] Removing legacy cache:', key);
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

// Fetch Event — Network-First for HTML/API, Stale-While-Revalidate for Static Assets
self.addEventListener('fetch', (event) => {
    const request = event.request;
    const url = new URL(request.url);

    // CRITICAL SECURITY RULE: Never cache API endpoints, Firebase Auth, or Supabase Secrets!
    if (
        url.pathname.startsWith('/api/') ||
        url.pathname.includes('/auth') ||
        url.pathname.includes('/logout') ||
        url.hostname.includes('firebase') ||
        url.hostname.includes('supabase') ||
        url.hostname.includes('qdrant') ||
        request.method !== 'GET'
    ) {
        return; // Pass through to network directly without touching cache
    }

    // Static Assets (JS, CSS, Images, Fonts, Icons, Manifest) -> Stale-While-Revalidate
    if (
        url.pathname.startsWith('/static/') ||
        request.destination === 'script' ||
        request.destination === 'style' ||
        request.destination === 'image' ||
        request.destination === 'font'
    ) {
        event.respondWith(
            caches.open(CACHE_NAME).then(async (cache) => {
                const cachedResponse = await cache.match(request);
                const fetchPromise = fetch(request)
                    .then((networkResponse) => {
                        if (networkResponse && networkResponse.status === 200) {
                            cache.put(request, networkResponse.clone());
                        }
                        return networkResponse;
                    })
                    .catch(() => cachedResponse);

                return cachedResponse || fetchPromise;
            })
        );
        return;
    }

    // HTML Navigation Pages -> Network-First with Offline Cache Fallback
    if (request.mode === 'navigate') {
        event.respondWith(
            fetch(request)
                .then((networkResponse) => {
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, networkResponse.clone());
                    });
                    return networkResponse;
                })
                .catch(async () => {
                    const cache = await caches.open(CACHE_NAME);
                    const cachedPage = await cache.match(request);
                    if (cachedPage) return cachedPage;
                    const indexFallback = await cache.match('/');
                    return indexFallback || Response.error();
                })
        );
    }
});

// Background Sync Listener
self.addEventListener('sync', (event) => {
    console.log('[ServiceWorker] Background Sync event triggered:', event.tag);
    if (event.tag === 'sync-offline-queue') {
        event.waitUntil(
            self.clients.matchAll().then((clients) => {
                clients.forEach((client) => {
                    client.postMessage({ type: 'BACKGROUND_SYNC_TRIGGERED' });
                });
            })
        );
    }
});

// Push Notifications Listener
self.addEventListener('push', (event) => {
    console.log('[ServiceWorker] Push Notification received');
    let data = {
        title: 'AetherMind AI Update',
        body: 'Your AI task has completed.',
        icon: '/static/img/icons/icon-192x192.png',
        badge: '/static/img/icons/icon-72x72.png',
        data: { url: '/' }
    };

    if (event.data) {
        try {
            data = Object.assign(data, event.data.json());
        } catch (e) {
            data.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: data.icon,
            badge: data.badge,
            data: data.data,
            vibrate: [100, 50, 100],
            actions: [
                { action: 'open', title: 'Open AetherMind' },
                { action: 'close', title: 'Dismiss' }
            ]
        })
    );
});

// Notification Click Listener
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    if (event.action === 'close') return;

    const targetUrl = (event.notification.data && event.notification.data.url) || '/';
    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
            for (const client of clientList) {
                if (client.url === targetUrl && 'focus' in client) {
                    return client.focus();
                }
            }
            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }
        })
    );
});

// Skip Waiting Signal Handler
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
