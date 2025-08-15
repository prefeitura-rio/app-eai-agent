/**
 * Centralized date formatting utilities
 * Use these functions to ensure consistent date formatting across the application
 */

/**
 * Formats a date string consistently using UTC timezone
 * @param dateString - ISO date string
 * @returns Formatted date in Brazilian locale with UTC timezone (dd/MM/yyyy, HH:mm:ss)
 */
export function formatDateTime(dateString: string): string {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return date.toLocaleString('pt-BR', { timeZone: 'UTC' });
}

/**
 * Formats a date string to Brazilian date format using UTC timezone
 * @param dateString - ISO date string or date-only string (YYYY-MM-DD)
 * @returns Formatted date in dd/MM/yyyy format
 */
export function formatDate(dateString: string): string {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
}

/**
 * Extracts date key (YYYY-MM-DD) from ISO date string for grouping
 * @param dateString - ISO date string
 * @returns Date key in YYYY-MM-DD format
 */
export function extractDateKey(dateString: string): string {
  if (!dateString) return '';
  return dateString.split('T')[0];
}

/**
 * Formats time only from ISO date string using UTC timezone
 * @param dateString - ISO date string
 * @returns Time in HH:mm:ss format
 */
export function formatTime(dateString: string): string {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return date.toLocaleTimeString('pt-BR', { timeZone: 'UTC' });
}