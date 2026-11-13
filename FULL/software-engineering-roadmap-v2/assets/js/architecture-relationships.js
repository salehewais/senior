/**
 * Architecture Relationships — visual / additional overview page.
 * Shows how OOD, PoEAA, DDD, Application Architecture, EIP, and System Design
 * relate without merging distinct areas. Not part of the original Markdown.
 */
(function (global) {
  const PAGE_ID = "architecture-relationships";

  const MERMAID_MAP = `flowchart TB
  subgraph ObjectLens["Object & domain lenses"]
    OOD["OOD<br/>objects · responsibilities · GoF"]
    GoF["GoF patterns<br/>inside OOD"]
    PoEAA["PoEAA<br/>enterprise app patterns"]
    DDD_S["DDD Strategic<br/>contexts · maps"]
    DDD_T["DDD Tactical<br/>aggregates · entities"]
  end
  subgraph AppLens["Application structure"]
    AppArch["Application Architecture<br/>modules · layers · boundaries"]
    PresArch["Presentation Architecture<br/>UI · state · interaction"]
  end
  subgraph IntegrationLens["Integration & composition"]
    EIP["EIP<br/>message-based integration"]
    RTC["Real-Time Comms<br/>WS · SSE · polling"]
    SD["System Design<br/>composes many concerns"]
  end

  OOD --- GoF
  OOD -->|"feeds object design"| AppArch
  OOD -->|"complements"| PoEAA
  OOD -->|"tactical modeling"| DDD_T
  PoEAA -->|"implements inside"| AppArch
  PoEAA -.->|"≠ GoF · different catalog"| GoF
  DDD_S -->|"bounds"| DDD_T
  DDD_S -->|"shapes"| AppArch
  AppArch -->|"hosts UI within"| PresArch
  AppArch -->|"integrates via"| EIP
  AppArch -->|"used by"| SD
  DDD_S -->|"used by"| SD
  DDD_T -->|"used by"| SD
  EIP -->|"used by"| SD
  EIP -.->|"≠ realtime transport patterns"| RTC
  RTC -->|"part of"| SD
  PresArch -.->|"≠ Application Architecture"| AppArch

  classDef core fill:#ccfbf1,stroke:#0d6e6e,color:#1a2332
  classDef related fill:#e0f2fe,stroke:#0369a1,color:#1a2332
  classDef distinct fill:#fef3c7,stroke:#9a6700,color:#1a2332
  class OOD,PoEAA,DDD_S,DDD_T,AppArch,EIP,SD core
  class GoF,PresArch,RTC related
  class PresArch,RTC,GoF distinct

  click OOD "#03-object-oriented-design-ood" "Open OOD"
  click GoF "#34-gof-design-patterns" "Open GoF"
  click PoEAA "#06-patterns-of-enterprise-application-architecture-poeaa" "Open PoEAA"
  click DDD_S "#71-strategic-ddd" "Open Strategic DDD"
  click DDD_T "#72-tactical-ddd" "Open Tactical DDD"
  click AppArch "#04-application-architecture" "Open Application Architecture"
  click PresArch "#05-presentation-architecture" "Open Presentation Architecture"
  click EIP "#09-enterprise-integration-patterns-eip" "Open EIP"
  click RTC "#102-networking-and-communication" "Open Networking & Communication"
  click SD "#10-system-design" "Open System Design"`

  const NODES = [
    {
      id: "ood",
      title: "OOD",
      fullTitle: "Object-Oriented Design",
      href: "#03-object-oriented-design-ood",
      owns: "Objects, responsibilities, relationships, SOLID, UML, and reusable design (including GoF).",
      layer: "Object design lens",
    },
    {
      id: "gof",
      title: "GoF",
      fullTitle: "Gang of Four Design Patterns",
      href: "#34-gof-design-patterns",
      owns: "Creational, structural, and behavioral object patterns studied under OOD — not the PoEAA catalog.",
      layer: "Inside OOD",
    },
    {
      id: "app-arch",
      title: "Application Architecture",
      fullTitle: "Application Architecture",
      href: "#04-application-architecture",
      owns: "Whole-application structure: styles, layers, modules, dependency rules, and infrastructure boundaries.",
      layer: "Application structure",
    },
    {
      id: "pres-arch",
      title: "Presentation Architecture",
      fullTitle: "Presentation Architecture",
      href: "#05-presentation-architecture",
      owns: "UI organization: views, presenters/view-models, state, rendering, and user interaction — not the whole app.",
      layer: "UI concern (distinct)",
    },
    {
      id: "poeaa",
      title: "PoEAA",
      fullTitle: "Patterns of Enterprise Application Architecture",
      href: "#06-patterns-of-enterprise-application-architecture-poeaa",
      owns: "Enterprise implementation patterns for domain logic, persistence, web presentation, distribution, and session state.",
      layer: "Enterprise app patterns",
    },
    {
      id: "ddd-strategic",
      title: "DDD Strategic",
      fullTitle: "Domain-Driven Design — Strategic",
      href: "#71-strategic-ddd",
      owns: "Domain understanding, bounded contexts, and context-mapping relationships across a large domain.",
      layer: "Domain boundaries",
    },
    {
      id: "ddd-tactical",
      title: "DDD Tactical",
      fullTitle: "Domain-Driven Design — Tactical",
      href: "#72-tactical-ddd",
      owns: "Building blocks inside a context: aggregates, entities, value objects, repositories, domain events.",
      layer: "Domain modeling",
    },
    {
      id: "eip",
      title: "EIP",
      fullTitle: "Enterprise Integration Patterns",
      href: "#09-enterprise-integration-patterns-eip",
      owns: "Message-based integration: channels, routing, transformation, endpoints, and system management.",
      layer: "Service/app integration",
    },
    {
      id: "rtc",
      title: "Real-Time Communication",
      fullTitle: "Real-Time Communication Patterns",
      href: "#102-networking-and-communication",
      owns: "Connection and push models (WebSockets, SSE, long polling, etc.) — transport/interaction, not the EIP catalog.",
      layer: "Networking (distinct from EIP)",
    },
    {
      id: "system-design",
      title: "System Design",
      fullTitle: "System Design",
      href: "#10-system-design",
      owns: "Composes networking, storage, cache, scale, messaging, reliability, security, and ops into a coherent system.",
      layer: "Cross-cutting composition",
    },
  ];

  const EDGES = [
    {
      from: "OOD",
      to: "Application Architecture",
      why: "Object design informs how modules and layers express responsibilities; OOD does not define the whole architecture.",
      fromHref: "#03-object-oriented-design-ood",
      toHref: "#04-application-architecture",
    },
    {
      from: "OOD",
      to: "PoEAA",
      why: "Complementary lenses: OOD shapes objects; PoEAA catalogs enterprise implementation patterns that often use those objects.",
      fromHref: "#03-object-oriented-design-ood",
      toHref: "#06-patterns-of-enterprise-application-architecture-poeaa",
    },
    {
      from: "OOD / GoF",
      to: "PoEAA",
      why: "PoEAA ≠ GoF. GoF are object-design patterns; PoEAA are enterprise application patterns (persistence, distribution, etc.).",
      fromHref: "#34-gof-design-patterns",
      toHref: "#06-patterns-of-enterprise-application-architecture-poeaa",
      distinct: true,
    },
    {
      from: "OOD",
      to: "DDD Tactical",
      why: "Tactical DDD reuses object-modeling skill inside bounded contexts; DDD adds domain language and aggregate rules.",
      fromHref: "#03-object-oriented-design-ood",
      toHref: "#72-tactical-ddd",
    },
    {
      from: "DDD Strategic",
      to: "DDD Tactical",
      why: "Strategic ≠ tactical. Context maps and subdomain types bound the model; tactical blocks implement inside a context.",
      fromHref: "#71-strategic-ddd",
      toHref: "#72-tactical-ddd",
      distinct: true,
    },
    {
      from: "Application Architecture",
      to: "Presentation Architecture",
      why: "Application Architecture ≠ Presentation Architecture. App arch owns overall modules/layers; presentation owns the UI layer.",
      fromHref: "#04-application-architecture",
      toHref: "#05-presentation-architecture",
      distinct: true,
    },
    {
      from: "PoEAA / DDD",
      to: "Application Architecture",
      why: "Enterprise and domain patterns are hosted inside an application’s layers, ports, and module boundaries.",
      fromHref: "#04-application-architecture",
      toHref: "#04-application-architecture",
    },
    {
      from: "Application Architecture",
      to: "EIP",
      why: "When apps/services collaborate asynchronously, EIP supplies the messaging vocabulary for that integration surface.",
      fromHref: "#04-application-architecture",
      toHref: "#09-enterprise-integration-patterns-eip",
    },
    {
      from: "EIP",
      to: "Real-Time Communication",
      why: "EIP ≠ Real-Time Communication Patterns. EIP is message-integration design; realtime covers connection/push transports.",
      fromHref: "#09-enterprise-integration-patterns-eip",
      toHref: "#102-networking-and-communication",
      distinct: true,
    },
    {
      from: "System Design",
      to: "App Arch · DDD · EIP · …",
      why: "System Design connects multiple areas (architecture, messaging, storage, scale) but does not replace studying each pillar.",
      fromHref: "#10-system-design",
      toHref: "#10-system-design",
      distinct: true,
    },
  ];

  const DISTINCTIONS = [
    {
      title: "OOD ≠ Application Architecture ≠ Presentation Architecture",
      body: "OOD designs objects and collaboration. Application Architecture organizes the whole application. Presentation Architecture organizes only the UI/interaction layer.",
      links: [
        { label: "OOD", href: "#03-object-oriented-design-ood" },
        { label: "Application Architecture", href: "#04-application-architecture" },
        { label: "Presentation Architecture", href: "#05-presentation-architecture" },
      ],
    },
    {
      title: "PoEAA ≠ GoF (but may relate)",
      body: "GoF patterns live under OOD and solve object-structure/behavior problems. PoEAA patterns solve enterprise application problems (domain logic organization, OR mapping, session state, distribution).",
      links: [
        { label: "GoF", href: "#34-gof-design-patterns" },
        { label: "PoEAA", href: "#06-patterns-of-enterprise-application-architecture-poeaa" },
      ],
    },
    {
      title: "DDD Strategic ≠ Tactical",
      body: "Strategic design draws bounded contexts and maps relationships between them. Tactical design supplies building blocks used inside a single context.",
      links: [
        { label: "Strategic DDD", href: "#71-strategic-ddd" },
        { label: "Tactical DDD", href: "#72-tactical-ddd" },
      ],
    },
    {
      title: "EIP ≠ Real-Time Communication Patterns",
      body: "EIP catalogs how independent applications exchange messages. Real-time communication patterns describe client/server connection and push models used in networking and system design.",
      links: [
        { label: "EIP", href: "#09-enterprise-integration-patterns-eip" },
        { label: "Networking & Communication", href: "#102-networking-and-communication" },
      ],
    },
    {
      title: "System Design connects — it does not replace",
      body: "System Design draws on Application Architecture, DDD, EIP, concurrency, DBMS, and networking to design a whole system. Studying System Design alone is not a substitute for those pillars.",
      links: [
        { label: "System Design", href: "#10-system-design" },
        { label: "Cross-Topic Notes", href: "#cross-topic-relationships-and-study-notes" },
      ],
    },
  ];

  function escape(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function renderNodeCards() {
    return NODES.map(
      (n) => `
      <a class="arch-node-card" href="${escape(n.href)}" data-arch-node="${escape(n.id)}">
        <span class="arch-node-kicker">${escape(n.layer)}</span>
        <strong class="arch-node-title">${escape(n.title)}</strong>
        <span class="arch-node-full">${escape(n.fullTitle)}</span>
        <span class="arch-node-owns">${escape(n.owns)}</span>
        <span class="arch-node-cta">Open roadmap section →</span>
      </a>`
    ).join("");
  }

  function renderEdges() {
    return EDGES.map(
      (e) => `
      <li class="arch-edge-item${e.distinct ? " is-distinct" : ""}">
        <div class="arch-edge-pair">
          <a href="${escape(e.fromHref)}">${escape(e.from)}</a>
          <span class="arch-edge-arrow" aria-hidden="true">→</span>
          <a href="${escape(e.toHref)}">${escape(e.to)}</a>
          ${e.distinct ? '<span class="arch-edge-badge">keep distinct</span>' : ""}
        </div>
        <p>${escape(e.why)}</p>
      </li>`
    ).join("");
  }

  function renderDistinctions() {
    return DISTINCTIONS.map(
      (d) => `
      <article class="arch-distinction">
        <h4>${escape(d.title)}</h4>
        <p>${escape(d.body)}</p>
        <p class="arch-distinction-links">
          ${d.links
            .map((l) => `<a href="${escape(l.href)}">${escape(l.label)}</a>`)
            .join('<span class="sep">·</span>')}
        </p>
      </article>`
    ).join("");
  }

  function renderPage() {
    return `
<article class="topic-section arch-relationships-page visual-extra-page" id="${PAGE_ID}"
  data-title="Architecture Relationships" data-topic-index="-1" data-visual-extra="true">
  <header class="topic-header">
    <span class="topic-number">AR</span>
    <h2>Architecture Relationships</h2>
    <p class="arch-subtitle" lang="ar">خريطة العلاقات بين محاور التصميم والعمارة</p>
    <div class="topic-meta">
      <span class="badge">Visual / additional</span>
      <span class="badge">Overview map</span>
      <span class="badge">${NODES.length} linked areas</span>
    </div>
  </header>

  <div class="callout arch-page-callout">
    <strong>Visual / additional material.</strong>
    This page is an interactive map of relationships. It does <em>not</em> replace the original roadmap sections or the
    <a href="#cross-topic-relationships-and-study-notes">Cross-Topic Relationships &amp; Study Notes</a>.
    Use it to see the big picture, then study each pillar in its own section.
  </div>

  <p class="paragraph">
    Learners often treat OOD, PoEAA, DDD, Application Architecture, EIP, and System Design as isolated islands.
    They are related but <strong>not interchangeable</strong>: each owns a different concern. The map below shows
    how they connect while keeping important distinctions visible.
  </p>

  <aside class="diagram-panel visual-extra" data-diagram-key="architecture-relationships-map" id="architecture-relationships-map">
    <div class="diagram-header">
      <div>
        <h4>Architecture Relationship Map</h4>
        <p>Major areas and how they relate. Dashed edges mark “related but not the same.” Zoom or expand on small screens.</p>
      </div>
      <span class="diagram-tag">Visual / additional</span>
    </div>
    <div class="diagram-body">
      <div class="diagram-zoom" data-zoom="1" data-mermaid-src="architecture-relationships-map">
        <pre class="mermaid">${MERMAID_MAP}</pre>
      </div>
    </div>
    <div class="diagram-actions">
      <button type="button" data-action="zoom-in">Zoom in</button>
      <button type="button" data-action="zoom-out">Zoom out</button>
      <button type="button" data-action="zoom-reset">Reset</button>
      <button type="button" data-action="expand">Expand</button>
    </div>
  </aside>

  <section class="category" id="architecture-relationships-nodes" data-title="Area explanations">
    <h3>What each area owns</h3>
    <p class="paragraph">Click a card to jump to the matching roadmap section.</p>
    <div class="arch-node-grid">
      ${renderNodeCards()}
    </div>
  </section>

  <section class="category" id="architecture-relationships-edges" data-title="Why the connections exist">
    <h3>Why these connections exist</h3>
    <ul class="arch-edge-list">
      ${renderEdges()}
    </ul>
  </section>

  <section class="category" id="architecture-relationships-distinctions" data-title="Keep these distinct">
    <h3>Keep these distinct</h3>
    <div class="arch-distinction-grid">
      ${renderDistinctions()}
    </div>
  </section>

  <section class="category" id="architecture-relationships-study-path" data-title="Suggested reading order">
    <h3>Suggested reading path (not a strict dependency graph)</h3>
    <ol class="arch-path-list">
      <li><a href="#03-object-oriented-design-ood">OOD</a> (with <a href="#34-gof-design-patterns">GoF</a>) — object design foundations</li>
      <li><a href="#04-application-architecture">Application Architecture</a> — structure the whole application</li>
      <li><a href="#05-presentation-architecture">Presentation Architecture</a> — UI layer (parallel once app boundaries exist)</li>
      <li><a href="#06-patterns-of-enterprise-application-architecture-poeaa">PoEAA</a> — enterprise implementation patterns</li>
      <li><a href="#07-domain-driven-design-ddd">DDD</a> — <a href="#71-strategic-ddd">strategic</a> then <a href="#72-tactical-ddd">tactical</a></li>
      <li><a href="#09-enterprise-integration-patterns-eip">EIP</a> — message-based integration between apps/services</li>
      <li><a href="#10-system-design">System Design</a> — compose the above with scale, data, reliability, and ops</li>
    </ol>
    <p class="paragraph">
      Also see the original study notes:
      <a href="#ood-vs-poeaa-vs-ddd">OOD vs PoEAA vs DDD</a>,
      <a href="#application-architecture-vs-presentation-architecture">App vs Presentation</a>,
      <a href="#eip-vs-system-design">EIP vs System Design</a>.
    </p>
  </section>
</article>`;
  }

  function getSearchEntries() {
    const entries = [
      {
        kind: "heading",
        id: PAGE_ID,
        title: "Architecture Relationships",
        path: [],
        search: "architecture relationships ood poeaa ddd application eip system design overview map visual",
      },
      {
        kind: "heading",
        id: "architecture-relationships-nodes",
        title: "What each area owns",
        path: ["Architecture Relationships"],
        search: "architecture relationships nodes owns layers concerns",
      },
      {
        kind: "heading",
        id: "architecture-relationships-edges",
        title: "Why these connections exist",
        path: ["Architecture Relationships"],
        search: "architecture relationships edges connections why relate",
      },
      {
        kind: "heading",
        id: "architecture-relationships-distinctions",
        title: "Keep these distinct",
        path: ["Architecture Relationships"],
        search:
          "architecture relationships distinctions ood application presentation poeaa gof ddd strategic tactical eip realtime system design",
      },
      {
        kind: "heading",
        id: "architecture-relationships-study-path",
        title: "Suggested reading path",
        path: ["Architecture Relationships"],
        search: "architecture relationships study path reading order",
      },
    ];

    NODES.forEach((n) => {
      entries.push({
        kind: "concept",
        id: PAGE_ID + "--" + n.id,
        title: n.fullTitle + " — " + n.owns,
        path: ["Architecture Relationships", "What each area owns"],
        search: ("architecture relationships " + n.title + " " + n.fullTitle + " " + n.owns + " " + n.layer).toLowerCase(),
        jumpId: n.href.slice(1),
      });
    });

    DISTINCTIONS.forEach((d, i) => {
      entries.push({
        kind: "concept",
        id: PAGE_ID + "--distinction-" + i,
        title: d.title,
        path: ["Architecture Relationships", "Keep these distinct"],
        search: ("architecture relationships " + d.title + " " + d.body).toLowerCase(),
        jumpId: "architecture-relationships-distinctions",
      });
    });

    return entries;
  }

  function sidebarHtml() {
    return `
<li class="nav-item level-1 nav-special" data-nav-id="${PAGE_ID}" data-status="overview" data-always-show="true">
  <div class="nav-row">
    <button type="button" class="nav-toggle empty" aria-hidden="true"></button>
    <a class="nav-link" href="#${PAGE_ID}">
      <span class="nav-status overview" aria-hidden="true"></span>
      <span class="label">Architecture Relationships</span>
      <span class="nav-pill">Map</span>
    </a>
  </div>
</li>`;
  }

  function tocHtml() {
    return `
<li><a href="#${PAGE_ID}" class="depth-1 toc-special">Architecture Relationships</a></li>
<li><a href="#architecture-relationships-nodes" class="depth-3">What each area owns</a></li>
<li><a href="#architecture-relationships-edges" class="depth-3">Why connections exist</a></li>
<li><a href="#architecture-relationships-distinctions" class="depth-3">Keep these distinct</a></li>
<li><a href="#architecture-relationships-study-path" class="depth-3">Suggested reading path</a></li>`;
  }

  function wireDiagramActions(root) {
    const panel = (root || document).querySelector(
      `#${PAGE_ID} .diagram-panel[data-diagram-key="architecture-relationships-map"]`
    );
    if (!panel || panel.dataset.wired === "1") return;
    panel.dataset.wired = "1";
    panel.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-action]");
      if (!btn) return;
      const zoomEl = panel.querySelector(".diagram-zoom");
      let z = parseFloat(zoomEl.dataset.zoom || "1");
      const action = btn.dataset.action;
      if (action === "zoom-in") z = Math.min(2.5, z + 0.15);
      if (action === "zoom-out") z = Math.max(0.6, z - 0.15);
      if (action === "zoom-reset") z = 1;
      if (action === "expand") {
        panel.classList.toggle("expanded");
        if (panel.classList.contains("expanded")) {
          panel.style.position = "fixed";
          panel.style.inset = "5vh 5vw";
          panel.style.zIndex = "300";
          panel.style.maxHeight = "90vh";
          panel.style.overflow = "auto";
        } else {
          panel.style.position = "";
          panel.style.inset = "";
          panel.style.zIndex = "";
          panel.style.maxHeight = "";
          panel.style.overflow = "";
        }
      }
      zoomEl.dataset.zoom = String(z);
      zoomEl.style.transform = `scale(${z})`;
    });
  }

  global.ArchitectureRelationships = {
    PAGE_ID,
    MERMAID_MAP,
    NODES,
    EDGES,
    renderPage,
    getSearchEntries,
    sidebarHtml,
    tocHtml,
    wireDiagramActions,
  };
})(window);
