const C='asikurt-v18',F=['./','index.html','manifest.json','icon-192.png','icon-512.png'];
self.addEventListener('install',e=>{e.waitUntil((async()=>{
  const c=await caches.open(C);
  await Promise.all(F.map(async path=>{
    const url=new URL(path,self.registration.scope).href;
    const response=await fetch(url,{cache:'reload'});
    if(!response.ok)throw new Error(`Önbellek dosyası alınamadı: ${path}`);
    await c.put(url,response);
  }));
  await self.skipWaiting();
})())});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(k=>Promise.all(k.filter(x=>x.startsWith('asikurt-')&&x!==C).map(x=>caches.delete(x)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{const r=e.request,u=new URL(r.url);if(r.method!=='GET'||u.origin!==location.origin||!F.some(x=>new URL(x,self.registration.scope).pathname===u.pathname))return;
e.respondWith(fetch(r.url,{cache:'no-store'}).then(async res=>{if(res.ok)await caches.open(C).then(c=>c.put(r.url,res.clone()));return res}).catch(async error=>{
  const cached=await caches.match(r.url)||await caches.match(new URL('index.html',self.registration.scope).href);
  if(cached)return cached;
  throw error;
}))});
