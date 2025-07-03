/*
 * Final Integrated JavaScript
 * Contains core logic and visualization features.
 * Refactored to implement new data display requirements.
 */

// --- GLOBAL STATE ---
let appState = {
  allRuns: [],
  selectedRunId: null,
  filters: {},
  originalJsonData: null,
  currentToken: localStorage.getItem("adminToken"),
};

// --- DOM ELEMENT SELECTORS ---
const getElement = (id) => document.getElementById(id);

const elements = {
  loginOverlay: getElement("login-overlay"),
  loginForm: getElement("loginForm"),
  errorMsg: getElement("errorMsg"),
  experimentsPanel: getElement("experimentsPanel"),
  logoutBtn: getElement("logoutBtn"),
  experimentIdInput: getElement("experimentIdInput"),
  fetchExperimentBtn: getElement("fetchExperimentBtn"),
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
  if (appState.currentToken) {
    showExperimentsPanel();
  } else {
    elements.loginOverlay.classList.remove("d-none");
  }

  elements.loginForm.addEventListener("submit", handleLogin);
  elements.logoutBtn.addEventListener("click", handleLogout);
  elements.fetchExperimentBtn.addEventListener("click", fetchExperimentData);
  elements.experimentIdInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") fetchExperimentData();
  });
  elements.runList.addEventListener("click", handleRunClick);
  // elements.toggleDiffBtn.addEventListener("click", handleToggleDiff); // Removed as requested
});

// --- AUTHENTICATION (Unchanged as per instructions) ---
function handleLogin(e) {
  e.preventDefault();
  const tokenInput = getElement("token");
  const token = tokenInput.value.trim().replace(/["\n\r]/g, "");
  if (!token) return;

  const API_BASE_URL =
    window.API_BASE_URL_OVERRIDE ||
    "https://services.staging.app.dados.rio/eai-agent";
  // Assuming 'requestUrl' is meant to be a placeholder for a general API endpoint to validate the token
  // For a real application, you'd typically have a specific /auth/validate or /me endpoint.
  // For now, I'll use a generic existing endpoint (like data endpoint without params) if no specific one is defined for validation,
  // or you should replace this with your actual token validation URL.
  // Using a dummy URL for now, as per previous instructions context this might have been implied for a general fetch.
  // If the server requires *any* endpoint with valid token, /data without params might work or needs specific /auth endpoint.
  const validationUrl = `${API_BASE_URL}/data?id=dummy`; // A non-existent but authenticated endpoint just to check token

  fetch(validationUrl, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
  })
    .then((response) => {
      // If the response is not OK, it means the token is likely invalid or expired.
      if (!response.ok) {
        // Attempt to parse error message from response body if available
        return response
          .json()
          .then((errorData) => {
            throw new Error(
              errorData.detail ||
                `Authentication failed (Status: ${response.status})`
            );
          })
          .catch(() => {
            // If JSON parsing fails, use generic error message
            throw new Error(
              `Authentication failed (Status: ${response.status})`
            );
          });
      }
      // If response is OK, token is valid
      return response.json(); // Or just response.text() if body is not important
    })
    .then(() => {
      localStorage.setItem("adminToken", token);
      appState.currentToken = token;
      showExperimentsPanel(); // Correctly shows the panel
    })
    .catch((error) => {
      elements.errorMsg.textContent = `Token inválido ou erro de autenticação: ${error.message}`;
      elements.errorMsg.classList.remove("d-none");
    });
}

function handleLogout() {
  localStorage.removeItem("adminToken");
  appState.currentToken = null;
  location.reload();
}

// FIX: Ensure d-flex is added when showing the panel
function showExperimentsPanel() {
  elements.loginOverlay.classList.add("d-none");
  elements.experimentsPanel.classList.remove("d-none");
  elements.experimentsPanel.classList.add("d-flex"); // Crucial line to apply flex display
}

// --- DATA FETCHING ---
function fetchExperimentData() {
  const expId = elements.experimentIdInput.value.trim();
  if (!expId) {
    showAlert("Por favor, insira um ID de experimento.", "warning");
    return;
  }

  setLoadingState(true);

  const API_BASE_URL =
    window.API_BASE_URL_OVERRIDE ||
    "https://services.staging.app.dados.rio/eai-agent";
  const url = `${API_BASE_URL}/admin/experiments_v2/data?id=${encodeURIComponent(
    expId
  )}`;

  fetch(url, {
    headers: {
      Authorization: `Bearer ${appState.currentToken}`,
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

      renderMetadata(data.experiment_metadata);
      calculateAndRenderSummaryMetrics(data.experiment);
      renderFilters(data.experiment);
      renderRunList(appState.allRuns);
      resetDetailsPanel();

      showAlert("Experimento carregado com sucesso!", "success");
      elements.welcomeScreen.classList.add("d-none");
      elements.resultContainer.classList.remove("d-none");
    })
    .catch((error) => {
      console.error("Erro ao buscar experimento:", error);
      showAlert(`Falha ao buscar o experimento: ${error.message}`, "danger");
      elements.resultContainer.classList.add("d-none");
      elements.welcomeScreen.classList.remove("d-none");
    })
    .finally(() => {
      setLoadingState(false);
    });
}

// --- RENDERING LOGIC ---

function renderRunList(runs) {
  elements.runList.innerHTML = "";
  if (!runs || runs.length === 0) {
    elements.runList.innerHTML = `<li class="list-group-item">Nenhum run encontrado.</li>`;
    elements.runCountBadge.textContent = "0";
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
  elements.runCountBadge.textContent = runs.length;
}

function handleRunClick(e) {
  const target = e.target.closest(".list-group-item-action");
  if (!target) return;

  e.preventDefault();
  const runId = target.dataset.runId;
  if (runId === appState.selectedRunId) return;

  appState.selectedRunId = runId;

  const currentlyActive = elements.runList.querySelector(".active");
  if (currentlyActive) currentlyActive.classList.remove("active");
  target.classList.add("active");

  renderDetailsPanel();
}

/**
 * MODIFIED: No longer calls the renderErrors function.
 */
function renderDetailsPanel() {
  if (!appState.selectedRunId) {
    resetDetailsPanel();
    return;
  }

  const selectedRun = appState.allRuns.find(
    (run) =>
      (run.example_id_clean || `run-${appState.allRuns.indexOf(run)}`) ===
      appState.selectedRunId
  );
  if (!selectedRun) {
    showAlert("Erro: Run selecionado não encontrado.", "danger");
    return;
  }

  elements.userMessageContainer.textContent =
    selectedRun.input.mensagem_whatsapp_simulada;
  renderComparison(selectedRun); // Diff button removed, this always renders side-by-side
  renderEvaluations(selectedRun.annotations);
  renderReasoningTimeline(selectedRun.output.agent_output?.ordered);
  // renderErrors(selectedRun); // Removed as requested

  elements.detailsPlaceholder.classList.add("d-none");
  elements.detailsContent.classList.remove("d-none");

  // Scroll to top of details panel when new run is selected
  if (elements.mainContentWrapper) {
    elements.mainContentWrapper.scrollTop = 0;
  }
}

function resetDetailsPanel() {
  elements.detailsPlaceholder.classList.remove("d-none");
  elements.detailsContent.classList.add("d-none");
  appState.selectedRunId = null;
  const currentlyActive = elements.runList.querySelector(".active");
  if (currentlyActive) currentlyActive.classList.remove("active");
}

// MODIFIED: Simplified as diff button is removed
function renderComparison(runData) {
  const agentAnswerHtml = runData.output.agent_output?.ordered.find(
    (m) => m.type === "assistant_message"
  )
    ? marked.parse(
        runData.output.agent_output.ordered.find(
          (m) => m.type === "assistant_message"
        ).message.content
      )
    : "<p>N/A</p>";
  const goldenAnswerHtml = runData.reference_output.golden_answer
    ? marked.parse(runData.reference_output.golden_answer)
    : "<p>N/A</p>";

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

/**
 * MODIFIED: Score position moved to the left.
 * MODIFIED: "Golden Link in Tool Calling" explanation is now expandable and starts collapsed, using consistent styling.
 * MODIFIED: "Golden Link in Answer" also gets the collapse button if its explanation is JSON.
 */
function renderEvaluations(annotations) {
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

  const desiredOrder = [
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];
  const sortedAnnotations = [...annotations].sort((a, b) => {
    const indexA = desiredOrder.indexOf(a.name);
    const indexB = desiredOrder.indexOf(b.name);
    return (
      (indexA === -1 ? Infinity : indexA) -
      (indexB === -1 ? Infinity : indexB)
    );
  });

  elements.evaluationsContainer.innerHTML = sortedAnnotations
    .map((ann) => {
      let explanationContentHtml = "";
      let isJsonExplanation = false;

      if (ann.explanation) {
        if (typeof ann.explanation === "object") {
          explanationContentHtml = `<pre><code>${JSON.stringify(
            ann.explanation,
            null,
            2
          )}</code></pre>`;
          isJsonExplanation = true;
        } else if (typeof ann.explanation === "string") {
          if (ann.name === "Answer Similarity") {
            explanationContentHtml = marked.parse(ann.explanation);
          } else {
            // This covers plain text explanations for all other annotations,
            // including Golden Link in Answer/Tool Calling when they are plain text.
            explanationContentHtml = `<div class="p-2 bg-light border rounded">${ann.explanation}</div>`;
          }
        }
      }

      let finalExplanationSection = "";
      if (explanationContentHtml) {
        // Apply collapse button only for specific annotations and if the content is JSON
        if (
          (ann.name === "Golden Link in Tool Calling" ||
            ann.name === "Golden Link in Answer") &&
          isJsonExplanation
        ) {
          // Using a combination of annotation name and selectedRunId for a robust unique ID
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
          // For Answer Similarity (always displayed directly), and any Golden Link explanation that is NOT JSON,
          // and other annotations that don't need a collapse button.
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
 */
function renderReasoningTimeline(orderedSteps) {
  const parentHeader =
    elements.reasoningTimelineContainer.previousElementSibling;

  // Clear previous summary
  const existingSummary = parentHeader.querySelector("#reasoning-summary");
  if (existingSummary) existingSummary.remove();

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

  if (Object.keys(toolCallCounts).length > 0) {
    const badges = Object.entries(toolCallCounts)
      .map(
        ([name, count]) =>
          `<span class="badge rounded-pill text-bg-secondary tool-call-badge">${name}: ${count} chamada(s)</span>`
      )
      .join(" ");
    const summaryHtml = `<div id="reasoning-summary">${badges}</div>`;
    parentHeader.insertAdjacentHTML("beforeend", summaryHtml);
  }

  // Group steps by their step_id to apply sequential numbering to logical flows
  let groupedSequences = [];
  let currentSequenceGroup = [];
  let lastStepId = null;

  orderedSteps.forEach((step) => {
    // Handle usage statistics as a separate, non-numbered sequence
    if (step.type === "letta_usage_statistics") {
      if (currentSequenceGroup.length > 0) {
        groupedSequences.push(currentSequenceGroup);
      }
      groupedSequences.push([step]); // Add usage stats as its own group
      currentSequenceGroup = []; // Reset for next main sequence
      lastStepId = null; // Ensure next non-stats step starts a new sequence number
    } else {
      const currentStepId = step.step_id;

      // If step_id changes, or it's the very first main step, start a new group
      if (currentStepId !== lastStepId && currentSequenceGroup.length > 0) {
        groupedSequences.push(currentSequenceGroup);
        currentSequenceGroup = [];
      }
      currentSequenceGroup.push(step);
      lastStepId = currentStepId;
    }
  });

  // Push the last remaining sequence if any
  if (currentSequenceGroup.length > 0) {
    groupedSequences.push(currentSequenceGroup);
  }

  let sequenceCounter = 0; // For numbering logical sequences (e.g., 1., 2., 3.)

  const timelineItemsHtml = groupedSequences
    .map((group) => {
      // Determine if this group contributes to the main sequence numbering
      const isMainSequenceGroup = group.some((s) =>
        [
          "reasoning_message",
          "tool_call_message",
          "tool_return_message",
          "assistant_message",
        ].includes(s.type)
      );

      let groupHtml = "";
      if (isMainSequenceGroup) {
        sequenceCounter++;
      }

      group.forEach((step, indexInGroup) => {
        let iconClass = "";
        let icon = "";
        let title = "";
        let content = "";

        // Add the global step number if it's a main sequence group
        const stepPrefix = isMainSequenceGroup ? `${sequenceCounter}. ` : "";

        switch (step.type) {
          case "reasoning_message":
            iconClass = "timeline-icon-reasoning";
            icon = "bi-lightbulb";
            title = `${stepPrefix}Raciocínio`;
            content = `<p class="mb-0 fst-italic">"${step.message.reasoning}"</p>`;
            break;
          case "tool_call_message":
            iconClass = "timeline-icon-toolcall";
            icon = "bi-tools";
            title = `${stepPrefix}Chamada de Ferramenta: ${step.message.tool_call.name}`;
            content = `<pre><code>${JSON.stringify(
              step.message.tool_call.arguments,
              null,
              2
            )}</code></pre>`;
            break;
          case "tool_return_message":
            iconClass = "timeline-icon-return";
            icon = "bi-box-arrow-in-left";
            title = `${stepPrefix}Retorno da Ferramenta: ${step.message.name}`;
            const toolReturn = step.message.tool_return;

            let returnSections = [];
            if (typeof toolReturn === "object" && toolReturn !== null) {
              if (toolReturn.text) {
                returnSections.push(`
                              <div class="tool-return-section">
                                  <h6>Texto:</h6>
                                  <div class="p-2 bg-light border rounded mt-1">${marked.parse(
                                    String(toolReturn.text)
                                  )}</div>
                              </div>`);
              }
              if (toolReturn.sources && toolReturn.sources.length > 0) {
                // MODIFIED: Add collapse for Sources with consistent styling and new line positioning
                // Robust ID generation using selectedRunId and indexInGroup
                const collapseId = `collapse-sources-${appState.selectedRunId}-${indexInGroup}`;
                returnSections.push(`
                              <div class="tool-return-section">
                                  <h6>Fontes (Sources):</h6>
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
                                  <h6>Consultas de Busca Web (Web Search Queries):</h6>
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
            iconClass = "timeline-icon-assistant"; // Specific icon class for assistant message
            icon = "bi-chat-text"; // A chat icon for assistant message
            title = `${stepPrefix}Mensagem do Assistente`;
            content = marked.parse(step.message.content);
            break;
          case "letta_usage_statistics":
            iconClass = "timeline-icon-stats"; // Specific icon class for stats
            icon = "bi-bar-chart-fill";
            title = "Estatísticas de Uso"; // Simplified title (no step prefix for stats)
            content = `
                      <p class="mb-0"><strong>Tokens Totais:</strong> ${step.message.total_tokens}</p>
                      <p class="mb-0"><strong>Tokens de Prompt:</strong> ${step.message.prompt_tokens}</p>
                      <p class="mb-0"><strong>Tokens de Conclusão:</strong> ${step.message.completion_tokens}</p>
                  `;
            break;
          default:
            return ""; // Ignore other step types
        }

        groupHtml += `
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
      });
      return groupHtml;
    })
    .join("");

  elements.reasoningTimelineContainer.innerHTML = `<div class="timeline">${timelineItemsHtml}</div>`;
}

// handleToggleDiff removed as the button is removed

// --- FILTERING LOGIC ---

function renderFilters(experimentData) {
  const filterOptions = {};
  experimentData.forEach((exp) => {
    exp.annotations?.forEach((ann) => {
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
          <div id="dynamicFilters" class="d-flex flex-wrap gap-2">${filtersHtml}</div>
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

  renderRunList(filteredRuns);
  resetDetailsPanel();
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
    elements.loadingIndicator.classList.remove("d-none");
    elements.fetchExperimentBtn.disabled = true;
    elements.fetchExperimentBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...`;
  } else {
    elements.loadingIndicator.classList.add("d-none");
    elements.fetchExperimentBtn.disabled = false;
    elements.fetchExperimentBtn.innerHTML = `<i class="bi bi-search me-1"></i> Buscar`;
  }
}

function showAlert(message, type = "danger") {
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
  if (appState.originalJsonData) {
    const dataStr = JSON.stringify(appState.originalJsonData, null, 2);
    const blob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "experiment_data.json"; // Suggested filename
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url); // Clean up the object URL
  } else {
    showAlert("Nenhum dado de experimento para baixar.", "warning");
  }
}

/**
 * MODIFIED: Corrected HTML escaping for prompt content inside pre/code tags.
 * Added download JSON button.
 */
function renderMetadata(metadata) {
  if (!metadata) return;
  const createPromptSectionHTML = (title, id, collapseId) => {
    return `
            <div class="metadata-item-full-width">
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${title}</strong>
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                        <i class="bi bi-arrows-expand"></i> Ver/Ocultar
                    </button>
                </div>
                <div class="collapse mt-2" id="${collapseId}">
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
          <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
              <h4 class="mb-0">Parâmetros do Experimento</h4>
              <div>
                  <button class="btn btn-sm btn-outline-secondary" data-bs-toggle="modal" data-bs-target="#jsonModal"><i class="bi bi-code-slash me-1"></i> Ver JSON</button>
                  <button class="btn btn-sm btn-info ms-2" id="downloadJsonBtn"><i class="bi bi-download me-1"></i> Baixar JSON</button>
              </div>
          </div>
          <hr class="my-3">
          <div class="metadata-grid">
              <div class="metadata-item"><strong>Modelo de Avaliação:</strong> ${
                metadata.eval_model || "N/A"
              }</div>
              <div class="metadata-item"><strong>Modelo de Resposta:</strong> ${
                metadata.final_repose_model || "N/A"
              }</div>
              <div class="metadata-item"><strong>Temperatura:</strong> ${
                metadata.temperature ?? "N/A"
              }</div>
              <div class="metadata-item"><strong>Ferramentas:</strong> ${
                metadata.tools?.join(", ") || "N/A"
              }</div>
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
  // Attach event listener for the new download button
  getElement("downloadJsonBtn").addEventListener(
    "click",
    downloadOriginalJson
  );

  getElement("jsonModal").addEventListener("show.bs.modal", () => {
    const jsonModalContent = document.querySelector("#jsonModal pre code");
    if (jsonModalContent && appState.originalJsonData) {
      jsonModalContent.textContent = JSON.stringify(
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
 */
function calculateAndRenderSummaryMetrics(experimentData) {
  const metrics = {};
  const totalRuns = experimentData.length;
  if (totalRuns === 0) {
    elements.summaryMetricsContainer.innerHTML = "";
    return;
  }

  // 1. Aggregate data: scores for average, and counts for distribution
  experimentData.forEach((exp) => {
    exp.annotations?.forEach((ann) => {
      if (!metrics[ann.name]) {
        metrics[ann.name] = { scores: [], counts: {} };
      }
      metrics[ann.name].scores.push(ann.score);
      const scoreStr = ann.score.toFixed(1); // Group scores by one decimal place
      metrics[ann.name].counts[scoreStr] =
        (metrics[ann.name].counts[scoreStr] || 0) + 1;
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
      (desiredOrder.indexOf(a) ?? Infinity) -
      (desiredOrder.indexOf(b) ?? Infinity)
  );

  // 2. Render HTML for each metric
  let metricsHtml = sortedMetricNames
    .map((name) => {
      const metric = metrics[name];
      const average =
        metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;

      // Sort score distribution from highest to lowest score
      const sortedDistribution = Object.entries(metric.counts).sort(
        ([scoreA], [scoreB]) => parseFloat(scoreB) - parseFloat(scoreA)
      );

      const distributionHtml = sortedDistribution
        .map(([score, count]) => {
          const percentage = (count / totalRuns) * 100;
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
                  ? `<div class="metric-distribution-header">Distribuição</div>${distributionHtml}`
                  : ""
              }
          </div>`;
    })
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
