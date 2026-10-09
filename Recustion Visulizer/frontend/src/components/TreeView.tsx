import { useEffect, useMemo, useRef, useState } from "react";
import { NODE_H, buildTree, fitTransform, frameTree, layoutTree, type PlacedNode } from "../layout";
import type { TraceEvent } from "../types";

type Props = {
  events: TraceEvent[];
  cursor: number;
  error: string | null;
  truncated: boolean;
  timedOut: boolean;
  traceKey: number;
  call: string;
};

type View = { x: number; y: number; k: number };

export default function TreeView({
  events,
  cursor,
  error,
  truncated,
  timedOut,
  traceKey,
  call,
}: Props) {
  const hostRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 800, h: 600 });
  const [view, setView] = useState<View>({ x: 40, y: 48, k: 1 });
  const userMoved = useRef(false);
  const drag = useRef<{ px: number; py: number; x: number; y: number } | null>(null);

  const placed = useMemo(() => {
    const root = buildTree(events.slice(0, cursor));
    if (!root) return [];
    return layoutTree(root);
  }, [events, cursor]);

  useEffect(() => {
    const el = hostRef.current;
    if (!el) return;
    const observer = new ResizeObserver(() => {
      setSize({ w: el.clientWidth, h: el.clientHeight });
    });
    observer.observe(el);
    setSize({ w: el.clientWidth, h: el.clientHeight });
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    userMoved.current = false;
  }, [traceKey]);

  useEffect(() => {
    if (userMoved.current || placed.length === 0 || size.w < 20) return;
    const focusId = cursor > 0 ? events[cursor - 1]?.id ?? null : null;
    setView(frameTree(placed, focusId, size.w, size.h));
  }, [placed, cursor, events, size, traceKey]);

  useEffect(() => {
    const el = hostRef.current;
    if (!el) return;
    const onWheel = (event: WheelEvent) => {
      event.preventDefault();
      userMoved.current = true;
      const rect = el.getBoundingClientRect();
      const px = event.clientX - rect.left;
      const py = event.clientY - rect.top;
      const factor = event.deltaY < 0 ? 1.08 : 1 / 1.08;
      setView((current) => {
        const k = clamp(current.k * factor, 0.12, 2.8);
        const ratio = k / current.k;
        return {
          k,
          x: px - (px - current.x) * ratio,
          y: py - (py - current.y) * ratio,
        };
      });
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, []);

  const byId = useMemo(() => new Map(placed.map((node) => [node.id, node])), [placed]);
  const focus = cursor > 0 ? events[cursor - 1] : null;
  const notices = [
    truncated ? "Stopped after 400 calls, so this tree is incomplete." : null,
    timedOut ? "Stopped after 2 seconds, so this tree may be incomplete." : null,
    error,
  ].filter((item): item is string => Boolean(item));

  function zoomBy(factor: number) {
    userMoved.current = true;
    setView((current) => {
      const k = clamp(current.k * factor, 0.12, 2.8);
      const cx = size.w / 2;
      const cy = size.h / 2;
      const ratio = k / current.k;
      return {
        k,
        x: cx - (cx - current.x) * ratio,
        y: cy - (cy - current.y) * ratio,
      };
    });
  }

  return (
    <div
      className="tree-host"
      ref={hostRef}
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        drag.current = { px: event.clientX, py: event.clientY, x: view.x, y: view.y };
        event.currentTarget.setPointerCapture(event.pointerId);
      }}
      onPointerMove={(event) => {
        const start = drag.current;
        if (!start) return;
        userMoved.current = true;
        setView((current) => ({
          ...current,
          x: start.x + event.clientX - start.px,
          y: start.y + event.clientY - start.py,
        }));
      }}
      onPointerUp={() => {
        drag.current = null;
      }}
      onDoubleClick={() => {
        userMoved.current = true;
        setView(fitTransform(placed, size.w, size.h));
      }}
    >
      {notices.length > 0 && (
        <div className="notices">
          {notices.map((notice) => (
            <p key={notice} className={notice === error ? "notice error" : "notice"}>
              {notice}
            </p>
          ))}
        </div>
      )}

      {events.length === 0 && !error && (
        <div className="empty-tree">
          <p>Run a function to grow its call tree.</p>
          <p className="empty-hint">Nodes show the call. Edges show the returned value.</p>
        </div>
      )}

      {events.length > 0 && cursor === 0 && (
        <div className="empty-tree subtle">
          <p>Press play or step forward.</p>
        </div>
      )}

      <svg className="tree-svg" role="img" aria-label="Recursion tree">
        <g transform={`translate(${view.x} ${view.y}) scale(${view.k})`}>
          {placed.map((node) => {
            if (node.parentId == null) return null;
            const parent = byId.get(node.parentId);
            if (!parent) return null;
            const y1 = parent.y + NODE_H / 2;
            const y2 = node.y - NODE_H / 2;
            const showValue = node.returnIndex !== null;
            const onStack = !showValue;
            return (
              <g key={`link-${node.id}`}>
                <path
                  d={curve(parent.x, y1, node.x, y2)}
                  className={onStack ? "edge edge-stack" : "edge"}
                />
                {showValue && node.value !== null && (
                  <EdgeLabel
                    x={parent.x + (node.x - parent.x) * 0.55}
                    y={y1 + (y2 - y1) * 0.62}
                    value={node.value}
                    error={node.error}
                  />
                )}
              </g>
            );
          })}
          {placed.map((node) => (
            <TreeNodeView key={node.id} node={node} focusId={focus?.id ?? null} focusType={focus?.type ?? null} />
          ))}
        </g>
      </svg>

      {call.trim() && events.length > 0 && <div className="tree-call">{call.trim()}</div>}

      <div className="zoom-controls">
        <button type="button" aria-label="Zoom in" onClick={() => zoomBy(1.15)}>
          +
        </button>
        <button type="button" aria-label="Zoom out" onClick={() => zoomBy(1 / 1.15)}>
          −
        </button>
        <button
          type="button"
          aria-label="Fit"
          onClick={() => {
            userMoved.current = true;
            setView(fitTransform(placed, size.w, size.h));
          }}
        >
          Fit
        </button>
      </div>
    </div>
  );
}

function TreeNodeView({
  node,
  focusId,
  focusType,
}: {
  node: PlacedNode;
  focusId: number | null;
  focusType: "call" | "return" | "line" | null;
}) {
  const returned = node.returnIndex !== null;
  const focused = focusId === node.id;
  const className = [
    "node",
    focused && (focusType === "call" || focusType === "line") ? "node-current" : "",
    focused && focusType === "return" ? "node-returned-now" : "",
    !focused && !returned ? "node-stack" : "",
    !focused && returned ? "node-done" : "",
    node.error && returned ? "node-error" : "",
  ]
    .filter(Boolean)
    .join(" ");
  const showRootValue = node.parentId == null && returned && node.value !== null;

  return (
    <g className={className} transform={`translate(${node.x} ${node.y})`}>
      {showRootValue && (
        <g className={node.error ? "root-value error" : "root-value"} transform={`translate(0 ${-NODE_H / 2 - 18})`}>
          <rect width={labelWidth(node.value!)} height={20} x={-labelWidth(node.value!) / 2} y={-10} rx={10} />
          <text>{shortValue(node.value!)}</text>
        </g>
      )}
      <rect width={node.width} height={NODE_H} x={-node.width / 2} y={-NODE_H / 2} rx={9} />
      <text>{node.label}</text>
      <title>{node.label}</title>
    </g>
  );
}

function EdgeLabel({
  x,
  y,
  value,
  error,
}: {
  x: number;
  y: number;
  value: string;
  error: boolean;
}) {
  const text = shortValue(value);
  const width = labelWidth(text);
  return (
    <g className={error ? "edge-label error" : "edge-label"} transform={`translate(${x} ${y})`}>
      <rect width={width} height={20} x={-width / 2} y={-10} rx={10} />
      <text>{text}</text>
      <title>{value}</title>
    </g>
  );
}

function shortValue(value: string): string {
  return value.length > 28 ? `${value.slice(0, 27)}…` : value;
}

function labelWidth(value: string): number {
  return Math.max(28, Math.ceil(shortValue(value).length * 7.2 + 16));
}

function curve(x1: number, y1: number, x2: number, y2: number): string {
  const mid = (y1 + y2) / 2;
  return `M${x1},${y1}C${x1},${mid} ${x2},${mid} ${x2},${y2}`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
