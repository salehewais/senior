import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  buildRelationGraph,
  fitTransform,
  placeGraph,
  type Bounds,
  type BoxSize,
  type DrawnArrow,
} from "../graphLayout";
import type { Step } from "../types";
import { FrameTable, ObjectBox } from "./Cards";

type View = { x: number; y: number; k: number };

const EMPTY_BOUNDS: Bounds = { minX: 0, minY: 0, maxX: 1, maxY: 1 };

export function RelationGraph({ step, traceId }: { step: Step | null; traceId: number }) {
  const hostRef = useRef<HTMLDivElement>(null);
  const sceneRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ w: 800, h: 640 });
  const [view, setView] = useState<View>({ x: 40, y: 48, k: 1 });
  const [sizes, setSizes] = useState<Record<string, BoxSize> | null>(null);
  const userMoved = useRef(false);
  const drag = useRef<{ px: number; py: number; x: number; y: number } | null>(null);

  const model = useMemo(() => (step ? buildRelationGraph(step) : null), [step]);
  const placement = useMemo(() => (model && sizes ? placeGraph(model, sizes) : null), [model, sizes]);

  useLayoutEffect(() => {
    const root = sceneRef.current;
    if (!root || !model) return;

    function measure() {
      const scene = sceneRef.current;
      if (!scene) return;
      const next: Record<string, BoxSize> = {};
      scene.querySelectorAll<HTMLElement>("[data-node]").forEach((card) => {
        const id = card.dataset.node;
        if (!id) return;
        const scale = card.offsetWidth > 0 ? card.getBoundingClientRect().width / card.offsetWidth : 1;
        const cardRect = card.getBoundingClientRect();
        const ports: Record<string, { x: number; y: number }> = {};
        card.querySelectorAll<HTMLElement>("[data-port]").forEach((port) => {
          const key = port.dataset.port;
          if (!key) return;
          const rect = port.getBoundingClientRect();
          ports[key] = {
            x: round((rect.right - cardRect.left) / scale),
            y: round((rect.top + rect.height / 2 - cardRect.top) / scale),
          };
        });
        next[id] = { w: round(card.offsetWidth), h: round(card.offsetHeight), ports };
      });
      setSizes((current) => (current && sameSizes(current, next) ? current : next));
    }

    measure();
    const observer = new ResizeObserver(measure);
    root.querySelectorAll<HTMLElement>("[data-node]").forEach((card) => observer.observe(card));
    return () => observer.disconnect();
  }, [model]);

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

  useLayoutEffect(() => {
    userMoved.current = false;
  }, [traceId]);

  useLayoutEffect(() => {
    if (userMoved.current || !placement || size.w < 20) return;
    setView(fitTransform(placement.bounds, size.w, size.h));
  }, [placement, size, traceId]);

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

  function fit() {
    if (!placement) return;
    userMoved.current = true;
    setView(fitTransform(placement.bounds, size.w, size.h));
  }

  const bounds = placement?.bounds ?? EMPTY_BOUNDS;
  const sceneW = Math.max(1, bounds.maxX - Math.min(0, bounds.minX));
  const sceneH = Math.max(1, bounds.maxY - Math.min(0, bounds.minY));

  return (
    <div
      className="graph-host"
      ref={hostRef}
      onPointerDown={(event) => {
        if (event.button !== 0) return;
        if ((event.target as HTMLElement).closest(".zoom-controls")) return;
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
      onDoubleClick={(event) => {
        if ((event.target as HTMLElement).closest(".zoom-controls")) return;
        fit();
      }}
    >
      {!step && <p className="placeholder graph-empty">Visualize a program to see how names and objects connect.</p>}
      {step?.exception && (
        <div className="exception graph-exception">
          {step.exception.type}: {step.exception.message}
        </div>
      )}
      {model && (
        <div
          className="graph-scene"
          ref={sceneRef}
          style={{
            transform: `translate(${view.x}px, ${view.y}px) scale(${view.k})`,
            transformOrigin: "0 0",
            visibility: placement ? "visible" : "hidden",
          }}
        >
          <svg className="arrow-layer graph-arrows" aria-hidden="true" width={sceneW} height={sceneH}>
            <defs>
              <marker id="graph-arrow-head" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="8" markerHeight="8" orient="auto">
                <path d="M0,0 L8,4 L0,8 z" />
              </marker>
            </defs>
            {(placement?.arrows ?? []).map((arrow) => (
              <ArrowPath key={arrow.id} arrow={arrow} />
            ))}
          </svg>
          {model.nodes.map((node) => {
            const placed = placement?.nodes.find((item) => item.id === node.id);
            return (
              <div
                key={node.id}
                className="graph-node"
                data-node={node.id}
                style={{ left: placed?.x ?? 0, top: placed?.y ?? 0 }}
              >
                {node.frame && <FrameTable frame={node.frame} />}
                {node.objectView && <ObjectBox view={node.objectView} />}
              </div>
            );
          })}
        </div>
      )}
      {step && (
        <div className="zoom-controls">
          <button type="button" aria-label="Zoom in" onClick={() => zoomBy(1.15)}>
            +
          </button>
          <button type="button" aria-label="Zoom out" onClick={() => zoomBy(1 / 1.15)}>
            −
          </button>
          <button type="button" aria-label="Fit" onClick={fit}>
            Fit
          </button>
        </div>
      )}
    </div>
  );
}

function ArrowPath({ arrow }: { arrow: DrawnArrow }) {
  return <path d={arrow.d} markerEnd="url(#graph-arrow-head)" />;
}

function sameSizes(current: Record<string, BoxSize>, next: Record<string, BoxSize>): boolean {
  const currentKeys = Object.keys(current);
  const nextKeys = Object.keys(next);
  if (currentKeys.length !== nextKeys.length) return false;
  for (const key of nextKeys) {
    const a = current[key];
    const b = next[key];
    if (!a || a.w !== b.w || a.h !== b.h) return false;
    const ports = Object.keys(b.ports);
    if (ports.length !== Object.keys(a.ports).length) return false;
    for (const port of ports) {
      if (!a.ports[port] || a.ports[port].x !== b.ports[port].x || a.ports[port].y !== b.ports[port].y) return false;
    }
  }
  return true;
}

function round(value: number): number {
  return Math.round(value * 10) / 10;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}
