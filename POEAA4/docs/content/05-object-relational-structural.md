# أنماط هيكلية للكائنات والعلاقات (Object-Relational Structural Patterns)





# Identity Field

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## علاقته بأودو

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

## الخلاصة
Identity Field بيحل مشكلة:

> How can an object identify its corresponding database row?

---

## النمط التالي

**2. Foreign Key Mapping**

وده هيكون مهم جدًا؛ لأننا بعد ما عرفنا إزاي نربط Object بسجل في قاعدة البيانات، هنشوف إزاي نمثل العلاقات بين الـ Objects باستخدام Foreign Keys.

نكمل يا صاحبي. وصلنا للنمط الثاني في مجموعة **Object-Relational Structural Patterns** من كتاب Fowler.


# Foreign Key Mapping

## المشكلة

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

## الفكرة والحل

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

## علاقته بأودو

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


# Association Table Mapping

## المشكلة

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

## الفكرة والحل

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

## علاقته بأودو

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

## الخلاصة
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


# Dependent Mapping

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## علاقته بأودو

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


# Embedded Value

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## علاقته بالعمارة

Embedded Value مش Application Architecture Pattern.

هو Persistence Mapping Pattern.

في Clean Architecture:

- الـ Domain يحتوي Address أو Money كـ Objects.
- الـ Infrastructure مسؤولة عن تحويلهم إلى أعمدة.
- الـ Domain مش محتاج يعرف إن address_city عمود في جدول customers.

وده تطبيق واضح لفصل الـ Domain Model عن تفاصيل التخزين.

---

## علاقته بأودو

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


# Serialized LOB

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## علاقته بأودو

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


# Single Table Inheritance

خلينا نكمل في **Object-Relational Structural Patterns** بنفس طريقتنا.

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## أقرب GoF Pattern

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

## علاقته بالعمارة

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

## علاقته بأودو

هنا محتاجين نكون دقيقين؛ لأن Odoo عنده أكتر من استراتيجية للـ Model Inheritance.

### _inherit

لما تستخدم _inherit بدون _name، فأنت غالبًا بتوسع Model موجود بالفعل، وتضيف له Fields أو Methods.

ده مش معناه تلقائيًا إنك بتطبق Single Table Inheritance.

### _name مع _inherit

لما تنشئ Model جديد باستخدام _name و`_inherit`، فأنت بتنشئ Model جديد يرث Fields وMethods من Model آخر، وله تمثيل مستقل في قاعدة البيانات.

### _inherits

ده اسمه Delegation Inheritance في Odoo، وبيعتمد على ربط Models ببعض عن طريق Many2one.

مش Single Table Inheritance.

## الخلاصة

مجرد استخدام _inherit أو _inherits في Odoo لا يكفي لتصنيف التنفيذ على إنه Fowler's Single Table Inheritance. لازم نبص على استراتيجية التخزين الفعلية.

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


# Class Table Inheritance

## المشكلة

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


# Concrete Table Inheritance

## المشكلة

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


# Inheritance Mappers

## المشكلة

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
