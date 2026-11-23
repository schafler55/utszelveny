// The site root used to be the web app itself, with a service worker covering the whole site.
// The app now lives in app/ with its own service worker. This one replaces the old root worker
// and removes itself, so the landing page is always loaded fresh from the network.
// (The old worker's cache is cleared by the app's own worker in app/.)
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    await self.registration.unregister();
    for (const c of await self.clients.matchAll({type: "window"})) c.navigate(c.url);
  })());
});
