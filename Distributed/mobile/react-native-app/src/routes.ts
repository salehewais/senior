export type Route =
  | { name: 'login' }
  | { name: 'register' }
  | { name: 'catalog' }
  | { name: 'product'; productId: string }
  | { name: 'cart' }
  | { name: 'checkout' }
  | { name: 'orders' }
  | { name: 'order'; orderId: string }
  | { name: 'notifications' };

export const tabs = ['catalog', 'cart', 'orders', 'notifications'] as const;

export type TabName = (typeof tabs)[number];

export function isTab(name: Route['name']): name is TabName {
  return tabs.some(tab => tab === name);
}
