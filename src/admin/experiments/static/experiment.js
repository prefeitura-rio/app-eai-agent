// Elementos DOM principais
const experimentIdInput = document.getElementById("experimentIdInput");
const fetchExperimentBtn = document.getElementById("fetchExperimentBtn");
const resultContainer = document.getElementById("resultContainer");
const resultJson = document.getElementById("resultJson");
const loadingIndicator = document.getElementById("loadingIndicator");
const alertArea = document.getElementById("alertArea");
const experimentsPanel = document.getElementById("experimentsPanel");
const logoutBtn = document.getElementById("logoutBtn");

// Variáveis globais
let currentToken = localStorage.getItem("adminToken");
let PHOENIX_ENDPOINT = "";

// API base URL - ajustar de acordo com o ambiente
const API_BASE_URL = "https://services.staging.app.dados.rio/eai-agent";

// Configuração inicial
document.addEventListener("DOMContentLoaded", function () {
  console.log("DOM carregado, inicializando painel de experimentos");

  // Verificar se já existe um token salvo
  if (currentToken) {
    showExperimentsPanel();
  }

  // Event Listeners
  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogout);
  }

  // Adicionar listener para o evento de experimentos prontos
  document.addEventListener("experimentsReady", function (e) {
    console.log("Evento experimentsReady recebido");

    // Aguardar um momento para garantir que os elementos estejam prontos
    setTimeout(() => {
      console.log("Iniciando funcionalidades de experimentos");
      initializeExperimentsFunctionality();
    }, 100);
  });
});

// Funções de UI
function showExperimentsPanel() {
  if (experimentsPanel) {
    document.querySelector(".login-container").classList.add("d-none");
    experimentsPanel.classList.remove("d-none");

    // Inicializar funcionalidades se os elementos estiverem prontos
    setTimeout(() => {
      initializeExperimentsFunctionality();
    }, 100);
  }
}

function showAlert(message, type = "danger") {
  if (alertArea) {
    alertArea.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
  }
}

// Manipuladores de eventos
function handleLogout() {
  localStorage.removeItem("adminToken");
  location.reload();
}

function initializeExperimentsFunctionality() {
  console.log("Inicializando funcionalidades de experimentos");

  // Event listeners da funcionalidade principal
  if (fetchExperimentBtn) {
    fetchExperimentBtn.addEventListener("click", function () {
      console.log("Button clicked");
      fetchExperimentData();
    });
  }

  if (experimentIdInput) {
    experimentIdInput.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        console.log("Enter key pressed");
        fetchExperimentData();
      }
    });
  }

  console.log("Event listeners attached");
  fetchConfig();
}

// Função para buscar a configuração do backend
function fetchConfig() {
  console.log("Fetching config...");

  fetch("config", {
    headers: { Authorization: `Bearer ${currentToken}` },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Erro ao buscar configuração");
      }
      return response.json();
    })
    .then((data) => {
      console.log("Config response:", data);
      PHOENIX_ENDPOINT = data.phoenix_endpoint;
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
    })
    .catch((error) => {
      console.error("Erro ao buscar configuração:", error);
      showAlert(
        "Não foi possível obter a configuração do servidor.",
        "danger"
      );
      if (fetchExperimentBtn) {
        fetchExperimentBtn.disabled = true;
      }
    });
}

// Função para buscar os dados do experimento
function fetchExperimentData() {
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

  const url = `${PHOENIX_ENDPOINT}v1/experiments/${expId}/json`;

  fetch(url, {
    headers: { Authorization: `Bearer ${currentToken}` },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      if (resultJson) {
        resultJson.textContent = JSON.stringify(data, null, 2);
      }
      if (resultContainer) {
        resultContainer.classList.remove("d-none");
      }
    })
    .catch((error) => {
      console.error("Erro ao buscar dados do experimento:", error);
      const errorMessage = error.message || "Erro desconhecido.";
      showAlert(`Falha ao buscar o experimento: ${errorMessage}`, "danger");
    })
    .finally(() => {
      if (loadingIndicator) {
        loadingIndicator.classList.add("d-none");
      }
      if (fetchExperimentBtn) {
        fetchExperimentBtn.disabled = false;
        fetchExperimentBtn.innerHTML =
          '<i class="bi bi-search me-1"></i> Buscar';
      }
    });
}
