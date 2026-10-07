"""Chapters 9–11: domain logic, data source, OR behavior."""

from peaa.authoring.model import Section

DOM = "peaa/lab/patterns/domain_logic.py"
DS = "peaa/lab/patterns/data_source.py"
BEH = "peaa/lab/patterns/or_behavioral.py"


def _s(**kwargs) -> Section:
    return Section(**kwargs)


def sections() -> list[Section]:
    return [
        _s(
            id="ch09-domain-logic",
            nav="Ch.9 Domain logic",
            group="الجزء ٢ · منطق النطاق",
            title="Domain Logic Patterns",
            subtitle="أربع طرق لتنظيم قواعد الإيجار",
            icon="📚",
            tone="purple",
            intent="الفصل يجمع الاختيارات اللي السرد قدّمها: إجراء لكل عملية، نموذج كائنات، وحدة جدول، وطبقة خدمة تنسّق. اختَر حسب كثافة القواعد مش حسب الموضة.",
            use=["مراجعة قرار منطق عقد التأجير قبل كتابة الجداول.", "مقارنة ناتج نفس القسط تحت أكثر من تنظيم."],
            avoid=["خلط الأنماط الأربعة في نفس العملية من غير سبب.", "خدمة تطبيق فيها كل حسابات العقد وسطر SQL طويل."],
            diagram="Transaction Script | Domain Model | Table Module\n                 Service Layer orchestrates",
            relations=[("Transaction Script", "pattern-transaction-script"), ("Domain Model", "pattern-domain-model"), ("Table Module", "pattern-table-module"), ("Service Layer", "pattern-service-layer")],
            lab=DOM, demo="domain_model",
            snippet="print(load_domain_lease(conn, 1).monthly_total())",
            tasks=["اقرأ الأنماط الأربعة وعلّم على اللي يناسب عقدًا فيه خصم كمية وإرجاع مبكر.", "شغّل المعامل الأربعة وتأكد إن المبلغ واحد لما القاعدة واحدة."],
            questions=[
                ("الفصل ده عن قاعدة البيانات؟", "لا. عن مكان قواعد العمل. الحفظ في الفصل ١٠."),
                ("أنسب نمط لعقد معقّد متغير؟", "Domain Model، وغالبًا Service Layer قدامه."),
                ("Table Module قريب من إيه؟", "من التعامل مع مجموعة سجلات، مش من كائن لكل عقد غني بالسلوك."),
                ("Service Layer بديل للدومين؟", "لا، منسّق. الدومين أو السكربت جواه."),
            ],
        ),
        _s(
            id="pattern-transaction-script",
            nav="Transaction Script",
            group="الجزء ٢ · منطق النطاق",
            title="Transaction Script",
            subtitle="إجراء واحد يفوتر العقد من الجداول",
            icon="📜",
            tone="purple",
            intent="كل حالة استخدام إجراء: اقرأ بنود العقد، اجمع السعر في الكمية، اكتب فاتورة. منطقي وسهل التتبع لما القواعد قليلة وما تتقاطعش.",
            use=["فوترة مباشرة من غير شجرة كائنات.", "تقارير وإجراءات ليلية واضحة الخطوة."],
            avoid=["لما نفس القاعدة تتندّه من خمس إجراءات وتبدأ تتكرر.", "لما العقد فيه أنواع وخصومات بتتفاعل مع بعض."],
            diagram="bill_lease(id):\n  SQL lines → sum → INSERT invoice",
            relations=[("Domain Model", "pattern-domain-model"), ("Service Layer", "pattern-service-layer"), ("Table Data Gateway", "pattern-table-data-gateway")],
            lab=DOM, demo="transaction_script",
            snippet="""
total = 0
for row in lines:
    total += row["monthly_rate_cents"] * row["quantity"]
insert_invoice(lease_id, total)
            """,
            tasks=["أضف في الإجراء شرط إرجاع مبكر يخصم أسبوعًا.", "استخرج التجميع لدالة ولاحظ إنك بدأت تقترب من نموذج.", "قارن طول الإجراء بعد ثلاث قواعد جديدة."],
            questions=[
                ("فين المنطق؟", "في الدالة، جنب الاستعلام، مش على كائن Lease."),
                ("إيه ميزته؟", "تقرأ العملية من فوق لتحت."),
                ("إيه علامة إنها ضاقت؟", "نسخ الشرط في إجراء الترقية وإجراء الإرجاع."),
                ("ينفع تستدعي بوابة جدول من جواها؟", "أيوه. البوابة تخبي SQL والإجراء يفضل ينسّق العملية."),
            ],
        ),
        _s(
            id="pattern-domain-model",
            nav="Domain Model",
            group="الجزء ٢ · منطق النطاق",
            title="Domain Model",
            subtitle="Lease و Asset يحملان قاعدة القسط",
            icon="🏛️",
            tone="purple",
            intent="الكائنات تمثل العقد والبند والأصل، والسلوك عليها: البند يحسب أجره، والعقد يجمع. مناسب لما قواعد التأجير تتفرع وتتعامل مع بعضها.",
            use=["خصومات، غرامات، وترقيات تتداخل.", "نفس القواعد من شاشة ومن مهمة."],
            avoid=["نموذج معقّد لعملية جمع واحدة.", "حط SQL داخل Lease لو اخترت كمان Data Mapper."],
            diagram="Lease\n  lines: LeaseLine\n    asset: Asset\n  monthly_total()",
            relations=[("Transaction Script", "pattern-transaction-script"), ("Data Mapper", "pattern-data-mapper"), ("Money", "pattern-money")],
            lab=DOM, demo="domain_model",
            snippet="""
@dataclass
class Lease:
    lines: list
    def monthly_total(self) -> Money:
        total = Money(0)
        for line in self.lines:
            total += line.charge()
        return total
            """,
            tasks=["أضف نوع أصل ثالث وقاعدة سعر مختلفة على الكائن مش في SQL.", "ارسم الكائنات قبل ما تفتح الجدول.", "وصّل النموذج بـ LeaseMapper من غير ما Lease يستورد sqlite."],
            questions=[
                ("القسط 900 جه منين؟", "500 للشاحنة و200×2 للرافعة، والمجموع على Lease."),
                ("ليه Money مش float؟", "عشان العملة والسنت يفضلوا دقيقين."),
                ("النموذج بيحفظ نفسه؟", "في الشكل النقي لأ. الحفظ Mapper أو Active Record لو اخترته بوعي."),
                ("إمتى ترجع للسكربت؟", "لو الكائنات بقت تمرير بيانات فاضي والمنطق لسه في دالة واحدة."),
            ],
        ),
        _s(
            id="pattern-table-module",
            nav="Table Module",
            group="الجزء ٢ · منطق النطاق",
            title="Table Module",
            subtitle="كلاس واحد يعمل على صفوف العقد",
            icon="📊",
            tone="purple",
            intent="بدل كائن لكل عقد، فيه كلاس LeaseTable ياخد مجموعة صفوف ويحسب عليها. قريب من شاشات وقواعد بتتعامل مع نتيجة استعلام ككتلة.",
            use=["منطق بسيط على نتيجة جدول.", "بيئة سجلّات مش كائنات غنية."],
            avoid=["سلوك مختلف لكل نوع أصل يصعب تمثيله على صف عام.", "خلطه مع Domain Model لنفس العملية من غير حدود."],
            diagram="rows[] → LeaseTable.monthly_total()",
            relations=[("Record Set", "pattern-record-set"), ("Transaction Script", "pattern-transaction-script"), ("Domain Model", "pattern-domain-model")],
            lab=DOM, demo="table_module",
            snippet="""
class LeaseTable:
    def monthly_total(self) -> Money:
        cents = sum(r["monthly_rate_cents"] * r["quantity"] for r in self.rows)
        return Money(cents)
            """,
            tasks=["مرّر صفوف عقدين للكلاس واطبع مجموع كل عقد.", "أضف عمود خصم في الصف وطبّقه داخل الوحدة.", "اكتب فرقًا عن Domain Model بجملة."],
            questions=[
                ("كم نسخة من الكلاس لعشرة عقود؟", "وحدة واحدة تخدم الصفوف، مش عشرة كائنات غنية بالضرورة."),
                ("إيه اللي بيدخله؟", "مجموعة قواميس أو Record Set، مش بيان كسول."),
                ("ينفع يحفظ؟", "غالبًا الحساب هنا والحفظ في بوابة، عشان ما يتضاعفش الدور."),
                ("ليه ناتجه 900؟", "نفس أرقام البنود، تنظيم مختلف."),
            ],
        ),
        _s(
            id="pattern-service-layer",
            nav="Service Layer",
            group="الجزء ٢ · منطق النطاق",
            title="Service Layer",
            subtitle="bill() تنسّق والنموذج يحسب",
            icon="🎛️",
            tone="purple",
            intent="طبقة التطبيق تعرّف العمليات المتاحة: فوتر، أرجِع، رقِّ. جواها معاملة واستدعاء الدومين. الواجهة ما تعرفش ترتيب الحفظ.",
            use=["أكتر من واجهة لنفس الفوترة.", "حاجات تطبيق زي الترانزاكشن حوالين الدومين."],
            avoid=["نقل كل قواعد القسط إلى الخدمة وترك Lease فاضي.", "خدمة لكل دالة كائن من غير حالة استخدام."],
            diagram="UI → BillingService.bill → Lease.monthly_total → INSERT",
            relations=[("Domain Model", "pattern-domain-model"), ("Remote Facade", "pattern-remote-facade"), ("Layering", "ch01-layering")],
            lab=DOM, demo="service_layer",
            snippet="""
class BillingService:
    def bill(self, lease_id: int) -> Money:
        total = load_domain_lease(self.conn, lease_id).monthly_total()
        insert_invoice(self.conn, lease_id, total)
        return total
            """,
            tasks=["أضف return_asset على الخدمة تغيّر الحالة بعد ما الدومين يوافق.", "خلّي الواجهة تنادي الخدمة بس وامسح أي SQL من طبقة العرض.", "اكتب اختبارًا على الخدمة بـ Service Stub."],
            questions=[
                ("الخدمة دومين ولا تطبيق؟", "تطبيق. الدومين هو Lease."),
                ("تفرقها عن Transaction Script؟", "السكربت هو المنطق كله. الخدمة تقدر تنادي نموذج."),
                ("تفرقها عن Remote Facade؟", "الخدمة محلية. الواجهة البعيدة تغلّف نداءً عبر الحدود."),
                ("ليه الفاتورة تتكتب هنا مش في Lease؟", "الكتابة أثر جانبي للعملية. النموذج يحسب، والخدمة تثبّت المعاملة."),
            ],
        ),
        _s(
            id="ch10-data-source",
            nav="Ch.10 Data source",
            group="الجزء ٢ · مصدر البيانات",
            title="Data Source Architectural Patterns",
            subtitle="مين يمتلك SQL: بوابة، صف، سجل نشط، أم مابر",
            icon="💾",
            tone="blue",
            intent="بعد ما تعرف فين القواعد، اختَر شكل الوصول للجدول. البوابة كلاس للجدول كله. بوابة الصف كائن لكل صف. Active Record كائن دومين يحفظ نفسه. Data Mapper يفصل الاتنين.",
            use=["أي حفظ لعقد الإيجار في جداول.", "مقارنة الأنماط الأربعة على نفس الصف."],
            avoid=["مابر كامل قبل ما البوابة البسيطة تخلص المطلوب.", "كائن دومين غني وفي نفس الوقت فيه SQL مبعثر في الواجهة."],
            diagram="Table Gateway → Row Gateway → Active Record → Data Mapper\n(SQL hidden)   (row object)  (domain+save)   (domain | mapper)",
            relations=[("Table Data Gateway", "pattern-table-data-gateway"), ("Row Data Gateway", "pattern-row-data-gateway"), ("Active Record", "pattern-active-record"), ("Data Mapper", "pattern-data-mapper")],
            lab=DS, demo="data_mapper",
            snippet="lease = LeaseMapper(conn).find(1)",
            tasks=["بدّل حالة العقد مرة ببوابة جدول ومرة بمابر.", "اكتب جدول مقارنة من أربع خلايا: فين SQL وفين القواعد."],
            questions=[
                ("الأنماط دي بديل للدومين؟", "لا. دي شكل مصدر البيانات. الدومين قرار الفصل ٩."),
                ("أبعد نمط عن SQL داخل الكائن؟", "Data Mapper."),
                ("أقرب نمط للبساطة مع كائن بيحفظ نفسه؟", "Active Record."),
                ("البوابة بتستقبل دومين غني؟", "عادة لأ. بتستقبل معرفات وقيم وترجع صفوف."),
            ],
        ),
        _s(
            id="pattern-table-data-gateway",
            nav="Table Data Gateway",
            group="الجزء ٢ · مصدر البيانات",
            title="Table Data Gateway",
            subtitle="كل SQL لجدول leases في كلاس واحد",
            icon="🚪",
            tone="blue",
            intent="كلاس واحد يعرف يجد صف العقد ويحدّث حالته. باقي التطبيق ما يكتبش جملة SQL لهذا الجدول. مناسب كأبسط إخفاء لقاعدة البيانات.",
            use=["واجهة ضيقة فوق جدول.", "Transaction Script محتاج مكان يحط فيه SQL."],
            avoid=["كائن بوابة يكبر حتى يصبح مابر وخدمات ونماذج.", "منطق خصم القسط داخل البوابة."],
            diagram="LeaseTableGateway.find / set_status\n        only this class touches leases SQL",
            relations=[("Row Data Gateway", "pattern-row-data-gateway"), ("Gateway", "pattern-gateway"), ("Transaction Script", "pattern-transaction-script")],
            lab=DS, demo="table_data_gateway",
            snippet="""
class LeaseTableGateway:
    def set_status(self, lease_id, status):
        self.conn.execute(
            "UPDATE leases SET status = ? WHERE id = ?",
            (status, lease_id),
        )
            """,
            tasks=["أضف find_active على البوابة واستخدمها من سكربت.", "امنع أي ملف تاني يكتب UPDATE leases.", "أرجع صفًا وخليه يتحول لنموذج بره البوابة."],
            questions=[
                ("الكلاس يمثل صف ولا جدول؟", "الجدول، أو نوع الوصول للجدول."),
                ("بيرجع كائن دومين؟", "في المعمل بيرجع صف. التحويل قرار أعلى."),
                ("فرقه عن Gateway العام؟", "Gateway يغلّف أي واجهة خارجية. Table Data Gateway مخصوص لجدول."),
                ("فين المعاملة؟", "غالبًا المستدعي أو Unit of Work، مش شرط داخل كل دالة."),
            ],
        ),
        _s(
            id="pattern-row-data-gateway",
            nav="Row Data Gateway",
            group="الجزء ٢ · مصدر البيانات",
            title="Row Data Gateway",
            subtitle="كائن لكل صف يعرف يحدّث نفسه",
            icon="🧾",
            tone="blue",
            intent="كل صف عقد كائن فيه الحقول ودالة update. قريب من Active Record لكن من غير ما تدّعي إن فيه قواعد عمل غنية. البيانات والكتابة بس.",
            use=["صفوف بسيطة والتطبيق يعدّل حقولًا ثم يحفظ.", "خطوة وسطى قبل ما الدومين ينضج."],
            avoid=["حشر monthly_total المعقّد هنا وتسميته دومين.", "نسخ كثيرة تعيش طويلًا وتختلف عن القاعدة."],
            diagram="row = LeaseRow(sql row)\nrow.status = returned\nrow.update()",
            relations=[("Table Data Gateway", "pattern-table-data-gateway"), ("Active Record", "pattern-active-record"), ("Identity Map", "pattern-identity-map")],
            lab=DS, demo="row_data_gateway",
            snippet="""
row.status = "returned"
row.update()  # writes this id only
            """,
            tasks=["غيّر حالتين لصفّين واحفظ كل واحد.", "أضف حقل version على الكائن من غير قاعدة عمل.", "اكتب ليه ده لسه مش Domain Model."],
            questions=[
                ("كم كائن لعقدين؟", "كائنان، واحد لكل صف."),
                ("السلوك التجاري فين؟", "مش هنا. هنا حقول وتحديث."),
                ("إيه اللي يميزه عن Active Record؟", "Active Record يضيف سلوك الدومين على نفس كائن الحفظ."),
                ("خطر النسخ؟", "تحميل الصف مرتين يعمل كائنين يختلفان. عالجها بـ Identity Map لو مهم."),
            ],
        ),
        _s(
            id="pattern-active-record",
            nav="Active Record",
            group="الجزء ٢ · مصدر البيانات",
            title="Active Record",
            subtitle="كائن العقد يحسب ويحفظ",
            icon="✏️",
            tone="blue",
            intent="Lease يعرف القسط ويعرف save. نمط سريع لما الدومين بسيط والجدول قريب من الكائن. الاقتران بقاعدة البيانات هو التمن.",
            use=["كائنات تكاد تطابق الصفوف وقواعدها محدودة.", "نماذج أولية تتحول لمابر لو كبرت."],
            avoid=["مجال معقّد هتختبره من غير قاعدة.", "وراثة جدول معقّدة جوه نفس الكائن."],
            diagram="ActiveLease.monthly_total()\nActiveLease.save()  → UPDATE",
            relations=[("Domain Model", "pattern-domain-model"), ("Data Mapper", "pattern-data-mapper"), ("Row Data Gateway", "pattern-row-data-gateway")],
            lab=DS, demo="active_record",
            snippet="""
lease.status = "active"
print(lease.monthly_total())
lease.save()
            """,
            tasks=["أضف save يرفض حالة فارغة قبل الكتابة.", "انقل monthly_total لكائن دومين خالص وقارن الاختبار.", "سمِّ اعتماد الكائن على conn."],
            questions=[
                ("ليه الاختبار أصعب؟", "لأن السلوك والحفظ متلاصقين؛ غالبًا تحتاج قاعدة أو اتصال."),
                ("ينفع مع Domain Model الغني؟", "ينفع في البداية. لو القواعد كبرت، افصل مابر."),
                ("إيه اللي المعمل بيطبعه؟", "USD 900.00 ثم الحالة."),
                ("فرقه عن بوابة الصف؟", "بوابة الصف بيانات. Active Record يضيف سلوك العمل."),
            ],
        ),
        _s(
            id="pattern-data-mapper",
            nav="Data Mapper",
            group="الجزء ٢ · مصدر البيانات",
            title="Data Mapper",
            subtitle="Lease ما يعرفش SQL والمابر يترجم",
            icon="🔀",
            tone="blue",
            intent="كائن الدومين فيه can_bill والحالة. LeaseMapper يقرأ الصف ويبني الكائن، ويكتب الكائن إلى UPDATE. الاتجاهين منفصلين. أنسب اختيار لو نموذج الإيجار هيعيش أطول من شكل الجدول.",
            use=["دومين غني وقاعدة علائقية.", "اختبار القواعد من غير اتصال."],
            avoid=["مابر لكل حقل في تطبيق من ثلاث شاشات.", "تسريب Row إلى الواجهة."],
            diagram="DomainLease  ← LeaseMapper →  leases row",
            relations=[("Domain Model", "pattern-domain-model"), ("Unit of Work", "pattern-unit-of-work"), ("Repository", "pattern-repository")],
            lab=DS, demo="data_mapper",
            snippet="""
lease = mapper.find(1)
lease.status = "closed"   # no SQL here
mapper.update(lease)
            """,
            tasks=["أضف حقلًا على الكائن مش عمودًا بعد، وخلّي المابر يتجاهله.", "اكتب اختبار can_bill من غير sqlite.", "اربط المابر بـ Unit of Work بدل commit داخل update."],
            questions=[
                ("مين فيه can_bill؟", "DomainLease. المابر ما يعرفش القاعدة."),
                ("ليه الانفصال مفيد؟", "تغيّر الجدول أو تختبر القاعدة لوحدها."),
                ("إيه ثمنه؟", "كود ترجمة أكتر بين الحقل والعمود."),
                ("علاقته بـ Repository؟", "المستودع واجهة مجموعة. المابر آلية التحميل والحفظ."),
            ],
        ),
        _s(
            id="ch11-or-behavioral",
            nav="Ch.11 OR behavior",
            group="الجزء ٢ · سلوك الربط",
            title="Object-Relational Behavioral Patterns",
            subtitle="وحدة العمل، خريطة الهوية، والتحميل الكسول",
            icon="🔁",
            tone="teal",
            intent="سلوك الجلسة مع القاعدة: تتبّع إيه اللي اتغير واكتبه مرة، لا تكرر كائن الصف في الذاكرة، ولا تحمّل البنود قبل ما تتلمس.",
            use=["نموذج كائنات فوق جداول.", "جلسة طلب فيها عدة تعديلات."],
            avoid=["الأنماط الثلاثة في سكربت من استعلام واحد.", "Lazy Load يخبي نداء شبكة."],
            diagram="Identity Map (same object)\nUnit of Work (commit once)\nLazy Load (lines on touch)",
            relations=[("Unit of Work", "pattern-unit-of-work"), ("Identity Map", "pattern-identity-map"), ("Lazy Load", "pattern-lazy-load")],
            lab=BEH, demo="unit_of_work",
            snippet="uow.register_dirty(1, 'billed'); uow.commit()",
            tasks=["في طلب واحد وسّخ عقدًا وأضف عقدًا واعمل commit واحد.", "حمّل العقد مرتين وتأكد إن الهوية واحدة."],
            questions=[
                ("الثلاثة عن شكل الجدول؟", "لا. الشكل في الفصل ١٢. هنا سلوك التحميل والحفظ."),
                ("Unit of Work بتستبدل المعاملة؟", "بتجمع التغييرات ثم تستخدم معاملة عند commit."),
                ("Identity Map بتحل إيه؟", "نسختين لنفس المفتاح."),
                ("Lazy Load خطرها؟", "استعلام مفاجئ، أو عاصفة استعلامات لو لمست بيانًا بيانًا."),
            ],
        ),
        _s(
            id="pattern-unit-of-work",
            nav="Unit of Work",
            group="الجزء ٢ · سلوك الربط",
            title="Unit of Work",
            subtitle="جديد، متّسخ، ومحذوف ثم كتابة واحدة",
            icon="📦",
            tone="teal",
            intent="بدل ما كل كائن يعمل commit، الوحدة تسجّل الجديد والمتغير والمحذوف وتكتبهم في نهاية العملية. المعمل يعلّم عقد ١ متّسخ ويضيف عقد ٩.",
            use=["عدة كائنات تتغير في طلب واحد.", "عايز ترتيب الكتابة (الأب قبل البنود) في مكان واحد."],
            avoid=["استعلام قراءة فقط.", "نسيان تسجيل كائن اتعدل في الذاكرة."],
            diagram="register_dirty(1)\nregister_new(9)\ncommit → UPDATE + INSERT",
            relations=[("Data Mapper", "pattern-data-mapper"), ("Identity Map", "pattern-identity-map"), ("Implicit Lock", "pattern-implicit-lock")],
            lab=BEH, demo="unit_of_work",
            snippet="""
uow.register_dirty(1, "billed")
uow.register_new(9, 2, "draft")
uow.commit()
            """,
            tasks=["سجّل حذف عقد وأكّد إنه اختفى بعد commit فقط.", "رتّب كتابة الأب قبل البنود لو أضفت خطوطًا جديدة.", "اربط التسجيل بتعديل خاصية على الكائن تلقائيًا."],
            questions=[
                ("إيه الثلاث قوائم؟", "new و dirty و deleted."),
                ("ليه commit واحد؟", "عشان العملية كلها تنجح أو تترجع، ومن غير كتابات نصّية."),
                ("محتاج Identity Map معاها؟", "مفيد عشان ما تسجّلش نفس الكائن مرتين كنسخ."),
                ("المعمل بيخلّي حالة العقد ١ إيه؟", "billed، ويظهر عقد 9 draft."),
            ],
        ),
        _s(
            id="pattern-identity-map",
            nav="Identity Map",
            group="الجزء ٢ · سلوك الربط",
            title="Identity Map",
            subtitle="مفتاح واحد يعني كائن واحد في الجلسة",
            icon="🪪",
            tone="teal",
            intent="أول تحميل للعقد يبني الكائن ويخزّنه في خريطة. التحميل التاني يرجّع نفس المرجع. تعديل الحالة على الأول يظهر في التاني لأنهم واحد.",
            use=["جلسة فيها نفس العقد يُطلب من أكثر من مكان.", "منع تضارب نسخ قبل الحفظ."],
            avoid=["خريطة عامة لكل العمليات من غير حدود جلسة.", "كاش طويل يعيش بعد ما الصف يتغير في قاعدة أخرى."],
            diagram="get(1) → load → cache\nget(1) → cache hit (same object)",
            relations=[("Unit of Work", "pattern-unit-of-work"), ("Identity Field", "pattern-identity-field"), ("Data Mapper", "pattern-data-mapper")],
            lab=BEH, demo="identity_map",
            snippet="""
first = ident.get(1)
second = ident.get(1)
first["status"] = "touched"
# second["status"] is touched, first is second
            """,
            tasks=["أثبت إن is ترجع True للتحميلين.", "امسح الخريطة بين طلبين HTTP.", "اشرح إيه اللي يحصل لو خريطة الهوية أقدم من تحديث مستخدم تاني."],
            questions=[
                ("الخريطة بتستبدل المفتاح في القاعدة؟", "لا. المفتاح في الصف. الخريطة في الذاكرة."),
                ("نطاقها؟", "جلسة أو طلب، مش عمر العملية كلها إلا بوعي."),
                ("علاقتها بـ Identity Field؟", "الحقل هو المفتاح. الخريطة تستخدمه عشان تمنع التكرار."),
                ("المعمل بيغيّر إيه؟", "حالة النسخة الوحيدة إلى touched."),
            ],
        ),
        _s(
            id="pattern-lazy-load",
            nav="Lazy Load",
            group="الجزء ٢ · سلوك الربط",
            title="Lazy Load",
            subtitle="بنود العقد تتحمل عند أول لمسة",
            icon="⏳",
            tone="teal",
            intent="بناء Lease ما يجيبش البنود فورًا. أول قراءة للخاصية تنفّذ الاستعلام ثم تحفظ الناتج. مفيد لو كثير من المسارات ما تحتاجش البنود.",
            use=["علاقة تقيلة ومش دايمًا مطلوبة.", "قائمة عقود من غير تفاصيل."],
            avoid=["الوصول للخاصية جوه حلقة على مئات العقود فيعمل استعلامًا لكل واحد.", "كسول عبر نداء بعيد."],
            diagram="LazyLease created (lines is None)\ntouch .lines → SELECT → cached",
            relations=[("Identity Map", "pattern-identity-map"), ("Dependent Mapping", "pattern-dependent-mapping"), ("Data Mapper", "pattern-data-mapper")],
            lab=BEH, demo="lazy_load",
            snippet="""
print(lease._lines)   # None
print(lease.lines)    # fetches once
print(lease.lines)    # no second fetch
            """,
            tasks=["عدّ الاستعلامات عند لمسة واحدة ولمسة ثانية.", "اكتب مسار قائمة ما يلمسش lines.", "حوّل التحميل إلى تحميل مسبق وقارن عدد الاستعلامات."],
            questions=[
                ("إمتى الاستعلام بيحصل؟", "أول استخدام للخاصية، مش وقت بناء الكائن."),
                ("إيه عاصفة N+1؟", "استعلام للقائمة ثم استعلام لكل عنصر لأن كل واحد كسول."),
                ("فين الخطر مع الواجهة البعيدة؟", "كل لمسة تبقى رحلة شبكة."),
                ("المعمل بيحمّل كام بند؟", "بندين للعقد ١."),
            ],
        ),
    ]
