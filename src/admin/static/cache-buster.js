/**
 * Cache Buster - Evita problemas com cache de arquivos estáticos
 * 
 * Este script adiciona um parâmetro de versão aos arquivos CSS e JS
 * para forçar o navegador a baixar as versões mais recentes dos arquivos.
 */
(function() {
    // Gera um timestamp ou versão aleatória
    const version = new Date().getTime();
    
    // Função para adicionar parâmetro de versão a todos os links CSS e scripts
    function addVersionToAssets() {
        // Adiciona versão aos arquivos CSS
        const cssLinks = document.querySelectorAll('link[rel="stylesheet"]');
        cssLinks.forEach(link => {
            // Apenas para arquivos locais (não para CDNs)
            if (link.href && link.href.includes('/admin/static/')) {
                link.href = updateQueryStringParameter(link.href, 'v', version);
            }
        });
        
        // Adiciona versão aos arquivos JavaScript
        const scripts = document.querySelectorAll('script');
        scripts.forEach(script => {
            // Apenas para arquivos locais (não para CDNs)
            if (script.src && script.src.includes('/admin/static/')) {
                script.src = updateQueryStringParameter(script.src, 'v', version);
            }
        });
    }
    
    // Função para adicionar ou atualizar parâmetro de consulta em uma URL
    function updateQueryStringParameter(uri, key, value) {
        // Remove hash ou fragmento
        const i = uri.indexOf('#');
        const hash = i === -1 ? '' : uri.substr(i);
        uri = i === -1 ? uri : uri.substr(0, i);
        
        // Verifica se já existe um parâmetro de consulta
        const re = new RegExp("([?&])" + key + "=.*?(&|$)", "i");
        const separator = uri.indexOf('?') !== -1 ? "&" : "?";
        
        if (uri.match(re)) {
            // Atualiza valor existente
            return uri.replace(re, '$1' + key + "=" + value + '$2') + hash;
        } else {
            // Adiciona novo parâmetro
            return uri + separator + key + "=" + value + hash;
        }
    }
    
    // Adiciona evento para aplicar a versão aos assets quando o DOM estiver carregado
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addVersionToAssets);
    } else {
        addVersionToAssets();
    }
})(); 