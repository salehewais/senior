import type { Binding, HeapObject, Step, Value } from "./types";

export type Point = { x: number; y: number };
export type Rect = { x: number; y: number; w: number; h: number };
export type Side = "left" | "right" | "top" | "bottom";

export type ValueSlot = { port: string; value: Value };

export type FrameView = {
  id: string;
  title: string;
  current: boolean;
  rows: { name: string; slot: ValueSlot }[];
  extra: ValueSlot | null;
};

export type ObjectView = {
  heapId: string;
  object: HeapObject;
  classSlot: ValueSlot | null;
  cells: ValueSlot[] | null;
  pairs: { key: ValueSlot; value: ValueSlot }[] | null;
  attrs: { name: string; slot: ValueSlot }[];
  closure: { name: string; slot: ValueSlot }[];
};

export type GraphNode = {
  id: string;
  kind: "frame" | "object";
  column: number;
  order: number;
  frame?: FrameView;
  objectView?: ObjectView;
};

export type GraphEdge = {
  id: string;
  from: string;
  to: string;
  port: string;
  back: boolean;
  self: boolean;
};

export type GraphModel = {
  nodes: GraphNode[];
  edges: GraphEdge[];
};

export type BoxSize = { w: number; h: number; ports: Record<string, Point> };

export type PlacedNode = GraphNode & { x: number; y: number; w: number; h: number };

export type DrawnArrow = { id: string; d: string };

export type Bounds = { minX: number; minY: number; maxX: number; maxY: number };

export type GraphPlacement = {
  nodes: PlacedNode[];
  arrows: DrawnArrow[];
  bounds: Bounds;
};

export type RouteEdge = {
  id: string;
  targetId: string;
  source: Point;
  sourceBox: Rect;
  targetBox: Rect;
  self: boolean;
};

const COLUMN_GAP = 88;
const ROW_GAP = 28;
const CELL_KINDS = new Set(["list", "tuple", "set", "frozenset"]);

function isPair(item: Value | { key: Value; value: Value }): item is { key: Value; value: Value } {
  return "key" in item && "value" in item;
}

export function frameViews(step: Step): FrameView[] {
  const functionFrames = step.stack.filter((frame) => frame.func !== "<module>");
  const frames: FrameView[] = [
    {
      id: "frame:global",
      title: "Global frame",
      current: functionFrames.length === 0,
      rows: step.globals.map((binding) => ({
        name: binding.name,
        slot: { port: "frame:global:b:" + binding.name, value: binding.value },
      })),
      extra: null,
    },
  ];
  functionFrames.forEach((frame, index) => {
    const id = `frame:${index}`;
    const current = index === functionFrames.length - 1;
    const showReturn = current && step.event === "return" && step.func === frame.func;
    frames.push({
      id,
      title: frame.func,
      current,
      rows: frame.locals.map((binding) => ({
        name: binding.name,
        slot: { port: `${id}:b:${binding.name}`, value: binding.value },
      })),
      extra: showReturn
        ? { port: `${id}:return`, value: step.return_value ?? { kind: "none" } }
        : null,
    });
  });
  return frames;
}

export function objectView(heapId: string, object: HeapObject): ObjectView {
  const classSlot =
    object.class_ref?.kind === "ref" ? { port: `${heapId}:class`, value: object.class_ref } : null;
  const cells = CELL_KINDS.has(object.kind)
    ? (object.items?.filter((item): item is Value => !isPair(item)) ?? []).map((value, index) => ({
        port: `${heapId}:i:${index}`,
        value,
      }))
    : null;
  const pairs =
    object.kind === "dict"
      ? (object.items?.filter(isPair) ?? []).map((pair, index) => ({
          key: { port: `${heapId}:k:${index}`, value: pair.key },
          value: { port: `${heapId}:v:${index}`, value: pair.value },
        }))
      : null;
  return {
    heapId,
    object,
    classSlot,
    cells,
    pairs,
    attrs: namedSlots(heapId, "a", object.attrs),
    closure: namedSlots(heapId, "c", object.closure),
  };
}

function namedSlots(heapId: string, kind: string, bindings: Binding[] | undefined): { name: string; slot: ValueSlot }[] {
  return (bindings ?? []).map((binding) => ({
    name: binding.name,
    slot: { port: `${heapId}:${kind}:${binding.name}`, value: binding.value },
  }));
}

function slotsOf(view: ObjectView): ValueSlot[] {
  const slots: ValueSlot[] = [];
  if (view.classSlot) slots.push(view.classSlot);
  if (view.cells) slots.push(...view.cells);
  if (view.pairs) {
    for (const pair of view.pairs) slots.push(pair.key, pair.value);
  }
  for (const row of view.attrs) slots.push(row.slot);
  for (const row of view.closure) slots.push(row.slot);
  return slots;
}

export function buildRelationGraph(step: Step): GraphModel {
  const frames = frameViews(step);
  const objects = Object.entries(step.heap).map(([heapId, object]) => objectView(heapId, object));
  const nodeIds = new Set<string>([...frames.map((frame) => frame.id), ...objects.map((view) => `obj:${view.heapId}`)]);
  const edges: GraphEdge[] = [];
  let seq = 0;
  const order = new Map<string, number>();

  function claim(id: string) {
    if (!order.has(id)) order.set(id, seq++);
  }

  function link(from: string, slot: ValueSlot) {
    if (slot.value.kind !== "ref") return;
    const to = `obj:${slot.value.id}`;
    if (!nodeIds.has(to)) return;
    edges.push({ id: slot.port, from, to, port: slot.port, back: false, self: false });
    claim(to);
  }

  for (const frame of frames) claim(frame.id);
  for (const frame of frames) {
    for (const row of frame.rows) link(frame.id, row.slot);
    if (frame.extra) link(frame.id, frame.extra);
  }

  const queue = objects
    .map((view) => `obj:${view.heapId}`)
    .filter((id) => order.has(id))
    .sort((a, b) => (order.get(a) ?? 0) - (order.get(b) ?? 0));
  const views = new Map(objects.map((view) => [`obj:${view.heapId}`, view]));
  for (let index = 0; index < queue.length; index++) {
    const view = views.get(queue[index]);
    if (!view) continue;
    for (const slot of slotsOf(view)) {
      const before = order.size;
      link(`obj:${view.heapId}`, slot);
      const to = slot.value.kind === "ref" ? `obj:${slot.value.id}` : "";
      if (to && order.size !== before) queue.push(to);
    }
  }
  for (const view of objects) claim(`obj:${view.heapId}`);

  const nodes: GraphNode[] = [
    ...frames.map((frame) => ({
      id: frame.id,
      kind: "frame" as const,
      column: 0,
      order: order.get(frame.id) ?? 0,
      frame,
    })),
    ...objects.map((view) => ({
      id: `obj:${view.heapId}`,
      kind: "object" as const,
      column: 1,
      order: order.get(`obj:${view.heapId}`) ?? 0,
      objectView: view,
    })),
  ];

  markCycles(nodes, edges);
  assignColumns(nodes, edges);
  return { nodes, edges };
}

/** A reference back to a node already on the walk is a cycle, so that edge does not add another column. */
function markCycles(nodes: GraphNode[], edges: GraphEdge[]) {
  const outgoing = new Map<string, GraphEdge[]>();
  for (const edge of edges) {
    const list = outgoing.get(edge.from) ?? [];
    list.push(edge);
    outgoing.set(edge.from, list);
  }
  const onPath = new Set<string>();
  const seen = new Set<string>();

  function visit(id: string) {
    seen.add(id);
    onPath.add(id);
    for (const edge of outgoing.get(id) ?? []) {
      if (edge.to === id) {
        edge.self = true;
        continue;
      }
      if (onPath.has(edge.to)) {
        edge.back = true;
        continue;
      }
      if (!seen.has(edge.to)) visit(edge.to);
    }
    onPath.delete(id);
  }

  for (const node of nodes) {
    if (node.kind === "frame" && !seen.has(node.id)) visit(node.id);
  }
  for (const node of nodes) {
    if (!seen.has(node.id)) visit(node.id);
  }
}

function assignColumns(nodes: GraphNode[], edges: GraphEdge[]) {
  const byId = new Map(nodes.map((node) => [node.id, node]));
  for (const node of nodes) node.column = node.kind === "frame" ? 0 : -1;

  const forward = edges.filter((edge) => !edge.back && !edge.self);
  const pointed = new Set(forward.map((edge) => edge.to));
  for (const node of nodes) {
    if (node.kind === "object" && !pointed.has(node.id)) node.column = 1;
  }

  for (let pass = 0; pass < nodes.length; pass++) {
    let changed = false;
    for (const edge of forward) {
      const source = byId.get(edge.from);
      const target = byId.get(edge.to);
      if (!source || !target || source.column < 0) continue;
      const next = source.column + 1;
      if (target.column < 0 || next < target.column) {
        target.column = next;
        changed = true;
      }
    }
    if (!changed) break;
  }
  for (const node of nodes) {
    if (node.column < 0) node.column = 1;
  }
}

export function placeGraph(model: GraphModel, sizes: Record<string, BoxSize>): GraphPlacement {
  const columns = new Map<number, GraphNode[]>();
  for (const node of model.nodes) {
    const list = columns.get(node.column) ?? [];
    list.push(node);
    columns.set(node.column, list);
  }
  const placed = new Map<string, PlacedNode>();
  let x = 0;
  const columnIndexes = [...columns.keys()].sort((a, b) => a - b);
  for (const column of columnIndexes) {
    const group = (columns.get(column) ?? []).slice().sort((a, b) => a.order - b.order);
    let y = 0;
    let width = 0;
    for (const node of group) {
      const size = sizes[node.id] ?? { w: 180, h: 48, ports: {} };
      const next: PlacedNode = { ...node, x, y, w: size.w, h: size.h };
      placed.set(node.id, next);
      y += size.h + ROW_GAP;
      width = Math.max(width, size.w);
    }
    x += width + COLUMN_GAP;
  }

  const nodes = model.nodes.map((node) => placed.get(node.id)!).filter(Boolean);
  const routes: RouteEdge[] = [];
  for (const edge of model.edges) {
    const source = placed.get(edge.from);
    const target = placed.get(edge.to);
    const port = source ? sizes[edge.from]?.ports[edge.port] : undefined;
    if (!source || !target || !port) continue;
    routes.push({
      id: edge.id,
      targetId: edge.to,
      source: { x: source.x + port.x, y: source.y + port.y },
      sourceBox: { x: source.x, y: source.y, w: source.w, h: source.h },
      targetBox: { x: target.x, y: target.y, w: target.w, h: target.h },
      self: edge.self || edge.from === edge.to,
    });
  }
  const routed = routeArrows(routes);
  return { nodes, arrows: routed.arrows, bounds: boundsOf(nodes, routed.points) };
}

export function routeArrows(edges: RouteEdge[]): { arrows: DrawnArrow[]; points: Point[] } {
  const selfEdges = edges.filter((edge) => edge.self);
  const others = edges.filter((edge) => !edge.self);
  const selfGroups = groupBy(selfEdges, (edge) => edge.targetId);
  const sideGroups = new Map<string, { edge: RouteEdge; side: Side }[]>();

  for (const edge of others) {
    const side = nearestSide(edge.source, edge.targetBox);
    const key = `${edge.targetId}:${side}`;
    const list = sideGroups.get(key) ?? [];
    list.push({ edge, side });
    sideGroups.set(key, list);
  }

  const arrows: DrawnArrow[] = [];
  const points: Point[] = [];
  let lane = 0;
  let minY = Infinity;
  let maxY = -Infinity;
  for (const edge of edges) {
    minY = Math.min(minY, edge.source.y, edge.sourceBox.y, edge.targetBox.y);
    maxY = Math.max(maxY, edge.source.y, edge.sourceBox.y + edge.sourceBox.h, edge.targetBox.y + edge.targetBox.h);
  }
  const routeBounds = {
    minY: Number.isFinite(minY) ? minY : 0,
    maxY: Number.isFinite(maxY) ? maxY : 0,
  };
  const boxes = edges.flatMap((edge) => [edge.sourceBox, edge.targetBox]);

  for (const group of selfGroups.values()) {
    group.sort((a, b) => a.source.y - b.source.y || a.source.x - b.source.x);
    group.forEach((edge, index) => {
      const path = selfLoop(edge, index, group.length);
      arrows.push({ id: edge.id, d: path.d });
      points.push(...path.points);
    });
  }

  const gutter: { edge: RouteEdge; side: Side; end: Point }[] = [];
  for (const group of sideGroups.values()) {
    const side = group[0].side;
    group.sort((a, b) => along(a.edge.source, side) - along(b.edge.source, side));
    group.forEach((item, index) => {
      const end = spreadPoint(item.edge.targetBox, side, index, group.length);
      if (clearlyForward(item.edge.source, item.edge.targetBox)) {
        const path = curve(item.edge.source, end);
        arrows.push({ id: item.edge.id, d: path.d });
        points.push(...path.points);
      } else {
        gutter.push({ edge: item.edge, side, end });
      }
    });
  }

  gutter.sort((a, b) => a.edge.source.y - b.edge.source.y || a.edge.source.x - b.edge.source.x);
  for (const item of gutter) {
    const path = gutterRoute(item.edge, item.side, item.end, lane, routeBounds, boxes);
    lane += 1;
    arrows.push({ id: item.edge.id, d: path.d });
    points.push(...path.points);
  }

  return { arrows, points };
}

export function fitTransform(bounds: Bounds, width: number, height: number): { x: number; y: number; k: number } {
  if (width < 10 || height < 10 || !Number.isFinite(bounds.minX)) {
    return { x: 40, y: 48, k: 1 };
  }
  const pad = 36;
  const boundsW = Math.max(1, bounds.maxX - bounds.minX);
  const boundsH = Math.max(1, bounds.maxY - bounds.minY);
  const k = Math.max(0.12, Math.min(1.35, (width - pad * 2) / boundsW, (height - pad * 2) / boundsH));
  const cx = (bounds.minX + bounds.maxX) / 2;
  const cy = (bounds.minY + bounds.maxY) / 2;
  return {
    k,
    x: width / 2 - cx * k,
    y: height / 2 - cy * k,
  };
}

function boundsOf(nodes: PlacedNode[], points: Point[]): Bounds {
  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;
  for (const node of nodes) {
    minX = Math.min(minX, node.x);
    minY = Math.min(minY, node.y);
    maxX = Math.max(maxX, node.x + node.w);
    maxY = Math.max(maxY, node.y + node.h);
  }
  for (const point of points) {
    minX = Math.min(minX, point.x);
    minY = Math.min(minY, point.y);
    maxX = Math.max(maxX, point.x);
    maxY = Math.max(maxY, point.y);
  }
  if (!Number.isFinite(minX)) return { minX: 0, minY: 0, maxX: 1, maxY: 1 };
  return { minX, minY, maxX, maxY };
}

function groupBy<T>(items: T[], key: (item: T) => string): Map<string, T[]> {
  const groups = new Map<string, T[]>();
  for (const item of items) {
    const id = key(item);
    const list = groups.get(id) ?? [];
    list.push(item);
    groups.set(id, list);
  }
  return groups;
}

function along(point: Point, side: Side): number {
  return side === "top" || side === "bottom" ? point.x : point.y;
}

function nearestSide(point: Point, box: Rect): Side {
  const sides: Side[] = ["left", "right", "top", "bottom"];
  let best: Side = "left";
  let bestDist = Infinity;
  for (const side of sides) {
    const dist = distanceToSide(point, box, side);
    if (dist < bestDist) {
      bestDist = dist;
      best = side;
    }
  }
  return best;
}

function distanceToSide(point: Point, box: Rect, side: Side): number {
  if (side === "left") return Math.hypot(point.x - box.x, clamp(point.y, box.y, box.y + box.h) - point.y);
  if (side === "right") {
    return Math.hypot(point.x - (box.x + box.w), clamp(point.y, box.y, box.y + box.h) - point.y);
  }
  if (side === "top") return Math.hypot(clamp(point.x, box.x, box.x + box.w) - point.x, point.y - box.y);
  return Math.hypot(clamp(point.x, box.x, box.x + box.w) - point.x, point.y - (box.y + box.h));
}

function spreadPoint(box: Rect, side: Side, index: number, count: number): Point {
  const vertical = side === "left" || side === "right";
  const length = vertical ? box.h : box.w;
  const inset = Math.min(14, length * 0.22);
  const span = Math.max(1, length - inset * 2);
  const pos = count === 1 ? length / 2 : inset + (span * index) / (count - 1);
  if (side === "left") return { x: box.x, y: box.y + pos };
  if (side === "right") return { x: box.x + box.w, y: box.y + pos };
  if (side === "top") return { x: box.x + pos, y: box.y };
  return { x: box.x + pos, y: box.y + box.h };
}

function clearlyForward(source: Point, target: Rect): boolean {
  return target.x >= source.x + 24;
}

function curve(from: Point, to: Point): { d: string; points: Point[] } {
  const dx = to.x - from.x;
  const bend = Math.min(Math.max(28, Math.abs(dx) / 2), Math.abs(dx) * 0.75);
  const dir = dx >= 0 ? 1 : -1;
  const c1 = { x: from.x + bend * dir, y: from.y };
  const c2 = { x: to.x - bend * dir, y: to.y };
  return {
    d: `M ${n(from.x)} ${n(from.y)} C ${n(c1.x)} ${n(c1.y)}, ${n(c2.x)} ${n(c2.y)}, ${n(to.x)} ${n(to.y)}`,
    points: [from, c1, c2, to],
  };
}

function selfLoop(edge: RouteEdge, index: number, count: number): { d: string; points: Point[] } {
  const box = edge.targetBox;
  const right = box.x + box.w;
  const inset = Math.min(12, box.h * 0.2);
  const span = Math.max(1, box.h - inset * 2);
  const endY = box.y + (count === 1 ? Math.min(box.h - 10, Math.max(10, edge.source.y - box.y + 14)) : inset + (span * index) / (count - 1));
  const out = right + 32 + index * 14;
  const crest = Math.min(edge.source.y, endY) - 26 - index * 12;
  return rounded([
    edge.source,
    { x: out, y: edge.source.y },
    { x: out, y: crest },
    { x: right, y: crest },
    { x: right, y: endY },
  ]);
}

function gutterRoute(
  edge: RouteEdge,
  side: Side,
  end: Point,
  lane: number,
  bounds: { minY: number; maxY: number },
  boxes: Rect[],
): { d: string; points: Point[] } {
  const gap = 16;
  const source = edge.sourceBox;
  const target = edge.targetBox;
  const start = edge.source;
  const outerRight = rightOfColumn(source, boxes) + gap;
  const sky = bounds.minY - 22 - lane * 14;
  const floor = bounds.maxY + 22 + lane * 14;
  const targetIsLeft = target.x + target.w <= start.x - 8;

  if (targetIsLeft || side === "left") {
    const approachX = side === "left" ? leftOfColumn(target, boxes) - gap : rightOfColumn(target, boxes) + gap;
    const laneY = side === "bottom" ? floor : sky;
    return rounded([
      start,
      { x: outerRight, y: start.y },
      { x: outerRight, y: laneY },
      { x: approachX, y: laneY },
      { x: approachX, y: end.y },
      end,
    ]);
  }

  return rounded([
    start,
    { x: outerRight, y: start.y },
    { x: outerRight, y: end.y },
    end,
  ]);
}

function rightOfColumn(source: Rect, boxes: Rect[]): number {
  const spanRight = source.x + source.w;
  let right = spanRight;
  for (const box of boxes) {
    if (box.x < spanRight && box.x + box.w > source.x) right = Math.max(right, box.x + box.w);
  }
  return right;
}

function leftOfColumn(source: Rect, boxes: Rect[]): number {
  const spanRight = source.x + source.w;
  let left = source.x;
  for (const box of boxes) {
    if (box.x < spanRight && box.x + box.w > source.x) left = Math.min(left, box.x);
  }
  return left;
}

function rounded(raw: Point[]): { d: string; points: Point[] } {
  const points = raw.filter((point, index) => {
    if (index === 0) return true;
    const prev = raw[index - 1];
    return Math.hypot(point.x - prev.x, point.y - prev.y) > 0.5;
  });
  if (points.length < 2) {
    const only = points[0] ?? { x: 0, y: 0 };
    return { d: `M ${n(only.x)} ${n(only.y)}`, points };
  }
  const radius = 12;
  const cmds = [`M ${n(points[0].x)} ${n(points[0].y)}`];
  for (let index = 1; index < points.length - 1; index++) {
    const prev = points[index - 1];
    const current = points[index];
    const next = points[index + 1];
    const d1 = Math.hypot(current.x - prev.x, current.y - prev.y);
    const d2 = Math.hypot(next.x - current.x, next.y - current.y);
    const r = Math.min(radius, d1 / 2, d2 / 2);
    if (r < 1 || d1 === 0 || d2 === 0) {
      cmds.push(`L ${n(current.x)} ${n(current.y)}`);
      continue;
    }
    const ax = current.x - ((current.x - prev.x) / d1) * r;
    const ay = current.y - ((current.y - prev.y) / d1) * r;
    const bx = current.x + ((next.x - current.x) / d2) * r;
    const by = current.y + ((next.y - current.y) / d2) * r;
    cmds.push(`L ${n(ax)} ${n(ay)} Q ${n(current.x)} ${n(current.y)} ${n(bx)} ${n(by)}`);
  }
  const last = points[points.length - 1];
  cmds.push(`L ${n(last.x)} ${n(last.y)}`);
  return { d: cmds.join(" "), points };
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function n(value: number): string {
  return (Math.round(value * 10) / 10).toString();
}
