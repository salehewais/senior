import { readAccessClaims } from '../auth/claims';
import { session } from '../auth/session';
import { apiBaseUrl } from '../config';
import { ApiError, apiErrorFromPayload } from './errors';
import type { TokenPair } from './types';

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  retried?: boolean;
};

function correlationId(): string {
  // A correlation id is not a secret and not a trace id.
  const hex = '0123456789abcdef';
  let id = '';
  for (let index = 0; index < 36; index += 1) {
    if (index === 8 || index === 13 || index === 18 || index === 23) {
      id += '-';
    } else if (index === 14) {
      id += '4';
    } else if (index === 19) {
      id += hex[8 + Math.floor(Math.random() * 4)];
    } else {
      id += hex[Math.floor(Math.random() * 16)];
    }
  }
  return id;
}

let refreshInFlight: Promise<boolean> | null = null;

export function refreshOnce(): Promise<boolean> {
  if (!refreshInFlight) {
    refreshInFlight = performRefresh().finally(() => {
      refreshInFlight = null;
    });
  }
  return refreshInFlight;
}

function accessLooksExpired(): boolean {
  const token = session.accessToken;
  if (!token) {
    return false;
  }
  const { exp } = readAccessClaims(token);
  if (exp === null) {
    return false;
  }
  return Date.now() / 1000 >= exp;
}

async function performRefresh(): Promise<boolean> {
  const refreshToken = session.refreshToken;
  if (!refreshToken) {
    return false;
  }
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
        'X-Correlation-Id': correlationId(),
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
  } catch {
    return false;
  }
  if (!response.ok) {
    session.clear();
    return false;
  }
  const pair = (await response.json()) as TokenPair;
  session.setTokens(pair.access_token, pair.refresh_token);
  return true;
}

async function readApiError(response: Response): Promise<ApiError> {
  try {
    return apiErrorFromPayload(response.status, await response.json());
  } catch {
    return apiErrorFromPayload(response.status, null);
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const method = options.method ?? 'GET';
  const isAuthPath = path.startsWith('/api/v1/auth/');
  const sendBearer = options.auth ?? !isAuthPath;
  let retried = options.retried ?? false;
  if (sendBearer && !retried && accessLooksExpired()) {
    retried = true;
    const refreshed = await refreshOnce();
    if (!refreshed) {
      session.clear();
    }
  }
  const headers = new Headers();
  headers.set('Accept', 'application/json');
  headers.set('X-Correlation-Id', correlationId());
  if (sendBearer && session.accessToken) {
    headers.set('Authorization', `Bearer ${session.accessToken}`);
  }
  let body: string | undefined;
  if (options.body !== undefined) {
    headers.set('Content-Type', 'application/json');
    body = JSON.stringify(options.body);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      method,
      headers,
      body,
    });
  } catch {
    throw new ApiError(0, 'The gateway could not be reached.', null, null);
  }

  if (response.status === 401 && sendBearer) {
    if (!retried) {
      const refreshed = await refreshOnce();
      if (refreshed) {
        return apiRequest<T>(path, { ...options, retried: true });
      }
    }
    session.clear();
  }

  if (response.status === 204) {
    return undefined as T;
  }
  if (!response.ok) {
    throw await readApiError(response);
  }
  return (await response.json()) as T;
}
