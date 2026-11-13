/**
 * Main app: render roadmap content, wire progress/search/theme/filters.
 */
(function () {
  const content = window.ROADMAP_CONTENT;
  if (!content) {
    document.body.innerHTML =
      "<p style='padding:2rem;font-family:sans-serif'>Failed to load roadmap-content.js</p>";
    return;
  }

  const filterState = { status: "all" }; // all | complete | in-progress | not-started

  function escapeHtml(s) {
    return RoadmapSearch.escapeHtml(s);
  }

  function inlineFormat(text) {
    // **bold** and preserve rest
    let t = escapeHtml(text);
    t = t.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    return t;
  }

  function topicNumber(title) {
    const m = title.match(/^(\d{2})\s*—/);
    if (m) return m[1];
    if (title.startsWith("Supporting")) return "SF";
    if (title.startsWith("Cross-Topic")) return "XR";
    if (title.startsWith("Recommended")) return "ST";
    if (title.startsWith("Roadmap Overview")) return "00";
    return "•";
  }

  function renderList(items, ordered) {
    const tag = ordered ? "ol" : "ul";
    const extra =
      items.length && items[0].text && /^\*\*/.test("") ? "" : "";
    // Detect study strategy numbered list by parent later — use class for concepts
    let html = `<${tag} class="concept-list">`;
    for (const item of items) {
      const done = RoadmapProgress.isDone(item.id);
      const hasKids = item.children && item.children.length > 0;
      html += `<li data-concept-id="${escapeHtml(item.id)}">`;
      html += `<div class="concept-item${done ? " done" : ""}">`;
      html += `<input type="checkbox" class="concept-check" data-id="${escapeHtml(
        item.id
      )}" ${done ? "checked" : ""} aria-label="Mark complete: ${escapeHtml(
        item.text.replace(/"/g, "'")
      )}" />`;
      html += `<span class="concept-label" id="${escapeHtml(item.id)}">${inlineFormat(
        item.text
      )}</span>`;
      html += `</div>`;
      if (hasKids) {
        html += renderList(item.children, item.children[0]?.ordered);
      }
      html += `</li>`;
    }
    html += `</${tag}>`;
    return html;
  }

  function renderBlocks(blocks, sectionTitle) {
    let html = "";
    for (const block of blocks || []) {
      if (block.type === "blockquote") {
        html += `<blockquote class="blockquote">${inlineFormat(
          block.text
        ).replace(/\n/g, "<br>")}</blockquote>`;
      } else if (block.type === "callout") {
        html += `<div class="callout">${inlineFormat(block.text)}</div>`;
      } else if (block.type === "paragraph") {
        html += `<p class="paragraph">${inlineFormat(block.text)}</p>`;
      } else if (block.type === "list") {
        const isStrategy =
          sectionTitle && sectionTitle.indexOf("Recommended Study Strategy") !== -1;
        if (isStrategy && (!blocks.some((b) => b !== block && b.type === "list") || true)) {
          // Use special numbered look for top-level strategy questions
          const topLevelNumbered = block.items.every((it) => it.ordered);
          if (topLevelNumbered && sectionTitle === "Recommended Study Strategy") {
            html += `<ol class="strategy-steps concept-list">`;
            for (const item of block.items) {
              const done = RoadmapProgress.isDone(item.id);
              html += `<li data-concept-id="${escapeHtml(item.id)}">`;
              html += `<div class="concept-item${done ? " done" : ""}">`;
              html += `<input type="checkbox" class="concept-check" data-id="${escapeHtml(
                item.id
              )}" ${done ? "checked" : ""} />`;
              html += `<span class="concept-label" id="${escapeHtml(
                item.id
              )}">${inlineFormat(item.text)}</span></div></li>`;
            }
            html += `</ol>`;
            continue;
          }
        }
        html += renderList(block.items, block.items[0]?.ordered);
      }
    }
    return html;
  }

  function headingTag(level) {
    return "h" + Math.min(6, Math.max(2, level + 1));
  }

  function renderChild(child, depth) {
    const ids = RoadmapProgress.collectIdsFromSection(child);
    const summary = RoadmapProgress.summarize(ids);
    const cls = depth <= 2 ? "category" : "subcategory";
    let html = `<section class="${cls}" id="${escapeHtml(
      child.id
    )}" data-title="${escapeHtml(child.title)}">`;
    const tag = depth === 1 ? "h3" : depth === 2 ? "h4" : "h5";
    html += `<${tag}>${escapeHtml(child.title)}</${tag}>`;
    if (ids.length) {
      html += `<div class="category-progress" data-section-progress="${escapeHtml(
        child.id
      )}">
        <span class="mini-bar"><span style="width:${summary.pct}%"></span></span>
        <span>${summary.done}/${summary.total} · ${statusLabel(summary.status)}</span>
      </div>`;
    }
    html += `<div class="section-body">${renderBlocks(child.blocks, child.title)}</div>`;
    for (const c of child.children || []) {
      html += renderChild(c, depth + 1);
    }
    html += `</section>`;
    return html;
  }

  function statusLabel(status) {
    if (status === "complete") return "Complete";
    if (status === "in-progress") return "In Progress";
    return "Not Started";
  }

  function renderTopic(section, index) {
    const ids = RoadmapProgress.collectIdsFromSection(section);
    const summary = RoadmapProgress.summarize(ids);
    const num = topicNumber(section.title);
    let html = `<article class="topic-section" id="${escapeHtml(
      section.id
    )}" data-title="${escapeHtml(section.title)}" data-topic-index="${index}">`;
    html += `<header class="topic-header">`;
    html += `<span class="topic-number">${escapeHtml(num)}</span>`;
    html += `<h2>${escapeHtml(section.title)}</h2>`;
    html += `<div class="topic-meta">`;
    html += `<span class="badge ${summary.status}" data-topic-badge="${escapeHtml(
      section.id
    )}">${statusLabel(summary.status)} · ${summary.pct}%</span>`;
    html += `<span class="badge">${ids.length} concepts</span>`;
    html += `<span class="badge">${(section.children || []).length} categories</span>`;
    html += `</div></header>`;
    html += `<div class="section-body">${renderBlocks(section.blocks, section.title)}</div>`;
    for (const child of section.children || []) {
      html += renderChild(child, 1);
    }
    html += `</article>`;
    return html;
  }

  function renderIntro() {
    const meta = content.meta;
    let html = `<section class="intro-banner" id="top">`;
    html += `<p class="paragraph" style="font-size:1.05rem;color:var(--text)">${escapeHtml(
      meta.originalSubtitle || meta.subtitle
    )}</p>`;
    if (meta.introNote) {
      html += `<blockquote class="blockquote">${inlineFormat(meta.introNote).replace(
        /\n/g,
        "<br>"
      )}</blockquote>`;
    }
    html += `<p class="paragraph" style="font-size:0.85rem;color:var(--text-muted)">Source: ${escapeHtml(
      meta.sourceFile
    )} · ${content.stats.headingCount} headings · ${
      content.stats.conceptCount
    } trackable concepts</p>`;
    html += `</section>`;
    return html;
  }

  function buildSidebar() {
    const nav = document.getElementById("nav-tree");
    let html = "";

    // Special overview item — Architecture Relationships (visual / additional)
    if (window.ArchitectureRelationships) {
      html += ArchitectureRelationships.sidebarHtml();
    }

    function itemHtml(sec, level) {
      const kids = sec.children || [];
      const ids = RoadmapProgress.collectIdsFromSection(sec);
      const summary = RoadmapProgress.summarize(ids);
      const statusClass =
        summary.status === "complete"
          ? "done"
          : summary.status === "in-progress"
            ? "partial"
            : "";
      const hasKids = kids.length > 0;
      // Collapse deep levels by default except first two depths
      const collapsed = level >= 2 ? " collapsed" : "";
      let out = `<li class="nav-item level-${level}${collapsed}" data-nav-id="${escapeHtml(
        sec.id
      )}" data-status="${summary.status}">`;
      out += `<div class="nav-row">`;
      out += `<button type="button" class="nav-toggle${
        hasKids ? "" : " empty"
      }" aria-expanded="${level < 2 ? "true" : "false"}" aria-label="Toggle">${
        hasKids ? "▸" : ""
      }</button>`;
      out += `<a class="nav-link" href="#${escapeHtml(sec.id)}">`;
      out += `<span class="nav-status ${statusClass}" data-nav-status="${escapeHtml(
        sec.id
      )}"></span>`;
      out += `<span class="label">${escapeHtml(sec.title)}</span>`;
      if (ids.length) out += `<span class="count">${summary.done}/${ids.length}</span>`;
      out += `</a></div>`;
      if (hasKids) {
        out += `<ul>`;
        for (const c of kids) out += itemHtml(c, level + 1);
        out += `</ul>`;
      }
      out += `</li>`;
      return out;
    }

    for (const sec of content.sections) {
      html += itemHtml(sec, 1);
    }
    nav.innerHTML = html;

    nav.addEventListener("click", (e) => {
      const toggle = e.target.closest(".nav-toggle");
      if (!toggle || toggle.classList.contains("empty")) return;
      e.preventDefault();
      const li = toggle.closest(".nav-item");
      const collapsed = li.classList.toggle("collapsed");
      toggle.setAttribute("aria-expanded", collapsed ? "false" : "true");
      toggle.textContent = "▸";
    });
  }

  function buildToc() {
    const toc = document.getElementById("toc-list");
    let html = "";
    if (window.ArchitectureRelationships) {
      html += ArchitectureRelationships.tocHtml();
    }
    for (const sec of content.sections) {
      html += `<li><a href="#${escapeHtml(sec.id)}" class="depth-1">${escapeHtml(
        sec.title.length > 40 ? sec.title.slice(0, 40) + "…" : sec.title
      )}</a></li>`;
      for (const child of sec.children || []) {
        html += `<li><a href="#${escapeHtml(child.id)}" class="depth-3">${escapeHtml(
          child.title.length > 36 ? child.title.slice(0, 36) + "…" : child.title
        )}</a></li>`;
      }
    }
    toc.innerHTML = html;
  }

  function renderAll() {
    const root = document.getElementById("content");
    let html = renderIntro();
    html += `<div class="study-nav" id="study-nav-top">
      <button type="button" id="study-prev">← Previous</button>
      <span id="study-label"></span>
      <button type="button" id="study-next">Next →</button>
    </div>`;
    // Visual overview page — placed before roadmap topics for discoverability
    if (window.ArchitectureRelationships) {
      html += ArchitectureRelationships.renderPage();
    }
    content.sections.forEach((sec, i) => {
      html += renderTopic(sec, i);
    });
    html += `<div class="study-nav">
      <button type="button" class="study-prev-dup">← Previous</button>
      <button type="button" class="study-next-dup">Next →</button>
    </div>`;
    root.innerHTML = html;

    if (window.ArchitectureRelationships) {
      ArchitectureRelationships.wireDiagramActions(root);
    }

    // Wire dup study buttons
    document.querySelectorAll(".study-prev-dup").forEach((b) => {
      b.addEventListener("click", () => document.getElementById("study-prev")?.click());
    });
    document.querySelectorAll(".study-next-dup").forEach((b) => {
      b.addEventListener("click", () => document.getElementById("study-next")?.click());
    });
  }

  function updateProgressUI() {
    const allIds = content.concepts.map((c) => c.id);
    const overall = RoadmapProgress.summarize(allIds);
    const fill = document.getElementById("progress-fill");
    const pct = document.getElementById("progress-pct");
    if (fill) fill.style.width = overall.pct + "%";
    if (pct) pct.textContent = overall.pct + "%";

    content.sections.forEach((sec) => {
      const ids = RoadmapProgress.collectIdsFromSection(sec);
      const summary = RoadmapProgress.summarize(ids);
      const badge = document.querySelector(`[data-topic-badge="${CSS.escape(sec.id)}"]`);
      if (badge) {
        badge.className = `badge ${summary.status}`;
        badge.textContent = `${statusLabel(summary.status)} · ${summary.pct}%`;
      }
      const navStatus = document.querySelector(`[data-nav-status="${CSS.escape(sec.id)}"]`);
      if (navStatus) {
        navStatus.className =
          "nav-status " +
          (summary.status === "complete"
            ? "done"
            : summary.status === "in-progress"
              ? "partial"
              : "");
      }
      const navItem = document.querySelector(`[data-nav-id="${CSS.escape(sec.id)}"]`);
      if (navItem) {
        navItem.dataset.status = summary.status;
        const count = navItem.querySelector(":scope > .nav-row .count");
        if (count && ids.length) count.textContent = `${summary.done}/${ids.length}`;
      }

      function walk(s) {
        const sid = s.id;
        const sids = RoadmapProgress.collectIdsFromSection(s);
        const sum = RoadmapProgress.summarize(sids);
        const prog = document.querySelector(`[data-section-progress="${CSS.escape(sid)}"]`);
        if (prog) {
          const bar = prog.querySelector(".mini-bar > span");
          if (bar) bar.style.width = sum.pct + "%";
          const label = prog.querySelector("span:last-child");
          if (label) label.textContent = `${sum.done}/${sum.total} · ${statusLabel(sum.status)}`;
        }
        const ni = document.querySelector(`[data-nav-id="${CSS.escape(sid)}"]`);
        if (ni) {
          ni.dataset.status = sum.status;
          const st = ni.querySelector(`[data-nav-status="${CSS.escape(sid)}"]`);
          if (st) {
            st.className =
              "nav-status " +
              (sum.status === "complete"
                ? "done"
                : sum.status === "in-progress"
                  ? "partial"
                  : "");
          }
          const c = ni.querySelector(":scope > .nav-row .count");
          if (c && sids.length) c.textContent = `${sum.done}/${sids.length}`;
        }
        (s.children || []).forEach(walk);
      }
      walk(sec);
    });

    applyFilters();
  }

  function wireProgressClicks() {
    document.getElementById("content").addEventListener("change", (e) => {
      const cb = e.target.closest(".concept-check");
      if (!cb) return;
      const id = cb.dataset.id;
      RoadmapProgress.setDone(id, cb.checked);
      const item = cb.closest(".concept-item");
      if (item) item.classList.toggle("done", cb.checked);
      updateProgressUI();
    });
  }

  function wireSearch() {
    const extra =
      (window.ArchitectureRelationships && ArchitectureRelationships.getSearchEntries()) || [];
    RoadmapSearch.buildIndex(content, extra);
    const input = document.getElementById("global-search");
    const results = document.getElementById("search-results");
    let active = -1;
    let current = [];

    function renderResults(items, q) {
      current = items;
      active = -1;
      if (!q.trim()) {
        results.classList.remove("open");
        results.innerHTML = "";
        return;
      }
      if (!items.length) {
        results.innerHTML = `<div class="search-result">No matches</div>`;
        results.classList.add("open");
        return;
      }
      results.innerHTML = items
        .map(
          (it, i) => `
        <button type="button" class="search-result" data-idx="${i}" data-id="${escapeHtml(
            it.jumpId || it.id
          )}">
          <span>${RoadmapSearch.highlight(it.title, q)}</span>
          <span class="path">${escapeHtml(
            (it.path.length ? it.path.slice(-3) : ["Architecture Relationships"]).join(" › ")
          )}</span>
        </button>`
        )
        .join("");
      results.classList.add("open");
    }

    input.addEventListener("input", () => {
      const q = input.value;
      renderResults(RoadmapSearch.search(q, 35), q);
    });

    results.addEventListener("click", (e) => {
      const btn = e.target.closest(".search-result");
      if (!btn || !btn.dataset.id) return;
      navigateToResult(btn.dataset.id, input.value);
      results.classList.remove("open");
      input.blur();
    });

    input.addEventListener("keydown", (e) => {
      const buttons = [...results.querySelectorAll(".search-result[data-id]")];
      if (e.key === "ArrowDown") {
        e.preventDefault();
        active = Math.min(buttons.length - 1, active + 1);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        active = Math.max(0, active - 1);
      } else if (e.key === "Enter") {
        e.preventDefault();
        const btn = buttons[active] || buttons[0];
        if (btn) {
          navigateToResult(btn.dataset.id, input.value);
          results.classList.remove("open");
        }
        return;
      } else if (e.key === "Escape") {
        results.classList.remove("open");
        return;
      } else return;
      buttons.forEach((b, i) => b.setAttribute("aria-selected", i === active ? "true" : "false"));
      buttons[active]?.scrollIntoView({ block: "nearest" });
    });

    document.addEventListener("click", (e) => {
      if (!e.target.closest(".search-wrap")) results.classList.remove("open");
    });
  }

  function navigateToResult(id, query) {
    RoadmapNav.expandAncestors(id);
    // If concept, ensure parent topic visible
    const el = document.getElementById(id);
    if (el) {
      const topic = el.closest(".topic-section");
      if (document.body.classList.contains("study-mode") && topic) {
        RoadmapNav.showOnlyTopic(topic.id);
      }
      RoadmapNav.scrollToId(id);
      // Highlight match in label
      if (query && el.classList.contains("concept-label") === false) {
        // id may be on concept-label span
      }
      const label = document.getElementById(id);
      if (label && query && label.classList.contains("concept-label")) {
        const raw = label.textContent;
        label.innerHTML = RoadmapSearch.highlight(raw, query);
        setTimeout(() => {
          label.textContent = raw;
          // restore bold formatting roughly
          label.innerHTML = inlineFormat(raw);
        }, 2500);
      }
    } else {
      // heading id
      RoadmapNav.scrollToId(id);
    }
    history.replaceState(null, "", "#" + id);
  }

  function wireTheme() {
    const saved = localStorage.getItem("se-roadmap-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const theme = saved || (prefersDark ? "dark" : "light");
    setTheme(theme);
    document.getElementById("theme-toggle").addEventListener("click", async () => {
      const next =
        document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(next);
      localStorage.setItem("se-roadmap-theme", next);
      if (window.RoadmapDiagrams) await RoadmapDiagrams.rethemeDiagrams();
    });
  }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const btn = document.getElementById("theme-toggle");
    if (btn) {
      btn.title = theme === "dark" ? "Switch to light mode" : "Switch to dark mode";
      btn.setAttribute("aria-label", btn.title);
      btn.textContent = theme === "dark" ? "☀" : "☾";
    }
  }

  function wireFilters() {
    document.querySelectorAll(".filter-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        document.querySelectorAll(".filter-chip").forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        filterState.status = chip.dataset.filter;
        applyFilters();
      });
    });
  }

  function applyFilters() {
    const status = filterState.status;
    document.querySelectorAll("#nav-tree > .nav-item").forEach((li) => {
      // Overview / visual map always visible in the sidebar
      if (li.dataset.alwaysShow === "true") {
        li.classList.remove("hidden");
        return;
      }
      if (status === "all") {
        li.classList.remove("hidden");
        return;
      }
      const st = li.dataset.status;
      // Match filter: complete / in-progress / not-started
      const show = st === status;
      li.classList.toggle("hidden", !show);
    });
  }

  function init() {
    document.getElementById("site-title").textContent = content.meta.title;
    document.getElementById("site-subtitle").textContent = content.meta.subtitle;
    document.title = content.meta.title;

    renderAll();
    buildSidebar();
    buildToc();
    wireProgressClicks();
    wireSearch();
    wireTheme();
    wireFilters();
    updateProgressUI();

    const topicIds = [
      ...(window.ArchitectureRelationships
        ? [ArchitectureRelationships.PAGE_ID]
        : []),
      ...content.sections.map((s) => s.id),
    ];
    RoadmapNav.initNavigation({ topicIds });

    // Expand first roadmap topic (skip special overview item) by default in sidebar
    document.querySelectorAll("#nav-tree > .nav-item:not(.nav-special)").forEach((li, i) => {
      if (i === 0) li.classList.remove("collapsed");
    });

    RoadmapDiagrams.initDiagrams().then(() => {
      // Re-observe after diagrams inserted? nav already set
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
