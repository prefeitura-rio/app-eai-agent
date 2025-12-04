import { SEVICOS_API_BASE_URL } from '@/app/components/config';
import { Service, ServiceListResponse, ServiceFilters, TombamentoParams, FilterOptions } from '../types';
import { getAccessToken, clearAccessToken } from './govbr-auth';

const API_BASE = SEVICOS_API_BASE_URL;
const SERVICES_ENDPOINT = '/app-busca-search/api/v1/admin/services';

// Custom error para autenticacao
export class AuthenticationError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = getAccessToken();

  if (!token) {
    throw new AuthenticationError('Nao autenticado');
  }

  const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
    ...options.headers,
  };

  try {
    const response = await fetch(url, { ...options, headers });

    // 401 = Token inválido/expirado, 403 = Token sem permissão
    if (response.status === 401 || response.status === 403) {
      console.log('[API] Token expirado ou sem permissao. Limpando token...');
      clearAccessToken();
      throw new AuthenticationError('Sessao expirada ou sem permissao. Faca login novamente.');
    }

    return response;
  } catch (error) {
    // Se for erro de rede/CORS, também limpar token e pedir reautenticação
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      console.log('[API] Erro de rede (possivelmente CORS ou token invalido). Limpando token...');
      clearAccessToken();
      throw new AuthenticationError('Erro de conexao ou sessao expirada. Faca login novamente.');
    }
    // Se já for AuthenticationError, apenas repassa
    throw error;
  }
}

function buildQueryParams(filters: ServiceFilters): string {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== '' && value !== null) {
      params.append(key, String(value));
    }
  });

  return params.toString();
}

export async function listServices(filters: ServiceFilters = {}): Promise<ServiceListResponse> {
  const queryParams = buildQueryParams(filters);
  const url = `${API_BASE}${SERVICES_ENDPOINT}${queryParams ? `?${queryParams}` : ''}`;

  const response = await fetchWithAuth(url);

  if (!response.ok) {
    throw new Error(`Erro ao listar servicos: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getService(id: string): Promise<Service> {
  const url = `${API_BASE}${SERVICES_ENDPOINT}/${id}`;
  const response = await fetchWithAuth(url);

  if (!response.ok) {
    throw new Error(`Erro ao buscar servico: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function createService(data: Service): Promise<Service> {
  const url = `${API_BASE}${SERVICES_ENDPOINT}`;
  const response = await fetchWithAuth(url, {
    method: 'POST',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Erro ao criar servico: ${response.status}`);
  }

  return response.json();
}

export async function updateService(id: string, data: Service): Promise<Service> {
  const url = `${API_BASE}${SERVICES_ENDPOINT}/${id}`;
  const response = await fetchWithAuth(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || `Erro ao atualizar servico: ${response.status}`);
  }

  return response.json();
}

export async function deleteService(id: string): Promise<void> {
  const url = `${API_BASE}${SERVICES_ENDPOINT}/${id}`;
  const response = await fetchWithAuth(url, {
    method: 'DELETE',
  });

  if (!response.ok) {
    throw new Error(`Erro ao deletar servico: ${response.status} ${response.statusText}`);
  }
}

export async function publishService(id: string, tombamento?: TombamentoParams): Promise<Service> {
  const url = `${API_BASE}${SERVICES_ENDPOINT}/${id}/publish`;
  const response = await fetchWithAuth(url, {
    method: 'PATCH',
    body: JSON.stringify(tombamento || {}),
  });

  if (!response.ok) {
    throw new Error(`Erro ao publicar servico: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function unpublishService(id: string): Promise<Service> {
  const url = `${API_BASE}${SERVICES_ENDPOINT}/${id}/unpublish`;
  const response = await fetchWithAuth(url, {
    method: 'PATCH',
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error(`Erro ao despublicar servico: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

export async function getFilterOptions(): Promise<FilterOptions> {
  // Busca todos os servicos para extrair valores unicos
  const response = await listServices({ per_page: 1000 });

  const temaGeralSet = new Set<string>();
  const autorSet = new Set<string>();

  response.services.forEach(service => {
    if (service.tema_geral) temaGeralSet.add(service.tema_geral);
    if (service.autor) autorSet.add(service.autor);
  });

  return {
    tema_geral: Array.from(temaGeralSet).sort(),
    autor: Array.from(autorSet).sort(),
  };
}
