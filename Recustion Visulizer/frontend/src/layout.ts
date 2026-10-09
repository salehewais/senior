import { hierarchy, tree } from "d3-hierarchy";
import type { TraceEvent } from "./types";

export const NODE_H = 36;

export type TreeNode = {
  id: number;
  name: string;
  args: string[];
  label: string;
  width: number;
  callIndex: number;
  returnIndex: number | null;
  value: string | null;
  error: boolean;
  children: TreeNode[];
};

export type PlacedNode = {
  id: number;
  label: string;
  width: number;
  x: number;
  y: number;
  callIndex: number;
  returnIndex: number | null;
  value: string | null;
  error: boolean;
  parentId: number | null;
};

export function nodeLabel(name: string, args: string[]): string {
  return `${name}(${args.join(", ")})`;
}

export function nodeWidth(label: string): number {
  return Math.max(84, Math.ceil(label.length * 7.7 + 28));
}

export function buildTree(events: TraceEvent[]): TreeNode | null {
  const nodes = new Map<number, TreeNode>();
  let root: TreeNode | null = null;
  events.forEach((event, index) => {
    if (event.type === "call") {
      const label = nodeLabel(event.name, event.args);
      const node: TreeNode = {
        id: event.id,
        name: event.name,
        args: event.args,
        label,
        width: nodeWidth(label),
        callIndex: index,
        returnIndex: null,
        value: null,
        error: false,
        children: [],
      };
      nodes.set(event.id, node);
      if (event.parent == null) root = node;
      else nodes.get(event.parent)?.children.push(node);
    } else if (event.type === "return") {
      const node = nodes.get(event.id);
      if (node) {
        node.returnIndex = index;
        node.value = event.value;
        node.error = event.error;
      }
    }
  });
  return root;
}

export function layoutTree(root: TreeNode): PlacedNode[] {
  const laid = tree<TreeNode>()
    .nodeSize([1, 98])
    .separation((a, b) => {
      const gap = (a.data.width + b.data.width) / 2 + 28;
      return a.parent === b.parent ? gap : gap + 24;
    })(hierarchy(root, (node) => (node.children.length ? node.children : null)));

  const placed: PlacedNode[] = [];
  laid.each((node) => {
    placed.push({
      id: node.data.id,
      label: node.data.label,
      width: node.data.width,
      x: node.x,
      y: node.y,
      callIndex: node.data.callIndex,
      returnIndex: node.data.returnIndex,
      value: node.data.value,
      error: node.data.error,
      parentId: node.parent ? node.parent.data.id : null,
    });
  });
  return placed;
}

export function focusRoot(nodes: PlacedNode[], width: number, height: number) {
  const root = nodes.find((node) => node.parentId == null) ?? nodes[0];
  if (!root || width < 10 || height < 10) {
    return { x: width / 2, y: 48, k: 1 };
  }
  return {
    k: 1,
    x: width / 2 - root.x,
    y: Math.min(height * 0.22, 72) - root.y,
  };
}

export function frameTree(
  nodes: PlacedNode[],
  focusId: number | null,
  width: number,
  height: number,
) {
  const fitted = fitTransform(nodes, width, height);
  if (fitted.k >= 0.62) return fitted;
  const root = nodes.find((node) => node.parentId == null);
  const focus = nodes.find((node) => node.id === focusId);
  if (focus && focus !== root) {
    return { k: 1, x: width / 2 - focus.x, y: height / 2 - focus.y };
  }
  return focusRoot(nodes, width, height);
}

export function fitTransform(nodes: PlacedNode[], width: number, height: number) {
  if (!nodes.length || width < 10 || height < 10) {
    return { x: width / 2, y: 48, k: 1 };
  }
  let minX = Infinity;
  let maxX = -Infinity;
  let minY = Infinity;
  let maxY = -Infinity;
  for (const node of nodes) {
    minX = Math.min(minX, node.x - node.width / 2);
    maxX = Math.max(maxX, node.x + node.width / 2);
    minY = Math.min(minY, node.y - NODE_H / 2 - 32);
    maxY = Math.max(maxY, node.y + NODE_H / 2 + 12);
  }
  const pad = 40;
  const boundsW = Math.max(1, maxX - minX);
  const boundsH = Math.max(1, maxY - minY);
  const k = Math.max(
    0.12,
    Math.min(1.35, (width - pad * 2) / boundsW, (height - pad * 2) / boundsH),
  );
  const cx = (minX + maxX) / 2;
  const cy = (minY + maxY) / 2;
  return {
    k,
    x: width / 2 - cx * k,
    y: height / 2 - cy * k,
  };
}
