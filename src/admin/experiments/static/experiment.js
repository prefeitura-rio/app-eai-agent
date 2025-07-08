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

    // Scroll to top of details panel when new run is selected
    if (elements.mainContentWrapper) {
      elements.mainContentWrapper.scrollTop = 0;
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
