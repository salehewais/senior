import Editor, { type OnMount } from "@monaco-editor/react";
import { useEffect, useRef, useState } from "react";
import type * as Monaco from "monaco-editor";

type Props = {
  source: string;
  call: string;
  fontSize: number;
  wrap: boolean;
  currentLine: number | null;
  onSource: (source: string) => void;
  onCall: (call: string) => void;
  onFontSize: (size: number) => void;
  onWrap: (wrap: boolean) => void;
  onRun: () => void;
};

const KEYWORDS = [
  "def",
  "return",
  "if",
  "elif",
  "else",
  "for",
  "while",
  "break",
  "continue",
  "and",
  "or",
  "not",
  "in",
  "is",
  "True",
  "False",
  "None",
  "lambda",
  "pass",
];

let completionsRegistered = false;

function registerCompletions(monaco: typeof Monaco) {
  if (completionsRegistered) return;
  completionsRegistered = true;
  monaco.languages.registerCompletionItemProvider("python", {
    provideCompletionItems(model, position) {
      const word = model.getWordUntilPosition(position);
      const range = {
        startLineNumber: position.lineNumber,
        endLineNumber: position.lineNumber,
        startColumn: word.startColumn,
        endColumn: word.endColumn,
      };
      const found = model.getValue().match(/\b[A-Za-z_][A-Za-z0-9_]*\b/g) ?? [];
      const labels = [...new Set([...KEYWORDS, ...found])];
      return {
        suggestions: labels.map((label) => ({
          label,
          kind: KEYWORDS.includes(label)
            ? monaco.languages.CompletionItemKind.Keyword
            : monaco.languages.CompletionItemKind.Variable,
          insertText: label,
          range,
        })),
      };
    },
  });
}

export default function EditorPane({
  source,
  call,
  fontSize,
  wrap,
  currentLine,
  onSource,
  onCall,
  onFontSize,
  onWrap,
  onRun,
}: Props) {
  const runRef = useRef(onRun);
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const decorationsRef = useRef<Monaco.editor.IEditorDecorationsCollection | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    runRef.current = onRun;
  }, [onRun]);

  useEffect(() => {
    const editor = editorRef.current;
    const decorations = decorationsRef.current;
    if (!editor || !decorations) return;
    if (currentLine == null) {
      decorations.clear();
      return;
    }
    decorations.set([
      {
        range: {
          startLineNumber: currentLine,
          startColumn: 1,
          endLineNumber: currentLine,
          endColumn: 1,
        },
        options: {
          isWholeLine: true,
          className: "debug-current-line",
          marginClassName: "debug-current-margin",
        },
      },
    ]);
    editor.revealLineInCenterIfOutsideViewport(currentLine);
  }, [currentLine, mounted]);

  const handleMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    decorationsRef.current = editor.createDecorationsCollection();
    setMounted(true);
    monaco.editor.defineTheme("recurse-dark", {
      base: "vs-dark",
      inherit: true,
      rules: [],
      colors: {
        "editor.background": "#1a1814",
        "editor.foreground": "#f3efe4",
        "editorLineNumber.foreground": "#6f675c",
        "editorLineNumber.activeForeground": "#d8d0c4",
        "editorCursor.foreground": "#e07a3d",
        "editor.selectionBackground": "#3d3428",
        "editor.lineHighlightBackground": "#24211c",
      },
    });
    monaco.editor.setTheme("recurse-dark");
    registerCompletions(monaco);
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      runRef.current();
    });
  };

  return (
    <div className="editor-pane">
      <div className="editor-toolbar">
        <span className="editor-kicker">Python</span>
        <div className="editor-tools">
          <button
            type="button"
            onClick={() => onFontSize(Math.max(12, fontSize - 1))}
            aria-label="Decrease font size"
          >
            A−
          </button>
          <span className="font-size">{fontSize}</span>
          <button
            type="button"
            onClick={() => onFontSize(Math.min(22, fontSize + 1))}
            aria-label="Increase font size"
          >
            A+
          </button>
          <button
            type="button"
            className={wrap ? "pressed" : ""}
            aria-pressed={wrap}
            onClick={() => onWrap(!wrap)}
          >
            Wrap
          </button>
        </div>
      </div>
      <div className="editor-fill">
        <Editor
          language="python"
          theme="recurse-dark"
          value={source}
          onChange={(value) => onSource(value ?? "")}
          onMount={handleMount}
          loading={<div className="editor-loading">Loading editor…</div>}
          options={{
            fontSize,
            fontFamily: "'IBM Plex Mono', ui-monospace, monospace",
            fontLigatures: false,
            wordWrap: wrap ? "on" : "off",
            minimap: { enabled: false },
            scrollBeyondLastLine: false,
            padding: { top: 16, bottom: 16 },
            smoothScrolling: true,
            renderLineHighlight: "line",
            overviewRulerLanes: 0,
            hideCursorInOverviewRuler: true,
            scrollbar: { verticalScrollbarSize: 8, horizontalScrollbarSize: 8 },
            tabSize: 4,
            automaticLayout: true,
            bracketPairColorization: { enabled: true },
          }}
        />
      </div>
      <form
        className="call-row"
        onSubmit={(event) => {
          event.preventDefault();
          onRun();
        }}
      >
        <label htmlFor="starting-call">Starting call</label>
        <input
          id="starting-call"
          value={call}
          spellCheck={false}
          autoCapitalize="off"
          placeholder="fib(5)"
          onChange={(event) => onCall(event.target.value)}
        />
      </form>
    </div>
  );
}
