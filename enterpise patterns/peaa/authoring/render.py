"""Render study sections to one HTML guide."""

from __future__ import annotations

import html
import re
from pathlib import Path

from peaa.authoring.model import Section

_TOKEN = re.compile(
    r"(#.*?$)"
    r"|(\"(?:\\.|[^\"\\])*\")"
    r"|('(?:\\.|[^'\\])*')"
    r"|\b(class|def|return|if|elif|else|for|while|import|from|as|with|try|except|raise|None|True|False|and|or|not|in|is|lambda|yield|async|await)\b"
    r"|(\b\d+\b)"
    r"|\b([A-Z][A-Za-z0-9_]*)\b",
    re.M,
)


def highlight(src: str) -> str:
    parts: list[str] = []
    pos = 0
    for match in _TOKEN.finditer(src):
        parts.append(html.escape(src[pos : match.start()]))
        comment, dbl, single, keyword, number, cls = match.groups()
        if comment is not None:
            parts.append(f'<span class="cm">{html.escape(comment)}</span>')
        elif dbl is not None or single is not None:
            parts.append(f'<span class="str">{html.escape(match.group(0))}</span>')
        elif keyword is not None:
            parts.append(f'<span class="kw">{keyword}</span>')
        elif number is not None:
            parts.append(f'<span class="num">{number}</span>')
        elif cls is not None:
            parts.append(f'<span class="cl">{cls}</span>')
        pos = match.end()
    parts.append(html.escape(src[pos:]))
    return "".join(parts)


def _lis(items: list[str]) -> str:
    body = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return f'<ul class="plain-list">{body}</ul>'


def _code(snippet: str, lang: str = "Python") -> str:
    return f"""<button class="code-toggle" type="button" onclick="toggleCode(this)">عرض الكود ↓</button>
<div class="collapsible">
<div class="code-wrap">
<div class="code-header"><div class="code-dots"><div class="code-dot" style="background:#ff5f57"></div><div class="code-dot" style="background:#febc2e"></div><div class="code-dot" style="background:#28c840"></div></div><div class="code-lang">{html.escape(lang)}</div></div>
<pre>{highlight(snippet.strip())}</pre>
</div>
</div>"""


def render_section(section: Section) -> str:
    section.validate()
    rel = "".join(
        f'<a href="#{html.escape(target)}">{html.escape(label)}</a>'
        for label, target in section.relations
    )
    notes = "".join(f"<p class=\"lead\">{html.escape(note)}</p>" for note in section.notes)
    tasks = "".join(
        f'<div class="task-card"><div class="task-card-label">مهمة {index}</div><p>{html.escape(task)}</p></div>'
        for index, task in enumerate(section.tasks, start=1)
    )
    questions = "".join(
        f"""<div class="question-block"><p><strong>{index}.</strong> {html.escape(question)}</p>
<details class="answer-panel"><summary>الإجابة</summary><p>{html.escape(answer)}</p></details></div>"""
        for index, (question, answer) in enumerate(section.questions, start=1)
    )
    return f"""
<section class="section" id="{html.escape(section.id)}">
  <div class="section-header">
    <div class="section-icon bg-{section.tone}">{section.icon}</div>
    <div>
      <div class="section-title c-{section.tone}">{html.escape(section.title)}</div>
      <div class="subtitle-ar">{html.escape(section.subtitle)}</div>
    </div>
  </div>
  <p class="lead">{html.escape(section.intent)}</p>
  {notes}
  <div class="grid-2">
    <div class="card bg-teal">
      <div class="card-title c-teal">متى تستخدمه</div>
      {_lis(section.use)}
    </div>
    <div class="card bg-coral">
      <div class="card-title c-coral">متى تتجنبه</div>
      {_lis(section.avoid)}
    </div>
  </div>
  <div class="diagram-box">
    <div class="code-header"><div class="code-lang">Map</div></div>
    <pre>{html.escape(section.diagram.strip())}</pre>
  </div>
  <p class="lead" style="margin-bottom:8px;">أنماط قريبة</p>
  <div class="rel-links">{rel}</div>
  <p class="lab-meta">lab: {html.escape(section.lab)} · python -m peaa.lab.run_demo {html.escape(section.demo)}</p>
  {_code(section.snippet)}
  {section.html_block}
  <h3 class="section-title" style="font-size:18px;margin:28px 0 8px;">مهام</h3>
  {tasks}
  <h3 class="section-title" style="font-size:18px;margin:28px 0 8px;">أسئلة</h3>
  {questions}
</section>
"""


def render_nav(sections: list[Section]) -> str:
    chunks = [
        '<div class="nav-logo">PEAA Guide</div>',
        '<a href="../index.html" class="nav-link nav-link--hub"><span class="nav-dot"></span>← Road Map</a>',
    ]
    current = None
    for section in sections:
        if section.group != current:
            current = section.group
            chunks.append(f'<div class="nav-section">{html.escape(current)}</div>')
        chunks.append(
            f'<a href="#{html.escape(section.id)}" class="nav-link"><span class="nav-dot"></span>{html.escape(section.nav)}</a>'
        )
    return "\n".join(chunks)


def render_page(sections: list[Section]) -> str:
    body = "\n".join(render_section(section) for section in sections)
    pattern_count = sum(1 for section in sections if section.id.startswith("pattern-"))
    conc_count = sum(1 for section in sections if section.id.startswith("conc-"))
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Enterprise Patterns — دليل PEAA</title>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Tajawal:wght@300;400;500;700&family=Space+Grotesk:wght@400;500;600;700&family=Cairo:wght@300;400;600;700;900&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../roadmap.css">
<script src="../roadmap.js" defer></script>
</head>
<body class="page-guide">

<div class="progress-bar" id="progress"></div>
<button class="nav-toggle" id="navToggle" type="button" aria-label="فتح القائمة" onclick="toggleNav()">☰</button>
<div class="nav-backdrop" id="navBackdrop" onclick="closeNav()"></div>

<nav class="side-nav" id="sidenav">
{render_nav(sections)}
</nav>

<div class="main-wrapper">
<div class="hero">
  <div class="hero-badge">Study Guide · original notes</div>
  <h1>Enterprise Patterns</h1>
  <p>خريطة دراسية لأنماط تطبيقات المؤسسات، على قصة عقود التأجير، مع جزء إضافي لتزامن الخيوط والمهام. الشرح مكتوب من جديد، وأسماء الأنماط تتبع فهرس الكتاب.</p>
  <div class="hero-stats">
    <div class="hero-stat"><div class="num">8</div><div class="lbl">Narrative chapters</div></div>
    <div class="hero-stat"><div class="num">{pattern_count}</div><div class="lbl">PEAA patterns</div></div>
    <div class="hero-stat"><div class="num">{conc_count}</div><div class="lbl">Thread patterns</div></div>
    <div class="hero-stat"><div class="num">14</div><div class="lbl">Week roadmap</div></div>
    <div class="hero-stat"><div class="num">80–110</div><div class="lbl">Study hours</div></div>
  </div>
</div>
{body}
<footer class="landing-footer" style="margin-inline-start:0;">
  <p>Enterprise Patterns · شرح أصلي للمذاكرة · المعامل: <code style="font-family:var(--mono);font-size:12px;">python -m peaa.lab.run_demo --list</code></p>
</footer>
</div>
</body>
</html>
"""


def write_guide(sections: list[Section], path: Path) -> None:
    ids = [section.id for section in sections]
    if len(ids) != len(set(ids)):
        raise SystemExit("duplicate section id")
    path.write_text(render_page(sections), encoding="utf-8")
