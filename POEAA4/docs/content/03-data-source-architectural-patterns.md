# أنماط معمارية لمصدر البيانات (Data Source Architectural Patterns)





# Table Data Gateway

## المشكلة

تخيل عندك تطبيق لإدارة الطلبات، وبتستخدم PostgreSQL.

عندك عمليات مختلفة بتحتاج تتعامل مع جدول orders:

- جلب طلب.
- جلب كل الطلبات.
- إنشاء طلب.
- تعديل طلب.
- حذف طلب.

ممكن تكتب SQL مباشرة داخل كل Function محتاجة تتعامل مع الجدول:

```python
def get_order(order_id):
    cursor.execute(
        "SELECT * FROM orders WHERE id = %s",
        (order_id,)
    )

def create_order(data):
    cursor.execute(
        "INSERT INTO orders ...",
        ...
    )

def cancel_order(order_id):
    cursor.execute(
        "UPDATE orders SET status = ...",
        ...
    )
```

مع زيادة التطبيق، هتلاقي SQL متوزع في أماكن مختلفة.

وده بيؤدي لمشاكل:

1. تكرار SQL في أكتر من مكان.
1. صعوبة تعديل Schema قاعدة البيانات.
1. صعوبة مراجعة وتحسين Queries.
1. ارتباط Business Logic بتفاصيل الوصول للبيانات.
1. صعوبة إعادة استخدام عمليات الوصول لنفس الجدول.

إحنا محتاجين مكان مركزي مسؤول عن كل عمليات الوصول لجدول معين.

## الفكرة والحل

تعريف Fowler:

**An object that acts as a gateway to a database table. One instance handles all the rows in the table.**

خلينا نفهم التعريف.

بننشئ Object واحد مسؤول عن التعامل مع جدول معين، ويحتوي على SQL الخاصة بالجدول ده.

مثلًا:

```plain text
             OrdersTableGateway
                     |
          +----------+----------+
          |          |          |
        SELECT     INSERT     UPDATE
          |          |          |
          +----------+----------+
                     |
                  orders
                   Table
```

لاحظ النقطة المهمة:

**One instance handles all the rows.**

يعني عندنا Object واحد مسؤول عن جميع Rows الموجودة في جدول orders.

مش بنعمل Gateway Object لكل Order.

وده الفرق اللي هنحتاج نفتكره لما نوصل إلى Row Data Gateway.

## مثال

هنستخدم SQLite عشان المثال يكون قابل للتشغيل من غير إعداد PostgreSQL.

**أولًا: إنشاء الجدول**

```python
import sqlite3

connection = sqlite3.connect(":memory:")

connection.execute("""
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        total REAL,
        status TEXT
    )
""")

connection.commit()
```

**ثانيًا: إنشاء Table Data Gateway**

```python
class OrdersTableGateway:

    def __init__(self, connection):
        self.connection = connection

    def find_all(self):
        cursor = self.connection.execute("""
            SELECT id, customer_id, total, status
            FROM orders
        """)

        return cursor.fetchall()

    def find_by_id(self, order_id):
        cursor = self.connection.execute("""
            SELECT id, customer_id, total, status
            FROM orders
            WHERE id = ?
        """, (order_id,))

        return cursor.fetchone()

    def insert(self, customer_id, total):
        cursor = self.connection.execute("""
            INSERT INTO orders (
                customer_id,
                total,
                status
            )
            VALUES (?, ?, ?)
        """, (customer_id, total, "draft"))

        self.connection.commit()

        return cursor.lastrowid
```

**ثالثًا: الاستخدام**

```python
orders_gateway = OrdersTableGateway(connection)

order_id = orders_gateway.insert(
    customer_id=10,
    total=500
)

order = orders_gateway.find_by_id(order_id)

print(order)

orders_gateway.update_status(
    order_id,
    "confirmed"
)

print(orders_gateway.find_all())
```

## 4. إيه اللي حققناه؟

خلينا نلاحظ المسؤوليات:

المسؤولية	مكانها
كتابة SQL	OrdersTableGateway
تنفيذ SELECT	OrdersTableGateway
تنفيذ INSERT	OrdersTableGateway
تنفيذ UPDATE	OrdersTableGateway
تنفيذ DELETE	OrdersTableGateway
تحديد قواعد تأكيد الطلب	ليست مسؤوليته

آخر نقطة مهمة جدًا.

الـ Table Data Gateway مسؤول عن Data Access، مش عن Business Logic.

يعني مش المفروض نحط فيه قاعدة زي:

```python
if order.total > 1000:
    apply_discount()
```

دي مسؤولية Business Logic، مش Data Source Access.

## أقرب GoF Pattern

هنا عندنا تشابه واضح مع:

### Facade

**وجه التشابه:**

الاتنين بيقدموا واجهة موحدة تخفي تفاصيل داخلية.

مثلًا الـ Client بدل ما يتعامل مع SQL وDatabase Connection مباشرة، بيتعامل مع:

```python
orders_gateway.find_by_id(10)
```

**الاختلاف في Intent:**

Facade	Table Data Gateway
يبسط التعامل مع Subsystem	يغلف الوصول إلى Database Table
ممكن يجمع واجهات عدة Objects	يركز على Table أو View معين
مش شرط يكون Data Access	متخصص في Data Access

إذًا Table Data Gateway مش Facade، رغم التشابه في شكل الواجهة.

### Gateway

في Base Patterns عندنا Gateway.

وده فعلًا قريب منه جدًا.

لكن لازم نفرّق:

- Gateway هو مفهوم أوسع لتغليف الوصول إلى External System أو Resource.
- Table Data Gateway تطبيق متخصص لفكرة Gateway، بيغلف الوصول إلى Database Table.

وده تشابه في الغرض والبنية، مش GoF Pattern مستقل.

## علاقته بالعمارة

ممكن يظهر في Layered Architecture بالشكل ده:

```plain text
Presentation Layer
        |
        v
Business Logic Layer
        |
        v
Table Data Gateway
        |
        v
Database
```

وممكن تستخدمه داخل Clean Architecture.

لكن هنا لازم ننتبه:

لو الـ Gateway موجود داخل Infrastructure، والـ Application بيعتمد على Interface موجودة في Application، فده بيساعد في تحقيق Dependency Inversion.

مثلًا:

```plain text
Application
    |
    v
IOrderGateway
    ^
    |
Infrastructure
    |
    v
OrdersTableGateway
    |
    v
Database
```

الـ OrdersTableGateway هنا هو Implementation، والـ Interface موجودة في الجهة اللي تحتاجها.

لكن وجود Table Data Gateway وحده لا يعني إنك طبقت Clean Architecture أو Dependency Inversion.

## 7. علاقته بـ DDD

هنا الفرق مهم.

في DDD عندنا Repository.

ممكن تسأل: هل Table Data Gateway هو Repository؟

**لا، مش نفس الـ Pattern.**

خلينا نقارن:

Table Data Gateway	Repository
يتعامل مع Database Table	يتعامل مع Domain Objects
غالبًا يرجع Records أو Record Sets	غالبًا يرجع Entities أو Aggregates
بيعرف تفاصيل الجدول	يخفي تفاصيل Persistence
SQL وعمليات الجدول مسؤوليته	يوفر Collection-like interface للـ Domain

مثال:

```python

## علاقته بأودو

خلينا نربط النمط بشغلك.

في Odoo لما تكتب:

```python
orders = self.env["sale.order"].search([
    ("state", "=", "sale")
])
```

هل ده Table Data Gateway؟

**لا، مش بالمعنى الدقيق.**

لأن Odoo ORM بيقدم Model وRecordsets وDomain Expressions وبيتعامل مع العلاقات والسلوكيات، مش مجرد Gateway مخصص لجدول واحد يعيد Records خام.

كمان Model واحد في Odoo ممكن يتعامل مع أكثر من جدول في حالات الوراثة والتركيب وغيرها.

فمجرد إن عندك Model مربوط بجدول لا يكفي لتصنيفه Table Data Gateway.

---


# Row Data Gateway

## المشكلة

في الـ Table Data Gateway كان عندنا Object واحد مسؤول عن جدول كامل.

لكن تخيل إن عندنا نظام فيه آلاف الطلبات، وكل طلب محتاج نتعامل معاه بشكل مستقل.

مثلًا:

- جلب طلب معين.
- تعديل حالة طلب معين.
- تغيير قيمة طلب معين.
- حذف طلب معين.

ممكن نستخدم Table Data Gateway، لكن كل مرة هنحتاج نمرر order_id للـ Gateway عشان يحدد الصف المطلوب.

هل ممكن يكون عندنا Object يمثل كل Row بشكل مستقل، ويكون مسؤول عن الوصول للبيانات الخاصة بالـ Row دي؟

هنا بيظهر Row Data Gateway.

## الفكرة والحل

**Row Data Gateway** هو Object بيمثل Row واحدة من جدول قاعدة البيانات، وبيوفر واجهة للتعامل مع البيانات الخاصة بالـ Row دي.

يعني بدل:

```plain text
             OrdersTableGateway
                     |
          +----------+----------+
          |          |          |
        Order 1    Order 2    Order 3
```

هنكون عندنا:

```plain text
       OrderRowGateway       OrderRowGateway
              |                     |
          Row 1                 Row 2
              |                     |
           orders                orders
                  Database
```

كل Object مسؤول عن Row واحدة.

لاحظ إننا هنا بنتكلم عن Data Access، مش بالضرورة Business Logic.

## مثال

هنستخدم نفس جدول الطلبات.

**أولًا: Row Data Gateway**

```python
class OrderRowGateway:

    def __init__(self, connection, order_id):
        self.connection = connection
        self.order_id = order_id

    def load(self):
        cursor = self.connection.execute("""
            SELECT id, customer_id, total, status
            FROM orders
            WHERE id = ?
        """, (self.order_id,))

        row = cursor.fetchone()

        if row is None:
            raise ValueError("Order not found")

        self.customer_id = row[1]
        self.total = row[2]
        self.status = row[3]

    def update_status(self, status):
        self.connection.execute("""
            UPDATE orders
            SET status = ?
            WHERE id = ?
        """, (status, self.order_id))

        self.connection.commit()

        self.status = status

    def delete(self):
        self.connection.execute("""
            DELETE FROM orders
```

**ثانيًا: الاستخدام**

```python
order = OrderRowGateway(connection, order_id=1)

order.load()

print(order.total)
print(order.status)

order.update_status("confirmed")
```

لاحظ هنا إننا أنشأنا Object لطلب معين.

والـ Object ده بيتعامل مع Row واحدة فقط.

## 4. الفرق بين Table Data Gateway وRow Data Gateway

دي أهم نقطة في النمطين.

المقارنة	Table Data Gateway	Row Data Gateway
وحدة التمثيل	جدول كامل	صف واحد
عدد Objects	غالبًا Object واحد لكل جدول	Object لكل Row
التعامل مع البيانات	عمليات على مجموعة Rows	عمليات على Row محددة
تحديد السجل	تمرير ID أو شروط البحث	الـ Object مرتبط بسجل محدد
المسؤولية	Data Access	Data Access

خلينا نوضح الفرق في الاستخدام:

**Table Data Gateway:**

```python
gateway = OrdersTableGateway(connection)

order = gateway.find_by_id(10)

gateway.update_status(10, "confirmed")
```

**Row Data Gateway:**

```python
order = OrderRowGateway(connection, 10)

order.load()

order.update_status("confirmed")
```

في الأول الـ Gateway هو اللي بيستقبل هوية السجل.

في الثاني الـ Object نفسه مرتبط بسجل معين.

## أقرب GoF Pattern

مفيش GoF Pattern مكافئ مباشرة لـ Row Data Gateway، لكن فيه تشابهات.

### Proxy

**وجه التشابه:**

الـ Row Data Gateway ممكن يمثل نقطة وصول لسجل معين، ويخفي تفاصيل التعامل مع قاعدة البيانات.

وده قريب من Proxy اللي بيوفر وسيطًا للوصول إلى Object آخر.

**الاختلاف في Intent:**

Proxy	Row Data Gateway
يتحكم في الوصول إلى Real Subject	يغلف الوصول إلى Database Row
ممكن يستخدم Lazy Loading أو Access Control	يوفر عمليات Data Access لسجل معين
مش شرط يتعامل مع Database	متخصص في Database Access

إذًا التشابه في فكرة الوساطة وإخفاء التفاصيل، لكن الهدف مختلف.

### Active Record

وده أقرب تشابه عملي، لكنه مش GoF Pattern.

الاتنين ممكن يكون عندهم Object لكل Row، والاتنين ممكن يوفروا عمليات زي update() و`delete()`.

لكن الفرق الحقيقي في مكان الـ Business Logic، وده هنوضحه بالتفصيل بعد شوية.

## 6. الفرق بين Row Data Gateway وActive Record

دي نقطة مهمة جدًا، ومش عايزك تخلط بينهم.

### Row Data Gateway

الـ Object مسؤول عن الوصول للبيانات فقط.

مثلًا:

```python
order.update_status("confirmed")
```

هنا update_status() بتنفذ عملية تحديث في قاعدة البيانات.

لكن مش بالضرورة تكون هي المسؤولة عن تقرير هل تأكيد الطلب مسموح أم لا.

### Active Record

الـ Object بيجمع بين:

- بيانات السجل.
- Business Logic الخاصة به.
- عمليات Persistence.

مثلًا:

```python
order.confirm()
order.save()
```

هنا confirm() ممكن تحتوي على قواعد المجال، و`save()` تحفظ البيانات.

المقارنة	Row Data Gateway	Active Record
يمثل Row	نعم	نعم
يحتوي Data Access	نعم	نعم
يحتوي Business Logic	ليس هدفه الأساسي	نعم
يحفظ نفسه	ممكن يوفر عمليات تحديث	نعم
يفصل Domain Logic عن Persistence	بصورة أكبر	لا، يدمج المسؤوليتين

**ملحوظة:** وجود Method اسمها confirm() وحده لا يجعل الـ Object Active Record؛ المهم المسؤوليات والتصميم الفعلي.

## علاقته بالعمارة

ممكن تستخدم Row Data Gateway داخل Layered Architecture:

```plain text
Presentation Layer
        |
        v
Business Logic Layer
        |
        v
Row Data Gateway
        |
        v
Database
```

وممكن استخدامه داخل Clean Architecture باعتباره جزءًا من Infrastructure.

لكن الأفضل إن الـ Application أو Domain ما يعتمدوش على تفاصيل PostgreSQL أو SQL مباشرة.

مثلًا:

```plain text
Application
     |
     v
OrderRepository (Interface)
     ^
     |
Infrastructure
     |
     v
OrderRowGateway
     |
     v
Database
```

هنا الـ Repository ممكن يستخدم Row Data Gateway داخليًا.

## 8. علاقته بـ DDD

في DDD، الـ Row Data Gateway مش بديل عن Repository أو Aggregate.

خلينا نفصل المسؤوليات:

- Aggregate: يحدد حدود الاتساق وقواعد المجال.
- Repository: يوفر الوصول إلى Aggregates.
- Row Data Gateway: يوفر الوصول إلى Row في قاعدة البيانات.

ممكن Repository يستخدم Row Data Gateway داخليًا لتحميل البيانات وتحديثها، لكن الـ Domain مش المفروض يعتمد عليه مباشرة.

## علاقته بأودو

في Odoo عندك:

```python
order = self.env["sale.order"].browse(10)
```

هنا عندك Recordset بيمثل سجلًا أو مجموعة سجلات.

هل ده Row Data Gateway؟

**مش بالضرورة، والتصنيف الدقيق إنه Odoo ORM Recordset.**

لأن Odoo Recordset عنده سلوك أوسع من مجرد تغليف Data Access لصف واحد، وبيوفر ORM Operations وBusiness Methods وRecord Cache وغير ذلك.

حتى لو استخدمت:

```python
order = self.env["sale.order"].browse(10)
order.write({"state": "sale"})
```

فده مش تطبيق حرفي لـ Row Data Gateway.

التشابه هنا في مستوى التعامل مع سجل معين، لكن الـ Intent مختلف.

---

## 10. إمتى أستخدمه؟

الحالة	الاختيار
عايز Object لكل Row مسؤول عن Data Access	Row Data Gateway
عايز Object واحد مسؤول عن جدول كامل	Table Data Gateway
عايز Object يجمع Data وBusiness Logic وPersistence	Active Record
عايز Domain Objects مستقلة عن Persistence	Data Mapper

## الخلاصة
**Row Data Gateway** بيعمل Object لكل Row في قاعدة البيانات، والـ Object ده مسؤول عن عمليات الوصول للسجل وتعديله.

وأهم مقارنة لحد دلوقتي:

- Table Data Gateway: واحد للجدول.
- Row Data Gateway: واحد لكل Row.
- Active Record: واحد لكل Row، لكن بيجمع Data Access وBusiness Logic.

---

**التالي: Active Record**

وده هيكون مهم جدًا؛ لأنه هنقدر نقارن بينه وبين Odoo ORM، وكمان نفهم ليه Fowler بيعتبره Pattern مختلف عن Row Data Gateway.


# Active Record

هنكمل في مجموعة **Data Source Architectural Patterns** من كتاب *Patterns of Enterprise Application Architecture*.

خلينا نبدأ من أهم نقطة: الـ Active Record بيختلف عن الـ Row Data Gateway في إنه مش مجرد Object مسؤول عن الوصول للداتا؛ ده كمان بيحتوي على الـ Business Logic المرتبطة بالسجل نفسه.

## المشكلة

تخيل عندنا جدول orders في قاعدة البيانات:

id	customer	total	status
1	Ahmed	500	draft
2	Mohamed	800	confirmed

إحنا محتاجين نمثل كل Order في Python Object.

لكن عندنا مسؤوليتين:

1. التعامل مع قاعدة البيانات: تحميل، حفظ، تحديث، حذف.
1. تنفيذ قواعد المجال (Business Logic): تأكيد الطلب، حساب الإجمالي، التحقق من إمكانية الإلغاء.

السؤال: هل نفصل المسؤوليتين في Objects مختلفة، ولا نجمعهم في Object واحد؟

الـ Active Record اختار إنه يجمعهم.

## الفكرة والحل

حسب تعريف Fowler:

**An object that wraps a row in a database table or view, encapsulates database access, and adds domain logic on that data.**

بمعنى إن كل Object بيمثل Row واحدة، وبيحتوي على:

- بيانات السجل (Data).
- عمليات الوصول لقاعدة البيانات (Persistence Operations).
- منطق المجال المرتبط بالسجل (Domain Logic).

تصور التركيب بالشكل ده:

```plain text
                 ActiveRecord: Order
                         |
             +-----------+-----------+
             |           |           |
           Data       Persistence   Domain Logic
             |           |           |
          order_id      save()     confirm()
          total         delete()   cancel()
          status        reload()   calculate_total()
             |           |           |
             +-----------+-----------+
                         |
                      Database
```

يعني الـ Order نفسه يعرف بياناته، ويعرف إزاي يحفظ نفسه، ويعرف ينفذ السلوك المرتبط بيه.

## مثال

هنستخدم SQLite عشان المثال يكون عملي، مع تبسيط بعض التفاصيل لتوضيح الـ Pattern.

```python
import sqlite3

class Order:
    def __init__(self, order_id, customer, total, status):
        self.id = order_id
        self.customer = customer
        self.total = total
        self.status = status

    @classmethod
    def find(cls, connection, order_id):
        cursor = connection.execute(
            """
            SELECT id, customer, total, status
            FROM orders
            WHERE id = ?
            """,
            (order_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return cls(*row)

    def confirm(self, connection):
        if self.status != "draft":
            raise ValueError("Only draft orders can be confirmed")

        if self.total <= 0:
            raise ValueError("Order total must be positive")

        self.status = "confirmed"
        self.save(connection)
```

الاستخدام:

```python
connection = sqlite3.connect("shop.db")

order = Order.find(connection, 1)

if order:
    order.confirm(connection)
```

خد بالك من السطر ده:

```python
order.confirm(connection)
```

إحنا بنطلب من الـ Order إنه ينفذ عملية منطقية تخصه، وهو داخليًا بيغير حالته وبيحفظ التغيير في قاعدة البيانات.

وده جوهر الـ Active Record.

ملحوظة: المثال تعليمي، وفي التطبيقات الحقيقية محتاجين نهتم بالـ Transactions والـ Concurrency والـ Error Handling وفصل إدارة الاتصال بقاعدة البيانات.

## 4. علاقته بأنماط GoF

هنا لازم نكون دقيقين: **مفيش GoF Pattern مكافئ مباشرة للـ Active Record.**

ليه؟

لأن Active Record بيحل مشكلة مختلفة:

- GoF بيركز على تصميم التعاون بين Objects، وإنشاء Objects، وتنظيم سلوكها.
- Active Record بيركز على تنظيم Domain Data وPersistence في تطبيقات الأعمال.

ممكن تلاقي تشابهات شكلية:

GoF Pattern	وجه التشابه	الاختلاف
Facade	الـ Active Record بيقدم واجهة للتعامل مع البيانات	Facade بيبسط واجهة نظام فرعي، مش بالضرورة يمثل Row أو يحتوي Business Logic
Template Method	ممكن بعض عمليات الحفظ تستخدم خطوات قابلة للتخصيص	ده مش تعريف Active Record ولا هدفه

إذن مفيش داعي نصنفه تحت GoF لمجرد إننا لقينا تشابه في بعض التفاصيل.

## 5. الفرق بين Active Record وRow Data Gateway

دي أهم مقارنة في الموضوع كله.

الاتنين بيستخدموا Object لكل Row، لكن الاختلاف في المسؤوليات.

**Row Data Gateway**

## OrderRowGateway

```plain text
+-----------------------+
|   OrderRowGateway     |
+-----------------------+
| load()                |
| save()                |
| update_status()       |
| delete()              |
+-----------------------+
           |
        Database
```

مسؤول عن الوصول للداتا فقط. منطق المجال موجود في مكان آخر.

---

**Active Record**

## Order

```plain text
+-----------------------+
|        Order          |
+-----------------------+
| id                    |
| total                 |
| status                |
|-----------------------|
| save()                |
| delete()              |
| confirm()             |
| cancel()              |
+-----------------------+
           |
        Database
```

مسؤول عن الوصول للداتا، وكمان منطق المجال المرتبط بالسجل.

المقارنة	Row Data Gateway	Active Record
Object لكل Row	نعم	نعم
يحتوي بيانات السجل	نعم	نعم
يحتوي Persistence Logic	نعم	نعم
يحتوي Domain Logic	لا، في التصميم المعتاد	نعم
يفصل Business Logic عن Data Access	بدرجة أكبر	لا، بيجمعهم

## الخلاصة

الفرق مش في عدد الـ Objects، الفرق في الـ Intent وتوزيع المسؤوليات.

## علاقته بالعمارة

هل ممكن نستخدم Active Record مع Layered Architecture؟

أيوه.

في تصميم Layered Architecture ممكن يكون الـ Active Record جزءًا من طبقة الـ Domain أو Business Objects، مع إنه بيتعامل مع قاعدة البيانات بنفسه.

```plain text
        Presentation Layer
                 |
        Business / Domain Layer
                 |
           Active Record
          /            \
    Domain Logic     Persistence
                         |
                    Database
```

لكن لاحظ إننا هنا سمحنا للـ Domain Object إنه يعرف تفاصيل الـ Persistence.

وده بيخلق نوع من الـ Coupling بين منطق المجال وقاعدة البيانات.

### طيب مع Clean Architecture؟

هنا الموضوع محتاج انتباه.

الـ Clean Architecture بتشترط إن اتجاه الاعتماد يكون ناحية الداخل:

```plain text
Infrastructure  --->  Application  --->  Domain
```

لو الـ Domain Object بيعتمد على sqlite3 أو ORM معين بشكل مباشر، يبقى عندنا مشكلة مع Dependency Rule.

لكن مش معنى كده إن Active Record مستحيل يتواجد في نظام بيستخدم Clean Architecture؛ ممكن تستخدمه في طبقة خارجية أو كـ Persistence Model، وتفصل عنه الـ Domain Model الداخلي.

المهم إنك متخلّيش الـ Domain الداخلي يعتمد على تفاصيل قاعدة البيانات.

## 7. علاقته بـ DDD

هل Active Record يتعارض مع DDD؟

**مش بالضرورة.**

ممكن تستخدمه في نظام بيطبق بعض مفاهيم DDD، لكن فيه نقطة مهمة:

في DDD، خصوصًا لما يكون عندك Domain Model معقد، بنحب نفصل بين:

- Domain Logic.
- Persistence Infrastructure.

لأننا عايزين الـ Domain Model يعبر عن قواعد المجال، مش عن تفاصيل تخزين البيانات.

وده بيخلي الـ Active Record أقل ملاءمة غالبًا للـ Domain Models المعقدة.

لكن في أنظمة أبسط، ممكن يكون اختيار عملي ومناسب.

## علاقته بأودو

خلينا نطبق الكلام على Odoo.

لما تكتب:

```python
order = self.env["sale.order"].browse(10)

order.action_confirm()
```

ممكن تقول إن فيه تشابه واضح مع Active Record:

- عندك Model بيمثل بيانات الطلب.
- عندك ORM مسؤول عن Persistence.
- عندك Business Methods زي action_confirm().

لكن هل نقدر نقول إن Odoo هو تطبيق مطابق لـ Active Record؟

مش بالدقة دي.

Odoo ORM بيقدم مجموعة قدرات أوسع، منها:

- Recordsets ممكن تحتوي على أكثر من سجل.
- العلاقات بين Models.
- Computed Fields.
- Inheritance.
- Prefetching وCaching.
- التحكم في Transactions من خلال الـ Framework.

إذن نقدر نقول إن فيه **Active Record-like characteristics** في تصميم Odoo Models، لكن اختزاله بالكامل في Active Record مش وصف دقيق.

---

## 9. إمتى أستخدم Active Record؟

استخدمه لما:

- التطبيق بسيط أو متوسط التعقيد.
- الـ Business Logic المرتبطة بالسجل محدودة نسبيًا.
- عايز طريقة مباشرة وسريعة للتعامل مع الداتا.
- مش محتاج فصل صارم بين Domain Model وPersistence.

فكر في بدائل زي Data Mapper مع Repository لما:

- الـ Domain Logic معقدة.
- محتاج Domain Model مستقل عن ORM.
- عندك قواعد عمل كثيرة ومتشابكة.
- محتاج تختبر منطق المجال بمعزل عن قاعدة البيانات.

## الخلاصة
خلينا نثبت الفرق بين التلاتة اللي شرحناهم:

Pattern	الفكرة الأساسية
Table Data Gateway	Object واحد يتعامل مع كل Rows في Table
Row Data Gateway	Object لكل Row مسؤول عن Data Access
Active Record	Object لكل Row يجمع Data Access وDomain Logic

**والسؤال اللي عايزك تفكر فيه قبل ما ننتقل للي بعده:**

لو عندنا Order فيه 30 قاعدة Business Logic، وعندنا 15 عملية مختلفة بتتعامل مع الطلب، هل Active Record لسه اختيار مناسب؟ ولا بدأنا نحتاج نفصل الـ Domain Model عن الـ Persistence؟

النمط التالي في المجموعة هو **Data Mapper**، وده مهم جدًا لأنه بيقدم اتجاهًا مختلفًا تمامًا عن Active Record.


# Data Mapper

ندخل دلوقتي على واحد من أهم الـ Patterns في مجموعة **Data Source Architectural Patterns**، وخصوصًا إنه بيقدم عكس الاتجاه اللي شفناه في الـ Active Record.

خلينا نفهمه بهدوء، لأن الفرق بينه وبين Active Record هو أساس فهم تصميم الـ Persistence في الأنظمة الكبيرة.

## المشكلة

تخيل عندنا نظام تجارة إلكترونية، وفيه Domain Model بالشكل ده:

```python
class Order:
    def __init__(self, order_id, customer, items):
        self.id = order_id
        self.customer = customer
        self.items = items

    def confirm(self):
        if not self.items:
            raise ValueError("Order must contain items")

        # Business rules
```

الـ Order هنا مسؤول عن قواعد المجال (Domain Logic).

لكن عندنا مشكلة: إزاي نحفظ الـ Order ده في قاعدة البيانات؟

ممكن نضيف جواه SQL وعمليات save() و`load()`، زي ما عملنا في Active Record.

لكن كده الـ Domain Object هيبقى عارف تفاصيل قاعدة البيانات.

وده يخلق مشاكل:

1. تغيير قاعدة البيانات ممكن يأثر على الـ Domain Model.
1. الـ Business Logic هتبقى مرتبطة بتفاصيل الـ Persistence.
1. اختبار الـ Domain Logic هيبقى أصعب لو محتاج قاعدة بيانات.
1. شكل الـ Objects في الـ Domain مش لازم يكون مطابق لشكل الجداول في Database.

إذن إحنا محتاجين نفصل المسؤوليتين.

## الفكرة والحل

الـ Data Mapper بيعمل فصل بين الـ Domain Objects والـ Database.

بمعنى:

- الـ Domain Object مسؤول عن بياناته وقواعد المجال.
- الـ Data Mapper مسؤول عن نقل البيانات بين الـ Domain Objects ومصدر البيانات.

تعريف Fowler:

**A layer of Mappers that moves data between objects and a database while keeping them independent of each other and the mapper itself.**

خلينا نشوف التصور:

```plain text
             Application
                  |
                  v
             Domain Model
                  |
                Order
                  |
          +-------+-------+
          |               |
      Domain Logic     Domain Data
                          |
                          |  Data Mapper
                          v
                  +---------------+
                  |  OrderMapper  |
                  +---------------+
                          |
                    SQL / Database
                          |
                          v
                       Orders
```

خد بالك من النقطة الأساسية:

الـ Order مش محتاج يعرف إن فيه OrderMapper أصلًا.

والـ OrderMapper هو اللي يعرف إزاي يحول بيانات الـ Order إلى بيانات قابلة للتخزين، والعكس.

## مثال

هنستخدم نفس مثال الطلبات عشان المقارنة تبقى واضحة.

**أولًا: Domain Model**

```python
class Order:
    def __init__(self, order_id, customer, total, status):
        self.id = order_id
        self.customer = customer
        self.total = total
        self.status = status

    def confirm(self):
        if self.status != "draft":
            raise ValueError("Only draft orders can be confirmed")

        if self.total <= 0:
            raise ValueError("Order total must be positive")

        self.status = "confirmed"
```

لاحظ إن مفيش أي SQL أو save() أو delete().

الـ Order مهتم بقواعد المجال فقط.

**ثانيًا: Data Mapper**

```python
class OrderMapper:
    def __init__(self, connection):
        self.connection = connection

    def find_by_id(self, order_id):
        cursor = self.connection.execute(
            """
            SELECT id, customer, total, status
            FROM orders
            WHERE id = ?
            """,
            (order_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return Order(
            order_id=row[0],
            customer=row[1],
            total=row[2],
            status=row[3]
        )

    def insert(self, order):
        cursor = self.connection.execute(
            """
            INSERT INTO orders (customer, total, status)
            VALUES (?, ?, ?)
            """,
            (order.customer, order.total, order.status)
        )

        self.connection.commit()
```

**ثالثًا: الاستخدام**

```python
mapper = OrderMapper(connection)

order = mapper.find_by_id(10)

if order:
    order.confirm()
    mapper.update(order)
```

هنا حصل إيه؟

1. الـ Mapper قرأ البيانات من قاعدة البيانات.
1. حولها إلى Order Object.
1. الـ Order نفذ الـ Business Logic.
1. الـ Mapper حفظ التغييرات في قاعدة البيانات.

كل Object عنده مسؤولية واضحة.

المثال تعليمي ومبسط؛ في تطبيق حقيقي هنحتاج Transaction Management، ومعالجة التزامن، والتعامل مع العلاقات والـ Identity Mapping وغيرها.

## 4. علاقته بأنماط GoF

هنا برضه مفيش GoF Pattern مكافئ مباشرة للـ Data Mapper.

لكن فيه تشابهات ممكن تظهر في التنفيذ:

GoF Pattern	وجه التشابه	الاختلاف
Adapter	تحويل البيانات من شكل إلى شكل آخر	Adapter هدفه التوافق بين واجهتين، أما Data Mapper هدفه فصل Domain Objects عن Persistence
Bridge	فصل جزأين ممكن يتغيروا بشكل مستقل	Bridge يفصل Abstraction عن Implementation، بينما Data Mapper يفصل Domain Model عن Data Source
Strategy	ممكن تبديل طريقة الـ Mapping	Strategy نمط لتبديل الخوارزميات، مش لتنظيم Persistence

**النتيجة:** Data Mapper نمط Enterprise Application Architecture، وليس تطبيقًا مباشرًا لأي GoF Pattern.

## 5. الفرق بين Data Mapper وActive Record

دي أهم مقارنة في الدرس.

**Active Record**

```plain text
+-----------------------+
|        Order          |
+-----------------------+
| id                    |
| total                 |
| status                |
|-----------------------|
| confirm()             |
| save()                |
| delete()              |
+-----------------------+
           |
        Database
```

الـ Object نفسه مسؤول عن الـ Domain Logic والـ Persistence.

---

**Data Mapper**

```plain text
+------------------+
|      Order       |
+------------------+
| id               |
| total            |
| status           |
|------------------|
| confirm()        |
+------------------+

        |
        | Data
        v

+------------------+
|   OrderMapper    |
+------------------+
| find_by_id()     |
| insert()         |
| update()         |
+------------------+
        |
     Database
```

الـ Domain Object منفصل عن الـ Persistence Object.

المقارنة	Active Record	Data Mapper
Domain Logic	داخل الـ Object	داخل الـ Domain Object
Persistence Logic	داخل الـ Object	داخل Mapper منفصل
الاعتماد على Database	أعلى	أقل
فصل Domain عن Persistence	ضعيف نسبيًا	قوي
مناسب لـ Domain معقد	أقل ملاءمة غالبًا	أكثر ملاءمة غالبًا

لاحظ إن Data Mapper مش معناه إن الـ Domain Model لازم يكون معقد، هو فقط بيسمحلك تفصل المسؤوليات حتى لو المجال بسيط.

## علاقته بالعمارة

### مع Layered Architecture

الـ Data Mapper غالبًا مكانه في طبقة الـ Data Access أو Infrastructure.

```plain text
       Presentation Layer
                |
                v
       Application Layer
                |
                v
         Domain Layer
                |
                | Domain Objects
                v
        Data Access Layer
                |
           Data Mapper
                |
                v
             Database
```

الرسم ده توضيحي لتوزيع المسؤوليات، مش شرط يكون اتجاه الاعتماد البرمجي مطابقًا لاتجاه الأسهم.

### مع Clean Architecture

هنا Data Mapper بيكون مناسب جدًا.

لأننا نقدر نخلي الـ Domain مستقل، ونخلي تفاصيل التخزين في الطبقات الخارجية.

```plain text
          Infrastructure
          +------------+
          | SQL Mapper |
          | Repository |
          +------------+
                 |
                 v
          Application
          +------------+
          | Use Cases  |
          +------------+
                 |
                 v
             Domain
          +------------+
          | Order      |
          | Customer   |
          +------------+
```

والأدق في Clean Architecture إن الـ Domain لا يعتمد على الـ Mapper.

ممكن الـ Application Layer تعرف Interface للـ Repository، والـ Infrastructure تنفذها باستخدام Data Mapper.

## 7. علاقته بـ DDD

هنا العلاقة مهمة جدًا.

في DDD ممكن يكون عندنا:

- Entity: بيمثل كيان له Identity.
- Value Object: بيمثل قيمة.
- Aggregate: حدود اتساق وقواعد مجال.
- Repository: يوفر واجهة للتعامل مع Aggregates.
- Data Mapper: ينقل البيانات بين Domain Objects ومصدر البيانات.

تصور العلاقة:

```plain text
        Application Service
                 |
                 v
             Repository
                 |
                 v
          Data Mapper
                 |
                 v
              Database

                 ^
                 |
             Domain
              Order
```

بس خد بالك من الفرق:

**Repository مش هو Data Mapper.**

Repository	Data Mapper
يتعامل مع Domain Objects أو Aggregates	يحول البيانات بين Objects وData Source
يقدم واجهة تشبه Collection	مسؤول عن Mapping
مفهوم مهم في DDD	نمط في Data Access
ممكن يستخدم Data Mapper داخليًا	لا يشترط وجود Repository

يعني ممكن يكون عندك:

```plain text
OrderRepository
       |
       v
OrderMapper
       |
       v
   Database
```

الـ Repository يقول: هاتلي الـ Order رقم 10.

والـ Mapper يعرف إزاي يقرأ البيانات ويحولها إلى Order Object.

## علاقته بأودو

خلينا نربط الكلام بأودو.

لما تكتب:

```python
order = self.env["sale.order"].browse(10)
order.action_confirm()
```

أنت بتتعامل مع ORM بيدير عملية تحويل البيانات من وإلى قاعدة البيانات.

لكن هل Odoo بيطبق Data Mapper Pattern بالشكل التقليدي؟

مش بالضرورة.

السبب إن Odoo Models نفسها مرتبطة بالـ ORM، وبتحتوي على Fields وMethods، والـ ORM بيتولى تفاصيل التخزين والتحميل.

فمش عندنا بالضرورة Domain Object مستقل تمامًا عن Persistence، زي المثال اللي عملناه.

كمان مش معنى إن ORM بيعمل Mapping بين Python Objects وDatabase Rows إنه تلقائيًا يطبق Fowler's Data Mapper Pattern بنفس المعنى المعماري؛ لازم ننظر لتوزيع المسؤوليات وعلاقة الـ Domain بالـ Persistence.

---

## 9. إمتى أستخدم Data Mapper؟

استخدمه لما:

- عندك Domain Logic معقدة.
- عايز تفصل الـ Domain Model عن قاعدة البيانات.
- محتاج تختبر الـ Domain من غير Database.
- شكل الـ Database مختلف عن شكل الـ Domain Objects.
- عندك احتمالية تغيير ORM أو Data Source من غير تغيير الـ Domain.

## الخلاصة
وصلنا لحد هنا لأربع أنماط:

Pattern	المسؤولية الأساسية
Table Data Gateway	التعامل مع كل Rows في Table
Row Data Gateway	التعامل مع Row محددة
Active Record	Data + Persistence + Domain Logic
Data Mapper	فصل Domain Objects عن Persistence

**النقطة اللي عايزك تثبتها:**

الـ Active Record بيقول: الـ Object يعرف يحفظ نفسه.

الـ Data Mapper بيقول: الـ Object مش محتاج يعرف أي حاجة عن طريقة حفظه.

والنمط التالي هو **Table Module**؟ لا، ده اتشرح بالفعل في مجموعة Domain Logic. التالي في مجموعة Data Source Architectural Patterns هو **Metadata Mapping**، وهنشوف فيه إزاي نستخدم Metadata لوصف العلاقة بين الـ Objects والجداول بدل كتابة تفاصيل الـ Mapping يدويًا في كل مرة.

معاك حق 😂 أنا كتبت المحتوى بالعربي، لكن ترتيب العناصر والرسومات والجداول لسه ظاهر بالشكل المعتاد من الشمال لليمين.

هظبط ده من هنا:

- الشرح العربي يبدأ من اليمين، والمصطلحات الإنجليزية تندمج وسط الكلام.
- الجداول يكون ترتيب أعمدتها من اليمين للشمال.
- الرسومات المعمارية يكون اتجاه تدفقها من اليمين للشمال.
- الأكواد تفضل LTR بطبيعتها، عشان تفضل صحيحة وسهلة القراءة.
- هحافظ على نفس منهج شرح كل Pattern والمقارنة مع GoF وClean Architecture وDDD وOdoo.

**هنكمل من Metadata Mapping، وبنفس مستوى التفصيل، مع مراعاة اتجاه العرض من اليمين للشمال.**

حاضر يا صاحبي 😂 خلينا نعيد شرح **Data Mapper Pattern** من الأول، مع ترتيب الشرح والجداول والرسومات من اليمين للشمال، ونحافظ على نفس المنهج اللي ماشيين عليه.
