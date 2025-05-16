// Definição de componentes React para o painel administrativo

// Componente de Login
const Login = ({ onLogin }) => {
    const [token, setToken] = React.useState('');
    const [error, setError] = React.useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!token.trim()) {
            setError('Por favor, insira um token válido');
            return;
        }

        // Salvar o token no localStorage
        localStorage.setItem('adminToken', token);
        onLogin(token);
    };

    return (
        <div className="login-container">
            <h2 className="mb-4 text-center">Painel Administrativo</h2>
            <form onSubmit={handleSubmit}>
                <div className="mb-3">
                    <label htmlFor="token" className="form-label">Token de Autenticação</label>
                    <input
                        type="password"
                        className="form-control"
                        id="token"
                        value={token}
                        onChange={(e) => setToken(e.target.value)}
                        placeholder="Insira o token de autenticação"
                    />
                </div>
                {error && <div className="alert alert-danger">{error}</div>}
                <button type="submit" className="btn btn-primary w-100">Entrar</button>
            </form>
        </div>
    );
};

// Componente de Histórico
const PromptHistory = ({ history, onSelectPrompt, activePromptId }) => {
    return (
        <div className="history-container">
            <h4>Histórico de Prompts</h4>
            <div className="list-group mt-3">
                {history.map((item) => (
                    <div
                        key={item.prompt_id}
                        className={`history-item ${item.prompt_id === activePromptId ? 'active' : ''}`}
                        onClick={() => onSelectPrompt(item)}
                    >
                        <div className="d-flex justify-content-between">
                            <strong>v{item.version}</strong>
                            <small>{new Date(item.created_at).toLocaleDateString()}</small>
                        </div>
                        <div>
                            {item.is_active && <span className="badge bg-success me-1">Ativo</span>}
                            {item.metadata && item.metadata.author && (
                                <span className="metadata-badge">Autor: {item.metadata.author}</span>
                            )}
                        </div>
                        <div className="text-truncate mt-1 small">
                            {item.content.substring(0, 50)}...
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Componente do Editor de Prompt
const PromptEditor = ({ currentPrompt, onChange, onSubmit, isSubmitting }) => {
    const [tags, setTags] = React.useState([]);
    const [newTag, setNewTag] = React.useState('');
    const [metadata, setMetadata] = React.useState({
        author: '',
        reason: ''
    });
    const [updateAgents, setUpdateAgents] = React.useState(true);

    React.useEffect(() => {
        if (currentPrompt && currentPrompt.metadata) {
            setMetadata(currentPrompt.metadata);
            if (currentPrompt.tags) setTags(currentPrompt.tags);
        }
    }, [currentPrompt]);

    const handleAddTag = () => {
        if (newTag.trim() && !tags.includes(newTag.trim())) {
            setTags([...tags, newTag.trim()]);
            setNewTag('');
        }
    };

    const handleRemoveTag = (tag) => {
        setTags(tags.filter(t => t !== tag));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({
            tags,
            metadata,
            updateAgents
        });
    };

    return (
        <div className="prompt-container">
            <h4>Editor de System Prompt</h4>
            <form onSubmit={handleSubmit}>
                <div className="mb-3 mt-3">
                    <label htmlFor="promptText" className="form-label">Conteúdo do Prompt</label>
                    <textarea
                        id="promptText"
                        className="prompt-editor"
                        value={currentPrompt.content || ''}
                        onChange={(e) => onChange(e.target.value)}
                        required
                    ></textarea>
                </div>

                <div className="row mb-3">
                    <div className="col-md-6">
                        <label htmlFor="author" className="form-label">Autor</label>
                        <input
                            type="text"
                            className="form-control"
                            id="author"
                            value={metadata.author}
                            onChange={(e) => setMetadata({...metadata, author: e.target.value})}
                        />
                    </div>
                    <div className="col-md-6">
                        <label htmlFor="reason" className="form-label">Motivo da Atualização</label>
                        <input
                            type="text"
                            className="form-control"
                            id="reason"
                            value={metadata.reason}
                            onChange={(e) => setMetadata({...metadata, reason: e.target.value})}
                        />
                    </div>
                </div>

                <div className="mb-3">
                    <label className="form-label">Tags</label>
                    <div className="input-group">
                        <input
                            type="text"
                            className="form-control"
                            value={newTag}
                            onChange={(e) => setNewTag(e.target.value)}
                            placeholder="Adicionar tag"
                        />
                        <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={handleAddTag}
                        >
                            Adicionar
                        </button>
                    </div>
                    <div className="mt-2">
                        {tags.map(tag => (
                            <span key={tag} className="badge bg-secondary me-1 mb-1">
                                {tag}
                                <button
                                    type="button"
                                    className="btn-close btn-close-white ms-1"
                                    onClick={() => handleRemoveTag(tag)}
                                    style={{ fontSize: '0.5rem' }}
                                ></button>
                            </span>
                        ))}
                    </div>
                </div>

                <div className="form-check mb-3">
                    <input
                        className="form-check-input"
                        type="checkbox"
                        id="updateAgents"
                        checked={updateAgents}
                        onChange={(e) => setUpdateAgents(e.target.checked)}
                    />
                    <label className="form-check-label" htmlFor="updateAgents">
                        Atualizar agentes existentes
                    </label>
                </div>

                <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isSubmitting}
                >
                    {isSubmitting ? 'Salvando...' : 'Salvar Alterações'}
                </button>
            </form>
        </div>
    );
};

// Componente principal do Admin
const AdminPanel = ({ token, onLogout }) => {
    const [agentType, setAgentType] = React.useState('agentic_search');
    const [promptHistory, setPromptHistory] = React.useState([]);
    const [currentPrompt, setCurrentPrompt] = React.useState({ content: '' });
    const [isLoading, setIsLoading] = React.useState(true);
    const [error, setError] = React.useState('');
    const [successMessage, setSuccessMessage] = React.useState('');
    const [isSubmitting, setIsSubmitting] = React.useState(false);
    const [activePromptId, setActivePromptId] = React.useState(null);

    // Configuração do cliente HTTP com o token
    const api = axios.create({
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    // Carregar dados iniciais
    React.useEffect(() => {
        fetchPromptHistory();
        fetchCurrentPrompt();
    }, [agentType]);

    // Buscar histórico de prompts
    const fetchPromptHistory = async () => {
        setIsLoading(true);
        try {
            const response = await api.get(`/api/v1/system-prompt/history?agent_type=${agentType}`);
            setPromptHistory(response.data.prompts);
            
            // Identificar o prompt ativo
            const activePrompt = response.data.prompts.find(p => p.is_active);
            if (activePrompt) {
                setActivePromptId(activePrompt.prompt_id);
            }
        } catch (err) {
            setError('Erro ao carregar histórico de prompts');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    // Buscar prompt atual
    const fetchCurrentPrompt = async () => {
        setIsLoading(true);
        try {
            const response = await api.get(`/api/v1/system-prompt?agent_type=${agentType}`);
            setCurrentPrompt({
                content: response.data.prompt,
                agent_type: response.data.agent_type,
                version: response.data.version,
                prompt_id: response.data.prompt_id,
                created_at: response.data.created_at,
                metadata: {}
            });
            
            if (response.data.prompt_id) {
                setActivePromptId(response.data.prompt_id);
            }
        } catch (err) {
            setError('Erro ao carregar prompt atual');
            console.error(err);
        } finally {
            setIsLoading(false);
        }
    };

    // Atualizar conteúdo do prompt atual
    const handlePromptChange = (content) => {
        setCurrentPrompt({ ...currentPrompt, content });
    };

    // Selecionar um prompt do histórico
    const handleSelectPrompt = (prompt) => {
        setCurrentPrompt({
            content: prompt.content,
            prompt_id: prompt.prompt_id,
            version: prompt.version,
            created_at: prompt.created_at,
            metadata: prompt.metadata || {},
            tags: prompt.tags || []
        });
        setActivePromptId(prompt.prompt_id);
    };

    // Enviar atualização do prompt
    const handleSubmitPrompt = async (formData) => {
        setError('');
        setSuccessMessage('');
        setIsSubmitting(true);
        
        try {
            const payload = {
                new_prompt: currentPrompt.content,
                agent_type: agentType,
                update_agents: formData.updateAgents,
                tags: formData.tags,
                metadata: formData.metadata
            };
            
            const response = await api.post('/api/v1/system-prompt', payload);
            
            setSuccessMessage('Prompt atualizado com sucesso!');
            
            // Recarregar dados
            await fetchPromptHistory();
            await fetchCurrentPrompt();
        } catch (err) {
            setError(`Erro ao atualizar prompt: ${err.response?.data?.detail || err.message}`);
            console.error(err);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="admin-container">
            <div className="navbar">
                <h1 className="nav-title">Painel Admin - System Prompts</h1>
                <button
                    className="btn btn-sm btn-outline-light"
                    onClick={() => {
                        localStorage.removeItem('adminToken');
                        onLogout();
                    }}
                >
                    Sair
                </button>
            </div>

            {error && (
                <div className="alert alert-danger alert-dismissible fade show" role="alert">
                    {error}
                    <button
                        type="button"
                        className="btn-close"
                        onClick={() => setError('')}
                    ></button>
                </div>
            )}

            {successMessage && (
                <div className="alert alert-success alert-dismissible fade show" role="alert">
                    {successMessage}
                    <button
                        type="button"
                        className="btn-close"
                        onClick={() => setSuccessMessage('')}
                    ></button>
                </div>
            )}

            <div className="mb-3">
                <label htmlFor="agentType" className="form-label">Tipo de Agente</label>
                <select
                    id="agentType"
                    className="form-select"
                    value={agentType}
                    onChange={(e) => setAgentType(e.target.value)}
                >
                    <option value="agentic_search">Agentic Search</option>
                    <option value="chat">Chat</option>
                </select>
            </div>

            {isLoading ? (
                <div className="d-flex justify-content-center my-5">
                    <div className="spinner-border text-primary" role="status">
                        <span className="visually-hidden">Carregando...</span>
                    </div>
                </div>
            ) : (
                <div className="flex-container">
                    <PromptEditor
                        currentPrompt={currentPrompt}
                        onChange={handlePromptChange}
                        onSubmit={handleSubmitPrompt}
                        isSubmitting={isSubmitting}
                    />
                    <PromptHistory
                        history={promptHistory}
                        onSelectPrompt={handleSelectPrompt}
                        activePromptId={activePromptId}
                    />
                </div>
            )}
        </div>
    );
};

// Aplicativo principal
const App = () => {
    const [token, setToken] = React.useState(localStorage.getItem('adminToken'));

    const handleLogin = (newToken) => {
        setToken(newToken);
    };

    const handleLogout = () => {
        setToken(null);
    };

    return token ? (
        <AdminPanel token={token} onLogout={handleLogout} />
    ) : (
        <Login onLogin={handleLogin} />
    );
};

// Renderização do aplicativo
const container = document.getElementById('app');
const root = ReactDOM.createRoot(container);
root.render(<App />); 