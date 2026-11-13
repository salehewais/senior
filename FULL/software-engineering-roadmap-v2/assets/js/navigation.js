/**
 * Sidebar, scroll spy, study mode, breadcrumbs, back-to-top.
 */
(function (global) {
  let studyIndex = 0;
  let topicIds = [];

  function initNavigation(opts) {
    topicIds = opts.topicIds || [];
    wireSidebarToggle();
    wireBackToTop();
    wireStudyMode();
    wireHashNavigation();
    observeActiveSections();
  }

  function wireSidebarToggle() {
    const btn = document.getElementById("menu-toggle");
    const backdrop = document.getElementById("sidebar-backdrop");
    if (btn) {
      btn.addEventListener("click", () => {
        document.body.classList.toggle("sidebar-open");
      });
    }
    if (backdrop) {
      backdrop.addEventListener("click", () => {
        document.body.classList.remove("sidebar-open");
      });
    }
    document.addEventListener("click", (e) => {
      const link = e.target.closest(".sidebar a.nav-link");
      if (link && window.matchMedia("(max-width: 900px)").matches) {
        document.body.classList.remove("sidebar-open");
      }
    });
  }

  function wireBackToTop() {
    const btn = document.getElementById("back-to-top");
    if (!btn) return;
    window.addEventListener(
      "scroll",
      () => {
        btn.classList.toggle("visible", window.scrollY > 500);
      },
      { passive: true }
    );
    btn.addEventListener("click", () => {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function wireStudyMode() {
    const btn = document.getElementById("study-toggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const on = document.body.classList.toggle("study-mode");
      btn.setAttribute("aria-pressed", on ? "true" : "false");
      if (on) {
        const current = getCurrentTopicId();
        studyIndex = Math.max(0, topicIds.indexOf(current));
        showOnlyTopic(topicIds[studyIndex]);
        updateStudyNav();
      } else {
        showAllTopics();
      }
    });

    const prev = document.getElementById("study-prev");
    const next = document.getElementById("study-next");
    if (prev) {
      prev.addEventListener("click", () => {
        if (studyIndex > 0) {
          studyIndex -= 1;
          showOnlyTopic(topicIds[studyIndex]);
          updateStudyNav();
          scrollToId(topicIds[studyIndex]);
        }
      });
    }
    if (next) {
      next.addEventListener("click", () => {
        if (studyIndex < topicIds.length - 1) {
          studyIndex += 1;
          showOnlyTopic(topicIds[studyIndex]);
          updateStudyNav();
          scrollToId(topicIds[studyIndex]);
        }
      });
    }
  }

  function updateStudyNav() {
    const prev = document.getElementById("study-prev");
    const next = document.getElementById("study-next");
    const label = document.getElementById("study-label");
    if (prev) prev.disabled = studyIndex <= 0;
    if (next) next.disabled = studyIndex >= topicIds.length - 1;
    if (label) {
      label.textContent = `${studyIndex + 1} / ${topicIds.length}`;
    }
  }

  function showOnlyTopic(id) {
    document.querySelectorAll(".topic-section").forEach((el) => {
      el.classList.toggle("hidden", el.id !== id);
    });
  }

  function showAllTopics() {
    document.querySelectorAll(".topic-section").forEach((el) => {
      el.classList.remove("hidden");
    });
  }

  function getCurrentTopicId() {
    const sections = [...document.querySelectorAll(".topic-section")];
    let current = topicIds[0];
    const y = window.scrollY + 120;
    for (const sec of sections) {
      if (sec.offsetTop <= y) current = sec.id;
    }
    return current;
  }

  function wireHashNavigation() {
    document.addEventListener("click", (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      const id = decodeURIComponent(a.getAttribute("href").slice(1));
      if (!id) return;
      const el = document.getElementById(id);
      if (!el) return;
      e.preventDefault();
      if (document.body.classList.contains("study-mode")) {
        const topic = el.closest(".topic-section");
        if (topic) {
          studyIndex = Math.max(0, topicIds.indexOf(topic.id));
          showOnlyTopic(topic.id);
          updateStudyNav();
        }
      }
      scrollToId(id);
      history.replaceState(null, "", "#" + id);
    });

    if (location.hash) {
      const id = decodeURIComponent(location.hash.slice(1));
      requestAnimationFrame(() => scrollToId(id));
    }
  }

  function scrollToId(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.scrollIntoView({ behavior: "smooth", block: "start" });
    flash(el);
  }

  function flash(el) {
    el.classList.add("flash-target");
    setTimeout(() => el.classList.remove("flash-target"), 1200);
  }

  function observeActiveSections() {
    const links = document.querySelectorAll(".sidebar a.nav-link, .toc-list a");
    const map = new Map();
    links.forEach((a) => {
      const id = a.getAttribute("href")?.slice(1);
      if (id) {
        if (!map.has(id)) map.set(id, []);
        map.get(id).push(a);
      }
    });

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const id = entry.target.id;
          document.querySelectorAll(".nav-row.active").forEach((r) => r.classList.remove("active"));
          document.querySelectorAll(".toc-list a.active").forEach((a) => a.classList.remove("active"));
          const anchors = map.get(id) || [];
          anchors.forEach((a) => {
            a.classList.add("active");
            const row = a.closest(".nav-row");
            if (row) row.classList.add("active");
          });
          updateBreadcrumbs(entry.target);
        });
      },
      { rootMargin: "-20% 0px -65% 0px", threshold: 0 }
    );

    document.querySelectorAll(".topic-section, .category, .subcategory").forEach((el) => {
      if (el.id) observer.observe(el);
    });
  }

  function updateBreadcrumbs(el) {
    const trail = [];
    let node = el;
    while (node && node !== document.getElementById("content")) {
      if (node.id && (node.classList.contains("topic-section") || node.classList.contains("category") || node.classList.contains("subcategory"))) {
        const title =
          node.querySelector(":scope > .topic-header h2, :scope > h3, :scope > h4, :scope > h5")?.textContent ||
          node.getAttribute("data-title") ||
          node.id;
        trail.unshift({ id: node.id, title: title.trim() });
      }
      node = node.parentElement;
    }
    const elBc = document.getElementById("breadcrumbs");
    if (!elBc) return;
    elBc.innerHTML =
      '<a href="#roadmap-overview">Home</a>' +
      trail
        .map(
          (t) =>
            `<span class="sep">/</span><a href="#${t.id}">${RoadmapSearch.escapeHtml(
              t.title.length > 48 ? t.title.slice(0, 48) + "…" : t.title
            )}</a>`
        )
        .join("");
  }

  function expandAncestors(id) {
    const link = document.querySelector(`.sidebar a.nav-link[href="#${CSS.escape(id)}"]`);
    if (!link) return;
    let li = link.closest(".nav-item");
    while (li) {
      li.classList.remove("collapsed");
      const toggle = li.querySelector(":scope > .nav-row .nav-toggle");
      if (toggle) toggle.setAttribute("aria-expanded", "true");
      li = li.parentElement?.closest(".nav-item");
    }
  }

  global.RoadmapNav = {
    initNavigation,
    scrollToId,
    expandAncestors,
    showOnlyTopic,
    showAllTopics,
  };
})(window);
