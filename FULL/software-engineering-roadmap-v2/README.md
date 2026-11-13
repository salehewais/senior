# Software Engineering Master Roadmap — Interactive Learning Site

Static, offline-friendly HTML learning website generated from `Software_Engineering_Master_Roadmap.md`.

## How to run

Open the site locally (no build step, no backend):

```bash
# Option A — open the file directly
xdg-open software-engineering-roadmap/index.html
# or double-click index.html

# Option B — local static server (recommended if browser blocks file:// modules/CDN)
cd software-engineering-roadmap
python3 -m http.server 8765
# then visit http://localhost:8765/
```

Works by opening `index.html`. Mermaid diagrams load from a CDN; if offline, diagram source remains in the page and a fallback note is shown.

## How to customize

| Goal | What to edit |
|---|---|
| Update roadmap text | Edit `../Software_Engineering_Master_Roadmap.md`, then re-run `python3 scripts/parse_roadmap.py` |
| Visual theme / colors | `assets/css/themes.css` (CSS variables; light + dark) |
| Layout / typography | `assets/css/styles.css`, `assets/css/responsive.css` |
| Progress / search / nav behavior | `assets/js/progress.js`, `search.js`, `navigation.js`, `app.js` |
| Architecture diagrams | `assets/js/diagrams.js` (tagged as visual/additional material) |
| Architecture Relationships overview page | `assets/js/architecture-relationships.js` (visual/IA map; sidebar “Map” item) |
| Clear saved progress | DevTools → Application → Local Storage → remove `se-roadmap-progress-v1` |

## Architecture & implementation decisions

**Content / presentation separation**

- `data/roadmap-content.js` holds the entire structured roadmap (headings, notes, nested lists, trackable concept IDs).
- `scripts/parse_roadmap.py` parses the Markdown into that data file so content updates stay mechanical and complete.
- `assets/js/app.js` renders the DOM from data; CSS never owns content.

**UI shell**

- Sticky header: title, subtitle, search, overall progress, study mode, theme toggle.
- Collapsible hierarchical sidebar with counts + completion indicators + status filters.
- Main article per H1 topic; nested categories for H2–H4.
- Right TOC on wide screens; mobile drawer sidebar.
- Study mode: hides chrome, focuses one topic, prev/next.

**Interactions**

- Progress checkboxes persist in `localStorage` (`se-roadmap-progress-v1`).
- Instant client-side search across headings + concepts.
- Smooth scroll, breadcrumbs, back-to-top, hash navigation.
- Light/dark theme persisted separately (`se-roadmap-theme`).

**Diagrams**

- Mermaid.js via CDN (`mermaid@11` ESM).
- Additional relationship/architecture visuals are explicitly labeled **Visual / additional** so they never replace original roadmap text.
- Covers: topic relationship map, layered/clean/hexagonal, MVC family, MVI/Flux, DDD strategic/tactical, concurrency families, EIP messaging/routing, system design stack, realtime communication.

**Architecture Relationships page (visual / IA)**

- Dedicated overview section `#architecture-relationships` (sidebar top “Map” item + TOC).
- Interactive Mermaid map linking OOD, GoF, PoEAA, DDD Strategic/Tactical, Application Architecture, Presentation Architecture, EIP, Real-Time Communication, and System Design.
- Node cards and edge explanations navigate to the corresponding original roadmap sections.
- Marked **Visual / additional** — does not replace Cross-Topic Relationships & Study Notes or any original Markdown content.
- Included in client-side search; works with study mode / hash navigation / theme toggle.

**Design**

- Premium technical docs look (Linear/GitBook-like).
- Fonts: Source Serif 4 (display) + IBM Plex Sans/Mono.
- Teal/slate token system; light + dark; subtle pattern background; minimal motion.

## Validation summary (pre-release)

| Check | Result |
|---|---|
| Original headings represented | **130** inventory headings → **128** section headings in site + doc title/subtitle in header/meta (**0 missing**) |
| List / pattern / problem items | **978 / 978** preserved |
| Trackable concepts | **978** |
| Main H1 topics | **14** (Overview → Strategy) |
| Nav / search / progress / theme | Implemented; progress persists across refresh |
| Diagram section anchors | All diagram targets resolve |
| Architecture Relationships page | Visual overview at `#architecture-relationships` (sidebar + search); links into original sections |
| Local open | `index.html` + optional `python3 -m http.server` |

## Known limitations

- Mermaid requires network access to the jsDelivr CDN unless you vendor the library under `assets/js/`. Offline: content and SVG placeholders still work; diagrams show a fallback note.
- Google Fonts CDN is used for typography; system fallbacks apply if blocked.
- Opening via `file://` may restrict ES module CDN imports in some browsers — use a local static server if diagrams do not render.
- Diagrams and the Architecture Relationships page are explanatory / IA additions; they are not part of the original Markdown.
- Mermaid node `click` navigation depends on CDN Mermaid with `securityLevel: "loose"`; node cards and edge links remain available if click handlers do not attach.

## Project structure

```
software-engineering-roadmap/
├── index.html
├── README.md
├── assets/css/{styles,themes,responsive}.css
├── assets/js/{app,navigation,search,progress,diagrams,architecture-relationships}.js
├── assets/images/
├── data/roadmap-content.js
├── data/content-inventory.json
├── data/coverage-report-table.md
└── scripts/parse_roadmap.py
```

## CONTENT COVERAGE REPORT

Mapping of every original Markdown heading (plus document title/subtitle/intro note) to website locations. Full checklist used for release validation.

| Original Markdown section | Website location |
|---|---|
| `# Software Engineering Master Roadmap` (doc title) | Header title + `document.title` |
| `## A structured roadmap…` (subtitle) | Header subtitle; full original subtitle in meta/intro |
| Intro note (blockquote after title) | Intro banner blockquote |
| *(site addition)* Architecture Relationships overview map | Main `#architecture-relationships` · sidebar (top “Map”) · TOC · search — **Visual / additional**, not from Markdown |
| `# Roadmap Overview` | Main `#roadmap-overview` · sidebar · TOC |
| `## Phase 1 — Engineering Foundations` | Main `#phase-1-engineering-foundations` · sidebar · TOC |
| `## Phase 2 — Software Design & Architecture` | Main `#phase-2-software-design-and-architecture` · sidebar · TOC |
| `## Phase 3 — Concurrency & Integration` | Main `#phase-3-concurrency-and-integration` · sidebar · TOC |
| `## Phase 4 — Distributed Systems & System Architecture` | Main `#phase-4-distributed-systems-and-system-architecture` · sidebar · TOC |
| `## Supporting Foundations (study alongside the roadmap)` | Main `#supporting-foundations-study-alongside-the-roadmap` · sidebar · TOC |
| `# 01 — Problem Solving & Data Structures & Algorithms (DSA)` | Main `#01-problem-solving-and-data-structures-and-algorithms-dsa` · sidebar · TOC |
| `## 1.1 Complexity Analysis` | Main `#11-complexity-analysis` · sidebar · TOC |
| `## 1.2 Fundamental Data Structures` | Main `#12-fundamental-data-structures` · sidebar · TOC |
| `## 1.3 Advanced Data Structures` | Main `#13-advanced-data-structures` · sidebar · TOC |
| `## 1.4 Core Problem-Solving Patterns & Techniques` | Main `#14-core-problem-solving-patterns-and-techniques` · sidebar · TOC |
| `## 1.5 Recursion Roadmap & Problem Tracker` | Main `#15-recursion-roadmap-and-problem-tracker` · sidebar · TOC |
| `### A. Recursion (العودية)` | Main `#a-recursion-العودية` · sidebar · TOC |
| `#### Common Problems` | Main `#a-recursion-العودية-common-problems` · sidebar · TOC |
| `#### Training Path` | Main `#a-recursion-العودية-training-path` · sidebar · TOC |
| `### B. Trees (الأشجار)` | Main `#b-trees-الأشجار` · sidebar · TOC |
| `#### Common Problems` | Main `#b-trees-الأشجار-common-problems` · sidebar · TOC |
| `### C. Backtracking (التراجع)` | Main `#c-backtracking-التراجع` · sidebar · TOC |
| `#### Core Problems` | Main `#c-backtracking-التراجع-core-problems` · sidebar · TOC |
| `#### Additional Problems` | Main `#c-backtracking-التراجع-additional-problems` · sidebar · TOC |
| `### D. Dynamic Programming (البرمجة الديناميكية)` | Main `#d-dynamic-programming-البرمجة-الديناميكية` · sidebar · TOC |
| `#### Common Problems` | Main `#d-dynamic-programming-البرمجة-الديناميكية-common-problems` · sidebar · TOC |
| `### E. Graphs (الرسوم البيانية)` | Main `#e-graphs-الرسوم-البيانية` · sidebar · TOC |
| `#### Common Problems` | Main `#e-graphs-الرسوم-البيانية-common-problems` · sidebar · TOC |
| `# 02 — DBMS & Data Management` | Main `#02-dbms-and-data-management` · sidebar · TOC |
| `## 2.1 Core Concepts & Architecture` | Main `#21-core-concepts-and-architecture` · sidebar · TOC |
| `## 2.2 Relational Database Design` | Main `#22-relational-database-design` · sidebar · TOC |
| `## 2.3 Transactions & Concurrency Control` | Main `#23-transactions-and-concurrency-control` · sidebar · TOC |
| `## 2.4 Storage, Indexing & Query Performance` | Main `#24-storage-indexing-and-query-performance` · sidebar · TOC |
| `## 2.5 Distributed Databases & Scaling` | Main `#25-distributed-databases-and-scaling` · sidebar · TOC |
| `## 2.6 Database Types & Engines` | Main `#26-database-types-and-engines` · sidebar · TOC |
| `### Relational Databases (SQL)` | Main `#relational-databases-sql` · sidebar · TOC |
| `### Non-Relational Databases (NoSQL)` | Main `#non-relational-databases-nosql` · sidebar · TOC |
| `# 03 — Object-Oriented Design (OOD)` | Main `#03-object-oriented-design-ood` · sidebar · TOC |
| `## 3.1 OOP Fundamentals` | Main `#31-oop-fundamentals` · sidebar · TOC |
| `## 3.2 Object Relationships` | Main `#32-object-relationships` · sidebar · TOC |
| `## 3.3 Design Principles` | Main `#33-design-principles` · sidebar · TOC |
| `### SOLID Principles` | Main `#solid-principles` · sidebar · TOC |
| `### General Principles` | Main `#general-principles` · sidebar · TOC |
| `## 3.4 GoF Design Patterns` | Main `#34-gof-design-patterns` · sidebar · TOC |
| `### Creational Patterns (5)` | Main `#creational-patterns-5` · sidebar · TOC |
| `### Structural Patterns (7)` | Main `#structural-patterns-7` · sidebar · TOC |
| `### Behavioral Patterns (11)` | Main `#behavioral-patterns-11` · sidebar · TOC |
| `## 3.5 UML & Object Modeling` | Main `#35-uml-and-object-modeling` · sidebar · TOC |
| `# 04 — Application Architecture` | Main `#04-application-architecture` · sidebar · TOC |
| `## 4.1 Architectural Styles` | Main `#41-architectural-styles` · sidebar · TOC |
| `## 4.2 Architectural Patterns` | Main `#42-architectural-patterns` · sidebar · TOC |
| `## 4.3 Core Concepts & Principles` | Main `#43-core-concepts-and-principles` · sidebar · TOC |
| `## 4.4 Application Organization` | Main `#44-application-organization` · sidebar · TOC |
| `## 4.5 Integration Architecture` | Main `#45-integration-architecture` · sidebar · TOC |
| `# 05 — Presentation Architecture` | Main `#05-presentation-architecture` · sidebar · TOC |
| `## 5.1 Core Architectural Patterns` | Main `#51-core-architectural-patterns` · sidebar · TOC |
| `## 5.2 Advanced & Mobile-Specific Patterns` | Main `#52-advanced-and-mobile-specific-patterns` · sidebar · TOC |
| `## 5.3 Modern Frontend & Component Architectures` | Main `#53-modern-frontend-and-component-architectures` · sidebar · TOC |
| `## 5.4 State Management & Reactive Patterns` | Main `#54-state-management-and-reactive-patterns` · sidebar · TOC |
| `## 5.5 Core Concepts & Mechanisms` | Main `#55-core-concepts-and-mechanisms` · sidebar · TOC |
| `# 06 — Patterns of Enterprise Application Architecture (PoEAA)` | Main `#06-patterns-of-enterprise-application-architecture-poeaa` · sidebar · TOC |
| `## 6.1 Domain Logic Patterns (4)` | Main `#61-domain-logic-patterns-4` · sidebar · TOC |
| `## 6.2 Data Source Architectural Patterns (4)` | Main `#62-data-source-architectural-patterns-4` · sidebar · TOC |
| `## 6.3 Object-Relational Behavioral Patterns (3)` | Main `#63-object-relational-behavioral-patterns-3` · sidebar · TOC |
| `## 6.4 Object-Relational Structural Patterns` | Main `#64-object-relational-structural-patterns` · sidebar · TOC |
| `## 6.5 Object-Relational Metadata Mapping Patterns (3)` | Main `#65-object-relational-metadata-mapping-patterns-3` · sidebar · TOC |
| `## 6.6 Web Presentation Patterns (7)` | Main `#66-web-presentation-patterns-7` · sidebar · TOC |
| `## 6.7 Distribution Patterns (2)` | Main `#67-distribution-patterns-2` · sidebar · TOC |
| `## 6.8 Offline Concurrency Patterns (4)` | Main `#68-offline-concurrency-patterns-4` · sidebar · TOC |
| `## 6.9 Session State Patterns (3)` | Main `#69-session-state-patterns-3` · sidebar · TOC |
| `## 6.10 Base Patterns (11)` | Main `#610-base-patterns-11` · sidebar · TOC |
| `# 07 — Domain-Driven Design (DDD)` | Main `#07-domain-driven-design-ddd` · sidebar · TOC |
| `## 7.1 Strategic DDD` | Main `#71-strategic-ddd` · sidebar · TOC |
| `### Domain Understanding` | Main `#domain-understanding` · sidebar · TOC |
| `### Model Boundaries` | Main `#model-boundaries` · sidebar · TOC |
| `### Context Mapping Patterns` | Main `#context-mapping-patterns` · sidebar · TOC |
| `## 7.2 Tactical DDD` | Main `#72-tactical-ddd` · sidebar · TOC |
| `## 7.3 DDD Implementation & Modeling Concepts` | Main `#73-ddd-implementation-and-modeling-concepts` · sidebar · TOC |
| `# 08 — Concurrency Patterns` | Main `#08-concurrency-patterns` · sidebar · TOC |
| `## 8.1 Task Execution & Scheduling` | Main `#81-task-execution-and-scheduling` · sidebar · TOC |
| `## 8.2 Synchronization Patterns` | Main `#82-synchronization-patterns` · sidebar · TOC |
| `## 8.3 Coordination & Synchronization Primitives` | Main `#83-coordination-and-synchronization-primitives` · sidebar · TOC |
| `## 8.4 Event Handling & Asynchronous Architecture` | Main `#84-event-handling-and-asynchronous-architecture` · sidebar · TOC |
| `## 8.5 Parallel Computing Patterns` | Main `#85-parallel-computing-patterns` · sidebar · TOC |
| `## 8.6 Shared State & Thread Safety` | Main `#86-shared-state-and-thread-safety` · sidebar · TOC |
| `## 8.7 Flow Control & Performance` | Main `#87-flow-control-and-performance` · sidebar · TOC |
| `## 8.8 Distributed Concurrency Patterns` | Main `#88-distributed-concurrency-patterns` · sidebar · TOC |
| `# 09 — Enterprise Integration Patterns (EIP)` | Main `#09-enterprise-integration-patterns-eip` · sidebar · TOC |
| `## 9.1 Messaging Systems` | Main `#91-messaging-systems` · sidebar · TOC |
| `## 9.2 Messaging Channels` | Main `#92-messaging-channels` · sidebar · TOC |
| `## 9.3 Message Construction` | Main `#93-message-construction` · sidebar · TOC |
| `## 9.4 Message Routing` | Main `#94-message-routing` · sidebar · TOC |
| `## 9.5 Message Transformation` | Main `#95-message-transformation` · sidebar · TOC |
| `## 9.6 Messaging Endpoints` | Main `#96-messaging-endpoints` · sidebar · TOC |
| `## 9.7 System Management` | Main `#97-system-management` · sidebar · TOC |
| `## 9.8 Complementary Integration & Messaging Patterns` | Main `#98-complementary-integration-and-messaging-patterns` · sidebar · TOC |
| `### Reliability & Delivery` | Main `#reliability-and-delivery` · sidebar · TOC |
| `### Event-Driven Integration` | Main `#event-driven-integration` · sidebar · TOC |
| `### Distributed Workflow & Coordination` | Main `#distributed-workflow-and-coordination` · sidebar · TOC |
| `### Observability & Operations` | Main `#observability-and-operations` · sidebar · TOC |
| `## 9.9 Integration Concepts to Understand` | Main `#99-integration-concepts-to-understand` · sidebar · TOC |
| `# 10 — System Design` | Main `#10-system-design` · sidebar · TOC |
| `## 10.1 System Design Fundamentals` | Main `#101-system-design-fundamentals` · sidebar · TOC |
| `## 10.2 Networking & Communication` | Main `#102-networking-and-communication` · sidebar · TOC |
| `## 10.3 Data Storage (Databases)` | Main `#103-data-storage-databases` · sidebar · TOC |
| `### Relational Databases` | Main `#relational-databases` · sidebar · TOC |
| `### NoSQL Databases` | Main `#nosql-databases` · sidebar · TOC |
| `### CAP Theorem` | Main `#cap-theorem` · sidebar · TOC |
| `### Database Design` | Main `#database-design` · sidebar · TOC |
| `## 10.4 Caching` | Main `#104-caching` · sidebar · TOC |
| `## 10.5 Scalability Patterns` | Main `#105-scalability-patterns` · sidebar · TOC |
| `## 10.6 Distributed Systems Concepts` | Main `#106-distributed-systems-concepts` · sidebar · TOC |
| `## 10.7 Messaging & Async Processing` | Main `#107-messaging-and-async-processing` · sidebar · TOC |
| `## 10.8 Microservices Architecture` | Main `#108-microservices-architecture` · sidebar · TOC |
| `## 10.9 Security` | Main `#109-security` · sidebar · TOC |
| `## 10.10 High Availability & Reliability` | Main `#1010-high-availability-and-reliability` · sidebar · TOC |
| `## 10.11 Observability & Monitoring` | Main `#1011-observability-and-monitoring` · sidebar · TOC |
| `## 10.12 Design Patterns (System Level)` | Main `#1012-design-patterns-system-level` · sidebar · TOC |
| `## 10.13 Data Processing` | Main `#1013-data-processing` · sidebar · TOC |
| `## 10.14 Cloud & Infrastructure` | Main `#1014-cloud-and-infrastructure` · sidebar · TOC |
| `## 10.15 Common System Design Interview Problems` | Main `#1015-common-system-design-interview-problems` · sidebar · TOC |
| `# Supporting Foundations` | Main `#supporting-foundations` · sidebar · TOC |
| `## A. Software Engineering Practices` | Main `#a-software-engineering-practices` · sidebar · TOC |
| `## B. Operating Systems Fundamentals` | Main `#b-operating-systems-fundamentals` · sidebar · TOC |
| `## C. Computer Networking Fundamentals` | Main `#c-computer-networking-fundamentals` · sidebar · TOC |
| `# Cross-Topic Relationships & Study Notes` | Main `#cross-topic-relationships-and-study-notes` · sidebar · TOC |
| `## OOD vs PoEAA vs DDD` | Main `#ood-vs-poeaa-vs-ddd` · sidebar · TOC |
| `## Application Architecture vs Presentation Architecture` | Main `#application-architecture-vs-presentation-architecture` · sidebar · TOC |
| `## Concurrency vs EIP` | Main `#concurrency-vs-eip` · sidebar · TOC |
| `## EIP vs System Design` | Main `#eip-vs-system-design` · sidebar · TOC |
| `## Suggested Practical Project` | Main `#suggested-practical-project` · sidebar · TOC |
| `# Recommended Study Strategy` | Main `#recommended-study-strategy` · sidebar · TOC |
### Concept / list coverage

- Every nested list item from the Markdown (DSA problem trackers, GoF patterns, PoEAA catalogs, EIP catalogs, System Design interview problems, Supporting Foundations, etc.) is present as a trackable concept checkbox in the corresponding section.
- Blockquotes and Arabic callout questions under Concurrency are preserved as callouts/blockquotes.
- Cross-topic study notes and the 10-question study strategy are preserved verbatim.

### Gaps

- **None known** relative to the source Markdown inventory (headings + list items). Document title and subtitle live in the chrome/meta rather than as scroll sections by design.
