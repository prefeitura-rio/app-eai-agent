// --- APP STATE ---
const appState = {
  currentToken: localStorage.getItem("adminToken"),
  fullExperimentData: null,
  filteredRuns: [],
  selectedRunId: null,
};

// --- DOM ELEMENTS ---
const elements = {
  loginContainer: document.querySelector(".login-container"),
  experimentsPanel: document.getElementById("experimentsPanel"),
  logoutBtn: document.getElementById("logoutBtn"),
  experimentIdInput: document.getElementById("experimentIdInput"),
  fetchExperimentBtn: document.getElementById("fetchExperimentBtn"),
  loadingIndicator: document.getElementById("loadingIndicator"),
  alertArea: document.getElementById("alertArea"),
  resultContainer: document.getElementById("resultContainer"),
  metadataContainer: document.getElementById("metadataContainer"),
  summaryMetricsContainer: document.getElementById("summaryMetricsContainer"),
  filterContainer: document.getElementById("filterContainer"),
  testRunList: document.getElementById("test-run-list"),
  mainContentArea: document.getElementById("main-content-area"),
  jsonModalCode: document.querySelector("#jsonModal pre code"),
  testRunItemTemplate: document.getElementById("test-run-item-template"),
};

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  if (appState.currentToken) {
    showExperimentsPanel();
  }
  document.addEventListener("experimentsReady", initializeApp);
});

function showExperimentsPanel() {
  elements.loginContainer.classList.add("d-none");
  elements.experimentsPanel.classList.remove("d-none");
}

function initializeApp() {
  elements.logoutBtn.addEventListener("click", handleLogout);
  elements.fetchExperimentBtn.addEventListener("click", fetchExperimentData);
  elements.experimentIdInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") fetchExperimentData();
  });
  elements.testRunList.addEventListener("click", handleTestRunSelect);
}

// --- EVENT HANDLERS ---
function handleLogout() {
  localStorage.removeItem("adminToken");
  location.reload();
}

function handleTestRunSelect(event) {
  const selectedItem = event.target.closest(".test-run-item");
  if (selectedItem && selectedItem.dataset.id !== appState.selectedRunId) {
    appState.selectedRunId = selectedItem.dataset.id;
    render();
  }
}

function handleFilters() {
  const activeFilters = {};
  elements.filterContainer.querySelectorAll("select").forEach((select) => {
    if (select.value) {
      activeFilters[select.dataset.metricName] = parseFloat(select.value);
    }
  });

  appState.filteredRuns = appState.fullExperimentData.experiment.filter(
    (exp) => {
      if (Object.keys(activeFilters).length === 0) return true;

      const annotations = exp.annotations || [];
      return Object.entries(activeFilters).every(
        ([metricName, targetScore]) => {
          const annotation = annotations.find(
            (ann) => ann.name === metricName
          );
          return annotation && annotation.score === targetScore;
        }
      );
    }
  );

  if (
    appState.selectedRunId &&
    !appState.filteredRuns.some(
      (run) => run.output.metadata.id === appState.selectedRunId
    )
  ) {
    appState.selectedRunId = null;
  }
  render();
}

function clearFilters() {
  elements.filterContainer
    .querySelectorAll("select")
    .forEach((select) => (select.value = ""));
  handleFilters();
}

// --- DATA FETCHING ---
async function fetchExperimentData() {
  const expId = elements.experimentIdInput.value.trim();
  if (!expId) {
    showAlert("Por favor, insira um ID de experimento.", "warning");
    return;
  }

  setLoading(true);
  resetUI();

  try {
    const url = `data?id=${encodeURIComponent(expId)}`;
    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${appState.currentToken}`,
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
    appState.fullExperimentData = data;
    appState.filteredRuns = [...data.experiment];
    appState.selectedRunId = null;

    elements.resultContainer.classList.remove("d-none");
    render();
    showAlert("Experimento carregado com sucesso!", "success");
  } catch (error) {
    console.error("Erro ao buscar experimento:", error);
    showAlert(`Falha ao buscar o experimento: ${error.message}`, "danger");
  } finally {
    setLoading(false);
  }
}

// --- RENDERING LOGIC ---
function render() {
  if (!appState.fullExperimentData) return;

  renderMetadata(appState.fullExperimentData.experiment_metadata);
  renderSummaryMetrics(appState.fullExperimentData.experiment);
  renderFilters(appState.fullExperimentData.experiment);
  renderSidebar();
  renderMainContent();
}

function renderSidebar() {
  elements.testRunList.innerHTML = "";

  appState.filteredRuns.forEach((run) => {
    const item =
      elements.testRunItemTemplate.content.cloneNode(true).firstElementChild;
    const runId = run.output.metadata.id;

    item.dataset.id = runId;
    item.querySelector(".test-id span").textContent = runId;

    if (runId === appState.selectedRunId) {
      item.classList.add("active");
    }

    const metricsContainer = item.querySelector(".test-metrics");
    (run.annotations || []).slice(0, 2).forEach((ann) => {
      const badge = document.createElement("span");
      badge.className = `metric-badge ${getScoreClass(ann.score)}`;
      badge.textContent = `${ann.name.split(" ")[0]}: ${ann.score.toFixed(
        1
      )}`;
      metricsContainer.appendChild(badge);
    });

    elements.testRunList.appendChild(item);
  });
}

function renderMainContent() {
  if (!appState.selectedRunId) {
    elements.mainContentArea.innerHTML = `
          <div class="placeholder-content">
              <i class="bi bi-eyedropper"></i>
              <h5>Selecione um Test Run</h5>
              <p>Clique em um item da lista à esquerda para ver os detalhes.</p>
          </div>`;
    return;
  }

  const runData = appState.fullExperimentData.experiment.find(
    (exp) => exp.output.metadata.id === appState.selectedRunId
  );
  if (!runData) return;

  elements.mainContentArea.innerHTML = "";

  const userMessageSection = createSection(
    "Mensagem do Usuário",
    `
      <div class="alert alert-secondary">${runData.input.mensagem_whatsapp_simulada}</div>
  `
  );
  elements.mainContentArea.appendChild(userMessageSection);

  const agentAnswerHtml = marked.parse(
    runData.output.agent_output?.ordered.find(
      (m) => m.type === "assistant_message"
    )?.message.content || "N/A"
  );
  const goldenAnswerHtml = marked.parse(
    runData.reference_output.golden_answer || "N/A"
  );
  const diffHtml = generateDiffHtml(goldenAnswerHtml, agentAnswerHtml);

  const comparisonSection = createSection(
    "Comparação de Respostas",
    `
      <div class="row g-4">
          <div class="col-md-6">
              <div class="comparison-box">
                  <h5><i class="bi bi-robot text-primary"></i> Resposta do Agente</h5>
                  <div class="diff-output">${diffHtml.agent}</div>
              </div>
          </div>
          <div class="col-md-6">
              <div class="comparison-box">
                  <h5><i class="bi bi-trophy-fill" style="color:var(--gold);"></i> Resposta de Referência</h5>
                  <div class="diff-output">${diffHtml.golden}</div>
              </div>
          </div>
      </div>
  `
  );
  elements.mainContentArea.appendChild(comparisonSection);

  elements.mainContentArea.appendChild(
    createSection("Avaliações", renderEvaluations(runData.annotations))
  );
  elements.mainContentArea.appendChild(
    createSection(
      "Passo a Passo do Agente",
      renderReasoningTimeline(runData.output.agent_output?.ordered)
    )
  );
}

function renderMetadata(metadata) {
  if (!metadata) return;

  const promptsHTML = `
      <div class="d-flex justify-content-between align-items-center mt-3">
          <strong>System Prompt Principal</strong>
          <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#systemPromptCollapse"><i class="bi bi-arrows-expand"></i></button>
      </div>
      <div class="collapse" id="systemPromptCollapse"><pre><code>${
        metadata.system_prompt || ""
      }</code></pre></div>
  `;

  elements.metadataContainer.innerHTML = `
      <div class="card mb-4">
          <div class="card-body">
              <div class="d-flex justify-content-between align-items-center">
                  <h4 class="card-title mb-0">Parâmetros do Experimento</h4>
                  <div>
                      <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#jsonModal"><i class="bi bi-code-slash"></i> Ver JSON</button>
                      <button class="btn btn-sm btn-primary" id="downloadJsonBtn"><i class="bi bi-download"></i> Baixar JSON</button>
                  </div>
              </div>
              <hr>
              <p class="mb-1"><strong>Modelo de Avaliação:</strong> ${
                metadata.eval_model || "N/A"
              }</p>
              <p class="mb-1"><strong>Modelo de Resposta Final:</strong> ${
                metadata.final_repose_model || "N/A"
              }</p>
              ${promptsHTML}
          </div>
      </div>
  `;

  elements.jsonModalCode.textContent = JSON.stringify(
    appState.fullExperimentData,
    null,
    2
  );
  document.getElementById("downloadJsonBtn").addEventListener("click", () => {
    const expId = elements.experimentIdInput.value.trim() || "experiment";
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(
        JSON.stringify(appState.fullExperimentData, null, 2)
      );
    const a = document.createElement("a");
    a.href = dataStr;
    a.download = `experiment-${expId}.json`;
    a.click();
    a.remove();
  });
}

function renderSummaryMetrics(experimentData) {
  const metrics = {};
  experimentData.forEach((exp) => {
    (exp.annotations || []).forEach((ann) => {
      if (!metrics[ann.name]) metrics[ann.name] = { scores: [], counts: {} };
      metrics[ann.name].scores.push(ann.score);
      const scoreKey = ann.score;
      metrics[ann.name].counts[scoreKey] =
        (metrics[ann.name].counts[scoreKey] || 0) + 1;
    });
  });

  const desiredOrder = [
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];
  const sortedMetricNames = Object.keys(metrics).sort(
    (a, b) =>
      (desiredOrder.indexOf(a) ?? 99) - (desiredOrder.indexOf(b) ?? 99)
  );

  let metricsHtml = `<h5 class="sidebar-section-title">Métricas Gerais (${experimentData.length} runs)</h5>`;
  sortedMetricNames.forEach((name) => {
    const metric = metrics[name];
    const average =
      metric.scores.length > 0
        ? metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length
        : 0;
    const distributionHtml = Object.entries(metric.counts)
      .sort(([scoreA], [scoreB]) => parseFloat(scoreB) - parseFloat(scoreA))
      .map(
        ([score, count]) =>
          `<span>${parseFloat(score).toFixed(1)}: ${count}</span>`
      )
      .join("");

    metricsHtml += `
          <div class="summary-metric-item">
              <h6>${name}</h6>
              <div class="average-score">${average.toFixed(2)}</div>
              <div class="score-distribution">${distributionHtml}</div>
          </div>`;
  });
  elements.summaryMetricsContainer.innerHTML = metricsHtml;
}

function renderFilters(experimentData) {
  const filterOptions = {};
  experimentData.forEach((exp) => {
    (exp.annotations || []).forEach((ann) => {
      if (!filterOptions[ann.name]) filterOptions[ann.name] = new Set();
      filterOptions[ann.name].add(ann.score);
    });
  });

  const desiredOrder = [
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];
  const sortedFilterNames = Object.keys(filterOptions).sort(
    (a, b) =>
      (desiredOrder.indexOf(a) ?? 99) - (desiredOrder.indexOf(b) ?? 99)
  );

  let filtersHtml = sortedFilterNames
    .map((name) => {
      const scores = Array.from(filterOptions[name]).sort((a, b) => a - b);
      let optionsHtml =
        '<option value="">Qualquer Nota</option>' +
        scores
          .map(
            (score) => `<option value="${score}">${score.toFixed(1)}</option>`
          )
          .join("");
      return `
          <div class="mb-2">
              <label class="form-label small fw-bold">${name}</label>
              <select class="form-select form-select-sm" data-metric-name="${name}">${optionsHtml}</select>
          </div>`;
    })
    .join("");

  if (filtersHtml) {
    elements.filterContainer.innerHTML = `
          <div class="card mt-4 mb-4">
               <div class="card-body">
                   <h5 class="card-title small">Filtros de Avaliação</h5>
                   ${filtersHtml}
                   <div class="d-flex gap-2 mt-3">
                       <button id="applyFiltersBtn" class="btn btn-sm btn-primary w-100">Aplicar</button>
                       <button id="clearFiltersBtn" class="btn btn-sm btn-outline-secondary w-100">Limpar</button>
                   </div>
               </div>
          </div>`;
    document
      .getElementById("applyFiltersBtn")
      .addEventListener("click", handleFilters);
    document
      .getElementById("clearFiltersBtn")
      .addEventListener("click", clearFilters);
  }
}

function renderEvaluations(annotations) {
  if (!annotations || annotations.length === 0)
    return "<p>Nenhuma avaliação disponível.</p>";

  const grid = document.createElement("div");
  grid.className = "evaluation-grid";

  annotations.forEach((ann) => {
    const card = document.createElement("div");
    card.className = "evaluation-card";

    let explanationContent = "";
    if (ann.explanation) {
      explanationContent =
        typeof ann.explanation === "object"
          ? `<pre><code>${JSON.stringify(
              ann.explanation,
              null,
              2
            )}</code></pre>`
          : marked.parse(String(ann.explanation));
    }

    card.innerHTML = `
          <div class="d-flex justify-content-between align-items-center mb-2">
              <p class="name mb-0">${ann.name}</p>
              <div class="score ${getScoreClass(
                ann.score
              )}">${ann.score.toFixed(1)}</div>
          </div>
          ${
            explanationContent
              ? `<div class="explanation">${explanationContent}</div>`
              : ""
          }
      `;
    grid.appendChild(card);
  });
  return grid.outerHTML;
}

function renderReasoningTimeline(orderedSteps) {
  if (!orderedSteps || orderedSteps.length === 0)
    return "<p>Nenhum passo a passo disponível.</p>";

  const timeline = document.createElement("div");
  timeline.className = "reasoning-timeline";

  orderedSteps.forEach((step) => {
    const stepEl = document.createElement("div");
    let title = "",
      content = "",
      typeClass = "";

    if (step.type === "reasoning_message") {
      typeClass = "type-reasoning";
      title = "🧠 Raciocínio";
      content = `<div class="step-content reasoning">"${step.message.reasoning}"</div>`;
    } else if (step.type === "tool_call_message") {
      typeClass = "type-tool-call";
      title = `🔧 Chamada de Ferramenta: <strong>${step.message.tool_call.name}</strong>`;
      content = `<div class="step-content"><pre><code>${JSON.stringify(
        step.message.tool_call.arguments,
        null,
        2
      )}</code></pre></div>`;
    } else if (step.type === "tool_return_message") {
      typeClass = "type-tool-return";
      title = "↪️ Retorno da Ferramenta";
      const returnData = step.message.tool_return;
      const contentData =
        typeof returnData === "object" && returnData !== null
          ? JSON.stringify(returnData, null, 2)
          : String(returnData);
      content = `<div class="step-content"><pre><code>${contentData}</code></pre></div>`;
    }

    if (title) {
      stepEl.className = `reasoning-step ${typeClass}`;
      stepEl.innerHTML = `<div class="step-title">${title}</div>${content}`;
      timeline.appendChild(stepEl);
    }
  });
  return timeline.outerHTML;
}

// --- UTILITY FUNCTIONS ---
function setLoading(isLoading) {
  elements.loadingIndicator.classList.toggle("d-none", !isLoading);
  elements.fetchExperimentBtn.disabled = isLoading;
  elements.fetchExperimentBtn.innerHTML = isLoading
    ? '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...'
    : '<i class="bi bi-search me-1"></i> Buscar';
}

function resetUI() {
  appState.fullExperimentData = null;
  appState.filteredRuns = [];
  appState.selectedRunId = null;
  elements.alertArea.innerHTML = "";
  elements.resultContainer.classList.add("d-none");
  elements.metadataContainer.innerHTML = "";
  elements.summaryMetricsContainer.innerHTML = "";
  elements.filterContainer.innerHTML = "";
  elements.testRunList.innerHTML = "";
  elements.mainContentArea.innerHTML = "";
}

function showAlert(message, type = "danger") {
  const alertId = `alert-${Date.now()}`;
  elements.alertArea.innerHTML = `
      <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
          ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>`;
  if (type === "success") {
    setTimeout(() => document.getElementById(alertId)?.remove(), 4000);
  }
}

function getScoreClass(score) {
  if (score === 1.0) return "score-high";
  if (score === 0.0) return "score-low";
  return "score-mid";
}

function createSection(title, content) {
  const section = document.createElement("div");
  section.innerHTML = `<h3 class="section-title">${title}</h3>${content}`;
  return section;
}

function generateDiffHtml(goldenText, agentText) {
  const cleanGolden =
    new DOMParser().parseFromString(goldenText, "text/html").body
      .textContent || "";
  const cleanAgent =
    new DOMParser().parseFromString(agentText, "text/html").body
      .textContent || "";

  const goldenLines = cleanGolden.split("\n");
  const agentLines = cleanAgent.split("\n");

  const matrix = Array(agentLines.length + 1)
    .fill(null)
    .map(() => Array(goldenLines.length + 1).fill(0));
  for (let i = 1; i <= agentLines.length; i++) {
    for (let j = 1; j <= goldenLines.length; j++) {
      if (agentLines[i - 1] === goldenLines[j - 1]) {
        matrix[i][j] = 1 + matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.max(matrix[i - 1][j], matrix[i][j - 1]);
      }
    }
  }

  let i = agentLines.length,
    j = goldenLines.length;
  let agentResult = [],
    goldenResult = [];

  while (i > 0 || j > 0) {
    if (i > 0 && j > 0 && agentLines[i - 1] === goldenLines[j - 1]) {
      agentResult.unshift(agentLines[i - 1]);
      goldenResult.unshift(goldenLines[j - 1]);
      i--;
      j--;
    } else if (j > 0 && (i === 0 || matrix[i][j - 1] >= matrix[i - 1][j])) {
      goldenResult.unshift(`<del>${goldenLines[j - 1]}</del>`);
      agentResult.unshift("");
      j--;
    } else if (i > 0 && (j === 0 || matrix[i][j - 1] < matrix[i - 1][j])) {
      agentResult.unshift(`<ins>${agentLines[i - 1]}</ins>`);
      goldenResult.unshift("");
      i--;
    } else {
      break;
    }
  }

  // Filter out empty lines that were placeholders for alignment
  const finalGolden = goldenResult.filter((line) => line !== "").join("\n");
  const finalAgent = agentResult.filter((line) => line !== "").join("\n");

  return {
    golden: `<pre>${finalGolden}</pre>`,
    agent: `<pre>${finalAgent}</pre>`,
  };
}
