export type Example = {
  id: string;
  title: string;
  category: string;
  source: string;
  call: string;
};

export type LoopFrame = {
  kind: "for" | "while";
  start: string | null;
  end: string | null;
  index: string | null;
  condition: string | null;
  conditionValue?: string | null;
};

export type CallEvent = {
  type: "call";
  id: number;
  parent: number | null;
  name: string;
  args: string[];
  depth: number;
  line?: number;
  params: Record<string, string>;
  argExprs: string[];
  locals: Record<string, string>;
  callerLocals: Record<string, string>;
  loops?: LoopFrame[] | null;
  callerLoops?: LoopFrame[] | null;
};

export type ReturnEvent = {
  type: "return";
  id: number;
  value: string;
  error: boolean;
  line?: number;
  locals: Record<string, string>;
  callerLocals: Record<string, string>;
  loops?: LoopFrame[] | null;
  callerLoops?: LoopFrame[] | null;
};

export type LineEvent = {
  type: "line";
  id: number;
  line: number;
  locals: Record<string, string>;
  changed: string[];
  loops?: LoopFrame[] | null;
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
