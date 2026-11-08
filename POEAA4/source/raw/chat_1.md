---
title: مقارنة Separated Interface (1)
url: https://chatgpt.com/g/g-p-6aef8f7176848191b87a5d98247e8052-poeaa/c/6aee602e-cd70-83e9-ae93-7e2499ed46b8
h1s: ['Pattern\tرقم الصفحة في الكتاب', '11. Record Set', 'Domain Logic Patterns', '1. Transaction Script', '2. Domain Model', '3. Table Module', '800', '800', '300', 'Domain Logic Patterns', '1. Transaction Script', '4. Service Layer', 'مراجعة مجموعة Domain Logic Patterns كاملة', 'Data Source Architectural Patterns', '1. Table Data Gateway', 'Table Data Gateway', '2. Row Data Gateway', '3. Active Record Pattern', '3. Active Record Pattern']
len: 81047
msgCount: 13
---

بص، إحساسك إن فيه Pattern ناقص يستاهل المراجعة فعلًا، لكن خلينا نفرّق بين حاجتين:

- هل فيه Pattern ناقص من **تصنيف Base Patterns نفسه** في كتاب Fowler؟
- ولا فيه Pattern تاني في الكتاب قريب من المجموعة دي، فممكن نكون حاطينه تحت تصنيف مختلف؟

هراجع فهرس الكتاب وتصنيفاته قبل ما أقولك إن العشرة دول القائمة الكاملة.

😂😂 أيوه يا هندسة، **فيه Pattern ناقص فعلًا، واسمه Record Set.**

راجعت كتالوج Martin Fowler الرسمي، ووجدت إن قائمة **Base Patterns** في الفصل 18 مكوّنة من **11 Pattern مش 10**. martinfowler.comraw.githubusercontent.com

## القائمة الكاملة

#	Pattern	رقم الصفحة في الكتاب
1	Gateway	466
2	Service Stub	504
3	Record Set	508
4	Mapper	473
5	Layer Supertype	475
6	Separated Interface	476
7	Registry	480
8	Value Object	486
9	Money	488
10	Special Case	496
11	Plugin	499

## Record Set — إيه فكرته؟

(Pattern لم نشرحه بعد)

**التعريف:**

An in-memory representation of tabular data.

يعني Object بيمثل بيانات في شكل جدولي داخل الذاكرة، قريب من شكل الـ Database Result Set.

مثال تخيلي:

```plain text
RecordSet
│
├── Columns
│   ├── id
│   ├── name
│   └── email
│
└── Rows
    ├── [1, "Ahmed", "a@test.com"]
    ├── [2, "Ali",   "b@test.com"]
    └── [3, "Omar",  "c@test.com"]
```

الفكرة إنه يديك تمثيل موحد لمجموعة بيانات جدولية، بدل ما تكون مرتبطًا بكيفية جلب البيانات أو تمثيلها في مصدر معين.

وده مش معناه إنه Database أو ORM.

**هنشرحه بنفس منهجنا السابق:**

1. المشكلة التي يعالجها.
1. الفكرة وطريقة العمل.
1. مثال Python.
1. أقرب GoF Pattern والفرق في الـ Intent.
1. علاقته بالـ Application Architecture.

وبكده نكون غطينا الـ 11 Pattern كاملين، بعد ما نضيف Record Set. martinfowler.comraw.githubusercontent.com

رابط الكتالوج الرسمي لـ Fowler.


تمام يا هندسة 😂❤️ هنشرح **Record Set** بنفس المنهج اللي مشينا بيه في العشرة Patterns السابقة، وبنفس مستوى التفصيل.

وهلتزم إن الشرح العربي يكون من اليمين للشمال، وأفصل الأكواد والمصطلحات الإنجليزية في أماكن مستقلة عشان اتجاه القراءة ما يتلخبطش.

# 11. Record Set

(Base Pattern — PoEAA)

## 1. المشكلة (The Problem)

تخيل إن عندك Application بيتعامل مع قاعدة بيانات، وبيحتاج يعرض مجموعة من العملاء.

قاعدة البيانات بترجع نتيجة بالشكل ده:

ID	Name	Email
1	Ahmed	ahmed@test.com
2	Ali	ali@test.com
3	Omar	omar@test.com

المشكلة إن نتيجة الاستعلام ممكن تكون مرتبطة بتفاصيل خاصة بالـ Database Driver أو طريقة الوصول للبيانات.

مثلًا:

- Database Driver بيرجع Result Object معين.
- كل Driver ممكن يكون له API مختلفة.
- الـ Application محتاج يتعامل مع البيانات ويقرأ الصفوف والأعمدة.
- مش عايزين منطق التطبيق يرتبط بتفاصيل الـ Database Result الأصلي.

إحنا محتاجين تمثيل موحد للبيانات الجدولية داخل الذاكرة.

## 2. الفكرة (The Solution)

**Record Set** هو Object بيمثل مجموعة من البيانات في شكل جدول داخل الذاكرة (In-Memory Tabular Data).

بمعنى إنه بيحتوي على:

- Columns: أسماء الأعمدة.
- Rows: الصفوف.
- Values: القيم الموجودة في كل خلية.

والـ Application يقدر يتعامل مع الـ Record Set بدون ما يحتاج يعرف تفاصيل الـ Database Driver اللي جاب البيانات.

## 3. مثال عملي باستخدام Python

خلينا نبني مثال بسيط.

**أولًا: Record Set**

```python
class RecordSet:
    def __init__(self, columns, rows):
        self.columns = columns
        self.rows = rows

    def get_value(self, row_index, column_name):
        column_index = self.columns.index(column_name)
        return self.rows[row_index][column_index]

    def get_rows(self):
        return [
            dict(zip(self.columns, row))
            for row in self.rows
        ]
```

**ثانيًا: البيانات**

```python
columns = ["id", "name", "email"]

rows = [
    (1, "Ahmed", "ahmed@test.com"),
    (2, "Ali", "ali@test.com"),
    (3, "Omar", "omar@test.com"),
]

record_set = RecordSet(columns, rows)
```

**ثالثًا: الاستخدام**

```python
print(record_set.get_value(0, "name"))

print(record_set.get_rows())
```

النتيجة:

```plain text
Ahmed

[
    {
        'id': 1,
        'name': 'Ahmed',
        'email': 'ahmed@test.com'
    },
    ...
]
```

لاحظ إن الـ Application بيتعامل مع واجهة موحدة، ومش محتاج يعرف البيانات جت من PostgreSQL ولا SQL Server ولا أي مصدر آخر.

## 4. أقرب GoF Pattern

هنا لازم نفرّق بين التشابه في الشكل والتشابه في الهدف.

### أقرب تشابه: Adapter

**وجه التشابه:**

الاتنين ممكن يخلّوا التعامل مع مصدر بيانات أو واجهة مختلفة أسهل بالنسبة للـ Client.

**الاختلاف في Intent:**

Adapter	Record Set
يحل مشكلة عدم توافق واجهتين	يمثل البيانات في شكل جدولي داخل الذاكرة
يركز على Interface Compatibility	يركز على Tabular Data Representation
ممكن يحول واجهة إلى واجهة أخرى	ممكن يكون هو نفسه شكل البيانات الموحد

إذًا Record Set مش نوع من Adapter، ومش بديل عنه.

ممكن تستخدم Adapter عشان تحول نتيجة Database Driver إلى Record Set.

وده معناه إن الاتنين ممكن يشتغلوا مع بعض.

## 5. علاقته بالـ Application Architecture

Record Set مش Architecture Pattern، لكنه Data Representation Pattern.

ممكن يظهر في:

- Data Access Layer.
- Integration بين أنظمة مختلفة.
- Reporting Systems.
- التطبيقات اللي بتتعامل مع نتائج استعلامات متعددة.

**مثال معماري:**

```plain text
Application
    |
    v
Data Access Layer
    |
    v
Database Adapter
    |
    v
Database Driver
    |
    v
Database
```

الـ Database Adapter ممكن يحول نتيجة الاستعلام إلى Record Set، وبعدها الـ Application يتعامل مع التمثيل الموحد.

## 6. علاقته بـ Clean Architecture

ممكن تستخدم Record Set في Clean Architecture، لكن مكانه يعتمد على طبيعة استخدامه.

مثلًا:

```plain text
Presentation
     |
Application
     |
Infrastructure
     |
Database
```

لو Record Set مجرد تمثيل لنتائج استعلامات خاصة بالـ Infrastructure، فمن الطبيعي يكون استخدامه داخل Infrastructure.

لكن لو استخدمته كـ Contract بين Application وInfrastructure، لازم تفكر هل ده مناسب فعلًا، ولا الأفضل إن الـ Application يستقبل DTOs أو Domain Objects.

**مهم:** مش كل البيانات الجدولية لازم تتحول إلى Record Set، ومش معنى وجوده إننا نستخدمه بدل Domain Entities.

---

## 7. الفرق بين Record Set و Data Mapper و Active Record

دي نقطة مهمة جدًا عشان الأسماء قريبة من بعض:

Pattern	مسؤوليته
Record Set	تمثيل مجموعة بيانات في شكل جدولي داخل الذاكرة
Data Mapper	نقل البيانات بين Domain Objects وقاعدة البيانات
Active Record	الـ Object نفسه يحتوي بياناته وسلوك الـ Persistence

يعني التلاتة مش بدائل لبعض.

---

**الخلاصة:**

Record Set بيحل مشكلة تمثيل نتائج البيانات الجدولية داخل الذاكرة بشكل موحد.

وأقرب GoF ليه من ناحية التشابه العملي هو Adapter، لكن مفيش GoF Pattern مكافئ له بشكل مباشر؛ لأن الهدف الأساسي مختلف.

وبكده اكتملت معانا قائمة الـ 11 Base Patterns في PoEAA.


طبعًا يا هندسة 😂

هننتقل دلوقتي إلى مجموعة **Domain Logic Patterns** في كتاب:

*Patterns of Enterprise Application Architecture — Martin Fowler*

وهنحافظ على نفس المنهج اللي اتفقنا عليه:

1. المشكلة التي يعالجها الـ Pattern.
1. الفكرة والحل (The Solution).
1. مثال عملي باستخدام Python.
1. أقرب GoF Pattern، ووجه التشابه والاختلاف في الـ Intent.
1. علاقته بالـ Application Architecture.
1. علاقته بـ Clean Architecture وDDD لما يكون فيه ارتباط حقيقي.

وهنشرح كل Pattern لوحده، من غير ما نخلط بينه وبين الأنماط القريبة منه. والشرح بالعربي من اليمين للشمال، والأكواد في مقاطع مستقلة.

# Domain Logic Patterns

قبل ما نبدأ، فيه نقطة مهمة جدًا: المجموعة دي في الكتاب فيها **4 Patterns**، مش 3:

1. Transaction Script
1. Domain Model
1. Table Module
1. Service Layer

وده وفقًا لفهرس Fowler الرسمي وفصل الكتاب التاسع. martinfowler.comoreilly.com

---

# 1. Transaction Script

(Domain Logic Pattern)

## 1. المشكلة (The Problem)

تخيل إن عندك E-commerce System، والعميل عايز يعمل Checkout.

العملية دي محتاجة:

1. التأكد إن المنتجات متاحة.
1. حساب إجمالي الطلب.
1. تطبيق الخصم.
1. حساب تكلفة الشحن.
1. إنشاء الطلب.
1. خصم الكميات من المخزون.
1. تسجيل عملية الدفع.

السؤال هنا: هننظم الـ Business Logic دي إزاي؟

أبسط طريقة إننا نكتب Procedure مسؤولة عن تنفيذ العملية كلها.

لكن تخيل إن عندك 50 عملية مختلفة في النظام، وكل عملية فيها Business Logic خاصة بيها.

إزاي ننظم الكود بحيث نقدر نفهم كل عملية ونعدلها بسهولة؟

## 2. الفكرة (The Solution)

فكرة Transaction Script بسيطة:

**كل Business Transaction أو User Action ليها Procedure مسؤولة عن تنفيذ الـ Logic الخاص بيها.**

يعني بدل ما نوزع الـ Business Logic على مجموعة Objects، بننظمها حول العمليات نفسها.

مثلًا:

- checkout_order()
- cancel_order()
- register_customer()
- calculate_shipping()

كل Function مسؤولة عن تنفيذ Use Case أو عملية معينة.

مش شرط تكون Function واحدة ضخمة؛ ممكن تستدعي Helper Functions، لكن التنظيم الأساسي يفضل قائمًا على العمليات.

## 3. مثال عملي باستخدام Python

خلينا نعمل Checkout بسيط.

```python
class OrderRepository:
    def save(self, order):
        print("Order saved")

class InventoryRepository:
    def decrease_stock(self, product_id, quantity):
        print(f"Stock decreased: {product_id}")

class PaymentGateway:
    def charge(self, amount):
        print(f"Charged: {amount}")

def checkout_order(cart, payment_gateway,
                   order_repository, inventory_repository):

    # 1. Validate products
    for item in cart:
        if item["quantity"] <= 0:
            raise ValueError("Invalid quantity")

        if item["stock"] < item["quantity"]:
            raise ValueError("Insufficient stock")

    # 2. Calculate total
    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    # 3. Apply discount
    if total >= 1000:
        total *= 0.9

    # 4. Process payment
    payment_gateway.charge(total)

    # 5. Save order
    order = {
        "items": cart,
        "total": total,
    }

    order_repository.save(order)

    # 6. Decrease stock
    for item in cart:
        inventory_repository.decrease_stock(
            item["product_id"],
            item["quantity"],
        )

    return order
```

لاحظ هنا إن الـ Business Logic كلها متجمعة داخل Procedure واحدة مسؤولة عن عملية Checkout.

والـ Repositories والـ Gateway مجرد Dependencies بتتعامل معاها الـ Procedure.

**ملحوظة:** المثال توضيحي لفكرة Transaction Script، وليس تنفيذًا Production-ready؛ لأن الدفع والمخزون والـ Database محتاجين Transaction Management وتعامل مع حالات الفشل والتعويض.

## 4. أقرب GoF Pattern

هنا عندنا تشابه مع نمطين، لكن مفيش GoF Pattern مكافئ مباشرة.

### Command

**وجه التشابه:**

الـ Command بيمثل طلب أو عملية يمكن تنفيذها، وTransaction Script برضه ممكن يمثل عملية معينة.

**الاختلاف في Intent:**

Command	Transaction Script
يحول الطلب إلى Object	ينظم الـ Business Logic في Procedures
يسمح بتغليف الطلب وتمريره وتخزينه أو تأجيله	يركز على تنفيذ العملية
يدعم Undo/Queue وغيرها حسب التصميم	مش بيشترط أيًا من ده

ممكن تنفذ Transaction Script داخل Command، لكن ده مش معناه إنهم نفس الـ Pattern.

### Template Method

**وجه التشابه:**

ممكن تلاحظ إن Transaction Script عنده خطوات متتابعة لتنفيذ العملية.

**الاختلاف:**

Template Method بيحدد Skeleton لخوارزمية داخل Base Class، والـ Subclasses بتخصص بعض الخطوات.

أما Transaction Script فمش محتاج Inheritance أصلًا.

## 5. علاقته بالـ Application Architecture

Transaction Script هو طريقة لتنظيم الـ Domain Logic، وليس Architecture كاملة.

ممكن تستخدمه داخل:

- Layered Architecture.
- Clean Architecture.
- Hexagonal Architecture.

مثلًا في Clean Architecture:

```plain text
Presentation
     |
     v
Application Use Case
     |
     v
Transaction Script
     |
     v
Output Ports
     |
     v
Infrastructure
```

لكن خلي بالك: ده توزيع توضيحي، مش شرط إن كل Transaction Script يبقى في مكان اسمه Application أو Domain. المهم هو فصل المسؤوليات واتجاه الاعتماديات.

## 6. علاقته بـ DDD

هنا فيه فرق مهم جدًا.

Transaction Script مش هو الأسلوب الأساسي اللي DDD بيبني عليه الـ Domain Model.

في DDD، بنحاول نمثل مفاهيم المجال وسلوكها داخل Domain Objects، خصوصًا لما تكون قواعد العمل معقدة ومترابطة.

أما Transaction Script فبيحط منطق العملية أساسًا في Procedure.

وده لا يعني إن Transaction Script غلط أو غير احترافي.

Fowler نفسه بيعتبره اختيارًا مناسبًا للأنظمة ذات الـ Domain Logic البسيطة نسبيًا. accc.orgraw.githubusercontent.com

---

## 7. إمتى أستخدمه؟

الحالة	الاختيار
Business Logic بسيطة	Transaction Script مناسب
CRUD Operations بسيطة	Transaction Script مناسب
قواعد معقدة ومترابطة بين Entities	Domain Model غالبًا أنسب
نفس القواعد مستخدمة في عمليات متعددة	راجع احتمالية استخراج Domain Model
Workflow طويل ومعقد	قد تحتاج تنظيمًا إضافيًا

## الخلاصة

**Transaction Script** بينظم الـ Business Logic حول العمليات (Transactions)، بحيث كل عملية ليها Procedure مسؤولة عن تنفيذها.

وأهم نقطة عايزك تخرج بيها:

الفرق الجوهري بين Transaction Script وDomain Model مش مجرد إن واحد Functions والتاني Classes.

الفرق هو **إحنا بننظم الـ Business Logic حول إيه؟**

- Transaction Script: حول العمليات.
- Domain Model: حول مفاهيم المجال وسلوكها.

وده هيكون محور المقارنة لما نبدأ الـ Pattern اللي بعده.

**التالي: Domain Model** — وده من أهم الأنماط في المجموعة؛ لأنه بيغير طريقة تفكيرك في توزيع الـ Business Logic بالكامل.


يلا بينا يا هندسة. وصلنا لأهم Pattern في المجموعة دي من ناحية طريقة التفكير في الـ Business Logic.

# 2. Domain Model

(Domain Logic Pattern)

## 1. المشكلة (The Problem)

خلينا نستخدم نفس مثال الـ E-commerce اللي بدأنا بيه.

عندنا نظام فيه:

- Customers
- Orders
- Products
- Payments
- Discounts
- Inventory

وعندنا قواعد Business مختلفة:

- الطلب لا يمكن إلغاؤه بعد الشحن.
- الخصم لا يمكن أن يتجاوز حدًا معينًا.
- لا يمكن تأكيد الطلب بدون منتجات.
- إجمالي الطلب لازم يساوي مجموع عناصره بعد تطبيق الخصومات.
- بعض العملاء عندهم شروط خصم مختلفة.

في البداية ممكن نكتب كل ده داخل Functions منفصلة.

لكن مع زيادة النظام، هنواجه مشاكل:

1. نفس القاعدة ممكن تتكرر في أكتر من مكان.
1. الـ Business Logic ممكن تتوزع بين Services وControllers.
1. تعديل قاعدة واحدة ممكن يحتاج تعديلات في أماكن متعددة.
1. العلاقات بين مفاهيم الـ Business مش بتكون واضحة في الكود.

المشكلة الأساسية هنا إننا بننظم الـ Logic حول العمليات، بينما طبيعة المجال نفسها بقت معقدة ومترابطة.

## 2. الفكرة (The Solution)

تعريف Fowler:

**An object model of the domain that incorporates both behavior and data.** martinfowler.comaccc.org

يعني إيه؟

بدل ما نخلي الـ Business Logic كلها داخل Functions مستقلة، بنبني مجموعة Objects بتمثل مفاهيم المجال الحقيقي.

وكل Object بيجمع:

- Data: البيانات التي تخص المفهوم.
- Behavior: السلوك والقواعد المرتبطة بالمفهوم.

مثلًا:

Order مش مجرد Object بيحتوي على id و`total`.

هو كمان مسؤول عن سلوكيات الطلب، زي:

- add_item()
- remove_item()
- confirm()
- cancel()
- calculate_total()

بالتالي بنحاول نخلي الـ Business Rules قريبة من الـ Business Data اللي بتخصها.

وده هو جوهر Domain Model.

## 3. مثال عملي باستخدام Python

هنبني نموذج صغير للطلبات.

**أولًا: Product**

```python
class Product:
    def __init__(self, product_id, name, price):
        if price <= 0:
            raise ValueError("Price must be positive")

        self.id = product_id
        self.name = name
        self.price = price
```

**ثانيًا: OrderItem**

```python
class OrderItem:
    def __init__(self, product, quantity):
        if quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.product = product
        self.quantity = quantity

    def subtotal(self):
        return self.product.price * self.quantity
```

لاحظ إن حساب الـ Subtotal موجود في OrderItem، لأنه مسؤول عن تمثيل عنصر الطلب وكميته.

**ثالثًا: Order**

```python
class Order:
    def __init__(self):
        self.items = []
        self.status = "draft"

    def add_item(self, item):
        if self.status != "draft":
            raise ValueError("Cannot modify confirmed order")

        self.items.append(item)

    def calculate_total(self):
        return sum(
            item.subtotal()
            for item in self.items
        )

    def confirm(self):
        if not self.items:
            raise ValueError("Cannot confirm empty order")

        if self.status != "draft":
            raise ValueError("Order cannot be confirmed")

        self.status = "confirmed"

    def cancel(self):
        if self.status == "shipped":
            raise ValueError("Cannot cancel shipped order")

        self.status = "cancelled"
```

**رابعًا: الاستخدام**

```python
product = Product(
    product_id=1,
    name="Laptop",
    price=500
)

item = OrderItem(
    product=product,
    quantity=2
)

order = Order()

order.add_item(item)

print(order.calculate_total())  # 1000

order.confirm()

print(order.status)  # confirmed
```

## 4. إيه اللي اتغير مقارنة بـ Transaction Script؟

دي أهم مقارنة في الموضوع كله.

في Transaction Script:

```python
def confirm_order(order):
    if not order["items"]:
        raise ValueError("Empty order")

    if order["status"] != "draft":
        raise ValueError("Invalid status")

    order["status"] = "confirmed"
```

الـ Procedure هي اللي مسؤولة عن تنفيذ قواعد العملية.

أما في Domain Model:

```python
order.confirm()
```

الـ Order نفسه مسؤول عن تطبيق قواعد تأكيد الطلب.

لاحظ إن الفرق مش مجرد تحويل Function إلى Method.

الفرق في **مكان امتلاك الـ Business Rules والمسؤولية عنها**.

Transaction Script	Domain Model
ينظم الـ Logic حول العمليات	ينظم الـ Logic حول مفاهيم المجال
الإجراءات مسؤولة عن تنفيذ القواعد	Objects تحتوي البيانات والسلوك
مناسب للـ Logic البسيطة	مناسب للـ Logic المعقدة
ممكن تلاقي قواعد المجال موزعة على Procedures	نحاول تجميع القواعد بالقرب من المفاهيم التي تخصها

## 5. أقرب GoF Pattern

هنا مفيش GoF Pattern واحد مكافئ لـ Domain Model؛ لأنه أسلوب أوسع لتنظيم الـ Domain Logic.

لكن فيه تشابهات مهمة.

### Strategy

**وجه التشابه:**

الاتنين ممكن يستخدموا Objects لتمثيل سلوكيات مختلفة.

مثلًا عندنا طرق مختلفة لحساب الخصم:

```python
class DiscountStrategy:
    def calculate(self, total):
        raise NotImplementedError

class RegularDiscount(DiscountStrategy):
    def calculate(self, total):
        return 0

class PremiumDiscount(DiscountStrategy):
    def calculate(self, total):
        return total * 0.10
```

ممكن الـ Domain Model يستخدم Strategy لحساب الخصم.

**الاختلاف في Intent:**

- Strategy هدفه فصل Algorithm قابل للتغيير أو الاستبدال.
- Domain Model هدفه تمثيل المجال وبياناته وسلوكه.

يعني Strategy ممكن يكون جزء من Domain Model، لكنه مش بديل عنه.

### State

**وجه التشابه:**

ممكن يكون عندنا Order بيتصرف بشكل مختلف حسب حالته.

مثلًا:

- Draft
- Confirmed
- Shipped
- Cancelled

وده قريب من مشكلة State Pattern.

**الاختلاف في Intent:**

- State بينظم السلوك المتغير حسب الحالة الداخلية للـ Object.
- Domain Model بيمثل المجال ككل، بما فيه البيانات والقواعد والعلاقات.

ممكن تستخدم State داخل Domain Model لتنظيم دورة حياة Order، لكن مش كل Domain Model محتاج State Pattern.

## 6. علاقته بالـ Application Architecture

Domain Model مش Architecture كاملة، لكنه طريقة لتنظيم الـ Business Logic.

ممكن تستخدمه داخل:

- Layered Architecture.
- Clean Architecture.
- Hexagonal Architecture.
- Onion Architecture.

مثلًا في Clean Architecture:

```plain text
        Presentation
              |
              v
         Application
              |
              v
          Domain
              ^
              |
       Infrastructure
```

الـ Domain Model بيكون في أعمق طبقة منطقية.

والـ Application Use Cases بتنسق تنفيذ العمليات باستخدام الـ Domain Objects.

أما Infrastructure فمسؤولة عن التفاصيل التقنية زي Database وExternal APIs.

**ملحوظة:** الرسم توضيحي للعلاقات، وليس ترتيبًا إلزاميًا لملفات المشروع.

## 7. علاقته بـ DDD

هنا لازم نقف شوية.

**Domain Model في PoEAA هو Pattern، بينما DDD منهجية أوسع لتصميم البرمجيات حول الـ Domain.**

في DDD، الـ Domain Model يعتبر عنصرًا أساسيًا.

لكن DDD بيقدم مفاهيم وتفاصيل إضافية، منها:

- Entities
- Value Objects
- Aggregates
- Domain Services
- Domain Events
- Repositories
- Bounded Contexts

مش معنى كده إن كل Domain Model لازم يكون DDD كامل.

ممكن تعمل Domain Model بسيط من غير ما تطبق كل مفاهيم DDD.

والعكس مهم: وجود Classes وObjects في المشروع لا يعني تلقائيًا إن عندك Domain Model غني.

Fowler بيؤكد إن Domain Model مناسب خصوصًا لما تكون قواعد العمل والعلاقات معقدة، وده أحد الأسباب اللي بتخلي DDD يهتم بيه. martinfowler.comlearn.microsoft.com

---

## 8. إمتى أستخدمه؟

الحالة	الاختيار
CRUD بسيط جدًا	Transaction Script غالبًا أبسط
قواعد Business قليلة ومستقلة	Transaction Script ممكن يكون كافيًا
قواعد كثيرة ومترابطة	Domain Model
سلوك يتغير حسب حالة الـ Entity	Domain Model مع إمكانية استخدام State
قواعد معقدة خاصة بمفاهيم المجال	Domain Model

## 9. نقطة مهمة: Anemic Domain Model

فيه مصطلح لازم تعرفه اسمه:

**Anemic Domain Model**

وده بيحصل لما تعمل Classes شكلها Domain Model، لكن هي في الحقيقة مجرد Data Containers.

مثلًا:

```python
class Order:
    def __init__(self):
        self.items = []
        self.status = "draft"
        self.total = 0
```

وبعدين تحط كل الـ Business Logic في Services خارجية:

```python
class OrderService:
    def confirm(self, order):
        if not order.items:
            raise ValueError("Empty order")

        order.status = "confirmed"
```

هنا الـ Order مجرد بيانات، والـ Service هي اللي تمتلك قواعده.

ده مش بالضرورة تصميم غلط في كل الحالات، لكن لو هدفك تطبيق Domain Model غني، فده بيكون عكس الاتجاه اللي بتحاول توصله.

---

## الخلاصة

الـ Domain Model بيغير طريقة تنظيم التفكير في الـ Business Logic:

- Transaction Script: العملية هي مركز التنظيم.
- Domain Model: مفاهيم المجال وسلوكها هي مركز التنظيم.

وأهم حاجة: **Domain Model مش معناه إننا نحول كل Function إلى Method داخل Class.**

المطلوب إننا نفهم مفاهيم الـ Business ونحدد كل قاعدة وسلوك مسؤولية مين.

---

**السؤال اللي عايزك تفكر فيه قبل ما ننتقل لـ Table Module:**

لو عندي Order، وعندي قاعدة بتقول إن العميل Premium بياخد خصم 10%.

هل الأفضل إن Order يحسب الخصم بنفسه؟ ولا Customer؟ ولا نعمل DiscountPolicy مستقلة؟

مفيش إجابة واحدة صحيحة في كل الأنظمة؛ المهم تحدد المسؤولية بناءً على معنى القاعدة في الـ Domain.


نكمل يا هندسة. المرة دي عندنا Pattern مهم جدًا، خصوصًا لما نتعامل مع قواعد بيانات علائقية ونحاول ننظم الـ Business Logic من غير ما نبني Domain Model كامل.

# 3. Table Module

(Domain Logic Pattern)

## 1. المشكلة (The Problem)

تخيل إن عندك نظام لإدارة المبيعات، وفيه جدول اسمه:

orders

والجدول ده بيحتوي على آلاف الطلبات.

عندك عمليات زي:

- حساب إجمالي المبيعات.
- حساب الضريبة.
- حساب الخصومات.
- تحديد الطلبات المتأخرة.
- حساب إجمالي مبيعات كل عميل.

ممكن تنفذ كل عملية داخل Functions منفصلة، وده قريب من Transaction Script.

وممكن تعمل Object لكل Order، وتخلي كل Order مسؤول عن سلوكه، وده قريب من Domain Model.

لكن فيه حالة تالتة:

أنت عايز تنظم الـ Business Logic حول جدول قاعدة البيانات نفسه، بحيث يكون عندك Object واحد مسؤول عن منطق جدول معين.

إزاي نعمل ده؟

## 2. الفكرة (The Solution)

**Table Module** هو Object يحتوي على Business Logic مرتبطة بجدول معين في قاعدة البيانات.

يعني بدل ما تعمل Object مستقل لكل Row، بتعمل Object يمثل الجدول ككل، وعملياته بتشتغل على مجموعة السجلات.

مثلًا:

```plain text
                 SalesTableModule
                        |
          +-------------+-------------+
          |             |             |
       orders        customers      products
```

للتوضيح، في تطبيقنا ممكن يكون عندنا:

- OrdersTableModule
- CustomersTableModule
- ProductsTableModule

وكل واحد مسؤول عن Business Logic الخاصة بالجدول اللي بيمثله.

**الفرق الجوهري:** الـ Table Module بيتعامل مع مجموعة Rows، مش مع كل Row باعتباره Object مستقل له سلوكه الخاص.

## 3. مثال عملي باستخدام Python

هنعمل مثال بسيط لإدارة الطلبات.

**أولًا: البيانات**

```python
orders = [
    {
        "id": 1,
        "customer_id": 10,
        "amount": 500,
        "status": "confirmed",
    },
    {
        "id": 2,
        "customer_id": 10,
        "amount": 300,
        "status": "confirmed",
    },
    {
        "id": 3,
        "customer_id": 20,
        "amount": 700,
        "status": "cancelled",
    },
]
```

**ثانيًا: Table Module**

```python
class OrdersTableModule:

    def __init__(self, orders):
        self.orders = orders

    def calculate_total_sales(self):
        return sum(
            order["amount"]
            for order in self.orders
            if order["status"] == "confirmed"
        )

    def calculate_customer_sales(self, customer_id):
        return sum(
            order["amount"]
            for order in self.orders
            if (
                order["customer_id"] == customer_id
                and order["status"] == "confirmed"
            )
        )

    def cancel_order(self, order_id):
        for order in self.orders:
            if order["id"] == order_id:
                if order["status"] == "cancelled":
                    raise ValueError("Already cancelled")

                order["status"] = "cancelled"
                return

        raise ValueError("Order not found")
```

**ثالثًا: الاستخدام**

```python
orders_module = OrdersTableModule(orders)

print(orders_module.calculate_total_sales())
# 800

print(orders_module.calculate_customer_sales(10))
# 800

orders_module.cancel_order(1)

print(orders_module.calculate_total_sales())
# 300
```

لاحظ هنا إننا ما عملناش Order Object لكل طلب.

عندنا Object واحد مسؤول عن منطق مجموعة الطلبات.

وده جوهر Table Module.

المثال مبسط لتوضيح النمط؛ في التطبيق الحقيقي هتحتاج فصل الوصول للبيانات وإدارة المعاملات والتحقق من سلامة التعديلات.

## 4. أقرب GoF Pattern

مفيش GoF Pattern مكافئ مباشرة لـ Table Module، لكن فيه تشابهات تستحق المقارنة.

### Facade

**وجه التشابه:**

ممكن Table Module يقدم مجموعة عمليات من خلال واجهة واحدة، وده يشبه Facade في تبسيط التعامل مع مجموعة من التفاصيل.

**الاختلاف في Intent:**

Facade	Table Module
يبسط التعامل مع Subsystem	ينظم Business Logic الخاصة بجدول
يخفي تعقيد مجموعة من المكونات	يمثل منطق جدول معين
مش شرط يحتوي Business Logic	يحتوي Business Logic

إذًا Table Module مش Facade، حتى لو واجهته بتبدو مشابهة له.

### Strategy

ممكن تستخدم Strategy داخل Table Module لتغيير طريقة حساب الضريبة أو الخصم.

لكن:

- Strategy مسؤوليته تبديل Algorithm.
- Table Module مسؤوليته تنظيم Logic مرتبطة بجدول.

يعني Strategy ممكن يكون جزءًا منه، لكنه مش بديل عنه.

## 5. الفرق بين Transaction Script وDomain Model وTable Module

دي أهم مقارنة في المجموعة لحد دلوقتي.

المقارنة	Transaction Script	Domain Model	Table Module
محور التنظيم	العملية	Domain Objects	جدول البيانات
الوحدة الأساسية	Procedure	Object لكل مفهوم/كيان	Object لكل جدول
التعامل مع البيانات	حسب العملية	Objects فردية مترابطة	مجموعة Rows
السلوك	داخل Procedures	داخل Domain Objects	داخل Table Modules
التعقيد المناسب	بسيط نسبيًا	متوسط إلى معقد	متوسط نسبيًا

خلينا نثبت الفرق بمثال:

لو عندنا 1000 Order:

- Transaction Script: تنفذ عملية على الطلبات من خلال Procedure.
- Domain Model: ممكن يكون عندك 1000 Order Object، كل واحد يحمل بياناته وسلوكه.
- Table Module: عندك OrdersTableModule واحد يتعامل مع مجموعة الطلبات.

طبعًا دي مقارنة على مستوى أسلوب تنظيم الـ Logic، مش قاعدة إن كل تطبيق لازم يحمل 1000 Object في الذاكرة.

## 6. علاقته بالـ Application Architecture

Table Module مش Architecture Pattern، لكنه طريقة لتنظيم الـ Domain Logic.

ممكن يظهر في Layered Architecture بالشكل ده:

```plain text
Presentation Layer
        |
        v
Business Logic Layer
        |
        v
OrdersTableModule
        |
        v
Data Access Layer
        |
        v
Database
```

وممكن تستخدمه داخل Clean Architecture أيضًا، بشرط الحفاظ على اتجاه الاعتماديات.

مثلًا، لو الـ Table Module جزء من الـ Domain Logic، فلا ينبغي أن يعتمد مباشرة على PostgreSQL أو ORM محدد.

أما تفاصيل جلب البيانات وحفظها فتكون خارج الـ Domain.

## 7. علاقته بـ DDD

هنا لازم نفرّق بين المصطلحات.

Table Module مش هو Entity ولا Aggregate في DDD.

في DDD:

- الـ Entity بيمثل كيان له Identity وسلوك.
- الـ Aggregate بيحدد حدود الاتساق والتحكم في التعديلات.
- الـ Table Module بيمثل منطقًا متعلقًا بجدول ومجموعة سجلات.

بالتالي مش بنعتبر Table Module تطبيقًا لـ DDD.

هو أسلوب مختلف لتنظيم الـ Domain Logic، وغالبًا Domain Model بيكون أنسب لما تكون عندك قواعد واتصالات معقدة بين الكيانات.

## 8. علاقته بأودو (Odoo)

خلينا نربط الكلام بحاجة تعرفها.

في Odoo عندك Model زي:

```python
class SaleOrder(models.Model):
    _name = "sale.order"
```

ممكن تلاحظ إن الـ Model عنده Methods بتتعامل مع Recordsets:

```python
def action_confirm(self):
    for order in self:
        # Business logic
        ...
```

هل ده معناه إن Odoo بيطبق Table Module؟

**لا، مش بالضرورة.**

رغم وجود تشابه ظاهري، Odoo ORM عنده مفهوم Recordset خاص به، والـ Model Methods بتشتغل على Recordsets، لكن ده مش كافي لتصنيفه كـ Table Module.

السبب إن Table Module له Intent محدد في Fowler، ومجرد إن Object بيتعامل مع مجموعة Records لا يثبت استخدام النمط.

دي نقطة مهمة جدًا عشان ما نخلطش بين Record Set وTable Module وOdoo Recordset.

---

## 9. إمتى أستخدمه؟

الحالة	الاختيار
منطق بسيط متعلق بعملية واحدة	Transaction Script
منطق معقد مرتبط بكيانات وسلوكها	Domain Model
منطق منظم حول جدول ومجموعة سجلات	Table Module
قواعد متشابكة بين كيانات متعددة	Domain Model غالبًا أنسب

## الخلاصة

**Table Module** بيجمع الـ Business Logic المرتبطة بجدول معين داخل Object واحد، وبيتعامل مع مجموعة السجلات بدل ما ينشئ Domain Object مستقل لكل سجل.

والفرق الأساسي بين الأنماط الثلاثة:

- Transaction Script: العملية هي محور التنظيم.
- Domain Model: الكيانات ومفاهيم المجال هي محور التنظيم.
- Table Module: الجدول هو محور التنظيم.

---

**التالي: Service Layer**

وده Pattern مهم جدًا لأنه هيخلينا نفهم العلاقة بين الـ Application Operations والـ Domain Logic، وكمان هنقدر نقارن بينه وبين Application Service في Clean Architecture وDDD.


طبعًا يا هندسة 😂

هننتقل دلوقتي إلى مجموعة **Domain Logic Patterns** في كتاب:

*Patterns of Enterprise Application Architecture — Martin Fowler*

وهنحافظ على نفس المنهج اللي اتفقنا عليه:

1. المشكلة التي يعالجها الـ Pattern.
1. الفكرة والحل (The Solution).
1. مثال عملي باستخدام Python.
1. أقرب GoF Pattern، ووجه التشابه والاختلاف في الـ Intent.
1. علاقته بالـ Application Architecture.
1. علاقته بـ Clean Architecture وDDD لما يكون فيه ارتباط حقيقي.

وهنشرح كل Pattern لوحده، من غير ما نخلط بينه وبين الأنماط القريبة منه. والشرح بالعربي من اليمين للشمال، والأكواد في مقاطع مستقلة.

# Domain Logic Patterns

قبل ما نبدأ، فيه نقطة مهمة جدًا: المجموعة دي في الكتاب فيها **4 Patterns**، مش 3:

1. Transaction Script
1. Domain Model
1. Table Module
1. Service Layer

وده وفقًا لفهرس Fowler الرسمي وفصل الكتاب التاسع. martinfowler.comoreilly.com

---

# 1. Transaction Script

(Domain Logic Pattern)

## 1. المشكلة (The Problem)

تخيل إن عندك E-commerce System، والعميل عايز يعمل Checkout.

العملية دي محتاجة:

1. التأكد إن المنتجات متاحة.
1. حساب إجمالي الطلب.
1. تطبيق الخصم.
1. حساب تكلفة الشحن.
1. إنشاء الطلب.
1. خصم الكميات من المخزون.
1. تسجيل عملية الدفع.

السؤال هنا: هننظم الـ Business Logic دي إزاي؟

أبسط طريقة إننا نكتب Procedure مسؤولة عن تنفيذ العملية كلها.

لكن تخيل إن عندك 50 عملية مختلفة في النظام، وكل عملية فيها Business Logic خاصة بيها.

إزاي ننظم الكود بحيث نقدر نفهم كل عملية ونعدلها بسهولة؟

## 2. الفكرة (The Solution)

فكرة Transaction Script بسيطة:

**كل Business Transaction أو User Action ليها Procedure مسؤولة عن تنفيذ الـ Logic الخاص بيها.**

يعني بدل ما نوزع الـ Business Logic على مجموعة Objects، بننظمها حول العمليات نفسها.

مثلًا:

- checkout_order()
- cancel_order()
- register_customer()
- calculate_shipping()

كل Function مسؤولة عن تنفيذ Use Case أو عملية معينة.

مش شرط تكون Function واحدة ضخمة؛ ممكن تستدعي Helper Functions، لكن التنظيم الأساسي يفضل قائمًا على العمليات.

## 3. مثال عملي باستخدام Python

خلينا نعمل Checkout بسيط.

```python
class OrderRepository:
    def save(self, order):
        print("Order saved")

class InventoryRepository:
    def decrease_stock(self, product_id, quantity):
        print(f"Stock decreased: {product_id}")

class PaymentGateway:
    def charge(self, amount):
        print(f"Charged: {amount}")

def checkout_order(cart, payment_gateway,
                   order_repository, inventory_repository):

    # 1. Validate products
    for item in cart:
        if item["quantity"] <= 0:
            raise ValueError("Invalid quantity")

        if item["stock"] < item["quantity"]:
            raise ValueError("Insufficient stock")

    # 2. Calculate total
    total = sum(
        item["price"] * item["quantity"]
        for item in cart
    )

    # 3. Apply discount
    if total >= 1000:
        total *= 0.9

    # 4. Process payment
    payment_gateway.charge(total)
```

لاحظ هنا إن الـ Business Logic كلها متجمعة داخل Procedure واحدة مسؤولة عن عملية Checkout.

والـ Repositories والـ Gateway مجرد Dependencies بتتعامل معاها الـ Procedure.

**ملحوظة:** المثال توضيحي لفكرة Transaction Script، وليس تنفيذًا Production-ready؛ لأن الدفع والمخزون والـ Database محتاجين Transaction Management وتعامل مع حالات الفشل والتعويض.

## 4. أقرب GoF Pattern

هنا عندنا تشابه مع نمطين، لكن مفيش GoF Pattern مكافئ مباشرة.

### Command

**وجه التشابه:**

الـ Command بيمثل طلب أو عملية يمكن تنفيذها، وTransaction Script برضه ممكن يمثل عملية معينة.

**الاختلاف في Intent:**

Command	Transaction Script
يحول الطلب إلى Object	ينظم الـ Business Logic في Procedures
يسمح بتغليف الطلب وتمريره وتخزينه أو تأجيله	يركز على تنفيذ العملية
يدعم Undo/Queue وغيرها حسب التصميم	مش بيشترط أيًا من ده

ممكن تنفذ Transaction Script داخل Command، لكن ده مش معناه إنهم نفس الـ Pattern.

### Template Method

**وجه التشابه:**

ممكن تلاحظ إن Transaction Script عنده خطوات متتابعة لتنفيذ العملية.

**الاختلاف:**

Template Method بيحدد Skeleton لخوارزمية داخل Base Class، والـ Subclasses بتخصص بعض الخطوات.

أما Transaction Script فمش محتاج Inheritance أصلًا.

## 5. علاقته بالـ Application Architecture

Transaction Script هو طريقة لتنظيم الـ Domain Logic، وليس Architecture كاملة.

ممكن تستخدمه داخل:

- Layered Architecture.
- Clean Architecture.
- Hexagonal Architecture.

مثلًا في Clean Architecture:

```plain text
Presentation
     |
     v
Application Use Case
     |
     v
Transaction Script
     |
     v
Output Ports
     |
     v
Infrastructure
```

لكن خلي بالك: ده توزيع توضيحي، مش شرط إن كل Transaction Script يبقى في مكان اسمه Application أو Domain. المهم هو فصل المسؤوليات واتجاه الاعتماديات.

## 6. علاقته بـ DDD

هنا فيه فرق مهم جدًا.

Transaction Script مش هو الأسلوب الأساسي اللي DDD بيبني عليه الـ Domain Model.

في DDD، بنحاول نمثل مفاهيم المجال وسلوكها داخل Domain Objects، خصوصًا لما تكون قواعد العمل معقدة ومترابطة.

أما Transaction Script فبيحط منطق العملية أساسًا في Procedure.

وده لا يعني إن Transaction Script غلط أو غير احترافي.

Fowler نفسه بيعتبره اختيارًا مناسبًا للأنظمة ذات الـ Domain Logic البسيطة نسبيًا. accc.orgraw.githubusercontent.com

---

## 7. إمتى أستخدمه؟

الحالة	الاختيار
Business Logic بسيطة	Transaction Script مناسب
CRUD Operations بسيطة	Transaction Script مناسب
قواعد معقدة ومترابطة بين Entities	Domain Model غالبًا أنسب
نفس القواعد مستخدمة في عمليات متعددة	راجع احتمالية استخراج Domain Model
Workflow طويل ومعقد	قد تحتاج تنظيمًا إضافيًا

## الخلاصة

**Transaction Script** بينظم الـ Business Logic حول العمليات (Transactions)، بحيث كل عملية ليها Procedure مسؤولة عن تنفيذها.

وأهم نقطة عايزك تخرج بيها:

الفرق الجوهري بين Transaction Script وDomain Model مش مجرد إن واحد Functions والتاني Classes.

الفرق هو **إحنا بننظم الـ Business Logic حول إيه؟**

- Transaction Script: حول العمليات.
- Domain Model: حول مفاهيم المجال وسلوكها.

وده هيكون محور المقارنة لما نبدأ الـ Pattern اللي بعده.

**التالي: Domain Model** — وده من أهم الأنماط في المجموعة؛ لأنه بيغير طريقة تفكيرك في توزيع الـ Business Logic بالكامل.


نكمل يا هندسة. وصلنا لآخر Pattern في مجموعة **Domain Logic Patterns**، وده من أكتر الأنماط اللي بيحصل فيها خلط مع مصطلحات تانية في Clean Architecture وDDD.

# 4. Service Layer

(Domain Logic Pattern)

## 1. المشكلة (The Problem)

تخيل عندك E-commerce System، وعندك أكتر من طريقة للتعامل مع الطلبات:

- Web Application.
- Mobile Application.
- REST API.
- Background Jobs.
- Admin Dashboard.

كل واحدة من دول محتاجة تنفذ عمليات زي:

- إنشاء Order.
- تأكيد Order.
- إلغاء Order.
- حساب إجمالي الطلب.

السؤال: هل هنكتب الـ Business Logic داخل كل Controller أو API Endpoint؟

طبعًا لأ.

لأننا لو عملنا كده، هنواجه مشاكل:

1. تكرار الـ Business Logic بين Web وMobile وAPI.
1. اختلاف سلوك العملية حسب طريقة استدعائها.
1. صعوبة التحكم في Transactions.
1. صعوبة تحديد العمليات المتاحة للتطبيقات الخارجية.
1. صعوبة اختبار الـ Business Operations بشكل مستقل عن Presentation.

إحنا محتاجين طبقة توفر واجهة موحدة للعمليات اللي التطبيق بيقدمها.

## 2. الفكرة (The Solution)

تعريف Fowler:

**A Service Layer defines an application's boundary and its set of available operations from the perspective of interfacing client layers.** oreilly.commartinfowler.com

خلينا نفهم التعريف.

الـ Service Layer هي طبقة بتحدد:

- Application Boundary: حدود التطبيق والعمليات المتاحة منه.
- Application Operations: العمليات اللي الـ Clients يقدروا يطلبوها.
- Coordination: تنسيق تنفيذ العمليات المختلفة.
- Transaction Control: التحكم في حدود المعاملات عند الحاجة.

بمعنى أبسط:

بدل ما الـ Controller يعرف تفاصيل تنفيذ Checkout، هو بيطلب من Service Layer تنفيذ العملية.

والـ Service Layer هي اللي بتنسق التنفيذ.

## 3. مثال عملي باستخدام Python

هنستخدم نفس مثال الـ E-commerce.

**أولًا: Domain Model**

```python
class Order:
    def __init__(self):
        self.items = []
        self.status = "draft"

    def add_item(self, item):
        if self.status != "draft":
            raise ValueError("Cannot modify order")

        self.items.append(item)

    def calculate_total(self):
        return sum(
            item["price"] * item["quantity"]
            for item in self.items
        )

    def confirm(self):
        if not self.items:
            raise ValueError("Empty order")

        if self.status != "draft":
            raise ValueError("Invalid order status")

        self.status = "confirmed"
```

لاحظ إن الـ Order مسؤول عن قواعده الداخلية.

**ثانيًا: Repository**

```python
class OrderRepository:
    def save(self, order):
        print("Order saved")

    def get_by_id(self, order_id):
        print(f"Fetching order: {order_id}")
        return Order()
```

**ثالثًا: Service Layer**

```python
class OrderService:

    def __init__(self, order_repository):
        self.order_repository = order_repository

    def create_order(self, items):
        order = Order()

        for item in items:
            order.add_item(item)

        self.order_repository.save(order)

        return order

    def confirm_order(self, order_id):
        order = self.order_repository.get_by_id(order_id)

        order.confirm()

        self.order_repository.save(order)

        return order.calculate_total()
```

هنا OrderService بتنسق العملية:

1. تجيب الطلب من Repository.
1. تستدعي سلوك الـ Domain Model.
1. تحفظ التغييرات.
1. ترجع النتيجة للـ Client.

لاحظ إن OrderService مش هي اللي بتقرر هل الطلب الفارغ ينفع يتأكد ولا لأ.

القرار ده موجود في Order.confirm().

وده فصل مهم بين مسؤولية التنسيق ومسؤولية قواعد المجال.

**رابعًا: Controller**

```python
class OrderController:

    def __init__(self, order_service):
        self.order_service = order_service

    def confirm(self, order_id):
        total = self.order_service.confirm_order(order_id)

        return {
            "status": "success",
            "total": total,
        }
```

الـ Controller مش محتاج يعرف تفاصيل الـ Repository أو طريقة تأكيد الطلب.

هو بيتعامل مع Service Layer.

## 4. أقرب GoF Pattern

مفيش GoF Pattern مكافئ مباشرة لـ Service Layer، لكن فيه تشابهات مهمة.

### Facade

**وجه التشابه:**

الاتنين ممكن يوفروا واجهة بسيطة تخفي تفاصيل مجموعة من العمليات الداخلية.

مثلًا:

```python
order_service.confirm_order(order_id)
```

الـ Client مش محتاج يعرف كل التفاصيل اللي بتحصل داخليًا.

**الاختلاف في Intent:**

Facade	Service Layer
يبسط واجهة Subsystem	يحدد Application Boundary
يخفي تعقيد مجموعة مكونات	يوفر مجموعة Application Operations
ممكن يكون مجرد واجهة تنسيقية	ممكن يدير Transactions وينسق Domain Logic

إذًا Service Layer مش مجرد Facade، رغم وجود تشابه واضح.

### Mediator

**وجه التشابه:**

الاتنين ممكن يقللوا الترابط المباشر بين مجموعة من Objects.

**الاختلاف في Intent:**

- Mediator ينظم التواصل والتفاعل بين Objects.
- Service Layer تعرض Application Operations وتنسق تنفيذها.

ممكن Service Layer تستخدم Mediator داخليًا، لكن مش هما نفس النمط.

## 5. الفرق بين Service Layer وDomain Model

دي نقطة مهمة جدًا.

خلينا نفترض إن عندنا عملية تأكيد الطلب.

مين مسؤول عن إيه؟

المسؤولية	Domain Model	Service Layer
هل الطلب الفارغ يمكن تأكيده؟	نعم	لا
تغيير حالة الطلب	نعم	يطلب تنفيذ التغيير
حساب قيمة الطلب	حسب قواعد المجال	ممكن ينسق استدعاء الحساب
جلب الطلب من Repository	لا	نعم، عادةً
تنسيق العملية	لا، مش مسؤوليته الأساسية	نعم
تحديد حدود المعاملة	ليس مسؤوليته الأساسية	ممكن يكون مسؤولًا عنها

القاعدة المهمة:

**Domain Model يمتلك قواعد المجال، وService Layer تنسق تنفيذ Application Operations.**

لكن ده مش معناه إن كل Business Logic لازم تكون داخل Domain Model؛ فيه قواعد تنسيقية أو قواعد خاصة بالـ Use Case مكانها الطبيعي في Application Service.

## 6. علاقته بالـ Application Architecture

هنا هنبدأ نربط الأنماط بالمعمارية.

ممكن Service Layer تظهر في Layered Architecture بالشكل ده:

```plain text
Presentation Layer
        |
        v
   Service Layer
        |
        v
   Domain Layer
        |
        v
 Data Access Layer
```

وده مثال شائع، مش الشكل الوحيد الممكن.

### Clean Architecture

في Clean Architecture عندنا Application Layer، واللي غالبًا بتحتوي على Use Cases.

ممكن نعتبر الـ Application Services تنفيذًا لفكرة Service Layer، لكن مش كل Application Service لازم يكون مطابقًا حرفيًا لتعريف Fowler.

مثلًا:

```plain text
Presentation
     |
     v
Application
     |
     +---- ConfirmOrderUseCase
     |
     +---- CreateOrderUseCase
     |
     v
Domain
     |
     v
Infrastructure
```

الـ Use Case هنا ممكن يمثل Application Operation من العمليات اللي بتقدمها Service Layer.

لكن لازم ناخد بالنا من نقطة:

**Service Layer في Fowler مش هي نفسها Clean Architecture Application Layer بالكامل.**

الأولى Pattern لتنظيم العمليات وحدود التطبيق، والثانية جزء من Architecture أوسع بتحدد توزيع المسؤوليات واتجاه الاعتماديات.

## 7. علاقته بـ DDD

في DDD عندنا مفهوم اسمه:

**Application Service**

وده قريب جدًا من Service Layer.

الـ Application Service مسؤولة عن:

- تنسيق Use Cases.
- استدعاء Repositories.
- استدعاء Domain Objects.
- التحكم في Workflow.
- إدارة المعاملات حسب التصميم.

لكنها مش المفروض تتحول لمكان نحط فيه كل قواعد المجال.

كمان DDD عنده مفهوم مختلف اسمه:

**Domain Service**

وده مسؤول عن Domain Logic لا تنتمي بشكل طبيعي إلى Entity أو Value Object واحد.

مثال:

```python
class MoneyTransferService:

    def transfer(self, source, destination, amount):
        if source.balance < amount:
            raise ValueError("Insufficient balance")

        source.withdraw(amount)
        destination.deposit(amount)
```

هنا عملية التحويل بتتعلق بحسابين، وممكن يكون من الأنسب تمثيلها كـ Domain Service حسب نموذج المجال.

أما Application Service فممكن تستدعي Domain Service دي وتنسق العملية مع Repository وTransaction.

إذًا:

Application Service	Domain Service
تنسيق Use Cases	تنفيذ Domain Logic
تتعامل مع Repositories	تتعامل مع Domain Objects
تهتم بـ Application Workflow	تهتم بقواعد المجال
غالبًا في Application Layer	في Domain Layer

## 8. علاقته بأودو (Odoo)

خلينا نربط الكلام بأودو.

لما يكون عندك:

```python
class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        ...
```

مش معنى إن عندك Method اسمها action_confirm إنها تلقائيًا Service Layer.

دي Method على الـ Model، وممكن تكون جزءًا من Domain/Application Behavior حسب مسؤولياتها الفعلية.

أما لو عندك Service مسؤولة عن تنسيق عملية كاملة، مثل:

1. جلب الطلب.
1. التحقق من صلاحيات العملية.
1. استدعاء action_confirm.
1. إرسال حدث إلى نظام خارجي.
1. تسجيل نتيجة العملية.

فهنا بنقرب من فكرة Service Layer.

لكن Odoo عنده تصميم Framework خاص به، ومش صح نصنف كل Model Method أو Controller على إنه تطبيق حرفي لـ Service Layer.

---

## 9. إمتى أستخدم Service Layer؟

الحالة	هل Service Layer مناسبة؟
عندك Web وMobile وAPI بيستخدموا نفس العمليات	نعم
محتاج تنسيق عدة Domain Objects	نعم
محتاج تنظيم حدود Use Cases	نعم
عندك CRUD بسيط جدًا	ممكن تكون بسيطة جدًا
عايز تحط كل Business Rules في مكان واحد	لا، ده غالبًا هيؤدي إلى Anemic Domain Model

## الخلاصة النهائية

Service Layer بتحدد العمليات اللي التطبيق بيقدمها للـ Clients، وبتنسق تنفيذها باستخدام الـ Domain Model والـ Repositories والخدمات الأخرى.

والفرق الأساسي:

- Transaction Script: تنظيم الـ Business Logic حول العمليات.
- Domain Model: تنظيم الـ Business Logic حول مفاهيم المجال.
- Table Module: تنظيم الـ Business Logic حول الجداول.
- Service Layer: تحديد وتنظيم Application Operations وتنسيق تنفيذها.

---

# مراجعة مجموعة Domain Logic Patterns كاملة

Chapter 9 — Fowler

Pattern	السؤال الأساسي الذي يجيب عنه
Transaction Script	كيف أنظم الـ Logic حول كل عملية؟
Domain Model	كيف أمثل المجال وسلوكه في Objects؟
Table Module	كيف أنظم الـ Logic حول جدول كامل؟
Service Layer	كيف أحدد عمليات التطبيق وأنسق تنفيذها؟

**ملحوظة مهمة:** الأنماط الأربعة مش اختيارات متعارضة بالكامل. ممكن تستخدم Service Layer مع Domain Model، مثلًا، لأن كل واحد بيعالج مشكلة مختلفة.

وبكده نكون خلصنا مجموعة **Domain Logic Patterns** بالكامل.


لا يا هندسة، **Service Layer مش نوع من Separated Interface، ومفيش علاقة تصنيفية مباشرة بينهم.**

لكن ممكن تستخدم الاتنين مع بعض في نفس التصميم.

خليني أوضح الفرق؛ لأن السؤال ده مهم معماريًا.

## 1. كل Pattern بيحل مشكلة مختلفة

**Service Layer**

بيجاوب عن السؤال:

إزاي أحدد العمليات اللي التطبيق بيقدمها للـ Clients، وأنظم تنفيذها؟

مثال:

```python
class OrderService:

    def create_order(self, items):
        ...

    def confirm_order(self, order_id):
        ...

    def cancel_order(self, order_id):
        ...
```

**Separated Interface**

بيجاوب عن سؤال مختلف:

إزاي أفصل تعريف الـ Interface عن الـ Implementation، وأخلي الـ Dependency Direction مناسب؟

مثال:

```plain text
application/
    interfaces/
        order_repository.py

    services/
        order_service.py

infrastructure/
    postgres/
        order_repository.py
```

## 2. إزاي نستخدم الاتنين مع بعض؟

تخيل التصميم التالي:

```plain text
             Presentation
                  |
                  v
          OrderService
                  |
                  v
          OrderRepository
             (Interface)
                  ^
                  |
       PostgresOrderRepository
          (Implementation)
```

هنا عندنا:

- OrderService: بتطبق فكرة Service Layer.
- OrderRepository: العقد أو الـ Interface.
- PostgresOrderRepository: التنفيذ الفعلي.
- فصل الـ Interface عن التنفيذ: تطبيق لفكرة Separated Interface.

لاحظ إن Service Layer ممكن تعتمد على Separated Interface، لكن ده لا يجعلها نوعًا منه.

## 3. مقارنة مباشرة

المقارنة	Service Layer	Separated Interface
التصنيف	Domain Logic Pattern	Base Pattern
المشكلة	تنظيم Application Operations	فصل العقد عن التنفيذ
التركيز	Application Boundary	Dependency Structure
يحتاج Interface؟	لا	نعم
ممكن تستخدمهم معًا؟	نعم	نعم

## 4. نقطة أعمق شوية

ممكن أصلًا تعمل Service Layer بدون Separated Interface:

```python
class OrderService:

    def __init__(self):
        self.repository = PostgresOrderRepository()
```

وده يحقق فكرة Service Layer، لكنه لا يحقق فصل الاعتماديات بالطريقة اللي بيستهدفها Separated Interface.

وممكن تعمل Separated Interface من غير Service Layer، مثلًا مع Repository أو Gateway.

---

**الخلاصة:**

العلاقة بينهم علاقة تكامل وليست علاقة وراثة أو تصنيف.

- Service Layer بتنظم *ما الذي يقدمه التطبيق؟*
- Separated Interface بتنظم *أين يوجد العقد؟ ومن يعتمد على من؟*

ودي نقطة مهمة جدًا في فهمك للعلاقة بين PoEAA وClean Architecture: ممكن تجمع Patterns من مجموعات مختلفة لتحقيق تصميم معماري واحد.


طيب كمل بنفس النمط في ال

## Data Source Architectural Patterns


تمام يا هندسة 😂

ندخل على مجموعة جديدة من كتاب Fowler:

# Data Source Architectural Patterns

المجموعة دي مختلفة عن المجموعات السابقة؛ لأن تركيزها الأساسي مش على تنظيم الـ Business Logic، لكن على **إزاي نمثل مصدر البيانات ونتعامل معاه داخل التطبيق.**

يعني هنتكلم عن العلاقة بين الـ Objects والـ Database، ومين المسؤول عن قراءة البيانات وكتابتها، وإزاي نفصل الـ Domain Logic عن تفاصيل الـ Persistence.

هنمشي بنفس منهجنا:

1. المشكلة التي يعالجها الـ Pattern.
1. الفكرة والحل.
1. مثال عملي باستخدام Python.
1. أقرب GoF Pattern، والفرق في الـ Intent.
1. علاقته بالـ Application Architecture.
1. علاقته بـ Clean Architecture وDDD وOdoo عند وجود ارتباط حقيقي.

وبالمناسبة، لازم نفرّق من البداية بين **Data Source Architectural Patterns** وبين **Data Access Patterns**؛ لأن Fowler بيصنفهم كمجموعتين مختلفتين.

المجموعة دي فيها 4 Patterns، وهنبدأ بأول واحد:

# 1. Table Data Gateway

(Data Source Architectural Pattern)

## 1. المشكلة (The Problem)

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

## 2. الفكرة (The Solution)

تعريف Fowler:

**An object that acts as a gateway to a database table. One instance handles all the rows in the table.** martinfowler.commartinfowler.com

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

## 3. مثال عملي باستخدام Python

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

## 5. أقرب GoF Pattern

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

## 6. علاقته بالـ Application Architecture

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
# Table Data Gateway
gateway.find_by_id(10)
```

ممكن يرجع:

```python
(10, 100, 500, "draft")
```

بينما Repository ممكن يرجع:

```python
order = order_repository.get_by_id(10)

order.confirm()
```

الفرق إن Repository بيتعامل مع مفهوم Order في الـ Domain، مش مجرد Row في جدول.

ممكن Repository يستخدم Table Data Gateway داخليًا، لكن الاتنين مش نفس الشيء.

## 8. علاقته بأودو (Odoo)

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

## 9. إمتى أستخدمه؟

الحالة	الاختيار
Transaction Script مع SQL متكرر	Table Data Gateway مناسب
عايز تجمع SQL الخاصة بجدول واحد	مناسب
عايز Domain Objects غنية ومستقلة عن Database Schema	Data Mapper غالبًا أنسب
عايز Object يحتوي بيانات Row وسلوكها ويعمل Persistence بنفسه	Active Record
عايز Object يمثل Row ويغلف Data Access فقط	Row Data Gateway

## الخلاصة

**Table Data Gateway** هو Object مسؤول عن جميع عمليات الوصول إلى جدول معين، وبيجمع SQL الخاصة بالجدول في مكان واحد.

وأهم فرق لازم تفتكره:

- Table Data Gateway: Object واحد للجدول كله.
- Row Data Gateway: Object لكل Row.
- Active Record: Object لكل Row، ويجمع Data Access مع Domain Logic.
- Data Mapper: يفصل Domain Objects عن تفاصيل Database Mapping.

---

**التالي: Row Data Gateway**

وده هيكون ممتع جدًا؛ لأننا هنغير وحدة التنظيم من Table كاملة إلى Record واحدة، وهنشوف ليه Fowler بيفصل بينه وبين Active Record رغم التشابه الكبير بينهم.


يلا نكمل يا هندسة 😂

المرة دي هنشوف Pattern قريب جدًا من اللي فات، لكن فيه اختلاف جوهري في طريقة تمثيل البيانات والتعامل معاها.

# 2. Row Data Gateway

(Data Source Architectural Pattern)

## 1. المشكلة (The Problem)

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

## 2. الفكرة (The Solution)

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

## 3. مثال عملي باستخدام Python

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

## 5. أقرب GoF Pattern

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

## 7. علاقته بالـ Application Architecture

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

## 9. علاقته بأودو (Odoo)

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


# 3. Active Record Pattern

هنكمل في مجموعة **Data Source Architectural Patterns** من كتاب *Patterns of Enterprise Application Architecture*.

خلينا نبدأ من أهم نقطة: الـ Active Record بيختلف عن الـ Row Data Gateway في إنه مش مجرد Object مسؤول عن الوصول للداتا؛ ده كمان بيحتوي على الـ Business Logic المرتبطة بالسجل نفسه.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال Python

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

    def cancel(self, connection):
        if self.status == "cancelled":
            raise ValueError("Order is already cancelled")

        self.status = "cancelled"
        self.save(connection)

    def save(self, connection):
        if self.id is None:
            cursor = connection.execute(
                """
                INSERT INTO orders (customer, total, status)
                VALUES (?, ?, ?)
                """,
                (self.customer, self.total, self.status)
            )

            self.id = cursor.lastrowid

        else:
            connection.execute(
                """
                UPDATE orders
                SET customer = ?, total = ?, status = ?
                WHERE id = ?
                """,
                (self.customer, self.total, self.status, self.id)
            )

        connection.commit()

    def delete(self, connection):
        if self.id is None:
            return

        connection.execute(
            "DELETE FROM orders WHERE id = ?",
            (self.id,)
        )

        connection.commit()
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

**الخلاصة:** الفرق مش في عدد الـ Objects، الفرق في الـ Intent وتوزيع المسؤوليات.

## 6. علاقته بالـ Application Architecture

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

## 8. علاقته بـ Odoo

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


# 3. Active Record Pattern

هنكمل في مجموعة **Data Source Architectural Patterns** من كتاب *Patterns of Enterprise Application Architecture*.

خلينا نبدأ من أهم نقطة: الـ Active Record بيختلف عن الـ Row Data Gateway في إنه مش مجرد Object مسؤول عن الوصول للداتا؛ ده كمان بيحتوي على الـ Business Logic المرتبطة بالسجل نفسه.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال Python

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

**الخلاصة:** الفرق مش في عدد الـ Objects، الفرق في الـ Intent وتوزيع المسؤوليات.

## 6. علاقته بالـ Application Architecture

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

## 8. علاقته بـ Odoo

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
