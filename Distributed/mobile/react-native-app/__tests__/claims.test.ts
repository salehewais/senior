import { readAccessClaims } from '../src/auth/claims';

const BASE64_ALPHABET =
  'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';

function encodeBase64Url(text: string): string {
  const bytes = Array.from(text, char => char.charCodeAt(0));
  let encoded = '';
  for (let index = 0; index < bytes.length; index += 3) {
    const first = bytes[index];
    const second = index + 1 < bytes.length ? bytes[index + 1] : -1;
    const third = index + 2 < bytes.length ? bytes[index + 2] : -1;
    encoded += BASE64_ALPHABET[Math.floor(first / 4)];
    const secondBits = second < 0 ? 0 : second;
    encoded += BASE64_ALPHABET[(first % 4) * 16 + Math.floor(secondBits / 16)];
    if (second < 0) {
      break;
    }
    const thirdBits = third < 0 ? 0 : third;
    encoded += BASE64_ALPHABET[(second % 16) * 4 + Math.floor(thirdBits / 64)];
    if (third < 0) {
      break;
    }
    encoded += BASE64_ALPHABET[third % 64];
  }
  return encoded.replace(/\+/g, '-').replace(/\//g, '_');
}

function tokenWithPayload(payload: Record<string, unknown>): string {
  return `header.${encodeBase64Url(JSON.stringify(payload))}.sig`;
}

describe('access claims', () => {
  it('reads role and exp without treating them as proof', () => {
    const claims = readAccessClaims(
      tokenWithPayload({ role: 'customer', exp: 1_700_000_000 }),
    );
    expect(claims).toEqual({ role: 'customer', exp: 1_700_000_000 });
  });

  it('returns empty claims when the payload is not an object', () => {
    expect(readAccessClaims('a.b.c')).toEqual({ role: null, exp: null });
  });
});
