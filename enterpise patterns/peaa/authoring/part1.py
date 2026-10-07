"""Part 1 narrative chapters and the guide introduction."""

from peaa.authoring.model import Section

STORY = "peaa/lab/lease_app/story.py"


def sections() -> list[Section]:
    return [
        Section(
            id="intro",
            nav="كيف تذاكر الدليل",
            group="المقدمة",
            title="How to use this guide",
            subtitle="خريطة للكتاب، مش نسخة من فصوله",
            icon="📘",
            tone="purple",
            intent="الدليل يرتّب أفكار أنماط تطبيقات المؤسسات على قصة واحدة: نظام تأجير أصول بعد توقيع العقد (فوترة، ترقية أصل، إرجاع مبكر). الشرح مكتوب من جديد بالعربي مع المصطلح الإنجليزي. أسماء الأنماط وترتيبها يتبعان فهرس الكتاب، والنص ليس نقلًا للفصول.",
            notes=[
                "الجزء ١ سرد معماري. الجزء ٢ مرجع الأنماط. الجزء ٣ إضافة دراسية عن خيوط ومهام داخل العملية، وهو مختلف عن أقفال الجلسات في الفصلين ٥ و١٦.",
            ],
            use=[
                "لما تبني نظام أعمال فيه شاشات، قواعد، وقاعدة علائقية.",
                "لما تبيّن الفرق بين نمط وآخر على نفس عقد الإيجار بدل أمثلة متفرقة.",
            ],
            avoid=[
                "لو بتدور على نقل حرفي للكتاب أو كود إنتاج جاهز.",
                "لو المشكلة نظام مضمّن أو تحكم صناعي؛ الكتاب أصلًا مش موجّه لكده.",
            ],
            diagram="""
Part 1  narratives     layering → domain → database → web → sessions
Part 2  pattern catalog   51 named patterns, same lease story
Part 3  threads/tasks     pools, locks, reactor, rate limit, bulkhead
            """,
            relations=[
                ("Layering", "ch01-layering"),
                ("Domain Model", "pattern-domain-model"),
                ("Offline vs threads", "part3-concurrency"),
                ("14-week plan", "roadmap"),
            ],
            lab=STORY,
            demo="together",
            snippet="""
# from the enterpise patterns directory
# python -m peaa.lab.run_demo together
from peaa.lab.lease_app.db import fresh
from peaa.lab.patterns.domain_logic import BillingService

total = BillingService(fresh()).bill(1)
print(total)  # USD 900.00
            """,
            tasks=[
                "شغّل python -m peaa.lab.run_demo --list من مجلد enterpise patterns واختر معملًا واحدًا من الجزء ١ ومعملًا من الجزء ٣.",
                "ارسم على ورقة الثلاث طبقات لعقد الإيجار: مين يحسب القسط، ومين يكتب SQL، ومين يعرض الناتج.",
                "اكتب فرقًا بجملة بين قفل مستخدمين على نفس الصف، وقفل خيطين داخل العملية.",
            ],
            questions=[
                ("إيه اللي الدليل مش بيحاول يعمله؟", "مش بيعيد طباعة الكتاب ولا يقدّم تطبيق إنتاج. بيشرح الأنماط بشرحك أنت وتجربة بايثون قصيرة."),
                ("ليه نفس نطاق التأجير في كل المعامل؟", "عشان المقارنة تبقى عادلة: Transaction Script و Domain Model و Data Mapper يشتغلوا على نفس العقد ونفس 900 دولار."),
                ("Part 3 موجود في الكتاب؟", "لا. أضيف كخريطة لتزامن الخيوط والمهام، منفصل عن Offline Concurrency."),
                ("امتى تقرأ الجزء ١ ومتى تغطس في الجزء ٢؟", "اقرأ السرد بالترتيب عشان الصورة، وبعدين ارجع لنمط الجزء ٢ لما تحتاجه في التصميم."),
                ("إيه أمر تشغيل معمل واحد؟", "من مجلد الدليل: python -m peaa.lab.run_demo ثم اسم المعمل، مثل domain_model."),
            ],
        ),
        Section(
            id="ch01-layering",
            nav="Ch.1 Layering",
            group="الجزء ١ · السرد",
            title="Layering",
            subtitle="ثلاث طبقات: عرض، نطاق، مصدر بيانات",
            icon="🏛️",
            tone="teal",
            intent="Layering بيفصل واجهة المستخدم عن قواعد الإيجار وعن طريقة الحفظ. التغيير في شكل الشاشة ما يغيّرش حساب القسط، وتبديل SQLite ببوابة تانية ما يعيدش كتابة القواعد.",
            use=[
                "أي نظام مؤسسي له واجهة وقاعدة وقواعد عمل.",
                "لما الفريق هيتقسم: ناس على الشاشات وناس على الدومين وناس على البيانات.",
            ],
            avoid=[
                "سكربت تقرير لمرة واحدة من غير ما الطبقات تديك فايدة.",
                "حط منطق القسط في القالب أو في زرار الواجهة.",
            ],
            diagram="""
Presentation     CLI / page        "اعرض الفاتورة"
      |  calls
Domain           Lease.monthly_total()
      |  asks
Data Source      SQL / gateway / mapper
            """,
            relations=[
                ("Organizing Domain Logic", "ch02-domain-logic"),
                ("Service Layer", "pattern-service-layer"),
                ("Data Mapper", "pattern-data-mapper"),
            ],
            lab=STORY,
            demo="layering",
            snippet="""
# Presentation stays thin: it asks the service and prints.
total = BillingService(conn).bill(1)
print("presentation shows", total)
            """,
            tasks=[
                "في story.py حدّد السطر اللي يمثل كل طبقة في demo layering.",
                "انقل حساب القسط من SQL داخل Transaction Script إلى دالة على كائن Lease وقارن الناتج.",
                "اكتب سيناريو: تغيّر العملة في الواجهة بس. أي طبقة تتغير وأي طبقة تفضل؟",
            ],
            questions=[
                ("إيه الطبقات الثلاث الأساسية؟", "Presentation للعرض والإدخال، Domain لقواعد العمل، Data Source للقراءة والكتابة."),
                ("ليه منحبش SQL جوه قالب الصفحة؟", "عشان شكل الشاشة وقواعد الإيجار وديمومة البيانات تتغير لأسباب مختلفة."),
                ("فين تعيش طبقة الدومين؟", "غالبًا على السيرفر مع مصدر البيانات. العرض ممكن يكون متصفح أو عميل بعيد."),
                ("إيه علامة إن الطبقات اختلطت؟", "الواجهة بتعرف أسماء الأعمدة، أو كائن الدومين بيعمل commit بنفسه من غير حدود واضحة."),
                ("إيه علاقة الفصل ده بـ Service Layer؟", "الخدمة بتنسّق حالة استخدام وتستدعي الدومين، والواجهة ما تدخلش على الجداول."),
            ],
        ),
        Section(
            id="ch02-domain-logic",
            nav="Ch.2 Domain logic",
            group="الجزء ١ · السرد",
            title="Organizing Domain Logic",
            subtitle="فين تحط حساب القسط: إجراء، كائنات، أم جدول",
            icon="🧠",
            tone="purple",
            intent="منطق النطاق هو قواعد العمل: القسط، الإرجاع المبكر، الترقية. تقدر تحطه في إجراءات (Transaction Script)، أو في كائنات غنية (Domain Model)، أو في كلاس يشتغل على مجموعة صفوف (Table Module). Service Layer ينسّق فوق أي اختيار.",
            use=[
                "لما قواعد الإيجار هتكبر أو تتفرع حسب نوع العقد.",
                "لما عايز نفس القاعدة تتنفّذ من شاشة ومن مهمة ليلية.",
            ],
            avoid=[
                "اختيار Domain Model لعقد فيه ثلاث حقول ومن غير قواعد.",
                "تكرار نفس شرط الإرجاع المبكر في كل شاشة.",
            ],
            diagram="""
simple rules     Transaction Script  (function + SQL)
rich rules       Domain Model        (Lease, Asset, Line)
record screens   Table Module        (one class, many rows)
coordination     Service Layer       (bill, return, upgrade)
            """,
            relations=[
                ("Transaction Script", "pattern-transaction-script"),
                ("Domain Model", "pattern-domain-model"),
                ("Table Module", "pattern-table-module"),
                ("Service Layer", "pattern-service-layer"),
            ],
            lab=STORY,
            demo="organizing_domain",
            snippet="""
model_total = load_domain_lease(conn, 1).monthly_total()
table_total = LeaseTable(rows).monthly_total()
# same lease, same USD 900.00
            """,
            tasks=[
                "شغّل organizing_domain وتأكد إن النموذجين يطلعوا نفس المبلغ.",
                "أضف قاعدة: خصم 10٪ لو الكمية أكبر من 1. نفّذها مرة في سكربت ومرة على LeaseLine.",
                "اكتب متى تختار Table Module لشاشة بنود العقد.",
            ],
            questions=[
                ("إيه الفرق بين Transaction Script و Domain Model؟", "الأول إجراء لكل حالة استخدام والمنطق في الدوال. التاني كائنات تحمل السلوك والعلاقات."),
                ("إيه Table Module؟", "كلاس واحد يخدم كل صفوف جدول أو نتيجة، مناسب لبيئات بتشتغل على مجموعات سجلات."),
                ("Service Layer بيغني عن الدومين؟", "لا. بينسّق التطبيق (معاملة، صلاحيات، ترتيب الخطوات) ويستدعي الدومين أو السكربت."),
                ("إمتى السكربت أنضف من النموذج؟", "لما الحالة استخدام بسيطة والمنطق قليل ومباشر على الجداول."),
                ("ليه المعمل بيطبع المبلغ مرتين؟", "عشان تثبت إن اختيار التنظيم ما يغيّرش نتيجة عقد نورة: 500 + 200×2 = 900 دولار."),
            ],
        ),
        Section(
            id="ch03-orm",
            nav="Ch.3 Mapping",
            group="الجزء ١ · السرد",
            title="Mapping to Relational Databases",
            subtitle="من كائنات الإيجار إلى جداول علائقية",
            icon="🗄️",
            tone="blue",
            intent="الذاكرة كائنات مترابطة، وقاعدة البيانات جداول وصفوف. الربط محتاج قرارات: مين يكتب SQL (بوابة، Active Record، أم Mapper)، وإزاي تحمل العلاقات، وإزاي تربط الوراثة، وإزاي تعيد استخدام وصف الحقول.",
            use=[
                "لما الدومين كائنات وقاعدة البيانات علائقية.",
                "لما عايز تفهم إيه اللي أداة الـ ORM بتعمله تحت الغطا.",
            ],
            avoid=[
                "بناء إطار mapping كامل قبل ما الحالة البسيطة تستقر.",
                "خلط هوية الصف بهوية الكائن من غير Identity Field واضح.",
            ],
            diagram="""
behavioral   Unit of Work · Identity Map · Lazy Load
structural   keys, associations, embedded Money, inheritance tables
metadata     field maps · Query Object · Repository
            """,
            relations=[
                ("Data Mapper", "pattern-data-mapper"),
                ("Unit of Work", "pattern-unit-of-work"),
                ("Repository", "pattern-repository"),
                ("Identity Field", "pattern-identity-field"),
            ],
            lab=STORY,
            demo="mapping_preview",
            snippet="""
lease = LeaseMapper(conn).find(1)
print(lease.can_bill())  # domain method, no SQL on Lease
            """,
            tasks=[
                "ارسم جداول customers و leases و lease_lines والأسهم بينهم.",
                "حمّل نفس العقد مرتين ولاحظ متى تحتاج Identity Map.",
                "اكتب فرق جملة بين Active Record و Data Mapper على Lease.",
            ],
            questions=[
                ("إيه المشكلة السلوكية في الربط؟", "متى تحمّل، متى تحفظ التغييرات، وإزاي ما تعملش نسختين لنفس الصف."),
                ("إيه المشكلة الهيكلية؟", "المفاتيح، العلاقات، القيم المركبة زي Money، ووراثة الأنواع زي شاحنة ورافعة."),
                ("الميتاداتا بتفيدك إمتى؟", "لما وصف الأعمدة يتكرر أو عايز Query Object يتكوّن وقت التشغيل."),
                ("ليه الاتصال بقاعدة البيانات قرار معماري؟", "لأن فتح الاتصال وإدارته جزء من مصدر البيانات مش من قاعدة القسط."),
                ("Data Mapper بيخلّي الدومين يعرف SQL؟", "لا. المابر يترجم بين الكائن والصف، والكائن يفضل قواعد عمل."),
            ],
        ),
        Section(
            id="ch04-web",
            nav="Ch.4 Web",
            group="الجزء ١ · السرد",
            title="Web Presentation",
            subtitle="إزاي الطلب يوصل للنموذج ويرجع عرض",
            icon="🌐",
            tone="amber",
            intent="عرض الويب بيفصل النموذج عن طريقة الرسم وعن اللي يستقبل الطلب. MVC هو التقسيم الكبير. بعد كده تختار: كنترولر لكل صفحة أو كنترولر أمامي واحد، وعرض قالب أو تحويل، ومسار خطوات لو العملية معالج.",
            use=[
                "تطبيق ويب يعرض عقد الإيجار ويستقبل أمر الفوترة.",
                "لما نفس النموذج هيتقدم كنص وHTML أو JSON.",
            ],
            avoid=[
                "حشر حساب القسط داخل القالب.",
                "كنترولر أمامي معقّد لصفحة واحدة ثابتة.",
            ],
            diagram="""
request → controller → model (Lease)
                ↓
              view (template or transform)
            """,
            relations=[
                ("MVC", "pattern-mvc"),
                ("Front Controller", "pattern-front-controller"),
                ("Template View", "pattern-template-view"),
                ("Application Controller", "pattern-application-controller"),
            ],
            lab=STORY,
            demo="web_preview",
            snippet="""
def view(lease):
    return f"Lease #{lease['id']} is {lease['status']}"
            """,
            tasks=[
                "ارسم طلب GET /lease/1 من الكنترولر للنموذج ثم النص.",
                "حوّل نفس النموذج إلى JSON من غير ما تغيّر Lease.",
                "اكتب خطوات معالج إرجاع الأصل: اختيار، تأكيد، إنهاء.",
            ],
            questions=[
                ("MVC بيفصل إيه؟", "Model الحالة والقواعد، View العرض، Controller يستقبل الإدخال ويختار العرض."),
                ("Page Controller مقابل Front Controller؟", "الأول دالة أو كائن لكل صفحة. التاني نقطة دخول توجّه للـ handlers."),
                ("Template View بيعمل إيه؟", "يدمج بيانات النموذج في قالب جاهز."),
                ("Transform View؟", "يحوّل النموذج إلى مستند (JSON أو XML) من غير قالب HTML."),
                ("ليه العرض ما يحمّلش من الجداول بنفسه؟", "عشان تقدر تغيّر الواجهة أو تعيد استخدام النموذج من واجهة بعيدة."),
            ],
        ),
        Section(
            id="ch05-concurrency",
            nav="Ch.5 Concurrency",
            group="الجزء ١ · السرد",
            title="Concurrency",
            subtitle="مستخدمان يعدّلان نفس عقد الإيجار",
            icon="👥",
            tone="coral",
            intent="هنا التزامن معناه جلسات ومستخدمين على نفس البيانات، مش خيوط المعالج. المشاكل: تعديل ضايع، قراءة غير متسقة. الحلول تتدرج من عزل قاعدة البيانات إلى أقفال متفائلة أو متشائمة تعيش خارج المعاملة القصيرة لأن المستخدم بيفكر دقايق.",
            notes=[
                "أقفال الخيوط والطوابير والمفاعل في الجزء ٣. ابدأ من هنا لو السؤال عن مستخدمين، ومن Part 3 لو السؤال عن threads داخل العملية.",
            ],
            use=[
                "شخصان يفتحان نفس العقد ويحفظان حالة مختلفة.",
                "معاملة قصيرة داخل قاعدة البيانات حول تحديث القسط.",
            ],
            avoid=[
                "قفل صف مدة ما المستخدم شايف الشاشة، من غير مهلة انتهاء.",
                "خلط مصطلح Offline Lock مع threading.Lock كأنهم نفس الأداة.",
            ],
            diagram="""
session A reads version 0
session B reads version 0
A commits version 1
B must fail or reload     ← optimistic

threads / pools / reactor  →  #part3-concurrency
            """,
            relations=[
                ("Optimistic Offline Lock", "pattern-optimistic-offline-lock"),
                ("Pessimistic Offline Lock", "pattern-pessimistic-offline-lock"),
                ("Part 3 threads", "part3-concurrency"),
            ],
            lab=STORY,
            demo="offline_preview",
            snippet="""
save_with_version(conn, 1, "billed", version)
# second save with the old version raises Conflict
            """,
            tasks=[
                "مثّل جلستين يعدّلان status ونفّذ التعارض في معمل optimistic_offline_lock.",
                "اكتب جملة تفرّق بين معاملة SQL وقفل أوفلاين أثناء تحرير الشاشة.",
                "من الجزء ٣، سمِّ نمطًا واحدًا تحمي بيه عدّادًا داخل العملية، ووضّح إنه مش بديل version column.",
            ],
            questions=[
                ("إيه lost update؟", "قراءة مشتركة ثم كتابتان؛ الكتابة الأخيرة تمسح الأولى من غير ما تحس."),
                ("المتفائل إيه فكرته؟", "اسمح بالتعديل المتوازي واكتشف التعارض عند الحفظ برقم إصدار."),
                ("المتشائم؟", "امنع الآخر يحرر لحد ما صاحب القفل يخلّص أو القفل ينتهي."),
                ("ليه اسمه offline؟", "لأن التفكير البشري أطول من معاملة قاعدة البيانات، فالقفل أو الإصدار يعيش بين الطلبات."),
                ("هل Thread Pool يحل تعارض مستخدمين؟", "لا. تجمع الخيوط ينفّذ مهامًا داخل العملية. تعارض الصفوف يحتاج إصدار أو قفل عمل."),
            ],
        ),
        Section(
            id="ch06-session",
            nav="Ch.6 Session state",
            group="الجزء ١ · السرد",
            title="Session State",
            subtitle="التطبيق بلا حالة مقابل معالج يتذكر الخطوة",
            icon="🧭",
            tone="teal",
            intent="طلب عرض عقد يقدر يكون بلا حالة: كل حاجة في الرابط. معالج إرجاع الأصل محتاج يتذكر الخطوة والأصل المختار. الحالة دي ممكن ترجع مع العميل، أو تقعد في ذاكرة السيرفر، أو تتخزن في قاعدة.",
            use=[
                "معالج متعدد الخطوات لا يكتمل في طلب واحد.",
                "خوادم متعددة لما الحالة في العميل أو في قاعدة مشتركة.",
            ],
            avoid=[
                "حفظ كائنات دومين حية كاملة داخل جلسة السيرفر.",
                "حالة سيرفر محلية وأنت خلف موازن من غير تثبيت الجلسة أو مخزن مشترك.",
            ],
            diagram="""
stateless     GET /leases/1
client state  hidden fields come back next post
server state  session id → memory map
db state      sessions table
            """,
            relations=[
                ("Client Session State", "pattern-client-session-state"),
                ("Server Session State", "pattern-server-session-state"),
                ("Database Session State", "pattern-database-session-state"),
            ],
            lab=STORY,
            demo="session_preview",
            snippet="""
stateless = {"path": "/leases/1"}
stateful = {"session": "sess-7", "wizard": "confirm"}
            """,
            tasks=[
                "حوّل معالج الإرجاع إلى حقول مخفية يرسلها المتصفح كل مرة.",
                "اكتب نفس الحالة في جدول sessions وقارن إيه اللي يحصل لو عملية السيرفر وقعت.",
                "حدّد بيانات ممنوع تخزينها في الجلسة (كلمة سر، كائن SQL مفتوح).",
            ],
            questions=[
                ("إيه فايدة انعدام الحالة؟", "أي خادم يرد على الطلب، وإعادة التشغيل ما تمسحش محادثة لأن مفيش محادثة على الخادم."),
                ("إمتى الحالة ضرورية؟", "لما العملية تمتد لعدة طلبات زي معالج الإرجاع."),
                ("خطر حالة العميل؟", "العميل يقدر يغيّر الحقول، فلازم تتحقق وتوقّع أو تعيد الفحص."),
                ("خطر حالة السيرفر في الذاكرة؟", "تضيع مع إعادة التشغيل وما تتشاركش بين العقد بسهولة."),
                ("Database Session State بتضحي بإيه؟", "بضربة قاعدة لكل طلب مقابل بقاء الحالة ومشاركتها."),
            ],
        ),
        Section(
            id="ch07-distribution",
            nav="Ch.7 Distribution",
            group="الجزء ١ · السرد",
            title="Distribution Strategies",
            subtitle="لا توزّع الكائنات بالسذاجة",
            icon="📡",
            tone="blue",
            intent="نداء بعيد أغلى وأعرض للتعطل من نداء محلي. واجهة فيها عشرات الدوال الرفيعة عبر الشبكة بتبقى بطيئة. اجمع العملية في واجهة خشنة، وانقل البيانات في كائن مسطّح بدل ما تسحب بيانًا بيانًا.",
            use=[
                "عملية بعيدة حقيقية: تطبيق آخر يفوتر عقدًا.",
                "حد واضح بين خدمتين، بعدد نداءات قليل.",
            ],
            avoid=[
                "جعل كل كائن دومين بعيدًا «عشان المرونة» من غير قياس.",
                "إرجاع بيان كسول عبر الشبكة فيطلب عشرات النداءات.",
            ],
            diagram="""
fine calls (avoid):  getLease, getLine, getLine, getAsset, getRate
coarse call:         billAndSummarize(leaseId) → DTO
            """,
            relations=[
                ("Remote Facade", "pattern-remote-facade"),
                ("Data Transfer Object", "pattern-dto"),
                ("Service Layer", "pattern-service-layer"),
            ],
            lab=STORY,
            demo="distribution_preview",
            snippet="""
summary = RemoteLeaseFacade(conn).bill_and_summarize(1)
# one round trip: id, status, cents, currency
            """,
            tasks=[
                "عدّ النداءات لو العميل البعيد حمّل كل بند لوحده، ثم صمّم نداءً واحدًا يعيد الملخص.",
                "اشرح ليه Lease بكل خطوطه مش أنسب شيء ينعاد على السلك.",
                "ارسم الحد: إيه المحلي داخل العملية وإيه اللي يعبر الشبكة.",
            ],
            questions=[
                ("ليه توزيع الكائنات مغرٍ وخطير؟", "يبان كأن النداء البعيد زي المحلي، فيخبي زمن الشبكة والفشل."),
                ("Remote Facade بيعالج إيه؟", "يجمّع عملية كاملة في دالة خشنة تقلل عدد الرحلات."),
                ("DTO فرقه عن كائن الدومين؟", "الـ DTO شكل نقل من غير سلوك عمل، غالبًا مسطّح وقابل للتسلسل."),
                ("Lazy Load عبر الحدود البعيدة؟", "غالبًا فكرة سيئة لأن كل لمسة تعمل نداءً."),
                ("إمتى التوزيع واجب؟", "لما جزء من النظام لازم يعيش في عملية أو آلة أخرى، مش كاختيار افتراضي."),
            ],
        ),
        Section(
            id="ch08-together",
            nav="Ch.8 Together",
            group="الجزء ١ · السرد",
            title="Putting It All Together",
            subtitle="من الدومين نزولًا إلى مصدر البيانات",
            icon="🧩",
            tone="amber",
            intent="ابدأ بقواعد الإيجار وهي لسه في الذاكرة. لما تستقر، وصّلها بمصدر بيانات بالمابر أو البوابة، وحط Service Layer قدامها للفوترة. الواجهة تطلب الخدمة، والخدمة تطلب الدومين، والمابر يحفظ.",
            use=[
                "تصميم تطبيق جديد: الدومين أولًا ثم التخزين.",
                "مراجعة مسار طلب كامل قبل ما تدخل في أنماط الجزء ٢ واحدًا واحدًا.",
            ],
            avoid=[
                "البدء بتصميم عشرات الجداول قبل ما تسمي قواعد العقد.",
                "إيقاف القصة عند الكائنات من غير ما تجرب الحفظ والقراءة.",
            ],
            diagram="""
1 Domain Lease.monthly_total
2 Mapper or gateway persists invoices
3 Service.bill coordinates
4 Presentation prints USD 900.00
            """,
            relations=[
                ("Layering", "ch01-layering"),
                ("Domain Model", "pattern-domain-model"),
                ("Data Mapper", "pattern-data-mapper"),
                ("Capstone weeks", "roadmap"),
            ],
            lab=STORY,
            demo="together",
            snippet="""
print("domain", load_domain_lease(conn, 1).monthly_total())
print("billed", BillingService(conn).bill(1))
            """,
            tasks=[
                "اتبع demo together وسمِّ كل سطر بطبقته.",
                "أضف خطوة إرجاع: الخدمة تغيّر الحالة والمابر يحفظها.",
                "اكتب قائمة أنماط الجزء ٢ اللي المسار ده لمسها فعلًا.",
            ],
            questions=[
                ("ليه نبدأ بالدومين؟", "لأن تعقيد الإيجار في القواعد، والجداول وسيلة حفظ مش مصدر المعنى."),
                ("إيه ترتيب الطبقات في الطلب؟", "عرض → خدمة → دومين → مصدر بيانات، والرجوع بعكس الاتجاه بالبيانات."),
                ("Active Record ينفع في القصة دي؟", "ينفع لو الكائن بسيط ومستعد يحمل الحفظ. المابر أنسب لو القواعد هتنفصل عن SQL."),
                ("إيه اللي لسه ناقص بعد الفصل ٨؟", "تفاصيل كل نمط: الأقفال، الجلسة، الوراثة، الواجهة البعيدة. دي مرجع الجزء ٢."),
                ("إيه ناتج المعمل المتوقع؟", "المبلغ USD 900.00 من الدومين ثم نفس المبلغ بعد الفوترة."),
            ],
        ),
    ]
