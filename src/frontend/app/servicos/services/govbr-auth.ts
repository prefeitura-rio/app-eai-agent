import Cookies from 'js-cookie';

const ACCESS_TOKEN_KEY = 'servicos_access_token';
const TOKEN_EXPIRY_DAYS = 7;

/**
 * Recupera o access token dos cookies
 */
export function getAccessToken(): string | null {
  const token = Cookies.get(ACCESS_TOKEN_KEY) || null;
  if (token) {
    console.log('[Auth] Token encontrado no cookie');
  } else {
    console.log('[Auth] Nenhum token encontrado');
  }
  return token;
}

/**
 * Salva o access token nos cookies
 */
export function setAccessToken(accessToken: string): void {
  console.log('[Auth] Salvando access token...');
  Cookies.set(ACCESS_TOKEN_KEY, accessToken, {
    expires: TOKEN_EXPIRY_DAYS,
    sameSite: 'lax',
    path: '/',
  });
  console.log('[Auth] Token salvo com sucesso');
}

/**
 * Remove o access token dos cookies
 */
export function clearAccessToken(): void {
  console.log('[Auth] Removendo access token...');

  // Remover com path / para garantir
  Cookies.remove(ACCESS_TOKEN_KEY, { path: '/' });

  // Tentar remover sem path também (por precaução)
  Cookies.remove(ACCESS_TOKEN_KEY);

  // Verificar se realmente foi removido
  const stillExists = Cookies.get(ACCESS_TOKEN_KEY);
  if (stillExists) {
    console.error('[Auth] FALHA: Token ainda existe após remoção!', stillExists);
  } else {
    console.log('[Auth] Token removido com sucesso');
  }
}

/**
 * Verifica se o usuario esta autenticado
 */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}
