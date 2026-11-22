const C="utszelveny-v1.2.0";
const FILES=["./","./index.html","./manifest.webmanifest","./icon-192.png","./icon-512.png","./icon-maskable-512.png"];
// A new version installs in the background (cache:"reload" = from the server, not the browser's HTTP cache) and then
// waits: the app asks the user, and "Frissítés" sends "skip". Otherwise it takes over once every ÚtSzelvény tab is closed.
// Saved data (localStorage) is not part of this cache, so an update never touches it.
self.addEventListener("install",e=>{e.waitUntil(caches.open(C).then(c=>c.addAll(FILES.map(f=>new Request(f,{cache:"reload"})))))});
self.addEventListener("message",e=>{if(e.data==="skip")self.skipWaiting()});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x!==C).map(x=>caches.delete(x)))));self.clients.claim()});
// only the app's own files are served from the cache; map tiles go straight to the network (browser HTTP cache)
// ?fresh (the update check, the texts overview page reading index.html) always goes to the network
self.addEventListener("fetch",e=>{const u=new URL(e.request.url);if(u.origin!==self.location.origin||u.searchParams.has("fresh"))return;e.respondWith(caches.match(e.request,{ignoreSearch:true}).then(r=>r||fetch(e.request)))});
