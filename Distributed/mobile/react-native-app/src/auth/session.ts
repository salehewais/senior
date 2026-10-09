import { useSyncExternalStore } from 'react';

import { readAccessClaims } from './claims';

export type SessionSnapshot = {
  accessToken: string | null;
  refreshToken: string | null;
  role: string | null;
};

type Listener = () => void;

let accessToken: string | null = null;
let refreshToken: string | null = null;
let role: string | null = null;
const listeners = new Set<Listener>();
let snapshot: SessionSnapshot = currentSnapshot();

function currentSnapshot(): SessionSnapshot {
  return { accessToken, refreshToken, role };
}

function publish(): void {
  snapshot = currentSnapshot();
  for (const listener of listeners) {
    listener();
  }
}

function setTokens(nextAccess: string, nextRefresh: string): void {
  accessToken = nextAccess;
  refreshToken = nextRefresh;
  role = readAccessClaims(nextAccess).role;
  publish();
}

function clear(): void {
  accessToken = null;
  refreshToken = null;
  role = null;
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
  subscribe,
  getSnapshot,
};

export function useSession(): SessionSnapshot {
  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}
