import {
  addToCart,
  describeCartTotal,
  estimateCart,
  orderItemsBody,
  type CartLine,
  type CartProduct,
} from '../src/cart';
import { formatMoney } from '../src/money';

function line(overrides: Partial<CartLine> = {}): CartLine {
  return {
    productId: 'mug',
    sku: 'MUG-1',
    name: 'Mug',
    unitAmountMinor: 199,
    currency: 'USD',
    quantity: 2,
    ...overrides,
  };
}

const activeMug: CartProduct = {
  id: 'mug',
  sku: 'MUG-1',
  name: 'Mug',
  unitAmountMinor: 199,
  currency: 'USD',
  active: true,
};

describe('cart total display', () => {
  it('formats dollars from integer minor units', () => {
    expect(formatMoney(448, 'USD')).toBe('4.48 USD');
    expect(formatMoney(10, 'USD')).toBe('0.10 USD');
    expect(formatMoney(0, 'EUR')).toBe('0.00 EUR');
  });

  it('sums a cart with integer multiplication', () => {
    const lines = [
      line({ unitAmountMinor: 199, quantity: 2 }),
      line({ productId: 'soap', unitAmountMinor: 50, quantity: 1 }),
    ];
    expect(estimateCart(lines)).toEqual({
      kind: 'total',
      amountMinor: 448,
      currency: 'USD',
    });
    expect(describeCartTotal(lines)).toBe('Estimated total: 4.48 USD');
  });

  it('does not add different currencies into one number', () => {
    const lines = [
      line(),
      line({
        productId: 'euro',
        currency: 'EUR',
        unitAmountMinor: 100,
        quantity: 1,
      }),
    ];
    expect(describeCartTotal(lines)).toBe('Estimated total: mixed currencies');
  });

  it('labels an empty cart without inventing a currency', () => {
    expect(describeCartTotal([])).toBe('Estimated total: —');
  });

  it('refuses to add an inactive product', () => {
    expect(addToCart([], { ...activeMug, active: false }, 1)).toBeNull();
  });

  it('sends product id and quantity only', () => {
    expect(orderItemsBody([line()])).toEqual({
      items: [{ product_id: 'mug', quantity: 2 }],
    });
  });
});
