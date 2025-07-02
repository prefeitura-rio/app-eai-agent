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
    console.log(
      "Evento experimentsReady recebido, inicializando funcionalidades."
    );
    // Aguardar um momento para garantir que os elementos estejam prontos
    setTimeout(initializeExperimentsFunctionality, 100);
  });
});

// Funções de UI
function showExperimentsPanel() {
  if (experimentsPanel) {
    document.querySelector(".login-container").classList.add("d-none");
    experimentsPanel.classList.remove("d-none");
    setTimeout(initializeExperimentsFunctionality, 100);
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

  if (fetchExperimentBtn) {
    fetchExperimentBtn.addEventListener("click", fetchExperimentData);
  }

  if (experimentIdInput) {
    experimentIdInput.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        fetchExperimentData();
      }
    });
  }

  console.log("Event listeners attached");
}

// Função para buscar os dados do experimento através do proxy do backend
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

  // Prepara a UI para a requisição
  loadingIndicator.classList.remove("d-none");
  resultContainer.classList.add("d-none");
  alertArea.innerHTML = "";
  fetchExperimentBtn.disabled = true;
  fetchExperimentBtn.innerHTML =
    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';

  // A URL agora aponta para o nosso endpoint de proxy no backend.
  // O navegador fará a chamada para /eai-agent/admin/experiments/data?id=...
  const url = `data?id=${encodeURIComponent(expId)}`;
  console.log("Buscando dados via proxy do backend:", url);

  fetch(url, {
    headers: {
      Authorization: `Bearer ${currentToken}`,
      "Content-Type": "application/json",
    },
  })
    .then(async (response) => {
      // Se a resposta não for OK, tenta extrair o erro do corpo JSON
      if (!response.ok) {
        const errorData = await response.json().catch(() => null); // Tenta parsear JSON, se falhar retorna null
        const errorMessage =
          errorData?.detail ||
          `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
      }
      return response.json();
    })
    .then((data) => {
      // Sucesso
      resultJson.textContent = JSON.stringify(data, null, 2);
      resultContainer.classList.remove("d-none");
      showAlert("Experimento carregado com sucesso!", "success");
    })
    .catch((error) => {
      // Erros de rede ou erros retornados pelo nosso backend
      console.error("Erro ao buscar experimento:", error);
      showAlert(`Falha ao buscar o experimento: ${error.message}`, "danger");
    })
    .finally(() => {
      // Restaura a UI
      loadingIndicator.classList.add("d-none");
      fetchExperimentBtn.disabled = false;
      fetchExperimentBtn.innerHTML =
        '<i class="bi bi-search me-1"></i> Buscar';
    });
}
