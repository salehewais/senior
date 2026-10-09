# Architecture learning portal

**Status: the HTML explorer is the bilingual learning page.** Open [system-architecture.html](system-architecture.html) from this directory. The page is one file. It does not load a CDN, a font host, or any other network request. It works from a local `file://` tab in a normal browser. Some embedded browsers block `file://`. In that case serve the repository with a static file server and open `docs/system-architecture.html`. The page still does not call the network.

The same picture in prose is [current-architecture.md](current-architecture.md). The classification of what is implemented is [extension-gap-analysis.md](extension-gap-analysis.md). This page tells you how to use the HTML. It does not copy the broker, outbox, Kubernetes, observability, testing, or security write-ups.

## What the page is for

Sixteen chapters walk the repository: boundaries, folders, a request, Clean Architecture, the unit of work, the outbox, RabbitMQ, the saga, consistency, Redis, Traefik and kind, Django and Odoo, Flask and React Native, monitoring, and tests. A system map and a workflow tracer sit beside the chapters.

A badge says whether a topic is implemented, only partly implemented, or still planned. The shipped saga worker does not reach `COMPLETED` against a running Odoo. Mock notification delivery is implemented. FCM, SMTP, and an inbox API are not. Those limits are written on the page. They are not implied by a diagram.

## How to open it

From the repository root:

```bash
xdg-open docs/system-architecture.html
```

Or open the file from the editor. Relative links point at Markdown and source next to this directory. If the browser downloads a `.py` file instead of showing it, open that repository path in the editor. Each linked path is also printed as text, with a copy button.

## Language

The header has **English** and **العربية**. Arabic uses a right-to-left layout. English identifiers, file names, class names, and API paths stay in English.

The choice is stored in this browser under the key `commerce-portal-lang`. That is the only saved preference. Chapter, map selection, workflow, and step are in the URL hash, so a reload keeps the place you were reading. Switching language does not clear them.

Quiz answers stay visible only until you hide them or reload. They are not saved. The "opened in this tab" count is not saved.

## How to move around

- The sidebar lists the chapters. On a narrow screen, use **Show chapters**.
- **Chapter**, **Map**, and **Workflows** switch the main panel. On a narrow screen those controls are repeated above the text.
- Search matches the current language and lists chapters and workflows above the chapter, the map, or the tracer. Choosing a hit opens that chapter or workflow. It does not leave the page.
- Previous and next sit at the bottom of a chapter. Left and right arrow keys do the same when focus is not in the search box. In Arabic, the arrows follow the reading direction.
- The map filters services, databases, messaging, infrastructure, and clients. Select a component for its responsibility, inputs, outputs, store, neighbors, paths, and failures.
- The workflow tracer is step by step. A planned step is labeled planned. The duplicate-message walk ends with the HTTP idempotency key, which is documented and not built. The notification walk ends with real delivery, which is not built.

## What this page does not do

Compose, kind, Locust, and a restore were not started to write the page. Pass counts from 9 October 2026 are only the ones recorded in [testing.md](testing.md). The page does not claim a measured split of requests across pods.
