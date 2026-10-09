import type { Example, TraceResponse } from "./types";

export async function fetchExamples(): Promise<Example[]> {
  const response = await fetch("/api/examples");
  if (!response.ok) {
    throw new Error("Could not load examples.");
  }
  return response.json() as Promise<Example[]>;
}

export async function traceSource(source: string, call: string, debug = false): Promise<TraceResponse> {
  const response = await fetch("/api/trace", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source, call, debug }),
  });
  if (!response.ok) {
    throw new Error("The tracer rejected the run.");
  }
  return response.json() as Promise<TraceResponse>;
}
