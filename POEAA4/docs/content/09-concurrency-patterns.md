# أنماط التزامن (Concurrency Patterns)





# Optimistic Offline Lock

## المشكلة

نرجع لمثال الـ Order.

عندنا موظفين فتحوا نفس الطلب في نفس الوقت.

**سيناريو Lost Update**

الطلب رقم 101، والكمية الأصلية 10.

**الموظف الأول**

# 10

الكمية التي قرأها

يعدلها إلى 15

**الموظف الثاني**

# 10

الكمية التي قرأها

يعدلها إلى 20

---

**تسلسل الحفظ**

```plain text
Database  <---  Save: Quantity = 15  <---  Employee 1

Database  <---  Save: Quantity = 20  <---  Employee 2
```

(Lost Update)

التعديل الأول اختفى، وأصبحت الكمية 20 بدلًا من اكتشاف التعارض.

المشكلة إن الموظف الثاني مش عارف إن حد عدّل البيانات بعد ما قرأها.

إحنا محتاجين نكتشف إن البيانات اتغيرت قبل ما نسمح بالحفظ.

## الفكرة والحل

فكرة **Optimistic Offline Lock** إننا نفترض إن التعارضات مش بتحصل كثيرًا، وبالتالي نسمح لأكثر من مستخدم يقرأ ويعدل نفس البيانات بدون حجزها.

لكن عند الحفظ، نتحقق إن البيانات لم تتغير منذ لحظة قراءتها.

لو اتغيرت، نرفض الحفظ ونبلغ المستخدم بوجود Conflict.

أشهر طريقة لتنفيذ الفكرة هي استخدام **Version Number**.

كل Record عنده Version:

```plain text
Order ID = 101
Quantity = 10
Version  = 1
```

لما المستخدم يقرأ البيانات، يحتفظ بالـ Version اللي قرأه.

وعند الحفظ، نقارن الـ Version الحالي في قاعدة البيانات بالـ Version اللي المستخدم قرأه.

- لو متساويين: نسمح بالتعديل ونزيد Version.
- لو مختلفين: نرفض التعديل لأن فيه تغيير حصل بعد القراءة.

**Optimistic Offline Lock**

**قبل التعديل**

```plain text
Database Version = 1
User A Version   = 1
User B Version   = 1
```

---

**الموظف الأول يحفظ**

```plain text
Database Version = 1
User A Version   = 1

Update succeeds
Database Version = 2
```

(First Update Accepted)

---

**الموظف الثاني يحفظ**

```plain text
Database Version = 2
User B Version   = 1

2 != 1
```

(Concurrency Conflict)

النظام يرفض التعديل بدل ما يسمح بـ Lost Update.

وبالاتجاه من اليمين للشمال:

```plain text
Database  <---  Version Check  <---  Save Request  <---  User
```

## مثال

هنستخدم Version Column.

### أولًا: تصميم الجدول

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);
```

البيانات:

```plain text
id | quantity | version
---|----------|--------
1  | 10       | 1
```

### ثانيًا: قراءة البيانات

```python
def get_order(cursor, order_id):

    cursor.execute(
        """
        SELECT id, quantity, version
        FROM orders
        WHERE id = %s
        """,
        (order_id,)
    )

    return cursor.fetchone()
```

المستخدم هيقرأ:

```python
{
    "id": 1,
    "quantity": 10,
    "version": 1
}
```

### ثالثًا: الحفظ مع التحقق من Version

```python
def update_order(
    cursor,
    order_id,
    new_quantity,
    expected_version
):

    cursor.execute(
        """
        UPDATE orders
        SET
            quantity = %s,
            version = version + 1
        WHERE
            id = %s
            AND version = %s
        """,
        (
            new_quantity,
            order_id,
            expected_version
        )
    )

    if cursor.rowcount == 0:
        raise Exception(
            "Concurrency Conflict"
        )
```

ركز في الجزء ده:

```sql
WHERE id = %s AND version = %s
```

إحنا مش بنعمل Update لمجرد إن الـ Record موجود.

إحنا بنعمل Update بشرط إن الـ Version ما زال هو نفسه اللي المستخدم قرأه.

والعملية كلها عبارة عن SQL Statement واحدة، وبالتالي التحقق والتعديل بيحصلوا بشكل Atomic على مستوى قاعدة البيانات.

### رابعًا: السيناريو

الموظف الأول:

```python
update_order(
    cursor,
    order_id=1,
    new_quantity=15,
    expected_version=1
)
```

النتيجة:

```plain text
quantity = 15
version  = 2
```

الموظف الثاني:

```python
update_order(
    cursor,
    order_id=1,
    new_quantity=20,
    expected_version=1
)
```

النتيجة:

```plain text
Concurrency Conflict
```

لأن Version الحالي أصبح 2، بينما الموظف الثاني بيحاول الحفظ باستخدام Version قديم وهو 1.

**ملحوظة مهمة:** لازم عملية التعديل تكون داخل Transaction، ولازم نتعامل مع Conflict بشكل مناسب، مثل إعادة تحميل البيانات ومراجعة التعديلات. مينفعش نعيد تنفيذ نفس التعديل القديم تلقائيًا بدون فهم أثره.

## 4. هل Version Number هي الطريقة الوحيدة؟

لا.

فيه أكثر من طريقة لتنفيذ Optimistic Locking:

1. **Version Number:** رقم يزيد مع كل تعديل.
1. **Timestamp:** مقارنة آخر وقت تعديل.
1. **Hash / Original Values:** مقارنة القيم القديمة بالقيم الحالية.

لكن Version Number غالبًا أوضح وأكثر أمانًا من الاعتماد على Timestamp، خصوصًا لو دقة الوقت أو تزامنه مش مضمونين.

## أقرب GoF Pattern

هل Optimistic Offline Lock له GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern مطابق له.**

لكن ممكن تلاحظ تشابهات جزئية:

### Observer

ممكن تستخدم Observer لإبلاغ المستخدم إن البيانات اتغيرت.

لكن الفرق:

- Observer هدفه نشر الإشعارات عند حدوث تغييرات.
- Optimistic Offline Lock هدفه منع الكتابة بناءً على نسخة قديمة.

### State

ممكن يكون عندك حالة للـ Record أو عملية الحفظ، مثل:

- Unchanged
- Modified
- Conflict

لكن State مش هو Optimistic Offline Lock.

الـ Optimistic Offline Lock آلية لإدارة التزامن والتحقق من صلاحية التعديل، وليس Behavioral Pattern من GoF.

## 6. علاقته بـ Application Architecture

Optimistic Offline Lock مش بديل عن Layered أو Clean Architecture.

هو Concurrency Pattern ممكن نستخدمه داخل أي Application Architecture تحتاج حماية التعديلات المتزامنة.

مثلًا:

```plain text
Database  <---  Repository  <---  Application Service  <---  Controller  <---  User
```

وقت الحفظ، الـ Repository أو Data Access Layer ينفذ عملية الـ Version Check والـ Conditional Update.

وممكن الـ Application Service يتعامل مع Conflict ويقرر إزاي يرجع النتيجة للمستخدم.

## علاقته بالعمارة

في Clean Architecture ممكن يكون التنفيذ موزع كالتالي:

```plain text
Database  <---  Repository  <---  Use Case  <---  Input Adapter  <---  User
```

- Input Adapter يستقبل التعديل والـ Version المتوقع.
- Use Case ينسق عملية التحديث.
- Repository ينفذ الـ Conditional Update.
- Database تضمن Atomicity للشرط والتعديل.

لو حصل Conflict، الـ Repository يرجع نتيجة واضحة أو يرفع Exception مناسبة، والـ Use Case يحدد طريقة التعامل معها.

والـ Domain ممكن يحتوي على قواعد العمل، لكنه مش محتاج يعرف تفاصيل SQL أو كيفية تنفيذ Version Check.

## 8. علاقته بـ DDD

في DDD، ممكن نستخدم Optimistic Concurrency Control لحماية Aggregate من التعديل بناءً على نسخة قديمة.

تخيل إن عندك Order Aggregate.

موظفان حمّلا نفس الـ Aggregate، وكل واحد عمل تعديل مستقل.

عند حفظ الأول، يتغير الـ Version.

وعند محاولة حفظ الثاني، Repository يكتشف إن الـ Version اختلف ويرفض الحفظ.

ده مهم للحفاظ على **Aggregate Invariants** ومنع تعديل قديم من الكتابة فوق حالة أحدث.

لكن لازم نفرق بين:

- Version الخاص بالتزامن.
- Business Status الخاص بالـ Order.

مثلًا version = 5 مش معناه إن الطلب في الحالة الخامسة؛ ده مجرد رقم يمثل نسخة البيانات.

## علاقته بأودو

دي نقطة مهمة بالنسبة لطبيعة أنظمة ERP.

في PostgreSQL عندنا MVCC، وده بيسمح للـ Transactions بقراءة نسخ متسقة من البيانات حسب مستوى العزل.

لكن **MVCC مش هو نفسه Optimistic Offline Lock**.

الفرق:

- MVCC ينظم رؤية النسخ والتزامن على مستوى قاعدة البيانات.
- Optimistic Offline Lock يحمي Business Transaction طويلة نسبيًا من الكتابة فوق تعديلات مستخدم آخر.

يعني وجود MVCC مش معناه تلقائيًا إن عندك حماية كاملة من Lost Updates الناتجة عن تعديل المستخدم لنسخة قديمة.

في Odoo، لو عندك عملية طويلة بين فتح الفورم وحفظه، لازم تفكر في كيفية اكتشاف التعديلات المتزامنة، خصوصًا لو فيه Custom Logic أو API أو عمليات خارج دورة الحفظ المعتادة.

ولا تفترض إن كل موديلات Odoo عندها Version Column مخصص بنفس آلية المثال؛ آلية الحماية لازم تتحدد وتُنفذ حسب تصميم العملية.

## 10. إمتى نستخدم Optimistic Offline Lock؟

استخدمه لما:

- عدد التعارضات المتوقع قليل.
- المستخدمون ممكن يفتحوا نفس البيانات لفترات طويلة.
- مش عايز تحجز البيانات أثناء عمل المستخدم.
- محتاج تمنع Lost Updates.
- تقدر تطلب من المستخدم مراجعة التعديلات عند حدوث Conflict.

لكن لو التعارضات كثيرة جدًا، أو تكلفة رفض العملية وإعادتها عالية، ممكن تفكر في Pessimistic Offline Lock.

---

## الخلاصة
**Optimistic Offline Lock**

- يسمح لأكثر من مستخدم بتعديل نفس البيانات مبدئيًا.
- لا يحجز الـ Record أثناء فترة عمل المستخدم.
- يتحقق من عدم تغير البيانات عند الحفظ.
- أشهر تطبيق له Version Number.
- يمنع Lost Update عن طريق رفض التعديلات القديمة.
- مناسب عندما تكون التعارضات قليلة نسبيًا.

**النمط التالي: Pessimistic Offline Lock.**

وهنا هنقلب الفكرة تمامًا: بدل ما نسمح للجميع بالتعديل ونكتشف التعارض عند الحفظ، هنحاول نحجز البيانات من البداية حتى لا يعدلها مستخدم آخر في نفس الوقت.


# Pessimistic Offline Lock

بعد ما فهمنا **Optimistic Offline Lock**، هننتقل لفكرة عكسية تقريبًا.

في Optimistic كنا بنسمح لأكثر من مستخدم يشتغل على نفس البيانات، ونكتشف التعارض وقت الحفظ.

أما هنا، فهنحاول نمنع التعارض من البداية عن طريق **حجز البيانات (Locking)**.

## المشكلة

تخيل عندنا نظام ERP، وموظف فاتح أمر بيع (Sales Order) وبيعدّل فيه.

في نفس الوقت، موظف تاني فتح نفس الأمر وعايز يعدّل فيه.

إحنا عايزين نضمن إن موظف واحد فقط هو اللي يقدر يعدّل الأمر في الوقت ده.

المشكلة إننا مش بنتكلم عن Database Transaction قصيرة؛ إحنا بنتكلم عن عملية مستخدم ممكن تستمر عدة دقائق.

مينفعش نفتح Database Transaction ونسيبها مفتوحة طول الوقت؛ ده ممكن يسبب مشاكل في الـ Locks والـ Connections والـ Transaction Management.

إذن محتاجين Lock مستقل عن عمر الـ Database Transaction.

## الفكرة والحل

فكرة **Pessimistic Offline Lock** إن المستخدم يحجز الـ Business Object قبل ما يبدأ تعديله.

لو الحجز نجح، يقدر يكمل شغله.

لو مستخدم تاني حاول يحجز نفس الـ Object، النظام يرفض أو يجعله ينتظر حسب تصميم النظام.

التدفق من اليمين للشمال:

```plain text
User A  <---  Acquire Lock  <---  Order 101
                                  |
User B  <---  Lock Rejected  <---  Order 101
```

بمعنى:

1. المستخدم الأول يطلب حجز Order 101.
1. النظام يمنحه الـ Lock.
1. المستخدم الأول يعدّل ويحفظ.
1. المستخدم الأول يحرر الـ Lock.
1. المستخدم الثاني يقدر يحجز الطلب بعد كده.

**مثال توضيحي**

**Order #101** (Locked)

---

الموظف الأول (Lock Owner)

الموظف الثاني (Access Denied)

الحجز هنا على مستوى الـ Business Object، وليس مجرد قفل SQL Transaction مفتوحة طوال فترة عمل الموظف.

## مثال

هننفذ مثال مبسط باستخدام جدول منفصل لإدارة الأقفال.

### أولًا: تصميم الجدول

```sql
CREATE TABLE offline_locks (
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    PRIMARY KEY (resource_type, resource_id)
);
```

الجدول ده بيحدد:

- نوع الـ Object المحجوز.
- الـ ID الخاص به.
- المستخدم اللي حجزه.
- وقت انتهاء الحجز.

### ثانيًا: الحصول على Lock

```python
def acquire_lock(
    cursor,
    resource_type,
    resource_id,
    owner_id,
    expires_at
):
    cursor.execute(
        """
        INSERT INTO offline_locks (
            resource_type,
            resource_id,
            owner_id,
            expires_at
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (
            resource_type,
            resource_id,
            owner_id,
            expires_at
        )
    )

    return cursor.rowcount == 1
```

لو المستخدم الأول حجز الطلب، الـ INSERT ينجح.

لو المستخدم الثاني حاول يحجز نفس الطلب، الـ Primary Key يمنع إنشاء Lock آخر لنفس الـ Resource.

### ثالثًا: تحرير الـ Lock

```python
def release_lock(
    cursor,
    resource_type,
    resource_id,
    owner_id
):
    cursor.execute(
        """
        DELETE FROM offline_locks
        WHERE resource_type = %s
          AND resource_id = %s
          AND owner_id = %s
        """,
        (
            resource_type,
            resource_id,
            owner_id
        )
    )
```

لاحظ إننا بنتأكد من owner_id قبل الحذف، عشان مستخدم ما يقدرش يحرر Lock مملوك لمستخدم تاني.

**ملحوظة مهمة:** المثال ده توضيحي، ومحتاج إدارة صحيحة للـ Transactions، وانتهاء الصلاحية، وتجديد الحجز، والتحقق من ملكية الـ Lock قبل كل عملية حفظ. مجرد وجود expires_at في الجدول مش كفاية لتطبيق انتهاء الحجز تلقائيًا.

### رابعًا: إيه اللي يحصل لو المستخدم قفل الصفحة بدون ما يحرر الـ Lock؟

هنا بنواجه مشكلة مهمة جدًا.

تخيل المستخدم حجز الطلب، وبعدها:

- قفل المتصفح.
- الإنترنت فصل.
- الجهاز عمل Restart.
- المستخدم نسي يحرر الحجز.

الطلب ممكن يفضل محجوز للأبد!

عشان كده بنستخدم مفهوم اسمه **Lease / Lock Expiration**.

يعني الـ Lock بيكون له مدة صلاحية.

مثلًا:

```plain text
Lock Owner = User A
Expires At = 10:30
```

لو المستخدم لم يجدد الحجز قبل 10:30، النظام يسمح بانتهاء الـ Lock.

وممكن المستخدم يجدد الحجز دوريًا عن طريق **Heartbeat**.

```plain text
User A  <---  Renew Lock  <---  Lock Manager
```

لكن فيه مشكلة إضافية: ماذا لو انتهى الحجز القديم، وحصل مستخدم آخر على حجز جديد، وبعدها المستخدم القديم حاول الحفظ؟

هنا نحتاج نتأكد إن المستخدم القديم لم يعد يملك صلاحية التعديل.

في الأنظمة الأكثر تعقيدًا ممكن نستخدم **Fencing Token**، وهو رقم متزايد مع كل Lock جديد، بحيث ترفض طبقة التخزين أي عملية قادمة من صاحب Lock قديم.

مثلًا:

```plain text
User A gets token = 10
Lock expires

User B gets token = 11

User A tries to save with token = 10
                         |
                         v
                    Rejected
```

دي نقطة مهمة جدًا في الأنظمة الموزعة؛ لأن انتهاء الـ Lock وحده لا يضمن إن صاحب الحجز القديم توقف فعلًا عن تنفيذ العمليات.

---

## أقرب GoF Pattern

هل عندنا GoF Pattern مطابق لـ Pessimistic Offline Lock؟

**لا، مفيش نظير مباشر.**

لكن فيه تشابه في الفكرة مع:

**1. Monitor Object**

- Monitor Object بينظم الوصول المتزامن إلى Object داخل عملية أو بيئة تشغيل مشتركة.
- Pessimistic Offline Lock ينظم وصول المستخدمين إلى Business Object خلال Business Transaction طويلة.

الفرق إن Monitor Object غالبًا مرتبط بالتزامن داخل الذاكرة، بينما Pessimistic Offline Lock مرتبط بالتزامن بين مستخدمين وعمليات مستقلة.

**2. Proxy**

ممكن تستخدم Proxy لمنع الوصول إلى Object غير متاح أو غير محجوز للمستخدم.

لكن Proxy مجرد وسيلة لتنظيم الوصول، وليس آلية الـ Offline Lock نفسها.

إذن التشابه هنا في بعض آليات التنفيذ، مش في الـ Intent الأساسي.

---

## 5. علاقته بـ Application Architecture

زي ما اتفقنا، ده مش Application Architecture مستقل.

ممكن تستخدمه داخل Layered Architecture أو Clean Architecture.

مثال:

```plain text
User  <---  Controller  <---  Application Service
                                  |
                                  v
                            Lock Manager
                                  |
                                  v
                              Database
```

الـ Application Service ينسق العملية:

1. يطلب حجز الـ Object.
1. ينفذ الـ Business Operation.
1. يحفظ التعديلات.
1. يحرر الحجز.

والـ Lock Manager مسؤول عن تفاصيل إدارة الحجز.

مهم نفصل بين مسؤولية إدارة الحجز ومسؤولية تنفيذ الـ Business Logic.

## علاقته بالعمارة

في Clean Architecture ممكن نعرّف Interface لإدارة الأقفال:

```python
from typing import Protocol

class LockManager(Protocol):

    def acquire(self, resource_id: int, owner_id: int):
        ...

    def release(self, resource_id: int, owner_id: int):
        ...
```

والـ Use Case يعتمد على الـ Interface بدل الاعتماد المباشر على PostgreSQL.

```python
class UpdateOrder:

    def __init__(self, lock_manager, order_repository):
        self.lock_manager = lock_manager
        self.order_repository = order_repository

    def execute(self, order_id, user_id, quantity):

        acquired = self.lock_manager.acquire(
            order_id,
            user_id
        )

        if not acquired:
            raise Exception("Order is already locked")

        try:
            order = self.order_repository.get(order_id)
            order.update_quantity(quantity)

            self.order_repository.save(order)

        finally:
            self.lock_manager.release(order_id, user_id)
```

ده مثال مبسط، لكنه يوضح فصل الـ Policy عن الـ Mechanism.

في تطبيق حقيقي لازم كمان نراعي إن الـ Lock يفضل محميًا خلال عملية الحفظ، وإن فشل الحفظ أو انقطاع الاتصال لا يترك النظام في حالة غير متسقة.

## 7. علاقته بـ DDD

ممكن نستخدم Pessimistic Offline Lock مع الـ Aggregate.

تخيل عندك:

```plain text
Order Aggregate
    |
    +-- Order Lines
    |
    +-- Customer Reference
```

لو عندك عملية تعديل حساسة على الـ Order، ممكن تحجز الـ Aggregate كله بحيث تمنع مستخدمًا آخر من إجراء عملية متعارضة عليه.

لكن خد بالك:

**الـ Lock مش جزء من الـ Aggregate بالضرورة.**

هو آلية لإدارة التزامن، وممكن تكون مسؤولية Application Layer أو Infrastructure Layer.

كمان لازم تحدد نطاق الحجز بناءً على قواعد العمل، مش لمجرد إن Objects مرتبطة ببعض.

## علاقته بأودو

في Odoo، تخيل إن عندك عملية تخصيص مخزون أو معالجة أمر بيع، وفيه أكثر من مستخدم بيحاول يعدل نفس الـ Business Resource.

ممكن تحتاج Lock منطقي على مستوى العملية، لكن لازم تفرق بين حاجتين:

- PostgreSQL SELECT FOR UPDATE: قفل على مستوى Database Transaction، وينتهي مع انتهاء الـ Transaction.
- Pessimistic Offline Lock: حجز يستمر خلال فترة عمل المستخدم، حتى لو كل عملية Database Transaction انتهت بالفعل.

فمش كل استخدام لـ SELECT FOR UPDATE يعتبر Pessimistic Offline Lock.

كمان لو هتطبق Lock Manager مخصص في Odoo، لازم تراعي تعدد الـ Workers، وملكية الحجز، وانتهاء الصلاحية، وعدم السماح بتعديل البيانات بعد فقدان الحجز.

---

## 9. مقارنة Optimistic وPessimistic

خلينا نثبت الفرق؛ لأن النمطين بيتلخبطوا بسهولة.

المقارنة	Optimistic	Pessimistic
الفكرة	اكتشاف التعارض	منع التعارض مسبقًا
الحجز	لا يوجد حجز مسبق	يوجد حجز
تعدد المستخدمين	مسموح مبدئيًا	مستخدم واحد يملك الحجز
اكتشاف المشكلة	عند الحفظ	عند طلب الحجز
التكلفة	تكلفة التعامل مع Conflict	تكلفة إدارة Lock
الأنسب	تعارضات قليلة	تعارضات متكررة أو مكلفة

## 10. إمتى نستخدم Pessimistic Offline Lock؟

استخدمه لما:

- التعارضات متكررة.
- تكلفة حدوث التعارض عالية.
- إعادة تنفيذ العملية صعبة.
- محتاج تضمن إن مستخدم واحد فقط يعدل موردًا معينًا في نفس الوقت.

لكن تجنبه لو الحجز هيعطل المستخدمين باستمرار، أو لو المستخدمين ممكن ينسوا تحرير الأقفال، أو لو نظامك موزع ومش عندك آلية موثوقة لإدارة انتهاء الحجز.

---


# Coarse-Grained Lock

النمط ده مرتبط جدًا باللي فات، لكن فيه اختلاف مهم لازم نفهمه.

في **Pessimistic Offline Lock** كنا بنجاوب عن السؤال:

> إزاي أمنع أكثر من مستخدم من تعديل نفس الـ Business Object في نفس الوقت؟

أما في **Coarse-Grained Lock** فالسؤال مختلف:

> إيه حجم أو نطاق الـ Object اللي المفروض أحجزه أصلًا؟

يعني المشكلة هنا مش مجرد إزاي نعمل Lock، لكن **نحجز إيه بالضبط؟**

## المشكلة

تخيل عندنا نظام مبيعات، وعندنا Order بالشكل ده:

```plain text
Order #100
    |
    +--- Order Line #1
    |
    +--- Order Line #2
    |
    +--- Order Line #3
    |
    +--- Payment
```

موظف بيعدل Order Line #1، وموظف تاني بيعدل Order Line #2.

لو عملنا Lock لكل Object بشكل مستقل، الاتنين ممكن يشتغلوا في نفس الوقت.

لكن ماذا لو تعديل الـ Order Line الأول أثر على إجمالي الطلب، وتعديل الثاني أثر على نفس الإجمالي؟

ممكن نواجه مشاكل في اتساق البيانات (Consistency).

ولو قررنا نحجز كل Object لوحده، هنحتاج ندير مجموعة Locks:

- Lock للـ Order.
- Lock لكل Order Line.
- Lock للـ Payment.
- Lock لأي Object مرتبط بالعملية.

وده ممكن يؤدي إلى تعقيد كبير في إدارة الأقفال.

## الفكرة والحل

بدل ما نحجز كل Object بشكل مستقل، بنحدد **مجموعة Objects مترابطة** ونعتبرها وحدة واحدة للحجز.

يعني بدل:

```plain text
Line #1  <---  Lock A

Line #2  <---  Lock B

Payment  <---  Lock C

Order    <---  Lock D
```

نحجز الـ Order بالكامل:

```plain text
Order #100
    |
    +--- Order Line #1
    |
    +--- Order Line #2
    |
    +--- Order Line #3
    |
    +--- Payment

          ^
          |
     One Shared Lock
```

وبالترتيب من اليمين للشمال:

```plain text
Order + Lines + Payment  <---  One Coarse-Grained Lock
```

بالتالي أي مستخدم يريد تعديل جزء من المجموعة المحجوزة لازم يحصل على نفس الـ Lock.

الفكرة الأساسية هي تقليل عدد الأقفال التي يجب إدارتها، عن طريق توسيع نطاق القفل.

**مثال: Order #100**

Order (Locked)

---

Order Line #1 (Protected)

Order Line #2 (Protected)

Payment (Protected)

الـ Lock واحد على مستوى Order، لكن تأثيره يمتد إلى العمليات التي تعدّل الأجزاء التابعة له.

## مثال

هنفترض إن عندنا Order يحتوي على مجموعة Order Lines.

بدل ما نحجز كل Line، هنحجز الـ Order نفسه.

```python
class LockManager:

    def __init__(self):
        self.locks = {}

    def acquire(self, resource_id, owner_id):
        if resource_id in self.locks:
            return False

        self.locks[resource_id] = owner_id
        return True

    def release(self, resource_id, owner_id):
        if self.locks.get(resource_id) != owner_id:
            return False

        del self.locks[resource_id]
        return True
```

استخدامه:

```python
locks = LockManager()

# User A locks Order 100
locks.acquire("order:100", "user_a")

# User B wants to update Line 1
can_update = locks.acquire("order:100", "user_b")

print(can_update)  # False
```

لاحظ إننا لم نستخدم:

```python
locks.acquire("order_line:1", "user_b")
```

لأننا قررنا إن نطاق الحجز هو الـ Order بالكامل.

لكن فيه شرط مهم جدًا:

**كل العمليات التي تعدّل أجزاء الـ Order لازم تحترم نفس Lock.**

لو فيه API أو Background Job بيعدل الـ Order Lines من غير ما يتحقق من Lock الـ Order، يبقى الحماية غير مكتملة.

المثال هنا تعليمي فقط؛ وفي الإنتاج نحتاج Lock Manager مشتركًا بين كل الـ Workers، مع تخزين ذري للأقفال وانتهاء صلاحيتها.

---

## أقرب GoF Pattern

هل Coarse-Grained Lock له GoF Pattern مطابق؟

**لا يوجد GoF Pattern مطابق له.**

لكن ممكن نلاحظ تشابهًا جزئيًا مع:

**Facade Pattern**

الـ Facade بيقدم واجهة موحدة للتعامل مع مجموعة من الأنظمة أو الكائنات الفرعية.

أما Coarse-Grained Lock فبيتعامل مع مجموعة Objects كنطاق واحد للحجز.

الفرق:

- Facade هدفه تبسيط واجهة الاستخدام.
- Coarse-Grained Lock هدفه تقليل تعقيد إدارة التزامن عن طريق توسيع نطاق الحجز.

إذن التشابه في التعامل مع مجموعة Objects من خلال نقطة واحدة، وليس في الـ Intent.

---

## 5. علاقته بـ Application Architecture

النمط ده مش Architecture مستقلة، لكنه ممكن يظهر داخل أي Application Architecture.

مثلًا في Layered Architecture:

```plain text
User  <---  Controller  <---  Application Service
                                  |
                                  v
                              Lock Manager
                                  |
                                  v
                              Order Scope
```

الـ Application Service يطلب حجز الـ Order بالكامل قبل تنفيذ العملية.

ومش مهم إذا كان النظام Layered أو Clean أو Hexagonal؛ المهم إن كل عمليات التعديل على نفس النطاق تحترم سياسة الحجز.

## علاقته بالعمارة

في Clean Architecture ممكن نعرّف Port مسؤول عن الحجز:

```python
class OrderLock(Protocol):

    def acquire(self, order_id: int, user_id: int) -> bool:
        ...

    def release(self, order_id: int, user_id: int) -> bool:
        ...
```

الـ Use Case يتعامل مع OrderLock بدل تفاصيل قاعدة البيانات.

```plain text
Database Lock Implementation
             |
             v
       OrderLock Port
             ^
             |
        Use Case
             ^
             |
        Controller
```

لاحظ اتجاه الاعتماد في الرسم من اليمين للشمال:

```plain text
Controller  --->  Use Case  --->  OrderLock Interface
```

والـ Infrastructure هي اللي تنفذ الـ Interface.

المهم هنا إن Clean Architecture لا تفرض علينا نطاق القفل؛ تحديد النطاق قرار متعلق بالـ Business Requirements.

---

## 7. علاقته بـ DDD

هنا عندنا ارتباط مهم جدًا.

في DDD عندنا مفهوم اسمه **Aggregate**.

الـ Aggregate عبارة عن مجموعة Objects مرتبطة ببعض، وبتتعامل مع قواعد اتساق محددة من خلال Aggregate Root.

مثلًا:

```plain text
Order (Aggregate Root)
    |
    +--- OrderLine
    |
    +--- OrderLine
    |
    +--- OrderLine
```

ممكن يكون الـ Order هو نطاق الحجز المناسب، لأن التعديلات على الـ Order Lines لازم تحافظ على قواعد الـ Order.

لكن خلي بالك من نقطة دقيقة:

**Coarse-Grained Lock مش هو نفسه Aggregate.**

- Aggregate مفهوم في DDD لتحديد حدود الاتساق والتحكم في التعديلات.
- Coarse-Grained Lock نمط لإدارة التزامن على نطاق مجموعة Objects.

ممكن نستخدم حدود الـ Aggregate لتحديد نطاق الـ Lock، لكن مش شرط يكونوا متطابقين في كل نظام.

كمان مش كل Object مرتبط بالـ Order لازم يكون جزءًا من نفس الـ Aggregate أو يدخل في نفس الحجز.

---

## علاقته بأودو

خلينا ناخد مثال من Odoo.

عندنا:

- sale.order
- sale.order.line

لو قررنا إن تعديل أي sale.order.line لازم يتم في ظل حجز الـ sale.order الأب، يبقى ممكن نستخدم الـ Order ID باعتباره Lock Resource.

```plain text
sale.order
    |
    +--- sale.order.line
    |
    +--- sale.order.line
    |
    +--- sale.order.line

        One Lock on sale.order
```

أي عملية تعديل على الـ Lines لازم تتحقق من حجز الـ Order.

لكن لازم ننتبه:

- Odoo ORM مش هيفرض علينا السياسة دي تلقائيًا.
- لازم نغطي كل مسارات التعديل: UI، RPC، API، Cron، وعمليات الـ Background.
- قفل الـ Order لا يمنع تلقائيًا أي كود يكتب مباشرة على الـ Lines.
- لا نحتاج بالضرورة إلى قفل كل الـ Database Rows؛ ممكن نستخدم Lock منطقيًا مستقلًا عن Database Row Locks.

---

## 9. عيوب ومميزات Coarse-Grained Lock

**المميزات:**

- عدد أقفال أقل.
- إدارة أبسط للتزامن.
- يقلل تعارضات التعديلات داخل مجموعة مترابطة.
- مناسب عندما تكون Objects مرتبطة بقواعد اتساق مشتركة.

**العيوب:**

- ممكن يمنع مستخدمًا من تعديل جزء لا يتعارض فعليًا مع تعديل مستخدم آخر.
- يقلل مستوى الـ Concurrency.
- ممكن يسبب انتظارًا غير ضروري.
- اختيار نطاق كبير جدًا يجعل النظام أقل قابلية للتوسع.

مثال:

لو موظف بيعدل عنوان Order، وموظف تاني بيعدل ملاحظة داخل Order Line، ممكن ما يكونش فيه تعارض حقيقي بين العمليتين، لكن الـ Coarse-Grained Lock هيمنعهم من العمل معًا.

وده هو الـ Trade-off الأساسي.

---

## 10. الفرق بين الأنماط الثلاثة حتى الآن

النمط	السؤال الذي يجيب عنه
Optimistic Offline Lock	إزاي أكتشف التعارض عند الحفظ؟
Pessimistic Offline Lock	إزاي أحجز المورد قبل التعديل؟
Coarse-Grained Lock	إيه نطاق المورد اللي هحجزه؟

---

# النمط الرابع والأخير: Implicit Lock

هنا هنتكلم عن مشكلة مختلفة شوية:

لو عندنا Locking Strategy، هل لازم كل Developer يفتكر بنفسه إنه يعمل Acquire وRelease في كل عملية؟

ولا ممكن نخلي الـ Lock يحصل بشكل ضمني من خلال آلية موجودة في النظام؟

وده موضوع **Implicit Lock**.


# Implicit Lock

وصلنا لآخر نمط في مجموعة **Offline Concurrency Patterns**.

في الأنماط السابقة كنا بنحدد مين يحجز الـ Object، وإمتى، وإيه نطاق الحجز.

لكن هنا عندنا سؤال مختلف:

**هل لازم الـ Developer يطلب الـ Lock بنفسه في كل عملية؟ ولا ممكن النظام يدير عملية الحجز بشكل ضمني؟**

وده جوهر Implicit Lock.

## المشكلة

تخيل إن عندك نظام بيستخدم Pessimistic Offline Lock.

كل مرة Developer يكتب Use Case لتعديل Order، لازم يفتكر يعمل:

1. Acquire Lock.
1. ينفذ التعديلات.
1. Release Lock.

مثال:

```python
def update_order(order_id, user_id):

    lock_manager.acquire(order_id, user_id)

    try:
        order = repository.get(order_id)
        order.update()
        repository.save(order)

    finally:
        lock_manager.release(order_id, user_id)
```

المشكلة إن عندك عشرات أو مئات العمليات اللي بتتعامل مع نفس الـ Objects.

ممكن Developer ينسى يعمل Acquire Lock في عملية معينة.

أو يعمل Lock على الـ Order وينسى إن فيه عملية تانية بتعدل نفس الـ Order من خلال مسار مختلف.

وبالتالي سياسة التزامن مش مطبقة بشكل موحد.

## الفكرة والحل

بدل ما كل Developer يكون مسؤول عن طلب الـ Lock يدويًا، نخلي النظام يتولى تحديد الأقفال المطلوبة والحصول عليها ضمن آلية تنفيذ العملية.

يعني الـ Lock يحصل **Implicitly** بدل ما يكون استدعاءً صريحًا في كل Use Case.

مثال توضيحي:

```plain text
User Request  <---  Application Service
                          |
                          v
                    Lock Manager
                          |
                          v
                    Business Logic
```

الـ Application Service أو آلية وسيطة تعرف الموارد المطلوب حجزها، وتدير الحجز تلقائيًا.

لكن خد بالك: كلمة Implicit مش معناها إن النظام بيخمن لوحده كل الـ Objects اللي محتاج يقفلها.

لازم يكون فيه مصدر واضح للمعلومات، مثل:

- Metadata.
- Mapping بين أنواع العمليات والموارد.
- Unit of Work.
- Transaction Context.
- قواعد محددة في الـ Framework.

الفكرة إن الـ Developer مش مضطر يكرر تفاصيل الحجز في كل مكان.

## مثال

هنستخدم Decorator لتوضيح الفكرة.

بدل ما نكتب Acquire وRelease داخل كل Use Case، هنعرّف الـ Lock كـ Metadata على العملية.

```python
from functools import wraps

def requires_lock(resource_arg):

    def decorator(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):

            resource_id = kwargs[resource_arg]
            owner_id = kwargs["user_id"]

            acquired = self.lock_manager.acquire(
                resource_id,
                owner_id
            )

            if not acquired:
                raise Exception("Resource is locked")

            try:
                return func(self, *args, **kwargs)

            finally:
                self.lock_manager.release(
                    resource_id,
                    owner_id
                )

        return wrapper

    return decorator
```

استخدامه:

```python
class OrderService:

    def __init__(self, lock_manager, repository):
        self.lock_manager = lock_manager
        self.repository = repository

    @requires_lock("order_id")
    def update_order(self, order_id, user_id):

        order = self.repository.get(order_id)

        order.update()

        self.repository.save(order)
```

لاحظ الفرق.

**Explicit Locking:**

```python
lock_manager.acquire(...)
try:
    # Business Logic
finally:
    lock_manager.release(...)
```

**Implicit Locking:**

```python
@requires_lock("order_id")
def update_order(...):
    # Business Logic
```

الـ Decorator بيدير عملية الحجز والتحرير بدل ما نكررها داخل الـ Business Logic.

المثال تعليمي: في تطبيق حقيقي لازم نتأكد من إن الـ Lock يمتد طوال الـ Business Transaction المطلوبة، وليس فقط طوال تنفيذ HTTP Request قصير، مع دعم الـ Lease وملكية الحجز والتعامل مع فشل العملية.

---

## أقرب GoF Pattern

مفيش GoF Pattern مطابق تمامًا لـ Implicit Lock.

لكن عندنا تشابهات مهمة:

**1. Proxy Pattern**

الـ Proxy ممكن يعترض الوصول إلى Object وينفذ عمليات إضافية قبل تمرير الطلب.

```plain text
Client  <---  Proxy  <---  Real Object
                  |
                  +--- Acquire Lock
```

لكن Proxy هدفه التحكم في الوصول إلى Object، بينما Implicit Lock هدفه تطبيق سياسة الحجز بدون تكرار طلبها في كل عملية.

**2. Decorator Pattern**

الـ Decorator بيضيف مسؤولية إضافية حول تنفيذ العملية الأصلية.

وده أقرب للمثال اللي كتبناه، لأننا أضفنا Locking Behavior حول الـ Use Case.

لكن برضه مش نفس الـ Intent.

الـ Decorator وسيلة تنفيذ، مش نمط التزامن نفسه.

## 5. علاقته بـ Application Architecture

Implicit Lock مش Architecture مستقلة.

هو أسلوب لتطبيق سياسة التزامن داخل الـ Application Architecture.

ممكن تلاقيه في:

- Layered Architecture.
- Clean Architecture.
- Hexagonal Architecture.

مثال:

```plain text
User  <---  Controller  <---  Application Service
                                  |
                                  v
                            Lock Interceptor
                                  |
                                  v
                              Lock Manager
                                  |
                                  v
                              Database
```

الـ Lock Interceptor يتولى تطبيق سياسة الحجز، والـ Lock Manager مسؤول عن إدارة ملكية الأقفال.

## علاقته بالعمارة

في Clean Architecture نقدر نفصل الموضوع كالتالي:

- الـ Use Case يحدد العملية التي تحتاج Lock.
- الـ Port يعرّف واجهة الحجز.
- الـ Infrastructure تنفذ آلية الحجز.
- Decorator أو Interceptor يضيف السلوك بشكل تلقائي.

مثلاً:

```plain text
HTTP Request  <---  Controller  <---  Use Case
                                      |
                                      v
                                Lock Policy
                                      |
                                      v
                                Lock Port
                                      ^
                                      |
                              Infrastructure
```

وهنا عندنا قرار معماري مهم:

هل الـ Lock Policy جزء من الـ Use Case نفسه، أم نطبقه من خلال Interceptor؟

الإجابة تعتمد على طبيعة الـ Business Rule.

لو العملية لا يمكن تنفيذها بدون حجز مورد معين، لازم يكون الـ Use Case واضحًا في اعتماده على سياسة الحجز، حتى لو تفاصيل التنفيذ مخفية خلف Decorator أو Interceptor.

مش معنى إننا استخدمنا Implicit Lock إننا نخفي Business Rule مهمة عن التطبيق.

## 7. علاقته بـ DDD

هنا نقدر نستفيد من الـ Aggregate Metadata أو الـ Application Services.

مثلاً ممكن يكون عندنا:

```plain text
Update Order
    |
    +--- Requires Lock: Order Aggregate

Cancel Order
    |
    +--- Requires Lock: Order Aggregate

Update Customer
    |
    +--- Requires Lock: Customer Aggregate
```

النظام يحدد الـ Lock المطلوب بناءً على العملية.

لكن لازم ننتبه:

- الـ Aggregate يحدد حدود الاتساق في DDD.
- Implicit Lock يحدد طريقة تطبيق سياسة الحجز.
- مش كل Aggregate لازم يكون عليه Lock.
- ومش كل عملية على Aggregate تستلزم Offline Lock.

## علاقته بأودو

في Odoo ممكن نعمل آلية مشابهة باستخدام:

- Decorators.
- Model Methods.
- Service Classes.
- Context.
- Custom Lock Manager.

مثلاً ممكن يكون عندنا Model Method مسؤولة عن تعديل Order، وكل عمليات التعديل تمر من خلال طبقة مشتركة تتحقق من Lock.

لكن فيه نقطة مهمة جدًا:

استخدام Decorator وحده مش كفاية لو فيه طرق أخرى للوصول للبيانات.

لو فيه Developer بيعدل الـ Order من خلال RPC أو Cron أو API، لازم كل مسارات الكتابة تخضع لنفس سياسة الحجز.

كمان الـ Context في Odoo مش وسيلة حماية أمنية؛ المستخدم ممكن يمرر قيم Context بنفسه، فلازم التحقق من ملكية الـ Lock يتم من مصدر موثوق.

---

## 9. الفرق بين الأنماط الأربعة

خلينا نربط المجموعة كلها ببعض:

النمط	السؤال الأساسي
Optimistic Offline Lock	إزاي أكتشف التعارض عند الحفظ؟
Pessimistic Offline Lock	إزاي أحجز الـ Object قبل التعديل؟
Coarse-Grained Lock	إيه حجم ونطاق الـ Lock؟
Implicit Lock	إزاي أطبق الـ Lock بدون تكرار طلبه يدويًا؟

## 10. الخريطة النهائية لـ Offline Concurrency Patterns

```plain text
Offline Concurrency Patterns
          |
          +--- Optimistic Offline Lock
          |
          +--- Pessimistic Offline Lock
          |              |
          |              +--- Coarse-Grained Lock
          |              |
          |              +--- Implicit Lock
```

الرسم بيوضح علاقتهم المفاهيمية في الدراسة، مش شجرة وراثة أو تصنيف رسمي لعلاقة الأنماط ببعضها.

---

**وبكده نكون خلصنا Offline Concurrency Patterns الأربعة في خريطة PoEAA اللي ماشيين عليها.**

النقطة الأهم: الأنماط الأربعة مش بدائل لبعضها بالضرورة؛ ممكن تستخدم Pessimistic Offline Lock مع Coarse-Grained Lock وتطبق إدارته بطريقة Implicit.

وده معناه إننا بنتعامل مع قرارات مختلفة: استراتيجية التزامن، نطاق الحجز، وطريقة تطبيقه.

كمل بنفس الاسلوب من اليمين للشمال

## Session State Patterns

تمام يا هندسة 😂 نبدأ مجموعة جديدة من كتاب **Patterns of Enterprise Application Architecture (PoEAA)**، وهي:
