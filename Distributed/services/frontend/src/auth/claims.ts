export type AccessClaims = {
  role: string | null;
  exp: number | null;
};

function decodeBase64Url(segment: string): string {
  const base64 = segment.replace(/-/g, "+").replace(/_/g, "/");
  const padded = base64.padEnd(base64.length + ((4 - (base64.length % 4)) % 4), "=");
  const binary = atob(padded);
  const bytes = Uint8Array.from(binary, (char) => char.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

export function readAccessClaims(token: string): AccessClaims {
  // The signature is absent from this check. The UI hides admin controls when
  // the payload role is not admin. The API rejects a forged role because it
  // verifies the RS256 signature; this function does not.
  const empty: AccessClaims = { role: null, exp: null };
  try {
    const segment = token.split(".")[1];
    if (!segment) return empty;
    const parsed: unknown = JSON.parse(decodeBase64Url(segment));
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) return empty;
    const record = parsed as Record<string, unknown>;
    return {
      role: typeof record.role === "string" ? record.role : null,
      exp: typeof record.exp === "number" ? record.exp : null,
    };
  } catch {
    return empty;
  }
}
