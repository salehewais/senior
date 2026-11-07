#!/usr/bin/env python3
"""Build multi-page RTL HTML from POEAA3/source/combined.md only."""
from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source" / "combined.md"
OUT_DIR = ROOT

# Category boundaries detected from scraped headings / explicit category prose.
# First match of each regex wins; order is reading order in combined.md.
BOUNDARY_SPECS: list[tuple[str, str, str]] = [
    (
        r"^#\s+1\.\s+المشكلة اللي Separated Interface بيحلها\s*$",
        "Separated Interface",
        "separated-interface.html",
    ),
    (
        r"^#\s+1\.\s+Gateway\s*$",
        "Base Patterns",
        "base-patterns.html",
    ),
    (
        r"^#\s+Domain Logic Patterns\s*$",
        "Domain Logic Patterns",
        "domain-logic-patterns.html",
    ),
    (
        r"^#\s+Data Source Architectural Patterns\s*$",
        "Data Source Architectural Patterns",
        "data-source-architectural-patterns.html",
    ),
    (
        r"^#\s+Object-Relational Behavioral Patterns\s*$",
        "Object-Relational Behavioral Patterns",
        "object-relational-behavioral-patterns.html",
    ),
    (
        r"^#\s+Object-Relational Structural Patterns\s*$",
        "Object-Relational Structural Patterns",
        "object-relational-structural-patterns.html",
    ),
    (
        r"نكمل في \*\*Object-Relational Metadata Mapping Patterns\*\*",
        "Object-Relational Metadata Mapping Patterns",
        "object-relational-metadata-mapping-patterns.html",
    ),
    (
        r"^#\s+Web Presentation Patterns\s*$",
        "Web Presentation Patterns",
        "web-presentation-patterns.html",
    ),
    (
        r"^#\s+Distribution Patterns\s*$",
        "Distribution Patterns",
        "distribution-patterns.html",
    ),
    (
        r"^#\s+Offline Concurrency Patterns\s*$",
        "Offline Concurrency Patterns",
        "offline-concurrency-patterns.html",
    ),
    (
        r"^#\s+Session State Patterns\s*$",
        "Session State Patterns",
        "session-state-patterns.html",
    ),
]


@dataclass
class Category:
    title: str
    filename: str
    body: str


def load_source() -> str:
    text = SOURCE.read_text(encoding="utf-8")
    # Drop scrape source markers
    text = re.sub(r"^<!-- SOURCE:.*?-->\s*", "", text, flags=re.M)
    return text.strip() + "\n"


def split_categories(text: str) -> tuple[str, list[Category]]:
    matches: list[tuple[int, str, str]] = []
    for pattern, title, filename in BOUNDARY_SPECS:
        m = re.search(pattern, text, flags=re.M)
        if not m:
            continue
        matches.append((m.start(), title, filename))
    matches.sort(key=lambda t: t[0])

    # De-dupe identical filenames if a later marker somehow collides
    seen_files: set[str] = set()
    unique: list[tuple[int, str, str]] = []
    for start, title, filename in matches:
        if filename in seen_files:
            continue
        seen_files.add(filename)
        unique.append((start, title, filename))

    if not unique:
        raise SystemExit("No category boundaries found in combined.md")

    preamble = text[: unique[0][0]].strip()
    cats: list[Category] = []
    for i, (start, title, filename) in enumerate(unique):
        end = unique[i + 1][0] if i + 1 < len(unique) else len(text)
        body = text[start:end].strip()
        cats.append(Category(title=title, filename=filename, body=body))
    return preamble, cats


def inline_md(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r'<code class="inline">\1</code>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    return text


def detect_lang(code: str, fence_lang: str) -> str:
    if fence_lang:
        return fence_lang.lower()
    s = code.strip()
    if s.upper().startswith("CREATE ") or "PRIMARY KEY" in s.upper():
        return "sql"
    if s.startswith("{") and s.endswith("}"):
        return "json"
    return "python"


def render_code(code: str, fence_lang: str = "") -> str:
    lang = detect_lang(code, fence_lang)
    escaped = html.escape(code.rstrip("\n"))
    return (
        f'<div class="code-wrap" dir="ltr">'
        f'<div class="code-bar"><span class="lang">{html.escape(lang)}</span></div>'
        f'<pre class="code-block"><code class="language-{html.escape(lang)}">{escaped}</code></pre>'
        f"</div>"
    )


def render_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    out = ['<div class="table-wrap"><table>']
    header, body = rows[0], rows[1:]
    out.append("<thead><tr>")
    for cell in header:
        out.append(f"<th>{inline_md(cell)}</th>")
    out.append("</tr></thead><tbody>")
    for row in body:
        out.append("<tr>")
        for cell in row:
            out.append(f"<td>{inline_md(cell)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def is_pattern_h1(title: str) -> bool:
    return bool(re.match(r"^\d+\.\s+\S", title)) and "Patterns" not in title


def md_to_html(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    in_ul = False
    in_ol = False
    card_open = False

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_card() -> None:
        nonlocal card_open
        if card_open:
            out.append("</div></article>")
            card_open = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if stripped.startswith("```"):
            close_lists()
            fence_lang = stripped[3:].strip()
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            out.append(render_code("\n".join(code_lines), fence_lang))
            continue

        if stripped.startswith("|") and "|" in stripped[1:]:
            close_lists()
            rows: list[list[str]] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                row_line = lines[i].strip()
                if re.match(r"^\|\s*-+", row_line):
                    i += 1
                    continue
                cells = [c.strip() for c in row_line.strip("|").split("|")]
                rows.append(cells)
                i += 1
            out.append(render_table(rows))
            continue

        if not stripped:
            close_lists()
            i += 1
            continue

        if stripped.startswith("#### "):
            close_lists()
            out.append(f"<h4>{inline_md(stripped[5:])}</h4>")
            i += 1
            continue

        if stripped.startswith("### "):
            close_lists()
            out.append(f"<h3>{inline_md(stripped[4:])}</h3>")
            i += 1
            continue

        if stripped.startswith("## "):
            close_lists()
            close_card()
            out.append(f"<h2>{inline_md(stripped[3:])}</h2>")
            i += 1
            continue

        if stripped.startswith("# "):
            close_lists()
            title = stripped[2:].strip()
            if is_pattern_h1(title):
                close_card()
                slug = re.sub(r"[^\w\u0600-\u06ff]+", "-", title).strip("-").lower()
                out.append(f'<article class="pattern-card" id="{html.escape(slug)}">')
                out.append(f'<h3 class="pattern-title">{inline_md(title)}</h3>')
                out.append('<div class="card-body">')
                card_open = True
            else:
                close_card()
                out.append(f'<h2 class="section-title">{inline_md(title)}</h2>')
            i += 1
            continue

        if re.match(r"^[-*]\s+", stripped):
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_md(re.sub(r'^[-*]\s+', '', stripped))}</li>")
            i += 1
            continue

        if re.match(r"^\d+\.\s+", stripped):
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_md(re.sub(r'^\d+\.\s+', '', stripped))}</li>")
            i += 1
            continue

        if stripped.startswith("> "):
            close_lists()
            quote = [stripped[2:]]
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                q = lines[i].strip()
                quote.append(q[2:] if q.startswith("> ") else q[1:])
                i += 1
            out.append("<blockquote>" + "<br>".join(inline_md(q) for q in quote) + "</blockquote>")
            continue

        if stripped == "---":
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        close_lists()
        out.append(f"<p>{inline_md(stripped)}</p>")
        i += 1

    close_lists()
    close_card()
    return "\n".join(out)


CSS = r"""
:root {
  --bg: #eef0f5;
  --surface: #ffffff;
  --surface-2: #f6f7fb;
  --ink: #131a2a;
  --ink-muted: #596177;
  --accent: #3a50d9;
  --accent-soft: rgba(58, 80, 217, 0.10);
  --border: rgba(19, 26, 42, 0.11);
  --shadow: 0 1px 2px rgba(19, 26, 42, .05), 0 10px 30px -12px rgba(19, 26, 42, .14);
  --font-ar: "IBM Plex Sans Arabic", system-ui, sans-serif;
  --font-head: "Cairo", "IBM Plex Sans Arabic", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;
  color-scheme: light;
}
:root[data-theme="dark"] {
  --bg: #0c1018;
  --surface: #141a25;
  --surface-2: #19212f;
  --ink: #e7ebf4;
  --ink-muted: #9aa4ba;
  --accent: #8da2ff;
  --accent-soft: rgba(141, 162, 255, 0.13);
  --border: rgba(231, 235, 244, 0.10);
  --shadow: 0 1px 2px rgba(0,0,0,.3), 0 12px 32px -14px rgba(0,0,0,.6);
  color-scheme: dark;
}
*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-ar);
  font-size: 1.05rem;
  line-height: 1.85;
  color: var(--ink);
  background:
    radial-gradient(1200px 500px at 100% -10%, rgba(58,80,217,.10), transparent 55%),
    radial-gradient(900px 420px at 0% 100%, rgba(14,143,134,.08), transparent 50%),
    var(--bg);
}
.layout { display: grid; grid-template-columns: 17rem minmax(0, 1fr); min-height: 100vh; }
nav.toc {
  position: sticky; top: 0; align-self: start; max-height: 100vh; overflow-y: auto;
  padding: 1.25rem 1rem 2rem; background: var(--surface); border-inline-end: 1px solid var(--border);
}
.toc-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; padding-bottom: .75rem; border-bottom: 1px solid var(--border); }
.toc-title { font-family: var(--font-head); font-weight: 800; font-size: 1.25rem; margin: 0; }
.toc-title a { color: inherit; text-decoration: none; }
.icon-btn {
  width: 2.1rem; height: 2.1rem; display: grid; place-items: center; cursor: pointer;
  border: 1px solid var(--border); border-radius: 50%; background: var(--surface-2); color: var(--ink);
}
nav.toc ol { list-style: none; margin: 0; padding: 0; }
nav.toc a {
  display: block; padding: .45rem .65rem; border-radius: 8px; margin-bottom: .2rem;
  color: var(--ink-muted); text-decoration: none; font-size: .88rem; line-height: 1.4;
}
nav.toc a:hover, nav.toc a.active { background: var(--accent-soft); color: var(--ink); font-weight: 600; }
main.content { padding: 1.5rem clamp(1.25rem, 4vw, 3.5rem) 5rem; max-width: 56rem; width: 100%; margin-inline: auto; }
.page-header {
  position: relative; overflow: hidden; isolation: isolate;
  margin: 0 0 2rem; padding: clamp(1.4rem, 3.5vw, 2.4rem);
  border-radius: 22px; color: #f4f6ff;
  background: linear-gradient(135deg, #1d2a6b 0%, #2b3fc4 55%, #0e8f86 130%);
  box-shadow: var(--shadow);
}
.page-header h1 { font-family: var(--font-head); font-weight: 800; font-size: clamp(1.6rem, 4vw, 2.4rem); margin: 0 0 .6rem; line-height: 1.35; }
.page-header .lead { margin: 0; color: rgba(244,246,255,.86); max-width: 40rem; }
.hub-list { list-style: none; margin: 0; padding: 0; display: grid; gap: .75rem; }
.hub-list a {
  display: block; padding: 1rem 1.2rem; border-radius: 14px; text-decoration: none;
  background: var(--surface); border: 1px solid var(--border); color: var(--ink);
  box-shadow: var(--shadow); transition: border-color .15s, transform .15s;
}
.hub-list a:hover { border-color: color-mix(in srgb, var(--accent) 45%, var(--border)); transform: translateY(-1px); }
.hub-list strong { font-family: var(--font-head); display: block; margin-bottom: .2rem; }
.hub-list span { color: var(--ink-muted); font-size: .92rem; }
.section-title, h2 {
  font-family: var(--font-head); font-weight: 800; font-size: clamp(1.25rem, 2.4vw, 1.55rem);
  margin: 1.6rem 0 1rem; border-inline-start: 5px solid var(--accent); padding-inline-start: .85rem;
}
h3 { font-family: var(--font-head); font-size: 1.15rem; margin: 1.3rem 0 .7rem; }
h4 { margin: 1.1rem 0 .5rem; color: var(--accent); }
p { margin: 0 0 1rem; }
ul, ol { margin: 0 0 1rem; padding-inline-start: 1.35rem; }
li::marker { color: var(--accent); font-weight: 700; }
blockquote {
  margin: 1rem 0; padding: .8rem 1rem; border-inline-start: 3px solid var(--accent);
  background: var(--surface-2); border-radius: 0 10px 10px 0; color: var(--ink-muted);
}
hr { border: 0; border-top: 1px solid var(--border); margin: 2rem 0; }
.pattern-card {
  background: var(--surface); border: 1px solid var(--border); border-radius: 16px;
  margin: 1.1rem 0; box-shadow: var(--shadow); overflow: hidden;
  border-inline-start: 4px solid var(--accent);
}
.pattern-title {
  margin: 0; padding: 1rem 1.3rem .4rem; font-size: 1.12rem; font-weight: 700;
}
.card-body { padding: 0 1.3rem 1.2rem; }
.code-wrap {
  margin: .9rem 0 1.1rem; border-radius: 12px; overflow: hidden;
  background: #0f1420; border: 1px solid rgba(255,255,255,.08); direction: ltr;
}
.code-bar { padding: .35rem .9rem; background: #171d2c; border-bottom: 1px solid rgba(255,255,255,.07); }
.code-bar .lang { font: .75rem var(--font-mono); color: #8a94ad; }
.code-block {
  font-family: var(--font-mono); font-size: .84rem; line-height: 1.65; color: #dbe2f3;
  padding: 1rem 1.1rem; margin: 0; overflow-x: auto; white-space: pre;
}
code.inline {
  font-family: var(--font-mono); font-size: .86em; background: var(--accent-soft);
  color: var(--accent); padding: .1em .4em; border-radius: 6px; direction: ltr; unicode-bidi: embed;
}
.table-wrap { overflow-x: auto; margin: 1rem 0 1.5rem; border-radius: 14px; border: 1px solid var(--border); box-shadow: var(--shadow); }
table { width: 100%; border-collapse: collapse; font-size: .93rem; background: var(--surface); }
th, td { padding: .75rem 1rem; text-align: start; border-bottom: 1px solid var(--border); vertical-align: top; }
th { background: var(--surface-2); font-weight: 700; }
.page-nav {
  display: flex; flex-wrap: wrap; gap: .75rem; justify-content: space-between;
  margin-top: 2.5rem; padding-top: 1.25rem; border-top: 1px solid var(--border);
}
.page-nav a {
  color: var(--accent); text-decoration: none; font-weight: 600;
  padding: .55rem .9rem; border-radius: 10px; background: var(--accent-soft);
}
.note {
  font-size: .95rem; color: var(--ink-muted); padding: .85rem 1rem;
  background: var(--surface); border: 1px dashed var(--border); border-radius: 12px;
}
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  nav.toc { position: relative; max-height: none; border-inline-end: 0; border-bottom: 1px solid var(--border); }
  nav.toc ol { display: flex; gap: .25rem; overflow-x: auto; }
  nav.toc li { flex: none; }
  nav.toc a { white-space: nowrap; }
}
"""


def shell_page(
    title: str,
    body_html: str,
    cats: list[Category],
    active_file: str | None,
    prev_cat: Category | None = None,
    next_cat: Category | None = None,
) -> str:
    nav_items = ['<li><a href="index.html"' + (' class="active"' if active_file is None else '') + ">الرئيسية</a></li>"]
    for c in cats:
        cls = ' class="active"' if c.filename == active_file else ""
        nav_items.append(f'<li><a href="{html.escape(c.filename)}"{cls}>{html.escape(c.title)}</a></li>')

    page_nav = ""
    if active_file is not None:
        prev_html = (
            f'<a href="{html.escape(prev_cat.filename)}">→ {html.escape(prev_cat.title)}</a>'
            if prev_cat
            else '<a href="index.html">→ الرئيسية</a>'
        )
        next_html = (
            f'<a href="{html.escape(next_cat.filename)}">{html.escape(next_cat.title)} ←</a>'
            if next_cat
            else "<span></span>"
        )
        page_nav = f'<nav class="page-nav" aria-label="تنقل الصفحات">{prev_html}{next_html}</nav>'

    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@600;700;800&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Arabic:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/site.css">
</head>
<body>
  <div class="layout">
    <nav class="toc" aria-label="أقسام المرجع">
      <div class="toc-head">
        <p class="toc-title"><a href="index.html">POEAA</a></p>
        <button class="icon-btn" id="theme" type="button" aria-label="تبديل الوضع">☾</button>
      </div>
      <ol>
        {''.join(nav_items)}
      </ol>
    </nav>
    <main class="content">
      {body_html}
      {page_nav}
    </main>
  </div>
  <script>
    const root = document.documentElement;
    const saved = localStorage.getItem('poeaa3-theme');
    if (saved) root.setAttribute('data-theme', saved);
    document.getElementById('theme')?.addEventListener('click', () => {{
      const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      if (next === 'dark') root.setAttribute('data-theme', 'dark'); else root.removeAttribute('data-theme');
      localStorage.setItem('poeaa3-theme', next === 'dark' ? 'dark' : 'light');
    }});
  </script>
</body>
</html>
"""


def intro_from_preamble(preamble: str) -> str:
    """Short hub intro taken only from scraped preamble text."""
    lines = []
    for line in preamble.split("\n"):
        s = line.strip()
        if not s or s.startswith("<!--"):
            continue
        if s.startswith("#"):
            break
        # skip pure punctuation / backslash artifacts
        if s in {"\\", ">", "---"}:
            continue
        lines.append(s)
        if len(" ".join(lines)) > 320:
            break
    text = " ".join(lines).strip()
    if not text:
        # fall back to first non-empty paragraph anywhere in preamble
        for line in preamble.split("\n"):
            s = line.strip()
            if s and not s.startswith("#") and not s.startswith("<!--"):
                text = s
                break
    return text


def build() -> None:
    text = load_source()
    preamble, cats = split_categories(text)

    assets = OUT_DIR / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "site.css").write_text(CSS, encoding="utf-8")

    intro = intro_from_preamble(preamble)
    hub_items = []
    for c in cats:
        # short blurb: first non-heading paragraph inside category
        blurb = ""
        for line in c.body.split("\n"):
            s = line.strip()
            if not s or s.startswith("#") or s.startswith("```") or s.startswith("|"):
                continue
            blurb = s[:160]
            break
        hub_items.append(
            f'<li><a href="{html.escape(c.filename)}"><strong>{html.escape(c.title)}</strong>'
            f"<span>{inline_md(blurb)}</span></a></li>"
        )

    hub_body = f"""
      <header class="page-header">
        <h1>مرجع Patterns of Enterprise Application Architecture</h1>
        <p class="lead">{inline_md(intro)}</p>
      </header>
      <p class="note">المحتوى مأخوذ من محادثات مشروع ChatGPT POEAA فقط — بدون إضافة شروح خارج المصدر.</p>
      <h2>أقسام المرجع</h2>
      <ul class="hub-list">
        {''.join(hub_items)}
      </ul>
    """
    (OUT_DIR / "index.html").write_text(
        shell_page("POEAA — المرجع", hub_body, cats, None),
        encoding="utf-8",
    )

    for i, cat in enumerate(cats):
        prev_cat = cats[i - 1] if i > 0 else None
        next_cat = cats[i + 1] if i + 1 < len(cats) else None
        body = f"""
      <header class="page-header">
        <h1>{html.escape(cat.title)}</h1>
        <p class="lead">من مصدر ChatGPT POEAA — صفحة قسم واحد.</p>
      </header>
      {md_to_html(cat.body)}
        """
        (OUT_DIR / cat.filename).write_text(
            shell_page(f"{cat.title} — POEAA", body, cats, cat.filename, prev_cat, next_cat),
            encoding="utf-8",
        )
        print(f"wrote {cat.filename} ({len(cat.body)} chars)")

    print(f"wrote index.html with {len(cats)} categories")
    for c in cats:
        print(f" - {c.title} -> {c.filename}")


if __name__ == "__main__":
    build()
