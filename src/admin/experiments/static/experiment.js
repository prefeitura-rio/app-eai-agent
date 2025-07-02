document.addEventListener("DOMContentLoaded", () => {
  console.log("Experiment page JavaScript loaded successfully");

  // Elementos DOM de autenticação
  const loginForm = document.getElementById("loginForm");
  const experimentsPanel = document.getElementById("experimentsPanel");
  const errorMsg = document.getElementById("errorMsg");
  const logoutBtn = document.getElementById("logoutBtn");

  // Elementos DOM da funcionalidade principal
  const experimentIdInput = document.getElementById("experimentIdInput");
  const fetchExperimentBtn = document.getElementById("fetchExperimentBtn");
  const resultContainer = document.getElementById("resultContainer");
  const resultJson = document.getElementById("resultJson");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const alertArea = document.getElementById("alertArea");

  console.log("DOM elements found:", {
    loginForm: !!loginForm,
    experimentsPanel: !!experimentsPanel,
    experimentIdInput: !!experimentIdInput,
    fetchExperimentBtn: !!fetchExperimentBtn,
    resultContainer: !!resultContainer,
    resultJson: !!resultJson,
    loadingIndicator: !!loadingIndicator,
    alertArea: !!alertArea,
  });

  // Configuração da API
  const API_BASE_URL = "https://services.staging.app.dados.rio/eai-agent";
  let currentToken = localStorage.getItem("adminToken");
  let PHOENIX_ENDPOINT = "";

  // Verificar se já existe um token salvo
  if (currentToken) {
    showExperimentsPanel();
  }

  // Event listeners de autenticação
  if (loginForm) {
    loginForm.addEventListener("submit", handleLogin);
  }
  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogout);
  }

  // Funções de autenticação
  function handleLogin(e) {
    e.preventDefault();

    const token = document.getElementById("token").value.trim();
    if (!token) {
      errorMsg.textContent = "Por favor, insira um token válido";
      errorMsg.classList.remove("d-none");
      return;
    }

    // Testar token fazendo uma requisição de verificação
    fetch(`${API_BASE_URL}/api/v1/system-prompt`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Token inválido");
        }
        return response.json();
      })
      .then((data) => {
        // Token válido, salvar e mostrar painel
        localStorage.setItem("adminToken", token);
        currentToken = token;
        errorMsg.classList.add("d-none");
        showExperimentsPanel();
      })
      .catch((error) => {
        console.error("Erro na autenticação:", error);
        errorMsg.textContent = "Token inválido ou erro de conexão";
        errorMsg.classList.remove("d-none");
      });
  }

  function handleLogout() {
    localStorage.removeItem("adminToken");
    currentToken = null;
    document.querySelector(".login-container").classList.remove("d-none");
    experimentsPanel.classList.add("d-none");
    document.getElementById("token").value = "";
  }

  function showExperimentsPanel() {
    document.querySelector(".login-container").classList.add("d-none");
    experimentsPanel.classList.remove("d-none");
    // Inicializar funcionalidades após mostrar o painel
    initializeExperimentsFunctionality();
  }

  // Função para inicializar a funcionalidade principal após autenticação
  function initializeExperimentsFunctionality() {
    console.log("Initializing experiments functionality");

    // Event listeners da funcionalidade principal
    if (fetchExperimentBtn) {
      fetchExperimentBtn.addEventListener("click", () => {
        console.log("Button clicked");
        fetchExperimentData();
      });
    }

    if (experimentIdInput) {
      experimentIdInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
          console.log("Enter key pressed");
          fetchExperimentData();
        }
      });
    }

    console.log("Event listeners attached");
    fetchConfig();
  }

  // Função para buscar a configuração do backend. A URL relativa '/experiments/config'
  // será resolvida pelo navegador para '/admin/experiments/config'.
  const fetchConfig = async () => {
    console.log("Fetching config...");
    try {
      const response = await axios.get("config", {
        headers: { Authorization: `Bearer ${currentToken}` },
      });
      console.log("Config response:", response.data);
      PHOENIX_ENDPOINT = response.data.phoenix_endpoint;
      console.log("Phoenix endpoint set to:", PHOENIX_ENDPOINT);
      if (!PHOENIX_ENDPOINT) {
        showAlert(
          "A URL do serviço Phoenix não foi configurada no backend.",
          "danger"
        );
        if (fetchExperimentBtn) {
          fetchExperimentBtn.disabled = true;
        }
      }
    } catch (error) {
      console.error("Erro ao buscar configuração:", error);
      showAlert(
        "Não foi possível obter a configuração do servidor.",
        "danger"
      );
      if (fetchExperimentBtn) {
        fetchExperimentBtn.disabled = true;
      }
    }
  };

  // Função para buscar os dados do experimento
  const fetchExperimentData = async () => {
    if (!experimentIdInput || !fetchExperimentBtn) {
      console.error("DOM elements not found");
      return;
    }

    const expId = experimentIdInput.value.trim();
    if (!expId) {
      showAlert("Por favor, insira um ID de experimento.", "warning");
      return;
    }

    if (!PHOENIX_ENDPOINT) {
      showAlert(
        "Configuração do endpoint pendente. Tente novamente em alguns segundos.",
        "warning"
      );
      return;
    }

    if (loadingIndicator) {
      loadingIndicator.classList.remove("d-none");
    }
    if (resultContainer) {
      resultContainer.classList.add("d-none");
    }
    if (alertArea) {
      alertArea.innerHTML = "";
    }

    fetchExperimentBtn.disabled = true;
    fetchExperimentBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';

    try {
      const url = `${PHOENIX_ENDPOINT}v1/experiments/${expId}/json`;
      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${currentToken}` },
      });

      if (resultJson) {
        resultJson.textContent = JSON.stringify(response.data, null, 2);
      }
      if (resultContainer) {
        resultContainer.classList.remove("d-none");
      }
    } catch (error) {
      console.error("Erro ao buscar dados do experimento:", error);
      const errorMessage =
        error.response?.data?.detail || error.message || "Erro desconhecido.";
      showAlert(`Falha ao buscar o experimento: ${errorMessage}`, "danger");
    } finally {
      if (loadingIndicator) {
        loadingIndicator.classList.add("d-none");
      }
      fetchExperimentBtn.disabled = false;
      fetchExperimentBtn.innerHTML =
        '<i class="bi bi-search me-1"></i> Buscar';
    }
  };

  const showAlert = (message, type = "danger") => {
    if (alertArea) {
      alertArea.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      `;
    }
  };
});
