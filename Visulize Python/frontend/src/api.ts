import type { TraceResponse } from "./types";

export async function trace(code: string, stdin: string): Promise<TraceResponse> {
  const response = await fetch("/api/trace", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, stdin }),
  });
  if (!response.ok) {
    throw new Error(`The visualizer could not run that code (${response.status}).`);
  }
  return (await response.json()) as TraceResponse;
}
