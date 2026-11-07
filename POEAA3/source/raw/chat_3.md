---
title: مقارنة Separated Interface (3)
url: https://chatgpt.com/g/g-p-6aef8f7176848191b87a5d98247e8052-poeaa/c/6aef93c9-c66c-83ea-9769-9017942db1b4
h1s: ['4. Dependent Mapping', '5. Embedded Value', '6. Serialized LOB', '7. Single Table Inheritance (STI)', '2. Query Object', '3. Repository', 'Web Presentation Patterns', '1. Model View Controller (MVC)']
len: 58262
msgCount: 8
---

يلا نكمل يا صاحبي 😂

وصلنا للنمط الرابع في مجموعة **Object-Relational Structural Patterns** في كتاب Fowler.

# 4. Dependent Mapping

(Object-Relational Structural Pattern)

## 1. المشكلة (Problem)

تخيل عندك Order، وكل Order يحتوي على مجموعة من OrderLine.

كل OrderLine بتمثل منتجًا داخل الطلب، ومعاها الكمية والسعر.

في عالم الـ Objects ممكن نمثل ده بالشكل التالي:

```python
class Order:
    def __init__(self, order_id):
        self.id = order_id
        self.lines = []

class OrderLine:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
```

لاحظ إن OrderLine مرتبطة بالـ Order اللي تحتوي عليها.

لكن عند تخزين البيانات في Database، عندنا سؤال:

هل لازم كل Object يكون له جدول مستقل وهوية مستقلة؟ وهل لازم نتعامل مع OrderLine باعتبارها كيانًا مستقلًا عن Order؟

مش بالضرورة.

في بعض التصميمات، الـ OrderLine ملهاش معنى حقيقي خارج الـ Order الخاصة بيها.

مثلًا:

- حذف الـ Order يستلزم حذف الـ OrderLines التابعة ليها.
- الـ OrderLine لا يمكن نقلها عشوائيًا إلى Order أخرى.
- دورة حياة الـ OrderLine مرتبطة بدورة حياة الـ Order.

**إذن المشكلة: إزاي نخزن Objects تابعة لـ Objects أخرى، بحيث تكون طريقة تخزينها مرتبطة بالـ Owner؟**

## 2. الفكرة والحل (Solution)

فكرة Dependent Mapping هي إننا نعامل الـ Dependent Object باعتباره جزءًا من الـ Owner Object من ناحية الـ Persistence Mapping.

يعني بدل ما نحتاج جدولًا مستقلًا لكل Object، ممكن نخزن بيانات الـ Dependent Object داخل جدول الـ Owner باستخدام أعمدة إضافية.

خلينا نشوف:

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER,
    order_date DATE,

    line_1_product_id INTEGER,
    line_1_quantity INTEGER,
    line_1_price DECIMAL(10, 2),

    line_2_product_id INTEGER,
    line_2_quantity INTEGER,
    line_2_price DECIMAL(10, 2)
);
```

هنا بيانات الـ Order والـ OrderLines مخزنة داخل نفس الجدول.

لكن خد بالك: ده مجرد توضيح للفكرة، ومش تصميم عملي مناسب لقائمة OrderLines غير محدودة؛ لأننا هنحتاج عددًا ثابتًا من مجموعات الأعمدة.

في التطبيقات الواقعية ممكن نستخدم طرق أخرى حسب شكل الـ Dependent Object والـ Mapping المطلوب.

**الفكرة الأساسية: الـ Dependent Object لا يُعامل بالضرورة كسجل مستقل، بل يمكن دمج بياناته في تخزين الـ Owner.**

## 3. مثال Python

خلينا نمثل الفكرة في الـ Domain Model:

```python
class OrderLine:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

    def subtotal(self):
        return self.quantity * self.price

class Order:
    def __init__(self, order_id):
        self.id = order_id
        self.lines = []

    def add_line(self, line):
        self.lines.append(line)

    def total(self):
        return sum(line.subtotal() for line in self.lines)
```

لاحظ إن OrderLine هنا Object مستقل في الذاكرة، لكن مش شرط يكون له جدول مستقل في قاعدة البيانات.

ممكن الـ Mapper يحول الـ Order والـ Lines إلى شكل تخزين واحد.

مثال توضيحي مبسط:

```python
def save_order(order, db):
    data = {
        "id": order.id,
        "lines": [
            {
                "product_id": line.product_id,
                "quantity": line.quantity,
                "price": str(line.price),
            }
            for line in order.lines
        ],
    }

    db.save(data)
```

المثال هنا بيستخدم شكل تخزين افتراضي، مش SQL Relational Mapping كامل.

---

## 4. علاقته بـ GoF Patterns

هل يوجد GoF Pattern مكافئ مباشر؟

**لا، مفيش GoF Pattern مكافئ مباشر.**

لكن ممكن تلاحظ تشابهًا مع:

- Composite: لأن عندنا Object يحتوي Objects أخرى في شكل شجري.
- Flyweight: ممكن يحصل خلط بسبب مشاركة بعض البيانات أو تقليل عدد Objects.

لكن الفرق:

**Composite** هدفه تمثيل هياكل Objects بشكل هرمي والتعامل مع الأجزاء والمجموعات بصورة موحدة.

أما **Dependent Mapping** فهدفه تحديد كيفية تخزين الـ Dependent Objects المرتبطة بالـ Owner داخل قاعدة البيانات.

يعني ممكن تستخدم Composite في الـ Domain Model، وتستخدم Dependent Mapping في الـ Persistence، لكن مش بدائل لبعض.

## 5. الفرق بين Dependent Mapping وAssociation Table Mapping

دي نقطة مهمة جدًا.

**Association Table Mapping:**

بنستخدم جدولًا وسيطًا لتخزين العلاقة بين طرفين.

مثال: Student وCourse.

```plain text
Courses  <---  Student_Courses  <---  Students
```

**Dependent Mapping:**

بنخزن بيانات Object تابع داخل تخزين الـ Owner، بدل التعامل معه بالضرورة كسجل مستقل.

مثال: Order وOrderLine.

```plain text
OrderLine  <---  Order
```

الفرق في الهدف:

- Association Table Mapping: تخزين العلاقة بين Objects.
- Dependent Mapping: تخزين بيانات Objects التابعة ضمن تخزين الـ Owner.

---

## 6. علاقته بـ Application Architecture وClean Architecture

النمط ده مش Application Architecture Pattern.

هو جزء من Persistence Mapping.

في Clean Architecture:

- الـ Domain يحدد تركيب Order و`OrderLine`.
- الـ Infrastructure مسؤولة عن طريقة تخزينهم.
- الـ Domain مش محتاج يعرف هل الـ Lines مخزنة في نفس الجدول أو في جدول منفصل.

وده مثال مهم على فصل الـ Domain Model عن تفاصيل الـ Persistence.

## 7. علاقته بـ DDD

هنا لازم نفرق بين مفهومين:

**Dependent Object في Fowler** و **Entity / Value Object في DDD**.

مش كل Dependent Object لازم يكون Value Object، ومش كل Value Object لازم يُخزن باستخدام Dependent Mapping.

لكن فيه علاقة شائعة:

لو OrderLine عبارة عن جزء من Order، ومش لها هوية مستقلة خارج الـ Order، ممكن تكون Value Object أو جزءًا من Aggregate حسب قواعد المجال.

وفي DDD، ممكن يكون عندنا:

```plain text
Order Aggregate
    |
    +---- OrderLine
    |
    +---- OrderLine
    |
    +---- OrderLine
```

الـ Order هنا هو Aggregate Root، والـ OrderLine جزء من الـ Aggregate.

لكن خد بالك:

**Aggregate Boundary مش هو نفسه Dependent Mapping.**

الأول بيحدد حدود الاتساق والتحكم في التغييرات، والثاني بيحدد طريقة تخزين الـ Objects.

ممكن يكون عندك Dependent Object مخزن في جدول مستقل، ومع ذلك يظل تابعًا للـ Owner في الـ Domain.

---

## 8. علاقته بـ Odoo

خلينا نستخدم مثال sale.order و`sale.order.line`.

```python
class SaleOrder(models.Model):
    _inherit = "sale.order"

    custom_note = fields.Char()

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    custom_reference = fields.Char()
```

في Odoo:

- sale.order له جدول مستقل.
- sale.order.line له جدول مستقل.
- العلاقة بينهما ممثلة باستخدام order_id من نوع Many2one.

إذن هل sale.order.line مثال على Dependent Mapping؟

**مش من ناحية الـ Persistence Mapping بالمعنى الدقيق للنمط اللي شرحناه.**

لأن Odoo يخزن كل OrderLine في Row مستقلة داخل جدول مستقل.

لكن ممكن تكون OrderLine تابعة للـ Order من ناحية دورة الحياة والـ Domain Model.

وده يوضح الفرق بين:

- Domain Dependency.
- Persistence Dependency.

مش كل Object تابع لغيره في الـ Domain لازم يكون Dependent Mapping في قاعدة البيانات.

---

## 9. إمتى نستخدم Dependent Mapping؟

يكون مناسبًا لما:

- يكون الـ Dependent Object جزءًا من الـ Owner.
- تكون حياته مرتبطة بحياة الـ Owner.
- لا تحتاج التعامل معه كسجل مستقل.
- يكون دمج بياناته في تخزين الـ Owner مناسبًا لطبيعة البيانات.

لكن لو الـ Objects كثيرة أو متغيرة العدد، لازم تختار استراتيجية تخزين مناسبة؛ مش معنى Dependent Mapping إنك تحشر كل البيانات في أعمدة ثابتة.

---

## ملخص النمط

السؤال الذي يجيب عنه Dependent Mapping:

> How do you map dependent objects as part of their owner's persistence representation?

الفكرة:

**بدل ما يكون لكل Object تخزين مستقل بالضرورة، ممكن ندمج بيانات الـ Dependent Object داخل تخزين الـ Owner.**

## خريطة المجموعة حتى الآن

1. **Identity Field**
  ربط هوية الـ Object بهوية الـ Database Row.
1. **Foreign Key Mapping**
  تمثيل العلاقات باستخدام Foreign Keys.
1. **Association Table Mapping**
  تمثيل العلاقات باستخدام جدول وسيط.
1. **Dependent Mapping**
  دمج تخزين الـ Dependent Object مع الـ Owner.

**التالي في الكتاب: Embedded Value.**

وده هيكون مرتبط جدًا بالـ Value Objects اللي شرحناها قبل كده، وهنشوف إزاي نخزن مجموعة قيم داخل جدول الـ Owner بدل ما نحتاج جدولًا مستقلًا لها.


نكمل يا صاحبي 😂

النمط الخامس في مجموعة **Object-Relational Structural Patterns** هو:

# 5. Embedded Value

(Object-Relational Structural Pattern)

## 1. المشكلة (Problem)

تخيل عندك Customer، وكل Customer عنده عنوان Address.

في عالم الـ Objects، ممكن نمثل العنوان كـ Object مستقل:

```python
class Address:
    def __init__(self, city, street, postal_code):
        self.city = city
        self.street = street
        self.postal_code = postal_code

class Customer:
    def __init__(self, customer_id, name, address):
        self.id = customer_id
        self.name = name
        self.address = address
```

لاحظ إن Customer يحتوي على Address Object.

لكن في قاعدة البيانات، عندنا اختيارين:

1. نعمل جدول مستقل للعناوين ونربطه بالـ Customer.
1. نخزن بيانات العنوان داخل جدول الـ Customer نفسه.

هل فعلًا محتاجين جدول مستقل لكل Address؟

لو العنوان مجرد مجموعة قيم تخص العميل، ومش محتاجين نتعامل معاه ككيان مستقل، إنشاء جدول منفصل ممكن يكون تعقيدًا غير ضروري.

**إذن المشكلة: إزاي نخزن Value Object داخل جدول الـ Owner من غير ما ننشئ جدولًا مستقلًا له؟**

## 2. الفكرة والحل (Solution)

فكرة Embedded Value هي إننا نحتفظ بالـ Object كـ Object مستقل داخل الـ Domain Model، لكن عند التخزين ندمج بياناته كأعمدة داخل جدول الـ Owner.

خلينا نشوف:

تصميم قاعدة البيانات:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),

    address_city VARCHAR(100),
    address_street VARCHAR(150),
    address_postal_code VARCHAR(20)
);
```

لاحظ إن مفيش جدول اسمه addresses.

بيانات العنوان موجودة داخل جدول customers.

العلاقة من ناحية الـ Mapping:

```plain text
Address Object  <---  Customer Object
       |                    |
       |                    |
       +--------+-----------+
                |
                v
          customers Table
       ┌─────────────────────┐
       │ id                  │
       │ name                │
       │ address_city        │
       │ address_street      │
       │ address_postal_code│
       └─────────────────────┘
```

الـ Address لسه Object في الذاكرة، لكن بياناته اتخزنت كجزء من Row الـ Customer.

**وده جوهر Embedded Value.**

## 3. مثال Python

خلينا نبني المثال بصورة أوضح.

### Domain Model

```python
class Address:
    def __init__(self, city, street, postal_code):
        self.city = city
        self.street = street
        self.postal_code = postal_code

class Customer:
    def __init__(self, customer_id, name, address):
        self.id = customer_id
        self.name = name
        self.address = address
```

### Persistence Mapping

عند الحفظ:

```python
def save_customer(customer, db):
    db.execute(
        """
        UPDATE customers
        SET
            name = %s,
            address_city = %s,
            address_street = %s,
            address_postal_code = %s
        WHERE id = %s
        """,
        (
            customer.name,
            customer.address.city,
            customer.address.street,
            customer.address.postal_code,
            customer.id,
        )
    )
```

وعند التحميل:

```python
def load_customer(customer_id, db):
    row = db.execute(
        """
        SELECT *
        FROM customers
        WHERE id = %s
        """,
        (customer_id,)
    ).fetchone()

    if row is None:
        return None

    address = Address(
        city=row["address_city"],
        street=row["address_street"],
        postal_code=row["address_postal_code"],
    )

    return Customer(
        customer_id=row["id"],
        name=row["name"],
        address=address,
    )
```

لاحظ هنا إننا بنعمل Mapping بين:

- مجموعة أعمدة في Database.
- Object واحد في Domain Model.

ومش محتاجين Query إضافية لتحميل العنوان؛ لأنه موجود بالفعل في نفس Row.

---

## 4. علاقته بـ GoF Patterns

هل فيه GoF Pattern مكافئ مباشر؟

**لا، مفيش GoF Pattern مكافئ مباشر.**

لكن ممكن تلاحظ تشابهًا مع Composite؛ لأن عندنا Object يحتوي Objects أخرى.

الفرق:

- Composite هدفه تمثيل Hierarchical Object Structures.
- Embedded Value هدفه تحديد طريقة تخزين Value Object داخل جدول الـ Owner.

ممكن تستخدم Composite في تصميم الـ Objects، وتستخدم Embedded Value في الـ Persistence، لكن كل واحد بيحل مشكلة مختلفة.

---

## 5. الفرق بين Embedded Value وDependent Mapping

دي مقارنة مهمة جدًا.

**Embedded Value:**

بنخزن بيانات Value Object كأعمدة داخل جدول الـ Owner.

مثال:

Customer يحتوي على Address، وبيانات العنوان موجودة في جدول Customer.

**Dependent Mapping:**

بنخزن بيانات Object تابع كجزء من تمثيل تخزين الـ Owner، ومش شرط يكون Value Object.

الفرق الأساسي إن Embedded Value بيركز على تخزين مجموعة قيم كجزء من Row الـ Owner، بينما Dependent Mapping مفهوم أوسع لتخزين Objects التابعة.

بالتالي Embedded Value ممكن يُعتبر حالة متخصصة من فكرة Dependent Mapping، لكن Fowler بيفصلهم كنمطين مختلفين.

---

## 6. علاقته بـ Value Object في DDD

هنا العلاقة قوية جدًا.

في DDD، الـ Value Object:

- لا يمتلك Identity مستقلة.
- بيتحدد من خلال قيمه.
- غالبًا بيكون Immutable.
- ممكن يحتوي Business Behavior مرتبط بالقيم.

مثال:

```python
class Money:
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency

    def add(self, other):
        if self.currency != other.currency:
            raise ValueError("Currency mismatch")

        return Money(
            self.amount + other.amount,
            self.currency
        )
```

ممكن يكون عندك:

```python
class Order:
    def __init__(self, order_id, total):
        self.id = order_id
        self.total = total
```

والـ Money Object يتخزن داخل جدول orders كعمودين:

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    total_amount DECIMAL(12, 2),
    total_currency VARCHAR(3)
);
```

يعني:

```plain text
Money Object  <---  Order Object
     |                  |
     +--------+---------+
              |
              v
         orders Table
```

لكن انتبه: مش كل Value Object لازم نستخدم معاه Embedded Value؛ ممكن نخزن بعض أنواع الـ Value Objects بطرق أخرى حسب طبيعة البيانات والتصميم.

---

## 7. علاقته بـ Clean Architecture

Embedded Value مش Application Architecture Pattern.

هو Persistence Mapping Pattern.

في Clean Architecture:

- الـ Domain يحتوي Address أو Money كـ Objects.
- الـ Infrastructure مسؤولة عن تحويلهم إلى أعمدة.
- الـ Domain مش محتاج يعرف إن address_city عمود في جدول customers.

وده تطبيق واضح لفصل الـ Domain Model عن تفاصيل التخزين.

---

## 8. علاقته بـ Odoo

خلينا ناخد مثال عملي.

في Odoo، عندنا res.partner، والعنوان غالبًا ممثل باستخدام Fields داخل نفس Model:

```python
class Partner(models.Model):
    _inherit = "res.partner"

    building_number = fields.Char()
    street_name = fields.Char()
    postal_code_custom = fields.Char()
```

الـ Fields دي بتُخزن عادةً كأعمدة في جدول res_partner.

لكن هل ده معناه إن Odoo بيطبق Embedded Value بالكامل؟

**مش بالضرورة.**

لأننا هنا بنضيف Fields مباشرة للـ Model، ومش بالضرورة عندنا Value Object مستقل في الـ Domain Model.

كمان Odoo عنده Delegation وClassical Inheritance وORM mechanisms مختلفة، فلازم نصنف كل حالة حسب تصميمها الفعلي.

---

## 9. الفرق بين Embedded Value وForeign Key Mapping

خلينا نثبت الفرق:

**Embedded Value:**

```plain text
Address Object  <---  Customer Object
       \                  /
        \                /
         +--------------+
                |
                v
         Customer Table
```

الـ Address بيتخزن داخل جدول Customer نفسه.

**Foreign Key Mapping:**

```plain text
Address Table  <---  Customer Table
```

الـ Customer بيحتفظ بـ Foreign Key يشير إلى سجل مستقل في جدول Address.

المقارنة	Embedded Value	Foreign Key Mapping
مكان التخزين	جدول الـ Owner	جدول مرتبط
Identity مستقلة	غالبًا لا	ممكن توجد
Query إضافية	غالبًا لا	حسب التحميل
المشاركة بين عدة Owners	غير مناسبة عادةً	ممكنة حسب العلاقة

---

## 10. إمتى نستخدم Embedded Value؟

استخدمه لما:

- تكون البيانات مجموعة قيم مرتبطة بالـ Owner.
- مفيش احتياج لهوية مستقلة.
- مش محتاج مشاركة نفس السجل بين Owners متعددين.
- البيانات غالبًا بتُقرأ وتُحدّث مع الـ Owner.

وتجنبه لما يكون عندك Object محتاج Lifecycle مستقل أو علاقات مستقلة أو استعلامات وإدارة منفصلة.

---

## ملخص النمط

السؤال اللي بيجاوب عنه Embedded Value:

> How do you map a value object into the same database table as its owner?

الإجابة:

**بنحوّل خصائص الـ Value Object إلى أعمدة داخل جدول الـ Owner.**

## خريطة المجموعة حتى الآن

1. **Identity Field** — هوية الـ Object.
1. **Foreign Key Mapping** — العلاقات باستخدام Foreign Keys.
1. **Association Table Mapping** — العلاقات باستخدام جدول وسيط.
1. **Dependent Mapping** — تخزين Objects التابعة ضمن تمثيل الـ Owner.
1. **Embedded Value** — تخزين Value Object كأعمدة داخل جدول الـ Owner.

**التالي في ترتيب Fowler: Serialized LOB.**

وده هيكون عكس فكرة Embedded Value من ناحية طريقة التخزين تقريبًا: بدل ما نفك خصائص الـ Object إلى أعمدة، هنشوف إزاي نخزن مجموعة Objects كاملة في عمود واحد باستخدام Serialization.


نكمل يا صاحبي 😂

النمط السادس في مجموعة **Object-Relational Structural Patterns** هو:

# 6. Serialized LOB

(Object-Relational Structural Pattern)

## 1. المشكلة (Problem)

تخيل عندك Order يحتوي على مجموعة Objects داخلية:

- Order Information
- Order Items
- Shipping Details
- Custom Attributes
- Metadata

ممكن نمثلها في Python بالشكل التالي:

```python
class Order:
    def __init__(self, order_id, items, shipping, metadata):
        self.id = order_id
        self.items = items
        self.shipping = shipping
        self.metadata = metadata
```

في النمط السابق Embedded Value، كنا بنفك خصائص الـ Object ونحولها إلى أعمدة داخل جدول الـ Owner.

لكن تخيل عندك Object Graph كبير ومتغير، فيه Objects متداخلة وCollections.

هل لازم نحول كل Property إلى Column؟

ده ممكن ينتج عنه:

- عدد كبير جدًا من الأعمدة.
- صعوبة التعامل مع Structure متغير.
- تعقيد في Mapping للـ Objects المتداخلة.
- تغييرات متكررة في Schema كل ما شكل الـ Object يتغير.

**إذن المشكلة: إزاي نخزن Object Graph معقد داخل قاعدة بيانات علائقية، من غير ما نفك كل Object إلى أعمدة وجداول؟**

## 2. الفكرة والحل (Solution)

فكرة Serialized LOB هي:

نحوّل الـ Object Graph إلى صيغة Serialized، ونخزن الناتج بالكامل داخل عمود واحد في قاعدة البيانات.

LOB اختصار لـ:

**Large Object**

والمقصود هنا تخزين محتوى كبير داخل عمود، سواء باستخدام نوع BLOB أو CLOB أو نوع مناسب حسب قاعدة البيانات.

خلينا نشوف الفكرة:

**Object Graph**

Order + Items + Shipping + Metadata

**Serialization**

**Serialized Data**

JSON / XML / Binary Representation

**Database Storage**

**Single Database Column**

orders.serialized_data

يعني بدل ما يكون عندنا أعمدة لكل خاصية، بنخزن الـ Object Graph كله في عمود واحد.

وعند القراءة بنعمل العكس:

**Deserialization** لإعادة بناء الـ Objects.

---

## 3. مثال عملي باستخدام Python

خلينا نستخدم JSON كمثال.

### أولًا: Domain Objects

```python
class OrderItem:
    def __init__(self, product_id, quantity, price):
        self.product_id = product_id
        self.quantity = quantity
        self.price = price

class Shipping:
    def __init__(self, city, address):
        self.city = city
        self.address = address

class Order:
    def __init__(self, order_id, items, shipping):
        self.id = order_id
        self.items = items
        self.shipping = shipping
```

### ثانيًا: Serialization

JSON مش بيقدر يحول Python Objects تلقائيًا بشكل عام، فهنحتاج نحولها إلى Dictionaries:

```python
import json

def serialize_order(order):
    data = {
        "id": order.id,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": item.price,
            }
            for item in order.items
        ],
        "shipping": {
            "city": order.shipping.city,
            "address": order.shipping.address,
        },
    }

    return json.dumps(data)
```

### ثالثًا: تخزين البيانات

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    serialized_data JSONB NOT NULL
);
```

وبعدها ممكن نخزن الناتج في العمود:

```python
serialized = serialize_order(order)

db.execute(
    """
    INSERT INTO orders (id, serialized_data)
    VALUES (%s, %s::jsonb)
    """,
    (order.id, serialized)
)
```

### رابعًا: Deserialization

نرجع البيانات إلى Objects:

```python
def deserialize_order(serialized):
    data = json.loads(serialized)

    items = [
        OrderItem(
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"],
        )
        for item in data["items"]
    ]

    shipping = Shipping(
        city=data["shipping"]["city"],
        address=data["shipping"]["address"],
    )

    return Order(
        order_id=data["id"],
        items=items,
        shipping=shipping,
    )
```

كده قدرنا نخزن Object Graph ونرجعه تاني.

المثال تعليمي. JSONB في PostgreSQL ليس Binary Serialization بالمعنى الحرفي، لكنه تمثيل JSON مخزن داخل قاعدة البيانات. Fowler يتكلم عن Serialization عمومًا، مش JSON فقط.

---

## 4. علاقته بـ GoF Patterns

هل فيه GoF Pattern مكافئ مباشر؟

**لا، مفيش GoF Pattern مكافئ مباشر.**

لكن فيه تشابه مع:

- Memento: لأن الاتنين ممكن يحتفظوا بحالة Object لاستعادتها لاحقًا.
- Prototype: لأننا ممكن نعيد بناء Objects من نسخة محفوظة من بياناتها.

لكن الفرق في الـ Intent:

**Memento** هدفه حفظ واستعادة حالة Object، غالبًا لدعم Undo/Redo أو استعادة الحالة.

**Serialized LOB** هدفه تخزين Object Graph داخل قاعدة البيانات في صورة Serialized Representation.

ممكن تستخدم Serialization داخل تطبيق بيطبق Memento، لكن مش معناها إن الاتنين نفس النمط.

---

## 5. الفرق بين Embedded Value وSerialized LOB

دي أهم مقارنة في الجزء ده.

**Embedded Value:**

بنفك الـ Object إلى مجموعة أعمدة واضحة داخل جدول الـ Owner.

مثال:

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    address_city VARCHAR(100),
    address_street VARCHAR(100)
);
```

**Serialized LOB:**

بنحول الـ Object Graph إلى صيغة واحدة ونخزنها في عمود واحد.

```sql
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    address_data JSONB
);
```

الفرق:

المقارنة	Embedded Value	Serialized LOB
طريقة التخزين	أعمدة متعددة	عمود واحد
البيانات	Properties مفككة	Serialized Structure
SQL Queries	سهلة نسبيًا	تعتمد على صيغة التخزين
Schema	أكثر ارتباطًا بالـ Object Structure	أكثر مرونة
تعديل خاصية	تحديث عمود	تحديث محتوى Serialized

---

## 6. علاقته بـ Application Architecture وClean Architecture

Serialized LOB مش Application Architecture Pattern.

هو Persistence Mapping Pattern.

في Clean Architecture:

- الـ Domain يحتوي Objects والـ Business Behavior.
- الـ Infrastructure مسؤولة عن Serialization وDeserialization.
- الـ Repository يخفي تفاصيل التخزين عن الـ Domain.

مثلاً، الـ Domain يتعامل مع:

```python
order = repository.get_order(10)
```

ومش محتاج يعرف إن البيانات مخزنة في JSONB أو BLOB.

لكن لازم نحافظ على فصل الـ Serialization Format عن الـ Domain Model قدر الإمكان.

---

## 7. علاقته بـ DDD

هنا فيه علاقة مهمة.

ممكن يكون عندك Aggregate كبير نسبيًا، وتريد تخزينه كوحدة واحدة.

مثلًا:

```plain text
Order Aggregate
    |
    +---- OrderLine
    |
    +---- ShippingInfo
    |
    +---- Metadata
```

ممكن تستخدم Serialized LOB لتخزين أجزاء من الـ Aggregate.

لكن فيه نقطة مهمة جدًا:

**DDD لا يفرض إن كل Aggregate يتخزن في Serialized LOB.**

كمان تخزين Aggregate بالكامل في JSON لا يعني تلقائيًا إنك حققت Aggregate Consistency؛ قواعد الاتساق لازم تظل مطبقة في الـ Domain وفي حدود المعاملات.

---

## 8. علاقته بـ Odoo وPostgreSQL

خلينا ناخد مثال من Odoo.

عندك حقل fields.Json:

```python
class MyModel(models.Model):
    _name = "my.model"

    name = fields.Char()
    metadata = fields.Json()
```

في PostgreSQL، حقل JSON في Odoo بيُخزن باستخدام نوع JSONB.

وده قريب من فكرة Serialized LOB من ناحية تخزين Structure داخل عمود واحد.

لكن لازم نفرق بين حاجتين:

- fields.Json مجرد نوع حقل يوفر تخزين JSON.
- Serialized LOB Pattern هو قرار تصميمي لتخزين Object Graph كتمثيل Serialized.

مش كل JSON Field في Odoo معناه إننا طبقنا Serialized LOB على مستوى التصميم.

### إمتى ده يكون مفيد في Odoo؟

مثلًا لو عندك Integration مع External System وبتحتاج تحتفظ بـ Payload متغير:

```python
external_payload = fields.Json()
```

ممكن يكون مناسب لتخزين بيانات الـ Integration اللي مش محتاج تحول كل خاصية فيها إلى Column مستقل.

لكن لو البيانات أساسية في Business Logic، وبتحتاج:

- Filtering متكرر.
- Joins.
- Constraints.
- Aggregations.
- Reporting.

فغالبًا الأفضل تصميم Fields وRelations واضحة بدل وضع كل شيء داخل JSON.

---

## 9. عيوب ومخاطر Serialized LOB

لازم نكون واضحين إن المرونة هنا ليها تكلفة.

1. **Querying:** الاستعلام عن البيانات الداخلية ممكن يكون أصعب أو أقل كفاءة حسب صيغة التخزين.
1. **Indexing:** محتاج تفكر في Indexes مناسبة للخصائص اللي بتبحث عنها.
1. **Schema Evolution:** تغيير شكل البيانات يحتاج Versioning أو Migration Strategy.
1. **Partial Updates:** تعديل جزء صغير من البيانات ممكن يتطلب التعامل مع الـ Serialized Structure.
1. **Data Integrity:** قيود الـ Foreign Keys والـ Database Constraints مش بنفس سهولة البيانات المفككة إلى جداول وأعمدة.
1. **Concurrency:** تعديل أجزاء مختلفة من نفس الـ Document ممكن يسبب تعارضات حسب طريقة التحديث.

---

## 10. إمتى نستخدم Serialized LOB؟

مناسب لما:

- عندك Object Graph معقد أو متغير.
- مش محتاج تعمل Queries كثيرة على كل Property.
- البيانات غالبًا بتُقرأ وتُكتب كوحدة واحدة.
- المرونة أهم من Relational Queryability.

مش مناسب لما تكون البيانات الأساسية محتاجة علاقات واستعلامات وقيود قوية على مستوى قاعدة البيانات.

---

## ملخص النمط

السؤال اللي بيجاوب عنه Serialized LOB:

> How do you store an object graph as a serialized representation in a single database column?

الإجابة:

**نحوّل الـ Object Graph إلى Serialized Representation ونخزنه داخل LOB واحد في قاعدة البيانات.**

## خريطة المجموعة حتى الآن

1. **Identity Field** — ربط هوية الـ Object بهوية الـ Row.
1. **Foreign Key Mapping** — تمثيل العلاقات باستخدام Foreign Keys.
1. **Association Table Mapping** — تمثيل العلاقات باستخدام جدول وسيط.
1. **Dependent Mapping** — تخزين Objects التابعة ضمن تمثيل الـ Owner.
1. **Embedded Value** — تخزين Value Object كأعمدة داخل جدول الـ Owner.
1. **Serialized LOB** — تخزين Object Graph كبيانات Serialized داخل عمود واحد.

**التالي في ترتيب Fowler: Single Table Inheritance.**

وده هيدخلنا في موضوع مهم جدًا: إزاي نمثل الـ Class Inheritance في Object-Oriented Model باستخدام Relational Database؟


# 7. Single Table Inheritance (STI)

خلينا نكمل في **Object-Relational Structural Patterns** بنفس طريقتنا.

## 1. المشكلة (Problem)

عندنا في الـ OOP مفهوم اسمه **Inheritance**.

يعني ممكن يكون عندنا Class أساسي اسمه Payment، ويتفرع منه أنواع مختلفة:

```plain text
             Payment
                |
        -----------------
        |               |
   CardPayment     CashPayment
```

كل نوع له بيانات مشتركة وبيانات خاصة بيه.

مثلًا:

- Payment: المبلغ والتاريخ.
- CardPayment: رقم البطاقة وآخر أربعة أرقام.
- CashPayment: الشخص الذي استلم المبلغ.

المشكلة إن قواعد البيانات العلائقية Relational Databases لا تدعم الـ Class Inheritance بنفس طريقة Python.

فالسؤال هنا:

**إزاي نمثل الـ Inheritance Hierarchy دي داخل Database؟**

## 2. الفكرة والحل (Solution)

فكرة **Single Table Inheritance** بسيطة:

بدل ما نعمل جدول لكل Class، نعمل **جدول واحد فقط** يحتوي على بيانات الـ Parent وكل الـ Subclasses.

ونضيف عمود اسمه **Discriminator Column** يحدد نوع الـ Object الموجود في كل Row.

**الـ Class Hierarchy في Python**

```plain text
               Payment
                  |
         -------------------
         |                 |
    CardPayment       CashPayment
```

---

**التمثيل في Database**

جدول واحد اسمه payments

id	payment_type	amount	card_last4	received_by
1	card	500	1234	NULL
2	cash	300	NULL	Ahmed
3	card	700	5678	NULL

---

كل Row يتم تحديد نوعها من خلال payment_type

(card) CardPayment

(cash) CashPayment

لاحظ إن:

- amount موجود لكل أنواع الـ Payment.
- card_last4 خاص بالـ Card Payment.
- received_by خاص بالـ Cash Payment.
- الأعمدة غير المستخدمة في نوع معين بتكون NULL.

وده جوهر النمط.

## 3. مثال عملي باستخدام Python

أولًا، نعرّف الـ Classes:

```python
class Payment:
    def __init__(self, amount):
        self.amount = amount

class CardPayment(Payment):
    def __init__(self, amount, card_last4):
        super().__init__(amount)
        self.card_last4 = card_last4

class CashPayment(Payment):
    def __init__(self, amount, received_by):
        super().__init__(amount)
        self.received_by = received_by
```

دلوقتي نحتاج نمثلهم في جدول واحد:

```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    payment_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    card_last4 VARCHAR(4),
    received_by VARCHAR(100)
);
```

نضيف بيانات:

```sql
INSERT INTO payments
    (id, payment_type, amount, card_last4, received_by)
VALUES
    (1, 'card', 500, '1234', NULL),
    (2, 'cash', 300, NULL, 'Ahmed');
```

طيب لما نقرأ البيانات من Database، إزاي نعرف نرجع أي Class؟

هنا بييجي دور الـ **Discriminator**:

```python
def load_payment(row):
    if row["payment_type"] == "card":
        return CardPayment(
            amount=row["amount"],
            card_last4=row["card_last4"]
        )

    if row["payment_type"] == "cash":
        return CashPayment(
            amount=row["amount"],
            received_by=row["received_by"]
        )

    raise ValueError("Unknown payment type")
```

لاحظ إن الـ payment_type هو اللي بيحدد الـ Class اللي هننشئ منه الـ Object.

إذًا عملية التحميل بتكون:

```plain text
Python Objects
      |
      | Save
      ↓
  payments Table
      |
      | Load + Discriminator
      ↓
Concrete Python Objects
```

وبصياغة اتجاهها من اليمين للشمال:

```plain text
Concrete Python Objects  <---  Discriminator  <---  payments Table
```

**ملاحظة مهمة:** الـ Database نفسها مش بتعرف إن فيه Inheritance. إحنا بننفذ استراتيجية التخزين دي عن طريق الـ Schema والـ ORM أو الـ Mapper.

## 4. أقرب GoF Pattern

هل فيه GoF Pattern مطابق لـ Single Table Inheritance؟

**لا، مفيش GoF Pattern مكافئ مباشر.**

لكن فيه تشابه جزئي مع:

### Factory Method

لما نقرأ Row ونشوف قيمة payment_type، بنختار الـ Class المناسب لإنشاء الـ Object.

يعني:

```plain text
Row + Discriminator
          |
          ↓
     Object Creation
          |
     ----------------
     |              |
 CardPayment    CashPayment
```

لكن خلي بالك من الفرق:

- **Factory Method:** هدفه تنظيم إنشاء Objects وتحديد الـ Concrete Product.
- **Single Table Inheritance:** هدفه تحديد طريقة تخزين Class Inheritance Hierarchy داخل جدول واحد.

إذًا وجود Factory أثناء تحميل البيانات مش معناه إن STI هو Factory Method.

## 5. علاقته بالأنماط الأخرى

أهم مقارنة هنا هي مع أنماط تخزين الـ Inheritance الأخرى.

النمط	طريقة التخزين
Single Table Inheritance	جدول واحد لكل الـ Hierarchy
Class Table Inheritance	جدول للـ Parent وجدول لكل Subclass
Concrete Table Inheritance	جدول مستقل لكل Concrete Class

هنشرح كل واحد في وقته، لكن الفرق الأساسي إن STI بيجمع كل البيانات في جدول واحد.

## 6. علاقته بالـ Application Architecture

خلينا نفصل بين مستويين:

- **Application Architecture:** بنقسم التطبيق إلى Layers أو Components إزاي؟
- **Single Table Inheritance:** بنمثل الـ Class Inheritance في قاعدة البيانات إزاي؟

إذًا STI مش Application Architecture Pattern، ده **Object-Relational Mapping Pattern**.

### علاقته بـ Clean Architecture

تخيل عندنا:

```plain text
Domain Layer:
    Payment
    CardPayment
    CashPayment

Infrastructure Layer:
    PaymentMapper
    Database
```

الـ Domain Layer مش المفروض يعرف إننا بنستخدم:

- جدول واحد.
- عمود اسمه payment_type.
- أعمدة NULL للأنواع الأخرى.

الـ Infrastructure هي اللي مسؤولة عن تحويل الـ Database Rows إلى Domain Objects والعكس.

وده مثال واضح على فصل الـ Persistence Concerns عن الـ Domain Model.

## 7. علاقته بـ DDD

في DDD ممكن يكون عندك Inheritance داخل الـ Domain Model.

مثلًا:

- Payment كـ Base Class.
- CardPayment و`CashPayment` كـ Subclasses.

لكن وجود Inheritance في الـ Domain لا يعني إنك لازم تستخدم Single Table Inheritance في قاعدة البيانات.

ممكن تختار:

- Single Table Inheritance.
- Class Table Inheritance.
- Concrete Table Inheritance.
- أو حتى Composition بدل Inheritance.

**القرار هنا متعلق بشكل الـ Domain Model واحتياجات الـ Persistence، مش مجرد إن عندك وراثة في الكود.**

## 8. علاقته بـ Odoo

هنا محتاجين نكون دقيقين؛ لأن Odoo عنده أكتر من استراتيجية للـ Model Inheritance.

### _inherit

لما تستخدم _inherit بدون _name، فأنت غالبًا بتوسع Model موجود بالفعل، وتضيف له Fields أو Methods.

ده مش معناه تلقائيًا إنك بتطبق Single Table Inheritance.

### _name مع _inherit

لما تنشئ Model جديد باستخدام _name و`_inherit`، فأنت بتنشئ Model جديد يرث Fields وMethods من Model آخر، وله تمثيل مستقل في قاعدة البيانات.

### _inherits

ده اسمه Delegation Inheritance في Odoo، وبيعتمد على ربط Models ببعض عن طريق Many2one.

مش Single Table Inheritance.

**الخلاصة:** مجرد استخدام _inherit أو _inherits في Odoo لا يكفي لتصنيف التنفيذ على إنه Fowler's Single Table Inheritance. لازم نبص على استراتيجية التخزين الفعلية.

---

## 9. مميزات وعيوب Single Table Inheritance

**المميزات:**

- جدول واحد فقط.
- Queries أبسط في حالات التعامل مع الـ Hierarchy كلها.
- مفيش Joins بين جداول الـ Parent والـ Subclasses.
- إضافة Subclass جديدة لا تتطلب إنشاء جدول جديد.

**العيوب:**

- عدد كبير من الأعمدة التي قد تكون NULL.
- الـ Constraints ممكن تبقى معقدة؛ لأن كل نوع له قواعد مختلفة.
- الجدول ممكن يكبر جدًا مع زيادة أنواع الـ Subclasses.
- الـ Schema مرتبط بقوة بتصميم الـ Inheritance Hierarchy.

## الخلاصة

**Single Table Inheritance**

بنمثل الـ Parent Class وكل الـ Subclasses داخل جدول واحد.

- جدول واحد لكل الـ Hierarchy.
- Discriminator يحدد نوع كل Row.
- الـ ORM أو Mapper ينشئ الـ Concrete Class المناسبة.
- لا يوجد GoF Equivalent مباشر.
- مناسب لما يكون عدد الـ Subclasses والأعمدة الإضافية معقولًا.

النمط التالي في نفس المجموعة هو:

**Class Table Inheritance**

وده هيكون مهم جدًا؛ لأنه بيحل مشكلة الـ NULL الكثيرة الموجودة في Single Table Inheritance، لكن باستخدام استراتيجية تخزين مختلفة.


# 2. Query Object

نكمل في **Object-Relational Metadata Mapping Patterns**.

النمط ده مهم جدًا؛ لأنه هيساعدنا نفهم إزاي الـ ORM بيبني Queries بطريقة منظمة بدل ما نعتمد على SQL Strings مكتوبة يدويًا.

## 1. المشكلة (Problem)

تخيل إن عندك نظام E-commerce، وعايز تعمل Search على المنتجات.

مرة المستخدم يبحث بالاسم:

```sql
SELECT * FROM products
WHERE name = 'Laptop';
```

ومرة يبحث بالسعر:

```sql
SELECT * FROM products
WHERE price > 1000;
```

ومرة يجمع أكتر من شرط:

```sql
SELECT * FROM products
WHERE category_id = 5
AND price > 1000
AND active = TRUE;
```

المشكلة إن التطبيق ممكن يحتوي على عشرات أو مئات شروط البحث المختلفة.

لو فضلنا نكتب SQL Strings لكل حالة، هنواجه مشاكل:

- تكرار SQL Logic.
- صعوبة تركيب شروط البحث بشكل ديناميكي.
- صعوبة إعادة استخدام شروط البحث.
- صعوبة اختبار الاستعلامات.
- زيادة احتمالية SQL Injection لو بنركب Strings بطريقة غير آمنة.

طيب هل ممكن نمثل الاستعلام نفسه كـ Object؟

هنا بييجي دور **Query Object**.

## 2. الفكرة والحل (Solution)

بدل ما نمثل الاستعلام كنص SQL، بنمثله في شكل Object يحتوي على الشروط والعمليات المطلوبة.

مثلًا بدل:

```sql
SELECT * FROM products
WHERE price > 1000
AND active = TRUE;
```

نعبر عنه باستخدام Objects:

```python
query = Query(Product)

query.where("price", ">", 1000)
query.where("active", "=", True)
```

وبعد كده الـ Query Object أو الـ Query Engine يحوّل الوصف ده إلى SQL وينفذه.

**تدفق العمل**

**Application Code**

يحدد شروط البحث

**Query Object**

يمثل شروط الاستعلام كـ Objects

**SQL Generator / Query Engine**

**Database**

الفكرة الأساسية: الاستعلام بقى Data Structure نقدر نبنيها ونعدلها ونركب أجزاء منها.

## 3. مثال عملي باستخدام Python

هنبني مثال تعليمي صغير.

أولًا نحتاج Object يمثل شرطًا واحدًا:

```python
class Condition:

    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value
```

بعد كده Query Object:

```python
class Query:

    def __init__(self, table):
        self.table = table
        self.conditions = []

    def where(self, field, operator, value):
        self.conditions.append(
            Condition(field, operator, value)
        )

        return self

    def to_sql(self):
        sql = f"SELECT * FROM {self.table}"

        if self.conditions:
            sql += " WHERE "

            parts = []

            for condition in self.conditions:
                parts.append(
                    f"{condition.field} "
                    f"{condition.operator} %s"
                )

            sql += " AND ".join(parts)

        return sql

    def get_params(self):
        return [
            condition.value
            for condition in self.conditions
        ]
```

نجرب:

```python
query = Query("products")

query.where("price", ">", 1000)
query.where("active", "=", True)

print(query.to_sql())
print(query.get_params())
```

الناتج:

```sql
SELECT * FROM products
WHERE price > %s AND active = %s
```

والـ Parameters:

```python
[1000, True]
```

لاحظ إننا فصلنا بين:

- وصف الاستعلام.
- تحويل الاستعلام إلى SQL.
- القيم المستخدمة في الاستعلام.

وده بيساعدنا نتجنب إدخال قيم المستخدم مباشرة داخل SQL String.

**تنبيه أمني:** المثال للتوضيح فقط؛ أسماء الجداول والأعمدة والـ Operators لازم يتم التحقق منها باستخدام Allowlist، لأن Parameters في SQL بتحمي قيم البيانات، لكنها لا تحمي أسماء الأعمدة والجداول.

## 4. مثال أكثر واقعية: تركيب الشروط

ممكن نحتاج نعمل شروط مركبة:

```sql
WHERE price > 1000
AND (
    category_id = 5
    OR category_id = 7
)
```

هنا ممكن نستخدم Composite Structure لتمثيل الشروط:

```plain text
              AND
             /   \
         price>1000 OR
                    / \
             category=5 category=7
```

بالتالي الـ Query Object ممكن يمثل:

- شروط فردية.
- AND / OR.
- Nested Conditions.
- Sorting.
- Pagination.
- Joins.

وده بيخلّي الاستعلام قابلًا للتركيب بدل ما يكون String ثابت.

## 5. أقرب GoF Pattern

هنا عندنا تشابه مهم مع نمطين:

### Composite

كل Condition ممكن تكون Leaf، ومجموعة Conditions ممكن تكون Composite تحتوي شروطًا أخرى.

مثال:

```plain text
           AND
          /   \
       Price   OR
              / \
          Category Active
```

الـ Composite بيسمح لنا نتعامل مع الشرط البسيط والشرط المركب من خلال Interface موحد.

### Interpreter

لو عندنا Query Expression Tree، ممكن نفسر الـ Tree ونحوّله إلى SQL.

لكن لازم نفرّق:

- **Query Object:** هدفه تمثيل الاستعلام كـ Object.
- **Composite:** تنظيم العناصر في بنية شجرية.
- **Interpreter:** تفسير تعبيرات وفق Grammar.

إذًا Composite وInterpreter ممكن يساعدوا في تنفيذ Query Object، لكن مش بدائل عنه.

## 6. علاقته بـ Application Architecture

Query Object مش Application Architecture Pattern؛ هو نمط متعلق بتمثيل الاستعلامات.

ممكن يظهر داخل Infrastructure Layer أو Data Access Layer.

مثلًا في Clean Architecture:

```plain text
Application Use Case
        |
        | Search Products
        ↓
Repository Interface
        |
        ↓
Infrastructure Repository
        |
        ↓
Query Object
        |
        ↓
Database
```

لاحظ إن الـ Query Object مش لازم يكون مكشوفًا للـ Domain أو Application.

ممكن يكون تفصيل داخلي في Infrastructure.

لكن في بعض الأنظمة ممكن Application Layer تستخدم Query Objects كجزء من Query API، حسب التصميم.

## 7. علاقته بـ DDD

في DDD، ممكن تستخدم Query Object لتنفيذ عمليات البحث عن Aggregates أو Read Models.

لكن فيه نقطة مهمة:

**Query Object مش هو Specification Pattern.**

الفرق:

- Query Object بيمثل الاستعلام المطلوب تنفيذه، وقد يتضمن شروطًا وترتيبًا وPagination.
- Specification بتمثل قاعدة أو معيارًا يمكن تقييمه أو تركيبه وإعادة استخدامه.

ممكن Specification تتحول إلى Query Object أو SQL Predicate.

لكن مش كل Query Object هي Specification.

## 8. علاقته بـ Odoo

هنا عندنا مثال قريب جدًا في الاستخدام.

في Odoo:

```python
products = self.env["product.product"].search([
    ("list_price", ">", 1000),
    ("active", "=", True),
])
```

الـ Domain List بيصف شروط البحث.

وبعدين Odoo ORM بيحوّل الوصف ده إلى استعلام مناسب لقاعدة البيانات.

وممكن نستخدم Operators زي:

```python
[
    "|",
    ("categ_id", "=", 5),
    ("categ_id", "=", 7),
]
```

لكن لازم نكون دقيقين:

- Odoo Domain هو Declarative Query Expression.
- Query Object في Fowler هو نمط لتمثيل الاستعلام في صورة Object.
- فيه تشابه مفاهيمي قوي بينهما، لكن مش بالضرورة تطابق حرفي في التنفيذ أو التصميم الداخلي.

---

## 9. إمتى نستخدم Query Object؟

استخدمه لما:

- عندك شروط بحث ديناميكية كثيرة.
- محتاج تركب شروط AND وOR.
- محتاج تعيد استخدام أجزاء من الاستعلام.
- عايز تفصل Query Definition عن SQL Generation.
- عندك Query Engine أو ORM محتاج تمثيل موحد للاستعلامات.

## الخلاصة

**Query Object**

بيمثل الاستعلام كـ Object بدل SQL String، وبيسمح ببناء الشروط وتركيبها وتعديلها، وبعد كده تحويلها إلى SQL.

- GoF الأقرب: Composite وInterpreter كأدوات تنفيذ، وليس بدائل مباشرة.
- ممكن يكون داخل Infrastructure Layer.
- مختلف عن Specification Pattern.
- Odoo Domains مثال قريب من الفكرة.

**النمط التالي في المجموعة: Repository.**

وده من أهم الأنماط في PoEAA، وهنحتاج نفهم علاقته بـ Data Mapper وDAO وService Layer وDDD؛ لأن فيه خلط شائع جدًا بين المفاهيم دي.


# 3. Repository

وصلنا لواحد من أهم الأنماط في كتاب **Patterns of Enterprise Application Architecture (PoEAA)**، وواحد من أكثر الأنماط اللي بيحصل فيها خلط مع أنماط تانية، خصوصًا:

- Data Mapper
- DAO
- Table Data Gateway
- Service Layer
- Repository في DDD

خلينا نفهمه من الأساس.

## 1. المشكلة (Problem)

تخيل إن عندنا Domain Model فيه Customer، والتطبيق محتاج ينفذ عمليات زي:

- إضافة Customer.
- البحث عن Customer باستخدام ID.
- البحث عن Customers حسب شروط معينة.
- حذف Customer.

ممكن نكتب SQL مباشرة داخل الـ Domain أو Application Logic:

```python
class OrderService:

    def create_order(self, customer_id):
        # SQL query directly here
        ...
```

لكن كده بدأنا نخلط بين حاجتين مختلفتين:

1. الـ Business Logic: إيه اللي التطبيق محتاج يعمله؟
1. الـ Data Access: إزاي نوصل للبيانات ونجيبها؟

ومع زيادة حجم التطبيق، هتلاقي تفاصيل الـ SQL والـ ORM والـ Mapping منتشرة في أماكن كتير.

**السؤال: هل ممكن نوفر للـ Domain طريقة يتعامل بيها مع البيانات كأنها Collection من Objects، من غير ما يعرف تفاصيل تخزينها؟**

هنا بييجي دور Repository.

## 2. الفكرة والحل (Solution)

تعريف Fowler للـ Repository قائم على إنه يعمل وسيط بين Domain Model وData Mapping Layers، ويقدم واجهة تشبه Collection من Domain Objects.

يعني بدل ما الـ Domain يتعامل مع SQL أو Database Tables، يتعامل مع Object مسؤول عن توفير الـ Domain Objects وتخزينها.

تخيل إن عندك Collection في الذاكرة:

```python
customers = [
    Customer(1, "Ahmed"),
    Customer(2, "Saleh"),
]
```

بدل ما التطبيق يحتاج يعرف البيانات دي جاية منين، يتعامل مع Repository بواجهة قريبة من التعامل مع Collection:

```python
customer = customer_repository.get_by_id(1)

customer_repository.add(customer)
```

الـ Repository هو اللي يتولى تفاصيل الوصول للبيانات.

**الفكرة الأساسية**

**Domain / Application**

يتعامل مع Domain Objects

**Repository**

واجهة تشبه Collection

**Data Mapper / Data Access**

يتعامل مع تفاصيل التخزين

**Database**

الفكرة المهمة هنا:

الـ Repository مش مجرد مكان بنكتب فيه SQL، لكنه بيقدم للـ Domain طريقة للتعامل مع مجموعة من Domain Objects.

## 3. مثال عملي باستخدام Python

هنبني مثال بسيط يوضح الفكرة.

### أولًا: Domain Model

```python
class Customer:

    def __init__(self, customer_id, name):
        self.id = customer_id
        self.name = name

    def change_name(self, new_name):
        if not new_name:
            raise ValueError("Name is required")

        self.name = new_name
```

لاحظ إن الـ Customer مش عارف أي حاجة عن Database.

### ثانيًا: Repository Interface

```python
from abc import ABC, abstractmethod

class CustomerRepository(ABC):

    @abstractmethod
    def get_by_id(self, customer_id):
        pass

    @abstractmethod
    def add(self, customer):
        pass

    @abstractmethod
    def remove(self, customer):
        pass
```

ده العقد اللي الـ Application هيتعامل معاه.

### ثالثًا: Infrastructure Implementation

هنعمل Implementation باستخدام In-Memory Storage للتبسيط:

```python
class InMemoryCustomerRepository(CustomerRepository):

    def __init__(self):
        self.customers = {}

    def get_by_id(self, customer_id):
        return self.customers.get(customer_id)

    def add(self, customer):
        self.customers[customer.id] = customer

    def remove(self, customer):
        self.customers.pop(customer.id, None)
```

ممكن بعد كده نعمل Implementation تاني باستخدام PostgreSQL:

```python
class PostgresCustomerRepository(CustomerRepository):

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, customer_id):
        # Execute SQL and map the result
        ...

    def add(self, customer):
        # Persist customer using SQL
        ...

    def remove(self, customer):
        # Delete customer using SQL
        ...
```

### رابعًا: Application Service

```python
class CustomerService:

    def __init__(self, customer_repository):
        self.customer_repository = customer_repository

    def rename_customer(self, customer_id, new_name):
        customer = self.customer_repository.get_by_id(
            customer_id
        )

        if customer is None:
            raise ValueError("Customer not found")

        customer.change_name(new_name)
```

التطبيق مش محتاج يعرف هل البيانات جاية من PostgreSQL أو In-Memory Storage.

نجرب:

```python
repository = InMemoryCustomerRepository()

customer = Customer(1, "Ahmed")
repository.add(customer)

service = CustomerService(repository)

service.rename_customer(1, "Saleh")

print(customer.name)
```

الناتج:

```plain text
Saleh
```

**خد بالك من نقطة مهمة:** المثال استخدم In-Memory Repository لتوضيح الواجهة. في تنفيذ PostgreSQL حقيقي، محتاجين كمان نحدد استراتيجية حفظ التغييرات والـ Transactions، سواء عن طريق save() أو Unit of Work أو آلية أخرى.

## 4. أقرب GoF Pattern

هل Repository له GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern بيطابقه بشكل مباشر.**

لكن فيه تشابهات جزئية:

### Facade

الـ Facade بيقدم واجهة مبسطة للتعامل مع Subsystem معقد.

والـ Repository بيقدم واجهة مبسطة للتعامل مع Data Mapping وData Access.

لكن الفرق في الـ Intent:

- Facade بيبسط التعامل مع Subsystem.
- Repository بيقدم واجهة تشبه Collection للتعامل مع Domain Objects، ويعزل Domain Model عن تفاصيل Data Mapping.

### Collection

فيه تشابه أقوى مع مفهوم Collection؛ لأن Repository بيخلي التعامل مع البيانات قريب من التعامل مع مجموعة Objects في الذاكرة.

لكن Collection نفسها مش GoF Design Pattern.

إذًا مفيش GoF Equivalent مباشر.

## 5. أهم مقارنة: Repository vs Data Mapper

دي لازم نفهمها كويس.

**Data Mapper** مسؤول عن تحويل البيانات بين Domain Objects وDatabase Records.

أما **Repository** فمسؤول عن توفير واجهة للتعامل مع مجموعة Domain Objects.

خلينا نشوف العلاقة:

```plain text
Domain Objects  <---  Repository  <---  Data Mapper  <---  Database
```

مثال:

لما أطلب:

```python
customer = repository.get_by_id(10)
```

الـ Repository ممكن يستعين بـ Data Mapper عشان:

1. يطلب البيانات من Database.
1. يحول الـ Row إلى Customer Object.
1. يرجع الـ Customer للتطبيق.

إذًا:

- Repository يحدد إزاي التطبيق يتعامل مع مجموعة الـ Objects.
- Data Mapper يحدد إزاي الـ Objects تتحول إلى Database Records والعكس.

**ممكن Repository يستخدم Data Mapper داخليًا، لكن مش لازم كل Repository يكون مبني على Data Mapper.**

## 6. Repository vs DAO vs Gateway

خلينا نفصل التلاتة لأنهم بيتخلطوا كتير.

**Repository**

بيتعامل مع Domain Objects ومجموعاتها.

```python
customer = customer_repository.get_by_id(10)
```

---

**DAO — Data Access Object**

بيقدم واجهة للوصول للبيانات، وغالبًا بيكون أقرب لتفاصيل الـ Data Source.

```python
row = customer_dao.fetch_by_id(10)
```

---

**Table Data Gateway**

Object مسؤول عن عمليات الوصول لجدول معين.

```python
rows = customer_gateway.find_by_email(email)
```

الفرق مش مجرد أسماء، لكن مستوى التجريد والـ Objects اللي كل واحد بيتعامل معاها.

ومهم تعرف إن DAO مصطلح مستخدم على نطاق واسع، وله تطبيقات مختلفة؛ مش كل DAO لازم يكون Table Data Gateway، ومش كل Repository مجرد DAO باسم مختلف.

## 7. علاقته بـ Application Architecture

Repository مش Application Architecture Pattern، لكنه ممكن يكون Component مهم داخل Application Architecture.

في Clean Architecture مثلًا:

```plain text
       Application Layer
               |
               ↓
       Repository Interface
               ↑
               |
      Infrastructure Layer
               |
               ↓
            Database
```

خلينا نلاحظ اتجاه الـ Dependency:

- Application تعتمد على Repository Interface.
- Infrastructure تنفذ الـ Interface.
- Infrastructure هي اللي تتعامل مع Database.

وده تطبيق عملي لمبدأ Dependency Inversion.

لكن انتبه:

**Repository Pattern مش هو Dependency Inversion Principle.**

الـ DIP مبدأ تصميم، والـ Repository واحد من الأساليب اللي ممكن تساعدنا نطبقه.

## 8. علاقته بـ DDD

هنا Repository له أهمية خاصة جدًا.

في DDD، غالبًا بنعمل Repository لكل Aggregate Root محتاجين نرجعه ونحفظه.

مثلًا:

```plain text
Order Aggregate
    |
    |-- Order
    |-- OrderLine
    |-- OrderAddress
```

بدل ما نعمل Repository لكل Entity داخل الـ Aggregate، غالبًا بنتعامل مع الـ Aggregate من خلال Repository الخاص بالـ Root:

```python
order = order_repository.get_by_id(order_id)

order.add_line(product, quantity)

order_repository.save(order)
```

ليه؟

لأن الـ Aggregate Root هو نقطة الدخول للتحكم في الـ Aggregate والحفاظ على قواعد الـ Consistency الخاصة به.

مش معنى كده إن كل Class لازم يكون لها Repository.

ومش معنى إن عندك Database Table يبقى لازم تعمل Repository ليها.

## 9. علاقته بـ Odoo

في Odoo، لما تكتب:

```python
customers = self.env["res.partner"].search([
    ("customer_rank", ">", 0)
])
```

أنت بتتعامل مع ORM Model وRecordsets.

هل ده Repository؟

فيه تشابه في فكرة توفير واجهة للوصول لمجموعة Records، لكن self.env["res.partner"] ليس تلقائيًا Fowler Repository بالمعنى الدقيق.

السبب إن Odoo Model وORM مسؤولان عن مجموعة واسعة من الوظائف، منها:

- تعريف الـ Fields.
- التعامل مع الـ Recordsets.
- البحث والقراءة والكتابة.
- إدارة العلاقات.
- تطبيق الـ Access Rights والـ Record Rules.
- عمليات الـ ORM الأخرى.

في تطبيق Odoo مخصص، ممكن تعمل Repository abstraction فوق ORM لو عندك سبب معماري واضح، لكن مش لازم تضيف Repository لكل Model لمجرد اتباع DDD أو Clean Architecture.

---

## 10. إمتى نستخدم Repository؟

استخدمه لما:

- عايز تعزل الـ Domain عن تفاصيل Data Access.
- عايز تتعامل مع Domain Objects كأنها Collection.
- عندك Domain Model محتاج استقلال عن Persistence.
- عايز توفر Implementations مختلفة لمصدر البيانات.
- بتستخدم DDD وعايز Repository عند حدود الـ Aggregate Roots.

لكن تجنبه لو هيكون مجرد طبقة إضافية بتكرر نفس واجهات ORM من غير قيمة حقيقية.

## الخلاصة النهائية للمجموعة

**Object-Relational Metadata Mapping Patterns**

1. **Metadata Mapping:** وصف العلاقة بين Objects وDatabase في Metadata.
1. **Query Object:** تمثيل الاستعلام في صورة Object.
1. **Repository:** توفير واجهة تشبه Collection للتعامل مع Domain Objects.

التلاتة بيتعاملوا مع تنظيم عملية الـ Persistence، لكن كل واحد بيحل مشكلة مختلفة.

وبكده نكون خلصنا مجموعة **Object-Relational Metadata Mapping Patterns**.

الخطوة المنطقية التالية في فهرس PoEAA هي **Web Presentation Patterns**، ودي مجموعة مختلفة؛ هنبدأ فيها من مشكلة التعامل مع HTTP Requests وResponses وعرض البيانات للمستخدم.


هنكمل في دول بنفس الاسلوب بس من اليمين للشمال

## Web Presentation Patterns


تمام يا صاحبي 😂 نبدأ مجموعة **Web Presentation Patterns**، وهنحافظ على نفس أسلوبنا، مع ترتيب الرسومات وتدفق العمليات من اليمين للشمال فعلًا.

# Web Presentation Patterns

قبل ما نبدأ بالأنماط، محتاجين نفهم المجموعة دي بتعالج إيه.

في تطبيقات الويب، عندنا مشكلة مختلفة عن اللي كنا بندرسه في Object-Relational Mapping.

هناك كنا بنسأل:

**إزاي نحول Objects إلى Database Records والعكس؟**

هنا السؤال:

**إزاي ننظم استقبال HTTP Requests، وتنفيذ العمليات المطلوبة، وتجهيز البيانات، وعرضها للمستخدم؟**

تخيل المستخدم فتح صفحة لعرض تفاصيل Order.

التطبيق محتاج:

1. يستقبل HTTP Request.
1. يحدد الصفحة أو العملية المطلوبة.
1. يستدعي الـ Application أو Domain Logic.
1. يجهز البيانات المطلوبة للعرض.
1. يرجع HTTP Response مناسب.

لو كل ده موجود داخل Controller واحد ضخم، هيبقى صعب نختبره ونطوره ونعيد استخدامه.

وهنا بيظهر دور Web Presentation Patterns.

## خريطة المجموعة

هنمشي حسب تصنيف Fowler:

## Web Presentation Patterns

1. **Model View Controller (MVC)**
  فصل Model عن View وController.
1. **Page Controller**
  Controller مسؤول عن صفحة ويب معينة أو Action داخل صفحة.
1. **Front Controller**
  مدخل مركزي يستقبل طلبات الويب ويوجهها للمعالجة المناسبة.
1. **Template View**
  استخدام Template لعرض البيانات داخل HTML.
1. **Transform View**
  تحويل بيانات المجال إلى شكل العرض داخل View مستقلة.
1. **Two Step View**
  فصل العرض الخاص بالتطبيق عن التنسيق النهائي العام.
1. **Application Controller**
  تنظيم التنقل بين الشاشات وتحديد الـ Views والـ Actions المناسبة حسب سير العمل.

ملحوظة: هنفرق أثناء الشرح بين الأنماط اللي بتنظم استقبال الطلبات والـ Controllers، والأنماط اللي بتنظم عرض البيانات.

---

# 1. Model View Controller (MVC)

## 1. المشكلة (Problem)

تخيل إنك بتبني Web Application لإدارة المبيعات.

عندك صفحة بتعرض Orders، والمستخدم يقدر:

- يعرض الطلبات.
- يفتح تفاصيل Order.
- يلغي Order.
- يعدل بياناته.

ممكن في البداية تكتب كل حاجة في مكان واحد:

```python
def orders_page(request):
    # Read HTTP Request

    # Validate input

    # Execute business logic

    # Query database

    # Generate HTML

    # Return HTTP Response
    ...
```

المشكلة إن الوظيفة الواحدة بقت مسؤولة عن حاجات مختلفة تمامًا:

- التعامل مع HTTP.
- تنفيذ Business Logic.
- الوصول إلى البيانات.
- عرض HTML.

وده بيعمل Tight Coupling بين أجزاء التطبيق.

مثلًا لو عايز تغير طريقة عرض الصفحة، ممكن تضطر تعدل كود التعامل مع الطلبات أو حتى Business Logic.

**السؤال: إزاي نفصل المسؤوليات دي عن بعضها؟**

## 2. الفكرة والحل (Solution)

فكرة MVC هي تقسيم Presentation Layer إلى ثلاثة أجزاء:

### Model

مسؤول عن بيانات التطبيق وسلوكه المرتبط بها.

في سياق Fowler، الـ Model يمثل Domain State وسلوك المجال، مش مجرد Database Model.

### View

مسؤولة عن عرض البيانات للمستخدم.

مثلًا HTML Page أو شاشة تعرض Order.

### Controller

مسؤول عن استقبال User Input، وتفسيره، والتنسيق مع Model والـ View.

**MVC — اتجاه تدفق العملية من اليمين للشمال**

**User**

HTTP Request / User Interaction

**Controller**

يستقبل الطلب وينسق العملية

**Model**

البيانات وسلوك المجال

**View**

تجهيز وعرض البيانات

**User**

HTML Response

الرسم السابق يوضح مسارًا مبسطًا، مش معناه إن كل تطبيق MVC لازم ينفذ التفاعل بنفس الترتيب الحرفي؛ بعض تطبيقات MVC فيها تفاعل مباشر بين Model وView أو آليات تحديث مختلفة.

## 3. مثال عملي باستخدام Python

خلينا نعمل مثال بسيط من غير Framework.

### Model

```python
class Order:
    def __init__(self, order_id, total):
        self.id = order_id
        self.total = total

    def is_expensive(self):
        return self.total > 1000
```

### View

```python
def render_order(order):
    return f"""
    <html>
        <body>
            <h1>Order #{order.id}</h1>
            <p>Total: {order.total}</p>
        </body>
    </html>
    """
```

### Controller

```python
class OrderController:

    def __init__(self, repository):
        self.repository = repository

    def show(self, order_id):
        order = self.repository.get_by_id(order_id)

        if order is None:
            return "404 Not Found"

        return render_order(order)
```

لاحظ توزيع المسؤوليات:

- Order: يمثل الـ Model.
- render_order: يمثل الـ View.
- OrderController: يتعامل مع الطلب وينسق بين الأجزاء.

## 4. أقرب GoF Pattern

هل MVC موجود ضمن GoF؟

**لا، MVC ليس واحدًا من أنماط GoF الـ 23.**

لكن توجد علاقات وتشابهات مع بعض الأنماط:

### Observer

في بعض تطبيقات MVC، الـ View تراقب تغييرات الـ Model، ولما يحصل تغيير يتم تحديث العرض.

هنا فيه علاقة مباشرة بفكرة Observer.

لكن Observer لا يساوي MVC؛ هو آلية ممكن تستخدم داخل MVC.

### Strategy

ممكن نفصل طريقة عرض البيانات أو بعض سلوكيات الـ Controller باستخدام Strategies.

لكن ده أيضًا مش معناه إن MVC هو Strategy.

**الخلاصة:** MVC نمط معماري لتنظيم Presentation، بينما Observer وStrategy أنماط تصميم ممكن تساعد في تنفيذه.

## 5. علاقته بـ Application Architecture

دي نقطة مهمة جدًا.

MVC مش بديل عن Layered Architecture أو Clean Architecture.

لأن كل واحد بيتعامل مع مستوى مختلف من التنظيم.

مثلًا:

**Layered Architecture:**

- Presentation Layer
- Business Layer
- Data Access Layer

أما MVC فهو بينظم مكونات الـ Presentation بشكل أساسي.

يعني ممكن يكون عندك:

```plain text
                 Web Application
                        |
                        ↓
               Presentation Layer
                        |
              -------------------
              |        |        |
           Model    View   Controller
```

لكن الـ Model هنا ممكن يعتمد على Business Layer أو يتعامل معها، حسب تصميم التطبيق.

## 6. علاقته بـ Clean Architecture وDDD

### Clean Architecture

ممكن تستخدم MVC في الـ Presentation Layer، وتخلي الـ Controller يستدعي Application Use Cases.

مثلًا:

```plain text
HTTP Request
      |
      ↓
Controller
      |
      ↓
Application Use Case
      |
      ↓
Domain Model
      |
      ↓
Response Model
      |
      ↓
View
```

واتجاه الرسم من اليمين للشمال:

```plain text
View  <---  Response Model  <---  Use Case  <---  Controller  <---  HTTP Request
```

المهم إن الـ Domain لا يعتمد على MVC أو HTML أو HTTP.

### DDD

في DDD:

- الـ Model ممكن يحتوي Domain Entities وValue Objects.
- الـ Controller يستقبل الطلبات.
- Application Services أو Use Cases تنسق تنفيذ العمليات.
- الـ View تعرض البيانات.

لكن متخلطش بين **MVC Model** و**DDD Domain Model** باعتبارهم دائمًا نفس الشيء؛ Model في MVC مفهوم أوسع، وتفاصيله تختلف حسب التطبيق.

## 7. علاقته بـ Odoo

في Odoo عندنا أجزاء تشبه MVC:

- Python Models: البيانات والسلوك.
- XML Views: واجهات العرض.
- Controllers: استقبال HTTP Routes.

مثال Controller:

```python
from odoo import http
from odoo.http import request

class OrderController(http.Controller):

    @http.route("/orders", type="http", auth="user")
    def orders(self):
        orders = request.env["sale.order"].search([])

        return request.render(
            "my_module.orders_template",
            {"orders": orders}
        )
```

لكن لازم نفهم إن Odoo مش مجرد MVC تقليدي:

- الـ ORM مسؤول عن إدارة الـ Models والـ Persistence.
- الـ Framework يتحكم في Routing وSecurity وRequest Lifecycle.
- الـ XML Views ليها آلية خاصة بالـ Odoo.
- في الواجهة الحديثة، OWL يقدم Component-based UI.

فالأدق نقول إن Odoo فيه MVC-like organization، مع Framework Architecture خاصة به.

---

## 8. إمتى نستخدم MVC؟

نستخدمه لما نحتاج:

- نفصل استقبال الطلبات عن عرض البيانات.
- نفصل منطق المجال عن تفاصيل الـ UI.
- ننظم Presentation Components.
- نسهل اختبار كل مسؤولية بشكل مستقل.

## الخلاصة

**Model View Controller**

- Model: بيانات التطبيق وسلوكه.
- View: عرض البيانات.
- Controller: استقبال Input والتنسيق بين الأجزاء.
- ليس GoF Pattern.
- يمكن استخدامه داخل Presentation Layer في Layered أو Clean Architecture.
- Observer قد يساعد في تنفيذ بعض أشكال MVC، لكنه ليس بديلًا عنه.

**النمط التالي: Page Controller.**

وده هيخلينا نفهم سؤال مهم: هل محتاج Controller مركزي لكل التطبيق، ولا ممكن كل صفحة يكون ليها Controller مستقل مسؤول عنها؟
