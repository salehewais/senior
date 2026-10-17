import { useState } from "react";
import { EXAMPLE_GROUPS } from "../examples";
import type { Example } from "../examples";

interface ExamplesProps {
  code: string;
  onPick: (example: Example) => void;
}

export function Examples({ code, onPick }: ExamplesProps) {
  const [open, setOpen] = useState(true);

  return (
    <section className="examples-panel">
      <button type="button" className="examples-toggle" aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        <span className="twist">{open ? "▾" : "▸"}</span>
        Examples
      </button>
      {open && (
        <div className="examples-body">
          {EXAMPLE_GROUPS.map((group) => (
            <div className="example-group" key={group.title}>
              <h3>{group.title}</h3>
              <div className="example-links">
                {group.examples.map((example) => (
                  <button
                    key={example.id}
                    type="button"
                    className={code === example.code ? "example-link current" : "example-link"}
                    onClick={() => onPick(example)}
                  >
                    {example.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
