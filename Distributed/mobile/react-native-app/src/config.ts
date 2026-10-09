/**
 * Documented public entry is the gateway on port 8080
 * (`deploy/gateway/compose.yaml`). Paths stay the ones Traefik already routes.
 * An Android emulator reaches the host as 10.0.2.2, not 127.0.0.1.
 */
export const API_BASE_URL = 'http://127.0.0.1:8080';

export function apiBaseUrl(): string {
  return API_BASE_URL.replace(/\/+$/, '');
}
