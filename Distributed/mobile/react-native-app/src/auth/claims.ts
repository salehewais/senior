export type AccessClaims = {
  role: string | null;
  exp: number | null;
};

const BASE64_ALPHABET =
  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

function decodeBase64Url(segment: string): string {
  const base64 = segment.replace(/-/g, '+').replace(/_/g, '/');
  const padded = base64.padEnd(
    base64.length + ((4 - (base64.length % 4)) % 4),
    '=',
  );
  const chars: string[] = [];
  for (let index = 0; index < padded.length; index += 4) {
    const first = BASE64_ALPHABET.indexOf(padded[index]);
    const second = BASE64_ALPHABET.indexOf(padded[index + 1]);
    const thirdChar = padded[index + 2];
    const fourthChar = padded[index + 3];
    const third = thirdChar === '=' ? -1 : BASE64_ALPHABET.indexOf(thirdChar);
    const fourth =
      fourthChar === '=' ? -1 : BASE64_ALPHABET.indexOf(fourthChar);
    if (first < 0 || second < 0) {
      throw new Error('invalid base64');
    }
    if (thirdChar !== '=' && third < 0) {
      throw new Error('invalid base64');
    }
    if (fourthChar !== '=' && fourth < 0) {
      throw new Error('invalid base64');
    }
    chars.push(String.fromCharCode(first * 4 + Math.floor(second / 16)));
    if (third >= 0) {
      chars.push(
        String.fromCharCode((second % 16) * 16 + Math.floor(third / 4)),
      );
    }
    if (third >= 0 && fourth >= 0) {
      chars.push(String.fromCharCode((third % 4) * 64 + fourth));
    }
  }
  return chars.join('');
}

export function readAccessClaims(token: string): AccessClaims {
  // The signature is not checked here. The API verifies RS256.
  const empty: AccessClaims = { role: null, exp: null };
  try {
    const segment = token.split('.')[1];
    if (!segment) {
      return empty;
    }
    const parsed: unknown = JSON.parse(decodeBase64Url(segment));
    if (!parsed || typeof parsed !== 'object' || Array.isArray(parsed)) {
      return empty;
    }
    const record = parsed as Record<string, unknown>;
    return {
      role: typeof record.role === 'string' ? record.role : null,
      exp: typeof record.exp === 'number' ? record.exp : null,
    };
  } catch {
    return empty;
  }
}
