export type Money = {
  amount_minor: number;
  currency: string;
};

export type Product = {
  id: string;
  sku: string;
  name: string;
  unit_price: Money;
  active: boolean;
  version: number;
};

export type ProductList = {
  items: Product[];
  limit: number;
  offset: number;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
};

export type Customer = {
  id: string;
  email: string;
  display_name: string;
  version: number;
};

export type OrderItem = {
  product_id: string;
  sku: string;
  quantity: number;
  unit_price: Money;
};

export type Order = {
  id: string;
  customer_id: string;
  status: string;
  saga_status: string | null;
  items: OrderItem[];
  total: Money;
  version: number;
  tracking_reference?: string | null;
  cancel_reason?: string | null;
};

export type OrderList = {
  items: Order[];
  next_cursor: string | null;
};
