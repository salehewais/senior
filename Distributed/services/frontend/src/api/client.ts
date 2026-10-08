import { readAccessClaims } from "../auth/claims";
import { session } from "../auth/session";
import { ApiError, apiErrorFromPayload } from "./errors";
import type { TokenPair } from "./types";

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  retried?: boolean;
};

export function apiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL?.trim();
  const base = configured && configured.length > 0 ? configured : "http://127.0.0.1:8000";
  return base.replace(/\/+$/, "");
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
  // exp is a display hint from an unverified payload. The server still rejects a bad token.
  const token = session.accessToken;
  if (!token) return false;
  const { exp } = readAccessClaims(token);
  if (exp === null) return false;
  return Date.now() / 1000 >= exp;
}

async function performRefresh(): Promise<boolean> {
  const refreshToken = session.refreshToken;
  if (!refreshToken) return false;
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      cache: "no-store",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
        "X-Correlation-Id": crypto.randomUUID(),
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

let restoreInFlight: Promise<void> | null = null;

export function restoreSession(): Promise<void> {
  restoreInFlight ??= (async () => {
    if (session.refreshToken && !session.accessToken) await refreshOnce();
    session.markReady();
  })();
  return restoreInFlight;
}

async function readApiError(response: Response): Promise<ApiError> {
  try {
    return apiErrorFromPayload(response.status, await response.json());
  } catch {
    return apiErrorFromPayload(response.status, null);
  }
}

export async function apiRequest<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const method = options.method ?? "GET";
  const isAuthPath = path.startsWith("/api/v1/auth/");
  const sendBearer = options.auth ?? !isAuthPath;
  let retried = options.retried ?? false;
  if (sendBearer && !retried && accessLooksExpired()) {
    retried = true;
    const refreshed = await refreshOnce();
    if (!refreshed) session.clear();
  }
  const headers = new Headers();
  headers.set("Accept", "application/json");
  // A correlation id is not a trace id. Do not replace this header with traceparent.
  headers.set("X-Correlation-Id", crypto.randomUUID());
  if (sendBearer && session.accessToken) {
    headers.set("Authorization", `Bearer ${session.accessToken}`);
  }
  let body: string | undefined;
  if (options.body !== undefined) {
    headers.set("Content-Type", "application/json");
    body = JSON.stringify(options.body);
  }

  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}${path}`, {
      method,
      headers,
      body,
      cache: "no-store",
    });
  } catch {
    throw new ApiError(0, "The order service could not be reached.", null, null);
  }

  if (response.status === 401 && sendBearer) {
    if (!retried) {
      const refreshed = await refreshOnce();
      if (refreshed) return apiRequest<T>(path, { ...options, retried: true });
    }
    session.clear();
  }

  if (response.status === 204) return undefined as T;
  if (!response.ok) throw await readApiError(response);
  return (await response.json()) as T;
}
