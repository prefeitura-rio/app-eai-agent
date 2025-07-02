document.addEventListener("DOMContentLoaded", () => {
  const experimentIdInput = document.getElementById("experimentIdInput");
  const fetchExperimentBtn = document.getElementById("fetchExperimentBtn");
  const resultContainer = document.getElementById("resultContainer");
  const resultJson = document.getElementById("resultJson");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const alertArea = document.getElementById("alertArea");

  let PHOENIX_ENDPOINT = "";

  // Função para buscar a configuração do backend. A URL relativa '/experiments/config'
  // será resolvida pelo navegador para '/admin/experiments/config'.
  const fetchConfig = async () => {
    try {
      const response = await axios.get("config"); // URL relativa funciona aqui
      PHOENIX_ENDPOINT = response.data.phoenix_endpoint;
      if (!PHOENIX_ENDPOINT) {
        showAlert(
          "A URL do serviço Phoenix não foi configurada no backend.",
          "danger"
        );
        fetchExperimentBtn.disabled = true;
      }
    } catch (error) {
      console.error("Erro ao buscar configuração:", error);
      showAlert(
        "Não foi possível obter a configuração do servidor.",
        "danger"
      );
      fetchExperimentBtn.disabled = true;
    }
  };

  // Função para buscar os dados do experimento
  const fetchExperimentData = async () => {
    const expId = experimentIdInput.value.trim();
    if (!expId) {
      showAlert("Por favor, insira um ID de experimento.", "warning");
      return;
    }

    if (!PHOENIX_ENDPOINT) {
      showAlert(
        "Configuração do endpoint pendente. Tente novamente em alguns segundos.",
        "warning"
      );
      return;
    }

    loadingIndicator.classList.remove("d-none");
    resultContainer.classList.add("d-none");
    alertArea.innerHTML = "";
    fetchExperimentBtn.disabled = true;
    fetchExperimentBtn.innerHTML =
      '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Buscando...';

    try {
      const url = `${PHOENIX_ENDPOINT}v1/experiments/${expId}/json`;
      const response = await axios.get(url);

      resultJson.textContent = JSON.stringify(response.data, null, 2);
      resultContainer.classList.remove("d-none");
    } catch (error) {
      console.error("Erro ao buscar dados do experimento:", error);
      const errorMessage =
        error.response?.data?.detail || error.message || "Erro desconhecido.";
      showAlert(`Falha ao buscar o experimento: ${errorMessage}`, "danger");
    } finally {
      loadingIndicator.classList.add("d-none");
      fetchExperimentBtn.disabled = false;
      fetchExperimentBtn.innerHTML =
        '<i class="bi bi-search me-1"></i> Buscar';
    }
  };

  const showAlert = (message, type = "danger") => {
    alertArea.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
  };

  fetchExperimentBtn.addEventListener("click", fetchExperimentData);
  experimentIdInput.addEventListener("keypress", (event) => {
    if (event.key === "Enter") {
      fetchExperimentData();
    }
  });

  fetchConfig();
});
