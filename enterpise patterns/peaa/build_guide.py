"""Roadmap section and guide assembly."""

from __future__ import annotations

import json
from pathlib import Path

from peaa.authoring.model import Section
from peaa.authoring.part1 import sections as part1
from peaa.authoring.part2_behavior import sections as behavior
from peaa.authoring.part2_interface import sections as interface
from peaa.authoring.part2_structure import sections as structure
from peaa.authoring.part3 import sections as part3
from peaa.authoring.render import write_guide

ROOT = Path(__file__).resolve().parents[1]
OUTLINE = Path(__file__).resolve().parent / "data" / "peaa-outline.json"
GUIDE = ROOT / "enterprise-patterns-guide.html"

ROADMAP_HTML = """
<div class="grid-2">
  <div class="roadmap-week"><div class="roadmap-week-title">Weeks 1–2</div><ul>
    <li><a href="#ch01-layering">Layering</a> و<a href="#ch02-domain-logic">تنظيم الدومين</a></li>
    <li><a href="#pattern-transaction-script">Transaction Script</a> مقابل <a href="#pattern-domain-model">Domain Model</a></li>
    <li><a href="#pattern-service-layer">Service Layer</a></li>
  </ul></div>
  <div class="roadmap-week"><div class="roadmap-week-title">Weeks 3–5</div><ul>
    <li><a href="#ch10-data-source">مصدر البيانات</a> حتى <a href="#pattern-data-mapper">Data Mapper</a></li>
    <li><a href="#ch11-or-behavioral">Unit of Work</a> و<a href="#pattern-lazy-load">Lazy Load</a></li>
    <li><a href="#ch12-or-structural">المفاتيح والوراثة</a></li>
  </ul></div>
  <div class="roadmap-week"><div class="roadmap-week-title">Weeks 6–7</div><ul>
    <li><a href="#ch14-web">ويب</a>: <a href="#pattern-mvc">MVC</a> إلى <a href="#pattern-application-controller">Application Controller</a></li>
    <li><a href="#pattern-remote-facade">Remote Facade</a> و<a href="#pattern-dto">DTO</a></li>
  </ul></div>
  <div class="roadmap-week"><div class="roadmap-week-title">Weeks 8–9</div><ul>
    <li><a href="#ch05-concurrency">تزامن المستخدمين</a> و<a href="#ch16-offline">أقفال أوفلاين</a></li>
    <li><a href="#ch17-session">حالة الجلسة</a></li>
  </ul></div>
  <div class="roadmap-week"><div class="roadmap-week-title">Weeks 10–11</div><ul>
    <li><a href="#ch18-base">أنماط الأساس</a> و<a href="#pattern-money">Money</a></li>
    <li>كابستون: أعد تجميع <a href="#ch08-together">مسار العقد</a> بخدمة ومابر</li>
  </ul></div>
  <div class="roadmap-week"><div class="roadmap-week-title">Weeks 12–13</div><ul>
    <li><a href="#part3-concurrency">Part 3</a>: <a href="#conc-thread-pool">Pool</a> و<a href="#conc-producer-consumer">طابور</a></li>
    <li><a href="#conc-rwlock">أقفال</a> و<a href="#conc-barrier">Barrier</a></li>
  </ul></div>
  <div class="roadmap-week"><div class="roadmap-week-title">Week 14</div><ul>
    <li><a href="#conc-reactor">Reactor</a> و<a href="#conc-proactor">Proactor</a></li>
    <li><a href="#conc-rate-limiter">Rate Limiter</a> و<a href="#conc-bulkhead">Bulkhead</a> و<a href="#conc-monitor-object">Monitor</a></li>
  </ul></div>
</div>
"""


def roadmap() -> Section:
    return Section(
        id="roadmap",
        nav="خارطة 14 أسبوع",
        group="الختام",
        title="Study Roadmap",
        subtitle="أربعة عشر أسبوعًا من السرد إلى الخيوط",
        icon="🗺️",
        tone="purple",
        intent="الخطة تمشي مع ترتيب الكتاب ثم جزء الخيوط. كل أسبوع يربطك بأقسام الدليل. لو عندك خبرة، اضغط الأسبوعين في واحد وخلّي الكابستون والمعامل ثابتين.",
        use=["مذاكرة بدوام جزئي حوالي 6–8 ساعات في الأسبوع.", "تحضير تصميم تطبيقات أعمال ومقابلة معمارية."],
        avoid=["حفظ الأسماء من غير تشغيل معمل.", "خلط أسبوع الأوفلاين مع أسبوع الخيوط في نفس اليوم من غير جملة الفرق."],
        diagram="1–2 domain · 3–5 data · 6–7 web · 8–9 sessions · 10–11 base · 12–14 threads",
        relations=[("Layering", "ch01-layering"), ("Data Mapper", "pattern-data-mapper"), ("Part 3", "part3-concurrency")],
        lab="peaa/lab/lease_app/story.py",
        demo="together",
        snippet="""
# week 11 capstone, from enterpise patterns/
python -m peaa.lab.run_demo together
python -m peaa.lab.run_demo optimistic_offline_lock
python -m peaa.lab.run_demo monitor_object
        """,
        tasks=[
            "في الأسبوع ١١ أعد مسار bill بخدمة ومابر واكتب الطبقات في تعليق قصير.",
            "في الأسبوع ١٤ شغّل rate_limiter و bulkhead واكتب جملة تفرقهم عن Optimistic Offline Lock.",
        ],
        questions=[
            ("أسبوعا ٣–٥ عن إيه؟", "مصدر البيانات وسلوك الربط وهيكله."),
            ("ليهه الأوفلاين قبل الجزء ٣؟", "عشان تخلص مفردات الكتاب ثم تضيف الخيوط من غير خلط."),
            ("إيه كابستون الجزء ١١؟", "إعادة تجميع عقد التأجير بخدمة ومابر."),
            ("أسبوع ١٤ يغطي إيه؟", "مفاعل وإكمال، ثم محدّد ومجمع حاجز ومراقب."),
        ],
        html_block=ROADMAP_HTML,
    )


def all_sections() -> list[Section]:
    return [*part1(), *behavior(), *structure(), *interface(), *part3(), roadmap()]


def check_outline(sections: list[Section]) -> None:
    payload = json.loads(OUTLINE.read_text(encoding="utf-8"))
    wanted = [item["id"] for item in payload["entries"]] + [item["id"] for item in payload["addons"]]
    have = {section.id for section in sections}
    missing = [item for item in wanted if item not in have]
    if missing:
        raise SystemExit("missing sections: " + ", ".join(missing))


def main() -> None:
    sections = all_sections()
    check_outline(sections)
    write_guide(sections, GUIDE)
    print(f"wrote {GUIDE} ({len(sections)} sections)")


if __name__ == "__main__":
    main()
