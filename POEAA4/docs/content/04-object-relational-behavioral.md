# أنماط سلوكية للكائنات والعلاقات (Object-Relational Behavioral Patterns)





# Unit of Work

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## علاقته بأودو

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


# Identity Map

نكمل في مجموعة **Object-Relational Behavioral Patterns** من كتاب Fowler.

النمط ده مرتبط جدًا بالـ ORM، وخصوصًا لما يكون عندك Objects كتير بتتعامل مع نفس البيانات أثناء تنفيذ عملية واحدة.

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## علاقته بأودو

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


# Lazy Load

## المشكلة

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

## الفكرة والحل

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

## علاقته بأودو

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
