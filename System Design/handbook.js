(function () {
  const CHECKS = "sd-handbook-v1";
  const MODE = "sd-handbook-mode";
  const phases = (window.SD_PHASES || []).slice().sort((a, b) => a.n - b.n);
  const nav = document.getElementById("phase-nav");
  const stage = document.getElementById("stage");
  const q = document.getElementById("q");
  const modeRef = document.getElementById("mode-ref");
  const modeTalk = document.getElementById("mode-talk");
  const progressLabel = document.getElementById("progress-label");
  const progressPct = document.getElementById("progress-pct");
  const progressFill = document.getElementById("progress-fill");

  const items = [];
  phases.forEach((phase) => {
    (phase.topics || []).forEach((topic) => items.push({ phase, item: topic, kind: "topic" }));
    (phase.problems || []).forEach((problem) => items.push({ phase, item: problem, kind: "problem" }));
  });

  let checks = {};
  try { checks = JSON.parse(localStorage.getItem(CHECKS)) || {}; } catch (e) { checks = {}; }
  let activeId = phases[0] ? phases[0].id : "";

  function saveChecks() {
    localStorage.setItem(CHECKS, JSON.stringify(checks));
    paintProgress();
  }

  function paintProgress() {
    const done = items.filter((row) => checks[row.item.id]).length;
    const total = items.length;
    const pct = total ? Math.round((done / total) * 100) : 0;
    progressLabel.textContent = done + " من " + total;
    progressPct.textContent = pct + "%";
    progressFill.style.width = pct + "%";
  }

  function hay(row) {
    const item = row.item;
    return [
      row.phase.ar, row.phase.en, item.ar, item.en, item.keys,
      item.definition, item.why, item.when, item.tradeoff, item.mistake, item.followup,
      item.opener, item.requirements, item.estimate, item.api, item.data,
      item.components, item.dive, item.bottleneck,
      (item.script || []).join(" ")
    ].join(" ").toLowerCase();
  }

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text != null) fillMixed(node, text);
    return node;
  }

  function fillMixed(node, text) {
    const re = /[A-Za-z][A-Za-z0-9./:+#_-]*(?:[ \t,/+&-]+[A-Za-z0-9][A-Za-z0-9./:+#_-]*)*/g;
    let last = 0;
    let match = re.exec(text);
    if (!match) {
      node.textContent = text;
      return;
    }
    while (match) {
      if (match.index > last) node.append(document.createTextNode(text.slice(last, match.index)));
      const term = document.createElement("span");
      term.className = "latin";
      term.dir = "ltr";
      term.textContent = match[0];
      node.append(term);
      last = match.index + match[0].length;
      match = re.exec(text);
    }
    if (last < text.length) node.append(document.createTextNode(text.slice(last)));
  }

  function block(title, text, className) {
    const section = el("section", className || "only-ref");
    section.append(el("h3", null, title), el("p", null, text));
    return section;
  }

  function fields() {
    const wrap = el("div", "fields");
    Array.from(arguments).forEach(function (node) { wrap.append(node); });
    return wrap;
  }

  function scriptBlock(lines) {
    const section = el("section", "script-block");
    section.append(el("h3", null, "السكربت"));
    (lines || []).forEach((line) => section.append(el("p", null, line)));
    return section;
  }

  function card(row) {
    const item = row.item;
    const article = el("article", "card");
    article.id = item.id;
    const top = el("div", "card-top");
    const box = el("button", "check" + (checks[item.id] ? " is-on" : ""));
    box.type = "button";
    box.setAttribute("aria-pressed", checks[item.id] ? "true" : "false");
    box.setAttribute("aria-label", "تعليم " + item.ar);
    box.textContent = checks[item.id] ? "✓" : "";
    box.addEventListener("click", function () {
      checks[item.id] = !checks[item.id];
      if (!checks[item.id]) delete checks[item.id];
      saveChecks();
      renderNav();
      box.classList.toggle("is-on", !!checks[item.id]);
      box.setAttribute("aria-pressed", checks[item.id] ? "true" : "false");
      box.textContent = checks[item.id] ? "✓" : "";
    });
    const titles = el("div");
    titles.append(el("h3", "topic-title", item.ar), el("p", "en", item.en));
    top.append(box, titles);
    article.append(top);
    if (row.kind === "topic") {
      article.append(
        fields(
          block("التعريف", item.definition),
          block("ليه يهم", item.why),
          block("إمتى تستخدمه وإمتى لأ", item.when, "only-ref span-2"),
          block("مفاضلة", item.tradeoff),
          block("غلطة شائعة", item.mistake, "only-ref mistake"),
          block("سؤال المتابعة", item.followup, "only-ref followup span-2")
        ),
        scriptBlock(item.script)
      );
    } else {
      article.append(
        fields(
          block("أول جملة", item.opener, "only-ref span-2"),
          block("المتطلبات", item.requirements, "only-ref span-2"),
          block("التقدير", item.estimate, "only-ref span-2"),
          block("API", item.api, "only-ref span-2"),
          block("موديل الداتا", item.data, "only-ref span-2"),
          block("المكوّنات", item.components, "only-ref span-2"),
          block("التعمق", item.dive, "only-ref span-2"),
          block("الاختناق", item.bottleneck, "only-ref span-2")
        ),
        scriptBlock(item.script)
      );
    }
    return article;
  }

  function phaseHead(phase) {
    const head = el("header", "phase-head");
    const kicker = el("p", "phase-kicker");
    kicker.append(el("span", "phase-index", String(phase.n).padStart(2, "0")));
    kicker.append(el("span", null, phase.en));
    const figure = el("figure", "diagram-stage");
    const frame = document.createElement("iframe");
    frame.src = phase.diagram;
    frame.title = phase.diagramTitle;
    frame.loading = "lazy";
    const cap = el("figcaption", "diagram-cap");
    cap.append(el("span", null, phase.diagramTitle));
    const link = el("a", "diagram-link", "صفحة الرسمة");
    link.href = phase.diagram;
    link.target = "_blank";
    link.rel = "noopener";
    cap.append(link);
    figure.append(frame, cap);
    head.append(kicker, el("h2", null, phase.ar), el("p", "lede", phase.lede), figure);
    return head;
  }

  function renderNav() {
    nav.replaceChildren();
    phases.forEach((phase) => {
      const count = (phase.topics || []).length + (phase.problems || []).length;
      const done = items.filter((row) => row.phase.id === phase.id && checks[row.item.id]).length;
      const button = el("button", "phase-btn" + (phase.id === activeId && !q.value.trim() ? " is-on" : ""));
      button.type = "button";
      button.append(
      el("span", "phase-num", String(phase.n)),
      el("span", "phase-name", phase.ar),
      el("small", null, phase.en),
      el("em", null, done + " / " + count)
    );
      button.addEventListener("click", function () {
        q.value = "";
        activeId = phase.id;
        history.replaceState(null, "", "#" + phase.id);
        render();
        window.scrollTo(0, 0);
      });
      nav.append(button);
    });
  }

  function renderStage() {
    const query = q.value.trim().toLowerCase();
    stage.replaceChildren();
    if (!phases.length) {
      stage.append(el("p", "empty", "لسه مفيش محتوى."));
      return;
    }
    if (query) {
      const hits = items.filter((row) => hay(row).includes(query));
      stage.append(el("p", "group-label", hits.length ? ("نتائج البحث: " + hits.length) : "مفيش نتيجة للكلمة دي."));
      let last = "";
      hits.forEach((row) => {
        if (row.phase.id !== last) {
          last = row.phase.id;
          stage.append(el("p", "group-label", "مرحلة " + row.phase.n + " — " + row.phase.ar));
        }
        stage.append(card(row));
      });
      return;
    }
    const phase = phases.find((entry) => entry.id === activeId) || phases[0];
    activeId = phase.id;
    stage.append(phaseHead(phase));
    if ((phase.topics || []).length) {
      stage.append(el("p", "group-label", "المواضيع"));
      phase.topics.forEach((topic) => stage.append(card({ phase, item: topic, kind: "topic" })));
    }
    if ((phase.problems || []).length) {
      stage.append(el("p", "group-label", "مسائل التصميم"));
      phase.problems.forEach((problem) => stage.append(card({ phase, item: problem, kind: "problem" })));
    }
  }

  function render() {
    renderNav();
    renderStage();
    paintProgress();
  }

  function setMode(talk) {
    document.body.classList.toggle("talk", talk);
    modeRef.classList.toggle("is-on", !talk);
    modeTalk.classList.toggle("is-on", talk);
    modeRef.setAttribute("aria-pressed", talk ? "false" : "true");
    modeTalk.setAttribute("aria-pressed", talk ? "true" : "false");
    localStorage.setItem(MODE, talk ? "talk" : "ref");
  }

  modeRef.addEventListener("click", function () { setMode(false); });
  modeTalk.addEventListener("click", function () { setMode(true); });
  q.addEventListener("input", render);
  q.addEventListener("search", render);

  const hash = location.hash.replace("#", "");
  const hashedPhase = phases.find((phase) => phase.id === hash);
  const hashedItem = items.find((row) => row.item.id === hash);
  if (hashedPhase) activeId = hashedPhase.id;
  if (hashedItem) activeId = hashedItem.phase.id;
  if (localStorage.getItem(MODE) === "talk") setMode(true);
  render();
  if (hashedItem) {
    const node = document.getElementById(hashedItem.item.id);
    if (node) node.scrollIntoView({ block: "start" });
  }
})();
