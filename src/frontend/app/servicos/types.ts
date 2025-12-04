export interface ServiceButton {
  titulo: string;
  descricao: string;
  url_service: string;
  ordem: number;
  is_enabled: boolean;
}

export interface ServiceAgents {
  exclusive_for_agents: boolean;
  tool_hint: string;
}

export interface Service {
  id?: string;
  nome_servico: string;
  tema_geral: string;
  orgao_gestor: string[];
  publico_especifico: string[];
  resumo: string;
  descricao_completa?: string;
  custo_servico?: string;
  tempo_atendimento?: string;
  resultado_solicitacao?: string;
  instrucoes_solicitante?: string;
  servico_nao_cobre?: string;
  documentos_necessarios?: string[];
  legislacao_relacionada?: string[];
  canais_digitais?: string[];
  canais_presenciais?: string[];
  is_free?: boolean;
  fixar_destaque?: boolean;
  awaiting_approval?: boolean;
  status: 0 | 1; // 0=Draft, 1=Published
  buttons?: ServiceButton[];
  agents?: ServiceAgents;
  extra_fields?: Record<string, unknown>;
  // Campos automáticos (readonly no form)
  autor?: string;
  created_at?: number;
  last_update?: number;
  published_at?: number;
  embedding?: number[];
  search_content?: string;
}

export interface ServiceListResponse {
  found: number;
  out_of: number;
  page: number;
  services: Service[];
}

export interface ServiceFilters {
  page?: number;
  per_page?: number;
  status?: 0 | 1 | '';
  author?: string;
  tema_geral?: string;
  awaiting_approval?: boolean;
  is_free?: boolean;
  published_at?: number;
  nome_servico?: string;
  field?: string;
  value?: string;
}

export interface FilterOptions {
  tema_geral: string[];
  autor: string[];
}

export interface TombamentoParams {
  origem?: string;
  id_servico_antigo?: string;
}
