"""Part 3 — in-process concurrency. Not in the PEAA book."""

from peaa.authoring.model import Section

WORK = "peaa/lab/concurrency/workers.py"
SYNC = "peaa/lab/concurrency/sync.py"
EXEC = "peaa/lab/concurrency/execution.py"
SAFE = "peaa/lab/concurrency/resilience.py"
G = "الجزء ٣ · تزامن داخل العملية"


def _s(**kwargs) -> Section:
    kwargs.setdefault("group", G)
    return Section(**kwargs)


def sections() -> list[Section]:
    return [
        _s(
            id="part3-concurrency",
            nav="Part 3 intro",
            group=G,
            title="Concurrency Patterns",
            subtitle="خيوط ومهام داخل العملية — إضافة مش من الكتاب",
            icon="🧵",
            tone="coral",
            intent="الجزء ده خريطة أنماط تنفيذ متوازٍ داخل عملية: تجمعات، طوابير، أقفال، أحداث، وعزل أعطال. مختلف عن فصل ٥ وفصل ١٦ اللي بيحموا صف عقد الإيجار بين مستخدمين.",
            notes=["لو السؤال «مستخدمان حفظوا نفس العقد» ارجع لـ Optimistic Offline Lock. لو السؤال «خيطان يعدّلان عدّادًا» كمّل هنا."],
            use=["مهام خلفية، طوابير، وحدود زمن داخل خدمة الفوترة.", "فهم اسم النمط قبل ما تستخدم أداة جاهزة."],
            avoid=["استبدال version column بـ Lock.", "نمط خيوط لمشكلة جلسة ويب."],
            diagram="""
PEAA offline     users / versions / business locks
Part 3           threads, tasks, queues, event loops, bulkheads
            """,
            relations=[("Ch.5 Concurrency", "ch05-concurrency"), ("Offline locks", "ch16-offline"), ("Thread Pool", "conc-thread-pool"), ("Monitor", "conc-monitor-object")],
            lab=WORK, demo="thread_pool",
            snippet="""
# users conflict on a row:
#   UPDATE ... WHERE version = ?
# threads share a counter:
#   with lock: counter += 1
            """,
            tasks=["اكتب مثالين: تعارض جلستين، وسباق خيطين، وسمِّ النمط لكل واحد.", "شغّل thread_pool و rate_limiter في نفس الجلسة."],
            questions=[
                ("الجزء في فهرس الكتاب؟", "لا. إضافة دراسية."),
                ("Offline Lock يوقف خيط؟", "لا. يحمى صفًا بين طلبات."),
                ("Thread Pool يحل lost update؟", "لا."),
                ("من أين تبدأ؟", "من تجمع أو طابور لو عندك مهام، ومن قفل لو عندك ذاكرة مشتركة."),
            ],
        ),
        _s(id="conc-thread-pool", nav="Thread Pool", title="Thread Pool / Worker Pool", subtitle="عدد ثابت من العمال لطابور شغل", icon="🏊", tone="coral",
           intent="بدل خيط لكل فاتورة، خزّان عمال يسحب من طابور. ThreadPoolExecutor يديك النسخة الجاهزة؛ المعمل يبيّن طابورًا يدويًا يجنبها.",
           use=["مهام كثيرة قصيرة وعايز تحدّ التوازي.", "مقارنة يدوي مع المكتبة."],
           avoid=["خيط لكل مهمة بلا حد.", "مهام تنتظر بعض داخل نفس الخزان فتعمل مأزق."],
           diagram="queue → workers w0 w1 w2\nexecutor.map for the same jobs",
           relations=[("Producer / Consumer", "conc-producer-consumer"), ("Bulkhead", "conc-bulkhead")],
           lab=WORK, demo="thread_pool",
           snippet="""
jobs.put(number)
# worker loops until None
with ThreadPoolExecutor(max_workers=3) as pool:
    squares = list(pool.map(lambda n: n * n, range(6)))
            """,
           tasks=["ارفع عدد المهام ولاحظ أسماء الخيوط في السجل.", "استبدل اليدوي بالمنفّذ فقط وقارن الكود.", "ضع حدًا للمهام المعلّقة."],
           questions=[("ليهه عدد ثابت؟", "عشان ما تفتحش خيطًا بلا سقف."), ("المعمل فيه شكلان؟", "طابور يدوي و ThreadPoolExecutor."), ("لو المهمة أسرع من التبديل؟", "ممكن عامل واحد يفرّغ الطابور. ده مش خطأ."), ("علاقته بأوفلاين؟", "لا يحمي صف قاعدة بين مستخدمين.")]),
        _s(id="conc-producer-consumer", nav="Producer / Consumer", title="Producer / Consumer", subtitle="طابور محدود يضغط المنتج", icon="🔁", tone="coral",
           intent="المنتج يضع أرقامًا والمستهلك يسحبها. الطابور سعته 2، فلو الامتلاء حصل المنتج ينتظر. ده ضغط عكسي من غير قائمة بلا نهاية.",
           use=["فصل توليد الفواتير عن إرسالها.", "حماية المستهلك البطيء."],
           avoid=["طابور بلا حد يبتلع الذاكرة.", "مستهلك واحد نقطة تعطل من غير رقابة."],
           diagram="producer → queue(max=2) → consumer",
           relations=[("Thread Pool", "conc-thread-pool"), ("Guarded Suspension", "conc-guarded-suspension")],
           lab=WORK, demo="producer_consumer",
           snippet="buffer = queue.Queue(maxsize=2)",
           tasks=["صغّر السعة ولاحظ إن الناتج النهائي لسه مرتب.", "أضف مستهلكًا ثانيًا.", "اكتب إيه اللي يحصل من غير maxsize."],
           questions=[("الضغط العكسي فين؟", "put يمنع المنتج والطابور ممتلئ."), ("المعمل يستهلك إيه؟", "0 إلى 4."), ("ليهه None؟", "إشارة إيقاف."), ("فرقه عن تجمع؟", "هنا الطرفان صريحان. التجمع عمال عامون.")]),
        _s(id="conc-active-object", nav="Active Object", title="Active Object", subtitle="نداء يتحول لرسالة على خيط خاص", icon="🎭", tone="coral",
           intent="ActiveBiller له خيط واحد وطابور. bill تضع رسالة وتنتظر الرد. التسلسل داخل الكائن من غير ما المستدعي يمسك قفلًا لكل حقل.",
           use=["كائن حالته تتعدل من نداءات كثيرة وعايز ترتيبًا.", "تغليف التزامن خلف دالة عادية."],
           avoid=["نداء متزامن غالي والمستدعي حساس للتأخير.", "كائنات نشطة كتير بعدد الخيوط بلا داعي."],
           diagram="bill() → queue → private thread → result box",
           relations=[("Monitor Object", "conc-monitor-object"), ("Future / Promise", "conc-future-promise")],
           lab=WORK, demo="active_object",
           snippet="box.put(method(arg))  # runs on the private thread",
           tasks=["أضف رسالة ثانية غير الفوترة.", "اجعل الإيقاف برسالة None.", "قارن مع قفل على الدوال."],
           questions=[("مين ينفّذ الجسم؟", "الخيط الخاص مش المستدعي."), ("المعمل يضيف كام؟", "1000 على المبلغ."), ("ليهه طابور؟", "عشان الطلبات تتسلسل."), ("فرقه عن Monitor؟", "المراقب يقفل الدالة. الكائن النشط يفصل خيط التنفيذ.")]),
        _s(id="conc-future-promise", nav="Future / Promise", title="Future / Promise", subtitle="نتيجة لسه هتوصل", icon="⏳", tone="coral",
           intent="ترسل الشغل وتاخد Future. as_completed يديك اللي خلّص. الوعد يفصل إطلاق المهمة عن انتظارها.",
           use=["عدة حسابات مستقلة.", "تجميع نتائج من غير ترتيب الإطلاق."],
           avoid=["نسيان قراءة الاستثناء من النتيجة.", "انتظار دائري بين وعدين."],
           diagram="submit → Future → as_completed → values",
           relations=[("Thread Pool", "conc-thread-pool"), ("Proactor", "conc-proactor")],
           lab=WORK, demo="future_promise",
           snippet="done = [future.result() for future in as_completed(futures)]",
           tasks=["اطبع النتائج بترتيب الإكمال ثم رتّبها.", "ارمِ خطأ من مهمة واقرأه من future.", "قارن مع انتظار خيط join يدوي."],
           questions=[("Future يمثل إيه؟", "نتيجة لم تكتمل بعد أو اكتملت."), ("المعمل يرجّع إيه مرتبًا؟", "0 و10 و20 و30."), ("ليهه as_completed؟", "تتعامل مع الجاهز أولًا."), ("الاستثناء فين؟", "يطلع لما تنادي result.")]),
        _s(id="conc-scheduler", nav="Scheduler", title="Scheduler", subtitle="مواعيد على كومة", icon="⏰", tone="coral",
           intent="المهام ليها زمن استحقاق. الكومة تطلع الأقرب. المعمل ساعة افتراضية: شغّل المستحق عند 0 ثم قدّم الساعة إلى 5 لتشغيل التذكير. من غير نوم هش.",
           use=["فوترة مؤجلة وتذكير.", "اختبار الزمن من غير sleep."],
           avoid=["نوم حقيقي في اختبار يتقلب.", "مهمة دورية من غير حد على التأخير المتراكم."],
           diagram="heap (due, name)\nrun due<=0 then advance clock to 5",
           relations=[("Thread Pool", "conc-thread-pool"), ("Rate Limiter", "conc-rate-limiter")],
           lab=WORK, demo="scheduler",
           snippet="heapq.heappush(pending, (clock + delay, seq, name))",
           tasks=["أضف مهمة عند الزمن 3 وتأكد إنها بين الدفعة الأولى والتذكير.", "اشرح ليه الساعة افتراضية.", "اربط مهمة الفوترة بـ BillingService."],
           questions=[("ليهه كومة؟", "أصغر زمن في القمة."), ("ترتيب المعمل؟", "bill ثم notify ثم remind."), ("ليه مش sleep؟", "عشان النتيجة تتكرر."), ("دوري إزاي؟", "بعد التشغيل أعد الجدولة بزمن جديد.")]),
        _s(id="conc-rwlock", nav="Read/Write Lock", title="Read/Write Lock", subtitle="قرّاء معًا أو كاتب وحده", icon="📖", tone="blue",
           intent="قراءات عقد كثيرة تمشي مع بعض. الكتابة تنتظر حتى يخلو القرّاء، والقرّاء ينتظرون الكاتب. أثقل من قفل عادي لما القراءة هي الغالبة.",
           use=["بيانات تتقرأ كثيرًا وتُكتب نادرًا.", "لقطة إعدادات أو تسعير."],
           avoid=["كتابة مستمرة؛ القفل العادي أبسط.", "سياسة تجويع الكاتب لو القرّاء ما يقفوش."],
           diagram="readers ++ while no writer\nwriter waits for readers == 0",
           relations=[("Lock Splitting", "conc-lock-splitting"), ("Monitor Object", "conc-monitor-object")],
           lab=SYNC, demo="rwlock",
           snippet="""
lock.acquire_read()
# ...
lock.release_read()
            """,
           tasks=["أضف كاتبًا ثانيًا ولاحظ التسلسل.", "اكتب مسار تجويع ممكن.", "قارن مع RLock لما الكل كاتب."],
           questions=[("القرّاء مع بعض؟", "نعم طالما مفيش كاتب."), ("الكاتب؟", "وحده."), ("المعمل يسجل إيه؟", "قراءتين ثم كتابة أو ترتيب متداخل آمن."), ("فرقه عن version؟", "ده قفل خيوط. الإصدار قفل عمل بين طلبات.")]),
        _s(id="conc-lock-splitting", nav="Lock Splitting", title="Lock Splitting", subtitle="قفل للفوترة وقفل للإشعار", icon="✂️", tone="blue",
           intent="عدادان مستقلان ما يتقاسموش قفلًا واحدًا. تقسيم القفل يقلل الانتظار لما الموارد ما تتقاطعش.",
           use=["حالتان ما تتعدّلش مع بعض.", "قفل خشن أصبح عنق زجاجة."],
           avoid=["تقسيم ثم نسيان ترتيب موحّد فتعمل مأزق.", "قفل لكل حقل والتداخل ما زال يحتاج الاثنين."],
           diagram="billing.lock  → billing.n\nnotify.lock   → notify.n",
           relations=[("Striped Locking", "conc-striped-locking"), ("Read/Write Lock", "conc-rwlock")],
           lab=SYNC, demo="lock_splitting",
           snippet="with box['lock']:\n    box['n'] += 1",
           tasks=["اجمع العدادين تحت قفل واحد وقارن الشكل.", "أضف موردًا ثالثًا مستقلاً.", "ارسم مأزقًا لو كل طرف أخذ قفل الآخر."],
           questions=[("ليهه قفلان؟", "الموردان مستقلان."), ("المعمل يعدّ كام؟", "100 و100."), ("خطر التقسيم؟", "مأزق لو الترتيب اختلف."), ("إمتى ترجع للقفل الخشن؟", "لما التعديل دايمًا يمس الاتنين.")]),
        _s(id="conc-striped-locking", nav="Striped Locking", title="Striped Locking", subtitle="المفتاح يختار قفلًا من مصفوفة", icon="🦓", tone="blue",
           intent="بدل قفل لكل عقد، مصفوفة أقفال. الهاش يختار الشريط. عقود مختلفة غالبًا ما تتعطلش، ونفس العقد يتسلسل. الذاكرة ثابتة.",
           use=["مفاتيح كثيرة والتوازي على مفاتيح مختلفة.", "كاش أو أرصدة."],
           avoid=["عدد شرائط صغير جدًا يعيد القفل الخشن.", "افتراض إن مفتاحين مختلفين دايمًا على شريطين."],
           diagram="hash(key) % 4 → lock → balance",
           relations=[("Lock Splitting", "conc-lock-splitting"), ("Read/Write Lock", "conc-rwlock")],
           lab=SYNC, demo="striped_locking",
           snippet="return self._locks[hash(key) % len(self._locks)]",
           tasks=["زِد الشرائط وقارن الفكرة.", "أثبت إن نفس المفتاح يتسلسل بجمع 10 و5.", "اشرح تصادم شريط."],
           questions=[("ليهه مش قفل لكل مفتاح؟", "عدد المفاتيح غير محدود."), ("ناتج المعمل؟", "15 و7."), ("تصادم يعني إيه؟", "مفتاحان مختلفان على نفس القفل فينتظرا بلا داع."), ("فرقه عن التقسيم؟", "التقسيم موارد معروفة. الشريط مفاتيح كثيرة.")]),
        _s(id="conc-guarded-suspension", nav="Guarded Suspension", title="Guarded Suspension", subtitle="استنى لحد الشرط", icon="🛑", tone="blue",
           intent="الخيط ينتظر على Condition مادام الفاتورة مش جاهزة. الناشر يغيّر الشرط ويعمل notify. الفحص داخل الحلقة لأن الاستيقاظ ممكن يكون مبكرًا.",
           use=["انتظار حدث مش زمن ثابت.", "يد بديلة عن النوم والحلقات العمياء."],
           avoid=["if بدل while قبل الانتظار.", "نسيان notify بعد تغيير الشرط."],
           diagram="while not ready: wait()\nready = True; notify_all()",
           relations=[("Producer / Consumer", "conc-producer-consumer"), ("Monitor Object", "conc-monitor-object")],
           lab=SYNC, demo="guarded_suspension",
           snippet="""
while not ready["value"]:
    cond.wait()
            """,
           tasks=["أضف مهلة انتظار.", "اشرح ليه while مش if.", "اربط الجاهزية بوضع عنصر في الطابور."],
           questions=[("الشرط إيه؟", "ready."), ("ليهه حلقة؟", "الاستيقاظ مش دايمًا يعني الشرط تحقق."), ("المعمل يضيف إيه للقائمة؟", "ran."), ("فرقه عن sleep؟", "بيصحى بالحدث مش بالزمن.")]),
        _s(id="conc-barrier", nav="Barrier", title="Barrier", subtitle="ما حدّش يكمل قبل ما الكل يوصل", icon="🚧", tone="blue",
           intent="ثلاث خيوط تسجّل وصولها ثم تنتظر على Barrier. مرحلة «انطلق» ما تبدأش إلا بعد الوصول الثالث. تنسيق مراحل مش حماية بيانات.",
           use=["مرحلة حساب تنتهي عند الجميع قبل الدمج.", "اختبار ترتيب المراحل."],
           avoid=["خيط ما هيوصلش فيعلق الباقي.", "استخدامه كقفل بيانات."],
           diagram="arrive arrive arrive | barrier | go go go",
           relations=[("Guarded Suspension", "conc-guarded-suspension"), ("Leader/Followers", "conc-leader-followers")],
           lab=SYNC, demo="barrier",
           snippet="barrier = threading.Barrier(3)\nbarrier.wait()",
           tasks=["غيّر العدد إلى 4 ولاحظ التعليق لو خيط ناقص ثم أصلح.", "اكتب مرحلتين بحاجزين.", "قارن مع join."],
           questions=[("بيحمي بيانات؟", "لا. ينسّق مرحلة."), ("المعمل يثبت إيه؟", "كل الوصول قبل أي انطلاق."), ("لو خيط سقط؟", "الباقي قد يعلق ما لم تكسر الحاجز."), ("فرقه عن Latch؟", "الحاجز يعاد استخدامه لمراحل. المزلاج غالبًا مرة.")]),
        _s(id="conc-work-stealing", nav="Work Stealing", title="Work Stealing", subtitle="العاطل يسحب من طرف زميله", icon="🫳", tone="teal",
           intent="كل عامل له طابور مزدوج. لو فاضي يسحب من طرف طابور غيره. المعمل مبسّط: طابور فيه ثلاث فواتير وآخر فاضي يسرق الأخيرة. يقلل تعطل عامل وهو زميله غارق.",
           use=["مهام غير متساوية الطول.", "جدولة داخل عملية بعدة طوابير."],
           avoid=["سرقة من الرأس فتصادم مع المالك.", "تنفيذ معقّد قبل ما طابور واحد يفشل."],
           diagram="deque A: bill-1 bill-2 | steal bill-3 → B",
           relations=[("Thread Pool", "conc-thread-pool"), ("Scheduler", "conc-scheduler")],
           lab=EXEC, demo="work_stealing",
           snippet="deques[thief].append(deques[victim].pop())",
           tasks=["اشرح ليه السرقة من الطرف الآخر.", "أضف عاملًا ثالثًا فاضيًا.", "قارن مع طابور مشترك واحد."],
           questions=[("مين يسرق؟", "العاطل من المشغول."), ("المعمل يعلّم المسروق إزاي؟", "بادئة stolen."), ("ليهه الطرف؟", "عشان يقلل التصادم مع المالك اللي يشتغل من الطرف التاني."), ("ده موازنة حمل؟", "شكل بسيط منها.")]),
        _s(id="conc-reactor", nav="Reactor", title="Reactor", subtitle="خيط واحد يوزّع الجاهز", icon="☢️", tone="teal",
           intent="selectors يراقب مقبسًا. لما البايتات تجهز، المعالج يقرأ. خيط واحد، أحداث كثيرة. المعمل زوج مآخذ محلي يرسل lease-bill.",
           use=["إدخال/إخراج كثير والانتظار على الشبكة هو الغالب.", "فهم حلقة أحداث قبل إطار."],
           avoid=["شغل ثقيل على خيط المفاعل يجمّد الكل.", "خلطه مع خيط لكل اتصال من غير سبب."],
           diagram="socketpair → select → on_read",
           relations=[("Proactor", "conc-proactor"), ("Leader/Followers", "conc-leader-followers")],
           lab=EXEC, demo="reactor",
           snippet="selector.register(left, selectors.EVENT_READ, on_read)",
           tasks=["أضف مقبسًا ثانيًا ومعالجًا مختلفًا.", "اكتب ليه الحساب الثقيل يطلع من الخيط.", "قارن مع خيط حاجب لكل اتصال."],
           questions=[("مين ينتظر؟", "خيط واحد على select."), ("المعمل يقرأ إيه؟", "lease-bill."), ("الخطر؟", "تعطيل الحلقة بشغل طويل."), ("فرقه عن Proactor؟", "المفاعل يبلغ إن المصدر جاهز. البرواكتور يبلغ إن العملية خلصت.")]),
        _s(id="conc-proactor", nav="Proactor", title="Proactor", subtitle="المعالج يشتغل عند اكتمال العملية", icon="✅", tone="teal",
           intent="تبدأ عملية غير حاجبة وتسجّل إكمال. لما الـ Future يخلص، النداء الراجع يشتغل. asyncio هنا تشبيه للإكمال مش خادم إنتاج. نوم صفري يتيح تشغيل النداء المجدول.",
           use=["إكمال قراءة أو كتابة من غير ما تلف على الجاهزية بنفسك.", "ربط بـ Future."],
           avoid=["نسيان إن النداء قد يتجدول مش ينفّذ فورًا.", "عمل ثقيل داخل نداء الإكمال."],
           diagram="set_result → scheduled callback → invoice-ready",
           relations=[("Reactor", "conc-reactor"), ("Future / Promise", "conc-future-promise")],
           lab=EXEC, demo="proactor",
           snippet="""
future.add_done_callback(on_done)
future.set_result("invoice-ready")
await asyncio.sleep(0)
            """,
           tasks=["أضف إكمالًا ثانيًا بخطأ.", "اشرح دور sleep(0).", "قارن بجملة مع Reactor."],
           questions=[("إيه اللي بيتبلَّغ؟", "إن العملية اكتملت."), ("ليهه sleep 0؟", "عشان نداء الإكمال المجدول يلحق يشتغل."), ("المعمل يطبع إيه؟", "invoice-ready."), ("فين التشبيه؟", "asyncio Future مش نموذج IOCP كامل.")]),
        _s(id="conc-leader-followers", nav="Leader/Followers", title="Leader/Followers", subtitle="القائد يأخذ الشغل ثم يرقّي التالي", icon="👑", tone="teal",
           intent="خيط واحد قائد ينتظر الحدث. لما الشغل يوصل يرقّي تابعًا ليصبح القائد، ثم يعالج هو. التابع الجديد جاهز للحدث التالي. المعمل يعالج أربع مهام بثلاثة خيوط.",
           use=["تجمع خيوط على مصدر أحداث واحد.", "تقليل زمن تعيين قائد جديد."],
           avoid=["تنفيذ معقّد وطابور عادي يكفي.", "تعليق لو الترقية نسيت notify."],
           diagram="leader takes job → promote follower → handle",
           relations=[("Thread Pool", "conc-thread-pool"), ("Reactor", "conc-reactor")],
           lab=EXEC, demo="leader_followers",
           snippet="job = pending.popleft()\npromote()",
           tasks=["عدّ مين عالج 10 و20 و30 و40.", "أضف مهمة خامسة.", "اكتب فرقًا عن طابور عمال عادي."],
           questions=[("مين ينتظر الحدث؟", "القائد فقط."), ("التابع بيعمل إيه؟", "ينتظر الترقية."), ("ليهه الترقية قبل المعالجة؟", "عشان حد يبقى جاهز للحدث الجاي."), ("المعمل يعالج كام مهمة؟", "أربع.")]),
        _s(id="conc-rate-limiter", nav="Rate Limiter", title="Rate Limiter", subtitle="دلو رموز يبوّب الفوترة", icon="🪣", tone="amber",
           intent="سعة 3 ورموز تتجدد مع الساعة. خمس محاولات: ثلاث تنجح واثنتان ترفض، ثم تقدّم ساعتين فيرجع رمز. يحمي تابعًا بطيئًا. الساعة افتراضية.",
           use=["حد نداءات على بوابة دفع أو بريد.", "اختبار الرفض من غير نوم."],
           avoid=["حد من غير رد واضح للمتصل.", "ساعة حقيقية في اختبار هش."],
           diagram="capacity 3 → T T T F F → advance 2 → T",
           relations=[("Bulkhead", "conc-bulkhead"), ("Scheduler", "conc-scheduler")],
           lab=SAFE, demo="rate_limiter",
           snippet="""
decisions = [bucket.allow() for _ in range(5)]
bucket.advance(2)
            """,
           tasks=["اربط الرفض برسالة للخدمة.", "غيّر المعدل وانتبه للتجدد.", "قارن مع طابور محدود."],
           questions=[("أول ثلاث؟", "مقبولة."), ("بعدها؟", "رفض حتى يتجدد الرصيد."), ("بعد advance(2)؟", "قبول واحد لأن المعدل 1 في الوحدة."), ("ده قفل بيانات؟", "لا. بوابة مرور.")]),
        _s(id="conc-bulkhead", nav="Bulkhead", title="Bulkhead", subtitle="طابور الإشعار الممتلئ لا يوقف الفوترة", icon="🚢", tone="amber",
           intent="حواجز السفينة: عطل جزء ما يغرقش الباقي. طابور إشعارات سعته 1 يمتلئ، وطابور الفوترة لسه يقبل. الموارد معزولة.",
           use=["تبعيات مختلفة الموثوقية.", "منع البريد البطيء من تجميد الفاتورة."],
           avoid=["عزل بالاسم والخيط الفعلي مشترك.", "حاجز لكل دالة من غير قياس."],
           diagram="billing queue (accepts)\nnotify queue (full → reject)",
           relations=[("Rate Limiter", "conc-rate-limiter"), ("Thread Pool", "conc-thread-pool")],
           lab=SAFE, demo="bulkhead",
           snippet="notifications.put_nowait('mail-2')  # Full",
           tasks=["املأ الفوترة وتأكد إن الإشعار لسه مستقلًا.", "ارسم حاجزين لخدمتين.", "اكتب فشلًا لو الطابور مشترك."],
           questions=[("الاستعارة؟", "حواجز السفينة."), ("المعمل: الإشعار التاني؟", "يُرفض والطابور ممتلئ."), ("الفوترة؟", "لسه فيها عنصران."), ("فرقه عن المحدّد؟", "المحدد يبوّب المعدل. الحاجز يعزل الموارد.")]),
        _s(id="conc-monitor-object", nav="Monitor Object", title="Monitor Object", subtitle="دوال متزامنة وشرط على الرصيد", icon="🛡️", tone="amber",
           intent="BalanceMonitor يقفل كل عملية. السحب ينتظر على الشرط حتى الإيداع يكفي. ده قفل داخل العملية لحماية الذاكرة، مش version بين مستخدمين.",
           use=["كائن مشترك بين خيوط وحالته لازم تتسق.", "انتظار شرط على نفس القفل."],
           avoid=["نداء خارجي طويل وأنت ماسك القفل.", "اعتباره بديل Optimistic Offline Lock."],
           diagram="withdraw waits\ndeposit notifies\nbalance 50 - 40 = 10",
           relations=[("Guarded Suspension", "conc-guarded-suspension"), ("Optimistic Offline Lock", "pattern-optimistic-offline-lock"), ("Part 3 intro", "part3-concurrency")],
           lab=SAFE, demo="monitor_object",
           snippet="""
with self._cv:
    while self._cents < cents:
        self._cv.wait()
    self._cents -= cents
            """,
           tasks=["أضف خيط سحب قبل الإيداع وتأكد الناتج 10.", "اكتب ليه while حول wait.", "اشرح الفرق عن قفل العقد الأوفلاين بجملة."],
           questions=[("القفل على إيه؟", "على حالة الكائن في الذاكرة."), ("المعمل الناتج؟", "10 سنت بعد إيداع 50 وسحب 40."), ("ليهه Condition؟", "السحب يستنى الرصيد."), ("يحل تعارض مستخدمين على الصف؟", "لا.")]),
    ]
