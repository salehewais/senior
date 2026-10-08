import { describe, expect, it } from "vitest";

import { apiErrorFromPayload, errorMessage } from "./errors";

describe("API error parsing", () => {
  it("shows the server message and drops diagnostic fields", () => {
    const error = apiErrorFromPayload(409, {
      error: {
        code: "INVALID_STATE_TRANSITION",
        message: "An order in CONFIRMED cannot move to CANCELLED.",
        correlation_id: "018f1c2a-3333-7c11-8a22-444444444444",
        details: [],
      },
      stack: "Traceback (most recent call last):\n  File secret.py",
      traceback: "secret",
    });
    expect(error.message).toBe("An order in CONFIRMED cannot move to CANCELLED.");
    expect(error.message).not.toMatch(/Traceback|secret/);
    expect(error.code).toBe("INVALID_STATE_TRANSITION");
    expect(error.correlationId).toBe("018f1c2a-3333-7c11-8a22-444444444444");
    expect(error.status).toBe(409);
    expect(errorMessage(error)).toBe(error.message);
  });

  it("does not treat a raw body or a thrown Error as a user message", () => {
    expect(apiErrorFromPayload(500, "Traceback (most recent call last)").message).toBe(
      "The request failed (500).",
    );
    expect(apiErrorFromPayload(400, {}).message).toBe("The request failed (400).");
    expect(errorMessage(new Error("Traceback (most recent call last)"))).toBe("The request failed.");
  });
});
