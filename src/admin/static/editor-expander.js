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
        
        // Garante que o overlay seja inserido no final do body para cobrir tudo
        document.body.appendChild(overlay);
        // Garante que o botão de fechar seja inserido no final do body
        document.body.appendChild(closeButton);
        
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
            
            // Oculta temporariamente o texto de suporte para não aparecer sobre o editor
            if (supportEmail) {
                supportEmail.style.visibility = 'hidden';
                supportEmail.style.opacity = '0';
            }
            
            // Adiciona classe ao body para impedir scroll
            document.body.classList.add('editor-expanded');
            document.body.style.overflow = 'hidden';
            
            // Configura overlay para cobrir toda a tela
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100vw';
            overlay.style.height = '100vh';
            overlay.style.zIndex = '10004';
            
            // Mostra overlay com animação
            overlay.classList.add('active');
            
            // Guarda o conteúdo e a posição do cursor
            const content = editor.value;
            const selectionStart = editor.selectionStart;
            const selectionEnd = editor.selectionEnd;
            
            // Pequeno timeout para garantir a transição suave
            setTimeout(() => {
                // Configura o editor expandido
                editor.classList.add('expanded');
                editor.style.zIndex = '10005';
                
                // Exibe o botão de fechar
                closeButton.style.display = 'flex';
                closeButton.style.zIndex = '10006';
                closeButton.style.top = '20px';
                closeButton.style.right = '20px';
                
                // Atualiza estado
                isExpanded = true;
                
                // Restaura o conteúdo e a posição do cursor
                editor.value = content;
                editor.selectionStart = selectionStart;
                editor.selectionEnd = selectionEnd;
                
                // Foca o editor para facilitar a digitação
                setTimeout(() => {
                    editor.focus();
                }, 50);
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
                document.body.classList.remove('editor-expanded');
                
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