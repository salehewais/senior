/** Display formatting only. Totals the server will store are computed in integer minor units. */

export function formatMoney(amountMinor: number, currency: string): string {
  const negative = amountMinor < 0;
  const abs = Math.abs(Math.trunc(amountMinor));
  const major = Math.floor(abs / 100);
  const cents = abs % 100;
  const digits = `${major}.${cents.toString().padStart(2, "0")}`;
  return `${negative ? "-" : ""}${digits} ${currency}`;
}

/** Parse a dollar field such as "12.50" into minor units without a binary float multiply. */
export function parseDollarsToMinor(text: string): number | null {
  const match = /^(\d+)(?:\.(\d{1,2}))?$/.exec(text.trim());
  if (!match) return null;
  const whole = Number(match[1]);
  if (!Number.isSafeInteger(whole)) return null;
  const fraction = (match[2] ?? "").padEnd(2, "0");
  return whole * 100 + Number(fraction);
}
