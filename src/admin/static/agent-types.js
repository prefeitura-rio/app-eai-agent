// Função para carregar tipos de agentes da API
function loadAgentTypes() {
    const token = localStorage.getItem('adminToken');
    if (!token) return;
    
    axios.get('/api/v1/system-prompt/agent-types', {
        headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(response => {
        const agentTypeSelect = document.getElementById('agentType');
        agentTypeSelect.innerHTML = ''; // Limpar opções existentes
        
        if (response.data && response.data.length > 0) {
            // Adicionar as opções retornadas pelo endpoint
            response.data.forEach(type => {
                const option = document.createElement('option');
                option.value = type;
                option.textContent = type;
                agentTypeSelect.appendChild(option);
            });
        } else {
            // Caso não haja tipos de agentes, adicionar opção padrão
            const option = document.createElement('option');
            option.value = "agentic_search";
            option.textContent = "agentic_search";
            agentTypeSelect.appendChild(option);
        }
        
        // Disparar o evento change para carregar o prompt do tipo selecionado
        const event = new Event('change');
        agentTypeSelect.dispatchEvent(event);
    })
    .catch(error => {
        console.error('Erro ao carregar tipos de agentes:', error);
        
        // Em caso de erro, definir "agentic_search" como fallback
        const agentTypeSelect = document.getElementById('agentType');
        agentTypeSelect.innerHTML = '';
        const option = document.createElement('option');
        option.value = "agentic_search";
        option.textContent = "agentic_search";
        agentTypeSelect.appendChild(option);
        
        // Disparar o evento change para carregar o prompt do tipo selecionado
        const event = new Event('change');
        agentTypeSelect.dispatchEvent(event);
    });
}

// Adicionar evento para carregar tipos de agentes após o login
document.addEventListener('agentTypesReady', loadAgentTypes);

// Verificar se o usuário já está logado
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('adminToken')) {
        // Se já estiver logado, iniciar carregamento dos tipos de agentes
        loadAgentTypes();
    }
}); 