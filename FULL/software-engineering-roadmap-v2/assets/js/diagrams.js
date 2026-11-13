/**
 * Meaningful architecture diagrams (Mermaid + SVG).
 * Labeled as visual/additional material — distinct from original roadmap text.
 */
(function (global) {
  const DIAGRAMS = {
    "relationship-map": {
      sectionId: "cross-topic-relationships-and-study-notes",
      title: "Roadmap Topic Relationship Map",
      explanation:
        "How major pillars relate without merging distinct areas. OOD ≠ App Arch ≠ Presentation; PoEAA ≠ GoF; DDD strategic ≠ tactical; concurrency ≠ EIP ≠ realtime; DB concurrency ≠ app concurrency; System Design connects but does not replace the others.",
      mermaid: `flowchart TB
  subgraph Foundations["Phase 1 — Foundations"]
    DSA["01 DSA"]
    DBMS["02 DBMS"]
    OOD["03 OOD / GoF"]
  end
  subgraph Design["Phase 2 — Design & Architecture"]
    AppArch["04 Application Architecture"]
    PresArch["05 Presentation Architecture"]
    PoEAA["06 PoEAA"]
    DDD["07 DDD"]
  end
  subgraph ConcInt["Phase 3 — Concurrency & Integration"]
    Conc["08 Concurrency Patterns"]
    EIP["09 EIP"]
  end
  subgraph Dist["Phase 4"]
    SD["10 System Design"]
  end
  Support["Supporting Foundations\\nSE Practices · OS · Networking"]

  DSA -.-> OOD
  DBMS -.-> PoEAA
  OOD --> AppArch
  OOD --> PoEAA
  AppArch --> PresArch
  AppArch --> DDD
  PoEAA --> DDD
  AppArch --> Conc
  DBMS -.->|"DB concurrency ≠ app concurrency"| Conc
  Conc --> EIP
  EIP --> SD
  AppArch --> SD
  DDD --> SD
  Support -.-> Foundations
  Support -.-> Design
  Support -.-> ConcInt
  Support -.-> Dist

  classDef distinct fill:#e8f4f3,stroke:#0d6e6e,color:#1a2332
  class DSA,DBMS,OOD,AppArch,PresArch,PoEAA,DDD,Conc,EIP,SD,Support distinct`,
    },

    "app-layered": {
      sectionId: "41-architectural-styles",
      title: "Layered Architecture — Dependency Direction",
      explanation:
        "Classic N-tier layering. Dependencies point inward/downward toward lower layers; upper layers know about lower ones, not the reverse.",
      mermaid: `flowchart TB
  UI["Presentation / UI Layer"]
  APP["Application / Service Layer"]
  DOM["Domain / Business Layer"]
  INF["Infrastructure / Data Layer"]
  UI --> APP --> DOM --> INF
  style UI fill:#dbeafe,stroke:#1d5fbf
  style APP fill:#ccfbf1,stroke:#0d6e6e
  style DOM fill:#fef3c7,stroke:#9a6700
  style INF fill:#e2e8f0,stroke:#475569`,
    },

    "app-clean-hex-onion": {
      sectionId: "42-architectural-patterns",
      title: "Clean / Hexagonal / Onion — Ports & Adapters",
      explanation:
        "Shared idea: domain at the center; adapters implement ports at the edges. Dependency rule: source code dependencies point toward the domain.",
      mermaid: `flowchart TB
  subgraph Outer["Adapters (Frameworks, DB, UI, APIs)"]
    Web["Web / UI Adapter"]
    DB["Persistence Adapter"]
    Ext["External API Adapter"]
  end
  subgraph Ports["Ports (Interfaces)"]
    InPort["Inbound Ports\\n(use cases)"]
    OutPort["Outbound Ports\\n(repositories, gateways)"]
  end
  subgraph Core["Domain / Entities / Use Cases"]
    Domain["Domain Model"]
  end
  Web --> InPort --> Domain
  Domain --> OutPort
  OutPort --> DB
  OutPort --> Ext
  style Domain fill:#ccfbf1,stroke:#0d6e6e
  style InPort fill:#e0f2fe,stroke:#0369a1
  style OutPort fill:#e0f2fe,stroke:#0369a1`,
    },

    "presentation-mvc-family": {
      sectionId: "51-core-architectural-patterns",
      title: "MVC · MVP · MVVM Interaction Flows",
      explanation:
        "Same Model/View concern split, different mediation: Controller (MVC), Presenter (MVP), ViewModel + binding (MVVM).",
      mermaid: `flowchart LR
  subgraph MVC["MVC"]
    V1[View] -->|user action| C[Controller]
    C --> M1[Model]
    M1 -->|update| V1
  end
  subgraph MVP["MVP"]
    V2[View] <-->|passive view| P[Presenter]
    P --> M2[Model]
  end
  subgraph MVVM["MVVM"]
    V3[View] <-->|data binding| VM[ViewModel]
    VM --> M3[Model]
  end`,
    },

    "presentation-mvi-flux": {
      sectionId: "53-modern-frontend-and-component-architectures",
      title: "MVI & Flux / Redux Unidirectional Flow",
      explanation:
        "Intent/action in, single state out. Unidirectional data flow reduces ad-hoc two-way mutation.",
      mermaid: `flowchart LR
  Intent[Intent / Action] --> Reducer[Reducer / Processor]
  Reducer --> State[Immutable State]
  State --> View[View / UI]
  View --> Intent
  style State fill:#ccfbf1,stroke:#0d6e6e`,
    },

    "ddd-strategic": {
      sectionId: "71-strategic-ddd",
      title: "Strategic DDD — Bounded Contexts & Context Map",
      explanation:
        "Strategic design draws boundaries (Bounded Contexts) and defines relationships on a Context Map — distinct from tactical building blocks.",
      mermaid: `flowchart TB
  subgraph Domain["Domain"]
    Core["Core Domain"]
    Support["Supporting Subdomain"]
    Generic["Generic Subdomain"]
  end
  BC1["Bounded Context A\\n(Orders)"]
  BC2["Bounded Context B\\n(Payments)"]
  BC3["Bounded Context C\\n(Catalog)"]
  Core --- BC1
  Support --- BC2
  Generic --- BC3
  BC1 -->|"Customer-Supplier"| BC2
  BC1 -->|"Anti-Corruption Layer"| BC3
  BC2 -.->|"Published Language / OHS"| Ext["External Partner"]
  style Core fill:#ccfbf1,stroke:#0d6e6e
  style BC1 fill:#e0f2fe,stroke:#0369a1
  style BC2 fill:#fef3c7,stroke:#9a6700`,
    },

    "ddd-tactical": {
      sectionId: "72-tactical-ddd",
      title: "Tactical DDD Building Blocks",
      explanation:
        "Tactical patterns model behavior inside a Bounded Context. Strategic ≠ tactical — both are required for full DDD practice.",
      mermaid: `flowchart TB
  AR["Aggregate Root"] --> E1[Entity]
  AR --> VO[Value Objects]
  AR --> Inv["Invariants"]
  Repo[Repository] --> AR
  Factory[Factory] --> AR
  DS[Domain Service] --> AR
  AR --> DE[Domain Events]
  AS[Application Service] --> Repo
  AS --> DS
  style AR fill:#ccfbf1,stroke:#0d6e6e`,
    },

    "concurrency-overview": {
      sectionId: "08-concurrency-patterns",
      title: "Curated Concurrency Patterns",
      explanation:
        "Ten core patterns for task execution, synchronization, thread safety, and event-driven concurrency — distinct from DB isolation and EIP messaging.",
      mermaid: `flowchart TB
  Q["Concurrency Patterns"]
  Q --> PC["Producer–Consumer"]
  Q --> TP["Thread Pool"]
  Q --> FP["Future / Promise"]
  Q --> RWL["Read–Write Lock"]
  Q --> MCV["Monitor / Condition Variable"]
  Q --> TC["Thread Confinement"]
  Q --> FJ["Fork–Join"]
  Q --> R["Reactor"]
  Q --> BS["Barrier Synchronization"]
  Q --> AO["Active Object"]
  style Q fill:#ccfbf1,stroke:#0d6e6e`,
    },


    "eip-messaging": {
      sectionId: "09-enterprise-integration-patterns-eip",
      title: "EIP Messaging & Delivery",
      explanation:
        "Messages move over channels, are translated, and use request–reply plus reliability patterns (competing consumers, dead letter, idempotent receiver, outbox).",
      mermaid: `flowchart LR
  AppA[Application A] --> CH[Message Channel]
  CH --> Trans[Message Translator]
  Trans --> RR[Request–Reply]
  RR --> CC[Competing Consumers]
  CC --> IR[Idempotent Receiver]
  IR --> AppB[Application B]
  CC -.-> DLC[Dead Letter Channel]
  AppA -.-> Outbox[Transactional Outbox]
  Outbox -.-> CH
  style CH fill:#e0f2fe,stroke:#0369a1
  style RR fill:#ccfbf1,stroke:#0d6e6e`,
    },


    "eip-routing": {
      sectionId: "09-enterprise-integration-patterns-eip",
      title: "Message Routing Patterns",
      explanation:
        "Content-based routing, split, and aggregate decide who receives which messages in the curated EIP set.",
      mermaid: `flowchart TB
  In[Incoming Message] --> CBR{Content-Based\nRouter}
  CBR -->|type A| A[Service A]
  CBR -->|type B| Split[Splitter]
  Split --> W1[Worker 1]
  Split --> W2[Worker 2]
  W1 --> Agg[Aggregator]
  W2 --> Agg
  Agg --> Out[Outbound Message]`,
    },


    "system-design-stack": {
      sectionId: "10-system-design",
      title: "System Design Concern Stack",
      explanation:
        "System Design composes networking, storage, caching, scale, reliability, security, and ops. It uses EIP/concurrency/architecture — it does not replace them.",
      mermaid: `flowchart TB
  Clients[Clients / CDN / DNS] --> Edge[API Gateway / LB]
  Edge --> Services[Stateless Services]
  Services --> Cache[Cache Layer]
  Services --> Queue[Async Messaging]
  Services --> DB[(Primary DB)]
  DB --> Replicas[(Read Replicas)]
  Queue --> Workers[Workers / Consumers]
  Services --> Obs[Observability]
  style Services fill:#ccfbf1,stroke:#0d6e6e
  style Queue fill:#e0f2fe,stroke:#0369a1`,
    },

    "realtime-comms": {
      sectionId: "102-networking-and-communication",
      title: "Real-Time Communication Options",
      explanation:
        "Additional visual: how common realtime approaches differ in connection model and push vs poll. Complements — does not replace — the networking topic list.",
      mermaid: `flowchart TB
  Client[Client]
  Client -->|"request/response"| REST[HTTP REST / gRPC]
  Client -->|"hold until event"| LP[Long Polling]
  Client -->|"full-duplex"| WS[WebSockets]
  Client -->|"server push"| SSE[SSE-style push]
  WS --> Hub[Realtime Hub / Gateway]
  Hub --> Svc[Backend Services]
  style WS fill:#ccfbf1,stroke:#0d6e6e`,
    },

    "ood-vs-others": {
      sectionId: "ood-vs-poeaa-vs-ddd",
      title: "OOD vs PoEAA vs DDD (Distinct Lenses)",
      explanation:
        "Visual reminder from the study notes: complementary lenses, not substitutes.",
      mermaid: `flowchart LR
  OOD["OOD\\nObjects, responsibilities,\\nGoF reuse"]
  PoEAA["PoEAA\\nEnterprise app\\nimplementation patterns"]
  DDD["DDD\\nDomain understanding\\n& boundaries"]
  OOD -.->|"complements"| PoEAA
  PoEAA -.->|"complements"| DDD
  OOD -.->|"complements"| DDD
  style OOD fill:#e0f2fe,stroke:#0369a1
  style PoEAA fill:#fef3c7,stroke:#9a6700
  style DDD fill:#ccfbf1,stroke:#0d6e6e`,
    },

    // Source of truth for retheme; page HTML is rendered by architecture-relationships.js
    "architecture-relationships-map": {
      sectionId: "architecture-relationships",
      title: "Architecture Relationship Map",
      explanation:
        "Big-picture map of OOD, PoEAA, DDD, Application Architecture, EIP, and System Design — related without merging.",
      mermaid: null, // filled from ArchitectureRelationships.MERMAID_MAP at init
      skipInject: true,
    },
  };

  function resolveMermaid(def) {
    if (def.mermaid) return def.mermaid;
    if (
      keyIsArchMap(def) &&
      global.ArchitectureRelationships &&
      global.ArchitectureRelationships.MERMAID_MAP
    ) {
      return global.ArchitectureRelationships.MERMAID_MAP;
    }
    return "";
  }

  function keyIsArchMap(def) {
    return def.sectionId === "architecture-relationships" && def.skipInject;
  }

  function injectDiagramPlaceholders() {
    if (
      DIAGRAMS["architecture-relationships-map"] &&
      global.ArchitectureRelationships
    ) {
      DIAGRAMS["architecture-relationships-map"].mermaid =
        global.ArchitectureRelationships.MERMAID_MAP;
    }

    Object.entries(DIAGRAMS).forEach(([key, def]) => {
      if (def.skipInject) return;
      const host = document.getElementById(def.sectionId);
      if (!host) return;
      const panel = document.createElement("aside");
      panel.className = "diagram-panel visual-extra";
      panel.dataset.diagramKey = key;
      panel.innerHTML = `
        <div class="diagram-header">
          <div>
            <h4>${escape(def.title)}</h4>
            <p>${escape(def.explanation)}</p>
          </div>
          <span class="diagram-tag">Visual / additional</span>
        </div>
        <div class="diagram-body">
          <div class="diagram-zoom" data-zoom="1">
            <pre class="mermaid">${def.mermaid}</pre>
          </div>
        </div>
        <div class="diagram-actions">
          <button type="button" data-action="zoom-in">Zoom in</button>
          <button type="button" data-action="zoom-out">Zoom out</button>
          <button type="button" data-action="zoom-reset">Reset</button>
          <button type="button" data-action="expand">Expand</button>
        </div>`;
      // Prefer after header / early in section
      const header =
        host.querySelector(".topic-header") ||
        host.querySelector(":scope > h3") ||
        host.querySelector(":scope > h4");
      if (header && header.nextSibling) {
        header.parentNode.insertBefore(panel, header.nextSibling);
      } else {
        host.insertBefore(panel, host.firstChild);
      }
    });

    document.querySelectorAll(".diagram-panel").forEach((panel) => {
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
    });
  }

  function escape(s) {
    return String(s)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  let mermaidWaitNotified = false;

  async function renderMermaid() {
    if (!global.mermaid) {
      // Soft wait note once; removed when CDN arrives. Avoid permanent false failure.
      if (!mermaidWaitNotified) {
        mermaidWaitNotified = true;
        document.querySelectorAll(".diagram-body").forEach((body) => {
          if (body.querySelector(".cdn-note")) return;
          const note = document.createElement("p");
          note.className = "cdn-note cdn-note-waiting";
          note.textContent = "Loading diagrams…";
          body.appendChild(note);
        });
        // If Mermaid never arrives, upgrade message after a delay
        setTimeout(() => {
          if (global.mermaid) return;
          document.querySelectorAll(".cdn-note-waiting").forEach((note) => {
            note.classList.remove("cdn-note-waiting");
            note.textContent =
              "Mermaid.js CDN could not be loaded. Diagram source is still present in the page; open online or vendor Mermaid locally to render.";
          });
        }, 8000);
      }
      return;
    }
    document.querySelectorAll(".cdn-note").forEach((n) => n.remove());
    const theme = document.documentElement.getAttribute("data-theme") === "dark" ? "dark" : "default";
    mermaid.initialize({
      startOnLoad: false,
      theme: theme === "dark" ? "dark" : "neutral",
      securityLevel: "loose",
      flowchart: { htmlLabels: true, curve: "basis" },
    });
    try {
      await mermaid.run({ querySelector: ".diagram-panel .mermaid" });
    } catch (e) {
      console.warn("Mermaid render issue", e);
    }
  }

  let placeholdersReady = false;

  async function initDiagrams() {
    if (!placeholdersReady) {
      injectDiagramPlaceholders();
      placeholdersReady = true;
    }
    await renderMermaid();
  }

  /** Called when Mermaid CDN finishes loading after first paint. */
  async function onMermaidReady() {
    if (!placeholdersReady) {
      injectDiagramPlaceholders();
      placeholdersReady = true;
    }
    await renderMermaid();
  }

  async function rethemeDiagrams() {
    // Re-render mermaid on theme change
    document.querySelectorAll(".diagram-panel .diagram-zoom").forEach((z) => {
      const key = z.closest(".diagram-panel")?.dataset.diagramKey;
      const def = DIAGRAMS[key];
      let src = def ? resolveMermaid(def) : "";
      if (!src && global.ArchitectureRelationships && key === "architecture-relationships-map") {
        src = global.ArchitectureRelationships.MERMAID_MAP;
      }
      if (!src) return;
      z.innerHTML = `<pre class="mermaid">${src}</pre>`;
    });
    await renderMermaid();
  }

  global.RoadmapDiagrams = {
    initDiagrams,
    onMermaidReady,
    rethemeDiagrams,
    DIAGRAMS,
  };
})(window);
