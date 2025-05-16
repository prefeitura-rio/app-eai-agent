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
    let expandButton = null;
    let isExpanded = false;
    let originalHeight = null;
    let editorContainer = null;
    
    // Função para inicializar a funcionalidade
    function initialize() {
        // Encontra os elementos necessários
        editor = document.getElementById('promptText');
        overlay = document.getElementById('editorOverlay');
        closeButton = document.getElementById('closeExpandedEditor');
        expandButton = document.getElementById('expandButton');
        
        if (!editor || !overlay || !closeButton) {
            console.error('Elementos necessários não encontrados');
            return;
        }
        
        // Salva a altura original
        originalHeight = editor.style.height || getComputedStyle(editor).height;
        editorContainer = editor.closest('.position-relative');
        
        // Remove o evento de duplo clique no editor para evitar conflitos
        // e adiciona apenas ao botão expandir
        if (expandButton) {
            expandButton.addEventListener('click', function(e) {
                e.preventDefault();
                expandEditor();
            });
        }
        
        closeButton.addEventListener('click', function(e) {
            e.stopPropagation(); // Evita propagação
            collapseEditor();
        });
        
        overlay.addEventListener('click', function(e) {
            e.stopPropagation(); // Evita propagação
            collapseEditor();
        });
        
        // Adiciona evento para tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isExpanded) {
                collapseEditor();
            }
        });
    }
    
    // Função para expandir o editor
    function expandEditor(event) {
        if (!isExpanded) {
            // Previne comportamento padrão
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            // Guarda a posição de scroll atual
            const scrollPosition = window.scrollY;
            
            // Desabilita o scroll do corpo da página
            document.body.style.overflow = 'hidden';
            
            // Aplica as classes
            editor.classList.add('expanded');
            overlay.classList.add('active');
            
            // Exibe o botão de fechar
            closeButton.style.display = 'flex';
            
            // Atualiza estado
            isExpanded = true;
            
            // Foca o editor para facilitar a digitação imediata
            setTimeout(() => {
                editor.focus();
                // Restaura a posição de scroll
                window.scrollTo(0, scrollPosition);
            }, 50);
        }
    }
    
    // Função para colapsar o editor
    function collapseEditor() {
        if (isExpanded) {
            // Guarda o conteúdo e a posição do cursor
            const content = editor.value;
            const selectionStart = editor.selectionStart;
            const selectionEnd = editor.selectionEnd;
            
            // Remove classes
            editor.classList.remove('expanded');
            overlay.classList.remove('active');
            
            // Esconde o botão
            closeButton.style.display = 'none';
            
            // Restaura o scroll do corpo da página
            document.body.style.overflow = 'auto';
            
            // Atualiza estado
            isExpanded = false;
            
            // Restaura o conteúdo e a posição do cursor
            setTimeout(() => {
                editor.value = content;
                editor.selectionStart = selectionStart;
                editor.selectionEnd = selectionEnd;
                
                // Garantir que a página faz scroll até o editor
                editor.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 50);
        }
    }
    
    // Inicializa quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        // Espera um pouco para garantir que outros scripts tenham carregado
        setTimeout(initialize, 300);
    });
})(); 