// Service Worker for Mahjong PWA
// Cache-first for static assets, network-first for API calls

const CACHE_NAME = 'mahjong-v1';
const STATIC_ASSETS = [
    '/game',
    '/static/styles/game.css',
    '/static/game/main.js',
    '/static/game/js/gameStore.js',
    '/static/game/js/gameActions.js',
    '/static/game/js/tileDisplay.js',
    '/static/game/js/claimsHandler.js',
    '/static/game/js/aiTurnHandler.js',
    '/static/game/js/celebrationScreen.js',
    '/static/game/js/bugReport.js',
    '/static/game/js/auth.js',
    '/static/game/js/statsScreen.js',
    '/static/img/tiles/tileset.png',
    '/static/audio/dingdong.mp3',
    '/static/manifest.json',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
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
