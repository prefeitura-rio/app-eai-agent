// --- ELEMENTOS DOM ---
const experimentIdInput = document.getElementById("experimentIdInput");
const fetchExperimentBtn = document.getElementById("fetchExperimentBtn");
const loadingIndicator = document.getElementById("loadingIndicator");
const alertArea = document.getElementById("alertArea");
const logoutBtn = document.getElementById("logoutBtn");
const resultContainer = document.getElementById("resultContainer");
const metadataContainer = document.getElementById("metadataContainer");
const experimentAccordion = document.getElementById("experimentAccordion");
const experimentsPanel = document.getElementById("experimentsPanel");

// --- VARIÁVEIS GLOBAIS ---
let currentToken = localStorage.getItem("adminToken");
let originalJsonData = null; // Para armazenar o JSON original

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

  // Helper para gerar uma seção de prompt colapsável
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
  if (!annotations || annotations.length === 0)
    return "<p>Nenhuma avaliação disponível.</p>";

  return annotations
    .map(
      (ann) => `
        <div class="evaluation-card">
            <div class="details">
                <div class="name">${ann.name}</div>
                ${
                  ann.explanation
                    ? `<div class="explanation">${ann.explanation}</div>`
                    : ""
                }
            </div>
            <div class="score ${getScoreClass(
              ann.score
            )}">${ann.score.toFixed(1)}</div>
        </div>
    `
    )
    .join("");
}

function renderReasoning(orderedSteps) {
  if (!orderedSteps || orderedSteps.length === 0) return "";

  return orderedSteps
    .map((step) => {
      if (step.type === "reasoning_message") {
        return `
                <div class="reasoning-step">
                    <strong>🧠 Raciocínio:</strong>
                    <p>"${step.message.reasoning}"</p>
                </div>`;
      }
      if (step.type === "tool_call_message") {
        return `
                <div class="reasoning-step">
                    <strong>🔧 Chamada de Ferramenta: ${
                      step.message.tool_call.name
                    }</strong>
                    <pre><code>${JSON.stringify(
                      step.message.tool_call.arguments,
                      null,
                      2
                    )}</code></pre>
                </div>`;
      }
      if (step.type === "tool_return_message" && step.message.tool_return) {
        const toolReturn =
          typeof step.message.tool_return === "string"
            ? step.message.tool_return
            : JSON.stringify(step.message.tool_return, null, 2);

        return `
                <div class="reasoning-step">
                    <strong>↪️ Retorno da Ferramenta:</strong>
                    <pre><code>${toolReturn}</code></pre>
                </div>`;
      }
      return "";
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

function renderExperimentReport(data) {
  metadataContainer.innerHTML = "";
  experimentAccordion.innerHTML = "";
  renderMetadata(data.experiment_metadata);

  data.experiment.forEach((exp, index) => {
    const sanitizedId = exp.example_id.replace(/[^a-zA-Z0-9_-]/g, "");
    const accordionId = `exp-${sanitizedId}`;
    const output = exp.output;
    const agentOutput = output.agent_output;
    const reference = exp.reference_output;

    const agentAnswerContent = agentOutput?.ordered.find(
      (m) => m.type === "assistant_message"
    )?.message.content;
    const goldenAnswerContent = reference.golden_answer;

    // Usa marked.js para renderizar o markdown, se o conteúdo existir
    const agentAnswerHtml = agentAnswerContent
      ? marked.parse(agentAnswerContent)
      : "<p>N/A</p>";
    const goldenAnswerHtml = goldenAnswerContent
      ? marked.parse(goldenAnswerContent)
      : "<p>N/A</p>";

    const accordionItemHTML = `
            <div class="accordion-item">
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
                            <div class="col-md-6">
                                <div class="comparison-box">
                                    <h5 class="agent-answer">🤖 Resposta do Agente</h5>
                                    <div>${agentAnswerHtml}</div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="comparison-box">
                                    <h5 class="golden-answer">🏆 Resposta de Referência (Golden)</h5>
                                    <div>${goldenAnswerHtml}</div>
                                </div>
                            </div>
                        </div>

                        <h4 class="section-title">Avaliações</h4>
                        ${renderEvaluations(exp.annotations)}
                        
                        ${renderCollapsibleReasoning(
                          agentOutput?.ordered,
                          accordionId
                        )}

                    </div>
                </div>
            </div>
        `;
    experimentAccordion.innerHTML += accordionItemHTML;
  });

  resultContainer.classList.remove("d-none");
}

// --- FUNÇÃO DE FETCH ---
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
        const errorMessage =
          errorData?.detail ||
          `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMessage);
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
