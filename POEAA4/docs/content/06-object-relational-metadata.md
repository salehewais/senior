# أنماط البيانات الوصفية للكائنات والعلاقات (Object-Relational Metadata Mapping Patterns)





# Metadata Mapping

## المشكلة

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


# Query Object

نكمل في **Object-Relational Metadata Mapping Patterns**.

النمط ده مهم جدًا؛ لأنه هيساعدنا نفهم إزاي الـ ORM بيبني Queries بطريقة منظمة بدل ما نعتمد على SQL Strings مكتوبة يدويًا.

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## مثال

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

## أقرب GoF Pattern

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

## علاقته بأودو

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


# Repository

وصلنا لواحد من أهم الأنماط في كتاب **Patterns of Enterprise Application Architecture (PoEAA)**، وواحد من أكثر الأنماط اللي بيحصل فيها خلط مع أنماط تانية، خصوصًا:

- Data Mapper
- DAO
- Table Data Gateway
- Service Layer
- Repository في DDD

خلينا نفهمه من الأساس.

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## أقرب GoF Pattern

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

## علاقته بأودو

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
