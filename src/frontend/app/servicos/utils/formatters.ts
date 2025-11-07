/**
 * Formata timestamp Unix para data legivel
 */
export function formatDate(timestamp?: number): string {
  if (!timestamp) return '-';

  const date = new Date(timestamp * 1000);
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Formata array de strings para exibicao
 */
export function formatArray(arr?: string[]): string {
  if (!arr || arr.length === 0) return '-';
  return arr.join(', ');
}

/**
 * Trunca texto longo
 */
export function truncate(text: string, maxLength: number = 50): string {
  if (text.length <= maxLength) return text;
  return `${text.substring(0, maxLength)}...`;
}

/**
 * Formata status de publicacao
 */
export function formatStatus(status: 0 | 1): string {
  return status === 1 ? 'Publicado' : 'Rascunho';
}
