/**
 * Service Worker para cache de arquivos estáticos
 *
 * Este service worker gerencia o cache de recursos estáticos para
 * melhorar o desempenho e permitir o uso offline.
 */

const CACHE_NAME = "admin-panel-cache-v1";
const CACHE_WHITELIST = [CACHE_NAME];

// Recursos a serem cacheados inicialmente
const INITIAL_CACHED_RESOURCES = [
  "/eai-agent/admin/static/app.js",
  "/eai-agent/admin/static/agent-types.js",
  "/eai-agent/admin/static/editor-expander.js",
  "/eai-agent/admin/static/style.css",
  "/eai-agent/admin/static/cache-buster.js",
];

// Instalação do Service Worker
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(INITIAL_CACHED_RESOURCES);
      })
      .then(() => {
        // Força a ativação imediata, sem esperar pela atualização da página
        return self.skipWaiting();
      })
  );
});

// Ativação do Service Worker
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            // Remove caches antigos que não estão na whitelist
            if (CACHE_WHITELIST.indexOf(cacheName) === -1) {
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        // Assume o controle de todas as páginas abertas
        return self.clients.claim();
      })
  );
});

// Interceptação de requisições fetch
self.addEventListener("fetch", (event) => {
  // Apenas para recursos da pasta admin/static
  if (event.request.url.includes("/admin/static/")) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Clona a resposta
          const responseClone = response.clone();

          // Abre o cache
          caches.open(CACHE_NAME).then((cache) => {
            // Adiciona a resposta ao cache
            cache.put(event.request, responseClone);
          });

          return response;
        })
        .catch(() => {
          // Se falhar, tenta usar o cache
          return caches.match(event.request);
        })
    );
  }
});
