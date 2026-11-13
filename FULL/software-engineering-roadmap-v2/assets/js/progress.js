/**
 * Progress tracking with localStorage persistence.
 */
(function (global) {
  const STORAGE_KEY = "se-roadmap-progress-v1";

  function load() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return { completed: {} };
      const parsed = JSON.parse(raw);
      return { completed: parsed.completed || {} };
    } catch {
      return { completed: {} };
    }
  }

  function save(state) {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ completed: state.completed, updatedAt: Date.now() })
      );
    } catch (e) {
      console.warn("Could not persist progress", e);
    }
  }

  let state = load();

  function isDone(id) {
    return Boolean(state.completed[id]);
  }

  function setDone(id, done) {
    if (done) state.completed[id] = true;
    else delete state.completed[id];
    save(state);
  }

  function toggle(id) {
    setDone(id, !isDone(id));
    return isDone(id);
  }

  function getCompletedSet() {
    return new Set(Object.keys(state.completed));
  }

  function summarize(conceptIds) {
    const total = conceptIds.length;
    let done = 0;
    for (const id of conceptIds) {
      if (isDone(id)) done += 1;
    }
    let pct = 0;
    if (total > 0) {
      if (done === 0) pct = 0;
      else if (done === total) pct = 100;
      else pct = Math.max(1, Math.round((done / total) * 100));
    }
    let status = "not-started";
    if (done === 0) status = "not-started";
    else if (done === total) status = "complete";
    else status = "in-progress";
    return { done, total, pct, status };
  }

  function collectIdsFromSection(section) {
    const ids = [];
    function walkList(items) {
      for (const item of items) {
        ids.push(item.id);
        if (item.children && item.children.length) walkList(item.children);
      }
    }
    function walk(sec) {
      for (const block of sec.blocks || []) {
        if (block.type === "list") walkList(block.items);
      }
      for (const child of sec.children || []) walk(child);
    }
    walk(section);
    return ids;
  }

  function clearAll() {
    state = { completed: {} };
    save(state);
  }

  global.RoadmapProgress = {
    isDone,
    setDone,
    toggle,
    summarize,
    collectIdsFromSection,
    getCompletedSet,
    clearAll,
    reload: () => {
      state = load();
    },
  };
})(window);
