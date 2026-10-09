import type { TraceEvent } from "../types";

type Props = {
  events: TraceEvent[];
  cursor: number;
  playing: boolean;
  speed: number;
  result: string | null;
  onTogglePlay: () => void;
  onStep: (delta: number) => void;
  onJump: (cursor: number) => void;
  onSpeed: (speed: number) => void;
};

const SLOW = 900;
const FAST = 50;

function describe(events: TraceEvent[], cursor: number): string {
  if (events.length === 0) return "Run a function to build its call tree";
  if (cursor <= 0) return "At the start";
  const event = events[cursor - 1];
  if (event.type === "call") {
    return `Called ${event.name}(${event.args.join(", ")})`;
  }
  const call = events.find((item) => item.type === "call" && item.id === event.id);
  const label = call && call.type === "call" ? `${call.name}(${call.args.join(", ")})` : null;
  if (event.type === "line") {
    return `Line ${event.line} in ${label ?? "the call"}`;
  }
  const name = label ?? "The call";
  if (event.error) return `${name} raised`;
  return `${name} returned ${event.value}`;
}

export default function PlaybackBar({
  events,
  cursor,
  playing,
  speed,
  result,
  onTogglePlay,
  onStep,
  onJump,
  onSpeed,
}: Props) {
  const total = events.length;
  const disabled = total === 0;
  const slider = Math.round(((SLOW - speed) / (SLOW - FAST)) * 100);

  return (
    <div className="playback">
      <div className="transport">
        <button
          type="button"
          aria-label="Restart"
          title="Restart"
          disabled={disabled}
          onClick={() => onJump(0)}
        >
          <RestartIcon />
        </button>
        <button
          type="button"
          aria-label="Step back"
          title="Step back"
          disabled={disabled || cursor === 0}
          onClick={() => onStep(-1)}
        >
          <StepBackIcon />
        </button>
        <button
          type="button"
          className="play"
          aria-label={playing ? "Pause" : "Play"}
          title={playing ? "Pause" : "Play"}
          disabled={disabled}
          onClick={onTogglePlay}
        >
          {playing ? <PauseIcon /> : <PlayIcon />}
        </button>
        <button
          type="button"
          aria-label="Step forward"
          title="Step forward"
          disabled={disabled || cursor >= total}
          onClick={() => onStep(1)}
        >
          <StepForwardIcon />
        </button>
        <button
          type="button"
          aria-label="Jump to end"
          title="Jump to end"
          disabled={disabled}
          onClick={() => onJump(total)}
        >
          <EndIcon />
        </button>
      </div>

      <p className="step-caption">{describe(events, cursor)}</p>

      <div className="playback-meta">
        <label className="speed">
          <span>Slow</span>
          <input
            type="range"
            min={0}
            max={100}
            aria-label="Playback speed"
            disabled={disabled}
            value={slider}
            onChange={(event) => {
              const next = Number(event.target.value);
              onSpeed(Math.round(SLOW - (next / 100) * (SLOW - FAST)));
            }}
          />
          <span>Fast</span>
        </label>
        <span className="counter">
          {cursor}/{total}
        </span>
        <span className="result">
          <span>Result</span>
          <strong>{result ?? "—"}</strong>
        </span>
      </div>
    </div>
  );
}

function PlayIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M4 2.5v11l10-5.5z" />
    </svg>
  );
}

function PauseIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M3 2h3.2v12H3zM9.8 2H13v12H9.8z" />
    </svg>
  );
}

function StepBackIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M4 2h2v12H4zM13 2.5v11L6 8z" />
    </svg>
  );
}

function StepForwardIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M3 2.5v11L10 8zM10 2h2v12h-2z" />
    </svg>
  );
}

function RestartIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M3 3h7v2H5v3H3z" />
      <path d="M8 4a5 5 0 1 1-4.3 7.5l1.7-.9A3.2 3.2 0 1 0 8 5.6V4z" />
    </svg>
  );
}

function EndIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="M2 3.2v9.6L7.2 8zM8 3.2v9.6L13.2 8z" />
    </svg>
  );
}
