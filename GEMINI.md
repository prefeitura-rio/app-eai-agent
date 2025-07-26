INSTRUCTIONS


Estou no meio de uma refatoracao, estou migrando um vanilla jss/html/css para nextjs

Estou na etapa de refazer a UI das paginas do src/frontend/app/experiments apartir dos arquivos originais listados na secao abaixo
É vital que vc examine os arquivos src/frontend/app/ para saber a nova estrutura do front

IMPORTANTE: iremos utilizar vanilla css + bootstrap! Bootstrap ja esta instalado

voce tem liberdade para introduzir novos styles no globals.css ou novos arquivos .css, app/components para styles que serao utilizados em multiplas paginas
ou experiments/components para as que serao utilizadas apenas nas paginas do experiments

Elabore um plano passo a passo e detalhado de como refazer a UI para seguir exatamente o padrao antigo

mantenha a autenticacao da forma que esta! ela ja esta funcionando bem. tambem nao remova os arquivos types 
e config eles estao funcionando bem dessa forma. A estrutura atual funciona bem, vc so deve focar em mudancas de UI/style
Seu plano ainda nao esta tao elaborado, vamos entrar mais no detalhe do que vc vai implementar de cada arquivo, qual é a fonte do arquivo que vai fornecer as mudancas e qual arquivo essas mudancas seram implementadas? Quero tudo muito bem detalhado

**Voce nao deve mudar os endpoints que adquire os dados, pois o backend foi modificado em relacao ao front antigo, foque apenas nas mudancas de UI/style**



# UI Refactoring Plan (Revised)

  Current State:

   * Project Setup: We have successfully removed all Tailwind CSS dependencies and established a new, modular styling
     architecture using CSS Modules and a global design system in globals.css.
   * Login Page: The login page (/login) has been completely redesigned with a modern, user-friendly interface that includes
     a theme toggle.
   * Home Page: The main dashboard (/) has been redesigned. It features a consistent, top-aligned header, a welcoming title,
     and a responsive two-column grid for navigation cards.
   * Experiments Page (`/experiments`):
       * The shared header is now fully responsive and displays context-aware titles and buttons.
       * The datasets table page is styled in a card, but we are still finalizing its responsiveness to ensure it looks
         perfect on all screen sizes.

  Next Steps:

   1. Finalize Datasets Table Responsiveness: Our immediate next step is to perfect the responsiveness of the datasets
      table on the /experiments page, ensuring it looks and functions correctly on all devices, especially on medium-sized
      screens.
   2. Refactor Dataset-Specific Page (`/experiments/[dataset_id]`): Once the main datasets page is complete, we will move
      on to the page for a specific dataset. This involves:
       * Implementing the tabbed interface to switch between "Experimentos" and "Exemplos".
       * Styling the "Experimentos" table, including the custom progress bars for metrics.
       * Styling the "Exemplos" table and implementing the "Load More" functionality.
   3. Refactor Experiment Details Page (`/experiments/[dataset_id]/[experiment_id]`): Finally, we will style the deepest
      level of the experiments section, focusing on a clear and organized presentation of the run details, comparisons, and
      evaluations.

  When you are ready to resume, we will pick up with perfecting the responsiveness of the datasets table.
### **Phase 4: Refactor Dataset-Specific Page (`/experiments/[dataset_id]`)**

1.  **Goal:** Replicate the tabbed UI from `dataset-experiments.html`.
2.  **Source Files:** `dataset-experiments.html`, `dataset-experiments.js`.
3.  **Target Files:**
    *   `src/frontend/app/experiments/components/dataset-experiments-client.tsx`
    *   `src/frontend/app/experiments/[dataset_id]/page.module.css`
4.  **Detailed Plan:**
    *   Create specific styles for the tabbed interface in `page.module.css`.
    *   The component will import these styles and apply them to the Bootstrap `nav-tabs`.
    *   The custom progress bars for metrics will be a reusable React component with its own CSS module (`ProgressBar.module.css`) to keep its logic and styling encapsulated.

### **Phase 5: Refactor Experiment Details Page (`/experiments/[dataset_id]/[experiment_id]`)**

1.  **Goal:** Style the experiment run details page consistently with the new design system.
2.  **Source Files:** `dataset-experiments.html` (for style inference).
3.  **Target Files:**
    *   `src/frontend/app/experiments/components/experiment-details-client.tsx`
    *   `src/frontend/app/experiments/[dataset_id]/[experiment_id]/page.module.css`
4.  **Detailed Plan:**
    *   The unique two-column layout for this page will be defined in its own `page.module.css`.
    *   The component will import these styles to structure the run list and the details view.
    *   The styling for cards and badges within this page will leverage the design tokens from `globals.css` and common component styles from the more general `experiments/page.module.css`.



ABAIXO OS ARQUIVOS ORIGINAIS


# Project Overview

## Overall Structure

```


└── static/
    ├── dataset-experiments.html
    ├── dataset-experiments.js
    ├── datasets.html
    ├── datasets.js
    ├── experiment.css
    ├── experiment.html
    └── experiment.js
```

## Folder `static`

### File `dataset-experiments.html`

Path: `static/dataset-experiments.html`


```html
<!DOCTYPE html>
<html lang="pt-BR" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Experimentos por Dataset</title>
    <!-- Libs -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>

    <!-- App CSS -->
    <link rel="stylesheet" href="/eai-agent/admin/experiments/static/experiment.css">
    <!-- Favicon -->
    <link rel="icon" href="{{BASE_API_URL}}/admin/experiments/favicon.ico" type="image/x-icon">
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-screen" class="d-flex justify-content-center align-items-center vh-100">
        <div class="text-center">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-3 text-muted">Verificando autenticação...</p>
        </div>
    </div>

    <!-- Painel Principal -->
    <div id="datasetExperimentsPanel" class="d-none d-flex flex-column vh-100">
        <!-- Global Header -->
        <header class="container-xl py-4">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                <div class="d-flex align-items-center gap-3">
                    <div>
                        <h1 class="h3 mb-0">Experimentos do Dataset</h1>
                        <small class="text-muted" id="dataset-name">Dataset: Carregando...</small>
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <a href="/eai-agent/admin/experiments/" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Voltar">
                        <i class="bi bi-arrow-left"></i>
                    </a>
                    <button id="refreshDatasetBtn" class="btn btn-outline-primary" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Atualizar">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button id="themeToggleBtn" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Tema">
                        <i class="bi bi-moon-fill" id="themeIcon"></i>
                    </button>
                    <button id="logoutBtn" class="btn btn-outline-danger" onclick="AuthCheck.logout()" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Sair">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- Main content area -->
        <div class="main-app-content flex-grow-1">
            <div class="container-xl py-4">
                <div id="loadingIndicator" class="d-none text-center my-5">
                    <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                </div>

                <div id="alertArea" class="mb-3"></div>

                <div id="welcome-screen" class="text-center text-muted p-5 border rounded bg-light">
                    <h3>Carregando dados do dataset...</h3>
                    <p class="mb-0">Aguarde enquanto buscamos os dados.</p>
                </div>

                <!-- Tabs Container -->
                <div id="tabsContainer" class="d-none">
                    <!-- Nav tabs -->
                    <ul class="nav nav-tabs" id="datasetTabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="experiments-tab" data-bs-toggle="tab" data-bs-target="#experiments" type="button" role="tab" aria-controls="experiments" aria-selected="true">
                                Experimentos (<span id="experiments-count-badge" class="fw-normal">0</span>)
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="examples-tab" data-bs-toggle="tab" data-bs-target="#examples" type="button" role="tab" aria-controls="examples" aria-selected="false">
                                Examples (<span id="examples-count-badge" class="fw-normal">0</span>)
                            </button>
                        </li>
                    </ul>

                    <!-- Tab content -->
                    <div class="tab-content" id="datasetTabContent">
                        <!-- Experiments Tab -->
                        <div class="tab-pane fade show active" id="experiments" role="tabpanel" aria-labelledby="experiments-tab">
                            <div class="card border-top-0">
                                <div class="card-header">
                                    <div class="d-flex align-items-center gap-3">
                                        <h5 class="mb-0">Experimentos</h5>
                                        <span class="text-muted">|</span>
                                        <div class="search-container">
                                            <i class="bi bi-search text-muted"></i>
                                            <input type="text" id="experiment-search" class="form-control" placeholder="Filtrar por nome do experimento..." style="width: 250px;">
                                        </div>
                                        <button id="downloadExperimentsCsvBtn" class="btn btn-sm btn-outline-success" title="Download CSV">
                                            <i class="bi bi-download me-1"></i>CSV
                                        </button>
                                    </div>
                                </div>
                                <div class="card-body p-0">
                                    <div class="table-responsive" id="experiments-table-container">
                                        <table class="table table-hover experiments-table mb-0">
                                            <thead class="table-light" id="experiments-table-header">
                                                <!-- Header will be dynamically generated -->
                                            </thead>
                                            <tbody id="experiments-table-body">
                                                <!-- Experiments will be populated here -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Examples Tab -->
                        <div class="tab-pane fade" id="examples" role="tabpanel" aria-labelledby="examples-tab">
                            <div class="card border-top-0">
                                <div class="card-header">
                                    <div class="d-flex align-items-center gap-3">
                                        <h5 class="mb-0">Examples</h5>
                                        <span class="text-muted">|</span>
                                        <div class="search-container">
                                            <i class="bi bi-search text-muted"></i>
                                            <input type="text" id="example-search" class="form-control" placeholder="Filtrar por conteúdo do exemplo..." style="width: 250px;">
                                        </div>
                                        <button id="downloadExamplesCsvBtn" class="btn btn-sm btn-outline-success" title="Download CSV">
                                            <i class="bi bi-download me-1"></i>CSV
                                        </button>
                                    </div>
                                </div>
                                <div class="card-body p-0">
                                    <div id="examples-loading" class="d-none text-center p-4">
                                        <div class="spinner-border text-primary" role="status">
                                            <span class="visually-hidden">Carregando examples...</span>
                                        </div>
                                    </div>
                                    <div class="table-responsive">
                                        <table class="table table-hover examples-table mb-0" style="table-layout: fixed;">
                                            <thead class="table-light">
                                                <tr>
                                                    <th class="align-middle" style="text-align: left !important; width: 15%;">ID</th>
                                                    <th class="align-middle" style="text-align: left !important; width: 35%;">Input</th>
                                                    <th class="align-middle" style="text-align: left !important; width: 35%;">Output</th>
                                                    <th class="align-middle" style="text-align: left !important; width: 15%;">Metadata</th>
                                                </tr>
                                            </thead>
                                            <tbody id="examples-table-body">
                                                <!-- Examples will be populated here -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal para detalhes do exemplo -->
    <div class="modal fade" id="exampleDetailsModal" tabindex="-1" aria-labelledby="exampleDetailsModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-xl modal-dialog-scrollable">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="exampleDetailsModalLabel">Detalhes do Exemplo</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <h6>ID do Exemplo: <span id="modalExampleId" class="fw-bold text-primary"></span></h6>
                    <hr>
                    <h5><i class="bi bi-arrow-right-circle me-2"></i>Input</h5>
                    <div id="modalExampleInput" class="markdown-content p-3 border rounded bg-light"></div>
                    <h5 class="mt-4"><i class="bi bi-arrow-left-circle me-2"></i>Output</h5>
                    <div id="modalExampleOutput" class="markdown-content p-3 border rounded bg-light"></div>
                    <h5 class="mt-4"><i class="bi bi-info-circle me-2"></i>Metadata</h5>
                    <pre class="bg-light p-3 border rounded"><code id="modalExampleMetadata"></code></pre>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Configuração global da API
        window.API_BASE_URL_OVERRIDE = '{{BASE_API_URL}}';
        
        // Injeta o dataset ID do backend
        window.DATASET_ID = '{{DATASET_ID}}';
        
        // Inicializar tooltips do Bootstrap com configurações otimizadas
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    delay: { show: 300, hide: 100 },
                    animation: true,
                    trigger: 'hover focus'
                });
            });
        });
    </script>
    <!-- Auth Check deve ser carregado PRIMEIRO -->
    <script src="/eai-agent/admin/experiments/static/auth-check.js"></script>
    <script src="/eai-agent/admin/experiments/static/dataset-experiments.js"></script>
</body>
</html> 
```


### File `dataset-experiments.js`

Path: `static/dataset-experiments.js`


```js
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

  // Sistema de carregamento por botão "Carregar Mais"

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

  // Link real para o experimento
  const experimentUrl = `/eai-agent/admin/experiments/${DATASET_ID}/${encodeURIComponent(
    experiment.id
  )}`;

  row.innerHTML = `
    <td class="align-middle" style="text-align: left !important;">
      <div class="d-flex align-items-center">
        <span class="badge bg-secondary me-2">#${
          experiment.sequenceNumber
        }</span>
        <div>
          <div class="fw-medium">
            <a href="${experimentUrl}" class="experiment-link">${escapeHtml(
    experiment.name
  )}</a>
          </div>
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
    ${metricCells}
    <td class="text-center align-middle" style="text-align: center !important;">
      <div class="fw-bold">${experiment.runCount}</div>
    </td>
    <td class="text-center align-middle" style="text-align: center !important;">
      <div><i class="bi bi-clock"></i> ${latencyMs}ms</div>
    </td>
    <td class="text-center align-middle" style="text-align: center !important;">
      <div>${errorRate}%</div>
    </td>
    <td class="text-center align-middle" style="text-align: center !important;">
      <button class="btn btn-sm btn-outline-secondary download-metadata-btn" title="Download Metadata" data-experiment-id="${
        experiment.id
      }" data-experiment-name="${escapeHtml(experiment.name)}">
        <i class="bi bi-download"></i>
      </button>
    </td>
  `;

  // Evento de clique na linha: ignora se for botão ou link
  row.addEventListener("click", (e) => {
    if (e.target.closest("button")) return;
    if (e.target.closest("a.experiment-link")) return;
    viewExperiment(experiment.id);
  });

  // Evento de clique no link: só intercepta clique simples para SPA
  const link = row.querySelector("a.experiment-link");
  if (link) {
    link.addEventListener("click", (e) => {
      if (
        e.button === 0 &&
        !e.ctrlKey &&
        !e.metaKey &&
        !e.shiftKey &&
        !e.altKey
      ) {
        e.preventDefault();
        viewExperiment(experiment.id);
      }
      // Qualquer outro caso, deixa o navegador agir normalmente
    });
  }

  // Evento de clique no botão de download
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
  // Processar métricas para exibir nomes completos - métricas são numéricas (centralizadas)
  const metricColumns = metrics.map((metric) => ({
    text: getShortMetricName(metric), // Using full names to avoid code changes when new metrics are added
    display: metric, // Keep full name for tooltip
    align: "center",
    column: "metric",
    metric: metric,
  }));

  const finalColumns = [
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
    ...metricColumns,
    {
      text: "Total<br/>Execuções",
      display: "total execuções",
      align: "center",
      column: "runCount",
    },
    {
      text: "Latência<br/>Média",
      display: "latência média",
      align: "center",
      column: "averageRunLatencyMs",
    },
    {
      text: "Taxa de<br/>Erro",
      display: "taxa de erro",
      align: "center",
      column: "errorRate",
    },
    {
      text: "Metadados",
      display: "Metadados",
      align: "center",
      column: null,
    },
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
          const metricClass = column.metric ? "metric-header" : "";
          const dataColumn = column.column
            ? `data-column="${column.column}"`
            : "";
          const dataMetric = column.metric
            ? `data-metric="${escapeHtml(column.metric)}"`
            : "";

          return `<th class="${alignClass} ${sortableClass} ${metricClass}" style="${inlineStyle}" ${dataColumn} ${dataMetric} title="${escapeHtml(
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
  let barClass = "metric-default";
  if (score >= 0.8) {
    barClass = "metric-high";
  } else if (score >= 0.5) {
    barClass = "metric-mid";
  } else {
    barClass = "metric-low";
  }

  return `
    <div>
      <div class="fw-bold mb-1">${score.toFixed(2)}</div>
      <div class="progress-container">
        <div class="progress-bar ${barClass}" style="width: ${percentage}%;" title="${escapeHtml(
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
  // Retornar o nome original completo para evitar ter que editar o código
  // quando novas métricas forem introduzidas
  return fullName;
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
    header.removeAttribute("aria-sort"); // Clear aria-sort attribute

    if (currentSort.column === sortKey) {
      header.classList.add("sort-active");
      if (currentSort.direction === "asc") {
        header.classList.add("sort-asc");
        header.setAttribute("aria-sort", "ascending"); // Add ARIA for accessibility
      } else if (currentSort.direction === "desc") {
        header.classList.add("sort-desc");
        header.setAttribute("aria-sort", "descending"); // Add ARIA for accessibility
      }
    } else {
      header.setAttribute("aria-sort", "none"); // Indicate sortable but not currently sorted
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
    isLoadingMoreExamples = false;
  } else {
    isLoadingMoreExamples = true;
    // Atualizar UI imediatamente para mostrar loading
    applyExampleFilter();
  }

  clearAlerts();

  try {
    console.log(
      "Carregando examples do dataset:",
      DATASET_ID,
      loadMore ? "(carregando mais)" : "(primeira carga)"
    );

    // Construir URL com parâmetros de paginação
    let url = `${API_BASE_URL}/admin/experiments/${DATASET_ID}/examples?first=1000`;
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
        `🔄 Carregados ${newExamples.length} novos examples. Total: ${allLoadedExamples.length}/${examplesData.exampleCount}. HasNextPage: ${examplesHasNextPage}`
      );

      // Aplicar filtro sempre para atualizar a UI
      // Mas resetar o estado de loading antes se for loadMore
      if (loadMore) {
        isLoadingMoreExamples = false;
        console.log(
          "🔄 isLoadingMoreExamples resetado para false ANTES do applyExampleFilter"
        );
      }
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
    }
    // O estado isLoadingMoreExamples já foi resetado no try block
  }
}

function displayExamples() {
  if (!examplesData) return;

  // Limpar tabela
  examplesTableBody.innerHTML = "";

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

    console.log(
      `🔍 Debug displayExamples: isLoadingMoreExamples=${isLoadingMoreExamples}, examplesHasNextPage=${examplesHasNextPage}, allLoadedExamples.length=${allLoadedExamples.length}, exampleCount=${examplesData.exampleCount}`
    );

    // Correção: Se não estamos carregando mais E há próxima página, mostrar botão
    // Se estivermos carregando mais, mostrar loading
    if (isLoadingMoreExamples) {
      // Mostra indicador de carregamento
      console.log("📝 Mostrando indicador de carregamento");
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
      console.log("🔘 Mostrando botão 'Carregar Mais'");
      console.log(
        `🔘 Condições: isLoadingMoreExamples=${isLoadingMoreExamples}, examplesHasNextPage=${examplesHasNextPage}`
      );
      statusRow.innerHTML = `
        <td colspan="4" class="text-center text-info py-3">
          <i class="bi bi-info-circle me-2"></i>
          <strong>Mostrando ${allLoadedExamples.length} de ${examplesData.exampleCount} examples.</strong>
                     <br><button class="btn btn-sm btn-primary mt-2" onclick="loadExamplesData(true)">
             <i class="bi bi-plus-circle me-1"></i>Carregar Mais 1000 Examples
           </button>
        </td>
      `;
    } else if (allLoadedExamples.length > 0) {
      // Mostra mensagem de conclusão
      console.log("✅ Mostrando mensagem de conclusão");
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

    // Se houver termo de busca E ainda há mais exemplos no servidor, mostrar opção de busca completa
    if (
      exampleSearchTerm &&
      examplesHasNextPage &&
      !isLoadingMoreExamples &&
      allLoadedExamples.length < examplesData.exampleCount
    ) {
      const searchStatusRow = document.createElement("tr");
      searchStatusRow.innerHTML = `
        <td colspan="4" class="text-center text-info py-3 border-top">
          <i class="bi bi-search me-2"></i>
          <strong>Pode haver mais resultados de busca.</strong>
          <br><button class="btn btn-sm btn-outline-info mt-2" onclick="loadAllExamplesForSearch()">
            <i class="bi bi-box-arrow-down me-1"></i>Carregar TODOS os Examples para Busca Completa
          </button>
          <br><small class="text-muted">Carregará ${
            examplesData.exampleCount - allLoadedExamples.length
          } examples restantes</small>
        </td>
      `;
      examplesTableBody.appendChild(searchStatusRow);
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
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.75rem 0.5rem;">
      <div class="d-flex align-items-start flex-column" style="gap: 0.25rem;">
        <span class="badge bg-secondary" style="font-size: 0.7rem; align-self: flex-start;">#${rowNumber}</span>
        <div class="fw-medium text-break" style="font-size: 0.8rem; word-wrap: break-word; overflow-wrap: break-word; max-width: 100%;">
          ${escapeHtml(exampleId)}
        </div>
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.75rem 0.5rem;">
      <div class="markdown-content" style="word-wrap: break-word; overflow-wrap: break-word; font-size: 0.9rem; line-height: 1.4;">
        ${inputHtml}
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.75rem 0.5rem;">
      <div class="markdown-content" style="word-wrap: break-word; overflow-wrap: break-word; font-size: 0.9rem; line-height: 1.4;">
        ${outputHtml}
      </div>
    </td>
    <td class="align-middle" style="text-align: left !important; vertical-align: top !important; padding: 0.75rem 0.5rem;">
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
      // sanitize: false removed for security - sanitization should be handled server-side
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
  const example = allLoadedExamples.find((e) => e.id.trim() === exampleId);
  if (!example) {
    console.warn("Example not found:", exampleId);
    showAlert("Exemplo não encontrado!", "warning");
    return;
  }

  // Populate modal with example data
  document.getElementById("modalExampleId").textContent = example.id;

  const inputText = formatObjectForDisplay(
    example.latestRevision?.input || {}
  );
  const outputText = formatObjectForDisplay(
    example.latestRevision?.output || {}
  );

  document.getElementById("modalExampleInput").innerHTML =
    renderMarkdown(inputText);
  document.getElementById("modalExampleOutput").innerHTML =
    renderMarkdown(outputText);

  // Format metadata as JSON
  let metadataJson = "{}";
  if (
    example.latestRevision?.metadata &&
    Object.keys(example.latestRevision.metadata).length > 0
  ) {
    metadataJson = JSON.stringify(example.latestRevision.metadata, null, 2);
  }
  document.getElementById("modalExampleMetadata").textContent = metadataJson;

  // Show the modal
  const exampleDetailsModal = new bootstrap.Modal(
    document.getElementById("exampleDetailsModal")
  );
  exampleDetailsModal.show();
}

function applyExampleFilter() {
  if (!allLoadedExamples || allLoadedExamples.length === 0) return;

  console.log(
    `🔍 applyExampleFilter chamado - allLoadedExamples: ${allLoadedExamples.length}, isLoadingMoreExamples: ${isLoadingMoreExamples}`
  );

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

  console.log(
    `🔍 filteredExamples: ${filteredExamples.length}, chamando displayExamples()`
  );

  // Re-render the table
  displayExamples();
}

// Nova função para carregar todos os exemplos especificamente para a busca
async function loadAllExamplesForSearch() {
  // Temporariamente desativar o input de busca
  const searchInput = document.getElementById("example-search");
  if (searchInput) {
    searchInput.disabled = true;
  }

  // Mostrar loading enquanto todos são carregados
  showExamplesLoading();

  try {
    // Chamar loadExamplesData em loop até hasNextPage ser false
    while (examplesHasNextPage) {
      await loadExamplesData(true); // loadMore = true
      // Pequeno atraso para evitar bloquear o navegador
      await new Promise((resolve) => setTimeout(resolve, 50));
    }

    // Reaplicar filtro agora que todos os dados estão carregados
    applyExampleFilter();

    showAlert(
      `Todos os ${allLoadedExamples.length} examples foram carregados. Busca completa aplicada!`,
      "success"
    );
  } catch (error) {
    console.error("Erro ao carregar todos os examples:", error);
    showAlert(
      "Erro ao carregar todos os examples: " + error.message,
      "danger"
    );
  } finally {
    hideExamplesLoading();
    if (searchInput) {
      searchInput.disabled = false;
      searchInput.focus(); // Return focus to search input
    }
  }
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

// Funcionalidade de carregamento por botão "Carregar Mais"

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
    csvData.push(["Número", "ID", "Entrada", "Saída", "Metadados"]);

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
    ...sortedMetrics,
    "Total Execuções",
    "Avg Latency (ms)",
    "Error Rate (%)",
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
      ...metricValues,
      experiment.runCount,
      latencyMs,
      errorRate,
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
window.loadAllExamplesForSearch = loadAllExamplesForSearch;

```


### File `datasets.html`

Path: `static/datasets.html`


```html
<!DOCTYPE html>
<html lang="pt-BR" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Datasets</title>
    <!-- Libs -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>

    <!-- App CSS -->
    <link rel="stylesheet" href="/eai-agent/admin/experiments/static/experiment.css">
    <!-- Favicon -->
    <link rel="icon" href="{{BASE_API_URL}}/admin/experiments/favicon.ico" type="image/x-icon">
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-screen" class="d-flex justify-content-center align-items-center vh-100">
        <div class="text-center">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-3 text-muted">Verificando autenticação...</p>
        </div>
    </div>

    <!-- Painel Principal -->
    <div id="datasetsPanel" class="d-none flex-column vh-100">
        <!-- Global Header -->
        <header class="container-xl py-4">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                <h1 class="h3 mb-0 me-4">Painel de Datasets</h1>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <button id="refreshDatasetsBtn" class="btn btn-outline-primary" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Atualizar">
                        <i class="bi bi-arrow-clockwise"></i>
                    </button>
                    <button id="themeToggleBtn" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Tema">
                        <i class="bi bi-moon-fill" id="themeIcon"></i>
                    </button>
                    <button id="logoutBtn" class="btn btn-outline-danger" onclick="AuthCheck.logout()" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Sair">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- Main content area -->
        <div class="main-app-content flex-grow-1">
            <div class="container-xl py-4">
                <div id="loadingIndicator" class="d-none text-center my-5">
                    <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                </div>

                <div id="alertArea" class="mb-3"></div>

                <div id="welcome-screen" class="text-center text-muted p-5 border rounded bg-light">
                    <h3>Bem-vindo ao Painel de Datasets</h3>
                    <p class="mb-0">Carregando datasets disponíveis...</p>
                </div>

                <!-- Datasets Container -->
                <div id="datasetsContainer" class="d-none">
                    <div class="row">
                        <div class="col-12">
                            <div class="card">
                                <div class="card-header">
                                    <div class="d-flex align-items-center gap-3">
                                        <h5 class="mb-0">Datasets Disponíveis (<span id="datasets-count-badge" class="fw-normal"></span>)</h5>
                                        <span class="text-muted">|</span>
                                        <div class="search-container">
                                            <i class="bi bi-search text-muted"></i>
                                            <input type="text" id="dataset-search" class="form-control" placeholder="Filtrar por nome do dataset..." style="width: 250px;">
                                        </div>
                                    </div>
                                </div>
                                <div class="card-body p-0">
                                    <div class="table-responsive">
                                        <table class="table table-hover datasets-table mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th class="align-middle sortable-header" style="text-align: left !important;" data-column="name">Nome</th>
                                                    <th class="align-middle sortable-header" style="text-align: left !important;" data-column="description">Descrição</th>
                                                    <th class="text-center align-middle sortable-header" style="text-align: center !important;" data-column="exampleCount">Exemplos</th>
                                                    <th class="text-center align-middle sortable-header" style="text-align: center !important;" data-column="experimentCount">Experimentos</th>
                                                    <th class="align-middle sortable-header" style="text-align: left !important;" data-column="createdAt">Criado em</th>
                                                </tr>
                                            </thead>
                                            <tbody id="datasets-table-body">
                                                <!-- Datasets will be populated here -->
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Configuração global da API
        window.API_BASE_URL_OVERRIDE = '{{BASE_API_URL}}';
        
        // Inicializar tooltips do Bootstrap com configurações otimizadas
        document.addEventListener('DOMContentLoaded', function() {
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    delay: { show: 300, hide: 100 },
                    animation: true,
                    trigger: 'hover focus'
                });
            });
        });
    </script>
    <!-- Auth Check deve ser carregado PRIMEIRO -->
    <script src="/eai-agent/admin/experiments/static/auth-check.js"></script>
    <script src="/eai-agent/admin/experiments/static/datasets.js"></script>
</body>
</html> 
```


### File `datasets.js`

Path: `static/datasets.js`


```js
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
  console.log("DOM carregado - Inicializando aplicação de datasets");

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
    console.log("Carregando datasets...");
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
  console.log("Navegando para experimentos do dataset:", datasetId);
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

```


### File `experiment.css`

Path: `static/experiment.css`


```css
/*
 * Unified and Clean CSS for Experiment Dashboard
 * Centralized design system with consistent color usage
 */

/* === DESIGN SYSTEM === */
:root {
    /* Core Colors */
    --color-bg: #F8FAFC;
    --color-surface: #FFFFFF;
    --color-surface-hover: #F0F3F7;
    --color-surface-code: #F5F7FA;
    
    /* Text Colors */
    --color-text: #2C3E50;
    --color-text-muted: #7F8C8D;
    --color-text-link: #3498DB;
    
    /* Brand */
    --color-primary: #0A74DA;
    --color-primary-light: #E6F3FC;
    
    /* Status Colors */
    --color-success: #2ECC71;
    --color-warning: #F39C12;
    --color-danger: #E74C3C;
    --color-info: #3498DB;
    
    /* Borders & Shadows */
    --color-border: #EAECEF;
    --color-border-strong: #D5DBDE;
    --color-shadow: rgba(0, 0, 0, 0.08);
    
    /* Table Specific */
    --color-table-header: var(--color-surface-hover);
    --color-table-hover: var(--color-primary-light);
    
    /* Progress Bar Colors */
    --color-metric-high: var(--color-success);
    --color-metric-mid: var(--color-warning);
    --color-metric-low: var(--color-danger);
    --color-metric-default: #6c757d;
}

[data-bs-theme="dark"] {
    /* Core Colors */
    --color-bg: #1A2129;
    --color-surface: #222B36;
    --color-surface-hover: #2E3A46;
    --color-surface-code: #161B22;
    
    /* Text Colors */
    --color-text: #E0E6EF;
    --color-text-muted: #9BAAB8;
    --color-text-link: #6FC3FF;
    
    /* Brand */
    --color-primary: #6FC3FF;
    --color-primary-light: rgba(111, 195, 255, 0.15);
    
    /* Status Colors */
    --color-success: #52D887;
    --color-warning: #DAA000;
    --color-danger: #FF7B7B;
    --color-info: #6FC3FF;
    
    /* Borders & Shadows */
    --color-border: #3A4753;
    --color-border-strong: #4D5C6B;
    --color-shadow: rgba(0, 0, 0, 0.3);
    
    /* Progress Bar Colors */
    --color-metric-high: var(--color-success);
    --color-metric-mid: var(--color-warning);
    --color-metric-low: var(--color-danger);
    --color-metric-default: #6c757d;
}

/* === BASE STYLES === */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body {
    height: 100%;
    margin: 0;
    padding: 0;
    overflow: hidden;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background-color: var(--color-bg);
    color: var(--color-text);
}

/* === TYPOGRAPHY === */
h1, h2, h3, h4, h5, h6 {
    font-family: inherit;
    line-height: 1.3;
    margin-bottom: 0.75rem;
    color: var(--color-text);
}

h1 { font-size: 2.5rem; font-weight: 700; }
h2 { font-size: 2rem; font-weight: 600; }
h3 { font-size: 1.5rem; font-weight: 600; }
h4 { font-size: 1.25rem; font-weight: 500; }
h5 { font-size: 1.125rem; font-weight: 500; }
h6 { font-size: 1rem; font-weight: 500; }

.text-muted, small {
    color: var(--color-text-muted);
    font-size: 0.875rem;
}

code, pre {
    font-family: 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
    font-size: 0.95em;
}

/* === LAYOUT === */
#experimentsPanel {
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
}

/* Reduce header padding aggressively */
#experimentsPanel header.py-4 {
    padding-top: 1rem !important;
    padding-bottom: 0.5rem !important;
    padding-right: 3rem !important;
}

.main-app-content {
    display: flex;
    flex-direction: row;
    flex-grow: 1;
    overflow: hidden;
    gap: 0.5rem;
    padding: 1rem 0.5rem;
}

#run-list-panel {
    width: 350px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    background-color: var(--color-surface);
    border-radius: 0.75rem;
    box-shadow: 0 4px 16px var(--color-shadow);
    overflow: hidden;
}

#run-list {
    overflow-y: auto;
    flex-grow: 1;
}

#main-content-wrapper {
    flex-grow: 1;
    overflow-y: auto;
    background-color: var(--color-bg);
    border-radius: 0.75rem;
    padding: 0 1rem;
}

/* === COMPONENTS === */
.card-component {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 4px 16px var(--color-shadow);
}

#metadataContainer .card-component h4 {
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px dashed var(--color-border);
}

/* Metadata grid optimization - 4 columns */
.metadata-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem 1rem;
    align-items: start;
}

.metadata-item {
    margin-bottom: 0.25rem;
}

.metadata-item-full-width {
    grid-column: 1 / -1;
    margin-top: 0.5rem;
    margin-bottom: 0.5rem;
}

.metadata-item-full-width:first-of-type {
    margin-top: 0;
}

/* System prompts back to vertical layout */

/* Optimize prompt section spacing */
.metadata-item-full-width .d-flex {
    margin-bottom: 0.5rem;
}

.metadata-item-full-width .collapse {
    margin-top: 0.5rem !important;
}

.metadata-item-full-width pre {
    margin: 0;
    background-color: var(--color-surface-code);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 1rem;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* Better button styling for metadata */
.metadata-item-full-width .btn-sm {
    font-size: 0.75rem;
    padding: 0.15rem 0.4rem;
    border-radius: 0.375rem;
    line-height: 1.2;
    min-height: auto;
}

.list-group-item {
    cursor: pointer;
    border: none;
    border-bottom: 1px solid var(--color-border);
    background-color: transparent;
    padding: 0.5rem 0.75rem;
    transition: all 0.3s ease;
    font-size: 1rem;
    line-height: 1.3;
}

.list-group-item.active {
    background-color: var(--color-primary-light);
    color: var(--color-primary);
    border-left: 4px solid var(--color-primary);
    font-weight: 600;
}

.list-group-item:hover {
    background-color: var(--color-surface-hover);
    transform: translateX(4px);
}

/* === BUTTONS === */
.btn-primary {
    background-color: var(--color-primary);
    border-color: var(--color-primary);
    color: white;
    font-weight: 500;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 8px var(--color-shadow);
    transition: all 0.3s ease;
}

.btn-primary:hover {
    background-color: var(--color-primary);
    border-color: var(--color-primary);
    transform: translateY(-1px);
    box-shadow: 0 4px 16px var(--color-shadow);
}

.btn-outline-primary { border-color: var(--color-primary); color: var(--color-primary); }
.btn-outline-secondary { border-color: var(--color-text-muted); color: var(--color-text-muted); }
.btn-outline-success { border-color: var(--color-success); color: var(--color-success); }
.btn-outline-warning { border-color: var(--color-warning); color: var(--color-warning); }
.btn-outline-danger { border-color: var(--color-danger); color: var(--color-danger); }
.btn-outline-info { border-color: var(--color-info); color: var(--color-info); }

.btn-outline-primary:hover { background-color: var(--color-primary); border-color: var(--color-primary); color: white; }
.btn-outline-secondary:hover { background-color: var(--color-text-muted); border-color: var(--color-text-muted); color: white; }
.btn-outline-success:hover { background-color: var(--color-success); border-color: var(--color-success); color: white; }
.btn-outline-warning:hover { background-color: var(--color-warning); border-color: var(--color-warning); color: white; }
.btn-outline-danger:hover { background-color: var(--color-danger); border-color: var(--color-danger); color: white; }
.btn-outline-info:hover { background-color: var(--color-info); border-color: var(--color-info); color: white; }

/* === FORMS === */
.form-control {
    background-color: var(--color-surface);
    border-color: var(--color-border);
    color: var(--color-text);
    border-radius: 0.5rem;
    padding: 0.75rem 1rem;
    transition: all 0.2s ease;
}

.form-control:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.2rem var(--color-primary-light);
    background-color: var(--color-surface);
    color: var(--color-text);
}

.form-control::placeholder {
    color: var(--color-text-muted);
}

/* === TABLES === */
.table {
    background-color: var(--color-surface);
    color: var(--color-text);
    margin-bottom: 0;
}

.table th {
    background-color: var(--color-table-header);
    color: var(--color-text);
    font-size: 0.85rem;
    font-weight: 600;
    padding: 0.75rem 1rem;
    border-bottom: 2px solid var(--color-border-strong);
    position: sticky;
    top: 0;
    z-index: 10;
    box-shadow: 0 2px 4px var(--color-shadow);
}

.table td {
    padding: 0.8rem 1rem;
    font-size: 0.9rem;
    vertical-align: middle;
    border-bottom: 1px solid var(--color-border-strong);
    color: var(--color-text);
}

.table tbody tr:hover {
    background-color: var(--color-table-hover);
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.table-responsive {
    overflow-x: auto;
    overflow-y: auto;
    max-height: 70vh;
    position: relative;
}

/* Table Alignment */
.table th:nth-child(1), .table th:nth-child(2), .table th:nth-child(3),
.table td:nth-child(1), .table td:nth-child(2), .table td:nth-child(3) {
    text-align: left !important;
}

.table th:nth-child(n+4), .table td:nth-child(n+4) {
    text-align: center !important;
}

/* Column Sizing */
.table td:nth-child(1) { min-width: 160px; max-width: 220px; }
.table td:nth-child(2) { 
    min-width: 250px; 
    max-width: 400px; 
    white-space: normal !important; 
    word-wrap: break-word !important; 
    line-height: 1.4; 
}

/* === METRICS & PROGRESS === */
.metric-header {
    white-space: normal !important;
    word-wrap: break-word !important;
    min-width: 80px;
    max-width: 120px;
    line-height: 1.2;
    padding: 0.5rem 0.25rem !important;
}

.progress-container {
    width: 60px;
    height: 6px;
    background-color: var(--color-border);
    border-radius: 99px;
    overflow: hidden;
    margin: 0 auto;
}

.progress-bar {
    height: 100%;
    border-radius: 99px;
    transition: width 0.3s ease;
}

/* Metric Score Classes */
.score-high, .metric-high { background-color: var(--color-metric-high) !important; }
.score-mid, .metric-mid { background-color: var(--color-metric-mid) !important; }
.score-low, .metric-low { background-color: var(--color-metric-low) !important; }
.metric-default { background-color: var(--color-metric-default) !important; }

/* === BADGES === */
.badge.bg-secondary {
    background-color: var(--color-surface-hover) !important;
    color: var(--color-text-muted) !important;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 0.25rem 0.5rem;
}

.badge.rounded-pill {
    font-size: 0.8rem;
    font-weight: 500;
    padding: 0.5rem 1rem;
    min-width: 2.5rem;
    text-align: center;
    border-radius: 1rem;
}

/* === FILTERS === */
.filter-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    align-items: start;
}

.filter-grid > div {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.filter-grid label {
    height: 2.5rem;
    display: flex;
    align-items: center;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}

.filter-grid .form-select {
    flex: 1;
    min-height: 2rem;
}

/* === SEARCH === */
.search-container {
    position: relative;
}

.search-container .form-control {
    border-radius: 20px;
    padding-left: 2.5rem;
    transition: all 0.2s ease;
}

.search-container .bi-search {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    z-index: 2;
    color: var(--color-text-muted);
}

/* === SORTING === */
.sortable-header {
    cursor: pointer;
    user-select: none;
    position: relative;
    padding-right: 20px !important;
    transition: background-color 0.2s ease;
}

.sortable-header:hover {
    background-color: var(--color-primary-light) !important;
}

.sortable-header::after {
    content: '↕';
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.8rem;
    color: var(--color-text-muted);
    opacity: 0.5;
}

.sortable-header.sort-asc::after {
    content: '↑';
    color: var(--color-primary);
    opacity: 1;
}

.sortable-header.sort-desc::after {
    content: '↓';
    color: var(--color-primary);
    opacity: 1;
}

.sortable-header.sort-active {
    background-color: var(--color-primary-light) !important;
    font-weight: 600;
}

/* === SUMMARY METRICS === */
.summary-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

@media (min-width: 1200px) {
    .summary-grid {
        grid-template-columns: repeat(5, 1fr);
    }
}

@media (min-width: 1400px) {
    .summary-grid {
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }
}

.summary-metric-card {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.75rem;
    padding: 1rem;
    transition: all 0.3s ease;
}

.summary-metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px var(--color-shadow);
}

.summary-metric-card {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.summary-metric-card h6 {
    color: var(--color-text-muted);
    margin-bottom: 0.75rem;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    line-height: 1.2;
    min-height: 2.4rem;
    display: flex;
    align-items: center;
}

.metric-main-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--color-text);
    margin-bottom: 0.75rem;
}

.metric-distribution-header {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.distribution-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}

.distribution-bar-bg {
    flex-grow: 1;
    height: 4px;
    background-color: var(--color-border);
    border-radius: 99px;
    overflow: hidden;
}

.distribution-bar {
    height: 100%;
    background-color: var(--color-primary);
    border-radius: 99px;
    transition: width 0.3s ease;
}

/* === EVALUATION CARDS === */
.evaluation-card {
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 1.5rem;
    margin-bottom: 2rem;
    background-color: var(--color-surface);
    box-shadow: 0 4px 16px var(--color-shadow);
}

.evaluation-card .score {
    font-size: 1.1rem;
    font-weight: bold;
    padding: 0.25rem 0.75rem;
    border-radius: 99px;
    color: white;
}

.explanation {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px dashed var(--color-border);
}

/* Evaluation explanation content boxes */
.explanation .collapse {
    margin-top: 0.5rem;
}

.explanation .collapse > div,
.explanation .collapse > pre,
.explanation .collapse > code {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.375rem;
    padding: 0.75rem;
    margin: 0;
}

/* JSON content in evaluations - immediate styling */
.evaluation-json-code {
    background-color: var(--color-surface-code) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0.375rem !important;
    padding: 0.75rem !important;
    margin: 0 !important;
    font-family: 'SFMono-Regular', Menlo, Monaco, Consolas, monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.4 !important;
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
}

.evaluation-json-code code {
    background: transparent !important;
    padding: 0 !important;
    color: var(--color-text) !important;
}

/* Fallback for existing classes */
.explanation .collapse pre {
    background-color: var(--color-surface-code) !important;
    font-family: 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
    font-size: 0.8rem;
    line-height: 1.4;
    white-space: pre-wrap;
    word-wrap: break-word;
}

/* Markdown content in evaluations */
.explanation .collapse .markdown-content {
    background-color: var(--color-surface) !important;
    line-height: 1.5;
}

/* === TIMELINE === */
.timeline {
    position: relative;
    padding-left: 10px;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background-color: var(--color-border);
}

.timeline-item {
    position: relative;
    margin-bottom: 2rem;
    padding-top: 1.5rem;
}

.timeline-icon {
    position: absolute;
    left: 15px;
    transform: translateX(-70%);
    top: 20px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: var(--color-surface);
    border: 2px solid;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    z-index: 5;
}

.timeline-icon-reasoning { color: #9d4edd; border-color: #9d4edd; }
.timeline-icon-toolcall { color: var(--color-warning); border-color: var(--color-warning); }
.timeline-icon-return { color: var(--color-success); border-color: var(--color-success); }
.timeline-icon-assistant { color: var(--color-primary); border-color: var(--color-primary); }
.timeline-icon-stats { color: var(--color-danger); border-color: var(--color-danger); }

.timeline-content {
    margin-left: 50px;
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.75rem;
    padding: 1.25rem;
    box-shadow: 0 2px 8px var(--color-shadow);
    transition: box-shadow 0.3s ease;
}

.timeline-content:hover {
    box-shadow: 0 4px 16px var(--color-shadow);
}

/* Tool call content should be in code box */
.timeline-content pre {
    background-color: var(--color-surface-code);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 0.75rem;
    margin-top: 0.5rem;
    font-family: 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
    font-size: 0.8rem;
    line-height: 1.4;
}

/* Tool return sections styling - simplified structure */
.tool-return-section {
    background-color: var(--color-surface);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 0.75rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 4px var(--color-shadow);
}

.tool-return-section h6 {
    color: var(--color-text);
    font-weight: 600;
    margin-bottom: 0.5rem;
    font-size: 0.85rem;
}

/* Text content in tool returns should flow naturally without extra box */
.tool-return-section .p-2 {
    background-color: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    margin-top: 0.25rem !important;
    padding: 0 !important;
}

/* Code content (Sources, JSON) should have code boxes */
.tool-return-section pre {
    background-color: var(--color-surface-code) !important;
    border: 1px solid var(--color-border) !important;
    border-radius: 0.375rem !important;
    padding: 0.75rem !important;
    margin-top: 0.5rem !important;
    font-size: 0.8rem;
    line-height: 1.4;
}

/* === COMPARISON GRID === */
.comparison-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.comparison-box {
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 1.25rem;
    background-color: var(--color-surface);
    box-shadow: 0 2px 8px var(--color-shadow);
}

.agent-answer-content,
.golden-answer-content {
    word-wrap: break-word;
    overflow-wrap: break-word;
    line-height: 1.5;
}

/* === MODALS === */
.modal-content {
    background-color: var(--color-surface);
    border-color: var(--color-border);
    border-radius: 0.75rem;
    box-shadow: 0 12px 48px var(--color-shadow);
}

.modal-header {
    background-color: var(--color-surface);
    border-bottom-color: var(--color-border);
    color: var(--color-text);
}

.modal-body {
    background-color: var(--color-surface);
    color: var(--color-text);
}

.modal-body pre {
    background-color: var(--color-surface-code);
    border: 1px solid var(--color-border);
    border-radius: 0.5rem;
    padding: 1rem;
    max-height: 500px;
    overflow-y: auto;
}

/* === CONTAINERS === */
.container-xl {
    max-width: none;
    width: 100%;
    margin: 0 auto;
    padding-left: 0.5rem;
    padding-right: 0.5rem;
}

/* === RESPONSIVE === */
@media (max-width: 992px) {
    .main-app-content {
        flex-direction: column;
        height: auto;
        overflow-y: auto;
    }
    
    #run-list-panel {
        width: 100%;
        max-height: 45vh;
    }
    
    #main-content-wrapper {
        height: auto;
    }
    
    .comparison-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .search-container input {
        width: 100% !important;
        max-width: 300px;
    }
}

@media (max-width: 768px) {
    .card-header .d-flex.align-items-center {
        flex-direction: column;
        align-items: flex-start !important;
        gap: 1rem !important;
    }
}

/* === DARK MODE OVERRIDES === */
[data-bs-theme="dark"] .bg-light {
    background-color: var(--color-surface-hover) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .border {
    border-color: var(--color-border) !important;
}

[data-bs-theme="dark"] .text-muted {
    color: var(--color-text-muted) !important;
}

[data-bs-theme="dark"] #welcome-screen {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text-muted) !important;
}

[data-bs-theme="dark"] .markdown-content {
    background-color: var(--color-surface-code) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] pre.bg-light {
    background-color: var(--color-surface-code) !important;
    color: var(--color-text) !important;
    border-color: var(--color-border) !important;
}

/* Loading and Loading Indicator Specific Styles */
[data-bs-theme="dark"] #loading-screen {
    background-color: var(--color-bg) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] #loadingIndicator {
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] #examples-loading {
    background-color: var(--color-surface) !important;
    color: var(--color-text) !important;
}

/* Spinner colors for dark mode */
[data-bs-theme="dark"] .spinner-border {
    color: var(--color-primary) !important;
}

[data-bs-theme="dark"] .spinner-border.text-primary {
    color: var(--color-primary) !important;
}

/* Modal content in dark mode */
[data-bs-theme="dark"] .modal-content {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
}

[data-bs-theme="dark"] .modal-header {
    background-color: var(--color-surface) !important;
    border-bottom-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .modal-body {
    background-color: var(--color-surface) !important;
    color: var(--color-text) !important;
}

/* === JSON MODAL - COMPLETE REWRITE === */
#jsonModal {
    --bs-modal-width: 95vw;
    --bs-modal-height: 95vh;
}

#jsonModal .modal-dialog {
    width: var(--bs-modal-width);
    height: var(--bs-modal-height);
    max-width: none;
    max-height: none;
    margin: 2.5vh auto;
}

#jsonModal .modal-content {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    border-radius: 0.75rem;
}

#jsonModal .modal-header {
    flex-shrink: 0;
    height: 60px;
    border-bottom: 1px solid var(--color-border);
}

#jsonModal .modal-body {
    flex: 1;
    padding: 0;
    overflow: hidden;
    position: relative;
}

#jsonModal .json-content {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: var(--color-surface-code);
    overflow: auto;
    font-family: 'SFMono-Regular', Menlo, Monaco, Consolas, monospace;
    font-size: 0.875rem;
    line-height: 1.5;
    padding: 1.5rem;
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    color: var(--color-text);
}

/* Dark mode for JSON modal */
[data-bs-theme="dark"] #jsonModal .json-content {
    background-color: var(--color-surface-code);
    color: var(--color-text);
}

/* === WORD WRAP FOR BUTTONS AND CONTENT === */
/* Ensure all collapsible buttons have proper text wrapping */
button[data-bs-toggle="collapse"],
.btn[data-bs-toggle="collapse"],
.explanation button,
.evaluation-card button {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
    text-align: center !important;
    line-height: 1.3 !important;
    min-height: 2.25rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    hyphens: auto !important;
}

/* Metadata buttons and content */
.metadata-item-full-width .btn {
    white-space: normal !important;
    word-wrap: break-word !important;
    text-align: left !important;
    line-height: 1.4;
}

.metadata-item-full-width pre,
.metadata-item-full-width code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    word-break: break-all !important;
    overflow-wrap: break-word !important;
}

/* Comparison content wrapping */
.comparison-box,
.comparison-box * {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

.comparison-box pre,
.comparison-box code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    word-break: break-all !important;
}

/* Timeline content wrapping */
.timeline-content,
.timeline-content * {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

.timeline-content pre,
.timeline-content code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    word-break: break-all !important;
}

/* Evaluation explanation wrapping */
.explanation,
.explanation * {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

/* Alert content wrapping */
.alert,
.alert * {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

/* General content areas */
#user-message-container,
#comparison-container,
#evaluations-container,
#reasoning-timeline-container {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
}

/* Ensure long URLs and text in content break properly */
a, .text-break, .word-break {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-all !important;
}

/* Specific button types that need text wrapping */
.download-metadata-btn,
button[title*="Ver"],
button[title*="Ocultar"],
button[title*="Detalhes"] {
    white-space: normal !important;
    word-wrap: break-word !important;
    text-align: center !important;
    line-height: 1.3 !important;
    min-height: 2.5rem;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}

/* Force wrap on buttons with specific text content */
button:has(.bi-arrows-expand),
.btn:has(.bi-arrows-expand),
button[data-bs-toggle="collapse"],
.btn[data-bs-toggle="collapse"] {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    text-align: center !important;
    line-height: 1.3 !important;
    min-height: 2.25rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    hyphens: auto !important;
}

/* Small buttons in tables and general usage */
.btn-sm {
    white-space: normal !important;
    word-wrap: break-word !important;
    line-height: 1.2 !important;
    padding: 0.25rem 0.5rem !important;
    font-size: 0.75rem !important;
    min-height: auto !important;
}

/* Ensure table buttons don't break layout */
.table .btn {
    white-space: normal !important;
    word-wrap: break-word !important;
    max-width: 120px;
    text-align: center !important;
}

/* Ultra specific rules for stubborn buttons */
button.btn.btn-sm.btn-outline-secondary[type="button"][data-bs-toggle="collapse"],
.btn.btn-sm.btn-outline-secondary[type="button"][data-bs-toggle="collapse"],
.explanation .btn,
.evaluation-card .btn,
.tool-return-section .btn,
.timeline-content .btn {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
    text-align: center !important;
    line-height: 1.3 !important;
    min-height: 2.25rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    hyphens: auto !important;
    max-width: none !important;
}

/* Specific targeting for collapse buttons and their content */
button[data-bs-toggle="collapse"],
.btn[data-bs-toggle="collapse"] {
    white-space: normal !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
    text-align: center !important;
    line-height: 1.3 !important;
    min-height: 2.25rem !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-wrap: wrap !important;
    hyphens: auto !important;
}

/* Content inside collapsed sections also needs text wrapping */
.collapse pre,
.collapse code,
.collapse .p-2,
.tool-return-section pre,
.tool-return-section code {
    white-space: pre-wrap !important;
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
}

/* Card and Alert overrides for dark mode */
[data-bs-theme="dark"] .card {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .card-header {
    background-color: var(--color-surface-hover) !important;
    border-bottom-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .card-body {
    background-color: var(--color-surface) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .alert-light {
    background-color: var(--color-surface-hover) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

/* Table overrides for better dark mode */
[data-bs-theme="dark"] .table {
    background-color: var(--color-surface) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .table th {
    background-color: var(--color-table-header) !important;
    color: var(--color-text) !important;
    border-color: var(--color-border-strong) !important;
}

[data-bs-theme="dark"] .table td {
    color: var(--color-text) !important;
    border-color: var(--color-border-strong) !important;
}

[data-bs-theme="dark"] .table-light,
[data-bs-theme="dark"] .table-light th,
[data-bs-theme="dark"] .table-light td {
    background-color: var(--color-table-header) !important;
    color: var(--color-text) !important;
}

/* Timeline and tool return sections dark mode */
[data-bs-theme="dark"] .timeline-content {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

/* Timeline pre code boxes dark mode */
[data-bs-theme="dark"] .timeline-content pre {
    background-color: var(--color-surface-code) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

/* Evaluation JSON immediate styling dark mode */
[data-bs-theme="dark"] .evaluation-json-code {
    background-color: var(--color-surface-code) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .evaluation-json-code code {
    color: var(--color-text) !important;
}

/* Evaluation explanation boxes dark mode */
[data-bs-theme="dark"] .explanation .collapse > div,
[data-bs-theme="dark"] .explanation .collapse > pre,
[data-bs-theme="dark"] .explanation .collapse > code {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .explanation .collapse pre {
    background-color: var(--color-surface-code) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .explanation .collapse .markdown-content {
    background-color: var(--color-surface) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .tool-return-section {
    background-color: var(--color-surface) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .tool-return-section h6 {
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .tool-return-section .p-2 {
    background-color: transparent !important;
    border-color: transparent !important;
    color: var(--color-text) !important;
}

[data-bs-theme="dark"] .tool-return-section pre {
    background-color: var(--color-surface-code) !important;
    border-color: var(--color-border) !important;
    color: var(--color-text) !important;
}

/* === AUTH PAGE STYLES === */
body.auth-page {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-info) 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}

.auth-container {
    background-color: var(--color-surface);
    border-radius: 1rem;
    box-shadow: 0 20px 60px var(--color-shadow);
    padding: 2.5rem;
    width: 100%;
    max-width: 420px;
    border: 1px solid var(--color-border);
}

.auth-header {
    text-align: center;
    margin-bottom: 2rem;
}

.auth-header h1 {
    color: var(--color-text);
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}

.auth-header p {
    color: var(--color-text-muted);
    font-size: 0.95rem;
    margin: 0;
}

.auth-body {
    margin-bottom: 1.5rem;
}

.auth-page .form-control {
    background-color: var(--color-surface);
    border: 2px solid var(--color-border);
    color: var(--color-text);
    border-radius: 0.75rem;
    padding: 1rem 1.25rem;
    font-size: 1rem;
    transition: all 0.3s ease;
}

.auth-page .form-control:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.25rem var(--color-primary-light);
    background-color: var(--color-surface);
    color: var(--color-text);
}

.auth-page .form-control::placeholder {
    color: var(--color-text-muted);
}

.auth-page .form-label {
    color: var(--color-text);
    font-weight: 600;
    margin-bottom: 0.75rem;
    font-size: 0.95rem;
}

.btn-auth {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-info) 100%);
    border: none;
    color: white;
    font-weight: 600;
    padding: 1rem 2rem;
    border-radius: 0.75rem;
    font-size: 1rem;
    transition: all 0.3s ease;
    box-shadow: 0 4px 16px var(--color-shadow);
}

.btn-auth:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px var(--color-shadow);
    color: white;
}

.loading-spinner {
    display: none;
}

.error-message {
    background-color: rgba(231, 76, 60, 0.1);
    border: 1px solid var(--color-danger);
    color: var(--color-danger);
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    display: none;
}

.success-message {
    background-color: rgba(46, 204, 113, 0.1);
    border: 1px solid var(--color-success);
    color: var(--color-success);
    padding: 1rem;
    border-radius: 0.75rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    display: none;
}

.auth-footer {
    text-align: center;
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border);
    color: var(--color-text-muted);
    font-size: 0.85rem;
}

/* === AUTH PAGE DARK MODE === */
[data-bs-theme="dark"] body.auth-page {
    background: linear-gradient(135deg, #1A2129 0%, #2E3A46 100%);
}

[data-bs-theme="dark"] .auth-container {
    background-color: var(--color-surface);
    border-color: var(--color-border);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.4);
}

[data-bs-theme="dark"] .auth-header h1 {
    color: var(--color-text);
}

[data-bs-theme="dark"] .auth-header p {
    color: var(--color-text-muted);
}

[data-bs-theme="dark"] .auth-page .form-control {
    background-color: var(--color-surface-hover);
    border-color: var(--color-border);
    color: var(--color-text);
}

[data-bs-theme="dark"] .auth-page .form-control:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 0.25rem var(--color-primary-light);
    background-color: var(--color-surface-hover);
    color: var(--color-text);
}

[data-bs-theme="dark"] .auth-page .form-control::placeholder {
    color: var(--color-text-muted);
}

[data-bs-theme="dark"] .auth-page .form-label {
    color: var(--color-text);
}

[data-bs-theme="dark"] .btn-auth {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-info) 100%);
}

[data-bs-theme="dark"] .btn-auth:hover {
    color: white;
}

[data-bs-theme="dark"] .error-message {
    background-color: rgba(255, 123, 123, 0.1);
    border-color: var(--color-danger);
    color: var(--color-danger);
}

[data-bs-theme="dark"] .success-message {
    background-color: rgba(82, 216, 135, 0.1);
    border-color: var(--color-success);
    color: var(--color-success);
}

[data-bs-theme="dark"] .auth-footer {
    border-top-color: var(--color-border);
    color: var(--color-text-muted);
}

[data-bs-theme="dark"] .auth-page .btn-outline-secondary {
    border-color: var(--color-border);
    color: var(--color-text-muted);
    background-color: transparent;
}

[data-bs-theme="dark"] .auth-page .btn-outline-secondary:hover {
    background-color: var(--color-surface-hover);
    border-color: var(--color-border);
    color: var(--color-text);
}
```


### File `experiment.html`

Path: `static/experiment.html`


```html
<!DOCTYPE html>
<html lang="pt-BR" data-bs-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Detalhes do Experimento</title>
    <!-- Libs -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>


    <!-- App CSS - Path confirmed to be correct as per instructions -->
    <link rel="stylesheet" href="/eai-agent/admin/experiments/static/experiment.css">
    <!-- Favicon -->
    <link rel="icon" href="{{BASE_API_URL}}/admin/experiments/favicon.ico" type="image/x-icon">
</head>
<body>
    <!-- Loading Screen -->
    <div id="loading-screen" class="d-flex justify-content-center align-items-center vh-100">
        <div class="text-center">
            <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            <p class="mt-3 text-muted">Verificando autenticação...</p>
        </div>
    </div>

    <!-- Painel Principal (Refactored to fixed sidebar layout) -->
    <div id="experimentsPanel" class="d-none d-flex flex-column vh-100"> <!-- Main app container, fills screen height -->

        <!-- Global Header -->
        <header class="container-xl py-4">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-3">
                <div class="d-flex align-items-center gap-3">
                    <div>
                        <h1 class="h3 mb-0" id="experiment-title">Detalhes do Experimento</h1>
                        <small class="text-muted" id="experiment-info">Análise detalhada de experimento</small>
                    </div>
                </div>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                    <a href="#" id="backToDatasetBtn" class="btn btn-outline-secondary d-none" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Voltar">
                        <i class="bi bi-arrow-left"></i>
                    </a>
                    <button id="viewJsonBtn" class="btn btn-outline-info d-none" data-bs-toggle="modal" data-bs-target="#jsonModal" title="Ver JSON" data-bs-placement="bottom">
                        <i class="bi bi-code-square"></i>
                    </button>
                    <button id="downloadJsonBtn" class="btn btn-outline-success d-none" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Download JSON">
                        <i class="bi bi-download"></i>
                    </button>
                    <button id="downloadJsonLlmBtn" class="btn btn-outline-warning d-none" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Exportar LLM">
                        <i class="bi bi-robot"></i>
                    </button>
                    <button id="themeToggleBtn" class="btn btn-outline-secondary" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Tema">
                        <i class="bi bi-moon-fill" id="themeIcon"></i>
                    </button>
                    <button id="logoutBtn" class="btn btn-outline-danger" onclick="AuthCheck.logout()" data-bs-toggle="tooltip" data-bs-placement="bottom" title="Sair">
                        <i class="bi bi-box-arrow-right"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- Main content area below header - this will be the flex container for sidebar and details -->
        <div class="main-app-content">

            <!-- Left Panel: Run List (Fixed Sidebar) -->
            <div id="run-list-panel">
                <div id="filterContainer" class="p-3 border-bottom"></div>
                <div class="list-header p-3 d-flex justify-content-between align-items-center">
                    <h5 class="mb-0">Execuções (Runs)</h5>
                    <span id="run-count-badge" class="badge bg-secondary-subtle text-secondary-emphasis rounded-pill"></span>
                </div>
                <!-- The run list is dynamically populated by JS. The HTML structure is prepared for a simplified ID display. -->
                <div id="run-list" class="list-group list-group-flush"></div>
            </div>

            <!-- Right Panel: Main Content (Scrollable) -->
            <div id="main-content-wrapper" class="flex-grow-1 overflow-y-auto">
                <div class="container-xl py-4"> <!-- Inner padding for right-side content -->

                    <div id="loadingIndicator" class="d-none text-center my-5">
                        <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                            <span class="visually-hidden">Carregando...</span>
                        </div>
                    </div>

                    <div id="alertArea" class="mb-3"></div>

                    <div id="welcome-screen" class="text-center text-muted p-5 border rounded bg-light">
                        <h3>Bem-vindo aos Detalhes do Experimento</h3>
                        <p class="mb-0">Navegue pelos datasets para visualizar experimentos específicos ou acesse diretamente via URL com parâmetro ?id=...</p>
                    </div>

                    <!-- Result container now sits cleanly within the main page container -->
                    <div id="resultContainer" class="d-none">
                        <!-- Metadata and Metrics Containers (now part of the scrollable main content) -->
                        <div id="metadataContainer" class="mb-4"></div>
                        <div id="summaryMetricsContainer" class="mb-4"></div>

                        <!-- Details Panel (now a standalone card-like component) -->
                        <div id="details-panel" class="card-component">
                            <div id="details-placeholder" class="d-flex h-100 align-items-center justify-content-center text-center text-muted p-4">
                                <div>
                                    <i class="bi bi-card-list" style="font-size: 3rem;"></i>
                                    <p class="mt-2">Selecione um run na lista à esquerda para ver os detalhes.</p>
                                </div>
                            </div>
                            <div id="details-content" class="d-none">
                                <h4 class="section-title">Mensagem do Usuário</h4>
                                <div id="user-message-container" class="alert alert-light"></div>

                                <h4 class="section-title mb-0">Comparação de Respostas</h4>
                                <!-- Removed toggle-diff-btn as requested -->
                                <div id="comparison-container" class="mt-3"></div>

                                <h4 class="section-title">Avaliações</h4>
                                <div id="evaluations-container"></div>

                                <div class="section-header">
                                    <h4 class="section-title">Cadeia de Pensamento (Reasoning)</h4>
                                    <!-- JS will inject tool call summary here -->
                                </div>
                                <div id="reasoning-timeline-container"></div>

                                <!-- Removed "Erros" section as requested -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal para visualização do JSON -->
    <div class="modal fade" id="jsonModal" tabindex="-1" aria-labelledby="jsonModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="jsonModalLabel">JSON Original do Experimento</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="json-content" id="jsonContent"><!-- Conteúdo do JSON será inserido aqui --></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal para Download JSON for LLM -->
    <div class="modal fade" id="downloadJsonLlmModal" tabindex="-1" aria-labelledby="downloadJsonLlmModalLabel" aria-hidden="true">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title" id="downloadJsonLlmModalLabel">Download JSON for LLM</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="numberOfExperimentsLlm" class="form-label">Número de experimentos (opcional)</label>
                        <input type="number" class="form-control" id="numberOfExperimentsLlm" min="1" placeholder="Deixe em branco para baixar todos">
                        <div class="form-text">Realiza o download de uma versão mais limpa dos dados do experimento. Se não especificar um número, todos os experimentos serão baixados. Se especificar, será feita uma seleção aleatória.</div>
                    </div>
                    
                    <div class="mb-3">
                        <label class="form-label">Filtros de Conteúdo</label>
                        <div class="form-text mb-3">Selecione quais tipos de dados incluir no download</div>
                        
                        <!-- Campos Básicos -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <h6 class="mb-0">Campos Básicos</h6>
                            </div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="filter_message_id" checked>
                                            <label class="form-check-label" for="filter_message_id">ID da Mensagem</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="filter_menssagem" checked>
                                            <label class="form-check-label" for="filter_menssagem">Mensagem do Usuário</label>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="filter_golden_answer" checked>
                                            <label class="form-check-label" for="filter_golden_answer">Resposta Esperada</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input" type="checkbox" id="filter_model_response" checked>
                                            <label class="form-check-label" for="filter_model_response">Resposta do Modelo</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Reasoning Messages -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="filter_reasoning_messages" checked>
                                    <label class="form-check-label fw-bold" for="filter_reasoning_messages">Mensagens de Raciocínio (reasoning_message)</label>
                                </div>
                            </div>
                        </div>

                        <!-- Tool Call Messages -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="filter_tool_call_messages" checked>
                                    <label class="form-check-label fw-bold" for="filter_tool_call_messages">Chamadas de Ferramentas (tool_call_message)</label>
                                </div>
                            </div>
                            <div class="card-body" id="tool_call_options" style="display: none;">
                                <div class="form-text mb-2">Selecione quais ferramentas incluir:</div>
                                <div id="tool_call_tools_list">
                                    <!-- Será populado dinamicamente -->
                                </div>
                            </div>
                        </div>

                        <!-- Tool Return Messages -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="filter_tool_return_messages" checked>
                                    <label class="form-check-label fw-bold" for="filter_tool_return_messages">Retornos de Ferramentas (tool_return_message)</label>
                                </div>
                            </div>
                            <div class="card-body" id="tool_return_options" style="display: none;">
                                <div class="form-text mb-2">Selecione quais ferramentas incluir:</div>
                                <div id="tool_return_tools_list" class="mb-3">
                                    <!-- Será populado dinamicamente -->
                                </div>
                                
                                <div class="form-text mb-2">Selecione quais conteúdos incluir:</div>
                                <div class="row">
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input tool-return-content" type="checkbox" id="content_text" checked>
                                            <label class="form-check-label" for="content_text">Texto de Resposta</label>
                                        </div>
                                        <div class="form-check">
                                            <input class="form-check-input tool-return-content" type="checkbox" id="content_sources" checked>
                                            <label class="form-check-label" for="content_sources">Fontes</label>
                                        </div>
                                    </div>
                                    <div class="col-6">
                                        <div class="form-check">
                                            <input class="form-check-input tool-return-content" type="checkbox" id="content_web_search_queries" checked>
                                            <label class="form-check-label" for="content_web_search_queries">Consultas Web</label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Metrics -->
                        <div class="card mb-3">
                            <div class="card-header">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="filter_metrics" checked>
                                    <label class="form-check-label fw-bold" for="filter_metrics">Métricas de Avaliação</label>
                                </div>
                            </div>
                            <div class="card-body" id="metrics_options" style="display: none;">
                                <div class="form-text mb-2">Selecione quais métricas incluir:</div>
                                <div id="metrics_list">
                                    <!-- Será populado dinamicamente -->
                                </div>
                            </div>
                        </div>

                        <div class="mt-3">
                            <button type="button" class="btn btn-sm btn-outline-secondary me-2" id="selectAllFiltersBtn">Selecionar Todos</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="deselectAllFiltersBtn">Limpar Seleção</button>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="button" class="btn btn-primary" id="confirmDownloadJsonLlm">
                        <i class="bi bi-download me-1"></i>Baixar JSON
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Configuração global da API (unchanged)
        window.API_BASE_URL_OVERRIDE = '{{BASE_API_URL}}';
        
        // Injeta IDs do backend se disponíveis
        window.DATASET_ID = '{{DATASET_ID}}';
        window.EXPERIMENT_ID = '{{EXPERIMENT_ID}}';
        
        // Inicializar tooltips do Bootstrap com configurações otimizadas
        document.addEventListener('DOMContentLoaded', function() {
            // Incluir tanto elementos com data-bs-toggle="tooltip" quanto elementos com apenas title
            var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"], [title]:not([data-bs-toggle="modal"])'));
            var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl, {
                    delay: { show: 300, hide: 100 },
                    animation: true,
                    trigger: 'hover focus'
                });
            });
            
            // Tratamento especial para o botão Ver JSON que tem modal
            var jsonBtn = document.getElementById('viewJsonBtn');
            if (jsonBtn) {
                new bootstrap.Tooltip(jsonBtn, {
                    delay: { show: 300, hide: 100 },
                    animation: true,
                    trigger: 'hover focus',
                    placement: 'bottom'
                });
            }
        });
    </script>
    <!-- Auth Check deve ser carregado PRIMEIRO -->
    <script src="/eai-agent/admin/experiments/static/auth-check.js"></script>
    <!-- App JS - Path confirmed to be correct as per instructions -->
    <script src="/eai-agent/admin/experiments/static/experiment.js"></script>
</body>
</html>
```


### File `experiment.js`

Path: `static/experiment.js`


```js
/*
 * Final Integrated JavaScript
 * Contains core logic and visualization features.
 * Refactored to implement new data display requirements.
 */

// Estado global da aplicação
const appState = {
  currentDatasetId: null,
  currentExperimentId: null,
  originalJsonData: null,
  allRuns: [],
  selectedRunId: null,
  // Adicionar estado para persistir filtros
  savedFilters: {
    basic_fields: [
      "message_id",
      "menssagem",
      "golden_answer",
      "model_response",
    ],
    reasoning_messages: { include: true },
    tool_call_messages: { include: true, selected_tools: null },
    tool_return_messages: {
      include: true,
      selected_tools: null,
      selected_content: ["text", "sources", "web_search_queries"],
    },
    metrics: { include: true, selected_metrics: null },
  },
};

// --- DOM ELEMENT SELECTORS ---
const getElement = (id) => {
  const element = document.getElementById(id);
  if (!element) {
    console.warn(`Element with id '${id}' not found`);
  }
  return element;
};

const elements = {
  loadingScreen: getElement("loading-screen"),
  experimentsPanel: getElement("experimentsPanel"),
  refreshExperimentBtn: getElement("refreshExperimentBtn"),
  downloadJsonBtn: getElement("downloadJsonBtn"),
  downloadJsonLlmBtn: getElement("downloadJsonLlmBtn"),
  viewJsonBtn: getElement("viewJsonBtn"),
  backToDatasetBtn: getElement("backToDatasetBtn"),
  themeToggleBtn: getElement("themeToggleBtn"),
  themeIcon: getElement("themeIcon"),
  experimentTitle: getElement("experiment-title"),
  experimentInfo: getElement("experiment-info"),
  loadingIndicator: getElement("loadingIndicator"),
  alertArea: getElement("alertArea"),
  welcomeScreen: getElement("welcome-screen"),
  resultContainer: getElement("resultContainer"),
  metadataContainer: getElement("metadataContainer"),
  summaryMetricsContainer: getElement("summaryMetricsContainer"),
  filterContainer: getElement("filterContainer"),
  runListPanel: getElement("run-list-panel"),
  runList: getElement("run-list"),
  runCountBadge: getElement("run-count-badge"),
  mainContentWrapper: getElement("main-content-wrapper"), // Selector for the right-hand scrollable wrapper
  detailsPanel: getElement("details-panel"),
  detailsPlaceholder: getElement("details-placeholder"),
  detailsContent: getElement("details-content"),
  userMessageContainer: getElement("user-message-container"),
  comparisonContainer: getElement("comparison-container"),
  evaluationsContainer: getElement("evaluations-container"),
  reasoningTimelineContainer: getElement("reasoning-timeline-container"),
  // errorsContainer: getElement("errors-container"), // Removed as requested
  // toggleDiffBtn: getElement("toggle-diff-btn"), // Removed as requested
};

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  // Inicializar tema
  initializeTheme();

  // Aguardar verificação de autenticação
  setTimeout(() => {
    if (AuthCheck.isAuthenticated()) {
      showExperimentsPanel();
    }
  }, 100);

  // Check for dataset_id and experiment_id from URL path or injected variables
  let datasetId = window.DATASET_ID;
  let experimentId = window.EXPERIMENT_ID;

  // If not injected, try to parse from URL path
  if (
    !datasetId ||
    datasetId === "{{DATASET_ID}}" ||
    !experimentId ||
    experimentId === "{{EXPERIMENT_ID}}"
  ) {
    const pathParts = window.location.pathname
      .split("/")
      .filter((part) => part);
    const adminIndex = pathParts.indexOf("admin");

    if (adminIndex >= 0 && pathParts[adminIndex + 1] === "experiments") {
      datasetId = pathParts[adminIndex + 2];
      experimentId = pathParts[adminIndex + 3];
    }
  }

  if (
    datasetId &&
    experimentId &&
    datasetId !== "{{DATASET_ID}}" &&
    experimentId !== "{{EXPERIMENT_ID}}"
  ) {
    appState.currentDatasetId = datasetId;
    appState.currentExperimentId = experimentId;

    // Auto-fetch if user is already authenticated
    if (AuthCheck.isAuthenticated()) {
      setTimeout(() => {
        fetchExperimentData(datasetId, experimentId);
      }, 500);
    }
  }

  // Removed login form and logout button event listeners - handled by AuthCheck
  if (elements.refreshExperimentBtn) {
    elements.refreshExperimentBtn.addEventListener("click", () => {
      if (appState.currentDatasetId && appState.currentExperimentId) {
        fetchExperimentData(
          appState.currentDatasetId,
          appState.currentExperimentId
        );
      }
    });
  }
  if (elements.downloadJsonBtn) {
    elements.downloadJsonBtn.addEventListener("click", downloadOriginalJson);
  }
  if (elements.downloadJsonLlmBtn) {
    elements.downloadJsonLlmBtn.addEventListener(
      "click",
      showDownloadJsonLlmModal
    );
  }
  if (elements.viewJsonBtn) {
    elements.viewJsonBtn.addEventListener("click", () => {
      // O modal será aberto automaticamente pelo data-bs-toggle
    });
  }
  if (elements.backToDatasetBtn) {
    elements.backToDatasetBtn.addEventListener("click", (e) => {
      e.preventDefault();
      if (appState.currentDatasetId) {
        window.location.href = `/eai-agent/admin/experiments/${appState.currentDatasetId}`;
      }
    });
  }
  if (elements.runList) {
    elements.runList.addEventListener("click", handleRunClick);
  }
  if (elements.themeToggleBtn) {
    elements.themeToggleBtn.addEventListener("click", toggleTheme);
  }

  // Event listener para o botão de confirmação do modal
  const confirmDownloadJsonLlmBtn = getElement("confirmDownloadJsonLlm");
  if (confirmDownloadJsonLlmBtn) {
    confirmDownloadJsonLlmBtn.addEventListener("click", downloadJsonForLlm);
  }

  // Event listeners para mostrar/esconder opções de filtro
  document.addEventListener("change", function (e) {
    if (
      e.target.id === "filter_tool_call_messages" ||
      e.target.id === "filter_tool_return_messages" ||
      e.target.id === "filter_metrics"
    ) {
      showDetailedOptions();
      // Salvar filtros automaticamente quando houver mudanças
      saveCurrentFilters();
    }

    // Salvar filtros para outros checkboxes também
    if (
      e.target.id === "filter_message_id" ||
      e.target.id === "filter_menssagem" ||
      e.target.id === "filter_golden_answer" ||
      e.target.id === "filter_model_response" ||
      e.target.id === "filter_reasoning_messages" ||
      e.target.id === "content_text" ||
      e.target.id === "content_sources" ||
      e.target.id === "content_web_search_queries" ||
      e.target.closest("#tool_call_tools_list") ||
      e.target.closest("#tool_return_tools_list") ||
      e.target.closest("#metrics_list")
    ) {
      saveCurrentFilters();
    }
  });

  // Event listeners para botões de seleção
  const selectAllFiltersBtn = getElement("selectAllFiltersBtn");
  const deselectAllFiltersBtn = getElement("deselectAllFiltersBtn");

  if (selectAllFiltersBtn) {
    selectAllFiltersBtn.addEventListener("click", () => {
      document
        .querySelectorAll('#downloadJsonLlmModal input[type="checkbox"]')
        .forEach((checkbox) => {
          checkbox.checked = true;
        });
      // Mostrar todas as opções
      showDetailedOptions();
      // Salvar filtros
      saveCurrentFilters();
    });
  }

  if (deselectAllFiltersBtn) {
    deselectAllFiltersBtn.addEventListener("click", () => {
      document
        .querySelectorAll('#downloadJsonLlmModal input[type="checkbox"]')
        .forEach((checkbox) => {
          checkbox.checked = false;
        });
      // Esconder todas as opções
      showDetailedOptions();
      // Salvar filtros
      saveCurrentFilters();
    });
  }
  // elements.toggleDiffBtn.addEventListener("click", handleToggleDiff); // Removed as requested
});

// --- AUTHENTICATION REMOVED - Now handled by auth-check.js ---

// FIX: Ensure d-flex is added when showing the panel
function showExperimentsPanel() {
  if (elements.loadingScreen) {
    elements.loadingScreen.classList.add("d-none");
  }
  if (elements.experimentsPanel) {
    elements.experimentsPanel.classList.remove("d-none");
    elements.experimentsPanel.classList.add("d-flex"); // Crucial line to apply flex display
  }

  // Check for dataset_id and experiment_id from URL path or injected variables after login
  let datasetId = window.DATASET_ID;
  let experimentId = window.EXPERIMENT_ID;

  // If not injected, try to parse from URL path
  if (
    !datasetId ||
    datasetId === "{{DATASET_ID}}" ||
    !experimentId ||
    experimentId === "{{EXPERIMENT_ID}}"
  ) {
    const pathParts = window.location.pathname
      .split("/")
      .filter((part) => part);
    const adminIndex = pathParts.indexOf("admin");

    if (adminIndex >= 0 && pathParts[adminIndex + 1] === "experiments") {
      datasetId = pathParts[adminIndex + 2];
      experimentId = pathParts[adminIndex + 3];
    }
  }

  if (
    datasetId &&
    experimentId &&
    datasetId !== "{{DATASET_ID}}" &&
    experimentId !== "{{EXPERIMENT_ID}}"
  ) {
    appState.currentDatasetId = datasetId;
    appState.currentExperimentId = experimentId;
    setTimeout(() => {
      fetchExperimentData(datasetId, experimentId);
    }, 500);
  }
}

// --- HEADER UPDATES ---
function updateExperimentHeader(
  metadata,
  datasetName = null,
  experimentName = null
) {
  if (elements.experimentTitle) {
    // Sempre manter "Dashboard de Experimentos" como título
    elements.experimentTitle.textContent = "Dashboard de Experimentos";
  }

  if (elements.experimentInfo) {
    let infoHtml = "";
    if (datasetName) {
      infoHtml += `Dataset: ${datasetName}`;
    }
    if (experimentName) {
      if (infoHtml) infoHtml += "<br>";
      infoHtml += `Experimento: ${experimentName}`;
    } else if (metadata && metadata.name) {
      if (infoHtml) infoHtml += "<br>";
      infoHtml += `Experimento: ${metadata.name}`;
    } else if (appState.currentExperimentId) {
      if (infoHtml) infoHtml += "<br>";
      infoHtml += `Experimento: ${appState.currentExperimentId}`;
    }

    if (!infoHtml) {
      infoHtml = "Análise detalhada de experimento";
    }

    elements.experimentInfo.innerHTML = infoHtml;
  }

  // Mostrar botão de voltar ao dataset
  if (elements.backToDatasetBtn && appState.currentDatasetId) {
    elements.backToDatasetBtn.classList.remove("d-none");
  }
}

// --- DATA FETCHING ---
function fetchExperimentData(datasetId = null, experimentId = null) {
  if (!datasetId || !experimentId) {
    showAlert("IDs do dataset e experimento são necessários.", "warning");
    return;
  }

  appState.currentDatasetId = datasetId;
  appState.currentExperimentId = experimentId;
  setLoadingState(true);

  const API_BASE_URL = window.API_BASE_URL_OVERRIDE;
  const url = `${API_BASE_URL}/admin/experiments/${encodeURIComponent(
    datasetId
  )}/${encodeURIComponent(experimentId)}/data`;

  fetch(url, {
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(async (response) => {
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail ||
            `HTTP ${response.status}: ${response.statusText}`
        );
      }
      return response.json();
    })
    .then((data) => {
      appState.originalJsonData = data;
      appState.allRuns = data.experiment;
      appState.selectedRunId = null;

      // Resetar filtros salvos para o novo experimento
      resetSavedFilters();

      // Atualizar informações no cabeçalho
      updateExperimentHeader(
        data.experiment_metadata,
        data.dataset_name,
        data.experiment_name
      );

      renderMetadata(data.experiment_metadata);
      calculateAndRenderSummaryMetrics(data.experiment);
      renderFilters(data.experiment);
      renderRunList(appState.allRuns);
      resetDetailsPanel();

      // Mostrar botões de ação
      if (elements.refreshExperimentBtn) {
        elements.refreshExperimentBtn.classList.remove("d-none");
      }
      if (elements.downloadJsonBtn) {
        elements.downloadJsonBtn.classList.remove("d-none");
      }
      if (elements.downloadJsonLlmBtn) {
        elements.downloadJsonLlmBtn.classList.remove("d-none");
      }
      if (elements.viewJsonBtn) {
        elements.viewJsonBtn.classList.remove("d-none");
      }

      showAlert("Experimento carregado com sucesso!", "success");
      if (elements.welcomeScreen) {
        elements.welcomeScreen.classList.add("d-none");
      }
      if (elements.resultContainer) {
        elements.resultContainer.classList.remove("d-none");
      }
    })
    .catch((error) => {
      console.error("Erro ao buscar experimento:", error);
      showAlert(`Falha ao buscar o experimento: ${error.message}`, "danger");
      if (elements.resultContainer) {
        elements.resultContainer.classList.add("d-none");
      }
      if (elements.welcomeScreen) {
        elements.welcomeScreen.classList.remove("d-none");
      }

      // Esconder botões de ação em caso de erro
      if (elements.refreshExperimentBtn) {
        elements.refreshExperimentBtn.classList.add("d-none");
      }
      if (elements.downloadJsonBtn) {
        elements.downloadJsonBtn.classList.add("d-none");
      }
      if (elements.downloadJsonLlmBtn) {
        elements.downloadJsonLlmBtn.classList.add("d-none");
      }
      if (elements.viewJsonBtn) {
        elements.viewJsonBtn.classList.add("d-none");
      }
      if (elements.backToDatasetBtn) {
        elements.backToDatasetBtn.classList.add("d-none");
      }
    })
    .finally(() => {
      setLoadingState(false);
    });
}

// --- RENDERING LOGIC ---

function renderRunList(runs) {
  if (!elements.runList) return;

  elements.runList.innerHTML = "";
  if (!runs || runs.length === 0) {
    elements.runList.innerHTML = `<li class="list-group-item">Nenhum run encontrado.</li>`;
    if (elements.runCountBadge) {
      elements.runCountBadge.textContent = "0";
    }
    return;
  }

  const fragment = document.createDocumentFragment();

  runs.forEach((run, index) => {
    // Use run.output.metadata.id if available, fallback to internal index
    const displayId = run.output?.metadata?.id || `${index + 1}`; // Removed "ID:" prefix
    const runId = run.example_id_clean || `run-${index}`; // Internal identifier remains the same

    const listItem = document.createElement("a");
    listItem.href = "#";
    listItem.className =
      "list-group-item list-group-item-action d-flex justify-content-between align-items-start";
    listItem.dataset.runId = runId;

    // Check if this run should be selected
    if (runId === appState.selectedRunId) {
      listItem.classList.add("active");
    }

    // MODIFICATION: Only display ID
    listItem.innerHTML = `
          <div class="ms-2 me-auto">
              <div class="fw-bold">ID: ${displayId}</div>
          </div>
      `;
    fragment.appendChild(listItem);
  });

  elements.runList.appendChild(fragment);
  if (elements.runCountBadge) {
    elements.runCountBadge.textContent = runs.length;
  }
}

function handleRunClick(e) {
  const target = e.target.closest(".list-group-item-action");
  if (!target) return;

  e.preventDefault();
  e.stopPropagation();

  const runId = target.dataset.runId;
  if (!runId) return;

  // Don't do anything if clicking the same run
  if (runId === appState.selectedRunId) return;

  // Clear any existing timeouts to prevent race conditions
  if (window.runClickTimeout) {
    clearTimeout(window.runClickTimeout);
  }
  if (window.renderDetailsTimeout) {
    clearTimeout(window.renderDetailsTimeout);
  }

  // Update state immediately
  appState.selectedRunId = runId;

  // Update active state immediately with force
  if (elements.runList) {
    // Remove active from all items
    elements.runList.querySelectorAll(".active").forEach((item) => {
      item.classList.remove("active");
    });
    // Add active to clicked item
    target.classList.add("active");
  }

  // Force a small delay to ensure DOM updates are complete
  requestAnimationFrame(() => {
    renderDetailsPanel();
  });
}

/**
 * MODIFIED: No longer calls the renderErrors function.
 */
function renderDetailsPanel() {
  // Salvar a posição de rolagem atual do painel de detalhes
  let previousScrollTop = 0;
  if (elements.mainContentWrapper) {
    previousScrollTop = elements.mainContentWrapper.scrollTop;
  }

  if (!appState.selectedRunId) {
    resetDetailsPanel();
    return;
  }

  const selectedRun = appState.allRuns.find((run, index) => {
    const runId = run.example_id_clean || `run-${index}`;
    return runId === appState.selectedRunId;
  });
  if (!selectedRun) {
    console.warn("Run selecionado não encontrado:", appState.selectedRunId);
    resetDetailsPanel();
    return;
  }

  try {
    if (elements.userMessageContainer) {
      elements.userMessageContainer.textContent =
        selectedRun.input.mensagem_whatsapp_simulada ||
        "Mensagem não disponível";
    }

    renderComparison(selectedRun);
    renderEvaluations(selectedRun.annotations);
    renderReasoningTimeline(selectedRun.output.agent_output?.ordered);

    if (elements.detailsPlaceholder) {
      elements.detailsPlaceholder.classList.add("d-none");
    }
    if (elements.detailsContent) {
      elements.detailsContent.classList.remove("d-none");
    }

    // Restaurar a posição de rolagem do painel de detalhes
    if (elements.mainContentWrapper) {
      elements.mainContentWrapper.scrollTop = previousScrollTop;
    }
  } catch (error) {
    console.error("Erro ao renderizar painel de detalhes:", error);
    showAlert("Erro ao carregar detalhes da run.", "warning");
  }
}

function resetDetailsPanel() {
  // Clear any pending timeouts
  if (window.runClickTimeout) {
    clearTimeout(window.runClickTimeout);
  }
  if (window.renderDetailsTimeout) {
    clearTimeout(window.renderDetailsTimeout);
  }

  if (elements.detailsPlaceholder) {
    elements.detailsPlaceholder.classList.remove("d-none");
  }
  if (elements.detailsContent) {
    elements.detailsContent.classList.add("d-none");
  }

  appState.selectedRunId = null;

  if (elements.runList) {
    const currentlyActive = elements.runList.querySelector(".active");
    if (currentlyActive) currentlyActive.classList.remove("active");
  }
}

// MODIFIED: Simplified as diff button is removed
function renderComparison(runData) {
  // Use a variable to store the found message and then safely access its properties
  const agentMessage = runData.output.agent_output?.ordered?.find(
    (m) => m.type === "assistant_message"
  );
  const agentAnswerHtml = agentMessage?.message?.content
    ? marked.parse(agentMessage.message.content)
    : "<p>N/A</p>";

  const goldenAnswerHtml = runData.reference_output.golden_answer
    ? marked.parse(runData.reference_output.golden_answer)
    : "<p>N/A</p>";

  if (elements.comparisonContainer) {
    elements.comparisonContainer.innerHTML = `
        <div class="comparison-grid">
            <div class="comparison-box">
                <h5>🤖 Resposta do Agente</h5>
                <div class="agent-answer-content">${agentAnswerHtml}</div>
            </div>
            <div class="comparison-box">
                <h5>🏆 Resposta de Referência (Golden)</h5>
                <div class="golden-answer-content">${goldenAnswerHtml}</div>
            </div>
        </div>
    `;
  }
}

/**
 * MODIFIED: Score position moved to the left.
 * MODIFIED: "Golden Link in Tool Calling" explanation is now expandable and starts collapsed, using consistent styling.
 * MODIFIED: "Golden Link in Answer" also gets the collapse button if its explanation is JSON.
 */
function renderEvaluations(annotations) {
  if (!elements.evaluationsContainer) return;

  if (!annotations || annotations.length === 0) {
    elements.evaluationsContainer.innerHTML =
      "<p>Nenhuma avaliação disponível.</p>";
    return;
  }
  const getScoreClass = (score) => {
    if (score === 1.0) return "score-high";
    if (score === 0.0) return "score-low";
    return "score-mid";
  };

  // Ordem preferencial para métricas conhecidas
  const preferredOrder = [
    "Answer Completeness",
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];

  // Ordenar: primeiro as preferidas (na ordem definida), depois as demais (alfabeticamente)
  const sortedAnnotations = [...annotations].sort((a, b) => {
    const indexA = preferredOrder.indexOf(a.name);
    const indexB = preferredOrder.indexOf(b.name);

    // Se ambas estão na lista preferida, ordenar pela posição na lista
    if (indexA !== -1 && indexB !== -1) {
      return indexA - indexB;
    }

    // Se apenas uma está na lista preferida, ela vem primeiro
    if (indexA !== -1) return -1;
    if (indexB !== -1) return 1;

    // Se nenhuma está na lista preferida, ordenar alfabeticamente
    return a.name.localeCompare(b.name);
  });

  elements.evaluationsContainer.innerHTML = sortedAnnotations
    .map((ann) => {
      let explanationContentHtml = "";
      let isJsonExplanation = false;

      if (ann.explanation) {
        if (typeof ann.explanation === "object") {
          // JSON: renderizar como código JSON formatado
          explanationContentHtml = `<pre class="evaluation-json-code"><code>${JSON.stringify(
            ann.explanation,
            null,
            2
          )}</code></pre>`;
          isJsonExplanation = true;
        } else if (typeof ann.explanation === "string") {
          // Markdown: renderizar como markdown
          explanationContentHtml = marked.parse(ann.explanation);
        }
      }

      let finalExplanationSection = "";
      if (explanationContentHtml) {
        // Para JSON, usar botão de collapse
        if (isJsonExplanation) {
          const collapseId = `collapse-explanation-${
            appState.selectedRunId
          }-${ann.name.replace(/\s+/g, "-")}`;
          finalExplanationSection = `
                <div class="explanation">
                    <button class="btn btn-sm btn-outline-secondary mb-2" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                        <i class="bi bi-arrows-expand me-1"></i> Ver Detalhes
                    </button>
                    <div class="collapse" id="${collapseId}">
                        ${explanationContentHtml}
                    </div>
                </div>
            `;
        } else {
          // Para markdown, mostrar diretamente
          finalExplanationSection = `<div class="explanation">${explanationContentHtml}</div>`;
        }
      }

      return `
          <div class="evaluation-card">
              <div class="d-flex justify-content-between align-items-center">
                  <div class="score ${getScoreClass(
                    ann.score
                  )} me-3">${ann.score.toFixed(1)}</div>
                  <p class="fw-bold mb-0 flex-grow-1">${ann.name}</p>
              </div>
              ${finalExplanationSection}
          </div>
      `;
    })
    .join("");
}

// --- VISUALIZATION FEATURES ---

/**
 * MODIFIED: Counts tool calls and displays a summary before the timeline.
 * MODIFIED: Tool call numbering added.
 * MODIFIED: Tool return message parsed into distinct sections (text, sources, web_search_queries).
 * MODIFIED: Added global step numbering prefix for all timeline items, grouped by step_id.
 * NEW: Added specific icons and colors for assistant messages and usage statistics.
 * MODIFIED: "Fontes (Sources)" section within tool return is now expandable and starts collapsed, with corrected positioning and styling.
 *
 * FIX: The logic for `sequenceCounter` was refined to correctly number distinct logical turns.
 * The `sequenceCounter` now increments for `reasoning_message` and `assistant_message` types,
 * and `tool_call_message` and `tool_return_message` use the current prefix from the most recent
 * reasoning/assistant message. `letta_usage_statistics` does not receive a prefix.
 */
function renderReasoningTimeline(orderedSteps) {
  if (!elements.reasoningTimelineContainer) return;

  const parentHeader =
    elements.reasoningTimelineContainer.previousElementSibling;

  // Clear previous summary
  if (parentHeader) {
    const existingSummary = parentHeader.querySelector("#reasoning-summary");
    if (existingSummary) existingSummary.remove();
  }

  if (!orderedSteps || orderedSteps.length === 0) {
    elements.reasoningTimelineContainer.innerHTML =
      '<p class="text-muted">Nenhum passo de raciocínio disponível.</p>';
    return;
  }

  // Count tool calls for summary badge
  const toolCallCounts = orderedSteps
    .filter((step) => step.type === "tool_call_message")
    .reduce((acc, step) => {
      const toolName = step.message.tool_call.name;
      acc[toolName] = (acc[toolName] || 0) + 1;
      return acc;
    }, {});

  if (Object.keys(toolCallCounts).length > 0 && parentHeader) {
    const badges = Object.entries(toolCallCounts)
      .map(
        ([name, count]) =>
          `<span class="badge rounded-pill text-bg-secondary tool-call-badge">${name}: ${count} chamada(s)</span>`
      )
      .join(" ");
    const summaryHtml = `<div id="reasoning-summary">${badges}</div>`;
    parentHeader.insertAdjacentHTML("beforeend", summaryHtml);
  }

  let sequenceCounter = 0; // For numbering logical sequences (e.g., 1., 2., 3.)
  let currentStepPrefix = ""; // Stores the prefix (e.g., "1. ") for the current logical sequence

  const timelineItemsHtml = orderedSteps
    .map((step, index) => {
      let iconClass = "";
      let icon = "";
      let title = "";
      let content = "";
      let isNumberedStep = true; // Flag to determine if step should get a number prefix

      switch (step.type) {
        case "reasoning_message":
          sequenceCounter++; // Increment for each new reasoning turn
          currentStepPrefix = `${sequenceCounter}. `;
          iconClass = "timeline-icon-reasoning";
          icon = "bi-lightbulb";
          title = `${currentStepPrefix}Raciocínio`;
          content = `<p class="mb-0 fst-italic">"${step.message.reasoning}"</p>`;
          break;
        case "tool_call_message":
          iconClass = "timeline-icon-toolcall";
          icon = "bi-tools";
          title = `${currentStepPrefix}Chamada de Ferramenta: ${step.message.tool_call.name}`; // Use current sequence prefix
          content = `<pre><code>${JSON.stringify(
            step.message.tool_call.arguments,
            null,
            2
          )}</code></pre>`;
          break;
        case "tool_return_message":
          iconClass = "timeline-icon-return";
          icon = "bi-box-arrow-in-left";
          title = `${currentStepPrefix}Retorno da Ferramenta: ${step.message.name}`; // Use current sequence prefix
          const toolReturn = step.message.tool_return;

          let returnSections = [];
          if (typeof toolReturn === "object" && toolReturn !== null) {
            if (toolReturn.text) {
              returnSections.push(`
                              <div class="tool-return-section">
                                  <h6>Content:</h6>
                                  <div class="p-2 bg-light border rounded mt-1">${marked.parse(
                                    String(toolReturn.text)
                                  )}</div>
                              </div>`);
            }
            if (toolReturn.sources && toolReturn.sources.length > 0) {
              // MODIFIED: Add collapse for Sources with consistent styling and new line positioning
              // Robust ID generation using selectedRunId and actual step index
              const collapseId = `collapse-sources-${appState.selectedRunId}-${index}`;
              returnSections.push(`
                              <div class="tool-return-section">
                                  <h6>Sources:</h6>
                                  <button class="btn btn-sm btn-outline-secondary mb-2" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                                      <i class="bi bi-arrows-expand me-1"></i> Ver/Ocultar
                                  </button>
                                  <div class="collapse" id="${collapseId}">
                                      <pre><code>${JSON.stringify(
                                        toolReturn.sources,
                                        null,
                                        2
                                      )}</code></pre>
                                  </div>
                              </div>`);
            }
            if (
              toolReturn.web_search_queries &&
              toolReturn.web_search_queries.length > 0
            ) {
              returnSections.push(`
                              <div class="tool-return-section">
                                  <h6>Web Search Queries:</h6>
                                  <pre><code>${JSON.stringify(
                                    toolReturn.web_search_queries,
                                    null,
                                    2
                                  )}</code></pre>
                              </div>`);
            }
          }

          content =
            returnSections.join("") ||
            '<div class="p-2 bg-light border rounded">Nenhum retorno detalhado.</div>';
          break;
        case "assistant_message":
          sequenceCounter++; // Increment for each new assistant message turn
          currentStepPrefix = `${sequenceCounter}. `;
          iconClass = "timeline-icon-assistant"; // Specific icon class for assistant message
          icon = "bi-chat-text"; // A chat icon for assistant message
          title = `Mensagem do Assistente`;
          content = marked.parse(step.message.content);
          break;
        case "letta_usage_statistics":
          isNumberedStep = false; // This step should not be numbered
          iconClass = "timeline-icon-stats"; // Specific icon class for stats
          icon = "bi-bar-chart-fill";
          title = "Estatísticas de Uso"; // No step prefix for stats
          content = `
                      <p class="mb-0"><strong>Tokens Totais:</strong> ${step.message.total_tokens}</p>
                      <p class="mb-0"><strong>Tokens de Prompt:</strong> ${step.message.prompt_tokens}</p>
                      <p class="mb-0"><strong>Tokens de Conclusão:</strong> ${step.message.completion_tokens}</p>
                  `;
          break;
        default:
          return ""; // Ignore other step types
      }

      // Determine the prefix to use for the current step's title
      const actualStepPrefix = isNumberedStep ? currentStepPrefix : "";

      return `
              <div class="timeline-item">
                  <div class="timeline-icon ${iconClass}">
                      <i class="bi ${icon}"></i>
                  </div>
                  <div class="timeline-content">
                      <h6>${title}</h6>
                      ${content}
                  </div>
              </div>
          `;
    })
    .join("");

  elements.reasoningTimelineContainer.innerHTML = `<div class="timeline">${timelineItemsHtml}</div>`;
}

// handleToggleDiff removed as the button is removed

// --- FILTERING LOGIC ---

function renderFilters(experimentData) {
  if (!elements.filterContainer) return;

  const filterOptions = {};
  experimentData.forEach((exp) => {
    exp.annotations?.forEach((ann) => {
      if (!filterOptions[ann.name]) filterOptions[ann.name] = new Set();
      filterOptions[ann.name].add(ann.score);
    });
  });

  const desiredOrder = [
    "Answer Completeness",
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];
  const sortedFilterNames = Object.keys(filterOptions).sort(
    (a, b) =>
      (desiredOrder.indexOf(a) ?? Infinity) -
      (desiredOrder.indexOf(b) ?? Infinity)
  );

  let filtersHtml = sortedFilterNames
    .map((name) => {
      const scores = Array.from(filterOptions[name]).sort((a, b) => a - b);
      const filterId = `filter-${name.replace(/\s+/g, "-")}`;
      let optionsHtml =
        '<option value="">Todos</option>' +
        scores
          .map(
            (score) => `<option value="${score}">${score.toFixed(1)}</option>`
          )
          .join("");
      return `
          <div class="flex-grow-1">
              <label for="${filterId}" class="form-label small fw-bold mb-1">${name}</label>
              <select id="${filterId}" class="form-select form-select-sm" data-metric-name="${name}">${optionsHtml}</select>
          </div>`;
    })
    .join("");

  if (filtersHtml) {
    elements.filterContainer.innerHTML = `
          <div id="dynamicFilters" class="filter-grid">${filtersHtml}</div>
          <div class="d-flex gap-2 mt-2">
              <button id="applyFiltersBtn" class="btn btn-sm btn-success flex-grow-1">Aplicar</button>
              <button id="clearFiltersBtn" class="btn btn-sm btn-outline-secondary">Limpar</button>
          </div>`;
    getElement("applyFiltersBtn").addEventListener("click", applyFilters);
    getElement("clearFiltersBtn").addEventListener("click", clearFilters);
  } else {
    elements.filterContainer.innerHTML = "";
  }
}

function applyFilters() {
  const activeFilters = {};
  elements.filterContainer.querySelectorAll("select").forEach((select) => {
    if (select.value)
      activeFilters[select.dataset.metricName] = parseFloat(select.value);
  });

  const filteredRuns =
    Object.keys(activeFilters).length === 0
      ? appState.allRuns
      : appState.allRuns.filter((run) => {
          return Object.entries(activeFilters).every(
            ([metricName, targetScore]) => {
              const annotation = run.annotations?.find(
                (ann) => ann.name === metricName
              );
              return annotation && annotation.score === targetScore;
            }
          );
        });

  // Check if current selection is still valid in filtered results
  const currentRunStillVisible =
    appState.selectedRunId &&
    filteredRuns.some((run, index) => {
      const runId = run.example_id_clean || `run-${index}`;
      return runId === appState.selectedRunId;
    });

  renderRunList(filteredRuns);

  // Only reset if current selection is no longer visible
  if (!currentRunStillVisible) {
    resetDetailsPanel();
  }
}

function clearFilters() {
  elements.filterContainer
    .querySelectorAll("select")
    .forEach((select) => (select.value = ""));
  renderRunList(appState.allRuns);
  resetDetailsPanel();
}

// --- UTILITY & TOP-LEVEL RENDERING ---

function setLoadingState(isLoading) {
  if (isLoading) {
    if (elements.loadingIndicator) {
      elements.loadingIndicator.classList.remove("d-none");
    }
    // Disable refresh button if it exists and is visible
    if (
      elements.refreshExperimentBtn &&
      !elements.refreshExperimentBtn.classList.contains("d-none")
    ) {
      elements.refreshExperimentBtn.disabled = true;
      elements.refreshExperimentBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Atualizando...`;
    }
  } else {
    if (elements.loadingIndicator) {
      elements.loadingIndicator.classList.add("d-none");
    }
    // Re-enable refresh button if it exists and is visible
    if (
      elements.refreshExperimentBtn &&
      !elements.refreshExperimentBtn.classList.contains("d-none")
    ) {
      elements.refreshExperimentBtn.disabled = false;
      elements.refreshExperimentBtn.innerHTML = `<i class="bi bi-arrow-clockwise me-1"></i> Atualizar`;
    }
  }
}

function showAlert(message, type = "danger") {
  if (!elements.alertArea) return;

  const alertId = `alert-${Date.now()}`;
  elements.alertArea.innerHTML = `
      <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>`;
  if (type === "success") {
    setTimeout(() => {
      const alertElement = getElement(alertId);
      if (alertElement)
        bootstrap.Alert.getOrCreateInstance(alertElement).close();
    }, 4000);
  }
}

/**
 * NEW: Function to download the original JSON data.
 */
function downloadOriginalJson() {
  if (!appState.originalJsonData) {
    showAlert("Nenhum dado para download.", "warning");
    return;
  }

  const jsonString = JSON.stringify(appState.originalJsonData, null, 2);
  const blob = new Blob([jsonString], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;

  // Gerar nome do arquivo: experiment_name__date_in_snake_case__experiment_data.json
  const experimentName =
    appState.originalJsonData?.experiment_name ||
    appState.originalJsonData?.experiment_metadata?.name ||
    "unknown_experiment";
  const cleanExperimentName = experimentName
    .replace(/[^a-zA-Z0-9_-]/g, "_")
    .replace(/_+/g, "_");
  const dateSnakeCase = new Date()
    .toISOString()
    .slice(0, 10)
    .replace(/-/g, "_");

  a.download = `${cleanExperimentName}__${dateSnakeCase}__experiment_data.json`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showAlert("Download iniciado!", "success");
}

/**
 * MODIFIED: Corrected HTML escaping for prompt content inside pre/code tags.
 * Added download JSON button.
 */
function renderMetadata(metadata) {
  if (!metadata || !elements.metadataContainer) return;
  const createPromptSectionHTML = (title, id, collapseId) => {
    return `
            <div class="metadata-item-full-width">
                <div class="d-flex align-items-center gap-2 mb-2">
                    <strong>${title}</strong>
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                        <i class="bi bi-arrows-expand me-1"></i><span>Ver/Ocultar</span>
                    </button>
                </div>
                <div class="collapse" id="${collapseId}">
                    <pre><code id="${id}"></code></pre>
                </div>
            </div>
        `;
  };
  const promptsHTML = `
  ${createPromptSectionHTML(
    "System Prompt Principal",
    "system-prompt-code",
    "systemPromptCollapse"
  )}
  ${createPromptSectionHTML(
    "System Prompt (Similaridade)",
    "system-prompt-similarity-code",
    "systemPromptSimilarityCollapse"
  )}
`;
  elements.metadataContainer.innerHTML = `
      <div class="card-component">
          <h4 class="mb-3">Parâmetros do Experimento</h4>
          <div class="metadata-grid">
              <div class="metadata-item">
                  <strong>Modelo de Avaliação:</strong><br>
                  <span class="text-muted">${
                    metadata.eval_model || "N/A"
                  }</span>
              </div>
              <div class="metadata-item">
                  <strong>Modelo de Resposta:</strong><br>
                  <span class="text-muted">${
                    metadata.final_repose_model || "N/A"
                  }</span>
              </div>
              <div class="metadata-item">
                  <strong>Temperatura:</strong><br>
                  <span class="text-muted">${
                    metadata.temperature ?? "N/A"
                  }</span>
              </div>
              <div class="metadata-item">
                  <strong>Ferramentas:</strong><br>
                  <span class="text-muted">${
                    metadata.tools?.join(", ") || "N/A"
                  }</span>
              </div>
              ${promptsHTML}
          </div>
      </div>`;

  if (metadata.system_prompt) {
    document.getElementById("system-prompt-code").textContent =
      metadata.system_prompt;
  }
  if (metadata.system_prompt_answer_similatiry) {
    document.getElementById("system-prompt-similarity-code").textContent =
      metadata.system_prompt_answer_similatiry;
  }
  // Removed metadata download button as per requirements

  getElement("jsonModal").addEventListener("show.bs.modal", () => {
    const jsonContent = document.getElementById("jsonContent");
    if (jsonContent && appState.originalJsonData) {
      jsonContent.textContent = JSON.stringify(
        appState.originalJsonData,
        null,
        2
      );
    }
  });
}

/**
 * MODIFIED: Calculates and renders detailed summary metrics, including average,
 * counts, and percentages for each score value.
 * MODIFIED: Now explicitly checks for desired metrics and displays a "not available" message if a metric has no data.
 * ALTERED: Now, if a metric has no data, its card is not rendered at all (instead of showing "not available").
 */
function calculateAndRenderSummaryMetrics(experimentData) {
  if (!elements.summaryMetricsContainer) return;

  const metrics = {};
  const totalRuns = experimentData.length;
  if (totalRuns === 0) {
    elements.summaryMetricsContainer.innerHTML = "";
    return;
  }

  // 1. Aggregate data: scores for average, and counts for distribution
  experimentData.forEach((exp) => {
    exp.annotations?.forEach((ann) => {
      // Only process if score is a valid number, otherwise it might skew calculations
      if (typeof ann.score === "number" && !isNaN(ann.score)) {
        if (!metrics[ann.name]) {
          metrics[ann.name] = { scores: [], counts: {} };
        }
        metrics[ann.name].scores.push(ann.score);
        const scoreStr = ann.score.toFixed(1); // Group scores by one decimal place
        metrics[ann.name].counts[scoreStr] =
          (metrics[ann.name].counts[scoreStr] || 0) + 1;
      }
    });
  });

  // Ordem preferencial para métricas conhecidas
  const preferredOrder = [
    "Answer Completeness",
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];

  // 2. Criar lista de todas as métricas disponíveis
  const allMetricNames = Object.keys(metrics);

  // Ordenar: primeiro as preferidas (na ordem definida), depois as demais (alfabeticamente)
  const sortedMetricNames = [];

  // Adicionar métricas preferidas na ordem definida
  preferredOrder.forEach((name) => {
    if (allMetricNames.includes(name)) {
      sortedMetricNames.push(name);
    }
  });

  // Adicionar métricas restantes em ordem alfabética
  allMetricNames
    .filter((name) => !preferredOrder.includes(name))
    .sort()
    .forEach((name) => {
      sortedMetricNames.push(name);
    });

  // 3. Render HTML para todas as métricas disponíveis
  let metricsHtml = sortedMetricNames
    .map((name) => {
      const metric = metrics[name];
      // Se a métrica não tem scores válidos, não renderizar
      if (!metric || metric.scores.length === 0) {
        return null;
      }

      // Existing rendering logic for available metrics
      const average =
        metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;

      // Sort score distribution from highest to lowest score
      const sortedDistribution = Object.entries(metric.counts).sort(
        ([scoreA], [scoreB]) => parseFloat(scoreB) - parseFloat(scoreA)
      );

      const distributionHtml = sortedDistribution
        .map(([score, count]) => {
          // Fix: Use metric.scores.length (actual count for this metric) instead of totalRuns
          const percentage = (count / metric.scores.length) * 100;
          return `
            <div class="distribution-item">
              <span class="fw-bold">${score}</span>
              <div class="distribution-bar-bg">
                  <div class="distribution-bar" style="width: ${percentage.toFixed(
                    2
                  )}%;"></div>
              </div>
              <span class="text-muted small">${count} (${percentage.toFixed(
            0
          )}%)</span>
            </div>
          `;
        })
        .join("");

      return `
          <div class="summary-metric-card">
              <h6>${name}</h6>
              <div class="metric-main-value">${average.toFixed(
                2
              )} <small class="text-muted h6 fw-normal">avg</small></div>
              ${
                distributionHtml
                  ? `<div class="metric-distribution-header">Dist.</div>${distributionHtml}`
                  : ""
              }
          </div>`;
    })
    .filter(Boolean) // Filter out null values
    .join("");

  elements.summaryMetricsContainer.innerHTML = `
      <div class="card-component">
          <h4 class="mb-3">Métricas Gerais (${totalRuns} runs)</h4>
          <div class="summary-grid">${
            metricsHtml ||
            '<p class="text-muted">Nenhuma métrica de resumo disponível.</p>'
          }</div>
      </div>`;
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

  if (elements.themeIcon) {
    if (theme === "dark") {
      elements.themeIcon.className = "bi bi-sun-fill";
    } else {
      elements.themeIcon.className = "bi bi-moon-fill";
    }
  }
}

function showDownloadJsonLlmModal() {
  // Popular opções de filtro baseadas nos dados carregados
  populateFilterOptions();

  // Restaurar filtros salvos
  restoreSavedFilters();

  // Mostrar opções detalhadas baseadas no estado dos checkboxes
  showDetailedOptions();

  const modal = new bootstrap.Modal(
    document.getElementById("downloadJsonLlmModal")
  );
  modal.show();
}

function saveCurrentFilters() {
  const filterConfig = getSelectedFilters();

  // Salvar apenas os campos que queremos persistir
  appState.savedFilters = {
    basic_fields: filterConfig.basic_fields,
    reasoning_messages: { include: filterConfig.reasoning_messages.include },
    tool_call_messages: {
      include: filterConfig.tool_call_messages.include,
      selected_tools: filterConfig.tool_call_messages.selected_tools,
    },
    tool_return_messages: {
      include: filterConfig.tool_return_messages.include,
      selected_tools: filterConfig.tool_return_messages.selected_tools,
      selected_content: filterConfig.tool_return_messages.selected_content,
    },
    metrics: {
      include: filterConfig.metrics.include,
      selected_metrics: filterConfig.metrics.selected_metrics,
    },
  };
}

function restoreSavedFilters() {
  const saved = appState.savedFilters;

  // Restaurar campos básicos
  getElement("filter_message_id").checked =
    saved.basic_fields.includes("message_id");
  getElement("filter_menssagem").checked =
    saved.basic_fields.includes("menssagem");
  getElement("filter_golden_answer").checked =
    saved.basic_fields.includes("golden_answer");
  getElement("filter_model_response").checked =
    saved.basic_fields.includes("model_response");

  // Restaurar reasoning messages
  getElement("filter_reasoning_messages").checked =
    saved.reasoning_messages.include;

  // Restaurar tool call messages
  getElement("filter_tool_call_messages").checked =
    saved.tool_call_messages.include;

  // Restaurar tool return messages
  getElement("filter_tool_return_messages").checked =
    saved.tool_return_messages.include;

  // Restaurar métricas
  getElement("filter_metrics").checked = saved.metrics.include;

  // Restaurar ferramentas selecionadas (após um pequeno delay para garantir que as listas foram populadas)
  setTimeout(() => {
    restoreSelectedTools(
      "tool_call_tools_list",
      saved.tool_call_messages.selected_tools
    );
    restoreSelectedTools(
      "tool_return_tools_list",
      saved.tool_return_messages.selected_tools
    );
    restoreSelectedMetrics(saved.metrics.selected_metrics);
    restoreSelectedContent(saved.tool_return_messages.selected_content);
  }, 100);
}

function resetSavedFilters() {
  // Resetar para valores padrão
  appState.savedFilters = {
    basic_fields: [
      "message_id",
      "menssagem",
      "golden_answer",
      "model_response",
    ],
    reasoning_messages: { include: true },
    tool_call_messages: { include: true, selected_tools: null },
    tool_return_messages: {
      include: true,
      selected_tools: null,
      selected_content: ["text", "sources", "web_search_queries"],
    },
    metrics: { include: true, selected_metrics: null },
  };
}

function restoreSelectedTools(containerId, selectedTools) {
  if (!selectedTools) return;

  const container = getElement(containerId);
  if (!container) return;

  container.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    const toolName = checkbox.getAttribute("data-original-name");
    checkbox.checked = selectedTools.includes(toolName);
  });
}

function restoreSelectedMetrics(selectedMetrics) {
  if (!selectedMetrics) return;

  const container = getElement("metrics_list");
  if (!container) return;

  container.querySelectorAll('input[type="checkbox"]').forEach((checkbox) => {
    const metricName = checkbox.getAttribute("data-original-name");
    checkbox.checked = selectedMetrics.includes(metricName);
  });
}

function restoreSelectedContent(selectedContent) {
  if (!selectedContent) return;

  // Restaurar checkboxes de conteúdo
  if (selectedContent.includes("text")) {
    getElement("content_text").checked = true;
  }
  if (selectedContent.includes("sources")) {
    getElement("content_sources").checked = true;
  }
  if (selectedContent.includes("web_search_queries")) {
    getElement("content_web_search_queries").checked = true;
  }
}

function showDetailedOptions() {
  // Mostrar/esconder opções de tool_call baseadas no checkbox
  const toolCallCheckbox = getElement("filter_tool_call_messages");
  const toolCallOptions = getElement("tool_call_options");
  if (toolCallCheckbox && toolCallOptions) {
    toolCallOptions.style.display = toolCallCheckbox.checked
      ? "block"
      : "none";
  }

  // Mostrar/esconder opções de tool_return baseadas no checkbox
  const toolReturnCheckbox = getElement("filter_tool_return_messages");
  const toolReturnOptions = getElement("tool_return_options");
  if (toolReturnCheckbox && toolReturnOptions) {
    toolReturnOptions.style.display = toolReturnCheckbox.checked
      ? "block"
      : "none";
  }

  // Mostrar/esconder opções de metrics baseadas no checkbox
  const metricsCheckbox = getElement("filter_metrics");
  const metricsOptions = getElement("metrics_options");
  if (metricsCheckbox && metricsOptions) {
    metricsOptions.style.display = metricsCheckbox.checked ? "block" : "none";
  }
}

function populateFilterOptions() {
  if (!appState.allRuns || appState.allRuns.length === 0) {
    return;
  }

  // Coletar ferramentas únicas
  const toolsFound = new Set();
  const metricsFound = new Set();

  appState.allRuns.forEach((run) => {
    // Coletar ferramentas das reasoning messages
    const reasoningMessages = run.output?.agent_output?.ordered || [];
    reasoningMessages.forEach((msg) => {
      if (
        msg.type === "tool_call_message" ||
        msg.type === "tool_return_message"
      ) {
        const toolName = msg.message?.tool_call?.name || msg.message?.name;
        if (toolName) {
          toolsFound.add(toolName);
        }
      }
    });

    // Coletar métricas das annotations
    const annotations = run.annotations || [];
    annotations.forEach((annotation) => {
      if (annotation.name) {
        metricsFound.add(annotation.name);
      }
    });
  });

  // Popular lista de ferramentas para tool_call
  populateToolsList("tool_call_tools_list", toolsFound, "tool_call_tool_");

  // Popular lista de ferramentas para tool_return
  populateToolsList(
    "tool_return_tools_list",
    toolsFound,
    "tool_return_tool_"
  );

  // Popular lista de métricas
  populateMetricsList(metricsFound);
}

function populateToolsList(containerId, tools, idPrefix) {
  const container = getElement(containerId);
  if (!container) return;

  container.innerHTML = "";

  if (tools.size === 0) {
    container.innerHTML =
      '<div class="text-muted">Nenhuma ferramenta encontrada</div>';
    return;
  }

  const sortedTools = Array.from(tools).sort();
  sortedTools.forEach((tool) => {
    const div = document.createElement("div");
    div.className = "form-check";
    div.innerHTML = `
      <input class="form-check-input" type="checkbox" id="${idPrefix}${tool.replace(
      /[^a-zA-Z0-9]/g,
      "_"
    )}" data-original-name="${tool}" checked>
      <label class="form-check-label" for="${idPrefix}${tool.replace(
      /[^a-zA-Z0-9]/g,
      "_"
    )}">${tool}</label>
    `;
    container.appendChild(div);
  });
}

function populateMetricsList(metrics) {
  const container = getElement("metrics_list");
  if (!container) return;

  container.innerHTML = "";

  if (metrics.size === 0) {
    container.innerHTML =
      '<div class="text-muted">Nenhuma métrica encontrada</div>';
    return;
  }

  const sortedMetrics = Array.from(metrics).sort();
  sortedMetrics.forEach((metric) => {
    const div = document.createElement("div");
    div.className = "form-check";
    div.innerHTML = `
      <input class="form-check-input" type="checkbox" id="metric_${metric.replace(
        /[^a-zA-Z0-9]/g,
        "_"
      )}" data-original-name="${metric}" checked>
      <label class="form-check-label" for="metric_${metric.replace(
        /[^a-zA-Z0-9]/g,
        "_"
      )}">${metric}</label>
    `;
    container.appendChild(div);
  });
}

function getSelectedFilters() {
  const filterConfig = {
    basic_fields: [],
    reasoning_messages: { include: false },
    tool_call_messages: { include: false, selected_tools: null },
    tool_return_messages: {
      include: false,
      selected_tools: null,
      selected_content: null,
    },
    metrics: { include: false, selected_metrics: null },
  };

  // Campos básicos
  if (getElement("filter_message_id")?.checked) {
    filterConfig.basic_fields.push("message_id");
  }
  if (getElement("filter_menssagem")?.checked) {
    filterConfig.basic_fields.push("menssagem");
  }
  if (getElement("filter_golden_answer")?.checked) {
    filterConfig.basic_fields.push("golden_answer");
  }
  if (getElement("filter_model_response")?.checked) {
    filterConfig.basic_fields.push("model_response");
  }

  // Reasoning messages
  if (getElement("filter_reasoning_messages")?.checked) {
    filterConfig.reasoning_messages.include = true;
  }

  // Tool call messages
  if (getElement("filter_tool_call_messages")?.checked) {
    filterConfig.tool_call_messages.include = true;

    // Coletar ferramentas selecionadas
    const selectedTools = [];
    document
      .querySelectorAll(
        '#tool_call_tools_list input[type="checkbox"]:checked'
      )
      .forEach((checkbox) => {
        // Usar o nome original da ferramenta do atributo data
        const toolName = checkbox.getAttribute("data-original-name");
        if (toolName) {
          selectedTools.push(toolName);
        }
      });

    if (selectedTools.length > 0) {
      filterConfig.tool_call_messages.selected_tools = selectedTools;
    }
  }

  // Tool return messages
  if (getElement("filter_tool_return_messages")?.checked) {
    filterConfig.tool_return_messages.include = true;

    // Coletar ferramentas selecionadas
    const selectedTools = [];
    document
      .querySelectorAll(
        '#tool_return_tools_list input[type="checkbox"]:checked'
      )
      .forEach((checkbox) => {
        // Usar o nome original da ferramenta do atributo data
        const toolName = checkbox.getAttribute("data-original-name");
        if (toolName) {
          selectedTools.push(toolName);
        }
      });

    if (selectedTools.length > 0) {
      filterConfig.tool_return_messages.selected_tools = selectedTools;
    }

    // Coletar conteúdo selecionado
    const selectedContent = [];
    document
      .querySelectorAll(".tool-return-content:checked")
      .forEach((checkbox) => {
        if (checkbox.id === "content_text") {
          selectedContent.push("text");
        } else if (checkbox.id === "content_sources") {
          selectedContent.push("sources");
        } else if (checkbox.id === "content_web_search_queries") {
          selectedContent.push("web_search_queries");
        }
      });

    if (selectedContent.length > 0) {
      filterConfig.tool_return_messages.selected_content = selectedContent;
    }
  }

  // Metrics
  if (getElement("filter_metrics")?.checked) {
    filterConfig.metrics.include = true;

    // Coletar métricas selecionadas
    const selectedMetrics = [];
    document
      .querySelectorAll('#metrics_list input[type="checkbox"]:checked')
      .forEach((checkbox) => {
        // Usar o nome original da métrica do atributo data
        const metricName = checkbox.getAttribute("data-original-name");
        if (metricName) {
          selectedMetrics.push(metricName);
        }
      });

    if (selectedMetrics.length > 0) {
      filterConfig.metrics.selected_metrics = selectedMetrics;
    }
  }

  return filterConfig;
}

async function downloadJsonForLlm() {
  if (!appState.currentDatasetId || !appState.currentExperimentId) {
    showAlert("IDs do dataset e experimento são necessários.", "warning");
    return;
  }

  // Salvar filtros atuais antes de fazer o download
  saveCurrentFilters();

  const numberOfExperimentsInput = getElement("numberOfExperimentsLlm");
  const numberOfExperiments = numberOfExperimentsInput?.value
    ? parseInt(numberOfExperimentsInput.value)
    : null;

  // Coletar filtros selecionados
  const filterConfig = getSelectedFilters();

  try {
    const API_BASE_URL = window.API_BASE_URL_OVERRIDE;
    let url = `${API_BASE_URL}/admin/experiments/${encodeURIComponent(
      appState.currentDatasetId
    )}/${encodeURIComponent(appState.currentExperimentId)}/data_clean`;

    const params = new URLSearchParams();

    if (numberOfExperiments && numberOfExperiments > 0) {
      params.append("number_of_random_experiments", numberOfExperiments);
    }

    // Adicionar filtros como parâmetro JSON
    if (Object.keys(filterConfig).length > 0) {
      params.append("filters", JSON.stringify(filterConfig));
    }

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(
        errorData?.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    const data = await response.json();
    const jsonString = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonString], { type: "application/json" });
    const url_download = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = url_download;

    // Gerar nome do arquivo: experiment_name__date_in_snake_case__random_number__experiment_data_llm.json
    const experimentName =
      appState.originalJsonData?.experiment_name ||
      appState.originalJsonData?.experiment_metadata?.name ||
      "unknown_experiment";
    const cleanExperimentName = experimentName
      .replace(/[^a-zA-Z0-9_-]/g, "_")
      .replace(/_+/g, "_");
    const dateSnakeCase = new Date()
      .toISOString()
      .slice(0, 10)
      .replace(/-/g, "_");
    const randomSuffix = numberOfExperiments
      ? `__${numberOfExperiments}random`
      : "__all";

    a.download = `${cleanExperimentName}__${dateSnakeCase}${randomSuffix}__experiment_data_llm.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url_download);

    // Fechar o modal
    const modal = bootstrap.Modal.getInstance(
      document.getElementById("downloadJsonLlmModal")
    );
    modal.hide();

    // Limpar o input
    if (numberOfExperimentsInput) {
      numberOfExperimentsInput.value = "";
    }

    showAlert("Download JSON for LLM iniciado!", "success");
  } catch (error) {
    console.error("Erro ao fazer download do JSON for LLM:", error);
    showAlert(`Erro ao fazer download: ${error.message}`, "danger");
  }
}

```









agora escreva o plano detalhado em um arquivo ./frontend.md na raiz do repositorio

