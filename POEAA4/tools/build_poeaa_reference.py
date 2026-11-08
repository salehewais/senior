#!/usr/bin/env python3
"""
Build an Arabic RTL HTML reference for Fowler's POEAA patterns
from exported chat sources under source/raw/.

Usage:
  python3 tools/build_poeaa_reference.py            # all groups
  python3 tools/build_poeaa_reference.py --pilot    # Base Patterns only
"""

from __future__ import annotations

import argparse
import html
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SOURCE_RAW = ROOT / "source" / "raw"
DOCS = ROOT / "docs"
CONTENT = DOCS / "content"
GROUPS_DIR = DOCS / "groups"
ASSETS_CSS = DOCS / "assets" / "css"
ASSETS_JS = DOCS / "assets" / "js"

GROUPS: list[dict] = [
    {
        "id": 1,
        "slug": "base-patterns",
        "title_ar": "الأنماط الأساسية",
        "title_en": "Base Patterns",
        "patterns": [
            "Gateway",
            "Mapper",
            "Layer Supertype",
            "Separated Interface",
            "Registry",
            "Value Object",
            "Money",
            "Special Case",
            "Plugin",
            "Service Stub",
            "Record Set",
        ],
    },
    {
        "id": 2,
        "slug": "domain-logic-patterns",
        "title_ar": "أنماط منطق المجال",
        "title_en": "Domain Logic Patterns",
        "patterns": [
            "Transaction Script",
            "Domain Model",
            "Table Module",
            "Service Layer",
        ],
    },
    {
        "id": 3,
        "slug": "data-source-architectural-patterns",
        "title_ar": "أنماط معمارية لمصدر البيانات",
        "title_en": "Data Source Architectural Patterns",
        "patterns": [
            "Table Data Gateway",
            "Row Data Gateway",
            "Active Record",
            "Data Mapper",
        ],
    },
    {
        "id": 4,
        "slug": "object-relational-behavioral",
        "title_ar": "أنماط سلوكية للكائنات والعلاقات",
        "title_en": "Object-Relational Behavioral Patterns",
        "patterns": [
            "Unit of Work",
            "Identity Map",
            "Lazy Load",
        ],
    },
    {
        "id": 5,
        "slug": "object-relational-structural",
        "title_ar": "أنماط هيكلية للكائنات والعلاقات",
        "title_en": "Object-Relational Structural Patterns",
        "patterns": [
            "Identity Field",
            "Foreign Key Mapping",
            "Association Table Mapping",
            "Dependent Mapping",
            "Embedded Value",
            "Serialized LOB",
            "Single Table Inheritance",
            "Class Table Inheritance",
            "Concrete Table Inheritance",
            "Inheritance Mappers",
        ],
    },
    {
        "id": 6,
        "slug": "object-relational-metadata",
        "title_ar": "أنماط البيانات الوصفية للكائنات والعلاقات",
        "title_en": "Object-Relational Metadata Mapping Patterns",
        "patterns": [
            "Metadata Mapping",
            "Query Object",
            "Repository",
        ],
    },
    {
        "id": 7,
        "slug": "web-presentation-patterns",
        "title_ar": "أنماط عرض الويب",
        "title_en": "Web Presentation Patterns",
        "patterns": [
            "Model View Controller",
            "Page Controller",
            "Front Controller",
            "Template View",
            "Transform View",
            "Two Step View",
            "Application Controller",
        ],
    },
    {
        "id": 8,
        "slug": "distribution-patterns",
        "title_ar": "أنماط التوزيع",
        "title_en": "Distribution Patterns",
        "patterns": [
            "Remote Facade",
            "Data Transfer Object",
        ],
    },
    {
        "id": 9,
        "slug": "concurrency-patterns",
        "title_ar": "أنماط التزامن",
        "title_en": "Concurrency Patterns",
        "patterns": [
            "Optimistic Offline Lock",
            "Pessimistic Offline Lock",
            "Coarse-Grained Lock",
            "Implicit Lock",
        ],
    },
    {
        "id": 10,
        "slug": "session-state-patterns",
        "title_ar": "أنماط حالة الجلسة",
        "title_en": "Session State Patterns",
        "patterns": [
            "Client Session State",
            "Server Session State",
            "Database Session State",
        ],
    },
]

PATTERN_TO_GROUP: dict[str, int] = {}
for g in GROUPS:
    for p in g["patterns"]:
        PATTERN_TO_GROUP[p.lower()] = g["id"]

# Aliases found in headings
PATTERN_ALIASES: dict[str, str] = {
    "mvc": "Model View Controller",
    "model view controller": "Model View Controller",
    "model-view-controller": "Model View Controller",
    "active record pattern": "Active Record",
    "money pattern": "Money",
    "dto": "Data Transfer Object",
    "data transfer object (dto)": "Data Transfer Object",
}

SECTION_TITLE_MAP = [
    (re.compile(r"^##\s*\d*\.?\s*The\s+problem.*$", re.I | re.M), "## المشكلة"),
    (re.compile(r"^##\s*\d*\.?\s*The\s+solution.*$", re.I | re.M), "## الفكرة والحل"),
    (re.compile(r"^##\s*\d*\.?\s*When\s+should\s+you\s+use.*$", re.I | re.M), "## متى تستخدمه"),
    (re.compile(r"^##\s*\d*\.?\s*Mental\s+model.*$", re.I | re.M), "## النموذج الذهني"),
    (re.compile(r"^##\s*\d*\.?\s*Structure\s*$", re.I | re.M), "## التركيب"),
    (re.compile(r"^##\s*\d*\.?\s*Implementation\s*$", re.I | re.M), "## التنفيذ"),
    (re.compile(r"^##\s*أولًا:.*المشكلة.*$", re.M), "## المشكلة"),
    (re.compile(r"^##\s*ثانيًا:.*الفكرة.*$", re.M), "## الفكرة والحل"),
    (re.compile(r"^##\s*ثالثًا:.*مثال.*$", re.M), "## مثال"),
    (re.compile(r"^##\s*رابعًا:.*(GoF|بيشبه).*$", re.M), "## أقرب GoF Pattern"),
    (re.compile(r"^##\s*خامسًا:.*Architecture.*$", re.M), "## علاقته بالعمارة"),
    (re.compile(r"^##\s*سادسًا:.*Architecture.*$", re.M), "## علاقته بالعمارة"),
    (re.compile(r"^##\s*\d+\.\s*المشكلة.*$", re.M), "## المشكلة"),
    (re.compile(r"^##\s*\d+\.\s*الفكرة.*$", re.M), "## الفكرة والحل"),
    (re.compile(r"^##\s*\d+\.\s*مثال.*$", re.M), "## مثال"),
    (re.compile(r"^##\s*\d+\.\s*أقرب GoF.*$", re.M), "## أقرب GoF Pattern"),
    (re.compile(r"^##\s*\d+\.\s*علاقته بالـ Application Architecture.*$", re.M), "## علاقته بالعمارة"),
    (re.compile(r"^##\s*\d+\.\s*علاقته بـ Clean Architecture.*$", re.M), "## علاقته بالعمارة"),
    (re.compile(r"^##\s*\d+\.\s*علاقته بـ(?:ـ)?\s*Odoo.*$", re.M), "## علاقته بأودو"),
    (re.compile(r"^##\s*\d+\.\s*علاقته بأودو.*$", re.M), "## علاقته بأودو"),
    (re.compile(r"^##\s*\d+\.\s*إمتى أستخدمه\??\s*$", re.M), "## متى تستخدمه"),
    (re.compile(r"^##\s*إمتى أستخدم.*$", re.M), "## متى تستخدمه"),
    (re.compile(r"^##\s*اختبر فهمك\s*$", re.M), "## اختبر فهمك"),
    (re.compile(r"^\*\*الخلاصة:\*\*\s*$", re.M), "## الخلاصة"),
    (re.compile(r"^##\s*الخلاصة\s*$", re.M), "## الخلاصة"),
]

URL_NOISE_RE = re.compile(
    r"\s*(?:https?://)?(?:www\.)?(?:martinfowler\.com|raw\.githubusercontent\.com|"
    r"web\.eecs\.umich\.edu|bursasiu\.ro)[^\s]*",
    re.I,
)

USERISH_START = re.compile(
    r"^(?:بص|تمام|نكمل|أيوه|اه |إيه رأيك|رد عليا|عايز|هنكمل|كمل|"
    r"معاك حق|طبعا|طبعًا|صح|يلا|هكمل|هننتقل|رابط الكتالوج)",
    re.M,
)

# Build alternation of known pattern names (longest first) to avoid false
# headings like "# False" / "# True" / "# 4000" from code outputs.
_PATTERN_ALT = "|".join(
    re.escape(p)
    for p in sorted(
        {p for g in GROUPS for p in g["patterns"]} | set(PATTERN_ALIASES.keys()),
        key=len,
        reverse=True,
    )
)
PATTERN_HEADING_RE = re.compile(
    rf"^#\s*(?:\d+\.\s*)?(?:النمط\s+(?:الثالث|الرابع|الثاني|الأول|الخامس)\s*:\s*)?"
    rf"(?P<name>{_PATTERN_ALT})(?:\s*\([^)]*\))?(?:\s+Pattern)?\s*$",
    re.M | re.I,
)

GROUP_SUMMARY_RE = re.compile(
    r"^#\s*(مراجعة(?:\s+مجموعة)?[^\n]*|الخريطة النهائية[^\n]*|مراجعة الأنماط[^\n]*)\s*$",
    re.M,
)

GAP_FILLINS: dict[str, str] = {
    "Metadata Mapping": """## المشكلة

تخيل إن عندك عشرات الـ Domain Objects، وكل Object محتاج Mapping صريح إلى جداول وأعمدة قاعدة البيانات.

لو كتبت كل Mapping يدويًا داخل كود ثابت، هتكرر قواعد متشابهة، وهتضطر تعدّل الكود في كل مرة يتغير فيها اسم عمود أو علاقة.

## الفكرة والحل

**Metadata Mapping** بيخلّي وصف التحويل بين Objects والجداول موجودًا كـ Metadata (إعدادات أو وصف تصريحي)، بينما محرّك عام (Mapping Engine) يقرأ هذا الوصف وينفّذ القراءة والكتابة.

بدل ما كل Mapper يحمل تفاصيل الأعمدة في كود صلب، التفاصيل تعيش في طبقة وصف قابلة للتعديل.

## مثال

```python
# Declarative metadata (simplified)
CUSTOMER_MAP = {
    "table": "customers",
    "fields": {
        "id": "id",
        "name": "full_name",
        "email": "email_address",
    },
}

class MetadataMapper:
    def __init__(self, metadata, connection):
        self.metadata = metadata
        self.connection = connection

    def find(self, entity_id):
        table = self.metadata["table"]
        cols = ", ".join(self.metadata["fields"].values())
        sql = f"SELECT {cols} FROM {table} WHERE id = %s"
        row = self.connection.fetch_one(sql, (entity_id,))
        return {
            field: row[column]
            for field, column in self.metadata["fields"].items()
        }
```

## أقرب GoF Pattern

أقرب تشبيه تعليمي هو **Interpreter** أو آليات تعتمد على وصف قابل للتشغيل، لكن مفيش GoF Pattern مطابق.

- التشابه: وجود وصف (Metadata) يُفسَّر في وقت التشغيل بدل منطق صلب متكرر.
- الفرق في الـ Intent: Metadata Mapping هدفه ربط Objects بقاعدة البيانات عبر وصف، وليس تفسير لغة أو قواعد عامة.
- البنية: غالبًا Engine + Metadata Store + Domain/Data representations، بينما Interpreter يركز على شجرة تعبيرات.

## علاقته بالعمارة

يظهر بقوة في ORMs والأطر التي تفصل Domain عن تفاصيل التخزين. يقلل التكرار، لكنه ينقل جزءًا من التعقيد إلى نظام الوصف والتشغيل.

## علاقته بأودو

في Odoo، تعريف الحقول والعلاقات داخل الـ Model (`fields.Char`, `Many2one`, …) يعمل كـ Metadata يقرأها الـ ORM لبناء الاستعلامات والجداول.

هذا قريب من روح Metadata Mapping، مع اختلاف أن Odoo يدمج الوصف مع نموذج كائني خاص بإطاره وليس Mapper منفصلًا بالمعنى الفاولري الحرفي.

## متى تستخدمه

- عند كثرة الكيانات وتكرار قواعد الـ Mapping.
- عندما تريد تغيير الربط دون إعادة كتابة منطق الوصول في كل Mapper.
- تجنّبه إذا كان عدد الكيانات صغيرًا والوضوح اليدوي أهم من العمومية.

## اختبر فهمك

1. ما الفرق بين Mapper مكتوب يدويًا وMetadata Mapping؟
2. هل وجود ORM يعني بالضرورة أنك تطبق Metadata Mapping كما وصفه Fowler؟ لماذا؟

## الخلاصة

Metadata Mapping ينقل تفاصيل الربط بين Objects وقاعدة البيانات إلى وصف يقرأه محرك عام، فيقلل التكرار ويزيد مرونة التغيير على حساب تعقيد طبقة الوصف.
""",
    "Class Table Inheritance": """## المشكلة

عندك تسلسل وراثة في الـ Domain (مثل `Employee` ← `SalariedEmployee` / `HourlyEmployee`)، وتريد حفظ البيانات العلائقية دون تكرار كل الحقول في جدول واحد ضخم، ودون فقدان وضوح كل نوع.

## الفكرة والحل

**Class Table Inheritance** يضع جدولًا لكل صنف في سلسلة الوراثة: جدول للأب يحوي الحقول المشتركة، وجدول لكل ابن يحوي حقوله الخاصة، مع مفتاح يربط صف الابن بصف الأب.

## مثال

```python
# Conceptual schema
# person(id, name)
# employee(person_id FK, employee_number)
# salaried_employee(person_id FK, annual_salary)
# hourly_employee(person_id FK, hourly_rate)

class ClassTablePersonMapper:
    def insert_salaried(self, employee):
        person_id = self.insert_person(employee.name)
        self.insert_employee(person_id, employee.number)
        self.insert_salaried(person_id, employee.annual_salary)
        return person_id
```

## أقرب GoF Pattern

لا يوجد GoF مكافئ مباشر. أقرب حديث بنيوي هو تنظيم التسلسل عبر التركيب الهرمي للجداول، وهو مختلف عن Template Method أو Bridge.

- التشابه السطحي: توزيع المسؤوليات على مستويات.
- الفرق في الـ Intent: هنا استراتيجية تخزين علائقية للوراثة، لا خوارزمية أو فصل Abstraction/Implementation كائني.

## علاقته بالعمارة

تناسب النماذج التي تحتاج مطابقة قريبة بين Class Hierarchy والمخطط العلائقي، مع قبول تكلفة JOIN عند التحميل.

## علاقته بأودو

Odoo يستخدم نماذج ووراثة خاصة (`_inherit`, delegation). وجود جداول متعددة أو امتدادات لا يعني تلقائيًا Class Table Inheritance الفاولري؛ العبرة باستراتيجية التخزين الفعلية وربط الصفوف بين جداول الأب/الابن.

## متى تستخدمه

- عندما تكون الحقول الخاصة بالأنواع كثيرة وتريد تجنب جدول عريض جدًا.
- عندما يهمك تطابق واضح بين الأصناف والجداول.
- تجنّبه إذا كانت قراءات الأنواع المشتقة كثيرة وتكلفة الـ JOINs مؤلمة.

## اختبر فهمك

1. أين تُخزَّن الحقول المشتركة في Class Table Inheritance؟
2. ما الثمن التشغيلي الأشهر لهذه الاستراتيجية؟

## الخلاصة

Class Table Inheritance يقابل كل صنف بجدول، ويربط صفوف الأبناء بالأب، فيحافظ على وضوح الوراثة مقابل تعقيد الاستعلام بالانضمامات.
""",
    "Concrete Table Inheritance": """## المشكلة

تريد تمثيل وراثة Domain في قاعدة علائقية، لكنك تفضّل أن يكون كل نوع ملموس مستقلًا في جدول واحد مكتمل الحقول، بلا JOIN مع جدول أب مشترك عند كل قراءة.

## الفكرة والحل

**Concrete Table Inheritance** ينشئ جدولًا لكل صنف ملموس (Concrete Class) يتضمّن كل حقوله: المشتركة والخاصة. غالبًا لا يوجد جدول للأب المجرّد، أو لا يُستخدم كمصدر أساسي للقراءة.

## مثال

```python
# salaried_employee(id, name, employee_number, annual_salary)
# hourly_employee(id, name, employee_number, hourly_rate)

class ConcreteEmployeeMapper:
    def find_salaried(self, employee_id):
        return self.db.fetch_one(
            "SELECT id, name, employee_number, annual_salary "
            "FROM salaried_employee WHERE id = %s",
            (employee_id,),
        )
```

## أقرب GoF Pattern

لا يوجد نظير GoF مباشر. المقارنة التعليمية تكون مع استراتيجيات الوراثة الأخرى (Single / Class Table)، لا مع أنماط التصميم الكائنية.

- التشابه: كلها حلول لتخزين Hierarchy.
- الفرق في الـ Intent والبنية: هنا جدول مكتفٍ ذاتيًا لكل نوع ملموس، مع تكرار محتمل للحقول المشتركة.

## علاقته بالعمارة

تبسّط قراءة نوع واحد، لكنها تصعّب الاستعلامات عبر كل الأنواع وتزيد خطر تكرار المخطط.

## علاقته بأودو

إن صممت جداول/نماذج منفصلة لكل نوع ملموس مع تكرار الحقول، فقد تقترب من Concrete Table Inheritance. نماذج Odoo القياسية غالبًا لا تطابق هذا حرفيًا؛ افحص التخزين الفعلي قبل التصنيف.

## متى تستخدمه

- عندما تقرأ الأنواع الملموسة منفصلة غالبًا.
- عندما تريد تجنّب JOINs الأب/الابن.
- تجنّبه إذا احتجت استعلامات موحّدة كثيرة عبر كل الفروع أو كرهت تكرار الأعمدة المشتركة.

## اختبر فهمك

1. أين تذهب الحقول المشتركة في Concrete Table Inheritance؟
2. لماذا قد يكون الاستعلام «كل الموظفين» أصعب هنا من Single Table Inheritance؟

## الخلاصة

Concrete Table Inheritance يخزّن كل نوع ملموس في جدول مكتمل، فيسرّع قراءة النوع الواحد مقابل تكرار المخطط وصعوبة الاستعلامات الشاملة.
""",
    "Inheritance Mappers": """## المشكلة

عندما تستخدم واحدة من استراتيجيات وراثة الجداول (Single / Class / Concrete)، تحتاج طبقة Mapping تعرف أي جدول(ات) تقرأ/تكتب حسب نوع الـ Object، دون أن تتسرّب تفاصيل الاستراتيجية إلى كل مكان في التطبيق.

## الفكرة والحل

**Inheritance Mappers** تنظيم لطبقة الـ Mappers يتعامل مع Hierarchy: غالبًا Mapper للأب يوجّه العمل، وMappers للأبناء تتعامل مع التفاصيل الخاصة بكل نوع، بما يتوافق مع استراتيجية التخزين المختارة.

## مثال

```python
class EmployeeMapper:
    def find(self, employee_id):
        kind = self.db.fetch_value(
            "SELECT kind FROM employee WHERE id = %s",
            (employee_id,),
        )
        if kind == "salaried":
            return SalariedEmployeeMapper(self.db).find(employee_id)
        if kind == "hourly":
            return HourlyEmployeeMapper(self.db).find(employee_id)
        raise ValueError("Unknown employee kind")
```

## أقرب GoF Pattern

أقرب تشبيه هو **Factory Method** أو **Strategy** من جهة اختيار السلوك حسب النوع، لكن Intent مختلف.

- التشابه: تفويض حسب النوع أو الاستراتيجية.
- الفرق: Inheritance Mappers جزء من حل Object-Relational للوراثة، لا إنشاء كائنات عام ولا تبديل خوارزمية مستقلة عن التخزين.

## علاقته بالعمارة

تبقي تفاصيل اختيار الجداول وقواعد التحميل داخل طبقة الـ Mapping، وتحمي Domain من معرفة استراتيجية الوراثة العلائقية.

## علاقته بأودو

Odoo ORM يخفي جزءًا كبيرًا من توجيه التحميل والحفظ حسب تعريف النماذج والوراثة. قد تشبه النتيجة روح Inheritance Mappers، لكن التنفيذ إطار عمل متكامل وليس مجموعة Mappers فاولرية صريحة.

## متى تستخدمه

- عند وجود Hierarchy مخزّنة بأي من استراتيجيات Fowler للوراثة.
- عندما تريد نقطة واحدة واعية بالنوع لاسترجاع الكائنات.
- غير ضروري إذا لم تكن لديك وراثة علائقية حقيقية.

## اختبر فهمك

1. ما دور Mapper الأب في Inheritance Mappers؟
2. هل Inheritance Mappers بديل عن Class Table Inheritance أم مكمل لها؟

## الخلاصة

Inheritance Mappers تنظّم طبقة التحويل حول تسلسل الوراثة، فتعزل اختيار الجداول وتحميل الأنواع عن بقية التطبيق، مكملةً لاستراتيجية التخزين المختارة.
""",
}


@dataclass
class PatternBlock:
    name: str
    slug: str
    source_file: str
    body: str
    score: float = 0.0
    group_id: int | None = None


@dataclass
class GroupBundle:
    group: dict
    summary_md: str = ""
    patterns: list[PatternBlock] = field(default_factory=list)


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


def arabic_ratio(text: str) -> float:
    ar = len(re.findall(r"[\u0600-\u06FF]", text))
    lat = len(re.findall(r"[A-Za-z]", text))
    total = ar + lat
    return (ar / total) if total else 0.0


def normalize_pattern_name(raw: str) -> str | None:
    name = raw.strip()
    name = re.sub(r"\s+", " ", name)
    name = re.sub(r"\s+Pattern$", "", name, flags=re.I)
    lower = name.lower()
    if lower in PATTERN_ALIASES:
        return PATTERN_ALIASES[lower]
    # Exact catalog match (case-insensitive)
    for canon in PATTERN_TO_GROUP:
        if canon == lower:
            # recover canonical casing from GROUPS
            gid = PATTERN_TO_GROUP[canon]
            for p in GROUPS[gid - 1]["patterns"]:
                if p.lower() == lower:
                    return p
    # Fuzzy contains for known names (longest first)
    candidates = sorted(PATTERN_TO_GROUP.keys(), key=len, reverse=True)
    for canon in candidates:
        if canon == lower or lower.startswith(canon + " ") or lower.endswith(" " + canon):
            gid = PATTERN_TO_GROUP[canon]
            for p in GROUPS[gid - 1]["patterns"]:
                if p.lower() == canon:
                    return p
    return None


def strip_front_matter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4 :].lstrip("\n")
    return text


def is_probably_user_chunk(chunk: str) -> bool:
    """Heuristic: short conversational / quiz-answer / continue prompts."""
    t = chunk.strip()
    if not t:
        return True
    # Gemini paste-back markers / user asking for reply
    if "سالت جيمناي" in t or "رد عليا" in t or "قالي الاجابة" in t:
        return True
    lines = [ln for ln in t.splitlines() if ln.strip()]
    if len(lines) <= 8 and len(t) < 500:
        if USERISH_START.search(t) or re.match(
            r"^(؟|\d+[\).\s]|Facade|Adapter|Proxy|صح|غلط|ايوه|أيوه)", t.strip()
        ):
            return True
        # Mostly short answers without teaching headings
        if not re.search(r"^#{1,3}\s+", t, re.M) and arabic_ratio(t) > 0.2 and len(t) < 350:
            return True
    return False


def split_turns(text: str) -> list[str]:
    """
    Approximate turn split without role tags:
    break before conversational userish openings that follow a blank line,
    and keep long structured teaching blocks intact.
    """
    text = strip_front_matter(text)
    # Split on double newlines into paragraphs, then regroup
    parts = re.split(r"\n{2,}", text)
    turns: list[str] = []
    buf: list[str] = []

    def flush():
        nonlocal buf
        if buf:
            turns.append("\n\n".join(buf).strip())
            buf = []

    for part in parts:
        p = part.strip()
        if not p:
            continue
        # Likely new user turn starting a short conversational beat
        if buf and is_probably_user_chunk(p) and len(p) < 600:
            flush()
            turns.append(p)
            continue
        # New major assistant teaching after user
        if buf and re.match(r"^#\s+\d+\.\s+[A-Za-z]", p):
            # keep attached to assistant stream
            buf.append(p)
            continue
        buf.append(p)
    flush()
    return turns


def extract_pattern_blocks_from_text(text: str, source_file: str) -> list[PatternBlock]:
    text = strip_front_matter(text)
    blocks: list[PatternBlock] = []
    matches = list(PATTERN_HEADING_RE.finditer(text))
    for i, m in enumerate(matches):
        raw_name = m.group("name").strip()
        # Skip non-pattern headings that look like code titles
        if raw_name.lower() in {"main.py", "true", "registry", "dependency injection"} and not re.match(
            r"^\d+\.", m.group(0)
        ):
            # bare Registry / Dependency Injection comparison headings
            if raw_name.lower() in {"registry"} and "Registry" in GROUPS[0]["patterns"]:
                pass
            else:
                continue
        name = normalize_pattern_name(raw_name)
        if not name:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # Also stop at group summary headings
        summary_hit = GROUP_SUMMARY_RE.search(text, start, end)
        # Allow body to include trailing quiz before next pattern; cut at domain group markers
        body = text[start:end].strip()
        # Truncate if a different major group title appears
        cut = re.search(
            r"^#\s+(Domain Logic Patterns|Data Source|Object.?Relational|Web Presentation|"
            r"Distribution Patterns|Concurrency|Session State|مراجعة)",
            body,
            re.M | re.I,
        )
        if cut and cut.start() > 80:
            body = body[: cut.start()].strip()
        # Drop ultra-short stubs
        if len(body) < 200:
            continue
        # Remove leading conversational restarts that aren't content
        body = re.sub(
            r"^(?:\(PoEAA[^\n]*\)|Base Pattern[^\n]*|\(Base Pattern[^\n]*\))\s*",
            "",
            body,
        ).strip()
        block = PatternBlock(
            name=name,
            slug=slugify(name),
            source_file=source_file,
            body=body,
            group_id=PATTERN_TO_GROUP.get(name.lower()),
        )
        block.score = score_block(block)
        blocks.append(block)
    return blocks


def extract_group_summaries(text: str, source_file: str) -> list[tuple[int | None, str]]:
    text = strip_front_matter(text)
    results: list[tuple[int | None, str]] = []
    matches = list(GROUP_SUMMARY_RE.finditer(text))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        # stop early at next numbered pattern after summary
        chunk = text[start:end]
        cut = PATTERN_HEADING_RE.search(chunk[len(m.group(0)) :])
        if cut:
            # relative offset
            abs_cut = len(m.group(0)) + cut.start()
            # only cut if the summary is long enough already
            if abs_cut > 200:
                chunk = chunk[:abs_cut]
        title = m.group(1)
        gid = None
        low = title.lower()
        if "domain logic" in low or "منطق المجال" in title or "domain" in low:
            gid = 2
        elif "data source" in low or "مصدر البيانات" in title:
            gid = 3
        elif "behavioral" in low or "سلوك" in title:
            gid = 4
        elif "structural" in low or "هيكلي" in title:
            gid = 5
        elif "metadata" in low or "البيانات الوصفية" in title:
            gid = 6
        elif "web" in low or "عرض الويب" in title or "presentation" in low:
            gid = 7
        elif "distribution" in low or "التوزيع" in title:
            gid = 8
        elif "concurrency" in low or "التزامن" in title:
            gid = 9
        elif "session" in low or "الجلسة" in title:
            gid = 10
        elif "الأنماط العشرة" in title or "base" in low or "الأساسية" in title:
            gid = 1
        results.append((gid, chunk.strip()))
    return results


def score_block(block: PatternBlock) -> float:
    body = block.body
    score = 0.0
    score += arabic_ratio(body) * 40
    length_bonus = min(len(body) / 4000.0, 1.0) * 15
    score += length_bonus
    checks = [
        (r"المشكلة|The problem", 8),
        (r"الفكرة|الحل|The solution", 8),
        (r"مثال|```python", 8),
        (r"GoF|Facade|Adapter|Proxy|Strategy|Bridge|Null Object", 10),
        (r"أودو|Odoo", 10),
        (r"اختبر فهمك|قبل ما ننتقل|عايز أتأكد", 6),
        (r"الخلاصة", 5),
        (r"Clean Architecture|DDD|علاقته بال", 5),
        (r"متى|إمتى|When should", 4),
    ]
    for pat, pts in checks:
        if re.search(pat, body, re.I):
            score += pts
    # Prefer Arabic teaching structure markers
    if re.search(r"أولًا:|ثانيًا:|## \d+\. المشكلة", body):
        score += 8
    # Penalize English-only Fowler catalog dump style
    if arabic_ratio(body) < 0.15:
        score -= 25
    # Penalize Gemini-correction essays that aren't the catalog teaching pass
    if "رد Gemini" in body or "سالت جيمناي" in body:
        score -= 20
    return score


def extract_named_sections(body: str) -> dict[str, str]:
    """Pull key Arabic sections for optional merge from runner-up versions."""
    found: dict[str, str] = {}
    matches = list(re.finditer(r"^##\s+([^\n]+)\s*$", body, re.M))
    for i, m in enumerate(matches):
        title = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[start:end].strip()
        key = None
        if re.search(r"اختبر فهمك", title):
            key = "quiz"
        elif re.search(r"أودو|Odoo", title, re.I):
            key = "odoo"
        elif re.search(r"أقرب GoF|بيشبه إيه في GoF", title, re.I):
            key = "gof"
        if key:
            found[key] = f"## {title}\n\n{content}".strip()
    return found


def merge_missing_sections(winner: PatternBlock, candidates: list[PatternBlock]) -> PatternBlock:
    win_secs = extract_named_sections(winner.body)
    need_quiz = "quiz" not in win_secs and "اختبر فهمك" not in winner.body
    need_odoo = "odoo" not in win_secs and not re.search(r"علاقته بـ(?:ـ)?\s*Odoo|علاقته بأودو", winner.body)
    need_gof = "gof" not in win_secs and not re.search(r"أقرب GoF|بيشبه إيه في GoF", winner.body)
    extras: list[str] = []
    for other in sorted(candidates, key=lambda x: -x.score):
        if other is winner or other.body == winner.body:
            continue
        secs = extract_named_sections(other.body)
        if need_quiz and "quiz" in secs:
            extras.append(secs["quiz"])
            need_quiz = False
        if need_odoo and "odoo" in secs:
            extras.append(secs["odoo"])
            need_odoo = False
        if need_gof and "gof" in secs:
            extras.append(secs["gof"])
            need_gof = False
    if extras:
        body = winner.body.rstrip() + "\n\n" + "\n\n".join(extras) + "\n"
        winner = PatternBlock(
            name=winner.name,
            slug=winner.slug,
            source_file=winner.source_file,
            body=body,
            score=winner.score + 2,
            group_id=winner.group_id,
        )
    return winner


def dedupe_patterns(blocks: Iterable[PatternBlock]) -> dict[str, PatternBlock]:
    by_name: dict[str, list[PatternBlock]] = {}
    for b in blocks:
        by_name.setdefault(b.name.lower(), []).append(b)

    winners: dict[str, PatternBlock] = {}
    for key, cands in by_name.items():
        ordered = sorted(
            cands,
            key=lambda b: (
                b.score,
                1 if re.search(r"Odoo|أودو", b.body, re.I) else 0,
                arabic_ratio(b.body),
                len(b.body),
            ),
            reverse=True,
        )
        # Close-score Odoo preference already baked into sort; still merge gaps
        winner = ordered[0]
        if len(ordered) > 1 and abs(ordered[0].score - ordered[1].score) < 3:
            a, b = ordered[0], ordered[1]
            a_odoo = bool(re.search(r"Odoo|أودو", a.body, re.I))
            b_odoo = bool(re.search(r"Odoo|أودو", b.body, re.I))
            if b_odoo and not a_odoo:
                winner = b
        winner = merge_missing_sections(winner, ordered)
        winners[key] = winner
    return winners


def clean_body(body: str) -> str:
    body = URL_NOISE_RE.sub("", body)
    body = re.sub(r"[ \t]+\n", "\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    # Drop pure user answer dumps that snuck in mid-body (short italic-less lines between ---)
    # Keep GoF sections intact — do not truncate.
    for rx, repl in SECTION_TITLE_MAP:
        body = rx.sub(repl, body)
    # Normalize leftover English section crumbs inside Arabic headings
    body = re.sub(r"（", "(", body)
    body = re.sub(r"\s*\(The Problem\)", "", body)
    body = re.sub(r"\s*\(The Solution\)", "", body)
    # Promote **الخلاصة:** paragraphs
    body = re.sub(r"^\*\*الخلاصة:\*\*\s*", "## الخلاصة\n\n", body, flags=re.M)
    # Capture trailing check questions as quiz if not already
    if "اختبر فهمك" not in body:
        quiz_bits = re.findall(
            r"(\*\*قبل ما ننتقل[^*]+\*\*\s*\n\n[^\n#]+(?:\n[^\n#]+){0,6})",
            body,
        )
        if quiz_bits:
            # leave in place; also ensure heading nearby
            body = re.sub(
                r"\*\*قبل ما ننتقل",
                "## اختبر فهمك\n\n**قبل ما ننتقل",
                body,
                count=1,
            )
    return body.strip()


def ensure_section_order_notes(md: str) -> str:
    """Light touch: ensure H1 exists; don't invent English teaching sections."""
    return md.strip() + "\n"


def md_to_html_fragment(md: str) -> str:
    """Minimal Markdown → HTML for our content subset."""
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_lang = ""
    code_buf: list[str] = []
    in_ul = False
    in_ol = False
    in_table = False
    table_rows: list[list[str]] = []

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def close_table():
        nonlocal in_table, table_rows
        if not in_table:
            return
        out.append('<div class="table-wrap" dir="rtl"><table>')
        for ri, row in enumerate(table_rows):
            tag = "th" if ri == 0 else "td"
            out.append("<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in row) + "</tr>")
        out.append("</table></div>")
        in_table = False
        table_rows = []

    def inline_format(text: str) -> str:
        text = html.escape(text)
        text = re.sub(r"`([^`]+)`", r'<code dir="ltr">\1</code>', text)
        text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
        return text

    while i < len(lines):
        line = lines[i]
        if in_code:
            if line.strip().startswith("```"):
                code = html.escape("\n".join(code_buf))
                out.append(
                    f'<pre class="code" dir="ltr"><code class="language-{html.escape(code_lang)}">{code}</code></pre>'
                )
                in_code = False
                code_buf = []
                code_lang = ""
            else:
                code_buf.append(line)
            i += 1
            continue

        if line.strip().startswith("```"):
            close_lists()
            close_table()
            in_code = True
            code_lang = line.strip()[3:].strip() or "text"
            i += 1
            continue

        # Pipe tables (GFM) and tab-separated tables
        pipe_row = re.match(r"^\|(.+)\|\s*$", line)
        sep_row = re.match(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$", line)
        if sep_row and in_table:
            i += 1
            continue
        if pipe_row and not line.startswith("#"):
            close_lists()
            cols = [c.strip() for c in pipe_row.group(1).split("|")]
            if not in_table:
                in_table = True
                table_rows = []
            table_rows.append([inline_format(c) for c in cols])
            i += 1
            continue
        if "\t" in line and not line.startswith("#"):
            close_lists()
            cols = [c.strip() for c in line.split("\t")]
            if len(cols) >= 2:
                if not in_table:
                    in_table = True
                    table_rows = []
                table_rows.append([inline_format(c) for c in cols])
                i += 1
                continue
        else:
            if in_table and not (pipe_row or ("\t" in line)):
                close_table()

        heading = re.match(r"^(#{1,4})\s+(.*)$", line)
        if heading:
            close_lists()
            level = len(heading.group(1))
            out.append(f"<h{level}>{inline_format(heading.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"^---+\s*$", line):
            close_lists()
            out.append("<hr>")
            i += 1
            continue

        ul = re.match(r"^[-*]\s+(.*)$", line)
        if ul:
            close_table()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline_format(ul.group(1))}</li>")
            i += 1
            continue

        ol = re.match(r"^(\d+)\.\s+(.*)$", line)
        if ol:
            close_table()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline_format(ol.group(2))}</li>")
            i += 1
            continue

        if not line.strip():
            close_lists()
            i += 1
            continue

        close_lists()
        # Plain diagram / preformatted ASCII
        if re.match(r"^[│├└┌┐┘┴┬┼─\|v\^\sA-Za-z0-9_\-\+\.]+$", line) and (
            "|" in line or "→" in line or line.strip() in {"v", "|", "^"}
        ):
            # gather contiguous diagram lines
            diag = [line]
            j = i + 1
            while j < len(lines) and lines[j].strip() and not lines[j].startswith("#") and not lines[j].startswith("```"):
                if re.search(r"[│├└|\tv]|Application|Domain|Infrastructure|Payment|Order", lines[j]):
                    diag.append(lines[j])
                    j += 1
                else:
                    break
            if len(diag) >= 2:
                out.append(
                    '<pre class="diagram" dir="ltr">'
                    + html.escape("\n".join(diag))
                    + "</pre>"
                )
                i = j
                continue

        out.append(f"<p>{inline_format(line)}</p>")
        i += 1

    close_lists()
    close_table()
    if in_code:
        code = html.escape("\n".join(code_buf))
        out.append(f'<pre class="code" dir="ltr"><code>{code}</code></pre>')
    return "\n".join(out)


def page_shell(
    title: str,
    body: str,
    *,
    depth: int = 0,
    extra_head: str = "",
) -> str:
    prefix = "../" * depth if depth else ""
    return f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Tajawal:wght@300;400;500;700&family=Space+Grotesk:wght@400;500;600;700&family=Cairo:wght@300;400;600;700;900&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}assets/css/reference.css">
  {extra_head}
</head>
<body>
  <div class="page-fade">
{body}
  </div>
  <script src="{prefix}assets/js/reference.js"></script>
</body>
</html>
"""


def render_index(catalog: list[dict], generated_groups: set[int]) -> str:
    items = []
    for g in catalog:
        ready = g["id"] in generated_groups
        href = f"groups/{g['id']:02d}-{g['slug']}.html"
        status = "" if ready else '<span class="badge">قريبًا</span>'
        pat_count = len(g["patterns"])
        items.append(
            f"""
        <a class="group-card {'is-ready' if ready else 'is-stub'}" href="{href}" data-group="{g['id']}">
          <span class="group-num">{g['id']:02d}</span>
          <span class="group-titles">
            <span class="group-title-ar">{html.escape(g['title_ar'])}</span>
            <span class="group-title-en" dir="ltr">{html.escape(g['title_en'])}</span>
          </span>
          <span class="group-meta">{pat_count} نمط {status}</span>
        </a>"""
        )

    # Search corpus: all pattern names with links (to group page anchors when ready)
    search_entries = []
    for g in catalog:
        href = f"groups/{g['id']:02d}-{g['slug']}.html"
        for p in g["patterns"]:
            search_entries.append(
                {
                    "name": p,
                    "group": g["title_en"],
                    "href": f"{href}#{slugify(p)}",
                    "ready": g["id"] in generated_groups,
                }
            )
    search_json = html.escape(
        __import__("json").dumps(search_entries, ensure_ascii=False)
    )

    body = f"""
  <header class="site-header hero">
    <p class="eyebrow">Martin Fowler · PoEAA</p>
    <h1 class="brand">مرجع أنماط تطبيقات المؤسسات (POEAA)</h1>
    <p class="subtitle">شرح عربي منظم لأنماط Fowler، مع الإبقاء على أسماء الأنماط والكود بالإنجليزية، وربط عملي بأودو عند وروده في المصدر.</p>
    <div class="search-panel">
      <label for="pattern-search">بحث باسم النمط الإنجليزي</label>
      <input id="pattern-search" type="search" dir="ltr" placeholder="e.g. Unit of Work, Data Mapper, Gateway" autocomplete="off">
      <ul id="search-results" class="search-results" hidden></ul>
    </div>
  </header>
  <main class="index-main">
    <h2 class="section-label">المجموعات</h2>
    <nav class="group-nav" aria-label="مجموعات الأنماط">
      {''.join(items)}
    </nav>
  </main>
  <footer class="site-footer">
    <p>مبني من محادثات الدراسة — المحتوى التعليمي للمساعد فقط، مع إزالة إجابات المستخدم المختصرة.</p>
  </footer>
  <script type="application/json" id="pattern-catalog">{search_json}</script>
"""
    return page_shell("مرجع أنماط تطبيقات المؤسسات (POEAA)", body, depth=0)


def render_group_page(bundle: GroupBundle, generated_groups: set[int]) -> str:
    g = bundle.group
    gid = g["id"]
    prev_g = GROUPS[gid - 2] if gid > 1 else None
    next_g = GROUPS[gid] if gid < len(GROUPS) else None

    def group_href(gg: dict) -> str:
        return f"{gg['id']:02d}-{gg['slug']}.html"

    nav_prev = (
        f'<a href="{group_href(prev_g)}">→ {html.escape(prev_g["title_ar"])}</a>'
        if prev_g
        else "<span></span>"
    )
    nav_next = (
        f'<a href="{group_href(next_g)}">{html.escape(next_g["title_ar"])} ←</a>'
        if next_g and next_g["id"] in generated_groups
        else (
            f'<span class="muted">{html.escape(next_g["title_ar"])} ←</span>'
            if next_g
            else "<span></span>"
        )
    )

    toc = "\n".join(
        f'<li><a href="#{html.escape(p.slug)}"><span dir="ltr">{html.escape(p.name)}</span></a></li>'
        for p in bundle.patterns
    )

    summary_html = md_to_html_fragment(bundle.summary_md) if bundle.summary_md else (
        f"<p>خريطة مجموعة <span dir=\"ltr\">{html.escape(g['title_en'])}</span> "
        f"({html.escape(g['title_ar'])}).</p>"
    )

    sections = []
    for p in bundle.patterns:
        body_html = md_to_html_fragment(p.body)
        sections.append(
            f"""
      <article class="pattern" id="{html.escape(p.slug)}" data-pattern="{html.escape(p.name)}">
        <header class="pattern-header">
          <p class="pattern-kicker">PoEAA · {html.escape(g['title_en'])}</p>
          <h2 class="pattern-title" dir="ltr">{html.escape(p.name)}</h2>
        </header>
        <div class="pattern-body">
{body_html}
        </div>
      </article>"""
        )

    body = f"""
  <header class="group-topbar">
    <a class="home-link" href="../index.html">المرجع</a>
    <div class="group-switch">{nav_prev}{nav_next}</div>
  </header>
  <header class="group-hero">
    <p class="eyebrow">المجموعة {gid:02d}</p>
    <h1>{html.escape(g['title_ar'])}</h1>
    <p class="subtitle" dir="ltr">{html.escape(g['title_en'])}</p>
  </header>
  <div class="group-layout">
    <aside class="toc-wrap">
      <nav class="toc" aria-label="محتويات الأنماط">
        <p class="toc-title">الأنماط</p>
        <ol>{toc}</ol>
      </nav>
    </aside>
    <main class="group-main">
      <section class="group-map" id="group-map">
        <h2>خريطة المجموعة</h2>
        {summary_html}
      </section>
      {''.join(sections)}
    </main>
  </div>
  <footer class="site-footer group-footer">
    <div class="group-switch">{nav_prev}<a href="../index.html">الفهرس</a>{nav_next}</div>
  </footer>
"""
    return page_shell(
        f"{g['title_ar']} · POEAA",
        body,
        depth=1,
    )


def render_stub_group(group: dict) -> str:
    items = "".join(
        f'<li><span dir="ltr">{html.escape(p)}</span></li>' for p in group["patterns"]
    )
    body = f"""
  <header class="group-topbar">
    <a class="home-link" href="../index.html">المرجع</a>
  </header>
  <header class="group-hero">
    <p class="eyebrow">المجموعة {group['id']:02d}</p>
    <h1>{html.escape(group['title_ar'])}</h1>
    <p class="subtitle" dir="ltr">{html.escape(group['title_en'])}</p>
  </header>
  <main class="group-main narrow">
    <p class="stub-note">هذه المجموعة لم تُولَّد بالكامل بعد. القائمة المتوقعة:</p>
    <ol class="stub-list">{items}</ol>
    <p><a href="../index.html">العودة إلى الفهرس</a></p>
  </main>
"""
    return page_shell(f"{group['title_ar']} · POEAA", body, depth=1)


def write_assets() -> None:
    css = r"""
:root {
  /* Reference palette (enterprise-patterns-guide / roadmap.css) */
  --bg: #0d0f14;
  --bg2: #13161e;
  --bg3: #1a1e28;
  --bg4: #222736;
  --border: #2a2f3e;
  --border2: #353b50;
  --text: #e8eaf0;
  --text2: #9aa0b8;
  --text3: #5a6080;
  --purple: #7c6af7;
  --purple2: #a89cf8;
  --teal: #2dd4a0;
  --teal2: #6ee9c4;
  --amber: #f5a623;
  --amber2: #fcc96b;
  --coral: #f06a50;
  --coral2: #f7987f;
  --blue: #4a9eff;
  --blue2: #82beff;
  --indigo: #7c9cff;
  --indigo2: #a8b8ff;
  --green: #5ec76a;
  --green2: #8ad192;
  --pink: #e879a0;
  --pink2: #f2a8c5;
  --radius: 10px;

  /* Site tokens mapped onto the reference palette */
  --ink: var(--text);
  --ink-soft: var(--text2);
  --paper: var(--bg);
  --paper-deep: var(--bg3);
  --accent: var(--purple);
  --accent-deep: var(--purple2);
  --line: var(--border);
  --code-bg: #0a0c11;
  --code-ink: #abb2bf;
  --shadow: 0 18px 50px rgba(0, 0, 0, 0.35);
  --toc-width: 15rem;
  --max: 72rem;
  --font-body: "Tajawal", "Cairo", sans-serif;
  --font-display: "Space Grotesk", "Cairo", "Tajawal", sans-serif;
  --font-mono: "IBM Plex Mono", "Fira Code", ui-monospace, monospace;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: var(--font-body);
  color: var(--ink);
  background:
    radial-gradient(ellipse 600px 300px at 20% 0%, rgba(124, 106, 247, 0.08), transparent 70%),
    radial-gradient(ellipse 500px 250px at 80% 10%, rgba(45, 212, 160, 0.06), transparent 70%),
    linear-gradient(180deg, #0d0f14 0%, #12162a 45%, #0d1520 100%);
  min-height: 100vh;
  line-height: 1.85;
  font-size: 1.05rem;
}

.page-fade {
  animation: fadeIn 520ms ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}

a { color: var(--accent-deep); text-decoration-thickness: 1px; text-underline-offset: 0.2em; }
a:hover { color: var(--teal2); }

.site-header.hero, .group-hero {
  max-width: var(--max);
  margin: 0 auto;
  padding: 3.5rem 1.5rem 1.5rem;
}
.brand, .group-hero h1 {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: clamp(2rem, 4vw, 3.2rem);
  line-height: 1.25;
  margin: 0.4rem 0 0.8rem;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #e8eaf0 0%, var(--purple2) 50%, var(--teal2) 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
}
.eyebrow {
  margin: 0;
  color: var(--accent-deep);
  font-family: var(--font-display);
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 0.85rem;
}
.subtitle { max-width: 42rem; color: var(--ink-soft); margin: 0; }

.search-panel {
  margin-top: 2rem;
  max-width: 36rem;
  display: grid;
  gap: 0.5rem;
}
.search-panel label { font-weight: 600; color: var(--text2); }
.search-panel input {
  font: inherit;
  padding: 0.85rem 1rem;
  border: 1px solid var(--line);
  background: var(--bg3);
  color: var(--ink);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.search-panel input:focus {
  outline: none;
  border-color: var(--purple);
  box-shadow: 0 0 0 3px rgba(124, 106, 247, 0.2);
}
.search-results {
  list-style: none;
  margin: 0;
  padding: 0.4rem;
  background: var(--bg2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
}
.search-results li a {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.55rem 0.7rem;
  text-decoration: none;
  color: var(--ink);
  border-radius: 0.3rem;
}
.search-results li a:hover { background: var(--bg3); }
.search-results .meta { color: var(--text3); font-size: 0.85rem; }

.index-main, .group-main.narrow {
  max-width: var(--max);
  margin: 0 auto;
  padding: 1rem 1.5rem 4rem;
}
.section-label {
  font-family: var(--font-display);
  font-size: 1.4rem;
  margin-bottom: 1rem;
  color: var(--ink);
}
.group-nav {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 0.9rem;
}
.group-card {
  display: grid;
  grid-template-columns: auto 1fr;
  grid-template-rows: auto auto;
  gap: 0.15rem 0.9rem;
  padding: 1.1rem 1.15rem;
  background: var(--bg2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  text-decoration: none;
  color: inherit;
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease;
}
.group-card:hover {
  transform: translateY(-2px);
  border-color: rgba(124, 106, 247, 0.35);
  box-shadow: var(--shadow);
}
.group-card.is-stub { opacity: 0.72; }
.group-num {
  grid-row: span 2;
  font-family: var(--font-display);
  font-size: 1.6rem;
  color: var(--accent-deep);
  align-self: center;
}
.group-title-ar { font-weight: 700; display: block; }
.group-title-en { color: var(--ink-soft); font-size: 0.92rem; display: block; }
.group-meta { grid-column: 2; color: var(--ink-soft); font-size: 0.86rem; }
.badge {
  display: inline-block;
  margin-inline-start: 0.35rem;
  padding: 0.05rem 0.4rem;
  border: 1px solid var(--line);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: var(--text3);
}

.site-footer {
  max-width: var(--max);
  margin: 0 auto;
  padding: 1rem 1.5rem 3rem;
  color: var(--ink-soft);
  font-size: 0.92rem;
  border-top: 1px solid var(--line);
}

.group-topbar {
  max-width: var(--max);
  margin: 0 auto;
  padding: 1rem 1.5rem 0;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
}
.group-switch {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  align-items: center;
}
.muted { color: var(--ink-soft); }

.group-layout {
  max-width: var(--max);
  margin: 0 auto;
  padding: 0 1.5rem 3rem;
  display: grid;
  grid-template-columns: var(--toc-width) minmax(0, 1fr);
  gap: 2rem;
  align-items: start;
}
.toc-wrap { position: sticky; top: 1rem; }
.toc {
  background: var(--bg2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 0.9rem 1rem;
  max-height: calc(100vh - 2rem);
  overflow: auto;
}
.toc-title { margin: 0 0 0.5rem; font-weight: 700; color: var(--purple2); font-family: var(--font-display); }
.toc ol { margin: 0; padding: 0 1rem 0 0; }
.toc a {
  display: block;
  padding: 0.25rem 0;
  color: var(--ink-soft);
  text-decoration: none;
  border-inline-start: 2px solid transparent;
  padding-inline-start: 0.45rem;
}
.toc a:hover { color: var(--ink); background: rgba(255, 255, 255, 0.03); }
.toc a.active {
  color: var(--accent-deep);
  border-inline-start-color: var(--accent);
  background: rgba(124, 106, 247, 0.08);
  font-weight: 600;
}

.group-map, .pattern {
  background: var(--bg2);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 1.4rem 1.35rem 1.6rem;
  margin-bottom: 1.25rem;
}
.pattern-kicker {
  margin: 0;
  color: var(--accent-deep);
  font-size: 0.86rem;
  font-weight: 600;
  font-family: var(--font-display);
}
.pattern-title {
  margin: 0.2rem 0 1rem;
  font-family: var(--font-display);
  font-size: clamp(1.6rem, 2.5vw, 2.1rem);
  color: var(--ink);
}
.pattern-body h2, .group-map h2 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  margin-top: 1.6rem;
  color: var(--ink);
}
.pattern-body h3 { font-size: 1.05rem; margin-top: 1.2rem; color: var(--text2); }
.pattern-body p { margin: 0.7rem 0; }
.pattern-body ul, .pattern-body ol { margin: 0.5rem 0 0.8rem; padding-inline-start: 1.3rem; }

pre.code, pre.diagram {
  background: var(--code-bg);
  color: var(--code-ink);
  padding: 1rem 1.1rem;
  border-radius: var(--radius);
  overflow: auto;
  direction: ltr;
  text-align: left;
  font-family: var(--font-mono);
  font-size: 0.92rem;
  line-height: 1.55;
  border: 1px solid var(--border);
  box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
}
code {
  font-family: var(--font-mono);
  font-size: 0.92em;
}
p code, li code, td code, th code {
  background: var(--bg4);
  color: var(--teal2);
  padding: 0.05em 0.35em;
  border-radius: 0.25rem;
}
.table-wrap { overflow: auto; margin: 0.8rem 0 1rem; }
table {
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
  background: var(--bg3);
}
th, td {
  border: 1px solid var(--line);
  padding: 0.45rem 0.7rem;
  vertical-align: top;
}
th { background: var(--bg4); font-weight: 600; color: var(--text2); }
hr {
  border: 0;
  border-top: 1px solid var(--line);
  margin: 1.4rem 0;
}
.stub-note { color: var(--ink-soft); }
.stub-list { line-height: 2; }

@media (max-width: 920px) {
  .group-layout { grid-template-columns: 1fr; }
  .toc-wrap { position: relative; top: 0; }
  .toc { max-height: none; }
}
"""
    js = r"""
(function () {
  const catalogEl = document.getElementById("pattern-catalog");
  const input = document.getElementById("pattern-search");
  const results = document.getElementById("search-results");

  if (catalogEl && input && results) {
    let catalog = [];
    try { catalog = JSON.parse(catalogEl.textContent || "[]"); } catch (e) { catalog = []; }

    function render(items) {
      if (!items.length) {
        results.hidden = true;
        results.innerHTML = "";
        return;
      }
      results.hidden = false;
      results.innerHTML = items.slice(0, 12).map((item) => {
        const ready = item.ready ? "" : " · قريبًا";
        return `<li><a href="${item.href}"><span dir="ltr">${item.name}</span><span class="meta" dir="ltr">${item.group}${ready}</span></a></li>`;
      }).join("");
    }

    input.addEventListener("input", () => {
      const q = input.value.trim().toLowerCase();
      if (!q) { render([]); return; }
      const hits = catalog.filter((p) => p.name.toLowerCase().includes(q));
      render(hits);
    });

    input.addEventListener("keydown", (ev) => {
      if (ev.key === "Enter") {
        const first = results.querySelector("a");
        if (first) first.click();
      }
    });
  }

  // TOC active section highlighting
  const tocLinks = Array.from(document.querySelectorAll(".toc a"));
  const patterns = tocLinks
    .map((a) => document.querySelector(a.getAttribute("href")))
    .filter(Boolean);

  if (tocLinks.length && patterns.length && "IntersectionObserver" in window) {
    const map = new Map();
    tocLinks.forEach((a) => map.set(a.getAttribute("href"), a));
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const id = "#" + entry.target.id;
        tocLinks.forEach((a) => a.classList.remove("active"));
        const link = map.get(id);
        if (link) link.classList.add("active");
      });
    }, { rootMargin: "-20% 0px -60% 0px", threshold: 0.1 });
    patterns.forEach((sec) => obs.observe(sec));
  }
})();
"""
    ASSETS_CSS.mkdir(parents=True, exist_ok=True)
    ASSETS_JS.mkdir(parents=True, exist_ok=True)
    (ASSETS_CSS / "reference.css").write_text(css.strip() + "\n", encoding="utf-8")
    (ASSETS_JS / "reference.js").write_text(js.strip() + "\n", encoding="utf-8")


def collect_from_sources() -> tuple[dict[str, PatternBlock], dict[int, str]]:
    all_blocks: list[PatternBlock] = []
    summaries: dict[int, str] = {}

    files = sorted(SOURCE_RAW.glob("chat_*.md"))
    for path in files:
        text = path.read_text(encoding="utf-8")
        # Prefer keeping assistant-heavy material: drop obvious short user turns
        # but pattern extraction is heading-based so we still scan full text.
        blocks = extract_pattern_blocks_from_text(text, path.name)
        all_blocks.extend(blocks)
        for gid, summary in extract_group_summaries(text, path.name):
            if gid is None:
                continue
            # keep richer Arabic summary
            prev = summaries.get(gid, "")
            if arabic_ratio(summary) >= arabic_ratio(prev) and len(summary) >= len(prev):
                summaries[gid] = summary

    winners = dedupe_patterns(all_blocks)

    # Inject authored gaps if missing or too thin
    for name, fill in GAP_FILLINS.items():
        key = name.lower()
        existing = winners.get(key)
        if existing is None or len(existing.body) < 600 or arabic_ratio(existing.body) < 0.25:
            winners[key] = PatternBlock(
                name=name,
                slug=slugify(name),
                source_file="authored_gap_fillin",
                body=fill.strip(),
                score=100,
                group_id=PATTERN_TO_GROUP[key],
            )

    # Clean bodies
    for b in winners.values():
        b.body = clean_body(b.body)

    return winners, summaries


def build_default_base_summary() -> str:
    return """## مراجعة الأنماط الأساسية

خريطة سريعة لـ Base Patterns في PoEAA:

| النمط | المشكلة الأساسية | أقرب GoF للمقارنة |
|---|---|---|
| Gateway | الوصول لنظام خارجي | Facade / Adapter |
| Service Stub | استبدال Service حقيقية ببديل | Proxy |
| Record Set | تمثيل بيانات جدولية في الذاكرة | Adapter (تشابه عملي فقط) |
| Mapper | تنظيم التواصل بين تمثيلين مستقلين | Adapter / Mediator |
| Layer Supertype | مشاركة سلوك داخل Layer | Template Method |
| Separated Interface | فصل العقد عن التنفيذ واتجاه الاعتماديات | Bridge |
| Registry | الوصول إلى Objects مسجلة | Singleton |
| Value Object | تمثيل قيمة بدون Identity | Flyweight |
| Money | تمثيل المبالغ والعملات | — (تخصص Value Object) |
| Special Case | تمثيل حالة خاصة بسلوك محدد | Null Object |
| Plugin | توسيع النظام بإضافات | Strategy / Abstract Factory |

**ملاحظة:** الجدول للمقارنة التعليمية، وليس لإعلان تكافؤ الأنماط.
"""


def convert_tab_tables(md: str) -> str:
    """Convert simple tab-separated blocks into Markdown pipe tables."""
    lines = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if "\t" in lines[i] and not lines[i].startswith("#"):
            block = []
            while i < len(lines) and "\t" in lines[i]:
                block.append([c.strip() for c in lines[i].split("\t")])
                i += 1
            if block:
                width = max(len(r) for r in block)
                norm = [r + [""] * (width - len(r)) for r in block]
                out.append("| " + " | ".join(norm[0]) + " |")
                out.append("| " + " | ".join("---" for _ in range(width)) + " |")
                for r in norm[1:]:
                    out.append("| " + " | ".join(r) + " |")
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def build(pilot: bool = False) -> None:
    write_assets()
    winners, summaries = collect_from_sources()

    CONTENT.mkdir(parents=True, exist_ok=True)
    GROUPS_DIR.mkdir(parents=True, exist_ok=True)

    generated: set[int] = set()
    target_groups = [GROUPS[0]] if pilot else GROUPS

    # Always emit index listing all groups; stub missing ones when pilot
    for g in GROUPS:
        if pilot and g["id"] != 1:
            stub_path = GROUPS_DIR / f"{g['id']:02d}-{g['slug']}.html"
            stub_path.write_text(render_stub_group(g), encoding="utf-8")
            continue

        patterns: list[PatternBlock] = []
        missing: list[str] = []
        for pname in g["patterns"]:
            block = winners.get(pname.lower())
            if block is None:
                missing.append(pname)
                continue
            patterns.append(block)

        summary = summaries.get(g["id"], "")
        if g["id"] == 1:
            # Prefer chat summary; ensure Record Set appears in map
            if not summary:
                summary = build_default_base_summary()
            else:
                summary = clean_body(summary)
                summary = convert_tab_tables(summary)
                summary = re.sub(r"^#\s+", "## ", summary, count=1, flags=re.M)
                if "Record Set" not in summary:
                    row = "| Record Set | تمثيل بيانات جدولية في الذاكرة | Adapter (تشابه عملي فقط) |"
                    # Insert after Plugin row if present, else after header separator
                    if re.search(r"^\| Plugin \|.*\|$", summary, re.M):
                        summary = re.sub(
                            r"(^\| Plugin \|.*\|$)",
                            r"\1\n" + row,
                            summary,
                            count=1,
                            flags=re.M,
                        )
                    elif re.search(r"^\| ---", summary, re.M):
                        summary = re.sub(
                            r"(^\| ---.*\|$)",
                            r"\1\n" + row,
                            summary,
                            count=1,
                            flags=re.M,
                        )
                    else:
                        summary += (
                            "\n\n**Record Set:** تمثيل بيانات جدولية داخل الذاكرة؛ "
                            "أقرب تشبيه GoF عملي هو Adapter دون تكافؤ في الـ Intent.\n"
                        )
        else:
            if summary:
                summary = convert_tab_tables(clean_body(summary))
                summary = re.sub(r"^#\s+", "## ", summary, count=1, flags=re.M)

        bundle = GroupBundle(group=g, summary_md=summary, patterns=patterns)

        # Markdown intermediates
        md_parts = [f"# {g['title_ar']} ({g['title_en']})\n", summary, "\n"]
        for p in patterns:
            md_parts.append(f"\n# {p.name}\n\n{p.body}\n")
        md_path = CONTENT / f"{g['id']:02d}-{g['slug']}.md"
        md_path.write_text("\n".join(md_parts), encoding="utf-8")

        html_path = GROUPS_DIR / f"{g['id']:02d}-{g['slug']}.html"
        html_path.write_text(render_group_page(bundle, {g["id"]} | generated), encoding="utf-8")
        generated.add(g["id"])

        print(f"[group {g['id']:02d}] wrote {html_path.relative_to(ROOT)} — {len(patterns)} patterns")
        if missing:
            print(f"  MISSING: {', '.join(missing)}")
        for p in patterns:
            flags = []
            if re.search(r"GoF|Facade|Adapter|Proxy|Strategy|Bridge|Null Object", p.body, re.I):
                flags.append("GoF")
            if re.search(r"Odoo|أودو", p.body, re.I):
                flags.append("Odoo")
            if re.search(r"اختبر فهمك", p.body):
                flags.append("quiz")
            print(f"  - {p.name} (score={p.score:.1f}, src={p.source_file}, {','.join(flags) or 'core'})")

    # Re-render group pages with full generated set for nav correctness
    if not pilot:
        winners2, summaries2 = winners, summaries
        for gid in sorted(generated):
            g = GROUPS[gid - 1]
            patterns = [winners2[p.lower()] for p in g["patterns"] if p.lower() in winners2]
            summary = summaries2.get(gid, "")
            if gid == 1:
                if not summary:
                    summary = build_default_base_summary()
                else:
                    summary = convert_tab_tables(clean_body(summary))
                    summary = re.sub(r"^#\s+", "## ", summary, count=1, flags=re.M)
                    if "Record Set" not in summary:
                        row = "| Record Set | تمثيل بيانات جدولية في الذاكرة | Adapter (تشابه عملي فقط) |"
                        if re.search(r"^\| Plugin \|.*\|$", summary, re.M):
                            summary = re.sub(
                                r"(^\| Plugin \|.*\|$)",
                                r"\1\n" + row,
                                summary,
                                count=1,
                                flags=re.M,
                            )
                        else:
                            summary += (
                                "\n\n**Record Set:** تمثيل بيانات جدولية داخل الذاكرة؛ "
                                "أقرب تشبيه GoF عملي هو Adapter دون تكافؤ في الـ Intent.\n"
                            )
            elif summary:
                summary = convert_tab_tables(clean_body(summary))
                summary = re.sub(r"^#\s+", "## ", summary, count=1, flags=re.M)
            bundle = GroupBundle(group=g, summary_md=summary, patterns=patterns)
            html_path = GROUPS_DIR / f"{g['id']:02d}-{g['slug']}.html"
            html_path.write_text(render_group_page(bundle, generated), encoding="utf-8")

    index_path = DOCS / "index.html"
    # In pilot, only group 1 is "ready" for search deep links quality; stubs still linked
    index_path.write_text(render_index(GROUPS, generated), encoding="utf-8")
    print(f"wrote {index_path.relative_to(ROOT)}")
    print(f"generated groups: {sorted(generated)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build POEAA Arabic RTL reference")
    parser.add_argument("--pilot", action="store_true", help="Build Base Patterns only")
    parser.add_argument("--all", action="store_true", help="Build all groups")
    args = parser.parse_args()
    pilot = args.pilot or not args.all
    # Default to pilot unless --all
    if args.all:
        pilot = False
    if not args.pilot and not args.all:
        pilot = True
    build(pilot=pilot)


if __name__ == "__main__":
    main()
