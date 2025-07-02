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
      console.log("Config response status:", response.status);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.json();
    })
    .then((data) => {
      console.log("Config response data:", data);
      PHOENIX_ENDPOINT = data.phoenix_endpoint;

      console.log("Phoenix endpoint original:", PHOENIX_ENDPOINT);
      console.log("Current page protocol:", window.location.protocol);
      console.log("Current page URL:", window.location.href);

      // Avisar sobre possível problema de Mixed Content mas não converter automaticamente
      if (
        PHOENIX_ENDPOINT &&
        PHOENIX_ENDPOINT.startsWith("http://") &&
        window.location.protocol === "https:"
      ) {
        console.warn("⚠️  AVISO: Mixed Content detectado!");
        console.warn(
          "Phoenix endpoint está em HTTP mas a página está em HTTPS"
        );
        console.warn("Isso pode causar erros de Mixed Content no navegador");
        console.warn(
          "Recomenda-se configurar HTTPS no Phoenix ou usar proxy reverso"
        );
      }

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
      console.error("Erro detalhado ao buscar configuração:", error);
      console.error("Error stack:", error.stack);
      showAlert(
        `Não foi possível obter a configuração do servidor: ${error.message}`,
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

  console.log("=== FETCH EXPERIMENT DEBUG ===");
  console.log("Experiment ID:", expId);
  console.log("Phoenix Endpoint:", PHOENIX_ENDPOINT);
  console.log("Final URL:", url);
  console.log("Page Protocol:", window.location.protocol);
  console.log(
    "URL Protocol:",
    url.startsWith("https://")
      ? "HTTPS"
      : url.startsWith("http://")
      ? "HTTP"
      : "Unknown"
  );
  console.log("===============================");

  fetch(url, {
    headers: {
      Authorization: `Bearer ${currentToken}`,
      "Content-Type": "application/json",
    },
    mode: "cors",
  })
    .then((response) => {
      console.log("=== RESPONSE DEBUG ===");
      console.log("Response status:", response.status);
      console.log("Response statusText:", response.statusText);
      console.log("Response headers:", response.headers);
      console.log("Response URL:", response.url);
      console.log("Response type:", response.type);
      console.log("======================");

      if (!response.ok) {
        throw new Error(
          `HTTP ${response.status}: ${response.statusText} - URL: ${response.url}`
        );
      }
      return response.json();
    })
    .then((data) => {
      console.log("=== SUCCESS DEBUG ===");
      console.log("Data received:", data);
      console.log("Data type:", typeof data);
      console.log("Data keys:", Object.keys(data || {}));
      console.log("====================");

      if (resultJson) {
        resultJson.textContent = JSON.stringify(data, null, 2);
      }
      if (resultContainer) {
        resultContainer.classList.remove("d-none");
      }

      showAlert("Experimento carregado com sucesso!", "success");
    })
    .catch((error) => {
      console.error("=== ERROR DEBUG ===");
      console.error("Error message:", error.message);
      console.error("Error name:", error.name);
      console.error("Error stack:", error.stack);
      console.error("Error object:", error);
      console.error("==================");

      let errorMessage = "Erro desconhecido";

      if (
        error.name === "TypeError" &&
        error.message.includes("Failed to fetch")
      ) {
        if (
          url.includes("ERR_SSL_PROTOCOL_ERROR") ||
          (url.startsWith("https://") && PHOENIX_ENDPOINT.includes(":6006"))
        ) {
          errorMessage = `Erro SSL: O servidor Phoenix em ${PHOENIX_ENDPOINT} não suporta HTTPS. Configure o servidor para usar HTTPS ou use um proxy reverso.`;
        } else if (
          url.startsWith("http://") &&
          window.location.protocol === "https:"
        ) {
          errorMessage = `Erro de Mixed Content: O endpoint Phoenix está em HTTP (${url}) mas a página está em HTTPS. Configure HTTPS no Phoenix ou use um proxy reverso.`;
        } else {
          errorMessage = `Erro de rede: Não foi possível conectar ao endpoint ${url}. Verifique se o serviço está rodando e acessível.`;
        }
      } else {
        errorMessage = `${error.message}`;
      }

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
