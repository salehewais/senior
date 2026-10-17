import type { FrameView, ObjectView, ValueSlot } from "../graphLayout";
import type { HeapObject, Value } from "../types";

function textOf(value: Value): string {
  switch (value.kind) {
    case "none":
      return "None";
    case "bool":
      return value.v ? "True" : "False";
    case "int":
      return String(value.v);
    case "float":
      return value.repr ?? String(value.v);
    case "str":
      return JSON.stringify(value.v);
    case "function":
      return `function ${value.name}`;
    case "class":
      return `class ${value.name}`;
    case "unknown":
      return `${value.type} ${value.repr}`.trim();
    case "ref":
      return "";
  }
}

function Port({ id, port }: { id: number; port: string }) {
  return <span className="port" data-from={String(id)} data-port={port} />;
}

function ValueView({ slot }: { slot: ValueSlot }) {
  if (slot.value.kind === "ref") return <Port id={slot.value.id} port={slot.port} />;
  return <span className="literal">{textOf(slot.value)}</span>;
}

function objectTitle(object: HeapObject): string {
  if (object.kind === "class") {
    const bases = object.bases?.length ? ` (extends ${object.bases.join(", ")})` : "";
    return `${object.name ?? "class"} class${bases}`;
  }
  if (object.kind === "function") {
    const params = (object.params ?? []).join(", ");
    return `function ${object.name ?? ""}(${params})`;
  }
  if (object.kind === "instance") return `${object.type ?? "object"} instance`;
  if (object.kind === "unknown") return object.type ?? "value";
  return object.kind;
}

export function ObjectBox({ view }: { view: ObjectView }) {
  const { object } = view;
  const showIndex = object.kind !== "set" && object.kind !== "frozenset";

  return (
    <article className={`obj obj-${object.kind}`} data-to={view.heapId}>
      <header>
        <span>{objectTitle(object)}</span>
        {view.classSlot && <ValueView slot={view.classSlot} />}
      </header>
      {view.cells && (
        <div className="obj-cells">
          {view.cells.map((slot, index) => (
            <div className="obj-cell" key={slot.port}>
              {showIndex && <span className="idx">{index}</span>}
              <ValueView slot={slot} />
            </div>
          ))}
        </div>
      )}
      {view.pairs && (
        <div className="obj-rows">
          {view.pairs.map((pair) => (
            <div className="bind-row" key={pair.key.port}>
              <ValueView slot={pair.key} />
              <ValueView slot={pair.value} />
            </div>
          ))}
        </div>
      )}
      {view.attrs.length > 0 && (
        <div className="obj-rows">
          {view.attrs.map((row) => (
            <div className="bind-row" key={row.slot.port}>
              <span className="bind-name">{row.name}</span>
              <ValueView slot={row.slot} />
            </div>
          ))}
        </div>
      )}
      {view.closure.length > 0 && (
        <div className="obj-rows">
          {view.closure.map((row) => (
            <div className="bind-row" key={row.slot.port}>
              <span className="bind-name">{row.name}</span>
              <ValueView slot={row.slot} />
            </div>
          ))}
        </div>
      )}
      {object.kind === "unknown" && object.repr && <p className="literal">{object.repr}</p>}
      {object.truncated && <p className="muted">truncated</p>}
    </article>
  );
}

export function FrameTable({ frame }: { frame: FrameView }) {
  return (
    <table className={frame.current ? "frame-table current" : "frame-table"}>
      <thead>
        <tr>
          <th colSpan={2}>{frame.title}</th>
        </tr>
      </thead>
      <tbody>
        {frame.rows.map((row) => (
          <tr key={row.slot.port}>
            <td className="var-name">{row.name}</td>
            <td className="var-value">
              <ValueView slot={row.slot} />
            </td>
          </tr>
        ))}
        {frame.extra && (
          <tr>
            <td className="var-name">return</td>
            <td className="var-value">
              <ValueView slot={frame.extra} />
            </td>
          </tr>
        )}
        {frame.rows.length === 0 && !frame.extra && (
          <tr>
            <td className="var-name" colSpan={2}>
              empty
            </td>
          </tr>
        )}
      </tbody>
    </table>
  );
}
