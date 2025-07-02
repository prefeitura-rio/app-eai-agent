document.addEventListener("DOMContentLoaded", () => {
  // --- STATE MANAGEMENT ---
  const state = {
    token: localStorage.getItem("adminToken"),
    fullExperimentData: null,
    activeRunId: null,
    filteredRunIds: [],
  };

  // --- DOM ELEMENTS ---
  const dom = {
    logoutBtn: document.getElementById("logoutBtn"),
    experimentsPanel: document.getElementById("experimentsPanel"),
    experimentIdInput: document.getElementById("experimentIdInput"),
    fetchExperimentBtn: document.getElementById("fetchExperimentBtn"),
    loadingIndicator: document.getElementById("loadingIndicator"),
    alertArea: document.getElementById("alertArea"),
    resultContainer: document.getElementById("resultContainer"),
    metadataContainer: document.getElementById("metadataContainer"),
    summaryMetricsContainer: document.getElementById(
      "summaryMetricsContainer"
    ),
    filterContainer: document.getElementById("filterContainer"),
    testRunsList: document.getElementById("test-runs-list"),
    mainContentArea: document.getElementById("main-content-area"),
  };

  // --- UTILITY & HELPER FUNCTIONS ---
  const showAlert = (message, type = "danger") => {
    const alertId = `alert-${Date.now()}`;
    dom.alertArea.innerHTML = `
          <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
              ${message}
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          </div>`;
    if (type === "success") {
      setTimeout(() => {
        const alertEl = document.getElementById(alertId);
        if (alertEl) new bootstrap.Alert(alertEl).close();
      }, 5000);
    }
  };

  const getScoreClass = (score) => {
    if (score === 1.0) return "score-high";
    if (score === 0.0) return "score-low";
    return "score-mid";
  };

  const getScoreBadgeClass = (score) => {
    if (score === 1.0) return "score-badge-high";
    if (score === 0.0) return "score-badge-low";
    return "score-badge-mid";
  };

  // --- RENDER FUNCTIONS ---

  const renderPlaceholder = (area, iconClass, title, text) => {
    area.innerHTML = `
          <div class="content-placeholder">
              <i class="bi ${iconClass}"></i>
              <h5>${title}</h5>
              <p>${text}</p>
          </div>`;
  };

  const renderMetadata = (metadata) => {
    if (!metadata) return;
    dom.metadataContainer.innerHTML = `
          <div class="card metadata-card">
              <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                  <h4 class="mb-0">Parâmetros do Experimento</h4>
                  <div>
                      <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#jsonModal">
                          <i class="bi bi-code-slash me-1"></i> Ver JSON
                      </button>
                      <button class="btn btn-sm btn-primary" id="downloadJsonBtn">
                          <i class="bi bi-download me-1"></i> Baixar JSON
                      </button>
                  </div>
              </div>
              <hr class="my-3">
              <div class="metadata-grid">
                  <div class="metadata-item"><strong>Modelo de Avaliação:</strong> ${
                    metadata.eval_model || "N/A"
                  }</div>
                  <div class="metadata-item"><strong>Modelo de Resposta Final:</strong> ${
                    metadata.final_repose_model || "N/A"
                  }</div>
                  <div class="metadata-item"><strong>Temperatura:</strong> ${
                    metadata.temperature || "N/A"
                  }</div>
                  <div class="metadata-item"><strong>Ferramentas:</strong> ${
                    metadata.tools?.join(", ") || "N/A"
                  }</div>
              </div>
          </div>`;

    document
      .getElementById("downloadJsonBtn")
      .addEventListener("click", downloadJson);
  };

  const renderSummaryMetrics = (runs) => {
    const metrics = {};
    runs.forEach((run) => {
      run.annotations?.forEach((ann) => {
        if (!metrics[ann.name])
          metrics[ann.name] = { scores: [], counts: {} };
        metrics[ann.name].scores.push(ann.score);
        metrics[ann.name].counts[ann.score] =
          (metrics[ann.name].counts[ann.score] || 0) + 1;
      });
    });

    const desiredOrder = [
      "Answer Similarity",
      "Activate Search Tools",
      "Golden Link in Answer",
      "Golden Link in Tool Calling",
    ];
    const sortedMetricNames = Object.keys(metrics).sort(
      (a, b) => desiredOrder.indexOf(a) - desiredOrder.indexOf(b)
    );

    const metricsHtml = sortedMetricNames
      .map((name) => {
        const metric = metrics[name];
        const average =
          metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;
        const distributionHtml = Object.entries(metric.counts)
          .sort(
            ([scoreA], [scoreB]) => parseFloat(scoreB) - parseFloat(scoreA)
          )
          .map(
            ([score, count]) =>
              `<span>${parseFloat(score).toFixed(1)}: ${count}</span>`
          )
          .join("");

        return `
              <div class="summary-metric-item">
                  <h6>${name}</h6>
                  <div class="average-score">${average.toFixed(2)}</div>
                  <div class="score-distribution">${distributionHtml}</div>
              </div>`;
      })
      .join("");

    dom.summaryMetricsContainer.innerHTML = `
          <div class="card metadata-card">
              <h4 class="mb-3">Métricas Gerais (${runs.length} runs)</h4>
              <div class="summary-grid">${metricsHtml}</div>
          </div>`;
  };

  const renderFilters = (runs) => {
    const filterOptions = {};
    runs.forEach((run) => {
      run.annotations?.forEach((ann) => {
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
      (a, b) => desiredOrder.indexOf(a) - desiredOrder.indexOf(b)
    );

    const filtersHtml = sortedFilterNames
      .map((name) => {
        const scores = Array.from(filterOptions[name]).sort((a, b) => a - b);
        const filterId = `filter-${name.replace(/\s+/g, "-")}`;
        const optionsHtml = scores
          .map(
            (score) => `<option value="${score}">${score.toFixed(1)}</option>`
          )
          .join("");
        return `
              <div class="flex-grow-1">
                  <label for="${filterId}" class="form-label small fw-bold">${name}</label>
                  <select id="${filterId}" class="form-select" data-metric-name="${name}">
                      <option value="">Qualquer Nota</option>${optionsHtml}
                  </select>
              </div>`;
      })
      .join("");

    if (filtersHtml) {
      dom.filterContainer.innerHTML = `
              <div class="card metadata-card">
                   <h4 class="mb-3">Filtros de Avaliação</h4>
                   <div id="dynamicFilters" class="d-flex flex-wrap gap-3">${filtersHtml}</div>
                   <div class="d-flex gap-2 mt-3">
                       <button id="applyFiltersBtn" class="btn btn-primary"><i class="bi bi-funnel-fill me-1"></i> Aplicar</button>
                       <button id="clearFiltersBtn" class="btn btn-outline-secondary">Limpar</button>
                   </div>
              </div>`;
      document
        .getElementById("applyFiltersBtn")
        .addEventListener("click", applyFilters);
      document
        .getElementById("clearFiltersBtn")
        .addEventListener("click", clearFilters);
    }
  };

  const renderSidebar = () => {
    const runsData = state.fullExperimentData.experiment.filter((run) =>
      state.filteredRunIds.includes(run.example_id)
    );

    if (runsData.length === 0) {
      dom.testRunsList.innerHTML = `<li class="list-group-item text-center text-muted">Nenhum resultado encontrado.</li>`;
      return;
    }

    dom.testRunsList.innerHTML = runsData
      .map((run) => {
        const scoresHtml = (run.annotations || [])
          .map(
            (ann) =>
              `<span class="run-score-badge ${getScoreBadgeClass(
                ann.score
              )}">${ann.name.split(" ")[0]}: ${ann.score.toFixed(1)}</span>`
          )
          .join("");
        return `
              <a href="#" class="list-group-item list-group-item-action" data-run-id="${run.example_id}">
                  <strong>ID do Teste: ${run.output.metadata.id}</strong>
                  <div class="run-item-scores">${scoresHtml}</div>
              </a>`;
      })
      .join("");
  };

  const renderMainContent = (runId) => {
    const runData = state.fullExperimentData.experiment.find(
      (r) => r.example_id === runId
    );
    if (!runData) {
      renderPlaceholder(
        dom.mainContentArea,
        "bi-x-circle",
        "Erro",
        "Não foi possível encontrar os dados para este Test Run."
      );
      return;
    }

    const agentAnswerHtml = runData.output.agent_output?.ordered.find(
      (m) => m.type === "assistant_message"
    )
      ? marked.parse(
          runData.output.agent_output.ordered.find(
            (m) => m.type === "assistant_message"
          ).message.content
        )
      : "<p class='text-muted'>N/A</p>";

    const goldenAnswerHtml = runData.reference_output.golden_answer
      ? marked.parse(runData.reference_output.golden_answer)
      : "<p class='text-muted'>N/A</p>";

    const evaluationsHtml = (runData.annotations || [])
      .map((ann) => {
        const explanationContent = ann.explanation
          ? marked.parse(ann.explanation)
          : "";
        return `
              <div class="evaluation-card">
                  <div class="main-info">
                      <p class="name">${ann.name}</p>
                      <div class="score ${getScoreClass(
                        ann.score
                      )}">${ann.score.toFixed(1)}</div>
                  </div>
                  ${
                    explanationContent
                      ? `<div class="explanation">${explanationContent}</div>`
                      : ""
                  }
              </div>`;
      })
      .join("");

    const reasoningSteps = runData.output.agent_output?.ordered || [];
    const reasoningHtml = reasoningSteps
      .map((step) => {
        if (step.type === "reasoning_message")
          return `<div class="reasoning-step"><strong>🧠 Raciocínio:</strong><p>"${step.message.reasoning}"</p></div>`;
        if (step.type === "tool_call_message")
          return `<div class="reasoning-step"><strong>🔧 Chamada de Ferramenta: ${
            step.message.tool_call.name
          }</strong><pre><code>${JSON.stringify(
            step.message.tool_call.arguments,
            null,
            2
          )}</code></pre></div>`;
        if (step.type === "tool_return_message")
          return `<div class="reasoning-step"><strong>↪️ Retorno:</strong><pre><code>${
            typeof step.message.tool_return === "string"
              ? step.message.tool_return
              : JSON.stringify(step.message.tool_return, null, 2)
          }</code></pre></div>`;
        return "";
      })
      .join("");

    dom.mainContentArea.innerHTML = `
          <h4 class="section-title">Mensagem do Usuário</h4>
          <div class="alert alert-secondary">${
            runData.input.mensagem_whatsapp_simulada
          }</div>

          <h4 class="section-title">Comparação de Respostas</h4>
          <div class="row g-4">
              <div class="col-lg-6"><div class="comparison-box"><h5 class="agent-answer">🤖 Resposta do Agente</h5><div class="markdown-content">${agentAnswerHtml}</div></div></div>
              <div class="col-lg-6"><div class="comparison-box"><h5 class="golden-answer">🏆 Resposta de Referência (Golden)</h5><div class="markdown-content">${goldenAnswerHtml}</div></div></div>
          </div>

          <h4 class="section-title">Avaliações</h4>
          <div class="evaluations-grid">${
            evaluationsHtml || "<p>Nenhuma avaliação disponível.</p>"
          }</div>

          <h4 class="section-title">Passo a Passo do Agente (Reasoning)</h4>
          <div>${
            reasoningHtml || "<p>Nenhum passo a passo disponível.</p>"
          }</div>
      `;
  };

  // --- APPLICATION LOGIC ---

  const initializeDashboard = (data) => {
    state.fullExperimentData = data;
    state.filteredRunIds = data.experiment.map((run) => run.example_id);

    renderMetadata(data.experiment_metadata);
    renderSummaryMetrics(data.experiment);
    renderFilters(data.experiment);
    renderSidebar();

    if (state.filteredRunIds.length > 0) {
      updateActiveRun(state.filteredRunIds[0]);
    } else {
      renderPlaceholder(
        dom.mainContentArea,
        "bi-inbox",
        "Nenhum Test Run",
        "Este experimento não contém nenhum resultado para exibir."
      );
    }

    dom.resultContainer.classList.remove("d-none");
  };

  const updateActiveRun = (runId) => {
    state.activeRunId = runId;

    // Update sidebar active state
    dom.testRunsList.querySelectorAll(".list-group-item").forEach((item) => {
      item.classList.toggle("active", item.dataset.runId === runId);
    });

    // Render main content
    renderMainContent(runId);
  };

  const applyFilters = () => {
    const activeFilters = {};
    document.querySelectorAll("#dynamicFilters select").forEach((select) => {
      if (select.value) {
        activeFilters[select.dataset.metricName] = parseFloat(select.value);
      }
    });

    state.filteredRunIds = state.fullExperimentData.experiment
      .filter((run) => {
        for (const metricName in activeFilters) {
          const targetScore = activeFilters[metricName];
          const annotation = run.annotations?.find(
            (ann) => ann.name === metricName
          );
          if (!annotation || annotation.score !== targetScore) {
            return false;
          }
        }
        return true;
      })
      .map((run) => run.example_id);

    renderSidebar();

    if (state.filteredRunIds.length > 0) {
      const newActiveId = state.filteredRunIds.includes(state.activeRunId)
        ? state.activeRunId
        : state.filteredRunIds[0];
      updateActiveRun(newActiveId);
    } else {
      renderPlaceholder(
        dom.mainContentArea,
        "bi-funnel",
        "Nenhum Resultado",
        "Ajuste os filtros para encontrar resultados."
      );
    }
  };

  const clearFilters = () => {
    document.querySelectorAll("#dynamicFilters select").forEach((select) => {
      select.value = "";
    });
    state.filteredRunIds = state.fullExperimentData.experiment.map(
      (run) => run.example_id
    );
    renderSidebar();
    if (state.activeRunId) {
      updateActiveRun(state.activeRunId);
    } else if (state.filteredRunIds.length > 0) {
      updateActiveRun(state.filteredRunIds[0]);
    }
  };

  const fetchExperimentData = () => {
    const expId = dom.experimentIdInput.value.trim();
    if (!expId) {
      showAlert("Por favor, insira um ID de experimento.", "warning");
      return;
    }

    dom.loadingIndicator.classList.remove("d-none");
    dom.resultContainer.classList.add("d-none");
    dom.alertArea.innerHTML = "";
    dom.fetchExperimentBtn.disabled = true;
    dom.fetchExperimentBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';

    const url = `data?id=${encodeURIComponent(expId)}`;
    fetch(url, { headers: { Authorization: `Bearer ${state.token}` } })
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
        initializeDashboard(data);
        showAlert("Experimento carregado com sucesso!", "success");
      })
      .catch((error) => {
        console.error("Erro ao buscar experimento:", error);
        showAlert(
          `Falha ao buscar o experimento: ${error.message}`,
          "danger"
        );
        dom.resultContainer.classList.add("d-none");
      })
      .finally(() => {
        dom.loadingIndicator.classList.add("d-none");
        dom.fetchExperimentBtn.disabled = false;
        dom.fetchExperimentBtn.innerHTML =
          '<i class="bi bi-search me-1"></i> Buscar';
      });
  };

  const downloadJson = () => {
    if (!state.fullExperimentData) return;
    const expId = dom.experimentIdInput.value.trim() || "experiment";
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(state.fullExperimentData, null, 2));
    const dl = document.createElement("a");
    dl.setAttribute("href", dataStr);
    dl.setAttribute("download", `experiment-${expId}.json`);
    dl.click();
    dl.remove();
  };

  // --- EVENT LISTENERS ---
  const handleLogout = () => {
    localStorage.removeItem("adminToken");
    location.reload();
  };

  const handleSidebarClick = (e) => {
    e.preventDefault();
    const target = e.target.closest(".list-group-item");
    if (
      target &&
      target.dataset.runId &&
      target.dataset.runId !== state.activeRunId
    ) {
      updateActiveRun(target.dataset.runId);
    }
  };

  const initializeEventListeners = () => {
    if (dom.logoutBtn) dom.logoutBtn.addEventListener("click", handleLogout);
    if (dom.fetchExperimentBtn)
      dom.fetchExperimentBtn.addEventListener("click", fetchExperimentData);
    if (dom.experimentIdInput)
      dom.experimentIdInput.addEventListener(
        "keypress",
        (e) => e.key === "Enter" && fetchExperimentData()
      );
    if (dom.testRunsList)
      dom.testRunsList.addEventListener("click", handleSidebarClick);

    // Setup JSON modal
    const jsonModal = document.getElementById("jsonModal");
    if (jsonModal) {
      jsonModal.addEventListener("show.bs.modal", () => {
        const preCode = jsonModal.querySelector("pre code");
        if (preCode && state.fullExperimentData) {
          preCode.textContent = JSON.stringify(
            state.fullExperimentData,
            null,
            2
          );
        }
      });
    }
  };

  // --- APP INITIALIZATION ---
  document.addEventListener("experimentsReady", initializeEventListeners);
  if (state.token) {
    // If already logged in from the HTML script part, initialize directly
    initializeEventListeners();
  }
  renderPlaceholder(
    dom.mainContentArea,
    "bi-clipboard-data",
    "Pronto para Análise",
    "Busque por um ID de experimento para começar."
  );
});
