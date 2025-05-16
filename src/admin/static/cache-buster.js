/**
 * Cache Buster - Previne o uso de cache desatualizado em arquivos estáticos
 * 
 * Este script adiciona um parâmetro de versão (timestamp) às URLs de
 * recursos estáticos para forçar o navegador a carregar a versão mais recente
 */

(function() {
    // Versão baseada no timestamp atual
    const version = new Date().getTime();
    
    // Função para adicionar versão aos recursos estáticos
    function addVersionToStaticResources() {
        // Processa todos os links CSS
        document.querySelectorAll('link[rel="stylesheet"]').forEach(link => {
            if (link.href.includes('/admin/static/')) {
                link.href = updateQueryStringParameter(link.href, 'v', version);
            }
        });
        
        // Processa todos os scripts
        document.querySelectorAll('script[src]').forEach(script => {
            if (script.src.includes('/admin/static/')) {
                script.src = updateQueryStringParameter(script.src, 'v', version);
            }
        });
        
        // Processa imagens e outros recursos
        document.querySelectorAll('img[src]').forEach(img => {
            if (img.src.includes('/admin/static/')) {
                img.src = updateQueryStringParameter(img.src, 'v', version);
            }
        });
    }
    
    // Função para atualizar ou adicionar um parâmetro à URL
    function updateQueryStringParameter(uri, key, value) {
        // Remove qualquer parâmetro existente
        const re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
        const separator = uri.indexOf('?') !== -1 ? "&" : "?";
        
        if (uri.match(re)) {
            return uri.replace(re, '$1' + key + "=" + value + '$2');
        } else {
            return uri + separator + key + "=" + value;
        }
    }
    
    // Executa quando o DOM estiver carregado
    document.addEventListener('DOMContentLoaded', addVersionToStaticResources);
})(); 