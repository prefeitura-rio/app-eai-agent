// Elementos DOM principais
const loginForm = document.getElementById('loginForm');
const adminPanel = document.getElementById('adminPanel');
const alertArea = document.getElementById('alertArea');
const agentTypeSelect = document.getElementById('agentType');
const loadingIndicator = document.getElementById('loadingIndicator');
const contentArea = document.getElementById('contentArea');
const promptText = document.getElementById('promptText');
const authorInput = document.getElementById('author');
const reasonInput = document.getElementById('reason');
const updateAgentsCheckbox = document.getElementById('updateAgents');
const saveButton = document.getElementById('saveButton');
const copyButton = document.getElementById('copyButton');
const historyList = document.getElementById('historyList');
const logoutBtn = document.getElementById('logoutBtn');
const errorMsg = document.getElementById('errorMsg');
const themeToggle = document.getElementById('themeToggle');

// Variáveis globais
let currentToken = localStorage.getItem('adminToken');
let currentPromptId = null;
let promptsData = []; // Array para armazenar todos os dados dos prompts
let currentTheme = localStorage.getItem('theme') || 'light';
let isHistoryItemView = false; // Nova variável para rastrear se estamos visualizando um item do histórico

// Configuração inicial
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando painel admin');
    
    // Inicializar tema
    initTheme();
    
    // Verificar se já existe um token salvo
    if (currentToken) {
        showAdminPanel();
        // Não chamar loadData() aqui - será chamado após carregamento dos tipos de agentes
    }
    
    // Event Listeners
    loginForm.addEventListener('submit', handleLogin);
    agentTypeSelect.addEventListener('change', loadData);
    saveButton.addEventListener('click', handleSavePrompt);
    logoutBtn.addEventListener('click', handleLogout);
    copyButton.addEventListener('click', handleCopyPrompt);
    
    // Adicionar listener para o toggle de tema
    if (themeToggle) {
        themeToggle.addEventListener('change', switchTheme);
    }
    
    // Adicionar event listener global para itens de histórico
    document.addEventListener('click', function(e) {
        console.log('Clique detectado em:', e.target);
        
        // Procurar pelo elemento .history-item mais próximo
        const historyItem = e.target.closest('.history-item');
        if (historyItem && historyItem.dataset.promptId) {
            console.log('Clique em item do histórico detectado via delegação de eventos');
            console.log('Prompt ID:', historyItem.dataset.promptId);
            console.log('Versão:', historyItem.dataset.version);
            
            e.preventDefault();
            e.stopPropagation();
            selectPromptById(historyItem.dataset.promptId);
        }
    });
    
    // Adicionar listener para o evento de tipos de agentes carregados
    document.addEventListener('agentTypesLoaded', function(e) {
        console.log('Evento agentTypesLoaded recebido:', e.detail);
        
        // Aguardar um momento para garantir que o valor do select esteja estável
        setTimeout(() => {
            console.log('Iniciando carregamento de dados após tipos de agentes carregados');
            loadData();
        }, 100);
    });
    
    // Adicionar debug específico para o historyList
    if (historyList) {
        console.log('Elemento historyList encontrado:', historyList);
        historyList.addEventListener('click', function(e) {
            console.log('Clique direto em historyList');
        });
    } else {
        console.error('Elemento historyList não encontrado no DOM');
    }
});

// Funções de tema
function initTheme() {
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeToggle) {
            themeToggle.checked = true;
        }
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        if (themeToggle) {
            themeToggle.checked = false;
        }
    }
}

function switchTheme(e) {
    if (e.target.checked) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        currentTheme = 'dark';
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        localStorage.setItem('theme', 'light');
        currentTheme = 'light';
    }
}

// Funções de UI
function showAdminPanel() {
    document.querySelector('.login-container').classList.add('d-none');
    adminPanel.classList.remove('d-none');
}

function showLoading() {
    loadingIndicator.classList.remove('d-none');
    contentArea.classList.add('d-none');
}

function hideLoading() {
    loadingIndicator.classList.add('d-none');
    contentArea.classList.remove('d-none');
}

function showAlert(message, type = 'success') {
    alertArea.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" 
                   onclick="this.parentElement.remove()"></button>
        </div>
    `;
}

// Manipuladores de eventos
function handleLogin(e) {
    e.preventDefault();
    
    const token = document.getElementById('token').value.trim();
    if (!token) {
        errorMsg.textContent = 'Por favor, insira um token válido';
        errorMsg.classList.remove('d-none');
        return;
    }
    
    // Testar token fazendo uma requisição de verificação
    fetch('/api/v1/system-prompt/history?agent_type=agentic_search', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        if (!response.ok && response.status !== 400) {
            // Se não for erro 400 (que pode ser só não ter prompts ainda)
            throw new Error('Token inválido');
        }
        return response.json();
    })
    .then(data => {
        // Token válido, salvar e mostrar painel
        localStorage.setItem('adminToken', token);
        currentToken = token;
        errorMsg.classList.add('d-none');
        showAdminPanel();
        
        // Disparar o evento para carregar tipos de agentes
        document.dispatchEvent(new Event('agentTypesReady'));
        
        // Não chamar loadData() aqui - será chamado após carregamento dos tipos de agentes
    })
    .catch(error => {
        errorMsg.textContent = 'Token inválido ou erro de conexão';
        errorMsg.classList.remove('d-none');
        console.error('Erro de autenticação:', error);
    });
}

function handleLogout() {
    localStorage.removeItem('adminToken');
    location.reload();
}

function handleSavePrompt() {
    const agentType = agentTypeSelect.value;
    const newPrompt = promptText.value;
    
    // Verificar se o prompt está vazio
    if (!newPrompt.trim()) {
        showAlert('O conteúdo do prompt não pode estar vazio', 'danger');
        return;
    }
    
    // Criar e mostrar modal de confirmação antes de salvar
    const saveConfirmModal = createConfirmationModal();
    document.body.appendChild(saveConfirmModal);
    
    // Obter referências aos elementos do modal
    const modalElement = document.getElementById('saveConfirmModal');
    const authorModalInput = document.getElementById('modalAuthorInput');
    const reasonModalInput = document.getElementById('modalReasonInput');
    const confirmSaveBtn = document.getElementById('confirmSaveBtn');
    
    // Sempre iniciar os campos vazios para forçar o preenchimento
    authorModalInput.value = '';
    reasonModalInput.value = '';
    
    // Mostrar o modal
    const modal = new bootstrap.Modal(modalElement);
    modal.show();
    
    // Adicionar evento ao botão de confirmação
    confirmSaveBtn.addEventListener('click', function() {
        // Verificar se os campos obrigatórios foram preenchidos
        if (!authorModalInput.value.trim()) {
            document.getElementById('authorModalFeedback').classList.remove('d-none');
            return;
        } else {
            document.getElementById('authorModalFeedback').classList.add('d-none');
        }
        
        if (!reasonModalInput.value.trim()) {
            document.getElementById('reasonModalFeedback').classList.remove('d-none');
            return;
        } else {
            document.getElementById('reasonModalFeedback').classList.add('d-none');
        }
        
        // Atualizar os valores dos inputs principais com os valores do modal
        authorInput.value = authorModalInput.value.trim();
        reasonInput.value = reasonModalInput.value.trim();
        
        // Fechar o modal
        modal.hide();
        
        // Remover o modal do DOM depois que for fechado
        modalElement.addEventListener('hidden.bs.modal', function () {
            saveConfirmModal.remove();
            
            // Continuar com o processo de salvamento
            proceedWithSave(agentType, newPrompt, authorInput.value, reasonInput.value);
        }, { once: true });
    });
}

function createConfirmationModal() {
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'saveConfirmModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'saveConfirmModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    modalDiv.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="saveConfirmModalLabel">Confirmar alterações</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                </div>
                <div class="modal-body">
                    <p>Preencha as informações abaixo para salvar as alterações:</p>
                    
                    <div class="mb-3">
                        <label for="modalAuthorInput" class="form-label">Autor <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="modalAuthorInput" required>
                        <div id="authorModalFeedback" class="invalid-feedback d-none">
                            O nome do autor é obrigatório.
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="modalReasonInput" class="form-label">Motivo da Atualização <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="modalReasonInput" required>
                        <div id="reasonModalFeedback" class="invalid-feedback d-none">
                            O motivo da atualização é obrigatório.
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="confirmSaveBtn">Salvar alterações</button>
                </div>
            </div>
        </div>
    `;
    
    return modalDiv;
}

function proceedWithSave(agentType, newPrompt, author, reason) {
    showLoading();
    
    const metadata = {
        author: author,
        reason: reason
    };
    
    const updateAgents = updateAgentsCheckbox.checked;
    
    // Criar payload
    const payload = {
        new_prompt: newPrompt,
        agent_type: agentType,
        update_agents: updateAgents,
        metadata: metadata
    };
    
    // Enviar requisição
    apiRequest('POST', '/api/v1/system-prompt', payload)
        .then(response => {
            hideLoading();
            showAlert(response.message || 'Prompt atualizado com sucesso!');
            loadData(); // Recarregar dados
        })
        .catch(error => {
            hideLoading();
            showAlert(error.message || 'Erro ao atualizar prompt', 'danger');
        });
}

function handleCopyPrompt() {
    // Usar API Clipboard moderna se disponível
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(promptText.value)
            .then(() => {
                showCopyFeedback();
            })
            .catch(err => {
                console.error('Erro ao copiar com Clipboard API:', err);
                // Fallback para o método antigo
                fallbackCopy();
            });
    } else {
        // Método antigo para navegadores que não suportam a API Clipboard
        fallbackCopy();
    }
}

function fallbackCopy() {
    try {
        promptText.select();
        const success = document.execCommand('copy');
        if (success) {
            showCopyFeedback();
        } else {
            console.error('Falha ao executar execCommand("copy")');
            showAlert('Não foi possível copiar o texto. Tente selecionar e copiar manualmente.', 'warning');
        }
    } catch (err) {
        console.error('Erro ao usar método de cópia alternativo:', err);
        showAlert('Não foi possível copiar o texto. Tente selecionar e copiar manualmente.', 'warning');
    }
}

function showCopyFeedback() {
    // Efeito visual feedback
    const originalText = copyButton.innerHTML;
    copyButton.innerHTML = '<i class="bi bi-check2 me-1"></i>Copiado!';
    copyButton.classList.add('btn-success');
    copyButton.classList.remove('btn-outline-secondary');
    
    setTimeout(() => {
        copyButton.innerHTML = originalText;
        copyButton.classList.remove('btn-success');
        copyButton.classList.add('btn-outline-secondary');
    }, 2000);
}

// Funções de dados
function loadData() {
    showLoading();
    const agentType = agentTypeSelect.value;
    
    // Resetar o estado de visualização de histórico
    isHistoryItemView = false;
    authorInput.disabled = false;
    reasonInput.disabled = false;
    
    // Remover classe visual de visualização
    authorInput.classList.remove('viewing-history');
    reasonInput.classList.remove('viewing-history');
    
    // Limpar campos de autor e motivo ao iniciar
    authorInput.value = '';
    reasonInput.value = '';
    
    // Carregar dados em paralelo
    Promise.all([
        // Carregar prompt atual (pode falhar se não existir)
        apiRequest('GET', `/api/v1/system-prompt?agent_type=${agentType}`)
            .catch(error => {
                // Se for erro de "não encontrado", retornamos um objeto vazio
                if (error.message && error.message.includes('Nenhum system prompt encontrado')) {
                    console.log('Nenhum prompt encontrado ainda, preparando para criar o primeiro');
                    return { prompt: '', is_new: true };
                }
                throw error; // Para outros erros, propagamos
            }),
        // Carregar histórico (pode estar vazio)
        apiRequest('GET', `/api/v1/system-prompt/history?agent_type=${agentType}`)
            .catch(error => {
                // Se falhar, retornamos lista vazia
                console.warn('Erro ao carregar histórico:', error);
                return { prompts: [] };
            })
    ])
    .then(([currentData, historyData]) => {
        // Log dos dados recebidos para depuração
        console.log('Dados atuais:', currentData);
        console.log('Dados do histórico:', historyData);
        
        // Preencher dados do prompt atual
        promptText.value = currentData.prompt || '';
        currentPromptId = currentData.prompt_id;
        
        // Metadados iniciais são mantidos vazios para forçar preenchimento ao salvar
        // Os campos já foram limpos no início da função loadData
        
        // Se for um prompt novo, mostramos mensagem de orientação
        if (currentData.is_new) {
            showAlert('Nenhum prompt configurado para este tipo de agente. Adicione o texto do prompt e clique em Salvar para criar o primeiro.', 'info');
        }
        
        // Armazenar prompt atual no promptsData para fácil acesso
        if (currentData.prompt && currentData.prompt_id && !historyData.prompts.some(p => p.prompt_id === currentData.prompt_id)) {
            // Adicionar o prompt atual ao array caso ainda não esteja lá
            historyData.prompts.unshift({
                prompt_id: currentData.prompt_id,
                version: currentData.version || 1,
                content: currentData.prompt,
                is_active: true,
                created_at: currentData.created_at || new Date().toISOString(),
                metadata: {}
            });
        }
        
        // Salvar os dados dos prompts globalmente para acesso fácil
        promptsData = historyData.prompts || [];
        
        // Limpar e preencher o histórico
        renderHistory(promptsData);
        
        hideLoading();
    })
    .catch(error => {
        hideLoading();
        showAlert('Erro ao carregar dados: ' + (error.message || 'Erro desconhecido'), 'danger');
        console.error('Erro ao carregar dados:', error);
    });
}

function renderHistory(prompts) {
    historyList.innerHTML = '';
    
    if (prompts.length === 0) {
        historyList.innerHTML = '<div class="text-muted p-3">Nenhum histórico disponível</div>';
        return;
    }
    
    prompts.forEach(prompt => {
        const isActive = prompt.is_active;
        const dateObj = new Date(prompt.created_at);
        
        // Ajustando para o fuso horário do Brasil (UTC-3)
        const brazilDate = new Date(dateObj);
        brazilDate.setHours(brazilDate.getHours() - 3);
        
        // Formatando data usando a data já ajustada para UTC-3
        const options = { 
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric' 
        };
        const date = brazilDate.toLocaleDateString('pt-BR', options);
        
        // Obtendo horas e minutos da data já ajustada
        const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        });
        
        // E usamos para formatar a data
        const timeStr = timeFormatter.format(brazilDate);
        
        // Obter texto para preview - tentamos diferentes propriedades
        let previewText = '(Sem conteúdo)';
        if (typeof prompt.content === 'string') {
            previewText = prompt.content.replace(/\n/g, ' ').trim();
        }
        
        const item = document.createElement('div');
        item.className = `history-item ${prompt.prompt_id === currentPromptId ? 'active' : ''}`;
        item.dataset.promptId = prompt.prompt_id;
        item.dataset.version = prompt.version;
        
        // Adaptando para corresponder ao layout visualizado na captura de tela
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span class="history-version">v${prompt.version}</span>
                <span class="history-date">${date} ${timeStr}</span>
            </div>
            <div class="my-2">
                ${isActive ? '<span class="badge bg-success me-1">Ativo</span>' : ''}
                ${prompt.metadata && prompt.metadata.author ? 
                    `<span class="metadata-badge">Autor: ${prompt.metadata.author}</span>` : ''}
                ${prompt.metadata && prompt.metadata.reason ? 
                    `<span class="metadata-badge">${prompt.metadata.reason}</span>` : ''}
            </div>
            <div class="history-preview" title="${previewText.length > 150 ? previewText.substring(0, 150) + '...' : previewText}">
                ${previewText.substring(0, 100)}${previewText.length > 100 ? '...' : ''}
            </div>
        `;
        
        // Readicionando o listener de clique diretamente, além da delegação de eventos
        item.addEventListener('click', function(e) {
            console.log('Clique direto no item do histórico:', prompt.prompt_id);
            selectPromptById(prompt.prompt_id);
            e.preventDefault();
            e.stopPropagation();
        });
        
        historyList.appendChild(item);
    });
    
    // Adiciona uma verificação para debugging
    console.log(`Renderizados ${prompts.length} itens no histórico`);
    document.querySelectorAll('.history-item').forEach(item => {
        console.log(`Item: v${item.dataset.version}, ID: ${item.dataset.promptId}`);
    });
}

// Nova função completamente reescrita para selecionar por ID
function selectPromptById(promptId) {
    console.log('Iniciando seleção de prompt por ID:', promptId);
    if (!promptId) {
        console.error('ID de prompt inválido:', promptId);
        showAlert('ID de prompt inválido', 'danger');
        return;
    }
    
    showLoading();
    
    // Usar o novo endpoint para buscar o prompt pelo ID
    const url = `/api/v1/system-prompt/by-id/${promptId}`;
    console.log('Buscando conteúdo completo na URL:', url);
    
    // Fazer requisição diretamente, sem passar por funções intermediárias
    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log(`Resposta da API: ${response.status} ${response.statusText}`);
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Dados recebidos da API:', data);
        
        // Atualizar o conteúdo do editor
        promptText.value = data.prompt || '';
        currentPromptId = promptId;
        
        // Encontrar o prompt no array local para obter metadados adicionais (apenas para visualização)
        const localPrompt = promptsData.find(p => p.prompt_id === promptId);
        if (localPrompt && localPrompt.metadata) {
            authorInput.value = localPrompt.metadata.author || '(Não informado)';
            reasonInput.value = localPrompt.metadata.reason || '(Não informado)';
        }
        
        // Atualizar a classe ativa nos itens do histórico
        updateActiveHistoryItem(promptId);
        
        hideLoading();
    })
    .catch(error => {
        console.error('Erro ao buscar dados completos do prompt:', error);
        
        // Tentar usar dados locais como fallback
        const localPrompt = promptsData.find(p => p.prompt_id === promptId);
        if (localPrompt && localPrompt.content) {
            console.log('Usando dados locais como fallback:', localPrompt.content);
            promptText.value = localPrompt.content;
            currentPromptId = promptId;
            
            if (localPrompt.metadata) {
                authorInput.value = localPrompt.metadata.author || '(Não informado)';
                reasonInput.value = localPrompt.metadata.reason || '(Não informado)';
            }
            
            updateActiveHistoryItem(promptId);
            showAlert('Usando dados locais do prompt (podem estar incompletos)', 'warning');
        } else {
            showAlert('Erro ao carregar dados do prompt: ' + error.message, 'danger');
        }
        
        hideLoading();
    });
}

// Função auxiliar para atualizar o item ativo no histórico
function updateActiveHistoryItem(promptId) {
    // Remover ativo de todos os itens
    const items = historyList.querySelectorAll('.history-item');
    items.forEach(item => item.classList.remove('active'));
    
    // Encontrar e marcar o novo item ativo
    const activeItem = historyList.querySelector(`.history-item[data-prompt-id="${promptId}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
    }
    
    // Definir que estamos visualizando um item do histórico
    isHistoryItemView = true;
    
    // Desabilitar edição dos campos de autor e motivo quando estiver visualizando histórico
    authorInput.disabled = true;
    reasonInput.disabled = true;
    
    // Adicionar classe visual para facilitar a percepção de que está em modo de visualização
    authorInput.classList.add('viewing-history');
    reasonInput.classList.add('viewing-history');
}

// Helper para fazer requisições API
function apiRequest(method, url, data = null) {
    console.log(`Fazendo requisição ${method} para ${url}`);
    
    const options = {
        method: method,
        headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    console.log('Opções da requisição:', { 
        url, 
        method: options.method,
        headers: { ...options.headers, 'Authorization': 'Bearer ***' } 
    });
    
    return fetch(url, options)
        .then(response => {
            console.log(`Resposta da API: ${response.status} ${response.statusText}`);
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Caso token seja inválido, fazer logout
                    handleLogout();
                    throw new Error('Token inválido ou expirado');
                }
                
                // Tentar obter detalhes do erro
                return response.json().then(errorData => {
                    console.error('Erro da API:', errorData);
                    throw new Error(`Erro ${response.status}: ${errorData.detail || response.statusText}`);
                }).catch(err => {
                    // Se não conseguir parsear JSON
                    throw new Error(`Erro ${response.status}: ${response.statusText}`);
                });
            }
            
            return response.json();
        });
} 