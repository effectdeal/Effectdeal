// No caching of private API data, documents or authenticated pages.
self.addEventListener('install',()=>self.skipWaiting());
self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));
self.addEventListener('fetch',event=>{if(event.request.mode==='navigate')event.respondWith(fetch(event.request).catch(()=>new Response('<!doctype html><html lang="cs"><meta name="viewport" content="width=device-width"><h1>EFFECT DEAL</h1><p>Připojte se k internetu a obnovte stránku.</p></html>',{headers:{'Content-Type':'text/html;charset=utf-8'}})))});
