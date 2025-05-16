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
    let originalEditorParent = null;
    
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
        
        // Salva a altura original e o elemento pai
        originalHeight = editor.style.height || getComputedStyle(editor).height;
        editorContainer = editor.closest('.position-relative');
        originalEditorParent = editor.parentNode;
        
        // Configura o overlay e botão de fechar
        overlay.style.display = 'none';
        closeButton.style.display = 'none';
        
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
            try {
                // Previne comportamento padrão
                if (event) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                
                // Guarda o conteúdo e a posição do cursor
                const content = editor.value;
                const selectionStart = editor.selectionStart;
                const selectionEnd = editor.selectionEnd;
                
                // Oculta temporariamente o texto de suporte
                if (supportEmail) {
                    supportEmail.style.visibility = 'hidden';
                    supportEmail.style.opacity = '0';
                }
                
                // Impede scroll do body
                document.body.classList.add('editor-expanded');
                document.body.style.overflow = 'hidden';
                
                // Move o overlay e botão para o body
                if (!document.body.contains(overlay)) {
                    document.body.appendChild(overlay);
                }
                if (!document.body.contains(closeButton)) {
                    document.body.appendChild(closeButton);
                }
                
                // Configura o overlay
                overlay.style.position = 'fixed';
                overlay.style.top = '0';
                overlay.style.left = '0';
                overlay.style.width = '100vw';
                overlay.style.height = '100vh';
                overlay.style.zIndex = '9998';
                overlay.style.display = 'block';
                
                // Mostra overlay com animação
                setTimeout(() => {
                    overlay.classList.add('active');
                    
                    // Move o editor para o final do body
                    document.body.appendChild(editor);
                    
                    // Configura o editor expandido
                    editor.classList.add('expanded');
                    editor.style.zIndex = '9999';
                    
                    // Configura o botão de fechar
                    closeButton.style.display = 'flex';
                    closeButton.style.zIndex = '10000';
                    closeButton.style.top = '20px';
                    closeButton.style.right = '20px';
                    
                    // Restaura o conteúdo e a posição do cursor
                    editor.value = content;
                    editor.selectionStart = selectionStart;
                    editor.selectionEnd = selectionEnd;
                    
                    // Atualiza estado
                    isExpanded = true;
                    
                    // Foca o editor
                    setTimeout(() => {
                        editor.focus();
                    }, 50);
                }, 10);
            } catch (error) {
                console.error('Erro ao expandir editor:', error);
            }
        }
    }
    
    // Função para colapsar o editor
    function collapseEditor() {
        if (isExpanded) {
            try {
                // Guarda o conteúdo e a posição do cursor
                const content = editor.value;
                const selectionStart = editor.selectionStart;
                const selectionEnd = editor.selectionEnd;
                
                // Remove classe expandida do editor
                editor.classList.remove('expanded');
                editor.style.zIndex = '';
                
                // Esconde o botão de fechar
                closeButton.style.display = 'none';
                
                // Inicia animação de fade-out do overlay
                overlay.classList.remove('active');
                
                // Dá tempo para a animação acontecer
                setTimeout(() => {
                    // Restaura o editor para sua posição original
                    if (originalEditorParent && editor.parentNode !== originalEditorParent) {
                        originalEditorParent.appendChild(editor);
                    }
                    
                    // Esconde completamente o overlay
                    overlay.style.display = 'none';
                    
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
                    
                    // Pequeno timeout para garantir que o editor esteja pronto
                    setTimeout(() => {
                        editor.selectionStart = selectionStart;
                        editor.selectionEnd = selectionEnd;
                        editor.focus();
                    }, 10);
                    
                    // Garantir que a página faz scroll até o editor
                    setTimeout(() => {
                        editor.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }, 100);
                }, 200);
            } catch (error) {
                console.error('Erro ao colapsar editor:', error);
                // Recuperação de erro: força o estado normal
                if (originalEditorParent) {
                    originalEditorParent.appendChild(editor);
                }
                editor.classList.remove('expanded');
                closeButton.style.display = 'none';
                overlay.classList.remove('active');
                overlay.style.display = 'none';
                document.body.style.overflow = 'auto';
                document.body.classList.remove('editor-expanded');
                isExpanded = false;
            }
        }
    }
    
    // Inicializa quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        // Espera um pouco para garantir que outros scripts tenham carregado
        setTimeout(initialize, 300);
    });
})(); 