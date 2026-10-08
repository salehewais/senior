import type { CartLine } from "../cart";
import { apiRequest } from "./client";
import type { Customer, Order, OrderList, Product, ProductList, TokenPair } from "./types";
import { session } from "../auth/session";

export async function registerAccount(email: string, displayName: string, password: string): Promise<void> {
  const pair = await apiRequest<TokenPair>("/api/v1/auth/register", {
    method: "POST",
    body: { email, display_name: displayName, password },
  });
  session.setTokens(pair.access_token, pair.refresh_token);
}

export async function loginAccount(email: string, password: string): Promise<void> {
  const pair = await apiRequest<TokenPair>("/api/v1/auth/login", {
    method: "POST",
    body: { email, password },
  });
  session.setTokens(pair.access_token, pair.refresh_token);
}

export async function logoutAccount(): Promise<void> {
  const refreshToken = session.refreshToken;
  try {
    if (refreshToken) {
      await apiRequest<void>("/api/v1/auth/logout", {
        method: "POST",
        body: { refresh_token: refreshToken },
      });
    }
  } finally {
    session.clear();
  }
}

export function getMe(): Promise<Customer> {
  return apiRequest<Customer>("/api/v1/customers/me");
}

export function listProducts(limit: number, offset: number): Promise<ProductList> {
  const params = new URLSearchParams({ limit: String(limit), offset: String(offset) });
  return apiRequest<ProductList>(`/api/v1/products?${params.toString()}`);
}

export function getProduct(productId: string): Promise<Product> {
  return apiRequest<Product>(`/api/v1/products/${productId}`);
}

export function createProduct(input: {
  sku: string;
  name: string;
  amountMinor: number;
  currency: string;
}): Promise<Product> {
  return apiRequest<Product>("/api/v1/products", {
    method: "POST",
    body: {
      sku: input.sku,
      name: input.name,
      unit_price: { amount_minor: input.amountMinor, currency: input.currency },
    },
  });
}

export function listOrders(limit: number, cursor: string | null): Promise<OrderList> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (cursor) params.set("cursor", cursor);
  return apiRequest<OrderList>(`/api/v1/orders?${params.toString()}`);
}

export function getOrder(orderId: string): Promise<Order> {
  return apiRequest<Order>(`/api/v1/orders/${orderId}`);
}

export function createOrder(lines: readonly CartLine[]): Promise<Order> {
  // The customer, prices, and total stay on the server. The cart estimate is not sent.
  return apiRequest<Order>("/api/v1/orders", {
    method: "POST",
    body: {
      items: lines.map((line) => ({ product_id: line.productId, quantity: line.quantity })),
    },
  });
}

export function confirmOrder(orderId: string): Promise<Order> {
  return apiRequest<Order>(`/api/v1/orders/${orderId}/confirm`, { method: "POST" });
}

export function cancelOrder(orderId: string): Promise<Order> {
  return apiRequest<Order>(`/api/v1/orders/${orderId}/cancel`, {
    method: "POST",
    body: { reason: "customer_request" },
  });
}
