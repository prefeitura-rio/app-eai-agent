// Elementos DOM principais
const loginForm = document.getElementById('loginForm');
const adminPanel = document.getElementById('adminPanel');
const alertArea = document.getElementById('alertArea');
const agentTypeSelect = document.getElementById('agentType');
const loadingIndicator = document.getElementById('loadingIndicator');
const contentArea = document.getElementById('contentArea');
const promptText = document.getElementById('promptText');
const updateAgentsCheckbox = document.getElementById('updateAgents');
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
const saveAllButton = document.getElementById('saveAllButton');
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
    saveAllButton.addEventListener('click', handleSaveAll);
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
        if (historyItem) {
            console.log('Clique em item do histórico detectado via delegação de eventos');
            console.log('Item dataset:', historyItem.dataset);
            
            // Evitar duplo processamento - itens unificados são processados pelo listener específico
            if (historyItem.dataset.itemType === 'unified') {
                return;
            }
            
            e.preventDefault();
            e.stopPropagation();
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



    // Listeners botões
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

function handleSaveAll() {
    const agentType = agentTypeSelect.value;
    const newPrompt = promptText.value;
    
    // Verificar se o prompt está vazio
    if (!newPrompt.trim()) {
        showAlert('O conteúdo do prompt não pode estar vazio', 'danger');
        return;
    }
    
    // Validar JSON dos memory blocks
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
    const saveConfirmModal = createUnifiedConfirmationModal();
    document.body.appendChild(saveConfirmModal);
    
    // Obter referências aos elementos do modal
    const modalElement = document.getElementById('saveUnifiedConfirmModal');
    const authorModalInput = document.getElementById('modalAuthorUnifiedInput');
    const reasonModalInput = document.getElementById('modalReasonUnifiedInput');
    const confirmSaveBtn = document.getElementById('confirmSaveUnifiedBtn');
    
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
            document.getElementById('authorUnifiedModalFeedback').classList.remove('d-none');
            return;
        } else {
            document.getElementById('authorUnifiedModalFeedback').classList.add('d-none');
        }
        
        if (!reasonModalInput.value.trim()) {
            document.getElementById('reasonUnifiedModalFeedback').classList.remove('d-none');
            return;
        } else {
            document.getElementById('reasonUnifiedModalFeedback').classList.add('d-none');
        }
        
        // Fechar o modal
        modal.hide();
        
        // Remover o modal do DOM depois que for fechado
        modalElement.addEventListener('hidden.bs.modal', function () {
            saveConfirmModal.remove();
            
            // Continuar com o processo de salvamento unificado
            proceedWithUnifiedSave(
                agentType, 
                newPrompt, 
                memoryBlocksArray, 
                authorModalInput.value.trim(), 
                reasonModalInput.value.trim()
            );
        }, { once: true });
    });
}

function createUnifiedConfirmationModal() {
    const modalDiv = document.createElement('div');
    modalDiv.className = 'modal fade';
    modalDiv.id = 'saveUnifiedConfirmModal';
    modalDiv.tabIndex = '-1';
    modalDiv.setAttribute('aria-labelledby', 'saveUnifiedConfirmModalLabel');
    modalDiv.setAttribute('aria-hidden', 'true');
    
    modalDiv.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="saveUnifiedConfirmModalLabel">Confirmar alterações unificadas</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fechar"></button>
                </div>
                <div class="modal-body">
                    <p>Preencha as informações abaixo para salvar as alterações em <strong>System Prompt E Configurações</strong> como uma única versão:</p>
                    
                    <div class="mb-3">
                        <label for="modalAuthorUnifiedInput" class="form-label">Autor <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="modalAuthorUnifiedInput" required>
                        <div id="authorUnifiedModalFeedback" class="invalid-feedback d-none">
                            O nome do autor é obrigatório.
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="modalReasonUnifiedInput" class="form-label">Motivo da Atualização <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="modalReasonUnifiedInput" required>
                        <div id="reasonUnifiedModalFeedback" class="invalid-feedback d-none">
                            O motivo da atualização é obrigatório.
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="confirmSaveUnifiedBtn">Salvar tudo junto</button>
                </div>
            </div>
        </div>
    `;
    
    return modalDiv;
}

function proceedWithUnifiedSave(agentType, newPrompt, memoryBlocksArray, author, reason) {
    showLoading();
    
    const updateAgents = updateAgentsCheckbox.checked;
    
    // Usar novo endpoint unificado para salvar tudo em uma única versão
    const unifiedPayload = {
        agent_type: agentType,
        prompt_content: newPrompt,
        memory_blocks: memoryBlocksArray,
        tools: toolsInput.value.split(',').map(t => t.trim()).filter(Boolean),
        model_name: modelNameInput.value.trim() || null,
        embedding_name: embeddingNameInput.value.trim() || null,
        update_agents: updateAgents,
        author: author,
        reason: reason
    };
    
    console.log('Salvando alterações unificadas com novo endpoint:', unifiedPayload);
    
    apiRequest('POST', `${API_BASE_URL}/api/v1/unified-save`, unifiedPayload)
        .then(response => {
            hideLoading();
            console.log('Salvamento unificado concluído:', response);
            
            let message = `${response.version_display} salva com sucesso!`;
            const alertType = response.success ? 'success' : 'warning';
            
            if (response.message && response.message !== 'Alterações salvas com sucesso') {
                message = response.message;
            }
            
            showAlert(message, alertType);
            loadData(); // Recarregar dados
        })
        .catch(error => {
            hideLoading();
            console.error('Erro no salvamento unificado:', error);
            showAlert('Erro ao salvar alterações: ' + (error.message || 'Erro desconhecido'), 'danger');
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
        // Carregar histórico unificado (novo endpoint)
        apiRequest('GET', `${API_BASE_URL}/api/v1/unified-history?agent_type=${agentType}&limit=50`)
            .catch(error => {
                console.warn('Erro ao carregar histórico unificado:', error);
                return { items: [] };
            })
    ])
    .then(([currentPromptData, currentConfigData, unifiedHistoryResponse]) => {
        console.log('Dados carregados:', { currentPromptData, currentConfigData, unifiedHistoryResponse });
        
        // Preencher dados do prompt atual
        promptText.value = currentPromptData.prompt || '';
        currentPromptId = currentPromptData.prompt_id;
        
        // Preencher dados da configuração atual
        memoryBlocksText.value = JSON.stringify(currentConfigData.memory_blocks || [], null, 2);
        toolsInput.value = (currentConfigData.tools || []).join(', ');
        modelNameInput.value = currentConfigData.model_name || '';
        embeddingNameInput.value = currentConfigData.embedding_name || '';
        currentConfigId = currentConfigData.config_id;
        
        // Usar histórico unificado do backend
        unifiedHistoryData = unifiedHistoryResponse.items || [];
        
        // Renderizar histórico unificado
        renderBackendUnifiedHistory(unifiedHistoryData);
        
        hideLoading();
    })
    .catch(error => {
        hideLoading();
        showAlert('Erro ao carregar dados: ' + (error.message || 'Erro desconhecido'), 'danger');
        console.error('Erro ao carregar dados:', error);
    });
}

// Funções de histórico unificado removidas - agora usamos dados do backend

// Função para renderizar o histórico unificado (dados do backend)
function renderBackendUnifiedHistory(historyItems) {
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
        
        // Determinar se está ativo baseado nos dados do backend
        const isActive = item.is_active;
        
        const historyItem = document.createElement('div');
        historyItem.className = `history-item ${isActive ? 'active' : ''}`;
        historyItem.dataset.itemId = item.version_id;
        historyItem.dataset.itemType = 'unified';
        historyItem.dataset.versionNumber = item.version_number;
        
        // Criar badges baseados no tipo de alteração
        let badges = '';
        if (item.change_type === 'both') {
            badges = '<span class="badge bg-primary me-1">Prompt + Config</span>';
        } else if (item.change_type === 'prompt') {
            badges = '<span class="badge bg-primary me-1">System Prompt</span>';
        } else if (item.change_type === 'config') {
            badges = '<span class="badge bg-info me-1">Configurações</span>';
        }
        
        // Usar nomenclatura correta da versão
        const versionDisplay = item.version_display || `eai-${new Date(item.created_at).toISOString().split('T')[0]}-v${item.version_number}`;
        
        historyItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span class="history-version">
                    <i class="bi bi-bookmark me-1 text-primary"></i>
                    ${versionDisplay}
                </span>
                <span class="history-date">${date} ${timeStr}</span>
            </div>
            <div class="my-2">
                ${badges}
                ${item.is_active ? '<span class="badge bg-success me-1">Ativo</span>' : ''}
                ${item.author ? 
                    `<span class="metadata-badge">Autor: ${item.author}</span>` : ''}
                ${item.reason ? 
                    `<span class="metadata-badge">${item.reason}</span>` : ''}
            </div>
            <div class="history-preview" title="${item.preview}">
                ${item.preview}
            </div>
        `;
        
        // Adicionar listener de clique para carregar a versão unificada
        historyItem.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            selectBackendUnifiedVersion(item);
        });
        
        historyList.appendChild(historyItem);
    });
    
    console.log(`Renderizados ${historyItems.length} itens no histórico unificado do backend`);
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
        
        // Metadados são exibidos apenas no histórico, não nos campos de edição
        
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
            
            // Metadados são exibidos apenas no histórico
            
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





// Função handleSaveConfig removida - agora usamos handleSaveAll

// Funções createConfigConfirmationModal e proceedWithConfigSave removidas - agora usamos versões unificadas



// Função selectConfigById removida - agora usamos selectUnifiedVersion

function selectBackendUnifiedVersion(item) {
    console.log('Selecionando versão unificada do backend:', item);
    showLoading();
    
    // Usar o endpoint de detalhes de versão para obter dados completos
    apiRequest('GET', `${API_BASE_URL}/api/v1/unified-history/version/${item.version_number}?agent_type=${agentTypeSelect.value}`)
        .then(versionDetails => {
            console.log('Detalhes da versão carregados:', versionDetails);
            
            // Preencher dados do prompt se existir
            if (versionDetails.prompt) {
                promptText.value = versionDetails.prompt.content || '';
                currentPromptId = versionDetails.prompt.prompt_id;
            } else {
                promptText.value = '';
                currentPromptId = null;
            }
            
            // Preencher dados da configuração se existir
            if (versionDetails.config) {
                memoryBlocksText.value = JSON.stringify(versionDetails.config.memory_blocks || [], null, 2);
                toolsInput.value = (versionDetails.config.tools || []).join(', ');
                modelNameInput.value = versionDetails.config.model_name || '';
                embeddingNameInput.value = versionDetails.config.embedding_name || '';
                currentConfigId = versionDetails.config.config_id;
            } else {
                memoryBlocksText.value = '[]';
                toolsInput.value = '';
                modelNameInput.value = '';
                embeddingNameInput.value = '';
                currentConfigId = null;
            }
            
            // Atualizar interface para mostrar que esta versão está selecionada
            updateActiveBackendHistoryItem(item);
            
            // Definir que estamos visualizando um item do histórico
            isHistoryItemView = true;
            
            hideLoading();
            console.log('Versão unificada carregada com sucesso');
        })
        .catch(error => {
            console.error('Erro ao carregar versão unificada:', error);
            hideLoading();
            showAlert('Erro ao carregar versão: ' + error.message, 'danger');
        });
}

function updateActiveBackendHistoryItem(selectedItem) {
    // Marcar o item selecionado como ativo no histórico
    document.querySelectorAll('.history-item').forEach(item => {
        if (item.dataset.versionNumber === selectedItem.version_number.toString()) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
    
    // Definir que estamos visualizando um item do histórico
    isHistoryItemView = true;
}

// ---------------------- RESET ALL ----------------------
function handleResetAll() {
    const agentType = agentTypeSelect.value;

    if (!confirm('Tem certeza que deseja resetar COMPLETAMENTE o banco de dados para este tipo de agente? Esta ação removerá TODO o histórico e recriará versões padrão. Esta ação NÃO pode ser desfeita.')) {
        return;
    }

    showLoading();

    const updateAgents = updateAgentsCheckbox.checked;

    // Usar o novo endpoint de reset unificado
    apiRequest('DELETE', `${API_BASE_URL}/api/v1/unified-reset?agent_type=${agentType}&update_agents=${updateAgents}`)
        .then(response => {
            hideLoading();
            console.log('Reset unificado concluído:', response);
            
            let message = response.message || 'Reset unificado concluído com sucesso!';
            if (response.version_display) {
                message = `Reset concluído! Nova versão ${response.version_display} criada.`;
                if (response.message.includes('agentes foram atualizados')) {
                    const agentInfo = response.message.split(',')[1];
                    if (agentInfo) {
                        message += ` ${agentInfo.trim()}`;
                    }
                }
            }
            const alertType = response.success ? 'success' : 'warning';
            
            showAlert(message, alertType);
            
            // Recarregar dados
            loadData();
        })
        .catch(error => {
            hideLoading();
            console.error('Erro no reset unificado:', error);
            showAlert('Erro ao executar reset unificado: ' + (error.message || 'Erro desconhecido'), 'danger');
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