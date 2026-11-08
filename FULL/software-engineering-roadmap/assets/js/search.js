/**
 * Instant client-side search across all concepts and headings.
 */
(function (global) {
  let index = [];

  function normalize(s) {
    return (s || "")
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "");
  }

  function buildIndex(content, extraEntries) {
    index = [];

    function walkSection(sec, path) {
      const p = path.concat(sec.title);
      index.push({
        kind: "heading",
        id: sec.id,
        title: sec.title,
        path: p.slice(0, -1),
        search: normalize(p.join(" ")),
      });
      for (const block of sec.blocks || []) {
        if (block.type === "list") walkItems(block.items, p);
      }
      for (const child of sec.children || []) walkSection(child, p);
    }

    function walkItems(items, path) {
      for (const item of items) {
        index.push({
          kind: "concept",
          id: item.id,
          title: item.text,
          path,
          search: normalize(path.join(" ") + " " + item.text),
        });
        if (item.children && item.children.length) {
          walkItems(item.children, path.concat(item.text));
        }
      }
    }

    for (const sec of content.sections) walkSection(sec, []);

    // Visual / additional pages (e.g. Architecture Relationships)
    for (const entry of extraEntries || []) {
      index.push({
        kind: entry.kind || "heading",
        id: entry.id,
        title: entry.title,
        path: entry.path || [],
        search: normalize(entry.search || entry.title),
        jumpId: entry.jumpId || null,
      });
    }
  }

  function search(query, limit) {
    const q = normalize(query.trim());
    if (!q) return [];
    const terms = q.split(/\s+/).filter(Boolean);
    const scored = [];
    for (const entry of index) {
      let score = 0;
      let ok = true;
      for (const term of terms) {
        const pos = entry.search.indexOf(term);
        if (pos === -1) {
          ok = false;
          break;
        }
        score += 10;
        if (normalize(entry.title).startsWith(term)) score += 20;
        if (normalize(entry.title).includes(term)) score += 8;
        if (pos < 20) score += 5;
      }
      if (ok) {
        if (entry.kind === "heading") score += 3;
        scored.push({ entry, score });
      }
    }
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, limit || 40).map((s) => s.entry);
  }

  function highlight(text, query) {
    const q = query.trim();
    if (!q) return escapeHtml(text);
    const terms = q.split(/\s+/).filter(Boolean);
    let out = escapeHtml(text);
    for (const term of terms) {
      const re = new RegExp("(" + escapeRegExp(term) + ")", "ig");
      out = out.replace(re, "<mark>$1</mark>");
    }
    return out;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function escapeRegExp(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  global.RoadmapSearch = {
    buildIndex,
    search,
    highlight,
    escapeHtml,
  };
})(window);
