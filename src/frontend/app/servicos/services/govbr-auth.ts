import Cookies from 'js-cookie';

const ACCESS_TOKEN_KEY = 'servicos_access_token';
const TOKEN_EXPIRY_DAYS = 7;

/**
 * Recupera o access token dos cookies
 */
export function getAccessToken(): string | null {
  return Cookies.get(ACCESS_TOKEN_KEY) || null;
}

/**
 * Salva o access token nos cookies
 */
export function setAccessToken(accessToken: string): void {
  Cookies.set(ACCESS_TOKEN_KEY, accessToken, {
    expires: TOKEN_EXPIRY_DAYS,
    sameSite: 'lax',
  });
}

/**
 * Remove o access token dos cookies
 */
export function clearAccessToken(): void {
  Cookies.remove(ACCESS_TOKEN_KEY);
}

/**
 * Verifica se o usuario esta autenticado
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}
