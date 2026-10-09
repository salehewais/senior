import { orderItemsBody, type CartLine } from '../cart';
import { session } from '../auth/session';
import { apiRequest } from './client';
import type {
  Customer,
  DeviceToken,
  DeviceTokenList,
  Order,
  OrderList,
  Product,
  ProductList,
  TokenPair,
} from './types';

export async function registerAccount(
  email: string,
  displayName: string,
  password: string,
): Promise<void> {
  const pair = await apiRequest<TokenPair>('/api/v1/auth/register', {
    method: 'POST',
    body: { email, display_name: displayName, password },
  });
  session.setTokens(pair.access_token, pair.refresh_token);
}

export async function loginAccount(
  email: string,
  password: string,
): Promise<void> {
  const pair = await apiRequest<TokenPair>('/api/v1/auth/login', {
    method: 'POST',
    body: { email, password },
  });
  session.setTokens(pair.access_token, pair.refresh_token);
}

export async function logoutAccount(): Promise<void> {
  const refreshToken = session.refreshToken;
  try {
    if (refreshToken) {
      await apiRequest<void>('/api/v1/auth/logout', {
        method: 'POST',
        body: { refresh_token: refreshToken },
      });
    }
  } finally {
    session.clear();
  }
}

export function getMe(): Promise<Customer> {
  return apiRequest<Customer>('/api/v1/customers/me');
}

export function listProducts(
  limit: number,
  offset: number,
): Promise<ProductList> {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });
  return apiRequest<ProductList>(`/api/v1/products?${params.toString()}`);
}

export function getProduct(productId: string): Promise<Product> {
  return apiRequest<Product>(`/api/v1/products/${productId}`);
}

export function listOrders(
  limit: number,
  cursor: string | null,
): Promise<OrderList> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (cursor) {
    params.set('cursor', cursor);
  }
  return apiRequest<OrderList>(`/api/v1/orders?${params.toString()}`);
}

export function getOrder(orderId: string): Promise<Order> {
  return apiRequest<Order>(`/api/v1/orders/${orderId}`);
}

export function createOrder(lines: readonly CartLine[]): Promise<Order> {
  return apiRequest<Order>('/api/v1/orders', {
    method: 'POST',
    body: orderItemsBody(lines),
  });
}

export function confirmOrder(orderId: string): Promise<Order> {
  return apiRequest<Order>(`/api/v1/orders/${orderId}/confirm`, {
    method: 'POST',
  });
}

export function cancelOrder(orderId: string): Promise<Order> {
  return apiRequest<Order>(`/api/v1/orders/${orderId}/cancel`, {
    method: 'POST',
    body: { reason: 'customer_request' },
  });
}

export function listDeviceTokens(): Promise<DeviceTokenList> {
  return apiRequest<DeviceTokenList>('/api/v1/device-tokens');
}

export function registerDeviceToken(
  token: string,
  platform: 'android' | 'ios',
): Promise<DeviceToken> {
  return apiRequest<DeviceToken>('/api/v1/device-tokens', {
    method: 'POST',
    body: { token, platform },
  });
}

export function deleteDeviceToken(tokenId: string): Promise<void> {
  return apiRequest<void>(`/api/v1/device-tokens/${tokenId}`, {
    method: 'DELETE',
  });
}
