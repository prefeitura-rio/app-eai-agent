// Configuração global
const API_BASE_URL =
  window.API_BASE_URL_OVERRIDE ||
  "https://services.staging.app.dados.rio/eai-agent";

// Estado da aplicação
let datasets = [];
let filteredDatasets = [];
let currentSort = { column: null, direction: null };
let searchTerm = "";

// Elementos DOM
const loadingScreen = document.getElementById("loading-screen");
const datasetsPanel = document.getElementById("datasetsPanel");
const refreshDatasetsBtn = document.getElementById("refreshDatasetsBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const welcomeScreen = document.getElementById("welcome-screen");
const datasetsContainer = document.getElementById("datasetsContainer");
const alertArea = document.getElementById("alertArea");
const datasetsTableBody = document.getElementById("datasets-table-body");
const datasetsCountBadge = document.getElementById("datasets-count-badge");
const datasetSearchInput = document.getElementById("dataset-search");

// Elementos do tema
const themeToggleBtn = document.getElementById("themeToggleBtn");
const themeIcon = document.getElementById("themeIcon");

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  // Inicializar tema
  initializeTheme();

  // Aguardar verificação de autenticação
  setTimeout(() => {
    if (AuthCheck.isAuthenticated()) {
      showDatasetsPanel();
      loadDatasets();
    }
  }, 100);

  // Event listeners
  if (refreshDatasetsBtn) {
    refreshDatasetsBtn.addEventListener("click", loadDatasets);
  }

  // Add sorting event listeners
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("sortable-header")) {
      const column = e.target.getAttribute("data-column");
      sortDatasets(column);
    }
  });

  // Add search event listener
  if (datasetSearchInput) {
    datasetSearchInput.addEventListener("input", (e) => {
      searchTerm = e.target.value.toLowerCase().trim();
      applyFilter();
    });
  }

  // Add theme toggle event listener
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", toggleTheme);
  }
});

// Funções de UI
function showDatasetsPanel() {
  if (loadingScreen) {
    loadingScreen.classList.add("d-none");
  }
  if (datasetsPanel) {
    datasetsPanel.classList.remove("d-none");
    datasetsPanel.classList.add("d-flex");
  }
}

// Funções de carregamento de dados
async function loadDatasets() {
  if (!AuthCheck.isAuthenticated()) {
    AuthCheck.redirectToAuth();
    return;
  }

  showLoading();
  clearAlerts();

  try {
    const response = await axios.get(
      `${API_BASE_URL}/admin/experiments/data`,
      {
        timeout: 30000,
      }
    );

    if (response.data && response.data.data && response.data.data.datasets) {
      datasets = response.data.data.datasets.edges.map((edge) => edge.node);
      applyFilter();
      hideWelcomeScreen();
    } else {
      throw new Error("Formato de resposta inválido");
    }
  } catch (error) {
    console.error("Erro ao carregar datasets:", error);
    showAlert(
      "Erro ao carregar datasets: " +
        (error.response?.data?.detail || error.message),
      "danger"
    );
  } finally {
    hideLoading();
  }
}

function displayDatasets() {
  datasetsTableBody.innerHTML = "";

  if (filteredDatasets.length === 0) {
    const message = searchTerm
      ? `Nenhum dataset encontrado para "${searchTerm}"`
      : "Nenhum dataset encontrado";

    datasetsTableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center text-muted py-4 align-middle">
                    <i class="bi bi-database" style="font-size: 2rem;"></i>
                    <p class="mt-2 mb-0">${message}</p>
                </td>
            </tr>
        `;
    datasetsCountBadge.textContent = "0";
    return;
  }

  filteredDatasets.forEach((dataset) => {
    const row = createDatasetRow(dataset);
    datasetsTableBody.appendChild(row);
  });

  datasetsCountBadge.textContent = filteredDatasets.length;
  datasetsContainer.classList.remove("d-none");

  // Force table alignment after rendering
  forceTableAlignment();
}

// Function to force table alignment after rendering
function forceTableAlignment() {
  const table = document.querySelector(".datasets-table");
  if (!table) return;

  // Force header alignment
  const headers = table.querySelectorAll("thead th");
  headers.forEach((header, index) => {
    if (index < 3 || index === 4) {
      header.style.textAlign = "left";
    } else {
      header.style.textAlign = "center";
    }
  });

  // Force cell alignment
  const rows = table.querySelectorAll("tbody tr");
  rows.forEach((row) => {
    const cells = row.querySelectorAll("td");
    cells.forEach((cell, index) => {
      if (index < 2 || index === 4) {
        cell.style.textAlign = "left";
      } else {
        cell.style.textAlign = "center";
      }
    });
  });
}

function createDatasetRow(dataset) {
  const row = document.createElement("tr");
  row.style.cursor = "pointer";

  const createdAt = new Date(dataset.createdAt).toLocaleString("pt-BR");
  const description = dataset.description || "Sem descrição";

  row.innerHTML = `
        <td class="align-middle" style="text-align: left !important;">
            <div class="d-flex align-items-center">
                <i class="bi bi-database me-2 text-primary"></i>
                <div>
                    <div class="fw-medium">${escapeHtml(dataset.name)}</div>
                </div>
            </div>
        </td>
        <td class="align-middle" style="text-align: left !important; white-space: normal; word-wrap: break-word;">
            <span>${escapeHtml(description)}</span>
        </td>
        <td class="text-center align-middle" style="text-align: center !important;">
            <span class="badge bg-info rounded-pill">${
              dataset.exampleCount
            }</span>
        </td>
        <td class="text-center align-middle" style="text-align: center !important;">
            <span class="badge bg-success rounded-pill">${
              dataset.experimentCount
            }</span>
        </td>
        <td class="align-middle" style="text-align: left !important;">
            <small class="text-muted">${createdAt}</small>
        </td>
    `;

  // Adicionar evento de clique na linha
  row.addEventListener("click", () => {
    viewDatasetExperiments(dataset.id);
  });

  return row;
}

function viewDatasetExperiments(datasetId) {
  window.location.href = `/eai-agent/admin/experiments/${datasetId}`;
}

// Funções de utilidade
function showLoading() {
  loadingIndicator.classList.remove("d-none");
}

function hideLoading() {
  loadingIndicator.classList.add("d-none");
}

function hideWelcomeScreen() {
  welcomeScreen.classList.add("d-none");
}

function showWelcomeScreen() {
  welcomeScreen.classList.remove("d-none");
}

function clearDatasets() {
  if (datasetsTableBody) {
    datasetsTableBody.innerHTML = "";
  }
  if (datasetsContainer) {
    datasetsContainer.classList.add("d-none");
  }
  showWelcomeScreen();
}

function showAlert(message, type = "info") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

  alertArea.appendChild(alertDiv);

  // Auto-remover após 5 segundos
  setTimeout(() => {
    if (alertDiv.parentNode) {
      alertDiv.remove();
    }
  }, 5000);
}

function clearAlerts() {
  alertArea.innerHTML = "";
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

// Sorting functions
function sortDatasets(column) {
  // Determine sort direction
  if (currentSort.column === column) {
    // Same column - toggle direction
    if (currentSort.direction === "asc") {
      currentSort.direction = "desc";
    } else if (currentSort.direction === "desc") {
      currentSort.direction = null;
      currentSort.column = null;
    } else {
      currentSort.direction = "asc";
    }
  } else {
    // Different column - start with ascending
    currentSort.column = column;
    currentSort.direction = "asc";
  }

  // Update header classes
  updateSortHeaders();

  // Apply filter and sort
  applyFilter();
}

function getSortValue(dataset, column) {
  switch (column) {
    case "name":
      return dataset.name.toLowerCase();
    case "description":
      return (dataset.description || "").toLowerCase();
    case "exampleCount":
      return dataset.exampleCount;
    case "experimentCount":
      return dataset.experimentCount;
    case "createdAt":
      return new Date(dataset.createdAt);
    default:
      return "";
  }
}

function updateSortHeaders() {
  const headers = document.querySelectorAll(".sortable-header");
  headers.forEach((header) => {
    const column = header.getAttribute("data-column");
    header.classList.remove("sort-asc", "sort-desc", "sort-active");

    if (currentSort.column === column) {
      header.classList.add("sort-active");
      if (currentSort.direction === "asc") {
        header.classList.add("sort-asc");
      } else if (currentSort.direction === "desc") {
        header.classList.add("sort-desc");
      }
    }
  });
}

// Filter and sort function
function applyFilter() {
  // First, filter the datasets
  if (searchTerm) {
    filteredDatasets = datasets.filter((dataset) =>
      dataset.name.toLowerCase().includes(searchTerm)
    );
  } else {
    filteredDatasets = [...datasets];
  }

  // Then, sort the filtered datasets
  if (currentSort.column && currentSort.direction) {
    filteredDatasets.sort((a, b) => {
      const aValue = getSortValue(a, currentSort.column);
      const bValue = getSortValue(b, currentSort.column);

      let comparison = 0;
      if (aValue < bValue) {
        comparison = -1;
      } else if (aValue > bValue) {
        comparison = 1;
      }

      return currentSort.direction === "asc" ? comparison : -comparison;
    });
  } else {
    // No sorting - restore original order (by creation date descending)
    filteredDatasets.sort(
      (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
    );
  }

  // Re-render the table
  displayDatasets();
}

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

// Exportar funções globais necessárias
window.viewDatasetExperiments = viewDatasetExperiments;
