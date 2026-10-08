import { useSyncExternalStore } from "react";

import { readAccessClaims } from "./claims";

const REFRESH_STORAGE_KEY = "commerce.refresh_token";

// Learning simplification. The access token stays in this module's memory.
// The refresh token is also copied to sessionStorage so a reload of this tab
// can call POST /api/v1/auth/refresh. Production would not do this: the server
// would set an httpOnly cookie, which page scripts cannot read. sessionStorage
// is readable by any script on this origin, the same exposure as localStorage.

export type SessionSnapshot = {
  accessToken: string | null;
  refreshToken: string | null;
  role: string | null;
  ready: boolean;
};

type Listener = () => void;

function readStoredRefresh(): string | null {
  if (typeof sessionStorage === "undefined") return null;
  try {
    return sessionStorage.getItem(REFRESH_STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredRefresh(value: string | null): void {
  if (typeof sessionStorage === "undefined") return;
  try {
    if (value === null) sessionStorage.removeItem(REFRESH_STORAGE_KEY);
    else sessionStorage.setItem(REFRESH_STORAGE_KEY, value);
  } catch {
    // A blocked storage API still leaves the tokens in memory for this page.
  }
}

let accessToken: string | null = null;
let refreshToken: string | null = readStoredRefresh();
let role: string | null = null;
let ready = refreshToken === null;
const listeners = new Set<Listener>();
let snapshot: SessionSnapshot = currentSnapshot();

function currentSnapshot(): SessionSnapshot {
  return { accessToken, refreshToken, role, ready };
}

function publish(): void {
  snapshot = currentSnapshot();
  for (const listener of listeners) listener();
}

function setTokens(nextAccess: string, nextRefresh: string): void {
  accessToken = nextAccess;
  refreshToken = nextRefresh;
  role = readAccessClaims(nextAccess).role;
  ready = true;
  writeStoredRefresh(nextRefresh);
  publish();
}

function clear(): void {
  accessToken = null;
  refreshToken = null;
  role = null;
  ready = true;
  writeStoredRefresh(null);
  publish();
}

function markReady(): void {
  if (ready) return;
  ready = true;
  publish();
}

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot(): SessionSnapshot {
  return snapshot;
}

export const session = {
  get accessToken() {
    return accessToken;
  },
  get refreshToken() {
    return refreshToken;
  },
  get role() {
    return role;
  },
  setTokens,
  clear,
  markReady,
  subscribe,
  getSnapshot,
};

export function useSession(): SessionSnapshot {
  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}
