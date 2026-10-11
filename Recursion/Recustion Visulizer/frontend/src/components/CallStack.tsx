import { useEffect, useMemo, useRef, useState, type PointerEvent as ReactPointerEvent } from "react";
import { buildCallRows, type CallList } from "../callStack";
import type { TraceEvent } from "../types";

const DEFAULT_HEIGHT = 220;
const MIN_HEIGHT = 72;
const MIN_TREE = 120;

type Props = {
  events: TraceEvent[];
  cursor: number;
  onJump: (cursor: number) => void;
};

export default function CallStack({ events, cursor, onJump }: Props) {
  const [list, setList] = useState<CallList>("stack");
  const [height, setHeight] = useState(DEFAULT_HEIGHT);
  const sectionRef = useRef<HTMLElement>(null);
  const bodyRef = useRef<HTMLDivElement>(null);
  const activeRef = useRef<HTMLTableRowElement>(null);
  const rows = useMemo(() => buildCallRows(events, cursor, list), [events, cursor, list]);

  useEffect(() => {
    const body = bodyRef.current;
    const row = activeRef.current;
    if (!body || !row) return;
    const bodyBox = body.getBoundingClientRect();
    const rowBox = row.getBoundingClientRect();
    if (rowBox.top < bodyBox.top) {
      body.scrollTop -= bodyBox.top - rowBox.top;
    } else if (rowBox.bottom > bodyBox.bottom) {
      body.scrollTop += rowBox.bottom - bodyBox.bottom;
    }
  }, [rows, cursor, list]);

  function onResizePointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    event.preventDefault();
    const handle = event.currentTarget;
    const section = sectionRef.current;
    if (!section) return;
    const startY = event.clientY;
    const startH = section.getBoundingClientRect().height;
    const tree = section.parentElement?.querySelector(".tree-host");
    const treeH = tree?.getBoundingClientRect().height ?? 0;
    const max = Math.max(MIN_HEIGHT, startH + treeH - MIN_TREE);
    const move = (ev: PointerEvent) => {
      const next = startH + (startY - ev.clientY);
      setHeight(Math.min(max, Math.max(MIN_HEIGHT, next)));
    };
    const up = () => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", up);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up);
    handle.setPointerCapture(event.pointerId);
  }

  return (
    <section className="call-stack" aria-label="Call stack" ref={sectionRef} style={{ height }}>
      <div
        className="stack-resize"
        role="separator"
        aria-orientation="horizontal"
        aria-label="Resize call stack"
        title="Drag to resize"
        tabIndex={0}
        onPointerDown={onResizePointerDown}
      />
      <div className="call-stack-head">
        <span className="call-stack-title">Call stack</span>
        <div className="stack-switch" role="radiogroup" aria-label="Which calls to list">
          <label className={list === "stack" ? "pressed" : ""}>
            <input
              type="radio"
              name="call-stack-list"
              value="stack"
              checked={list === "stack"}
              onChange={() => setList("stack")}
            />
            Stack
          </label>
          <label className={list === "all" ? "pressed" : ""}>
            <input
              type="radio"
              name="call-stack-list"
              value="all"
              checked={list === "all"}
              onChange={() => setList("all")}
            />
            All calls
          </label>
        </div>
      </div>
      {events.length === 0 ? (
        <p className="call-stack-empty">Run a function to see the call stack.</p>
      ) : (
        <div className="call-stack-body" ref={bodyRef}>
          <table>
            <thead>
              <tr>
                <th scope="col">Call</th>
                <th scope="col">Function</th>
                <th scope="col">Param</th>
                <th scope="col">Vars</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr
                  key={row.id}
                  ref={row.active ? activeRef : undefined}
                  className={[
                    row.active ? "is-active" : "",
                    row.returned ? "is-done" : "",
                    row.error ? "is-error" : "",
                  ]
                    .filter(Boolean)
                    .join(" ")}
                  aria-current={row.active ? "true" : undefined}
                  onClick={() => onJump(row.callCursor)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" || event.key === " ") {
                      event.preventDefault();
                      event.stopPropagation();
                      onJump(row.callCursor);
                    }
                  }}
                  tabIndex={0}
                >
                  <td className="call-num">{row.id}</td>
                  <td className="call-name">
                    {row.name}
                    {row.returned && row.returnValue != null && (
                      <span className="call-return"> → {row.returnValue}</span>
                    )}
                  </td>
                  <td>{row.param}</td>
                  <td>{row.vars}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
