---
title: مقارنة Separated Interface (2)
url: https://chatgpt.com/g/g-p-6aef8f7176848191b87a5d98247e8052-poeaa/c/6aee73d1-79d4-83ea-a066-7c1f1550c162
h1s: ['4. Data Mapper Pattern', '4. Data Mapper Pattern', 'Load', 'Object-Relational Behavioral Patterns', '1. Unit of Work Pattern', '2. Identity Map Pattern', 'False', 'True', '4000', 'False', '3. Lazy Load', 'لسه مفيش تحميل للـ items', 'هنا حصل التحميل لأول مرة', 'هنا استخدمنا البيانات المحملة', 'خلصنا Object-Relational Behavioral Patterns 🎯', 'Object-Relational Structural Patterns', '1. Identity Field', '2. Foreign Key Mapping', '3. Association Table Mapping']
len: 72136
msgCount: 11
---

# 4. Data Mapper Pattern

ندخل دلوقتي على واحد من أهم الـ Patterns في مجموعة **Data Source Architectural Patterns**، وخصوصًا إنه بيقدم عكس الاتجاه اللي شفناه في الـ Active Record.

خلينا نفهمه بهدوء، لأن الفرق بينه وبين Active Record هو أساس فهم تصميم الـ Persistence في الأنظمة الكبيرة.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال Python

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

## 6. علاقته بالـ Application Architecture

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

## 8. علاقته بـ Odoo

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

# 4. Data Mapper Pattern

إحنا كنا شرحنا قبل كده:

1. Table Data Gateway
1. Row Data Gateway
1. Active Record

ودلوقتي وصلنا إلى **Data Mapper**، وده مهم جدًا لأنه بيقدم فلسفة مختلفة عن Active Record.

## 1. المشكلة (Problem)

تخيل إن عندنا نظام تجارة إلكترونية، وفيه Order بيمثل طلب شراء.

الـ Order عنده بيانات وقواعد Business Logic:

- رقم الطلب.
- العميل.
- إجمالي الطلب.
- حالة الطلب.
- إمكانية تأكيد الطلب أو إلغائه.

ممكن نكتب الـ Domain Object بالشكل ده:

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

السؤال هنا: إزاي نحفظ الـ Order في قاعدة البيانات؟

عندنا اختيار إننا نضيف جواه save() و`delete()` وعمليات SQL.

لكن المشكلة إننا كده بنخلط مسؤوليتين مختلفتين:

- **Domain Logic:** القواعد الخاصة بالطلب.
- **Persistence Logic:** إزاي نحفظ الطلب ونسترجعه من قاعدة البيانات.

وده بيعمل Coupling بين الـ Domain Model والـ Database.

إحنا عايزين الـ Order يهتم بقواعد العمل، من غير ما يعرف هو بيتخزن فين أو إزاي.

## 2. الفكرة والحل (Solution)

الـ Data Mapper بيقدم حل بسيط في فكرته:

**نفصل الـ Domain Objects عن تفاصيل تخزين البيانات باستخدام Object وسيط اسمه Mapper.**

يعني بدل ما الـ Order يحفظ نفسه، عندنا OrderMapper هو المسؤول عن تحويل بيانات الـ Order إلى بيانات مناسبة لقاعدة البيانات، والعكس.

شوف العلاقة من اليمين للشمال:

```plain text
قاعدة البيانات  <---  Data Mapper  <---  Domain Object
  Database          OrderMapper        Order
```

خلينا نفهم المسؤوليات:

المسؤولية	مين المسؤول عنها؟
قواعد تأكيد الطلب	Order
حساب قواعد المجال	Order
قراءة البيانات من Database	OrderMapper
تحويل البيانات إلى Order	OrderMapper
حفظ Order في Database	OrderMapper
تحديث بيانات Order في Database	OrderMapper

لاحظ إن الـ Order مش محتاج يعرف أي حاجة عن الـ Mapper.

والـ Mapper هو اللي يعرف يتعامل مع قاعدة البيانات.

## 3. مثال Python

هنستخدم نفس مثال الطلبات.

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

لاحظ إن الـ Order لا يحتوي على:

- SQL.
- Database Connection.
- save().
- delete().
- ORM.

هو مسؤول عن منطق المجال فقط.

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

# Load
order = mapper.find_by_id(10)

if order:
    # Business Logic
    order.confirm()

    # Persistence
    mapper.update(order)
```

خلينا نمشي على التنفيذ:

```plain text
1. find_by_id(10)
          |
          v
2. OrderMapper يقرأ من Database
          |
          v
3. يحول البيانات إلى Order Object
          |
          v
4. Order ينفذ confirm()
          |
          v
5. OrderMapper ينفذ update()
          |
          v
6. Database تتحدث
```

لاحظ إن كل مسؤولية في مكانها.

المثال تعليمي ومبسط، وفي التطبيق الحقيقي هنحتاج Transaction Management وConcurrency Handling ومعالجة العلاقات بين الكيانات.

## 4. علاقته بأنماط GoF

هنا مفيش GoF Pattern مكافئ مباشرة للـ Data Mapper.

لكن ممكن نلاحظ تشابهات في بعض التفاصيل:

نمط GoF	وجه التشابه	الاختلاف في الهدف
Adapter	تحويل البيانات من شكل لشكل	التوافق بين واجهتين مختلفتين
Bridge	فصل جزأين قابلين للتغيير بشكل مستقل	فصل Abstraction عن Implementation
Strategy	إمكانية تغيير طريقة الـ Mapping	تبديل الخوارزميات

**مهم:** التشابه في بعض آليات التنفيذ مش معناه إنهم نفس الـ Pattern.

الـ Data Mapper هدفه الأساسي فصل الـ Domain Model عن الـ Persistence.

## 5. الفرق بين Data Mapper وActive Record

دي أهم مقارنة في المجموعة لحد دلوقتي.

### Active Record

الـ Object مسؤول عن البيانات والمنطق والحفظ.

```plain text
          Database
              |
              v
       +-------------+
       |    Order    |
       +-------------+
       | Data        |
       | confirm()   |
       | save()      |
       | delete()    |
       +-------------+
```

### Data Mapper

الـ Object مسؤول عن المجال فقط، والـ Mapper مسؤول عن التخزين.

```plain text
          Database
              |
              v
       +-------------+
       | OrderMapper |
       +-------------+
       | find()      |
       | insert()    |
       | update()    |
       +-------------+
              |
              v
       +-------------+
       |    Order    |
       +-------------+
       | Data        |
       | confirm()   |
       +-------------+
```

وجه المقارنة	Active Record	Data Mapper
Object يمثل Row	نعم	نعم
Domain Logic	داخل Object	داخل Domain Object
Persistence Logic	داخل Object	داخل Mapper
الارتباط بقاعدة البيانات	مباشر نسبيًا	منفصل
سهولة فصل Domain عن Database	أقل	أكبر
ملاءمة Domain معقد	أقل غالبًا	أكبر غالبًا

الخلاصة:

**Active Record:** الـ Object يعرف يحفظ نفسه.

**Data Mapper:** فيه Object خارجي مسؤول عن حفظ الـ Object.

## 6. علاقته بـ Application Architecture

**أولًا: Layered Architecture**

ممكن نستخدم Data Mapper في طبقة الوصول للبيانات:

```plain text
       Presentation Layer
                |
                v
       Application Layer
                |
                v
          Domain Layer
                |
                v
        Data Access Layer
                |
                v
           Data Mapper
                |
                v
             Database
```

لكن خد بالك: الرسم بيوضح توزيع المسؤوليات، مش بالضرورة اتجاه الاعتماد البرمجي.

**ثانيًا: Clean Architecture**

الـ Data Mapper مناسب جدًا مع Clean Architecture، لأنه بيساعدنا نخلي الـ Domain مستقل عن تفاصيل قاعدة البيانات.

التصور من اليمين للشمال:

```plain text
Database  <---  Data Mapper  <---  Application  <---  Domain
```

لكن فيه تفصيلة مهمة:

الـ Domain مش المفروض يعتمد على الـ Data Mapper.

ممكن الـ Application Layer تعتمد على Repository Interface، والـ Infrastructure تنفذ الـ Repository باستخدام Data Mapper.

## 7. علاقته بـ DDD

هنا لازم نفرق بين مفهومين:

**Repository وData Mapper مش نفس الحاجة.**

Repository	Data Mapper
يقدم واجهة للتعامل مع Aggregates	يحول البيانات بين Objects وDatabase
يتعامل مع Domain Objects	يتعامل مع Mapping
مفهوم مهم في DDD	نمط Data Access
ممكن يستخدم Mapper داخليًا	ممكن يعمل بدون Repository

مثال العلاقة:

```plain text
          Database
              |
              v
          Data Mapper
              |
              v
          Repository
              |
              v
       Application Service
              |
              v
          Domain Model
```

الرسم ده بيشرح التعاون بين المكونات بشكل مبسط، مش اتجاه الاعتماد في Clean Architecture.

الـ Repository ممكن يطلب من الـ Mapper تحميل Order، والـ Mapper يرجع Domain Object جاهز للاستخدام.

## 8. علاقته بـ Odoo

خلينا نربط ده بأودو.

لما تكتب:

```python
order = self.env["sale.order"].browse(10)

order.action_confirm()
```

عندك:

- ORM مسؤول عن Persistence.
- Model بيحتوي على Fields وMethods.
- action_confirm() ينفذ Business Logic.

هل ده معناه إن Odoo بيطبق Data Mapper بشكل مطابق؟

مش بالضرورة.

لأن Odoo Models مرتبطة بالـ ORM، والـ Domain Objects مش منفصلة عنه بنفس الصورة التقليدية اللي شفناها في المثال.

كمان الـ Odoo ORM بيقدم قدرات أوسع زي:

- Recordsets.
- Computed Fields.
- Relations.
- Inheritance.
- Prefetching.
- Caching.

فمينفعش نصنف Odoo كـ Data Mapper لمجرد إن الـ ORM بيحول البيانات بين Python وPostgreSQL.

## 9. إمتى نستخدم Data Mapper؟

استخدمه لما:

- عندك Domain Logic معقدة.
- عايز تفصل الـ Domain عن الـ Database.
- عايز تختبر الـ Domain بدون Database.
- شكل الـ Domain Objects مختلف عن شكل Database Tables.
- عايز تحافظ على استقلالية الـ Domain Model.

---

## الخلاصة النهائية

خلينا نرتب الأربعة Patterns اللي درسناهم، من اليمين للشمال:

Table Data Gateway	Row Data Gateway	Active Record	Data Mapper
Object واحد للجدول	Object لكل Row	Object لكل Row	Object منفصل للـ Mapping
Data Access	Data Access	Data + Logic + Persistence	فصل Domain عن Persistence

**ملحوظة مهمة:** الجدول هنا بيقارن أنماط مختلفة في توزيع المسؤوليات، مش سلسلة تطور لازم كل نظام يمر بيها.

النمط التالي في المجموعة هو **Metadata Mapping**، وهنشوف إزاي نستخدم Metadata لوصف العلاقة بين الـ Objects والجداول بدل كتابة كل تفاصيل الـ Mapping يدويًا.


طيب تمام ممكن بقي نكمل في جزء ال

## Object-Relational Behavioral Patterns

بنفس النمط بتاعنا ومن اليمين للشمال ؟


طبعًا يا صاحبي 😂 نبدأ مجموعة جديدة، ودي من أهم المجموعات في الكتاب، خصوصًا لو عايز تفهم إزاي الـ ORM بينظم التعامل مع الـ Objects أثناء تنفيذ العمليات.

# Object-Relational Behavioral Patterns

قبل ما نبدأ، خلينا نفهم المجموعة دي بتتكلم عن إيه.

إحنا في المجموعة السابقة **Data Source Architectural Patterns** كنا بنركز على إزاي نمثل البيانات ونتعامل مع مصدر البيانات.

أما هنا فتركيزنا على **سلوك الـ Objects أثناء تعاملها مع قاعدة البيانات**.

يعني مثلًا:

- إزاي نجمع التعديلات ونحفظها مع بعض؟
- إزاي نضمن إن نفس السجل ميتعملوش منه Objects مكررة؟
- إزاي نأجل تحميل البيانات لحد ما نحتاجها؟

المجموعة دي في كتاب Fowler بتحتوي على 3 Patterns أساسية:

الترتيب	Pattern	الفكرة الأساسية
1	Unit of Work	تتبع التغييرات وتجميع عمليات الحفظ
2	Identity Map	ضمان وجود نسخة Object واحدة لكل Database Identity داخل سياق معين
3	Lazy Load	تأجيل تحميل البيانات لحد الحاجة إليها

نبدأ بالأول.

---

# 1. Unit of Work Pattern

## 1. المشكلة (Problem)

تخيل عندنا عملية بيع في نظام تجارة إلكترونية.

العميل عمل Order يحتوي على 3 Products.

لما ننفذ العملية، ممكن نحتاج نعمل تعديلات على عدة Objects:

1. إنشاء Order جديد.
1. إنشاء Order Items.
1. تقليل مخزون المنتجات.
1. تحديث رصيد العميل أو بياناته.
1. حفظ كل التعديلات في قاعدة البيانات.

المشكلة إننا لو حفظنا كل Object بشكل مستقل، ممكن يحصل الآتي:

```plain text
حفظ Order             ✓
حفظ Order Items       ✓
تحديث Product Stock   ✓
تحديث Customer        ✗
```

كده العملية نفذت جزئيًا، وده ممكن يسبب بيانات غير متسقة.

إحنا محتاجين آلية تجمع التغييرات كلها، وتتعامل معاها باعتبارها وحدة عمل واحدة.

## 2. الفكرة والحل (Solution)

الـ **Unit of Work** هو Object بيتابع التغييرات اللي حصلت على مجموعة من Objects أثناء Business Transaction، وبعدين بينظم عمليات حفظ التغييرات دي في قاعدة البيانات.

يعني بدل ما كل Object يحفظ نفسه فورًا، الـ Unit of Work يتابع:

- الـ Objects الجديدة (New Objects).
- الـ Objects اللي اتعدلت (Dirty Objects).
- الـ Objects اللي اتحذفت (Deleted Objects).

وعند انتهاء العملية، بنطلب منه تنفيذ commit().

شوف التصور من اليمين للشمال:

```plain text
             Business Operation
                      |
                      v
                 Unit of Work
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
        New         Dirty       Deleted
       Objects      Objects     Objects
          |           |           |
          +-----------+-----------+
                      |
                      v
                Database Changes
                      |
                      v
                    Commit
```

الفكرة إن الـ Unit of Work بيجمع التغييرات، وبعد كده ينظم إرسالها إلى قاعدة البيانات.

**ملحوظة مهمة:** الـ Unit of Work مش مجرد List فيها Objects محتاجة تتحفظ؛ هو كمان مسؤول عن تنظيم دورة حياة التغييرات، وترتيب عمليات الحفظ عند الحاجة، والتعامل مع حدود الـ Transaction.

## 3. مثال Python

خلينا نعمل مثال تعليمي بسيط.

أولًا عندنا Domain Objects:

```python
class Product:
    def __init__(self, product_id, name, quantity):
        self.id = product_id
        self.name = name
        self.quantity = quantity

    def decrease_stock(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if self.quantity < amount:
            raise ValueError("Insufficient stock")

        self.quantity -= amount

class Order:
    def __init__(self, order_id, product_id, quantity):
        self.id = order_id
        self.product_id = product_id
        self.quantity = quantity
```

ثانيًا نعمل Unit of Work:

```python
class UnitOfWork:
    def __init__(self, repository):
        self.repository = repository

        self.new_objects = []
        self.dirty_objects = []
        self.deleted_objects = []

    def register_new(self, obj):
        self.new_objects.append(obj)

    def register_dirty(self, obj):
        self.dirty_objects.append(obj)

    def register_deleted(self, obj):
        self.deleted_objects.append(obj)

    def commit(self):
        try:
            for obj in self.new_objects:
                self.repository.insert(obj)

            for obj in self.dirty_objects:
                self.repository.update(obj)

            for obj in self.deleted_objects:
                self.repository.delete(obj)

            self.repository.commit_transaction()

        except Exception:
            self.repository.rollback_transaction()
            raise
```

ثالثًا: الاستخدام

```python
with repository.transaction():

    uow = UnitOfWork(repository)

    product = repository.get_product(10)

    product.decrease_stock(2)

    order = Order(
        order_id=None,
        product_id=product.id,
        quantity=2
    )

    uow.register_dirty(product)
    uow.register_new(order)

    uow.commit()
```

إيه اللي حصل؟

- المنتج اتعدل في الذاكرة.
- الطلب الجديد اتسجل في الـ Unit of Work.
- المنتج المعدل اتسجل في الـ Unit of Work.
- عند commit()، الـ Unit of Work نظم عمليات الحفظ.
- لو حصل خطأ أثناء الحفظ، بنعمل rollback().

المثال لتوضيح الفكرة، وليس تنفيذًا إنتاجيًا كاملًا. الـ Repository والـ Transaction Manager هنا افتراضيان، كما أن الـ Context Manager يحتاج أن يكون مسؤولًا عن حدود الـ Transaction بصورة متسقة.

## 4. علاقته بأنماط GoF

مفيش GoF Pattern مكافئ مباشرة للـ Unit of Work.

لكن فيه تشابهات في بعض التفاصيل:

GoF Pattern	وجه التشابه	الاختلاف
Command	ممكن يمثل كل تغيير كعملية مستقلة	Command بيغلف طلبًا قابلًا للتنفيذ، أما Unit of Work بيجمع تغييرات متعددة وينظم حفظها
Mediator	ممكن ينسق التعامل بين عدة Objects	Mediator هدفه تنظيم التواصل بين Objects، مش تتبع تغييرات قاعدة البيانات
Observer	ممكن يستخدم لمراقبة التغييرات	Observer هدفه الإشعار بالتغييرات، مش إدارة عملية Persistence

إذن مفيش واحد منهم هو Unit of Work.

## 5. علاقته بـ Application Architecture

### مع Layered Architecture

غالبًا الـ Unit of Work بيكون ضمن طبقة الـ Data Access أو Infrastructure.

```plain text
          Presentation
                |
                v
           Application
                |
                v
             Domain
                |
                v
         Data Access Layer
                |
                v
            Unit of Work
                |
                v
             Database
```

الـ Application Service ممكن تبدأ الـ Unit of Work وتحدد إمتى تعمل Commit أو Rollback.

والـ Domain نفسه مش محتاج يعرف تفاصيل الحفظ.

### مع Clean Architecture

ممكن نستخدمه مع Clean Architecture بصورة طبيعية.

الـ Application Layer تتعامل مع abstraction للـ Unit of Work، والـ Infrastructure توفر التنفيذ الفعلي.

```plain text
Infrastructure  <---  Application  --->  Domain
       |
       v
   Unit of Work
       |
       v
    Database
```

الرسم هنا بيوضح أماكن المسؤوليات، مش اتجاه الـ Dependency بشكل حرفي.

## 6. علاقته بـ DDD

الـ Unit of Work مهم جدًا في تطبيقات DDD.

تخيل إن عندك Aggregate Root اسمه Order، وجواه مجموعة OrderItems.

لما تعدل الطلب، محتاج تحفظ التغييرات المرتبطة بالـ Aggregate بشكل متسق.

الـ Repository ممكن يكون مسؤولًا عن تحميل وحفظ الـ Aggregate، والـ Unit of Work ينظم حفظ التغييرات ضمن Transaction.

لكن خلي بالك من فرق مهم:

**Unit of Work مش هو Aggregate.**

- Aggregate بيحدد حدود الاتساق (Consistency Boundary) في الـ Domain.
- Unit of Work بيتابع التغييرات وينظم حفظها في قاعدة البيانات.

ومش شرط كل Unit of Work يساوي Aggregate واحد؛ ممكن وحدة العمل تحتوي عدة Aggregates ضمن Transaction واحدة، حسب التصميم وقواعد الاتساق المطلوبة.

## 7. علاقته بـ Odoo

هنا عندنا مثال عملي مهم.

في Odoo، لما تنفذ عملية من خلال RPC، الـ Framework بيدير Database Cursor وTransaction مرتبطة بالعملية.

مثلًا:

```python
order = self.env["sale.order"].browse(10)

order.write({
    "note": "Updated note"
})

order.action_confirm()
```

أنت مش بتعمل commit() بعد كل عملية write() بنفسك.

الـ Framework بيدير الـ Transaction، وعند نجاح العملية بيتم اعتماد التغييرات، وعند حدوث Exception غير معالج يتم عمل Rollback للـ Transaction.

وده قريب من مفهوم Unit of Work من ناحية تجميع التغييرات وإدارة اعتمادها أو التراجع عنها.

لكن مهم نفرق:

- الـ Database Transaction بتضمن خصائص ACID على مستوى قاعدة البيانات.
- الـ Unit of Work Pattern مفهوم أوسع على مستوى التطبيق، بيتابع التغييرات على Objects وينظم عمليات حفظها.

كمان Odoo ORM عنده آليات خاصة زي Environment Cache وFlush، فلا يصح اختزال كل آليات الـ ORM في Unit of Work فقط.

---

## 8. الفرق بين Unit of Work وDatabase Transaction

دي نقطة مهمة جدًا وممكن تتسأل في Interview.

Database Transaction	Unit of Work
بتضمن تنفيذ مجموعة عمليات DB كوحدة ذرية	بتتابع تغييرات مجموعة Objects
مسؤولة عن Commit وRollback على مستوى DB	بتنظم عمليات Persistence
مفهوم على مستوى قاعدة البيانات	Pattern على مستوى التطبيق
ممكن تستخدم بدون Unit of Work	غالبًا يعتمد على Transaction عند الحفظ

بمعنى أبسط:

**Unit of Work يحدد إيه اللي محتاج يتحفظ، والـ Transaction تضمن إن عمليات قاعدة البيانات تتم كوحدة واحدة.**

الاتنين بيشتغلوا مع بعض، لكن مش نفس الحاجة.

---

## 9. إمتى نستخدم Unit of Work؟

استخدمه لما:

- عندك Business Operation بتعدل عدة Objects.
- محتاج تجمع عمليات الحفظ بدل تنفيذها بشكل منفصل.
- محتاج Commit أو Rollback منظم.
- عندك Domain Model فيه Objects وعلاقات متعددة.
- عايز تتحكم في Persistence بشكل مركزي.

## الخلاصة

ثبت عندك التعريف ده:

**Unit of Work = Track Changes + Organize Persistence + Coordinate Transaction.**

يعني هو المسؤول عن متابعة التغييرات وتجميع عمليات الحفظ وتنظيم تنفيذها.

والـ Pattern التالي هو **Identity Map**، وده هيكمل معانا الصورة؛ لأننا بعد ما عرفنا إزاي نتابع التغييرات، محتاجين نفهم إزاي نضمن إن نفس السجل في قاعدة البيانات ميتحولش لأكثر من Object داخل نفس سياق العمل.


# 2. Identity Map Pattern

نكمل في مجموعة **Object-Relational Behavioral Patterns** من كتاب Fowler.

النمط ده مرتبط جدًا بالـ ORM، وخصوصًا لما يكون عندك Objects كتير بتتعامل مع نفس البيانات أثناء تنفيذ عملية واحدة.

## 1. المشكلة (Problem)

تخيل عندنا جدول customers في قاعدة البيانات:

id	name	balance
10	Ahmed	5000

وعندنا في التطبيق عمليتين محتاجين يقرؤوا نفس العميل.

```python
customer_1 = load_customer(10)
customer_2 = load_customer(10)
```

لو كل استدعاء عمل Query جديدة وأنشأ Object جديد، هيحصل الآتي:

```python
customer_1 is customer_2

# False
```

مع إن الاتنين بيمثلوا نفس العميل في قاعدة البيانات!

المشكلة الأكبر تظهر لما نعدل أحد الـ Objects:

```python
customer_1.balance -= 1000

print(customer_1.balance)  # 4000
print(customer_2.balance)  # 5000
```

بقى عندنا نسختين مختلفتين من نفس العميل داخل التطبيق.

وده ممكن يؤدي إلى:

- بيانات غير متسقة داخل نفس العملية.
- تكرار تحميل نفس السجل من قاعدة البيانات.
- صعوبة تتبع التعديلات.
- مشاكل عند حفظ نسخ مختلفة من نفس السجل.

إذن إحنا محتاجين نضمن إن كل Database Identity يكون ليها Object واحد فقط داخل سياق العمل المحدد.

## 2. الفكرة والحل (Solution)

الـ **Identity Map** عبارة عن خريطة (Dictionary) بتحتفظ بالـ Objects اللي تم تحميلها من قاعدة البيانات، وبتربط كل Object بهويته.

لما نطلب سجل معين:

1. نبحث عن هويته في الـ Identity Map.
1. لو موجود، نرجع نفس الـ Object.
1. لو مش موجود، نقرأه من قاعدة البيانات.
1. ننشئ Object ونضيفه للخريطة.
1. نرجع الـ Object.

التصور من اليمين للشمال:

```plain text
        Request: Customer ID = 10
                    |
                    v
              Identity Map
                    |
             هل الـ ID موجود؟
               /        \
             نعم         لا
              |           |
              v           v
        Return Same    Load from DB
          Object           |
                           v
                     Create Object
                           |
                           v
                    Store in Map
                           |
                           v
                      Return Object
```

الفكرة الأساسية:

**نفس Database Identity = نفس Object Instance داخل نفس Identity Map.**

وده اسمه Identity Consistency.

## 3. مثال Python

خلينا نطبق الفكرة باستخدام Dictionary.

**أولًا: Domain Object**

```python
class Customer:
    def __init__(self, customer_id, name, balance):
        self.id = customer_id
        self.name = name
        self.balance = balance
```

**ثانيًا: Identity Map**

```python
class IdentityMap:
    def __init__(self):
        self._objects = {}

    def get(self, key):
        return self._objects.get(key)

    def add(self, key, obj):
        self._objects[key] = obj
```

**ثالثًا: Customer Repository**

```python
class CustomerRepository:
    def __init__(self, connection, identity_map):
        self.connection = connection
        self.identity_map = identity_map

    def find_by_id(self, customer_id):

        # 1. Check Identity Map
        customer = self.identity_map.get(customer_id)

        if customer is not None:
            return customer

        # 2. Load from Database
        cursor = self.connection.execute(
            """
            SELECT id, name, balance
            FROM customers
            WHERE id = ?
            """,
            (customer_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        # 3. Create Object
        customer = Customer(*row)

        # 4. Register Object
        self.identity_map.add(customer_id, customer)

        return customer
```

**رابعًا: الاستخدام**

```python
identity_map = IdentityMap()

repository = CustomerRepository(
    connection,
    identity_map
)

customer_1 = repository.find_by_id(10)
customer_2 = repository.find_by_id(10)

print(customer_1 is customer_2)
# True
```

لاحظ إننا في المرة الثانية رجعنا نفس الـ Object من الذاكرة، ومحتاجناش نعمل Query جديدة.

كمان:

```python
customer_1.balance -= 1000

print(customer_2.balance)
# 4000
```

لأن الاتنين بيشاوروا على نفس الـ Object.

المثال تعليمي. في تطبيق حقيقي، لازم نراعي نطاق حياة الـ Identity Map، وتعدد قواعد البيانات أو الشركات، والـ Composite Keys، والتزامن.

## 4. علاقته بأنماط GoF

مفيش GoF Pattern مكافئ مباشرة للـ Identity Map.

لكن ممكن نلاحظ تشابهات:

GoF Pattern	وجه التشابه	الاختلاف
Flyweight	إعادة استخدام Objects بدل إنشاء نسخ متكررة	Flyweight هدفه مشاركة الحالة لتقليل استهلاك الذاكرة
Singleton	ممكن يكون فيه Identity Map واحدة داخل Context معين	Singleton هدفه ضمان Instance واحدة من Class، مش Instance واحدة لكل Database Identity
Proxy	ممكن يستخدم Object وسيط للوصول إلى Object حقيقي	Proxy بيحل مشكلة التحكم في الوصول، مش منع تكرار تمثيل السجل

أهم تشابه هنا مع Flyweight هو إعادة الاستخدام، لكن الـ Intent مختلف.

## 5. علاقته بـ Application Architecture

### مع Layered Architecture

غالبًا الـ Identity Map بتكون ضمن Data Access / Persistence Infrastructure.

```plain text
       Presentation Layer
                |
                v
       Application Layer
                |
                v
          Domain Layer
                |
                v
        Data Access Layer
                |
                v
          Identity Map
                |
                v
             Database
```

الـ Repository أو Data Mapper ممكن يستخدم Identity Map داخليًا.

### مع Clean Architecture

ممكن تستخدم Identity Map في الـ Infrastructure من غير ما الـ Domain يعرف بوجودها.

```plain text
        Infrastructure
        +----------------+
        |  Repository    |
        |  Identity Map  |
        |  Data Mapper   |
        +----------------+
                |
                v
             Database
```

الـ Domain يستقبل Domain Objects عادية، ومش محتاج يعرف إزاي الـ Infrastructure بتمنع تكرارها.

## 6. علاقته بـ DDD

هنا عندنا نقطة مهمة.

في DDD، الـ Entity بتتميز بوجود Identity.

يعني ممكن يكون عندك:

```python
customer_1 = Customer(10, "Ahmed", 5000)
customer_2 = Customer(10, "Ahmed", 5000)
```

رغم إن الاتنين بيمثلوا نفس العميل من ناحية الـ Database ID، فهما مش نفس الـ Object Instance.

```python
customer_1 is customer_2

# False
```

الـ Identity Map بتحل المشكلة دي داخل سياق معين عن طريق إعادة نفس الـ Instance.

لكن لازم نفرق بين:

- **Entity Identity:** هوية الكيان في الـ Domain.
- **Object Identity:** هوية نسخة الـ Object في الذاكرة.
- **Database Identity:** المفتاح اللي بيحدد السجل في قاعدة البيانات.

الـ Identity Map بتربط بين الـ Database Identity والـ Object Instance.

كمان Identity Map مش هي Aggregate، ومش هي Repository، لكنها ممكن تكون جزءًا من تنفيذ Repository.

## 7. علاقته بـ Odoo

هنا المثال العملي مهم جدًا.

في Odoo عندك:

```python
customer_1 = self.env["res.partner"].browse(10)
customer_2 = self.env["res.partner"].browse(10)
```

الاتنين بيمثلوا نفس السجل، لكن خلي بالك:

**مينفعش نعتمد على إن customer_1 is customer_2 هترجع True.**

لأن Odoo Recordsets ليها سلوك خاص، وممكن تنشئ Recordset Objects مختلفة بتشير لنفس السجل.

الـ Odoo ORM عنده آليات Cache وPrefetch داخل الـ Environment، وده بيقلل تكرار قراءة البيانات وبيحافظ على إدارة البيانات داخل سياق العمل.

لكن الـ Recordset والـ Identity Map مش نفس الحاجة.

الـ Identity Map Pattern بيضمن إعادة نفس الـ Object Instance لنفس الهوية داخل نطاق محدد، بينما Odoo عنده آليات ORM أوسع لإدارة الـ Recordsets والـ Cache.

## 8. الفرق بين Identity Map وUnit of Work

الاتنين غالبًا بيشتغلوا مع بعض، لكن كل واحد بيحل مشكلة مختلفة.

Unit of Work	Identity Map
يتابع التغييرات	يمنع تكرار تمثيل نفس الهوية
يجمع New Objects	يحتفظ بالـ Loaded Objects
يتابع Dirty Objects	يرجع نفس الـ Instance
يتابع Deleted Objects	يقلل تكرار تحميل السجلات
ينظم عمليات الحفظ	يحافظ على Object Identity

تصور التعاون بينهم:

```plain text
          Application
               |
               v
          Repository
               |
       +-------+-------+
       |               |
       v               v
  Identity Map     Unit of Work
       |               |
       |               |
       v               v
       +-------+-------+
               |
               v
            Database
```

ببساطة:

- Identity Map بتقول: هل أنا حملت الـ Object ده قبل كده؟
- Unit of Work بتقول: إيه التغييرات اللي حصلت على الـ Objects وعايزين نحفظها؟

## 9. إمتى نستخدم Identity Map؟

استخدمه لما:

- نفس السجلات ممكن يتم تحميلها أكثر من مرة أثناء العملية.
- عندك Objects مرتبطة ببعضها وبتشير لنفس Entities.
- عايز تحافظ على اتساق الـ Object Instances.
- عايز تقلل تكرار عمليات القراءة.
- بتستخدم ORM أو Data Mapper فيه إدارة صريحة للـ Object Lifecycle.

**خد بالك:** لازم تحدد عمر الـ Identity Map بعناية. غالبًا بتكون مرتبطة بـ Session أو Unit of Work أو Request، مش Global Map تستمر طول عمر التطبيق؛ لأن الاحتفاظ بالـ Objects لفترة طويلة ممكن يسبب Stale Data واستهلاك ذاكرة زائد.

---

## الخلاصة

Pattern	الفكرة الأساسية
Unit of Work	تجميع التغييرات وتنظيم حفظها
Identity Map	Object واحد لكل Database Identity داخل Context
Lazy Load	تأجيل تحميل البيانات لوقت الحاجة

والنمط التالي والأخير في المجموعة دي هو **Lazy Load Pattern**.

وده هيجاوب على سؤال مهم جدًا:

إزاي نحمّل Order من قاعدة البيانات من غير ما نحمّل معاه كل Order Items والـ Customer والـ Payments، إلا لما نحتاجهم فعلًا؟


معاك حق، المشكلة مش في لغة الشرح، المشكلة في اتجاه ترتيب العناصر نفسها. خليني ألتزم بشكل أوضح من هنا.

هعيد كتابة أهم رسومات المقارنة السابقة، بحيث تبدأ القراءة من اليمين:

## Identity Map — اتجاه التنفيذ

```plain text
             Request: Customer ID = 10
                          |
                          v
                    Identity Map
                          |
                   هل الـ ID موجود؟
                      /       \
                    نعم        لا
                     |          |
                     v          v
                نفس الـ Object  Database
                                  |
                                  v
                             إنشاء Object
                                  |
                                  v
                           تخزينه في Map
                                  |
                                  v
                             إرجاع Object
```

## الفرق بين Unit of Work وIdentity Map

Identity Map	Unit of Work
تمنع تكرار تمثيل نفس السجل	تجمع التغييرات
تحتفظ بالـ Objects المحملة	تتابع Objects الجديدة
ترجع نفس الـ Instance	تتابع Objects المعدلة
تحافظ على Object Identity	تنظم عمليات الحفظ

## التعاون بينهما

```plain text
       Application
             |
             v
         Repository
             |
       +-----+-----+
       |           |
       v           v
  Identity Map   Unit of Work
       |           |
       +-----+-----+
             |
             v
          Database
```

**من هنا ورايح:** هخلي الرسومات تبدأ من اليمين، والجداول أرتب أعمدتها بحيث أول مفهوم يكون في أقصى اليمين، والأكواد تفضل بالاتجاه الطبيعي بتاعها.

ومش هعتبر إن كتابة العربي وحدها كفاية لتحقيق اتجاه القراءة اللي طلبته.


تمام يا صاحبي 😂 نكمل آخر Pattern في مجموعة **Object-Relational Behavioral Patterns** من كتاب Fowler:

# 3. Lazy Load

(Object-Relational Behavioral Pattern)

## 1. المشكلة (Problem)

تخيل عندك Order وفيه 1000 OrderLine، وكل OrderLine مرتبطة بـ Product، وكل Product عنده تفاصيل ومعلومات إضافية.

لما تعمل Load للـ Order، هل لازم تحمل كل البيانات المرتبطة بيه فورًا؟

مش بالضرورة.

ممكن تكون محتاج تعرض رقم الطلب وإجمالي قيمته فقط، ومش محتاج تفاصيل المنتجات أصلًا.

لو حملت كل البيانات من البداية، هتدفع تكلفة:

- Queries إضافية على قاعدة البيانات.
- استهلاك Memory أكبر.
- وقت أطول لتحميل الـ Object.
- نقل بيانات مش محتاجها في العملية الحالية.

**إذن المشكلة:** إزاي نخلي الـ Object متاح للاستخدام، من غير ما نحمل كل البيانات المرتبطة بيه من البداية؟

## 2. الفكرة والحل (Solution)

فكرة Lazy Load ببساطة:

**أجّل تحميل البيانات لحد اللحظة اللي أحتاج أستخدمها فيها.**

خلينا نشوف التدفق:

```plain text
Database  <---  Lazy Loading  <---  Order
                                      |
                               Access order.items
                                      |
                              Load items from DB
```

بمعنى إن:

1. بنعمل Load للـ Order من غير تحميل كل الـ OrderLine.
1. لما نطلب order.items لأول مرة، يحصل تحميل للبيانات.
1. البيانات تتحفظ في الـ Object أو الـ Cache.
1. الوصول التالي يستخدم البيانات المحملة بدل إعادة تحميلها.

لاحظ إن Lazy Load مش معناه إن البيانات مش هتتحمل؛ معناه إن **توقيت التحميل اتأجل**.

## 3. طرق تنفيذ Lazy Load عند Fowler

Fowler بيشرح أكتر من طريقة لتنفيذ الفكرة، ودي مهمة لأن Lazy Load مش مرتبط بتنفيذ واحد.

### A. Lazy Initialization

بنبدأ الـ Attribute بقيمة غير محملة، زي None، وأول مرة نحتاجها نحملها.

```python
class Order:
    def __init__(self, order_id, repository):
        self.id = order_id
        self.repository = repository
        self._items = None

    @property
    def items(self):
        if self._items is None:
            self._items = self.repository.load_items(self.id)

        return self._items
```

الاستخدام:

```python
order = Order(10, repository)

# لسه مفيش تحميل للـ items

items = order.items

# هنا حصل التحميل لأول مرة

items = order.items

# هنا استخدمنا البيانات المحملة
```

**الفكرة:** الـ Object نفسه مسؤول عن اكتشاف إن البيانات لم تُحمّل بعد، وتحميلها عند أول Access.

### B. Virtual Proxy

هنا بنستخدم Object بديل يمثل الـ Object الحقيقي.

الـ Proxy يستقبل الطلبات، وعند أول استخدام يحمل الـ Real Object ويوجه الطلبات إليه.

```plain text
Real Object  <---  Virtual Proxy  <---  Client
                       |
                  First Access
                       |
                  Load Real Object
```

مثال مبسط:

```python
class Product:
    def __init__(self, product_id, name):
        self.id = product_id
        self.name = name

class ProductProxy:
    def __init__(self, product_id, repository):
        self.product_id = product_id
        self.repository = repository
        self._real_product = None

    def _load(self):
        if self._real_product is None:
            self._real_product = self.repository.get(
                self.product_id
            )

    @property
    def name(self):
        self._load()
        return self._real_product.name
```

الـ Client بيتعامل مع ProductProxy وكأنه بيتعامل مع Product، لكن التحميل الحقيقي بيحصل عند الحاجة.

### C. Value Holder

هنا بنستخدم Object صغير يحتفظ بالقيمة أو بطريقة الحصول عليها، ويتولى تحميل القيمة عند أول طلب.

```python
class ValueHolder:
    def __init__(self, loader):
        self.loader = loader
        self._value = None
        self._loaded = False

    @property
    def value(self):
        if not self._loaded:
            self._value = self.loader()
            self._loaded = True

        return self._value
```

الاستخدام:

```python
items_holder = ValueHolder(
    lambda: repository.load_items(10)
)

items = items_holder.value
```

الفرق هنا إننا فصلنا مسؤولية تأجيل التحميل في Object مستقل اسمه ValueHolder.

### D. Ghost

الـ Object بيتولد في البداية بحالة جزئية، مثل الـ ID وبعض البيانات الأساسية، ولما نحتاج بياناته الكاملة يتم تحميلها.

مثلاً:

```python
class Customer:
    def __init__(self, customer_id, repository):
        self.id = customer_id
        self.repository = repository
        self._loaded = False
        self._name = None
        self._email = None

    def _load(self):
        if not self._loaded:
            data = self.repository.get(self.id)

            self._name = data["name"]
            self._email = data["email"]

            self._loaded = True

    @property
    def name(self):
        self._load()
        return self._name

    @property
    def email(self):
        self._load()
        return self._email
```

الـ Customer موجود بالفعل، لكن بياناته مش كاملة.

ملاحظة: الطرق الأربع دي أساليب تنفيذ لـ Lazy Load، وليست أربعة Patterns مستقلة ضمن مجموعة Fowler.

---

## 4. علاقته بـ GoF Patterns

أقرب Pattern في GoF هو:

**Proxy Pattern**

Proxy Patternلكن لازم نفرّق بين الـ Intent بتاع الاتنين.

- **Lazy Load:** هدفه تأجيل تحميل البيانات لوقت الحاجة.
- **Proxy:** هدفه توفير بديل يتحكم في الوصول إلى Object آخر.

ليه مش بديل مباشر؟

لأن Lazy Load ممكن يتنفذ من غير Proxy أصلًا، زي Lazy Initialization.

وفي المقابل، Proxy ممكن يستخدم لأهداف تانية غير Lazy Loading، زي Remote Proxy وProtection Proxy.

إذن العلاقة:

**Virtual Proxy هو أحد أساليب تنفيذ Lazy Load، لكن Lazy Load مش بالضرورة Proxy.**

---

## 5. الفرق بين Lazy Loading وEager Loading

خلينا نقارن الفكرتين.

**Lazy Loading:**

```plain text
Load Order  <---  Access Items  <---  Load Items
```

بنحمل الـ Order الأول، وبعد كده الـ Items عند الحاجة.

**Eager Loading:**

```plain text
Load Order + Items  <---  Access Order
```

بنحمل الـ Order والـ Items مع بعض من البداية.

المقارنة	Lazy Loading	Eager Loading
توقيت التحميل	عند الحاجة	من البداية
التكلفة الأولية	أقل غالبًا	أعلى غالبًا
عدد Queries	ممكن يزيد	ممكن يقل
استهلاك الذاكرة	أقل مبدئيًا	أكبر مبدئيًا
الخطر الشائع	N+1 Queries	تحميل بيانات غير مطلوبة

### خد بالك من مشكلة N+1

افترض عندك 100 Order، وكل Order عنده Items.

لو عملت Query لتحميل Orders، وبعد كده كل مرة توصل فيها لـ order.items يحصل Query منفصل:

```plain text
Orders Query
     |
     +---- Order 1 Items Query
     |
     +---- Order 2 Items Query
     |
     +---- Order 3 Items Query
     |
     +---- ...
     |
     +---- Order 100 Items Query
```

بدل Query واحدة أو عدد محدود من Queries، ممكن توصل إلى 101 Query!

وده سبب إن Lazy Loading مش دائمًا أفضل من Eager Loading.

الحل أحيانًا يكون Batch Loading أو Prefetching.

---

## 6. علاقته بالأنماط السابقة

مهم جدًا نفصل مسؤوليات الثلاثة:

**Unit of Work**

مسؤوليته تتبع التغييرات وتنظيم عملية الحفظ.

**Identity Map**

مسؤوليتها ضمان إن نفس Database Identity ترجع نفس Object Instance داخل نطاق معين.

**Lazy Load**

مسؤوليته تأجيل تحميل البيانات لحد الحاجة إليها.

ممكن الثلاثة يشتغلوا مع بعض داخل ORM واحد، لكن كل واحد بيحل مشكلة مختلفة.

---

## 7. علاقته بالمعمارية وDDD وClean Architecture

**Application Architecture**

Lazy Load مش Application Architecture Pattern، لكنه سلوك متعلق بطريقة الوصول إلى البيانات وتحميل الـ Objects، وغالبًا بيكون جزء من Persistence Layer أو ORM.

**Clean Architecture**

ممكن الـ Infrastructure Layer تنفذ Lazy Loading باستخدام ORM أو Proxy.

لكن خلي بالك: لو الـ Domain Objects بقت معتمدة على Database Session أو ORM Proxies بشكل مباشر، ممكن يحصل Coupling غير مرغوب فيه.

**DDD**

ممكن تستخدم Lazy Loading لتحميل Relationships أو Collections، لكن لازم تحترم Aggregate Boundaries.

مثلًا: مش معنى إن Order عنده علاقة بـ Customer إنك لازم تحمل كل بيانات الـ Customer وكل العلاقات التابعة ليه.

الـ Aggregate Root هو نقطة الدخول للتعامل مع الـ Aggregate، وLazy Loading مش مبرر لتجاوز الحدود دي.

---

## 8. علاقته بـ Odoo

خلينا ناخد مثال:

```python
order = self.env["sale.order"].browse(10)

lines = order.order_line
```

هنا عندك علاقة بين sale.order و sale.order.line.

الـ Odoo ORM عنده آليات للتحميل والـ Cache والـ Prefetch، وبالتالي ممكن البيانات المرتبطة تتحمل عند الوصول إليها أو بشكل جماعي حسب السياق.

لكن مهم جدًا:

- مش كل Access لحقل بيعمل SQL Query فورًا.
- الـ Prefetch ممكن يحمل بيانات سجلات أخرى مع السجل الحالي.
- الـ Cache ممكن يمنع تكرار القراءة من قاعدة البيانات.
- مش دقيق نقول إن كل Odoo Field يستخدم Lazy Load حصريًا.

---

## 9. إمتى تستخدم Lazy Load؟

استخدمه لما:

- عندك بيانات مرتبطة حجمها كبير.
- مش كل العمليات بتحتاج البيانات المرتبطة.
- تكلفة التحميل الأولي عالية.
- عندك تحكم في Session/Connection Lifetime.

وتجنب الاعتماد عليه بشكل أعمى لما:

- عندك Loop على مجموعة Records.
- كل العمليات تقريبًا محتاجة العلاقات.
- ممكن ينتج عنه N+1 Queries.
- الـ Objects ممكن تعيش بعد انتهاء الـ Database Session.

---

# خلصنا Object-Relational Behavioral Patterns 🎯

## ملخص المجموعة

**1. Unit of Work**

Track Changes & Organize Persistence

---

**2. Identity Map**

Maintain Object Identity

---

**3. Lazy Load**

Defer Object/Data Loading

وبكده خلصنا المجموعة دي بالكامل.

**الخطوة التالية في الكتاب:** Object-Relational Structural Patterns، ودي مجموعة مختلفة عن Behavioral Patterns، وهنبدأها من أول Pattern فيها: **Identity Field**.


يلا بينا يا هندسة 😂 نبدأ المجموعة الجديدة في كتاب **Patterns of Enterprise Application Architecture (PoEAA)**.

# Object-Relational Structural Patterns

المجموعة دي مختلفة عن المجموعة السابقة.

في المجموعة السابقة كنا بنتكلم عن سلوك الـ Objects أثناء التعامل مع قاعدة البيانات، زي:

- Unit of Work
- Identity Map
- Lazy Load

أما هنا فهنركز على **إزاي نمثل العلاقات والتركيب والوراثة بين الـ Objects داخل قاعدة البيانات العلائقية**.

يعني المشكلة الأساسية:

إزاي نحوّل الـ Object Structure إلى Relational Database Structure والعكس؟

---

# 1. Identity Field

(Object-Relational Structural Pattern)

## 1. المشكلة (Problem)

تخيل عندك Class اسمه Customer:

```python
class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
```

وعندك Database Table:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150)
);
```

لاحظ إن عندنا اختلاف:

- الـ Database عندها id بيمثل هوية كل Row.
- الـ Object عنده name و`email`، لكن مفيش Field بيمثل هوية السجل في قاعدة البيانات.

طيب لو عندي عميلين بنفس الاسم والإيميل، إزاي أميز كل واحد عن التاني؟

ولو حملت Customer من قاعدة البيانات وعدلت اسمه، إزاي أعرف أنهي Row المفروض أعمل لها UPDATE؟

هنا بتظهر المشكلة:

**إزاي نربط هوية الـ Object بهوية الـ Row داخل قاعدة البيانات؟**

## 2. الفكرة والحل (Solution)

الحل إننا نضيف Field داخل الـ Object يحتفظ بالـ Database Identity، وغالبًا بيكون هو الـ Primary Key.

يعني بدل ما الـ Object يحتوي على بيانات العميل فقط، هنضيف id.

```python
class Customer:
    def __init__(self, customer_id, name, email):
        self.id = customer_id
        self.name = name
        self.email = email
```

وبكده أصبح عندنا تطابق واضح:

```plain text
Database Row  <---  Identity Field  <---  Customer Object
     id                    id
```

الـ id الموجود في الـ Object هو اللي بيربطه بالسجل المقابل في قاعدة البيانات.

## 3. مثال عملي

خلينا نشوف دورة حياة الـ Object.

**أولًا: تحميل Customer من Database**

```python
def get_customer(customer_id):
    row = db.execute(
        "SELECT id, name, email FROM customers WHERE id = %s",
        [customer_id]
    ).fetchone()

    if row is None:
        return None

    return Customer(
        customer_id=row["id"],
        name=row["name"],
        email=row["email"]
    )
```

**ثانيًا: تعديل بيانات العميل**

```python
customer = get_customer(10)

customer.name = "Saleh"
```

**ثالثًا: حفظ التعديل**

```python
def save_customer(customer):
    db.execute(
        """
        UPDATE customers
        SET name = %s, email = %s
        WHERE id = %s
        """,
        [
            customer.name,
            customer.email,
            customer.id
        ]
    )
```

لاحظ إننا استخدمنا customer.id لتحديد السجل المطلوب تعديله.

من غير الـ Identity Field، هنحتاج آلية أخرى لتحديد السجل، وده ممكن يكون معقدًا وغير موثوق.

---

## 4. علاقته بـ GoF Patterns

هل فيه Pattern مباشر في GoF؟

**لا، مفيش GoF Pattern مكافئ مباشر.**

لأن Identity Field مش بيحل مشكلة تصميم سلوك أو تعاون Objects، لكنه بيحل مشكلة Mapping بين هوية الـ Object وهوية الـ Database Row.

ممكن تلاقي تشابه في بعض الاستخدامات مع:

- Flyweight: بسبب فكرة الهوية وإعادة استخدام Objects، لكن Intent مختلف.
- Proxy: ممكن يستخدم Identity Field لتحديد الـ Object الحقيقي، لكن ده مش جوهر Proxy.

إذن مفيش داعي نربطه غصبًا بأي GoF Pattern.

## 5. الفرق بين Identity Field وIdentity Map

دي نقطة مهمة جدًا لأننا لسه شارحين Identity Map.

**Identity Field:**

الـ Object نفسه بيحتفظ بالـ ID الخاص به.

**Identity Map:**

بتحتفظ بخريطة تربط Database Identity بالـ Object Instance.

مثال توضيحي:

```plain text
                  Identity Map
                /              \
          Customer ID 10     Customer ID 20
                |                 |
                v                 v
          Customer Object   Customer Object
                |                 |
             id = 10           id = 20
```

كل Customer عنده Identity Field، والـ Identity Map بتستخدم الهوية دي للوصول إلى الـ Object المناسب.

يعني:

- Identity Field = تخزين الهوية داخل الـ Object.
- Identity Map = إدارة وربط الـ Object Instances باستخدام الهوية.

الاتنين ممكن يشتغلوا مع بعض، لكن مش نفس الـ Pattern.

---

## 6. علاقته بـ Application Architecture وClean Architecture

Identity Field مش Application Architecture Pattern.

هو Pattern على مستوى الـ Object-Relational Mapping.

في Clean Architecture، ممكن يكون الـ ID موجود داخل الـ Domain Entity:

```python
class Customer:
    def __init__(self, customer_id, name):
        self.id = customer_id
        self.name = name
```

لكن خد بالك من نقطة مهمة:

مش شرط الـ Domain Identity تكون هي نفسها Database Primary Key.

مثلًا ممكن يكون عندك:

- Domain Identity: UUID يمثل هوية العميل داخل النظام.
- Database Primary Key: رقم داخلي BIGINT.

المهم إن الـ Domain يحدد مفهوم الهوية الخاص به، والـ Infrastructure تتولى Mapping مع قاعدة البيانات.

## 7. علاقته بـ DDD

في DDD، الـ Entity بتتميز بالهوية (Identity)، مش بمجرد قيم الخصائص.

مثلًا:

```python
customer_1 = Customer(id=10, name="Saleh")
customer_2 = Customer(id=20, name="Saleh")
```

رغم إن الاسمين متطابقين، فهما كيانان مختلفان بسبب اختلاف الهوية.

وده بيفرق الـ Entity عن Value Object.

- Entity: هويتها أساسية في تحديدها.
- Value Object: بتتحدد من خلال قيمها.

لكن Identity Field في Fowler تحديدًا بيتكلم عن تمثيل هوية الـ Object في الـ Database Mapping، مش عن تعريف Entity في DDD كله.

## 8. علاقته بـ Odoo

في Odoo، عندك الـ id الموجود في كل Model تقريبًا:

```python
order = self.env["sale.order"].browse(10)

print(order.id)
```

الـ id هنا بيمثل هوية السجل.

وده مثال واضح على فكرة Identity Field.

لكن لازم نفرق بين وجود id وبين تفاصيل الـ ORM؛ Odoo عنده طبقة ORM كاملة بتدير الـ Recordsets والـ Cache والـ Relations، وIdentity Field مجرد مفهوم واحد داخل الصورة الأكبر.

---

## 9. إمتى نستخدم Identity Field؟

لما تكون محتاج:

- تمييز كل Object عن غيره بهوية ثابتة.
- ربط الـ Object بسجل محدد في قاعدة البيانات.
- تنفيذ UPDATE وDELETE على السجل الصحيح.
- الحفاظ على هوية الـ Entity خلال عمليات التحميل والحفظ.

**الخلاصة:**

Identity Field بيحل مشكلة:

> How can an object identify its corresponding database row?

---

## النمط التالي

**2. Foreign Key Mapping**

وده هيكون مهم جدًا؛ لأننا بعد ما عرفنا إزاي نربط Object بسجل في قاعدة البيانات، هنشوف إزاي نمثل العلاقات بين الـ Objects باستخدام Foreign Keys.


نكمل يا صاحبي. وصلنا للنمط الثاني في مجموعة **Object-Relational Structural Patterns** من كتاب Fowler.

# 2. Foreign Key Mapping

(Object-Relational Structural Pattern)

## 1. المشكلة (Problem)

تخيل عندنا نظام Sales، وفيه Customer و Order.

العلاقة في عالم الـ Objects بالشكل ده:

- Customer عنده Orders.
- كل Order تابع لـ Customer واحد.

ممكن نمثل ده في Python بالشكل التالي:

```python
class Customer:
    def __init__(self, customer_id, name):
        self.id = customer_id
        self.name = name
        self.orders = []

class Order:
    def __init__(self, order_id, customer):
        self.id = order_id
        self.customer = customer
```

لاحظ إن الـ Order عنده Reference للـ Customer Object نفسه.

لكن في Relational Database مفيش مفهوم Object Reference بنفس الشكل.

إحنا عندنا Tables وRows وColumns.

فإزاي نمثل العلاقة دي داخل قاعدة البيانات؟

## 2. الفكرة والحل (Solution)

بنستخدم **Foreign Key** علشان نمثل العلاقة بين السجلات في قاعدة البيانات.

خلينا نشوف التصميم:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id)
);
```

لاحظ إن orders.customer_id بيشير إلى customers.id.

العلاقة أصبحت:

```plain text
Customer Object  <---  Order Object
       |                    |
       |                    |
       v                    v
customers Table  <---  orders Table
                         customer_id
```

الـ Object عنده Reference للـ Object الآخر، بينما قاعدة البيانات عندها Foreign Key يربط الـ Rows ببعضها.

**دي هي الفكرة الأساسية للنمط: تحويل العلاقة بين الـ Objects إلى علاقة Foreign Key بين الـ Database Rows.**

---

## 3. أنواع العلاقات (Relationships)

خلينا نشوف إزاي نستخدم Foreign Key Mapping مع أشهر العلاقات.

### A. One-to-Many

مثال: Customer عنده Orders كتير، وكل Order تابع لـ Customer واحد.

العلاقة:

```plain text
Customer 1  <---  N Orders
```

في قاعدة البيانات، الـ Foreign Key بيتحط في جدول الطرف Many:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id)
);
```

ليه في جدول orders؟

لأن كل Order محتاج يحتفظ بهوية الـ Customer الخاص بيه.

### B. Many-to-One

دي نفس العلاقة السابقة لكن من منظور الطرف الآخر.

الـ Order الواحد مرتبط بـ Customer واحد، لكن Customers ممكن يكون عندهم Orders كتير.

يعني:

```plain text
Customer  <---  Order
   1            N
```

مفيش تصميم Database جديد هنا؛ هي نفس علاقة One-to-Many، لكن بنبص عليها من الاتجاه العكسي.

### C. One-to-One

مثال: Employee عنده EmployeeProfile واحد.

ممكن نستخدم Foreign Key مع Unique Constraint:

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE employee_profiles (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER UNIQUE
        REFERENCES employees(id)
);
```

وجود UNIQUE بيضمن إن كل Employee مرتبط بحد أقصى Profile واحد.

ولو عايزين علاقة واحد لواحد إلزامية من الطرفين، لازم نصمم الـ Constraints بما يضمن المشاركة المطلوبة، مش مجرد Foreign Key وUnique في اتجاه واحد.

### D. Many-to-Many

مثال: Student ممكن يسجل في Courses كتير، والـ Course ممكن يكون فيه Students كتير.

هنا مش هنقدر نحط Foreign Key واحد في أي جدول ويحل العلاقة بالكامل.

بنحتاج جدول وسيط اسمه **Association Table** أو **Join Table**.

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE student_courses (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);
```

العلاقة:

```plain text
Students  <---  Student_Courses  <---  Courses
```

الجدول الوسيط بيحتفظ بعلاقات الطرفين.

وممكن كمان يحتوي بيانات إضافية، زي تاريخ التسجيل أو الدرجة.

---

## 4. علاقته بـ GoF Patterns

هل يوجد GoF Pattern مكافئ مباشر؟

**لا.**

Foreign Key Mapping مش هدفه تنظيم سلوك Objects أو إنشاء Objects أو التحكم في التعاون بينها.

هو أسلوب Mapping بين العلاقات في Object Model والعلاقات في Relational Database.

ممكن تلاحظ تشابهًا سطحيًا مع Adapter لأن فيه تحويل بين شكلين مختلفين، لكن ده مش Intent بتاع Adapter.

---

## 5. الفرق بين Foreign Key Mapping وData Mapper

دي نقطة مهمة.

**Data Mapper:**

مسؤول عن نقل البيانات بين Domain Objects وDatabase مع الحفاظ على استقلال الطرفين.

**Foreign Key Mapping:**

بيحدد إزاي نمثل العلاقات بين Objects باستخدام Foreign Keys في قاعدة البيانات.

يعني ممكن Data Mapper يستخدم Foreign Key Mapping أثناء تحويل العلاقات، لكن الاتنين مش نفس المستوى من المسؤولية.

---

## 6. علاقته بـ Application Architecture وClean Architecture

Foreign Key Mapping مش Application Architecture Pattern.

هو Pattern في طبقة الـ Persistence / Data Mapping.

في Clean Architecture:

- الـ Domain ممكن يحتوي Order عنده Reference إلى Customer أو يحتفظ بـ customer_id حسب التصميم.
- الـ Infrastructure مسؤولة عن تحويل العلاقات إلى Foreign Keys.
- الـ Database بتنفذ Referential Integrity باستخدام Constraints.

مهم: مش لازم الـ Domain Object يعرف إن العلاقة متنفذة عن طريق Foreign Key أصلًا.

---

## 7. علاقته بـ DDD

في DDD، لازم نفرق بين العلاقات في الـ Domain Model والعلاقات في الـ Database.

مثلًا:

```python
class Order:
    def __init__(self, order_id, customer_id):
        self.id = order_id
        self.customer_id = customer_id
```

ممكن نستخدم customer_id بدل ما نحمل Customer Object بالكامل.

وده بيكون مفيد خصوصًا لما Customer و`Order` تابعين لـ Aggregates مختلفة.

في DDD، غالبًا بنشير إلى Aggregate آخر باستخدام هويته بدل الاحتفاظ بكامل الـ Object Graph.

لكن خد بالك:

**Foreign Key Mapping مش هو Aggregate Design.**

الـ Foreign Key بيحدد علاقة على مستوى قاعدة البيانات، أما Aggregate Boundaries فبتحدد حدود الاتساق والتحكم في التغييرات على مستوى الـ Domain.

---

## 8. علاقته بـ Odoo

خلينا نربط الكلام بـ Odoo.

### Many2one

```python
class SaleOrder(models.Model):
    _inherit = "sale.order"

    customer_id = fields.Many2one(
        "res.partner",
        string="Customer"
    )
```

دي بتمثل علاقة Many-to-One على مستوى الـ ORM، وبتُخزن عادةً كـ Foreign Key في جدول sale_order.

### One2many

```python
class Partner(models.Model):
    _inherit = "res.partner"

    sale_order_ids = fields.One2many(
        "sale.order",
        "partner_id",
        string="Orders"
    )
```

لاحظ إن One2many مش معناه وجود عمود إضافي في جدول res_partner.

هو تمثيل عكسي للعلاقة، والـ Foreign Key موجود في جدول sale_order عن طريق partner_id.

### Many2many

```python
class Student(models.Model):
    _name = "school.student"

    course_ids = fields.Many2many(
        "school.course",
        string="Courses"
    )
```

الـ ORM عادةً بينشئ Association Table لتمثيل العلاقة.

إذن في Odoo:

- Many2one ← Foreign Key.
- One2many ← Reverse relation مبنية على Foreign Key موجود في الطرف الآخر.
- Many2many ← Association Table.

دي أمثلة عملية واضحة على فكرة Foreign Key Mapping، مع ملاحظة إن Odoo ORM بيقدم طبقة أعلى من مجرد تعريف الـ Foreign Keys.

---

## 9. ملخص النمط

السؤال الذي يجيب عنه Foreign Key Mapping:

> How do you map relationships between objects to foreign keys in a relational database?

الفكرة الأساسية:

**Object References في عالم الـ Objects ← Foreign Keys في عالم الـ Relational Database.**

والأنماط اللي خلصناها لحد دلوقتي:

1. Identity Field — ربط هوية الـ Object بهوية الـ Row.
1. Foreign Key Mapping — تمثيل العلاقات باستخدام Foreign Keys.

**النمط التالي في ترتيب Fowler: Association Table Mapping.**

وده هيكمل موضوع العلاقات، لكن هنركز فيه على العلاقات اللي بتحتاج جدول وسيط، وخصوصًا Many-to-Many.


نكمل يا صاحبي 😂

النمط الثالث في مجموعة **Object-Relational Structural Patterns** هو:

# 3. Association Table Mapping

(Object-Relational Structural Pattern)

## 1. المشكلة (Problem)

في النمط السابق، اتكلمنا عن تمثيل العلاقات بين الـ Objects باستخدام Foreign Keys.

لكن فيه علاقات مش ممكن نمثلها بسهولة باستخدام Foreign Key واحد في أحد الجدولين.

خلينا ناخد مثال:

عندنا Student و Course.

- الطالب ممكن يسجل في أكثر من كورس.
- الكورس ممكن يكون فيه أكثر من طالب.

يعني العلاقة Many-to-Many.

في عالم الـ Objects ممكن نمثلها كده:

```python
class Student:
    def __init__(self, student_id, name):
        self.id = student_id
        self.name = name
        self.courses = []

class Course:
    def __init__(self, course_id, name):
        self.id = course_id
        self.name = name
        self.students = []
```

لكن في Relational Database، لو وضعنا course_id داخل جدول الطلاب، هنقدر نخزن كورس واحد فقط لكل طالب في التصميم البسيط.

ولو وضعنا student_id داخل جدول الكورسات، هنقدر نخزن طالب واحد فقط لكل كورس.

إذن محتاجين طريقة تمثل العلاقة نفسها، مش مجرد إضافة Foreign Key في أحد الجدولين.

## 2. الفكرة والحل (Solution)

الحل هو إنشاء جدول وسيط مستقل يحتوي على Foreign Keys تشير إلى الجدولين المرتبطين.

الجدول ده اسمه:

**Association Table**

خلينا نشوف التصميم:

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE student_courses (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),

    PRIMARY KEY (student_id, course_id)
);
```

بص على العلاقة، وابدأ قراءتها من اليمين:

```plain text
Courses  <---  Student_Courses  <---  Students
```

الجدول الموجود في المنتصف مش مجرد جدول بيانات إضافي؛ هو بيمثل العلاقة بين الطالب والكورس.

مثلًا:

student_id	course_id
1	10
1	20
2	10
3	30

معنى البيانات دي:

- الطالب 1 مسجل في الكورسين 10 و20.
- الطالب 2 مسجل في الكورس 10.
- الطالب 3 مسجل في الكورس 30.

وبالتالي نفس الطالب ممكن يرتبط بكذا كورس، ونفس الكورس ممكن يرتبط بكذا طالب.

**دي الفكرة الأساسية للنمط: تخزين العلاقة نفسها داخل جدول مستقل يحتوي على مفاتيح الطرفين.**

---

## 3. هل الجدول الوسيط ممكن يحتوي بيانات إضافية؟

أيوه، ودي نقطة مهمة جدًا.

تخيل إن الطالب مش بس بيسجل في الكورس، لكن عندنا معلومات عن عملية التسجيل نفسها:

- تاريخ التسجيل.
- الدرجة النهائية.
- حالة التسجيل.
- تاريخ الانسحاب.

هل البيانات دي مكانها جدول students أو courses؟

لا، لأنها تخص العلاقة بين الطالب والكورس، مش الطالب وحده ولا الكورس وحده.

إذن نضيفها إلى Association Table:

```sql
CREATE TABLE student_courses (
    student_id INTEGER REFERENCES students(id),
    course_id INTEGER REFERENCES courses(id),

    enrollment_date DATE,
    grade DECIMAL(5, 2),
    status VARCHAR(30),

    PRIMARY KEY (student_id, course_id)
);
```

كده الجدول الوسيط أصبح بيحتفظ بمعلومات العلاقة نفسها.

وده مثال مهم على إن العلاقة ممكن يكون ليها Attributes خاصة بيها.

### مثال Python

```python
class Enrollment:
    def __init__(
        self,
        student_id,
        course_id,
        enrollment_date,
        grade=None,
        status="enrolled"
    ):
        self.student_id = student_id
        self.course_id = course_id
        self.enrollment_date = enrollment_date
        self.grade = grade
        self.status = status
```

لاحظ إننا مثلنا عملية التسجيل كـ Object مستقل.

لكن خد بالك: وجود Object اسمه Enrollment مش شرط في كل تطبيق لـ Association Table Mapping؛ ده اختيار في تصميم الـ Domain Model حسب احتياجات النظام.

---

## 4. علاقته بـ GoF Patterns

هل فيه GoF Pattern مكافئ مباشر؟

**لا، مفيش GoF Pattern مكافئ مباشر.**

لأن Association Table Mapping بيحل مشكلة تخزين العلاقات بين Objects داخل Relational Database.

مش بيحل مشكلة إنشاء Objects أو تنظيم سلوكها أو التعاون بينها.

ممكن تلاحظ تشابهًا سطحيًا مع بعض أنماط الـ Structural Design Patterns، لكن مفيش Intent مشترك كفاية علشان نقول إن واحد بديل للتاني.

---

## 5. الفرق بين Foreign Key Mapping وAssociation Table Mapping

دي أهم مقارنة في النمط ده.

**Foreign Key Mapping:**

العلاقة بتتمثل عن طريق Foreign Key موجود في أحد الجدولين.

مثال: كل Order تابع لـ Customer واحد.

```plain text
Orders  <---  Customers
```

والـ Foreign Key موجود في جدول Orders.

**Association Table Mapping:**

العلاقة بتتمثل عن طريق جدول وسيط مستقل.

مثال: Student وCourse بعلاقة Many-to-Many.

```plain text
Courses  <---  Student_Courses  <---  Students
```

الفرق الأساسي مش مجرد وجود Foreign Key؛ لأن Association Table نفسها تحتوي Foreign Keys.

الفرق هو **مكان وطريقة تخزين العلاقة**:

- Foreign Key Mapping: المفتاح موجود في جدول أحد الطرفين.
- Association Table Mapping: العلاقة لها جدول مستقل.

---

## 6. علاقته بـ Application Architecture وClean Architecture

Association Table Mapping مش Application Architecture Pattern.

هو أسلوب Mapping داخل طبقة الـ Persistence.

في Clean Architecture:

- الـ Domain يحدد العلاقة المطلوبة بين الكيانات.
- الـ Repository يوفر طريقة التعامل مع الكيانات والعلاقات.
- الـ Infrastructure تتولى تحويل العلاقة إلى Association Table.

مثلًا، الـ Domain ممكن يتعامل مع Student و`Course` بدون ما يعرف إن قاعدة البيانات عندها جدول اسمه student_courses.

وده مهم علشان نحافظ على استقلال الـ Domain عن تفاصيل قاعدة البيانات.

---

## 7. علاقته بـ DDD

هنا عندنا نقطة تستحق التركيز.

لو العلاقة بين Student وCourse مجرد ارتباط، ممكن نمثلها كـ Collection أو References حسب التصميم.

لكن لو عملية التسجيل نفسها لها Business Rules وحالة وسلوك، ممكن تكون Enrollment كيانًا مستقلًا في الـ Domain.

مثلاً:

- لا يمكن التسجيل في كورس مكتمل.
- لا يمكن التسجيل مرتين في نفس الكورس.
- لا يمكن الانسحاب بعد موعد معين.
- الدرجة لا يمكن تعديلها بعد اعتماد النتيجة.

في الحالة دي، Enrollment مش مجرد جدول وسيط تقني؛ ده مفهوم حقيقي في الـ Domain.

وممكن يكون له Lifecycle وقواعد Business خاصة بيه.

**لكن مهم:** Association Table مش معناها تلقائيًا إننا لازم ننشئ Entity في DDD. القرار يعتمد على معنى العلاقة وقواعد العمل الخاصة بيها.

---

## 8. علاقته بـ Odoo

خلينا نشوف مثال واضح في Odoo.

افترض عندنا Student وCourse، والطالب ممكن يسجل في كورسات متعددة.

```python
class Student(models.Model):
    _name = "school.student"

    name = fields.Char()

    course_ids = fields.Many2many(
        "school.course",
        string="Courses"
    )

class Course(models.Model):
    _name = "school.course"

    name = fields.Char()

    student_ids = fields.Many2many(
        "school.student",
        string="Students"
    )
```

في الحالة دي Odoo ORM بيمثل العلاقة باستخدام Many2many Relation Table.

وممكن تحدد اسم الجدول وأعمدته بنفسك:

```python
course_ids = fields.Many2many(
    comodel_name="school.course",
    relation="student_course_rel",
    column1="student_id",
    column2="course_id",
    string="Courses"
)
```

الـ Relation Table هنا بتحتوي على المفاتيح التي تربط الطلاب بالكورسات.

### طيب لو عايز أخزن تاريخ التسجيل والدرجة؟

هنا الـ Many2many العادية مش كفاية لو محتاج تدير بيانات العلاقة كسجلات مستقلة.

ممكن تعمل Model منفصل:

```python
class Enrollment(models.Model):
    _name = "school.enrollment"

    student_id = fields.Many2one(
        "school.student",
        required=True
    )

    course_id = fields.Many2one(
        "school.course",
        required=True
    )

    enrollment_date = fields.Date()
    grade = fields.Float()
    status = fields.Selection([
        ("enrolled", "Enrolled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ])
```

وهنا أصبح عندك Model يمثل عملية التسجيل نفسها.

وده اختيار مناسب لما العلاقة بقى ليها بيانات وسلوك وقواعد خاصة.

---

## 9. إمتى نستخدم Association Table Mapping؟

استخدمه لما:

- تكون العلاقة Many-to-Many.
- العلاقة نفسها تحتاج تخزين مستقل.
- تحتاج تخزين Attributes تخص العلاقة.
- تحتاج إدارة العلاقة بشكل منفصل عن الطرفين.

**الخلاصة:**

السؤال اللي بيجاوب عنه النمط:

> How do you map an association between objects to a relational database?

الإجابة:

**عن طريق إنشاء Association Table تحتوي على Foreign Keys للطرفين، وتمثل العلاقة بينهما.**

---

## وصلنا لفين في المجموعة؟

1. **Identity Field:** ربط هوية الـ Object بهوية الـ Database Row.
1. **Foreign Key Mapping:** تمثيل العلاقة باستخدام Foreign Key.
1. **Association Table Mapping:** تمثيل العلاقة باستخدام جدول وسيط مستقل.

النمط التالي في ترتيب Fowler:

**4. Dependent Mapping**

وده هيكون مهم لأنه بيتعامل مع حالة مختلفة: إزاي نخزن Objects تابعة لـ Objects أخرى، بحيث تكون طريقة تخزينها مرتبطة بالـ Owner بتاعها.
