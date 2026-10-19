const CACHE = 'inside-lab-v1';
const ASSETS = ['/', '/index.html', '/style.css', '/anatomy.css', '/app.mjs', '/model.mjs', '/icon.svg', '/manifest.webmanifest', '/ANATOMY-LICENSE.txt'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(c=>c.addAll(ASSETS)));self.skipWaiting();});
self.addEventListener('activate',event=>event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('inside-lab-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim())));
self.addEventListener('fetch',event=>{
  if(event.request.method!=='GET'||new URL(event.request.url).origin!==self.location.origin)return;
  event.respondWith(fetch(event.request).then(response=>{
    if(response.ok && ASSETS.includes(new URL(event.request.url).pathname)) { const copy=response.clone(); event.waitUntil(caches.open(CACHE).then(cache=>cache.put(event.request,copy))); }
    return response;
  }).catch(()=>caches.match(event.request).then(cached=>cached||new Response('Not available offline',{status:503}))));
});
