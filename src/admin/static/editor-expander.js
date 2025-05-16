/**
 * Editor Expander - Funcionalidade para expandir o editor de prompt
 * 
 * Este script adiciona a capacidade de expandir o editor de prompts 
 * ao clicar no botão expandir, tornando mais fácil a edição e visualização.
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
    let supportEmail = null;
    
    // Função para inicializar a funcionalidade
    function initialize() {
        // Encontra os elementos necessários
        editor = document.getElementById('promptText');
        overlay = document.getElementById('editorOverlay');
        closeButton = document.getElementById('closeExpandedEditor');
        expandButton = document.getElementById('expandButton');
        supportEmail = document.querySelector('.support-email');
        
        if (!editor || !overlay || !closeButton || !expandButton) {
            console.error('Elementos necessários não encontrados');
            return;
        }
        
        // Salva a altura original
        originalHeight = editor.style.height || getComputedStyle(editor).height;
        editorContainer = editor.closest('.position-relative');
        
        // Remove o evento de duplo clique no editor para evitar conflitos
        // e adiciona apenas ao botão expandir
        expandButton.addEventListener('click', function(e) {
            e.preventDefault();
            expandEditor(e);
        });
        
        closeButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            collapseEditor();
        });
        
        overlay.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
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
            
            // Certifica que o overlay cobre toda a página
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            
            // Oculta temporariamente o texto de suporte para não aparecer sobre o editor
            if (supportEmail) {
                supportEmail.style.visibility = 'hidden';
                supportEmail.style.opacity = '0';
            }
            
            // Aplica classes ao overlay primeiro para criar efeito de fade
            overlay.classList.add('active');
            
            // Pequeno timeout para garantir a transição suave
            setTimeout(() => {
                // Aplica a classe ao editor
                editor.classList.add('expanded');
                
                // Exibe o botão de fechar
                closeButton.style.display = 'flex';
                
                // Ajusta posição do botão de fechar baseado no tamanho atual do editor
                const editorRect = editor.getBoundingClientRect();
                closeButton.style.top = (editorRect.top - 25) + 'px';
                closeButton.style.right = (window.innerWidth - editorRect.right - 25) + 'px';
                
                // Desabilita o scroll do corpo da página
                document.body.style.overflow = 'hidden';
                
                // Atualiza estado
                isExpanded = true;
                
                // Foca o editor para facilitar a digitação imediata
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
            
            // Remove classes na ordem correta para animação suave
            editor.classList.remove('expanded');
            
            // Primeiro escondemos o botão fechar
            closeButton.style.display = 'none';
            
            // Depois removemos o overlay (com um pequeno atraso para transição)
            setTimeout(() => {
                overlay.classList.remove('active');
                
                // Restaura o scroll do corpo da página
                document.body.style.overflow = 'auto';
                
                // Restaura a visibilidade do texto de suporte
                if (supportEmail) {
                    supportEmail.style.visibility = 'visible';
                    supportEmail.style.opacity = '0.8';
                }
                
                // Atualiza estado
                isExpanded = false;
                
                // Restaura o conteúdo e a posição do cursor
                editor.value = content;
                editor.selectionStart = selectionStart;
                editor.selectionEnd = selectionEnd;
                
                // Garantir que a página faz scroll até o editor
                editor.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 150);
        }
    }
    
    // Inicializa quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        // Espera um pouco para garantir que outros scripts tenham carregado
        setTimeout(initialize, 300);
    });
})(); 