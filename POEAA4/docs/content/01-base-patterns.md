# الأنماط الأساسية (Base Patterns)

## مراجعة الأنماط العشرة

دلوقتي خلينا نجمع الأنماط اللي شرحناها في جدول واحد، عشان تقدر تراجع وظيفة كل Pattern وأقرب GoF للمقارنة.

| PoEAA Pattern | المشكلة الأساسية | أقرب GoF للمقارنة |
| --- | --- | --- |
| Gateway | الوصول لنظام خارجي | Facade / Adapter |
| Service Stub | استبدال Service حقيقية ببديل | Proxy |
| Mapper | تنظيم التواصل بين Objects مستقلة | Adapter / Mediator |
| Separated Interface | فصل العقد عن التنفيذ | Bridge |
| Registry | الوصول إلى Objects مسجلة | Singleton |
| Value Object | تمثيل قيمة بدون Identity | Flyweight |
| Money | تمثيل المبالغ والعملات | Strategy |
| Special Case | تمثيل حالة خاصة بسلوك محدد | Null Object |
| Plugin | توسيع النظام بإضافات | Strategy / Abstract Factory |
| Record Set | تمثيل بيانات جدولية في الذاكرة | Adapter (تشابه عملي فقط) |
| Layer Supertype | مشاركة سلوك داخل Layer | Template Method |

**ملاحظة مهمة:** الجدول ده بيعرض أقرب أنماط للمقارنة التعليمية، مش بيقول إن كل زوج متكافئ أو إن فيه علاقة اشتقاق مباشرة بينهم.

ومن وجهة نظري، أهم حاجة تخرج بيها من دراسة الأنماط العشرة مش حفظ أسماء GoF المقابلة؛ لكن القدرة على التمييز بين:

- Pattern بيعالج مشكلة في الوصول إلى الأنظمة الخارجية.
- Pattern بيعالج Dependency Direction.
- Pattern بيعالج Object Modeling.
- Pattern بيعالج Extensibility.
- Pattern بيعالج تنظيم السلوك المشترك.

وده هيساعدك تفهم إزاي الأنماط دي ممكن تتجمع مع بعض داخل Clean Architecture أو Layered Architecture من غير ما نخلط بين مسؤولياتها.



# Gateway

## المشكلة

تخيل إن عندك تطبيق E-Commerce، وعايز تتعامل مع خدمة دفع خارجية اسمها Payment Provider.

الخدمة دي بتوفر API، والتعامل معاها محتاج تفاصيل زي:

- HTTP Requests.
- Authentication.
- Headers.
- JSON Serialization.
- Error Handling.
- Response Parsing.

ممكن تكتب كل التفاصيل دي مباشرة داخل OrderService:

```python
class OrderService:

    def pay(self, order):
        # Authentication
        # Build HTTP request
        # Send request
        # Parse JSON response
        # Handle provider errors
        pass
```

المشكلة هنا إن OrderService بقى مسؤول عن حاجتين مختلفتين:

1. تنفيذ Business Logic الخاصة بالـ Order.
1. معرفة تفاصيل التعامل مع Payment Provider.

وده بيعمل Coupling بين الـ Business Logic والـ External System.

لو غيرت شركة الدفع، أو الـ API اتغير، هتضطر تعدل في كود التطبيق نفسه.

## الفكرة والحل

**Gateway هو Object بيعمل Encapsulation لطريقة الوصول إلى External System أو Resource.**

بمعنى أبسط:

بدل ما كل جزء في التطبيق يعرف يتعامل مع الخدمة الخارجية، بنعمل Object واحد مسؤول عن التعامل معاها.

**قبل استخدام Gateway**

Order Service

HTTP + Authentication + JSON + Business Logic

External Payment API

---

**بعد استخدام Gateway**

Order Service

Business Logic فقط

**Payment Gateway**

HTTP + Authentication + JSON + Error Handling

External Payment API

لاحظ إن الـ Gateway مش بالضرورة يكون API Gateway بالمعنى المستخدم في Microservices. هنا بنتكلم عن Design Pattern على مستوى الـ Objects.

## مثال

هنفصل التعامل مع مزود الدفع في كلاس مستقل:

```python
class PaymentGateway:

    def charge(self, amount, currency):
        # Authentication
        # Build HTTP request
        # Call external API
        # Parse response
        return {
            "success": True,
            "transaction_id": "TX-100"
        }

class OrderService:

    def __init__(self, payment_gateway):
        self.payment_gateway = payment_gateway

    def checkout(self, order):
        result = self.payment_gateway.charge(
            order.total,
            order.currency
        )

        if not result["success"]:
            raise Exception("Payment failed")

        order.mark_as_paid()
```

دلوقتي OrderService مش محتاج يعرف تفاصيل الـ HTTP أو الـ Authentication.

هو بيتعامل مع واجهة مفهومة بالنسبة له: charge().

---

## أقرب GoF Pattern

أقرب نمطين للمقارنة هما **Facade وAdapter**، لكن كل واحد فيهم له Intent مختلف.

**1. Facade**

(تشابه في تبسيط الوصول)

- Facade بيوفر واجهة موحدة ومبسطة للتعامل مع Subsystem معقد.
- Gateway بيوفر واجهة للتعامل مع External System أو Resource.
- الاتنين بيخفوا تفاصيل داخلية عن العميل.

**ليه Gateway مش بديل لـ Facade؟**

لأن Facade هدفه الأساسي تبسيط التعامل مع مجموعة من الكلاسات أو Subsystem، بينما Gateway هدفه تغليف نقطة الوصول إلى نظام أو مورد خارجي.

ممكن Gateway يستخدم Facade داخليًا، وممكن Facade يستخدم Gateway، حسب تصميم النظام.

---

**2. Adapter**

(تشابه في عزل اختلاف الواجهات)

- Adapter بيحوّل واجهة موجودة إلى واجهة متوقعة من العميل.
- Gateway بيغلف طريقة الوصول إلى نظام خارجي ويقدم واجهة مناسبة للتطبيق.

**ليه Gateway مش بديل لـ Adapter؟**

لأن Adapter عنده مشكلة محددة: عدم توافق واجهتين.

أما Gateway مش شرط يكون فيه أي عدم توافق أصلًا؛ ممكن يكون مجرد واجهة منظمة للتعامل مع API خارجية.

ممكن تعمل Gateway ويكون جواه Adapter لو محتاج تكيّف واجهة مزود الدفع مع الواجهة الداخلية.

### مقارنة سريعة

المقارنة	Gateway	Facade	Adapter
الهدف الأساسي	تغليف الوصول لنظام خارجي	تبسيط Subsystem	توافق واجهتين
يخفي تفاصيل	الاتصال بالنظام الخارجي	تعقيد Subsystem	اختلاف الواجهات
لازم يكون فيه External System؟	غالبًا نعم	لا	لا
هل ممكن يتداخلوا؟	نعم	نعم	نعم

## علاقته بالعمارة

Gateway ممكن يظهر في أكثر من Architecture:

- **Layered Architecture:** غالبًا داخل Infrastructure أو Data Access Layer.
- **Clean Architecture:** ممكن يكون Adapter في الطبقة الخارجية يتعامل مع External API.
- **Hexagonal Architecture:** ممكن يمثل Outbound Adapter يتواصل مع نظام خارجي من خلال Port.

لكن خد بالك: مش كل Gateway لازم يكون Repository، ومش كل Repository يعتبر Gateway. الـ Repository له مسؤولية مختلفة مرتبطة بإخفاء تفاصيل تخزين واسترجاع الـ Domain Objects.

---

## الخلاصة
Gateway بيحل مشكلة عزل التطبيق عن تفاصيل الوصول إلى نظام خارجي أو Resource.

أقرب GoF Patterns ليه:

- **Facade:** في تبسيط واجهة التعامل.
- **Adapter:** في إمكانية تقديم واجهة مناسبة للتطبيق.

لكنه مش بديل لأي واحد منهم؛ لأن المشكلة الأساسية اللي بيعالجها مختلفة.

---

## اختبر فهمك

**قبل ما ننتقل لـ Service Stub، عايز أتأكد إن فيه نقطة واضحة:**

هل الفرق بين Gateway وFacade وAdapter واضح عندك، خصوصًا إن التشابه في الشكل أو وجود Interface مش معناه إنهم نفس الـ Pattern؟


# Mapper

## المشكلة

تخيل عندك نظامين داخل نفس التطبيق، وكل نظام عنده طريقة مختلفة لتمثيل نفس المعلومة.

مثلًا، عندك نظام خاص بالعملاء، ونظام خاص بالفواتير.

نظام العملاء عنده الكائن بالشكل ده:

```python
class Customer:
    def __init__(self, customer_id, full_name, email):
        self.customer_id = customer_id
        self.full_name = full_name
        self.email = email
```

ونظام الفواتير عنده تمثيل مختلف:

```python
class InvoiceCustomer:
    def __init__(self, code, name, contact_email):
        self.code = code
        self.name = name
        self.contact_email = contact_email
```

الاتنين بيمثلوا العميل، لكن كل واحد عنده Structure مختلف.

السؤال: هل نخلي كل نظام يعرف تفاصيل النظام التاني؟

لو عملنا كده، هيحصل Coupling بين النظامين، وأي تغيير في تمثيل أحدهما ممكن يؤثر على الآخر.

هنا بيظهر دور Mapper.

## الفكرة والحل

**Mapper هو Object مسؤول عن إنشاء أو تنظيم التواصل بين Objects مستقلة عن بعضها.**

يعني بدل ما كل Object يعرف تفاصيل الـ Object الآخر، بنحط مسؤولية الربط أو التحويل في Object وسيط.

في المثال بتاعنا، الـ Mapper يعرف إزاي ينقل المعلومات من Customer إلى InvoiceCustomer.

**بدون Mapper**

Customer System

Invoice System

كل نظام محتاج يعرف تفاصيل النظام الآخر.

---

**باستخدام Mapper**

Customer

**Customer Mapper**

مسؤول عن الربط بين التمثيلين

InvoiceCustomer

## مثال

هنعمل Mapper مسؤول عن تحويل البيانات بين الكائنين:

```python
class CustomerMapper:

    @staticmethod
    def to_invoice_customer(customer):
        return InvoiceCustomer(
            code=customer.customer_id,
            name=customer.full_name,
            contact_email=customer.email
        )
```

دلوقتي نقدر نستخدمه بالشكل ده:

```python
customer = Customer(
    customer_id=10,
    full_name="Saleh Ewais",
    email="saleh@example.com"
)

invoice_customer = CustomerMapper.to_invoice_customer(customer)
```

النتيجة:

```python
InvoiceCustomer(
    code=10,
    name="Saleh Ewais",
    contact_email="saleh@example.com"
)
```

لاحظ إن:

- Customer مش محتاج يعرف أي حاجة عن InvoiceCustomer.
- InvoiceCustomer مش محتاج يعرف أي حاجة عن Customer.
- CustomerMapper هو المسؤول عن الربط بين الاتنين.

**لكن خلي بالك من نقطة مهمة:** تحويل البيانات من Object لآخر هو مثال شائع على استخدام Mapper، لكنه مش التعريف الكامل لنمط Fowler العام.

Mapper ممكن يكون مسؤولًا عن تنظيم التواصل بين كائنين مستقلين، والتحويل مجرد وسيلة ممكن يستخدمها لتحقيق ده.

## أقرب GoF Pattern

أقرب نمطين للمقارنة هنا هما Adapter و`Mediator`.

**1. Adapter**

(تشابه قوي)

الـ Adapter بيحوّل واجهة موجودة إلى واجهة تانية العميل متوقعها.

مثال:

عندك كلاس بيقدم:

```python
legacy.get_customer_data()
```

لكن التطبيق محتاج يتعامل مع:

```python
customer_repository.get()
```

ممكن تعمل Adapter يربط الواجهتين.

**أوجه التشابه مع Mapper:**

- الاتنين ممكن يعزلوا كائنين عن تفاصيل بعض.
- الاتنين ممكن يحولوا شكل البيانات أو طريقة التعامل.
- الاتنين ممكن يكونوا Objects وسيطة بين طرفين.

**ليه Mapper مش بديل لـ Adapter؟**

لأن Adapter مشكلته الأساسية عدم توافق واجهتين (Interface Incompatibility).

أما Mapper فاهتمامه الأساسي تنظيم التواصل بين Objects مستقلة.

ممكن Mapper يحوّل البيانات من Object لآخر من غير ما تكون فيه أي مشكلة في توافق الواجهات أصلًا.

---

**2. Mediator**

(تشابه في تنظيم التواصل)

الـ Mediator بيقلل الترابط المباشر بين مجموعة من Objects، عن طريق جعلها تتواصل من خلال Object وسيط.

**أوجه التشابه:**

- الاتنين ممكن يقللوا الاعتماد المباشر بين الكائنات.
- الاتنين بيستخدموا وسيطًا لتنظيم العلاقة بين الأطراف.

**ليه Mapper مش بديل لـ Mediator؟**

لأن Mediator هدفه تنظيم التفاعل والتواصل بين مجموعة من الكائنات.

أما Mapper فمش بالضرورة ينظم تفاعلات معقدة؛ ممكن تكون مسؤوليته مجرد إنشاء العلاقة أو نقل البيانات بين Objectين مستقلين.

### مقارنة سريعة

المقارنة	Mapper	Adapter	Mediator
المشكلة	تنظيم التواصل بين Objects مستقلة	عدم توافق الواجهات	تعقيد التواصل بين Objects
التركيز	الربط بين التمثيلات أو الكائنات	تحويل Interface	تنسيق التفاعل
عدد الأطراف	غالبًا طرفان	غالبًا طرفان	غالبًا عدة أطراف
الهدف	استقلال الأطراف	التوافق	تقليل الترابط

## خامسًا: نقطة مهمة جدًا — Mapper vs Data Mapper

هنا لازم نفرّق بين مصطلحين بيتستخدموا أحيانًا كأنهم نفس الحاجة.

**Mapper** هو الـ Base Pattern العام اللي بنتكلم عنه.

أما **Data Mapper** فهو Pattern متخصص في التعامل بين Objects وقاعدة البيانات.

مثلًا:

عندك Domain Object:

```python
class Product:
    def __init__(self, product_id, name, price):
        self.id = product_id
        self.name = name
        self.price = price
```

وعندك Database Table:

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);
```

الـ Data Mapper مسؤول عن نقل البيانات بين الـ Domain Objects والـ Database، مع الحفاظ على استقلال الـ Domain عن تفاصيل قاعدة البيانات.

**Domain Object**

Product

**Data Mapper**

Object ↔ Database Mapping

**Database**

Tables / Rows / Columns

وده مختلف عن Active Record:

- في Data Mapper، منطق الـ Domain والـ Persistence منفصلين.
- في Active Record، الـ Object نفسه بيحتوي على سلوك مرتبط بقراءة وكتابة بياناته.

وده موضوع مهم جدًا لما نيجي نناقش ORM وخصوصًا Odoo.

## علاقته بالعمارة

Mapper ممكن يظهر في أماكن مختلفة حسب مسؤوليته:

- **Clean Architecture:** ممكن تستخدمه لتحويل DTOs إلى Domain Objects أو العكس، أو لتحويل بيانات الأنظمة الخارجية.
- **Hexagonal Architecture:** ممكن يظهر داخل Adapter لتحويل البيانات بين Port والـ External System.
- **Layered Architecture:** ممكن يستخدم عند الحدود بين Presentation وApplication أو بين Application وPersistence.

لكن مش معنى كده إن كل تحويل بين Dictionary وObject لازم تعمل له Mapper Class مستقل. ده قرار تصميم يعتمد على تعقيد التحويل ومسؤولياته.

## الخلاصة
Mapper في PoEAA هو Object بينظم التواصل بين Objects مستقلة.

أقرب GoF Patterns ليه:

- **Adapter:** بسبب إمكانية تحويل الواجهات أو التمثيلات.
- **Mediator:** بسبب وجود وسيط يقلل الاعتماد المباشر بين الأطراف.

لكنه مش بديل عن أي واحد فيهم؛ لأن Intent مختلف.

ومتنساش الفرق بين Mapper العام وData Mapper المتخصص في الربط بين Objects وقاعدة البيانات.

---


# Layer Supertype

ده آخر Pattern في قائمتنا، وهنحتاج نفهمه كويس لأن فيه ناس بتخلطه مع فكرة Base Class العامة.

## المشكلة

تخيل عندك Application Layer فيها مجموعة Services:

```python
class OrderService:
    pass

class CustomerService:
    pass

class InvoiceService:
    pass
```

كل الـ Services دي ممكن تحتاج سلوكيات مشتركة خاصة بالطبقة، زي:

- الوصول إلى بعض الـ Layer-level utilities.
- تنفيذ عمليات مشتركة.
- توفير سلوك موحد للكائنات التابعة للطبقة.

ممكن تلاقي نفسك بتكرر نفس الكود داخل كل Class.

مثلاً:

```python
class OrderService:

    def log_operation(self, message):
        print(message)

class CustomerService:

    def log_operation(self, message):
        print(message)

class InvoiceService:

    def log_operation(self, message):
        print(message)
```

ده تكرار غير ضروري لو السلوك فعلًا مشترك ومناسب لكل الكلاسات دي.

السؤال: هل ممكن يكون عندنا Superclass واحدة تحتوي على السلوك المشترك الخاص بالـ Layer؟

هنا بيظهر Layer Supertype.

## الفكرة والحل

**Layer Supertype هو Base Class مشتركة للكلاسات الموجودة داخل Layer معينة، بحيث توفر السلوك أو الخصائص المشتركة الخاصة بالطبقة دي.**

لاحظ نقطتين:

1. مش Base Class لكل Classes المشروع.
1. مش بنعمل Inheritance لمجرد إن عندنا كود متكرر؛ لازم يكون فيه سلوك مشترك منطقي تابع للطبقة.

**Application Layer**

**ApplicationServiceBase**

Shared Layer Behavior

**OrderService**

**CustomerService**

**InvoiceService**

## مثال

هنعمل Base Class خاصة بالـ Application Layer.

```python
class ApplicationServiceBase:

    def log_operation(self, message):
        print(f"[APPLICATION] {message}")
```

وبعد كده الـ Services ترث منها:

```python
class OrderService(ApplicationServiceBase):

    def create_order(self):
        self.log_operation("Creating order")

class CustomerService(ApplicationServiceBase):

    def create_customer(self):
        self.log_operation("Creating customer")

class InvoiceService(ApplicationServiceBase):

    def create_invoice(self):
        self.log_operation("Creating invoice")
```

الاستخدام:

```python
order_service = OrderService()

order_service.create_order()
```

النتيجة:

```plain text
[APPLICATION] Creating order
```

دلوقتي السلوك المشترك موجود في مكان واحد، والـ Services بتستخدمه عن طريق Inheritance.

**لكن هل ده معناه إن كل Application Services لازم ترث من ApplicationServiceBase؟**

لأ.

لو الـ Base Class مش بتقدم سلوك مشترك حقيقي، يبقى وجودها مش مفيد.

كمان لو السلوك المشترك مش تابع منطقيًا للطبقة، ممكن يكون الأفضل استخدام Composition أو Utility Service مستقلة بدل Inheritance.

---

## أقرب GoF Pattern

أقرب GoF Patterns للمقارنة هما Template Method و`Composite` مش بنفس درجة التشابه، لكن Template Method هي المقارنة الأهم.

**1. Template Method**

(تشابه في استخدام Inheritance)

Template Method بيحدد Skeleton لخوارزمية داخل Base Class، وبيترك بعض الخطوات للـ Subclasses عشان تنفذها.

مثال:

```python
class ReportGenerator:

    def generate(self):
        self.fetch_data()
        self.format_data()
        self.export()

    def fetch_data(self):
        raise NotImplementedError

    def format_data(self):
        raise NotImplementedError

    def export(self):
        raise NotImplementedError
```

**أوجه التشابه:**

- الاتنين ممكن يستخدموا Base Class.
- الاتنين ممكن يشاركوا سلوكًا مشتركًا بين Subclasses.
- الاتنين بيستخدموا Inheritance.

**ليه Layer Supertype مش بديل لـ Template Method؟**

لأن Template Method هدفه تحديد خطوات Algorithm وترتيب تنفيذها.

أما Layer Supertype هدفه توفير سلوك أو خصائص مشتركة لكلاسات طبقة معينة.

مش لازم Layer Supertype يحتوي على Algorithm أصلًا.

---

**2. Composite**

(تشابه محدود جدًا)

Composite بيستخدم Tree Structure لتمثيل Objects فردية ومجموعات Objects من خلال Interface موحدة.

ممكن تلاقي Inheritance في تنفيذه، لكن ده مش معناه إنه مشابه وظيفيًا لـ Layer Supertype.

**ليه مش بديل عنه؟**

لأن Composite بيحل مشكلة تمثيل Hierarchical Structures، أما Layer Supertype بيحل مشكلة مشاركة السلوك الخاص بطبقة.

### مقارنة سريعة

المقارنة	Layer Supertype	Template Method
الهدف	مشاركة سلوك خاص بالطبقة	تحديد Skeleton لخوارزمية
Inheritance	نعم غالبًا	نعم
يحتوي على Algorithm؟	مش شرط	نعم
يحتاج Subclass Overrides؟	مش شرط	غالبًا
نطاق الاستخدام	Layer	Behavior / Algorithm

## علاقته بالعمارة

هنا لازم نفهم إن كل Layer ممكن يكون لها Supertype مختلف.

مثلاً:

```plain text
application/
    base/
        application_service_base.py

    services/
        order_service.py
        invoice_service.py

domain/
    base/
        domain_entity_base.py

    entities/
        order.py
        customer.py

infrastructure/
    base/
        infrastructure_repository_base.py

    repositories/
        postgres_order_repository.py
```

ده مثال توضيحي، مش قاعدة إن كل Layer لازم يكون عندها Base Class.

المهم إن السلوك المشترك يكون مرتبطًا فعلًا بمسؤوليات الطبقة.

### هل Layer Supertype مناسب لـ Clean Architecture؟

ممكن جدًا، بشرط إننا نحترم Dependency Rule.

مثلًا:

- ApplicationServiceBase ممكن تكون داخل Application.
- DomainEntityBase ممكن تكون داخل Domain لو فيه سلوك مشترك حقيقي.
- Infrastructure ممكن يكون لها Base Classes خاصة بيها.

لكن مينفعش Domain يرث من Infrastructure Base Class؛ لأن ده هيعكس اتجاه الاعتماديات.

## سادسًا: إمتى أستخدمه وإمتى أتجنبه؟

**استخدم Layer Supertype لما:**

- يكون عندك سلوك مشترك فعلًا بين Classes في نفس الطبقة.
- السلوك ده تابع لمسؤوليات الطبقة.
- الـ Base Class بتقلل التكرار من غير ما تفرض علاقات وراثة غير منطقية.

**تجنبه لما:**

- بتعمل Base Class ضخمة لكل المشروع.
- بتجمع وظائف ملهاش علاقة ببعض.
- بتستخدم Inheritance لمجرد مشاركة دوال بسيطة.
- بتخلق Coupling بين Layers مختلفة.

## الخلاصة
Layer Supertype هو Base Class مشتركة للكلاسات داخل Layer محددة، لتوفير السلوك المشترك الخاص بيها.

أقرب GoF Pattern:

- **Template Method:** بسبب استخدام Inheritance ومشاركة السلوك، لكن Template Method هدفه تنظيم Algorithm.
- **Composite:** تشابه شكلي محدود بسبب إمكانية استخدام Class Hierarchy، لكن Intent مختلف تمامًا.

---


# Separated Interface

النمط ده مهم جدًا؛ لأنه مرتبط بشكل مباشر بالـ Dependency Management، وهنحتاجه لما نتكلم عن Clean Architecture وHexagonal Architecture.

## المشكلة

تخيل إن عندك Application Layer محتاجة تتعامل مع Database.

ممكن تكتب الكود بالشكل ده:

```python
class PostgresUserRepository:

    def get_by_id(self, user_id):
        # PostgreSQL query
        pass

class UserService:

    def __init__(self):
        self.repository = PostgresUserRepository()

    def get_user(self, user_id):
        return self.repository.get_by_id(user_id)
```

إيه المشكلة هنا؟

UserService بقت معتمدة مباشرة على PostgresUserRepository.

وده معناه إن الـ Application Layer عارفة تفاصيل الـ Infrastructure Layer.

لو قررت تستبدل PostgreSQL بـ MongoDB، أو تستخدم In-Memory Repository للاختبار، هتحتاج تغيّر طريقة بناء الـ Service أو كودها.

المشكلة الأساسية هنا مش إننا بنستخدم Database.

المشكلة هي **اتجاه الاعتماديات (Dependency Direction)**.

## الفكرة والحل

**Separated Interface هو Pattern بيخلي تعريف الـ Interface موجود في Package منفصل عن Package اللي بيحتوي على Implementation.**

والفكرة المهمة في Fowler هي إن الـ Interface غالبًا بيتحط في الـ Package اللي محتاج يستخدمه، بينما الـ Implementation موجود في Package تاني.

بدل ما الـ Application تعتمد على Infrastructure، نخلي Infrastructure هي اللي تعتمد على الـ Interface اللي الـ Application عرّفته.

**قبل Separated Interface**

**Application**

UserService

**Infrastructure**

PostgresUserRepository

---

**بعد Separated Interface**

**Application**

UserService + UserRepository Interface

**Infrastructure**

PostgresUserRepository implements UserRepository

الأسهم هنا بتوضح اتجاه اعتماد الكود، مش اتجاه استدعاء الدوال وقت التشغيل.

لاحظ الفرق:

- الـ Application بتعرّف العقد اللي هي محتاجاه.
- الـ Infrastructure بتنفذ العقد ده.
- الـ Application مش محتاجة تعرف نوع قاعدة البيانات.

## مثال

### 1. تعريف الـ Interface داخل Application

```python
from abc import ABC, abstractmethod

class UserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id):
        pass
```

### 2. الـ Application Service

```python
class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_user(self, user_id):
        return self.repository.get_by_id(user_id)
```

لاحظ إن UserService مش بتعمل new لـ PostgresUserRepository.

هي بتستقبل أي Object يحقق العقد المطلوب.

### 3. Infrastructure Implementation

```python
class PostgresUserRepository(UserRepository):

    def get_by_id(self, user_id):
        # PostgreSQL query
        return {
            "id": user_id,
            "name": "Saleh"
        }
```

### 4. Composition Root

مين المسؤول عن توصيل الـ Implementation بالـ Application؟

الجزء المسؤول عن بناء التطبيق وتركيب مكوناته، وغالبًا بنسميه Composition Root.

```python
repository = PostgresUserRepository()

user_service = UserService(repository)

user = user_service.get_user(10)
```

كده حققنا الفصل بين الـ Application والـ Infrastructure.

## أقرب GoF Pattern

هنا المقارنة مختلفة شوية؛ لأن مفيش GoF Pattern مطابق له.

أقرب حاجة للمقارنة هي Bridge، وبعده Strategy.

**1. Bridge**

(تشابه في فصل التجريد عن التنفيذ)

Bridge هدفه فصل Abstraction عن Implementation بحيث كل واحد يقدر يتغير بشكل مستقل عن التاني.

مثال كلاسيكي: عندك أنواع مختلفة من Remote Controls، وأنواع مختلفة من Devices.

بدل ما تعمل Class لكل تركيبة، بتفصل الـ Remote Control عن Device Implementation.

**أوجه التشابه:**

- الاتنين بيفصلوا التعامل مع Abstraction عن تفاصيل Implementation.
- الاتنين ممكن يستخدموا Interfaces.
- الاتنين بيقللوا الاعتماد المباشر على Implementations محددة.

**ليه Separated Interface مش بديل لـ Bridge؟**

لأن Bridge بيحل مشكلة تعدد وتطور Hierarchies مستقلة.

أما Separated Interface فبيركز على مكان تعريف الـ Interface بالنسبة للـ Client والـ Implementation، وبالتالي اتجاه الاعتماديات بين الـ Packages.

ممكن تستخدم Separated Interface من غير ما يكون عندك Hierarchies متعددة أصلًا.

---

**2. Strategy**

(تشابه في الاعتماد على Abstraction)

Strategy بيسمح لك تبدّل بين خوارزميات مختلفة من خلال Interface مشتركة.

مثال: طرق مختلفة لحساب الخصم.

**ليه مش بديل لـ Separated Interface؟**

لأن Strategy هدفه تبديل Algorithms، بينما Separated Interface هدفه فصل الـ Interface عن الـ Implementation على مستوى تنظيم الاعتماديات.

ممكن Strategy يستخدم Separated Interface، لكن كل واحد بيحل مشكلة مختلفة.

### مقارنة سريعة

المقارنة	Separated Interface	Bridge	Strategy
الهدف	فصل تعريف العقد عن التنفيذ وتنظيم الاعتماديات	فصل Hierarchies	تبديل Algorithms
المستوى المعتاد	Packages / Modules	Objects / Classes	Objects / Classes
يحتاج أكثر من Implementation؟	لا	غالبًا توجد Variations	غالبًا توجد Strategies متعددة
المشكلة الأساسية	Dependency Direction	Structural Complexity	Algorithm Variation

## علاقته بالعمارة

دي أهم نقطة في النمط.

لازم نفرّق بين 3 مفاهيم:

**1. Dependency Inversion Principle (DIP)**

ده مبدأ من SOLID بيقول إن High-level Modules وLow-level Modules ما يعتمدوش على بعض بشكل مباشر، لكن يعتمدوا على Abstractions.

**2. Separated Interface**

ده Pattern لتنظيم الكود بحيث الـ Interface تكون في Package منفصل عن الـ Implementation، وغالبًا في Package العميل.

**3. Clean Architecture**

دي Architecture بتعتمد على جعل الاعتماديات البرمجية تتجه للداخل، ناحية الـ Business Rules.

ممكن نستخدم Separated Interface لتحقيق Dependency Inversion داخل Clean Architecture.

لكن مش معنى كده إن Separated Interface هو نفسه Clean Architecture أو إنه وحده بيحققها.

## سادسًا: مثال Folder Structure

```plain text
project/
│
├── application/
│   ├── interfaces/
│   │   └── user_repository.py
│   │
│   └── services/
│       └── user_service.py
│
├── infrastructure/
│   └── persistence/
│       └── postgres_user_repository.py
│
└── main.py
```

الـ Interface موجودة في application، والتنفيذ موجود في infrastructure.

وده مثال عملي على Separated Interface.

## الخلاصة
Separated Interface بيحل مشكلة اعتماد الـ Client على Package معينة عشان يحصل على Implementation.

أقرب GoF Pattern ليه هو:

- **Bridge:** بسبب الفصل بين Abstraction وImplementation.
- **Strategy:** بسبب استخدام Abstraction تسمح بتعدد Implementations.

لكنه مش بديل عن أي واحد منهم؛ لأن Intent مختلف.

---

**الترتيب اللي جاي:**


# Registry

## المشكلة

تخيل إن عندك تطبيق E-Commerce، وفيه مجموعة Services محتاجين يوصلوا لبعض.

مثلًا:

- OrderService
- PaymentService
- EmailService
- InventoryService

وعندك OrderService محتاجة تستخدم PaymentService.

ممكن تعمل الآتي:

```python
class OrderService:

    def __init__(self):
        self.payment_service = PaymentService()
```

لكن تخيل إن عندك عشرات الكلاسات، وكل واحد محتاج يوصل إلى Services مختلفة.

ممكن تبدأ تكرر إنشاء الـ Objects في أماكن كتير، أو تمرر Dependencies من خلال عدد كبير من Constructors.

هنا تظهر مشكلة تانية: إزاي Object يقدر يوصل إلى Object أو Service مشتركة ومعروفة داخل التطبيق؟

**Registry بيقدم حل للمشكلة دي.**

## الفكرة والحل

**Registry هو Object معروف (Well-known Object) تقدر Objects تانية تستخدمه للوصول إلى Objects أو Services مسجلة عنده.**

بمعنى أبسط:

تخيل إن عندك دليل مركزي، بتسجل فيه الخدمات، وأي جزء في التطبيق محتاج خدمة معينة يقدر يطلبها من الدليل ده.

**من غير Registry**

OrderService

ReportService

PaymentService

EmailService

كل جزء ممكن يحتاج طريقة مختلفة للوصول إلى الخدمات.

---

**باستخدام Registry**

OrderService

ReportService

PaymentService

EmailService

**Registry**

Central lookup point

الفكرة إن الـ Registry بيكون نقطة معروفة للوصول إلى الخدمات المسجلة.

## مثال

هنعمل Registry بسيط يخزن الخدمات باستخدام أسماء (Keys).

### 1. تعريف Registry

```python
class Registry:

    _services = {}

    @classmethod
    def register(cls, name, service):
        cls._services[name] = service

    @classmethod
    def get(cls, name):
        if name not in cls._services:
            raise KeyError(f"Service not found: {name}")

        return cls._services[name]
```

### 2. تعريف الخدمات

```python
class PaymentService:

    def charge(self, amount):
        return f"Charged {amount}"

class EmailService:

    def send(self, email, message):
        return f"Email sent to {email}"
```

### 3. تسجيل الخدمات

```python
Registry.register("payment", PaymentService())
Registry.register("email", EmailService())
```

### 4. الوصول للخدمات

```python
payment_service = Registry.get("payment")

result = payment_service.charge(500)

print(result)
```

النتيجة:

```plain text
Charged 500
```

لاحظ إن OrderService مش محتاجة تعرف تفاصيل إنشاء PaymentService أو مكان تخزينها.

هي بتطلبها من Registry.

---

## أقرب GoF Pattern

أقرب أنماط GoF للمقارنة هنا هي Singleton و`Abstract Factory`، لكن التشابه مش معناه إنهم نفس النمط.

**1. Singleton**

(تشابه في إتاحة Object معروف مركزيًا)

Singleton بيضمن وجود Instance واحدة من Class، ويوفر طريقة للوصول إليها.

ممكن تعمل Registry كـ Singleton عشان كل أجزاء التطبيق تستخدم نفس الـ Registry.

**ليه Registry مش بديل لـ Singleton؟**

لأن Singleton بيحل مشكلة عدد الـ Instances وطريقة الوصول إلى Instance واحدة.

أما Registry بيحل مشكلة البحث والوصول إلى Objects أو Services مسجلة.

ممكن Registry يكون Singleton، لكن مش لازم يكون كذلك.

يعني:

- Singleton يحدد طريقة إنشاء وإتاحة Registry.
- Registry يحدد مسؤولية تسجيل الخدمات والبحث عنها.
  ---
  **2. Abstract Factory**
  (تشابه في توفير الوصول إلى Objects)

Abstract Factory بيقدم Interface لإنشاء عائلات من Objects مترابطة من غير ما العميل يعرف Classes الفعلية.

**ليه Registry مش بديل لـ Abstract Factory؟**

لأن Factory مسؤوليته إنشاء Objects، بينما Registry مسؤوليته الوصول إلى Objects مسجلة بالفعل.

ممكن Registry يخزن Factory Objects، وممكن Factory يسجل المنتجات اللي بينشئها في Registry، لكن الاتنين مش بيحلوا نفس المشكلة.

### مقارنة سريعة

المقارنة	Registry	Singleton	Abstract Factory
الهدف	البحث عن Objects مسجلة	ضمان Instance واحدة	إنشاء عائلات Objects
المسؤولية	Lookup	Lifecycle / Instance	Object Creation
هل ينشئ Objects؟	مش بالضرورة	نعم، ينشئ Instance الخاصة به	نعم
هل يوفر وصولًا مركزيًا؟	نعم	إلى Instance واحدة	من خلال Factory

## خامسًا: Registry وعلاقته بـ Service Locator وDependency Injection

هنا لازم نقف شوية؛ لأن فيه مفاهيم قريبة جدًا من بعض.

### 1. Registry

هو مكان معروف لتسجيل Objects والبحث عنها.

### 2. Service Locator

هو أسلوب تصميم بيوفر نقطة مركزية تقدر تطلب منها Services وقت الحاجة.

مثال:

```python
class OrderService:

    def checkout(self, order):
        payment = Registry.get("payment")
        payment.charge(order.total)
```

هنا OrderService بتطلب الـ Dependency بنفسها.

وده مثال على استخدام Registry بأسلوب قريب من Service Locator.

### 3. Dependency Injection

في DI، بدل ما الـ Service تبحث بنفسها عن الـ Dependency، حد خارجي بيوفرها لها.

```python
class OrderService:

    def __init__(self, payment_service):
        self.payment_service = payment_service

    def checkout(self, order):
        self.payment_service.charge(order.total)
```

الفرق الأساسي:

**Service Locator**

OrderService

تطلب الـ Dependency بنفسها

Registry / Service Locator

---

**Dependency Injection**

Composition Root

مسؤول عن إنشاء وربط Dependencies

OrderService + PaymentService

الـ Dependency يتم تمريرها للـ Service

**إيه المشكلة في Service Locator؟**

إن الـ Dependencies بتكون مخفية داخل الكود.

لو بصيت على Constructor بتاع OrderService مش هتعرف إنه محتاج PaymentService.

وده بيصعّب فهم Dependencies واختبارها مقارنةً بالـ Constructor Injection.

علشان كده، في تصميمات كتير بتفضل Dependency Injection على Service Locator.

لكن ده مش معناه إن Registry أو Service Locator غلط دائمًا؛ استخدامهم بيعتمد على طبيعة النظام.

## علاقته بالعمارة

ممكن تلاقي Registry في تطبيقات مختلفة:

- **Layered Architecture:** ممكن تستخدمه للوصول إلى Services مشتركة.
- **Clean Architecture:** ممكن يظهر في Composition أو Infrastructure، لكن خلي بالك من استخدامه داخل الـ Domain أو Application لو هيخفي Dependencies ويكسر اتجاه الاعتماديات.
- **Plugin Architecture:** ممكن تستخدم Registry لتسجيل Plugins ثم البحث عنها بالاسم أو النوع.

ومهم جدًا: وجود Registry مش معناه إنك محتاج تحط كل Services التطبيق فيه. أحيانًا ده بيحول النظام إلى Global Service Locator ضخم.

## الخلاصة
Registry بيحل مشكلة الوصول إلى Objects أو Services مسجلة في نقطة مركزية معروفة.

أقرب GoF Patterns ليه:

- **Singleton:** بسبب فكرة الوصول المركزي إلى Object واحد، لكنه مش مسؤول عن تسجيل الخدمات.
- **Abstract Factory:** بسبب إتاحة الوصول إلى Objects، لكنه مسؤول عن إنشائها مش البحث عنها.

والفرق المهم اللي لازم تفتكره:

**Registry = Lookup**

**Factory = Creation**

**Singleton = Single Instance**

**Dependency Injection = Supplying Dependencies**

---


# Value Object

النمط ده من أهم الأنماط اللي هنقابلها في DDD، لكن خلينا نفهم تعريفه الأول بعيدًا عن DDD.

## المشكلة

تخيل عندك نظام لإدارة العملاء.

وعندك عميلين:

```python
customer_1 = {
    "name": "Ahmed",
    "city": "Cairo",
    "street": "Nasr City"
}

customer_2 = {
    "name": "Ahmed",
    "city": "Cairo",
    "street": "Nasr City"
}
```

هل العميل الأول هو نفسه العميل الثاني؟

مش بالضرورة. ممكن يكونوا شخصين مختلفين تمامًا، حتى لو بياناتهم متطابقة.

لكن خلينا نغير المثال.

عندك عنوانين:

```python
address_1 = {
    "city": "Cairo",
    "street": "Nasr City"
}

address_2 = {
    "city": "Cairo",
    "street": "Nasr City"
}
```

هل العنوان الأول يساوي العنوان الثاني؟

من ناحية القيمة، أيوه.

إحنا مش مهتمين إذا كان address_1 هو نفس الـ Object الموجود في الذاكرة بتاع address_2.

إحنا مهتمين إن القيم اللي جواهم متساوية.

وهنا تظهر فكرة Value Object.

## الفكرة والحل

**Value Object هو Object بتتحدد مساواته (Equality) بناءً على قيم خصائصه، مش بناءً على هويته (Identity).**

بمعنى:

- Entity: مهم مين هو الـ Object.
- Value Object: المهم إيه القيم اللي بيمثلها.

**Entity**

**Customer A**

ID = 101

Name = Ahmed

**Customer B**

ID = 102

Name = Ahmed

(مش متساويين)

رغم إن الاسم واحد، لكن الهوية مختلفة.

---

**Value Object**

City = Cairo

Street = Nasr City

City = Cairo

Street = Nasr City

(متساويين بالقيمة)

لأن الخصائص اللي بتحدد القيمة متطابقة.

## مثال

هنعمل Address كـ Value Object.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Address:
    city: str
    street: str
```

دلوقتي:

```python
address_1 = Address(
    city="Cairo",
    street="Nasr City"
)

address_2 = Address(
    city="Cairo",
    street="Nasr City"
)

print(address_1 == address_2)
```

النتيجة:

```plain text
True
```

ليه؟

لأن dataclass بتوفر Equality بناءً على قيم الحقول افتراضيًا.

وكمان استخدمنا:

```python
frozen=True
```

وده بيخلي الـ Object Immutable، بمعنى إنك مش هتقدر تغير قيمه بعد إنشائه.

مثلًا:

```python
address_1.city = "Alexandria"
```

هيؤدي إلى FrozenInstanceError.

### هل كل Value Object لازم يكون Immutable؟

مش ده التعريف الأساسي.

التعريف الأساسي هو إن المساواة بتتحدد بالقيمة مش بالهوية.

لكن Immutability ممارسة قوية جدًا مع Value Objects؛ لأنها بتخلي سلوكها أكثر وضوحًا وتقلل المشاكل الناتجة عن تغيير القيم بعد إنشاء الكائن.

## أقرب GoF Pattern

هنا فيه تشابه مهم مع Flyweight، لكن لازم نفرّق بينهم.

**1. Flyweight**

(تشابه في مشاركة القيم)

Flyweight هدفه تقليل استهلاك الذاكرة عن طريق مشاركة Objects متشابهة في بياناتها بين عدد كبير من المستخدمين.

مثال: لعبة فيها آلاف الأشجار، بدل ما تخزن نفس بيانات شكل الشجرة آلاف المرات، تشارك بيانات الشكل.

**أوجه التشابه:**

- الاتنين ممكن يعتمدوا على بيانات ثابتة أو غير قابلة للتغيير.
- الاتنين ممكن يستفيدوا من مشاركة Objects متساوية في القيمة.

**ليه Value Object مش بديل لـ Flyweight؟**

لأن Value Object بيحدد طريقة تمثيل القيمة والمساواة.

أما Flyweight بيحل مشكلة استهلاك الذاكرة عن طريق مشاركة الحالة المشتركة.

ممكن تستخدم Value Objects داخل Flyweight، لكن مش كل Value Object هو Flyweight.

---

**2. Prototype**

(تشابه محدود)

Prototype هدفه إنشاء Objects جديدة عن طريق نسخ Object موجود.

ممكن تنسخ Value Object لإنشاء قيمة جديدة قريبة من قيمة سابقة.

لكن Prototype مش مسؤول عن تحديد معنى المساواة بين Objects.

### مقارنة سريعة

المقارنة	Value Object	Flyweight
الهدف	تمثيل قيمة	تقليل استهلاك الذاكرة
المساواة	بالقيمة	مش هي الهدف الأساسي
المشاركة	ممكنة	أساسية في الفكرة
Immutability	شائعة جدًا	الحالة المشتركة غالبًا ثابتة

## خامسًا: علاقته بـ DDD

في DDD، الـ Value Object يعتبر مفهومًا أساسيًا في Tactical Design.

مثلًا، ممكن يكون عندك:

- Address
- Money
- DateRange
- Quantity
- Percentage

بدل ما تمثل كل حاجة بمجموعة Primitive Values متفرقة، بتجمع القيم المرتبطة ببعض داخل Object له معنى وقواعد واضحة.

وده بيساعدك تمنع حالات غير صحيحة.

مثلاً، Percentage ممكن يضمن إن القيمة بين 0 و100، و`Money` يضمن وجود عملة مع المبلغ.

لكن خلي بالك: Value Object مش مقتصر على DDD؛ ده مفهوم أوسع موجود في تصميم الـ Object-Oriented Software.

## الخلاصة
Value Object هو Object المساواة فيه بالقيمة، مش بالهوية.

أقرب GoF Pattern للمقارنة:

- **Flyweight:** بسبب إمكانية مشاركة Objects المتساوية، لكن Flyweight هدفه الأساسي تحسين استهلاك الذاكرة.
- **Prototype:** بسبب إمكانية نسخ Objects، لكن Prototype هدفه الإنشاء بالنسخ.

والنقطة الأساسية:

**Entity = Identity**

**Value Object = Value**

---

التالي عندنا **Money**، وده في الحقيقة مثال متخصص ومهم جدًا على Value Object، وهنشوف ليه تم فصله كنمط مستقل بدل ما نعتبره مجرد Decimal وخلاص.

تمام يا صاحبي. هنكمل بنفس ترتيب الشرح، مع الحفاظ على اتجاه القراءة من اليمين للشمال، وفصل الأكواد والمصطلحات الإنجليزية عن النص العربي.


# Money

## المشكلة

تخيل إنك بتبني نظام محاسبي، وعندك منتج سعره 100 جنيه.

ممكن تمثّل السعر باستخدام float:

```python
price = 100.50
```

للوهلة الأولى مفيش مشكلة، لكن فيه مشكلتين أساسيتين:

**المشكلة الأولى: دقة العمليات الحسابية.**

```python
print(0.1 + 0.2)
```

النتيجة:

```plain text
0.30000000000000004
```

وده بسبب طريقة تمثيل الأرقام العشرية باستخدام Floating Point.

**المشكلة الثانية: العملة.**

هل الرقم 100 معناه:

- 100 EGP؟
- 100 USD؟
- 100 EUR؟

الرقم لوحده مش كفاية لتمثيل مبلغ مالي.

كمان هل ينفع تجمع 100 جنيه مع 100 دولار؟

طبعًا مش من غير تحويل للعملة.

إذن المشكلة مش مجرد تمثيل رقم، إحنا محتاجين نمثل مفهوم مالي له قواعد خاصة.

## الفكرة والحل

**Money هو Value Object متخصص لتمثيل مبلغ مالي مع العملة الخاصة به، وتوفير العمليات الحسابية المناسبة له.**

يعني بدل ما نمثل المبلغ كرقم فقط، نمثله كـ Object يحتوي على:

- Amount: قيمة المبلغ.
- Currency: العملة.
- Arithmetic Rules: قواعد العمليات الحسابية.
- Rounding Rules: قواعد التقريب عند الحاجة.

**Money Object**

# 100.50 EGP

---

Amount **100.50**

Currency **EGP**

Type **Value Object**

## مثال

هنستخدم Decimal بدل float عشان نتعامل مع القيم المالية بدقة عشرية مناسبة.

### 1. إنشاء Money Object

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class Money:

    amount: Decimal
    currency: str

    def __post_init__(self):
        if not self.currency:
            raise ValueError("Currency is required")

        if not isinstance(self.amount, Decimal):
            raise TypeError("Amount must be Decimal")
```

### 2. تنفيذ عمليات الجمع

```python
@dataclass(frozen=True)
class Money:

    amount: Decimal
    currency: str

    def __post_init__(self):
        if not self.currency:
            raise ValueError("Currency is required")

        if not isinstance(self.amount, Decimal):
            raise TypeError("Amount must be Decimal")

    def __add__(self, other):

        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")

        return Money(
            amount=self.amount + other.amount,
            currency=self.currency
        )
```

الاستخدام:

```python
price_1 = Money(Decimal("100.50"), "EGP")
price_2 = Money(Decimal("50.25"), "EGP")

total = price_1 + price_2

print(total)
```

النتيجة:

```plain text
Money(amount=Decimal('150.75'), currency='EGP')
```

لكن لو حاولت تعمل:

```python
price_1 = Money(Decimal("100"), "EGP")
price_2 = Money(Decimal("100"), "USD")

total = price_1 + price_2
```

هيحصل Exception.

وده سلوك مقصود؛ لأن جمع عملتين مختلفتين من غير Currency Conversion مش عملية مالية صحيحة.

### 3. تنفيذ عملية الضرب

ممكن نحتاج نضرب مبلغ مالي في كمية:

```python
def __mul__(self, quantity):

    return Money(
        amount=self.amount * Decimal(str(quantity)),
        currency=self.currency
    )
```

مثلًا:

```python
unit_price = Money(Decimal("25.50"), "EGP")

total = unit_price * 4
```

النتيجة:

```plain text
102.00 EGP
```

ملاحظة: ده مثال تعليمي. تطبيق Money حقيقي محتاج كمان سياسات واضحة للـ Rounding، ودقة العملة، والضرب والقسمة والتوزيع.

---

## أقرب GoF Pattern

هنا لازم نكون دقيقين: مفيش GoF Pattern مطابق لـ Money.

أقرب مقارنة مفيدة هي Strategy و`Flyweight`، لكن التشابه جزئي.

**1. Strategy**

(تشابه في إمكانية تغيير قواعد الحساب)

Strategy بيسمح بتبديل Algorithm أو Policy من غير تغيير الكلاس اللي بيستخدمها.

ممكن تستخدم Strategy مع Money لاختيار سياسات مختلفة للتقريب أو تحويل العملات.

مثال:

- Banker's Rounding.
- Half Up Rounding.
- Currency Conversion Strategy.

**ليه Money مش بديل لـ Strategy؟**

لأن Money بيمثل قيمة مالية، بينما Strategy بتمثل خوارزمية أو سلوك قابل للاستبدال.

ممكن Money يستخدم Strategy داخليًا، لكن مش لازم.

---

**2. Flyweight**

(تشابه محدود)

ممكن تشارك بيانات العملة الثابتة، زي اسم العملة وعدد الخانات العشرية، بين عدد كبير من Money Objects.

لكن ده مش الهدف الأساسي من Money.

**ليه Money مش بديل لـ Flyweight؟**

Money هدفه صحة تمثيل العمليات المالية، بينما Flyweight هدفه تقليل استهلاك الذاكرة.

### مقارنة سريعة

المقارنة	Money	Strategy	Flyweight
الهدف	تمثيل المبالغ المالية	تبديل الخوارزميات	مشاركة الحالة لتوفير الذاكرة
يمثل قيمة؟	نعم	لا	لا، هو أسلوب مشاركة
يحتوي على قواعد مالية؟	نعم	ممكن يوفرها	لا
GoF Pattern؟	لا	نعم	نعم

## خامسًا: علاقته بـ DDD

Money من أشهر أمثلة Value Objects في DDD.

مثلًا، في نظام محاسبي:

```python
class Invoice:

    def __init__(self, total):
        self.total = total
```

بدل ما total يكون مجرد Decimal، ممكن يكون Money.

وبالتالي الـ Invoice مش محتاجة تعيد تنفيذ قواعد العملة والجمع في كل مكان.

كمان فيه نقطة مهمة:

**Currency Conversion مش مجرد قسمة أو ضرب.**

لازم تحدد:

- Exchange Rate.
- مصدر سعر الصرف.
- تاريخ سعر الصرف.
- سياسة التقريب.
- العملة المستهدفة.

وده مهم جدًا في الأنظمة المحاسبية والمالية.

## علاقته بالعمارة

Money ممكن يظهر في أي طبقة بتتعامل مع المبالغ المالية، لكن الأفضل إن قواعده الأساسية تكون في الـ Domain Model لو المبلغ جزء من Business Domain.

مثلاً:

```plain text
domain/
    value_objects/
        money.py
        currency.py

    entities/
        invoice.py
        order.py
```

وبالتالي الـ Domain نفسه يقدر يضمن صحة العمليات المالية من غير ما يعتمد على Database أو Framework.

## الخلاصة
Money هو Value Object متخصص في تمثيل المبالغ المالية والعملات وقواعد التعامل معاها.

مفيش GoF Pattern مطابق ليه.

أقرب المقارنات:

- **Strategy:** ممكن تستخدمه لتبديل سياسات التقريب والتحويل.
- **Flyweight:** ممكن تستخدمه لمشاركة بيانات العملات الثابتة.

لكن Money مش بديل لأي واحد فيهم.

---


# Special Case

## المشكلة

تخيل عندك تطبيق لإدارة العملاء.

وعندك كود بالشكل ده:

```python
def get_customer_name(customer):

    if customer is None:
        return "Unknown Customer"

    return customer.name
```

المشكلة إنك ممكن تلاقي نفس الشرط بيتكرر في أماكن كتير:

```python
if customer is None:
    ...
```

وفي مكان تاني:

```python
if customer is None:
    ...
```

وفي مكان ثالث:

```python
if customer is None:
    ...
```

كل مرة بيكون عندك Conditional Logic للتعامل مع حالة معينة.

ومع زيادة الحالات، الكود بيبقى مليان شروط.

السؤال هنا:

هل ممكن نمثل الحالة الخاصة نفسها كـ Object له سلوك مناسب بدل ما ننشر شروط التعامل معاها في كل مكان؟

هنا بيظهر Special Case.

## الفكرة والحل

**Special Case هو Pattern بنعمل فيه Object يمثل حالة معينة، ويوفر السلوك المناسب للحالة دي بدل ما نخلي كل Client يتعامل معاها باستخدام شروط متكررة.**

مثلاً:

- عميل غير معروف.
- مستخدم Guest.
- منتج غير متاح.
- حساب افتراضي.

بدل ما كل جزء في التطبيق يسأل هل الحالة موجودة أو لأ، ممكن يتعامل مع Object يمثل الحالة الخاصة.

**بدون Special Case**

Client

if customer is None

كل Client محتاج يعرف ويتعامل مع الحالة الخاصة.

---

**باستخدام Special Case**

Client

**Special Case Object**

سلوك محدد للحالة الخاصة

## مثال

عندنا Customer عادي:

```python
class Customer:

    def __init__(self, name):
        self.name = name

    def get_discount(self):
        return 10

    def get_display_name(self):
        return self.name
```

هنعمل Special Case يمثل العميل غير المعروف:

```python
class UnknownCustomer:

    def __init__(self):
        self.name = "Unknown Customer"

    def get_discount(self):
        return 0

    def get_display_name(self):
        return self.name
```

دلوقتي نقدر نستخدم الاثنين من خلال نفس العمليات:

```python
def print_customer_info(customer):

    print(customer.get_display_name())
    print(customer.get_discount())
```

الاستخدام:

```python
customer = UnknownCustomer()

print_customer_info(customer)
```

النتيجة:

```plain text
Unknown Customer
0
```

لاحظ إننا مش محتاجين نكتب:

```python
if customer is None:
```

داخل print_customer_info.

الـ Special Case نفسه بيوفر السلوك المناسب.

لكن فيه شرط مهم: لازم الحالة الخاصة تكون حالة مقبولة في الـ Business Domain.

لو العميل مطلوب إجباريًا لإنشاء فاتورة قانونية مثلًا، مينفعش نستبدل غيابه بـ UnknownCustomer ونتجاهل المشكلة. هنا لازم نرفض العملية أو نرفع Exception حسب قواعد النظام.

---

## أقرب GoF Pattern

أقرب GoF Pattern ليه هو Null Object، وده تشابه مهم جدًا.

**1. Null Object**

(أقرب نمط للمقارنة)

Null Object بيقدم Object له سلوك محدد بدل استخدام None أو null.

مثال:

بدل ما ترجع None لو مفيش Logger، ممكن ترجع NullLogger عنده log() لكن لا ينفذ أي شيء.

**أوجه التشابه:**

- الاتنين بيستبدلوا التعامل المباشر مع حالة خاصة بـ Object.
- الاتنين ممكن يقللوا Conditional Logic.
- الاتنين بيخلوا العميل يتعامل مع واجهة متوقعة.

**ليه Special Case مش بديل لـ Null Object؟**

لأن Null Object يعتبر حالة متخصصة من فكرة Special Case.

لكن Special Case أوسع؛ مش لازم يكون بديلًا عن None.

ممكن يكون Object يمثل مستخدم Guest بصلاحيات محددة، أو منتج غير متاح بسلوك معين.

---

**2. State**

(تشابه في تمثيل سلوك حسب الحالة)

State Pattern بيغير سلوك Object حسب حالته الداخلية عن طريق State Objects.

**ليه Special Case مش بديل لـ State؟**

لأن State هدفه تنظيم انتقالات وسلوك حالات Object خلال دورة حياته.

أما Special Case هدفه تمثيل حالة استثنائية أو خاصة وتوفير السلوك المناسب لها.

ممكن تستخدم State لتمثيل حالات كيان، وتستخدم Special Case لحالة معينة من الحالات دي، لكن كل واحد له Intent مختلف.

### مقارنة سريعة

المقارنة	Special Case	Null Object	State
الهدف	تمثيل حالة خاصة بسلوك محدد	استبدال null بسلوك آمن	تغيير السلوك حسب الحالة
يحتاج None؟	لا	غالبًا مرتبط بفكرة غيابه	لا
يدعم State Transitions؟	مش بالضرورة	مش الهدف	نعم
النطاق	أوسع	حالة متخصصة	دورة حياة Object

## خامسًا: علاقته بالـ DDD

في DDD، Special Case ممكن يظهر عند تمثيل حالات خاصة لها معنى في الـ Domain.

مثلاً:

- GuestUser
- UnknownCustomer
- UnavailableProduct

لكن لازم نكون حذرين: مش كل حالة Missing Data تتحول إلى Special Case.

فيه فرق بين:

- حالة خاصة مقبولة في الـ Business.
- بيانات ناقصة تمثل خطأ.
- حالة غير متوقعة تستدعي Exception.

مثال: عدم وجود صورة للمنتج ممكن يكون حالة مقبولة، لكن عدم وجود سعر لمنتج مطلوب بيعه ممكن يكون خطأ في البيانات.

## علاقته بالعمارة

ممكن تستخدم Special Case داخل الـ Domain Model أو Application Model، حسب طبيعة الحالة.

مثلاً:

```plain text
domain/
    customers/
        customer.py
        unknown_customer.py

    products/
        product.py
        unavailable_product.py
```

الفكرة إن السلوك الخاص يفضل قريبًا من المفهوم اللي بيمثله، بدل نشر الشروط في كل طبقات النظام.

## الخلاصة
Special Case بيحل مشكلة انتشار الشروط الخاصة بحالات معينة، عن طريق تمثيل الحالة نفسها كـ Object له سلوك مناسب.

أقرب GoF Pattern:

- **Null Object:** لأنه حالة متخصصة من Special Case.
- **State:** بسبب إمكانية تمثيل سلوك مختلف حسب الحالة.

لكن Special Case أوسع من Null Object، ومش بديل عن State.

---

التالي عندنا **Plugin**، وده مهم جدًا لفهم Extensibility وإزاي نخلي النظام قابل لإضافة Implementations جديدة من غير ما نعدّل في قلب التطبيق كل مرة.

نكمل بنفس المنهج، وهنحافظ على اتجاه النص العربي من اليمين للشمال، مع فصل الأكواد والمصطلحات الإنجليزية.


# Plugin

## المشكلة

تخيل إنك بتبني E-Commerce System، وعندك أكتر من Payment Provider:

- Paymob
- Stripe
- PayPal

ممكن تبدأ تكتب الكود بالشكل ده:

```python
class PaymentService:

    def pay(self, provider, amount):

        if provider == "stripe":
            # Stripe implementation
            pass

        elif provider == "paypal":
            # PayPal implementation
            pass

        elif provider == "paymob":
            # Paymob implementation
            pass
```

المشكلة إن كل ما تضيف Payment Provider جديد، هتحتاج تعدّل في PaymentService.

ومع زيادة عدد الـ Providers، الكلاس هيكبر ويصبح مرتبطًا بتفاصيل كل Implementation.

السؤال:

هل ممكن أضيف Payment Provider جديد من غير ما أعدل في الكود الأساسي المسؤول عن الدفع؟

هنا بيظهر دور Plugin.

## الفكرة والحل

**Plugin هو Pattern بيسمح بربط Implementations بالنظام وقت Configuration بدل ما تكون مرتبطة به بشكل ثابت وقت كتابة الكود أو Compile Time.**

بمعنى أبسط:

النظام الأساسي بيحدد Contract أو Interface.

وأي Implementation جديدة تقدر تلتزم بالـ Contract ده، وبعد كده يتم اختيارها وتوصيلها بالنظام عن طريق Configuration أو Registration أو Loading Mechanism.

**Plugin Architecture**

**Core Application**

يعرف الـ Contract فقط

**Plugin Interface**

Payment Provider Contract

**Stripe**

Plugin

**PayPal**

Plugin

**Paymob**

Plugin

الفكرة الأساسية إن الـ Core Application مش محتاجة تعرف تفاصيل كل Plugin.

هي محتاجة تعرف الـ Contract اللي كل Plugin لازم يلتزم بيه.

## مثال

هنعمل مثال بسيط لنظام Payment قابل لإضافة Providers جديدة.

### 1. تعريف الـ Contract

```python
from abc import ABC, abstractmethod

class PaymentPlugin(ABC):

    @abstractmethod
    def pay(self, amount):
        pass
```

### 2. إنشاء Plugins مختلفة

```python
class StripePlugin(PaymentPlugin):

    def pay(self, amount):
        return f"Stripe charged {amount}"

class PaymobPlugin(PaymentPlugin):

    def pay(self, amount):
        return f"Paymob charged {amount}"
```

كل Plugin عنده Implementation مختلفة، لكن الاتنين ملتزمين بنفس الـ Contract.

### 3. الـ Core Application

```python
class CheckoutService:

    def __init__(self, payment_plugin):
        self.payment_plugin = payment_plugin

    def checkout(self, amount):
        return self.payment_plugin.pay(amount)
```

لاحظ إن CheckoutService مش عارفة أي حاجة عن Stripe أو Paymob.

هي بتتعامل مع PaymentPlugin.

### 4. اختيار الـ Plugin أثناء Configuration

```python
def configure_payment(provider):

    plugins = {
        "stripe": StripePlugin,
        "paymob": PaymobPlugin,
    }

    plugin_class = plugins.get(provider)

    if plugin_class is None:
        raise ValueError("Unsupported payment provider")

    return plugin_class()
```

الاستخدام:

```python
payment_plugin = configure_payment("paymob")

checkout = CheckoutService(payment_plugin)

result = checkout.checkout(500)
```

النتيجة:

```plain text
Paymob charged 500
```

لو عايز تضيف Provider جديد، بتضيف Plugin جديد وتربطه في Configuration.

مش محتاج تعدّل CheckoutService.

ده مثال مبسط على Plugin Selection. الـ Plugin System الحقيقي ممكن يحتاج Dynamic Loading وMetadata وVersion Compatibility وSecurity Validation.

---

## أقرب GoF Pattern

أقرب GoF Patterns للمقارنة هما Strategy و`Abstract Factory`، لكن لازم نفصل بينهم كويس.

**1. Strategy**

(تشابه قوي في تعدد Implementations)

Strategy بيسمح لك بتبديل Algorithms مختلفة من خلال Interface مشتركة.

مثال: عندك أكثر من طريقة لحساب Shipping Cost.

```python
class ShippingStrategy:
    def calculate(self, weight):
        pass
```

**أوجه التشابه:**

- الاتنين ممكن يعتمدوا على Interface مشتركة.
- الاتنين بيسمحوا بوجود Implementations متعددة.
- الاتنين بيفصلوا الـ Client عن تفاصيل التنفيذ.

**ليه Plugin مش بديل لـ Strategy؟**

لأن Strategy هدفه تبديل Algorithm أو سلوك داخل التطبيق.

أما Plugin هدفه توسيع النظام بإضافة Implementations قابلة للربط وقت Configuration أو Loading.

بمعنى إن Strategy ممكن تكون جزءًا من Plugin، لكن Plugin عنده مفهوم أوسع متعلق بامتداد النظام.

---

**2. Abstract Factory**

(تشابه في فصل إنشاء Implementations)

Abstract Factory بيوفر Interface لإنشاء مجموعة من Objects مترابطة.

ممكن Plugin يحتوي على Factory لإنشاء المكونات الخاصة به.

**ليه Plugin مش بديل لـ Abstract Factory؟**

لأن Factory مسؤوليته إنشاء Objects.

أما Plugin مسؤوليته إضافة Implementation أو Extension للنظام.

ممكن Plugin يستخدم Abstract Factory داخله، لكن وجود Factory لوحده مش معناه إن عندك Plugin Architecture.

---

**3. Factory Method**

(تشابه في اختيار التنفيذ)

Factory Method بيسمح للـ Subclasses بتحديد نوع الـ Object اللي هيتم إنشاؤه.

Plugin ممكن يحتاج Factory Method لإنشاء مكوناته.

لكن Factory Method مش مسؤول عن تحميل Extensions أو اكتشافها أو تسجيلها.

### مقارنة سريعة

المقارنة	Plugin	Strategy	Abstract Factory
الهدف	توسيع النظام	تبديل Algorithm	إنشاء عائلات Objects
إضافة مكونات جديدة	نعم	إضافة Strategy	إضافة Factory
Configuration	جزء شائع من الفكرة	ممكن	ممكن
Dynamic Loading	ممكن	مش هدفه	مش هدفه
نطاق الاستخدام	Extensibility	Behavior	Object Creation

## علاقته بالعمارة

هنا Plugin بيظهر بشكل واضح في Plugin Architecture.

تخيل نظامًا فيه Core ثابت، وحوله Extensions قابلة للإضافة.

أمثلة:

- نظام يدعم Payment Providers متعددة.
- نظام يدعم Export Formats مختلفة.
- نظام يدعم Authentication Providers مختلفة.
- نظام يدعم Integrations مع أنظمة خارجية.

ممكن كمان تستخدم Plugin مع:

**Clean Architecture**

تعرّف Abstraction داخل الجزء الداخلي، وتوفر Implementations في الخارج، ويتم اختيارها عند Composition Root.

**Hexagonal Architecture**

تقدر تعتبر كل Plugin عبارة عن Adapter إضافي يحقق Port معينًا.

لكن مش كل Adapter هو Plugin؛ لأن Adapter ممكن يكون جزءًا ثابتًا من التطبيق، من غير أي آلية لتسجيل أو تحميل Extensions.

## سادسًا: الفرق بين Plugin وStrategy وSeparated Interface

دي مقارنة مهمة لأن التلاتة ممكن يظهروا مع بعض في نفس التصميم.

- Separated Interface: بيفصل مكان تعريف العقد عن مكان تنفيذها.
- Strategy: بيوفر سلوكيات أو Algorithms بديلة.
- Plugin: بيسمح بإضافة Implementations للنظام وربطها وقت Configuration.

ممكن تعمل Plugin Architecture باستخدام Separated Interface وStrategy مع بعض.

وده مش معناه إنهم نفس النمط.

## الخلاصة
Plugin بيحل مشكلة توسيع النظام بإضافة Implementations جديدة من غير ربط الـ Core بكل Implementation بشكل مباشر.

أقرب GoF Patterns:

- **Strategy:** بسبب تعدد Implementations القابلة للاختيار.
- **Abstract Factory:** بسبب إمكانية استخدام Factories لإنشاء مكونات الـ Plugin.
- **Factory Method:** بسبب إمكانية استخدامه في إنشاء الـ Objects.

لكن ولا واحد منهم بديل عن Plugin؛ لأن Plugin بيتعامل مع Extensibility على مستوى النظام.

---


# Service Stub

خلينا نبدأ بالمشكلة، وبعدها هنشوف علاقته بـ GoF؛ لأن فيه تشابه مهم جدًا بينه وبين Proxy.

## المشكلة

تخيل إن عندك تطبيق E-Commerce، وفيه جزء مسؤول عن حساب تكلفة الشحن.

أنت بتتعامل مع شركة شحن خارجية عندها API بالشكل ده:

```python
class ShippingService:

    def calculate_shipping(self, address, weight):
        # HTTP request to external shipping provider
        # Authentication
        # Wait for response
        # Parse response
        pass
```

وعندك OrderService بيعتمد على الخدمة دي:

```python
class OrderService:

    def __init__(self, shipping_service):
        self.shipping_service = shipping_service

    def checkout(self, order):
        shipping_cost = self.shipping_service.calculate_shipping(
            order.address,
            order.weight
        )

        return order.total + shipping_cost
```

دلوقتي أنت عايز تختبر OrderService.

هتواجهك مشاكل:

1. لازم خدمة الشحن الخارجية تكون شغالة.
1. لازم يكون عندك اتصال بالإنترنت.
1. ممكن الـ API تكون بطيئة.
1. ممكن الشركة تحاسبك على كل Request.
1. ممكن الخدمة ترجع Errors بشكل غير متوقع.
1. مش هتقدر تتحكم بسهولة في الـ Responses اللي بترجع أثناء الاختبار.

**السؤال هنا: هل لازم أتعامل مع خدمة الشحن الحقيقية كل مرة عشان أختبر الـ OrderService؟**

لأ.

وهنا بيظهر دور Service Stub.

## الفكرة والحل

**Service Stub هو بديل محلي (Local Substitute) بيحاكي سلوك Service حقيقية، بحيث تقدر تتعامل معاه بدل ما تتصل بالخدمة الحقيقية.**

بمعنى أبسط:

بدل ما الاختبار يتصل بشركة الشحن الحقيقية، هنعمل Implementation بديلة ترجع لنا نتائج متحكم فيها.

**بدون Service Stub**

OrderService

Real Shipping Service

(Network dependency)

External Shipping API

---

**باستخدام Service Stub**

OrderService

**Shipping Service Stub**

(Local substitute)

Controlled responses

مفيش اتصال بالشركة الخارجية أثناء الاختبار

لاحظ إن الـ Stub مش بيغير الـ Business Logic بتاعة OrderService.

هو بيغير الـ Dependency اللي بنحقنها فيه.

## مثال

هنبدأ بتعريف Interface مشترك للخدمة الحقيقية والـ Stub.

```python
from abc import ABC, abstractmethod

class ShippingService(ABC):

    @abstractmethod
    def calculate_shipping(self, address, weight):
        pass
```

### 1. Real Implementation

```python
class RealShippingService(ShippingService):

    def calculate_shipping(self, address, weight):
        # Call external shipping API
        return 100
```

### 2. Stub Implementation

```python
class ShippingServiceStub(ShippingService):

    def calculate_shipping(self, address, weight):
        return 20
```

### 3. OrderService

```python
class OrderService:

    def __init__(self, shipping_service):
        self.shipping_service = shipping_service

    def checkout(self, order):
        shipping_cost = self.shipping_service.calculate_shipping(
            order.address,
            order.weight
        )

        return order.total + shipping_cost
```

### 4. استخدام الـ Stub في الاختبار

```python
class Order:
    def __init__(self, address, weight, total):
        self.address = address
        self.weight = weight
        self.total = total

stub = ShippingServiceStub()

order_service = OrderService(stub)

order = Order(
    address="Cairo",
    weight=5,
    total=500
)

result = order_service.checkout(order)

assert result == 520
```

إيه اللي حصل؟

- OrderService مش عارف إذا كان بيتعامل مع Real Service أو Stub.
- الـ Stub رجّع 20 بدل ما يتصل بشركة الشحن.
- قدرنا نختبر الـ Business Logic من غير External Dependency.

### نقطة مهمة: هل الـ Stub لازم يرجع قيمة ثابتة؟

لأ. ممكن تتحكم في سلوكه حسب السيناريو اللي عايز تختبره.

مثلاً:

```python
class ShippingServiceStub(ShippingService):

    def __init__(self, shipping_cost):
        self.shipping_cost = shipping_cost

    def calculate_shipping(self, address, weight):
        return self.shipping_cost
```

وبالتالي:

```python
cheap_shipping = ShippingServiceStub(20)
expensive_shipping = ShippingServiceStub(100)
```

تقدر تختبر سيناريوهات مختلفة من غير ما تغير OrderService.

---

## أقرب GoF Pattern

هنا عندنا مقارنة مهمة مع **Proxy**.

**1. Proxy**

(أقرب GoF Pattern للمقارنة)

الـ Proxy هو Object بيقف كوسيط بين Client وReal Object، وبيتحكم في الوصول إليه.

مثلًا:

- Remote Proxy: يمثل Object موجود في مكان بعيد.
- Virtual Proxy: يؤجل إنشاء Object مكلف.
- Protection Proxy: يتحكم في صلاحيات الوصول.

**أوجه التشابه:**

- الاتنين ممكن يقدموا Object بنفس الواجهة اللي العميل متوقعها.
- الاتنين ممكن يخفوا تفاصيل التعامل مع خدمة أو Object آخر.
- العميل ممكن يتعامل معاهم من غير ما يعرف تفاصيل التنفيذ الداخلية.

**ليه Service Stub مش بديل لـ Proxy؟**

لأن الـ Proxy غالبًا بيكون وسيطًا للوصول إلى Real Object، بينما الـ Service Stub بيستبدل الخدمة الحقيقية بسلوك بديل متحكم فيه.

بمعنى:

- Proxy: ممكن يمرر الطلب للخدمة الحقيقية.
- Stub: ممكن يرجع Response محدد من غير ما يتصل بالخدمة الحقيقية أصلًا.
  ---
  **2. Null Object**
  (تشابه محدود في فكرة البديل)

Null Object بيوفر Object له سلوك محدد بدل التعامل مع None أو null.

Service Stub ممكن يرجع نتائج تمثل حالات معينة، لكن هدفه محاكاة خدمة حقيقية، مش توفير سلوك افتراضي لحالة غياب Object.

**ليه مش بديل عنه؟**

لأن Null Object بيعالج مشكلة التعامل مع غياب قيمة أو كائن، أما Stub بيعالج مشكلة الاعتماد على خدمة خارجية أثناء الاختبار أو التطوير.

### مقارنة سريعة

المقارنة	Service Stub	Proxy
الهدف	محاكاة Service	التحكم في الوصول إلى Object
هل يتصل بالـ Real Service؟	مش بالضرورة، وغالبًا لا	ممكن، حسب نوعه
الاستخدام الشائع	Testing / Development	Access Control / Remote Access / Lazy Loading
هل يمثل بديلًا حقيقيًا؟	نعم، أثناء الاستخدام المحدد	غالبًا وسيط للوصول

**ملحوظة:** Service Stub مش GoF Pattern، ومفيش نمط GoF مطابق ليه تمامًا.

---

## خامسًا: نفرّق بين Stub وMock وFake

دي نقطة مهمة لأن المصطلحات دي بتظهر كتير في Testing.

كلهم ممكن يكونوا أنواعًا من Test Doubles، لكن مش نفس الحاجة.

النوع	وظيفته
Stub	بيرجع Responses محددة مسبقًا
Mock	بيتيح التحقق من تفاعلات واستدعاءات متوقعة
Fake	Implementation بديلة شغالة، لكنها أبسط من الحقيقية

مثال سريع:

- Stub: تكلفة الشحن دائمًا 20.
- Mock: أتأكد إن calculate_shipping() اتندهت مرة واحدة.
- Fake: نظام شحن بسيط بيحسب التكلفة بناءً على الوزن، من غير الاتصال بالشركة الحقيقية.

المصطلحات دي أحيانًا بيختلف استخدامها بين مكتبات ومراجع الاختبار، لكن التمييز ده مفيد عمليًا.

---

## علاقته بالعمارة

Service Stub مش Architecture Pattern، لكنه ممكن يساعدك في اختبار أي Architecture تقريبًا.

- **Layered Architecture:** تستبدل External Service في الاختبارات.
- **Clean Architecture:** تستبدل الـ Outbound Adapter الحقيقي ببديل للاختبارات.
- **Hexagonal Architecture:** تقدم Adapter بديلًا للـ Port بدل الاتصال بالنظام الخارجي.

مثلاً في Clean Architecture:

```plain text
application/
    checkout_service.py
    ports/
        shipping_service.py

infrastructure/
    shipping/
        real_shipping_service.py

tests/
    stubs/
        shipping_service_stub.py
    test_checkout.py
```

الـ Stub هنا بيحقق نفس العقد (Contract) اللي الـ Application بيعتمد عليه.

## الخلاصة
Service Stub هدفه إنك تقدر تتعامل مع Service بديلة بدل الخدمة الحقيقية، خصوصًا لما تكون الخدمة الخارجية غير متاحة أو غير مناسبة للاختبار.

أقرب GoF Pattern للمقارنة هو:

- **Proxy:** لأن الاتنين ممكن يقدموا نفس الواجهة للـ Client ويخفوا تفاصيل التعامل.
- لكن Proxy هدفه التحكم في الوصول إلى Real Object، بينما Stub هدفه تقديم سلوك بديل متحكم فيه.

---


# Record Set

## المشكلة

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

## الفكرة والحل

**Record Set** هو Object بيمثل مجموعة من البيانات في شكل جدول داخل الذاكرة (In-Memory Tabular Data).

بمعنى إنه بيحتوي على:

- Columns: أسماء الأعمدة.
- Rows: الصفوف.
- Values: القيم الموجودة في كل خلية.

والـ Application يقدر يتعامل مع الـ Record Set بدون ما يحتاج يعرف تفاصيل الـ Database Driver اللي جاب البيانات.

## مثال

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

## أقرب GoF Pattern

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

## علاقته بالعمارة

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

## علاقته بالعمارة

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

## الخلاصة
Record Set بيحل مشكلة تمثيل نتائج البيانات الجدولية داخل الذاكرة بشكل موحد.

وأقرب GoF ليه من ناحية التشابه العملي هو Adapter، لكن مفيش GoF Pattern مكافئ له بشكل مباشر؛ لأن الهدف الأساسي مختلف.

وبكده اكتملت معانا قائمة الـ 11 Base Patterns في PoEAA.

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
