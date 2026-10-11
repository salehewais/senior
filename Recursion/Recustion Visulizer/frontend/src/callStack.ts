import type { TraceEvent } from "./types";

export type CallList = "stack" | "all";

export type CallRow = {
  id: number;
  name: string;
  param: string;
  vars: string;
  returned: boolean;
  error: boolean;
  returnValue: string | null;
  active: boolean;
  callCursor: number;
};

type Frame = {
  id: number;
  name: string;
  parent: number | null;
  names: string[];
  exprs: string[];
  values: Record<string, string>;
  vars: [string, string][];
  returned: boolean;
  error: boolean;
  returnValue: string | null;
  callCursor: number;
};

function applyLocals(frame: Frame, locals: Record<string, string>) {
  for (const name of frame.names) {
    if (Object.prototype.hasOwnProperty.call(locals, name)) {
      frame.values[name] = locals[name];
    }
  }
  const params = new Set(frame.names);
  const vars: [string, string][] = [];
  for (const [name, value] of Object.entries(locals)) {
    if (!params.has(name)) vars.push([name, value]);
  }
  frame.vars = vars;
}

function paramText(frame: Frame): string {
  return frame.names
    .map((name, index) => {
      const value = frame.values[name] ?? "?";
      const expr = frame.exprs[index] ?? "";
      if (expr && expr !== value) return `${expr} → ${value}`;
      return `${name} = ${value}`;
    })
    .join(", ");
}

function varsText(frame: Frame): string {
  return frame.vars.map(([name, value]) => `${name} = ${value}`).join(", ");
}

export function buildCallRows(events: TraceEvent[], cursor: number, list: CallList): CallRow[] {
  const frames = new Map<number, Frame>();
  const order: number[] = [];
  let stack: number[] = [];
  const seen = events.slice(0, cursor);

  for (let index = 0; index < seen.length; index += 1) {
    const event = seen[index];
    if (event.type === "call") {
      const names = Object.keys(event.params);
      const frame: Frame = {
        id: event.id,
        name: event.name,
        parent: event.parent,
        names,
        exprs: event.argExprs,
        values: { ...event.params },
        vars: [],
        returned: false,
        error: false,
        returnValue: null,
        callCursor: index + 1,
      };
      applyLocals(frame, event.locals);
      frames.set(event.id, frame);
      order.push(event.id);
      stack.push(event.id);
      if (event.parent != null) {
        const parent = frames.get(event.parent);
        if (parent) applyLocals(parent, event.callerLocals);
      }
    } else if (event.type === "line") {
      const frame = frames.get(event.id);
      if (frame) applyLocals(frame, event.locals);
    } else {
      const frame = frames.get(event.id);
      if (frame) {
        applyLocals(frame, event.locals);
        frame.returned = true;
        frame.error = event.error;
        frame.returnValue = event.value;
        if (frame.parent != null) {
          const parent = frames.get(frame.parent);
          if (parent) applyLocals(parent, event.callerLocals);
        }
      }
      stack = stack.filter((id) => id !== event.id);
    }
  }

  const activeId = cursor > 0 ? (events[cursor - 1]?.id ?? null) : null;
  const ids = list === "stack" ? stack : order;
  const rows: CallRow[] = [];
  for (const id of ids) {
    const frame = frames.get(id);
    if (!frame) continue;
    rows.push({
      id: frame.id,
      name: frame.name,
      param: paramText(frame),
      vars: varsText(frame),
      returned: frame.returned,
      error: frame.error,
      returnValue: frame.returnValue,
      active: frame.id === activeId,
      callCursor: frame.callCursor,
    });
  }
  return rows;
}
