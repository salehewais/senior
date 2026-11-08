(function () {
  const catalogEl = document.getElementById("pattern-catalog");
  const input = document.getElementById("pattern-search");
  const results = document.getElementById("search-results");

  if (catalogEl && input && results) {
    let catalog = [];
    try { catalog = JSON.parse(catalogEl.textContent || "[]"); } catch (e) { catalog = []; }

    function render(items) {
      if (!items.length) {
        results.hidden = true;
        results.innerHTML = "";
        return;
      }
      results.hidden = false;
      results.innerHTML = items.slice(0, 12).map((item) => {
        const ready = item.ready ? "" : " · قريبًا";
        return `<li><a href="${item.href}"><span dir="ltr">${item.name}</span><span class="meta" dir="ltr">${item.group}${ready}</span></a></li>`;
      }).join("");
    }

    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (!q) { render([]); return; }
      const hits = catalog.filter((p) => p.name.toLowerCase().includes(q));
      render(hits);
    });

    input.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        const first = results.querySelector("a");
        if (first) first.click();
      }
    });
  }

  // TOC active section highlighting
  const tocLinks = Array.from(document.querySelectorAll(".toc a"));
  const patterns = tocLinks
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);

  if (tocLinks.length && patterns.length && "IntersectionObserver" in window) {
    const map = new Map();
    tocLinks.forEach((a) => map.set(a.getAttribute("href"), a));
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = "#" + entry.target.id;
        tocLinks.forEach((a) => a.classList.remove("active"));
        const link = map.get(id);
        if (link) link.classList.add("active");
      });
    }, { rootMargin: "-20% 0px -60% 0px", threshold: 0.1 });
    patterns.forEach((sec) => obs.observe(sec));
  }
})();
