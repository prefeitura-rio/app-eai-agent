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

// Estado dos examples
let examplesData = null;
let filteredExamples = [];
let exampleSearchTerm = "";
let allLoadedExamples = []; // Array para armazenar todos os examples carregados
let examplesHasNextPage = false;
let examplesEndCursor = null;
let isLoadingMoreExamples = false;

// Elementos DOM
const loadingScreen = document.getElementById("loading-screen");
const datasetExperimentsPanel = document.getElementById(
  "datasetExperimentsPanel"
);
const refreshDatasetBtn = document.getElementById("refreshDatasetBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const welcomeScreen = document.getElementById("welcome-screen");
const tabsContainer = document.getElementById("tabsContainer");
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
const experimentsContainer = tabsContainer; // Using tabsContainer as the experiments container

// Elementos dos examples
const examplesTableBody = document.getElementById("examples-table-body");
const examplesCountBadge = document.getElementById("examples-count-badge");
const exampleSearchInput = document.getElementById("example-search");
const examplesLoading = document.getElementById("examples-loading");

// Elementos de dados do dataset
const datasetName = document.getElementById("dataset-name");

// Elementos do tema
const themeToggleBtn = document.getElementById("themeToggleBtn");
const themeIcon = document.getElementById("themeIcon");

// Elementos de download
const downloadExamplesCsvBtn = document.getElementById(
  "downloadExamplesCsvBtn"
);
const downloadExperimentsCsvBtn = document.getElementById(
  "downloadExperimentsCsvBtn"
);

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

  // Inicializar tema
  initializeTheme();

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
      searchTerm = e.target.value.trim();
      applyFilter();
    });
  }

  // Add examples search event listener
  if (exampleSearchInput) {
    exampleSearchInput.addEventListener("input", (e) => {
      exampleSearchTerm = e.target.value.trim();
      applyExampleFilter();
    });
  }

  // Add tab change event listener
  document.addEventListener("shown.bs.tab", (e) => {
    if (e.target.id === "examples-tab" && !examplesData) {
      loadExamplesData();
    }
  });

  // Scroll infinito removido - agora usamos botão "Carregar Mais"

  // Add theme toggle event listener
  if (themeToggleBtn) {
    themeToggleBtn.addEventListener("click", toggleTheme);
  }

  // Add download CSV event listeners
  if (downloadExamplesCsvBtn) {
    downloadExamplesCsvBtn.addEventListener("click", downloadExamplesCsv);
  }
  if (downloadExperimentsCsvBtn) {
    downloadExperimentsCsvBtn.addEventListener(
      "click",
      downloadExperimentsCsv
    );
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

      // Atualizar contador de examples se disponível
      if (experimentsData.exampleCount !== undefined) {
        if (examplesCountBadge) {
          examplesCountBadge.textContent = experimentsData.exampleCount;
        }
      }

      applyFilter();
      hideWelcomeScreen();
    } else {
      // Mesmo com erro, mostrar o container das tabs
      hideWelcomeScreen();
      throw new Error(
        "Formato de resposta inválido ou dataset não encontrado"
      );
    }
  } catch (error) {
    console.error("Erro ao carregar experimentos do dataset:", error);

    // Mostrar container das tabs mesmo com erro
    hideWelcomeScreen();

    // Criar um dataset vazio para mostrar a mensagem de "nenhum experimento"
    experimentsData = {
      name: "Dataset não encontrado",
      experiments: { edges: [] },
    };

    // Aplicar filtro para mostrar a mensagem de "nenhum experimento"
    applyFilter();

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

    // Gerar cabeçalho mesmo quando não há experimentos
    generateTableHeader(sortedMetrics);

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
  tabsContainer.classList.remove("d-none");
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

  const experiments = experimentsData.experiments.edges
    ? experimentsData.experiments.edges.map((edge) => edge.experiment)
    : [];

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

// Examples functions
async function loadExamplesData(loadMore = false) {
  if (!AuthCheck.isAuthenticated()) {
    AuthCheck.redirectToAuth();
    return;
  }

  if (!loadMore) {
    showExamplesLoading();
    // Reset para primeira carga
    allLoadedExamples = [];
    examplesHasNextPage = false;
    examplesEndCursor = null;
  } else {
    isLoadingMoreExamples = true;
  }

  clearAlerts();

  try {
    console.log(
      "Carregando examples do dataset:",
      DATASET_ID,
      loadMore ? "(carregando mais)" : "(primeira carga)"
    );

    // Construir URL com parâmetros de paginação
    let url = `${API_BASE_URL}/admin/experiments/${DATASET_ID}/examples?first=100`;
    if (loadMore && examplesEndCursor) {
      url += `&after=${encodeURIComponent(examplesEndCursor)}`;
    }

    const response = await axios.get(url, {
      timeout: 30000,
    });

    if (response.data && response.data.data && response.data.data.dataset) {
      const datasetData = response.data.data.dataset;

      // Na primeira carga, definir examplesData
      if (!loadMore) {
        examplesData = datasetData;

        // Atualizar contador de examples com o número total
        if (examplesData.exampleCount !== undefined) {
          if (examplesCountBadge) {
            examplesCountBadge.textContent = examplesData.exampleCount;
          }
        }
      }

      // Adicionar novos examples ao array
      const newExamples =
        datasetData.examples?.edges?.map((edge) => edge.example) || [];
      allLoadedExamples = allLoadedExamples.concat(newExamples);

      // Atualizar informações de paginação
      const pageInfo = datasetData.examples?.pageInfo;
      if (pageInfo) {
        examplesHasNextPage = pageInfo.hasNextPage;
        examplesEndCursor = pageInfo.endCursor;
      }

      console.log(
        `🔄 Carregados ${newExamples.length} novos examples. Total: ${allLoadedExamples.length}. HasNextPage: ${examplesHasNextPage}`
      );

      applyExampleFilter();
    } else {
      throw new Error(
        "Formato de resposta inválido ou examples não encontrados"
      );
    }
  } catch (error) {
    console.error("Erro ao carregar examples do dataset:", error);
    showAlert(
      "Erro ao carregar examples: " +
        (error.response?.data?.detail || error.message),
      "danger"
    );
  } finally {
    if (!loadMore) {
      hideExamplesLoading();
    } else {
      isLoadingMoreExamples = false;
    }
  }
}

function displayExamples() {
  if (!examplesData) return;

  // Limpar tabela (mas manter estrutura para scroll infinito)
  examplesTableBody.innerHTML = "";

  // Limpeza simples - sem scroll infinito

  if (filteredExamples.length === 0) {
    const message = exampleSearchTerm
      ? `Nenhum example encontrado para "${exampleSearchTerm}"`
      : "Nenhum example encontrado para este dataset";

    examplesTableBody.innerHTML = `
      <tr>
        <td colspan="4" class="text-center text-muted py-4">
          <i class="bi bi-file-text" style="font-size: 2rem;"></i>
          <p class="mt-2 mb-0">${message}</p>
        </td>
      </tr>
    `;
    examplesCountBadge.textContent = "0";
    return;
  }

  filteredExamples.forEach((example, index) => {
    const row = createExampleRow(example, index + 1);
    examplesTableBody.appendChild(row);
  });

  // Mostrar informações de carregamento e botão "Carregar Mais"
  if (examplesData && examplesData.exampleCount) {
    const statusRow = document.createElement("tr");

    if (isLoadingMoreExamples) {
      // Mostra indicador de carregamento
      statusRow.innerHTML = `
        <td colspan="4" class="text-center py-3">
          <div class="spinner-border spinner-border-sm text-primary me-2" role="status">
            <span class="visually-hidden">Carregando...</span>
          </div>
          <small>Carregando mais examples...</small>
        </td>
      `;
    } else if (examplesHasNextPage) {
      // Mostra botão para carregar mais
      statusRow.innerHTML = `
        <td colspan="4" class="text-center text-info py-3">
          <i class="bi bi-info-circle me-2"></i>
          <strong>Mostrando ${allLoadedExamples.length} de ${examplesData.exampleCount} examples.</strong>
                     <br><button class="btn btn-sm btn-primary mt-2" onclick="loadExamplesData(true)">
             <i class="bi bi-plus-circle me-1"></i>Carregar Mais 100 Examples
           </button>
        </td>
      `;
    } else if (allLoadedExamples.length > 0) {
      // Mostra mensagem de conclusão
      statusRow.innerHTML = `
        <td colspan="4" class="text-center text-success py-3">
          <i class="bi bi-check-circle me-2"></i>
          <strong>Todos os ${examplesData.exampleCount} examples foram carregados.</strong>
        </td>
      `;
    }

    if (statusRow.innerHTML) {
      examplesTableBody.appendChild(statusRow);
    }
  }

  // Manter o contador total, não apenas os filtrados
  if (examplesData.exampleCount !== undefined) {
    examplesCountBadge.textContent = examplesData.exampleCount;
  } else {
    examplesCountBadge.textContent = filteredExamples.length;
  }
}

function createExampleRow(example, rowNumber) {
  const row = document.createElement("tr");
  row.style.cursor = "pointer";

  const exampleId = example.id.trim();
  const input = example.latestRevision?.input || {};
  const output = example.latestRevision?.output || {};
  const metadata = example.latestRevision?.metadata || {};

  // Formatear input e output para display completo
  const inputText = formatObjectForDisplay(input);
  const outputText = formatObjectForDisplay(output);

  // Formatear metadata sem espaços desnecessários
  let metadataJson = "";
  if (metadata && Object.keys(metadata).length > 0) {
    // Formatar JSON mantendo indentação mas removendo espaços extras
    metadataJson = JSON.stringify(metadata, null, 2)
      .trim() // Remove espaços no início e fim
      .replace(/\n{3,}/g, "\n\n"); // Limita quebras de linha consecutivas
  } else {
    metadataJson = "{}";
  }

  // Renderizar markdown para input e output
  const inputHtml = renderMarkdown(inputText);
  const outputHtml = renderMarkdown(outputText);

  row.innerHTML = `
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.5rem; width: 15%;">
      <div class="d-flex align-items-start flex-column">
        <span class="badge bg-secondary mb-1" style="font-size: 0.7rem;">#${rowNumber}</span>
        <div class="fw-medium" style="font-size: 0.8rem; word-wrap: break-word; overflow-wrap: break-word;">
          ${escapeHtml(exampleId)}
        </div>
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.5rem; width: 35%;">
      <div class="markdown-content" style="word-wrap: break-word; overflow-wrap: break-word; font-size: 0.9rem; line-height: 1.4;">
        ${inputHtml}
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.5rem; width: 35%;">
      <div class="markdown-content" style="word-wrap: break-word; overflow-wrap: break-word; font-size: 0.9rem; line-height: 1.4;">
        ${outputHtml}
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.5rem; width: 15%;">
      <div style="white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; font-family: monospace; font-size: 0.8rem; line-height: 1.3;">${escapeHtml(
        metadataJson
      )}</div>
    </td>
  `;

  // Adicionar evento de clique na linha
  row.addEventListener("click", (e) => {
    // Permitir seleção de texto - não navegar se o usuário está selecionando texto
    if (window.getSelection().toString()) {
      return;
    }
    viewExampleDetails(exampleId);
  });

  return row;
}

function formatObjectForDisplay(obj) {
  if (!obj || typeof obj !== "object") {
    return String(obj || "").trim();
  }

  // Se for um objeto simples, tentar extrair a primeira propriedade de string
  const entries = Object.entries(obj);
  if (entries.length === 0) return "";

  // Procurar por propriedades que parecem ser o conteúdo principal
  const contentKeys = [
    "mensagem_whatsapp_simulada",
    "golden_answer",
    "content",
    "text",
    "message",
  ];
  for (const key of contentKeys) {
    if (obj[key]) {
      return String(obj[key]).trim();
    }
  }

  // Se não encontrar chaves conhecidas, usar a primeira propriedade string
  for (const [key, value] of entries) {
    if (typeof value === "string" && value.length > 0) {
      return value.trim();
    }
  }

  // Fallback para JSON formatado
  return JSON.stringify(obj, null, 2);
}

function renderMarkdown(text) {
  if (!text || typeof text !== "string") {
    return "";
  }

  // Configurar marked para ser mais seguro
  if (typeof marked !== "undefined") {
    marked.setOptions({
      breaks: true,
      gfm: true,
      sanitize: false,
      smartLists: true,
      smartypants: false,
    });

    try {
      return marked.parse(text.trim());
    } catch (error) {
      console.warn("Erro ao renderizar markdown:", error);
      return escapeHtml(text.trim());
    }
  }

  // Fallback se marked não estiver disponível
  return escapeHtml(text.trim());
}

function viewExampleDetails(exampleId) {
  // Log para debug - funcionalidade pode ser expandida no futuro
  console.log("Clicou no example:", exampleId);
}

function applyExampleFilter() {
  if (!allLoadedExamples || allLoadedExamples.length === 0) return;

  // Filtrar examples dos carregados
  if (exampleSearchTerm) {
    filteredExamples = allLoadedExamples.filter((example) => {
      const input = formatObjectForDisplay(
        example.latestRevision?.input || {}
      );
      const output = formatObjectForDisplay(
        example.latestRevision?.output || {}
      );
      const searchContent = (input + " " + output).toLowerCase();
      return searchContent.includes(exampleSearchTerm);
    });
  } else {
    filteredExamples = [...allLoadedExamples];
  }

  // Re-render the table
  displayExamples();
}

function showExamplesLoading() {
  if (examplesLoading) {
    examplesLoading.classList.remove("d-none");
  }
}

function hideExamplesLoading() {
  if (examplesLoading) {
    examplesLoading.classList.add("d-none");
  }
}

// Scroll infinito removido - funcionalidade substituída por botão "Carregar Mais"

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

// Função para resetar estado dos examples (útil para debugging)
function resetExamplesState() {
  allLoadedExamples = [];
  examplesHasNextPage = false;
  examplesEndCursor = null;
  isLoadingMoreExamples = false;
  examplesData = null;
  filteredExamples = [];
}

// Funções de download CSV
async function downloadExamplesCsv() {
  if (!examplesData || !examplesData.exampleCount) {
    showAlert("Nenhum example disponível para download.", "warning");
    return;
  }

  // Mostrar indicador de carregamento
  const originalText = downloadExamplesCsvBtn.innerHTML;
  downloadExamplesCsvBtn.innerHTML =
    '<span class="spinner-border spinner-border-sm me-1"></span>Baixando todos os examples...';
  downloadExamplesCsvBtn.disabled = true;

  try {
    // Carregar todos os examples disponíveis
    const allExamples = [];
    let hasNextPage = true;
    let cursor = null;
    let pageCount = 0;

    while (hasNextPage) {
      pageCount++;
      console.log(`📥 Carregando página ${pageCount} para download CSV...`);

      // Atualizar texto do botão com progresso
      downloadExamplesCsvBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Carregando página ${pageCount}...`;

      let url = `${API_BASE_URL}/admin/experiments/${DATASET_ID}/examples?first=1000`;
      if (cursor) {
        url += `&after=${encodeURIComponent(cursor)}`;
      }

      const response = await axios.get(url, { timeout: 30000 });

      if (response.data && response.data.data && response.data.data.dataset) {
        const datasetData = response.data.data.dataset;
        const newExamples =
          datasetData.examples?.edges?.map((edge) => edge.example) || [];
        allExamples.push(...newExamples);

        const pageInfo = datasetData.examples?.pageInfo;
        hasNextPage = pageInfo?.hasNextPage || false;
        cursor = pageInfo?.endCursor;

        console.log(
          `✅ Página ${pageCount}: ${newExamples.length} examples. Total: ${allExamples.length}/${examplesData.exampleCount}`
        );
      } else {
        break;
      }
    }

    if (allExamples.length === 0) {
      showAlert("Nenhum example encontrado para download.", "warning");
      return;
    }

    // Preparar dados CSV
    const csvData = [];

    // Cabeçalho
    csvData.push(["Número", "ID", "Input", "Output", "Metadata"]);

    // Dados
    allExamples.forEach((example, index) => {
      const exampleId = example.id.trim();
      const input = formatObjectForDisplay(
        example.latestRevision?.input || {}
      );
      const output = formatObjectForDisplay(
        example.latestRevision?.output || {}
      );
      const metadata = JSON.stringify(example.latestRevision?.metadata || {});

      csvData.push([
        index + 1,
        exampleId,
        input.replace(/"/g, '""'), // Escapar aspas duplas
        output.replace(/"/g, '""'),
        metadata.replace(/"/g, '""'),
      ]);
    });

    console.log(
      `📊 Gerando arquivo CSV com ${allExamples.length} examples...`
    );
    downloadExamplesCsvBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>Gerando CSV...`;

    // Converter para CSV
    const csvContent = csvData
      .map((row) => row.map((field) => `"${field}"`).join(","))
      .join("\n");

    // Gerar nome do arquivo com dataset name e data
    const datasetName = (examplesData.name || DATASET_ID).replace(
      /[^a-zA-Z0-9_-]/g,
      "_"
    );
    const createdDate = new Date().toISOString().split("T")[0];
    const fileName = `${datasetName}_${createdDate}.csv`;

    // Download
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", fileName);
    link.style.visibility = "hidden";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    showAlert(
      `Download de ${allExamples.length} examples realizado com sucesso!`,
      "success"
    );
  } catch (error) {
    console.error("Erro ao baixar examples:", error);
    showAlert(
      "Erro ao baixar examples: " + (error.message || "Erro desconhecido"),
      "danger"
    );
  } finally {
    // Restaurar botão
    downloadExamplesCsvBtn.innerHTML = originalText;
    downloadExamplesCsvBtn.disabled = false;
  }
}

function downloadExperimentsCsv() {
  if (!filteredExperiments || filteredExperiments.length === 0) {
    showAlert("Nenhum experimento carregado para download.", "warning");
    return;
  }

  // Descobrir todas as métricas únicas
  const allMetrics = new Set();
  filteredExperiments.forEach((experiment) => {
    if (experiment.annotationSummaries) {
      experiment.annotationSummaries.forEach((annotation) => {
        allMetrics.add(annotation.annotationName);
      });
    }
  });

  const sortedMetrics = sortMetrics(Array.from(allMetrics));

  // Preparar dados CSV
  const csvData = [];

  // Cabeçalho
  const headers = [
    "Número",
    "Nome",
    "Descrição",
    "Criado em",
    "Run Count",
    "Avg Latency (ms)",
    "Error Rate (%)",
    ...sortedMetrics,
    "Download Link",
  ];
  csvData.push(headers);

  // Dados
  filteredExperiments.forEach((experiment, index) => {
    const createdAt = new Date(experiment.createdAt).toLocaleString("pt-BR");
    const description = experiment.description || "Sem descrição";
    const errorRate = (experiment.errorRate * 100).toFixed(2);
    const latencyMs = experiment.averageRunLatencyMs
      ? experiment.averageRunLatencyMs.toFixed(2)
      : "N/A";

    // Valores das métricas
    const metricValues = sortedMetrics.map((metric) => {
      const annotation = experiment.annotationSummaries?.find(
        (ann) => ann.annotationName === metric
      );
      return annotation ? annotation.meanScore.toFixed(3) : "";
    });

    // Link para download do experimento
    const downloadLink = `${window.location.origin}/eai-agent/admin/experiments/${DATASET_ID}/${experiment.id}`;

    const row = [
      experiment.sequenceNumber,
      experiment.name.replace(/"/g, '""'),
      description.replace(/"/g, '""'),
      createdAt,
      experiment.runCount,
      latencyMs,
      errorRate,
      ...metricValues,
      downloadLink,
    ];

    csvData.push(row);
  });

  // Converter para CSV
  const csvContent = csvData
    .map((row) => row.map((field) => `"${field}"`).join(","))
    .join("\n");

  // Gerar nome do arquivo com dataset name e data
  const datasetName = (experimentsData?.name || DATASET_ID).replace(
    /[^a-zA-Z0-9_-]/g,
    "_"
  );
  const createdDate = new Date().toISOString().split("T")[0];
  const fileName = `${datasetName}_experiments_${createdDate}.csv`;

  // Download
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);
  link.setAttribute("href", url);
  link.setAttribute("download", fileName);
  link.style.visibility = "hidden";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  showAlert(
    `Download de ${filteredExperiments.length} experimentos realizado com sucesso!`,
    "success"
  );
}

// Exportar funções globais necessárias
window.viewExperiment = viewExperiment;
window.loadExamplesData = loadExamplesData;
