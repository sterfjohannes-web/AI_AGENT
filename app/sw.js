const C="r1";self.addEventListener("install",e=>e.waitUntil(caches.open(C).then(c=>c.addAll(["./","index.html","icon.svg"]))));
self.addEventListener("fetch",e=>{const u=e.request.url;
if(u.includes("report.json"))e.respondWith(fetch(e.request).then(r=>{const x=r.clone();caches.open(C).then(c=>c.put(e.request,x));return r}).catch(()=>caches.match(e.request)));
else e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))});
