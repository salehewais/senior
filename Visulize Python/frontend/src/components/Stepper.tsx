import { useEffect } from "react";

interface StepperProps {
  count: number;
  index: number;
  stopped: "step_limit" | "timeout" | null;
  onChange: (index: number) => void;
}

const STOP_TEXT = {
  step_limit: "Stopped at the step limit",
  timeout: "Stopped at the time limit",
} as const;

export function Stepper({ count, index, stopped, onChange }: StepperProps) {
  const atStart = count === 0 || index <= 0;
  const atEnd = count === 0 || index >= count - 1;
  const finished = count > 0 && index === count - 1 && !stopped;
  const label = count === 0 ? "" : stopped ? STOP_TEXT[stopped] : finished ? "Program terminated" : `Step ${index + 1} of ${count}`;

  useEffect(() => {
    function onKey(eventKey: KeyboardEvent) {
      const target = eventKey.target;
      if (target instanceof HTMLElement) {
        const tag = target.tagName;
        if (tag === "TEXTAREA" || tag === "INPUT") return;
      }
      if (eventKey.key === "ArrowRight" && index < count - 1) onChange(index + 1);
      if (eventKey.key === "ArrowLeft" && index > 0) onChange(index - 1);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [count, index, onChange]);

  return (
    <div className="stepper">
      <div className="stepper-buttons">
        <button type="button" onClick={() => onChange(0)} disabled={atStart}>
          {"<< First"}
        </button>
        <button type="button" onClick={() => onChange(index - 1)} disabled={atStart}>
          {"< Back"}
        </button>
        <button type="button" onClick={() => onChange(index + 1)} disabled={atEnd}>
          {"Forward >"}
        </button>
        <button type="button" onClick={() => onChange(Math.max(count - 1, 0))} disabled={atEnd}>
          {"Last >>"}
        </button>
      </div>
      <label className="stepper-track">
        <span className="step-status">{label}</span>
        <input
          type="range"
          min={0}
          max={Math.max(count - 1, 0)}
          value={count === 0 ? 0 : index}
          disabled={count === 0}
          aria-label="Execution step"
          onChange={(change) => onChange(Number(change.target.value))}
        />
      </label>
    </div>
  );
}
