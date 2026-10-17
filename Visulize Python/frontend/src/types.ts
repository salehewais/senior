export type EventKind = "line" | "call" | "return" | "exception";

export type Value =
  | { kind: "none" }
  | { kind: "bool"; v: boolean }
  | { kind: "int"; v: number }
  | { kind: "float"; v: number | null; repr?: string }
  | { kind: "str"; v: string }
  | { kind: "ref"; id: number }
  | { kind: "function"; name: string }
  | { kind: "class"; name: string }
  | { kind: "unknown"; type: string; repr: string };

export interface Binding {
  name: string;
  value: Value;
}

export interface StackFrame {
  func: string;
  line: number;
  locals: Binding[];
}

export interface HeapObject {
  kind: string;
  items?: Array<Value | { key: Value; value: Value }>;
  name?: string;
  type?: string;
  attrs?: Binding[];
  repr?: string;
  truncated?: boolean;
  bases?: string[];
  params?: string[];
  closure?: Binding[];
  class_ref?: Value;
}

export interface StepException {
  type: string;
  message: string;
}

export interface Step {
  line: number;
  event: EventKind;
  func: string;
  stdout: string;
  exception: StepException | null;
  stack: StackFrame[];
  globals: Binding[];
  heap: Record<string, HeapObject>;
  return_value?: Value | null;
}

export interface TraceError {
  type: string;
  message: string;
  line: number | null;
}

export interface TraceResponse {
  steps: Step[];
  stopped: "step_limit" | "timeout" | null;
  error?: TraceError | null;
}
