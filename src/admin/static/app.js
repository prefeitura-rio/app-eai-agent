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
    
    // Salvar token e mostrar painel admin
    localStorage.setItem('adminToken', token);
    currentToken = token;
    errorMsg.classList.add('d-none');
    showAdminPanel();
    loadData();
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
        // Carregar prompt atual
        apiRequest('GET', `/api/v1/system-prompt?agent_type=${agentType}`),
        // Carregar histórico
        apiRequest('GET', `/api/v1/system-prompt/history?agent_type=${agentType}`)
    ])
    .then(([currentData, historyData]) => {
        // Preencher dados do prompt atual
        promptText.value = currentData.prompt;
        currentPromptId = currentData.prompt_id;
        
        // Limpar e preencher o histórico
        renderHistory(historyData.prompts);
        
        hideLoading();
    })
    .catch(error => {
        hideLoading();
        showAlert('Erro ao carregar dados: ' + (error.message || 'Erro desconhecido'), 'danger');
    });
}

function renderHistory(prompts) {
    historyList.innerHTML = '';
    
    prompts.forEach(prompt => {
        const isActive = prompt.is_active;
        const date = new Date(prompt.created_at).toLocaleDateString();
        
        const item = document.createElement('div');
        item.className = `history-item ${prompt.prompt_id === currentPromptId ? 'active' : ''}`;
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
                ${prompt.content.substring(0, 50)}...
            </div>
        `;
        
        item.addEventListener('click', () => {
            selectPrompt(prompt);
        });
        
        historyList.appendChild(item);
    });
}

function selectPrompt(prompt) {
    promptText.value = prompt.content;
    currentPromptId = prompt.prompt_id;
    
    if (prompt.metadata) {
        authorInput.value = prompt.metadata.author || '';
        reasonInput.value = prompt.metadata.reason || '';
    }
    
    // Atualizar a classe ativa
    const items = historyList.querySelectorAll('.history-item');
    items.forEach(item => item.classList.remove('active'));
    
    // Encontrar e marcar o novo item ativo
    const activeItems = historyList.querySelectorAll(`.history-item`);
    activeItems.forEach(item => {
        if (item.textContent.includes(`v${prompt.version}`)) {
            item.classList.add('active');
        }
    });
}

// Helper para fazer requisições API
function apiRequest(method, url, data = null) {
    const options = {
        method,
        headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // Caso token seja inválido, fazer logout
                    handleLogout();
                    throw new Error('Token inválido ou expirado');
                }
                throw new Error(`Erro ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
} 