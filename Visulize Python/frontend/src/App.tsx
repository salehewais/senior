import { useRef, useState } from "react";
import { trace } from "./api";
import { CodePane } from "./components/CodePane";
import { Diagram } from "./components/Diagram";
import { Examples } from "./components/Examples";
import { RelationGraph } from "./components/RelationGraph";
import { Stepper } from "./components/Stepper";
import type { Example } from "./examples";
import type { Step, TraceError } from "./types";

const STARTER = 'print("hello world")\n';

export default function App() {
  const request = useRef(0);
  const [code, setCode] = useState(STARTER);
  const [stdin, setStdin] = useState("");
  const [steps, setSteps] = useState<Step[]>([]);
  const [index, setIndex] = useState(0);
  const [stopped, setStopped] = useState<"step_limit" | "timeout" | null>(null);
  const [error, setError] = useState<TraceError | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [pane, setPane] = useState<"graph" | "frames">("graph");
  const [traceId, setTraceId] = useState(0);

  function resetTrace() {
    request.current += 1;
    setSteps([]);
    setIndex(0);
    setStopped(null);
    setError(null);
    setStatus(null);
    setLoading(false);
  }

  async function visualize(nextCode = code, nextStdin = stdin) {
    const id = ++request.current;
    setLoading(true);
    setStatus(null);
    setPane("graph");
    try {
      const result = await trace(nextCode, nextStdin);
      if (id !== request.current) return;
      setSteps(result.steps);
      setTraceId((current) => current + 1);
      setIndex(result.steps.length > 0 ? result.steps.length - 1 : 0);
      setStopped(result.stopped);
      setError(result.error ?? null);
    } catch (err) {
      if (id !== request.current) return;
      setSteps([]);
      setIndex(0);
      setError(null);
      setStopped(null);
      setStatus(err instanceof Error ? err.message : "The visualizer could not run that code.");
    } finally {
      if (id === request.current) setLoading(false);
    }
  }

  function loadExample(example: Example) {
    setCode(example.code);
    setStdin(example.stdin);
    void visualize(example.code, example.stdin);
  }

  const step = steps[index] ?? null;
  const nextLine = step?.line ?? error?.line ?? null;
  const previousLine = index > 0 ? steps[index - 1].line : null;
  const justLine = previousLine != null && previousLine !== nextLine ? previousLine : null;

  return (
    <div className="page">
      <header className="top">
        <div>
          <h1>Python visualizer</h1>
          <p>Step through frames and objects. Arrows show which names point at the same object.</p>
        </div>
        <button className="primary" type="button" onClick={() => void visualize()} disabled={loading}>
          {loading ? "Running…" : "Visualize"}
        </button>
      </header>
      <Examples code={code} onPick={loadExample} />
      <div className="workspace">
        <section className="left">
          <CodePane
            code={code}
            nextLine={nextLine}
            justLine={justLine}
            onChange={(next) => {
              setCode(next);
              if (steps.length > 0 || error) resetTrace();
            }}
          />
          <Stepper count={steps.length} index={index} stopped={stopped} onChange={setIndex} />
          {steps.length > 0 && (
            <div className="legend">
              <span>
                <i className="swatch just" /> line that has just executed
              </span>
              <span>
                <i className="swatch next" /> next line to execute
              </span>
            </div>
          )}
          <label className="stdin">
            <span>stdin</span>
            <textarea
              value={stdin}
              spellCheck={false}
              rows={2}
              aria-label="stdin"
              onChange={(event) => {
                setStdin(event.target.value);
                if (steps.length > 0 || error) resetTrace();
              }}
            />
          </label>
          {status && <p className="exception">{status}</p>}
          {error && (
            <div className="exception">
              {error.type}
              {error.line != null ? ` on line ${error.line}` : ""}: {error.message}
            </div>
          )}
          <div className="output">
            <div className="output-label">Program output</div>
            <pre>{step?.stdout || ""}</pre>
          </div>
        </section>
        <section className={pane === "graph" ? "right pane-graph" : "right"}>
          <div className="view-switch" role="tablist" aria-label="Diagram view">
            <button type="button" role="tab" aria-selected={pane === "frames"} onClick={() => setPane("frames")}>
              Frames
            </button>
            <button type="button" role="tab" aria-selected={pane === "graph"} onClick={() => setPane("graph")}>
              Graph
            </button>
          </div>
          {pane === "frames" ? <Diagram step={step} /> : <RelationGraph step={step} traceId={traceId} />}
        </section>
      </div>
    </div>
  );
}
