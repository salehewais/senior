/** Display formatting only. Totals the server stores are integer minor units. */

export function formatMoney(amountMinor: number, currency: string): string {
  const negative = amountMinor < 0;
  const abs = Math.abs(Math.trunc(amountMinor));
  const major = Math.floor(abs / 100);
  const cents = abs % 100;
  const digits = `${major}.${cents.toString().padStart(2, '0')}`;
  return `${negative ? '-' : ''}${digits} ${currency}`;
}
