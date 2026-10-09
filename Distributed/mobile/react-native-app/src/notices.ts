import { useSyncExternalStore } from 'react';

export type SessionNotice = {
  id: string;
  text: string;
};

type Listener = () => void;

let notices: SessionNotice[] = [];
let snapshot: readonly SessionNotice[] = notices;
const listeners = new Set<Listener>();
let nextId = 1;

function publish(next: readonly SessionNotice[]): void {
  notices = [...next];
  snapshot = notices;
  for (const listener of listeners) {
    listener();
  }
}

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot(): readonly SessionNotice[] {
  return snapshot;
}

export const sessionNotices = {
  subscribe,
  getSnapshot,
  add(text: string): void {
    const id = String(nextId);
    nextId += 1;
    publish([{ id, text }, ...notices]);
  },
  clear(): void {
    publish([]);
  },
};

export function useSessionNotices(): readonly SessionNotice[] {
  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}
