/* App shell only. Auth, chat, feedback and all /api responses bypass this cache. */
const CACHE = 'inside-shell-v1';
self.addEventListener('install', event => {
  event.waitUntil((async () => {
    const cache = await caches.open(CACHE);
    const response = await fetch('/shell-assets.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('Offline shell manifest is unavailable');
    await cache.addAll(await response.json());
  })());
});
self.addEventListener('activate', event => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) if (name.startsWith('inside-shell-') && name !== CACHE) await caches.delete(name);
    await self.clients.claim();
  })());
});
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  if (event.request.method !== 'GET' || url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;
  if (event.request.mode === 'navigate') {
    event.respondWith(fetch(event.request).catch(async () => {
      const cached = await (await caches.open(CACHE)).match('/');
      return cached || new Response('Reconnect once to save the app for offline use.', { status: 503 });
    }));
  } else if (url.pathname.startsWith('/assets/') || /^\/(icon.*\.(svg|png)|manifest.webmanifest)$/.test(url.pathname)) {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      const saved = await cache.match(event.request);
      if (saved) return saved;
      const response = await fetch(event.request);
      if (response.ok) await cache.put(event.request, response.clone());
      return response;
    })());
  }
});
