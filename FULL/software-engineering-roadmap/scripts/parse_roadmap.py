#!/usr/bin/env python3
"""Parse Software_Engineering_Master_Roadmap.md into roadmap-content.js preserving all content."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MD_PATH = ROOT / "Software_Engineering_Master_Roadmap.md"
OUT_PATH = ROOT / "software-engineering-roadmap" / "data" / "roadmap-content.js"
INV_PATH = ROOT / "software-engineering-roadmap" / "data" / "content-inventory.json"


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("&", " and ")
    text = text.replace("—", "-").replace("–", "-")
    text = re.sub(r"[()]", "", text)
    text = re.sub(r"[^\w\s\-/]+", "", text, flags=re.UNICODE)
    text = re.sub(r"[\s_/]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:90] or "item"


def parse_inline(text: str) -> str:
    """Keep markdown inline markers; renderer will handle them."""
    return text.rstrip()


def parse_list_block(lines: list[str], start: int) -> tuple[list[dict], int]:
    """Parse a contiguous nested list starting at start. Returns (items, next_index)."""
    items: list[dict] = []
    stack: list[tuple[int, list]] = [(-1, items)]  # indent -> children list
    i = start

    while i < len(lines):
        line = lines[i]
        if not line.strip():
            # blank line ends list only if next non-blank is not a list continuation
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j >= len(lines):
                break
            nxt = lines[j]
            if re.match(r"^\s*([-*]|\d+\.)\s+", nxt):
                i = j
                continue
            break

        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.+)$", line)
        if not m:
            # bold question lines inside sections are not list items
            break

        indent = len(m.group(1).replace("\t", "    "))
        marker = m.group(2)
        text = parse_inline(m.group(3))
        ordered = marker.endswith(".")

        node = {
            "text": text,
            "ordered": ordered,
            "children": [],
        }

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            stack = [(-1, items)]
        stack[-1][1].append(node)
        stack.append((indent, node["children"]))
        i += 1

    return items, i


def assign_ids(nodes: list[dict], prefix: str, counter: list[int]) -> None:
    for node in nodes:
        counter[0] += 1
        base = slugify(node["text"][:60])
        node["id"] = f"{prefix}--{base}-{counter[0]}"
        if node.get("children"):
            assign_ids(node["children"], prefix, counter)


def flatten_concepts(nodes: list[dict], path: list[str], out: list[dict]) -> None:
    for node in nodes:
        title = node["text"]
        # strip trailing Arabic em-dash descriptions for search title? Keep full text.
        concept = {
            "id": node["id"],
            "title": title,
            "path": path[:],
            "hasChildren": bool(node.get("children")),
        }
        out.append(concept)
        if node.get("children"):
            flatten_concepts(node["children"], path + [title], out)


def main() -> None:
    md = MD_PATH.read_text(encoding="utf-8")
    lines = md.splitlines()

    # Document meta from first lines
    title = "Software Engineering Master Roadmap"
    subtitle = "A Structured Learning Path for Senior Software Engineers"
    intro_note = None

    sections: list[dict] = []
    current: dict | None = None
    heading_stack: list[dict] = []  # for nesting under current H1
    used_ids: set[str] = set()
    concept_counter = [0]

    def unique_id(base: str) -> str:
        sid = base
        n = 2
        while sid in used_ids:
            sid = f"{base}-{n}"
            n += 1
        used_ids.add(sid)
        return sid

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Skip the very first H1/H2 document title — stored as meta
        if i == 0 and stripped.startswith("# "):
            title = stripped[2:].strip()
            i += 1
            continue
        if i <= 3 and stripped.startswith("## ") and "structured roadmap" in stripped.lower():
            # Keep original subtitle text as well
            original_subtitle = stripped[3:].strip()
            i += 1
            # next may be blank then blockquote
            continue

        if not stripped:
            i += 1
            continue

        if re.match(r"^---+$", stripped):
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                q = lines[i].strip()
                q = re.sub(r"^>\s?", "", q)
                quote_lines.append(q)
                i += 1
            block = {"type": "blockquote", "text": "\n".join(quote_lines)}
            if current is None and intro_note is None:
                intro_note = "\n".join(quote_lines)
            elif current is not None:
                # attach to deepest heading in stack
                target = heading_stack[-1] if heading_stack else current
                target.setdefault("blocks", []).append(block)
            else:
                # orphan — create overview attachment later
                if sections:
                    sections[-1].setdefault("blocks", []).append(block)
            continue

        # Heading
        hm = re.match(r"^(#{1,6})\s+(.+)$", line)
        if hm:
            level = len(hm.group(1))
            text = hm.group(2).strip()

            # Resolve parent first (same rules as nesting) so sibling titles get correct prefixes
            if level == 1:
                parent = None
            else:
                while heading_stack and heading_stack[-1]["level"] >= level:
                    heading_stack.pop()
                parent = heading_stack[-1] if heading_stack else current

            base = slugify(text)
            # Prefix ambiguous/short headings with parent id for stable unique anchors
            if parent and (
                level >= 4
                or base
                in {
                    "common-problems",
                    "training-path",
                    "core-problems",
                    "additional-problems",
                }
            ):
                base = f"{parent['id']}-{base}"
            sid = unique_id(base)

            node = {
                "id": sid,
                "title": text,
                "level": level,
                "blocks": [],
                "children": [],
            }

            if level == 1:
                sections.append(node)
                current = node
                heading_stack = [node]
            else:
                if current is None:
                    sections.append(node)
                    current = node
                    heading_stack = [node]
                else:
                    parent = parent or current
                    parent["children"].append(node)
                    heading_stack.append(node)
            i += 1
            continue

        # Bold question line (concurrency Arabic questions) — treat as callout paragraph
        if re.match(r"^\*\*.+\*\*$", stripped) or (
            stripped.startswith("**") and stripped.endswith("**")
        ):
            target = heading_stack[-1] if heading_stack else current
            if target is not None:
                target.setdefault("blocks", []).append(
                    {"type": "callout", "text": stripped.strip("*").strip()}
                )
            i += 1
            continue

        # Numbered study strategy or overview numbered list
        if re.match(r"^\d+\.\s+", stripped) or re.match(r"^[-*]\s+", line):
            # Could be start of list — but overview uses "1. Topic" without indent under phase
            items, next_i = parse_list_block(lines, i)
            target = heading_stack[-1] if heading_stack else current
            if target is None:
                # shouldn't happen
                i = next_i
                continue
            prefix = target["id"]
            assign_ids(items, prefix, concept_counter)

            def reg(items_):
                for it in items_:
                    # guarantee uniqueness if collision
                    if it["id"] in used_ids:
                        it["id"] = unique_id(it["id"])
                    else:
                        used_ids.add(it["id"])
                    reg(it.get("children", []))

            reg(items)
            target.setdefault("blocks", []).append({"type": "list", "items": items})
            i = next_i
            continue

        # Plain paragraph
        para_lines = [stripped]
        i += 1
        while i < len(lines):
            s = lines[i].strip()
            if not s:
                break
            if s.startswith("#") or s.startswith(">") or re.match(r"^---+$", s):
                break
            if re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]):
                break
            if re.match(r"^\*\*.+\*\*$", s):
                break
            para_lines.append(s)
            i += 1
        target = heading_stack[-1] if heading_stack else current
        if target is not None:
            target.setdefault("blocks", []).append(
                {"type": "paragraph", "text": " ".join(para_lines)}
            )
        continue

    # Build flat concept index for search/progress (leaf-oriented but include all list nodes)
    concepts: list[dict] = []

    def walk_section(sec: dict, path: list[str]) -> None:
        p = path + [sec["title"]]
        for block in sec.get("blocks", []):
            if block["type"] == "list":
                flatten_concepts(block["items"], p, concepts)
        for child in sec.get("children", []):
            walk_section(child, p)

    for sec in sections:
        walk_section(sec, [])

    # Main topic ids for nav (numbered 01-10 + supporting + cross + strategy + overview)
    main_topics = []
    for sec in sections:
        main_topics.append(
            {
                "id": sec["id"],
                "title": sec["title"],
                "childCount": count_descendants(sec),
                "conceptCount": count_concepts_in(sec),
            }
        )

    data = {
        "meta": {
            "title": title,
            "subtitle": subtitle,
            "originalSubtitle": "A structured roadmap for Backend Engineering and Senior Software Engineering",
            "introNote": intro_note,
            "sourceFile": "Software_Engineering_Master_Roadmap.md",
        },
        "sections": sections,
        "concepts": concepts,
        "mainTopics": main_topics,
        "stats": {
            "sectionCount": len(sections),
            "conceptCount": len(concepts),
            "headingCount": count_all_headings(sections),
        },
    }

    # Verify against inventory
    inv = json.loads(INV_PATH.read_text(encoding="utf-8"))
    mapped_h1 = {s["title"] for s in sections}
    expected_h1 = set(inv["h1_titles"]) - {title}  # doc title not a section
    # Doc H1 is first in inventory
    expected_h1 = set(inv["h1_titles"][1:])  # skip document title
    missing_h1 = expected_h1 - mapped_h1
    extra_h1 = mapped_h1 - expected_h1

    js = (
        "/* Auto-generated from Software_Engineering_Master_Roadmap.md — do not edit by hand */\n"
        "window.ROADMAP_CONTENT = "
        + json.dumps(data, ensure_ascii=False, indent=2)
        + ";\n"
    )
    OUT_PATH.write_text(js, encoding="utf-8")

    report = {
        "concepts": len(concepts),
        "sections": len(sections),
        "headings": data["stats"]["headingCount"],
        "missing_h1": sorted(missing_h1),
        "extra_h1": sorted(extra_h1),
        "inventory_headings": inv["heading_count"],
        "mapped_headings_plus_doc_title": data["stats"]["headingCount"] + 1,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


def count_descendants(sec: dict) -> int:
    n = len(sec.get("children", []))
    for c in sec.get("children", []):
        n += count_descendants(c)
    return n


def count_concepts_in(sec: dict) -> int:
    n = 0
    for block in sec.get("blocks", []):
        if block["type"] == "list":

            def count_items(items):
                total = len(items)
                for it in items:
                    total += count_items(it.get("children", []))
                return total

            n += count_items(block["items"])
    for c in sec.get("children", []):
        n += count_concepts_in(c)
    return n


def count_all_headings(sections: list[dict]) -> int:
    n = 0

    def walk(s):
        nonlocal n
        n += 1
        for c in s.get("children", []):
            walk(c)

    for s in sections:
        walk(s)
    return n


if __name__ == "__main__":
    main()
