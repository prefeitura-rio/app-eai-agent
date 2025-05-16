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
const historyList = document.getElementById('historyList');
const logoutBtn = document.getElementById('logoutBtn');
const errorMsg = document.getElementById('errorMsg');

// Variáveis globais
let currentToken = localStorage.getItem('adminToken');
let currentPromptId = null;
let promptsData = []; // Array para armazenar todos os dados dos prompts

// Configuração inicial
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado, inicializando painel admin');
    // Verificar se já existe um token salvo
    if (currentToken) {
        showAdminPanel();
        loadData();
    }
    
    // Event Listeners
    loginForm.addEventListener('submit', handleLogin);
    agentTypeSelect.addEventListener('change', loadData);
    saveButton.addEventListener('click', handleSavePrompt);
    logoutBtn.addEventListener('click', handleLogout);
});

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
        loadData();
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
    showLoading();
    const agentType = agentTypeSelect.value;
    const newPrompt = promptText.value;
    const metadata = {
        author: authorInput.value,
        reason: reasonInput.value
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
            showAlert('Prompt atualizado com sucesso!');
            loadData(); // Recarregar dados
        })
        .catch(error => {
            hideLoading();
            showAlert(error.message || 'Erro ao atualizar prompt', 'danger');
        });
}

// Funções de dados
function loadData() {
    showLoading();
    const agentType = agentTypeSelect.value;
    
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
        
        // Se for um prompt novo, mostramos mensagem de orientação
        if (currentData.is_new) {
            showAlert('Nenhum prompt configurado para este tipo de agente. Adicione o texto do prompt e clique em Salvar para criar o primeiro.', 'info');
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
        const date = new Date(prompt.created_at).toLocaleDateString();
        
        // Obter texto para preview - tentamos diferentes propriedades
        let previewText = '(Sem conteúdo)';
        if (typeof prompt.content === 'string') {
            previewText = prompt.content;
        }
        
        const item = document.createElement('div');
        item.className = `history-item ${prompt.prompt_id === currentPromptId ? 'active' : ''}`;
        item.dataset.promptId = prompt.prompt_id;
        item.dataset.version = prompt.version;
        item.innerHTML = `
            <div class="d-flex justify-content-between">
                <strong>v${prompt.version}</strong>
                <small>${date}</small>
            </div>
            <div>
                ${isActive ? '<span class="badge bg-success me-1">Ativo</span>' : ''}
                ${prompt.metadata && prompt.metadata.author ? 
                    `<span class="metadata-badge">Autor: ${prompt.metadata.author}</span>` : ''}
            </div>
            <div class="text-truncate mt-1 small">
                ${previewText.substring(0, 50)}...
            </div>
        `;
        
        item.addEventListener('click', () => {
            // Passa o próprio prompt para garantir acesso ao conteúdo completo
            selectPromptById(prompt.prompt_id);
        });
        
        historyList.appendChild(item);
    });
}

// Nova função para selecionar por ID e obter o prompt novamente via API
function selectPromptById(promptId) {
    console.log('Buscando prompt por ID:', promptId);
    
    showLoading();
    const agentType = agentTypeSelect.value;
    
    // Buscar o prompt específico da API usando o history endpoint
    apiRequest('GET', `/api/v1/system-prompt/history?agent_type=${agentType}`)
        .then(data => {
            // Encontrar o prompt específico pelo ID
            const prompt = (data.prompts || []).find(p => p.prompt_id === promptId);
            
            if (!prompt) {
                console.error('Prompt não encontrado no histórico:', promptId);
                hideLoading();
                return;
            }
            
            console.log('Prompt encontrado:', prompt);
            
            // Agora buscamos o conteúdo completo usando o endpoint específico
            return apiRequest('GET', `/api/v1/system-prompt?agent_type=${agentType}&version=${prompt.version}`)
                .then(fullPrompt => {
                    console.log('Dados completos do prompt:', fullPrompt);
                    
                    // Usar o conteúdo completo do prompt
                    promptText.value = fullPrompt.prompt || '';
                    currentPromptId = promptId;
                    
                    if (prompt.metadata) {
                        authorInput.value = prompt.metadata.author || '';
                        reasonInput.value = prompt.metadata.reason || '';
                    }
                    
                    // Atualizar a classe ativa
                    const items = historyList.querySelectorAll('.history-item');
                    items.forEach(item => item.classList.remove('active'));
                    
                    // Encontrar e marcar o novo item ativo
                    const activeItem = historyList.querySelector(`.history-item[data-prompt-id="${promptId}"]`);
                    if (activeItem) {
                        activeItem.classList.add('active');
                    }
                    
                    hideLoading();
                })
                .catch(error => {
                    console.error('Erro ao buscar conteúdo completo do prompt:', error);
                    hideLoading();
                    showAlert('Erro ao carregar o conteúdo completo do prompt', 'danger');
                });
        })
        .catch(error => {
            console.error('Erro ao buscar histórico para seleção de prompt:', error);
            hideLoading();
            showAlert('Erro ao selecionar prompt do histórico', 'danger');
        });
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