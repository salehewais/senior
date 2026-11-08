# أنماط التوزيع (Distribution Patterns)





# Remote Facade

## المشكلة

تخيل عندك E-Commerce Application، والـ Backend موجود على Server، والـ Frontend موجود على Server أو جهاز مختلف.

داخل الـ Backend عندك Order Object بالشكل ده:

```python
class Order:

    def get_customer(self):
        pass

    def get_items(self):
        pass

    def calculate_total(self):
        pass

    def validate(self):
        pass

    def confirm(self):
        pass
```

وعندك Customer وProduct وPayment Objects.

لو الـ Client حاول يتعامل مع كل Object بشكل مباشر عن طريق Remote Calls، ممكن يحصل الآتي:

```plain text
Client  --->  Order.get_customer()
Client  --->  Order.get_items()
Client  --->  Order.calculate_total()
Client  --->  Order.validate()
Client  --->  Order.confirm()
```

المشكلة إن كل استدعاء هنا ممكن يحتاج Network Round Trip.

يعني لو عندنا 5 عمليات، ممكن نحتاج 5 اتصالات بالشبكة.

وده يسبب:

- زيادة Latency.
- زيادة Network Overhead.
- اعتماد الـ Client على تفاصيل الـ Domain Objects الداخلية.
- صعوبة تغيير تصميم الـ Backend بدون التأثير على الـ Client.
- زيادة عدد Remote Interfaces اللي لازم تتعرض.

**إحنا محتاجين واجهة Remote بسيطة تخلي الـ Client يتعامل مع النظام من خلال عمليات أكبر وأوضح بدل التعامل المباشر مع تفاصيل الـ Objects الداخلية.**

## الفكرة والحل

فكرة **Remote Facade** إننا نعمل واجهة مركزية تعرض مجموعة من العمليات ذات المستوى الأعلى للـ Remote Client.

الـ Facade يستقبل طلبًا واحدًا، وبعد كده يتعامل مع الـ Objects الداخلية وينسق تنفيذ العمليات المطلوبة.

بدل ما الـ Client يتواصل مع كل Object، يتعامل مع Facade واحد.

**Without Remote Facade**

```plain text
Remote Objects  <---  Network Calls  <---  Client
```

---

**With Remote Facade**

```plain text
Domain Objects  <---  Remote Facade  <---  Client
```

في الرسم، الـ Client موجود أقصى اليمين، والطلب يتحرك ناحية الشمال.

يعني بدل ما الـ Client يطلب خمس عمليات منفصلة، ممكن يستدعي عملية واحدة:

```python
order_service.confirm_order(order_id)
```

والـ Remote Facade يتولى التنسيق داخليًا.

## مثال

هنبني مثال مبسط باستخدام Facade عادي، وبعدها نوضح إزاي نخليه Remote.

### أولًا: الـ Domain Objects

```python
class Order:

    def __init__(self, order_id, total):
        self.id = order_id
        self.total = total
        self.confirmed = False

    def validate(self):
        return self.total > 0

    def confirm(self):
        if not self.validate():
            raise ValueError("Invalid order")

        self.confirmed = True
```

### ثانيًا: Remote Facade

```python
class OrderRemoteFacade:

    def __init__(self, repository):
        self.repository = repository

    def confirm_order(self, order_id):

        order = self.repository.get(order_id)

        if order is None:
            raise ValueError("Order not found")

        order.confirm()

        self.repository.save(order)

        return {
            "order_id": order.id,
            "status": "confirmed"
        }
```

### ثالثًا: الـ Client

```python
response = remote_facade.confirm_order(101)

print(response)
```

الناتج:

```python
{
    "order_id": 101,
    "status": "confirmed"
}
```

لاحظ إن الـ Client مش محتاج يعرف:

- إزاي نجيب Order من Repository.
- إزاي نتحقق من صحة الطلب.
- إزاي ننفذ Confirmation.
- إزاي نحفظ التعديلات.

كل ده مخفي خلف Remote Facade.

**ملاحظة مهمة:** الكود السابق يوضح تصميم الـ Facade، لكنه مش Remote فعليًا بمفرده. عشان يبقى Remote Facade لازم نعرضه من خلال وسيلة اتصال شبكية، زي HTTP API أو RPC.

## أقرب GoF Pattern

هنا عندنا تشابه واضح مع GoF Facade.

Facade.

لكن هل هما نفس النمط؟

**مش بالضبط.**

### GoF Facade

هدفه توفير واجهة بسيطة لنظام داخلي معقد، سواء النظام ده محلي أو داخل نفس الـ Process.

### Remote Facade

بيستخدم نفس فكرة الواجهة المبسطة، لكن في سياق Distributed System.

بالإضافة إلى تبسيط التعامل، بيهتم بمشاكل الاتصال عن بُعد وتقليل Network Calls.

المقارنة	GoF Facade	Remote Facade
المشكلة	تعقيد Subsystem	تعقيد التواصل مع Remote System
الاتصال	غالبًا محلي	عبر Network
الهدف	تبسيط Interface	تبسيط Remote Interface وتقليل الاتصالات
Network Latency	مش جزء أساسي	اعتبار أساسي

إذًا Remote Facade مستوحى من GoF Facade، لكنه متخصص في سياق التوزيع.

## 5. علاقته بـ Application Architecture

Remote Facade مش بديل عن Layered Architecture أو Clean Architecture.

هو Pattern بنستخدمه عند حدود التواصل بين نظامين أو بين Remote Client والـ Server.

مثلًا داخل Layered Architecture:

```plain text
              Remote Client
                    |
                    ↓
              Remote Facade
                    |
                    ↓
             Application Layer
                    |
                    ↓
               Domain Layer
                    |
                    ↓
             Infrastructure
```

وبالاتجاه من اليمين للشمال:

```plain text
Infrastructure  <---  Domain  <---  Application Layer  <---  Remote Facade  <---  Remote Client
```

الـ Remote Facade بيكون نقطة دخول للطلبات القادمة من خارج التطبيق، وبعدها يوجهها للـ Application Layer.

## علاقته بالعمارة

هنا العلاقة مهمة جدًا.

في Clean Architecture، ممكن نعتبر Remote Facade جزءًا من الـ Inbound Adapters أو واجهة الـ Delivery.

مثلًا:

```plain text
Domain  <---  Use Case  <---  Remote Facade  <---  HTTP / RPC  <---  Client
```

لكن خلي بالك:

Remote Facade مش هو Use Case.

- Remote Facade: يستقبل Remote Request ويحولها لاستدعاءات مناسبة.
- Use Case: ينفذ عملية التطبيق.
- Domain: يحتوي على Business Rules.

والـ Domain لا يعرف أي حاجة عن HTTP أو RPC أو Remote Facade.

## 7. علاقته بـ DDD

ممكن نستخدم Remote Facade كواجهة خارجية للتعامل مع Domain Model.

تخيل إن عندك Order Aggregate، ومش عايز الـ Client يتعامل مع تفاصيله الداخلية.

بدل ما تعرض الـ Aggregate بالكامل، توفر عمليات واضحة:

```python
confirm_order(order_id)
cancel_order(order_id)
get_order_summary(order_id)
```

الـ Remote Facade يستدعي Application Services أو Use Cases، وهي بدورها تتعامل مع الـ Aggregates.

وده مهم لأنك مش عايز Remote Client يقدر يعدل أجزاء داخلية من الـ Aggregate بطريقة تتجاوز Invariants.

لكن متخلطش بين Remote Facade وDDD Application Service؛ الأول مسؤول عن الواجهة البعيدة، والثاني مسؤول عن تنسيق عملية التطبيق.

## علاقته بأودو

تخيل عندك Odoo ERP وMobile Application منفصل.

بدل ما الموبايل يحتاج ينفذ عدة Requests للوصول إلى تفاصيل Order، ممكن توفر Endpoint واحد:

```python
@http.route(
    "/api/orders/confirm",
    type="json",
    auth="user",
    methods=["POST"]
)
def confirm_order(self, order_id):

    order = request.env["sale.order"].browse(order_id)

    order.action_confirm()

    return {
        "order_id": order.id,
        "status": order.state,
    }
```

ده مثال قريب من Remote Facade؛ لأنه بيوفر عملية أعلى مستوى بدل ما يكشف تفاصيل النظام الداخلية.

لكن مجرد وجود Odoo Controller مش معناه تلقائيًا إنه Remote Facade. لازم يكون دوره فعلًا تجميع العمليات وتوفير واجهة Remote مستقرة ومبسطة.

## 9. إمتى نستخدم Remote Facade؟

استخدمه لما:

- عندك Remote Clients محتاجين يتعاملوا مع Backend معقد.
- عايز تقلل Network Round Trips.
- عايز تخفي تفاصيل Domain Objects الداخلية.
- عايز توفر API مستقرة رغم تغيير التصميم الداخلي.
- عندك عمليات تتكون من عدة خطوات داخلية ويمكن تنفيذها من خلال طلب واحد.

لكن خد بالك: تجميع العمليات في Request واحد لا يعني إنك تحط كل عمليات النظام في Facade واحد ضخم. لازم تقسيم المسؤوليات يفضل واضح.

---

## الخلاصة
**Remote Facade**

- يوفر واجهة Remote بسيطة.
- يخفي تعقيد الـ Objects الداخلية.
- يقلل عدد Network Round Trips.
- مستوحى من GoF Facade لكنه متخصص في Distributed Systems.
- يمكن استخدامه كـ Inbound Adapter في Clean Architecture.
- لا يساوي Application Service أو API Gateway.

**النمط التالي: Data Transfer Object (DTO).**

وده هيكمل الصورة؛ لأننا عرفنا إزاي نوفر واجهة Remote للعمليات، ولسه محتاجين نفهم إزاي ننقل البيانات نفسها بكفاءة بين الأنظمة.


# Data Transfer Object

في النمط السابق **Remote Facade**، اتكلمنا عن توفير واجهة Remote تقلل عدد الاتصالات بين الـ Client والـ Server.

لكن فيه سؤال مهم:

**لما الـ Client يستدعي Remote Facade، هننقل البيانات بين الطرفين إزاي؟**

هل ننقل الـ Domain Objects نفسها؟ ولا ننقل مجموعة بيانات بسيطة مخصصة لعملية النقل؟

هنا بيظهر دور **Data Transfer Object (DTO)**.

## المشكلة

تخيل عندك Order Object داخل الـ Backend:

```python
class Order:

    def __init__(self, order_id, customer, items):
        self.id = order_id
        self.customer = customer
        self.items = items

    def calculate_total(self):
        return sum(
            item.price * item.quantity
            for item in self.items
        )

    def confirm(self):
        # Business rules
        pass
```

الـ Order ده مش مجرد بيانات، ده كمان يحتوي على Business Behavior.

لو حاولنا نرسل الـ Object نفسه إلى Remote Client، هنواجه مشاكل:

1. الـ Client ممكن يحتاج بيانات معينة فقط من الـ Object.
1. ممكن يكون الـ Object مرتبطًا بـ Objects أخرى كثيرة.
1. ممكن يحتوي على Methods وBehavior مش محتاجين ننقلها.
1. ممكن نكشف تفاصيل داخلية من الـ Domain Model.
1. Serialization للـ Object المعقد ممكن تكون صعبة.
1. ممكن نحتاج Network Calls إضافية لجلب كل جزء من البيانات.

مثلًا لو الموبايل محتاج يعرض ملخص الطلب، فهو مش محتاج يعرف كل تفاصيل الـ Order Aggregate.

إحنا محتاجين شكل بسيط من البيانات يكون مخصصًا للنقل.

## الفكرة والحل

فكرة **Data Transfer Object** إننا ننشئ Object يحتوي على مجموعة من البيانات المطلوبة للنقل بين العمليات أو الأنظمة.

الـ DTO غالبًا بيكون عبارة عن Fields وبدون Business Logic.

بدل ما ننقل Domain Object بالكامل، بنحول البيانات المطلوبة إلى DTO ونرسله للطرف الآخر.

**DTO Flow**

**Remote Client**

**Data Transfer Object**

Serializable data structure

**Remote Server**

وبالاتجاه من اليمين للشمال:

```plain text
Remote Server  <---  DTO  <---  Remote Client
```

الـ DTO ممكن ينتقل بصيغة JSON أو XML أو غيرها.

## مثال

هنبني مثال Order Summary.

### أولًا: Domain Object

```python
class Order:

    def __init__(self, order_id, customer, items):
        self.id = order_id
        self.customer = customer
        self.items = items

    def calculate_total(self):
        return sum(
            item["price"] * item["quantity"]
            for item in self.items
        )
```

الـ Domain Object عنده بيانات وسلوك.

### ثانيًا: إنشاء DTO

```python
from dataclasses import dataclass

@dataclass
class OrderDTO:

    order_id: int
    customer_name: str
    total: float
    status: str
```

لاحظ إن الـ DTO لا يحتوي على Business Rules.

هو مجرد شكل منظم للبيانات اللي عايزين ننقلها.

### ثالثًا: تحويل Domain Object إلى DTO

```python
def to_order_dto(order):

    return OrderDTO(
        order_id=order.id,
        customer_name=order.customer,
        total=order.calculate_total(),
        status="confirmed"
    )
```

### رابعًا: إرسال البيانات

```python
from dataclasses import asdict
import json

order = Order(
    order_id=101,
    customer="Saleh",
    items=[
        {"price": 100, "quantity": 2},
        {"price": 200, "quantity": 1},
    ]
)

dto = to_order_dto(order)

payload = json.dumps(asdict(dto))

print(payload)
```

الناتج:

```json
{
    "order_id": 101,
    "customer_name": "Saleh",
    "total": 400,
    "status": "confirmed"
}
```

إيه اللي حصل؟

1. عندنا Domain Object داخل الـ Server.
1. اخترنا البيانات المطلوبة للنقل.
1. حولناها إلى DTO.
1. عملنا Serialization إلى JSON.
1. بقى عندنا Payload قابل للإرسال عبر Network.

**ملحوظة:** Serialization مش هو DTO نفسه؛ الـ DTO هو هيكل البيانات، أما Serialization فهي عملية تحويله إلى صيغة قابلة للنقل أو التخزين.

## 4. هل DTO لازم يكون Read Only؟

مش شرط.

DTO ممكن يستخدم في اتجاهين:

**Server → Client**

مثلًا إرسال Order Details.

**Client → Server**

مثلًا استقبال بيانات إنشاء Order.

مثال:

```python
@dataclass
class CreateOrderDTO:

    customer_id: int
    product_id: int
    quantity: int
```

الـ Client يرسل البيانات دي للـ Server.

بعد كده الـ Server يحولها إلى Command أو Input Model مناسب للعملية.

لكن خلي بالك: استقبال DTO لا يعني الثقة في بياناته. لازم نعمل Validation وAuthorization ونطبق Business Rules داخل التطبيق والـ Domain.

## أقرب GoF Pattern

هل DTO له GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern مطابق له.**

لكن ممكن تلاحظ تشابهات مع بعض الأنماط.

### 1. Value Object

فيه تشابه لأن DTO غالبًا بيكون Object بسيط يحمل بيانات، وممكن يكون Immutable.

لكن الفرق:

- **Value Object:** يمثل قيمة لها معنى داخل نموذج المجال، وتهمنا خصائصها وقيمتها.
- **DTO:** يمثل بيانات مخصصة للنقل بين حدود النظام.

مثلًا:

```python
@dataclass(frozen=True)
class Money:
    amount: float
    currency: str
```

ده ممكن يكون Value Object داخل الـ Domain.

أما:

```python
@dataclass
class OrderDTO:
    order_id: int
    total: float
```

ده DTO مخصص للنقل.

إذًا مش كل DTO هو Value Object، ومش كل Value Object هو DTO.

### 2. Transfer Object

ممكن تلاقي اسم Transfer Object في مراجع أخرى، وهو قريب جدًا من DTO.

لكن في GoF الأصلي مفيش Pattern بالاسم ده.

## 6. الفرق بين DTO وRemote Facade

دي نقطة مهمة لأن النمطين بيكملوا بعض.

المقارنة	Remote Facade	DTO
المسؤولية	توفير واجهة للعمليات البعيدة	نقل البيانات
يمثل	Operations	Data
مثال	confirm_order()	OrderDTO
الهدف	تقليل Remote Calls وتبسيط الواجهة	نقل البيانات بكفاءة
العلاقة	يستخدم DTO غالبًا	ينتقل عبر Remote Facade

بمعنى آخر:

Remote Facade يحدد *إيه العمليات المتاحة*، والـ DTO يحدد *شكل البيانات التي تنتقل*.

ممكن نشوف الاثنين مع بعض:

```plain text
Remote Server
      |
      ↓
Remote Facade
      |
      ↓
OrderDTO
      |
      ↓
Network
      |
      ↓
Remote Client
```

وبالاتجاه من اليمين للشمال:

```plain text
Remote Client  <---  Network  <---  OrderDTO  <---  Remote Facade  <---  Remote Server
```

## 7. علاقته بـ Application Architecture

DTO مش Application Architecture Pattern مستقل.

هو نمط بيظهر عند حدود التواصل بين Layers أو Processes أو Systems.

مثلًا في Layered Architecture:

```plain text
Presentation Layer
        |
        ↓
Application Layer
        |
        ↓
Domain Layer
```

ممكن الـ Presentation Layer تستقبل DTO، وتحوله إلى Input Model، ثم تستدعي Application Layer.

وممكن Application Layer ترجع Output Data تتحول إلى DTO قبل إرسالها للـ Client.

لكن مهم: مش لازم كل Layer يكون ليها DTO خاص بيها. استخدام DTO بين Layers محلية أحيانًا يكون مجرد تعقيد غير ضروري.

## علاقته بالعمارة

هنا DTO مهم جدًا عند حدود الـ Adapters.

مثلًا:

```plain text
HTTP Response
      ↑
      |
Response DTO
      ↑
      |
Presenter
      ↑
      |
Use Case Output
      ↑
      |
Domain
```

وبالاتجاه من اليمين للشمال:

```plain text
HTTP Response  <---  Response DTO  <---  Presenter  <---  Use Case  <---  Domain
```

لكن خلي بالك من الفرق بين DTO وDomain Model.

الـ Domain لا يجب أن يعتمد على DTO خاص بـ HTTP أو Framework خارجي.

وممكن يكون عندنا أنواع مختلفة من DTOs:

- Request DTO.
- Response DTO.
- Event DTO.
- Integration DTO.

كل واحد له غرض مختلف حسب حدود التواصل.

## 9. علاقته بـ DDD

في DDD، DTO غالبًا بيستخدم عند حدود Application Layer أو Integration Layer.

مثلًا عندك Order Aggregate:

```python
class Order:

    def confirm(self):
        # Validate domain rules
        pass
```

مش المفروض نرسل الـ Aggregate نفسه للـ External System.

بدل كده نجهز DTO:

```python
@dataclass
class OrderConfirmationDTO:

    order_id: int
    customer_id: int
    total: float
```

وده بيساعدنا نحافظ على استقلالية الـ Domain Model.

لكن فيه نقطة مهمة:

**DTO مش هو Domain Event.**

- DTO هدفه نقل البيانات.
- Domain Event بيمثل حقيقة حصلت داخل الـ Domain.

ممكن Domain Event يتحول إلى Integration Event أو Event DTO قبل نشره لنظام خارجي، لكن المفاهيم مش متطابقة.

## علاقته بأودو

في Odoo، عند التعامل مع Mobile App أو External API، من الأفضل غالبًا نرجع بيانات منظمة بدل ما نكشف Recordsets أو تفاصيل ORM مباشرة.

مثال:

```python
@http.route(
    "/api/orders/<int:order_id>",
    type="json",
    auth="user"
)
def get_order(self, order_id):

    order = request.env["sale.order"].browse(order_id)

    if not order.exists():
        return {"error": "Order not found"}

    return {
        "id": order.id,
        "name": order.name,
        "partner": order.partner_id.name,
        "amount_total": order.amount_total,
        "state": order.state,
    }
```

الـ Dictionary هنا بيؤدي دور DTO في واجهة الـ API، رغم إننا مش عاملين Class باسم DTO.

وده مهم لأن:

- مش بنرسل Odoo Recordset نفسه.
- بنحدد البيانات اللي مسموح تظهر.
- بنفصل External API Contract عن تفاصيل ORM.
- نقدر نغير تفاصيل داخلية في Odoo بدون ما نكسر الـ Client طالما حافظنا على الـ Contract.

---

## 11. إمتى نستخدم DTO؟

استخدمه لما:

- بتنقل بيانات عبر Network.
- عندك Remote Facade أو API.
- عايز تفصل External Contract عن Domain Model.
- محتاج تتحكم في البيانات المكشوفة للـ Client.
- عندك Integration بين أنظمة مختلفة.
- محتاج تجميع بيانات من عدة Objects في Response واحدة.

لكن تجنب استخدام DTO لكل Object ولكل Method بدون سبب؛ كثرة التحويلات والـ Mapping ممكن تعمل Boilerplate كبير.

---

## الخلاصة النهائية لـ Distribution Patterns

## Distribution Patterns

**1. Remote Facade**

يوفر واجهة Remote مبسطة ويقلل عدد الاتصالات بين Client وServer.

---

**2. Data Transfer Object (DTO)**

ينقل مجموعة بيانات منظمة بين العمليات والأنظمة.

والعلاقة بينهم:

```plain text
Remote Client  <---  Network  <---  DTO  <---  Remote Facade  <---  Server
```

**ملاحظة تصنيفية:** النمطين دول هما النمطين الأساسيين تحت Distribution Patterns في خريطة Fowler التي ندرسها.

وبكده نكون خلصنا المجموعة دي. المجموعة التالية في خريطة PoEAA هي **Offline Concurrency Patterns**، ودي هتربطنا بموضوع الـ Concurrency والـ Transactions اللي اتكلمنا عنه قبل كده.

يلا بينا يا صاحبي 😂 نبدأ مجموعة جديدة من كتاب **Patterns of Enterprise Application Architecture (PoEAA)**، ودي من أهم المجموعات لأنها مرتبطة مباشرةً بالـ Transactions والـ Database والـ Concurrency.

# Offline Concurrency Patterns

## المشكلة

قبل ما ندخل في الأنماط، لازم نفهم معنى **Offline Concurrency**.

تخيل عندك نظام ERP، وفيه موظفين بيشتغلوا على نفس الـ Order.

- الموظف الأول فتح الطلب الساعة 10:00.
- الموظف الثاني فتح نفس الطلب الساعة 10:01.
- الموظف الأول عدّل الكمية وحفظ الساعة 10:05.
- الموظف الثاني عدّل السعر وحفظ الساعة 10:06.

المشكلة إن الموظف الثاني ممكن يحفظ نسخة قديمة من البيانات، وبالتالي يمسح تعديل الموظف الأول بدون ما يقصد.

وده اسمه **Lost Update Problem**.

طيب ليه بنسميها Offline Concurrency؟

لأن المستخدم ممكن يفتح البيانات ويشتغل عليها لفترة طويلة، بينما الـ Database Transaction نفسها مش مفتوحة طول الفترة دي.

يعني عندنا فرق بين:

**Database Transaction:**

- قصيرة نسبيًا.
- تبدأ وتنفذ عمليات وتنتهي بـ Commit أو Rollback.
- بتحمي مجموعة عمليات داخل حدود قاعدة البيانات.

**Business Transaction:**

- ممكن تبدأ لما المستخدم يفتح شاشة.
- تستمر دقائق أو ساعات.
- تشمل قراءة وتعديل ومراجعة وحفظ.
- ممكن تمر بعدة Database Transactions.

وده جوهر المشكلة: الـ Database مش هتفضل فاتحة Transaction واحدة طول فترة عمل المستخدم.

## خريطة المجموعة

في تصنيف Fowler، هنمشي على الأنماط الأربعة دي:

## Offline Concurrency Patterns

1. **Optimistic Offline Lock**
  اكتشاف التعارض عند الحفظ بدل منع المستخدمين من التعديل مسبقًا.
1. **Pessimistic Offline Lock**
  حجز البيانات لمستخدم واحد لمنع الآخرين من تعديلها في نفس الوقت.
1. **Coarse-Grained Lock**
  تحديد نطاق القفل ليشمل مجموعة من Objects المرتبطة.
1. **Implicit Lock**
  إخفاء تفاصيل إدارة الأقفال خلف آليات أو Components أخرى.

---
