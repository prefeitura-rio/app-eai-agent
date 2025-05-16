/**
 * Editor Expander - Funcionalidade para expandir o editor de prompt
 * 
 * Este script adiciona a capacidade de expandir o editor de prompts 
 * ao clicar nele, tornando mais fácil a edição e visualização.
 */

(function() {
    // Elementos do DOM
    let editor = null;
    let overlay = null;
    let closeButton = null;
    let isExpanded = false;
    
    // Função para inicializar a funcionalidade
    function initialize() {
        // Encontra os elementos necessários
        editor = document.getElementById('promptText');
        overlay = document.getElementById('editorOverlay');
        closeButton = document.getElementById('closeExpandedEditor');
        
        if (!editor || !overlay || !closeButton) {
            console.error('Elementos necessários não encontrados');
            return;
        }
        
        // Adiciona os eventos
        editor.addEventListener('click', toggleEditorExpansion);
        editor.addEventListener('focus', handleEditorFocus);
        closeButton.addEventListener('click', collapseEditor);
        overlay.addEventListener('click', collapseEditor);
        
        // Adiciona evento para tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isExpanded) {
                collapseEditor();
            }
        });
    }
    
    // Função para alternar entre expandido e normal
    function toggleEditorExpansion(event) {
        if (!isExpanded) {
            expandEditor();
        }
    }
    
    // Função para expandir o editor
    function expandEditor() {
        if (!isExpanded) {
            editor.classList.add('expanded');
            overlay.classList.add('active');
            closeButton.style.display = 'flex';
            isExpanded = true;
            
            // Foca o editor para facilitar a digitação imediata
            editor.focus();
            
            // Desabilita o scroll do corpo da página
            document.body.style.overflow = 'hidden';
        }
    }
    
    // Função para colapsar o editor
    function collapseEditor() {
        if (isExpanded) {
            editor.classList.remove('expanded');
            overlay.classList.remove('active');
            closeButton.style.display = 'none';
            isExpanded = false;
            
            // Restaura o scroll do corpo da página
            document.body.style.overflow = 'auto';
        }
    }
    
    // Função para lidar com o foco no editor
    function handleEditorFocus() {
        // Expande somente no primeiro foco
        if (!isExpanded) {
            expandEditor();
        }
    }
    
    // Inicializa quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        // Espera um pouco para garantir que outros scripts tenham carregado
        setTimeout(initialize, 100);
    });
})(); 