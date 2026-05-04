// Service Worker for Mahjong PWA
// Cache-first for static assets, network-first for API calls
// Paths are relative to service worker scope

const CACHE_NAME = 'mahjong-v2';

// Detect if running in Capacitor (local) mode vs server mode
// In Capacitor, web root = static/, so paths don't have /static/ prefix
const isCapacitor = self.location.protocol === 'capacitor:' || !self.location.pathname.startsWith('/static');
const prefix = isCapacitor ? '' : '/static';

const STATIC_ASSETS = [
    `${prefix}/game/index.html`,
    `${prefix}/styles/game.css`,
    `${prefix}/game/main.js`,
    `${prefix}/game/js/gameStore.js`,
    `${prefix}/game/js/gameActions.js`,
    `${prefix}/game/js/tileDisplay.js`,
    `${prefix}/game/js/claimsHandler.js`,
    `${prefix}/game/js/aiTurnHandler.js`,
    `${prefix}/game/js/celebrationScreen.js`,
    `${prefix}/game/js/bugReport.js`,
    `${prefix}/game/js/auth.js`,
    `${prefix}/game/js/statsScreen.js`,
    `${prefix}/img/tiles/tileset.png`,
    `${prefix}/audio/dingdong.mp3`,
    `${prefix}/manifest.json`,
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS).catch(err => {
                console.warn('SW: Failed to cache some assets:', err);
            });
        })
    );
    self.skipWaiting();
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
            );
        })
    );
    self.clients.claim();
});

self.addEventListener('fetch', (event) => {
    const url = new URL(event.request.url);

    // Network-first for API calls and WebSocket
    if (url.pathname.startsWith('/api/') || url.pathname === '/ws' || url.pathname === '/env.js') {
        event.respondWith(
            fetch(event.request).catch(() => caches.match(event.request))
        );
        return;
    }

    // Cache-first for static assets
    event.respondWith(
        caches.match(event.request).then((cached) => {
            return cached || fetch(event.request).then((response) => {
                // Cache successful GET responses
                if (event.request.method === 'GET' && response.status === 200) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
                }
                return response;
            });
        })
    );
});
