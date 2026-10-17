import { useEffect, useRef } from "react";

const LINE_HEIGHT = 22;
const PAD = 10;

interface CodePaneProps {
  code: string;
  nextLine: number | null;
  justLine: number | null;
  onChange: (code: string) => void;
}

export function CodePane({ code, nextLine, justLine, onChange }: CodePaneProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const lines = code.split("\n");
  const focusLine = nextLine ?? justLine;
  const contentHeight = Math.max(lines.length, 8) * LINE_HEIGHT + PAD * 2;
  const contentWidth = `${Math.max(...lines.map((line) => line.length), 24) + 2}ch`;

  useEffect(() => {
    const editor = editorRef.current;
    if (!editor || focusLine == null) return;
    const top = PAD + (focusLine - 1) * LINE_HEIGHT;
    const visible = top >= editor.scrollTop && top <= editor.scrollTop + editor.clientHeight - LINE_HEIGHT;
    if (!visible) {
      editor.scrollTop = Math.max(0, top - editor.clientHeight / 3);
    }
  }, [focusLine]);

  function mark(line: number) {
    if (line === nextLine) return "gutter-line next";
    if (line === justLine) return "gutter-line just";
    return "gutter-line";
  }

  return (
    <div className="editor" ref={editorRef}>
      <div className="editor-inner" style={{ minHeight: contentHeight }}>
        <div className="gutter" aria-hidden="true">
          {lines.map((_, index) => {
            const line = index + 1;
            return (
              <div key={line} className={mark(line)}>
                {line}
              </div>
            );
          })}
        </div>
        <div className="code-col" style={{ minWidth: contentWidth }}>
          {justLine != null && justLine !== nextLine && justLine >= 1 && justLine <= lines.length && (
            <div className="line-highlight just" style={{ top: PAD + (justLine - 1) * LINE_HEIGHT }} />
          )}
          {nextLine != null && nextLine >= 1 && nextLine <= lines.length && (
            <div className="line-highlight next" style={{ top: PAD + (nextLine - 1) * LINE_HEIGHT }} />
          )}
          <textarea
            className="code"
            value={code}
            spellCheck={false}
            wrap="off"
            aria-label="Python code"
            style={{ height: contentHeight }}
            onChange={(event) => onChange(event.target.value)}
            onKeyDown={(event) => {
              if (event.key !== "Tab") return;
              event.preventDefault();
              const el = event.currentTarget;
              const start = el.selectionStart;
              const end = el.selectionEnd;
              const next = code.slice(0, start) + "    " + code.slice(end);
              onChange(next);
              requestAnimationFrame(() => {
                el.selectionStart = el.selectionEnd = start + 4;
              });
            }}
          />
        </div>
      </div>
    </div>
  );
}
