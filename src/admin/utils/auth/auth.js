// Configuração global
const API_BASE_URL =
  window.API_BASE_URL_OVERRIDE ||
  "https://services.staging.app.dados.rio/eai-agent";

// Elementos DOM
const authForm = document.getElementById("authForm");
const authToken = document.getElementById("authToken");
const loginText = document.getElementById("loginText");
const loadingSpinner = document.getElementById("loadingSpinner");
const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");
const successMessage = document.getElementById("successMessage");
const successText = document.getElementById("successText");
const themeToggleBtn = document.getElementById("themeToggleBtn");
const themeIcon = document.getElementById("themeIcon");

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  console.log("Página de autenticação carregada");

  // Inicializar tema
  initializeTheme();

  // Verificar se já existe token válido
  const existingToken = localStorage.getItem("adminToken");
  if (existingToken) {
    console.log("Token encontrado, validando...");
    validateExistingToken(existingToken);
  }

  // Event listeners
  authForm.addEventListener("submit", handleLogin);
  authToken.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
      handleLogin(e);
    }
  });

  // Add theme toggle event listener
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", toggleTheme);
  }

  // Focar no input
  authToken.focus();
});

// Funções de autenticação
async function handleLogin(e) {
  e.preventDefault();

  const token = authToken.value.trim().replace(/["\n\r]/g, "");
  if (!token) {
    showError("Por favor, insira um token de autenticação.");
    return;
  }

  setLoadingState(true);
  hideMessages();

  try {
    await validateToken(token);

    // Salvar token
    localStorage.setItem("adminToken", token);

    showSuccess("Autenticação realizada com sucesso! Redirecionando...");

    // Redirecionar após sucesso
    setTimeout(() => {
      redirectToOriginalPage();
    }, 1500);
  } catch (error) {
    console.error("Erro na autenticação:", error);
    showError(`Falha na autenticação: ${error.message}`);
  } finally {
    setLoadingState(false);
  }
}

async function validateExistingToken(token) {
  try {
    await validateToken(token);
    console.log("Token válido, redirecionando...");
    redirectToOriginalPage();
  } catch (error) {
    console.log("Token inválido, removendo...");
    localStorage.removeItem("adminToken");
    authToken.focus();
  }
}

async function validateToken(token) {
  const API_BASE_URL_AUTH =
    "https://services.staging.app.dados.rio/eai-agent";
  const validationUrl = `${API_BASE_URL_AUTH}/api/v1/system-prompt`;

  const response = await fetch(validationUrl, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
      Accept: "application/json",
    },
    timeout: 10000,
  });

  if (!response.ok) {
    let errorMessage = `Authentication failed (Status: ${response.status})`;

    try {
      const errorData = await response.json();
      errorMessage = errorData.detail || errorMessage;
    } catch (e) {
      // Ignore JSON parsing errors
    }

    throw new Error(errorMessage);
  }

  return response.json();
}

function redirectToOriginalPage() {
  // Verificar se há uma página de destino específica
  const urlParams = new URLSearchParams(window.location.search);
  const returnUrl = urlParams.get("return");

  if (returnUrl) {
    // Decodificar e redirecionar para a URL original
    window.location.href = decodeURIComponent(returnUrl);
  } else {
    // Redirecionar para a página de datasets por padrão
    window.location.href = "/eai-agent/admin/experiments/";
  }
}

// Funções de UI
function setLoadingState(isLoading) {
  if (isLoading) {
    loginText.style.display = "none";
    loadingSpinner.style.display = "inline";
    authForm.querySelector('button[type="submit"]').disabled = true;
    authToken.disabled = true;
  } else {
    loginText.style.display = "inline";
    loadingSpinner.style.display = "none";
    authForm.querySelector('button[type="submit"]').disabled = false;
    authToken.disabled = false;
  }
}

function showError(message) {
  errorText.textContent = message;
  errorMessage.style.display = "block";
  successMessage.style.display = "none";

  // Focar no input após erro
  setTimeout(() => {
    authToken.focus();
    authToken.select();
  }, 100);
}

function showSuccess(message) {
  successText.textContent = message;
  successMessage.style.display = "block";
  errorMessage.style.display = "none";
}

function hideMessages() {
  errorMessage.style.display = "none";
  successMessage.style.display = "none";
}

// Função utilitária para outras páginas
window.AuthManager = {
  // Verificar se usuário está autenticado
  isAuthenticated: function () {
    return !!localStorage.getItem("adminToken");
  },

  // Obter token atual
  getToken: function () {
    return localStorage.getItem("adminToken");
  },

  // Redirecionar para autenticação
  redirectToAuth: function (currentUrl = null) {
    const authUrl = "/eai-agent/admin/experiments/static/auth.html";
    if (currentUrl) {
      window.location.href = `${authUrl}?return=${encodeURIComponent(
        currentUrl
      )}`;
    } else {
      window.location.href = authUrl;
    }
  },

  // Fazer logout
  logout: function () {
    localStorage.removeItem("adminToken");
    this.redirectToAuth();
  },

  // Validar token atual
  validateCurrentToken: async function () {
    const token = this.getToken();
    if (!token) {
      return false;
    }

    try {
      await validateToken(token);
      return true;
    } catch (error) {
      localStorage.removeItem("adminToken");
      return false;
    }
  },
};

// Theme management functions
function initializeTheme() {
  const savedTheme = localStorage.getItem("experiments-theme") || "light";
  applyTheme(savedTheme);
}

function toggleTheme() {
  const currentTheme =
    document.documentElement.getAttribute("data-bs-theme") || "light";
  const newTheme = currentTheme === "light" ? "dark" : "light";
  applyTheme(newTheme);
  localStorage.setItem("experiments-theme", newTheme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute("data-bs-theme", theme);

  if (themeIcon) {
    if (theme === "dark") {
      themeIcon.className = "bi bi-sun-fill";
    } else {
      themeIcon.className = "bi bi-moon-fill";
    }
  }
}

// Exportar para uso global
window.validateToken = validateToken;
