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

// Elementos DOM para Configuração

const memoryBlocksText = document.getElementById('memoryBlocks');
const toolsInput = document.getElementById('tools');
const modelNameInput = document.getElementById('modelName');
const embeddingNameInput = document.getElementById('embeddingName');
const authorCfgInput = document.getElementById('authorCfg');
const reasonCfgInput = document.getElementById('reasonCfg');
const updateAgentsCfgCheckbox = document.getElementById('updateAgentsCfg');
const saveConfigButton = document.getElementById('saveConfigButton');
const resetAllButton = document.getElementById('resetAllButton');
const deleteTestsBtn = document.getElementById('deleteTestsBtn');

// Variáveis globais
let currentToken = localStorage.getItem('adminToken');
let currentPromptId = null;
let currentConfigId = null;
let promptsData = []; // Array para armazenar todos os dados dos prompts
let configsData = []; // Array para armazenar todos os dados das configurações
let unifiedHistoryData = []; // Array para o histórico unificado
let currentTheme = localStorage.getItem('theme') || 'light';
let isHistoryItemView = false; // Nova variável para rastrear se estamos visualizando um item do histórico

// API base URL - ajustar de acordo com o ambiente
const API_BASE_URL = 'https://services.staging.app.dados.rio/eai-agent';

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
        
        // Não interceptar cliques em editores/inputs para permitir seleção de texto
        if (e.target.matches('.prompt-editor, #memoryBlocks, #tools, input[type="text"], textarea') || 
            e.target.closest('.prompt-editor, #memoryBlocks, #tools')) {
            return; // Permitir comportamento padrão
        }
        
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
            // Garantir que a interface esteja corretamente exibida
            checkPromptInterface();
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
    
    // Verificar interface ao carregar a página
    window.addEventListener('load', function() {
        setTimeout(checkPromptInterface, 500);
    });



    // Listener botão salvar config
    if (saveConfigButton) {
        saveConfigButton.addEventListener('click', handleSaveConfig);
    }

    if (resetAllButton) {
        resetAllButton.addEventListener('click', handleResetAll);
    }

    if (deleteTestsBtn) {
        deleteTestsBtn.addEventListener('click', handleDeleteTestAgents);
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
    fetch(`${API_BASE_URL}/api/v1/system-prompt/history?agent_type=agentic_search`, {
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
    apiRequest('POST', `${API_BASE_URL}/api/v1/system-prompt`, payload)
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
    
    // Carregar todos os dados em paralelo
    Promise.all([
        // Carregar prompt atual
        apiRequest('GET', `${API_BASE_URL}/api/v1/system-prompt?agent_type=${agentType}`)
            .catch(error => {
                if (error.message && error.message.includes('Nenhum system prompt encontrado')) {
                    return { prompt: '', is_new: true };
                }
                throw error;
            }),
        // Carregar configuração atual
        apiRequest('GET', `${API_BASE_URL}/api/v1/agent-config?agent_type=${agentType}`)
            .catch(err => ({ memory_blocks: '', tools: [], model_name: '', embedding_name: '' })),
        // Carregar histórico de prompts
        apiRequest('GET', `${API_BASE_URL}/api/v1/system-prompt/history?agent_type=${agentType}`)
            .catch(error => {
                console.warn('Erro ao carregar histórico de prompts:', error);
                return { prompts: [] };
            }),
        // Carregar histórico de configurações
        apiRequest('GET', `${API_BASE_URL}/api/v1/agent-config/history?agent_type=${agentType}`)
            .catch(() => ({ configs: [] }))
    ])
    .then(([currentPromptData, currentConfigData, promptHistoryData, configHistoryData]) => {
        console.log('Dados carregados:', { currentPromptData, currentConfigData, promptHistoryData, configHistoryData });
        
        // Preencher dados do prompt atual
        promptText.value = currentPromptData.prompt || '';
        currentPromptId = currentPromptData.prompt_id;
        
        // Preencher dados da configuração atual
        memoryBlocksText.value = JSON.stringify(currentConfigData.memory_blocks || [], null, 2);
        toolsInput.value = (currentConfigData.tools || []).join(', ');
        modelNameInput.value = currentConfigData.model_name || '';
        embeddingNameInput.value = currentConfigData.embedding_name || '';
        currentConfigId = currentConfigData.config_id;
        
        // Armazenar dados
        promptsData = promptHistoryData.prompts || [];
        configsData = configHistoryData.configs || [];
        
        // Criar histórico unificado com novo padrão de versionamento
        unifiedHistoryData = createUnifiedHistory(promptsData, configsData);
        
        // Renderizar histórico unificado
        renderUnifiedHistory(unifiedHistoryData);
        
        hideLoading();
    })
    .catch(error => {
        hideLoading();
        showAlert('Erro ao carregar dados: ' + (error.message || 'Erro desconhecido'), 'danger');
        console.error('Erro ao carregar dados:', error);
    });
}

// Função para criar o histórico unificado com novo padrão de versionamento
function createUnifiedHistory(prompts, configs) {
    const unified = [];
    
    // Processar prompts
    prompts.forEach(prompt => {
        unified.push({
            id: prompt.prompt_id,
            type: 'prompt',
            version: generateVersionString(prompt.created_at, prompt.version),
            originalVersion: prompt.version,
            created_at: prompt.created_at,
            is_active: prompt.is_active,
            metadata: prompt.metadata,
            content: prompt.content,
            preview: typeof prompt.content === 'string' ? 
                prompt.content.replace(/\n/g, ' ').trim().substring(0, 100) : 
                '(Sem conteúdo)'
        });
    });
    
    // Processar configurações
    configs.forEach(config => {
        unified.push({
            id: config.config_id,
            type: 'config',
            version: generateVersionString(config.created_at, config.version),
            originalVersion: config.version,
            created_at: config.created_at,
            is_active: config.is_active,
            metadata: config.metadata,
            tools: config.tools,
            model_name: config.model_name,
            embedding_name: config.embedding_name,
            preview: `Tools: ${(config.tools || []).join(', ')}`
        });
    });
    
    // Ordenar por data de criação (mais recente primeiro)
    unified.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    
    return unified;
}

// Função para gerar o padrão de versionamento eai-<YYYY>-<MM>-<DD>-v<X>
function generateVersionString(dateStr, version) {
    const date = new Date(dateStr);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `eai-${year}-${month}-${day}-v${version}`;
}

// Função para renderizar o histórico unificado
function renderUnifiedHistory(historyItems) {
    historyList.innerHTML = '';
    
    if (historyItems.length === 0) {
        historyList.innerHTML = '<div class="text-muted p-3">Nenhum histórico disponível</div>';
        return;
    }
    
    historyItems.forEach(item => {
        const dateObj = new Date(item.created_at);
        const brazilDate = new Date(dateObj);
        brazilDate.setHours(brazilDate.getHours() - 3);
        
        const date = brazilDate.toLocaleDateString('pt-BR', {
            day: '2-digit', 
            month: '2-digit', 
            year: 'numeric'
        });
        
        const timeStr = new Intl.DateTimeFormat('pt-BR', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }).format(brazilDate);
        
        // Determinar se está ativo baseado no tipo
        const isActive = (item.type === 'prompt' && item.id === currentPromptId) ||
                        (item.type === 'config' && item.id === currentConfigId);
        
        const historyItem = document.createElement('div');
        historyItem.className = `history-item ${isActive ? 'active' : ''}`;
        historyItem.dataset.itemId = item.id;
        historyItem.dataset.itemType = item.type;
        historyItem.dataset.version = item.originalVersion;
        
        // Ícone e cor baseados no tipo
        const typeInfo = item.type === 'prompt' ? 
            { icon: 'bi-pencil-square', label: 'System Prompt', color: 'primary' } :
            { icon: 'bi-gear', label: 'Configurações', color: 'info' };
        
        historyItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span class="history-version">
                    <i class="bi ${typeInfo.icon} me-1 text-${typeInfo.color}"></i>
                    ${item.version}
                </span>
                <span class="history-date">${date} ${timeStr}</span>
            </div>
            <div class="my-2">
                <span class="badge bg-${typeInfo.color} me-1">${typeInfo.label}</span>
                ${item.is_active ? '<span class="badge bg-success me-1">Ativo</span>' : ''}
                ${item.metadata && item.metadata.author ? 
                    `<span class="metadata-badge">Autor: ${item.metadata.author}</span>` : ''}
                ${item.metadata && item.metadata.reason ? 
                    `<span class="metadata-badge">${item.metadata.reason}</span>` : ''}
            </div>
            <div class="history-preview" title="${item.preview}">
                ${item.preview.substring(0, 100)}${item.preview.length > 100 ? '...' : ''}
            </div>
        `;
        
        // Adicionar listener de clique
        historyItem.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (item.type === 'prompt') {
                selectPromptById(item.id);
            } else {
                selectConfigById(item.id);
            }
        });
        
        historyList.appendChild(historyItem);
    });
    
    console.log(`Renderizados ${historyItems.length} itens no histórico unificado`);
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
    const url = `${API_BASE_URL}/api/v1/system-prompt/by-id/${promptId}`;
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
    // Atualizar o item ativo no histórico unificado
    currentPromptId = promptId;
    
    // Re-renderizar o histórico para refletir o novo item ativo
    unifiedHistoryData = createUnifiedHistory(promptsData, configsData);
    renderUnifiedHistory(unifiedHistoryData);
    
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

// Função para garantir que a interface do prompt seja exibida corretamente
function checkPromptInterface() {
    const contentArea = document.getElementById('contentArea');
    const promptSection = document.querySelector('.prompt-section');
    
    if (contentArea && promptSection) {
        console.log("Verificando interface do prompt");
        
        // Verificar se o contentArea está visível
        if (contentArea.classList.contains('d-none')) {
            console.log("contentArea está oculto, removendo classe d-none");
            contentArea.classList.remove('d-none');
        }
    } else {
        console.error("Elementos da interface não encontrados");
    }
}

// Verificar a interface quando os tipos de agentes forem carregados
document.addEventListener('agentTypesReady', function() {
    // Aguardar um momento para garantir que a interface seja carregada
    setTimeout(checkPromptInterface, 1000);
});

// Verificar novamente quando a página for totalmente carregada
window.addEventListener('load', function() {
    setTimeout(checkPromptInterface, 1500);
});





function handleSaveConfig() {
    const agentType = agentTypeSelect.value;

    // Validar JSON dos memory blocks antes de prosseguir
    let memoryBlocksValue = memoryBlocksText.value.trim();
    let memoryBlocksArray = null;
    if (memoryBlocksValue) {
        try {
            memoryBlocksArray = JSON.parse(memoryBlocksValue);
        } catch (e) {
            showAlert('Memory blocks devem ser JSON válido.', 'danger');
            return;
        }
    }

    // Criar e mostrar modal de confirmação antes de salvar
    const saveConfirmModal = createConfigConfirmationModal();
    document.body.appendChild(saveConfirmModal);
    
    // Obter referências aos elementos do modal
    const modalElement = document.getElementById('saveConfigConfirmModal');
    const authorModalInput = document.getElementById('modalAuthorConfigInput');
    const reasonModalInput = document.getElementById('modalReasonConfigInput');
    const confirmSaveBtn = document.getElementById('confirmSaveConfigBtn');
    
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
            document.getElementById('authorConfigModalFeedback').classList.remove('d-none');
            return;
        } else {
            document.getElementById('authorConfigModalFeedback').classList.add('d-none');
        }
        
        if (!reasonModalInput.value.trim()) {
            document.getElementById('reasonConfigModalFeedback').classList.remove('d-none');
            return;
        } else {
            document.getElementById('reasonConfigModalFeedback').classList.add('d-none');
        }
        
        // Atualizar os valores dos inputs principais com os valores do modal
        authorCfgInput.value = authorModalInput.value.trim();
        reasonCfgInput.value = reasonModalInput.value.trim();
        
        // Fechar o modal
        modal.hide();
        
        // Remover o modal do DOM depois que for fechado
        modalElement.addEventListener('hidden.bs.modal', function () {
            saveConfirmModal.remove();
            
            // Continuar com o processo de salvamento
            proceedWithConfigSave(agentType, memoryBlocksArray, authorCfgInput.value, reasonCfgInput.value);
        }, { once: true });
    });
}

function createConfigConfirmationModal() {
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'saveConfigConfirmModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'saveConfigConfirmModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    modalDiv.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="saveConfigConfirmModalLabel">Confirmar alterações da configuração</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                </div>
                <div class="modal-body">
                    <p>Preencha as informações abaixo para salvar as alterações da configuração:</p>
                    
                    <div class="mb-3">
                        <label for="modalAuthorConfigInput" class="form-label">Autor <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="modalAuthorConfigInput" required>
                        <div id="authorConfigModalFeedback" class="invalid-feedback d-none">
                            O nome do autor é obrigatório.
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="modalReasonConfigInput" class="form-label">Motivo da Atualização <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="modalReasonConfigInput" required>
                        <div id="reasonConfigModalFeedback" class="invalid-feedback d-none">
                            O motivo da atualização é obrigatório.
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="confirmSaveConfigBtn">Salvar configuração</button>
                </div>
            </div>
        </div>
    `;
    
    return modalDiv;
}

function proceedWithConfigSave(agentType, memoryBlocksArray, author, reason) {
    showLoading();
    
    const payload = {
        agent_type: agentType,
        memory_blocks: memoryBlocksArray,
        tools: toolsInput.value.split(',').map(t => t.trim()).filter(Boolean),
        model_name: modelNameInput.value.trim() || null,
        embedding_name: embeddingNameInput.value.trim() || null,
        update_agents: updateAgentsCfgCheckbox.checked,
        metadata: {
            author: author,
            reason: reason,
        },
    };

    apiRequest('POST', `${API_BASE_URL}/api/v1/agent-config`, payload)
        .then(response => {
            hideLoading();
            showAlert(response.message || 'Configuração salva com sucesso!');
            loadData(); // Recarregar todo o histórico unificado
        })
        .catch(err => {
            hideLoading();
            showAlert(err.message || 'Erro ao salvar configuração', 'danger');
        });
}



function selectConfigById(configId) {
    if (!configId) return;
    showLoading();
    const url = `${API_BASE_URL}/api/v1/agent-config/by-id/${configId}`;

    fetch(url, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) throw new Error(`Erro ${response.status}`);
            return response.json();
        })
        .then(data => {
            memoryBlocksText.value = JSON.stringify(data.memory_blocks || [], null, 2);
            toolsInput.value = (data.tools || []).join(', ');
            modelNameInput.value = data.model_name || '';
            embeddingNameInput.value = data.embedding_name || '';

            currentConfigId = configId;

            updateActiveConfigHistoryItem(configId);
            hideLoading();
        })
        .catch(err => {
            hideLoading();
            showAlert('Erro ao buscar configuração: ' + err.message, 'danger');
        });
}

function updateActiveConfigHistoryItem(configId) {
    // Atualizar o item ativo no histórico unificado
    currentConfigId = configId;
    
    // Re-renderizar o histórico para refletir o novo item ativo
    unifiedHistoryData = createUnifiedHistory(promptsData, configsData);
    renderUnifiedHistory(unifiedHistoryData);
}

// ---------------------- RESET ALL ----------------------
function handleResetAll() {
    const agentType = agentTypeSelect.value;

    if (!confirm('Tem certeza que deseja resetar System Prompt E Configuração do Agente para o padrão? Esta ação criará novas versões e não pode ser desfeita.')) {
        return;
    }

    showLoading();

    const updateAgents = updateAgentsCfgCheckbox.checked;

    const req1 = apiRequest('DELETE', `${API_BASE_URL}/api/v1/system-prompt/reset?agent_type=${agentType}&update_agents=${updateAgents}`);
    const req2 = apiRequest('DELETE', `${API_BASE_URL}/api/v1/agent-config/reset?agent_type=${agentType}&update_agents=${updateAgents}`);

    Promise.allSettled([req1, req2])
        .then(results => {
            hideLoading();
            const err = results.find(r => r.status === 'rejected');
            if (err) {
                showAlert('Erro ao resetar: ' + err.reason, 'danger');
            } else {
                showAlert('System Prompt e Configurações resetados com sucesso!');
                // Recarregar dados
                loadData();
            }
        });
}

// ---------------------- DELETE TEST AGENTS ----------------------
function handleDeleteTestAgents() {
    if (!confirm('Remover TODOS os agentes com tag "test"?')) {
        return;
    }

    showLoading();

    apiRequest('DELETE', `${API_BASE_URL}/api/v1/agents/tests`)
        .then(resp => {
            hideLoading();
            showAlert(resp.message || 'Agentes de teste removidos');
        })
        .catch(err => {
            hideLoading();
            showAlert(err.message || 'Erro ao remover agentes de teste', 'danger');
        });
} 