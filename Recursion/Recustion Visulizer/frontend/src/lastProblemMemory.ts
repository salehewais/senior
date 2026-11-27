/** Browser memory for the last selected example only. */

const STORAGE_KEY = "recursion-tree-last-problem";

export type LastProblemMemory = {
  exampleId: string;
};

export function loadLastProblem(): LastProblemMemory | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const data = JSON.parse(raw) as Partial<LastProblemMemory>;
    if (typeof data.exampleId !== "string" || !data.exampleId) return null;
    return { exampleId: data.exampleId };
  } catch {
    return null;
  }
}

export function saveLastProblem(exampleId: string): void {
  const memory: LastProblemMemory = { exampleId };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(memory));
}
