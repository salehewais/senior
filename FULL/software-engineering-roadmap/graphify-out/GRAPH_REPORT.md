# Graph Report - software-engineering-roadmap  (2026-11-08)

## Corpus Check
- 1 files · ~375 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: .css 3, (none) 1)

## Summary
- 28 nodes · 35 edges · 5 communities
- Extraction: 77% EXTRACTED · 23% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.86)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Roadmap App Core
- Navigation Progress
- Header Search Theme
- Mermaid Diagrams
- Shell Layout TOC

## God Nodes (most connected - your core abstractions)
1. `Software Engineering Master Roadmap` - 16 edges
2. `Site Header` - 5 edges
3. `Sidebar Roadmap Navigation` - 4 edges
4. `App Shell Layout` - 4 edges
5. `Overall Learning Progress Chip` - 3 edges
6. `Mermaid CDN Integration` - 3 edges
7. `Global Search` - 2 edges
8. `Theme Toggle` - 2 edges
9. `Completion Status Filters` - 2 edges
10. `Breadcrumbs` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Software Engineering Master Roadmap` --references--> `App Shell Layout`  [EXTRACTED]
  index.html → index.html  _Bridges community 0 → community 4_
- `Software Engineering Master Roadmap` --references--> `diagrams.js`  [EXTRACTED]
  index.html → index.html  _Bridges community 0 → community 3_
- `Software Engineering Master Roadmap` --references--> `navigation.js`  [EXTRACTED]
  index.html → index.html  _Bridges community 0 → community 1_
- `Software Engineering Master Roadmap` --references--> `search.js`  [EXTRACTED]
  index.html → index.html  _Bridges community 0 → community 2_
- `Site Header` --references--> `Overall Learning Progress Chip`  [EXTRACTED]
  index.html → index.html  _Bridges community 2 → community 1_

## Hyperedges (group relationships)
- **Client-side JS module load order** — index_roadmap_content_js, index_progress_js, index_search_js, index_navigation_js, index_architecture_relationships_js, index_diagrams_js, index_app_js [EXTRACTED 1.00]
- **App shell navigation layout** — index_app_shell, index_sidebar_navigation, index_toc_panel, index_breadcrumbs [EXTRACTED 1.00]
- **Header learning and UI controls** — index_site_header, index_global_search, index_progress_chip, index_study_mode, index_theme_toggle [EXTRACTED 1.00]

## Communities (5 total, 0 thin omitted)

### Community 0 - "Roadmap App Core"
Cohesion: 0.25
Nodes (9): app.js, architecture-relationships.js, Back to Top Button, responsive.css, roadmap-content.js, Skip to Content Accessibility Link, Software Engineering Master Roadmap, Structured Learning Path for Senior Software Engineers (+1 more)

### Community 1 - "Navigation Progress"
Cohesion: 0.33
Nodes (6): Completion Status Filters, Navigation Tree, navigation.js, Overall Learning Progress Chip, progress.js, Sidebar Roadmap Navigation

### Community 2 - "Header Search Theme"
Cohesion: 0.33
Nodes (6): Global Search, search.js, Site Header, Study Mode Toggle, Theme Toggle, themes.css

### Community 3 - "Mermaid Diagrams"
Cohesion: 0.50
Nodes (3): diagrams.js, Mermaid CDN Integration, RoadmapDiagrams

### Community 4 - "Shell Layout TOC"
Cohesion: 1.00
Nodes (3): App Shell Layout, Breadcrumbs, On This Page TOC Panel

## Knowledge Gaps
- **8 isolated node(s):** `Structured Learning Path for Senior Software Engineers`, `Study Mode Toggle`, `Navigation Tree`, `roadmap-content.js`, `architecture-relationships.js` (+3 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 9 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Software Engineering Master Roadmap` connect `Roadmap App Core` to `Navigation Progress`, `Header Search Theme`, `Mermaid Diagrams`, `Shell Layout TOC`?**
  _High betweenness centrality (0.840) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Overall Learning Progress Chip` (e.g. with `Completion Status Filters` and `progress.js`) actually correct?**
  _`Overall Learning Progress Chip` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Structured Learning Path for Senior Software Engineers`, `Study Mode Toggle`, `Navigation Tree` to the rest of the system?**
  _8 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Why does `App Shell Layout` connect `Shell Layout TOC` to `Roadmap App Core`, `Navigation Progress`?**
  _High betweenness centrality (0.206) - this node is a cross-community bridge._
- **Why does `Site Header` connect `Header Search Theme` to `Roadmap App Core`, `Navigation Progress`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._