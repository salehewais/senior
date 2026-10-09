import { useSyncExternalStore } from 'react';

import {
  addToCart,
  removeLine,
  setQuantity,
  type CartLine,
  type CartProduct,
} from './cart';

type Listener = () => void;

let lines: CartLine[] = [];
let snapshot: readonly CartLine[] = lines;
const listeners = new Set<Listener>();

function publish(next: readonly CartLine[]): void {
  lines = [...next];
  snapshot = lines;
  for (const listener of listeners) {
    listener();
  }
}

function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function getSnapshot(): readonly CartLine[] {
  return snapshot;
}

export const cartStore = {
  subscribe,
  getSnapshot,
  add(product: CartProduct, quantity: number): boolean {
    const next = addToCart(lines, product, quantity);
    if (!next) {
      return false;
    }
    publish(next);
    return true;
  },
  setQuantity(productId: string, quantity: number): void {
    publish(setQuantity(lines, productId, quantity));
  },
  remove(productId: string): void {
    publish(removeLine(lines, productId));
  },
  clear(): void {
    publish([]);
  },
};

export function useCart(): readonly CartLine[] {
  return useSyncExternalStore(subscribe, getSnapshot, getSnapshot);
}
