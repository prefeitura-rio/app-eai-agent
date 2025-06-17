/**
 * Editor Expander - Funcionalidade para expandir o editor de texto
 * 
 * Este script permite que o usuário expanda o editor de texto para ocupar
 * a maior parte da tela, melhorando a visualização de prompts longos.
 */
document.addEventListener('DOMContentLoaded', function() {
    const expandButton = document.getElementById('expandButton');
    const closeButton = document.getElementById('closeExpandedEditor');
    const editorOverlay = document.getElementById('editorOverlay');
    const promptEditor = document.getElementById('promptText');
    
    if (expandButton && closeButton && editorOverlay && promptEditor) {
        // Função para expandir o editor
        expandButton.addEventListener('click', function() {
            // Adicionar classes necessárias
            document.body.classList.add('editor-expanded');
            editorOverlay.classList.add('active');
            promptEditor.classList.add('expanded');
            
            // Salvar a posição atual do cursor
            const startPos = promptEditor.selectionStart;
            const endPos = promptEditor.selectionEnd;
            
            // Aplicar estilos de expansão
            promptEditor.style.position = 'fixed';
            promptEditor.style.top = '50%';
            promptEditor.style.left = '50%';
            promptEditor.style.transform = 'translate(-50%, -50%)';
            promptEditor.style.width = '80%';
            promptEditor.style.height = '70%';
            promptEditor.style.zIndex = '1001';
            promptEditor.style.fontSize = '16px';
            promptEditor.style.padding = '20px';
            promptEditor.style.boxShadow = '0 0 30px rgba(0, 0, 0, 0.3)';
            
            // Mostrando o overlay e o botão de fechar
            editorOverlay.style.display = 'block';
            closeButton.style.display = 'flex';
            
            // Devolver o foco ao editor e restaurar a posição do cursor
            promptEditor.focus();
            promptEditor.setSelectionRange(startPos, endPos);
        });
        
        // Função para fechar o editor expandido
        function closeExpandedEditor() {
            // Salvar a posição atual do cursor
            const startPos = promptEditor.selectionStart;
            const endPos = promptEditor.selectionEnd;
            
            // Remover estilos de expansão
            document.body.classList.remove('editor-expanded');
            editorOverlay.classList.remove('active');
            promptEditor.classList.remove('expanded');
            
            promptEditor.style.position = '';
            promptEditor.style.top = '';
            promptEditor.style.left = '';
            promptEditor.style.transform = '';
            promptEditor.style.width = '';
            promptEditor.style.height = '';
            promptEditor.style.zIndex = '';
            promptEditor.style.fontSize = '';
            promptEditor.style.padding = '';
            promptEditor.style.boxShadow = '';
            
            // Ocultando o overlay e o botão de fechar
            editorOverlay.style.display = '';
            closeButton.style.display = '';
            
            // Devolver o foco ao editor e restaurar a posição do cursor
            promptEditor.focus();
            promptEditor.setSelectionRange(startPos, endPos);
        }
        
        // Atribuir manipuladores de eventos para fechar o editor
        closeButton.addEventListener('click', closeExpandedEditor);
        editorOverlay.addEventListener('click', closeExpandedEditor);
        
        // Fechar com a tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.body.classList.contains('editor-expanded')) {
                closeExpandedEditor();
            }
        });
        
        // Adicionar efeito de animação ao expandir/contrair
        promptEditor.style.transition = 'all 0.3s ease-in-out';
    }
}); 