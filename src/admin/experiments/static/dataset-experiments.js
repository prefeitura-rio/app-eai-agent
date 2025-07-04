// Configuração global
const API_BASE_URL =
  window.API_BASE_URL_OVERRIDE ||
  "https://services.staging.app.dados.rio/eai-agent";
const DATASET_ID = window.DATASET_ID;

// Estado da aplicação
let experimentsData = null;
let filteredExperiments = [];
let currentSort = { column: null, direction: null };
let searchTerm = "";

// Elementos DOM
const loadingScreen = document.getElementById("loading-screen");
const datasetExperimentsPanel = document.getElementById(
  "datasetExperimentsPanel"
);
const refreshDatasetBtn = document.getElementById("refreshDatasetBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const welcomeScreen = document.getElementById("welcome-screen");
const experimentsContainer = document.getElementById("experimentsContainer");
const alertArea = document.getElementById("alertArea");
const experimentsTableBody = document.getElementById(
  "experiments-table-body"
);
const experimentsTableHeader = document.getElementById(
  "experiments-table-header"
);
const experimentsCountBadge = document.getElementById(
  "experiments-count-badge"
);
const experimentSearchInput = document.getElementById("experiment-search");

// Elementos de dados do dataset
const datasetName = document.getElementById("dataset-name");

// Inicialização
document.addEventListener("DOMContentLoaded", function () {
  console.log(
    "DOM carregado - Inicializando página de experimentos do dataset:",
    DATASET_ID
  );

  if (!DATASET_ID || DATASET_ID === "{{DATASET_ID}}") {
    showAlert(
      "ID do dataset não encontrado. Redirecionando para a página de datasets...",
      "warning"
    );
    setTimeout(() => {
      window.location.href = "/eai-agent/admin/experiments/";
    }, 3000);
    return;
  }

  // Aguardar verificação de autenticação
  setTimeout(() => {
    if (AuthCheck.isAuthenticated()) {
      showDatasetPanel();
      loadExperimentsData();
    }
  }, 100);

  // Event listeners
  if (refreshDatasetBtn) {
    refreshDatasetBtn.addEventListener("click", loadExperimentsData);
  }

  // Add sorting event listeners
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("sortable-header")) {
      const column = e.target.getAttribute("data-column");
      const metricName = e.target.getAttribute("data-metric");
      sortExperiments(column, metricName);
    }
  });

  // Add search event listener
  if (experimentSearchInput) {
    experimentSearchInput.addEventListener("input", (e) => {
      searchTerm = e.target.value.toLowerCase().trim();
      applyFilter();
    });
  }
});

// Funções de UI
function showDatasetPanel() {
  if (loadingScreen) {
    loadingScreen.classList.add("d-none");
  }
  if (datasetExperimentsPanel) {
    datasetExperimentsPanel.classList.remove("d-none");
    datasetExperimentsPanel.classList.add("d-flex");
  }
}

// Funções de carregamento de dados
async function loadExperimentsData() {
  if (!AuthCheck.isAuthenticated()) {
    AuthCheck.redirectToAuth();
    return;
  }

  showLoading();
  clearAlerts();

  try {
    console.log("Carregando experimentos do dataset:", DATASET_ID);
    const response = await axios.get(
      `${API_BASE_URL}/admin/experiments/${DATASET_ID}/data`,
      {
        timeout: 30000,
      }
    );

    if (response.data && response.data.data && response.data.data.dataset) {
      experimentsData = response.data.data.dataset;
      applyFilter();
      hideWelcomeScreen();
    } else {
      throw new Error(
        "Formato de resposta inválido ou dataset não encontrado"
      );
    }
  } catch (error) {
    console.error("Erro ao carregar experimentos do dataset:", error);
    showAlert(
      "Erro ao carregar experimentos: " +
        (error.response?.data?.detail || error.message),
      "danger"
    );

    // Se o dataset não for encontrado, redirecionar após alguns segundos
    if (error.response?.status === 404) {
      setTimeout(() => {
        window.location.href = "/eai-agent/admin/experiments/";
      }, 3000);
    }
  } finally {
    hideLoading();
  }
}

function displayExperiments() {
  if (!experimentsData) return;

  // Atualizar nome do dataset
  datasetName.textContent = `Dataset: ${
    experimentsData.name || experimentsData.id || "Carregando..."
  }`;

  // Descobrir todas as métricas únicas disponíveis
  const allMetrics = new Set();
  filteredExperiments.forEach((experiment) => {
    if (experiment.annotationSummaries) {
      experiment.annotationSummaries.forEach((annotation) => {
        allMetrics.add(annotation.annotationName);
      });
    }
  });

  // Ordenar métricas de forma consistente
  const sortedMetrics = sortMetrics(Array.from(allMetrics));

  // Gerar cabeçalho da tabela dinamicamente
  generateTableHeader(sortedMetrics);

  // Limpar tabela
  experimentsTableBody.innerHTML = "";

  if (filteredExperiments.length === 0) {
    const totalColumns = 7 + allMetrics.size; // 7 colunas fixas + métricas dinâmicas
    const message = searchTerm
      ? `Nenhum experimento encontrado para "${searchTerm}"`
      : "Nenhum experimento encontrado para este dataset";

    experimentsTableBody.innerHTML = `
      <tr>
        <td colspan="${totalColumns}" class="text-center text-muted py-4">
          <i class="bi bi-flask" style="font-size: 2rem;"></i>
          <p class="mt-2 mb-0">${message}</p>
        </td>
      </tr>
    `;
    experimentsCountBadge.textContent = "0";
    experimentsContainer.classList.remove("d-none");
    return;
  }

  filteredExperiments.forEach((experiment) => {
    const row = createExperimentRow(experiment, sortedMetrics);
    experimentsTableBody.appendChild(row);
  });

  // Force table alignment after rendering
  forceTableAlignment();

  experimentsCountBadge.textContent = filteredExperiments.length;
  experimentsContainer.classList.remove("d-none");
}

// Function to force table alignment after rendering
function forceTableAlignment() {
  const table = document.querySelector(".experiments-table");
  if (!table) return;

  // Force header alignment
  const headers = table.querySelectorAll("thead th");
  headers.forEach((header, index) => {
    if (index < 3) {
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
      if (index < 3) {
        cell.style.textAlign = "left";
      } else {
        cell.style.textAlign = "center";
      }
    });
  });
}

function createExperimentRow(experiment, allMetrics) {
  const row = document.createElement("tr");
  row.style.cursor = "pointer";

  const createdAt = new Date(experiment.createdAt).toLocaleDateString(
    "pt-BR"
  );
  const createdTime = new Date(experiment.createdAt).toLocaleTimeString(
    "pt-BR",
    {
      hour: "2-digit",
      minute: "2-digit",
    }
  );
  const description = experiment.description || "Sem descrição";
  const errorRate = (experiment.errorRate * 100).toFixed(2);
  const latencyMs = experiment.averageRunLatencyMs
    ? experiment.averageRunLatencyMs.toFixed(2)
    : "N/A";

  // Gerar células para métricas dinamicamente
  const metricCells = allMetrics
    .map(
      (metric) =>
        `<td class="text-center align-middle" style="text-align: center !important;">${createMetricCell(
          experiment,
          metric
        )}</td>`
    )
    .join("");

  row.innerHTML = `
    <td class="align-middle" style="text-align: left !important;">
      <div class="d-flex align-items-center">
        <span class="badge bg-secondary me-2">#${
          experiment.sequenceNumber
        }</span>
        <div>
          <div class="fw-medium">${escapeHtml(experiment.name)}</div>
        </div>
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; white-space: normal; word-wrap: break-word;">
      <span>${escapeHtml(description)}</span>
    </td>
    <td class="align-middle" style="text-align: left !important;">
      <div>
        <div>${createdAt}</div>
        <small class="text-muted">${createdTime}</small>
      </div>
    </td>
    <td class="text-center align-middle" style="text-align: center !important;">
      <div class="fw-bold">${experiment.runCount}</div>
    </td>
    <td class="text-center align-middle" style="text-align: center !important;">
      <div><i class="bi bi-clock"></i> ${latencyMs}ms</div>
    </td>
    <td class="text-center align-middle" style="text-align: center !important;">
      <div>${errorRate}%</div>
    </td>
    ${metricCells}
    <td class="text-center align-middle" style="text-align: center !important;">
      <button class="btn btn-sm btn-outline-secondary download-metadata-btn" title="Download Metadata" data-experiment-id="${
        experiment.id
      }" data-experiment-name="${escapeHtml(experiment.name)}">
        <i class="bi bi-download"></i>
      </button>
    </td>
  `;

  // Adicionar evento de clique na linha
  row.addEventListener("click", (e) => {
    // Não navegar se clicou no botão
    if (e.target.closest("button")) return;
    viewExperiment(experiment.id);
  });

  // Adicionar evento de clique no botão de download
  const downloadBtn = row.querySelector(".download-metadata-btn");
  if (downloadBtn) {
    downloadBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      downloadExperimentMetadata(experiment.id, experiment.name);
    });
  }

  return row;
}

function generateTableHeader(metrics) {
  const fixedColumns = [
    { text: "Nome", display: "name", align: "left", column: "name" },
    {
      text: "Descrição",
      display: "description",
      align: "left",
      column: "description",
    },
    {
      text: "Criado em",
      display: "created at",
      align: "left",
      column: "createdAt",
    },
    {
      text: "Run<br/>Count",
      display: "run count",
      align: "center",
      column: "runCount",
    },
    {
      text: "Avg latency",
      display: "avg latency",
      align: "center",
      column: "averageRunLatencyMs",
    },
    {
      text: "Error<br/>Rate",
      display: "error rate",
      align: "center",
      column: "errorRate",
    },
  ];

  // Processar métricas para adicionar quebras de linha - métricas são numéricas (centralizadas)
  const metricColumns = metrics.map((metric) => ({
    text: formatMetricHeader(metric),
    display: metric,
    align: "center",
    column: "metric",
    metric: metric,
  }));

  const finalColumns = [
    ...fixedColumns,
    ...metricColumns,
    { text: "metadata", display: "metadata", align: "center", column: null },
  ];

  const headerHtml = `
    <tr>
      ${finalColumns
        .map((column) => {
          const alignClass =
            column.align === "center"
              ? "text-center align-middle"
              : "align-middle";
          const inlineStyle =
            column.align === "center"
              ? "text-align: center !important;"
              : "text-align: left !important;";

          const sortableClass = column.column ? "sortable-header" : "";
          const dataColumn = column.column
            ? `data-column="${column.column}"`
            : "";
          const dataMetric = column.metric
            ? `data-metric="${escapeHtml(column.metric)}"`
            : "";

          return `<th class="${alignClass} ${sortableClass}" style="${inlineStyle}" ${dataColumn} ${dataMetric} title="${escapeHtml(
            column.display
          )}">${column.text}</th>`;
        })
        .join("")}
    </tr>
  `;

  experimentsTableHeader.innerHTML = headerHtml;
}

function formatMetricHeader(metricName) {
  // Quebrar nomes longos em duas linhas
  const words = metricName.split(" ");

  if (words.length <= 2) {
    return escapeHtml(metricName);
  }

  // Para 3+ palavras, quebrar aproximadamente no meio
  const mid = Math.ceil(words.length / 2);
  const firstLine = words.slice(0, mid).join(" ");
  const secondLine = words.slice(mid).join(" ");

  return `${escapeHtml(firstLine)}<br/>${escapeHtml(secondLine)}`;
}

function createMetricCell(experiment, metricName) {
  const annotation = experiment.annotationSummaries?.find(
    (ann) => ann.annotationName === metricName
  );

  if (!annotation) {
    return '<small class="text-muted">-</small>';
  }

  const score = annotation.meanScore;
  const percentage = (score * 100).toFixed(0);

  // Determinar cor da barra baseada no score
  let barColor = "#6c757d"; // cinza padrão
  if (score >= 0.8) {
    barColor = "#198754"; // verde
  } else if (score >= 0.5) {
    barColor = "#ffc107"; // amarelo
  } else {
    barColor = "#dc3545"; // vermelho
  }

  return `
    <div>
      <div class="fw-bold mb-1">${score.toFixed(2)}</div>
      <div class="progress-container">
        <div class="progress-bar" style="width: ${percentage}%; background-color: ${barColor};" title="${escapeHtml(
    metricName
  )}: ${score.toFixed(3)}"></div>
      </div>
    </div>
  `;
}

function sortMetrics(metrics) {
  // Ordem preferida para métricas conhecidas
  const preferredOrder = [
    "Answer Similarity",
    "Answer Completeness",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
    "Response Quality",
    "Factual Accuracy",
    "Relevance Score",
    "Coherence",
    "Helpfulness",
    "Safety Score",
    "Bias Detection",
    "Toxicity Score",
  ];

  const sortedMetrics = [];

  // Primeiro, adicionar métricas na ordem preferida
  preferredOrder.forEach((metric) => {
    if (metrics.includes(metric)) {
      sortedMetrics.push(metric);
    }
  });

  // Depois, adicionar métricas desconhecidas em ordem alfabética
  const unknownMetrics = metrics
    .filter((metric) => !preferredOrder.includes(metric))
    .sort();

  return [...sortedMetrics, ...unknownMetrics];
}

function getShortMetricName(fullName) {
  const shortNames = {
    "Answer Similarity": "Sim",
    "Answer Completeness": "Comp",
    "Golden Link in Answer": "Link-A",
    "Golden Link in Tool Calling": "Link-T",
    "Activate Search Tools": "Search",
    "Response Quality": "Quality",
    "Factual Accuracy": "Accuracy",
    "Relevance Score": "Relevance",
    Coherence: "Coherence",
    Helpfulness: "Helpful",
    "Safety Score": "Safety",
    "Bias Detection": "Bias",
    "Toxicity Score": "Toxicity",
  };

  // Se temos um nome abreviado conhecido, usar ele
  if (shortNames[fullName]) {
    return shortNames[fullName];
  }

  // Caso contrário, gerar abreviação inteligente
  const words = fullName.split(/[\s_-]+/);

  if (words.length === 1) {
    // Uma palavra: pegar primeiras 4-6 letras
    return words[0].substring(0, Math.min(6, words[0].length));
  } else if (words.length === 2) {
    // Duas palavras: primeira letra de cada + resto da primeira
    return words[0].substring(0, 3) + words[1].substring(0, 1).toUpperCase();
  } else {
    // Três ou mais palavras: primeira letra de cada palavra
    return words
      .slice(0, 4)
      .map((word) => word.substring(0, 1).toUpperCase())
      .join("");
  }
}

function viewExperiment(experimentId) {
  console.log("Navegando para experimento:", experimentId);
  window.location.href = `/eai-agent/admin/experiments/${DATASET_ID}/${encodeURIComponent(
    experimentId
  )}`;
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

async function downloadExperimentMetadata(experimentId, experimentName) {
  try {
    showLoading();

    const response = await axios.get(
      `${API_BASE_URL}/admin/experiments/${DATASET_ID}/${encodeURIComponent(
        experimentId
      )}/data`,
      {
        timeout: 30000,
      }
    );

    if (response.data) {
      // Criar o arquivo JSON para download
      const jsonData = JSON.stringify(response.data, null, 2);
      const blob = new Blob([jsonData], { type: "application/json" });
      const url = URL.createObjectURL(blob);

      // Criar link para download
      const a = document.createElement("a");
      a.href = url;
      a.download = `experiment_${experimentName || experimentId}_data.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showAlert("Download do metadata realizado com sucesso!", "success");
    } else {
      throw new Error("Dados não encontrados");
    }
  } catch (error) {
    console.error("Erro ao baixar metadata do experimento:", error);
    showAlert(
      "Erro ao baixar metadata: " +
        (error.response?.data?.detail || error.message),
      "danger"
    );
  } finally {
    hideLoading();
  }
}

// Sorting functions
function sortExperiments(column, metricName) {
  if (!experimentsData || !experimentsData.experiments) return;

  const sortKey = metricName || column;

  // Determine sort direction
  if (currentSort.column === sortKey) {
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
    currentSort.column = sortKey;
    currentSort.direction = "asc";
  }

  // Update header classes
  updateSortHeaders();

  // Apply filter and sort
  applyFilter();
}

function getSortValue(experiment, column) {
  switch (column) {
    case "name":
      return experiment.name.toLowerCase();
    case "description":
      return (experiment.description || "").toLowerCase();
    case "createdAt":
      return new Date(experiment.createdAt);
    case "runCount":
      return experiment.runCount;
    case "averageRunLatencyMs":
      return experiment.averageRunLatencyMs || 0;
    case "errorRate":
      return experiment.errorRate;
    default:
      // Handle metrics
      const annotation = experiment.annotationSummaries?.find(
        (ann) => ann.annotationName === column
      );
      return annotation ? annotation.meanScore : -1;
  }
}

function updateSortHeaders() {
  const headers = document.querySelectorAll(".sortable-header");
  headers.forEach((header) => {
    const column = header.getAttribute("data-column");
    const metric = header.getAttribute("data-metric");
    const sortKey = metric || column;

    header.classList.remove("sort-asc", "sort-desc", "sort-active");

    if (currentSort.column === sortKey) {
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
  if (!experimentsData || !experimentsData.experiments) return;

  const experiments = experimentsData.experiments.edges.map(
    (edge) => edge.experiment
  );

  // First, filter the experiments
  if (searchTerm) {
    filteredExperiments = experiments.filter((experiment) =>
      experiment.name.toLowerCase().includes(searchTerm)
    );
  } else {
    filteredExperiments = [...experiments];
  }

  // Then, sort the filtered experiments
  if (currentSort.column && currentSort.direction) {
    filteredExperiments.sort((a, b) => {
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
    filteredExperiments.sort(
      (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
    );
  }

  // Re-render the table
  displayExperiments();
}

// Exportar funções globais necessárias
window.viewExperiment = viewExperiment;
