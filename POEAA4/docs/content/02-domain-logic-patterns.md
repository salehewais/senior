# أنماط منطق المجال (Domain Logic Patterns)

## مراجعة مجموعة Domain Logic Patterns كاملة

Chapter 9 — Fowler

| Pattern | السؤال الأساسي الذي يجيب عنه |
| --- | --- |
| Transaction Script | كيف أنظم الـ Logic حول كل عملية؟ |
| Domain Model | كيف أمثل المجال وسلوكه في Objects؟ |
| Table Module | كيف أنظم الـ Logic حول جدول كامل؟ |
| Service Layer | كيف أحدد عمليات التطبيق وأنسق تنفيذها؟ |

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

| المقارنة | Service Layer | Separated Interface |
| --- | --- | --- |
| التصنيف | Domain Logic Pattern | Base Pattern |
| المشكلة | تنظيم Application Operations | فصل العقد عن التنفيذ |
| التركيز | Application Boundary | Dependency Structure |
| يحتاج Interface؟ | لا | نعم |
| ممكن تستخدمهم معًا؟ | نعم | نعم |

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

## الخلاصة
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



# Transaction Script

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## أقرب GoF Pattern

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

## علاقته بالعمارة

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

Fowler نفسه بيعتبره اختيارًا مناسبًا للأنظمة ذات الـ Domain Logic البسيطة نسبيًا. accc.org

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


# Domain Model

## المشكلة

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

## الفكرة والحل

تعريف Fowler:

**An object model of the domain that incorporates both behavior and data.**

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

## مثال

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

## أقرب GoF Pattern

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

## علاقته بالعمارة

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

Fowler بيؤكد إن Domain Model مناسب خصوصًا لما تكون قواعد العمل والعلاقات معقدة، وده أحد الأسباب اللي بتخلي DDD يهتم بيه.

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


# Table Module

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## أقرب GoF Pattern

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

## علاقته بالعمارة

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

## علاقته بأودو

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
1. الفكرة والحل.
1. مثال عملي باستخدام Python.
1. أقرب GoF Pattern، ووجه التشابه والاختلاف في الـ Intent.
1. علاقته بالـ Application Architecture.
1. علاقته بـ Clean Architecture وDDD لما يكون فيه ارتباط حقيقي.

وهنشرح كل Pattern لوحده، من غير ما نخلط بينه وبين الأنماط القريبة منه. والشرح بالعربي من اليمين للشمال، والأكواد في مقاطع مستقلة.


# Service Layer

## المشكلة

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

## الفكرة والحل

تعريف Fowler:

**A Service Layer defines an application's boundary and its set of available operations from the perspective of interfacing client layers.** oreilly.com

خلينا نفهم التعريف.

الـ Service Layer هي طبقة بتحدد:

- Application Boundary: حدود التطبيق والعمليات المتاحة منه.
- Application Operations: العمليات اللي الـ Clients يقدروا يطلبوها.
- Coordination: تنسيق تنفيذ العمليات المختلفة.
- Transaction Control: التحكم في حدود المعاملات عند الحاجة.

بمعنى أبسط:

بدل ما الـ Controller يعرف تفاصيل تنفيذ Checkout، هو بيطلب من Service Layer تنفيذ العملية.

والـ Service Layer هي اللي بتنسق التنفيذ.

## مثال

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

## أقرب GoF Pattern

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

## علاقته بالعمارة

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

## علاقته بأودو

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
