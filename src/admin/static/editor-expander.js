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
    
    // Debug para verificar se encontrou os elementos
    console.log("Elementos encontrados:", {
        expandButton: !!expandButton,
        closeButton: !!closeButton,
        editorOverlay: !!editorOverlay,
        promptEditor: !!promptEditor
    });
    
    if (expandButton && closeButton && editorOverlay && promptEditor) {
        // Função para expandir o editor
        expandButton.addEventListener('click', function(e) {
            console.log("Botão expandir clicado");
            e.preventDefault();
            e.stopPropagation();
            
            // Adicionar classes necessárias
            document.body.classList.add('editor-expanded');
            editorOverlay.classList.add('active');
            
            // Aplicar estilos de expansão
            promptEditor.classList.add('expanded');
            promptEditor.style.position = 'fixed';
            promptEditor.style.top = '50%';
            promptEditor.style.left = '50%';
            promptEditor.style.transform = 'translate(-50%, -50%)';
            promptEditor.style.width = '90%';
            promptEditor.style.height = '80%';
            promptEditor.style.zIndex = '1001';
            promptEditor.style.fontSize = '16px';
            promptEditor.style.padding = '20px';
            promptEditor.style.boxShadow = 'var(--glass-shadow)';
            promptEditor.style.backgroundColor = 'var(--card-bg)';
            promptEditor.style.backdropFilter = 'blur(10px)';
            
            // Mostrando o overlay e o botão de fechar
            editorOverlay.style.display = 'block';
            closeButton.style.display = 'flex';
            
            // Salvar a posição atual do cursor após a expansão
            setTimeout(() => {
                promptEditor.focus();
                const startPos = promptEditor.selectionStart;
                const endPos = promptEditor.selectionEnd;
                promptEditor.setSelectionRange(startPos, endPos);
            }, 100);
        });
        
        // Função para fechar o editor expandido
        function closeExpandedEditor() {
            console.log("Fechando editor expandido");
            
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
            promptEditor.style.backgroundColor = '';
            promptEditor.style.backdropFilter = '';
            
            // Ocultando o overlay e o botão de fechar
            editorOverlay.style.display = 'none';
            closeButton.style.display = 'none';
            
            // Devolver o foco ao editor e restaurar a posição do cursor após contração
            setTimeout(() => {
                promptEditor.focus();
                promptEditor.setSelectionRange(startPos, endPos);
            }, 100);
        }
        
        // Atribuir manipuladores de eventos para fechar o editor
        closeButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            closeExpandedEditor();
        });
        
        editorOverlay.addEventListener('click', closeExpandedEditor);
        
        // Fechar com a tecla ESC
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && document.body.classList.contains('editor-expanded')) {
                closeExpandedEditor();
            }
        });
        
        // Adicionar efeito de animação ao expandir/contrair
        promptEditor.style.transition = 'all 0.3s ease-in-out';
    } else {
        console.error("Alguns elementos necessários não foram encontrados para o editor-expander");
    }
}); 