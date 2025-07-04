// Script de verificação de autenticação
// Este script deve ser incluído ANTES de qualquer outro script da aplicação

(function () {
  "use strict";

  // Verificar se já estamos na página de autenticação
  if (window.location.pathname.includes("/auth")) {
    return; // Não fazer verificação se já estamos na página de auth
  }

  console.log("Verificando autenticação...");

  // Verificar se existe token
  const token = localStorage.getItem("adminToken");

  if (!token) {
    console.log("Token não encontrado, redirecionando para autenticação...");
    redirectToAuth();
    return;
  }

  // Validar token assincronamente
  validateTokenAsync(token);

  function redirectToAuth() {
    const currentUrl = window.location.href;
    const authUrl = "/eai-agent/admin/experiments/auth";
    window.location.href = `${authUrl}?return=${encodeURIComponent(
      currentUrl
    )}`;
  }

  async function validateTokenAsync(token) {
    try {
      const API_BASE_URL_AUTH =
        "https://services.staging.app.dados.rio/eai-agent";
      const validationUrl = `${API_BASE_URL_AUTH}/api/v1/system-prompt`;

      const response = await fetch(validationUrl, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
        timeout: 5000,
      });

      if (!response.ok) {
        throw new Error(`Authentication failed (Status: ${response.status})`);
      }

      console.log("Token válido, continuando...");
      // Token válido, permitir que a página continue carregando
    } catch (error) {
      console.log("Token inválido, removendo e redirecionando...", error);
      localStorage.removeItem("adminToken");
      redirectToAuth();
    }
  }

  // Disponibilizar funções globalmente para outras páginas
  window.AuthCheck = {
    redirectToAuth: redirectToAuth,

    getToken: function () {
      return localStorage.getItem("adminToken");
    },

    logout: function () {
      localStorage.removeItem("adminToken");
      redirectToAuth();
    },

    isAuthenticated: function () {
      return !!localStorage.getItem("adminToken");
    },
  };
})();
