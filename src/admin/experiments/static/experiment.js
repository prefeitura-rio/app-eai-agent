// --- ELEMENTOS DOM ---
const experimentIdInput = document.getElementById("experimentIdInput");
const fetchExperimentBtn = document.getElementById("fetchExperimentBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const alertArea = document.getElementById("alertArea");
const logoutBtn = document.getElementById("logoutBtn");
const resultContainer = document.getElementById("resultContainer");
const metadataContainer = document.getElementById("metadataContainer");
const summaryMetricsContainer = document.getElementById(
  "summaryMetricsContainer"
);
const filterContainer = document.getElementById("filterContainer");
const experimentAccordion = document.getElementById("experimentAccordion");
const experimentsPanel = document.getElementById("experimentsPanel");

// --- VARIÁVEIS GLOBAIS ---
let currentToken = localStorage.getItem("adminToken");
let originalJsonData = null;

// --- INICIALIZAÇÃO ---
document.addEventListener("DOMContentLoaded", function () {
  if (currentToken) {
    showExperimentsPanel();
  }
  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogout);
  }
  document.addEventListener(
    "experimentsReady",
    initializeExperimentsFunctionality
  );
});

// --- FUNÇÕES DE UI E LÓGICA ---

function showExperimentsPanel() {
  if (experimentsPanel) {
    document.querySelector(".login-container").classList.add("d-none");
    experimentsPanel.classList.remove("d-none");
    initializeExperimentsFunctionality();
  }
}

function initializeExperimentsFunctionality() {
  if (fetchExperimentBtn && !fetchExperimentBtn.dataset.listenerAttached) {
    fetchExperimentBtn.addEventListener("click", fetchExperimentData);
    fetchExperimentBtn.dataset.listenerAttached = "true";
  }
  if (experimentIdInput && !experimentIdInput.dataset.listenerAttached) {
    experimentIdInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") fetchExperimentData();
    });
    experimentIdInput.dataset.listenerAttached = "true";
  }
}

function handleLogout() {
  localStorage.removeItem("adminToken");
  location.reload();
}

function showAlert(message, type = "danger") {
  if (alertArea) {
    const alertId = `alert-${Date.now()}`;
    alertArea.innerHTML = `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    if (type === "success") {
      setTimeout(() => {
        const alertElement = document.getElementById(alertId);
        if (alertElement) {
          new bootstrap.Alert(alertElement).close();
        }
      }, 4000);
    }
  }
}

function getScoreClass(score) {
  if (score === 1.0) return "score-high";
  if (score === 0.0) return "score-low";
  return "score-mid";
}

// --- FUNÇÕES DE RENDERIZAÇÃO ---

function renderMetadata(metadata) {
  if (!metadata) return;
  const createPromptSection = (title, content, id) => {
    if (!content) return "";
    const escapedContent = content
      .replace(/&/g, "&")
      .replace(/</g, "<")
      .replace(/>/g, ">");
    return `
            <div class="metadata-item-full-width">
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${title}</strong>
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#${id}" aria-expanded="false" aria-controls="${id}">
                        <i class="bi bi-arrows-expand"></i> Ver/Ocultar
                    </button>
                </div>
                <div class="collapse mt-2" id="${id}">
                    <pre><code>${escapedContent}</code></pre>
                </div>
            </div>
        `;
  };
  const promptsHTML = `
        ${createPromptSection(
          "System Prompt Principal",
          metadata.system_prompt,
          "systemPromptCollapse"
        )}
        ${createPromptSection(
          "System Prompt (Similaridade)",
          metadata.system_prompt_answer_similatiry,
          "systemPromptSimilarityCollapse"
        )}
    `;
  metadataContainer.innerHTML = `
        <div class="card metadata-card">
            <div class="d-flex justify-content-between align-items-center flex-wrap gap-2">
                <h4 class="section-title mb-0 flex-grow-1" style="border-bottom: none; padding-bottom: 0;">Parâmetros do Experimento</h4>
                <div id="jsonActionsContainer">
                    <button class="btn btn-sm btn-outline-secondary" id="viewJsonBtn" data-bs-toggle="modal" data-bs-target="#jsonModal">
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
                ${promptsHTML}
            </div>
        </div>
    `;
  document.getElementById("viewJsonBtn").addEventListener("click", () => {
    const jsonModalContent = document.querySelector("#jsonModal pre code");
    if (jsonModalContent && originalJsonData) {
      jsonModalContent.textContent = JSON.stringify(
        originalJsonData,
        null,
        2
      );
    }
  });
  document.getElementById("downloadJsonBtn").addEventListener("click", () => {
    if (!originalJsonData) return;
    const expId = experimentIdInput.value.trim() || "experiment";
    const dataStr =
      "data:text/json;charset=utf-8," +
      encodeURIComponent(JSON.stringify(originalJsonData, null, 2));
    const downloadAnchorNode = document.createElement("a");
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `experiment-${expId}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  });
}

function renderEvaluations(annotations) {
  if (!annotations || annotations.length === 0) {
    return "<p>Nenhuma avaliação disponível.</p>";
  }
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
  return sortedAnnotations
    .map((ann) => {
      let explanationContent = "";
      if (ann.explanation) {
        if (ann.name === "Answer Similarity" && typeof ann.explanation === 'string') {
            explanationContent = marked.parse(ann.explanation);
        } else if (typeof ann.explanation === "object" && ann.explanation !== null) {
          explanationContent = `<pre><code>${JSON.stringify(
            ann.explanation,
            null,
            2
          )}</code></pre>`;
        } else {
          explanationContent = ann.explanation;
        }
      }
      return `
        <div class="evaluation-card">
            <div class="main-info">
                <p class="name">${ann.name}</p>
                <div class="score ${getScoreClass(ann.score)}">${ann.score.toFixed(1)}</div>
            </div>
            ${
              explanationContent
                ? `<div class="explanation">${explanationContent}</div>`
                : ""
            }
        </div>
        `;
    })
    .join("");
}

function renderReasoning(orderedSteps) {
  if (!orderedSteps || orderedSteps.length === 0) return "";
  return orderedSteps
    .map((step) => {
      let stepHtml = "";
      if (step.type === "reasoning_message") {
        stepHtml = `<strong>🧠 Raciocínio:</strong><p>"${step.message.reasoning}"</p>`;
      } else if (step.type === "tool_call_message") {
        stepHtml = `<strong>🔧 Chamada de Ferramenta: ${
          step.message.tool_call.name
        }</strong><pre><code>${JSON.stringify(
          step.message.tool_call.arguments,
          null,
          2
        )}</code></pre>`;
      } else if (
        step.type === "tool_return_message" &&
        step.message.tool_return
      ) {
        const toolReturnData = step.message.tool_return;
        let returnContentHtml = "";
        if (typeof toolReturnData === "object" && toolReturnData !== null) {
          const remainingData = { ...toolReturnData };
          const createSubSection = (title, data, isMarkdown = false) => {
            if (!data || (Array.isArray(data) && data.length === 0))
              return "";
            const content = isMarkdown
              ? `<div class="markdown-content">${marked.parse(data)}</div>`
              : `<pre><code>${JSON.stringify(data, null, 2)}</code></pre>`;
            return `<div class="mt-2"><strong>${title}</strong>${content}</div>`;
          };
          returnContentHtml += createSubSection(
            "Texto:",
            remainingData.text,
            true
          );
          delete remainingData.text;
          returnContentHtml += createSubSection(
            "Sources:",
            remainingData.sources
          );
          delete remainingData.sources;
          returnContentHtml += createSubSection(
            "Web Search Queries:",
            remainingData.web_search_queries
          );
          delete remainingData.web_search_queries;
          if (Object.keys(remainingData).length > 0) {
            returnContentHtml += createSubSection(
              "Dados Adicionais:",
              remainingData
            );
          }
        } else {
          returnContentHtml = `<pre><code>${
            typeof toolReturnData === "string"
              ? toolReturnData
              : JSON.stringify(toolReturnData, null, 2)
          }</code></pre>`;
        }
        stepHtml = `<strong>↪️ Retorno da Ferramenta:</strong>${returnContentHtml}`;
      }
      return stepHtml ? `<div class="reasoning-step">${stepHtml}</div>` : "";
    })
    .join("");
}

function renderCollapsibleReasoning(orderedSteps, accordionId) {
  if (!orderedSteps || orderedSteps.length === 0) {
    return `<h4 class="section-title">Passo a Passo do Agente (Reasoning)</h4><p>Nenhum passo a passo disponível.</p>`;
  }
  const reasoningCollapseId = `reasoning-collapse-${accordionId}`;
  return `
        <div class="d-flex justify-content-between align-items-center mt-4">
            <h4 class="section-title mb-0" style="border-bottom: none;">Passo a Passo do Agente (Reasoning)</h4>
            <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#${reasoningCollapseId}" aria-expanded="false" aria-controls="${reasoningCollapseId}">
                <i class="bi bi-arrows-expand"></i> Expandir
            </button>
        </div>
        <div class="collapse pt-3" id="${reasoningCollapseId}">
            ${renderReasoning(orderedSteps)}
        </div>
    `;
}

function calculateAndRenderSummaryMetrics(experimentData) {
  const metrics = {};
  experimentData.forEach((exp) => {
    if (!exp.annotations) return;
    exp.annotations.forEach((ann) => {
      if (!metrics[ann.name]) {
        metrics[ann.name] = { scores: [], counts: {} };
      }
      metrics[ann.name].scores.push(ann.score);
      metrics[ann.name].counts[ann.score] =
        (metrics[ann.name].counts[ann.score] || 0) + 1;
    });
  });

  let metricsHtml = "";
  const desiredOrder = [
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];
  const sortedMetricNames = Object.keys(metrics).sort((a, b) => {
    const indexA = desiredOrder.indexOf(a);
    const indexB = desiredOrder.indexOf(b);
    return (
      (indexA === -1 ? Infinity : indexA) -
      (indexB === -1 ? Infinity : indexB)
    );
  });

  for (const name of sortedMetricNames) {
    const metric = metrics[name];
    const average =
      metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;
    const distributionHtml = Object.entries(metric.counts)
      .sort(([scoreA], [scoreB]) => scoreB - scoreA)
      .map(([score, count]) => {
        const scoreF = parseFloat(score);
        const formattedScore =
          scoreF === 0.0 || scoreF === 1.0
            ? scoreF.toFixed(0)
            : scoreF.toFixed(1);
        return `<span>${formattedScore}: ${count}</span>`;
      })
      .join("");

    metricsHtml += `
            <div class="summary-metric-item">
                <h6>${name}</h6>
                <div class="average-score">${average.toFixed(2)}</div>
                <div class="score-distribution">${distributionHtml}</div>
            </div>
        `;
  }

  summaryMetricsContainer.innerHTML = `
        <div class="card metadata-card">
            <h4 class="section-title" style="border-bottom: none; margin: 0 0 1rem 0;">Métricas Gerais: ${experimentData.length} runs</h4>
            <div class="summary-grid">${metricsHtml}</div>
        </div>
    `;
}

function renderFilters(experimentData) {
  filterContainer.innerHTML = "";
  const filterOptions = {};
  experimentData.forEach((exp) => {
    if (exp.annotations) {
      exp.annotations.forEach((ann) => {
        if (!filterOptions[ann.name]) {
          filterOptions[ann.name] = new Set();
        }
        filterOptions[ann.name].add(ann.score);
      });
    }
  });

  const desiredOrder = [
    "Answer Similarity",
    "Activate Search Tools",
    "Golden Link in Answer",
    "Golden Link in Tool Calling",
  ];
  const sortedFilterNames = Object.keys(filterOptions).sort((a, b) => {
    const indexA = desiredOrder.indexOf(a);
    const indexB = desiredOrder.indexOf(b);
    return (
      (indexA === -1 ? Infinity : indexA) -
      (indexB === -1 ? Infinity : indexB)
    );
  });

  let filtersHtml = "";
  sortedFilterNames.forEach((name) => {
    const scores = Array.from(filterOptions[name]).sort((a, b) => a - b);
    const filterId = `filter-${name.replace(/\s+/g, "-")}`;

    let optionsHtml = '<option value="">Qualquer Nota</option>';
    scores.forEach((score) => {
      optionsHtml += `<option value="${score}">${score.toFixed(1)}</option>`;
    });

    filtersHtml += `
            <div class="flex-grow-1">
                <label for="${filterId}" class="form-label small fw-bold">${name}</label>
                <select id="${filterId}" class="form-select" data-metric-name="${name}">
                    ${optionsHtml}
                </select>
            </div>
        `;
  });

  if (filtersHtml) {
    filterContainer.innerHTML = `
            <div class="card metadata-card mt-4">
                 <h4 class="section-title" style="border-bottom: none; margin: 0 0 1rem 0;">Filtros de Avaliação</h4>
                 <div id="dynamicFilters" class="d-flex flex-wrap gap-3">${filtersHtml}</div>
                 <div class="d-flex gap-2 mt-3">
                     <button id="applyFiltersBtn" class="btn btn-success"><i class="bi bi-funnel-fill me-1"></i> Aplicar Filtros</button>
                     <button id="clearFiltersBtn" class="btn btn-outline-secondary">Limpar Filtros</button>
                 </div>
            </div>`;
    document
      .getElementById("applyFiltersBtn")
      .addEventListener("click", applyFilters);
    document
      .getElementById("clearFiltersBtn")
      .addEventListener("click", clearFilters);
  }
}

function applyFilters() {
  const activeFilters = {};
  document.querySelectorAll("#dynamicFilters select").forEach((select) => {
    if (select.value) {
      activeFilters[select.dataset.metricName] = parseFloat(select.value);
    }
  });

  document
    .querySelectorAll("#experimentAccordion .accordion-item")
    .forEach((item) => {
      const annotations = JSON.parse(item.dataset.annotations || "[]");
      let shouldShow = true;

      for (const metricName in activeFilters) {
        const targetScore = activeFilters[metricName];
        const annotation = annotations.find((ann) => ann.name === metricName);

        if (!annotation || annotation.score !== targetScore) {
          shouldShow = false;
          break;
        }
      }
      item.classList.toggle("d-none", !shouldShow);
    });
}

function clearFilters() {
  document.querySelectorAll("#dynamicFilters select").forEach((select) => {
    select.value = "";
  });
  document
    .querySelectorAll("#experimentAccordion .accordion-item")
    .forEach((item) => {
      item.classList.remove("d-none");
    });
}

function renderExperimentReport(data) {
  metadataContainer.innerHTML = "";
  summaryMetricsContainer.innerHTML = "";
  filterContainer.innerHTML = "";
  experimentAccordion.innerHTML = "";

  renderMetadata(data.experiment_metadata);
  calculateAndRenderSummaryMetrics(data.experiment);
  renderFilters(data.experiment);

  data.experiment.forEach((exp, index) => {
    const sanitizedId = exp.example_id.replace(/[^a-zA-Z0-9_-]/g, "");
    const accordionId = `exp-${sanitizedId}`;
    const output = exp.output;

    const agentAnswerHtml = exp.output.agent_output?.ordered.find(
      (m) => m.type === "assistant_message"
    )
      ? marked.parse(
          exp.output.agent_output.ordered.find(
            (m) => m.type === "assistant_message"
          ).message.content
        )
      : "<p>N/A</p>";
    const goldenAnswerHtml = exp.reference_output.golden_answer
      ? marked.parse(exp.reference_output.golden_answer)
      : "<p>N/A</p>";

    const accordionItem = document.createElement("div");
    accordionItem.className = "accordion-item mt-4";
    accordionItem.dataset.annotations = JSON.stringify(exp.annotations || []);
    accordionItem.innerHTML = `
        <h2 class="accordion-header" id="heading-${accordionId}">
            <button class="accordion-button ${
              index > 0 ? "collapsed" : ""
            }" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-${accordionId}" aria-expanded="${
      index === 0
    }" aria-controls="collapse-${accordionId}">
                <strong>ID do Teste:</strong> ${output.metadata.id}
            </button>
        </h2>
        <div id="collapse-${accordionId}" class="accordion-collapse collapse ${
      index === 0 ? "show" : ""
    }" aria-labelledby="heading-${accordionId}" data-bs-parent="#experimentAccordion">
            <div class="accordion-body">
                <h4 class="section-title">Mensagem do Usuário</h4>
                <div class="alert alert-secondary">${
                  exp.input.mensagem_whatsapp_simulada
                }</div>
                <h4 class="section-title">Comparação de Respostas</h4>
                <div class="row g-4">
                    <div class="col-md-6"><div class="comparison-box"><h5 class="agent-answer">🤖 Resposta do Agente</h5><div>${agentAnswerHtml}</div></div></div>
                    <div class="col-md-6"><div class="comparison-box"><h5 class="golden-answer">🏆 Resposta de Referência (Golden)</h5><div>${goldenAnswerHtml}</div></div></div>
                </div>
                <h4 class="section-title">Avaliações</h4>
                ${renderEvaluations(exp.annotations)}
                ${renderCollapsibleReasoning(
                  exp.output.agent_output?.ordered,
                  accordionId
                )}
            </div>
        </div>
    `;
    experimentAccordion.appendChild(accordionItem);
  });

  resultContainer.classList.remove("d-none");
}

function fetchExperimentData() {
  const expId = experimentIdInput.value.trim();
  if (!expId) {
    showAlert("Por favor, insira um ID de experimento.", "warning");
    return;
  }

  loadingIndicator.classList.remove("d-none");
  resultContainer.classList.add("d-none");
  alertArea.innerHTML = "";
  fetchExperimentBtn.disabled = true;
  fetchExperimentBtn.innerHTML =
    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';

  const url = `data?id=${encodeURIComponent(expId)}`;

  fetch(url, {
    headers: {
      Authorization: `Bearer ${currentToken}`,
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
      originalJsonData = data;
      renderExperimentReport(data);
      showAlert("Experimento carregado com sucesso!", "success");
    })
    .catch((error) => {
      console.error("Erro ao buscar experimento:", error);
      showAlert(`Falha ao buscar o experimento: ${error.message}`, "danger");
      resultContainer.classList.add("d-none");
    })
    .finally(() => {
      loadingIndicator.classList.add("d-none");
      fetchExperimentBtn.disabled = false;
      fetchExperimentBtn.innerHTML =
        '<i class="bi bi-search me-1"></i> Buscar';
    });
}