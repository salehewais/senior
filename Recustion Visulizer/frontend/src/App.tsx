import { useCallback, useEffect, useRef, useState } from "react";
import { fetchExamples, traceSource } from "./api";
import EditorPane from "./components/EditorPane";
import PlaybackBar from "./components/PlaybackBar";
import TreeView from "./components/TreeView";
import type { Example, TraceEvent } from "./types";

type Mode = "visualize" | "debug";

export default function App() {
  const [examples, setExamples] = useState<Example[]>([]);
  const [exampleId, setExampleId] = useState("");
  const [source, setSource] = useState("");
  const [call, setCall] = useState("fib(5)");
  const [fontSize, setFontSize] = useState(14);
  const [wrap, setWrap] = useState(true);
  const [editorWidth, setEditorWidth] = useState(480);
  const [events, setEvents] = useState<TraceEvent[]>([]);
  const [cursor, setCursor] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(320);
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [truncated, setTruncated] = useState(false);
  const [timedOut, setTimedOut] = useState(false);
  const [traceKey, setTraceKey] = useState(0);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [mode, setMode] = useState<Mode>("visualize");
  const [tracedMode, setTracedMode] = useState<Mode | null>(null);
  const runningRef = useRef(false);

  useEffect(() => {
    let cancelled = false;
    fetchExamples()
      .then((items) => {
        if (cancelled) return;
        setExamples(items);
        const first = items[0];
        if (first) {
          setExampleId(first.id);
          setSource(first.source);
          setCall(first.call);
        }
      })
      .catch(() => {
        if (!cancelled) setLoadError("Could not load examples. Is the API running on port 8000?");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const run = useCallback(async () => {
    if (runningRef.current) return;
    runningRef.current = true;
    setRunning(true);
    setPlaying(false);
    setError(null);
    try {
      const data = await traceSource(source, call, mode === "debug");
      setEvents(data.events);
      setCursor(data.events.length);
      setResult(data.result);
      setError(data.error);
      setTruncated(data.truncated);
      setTimedOut(data.timed_out);
      setTracedMode(mode);
      setTraceKey((key) => key + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The run failed.");
    } finally {
      runningRef.current = false;
      setRunning(false);
    }
  }, [call, mode, source]);

  useEffect(() => {
    if (!playing) return;
    if (cursor >= events.length) {
      setPlaying(false);
      return;
    }
    const timer = window.setTimeout(() => setCursor((current) => current + 1), speed);
    return () => window.clearTimeout(timer);
  }, [playing, cursor, events.length, speed]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.closest("input, textarea, select, .monaco-editor")) {
        return;
      }
      if (event.key === " ") {
        event.preventDefault();
        togglePlay();
      } else if (event.key === "ArrowRight") {
        event.preventDefault();
        step(1);
      } else if (event.key === "ArrowLeft") {
        event.preventDefault();
        step(-1);
      } else if (event.key === "Home") {
        event.preventDefault();
        jump(0);
      } else if (event.key === "End") {
        event.preventDefault();
        jump(events.length);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

  function togglePlay() {
    if (events.length === 0) return;
    if (playing) {
      setPlaying(false);
      return;
    }
    if (cursor >= events.length) setCursor(0);
    setPlaying(true);
  }

  function step(delta: number) {
    setPlaying(false);
    setCursor((current) => Math.min(events.length, Math.max(0, current + delta)));
  }

  function jump(next: number) {
    setPlaying(false);
    setCursor(Math.min(events.length, Math.max(0, next)));
  }

  function loadExample(id: string) {
    const example = examples.find((item) => item.id === id);
    if (!example) return;
    setExampleId(id);
    setSource(example.source);
    setCall(example.call);
    setPlaying(false);
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <Mark />
          <h1>Recursion Tree</h1>
        </div>
        <div className="top-actions">
          <label className="example-picker">
            <span>Example</span>
            <select
              aria-label="Examples"
              value={exampleId}
              onChange={(event) => loadExample(event.target.value)}
            >
              {examples.length === 0 && <option value="">Loading…</option>}
              {examples.map((example) => (
                <option key={example.id} value={example.id}>
                  {example.title}
                </option>
              ))}
            </select>
          </label>
          <div className="mode-switch" role="group" aria-label="Trace mode">
            <button
              type="button"
              className={mode === "visualize" ? "pressed" : ""}
              aria-pressed={mode === "visualize"}
              onClick={() => setMode("visualize")}
            >
              Visualize
            </button>
            <button
              type="button"
              className={mode === "debug" ? "pressed" : ""}
              aria-pressed={mode === "debug"}
              onClick={() => setMode("debug")}
            >
              Debug
            </button>
          </div>
          <button type="button" className="run" onClick={() => void run()} disabled={running || !source.trim()}>
            {running ? "Running…" : "Run"}
          </button>
        </div>
      </header>

      {loadError && <p className="load-error">{loadError}</p>}

      <div className="workspace">
        <div className="editor-slot" style={{ width: editorWidth }}>
          <EditorPane
            source={source}
            call={call}
            fontSize={fontSize}
            wrap={wrap}
            onSource={setSource}
            onCall={setCall}
            onFontSize={setFontSize}
            onWrap={setWrap}
            onRun={() => void run()}
            currentLine={currentLine(mode, events, cursor, running)}
          />
        </div>
        <div
          className="divider"
          role="separator"
          aria-orientation="vertical"
          aria-label="Resize editor"
          onPointerDown={(event) => {
            const startX = event.clientX;
            const startW = editorWidth;
            const target = event.currentTarget;
            target.setPointerCapture(event.pointerId);
            const move = (ev: PointerEvent) => {
              const next = startW + ev.clientX - startX;
              const max = Math.max(320, window.innerWidth - 280);
              setEditorWidth(Math.min(max, Math.max(280, next)));
            };
            const up = () => {
              target.removeEventListener("pointermove", move);
              target.removeEventListener("pointerup", up);
            };
            target.addEventListener("pointermove", move);
            target.addEventListener("pointerup", up);
          }}
        />
        <div className="stage">
          <TreeView
            events={events}
            cursor={cursor}
            error={error}
            truncated={truncated}
            timedOut={timedOut}
            traceKey={traceKey}
            call={call}
          />
          {mode === "debug" && (
            <VariablesStrip
              events={events}
              cursor={cursor}
              stale={events.length > 0 && tracedMode !== "debug"}
            />
          )}
          <PlaybackBar
            events={events}
            cursor={cursor}
            playing={playing}
            speed={speed}
            result={result}
            onTogglePlay={togglePlay}
            onStep={step}
            onJump={jump}
            onSpeed={setSpeed}
          />
        </div>
      </div>
    </div>
  );
}

function currentLine(mode: Mode, events: TraceEvent[], cursor: number, running: boolean): number | null {
  if (mode !== "debug" || running || cursor <= 0) return null;
  const event = events[cursor - 1];
  if (event.type === "line") return event.line;
  return event.line ?? null;
}

function VariablesStrip({
  events,
  cursor,
  stale,
}: {
  events: TraceEvent[];
  cursor: number;
  stale: boolean;
}) {
  if (stale) {
    return (
      <div className="variables">
        <p className="debug-note">Press Run again to step through lines.</p>
      </div>
    );
  }

  const current = cursor > 0 ? events[cursor - 1] : null;
  let locals: Record<string, string> | null = null;
  let changed: string[] = [];
  if (current) {
    for (let index = cursor - 1; index >= 0; index -= 1) {
      const event = events[index];
      if (event.type === "line" && event.id === current.id) {
        locals = event.locals;
        changed = event.changed;
        break;
      }
    }
  }
  const rows = locals ? Object.entries(locals) : [];

  return (
    <div className="variables" aria-label="Local variables">
      {rows.length === 0 ? (
        <p className="debug-note">Step to a line to see local variables.</p>
      ) : (
        rows.map(([name, value]) => (
          <div key={name} className={changed.includes(name) ? "var changed" : "var"}>
            <span className="var-name">{name}</span>
            <span className="var-value">{value}</span>
          </div>
        ))
      )}
    </div>
  );
}

function Mark() {
  return (
    <svg className="mark" viewBox="0 0 32 32" aria-hidden="true">
      <circle cx="16" cy="7" r="3.2" />
      <circle cx="7" cy="24" r="3.2" />
      <circle cx="25" cy="24" r="3.2" />
      <path d="M16 10.2 L7 20.6 M16 10.2 L25 20.6" />
    </svg>
  );
}
