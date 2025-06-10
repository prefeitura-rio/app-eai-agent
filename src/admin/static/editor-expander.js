/**
 * Editor Expander - Funcionalidade para expandir o editor de texto
 * 
 * Este script permite que o usuário expanda o editor de texto para ocupar
 * a maior parte da tela, melhorando a visualização de prompts longos.
 */
document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const expandButton = document.getElementById('expandButton');
    const promptText = document.getElementById('promptText');
    const editorOverlay = document.getElementById('editorOverlay');
    const closeExpandedEditor = document.getElementById('closeExpandedEditor');
    
    // Verificar se os elementos existem
    if (!expandButton || !promptText || !editorOverlay || !closeExpandedEditor) {
        console.error('Elementos necessários para o expander do editor não encontrados');
        return;
    }
    
    // Função para expandir o editor
    function expandEditor() {
        // Adicionar classe expandido ao editor
        promptText.classList.add('editor-expanded');
        
        // Mostrar overlay e botão de fechar
        editorOverlay.style.display = 'block';
        closeExpandedEditor.style.display = 'block';
        
        // Focar no editor expandido
        promptText.focus();
        
        // Adicionar listener para tecla Escape
        document.addEventListener('keydown', handleEscapeKey);
    }
    
    // Função para recolher o editor
    function collapseEditor() {
        // Remover classe expandido
        promptText.classList.remove('editor-expanded');
        
        // Esconder overlay e botão de fechar
        editorOverlay.style.display = 'none';
        closeExpandedEditor.style.display = 'none';
        
        // Remover listener da tecla Escape
        document.removeEventListener('keydown', handleEscapeKey);
    }
    
    // Handler para tecla Escape
    function handleEscapeKey(e) {
        if (e.key === 'Escape') {
            collapseEditor();
        }
    }
    
    // Adicionar event listeners
    expandButton.addEventListener('click', expandEditor);
    closeExpandedEditor.addEventListener('click', collapseEditor);
    editorOverlay.addEventListener('click', collapseEditor);
    
    // Prevenir que cliques no editor colapsem o editor
    promptText.addEventListener('click', function(e) {
        if (promptText.classList.contains('editor-expanded')) {
            e.stopPropagation();
        }
    });
}); 