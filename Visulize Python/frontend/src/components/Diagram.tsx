import { useLayoutEffect, useRef, useState } from "react";
import { frameViews, objectView, routeArrows, type Point, type Rect, type RouteEdge } from "../graphLayout";
import type { Step } from "../types";
import { FrameTable, ObjectBox } from "./Cards";

export function Diagram({ step }: { step: Step | null }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width: 0, height: 0 });
  const [arrows, setArrows] = useState<{ id: string; d: string }[]>([]);

  useLayoutEffect(() => {
    const container = containerRef.current;
    if (!container || !step) return;

    function draw() {
      const node = containerRef.current;
      if (!node) return;
      const origin = node.getBoundingClientRect();
      const targets = new Map<string, { box: Rect; el: HTMLElement }>();
      node.querySelectorAll<HTMLElement>("[data-to]").forEach((el) => {
        const id = el.dataset.to;
        if (!id) return;
        const rect = el.getBoundingClientRect();
        targets.set(id, {
          el,
          box: { x: rect.left - origin.left, y: rect.top - origin.top, w: rect.width, h: rect.height },
        });
      });

      const edges: RouteEdge[] = [];
      node.querySelectorAll<HTMLElement>("[data-port]").forEach((source) => {
        const id = source.dataset.from;
        const target = id ? targets.get(id) : undefined;
        if (!target) return;
        const from = source.getBoundingClientRect();
        const card = source.closest<HTMLElement>("[data-to], .frame-table");
        const cardRect = (card ?? source).getBoundingClientRect();
        const sourcePoint: Point = {
          x: from.right - origin.left,
          y: from.top + from.height / 2 - origin.top,
        };
        edges.push({
          id: source.dataset.port ?? id ?? "port",
          targetId: id ?? "object",
          source: sourcePoint,
          sourceBox: {
            x: cardRect.left - origin.left,
            y: cardRect.top - origin.top,
            w: cardRect.width,
            h: cardRect.height,
          },
          targetBox: target.box,
          self: target.el.contains(source),
        });
      });

      const routed = routeArrows(edges);
      const width = node.clientWidth;
      const height = node.clientHeight;
      setArrows((current) =>
        current.length === routed.arrows.length && current.every((item, index) => item.d === routed.arrows[index]?.d && item.id === routed.arrows[index]?.id)
          ? current
          : routed.arrows,
      );
      setSize((current) => (current.width === width && current.height === height ? current : { width, height }));
    }

    draw();
    const observer = new ResizeObserver(draw);
    observer.observe(container);
    window.addEventListener("resize", draw);
    return () => {
      observer.disconnect();
      window.removeEventListener("resize", draw);
    };
  }, [step]);

  if (!step) {
    return <p className="placeholder">Visualize a program to see frames and objects.</p>;
  }

  const frames = frameViews(step);
  const heapEntries = Object.entries(step.heap);

  return (
    <div className="diagram-wrap">
      {step.exception && (
        <div className="exception">
          {step.exception.type}: {step.exception.message}
        </div>
      )}
      <div className="diagram" ref={containerRef}>
        <svg
          className="arrow-layer"
          aria-hidden="true"
          viewBox={`0 0 ${Math.max(1, size.width)} ${Math.max(1, size.height)}`}
          width={Math.max(1, size.width)}
          height={Math.max(1, size.height)}
        >
          <defs>
            <marker id="frames-arrow-head" viewBox="0 0 8 8" refX="8" refY="4" markerWidth="8" markerHeight="8" orient="auto">
              <path d="M0,0 L8,4 L0,8 z" />
            </marker>
          </defs>
          {arrows.map((arrow) => (
            <path key={arrow.id} d={arrow.d} markerEnd="url(#frames-arrow-head)" />
          ))}
        </svg>
        <div className="frames-col">
          <h2>Frames</h2>
          {frames.map((frame) => (
            <FrameTable key={frame.id} frame={frame} />
          ))}
        </div>
        <div className="objects-col">
          <h2>Objects</h2>
          {heapEntries.length === 0 && <p className="muted">No objects on this step.</p>}
          {heapEntries.map(([id, object]) => (
            <ObjectBox key={id} view={objectView(id, object)} />
          ))}
        </div>
      </div>
    </div>
  );
}
