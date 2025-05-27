/**
 * Service Worker para controle de cache
 * 
 * Este service worker facilita o gerenciamento de cache dos recursos estáticos,
 * garantindo que o navegador sempre carregue a versão mais recente.
 */

// Nome do cache
const CACHE_NAME = 'admin-static-cache-v1';

// Lista de recursos que serão cacheados
const STATIC_RESOURCES = [
  '/admin/static/style.css',
  '/admin/static/app.js',
  '/admin/static/agent-types.js',
  '/admin/static/favicon.ico'
];

// Instalação do service worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        // Adiciona timestamp para forçar download de recursos atualizados
        const urlsWithTimestamp = STATIC_RESOURCES.map(url => {
          return url + '?v=' + new Date().getTime();
        });
        return cache.addAll(urlsWithTimestamp);
      })
  );
});

// Ativação do service worker
self.addEventListener('activate', event => {
  // Limpa caches antigos
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptação de requisições fetch
self.addEventListener('fetch', event => {
  // Apenas para recursos da pasta admin/static
  if (event.request.url.includes('/admin/static/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Clona a resposta
          const responseClone = response.clone();
          
          // Abre o cache
          caches.open(CACHE_NAME)
            .then(cache => {
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