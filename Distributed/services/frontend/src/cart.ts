import { formatMoney } from "./money";

export type CartLine = {
  productId: string;
  sku: string;
  name: string;
  unitAmountMinor: number;
  currency: string;
  quantity: number;
};

export type CartProduct = {
  id: string;
  sku: string;
  name: string;
  unitAmountMinor: number;
  currency: string;
  active: boolean;
};

type CartEstimate =
  | { kind: "empty" }
  | { kind: "mixed" }
  | { kind: "total"; amountMinor: number; currency: string };

function isPositiveInt(value: number): boolean {
  return Number.isInteger(value) && value >= 1;
}

export function estimateCart(lines: readonly CartLine[]): CartEstimate {
  if (lines.length === 0) return { kind: "empty" };
  const currency = lines[0].currency;
  let amountMinor = 0;
  for (const line of lines) {
    if (line.currency !== currency) return { kind: "mixed" };
    amountMinor += line.unitAmountMinor * line.quantity;
  }
  return { kind: "total", amountMinor, currency };
}

/** The cart page label. This number is an estimate; checkout does not send it. */
export function describeCartTotal(lines: readonly CartLine[]): string {
  const estimate = estimateCart(lines);
  if (estimate.kind === "empty") return "Estimated total: —";
  if (estimate.kind === "mixed") return "Estimated total: mixed currencies";
  return `Estimated total: ${formatMoney(estimate.amountMinor, estimate.currency)}`;
}

export function addToCart(
  lines: readonly CartLine[],
  product: CartProduct,
  quantity: number,
): readonly CartLine[] | null {
  if (!product.active || !isPositiveInt(quantity) || !Number.isInteger(product.unitAmountMinor)) {
    return null;
  }
  const existing = lines.find((line) => line.productId === product.id);
  if (!existing) {
    return [
      ...lines,
      {
        productId: product.id,
        sku: product.sku,
        name: product.name,
        unitAmountMinor: product.unitAmountMinor,
        currency: product.currency,
        quantity,
      },
    ];
  }
  return lines.map((line) =>
    line.productId === product.id
      ? {
          ...line,
          sku: product.sku,
          name: product.name,
          unitAmountMinor: product.unitAmountMinor,
          currency: product.currency,
          quantity: line.quantity + quantity,
        }
      : line,
  );
}

export function setQuantity(
  lines: readonly CartLine[],
  productId: string,
  quantity: number,
): readonly CartLine[] {
  if (!isPositiveInt(quantity)) return lines;
  return lines.map((line) => (line.productId === productId ? { ...line, quantity } : line));
}

export function removeLine(lines: readonly CartLine[], productId: string): readonly CartLine[] {
  return lines.filter((line) => line.productId !== productId);
}
