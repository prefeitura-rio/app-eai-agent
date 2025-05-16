// Versão simplificada para teste
const App = () => {
    return (
        <div className="container mt-5">
            <div className="alert alert-info">
                <h2>Painel Administrativo - Teste</h2>
                <p>Se você está vendo esta mensagem, o React está carregando corretamente.</p>
            </div>
            
            <div className="card">
                <div className="card-body">
                    <h3>Login</h3>
                    <div className="mb-3">
                        <label className="form-label">Token de Acesso</label>
                        <input type="password" className="form-control" placeholder="Digite o token" />
                    </div>
                    <button className="btn btn-primary">Entrar</button>
                </div>
            </div>
        </div>
    );
};

// Renderização do aplicativo
const container = document.getElementById('app');
ReactDOM.createRoot(container).render(<App />); 