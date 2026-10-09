export type Example = {
  id: string;
  title: string;
  source: string;
  call: string;
};

export type CallEvent = {
  type: "call";
  id: number;
  parent: number | null;
  name: string;
  args: string[];
  depth: number;
  line?: number;
};

export type ReturnEvent = {
  type: "return";
  id: number;
  value: string;
  error: boolean;
  line?: number;
};

export type LineEvent = {
  type: "line";
  id: number;
  line: number;
  locals: Record<string, string>;
  changed: string[];
};

export type TraceEvent = CallEvent | ReturnEvent | LineEvent;

export type TraceResponse = {
  events: TraceEvent[];
  result: string | null;
  error: string | null;
  truncated: boolean;
  timed_out: boolean;
  target: string | null;
};
