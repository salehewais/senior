import { useState, type PointerEvent as ReactPointerEvent } from "react";
import type { LoopFrame } from "../types";

const DEFAULT_WIDTH = 280;
const DEFAULT_HEIGHT = 280;
const MIN_WIDTH = 200;
const MIN_HEIGHT = 140;
const PANEL_MIN_VISIBLE = 48;

type Pos = { x: number; y: number };
type Size = { width: number; height: number };

type Props = {
  open: boolean;
  loops: LoopFrame[] | null;
  onClose: () => void;
};

function clampPos(x: number, y: number, width: number): Pos {
  const maxX = Math.max(0, window.innerWidth - PANEL_MIN_VISIBLE);
  const maxY = Math.max(0, window.innerHeight - PANEL_MIN_VISIBLE);
  return {
    x: Math.min(maxX, Math.max(-(width - PANEL_MIN_VISIBLE), x)),
    y: Math.min(maxY, Math.max(0, y)),
  };
}

function clampSize(width: number, height: number, x: number, y: number): Size {
  const maxWidth = Math.max(MIN_WIDTH, window.innerWidth - Math.max(0, x) - 8);
  const maxHeight = Math.max(MIN_HEIGHT, window.innerHeight - Math.max(0, y) - 8);
  return {
    width: Math.min(maxWidth, Math.max(MIN_WIDTH, width)),
    height: Math.min(maxHeight, Math.max(MIN_HEIGHT, height)),
  };
}

function defaultPos(): Pos {
  return {
    x: Math.max(16, window.innerWidth - DEFAULT_WIDTH - 24),
    y: Math.max(72, window.innerHeight - DEFAULT_HEIGHT - 40),
  };
}

export default function LoopPanel({ open, loops, onClose }: Props) {
  const [pos, setPos] = useState<Pos>(defaultPos);
  const [size, setSize] = useState<Size>({ width: DEFAULT_WIDTH, height: DEFAULT_HEIGHT });

  if (!open) return null;

  function onDragPointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    event.preventDefault();
    const handle = event.currentTarget;
    const startX = event.clientX;
    const startY = event.clientY;
    const origin = { ...pos };
    const width = size.width;

    const move = (ev: PointerEvent) => {
      setPos(clampPos(origin.x + (ev.clientX - startX), origin.y + (ev.clientY - startY), width));
    };
    const up = () => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", up);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up);
    handle.setPointerCapture(event.pointerId);
  }

  function onResizePointerDown(event: ReactPointerEvent<HTMLDivElement>) {
    if (event.button !== 0) return;
    event.preventDefault();
    event.stopPropagation();
    const handle = event.currentTarget;
    const startX = event.clientX;
    const startY = event.clientY;
    const origin = { ...size };
    const originPos = { ...pos };

    const move = (ev: PointerEvent) => {
      setSize(
        clampSize(
          origin.width + (ev.clientX - startX),
          origin.height + (ev.clientY - startY),
          originPos.x,
          originPos.y,
        ),
      );
    };
    const up = () => {
      handle.removeEventListener("pointermove", move);
      handle.removeEventListener("pointerup", up);
    };
    handle.addEventListener("pointermove", move);
    handle.addEventListener("pointerup", up);
    handle.setPointerCapture(event.pointerId);
  }

  const frames = loops ?? [];

  return (
    <div
      className="loop-panel"
      style={{ left: pos.x, top: pos.y, width: size.width, height: size.height }}
      role="dialog"
      aria-label="Loops"
    >
      <div className="loop-panel-head" onPointerDown={onDragPointerDown}>
        <span className="loop-panel-title">Loops</span>
        <button type="button" className="loop-panel-close" onClick={onClose} aria-label="Close loops panel">
          ×
        </button>
      </div>
      {frames.length === 0 ? (
        <p className="loop-panel-empty">Not inside a loop</p>
      ) : (
        <ul className="loop-panel-list">
          {frames.map((frame, index) => (
            <li key={`${frame.kind}-${index}`} className="loop-panel-item">
              <span className="loop-panel-badge">{frame.kind}</span>
              {frame.kind === "for" ? (
                <dl className="loop-panel-fields">
                  <div>
                    <dt>Start</dt>
                    <dd>{frame.start ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>End</dt>
                    <dd>{frame.end ?? "—"}</dd>
                  </div>
                  <div>
                    <dt>Index</dt>
                    <dd>{frame.index ?? "—"}</dd>
                  </div>
                  {frame.value != null ? (
                    <div>
                      <dt>Value</dt>
                      <dd>{frame.value}</dd>
                    </div>
                  ) : null}
                </dl>
              ) : (
                <dl className="loop-panel-fields">
                  <div>
                    <dt>Condition</dt>
                    <dd>
                      {frame.condition == null
                        ? "—"
                        : frame.conditionValue != null
                          ? `${frame.condition} → ${frame.conditionValue}`
                          : frame.condition}
                    </dd>
                  </div>
                </dl>
              )}
            </li>
          ))}
        </ul>
      )}
      <div
        className="loop-panel-resize"
        role="separator"
        aria-label="Resize loops panel"
        title="Drag to resize"
        onPointerDown={onResizePointerDown}
      />
    </div>
  );
}
