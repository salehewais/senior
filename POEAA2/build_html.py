#!/usr/bin/env python3
"""Generate index.html from POEAA Arabic reference markdown source."""
from __future__ import annotations

import html
import re
from pathlib import Path

SOURCE = Path("/tmp/poeaa_source.txt")
OUT = Path(__file__).resolve().parent / "index.html"

SECTION_IDS = {
    "أولًا: نفهم الخريطة قبل ما نحفظ أسماء الأنماط": "intro",
    "1. Domain Logic Patterns — فين نحط قواعد البزنس؟": "s1",
    "2. Data Source Architectural Patterns — إزاي نتعامل مع قاعدة البيانات؟": "s2",
    "3. Object-Relational Behavioral Patterns — إدارة تحميل وحفظ الكائنات": "s3",
    "4. Object-Relational Structural Patterns — إزاي نمثل الكائنات في الجداول؟": "s4",
    "5. Object-Relational Metadata Mapping Patterns — وصف الـ Mapping وإدارة الوصول للكائنات": "s5",
    "6. Web Presentation Patterns — استقبال الطلبات وعرض النتائج": "s6",
    "7. Distribution Patterns — التواصل بين العمليات والخدمات": "s7",
    "8. Offline Concurrency Patterns — التعامل مع التعارضات": "s8",
    "9. Session State Patterns — أين تعيش حالة المستخدم؟": "s9",
    "10. Base Patterns — الأنماط الأساسية اللي بتتكرر في أكتر من مكان": "s10",
    "11. إزاي الأنماط دي تشتغل مع بعض في مشروع حقيقي؟": "s11",
    "12. الخريطة النهائية للمراجعة": "s12",
    "13. أهم حاجة بالنسبة لك كمطور Odoo وPython": "s13",
}

ORDER_FLOW_STEPS = [
    ("استقبال الطلب", "Web Presentation — Controller"),
    ("تنسيق العملية", "Service Layer"),
    ("تطبيق قواعد البزنس", "Transaction Script أو Domain Model"),
    ("قراءة البيانات وكتابتها", "Repository / Data Mapper / Active Record"),
    ("إدارة التغييرات", "Unit of Work / Transaction / Concurrency Control"),
]

DIAGRAM_BLOCKS: dict[str, str] = {}


def load_source() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    # Drop user request preamble
    idx = text.find("# المرجع المنظم")
    if idx >= 0:
        text = text[idx:]
    intro = text.split("# المرجع المنظم", 1)[0]
    intro = intro.strip()
    if intro.startswith("i want"):
        lines = intro.split("\n")
        intro = "\n".join(lines[2:]).strip()
    return intro, text


def expand_python(code: str) -> str:
    code = code.strip()
    if code.count("\n") >= 4:
        return code
    if code.startswith("{") and "theme" in code:
        return code
    if "CREATE TABLE" in code and code.count("\n") >= 2:
        return code
    if "HTTP Request" in code or "Requests" in code or ("Cart" in code and "|" in code):
        return code
    if "Browser Cookie" in code:
        return code
    if "GET /" in code and "->" in code:
        return code

    stmt = (
        r"(?:if |elif |else:|for |while |return |raise |with |try:|except |pass|break|continue|"
        r"@|from |import |\w+\s*=|self\.|repository\.|order\.|product\.|customer\.|total )"
    )
    prev = None
    while prev != code:
        prev = code
        code = re.sub(rf"\s{{4,}}(?={stmt})", "\n    ", code)
        code = re.sub(rf"(?<=:)\s{{2,}}(?={stmt})", "\n    ", code)
        code = re.sub(r"\s{4,}(?=def |class )", "\n\n", code)
        code = re.sub(r"(?<=[\}}])\s{4,}(?=\w)", "\n    ", code)
    code = re.sub(r"(?<=\))\s{4,}(?=def |class )", "\n\n", code)
    return polish_python(code.strip())


def indent_class_bodies(code: str) -> str:
    lines = code.split("\n")
    out: list[str] = []
    in_class = False
    in_def = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append("")
            in_def = False
            continue
        if stripped.startswith("class ") and stripped.endswith(":"):
            in_class = True
            in_def = False
            out.append(stripped)
            continue
        if in_class:
            if stripped.startswith(("def ", "@")):
                out.append("    " + stripped)
                in_def = stripped.endswith(":")
                continue
            if in_def:
                out.append("        " + stripped)
            else:
                out.append("    " + stripped)
            continue
        out.append(line)
    return "\n".join(out)


def polish_python(code: str) -> str:
    code = re.sub(r"(import dataclass)(from )", r"\1\n\2", code)
    code = re.sub(r"(import \w+)(from )", r"\1\n\2", code)
    code = re.sub(r"(@dataclass)(class )", r"\1\n\n\2", code)
    code = re.sub(r"(class \w+(?:\([^)]*\))?:)\n+(def )", r"\1\n    \2", code)
    code = re.sub(r"(class \w+(?:\([^)]*\))?:)\n+(    @)", r"\1\n    \2", code)
    code = indent_class_bodies(code)
    for spaces in (4, 8):
        pad = " " * spaces
        inner = " " * (spaces + 4)
        code = re.sub(
            rf"(^{pad}if .+$)\n{pad}(raise .+$)",
            rf"\1\n{inner}\2",
            code,
            flags=re.M,
        )
    code = re.sub(r",    \}", ",\n    }", code)
    code = re.sub(r"=\ \{        ", "= {\n        ", code)
    code = re.sub(r",        ", ",\n        ", code)
    code = re.sub(r"        \}", "\n    }", code)
    code = re.sub(
        r"(^    def .+$)\n(?!(    |\s*$))(\S)",
        lambda m: f"{m.group(1)}\n    {m.group(3)}",
        code,
        flags=re.M,
    )
    return code


def detect_lang(code: str) -> str:
    if "CREATE TABLE" in code or code.strip().upper().startswith("UPDATE "):
        return "sql"
    if code.strip().startswith("{") and "theme" in code:
        return "json"
    if "HTTP Request" in code or "Requests\n" in code or "GET /" in code:
        return "diagram"
    if "Browser Cookie" in code:
        return "diagram"
    if re.search(r"^\w+\n\s+\|\n\s+v", code, re.M):
        return "diagram"
    return "python"


def render_diagram(code: str) -> str:
    key = code.strip()
    if key in DIAGRAM_BLOCKS:
        return DIAGRAM_BLOCKS[key]

    lines = [ln.rstrip() for ln in code.strip().split("\n")]

    if lines and lines[0] == "HTTP Request":
        return """
<div class="flow-diagram" dir="ltr">
  <div class="flow-node">HTTP Request</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node accent">Product Controller</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node">Application / Model</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node">Product View</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node">HTTP Response</div>
</div>"""

    if lines and lines[0] == "Requests":
        return """
<div class="tree-diagram" dir="ltr">
  <div class="flow-node">Requests</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node accent">Front Controller</div>
  <div class="tree-branches">
    <div class="tree-item">→ Product Handler</div>
    <div class="tree-item">→ Cart Handler</div>
    <div class="tree-item">→ Checkout Handler</div>
  </div>
</div>"""

    if lines and lines[0] == "Cart":
        return """
<div class="flow-diagram" dir="ltr">
  <div class="flow-node">Cart</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node">Address</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node">Payment</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node accent">Confirmation</div>
</div>"""

    if "Browser Cookie" in code:
        return """
<div class="flow-diagram session-diagram" dir="ltr">
  <div class="flow-node">Browser Cookie: session_id=abc123</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node">Server</div>
  <div class="flow-arrow">↓</div>
  <div class="flow-node accent">Redis Session</div>
</div>"""

    if any("->" in ln for ln in lines):
        items = "".join(
            f'<div class="route-line">{html.escape(ln.strip())}</div>' for ln in lines if ln.strip()
        )
        return f'<div class="route-diagram" dir="ltr">{items}</div>'

    return f'<pre class="diagram-fallback" dir="ltr">{html.escape(code)}</pre>'


def render_code(code: str) -> str:
    lang = detect_lang(code)
    if lang == "diagram":
        return render_diagram(code)
    if lang == "python":
        code = expand_python(code)
    escaped = html.escape(code)
    return f'<pre class="code-block" dir="ltr"><code class="language-{lang}">{escaped}</code></pre>'


def render_order_flow() -> str:
    parts = ['<ol class="order-flow">']
    for i, (title, detail) in enumerate(ORDER_FLOW_STEPS, 1):
        parts.append(
            f'<li><span class="step-num">{i}</span>'
            f'<div class="step-body"><strong>{html.escape(title)}</strong>'
            f'<span class="step-detail">{html.escape(detail)}</span></div></li>'
        )
    parts.append("</ol>")
    return "\n".join(parts)


def parse_table(lines: list[str], start: int) -> tuple[str, int]:
    rows: list[list[str]] = []
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if not line.startswith("|"):
            break
        if re.match(r"^\|\s*-+", line):
            i += 1
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
        i += 1
    if not rows:
        return "", start
    header = rows[0]
    body = rows[1:]
    out = ['<div class="table-wrap"><table><thead><tr>']
    for h in header:
        out.append(f"<th>{html.escape(h)}</th>")
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            out.append(f"<td>{inline_md(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out), i


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r'<code class="inline">\1</code>', text)
    return text


def meta_chip(line: str) -> str | None:
    rules: list[tuple[str, str, str]] = [
        (r"^مناسب إمتى\?", "when", "مناسب إمتى"),
        (r"^ملحوظة", "note", "ملحوظة"),
        (r"^المشكلة:", "problem", "المشكلة"),
        (r"^الهدف", "goal", "الهدف"),
        (r"^إمتى تحتاج", "when", "متى"),
        (r"^الاستخدام:", "usage", "الاستخدام"),
        (r"^الفائدة:", "goal", "الفائدة"),
        (r"^الفرق عن", "diff", "الفرق"),
        (r"^الفرق بين", "diff", "الفرق"),
        (r"^الفرق:", "diff", "الفرق"),
        (r"^الفرق ", "diff", "الفرق"),
        (r"^الفرq المهم", "diff", "الفرق"),
    ]
    for pat, kind, label in rules:
        if re.search(pat, line):
            return (
                f'<div class="meta-chip chip-{kind}">'
                f'<span class="chip-label">{html.escape(label)}</span>'
                f'<span class="chip-text">{inline_md(line)}</span></div>'
            )
    return None


def is_pattern_heading(line: str) -> re.Match | None:
    return re.match(r"^### (\d+\.\d+)\s+(.+)$", line)


def next_nonempty(lines: list[str], start: int) -> tuple[str, int] | tuple[None, int]:
    j = start
    while j < len(lines):
        s = lines[j].strip()
        if s:
            return s, j
        j += 1
    return None, j


def render_integration_flow(lines: list[str], start: int) -> tuple[str, int]:
    """Section 11: title / patterns / description triplets."""
    blocks: list[tuple[str, str]] = []
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("## ") or line.startswith("ده نموذج"):
            break
        if not line or line.startswith("|") or line.startswith("```"):
            i += 1
            continue
        pat, j1 = next_nonempty(lines, i + 1)
        desc, j2 = next_nonempty(lines, j1 + 1)
        if (
            pat
            and desc
            and not pat.startswith("#")
            and not desc.startswith("#")
            and not pat.startswith("ده نموذج")
        ):
            blocks.append((line, f"{pat} — {desc}"))
            i = j2 + 1
        else:
            i += 1
    if not blocks:
        return "", min(start + 1, len(lines))
    parts = ['<ol class="integration-flow">']
    for n, (title, detail) in enumerate(blocks, 1):
        parts.append(
            f'<li><span class="step-num">{n}</span>'
            f'<div class="step-body"><strong>{html.escape(title)}</strong>'
            f'<span class="step-detail">{html.escape(detail)}</span></div></li>'
        )
    parts.append("</ol>")
    return "\n".join(parts), i


def close_card(out: list[str], card_open: bool) -> bool:
    if card_open:
        out.append("</article>")
    return False


def convert_markdown(body: str, intro_para: str) -> str:
    lines = body.split("\n")
    out: list[str] = []
    i = 0
    sid = "intro"
    card_open = False

    # Title block
    out.append('<header class="page-header">')
    out.append("<p class=" + '"lead"' + ">" + inline_md(intro_para.replace("\n", " ")) + "</p>")
    out.append(
        "<h1>المرجع المنظم لـ Enterprise Application Patterns</h1>"
    )
    out.append("</header>")

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped.startswith("# ") and not stripped.startswith("## "):
            i += 1
            continue

        if stripped.startswith("## "):
            card_open = close_card(out, card_open)
            title = stripped[3:].strip()
            sid = SECTION_IDS.get(title, re.sub(r"\W+", "-", title)[:40])
            extra = ""
            if sid == "s13":
                extra = " odoo-panel"
            if any(s.startswith('<section id=') for s in out):
                out.append("</section>")
            out.append(f'<section id="{sid}" class="doc-section{extra}">')
            out.append(f"<h2>{html.escape(title)}</h2>")
            i += 1
            if sid == "intro":
                # skip until numbered list content — inject flow after intro paragraph
                while i < len(lines):
                    if lines[i].strip().startswith("1\\."):
                        break
                    if lines[i].strip() and not lines[i].strip().startswith("تخيل"):
                        if "المراحل" not in lines[i]:
                            pass
                    if lines[i].strip().startswith("تخيل"):
                        out.append(f"<p>{inline_md(lines[i].strip())}</p>")
                    i += 1
                out.append(render_order_flow())
                # skip old list until disclaimer
                while i < len(lines):
                    s = lines[i].strip()
                    if s.startswith("دي خريطة"):
                        out.append(f"<p class=\"note-inline\">{inline_md(s)}</p>")
                        i += 1
                        break
                    i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("##"):
                    p = lines[i].strip()
                    if p.startswith("والأهم"):
                        out.append(f"<p>{inline_md(p)}</p>")
                    i += 1
            if sid == "s11":
                while i < len(lines):
                    s = lines[i].strip()
                    if not s or s.startswith("##"):
                        break
                    if s == "العميل يرسل الطلب":
                        break
                    out.append(f"<p>{inline_md(s)}</p>")
                    i += 1
            continue

        if stripped.startswith("### "):
            m = is_pattern_heading(stripped)
            if m:
                card_open = close_card(out, card_open)
                num, name = m.group(1), m.group(2)
                out.append(f'<article class="pattern-card" id="{sid}-{num.replace(".", "-")}">')
                out.append(
                    f'<h3 class="pattern-title"><span class="pattern-num">{num}</span> {html.escape(name)}</h3>'
                )
                card_open = True
            else:
                card_open = close_card(out, card_open)
                out.append(f"<h3>{html.escape(stripped[4:])}</h3>")
            i += 1
            continue

        if stripped.startswith("```"):
            i += 1
            code_lines = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # closing ```
            out.append(render_code("\n".join(code_lines)))
            continue

        if stripped.startswith("|"):
            card_open = close_card(out, card_open)
            table_html, i = parse_table(lines, i)
            out.append(table_html)
            continue

        if sid == "s11" and stripped == "العميل يرسل الطلب":
            flow_html, i = render_integration_flow(lines, i)
            out.append(flow_html)
            continue

        chip = meta_chip(stripped)
        if chip:
            out.append(chip)
            i += 1
            continue

        if stripped.startswith("إيه اللي بيميزه"):
            out.append(f'<p class="idea-lead">{inline_md(stripped)}</p>')
            i += 1
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            out.append("<ul>")
            while i < len(lines) and lines[i].strip().startswith(("- ", "* ")):
                out.append(f"<li>{inline_md(lines[i].strip()[2:])}</li>")
                i += 1
            out.append("</ul>")
            continue

        if re.match(r"^\d+\\?\.\s", stripped) or re.match(r"^\d+\.\s", stripped):
            out.append("<ol>")
            while i < len(lines):
                s = lines[i].strip()
                if not (re.match(r"^\d+\\?\.\s", s) or re.match(r"^\d+\.\s", s)):
                    break
                text = re.sub(r"^\d+\\?\.\s*", "", s)
                text = re.sub(r"^\d+\.\s*", "", text)
                out.append(f"<li>{inline_md(text)}</li>")
                i += 1
            out.append("</ol>")
            continue

        if stripped.startswith("الفكرة:"):
            out.append(f'<p class="pattern-idea">{inline_md(stripped)}</p>')
        elif stripped.startswith("مناسب إمتى؟"):
            out.append(meta_chip(stripped) or f"<p>{inline_md(stripped)}</p>")
        elif stripped.startswith("المشكلة:"):
            out.append(meta_chip(stripped) or f"<p>{inline_md(stripped)}</p>")
        else:
            out.append(f"<p>{inline_md(stripped)}</p>")
        i += 1

    card_open = close_card(out, card_open)
    if any(s.startswith('<section id=') for s in out):
        out.append("</section>")
    return "\n".join(out)


CSS = """
:root {
  --paper: #f6f1e7;
  --paper-elevated: #fffdf8;
  --ink: #1c1a17;
  --ink-muted: #5c564c;
  --accent: #1b5e3a;
  --accent-soft: rgba(27, 94, 58, 0.12);
  --border: rgba(28, 26, 23, 0.12);
  --shadow: 0 1px 2px rgba(28, 26, 23, 0.06), 0 8px 24px rgba(28, 26, 23, 0.06);
  --sidebar-w: 17rem;
  --font-ar: "IBM Plex Sans Arabic", system-ui, sans-serif;
  --font-head: "Amiri", "IBM Plex Sans Arabic", serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
}
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-ar);
  font-size: 1.05rem;
  line-height: 1.75;
  color: var(--ink);
  background: var(--paper);
}
.layout {
  display: grid;
  grid-template-columns: var(--sidebar-w) 1fr;
  min-height: 100vh;
}
nav.toc {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow-y: auto;
  padding: 1.25rem 1rem 2rem;
  background: var(--paper-elevated);
  border-inline-start: 1px solid var(--border);
  box-shadow: var(--shadow);
}
nav.toc .toc-title {
  font-family: var(--font-head);
  font-size: 1.15rem;
  color: var(--accent);
  margin: 0 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--accent-soft);
}
nav.toc ol {
  list-style: none;
  margin: 0;
  padding: 0;
}
nav.toc a {
  display: block;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  color: var(--ink-muted);
  text-decoration: none;
  font-size: 0.88rem;
  line-height: 1.4;
  transition: background 0.15s, color 0.15s;
}
nav.toc a:hover { background: var(--accent-soft); color: var(--accent); }
nav.toc a.active {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}
main.content {
  padding: 2rem clamp(1.25rem, 4vw, 3.5rem) 4rem;
  max-width: 52rem;
}
.page-header { margin-bottom: 2.5rem; }
.page-header h1 {
  font-family: var(--font-head);
  font-size: clamp(1.75rem, 4vw, 2.35rem);
  color: var(--accent);
  margin: 0.75rem 0 0;
  line-height: 1.35;
}
.lead {
  font-size: 1.08rem;
  color: var(--ink-muted);
  margin: 0;
}
.doc-section { margin-bottom: 3rem; scroll-margin-top: 1rem; }
.doc-section > h2 {
  font-family: var(--font-head);
  font-size: 1.55rem;
  color: var(--accent);
  margin: 0 0 1.25rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid var(--border);
}
.doc-section h3:not(.pattern-title) {
  font-family: var(--font-head);
  font-size: 1.2rem;
  margin: 1.5rem 0 0.75rem;
  color: var(--ink);
}
.doc-section h4 {
  font-size: 1rem;
  margin: 1.25rem 0 0.5rem;
  color: var(--accent);
}
p { margin: 0 0 1rem; }
.note-inline { font-size: 0.95rem; color: var(--ink-muted); }
.pattern-card {
  background: var(--paper-elevated);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.25rem 1.35rem;
  margin: 1.25rem 0;
  box-shadow: var(--shadow);
}
.pattern-title {
  margin: 0 0 1rem;
  font-family: var(--font-ar);
  font-size: 1.1rem;
  font-weight: 600;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.5rem;
}
.idea-lead {
  font-weight: 600;
  color: var(--ink);
  margin-top: -0.25rem;
}
.pattern-idea {
  color: var(--ink-muted);
  font-size: 0.98rem;
}
.pattern-num {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  color: var(--accent);
  background: var(--accent-soft);
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
}
.meta-chip {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 0.75rem;
  align-items: baseline;
  padding: 0.55rem 0.75rem;
  margin: 0.65rem 0;
  border-radius: 8px;
  font-size: 0.92rem;
  background: var(--accent-soft);
  border-inline-start: 3px solid var(--accent);
}
.chip-label {
  font-weight: 600;
  color: var(--accent);
  white-space: nowrap;
}
.chip-diff { background: rgba(27, 94, 58, 0.08); }
.chip-note { background: rgba(92, 86, 76, 0.08); border-color: var(--ink-muted); }
.chip-when { background: rgba(27, 94, 58, 0.1); }
.code-block {
  font-family: var(--font-mono);
  font-size: 0.82rem;
  line-height: 1.55;
  background: #1e1c18;
  color: #e8e4dc;
  padding: 1rem 1.1rem;
  border-radius: 10px;
  overflow-x: auto;
  margin: 0.75rem 0 1rem;
  border: 1px solid rgba(255,255,255,0.06);
}
code.inline {
  font-family: var(--font-mono);
  font-size: 0.88em;
  background: var(--accent-soft);
  padding: 0.1em 0.35em;
  border-radius: 4px;
  direction: ltr;
  unicode-bidi: embed;
}
.table-wrap { overflow-x: auto; margin: 1rem 0 1.5rem; }
table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92rem;
  background: var(--paper-elevated);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow);
}
th, td {
  padding: 0.65rem 0.85rem;
  text-align: start;
  border-bottom: 1px solid var(--border);
}
th {
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 600;
}
tbody tr:nth-child(even) { background: rgba(27, 94, 58, 0.04); }
.order-flow, .integration-flow {
  list-style: none;
  margin: 1.25rem 0 1.5rem;
  padding: 0;
}
.order-flow li, .integration-flow li {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 0.85rem;
  padding-bottom: 0.85rem;
  border-bottom: 1px dashed var(--border);
}
.order-flow li:last-child, .integration-flow li:last-child { border-bottom: none; }
.step-num {
  flex-shrink: 0;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent);
  color: #fff;
  font-weight: 700;
  font-size: 0.9rem;
  border-radius: 50%;
}
.step-body { display: flex; flex-direction: column; gap: 0.2rem; }
.step-body strong { color: var(--ink); }
.step-detail {
  font-size: 0.92rem;
  color: var(--ink-muted);
  font-family: var(--font-mono);
  direction: ltr;
  text-align: start;
  unicode-bidi: embed;
}
.flow-diagram, .tree-diagram {
  margin: 1rem 0;
  padding: 1rem;
  background: var(--paper-elevated);
  border: 1px solid var(--border);
  border-radius: 10px;
  text-align: center;
  font-family: var(--font-mono);
  font-size: 0.88rem;
}
.flow-node {
  display: inline-block;
  padding: 0.45rem 0.85rem;
  background: #fff;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin: 0.15rem 0;
}
.flow-node.accent {
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}
.flow-arrow { color: var(--accent); line-height: 1.2; }
.tree-branches { margin-top: 0.5rem; text-align: start; display: inline-block; }
.tree-item { padding: 0.25rem 0; color: var(--ink-muted); }
.route-diagram {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  padding: 0.75rem 1rem;
  background: var(--paper-elevated);
  border-radius: 8px;
  margin: 0.75rem 0;
  direction: ltr;
}
.route-line { padding: 0.2rem 0; }
.odoo-panel {
  background: linear-gradient(135deg, rgba(27, 94, 58, 0.08), rgba(246, 241, 231, 0.9));
  border: 2px solid var(--accent);
  border-radius: 16px;
  padding: 1.5rem 1.75rem 2rem;
  margin-top: 2rem;
}
.odoo-panel > h2 { border-bottom-color: var(--accent); }
ul, ol { margin: 0 0 1rem; padding-inline-start: 1.35rem; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; grid-template-rows: auto 1fr; }
  nav.toc {
    position: sticky;
    top: 0;
    z-index: 10;
    max-height: none;
    border-inline-start: none;
    border-bottom: 1px solid var(--border);
    padding: 0.75rem 1rem;
  }
  nav.toc ol {
    display: flex;
    flex-wrap: nowrap;
    gap: 0.35rem;
    overflow-x: auto;
    padding-bottom: 0.25rem;
    -webkit-overflow-scrolling: touch;
  }
  nav.toc li { flex: 0 0 auto; }
  nav.toc a { white-space: nowrap; font-size: 0.8rem; }
  main.content { padding-top: 1.25rem; }
}
"""

JS = """
document.querySelectorAll('nav.toc a').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(a.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth' });
  });
});
const sections = [...document.querySelectorAll('.doc-section')];
const links = [...document.querySelectorAll('nav.toc a')];
const byId = Object.fromEntries(links.map(l => [l.getAttribute('href').slice(1), l]));
const obs = new IntersectionObserver(entries => {
  entries.forEach(en => {
    if (en.isIntersecting) {
      links.forEach(l => l.classList.remove('active'));
      byId[en.target.id]?.classList.add('active');
    }
  });
}, { rootMargin: '-20% 0px -65% 0px', threshold: 0 });
sections.forEach(s => obs.observe(s));
"""

NAV_LABELS = [
    ("intro", "الخريطة"),
    ("s1", "Domain Logic"),
    ("s2", "Data Source"),
    ("s3", "OR Behavioral"),
    ("s4", "OR Structural"),
    ("s5", "OR Metadata"),
    ("s6", "Web Presentation"),
    ("s7", "Distribution"),
    ("s8", "Concurrency"),
    ("s9", "Session State"),
    ("s10", "Base Patterns"),
    ("s11", "مع بعض"),
    ("s12", "خريطة المراجعة"),
    ("s13", "Odoo & Python"),
]


def build_nav() -> str:
    items = "".join(f'<li><a href="#{sid}">{label}</a></li>' for sid, label in NAV_LABELS)
    return f'<nav class="toc" aria-label="أقسام المرجع"><p class="toc-title">POEAA</p><ol>{items}</ol></nav>'


def main() -> None:
    intro_para, body = load_source()
    content = convert_markdown(body, intro_para)

    doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>مرجع Enterprise Application Patterns</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>{CSS}</style>
</head>
<body>
  <div class="layout">
    {build_nav()}
    <main class="content">
      {content}
    </main>
  </div>
  <script>{JS}</script>
</body>
</html>
"""
    OUT.write_text(doc, encoding="utf-8")
    print(f"Wrote {OUT} ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
