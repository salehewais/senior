import { useSyncExternalStore } from "react";

import { addToCart, removeLine, setQuantity, type CartLine, type CartProduct } from "./cart";

const CART_STORAGE_KEY = "commerce.cart";

// The cart is not an order. It stays in the browser until checkout posts one order.

type Listener = () => void;

function isCartLine(value: unknown): value is CartLine {
  if (!value || typeof value !== "object") return false;
  const line = value as Record<string, unknown>;
  return (
    typeof line.productId === "string" &&
    typeof line.name === "string" &&
    typeof line.sku === "string" &&
    typeof line.unitAmountMinor === "number" &&
    Number.isInteger(line.unitAmountMinor) &&
    line.unitAmountMinor >= 0 &&
    typeof line.currency === "string" &&
    typeof line.quantity === "number" &&
    Number.isInteger(line.quantity) &&
    line.quantity >= 1
  );
}

function readStoredCart(): CartLine[] {
  if (typeof sessionStorage === "undefined") return [];
  try {
    const raw = sessionStorage.getItem(CART_STORAGE_KEY);
    if (!raw) return [];
    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return parsed.filter(isCartLine);
  } catch {
    return [];
  }
}

let lines: CartLine[] = readStoredCart();
let snapshot: readonly CartLine[] = lines;
const listeners = new Set<Listener>();

function publish(next: readonly CartLine[]): void {
  lines = [...next];
  snapshot = lines;
  if (typeof sessionStorage !== "undefined") {
    try {
      sessionStorage.setItem(CART_STORAGE_KEY, JSON.stringify(next));
    } catch {
      // Keep the in-memory cart if storage is blocked.
    }
  }
  for (const listener of listeners) listener();
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
    if (!next) return false;
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
