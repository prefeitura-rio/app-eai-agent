// Componente bem simples para teste de carregamento
const App = () => {
    return React.createElement('div', { className: 'container mt-5' },
        React.createElement('div', { className: 'alert alert-success' },
            React.createElement('h2', null, 'Painel Administrativo'),
            React.createElement('p', null, 'O JavaScript está funcionando corretamente!')
        ),
        React.createElement('div', { className: 'card' },
            React.createElement('div', { className: 'card-body' },
                React.createElement('h3', null, 'Login'),
                React.createElement('div', { className: 'mb-3' },
                    React.createElement('label', { className: 'form-label' }, 'Token de Acesso'),
                    React.createElement('input', { type: 'password', className: 'form-control', placeholder: 'Digite o token' })
                ),
                React.createElement('button', { className: 'btn btn-primary' }, 'Entrar')
            )
        )
    );
};

// Renderização do aplicativo sem JSX, usando apenas React.createElement
const container = document.getElementById('app');
ReactDOM.createRoot(container).render(React.createElement(App)); 