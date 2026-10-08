export class ApiError extends Error {
  readonly status: number;
  readonly code: string | null;
  readonly correlationId: string | null;

  constructor(status: number, message: string, code: string | null, correlationId: string | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.correlationId = correlationId;
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/** Read the error envelope. Anything else, including a stack trace, stays off the screen. */
export function apiErrorFromPayload(status: number, payload: unknown): ApiError {
  const fallback = `The request failed (${status}).`;
  if (!isRecord(payload) || !isRecord(payload.error)) {
    return new ApiError(status, fallback, null, null);
  }
  const body = payload.error;
  const message = typeof body.message === "string" && body.message.trim() !== "" ? body.message : fallback;
  const code = typeof body.code === "string" ? body.code : null;
  const correlationId = typeof body.correlation_id === "string" ? body.correlation_id : null;
  return new ApiError(status, message, code, correlationId);
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return "The request failed.";
}
