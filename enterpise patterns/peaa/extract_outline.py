#!/usr/bin/env python3
"""Extract a stable PEAA outline from the local PDF.

Tries PyMuPDF bookmarks first. Falls back to ``pdftotext`` on the table of
contents and checks every expected chapter and pattern title. Part 3
concurrency entries are an add-on and are not read from the PDF.

استخراج فهرس ثابت من الـ PDF — الجزء ٣ إضافة دراسية مش من الكتاب.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "Patterns of Enterprise Application Architecture.pdf"
OUT = Path(__file__).resolve().parent / "data" / "peaa-outline.json"

# (kind, chapter, title as printed in the TOC, stable id)
PEAA_ENTRIES: list[tuple[str, int, str, str]] = [
    ("chapter", 1, "Layering", "ch01-layering"),
    ("chapter", 2, "Organizing Domain Logic", "ch02-domain-logic"),
    ("chapter", 3, "Mapping to Relational Databases", "ch03-orm"),
    ("chapter", 4, "Web Presentation", "ch04-web"),
    ("chapter", 5, "Concurrency", "ch05-concurrency"),
    ("chapter", 6, "Session State", "ch06-session"),
    ("chapter", 7, "Distribution Strategies", "ch07-distribution"),
    ("chapter", 8, "Putting It All Together", "ch08-together"),
    ("chapter", 9, "Domain Logic Patterns", "ch09-domain-logic"),
    ("pattern", 9, "Transaction Script", "pattern-transaction-script"),
    ("pattern", 9, "Domain Model", "pattern-domain-model"),
    ("pattern", 9, "Table Module", "pattern-table-module"),
    ("pattern", 9, "Service Layer", "pattern-service-layer"),
    ("chapter", 10, "Data Source Architectural Patterns", "ch10-data-source"),
    ("pattern", 10, "Table Data Gateway", "pattern-table-data-gateway"),
    ("pattern", 10, "Row Data Gateway", "pattern-row-data-gateway"),
    ("pattern", 10, "Active Record", "pattern-active-record"),
    ("pattern", 10, "Data Mapper", "pattern-data-mapper"),
    ("chapter", 11, "Object-Relational Behavioral Patterns", "ch11-or-behavioral"),
    ("pattern", 11, "Unit of Work", "pattern-unit-of-work"),
    ("pattern", 11, "Identity Map", "pattern-identity-map"),
    ("pattern", 11, "Lazy Load", "pattern-lazy-load"),
    ("chapter", 12, "Object-Relational Structural Patterns", "ch12-or-structural"),
    ("pattern", 12, "Identity Field", "pattern-identity-field"),
    ("pattern", 12, "Foreign Key Mapping", "pattern-foreign-key-mapping"),
    ("pattern", 12, "Association Table Mapping", "pattern-association-table-mapping"),
    ("pattern", 12, "Dependent Mapping", "pattern-dependent-mapping"),
    ("pattern", 12, "Embedded Value", "pattern-embedded-value"),
    ("pattern", 12, "Serialized LOB", "pattern-serialized-lob"),
    ("pattern", 12, "Single Table Inheritance", "pattern-single-table-inheritance"),
    ("pattern", 12, "Class Table Inheritance", "pattern-class-table-inheritance"),
    ("pattern", 12, "Concrete Table Inheritance", "pattern-concrete-table-inheritance"),
    ("pattern", 12, "Inheritance Mappers", "pattern-inheritance-mappers"),
    ("chapter", 13, "Object-Relational Metadata Mapping Patterns", "ch13-or-metadata"),
    ("pattern", 13, "Metadata Mapping", "pattern-metadata-mapping"),
    ("pattern", 13, "Query Object", "pattern-query-object"),
    ("pattern", 13, "Repository", "pattern-repository"),
    ("chapter", 14, "Web Presentation Patterns", "ch14-web"),
    ("pattern", 14, "Model View Controller", "pattern-mvc"),
    ("pattern", 14, "Page Controller", "pattern-page-controller"),
    ("pattern", 14, "Front Controller", "pattern-front-controller"),
    ("pattern", 14, "Template View", "pattern-template-view"),
    ("pattern", 14, "Transform View", "pattern-transform-view"),
    ("pattern", 14, "Two Step View", "pattern-two-step-view"),
    ("pattern", 14, "Application Controller", "pattern-application-controller"),
    ("chapter", 15, "Distribution Patterns", "ch15-distribution"),
    ("pattern", 15, "Remote Facade", "pattern-remote-facade"),
    ("pattern", 15, "Data Transfer Object", "pattern-dto"),
    ("chapter", 16, "Offline Concurrency Patterns", "ch16-offline"),
    ("pattern", 16, "Optimistic Offline Lock", "pattern-optimistic-offline-lock"),
    ("pattern", 16, "Pessimistic Offline Lock", "pattern-pessimistic-offline-lock"),
    ("pattern", 16, "Coarse-Grained Lock", "pattern-coarse-grained-lock"),
    ("pattern", 16, "Implicit Lock", "pattern-implicit-lock"),
    ("chapter", 17, "Session State Patterns", "ch17-session"),
    ("pattern", 17, "Client Session State", "pattern-client-session-state"),
    ("pattern", 17, "Server Session State", "pattern-server-session-state"),
    ("pattern", 17, "Database Session State", "pattern-database-session-state"),
    ("chapter", 18, "Base Patterns", "ch18-base"),
    ("pattern", 18, "Gateway", "pattern-gateway"),
    ("pattern", 18, "Mapper", "pattern-mapper"),
    ("pattern", 18, "Layer Supertype", "pattern-layer-supertype"),
    ("pattern", 18, "Separated Interface", "pattern-separated-interface"),
    ("pattern", 18, "Registry", "pattern-registry"),
    ("pattern", 18, "Value Object", "pattern-value-object"),
    ("pattern", 18, "Money", "pattern-money"),
    ("pattern", 18, "Special Case", "pattern-special-case"),
    ("pattern", 18, "Plugin", "pattern-plugin"),
    ("pattern", 18, "Service Stub", "pattern-service-stub"),
    ("pattern", 18, "Record Set", "pattern-record-set"),
]

# Not in the PDF. Thread/task patterns, distinct from offline concurrency.
ADDON_ENTRIES: list[tuple[str, str, str]] = [
    ("intro", "part3-concurrency", "Concurrency Patterns"),
    ("pattern", "conc-thread-pool", "Thread Pool / Worker Pool"),
    ("pattern", "conc-producer-consumer", "Producer / Consumer"),
    ("pattern", "conc-active-object", "Active Object"),
    ("pattern", "conc-future-promise", "Future / Promise"),
    ("pattern", "conc-scheduler", "Scheduler"),
    ("pattern", "conc-rwlock", "Read/Write Lock"),
    ("pattern", "conc-lock-splitting", "Lock Splitting"),
    ("pattern", "conc-striped-locking", "Striped Locking"),
    ("pattern", "conc-guarded-suspension", "Guarded Suspension"),
    ("pattern", "conc-barrier", "Barrier"),
    ("pattern", "conc-work-stealing", "Work Stealing"),
    ("pattern", "conc-reactor", "Reactor"),
    ("pattern", "conc-proactor", "Proactor"),
    ("pattern", "conc-leader-followers", "Leader/Followers"),
    ("pattern", "conc-rate-limiter", "Rate Limiter"),
    ("pattern", "conc-bulkhead", "Bulkhead"),
    ("pattern", "conc-monitor-object", "Monitor Object"),
]


def _toc_text_pdftotext() -> str:
    tool = shutil.which("pdftotext")
    if not tool:
        raise SystemExit("pdftotext is not installed")
    proc = subprocess.run(
        [tool, "-f", "1", "-l", "12", "-layout", str(PDF), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    text = proc.stdout
    start = text.find("Table of Contents")
    end = text.find("References")
    if start < 0 or end < 0:
        raise SystemExit("Could not locate the table of contents in pdftotext output")
    return text[start:end]


def _toc_text_pymupdf() -> str | None:
    try:
        import fitz  # type: ignore
    except ImportError:
        return None
    doc = fitz.open(PDF)
    toc = doc.get_toc()
    if not toc:
        return None
    return "\n".join(title for _level, title, _page in toc)


def load_toc_text() -> tuple[str, str]:
    bookmarks = _toc_text_pymupdf()
    if bookmarks:
        return bookmarks, "pymupdf-bookmarks"
    return _toc_text_pdftotext(), "pdftotext-toc"


def build() -> dict:
    if not PDF.is_file():
        raise SystemExit(f"PDF not found: {PDF}")
    toc, method = load_toc_text()
    missing = [title for _k, _c, title, _i in PEAA_ENTRIES if title not in toc]
    if missing:
        raise SystemExit("TOC is missing titles:\n" + "\n".join(missing))
    entries = [
        {
            "kind": kind,
            "part": 1 if chapter <= 8 else 2,
            "chapter": chapter,
            "title": title,
            "id": stable_id,
            "source": "pdf",
        }
        for kind, chapter, title, stable_id in PEAA_ENTRIES
    ]
    addons = [
        {"kind": kind, "part": 3, "title": title, "id": stable_id, "source": "addon"}
        for kind, stable_id, title in ADDON_ENTRIES
    ]
    return {
        "pdf": PDF.name,
        "extraction": method,
        "note": "Pattern names and structure come from the book TOC. Guide prose is original.",
        "entries": entries,
        "addons": addons,
    }


def main() -> None:
    payload = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(payload['entries'])} PEAA + {len(payload['addons'])} addon)")


if __name__ == "__main__":
    main()
