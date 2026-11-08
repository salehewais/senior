# أنماط عرض الويب (Web Presentation Patterns)





# Model View Controller

## المشكلة

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

## الفكرة والحل

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

## مثال

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

## أقرب GoF Pattern

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

## الخلاصة

MVC نمط معماري لتنظيم Presentation، بينما Observer وStrategy أنماط تصميم ممكن تساعد في تنفيذه.

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

## علاقته بالعمارة

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

## علاقته بأودو

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


# Page Controller

نكمل في **Web Presentation Patterns**.

النمط ده يعتبر أبسط طريقة لتنظيم الـ Controllers في تطبيقات الويب، وهنفهم منه الفرق بين إن كل صفحة يكون ليها Controller مستقل، وبين وجود Controller مركزي للتطبيق كله.

## المشكلة

تخيل عندنا Web Application لإدارة المبيعات، وفيه الصفحات التالية:

- صفحة عرض المنتجات.
- صفحة تفاصيل المنتج.
- صفحة عرض الطلبات.
- صفحة تفاصيل الطلب.
- صفحة إنشاء طلب جديد.

كل صفحة محتاجة تستقبل HTTP Request، وتنفذ العمليات المناسبة، وترجع Response.

ممكن نعمل Controller واحد مسؤول عن كل الصفحات:

```python
class ApplicationController:

    def handle(self, request):
        if request.path == "/products":
            ...

        elif request.path == "/orders":
            ...

        elif request.path == "/orders/create":
            ...

        elif request.path == "/products/details":
            ...
```

مع زيادة الصفحات، الـ Controller هيكبر، وهيبقى مسؤول عن عمليات مختلفة وغير مترابطة بشكل كافٍ.

**السؤال: هل ممكن نخلي كل صفحة مسؤولة عن معالجة طلباتها بنفسها؟**

## الفكرة والحل

فكرة **Page Controller** إننا ننشئ Controller لكل صفحة ويب، أو لكل مجموعة صغيرة من العمليات المرتبطة بصفحة معينة.

يعني:

- ProductsPageController مسؤول عن صفحة المنتجات.
- OrdersPageController مسؤول عن صفحة الطلبات.
- CreateOrderController مسؤول عن إنشاء الطلب.

كل Controller يستقبل الطلبات الخاصة بالصفحة، ويحدد البيانات المطلوبة، وينسق تنفيذ العملية، ويرجع الـ Response المناسب.

**Page Controller Architecture**

**HTTP Requests**

**Products**

Page Controller

**Orders**

Page Controller

**Create Order**

Page Controller

**Application / Domain Logic**

**Data Access**

لاحظ إن كل صفحة لها Controller خاص بيها، لكن ممكن كل الـ Controllers يستخدموا نفس Application Services والـ Domain Objects.

## مثال

هنستخدم مثال من غير Framework.

### Products Page Controller

```python
class ProductsPageController:

    def __init__(self, product_repository):
        self.product_repository = product_repository

    def handle(self, request):
        products = self.product_repository.get_all()

        return render_template(
            "products.html",
            {"products": products}
        )
```

### Orders Page Controller

```python
class OrdersPageController:

    def __init__(self, order_repository):
        self.order_repository = order_repository

    def handle(self, request):
        orders = self.order_repository.get_all()

        return render_template(
            "orders.html",
            {"orders": orders}
        )
```

### Create Order Controller

```python
class CreateOrderController:

    def __init__(self, create_order_use_case):
        self.create_order_use_case = create_order_use_case

    def handle(self, request):
        order_data = request.form

        order = self.create_order_use_case.execute(
            order_data
        )

        return redirect(f"/orders/{order.id}")
```

لاحظ إن كل Controller عنده مسؤولية محددة.

لكن مش معنى كده إننا بنكرر Business Logic؛ لأن العمليات المشتركة ممكن تكون موجودة داخل Use Cases أو Domain Services.

## مثال

Django مثال مناسب لفهم Page Controller.

```python
from django.shortcuts import render
from .models import Product

def products_page(request):
    products = Product.objects.all()

    return render(
        request,
        "products.html",
        {"products": products}
    )
```

هنا الـ View Function مسؤولة عن معالجة Request الخاص بصفحة المنتجات.

وفي صفحة الطلبات:

```python
def orders_page(request):
    orders = Order.objects.all()

    return render(
        request,
        "orders.html",
        {"orders": orders}
    )
```

كل View Function مسؤولة عن صفحة أو عملية محددة.

لكن مهم: مصطلح View في Django لا يعني بالضرورة View في MVC؛ لأن Django يستخدم مصطلحاته الخاصة، وتصميمه أقرب إلى MTV.

## أقرب GoF Pattern

هل Page Controller له GoF Equivalent مباشر؟

**لا يوجد GoF Pattern مطابق له مباشرة.**

لكن فيه تشابه جزئي مع:

### Command

كل Page Controller ممكن يستقبل طلبًا وينفذ عملية محددة.

مثلًا:

```plain text
Create Order Request
        |
        ↓
CreateOrderController
        |
        ↓
CreateOrderUseCase
```

لكن الفرق:

- **Command:** يمثل طلب تنفيذ عملية في شكل Object مستقل.
- **Page Controller:** ينظم معالجة HTTP Requests المرتبطة بصفحة معينة.

ممكن Page Controller يستخدم Command داخليًا، لكن مش هو نفسه Command.

### Front Controller

وده التشابه الأهم اللي هنحتاج نفهم الفرق بينه وبينه في النمط التالي.

- Page Controller: Controller لكل صفحة أو مجموعة عمليات مرتبطة بها.
- Front Controller: مدخل مركزي يستقبل الطلبات ويوجهها للمعالجة المناسبة.

الاتنين ممكن يشتغلوا مع بعض، مش بالضرورة يكونوا بدائل لبعض.

## 6. الفرق بين Page Controller وMVC

خلينا نثبت نقطة مهمة:

**MVC بيحدد تقسيم المسؤوليات إلى Model وView وController.**

أما Page Controller بيحدد طريقة تنظيم الـ Controllers حسب صفحات الويب.

يعني ممكن تستخدم MVC، وتطبق Page Controller لتنظيم جزء الـ Controller.

```plain text
MVC
 |
 ├── Model
 ├── View
 └── Controller
        |
        ├── ProductsPageController
        ├── OrdersPageController
        └── CreateOrderController
```

إذًا Page Controller مش بديل عن MVC؛ هو نمط أكثر تحديدًا لتنظيم الـ Controller.

## 7. علاقته بـ Application Architecture وClean Architecture

Page Controller مش Application Architecture Pattern.

هو Web Presentation Pattern.

في Clean Architecture ممكن يكون الـ Controller مجرد Adapter يستقبل HTTP Request ويستدعي Use Case.

```plain text
HTTP Request
      |
      ↓
Page Controller
      |
      ↓
Application Use Case
      |
      ↓
Domain Model
```

وبالاتجاه من اليمين للشمال:

```plain text
Domain Model  <---  Application Use Case  <---  Page Controller  <---  HTTP Request
```

الـ Controller مش المفروض يمتلك Business Rules الخاصة بالمجال؛ دوره الأساسي استقبال الطلب والتنسيق مع الطبقات الداخلية.

## علاقته بأودو

في Odoo عندك مثال واضح:

```python
from odoo import http
from odoo.http import request

class ProductController(http.Controller):

    @http.route("/products", type="http", auth="user")
    def products(self):
        products = request.env["product.product"].search([])

        return request.render(
            "my_module.products_template",
            {"products": products}
        )
```

وعندك Controller آخر للطلبات:

```python
class OrderController(http.Controller):

    @http.route("/orders", type="http", auth="user")
    def orders(self):
        orders = request.env["sale.order"].search([])

        return request.render(
            "my_module.orders_template",
            {"orders": orders}
        )
```

ده قريب من فكرة Page Controller؛ لأن كل Controller أو Handler مسؤول عن معالجة صفحة أو مجموعة Routes مرتبطة بوظيفة معينة.

لكن تقسيم Classes في Odoo مش هو معيار Fowler نفسه؛ الأهم هو مسؤولية الـ Controller عن معالجة الطلب المرتبط بصفحة أو Action.

---

## 9. المميزات والعيوب

**المميزات:**

- بسيط وسهل الفهم.
- كل صفحة لها مسؤولية واضحة.
- سهل الاختبار والتعديل.
- مناسب للتطبيقات الصغيرة والمتوسطة.
- يسمح بإعادة استخدام Application Logic بين الصفحات.

**العيوب:**

- ممكن يحصل تكرار بين Controllers.
- مع عدد صفحات كبير ممكن يزيد عدد الـ Controllers.
- بعض العمليات المشتركة تحتاج تنظيمًا إضافيًا.
- لا يوفر وحده إدارة مركزية للـ Request Processing.

## الخلاصة
**Page Controller**

- Controller لكل صفحة أو مجموعة عمليات مرتبطة بها.
- يستقبل HTTP Request.
- ينسق تنفيذ العملية.
- يجهز البيانات ويرجع Response.
- يمكن استخدامه داخل MVC وClean Architecture.
- لا يوجد GoF Equivalent مباشر.

**النمط التالي: Front Controller.**

وده مهم جدًا؛ لأنه هيجاوب عن سؤال: إيه اللي يحصل لو بدل ما كل Request يروح مباشرة إلى Page Controller، كل الطلبات تدخل الأول من نقطة مركزية واحدة؟


# Front Controller

نكمل في **Web Presentation Patterns** بنفس أسلوبنا.

النمط ده مرتبط جدًا بـ Page Controller، والفرق بينهم مهم لفهم تصميم Web Frameworks زي Django وOdoo وASP.NET وغيرها.

## المشكلة

في النمط السابق، شفنا إن كل صفحة ممكن يكون ليها Controller مستقل.

مثلًا:

- ProductsPageController
- OrdersPageController
- CustomersPageController
- LoginPageController

لكن تخيل إن عندك تطبيق كبير، وكل HTTP Request محتاج يمر بمجموعة عمليات مشتركة، زي:

- Authentication: التأكد من هوية المستخدم.
- Authorization: التحقق من الصلاحيات.
- Logging: تسجيل الطلبات.
- Error Handling: معالجة الأخطاء.
- Request Parsing: تجهيز بيانات الطلب.
- Routing: تحديد الـ Controller المناسب.

لو كل Page Controller نفذ العمليات دي بنفسه، هيحصل تكرار كبير.

**السؤال: هل ممكن يكون عندنا مدخل مركزي واحد يستقبل كل Requests، وينفذ العمليات المشتركة، وبعد كده يوجه كل Request للمعالجة المناسبة؟**

هنا بيظهر دور Front Controller.

## الفكرة والحل

فكرة **Front Controller** إننا نستخدم Controller مركزي يستقبل كل Requests الخاصة بالتطبيق، أو بمجموعة من وظائفه، وبعد كده يحدد المعالجة المناسبة ويوجه الطلب إليها.

بدل ما الطلب يروح مباشرة إلى Page Controller، هيعدي الأول على Front Controller.

**Page Controller vs Front Controller**

**Page Controller**

**HTTP Requests**

Products

Controller

Orders

Controller

Customers

Controller

---

**Front Controller**

**All HTTP Requests**

**Front Controller**

Authentication / Logging / Routing / Error Handling

Products

Handler

Orders

Handler

Customers

Handler

لاحظ إن الـ Front Controller مش شرط ينفذ كل العمليات بنفسه.

هو ممكن يفوض مسؤوليات معينة إلى Components متخصصة، وبعدها يوجه الطلب إلى الـ Handler المناسب.

## مثال

هنبني مثال مبسط من غير Framework.

### أولًا: Request

```python
class Request:

    def __init__(self, path, user):
        self.path = path
        self.user = user
```

### ثانيًا: Handlers

كل Handler مسؤول عن عملية معينة:

```python
class ProductsHandler:

    def handle(self, request):
        return "Products Page"

class OrdersHandler:

    def handle(self, request):
        return "Orders Page"
```

### ثالثًا: Front Controller

```python
class FrontController:

    def __init__(self):
        self.handlers = {
            "/products": ProductsHandler(),
            "/orders": OrdersHandler(),
        }

    def handle(self, request):

        # Authentication
        if request.user is None:
            return "401 Unauthorized"

        # Routing
        handler = self.handlers.get(request.path)

        if handler is None:
            return "404 Not Found"

        # Delegate request
        return handler.handle(request)
```

نجرب:

```python
front_controller = FrontController()

request = Request(
    path="/orders",
    user="Saleh"
)

response = front_controller.handle(request)

print(response)
```

الناتج:

```plain text
Orders Page
```

لاحظ تسلسل التنفيذ:

```plain text
HTTP Request
      |
      ↓
Front Controller
      |
      ├── Authentication
      |
      ├── Routing
      |
      ↓
Orders Handler
      |
      ↓
HTTP Response
```

وبالترتيب من اليمين للشمال:

```plain text
HTTP Response  <---  Orders Handler  <---  Front Controller  <---  HTTP Request
```

**ملاحظة:** المثال يوضح الفكرة فقط. في تطبيق حقيقي، Authentication وAuthorization وRouting غالبًا تكون مسؤوليات منفصلة، ومش لازم كلها تكون داخل Front Controller نفسه.

## أقرب GoF Pattern

هل Front Controller له GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern مطابق له بشكل مباشر.**

لكن عندنا تشابهات مع نمطين:

### 1. Chain of Responsibility

ممكن نستخدم Chain of Responsibility لمعالجة الطلب عبر مجموعة من المراحل.

مثلًا:

```plain text
HTTP Request
      |
      ↓
Authentication
      |
      ↓
Authorization
      |
      ↓
Logging
      |
      ↓
Routing
```

كل Handler ينفذ مسؤوليته، وبعدها يمرر الطلب للمرحلة التالية.

لكن الفرق:

- **Chain of Responsibility:** هدفه تمرير الطلب بين مجموعة Handlers حتى تتم معالجته.
- **Front Controller:** هدفه توفير مدخل مركزي لمعالجة Web Requests وتوجيهها.

ممكن Front Controller يستخدم Chain of Responsibility داخليًا، لكن مش هو نفسه.

### 2. Mediator

في Mediator، عندنا Object مركزي ينظم التواصل بين مجموعة Objects بدل ما تتواصل مباشرة مع بعضها.

وده فيه تشابه مع Front Controller لأنه بينظم تدفق الطلبات ويوجهها.

لكن:

- Mediator ينظم التواصل بين Components.
- Front Controller ينظم استقبال ومعالجة Web Requests.

إذًا التشابه في المركزية والتنسيق، لكن الـ Intent مختلف.

## 5. الفرق بين Front Controller وPage Controller

دي أهم مقارنة في النمط ده.

المقارنة	Page Controller	Front Controller
نقطة استقبال الطلب	Controller خاص بالصفحة	مدخل مركزي
عدد Controllers	متعددة حسب الصفحات	Front Controller مركزي مع Handlers
المعالجة المشتركة	ممكن تتكرر أو تتشارك	يمكن تجميعها في المدخل المركزي
التوجيه	غالبًا مباشر	مركزي
الاستخدام	صفحات وعمليات محددة	تطبيقات تحتاج معالجة مشتركة للطلبات

خلي بالك:

**Front Controller وPage Controller مش لازم يكونوا متعارضين.**

ممكن تستخدم Front Controller لاستقبال كل الطلبات، وبعدها يوجه كل طلب إلى Page Controller مناسب.

## 6. علاقته بـ Application Architecture

Front Controller هو Web Presentation Pattern، مش Application Architecture Pattern.

ممكن يكون جزءًا من Presentation Layer داخل Layered Architecture.

```plain text
              Web Application
                     |
                     ↓
              Presentation
                     |
                     ↓
              Front Controller
                     |
                     ↓
               Page Handler
                     |
                     ↓
              Application Layer
                     |
                     ↓
                Domain Layer
```

دوره هنا تنظيم مدخل الطلبات، مش امتلاك Business Logic.

## علاقته بالعمارة

هنا فيه علاقة مهمة.

في Clean Architecture، الـ Front Controller ممكن يكون جزءًا من الـ Infrastructure/Web Adapter، ويستدعي الـ Controllers أو Input Adapters المناسبة.

مثلًا:

```plain text
HTTP Request
      |
      ↓
Front Controller
      |
      ↓
Authentication / Routing
      |
      ↓
Input Adapter
      |
      ↓
Application Use Case
      |
      ↓
Domain
```

وبالاتجاه من اليمين للشمال:

```plain text
Domain  <---  Use Case  <---  Input Adapter  <---  Front Controller  <---  HTTP Request
```

لكن متخلطش بين Front Controller وInput Adapter.

- Front Controller مسؤول عن المدخل المركزي وتوجيه الطلبات.
- Input Adapter يحول مدخلات العالم الخارجي إلى الشكل الذي يتوقعه الـ Application.

ممكن يكونوا Component واحد في تطبيق بسيط، أو Components منفصلة في تطبيق أكبر.

## علاقته بأودو

في Odoo عندنا HTTP Request Lifecycle بيمر من خلال Framework Infrastructure مسؤولة عن استقبال الطلبات وتوجيهها إلى الـ Routes المناسبة.

مثلًا:

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

إحنا بنكتب Route Controller، لكن Odoo Framework هو اللي بيتولى استقبال HTTP Requests وإدارة Routing وRequest Lifecycle.

وده قريب من فكرة Front Controller على مستوى الـ Framework.

لكن مهم: مش معنى إن الـ Framework عنده Request Dispatcher مركزي إننا نقدر نصنف كل تفاصيل Odoo على إنها Fowler Front Controller حرفيًا من غير فحص التنفيذ.

ونفس الفكرة موجودة في Django؛ الـ URL Dispatcher والـ Middleware بيساهموا في تنظيم دورة الطلب، لكن كل جزء له مسؤولية مختلفة.

## 9. إمتى نستخدم Front Controller؟

يكون مفيد لما:

- عندك عدد كبير من HTTP Endpoints.
- عندك عمليات مشتركة محتاج تطبقها على الطلبات.
- عايز توحد معالجة الأخطاء والـ Routing.
- محتاج نقطة مركزية لإدارة Request Processing.
- عندك Web Framework أو Application يحتاج تنظيمًا واضحًا لدورة الطلب.

لكن خلي بالك من خطر مهم:

لو حطيت كل شيء داخل Front Controller، ممكن يتحول إلى **God Object** ضخم.

الحل إنك تفوض المسؤوليات إلى Middleware وAuthentication Services وRouter وHandlers متخصصة.

---

## الخلاصة
**Front Controller**

- مدخل مركزي يستقبل Web Requests.
- ينسق العمليات المشتركة ويوجه الطلبات.
- يفوض التنفيذ إلى Handlers متخصصة.
- لا يوجد GoF Equivalent مباشر.
- يمكن استخدام Chain of Responsibility وMediator كأدوات مساعدة في تنفيذه.
- يمكن استخدامه مع Page Controller.

**النمط التالي: Template View.**

وده هيغير تركيزنا من استقبال ومعالجة HTTP Requests إلى سؤال مختلف: إزاي نعرض البيانات داخل HTML بطريقة تفصل Presentation عن البيانات نفسها؟


# Template View

بعد ما اتكلمنا عن تنظيم استقبال الـ HTTP Requests باستخدام Front Controller، هننتقل لمشكلة مختلفة تمامًا: **إزاي نفصل شكل صفحة HTML عن البيانات اللي هنعرضها فيها؟**

وده جوهر نمط Template View.

## المشكلة

تخيل إن عندك صفحة بتعرض بيانات المنتجات.

ممكن تكتب HTML مباشرة داخل Python:

```python
def show_products(products):

    html = "<html><body>"

    for product in products:
        html += f"<h2>{product.name}</h2>"
        html += f"<p>{product.price}</p>"

    html += "</body></html>"

    return html
```

الكود ده شغال، لكن عندنا مشاكل:

1. خلطنا Business/Application Code مع HTML.
1. تعديل التصميم محتاج تعديل Python Code.
1. صعب إعادة استخدام أجزاء من التصميم.
1. صعب إن مصمم Frontend يشتغل على HTML بمعزل عن منطق التطبيق.
1. مع زيادة الصفحات، كود العرض هيكبر ويتكرر.

إحنا محتاجين نفصل مسؤولية تجهيز البيانات عن مسؤولية عرضها.

## الفكرة والحل

فكرة **Template View** إننا نكتب HTML Template يحتوي على أماكن مخصصة للبيانات الديناميكية.

وبعد كده نبعت الـ Template والبيانات إلى Template Engine، وهو المسؤول عن دمجهم وإنتاج HTML النهائي.

يعني بدل ما Python يبني HTML بنفسه، هو بيجهز البيانات فقط.

**Request Flow**

**HTML Response**

Final rendered page

**Template Engine**

Merges template with data

**HTML Template**

**Data**

**Application / Controller**

Prepares the data

وبنفس اتجاهنا من اليمين للشمال:

```plain text
HTML Response  <---  Template Engine  <---  (HTML Template + Data)
```

الفكرة الأساسية إن الـ Template مسؤول عن Presentation، والـ Application مسؤول عن تجهيز البيانات.

## مثال

هنستخدم Jinja2، وهو Template Engine مشهور في Python.

### أولًا: الـ Template

ملف templates/products.html:

```html
<html>
<body>

    <h1>Products</h1>

    {% for product in products %}

        <div>
            <h2>{{ product.name }}</h2>
            <p>{{ product.price }}</p>
        </div>

    {% endfor %}

</body>
</html>
```

لاحظ إن عندنا نوعين من العناصر:

- {{ }} لعرض قيمة.
- {% %} لتنفيذ تعليمات داخل الـ Template، زي Loop وCondition.

### ثانيًا: تجهيز البيانات

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader("templates")
)

template = env.get_template("products.html")

products = [
    {"name": "Laptop", "price": 1000},
    {"name": "Keyboard", "price": 100},
]

html = template.render(
    products=products
)

print(html)
```

الناتج النهائي:

```html
<html>
<body>

    <h1>Products</h1>

    <div>
        <h2>Laptop</h2>
        <p>1000</p>
    </div>

    <div>
        <h2>Keyboard</h2>
        <p>100</p>
    </div>

</body>
</html>
```

إيه اللي حصل؟

- Python جهز البيانات.
- HTML Template حدد شكل العرض.
- Jinja2 دمج الاثنين.
- النتيجة HTML جاهز للعرض.

**ملحوظة مهمة:** Template View مش معناه إن HTML لازم يكون خالي تمامًا من Logic؛ ممكن يحتوي على Loops وConditions بسيطة خاصة بالعرض. لكن Business Rules مش مكانها الـ Template.

## أقرب GoF Pattern

هل Template View هو نفسه Template Method؟

لا، لكن فيه تشابه في الاسم والفكرة العامة المتعلقة بالقوالب.

### Template Method

في GoF، Template Method بيحدد Skeleton لخوارزمية داخل Base Class، ويسمح للـ Subclasses بتغيير بعض الخطوات.

مثال:

```python
class Report:

    def generate(self):
        self.get_data()
        self.format_data()
        self.export()

    def get_data(self):
        pass

    def format_data(self):
        pass

    def export(self):
        pass
```

الـ Base Class بيحدد ترتيب تنفيذ الخوارزمية.

### Template View

أما Template View، فبيحدد شكل صفحة العرض، وبيستقبل بيانات ديناميكية لملء الأماكن المخصصة لها.

الفرق في الـ Intent:

- **Template Method:** إعادة استخدام هيكل خوارزمية مع إمكانية تغيير بعض خطواتها.
- **Template View:** فصل HTML Presentation عن البيانات التي سيتم عرضها.

إذًا مفيش GoF Equivalent مباشر.

## 5. علاقته بـ Application Architecture

Template View بيشتغل داخل Presentation Layer.

ممكن نستخدمه مع:

- MVC
- Layered Architecture
- Clean Architecture
- Page Controller
- Front Controller

مثلًا مع MVC:

```plain text
HTML Response  <---  Template View  <---  View
                                         ↑
                                         |
                                      Model Data
                                         ↑
                                         |
                                     Controller
```

الفكرة إن الـ Controller يجهز البيانات، والـ View يعرضها باستخدام Template.

Template View مش بديل عن MVC؛ هو طريقة لتنفيذ جزء العرض داخل MVC.

## علاقته بالعمارة

في Clean Architecture، الـ Template View يعتبر جزءًا من آلية تقديم البيانات للمستخدم، وبالتالي مكانه في الـ Outer Layers.

مثال:

```plain text
HTML Response
      ↑
      |
Template Engine
      ↑
      |
HTML Template
      ↑
      |
Presenter / View Adapter
      ↑
      |
Application Use Case
```

وبالترتيب من اليمين للشمال:

```plain text
HTML Response  <---  Template Engine  <---  HTML Template + View Data  <---  Presenter  <---  Use Case
```

لكن فيه نقطة مهمة:

الـ Use Case مش المفروض يعرف Jinja2 أو Django Templates أو أي Template Engine.

هو بيرجع نتيجة للتطبيق، والـ Presenter أو Adapter مسؤول عن تحويل النتيجة إلى شكل مناسب للعرض.

## 7. علاقته بـ DDD

العلاقة هنا بسيطة لكنها مهمة.

الـ Domain Model مسؤول عن قواعد العمل، وليس عن HTML.

مثلًا:

```python
class Order:

    def __init__(self, total):
        self.total = total

    def can_be_cancelled(self):
        return self.total > 0
```

الـ Domain يحدد هل الطلب قابل للإلغاء أم لا.

بعد كده الـ Application Layer يجهز البيانات اللازمة للعرض، والـ Template يعرضها.

**مينفعش نحط Business Rules داخل Jinja2 لمجرد إنها بتحدد إيه اللي يظهر للمستخدم.**

ممكن نعرض زر Cancel بناءً على قيمة can_cancel جهزها الـ Application، لكن قرار السماح بالإلغاء لازم يتحقق منه الـ Domain أو Application Logic عند تنفيذ العملية، مش مجرد إخفاء الزر.

## علاقته بأودو

Odoo بيستخدم QWeb Templates في Presentation.

مثال:

```xml
<template id="product_template">
    <t t-foreach="products" t-as="product">
        <div>
            <h2 t-esc="product.name"/>
            <p t-esc="product.list_price"/>
        </div>
    </t>
</template>
```

هنا:

- QWeb هو Template Engine.
- XML Template هو الـ Template.
- products هي البيانات.
- t-foreach مسؤولة عن تكرار العرض.
- t-esc تعرض القيمة مع escaping.

وده مثال واضح على Template View.

لكن خد بالك: QWeb مش مجرد HTML Template بسيط؛ عنده Directives وInheritance وآليات أخرى خاصة بـ Odoo.

## 9. إمتى نستخدم Template View؟

استخدمه لما:

- بتبني Server-Side Rendered Web Application.
- محتاج تفصل HTML عن Python.
- عندك صفحات متكررة في التصميم.
- عايز تعمل Reusable Components وTemplate Inheritance.
- عايز تسمح بتعديل Presentation بدون تعديل Application Logic.

ومن عيوبه إنك لو حطيت Logic كتير داخله، ممكن يتحول إلى مكان مليان Business Rules، وده يسبب صعوبة في الاختبار والصيانة.

---

## الخلاصة
**Template View**

- يفصل HTML عن Application Code.
- يستقبل Template وبيانات ديناميكية.
- يستخدم Template Engine لإنتاج HTML.
- لا يساوي GoF Template Method.
- يعمل داخل Presentation Layer.
- أمثلة: Jinja2 وDjango Templates وOdoo QWeb.

**النمط التالي: Transform View.**

وده مثير للاهتمام؛ لأنه بدل ما نستخدم Template ونملاه ببيانات، هنشوف طريقة تانية لتحويل بيانات التطبيق إلى Presentation باستخدام Transformation.


# Transform View

في النمط السابق **Template View**، كنا بنجهز HTML Template ونملأه بالبيانات باستخدام Template Engine.

لكن فيه طريقة تانية للتعامل مع Presentation، وهي إننا ناخد البيانات ونحوّلها مباشرةً إلى الشكل المطلوب للعرض.

وده جوهر **Transform View**.

## المشكلة

تخيل إن عندك Application بيرجع بيانات بالشكل ده:

```python
order = {
    "id": 101,
    "customer": "Saleh",
    "total": 1500,
    "status": "confirmed"
}
```

وعايز تعرض البيانات دي للمستخدم في صفحة HTML.

ممكن تستخدم Template View، لكن أحيانًا بيكون عندك احتياج مختلف:

- البيانات محتاجة تحويل كبير قبل العرض.
- عندك أكتر من شكل للـ Presentation.
- عايز تفصل طريقة تحويل البيانات عن منطق التطبيق.
- محتاج تحول البيانات إلى HTML أو XML أو صيغة Presentation أخرى.

المشكلة هنا مش مجرد ملء أماكن داخل HTML Template، لكن **تحويل مصدر البيانات إلى شكل Presentation كامل**.

## الفكرة والحل

فكرة Transform View إننا نستخدم Component مسؤول عن تحويل البيانات القادمة من التطبيق إلى Presentation Output.

بدل ما يكون عندنا Template يحتوي على أماكن للبيانات، بيكون عندنا Transformation Logic يحدد إزاي نحول البيانات إلى الناتج النهائي.

**Transform View Flow**

**Source Data**

Application Data

**Transform View**

Transformation Rules

**Presentation Output**

HTML / XML / Other Presentation Format

وبالاتجاه من اليمين للشمال:

```plain text
Presentation Output  <---  Transform View  <---  Source Data
```

الفرق الأساسي إن Transform View بيحوّل البيانات إلى الناتج، مش مجرد بيحطها داخل Template.

## مثال

هنفترض إن عندنا بيانات Order وعايزين نحولها إلى HTML.

### أولًا: مصدر البيانات

```python
order = {
    "id": 101,
    "customer": "Saleh",
    "total": 1500,
    "status": "confirmed"
}
```

### ثانيًا: Transform View

```python
from html import escape

class OrderTransformView:

    def render(self, order):

        status = escape(order["status"])

        status_color = (
            "green"
            if status == "confirmed"
            else "red"
        )

        return f"""
        <html>
            <body>
                <h1>Order #{order['id']}</h1>

                <p>Customer: {escape(order['customer'])}</p>

                <p>Total: {order['total']}</p>

                <p style="color:{status_color}">
                    Status: {status}
                </p>
            </body>
        </html>
        """
```

### ثالثًا: الاستخدام

```python
view = OrderTransformView()

html = view.render(order)

print(html)
```

الـ Transform View استقبل البيانات، وطبق عليها قواعد التحويل، وأنتج HTML كامل.

لاحظ إن المثال هنا توضيحي؛ في تطبيق حقيقي لازم نتحقق من صحة القيم ونتجنب إدخال بيانات غير موثوقة في HTML أو CSS.

## أقرب GoF Pattern

هل Transform View ليه GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern مطابق له بشكل مباشر.**

لكن ممكن نلاقي تشابهات جزئية:

### 1. Strategy

في Strategy، بنفصل خوارزمية ونقدر نبدل بينها.

مثلًا ممكن يكون عندنا:

- HTML Transformation
- XML Transformation
- PDF Transformation

وكل واحدة استراتيجية مختلفة لتحويل البيانات.

```python
class HtmlTransformer:

    def transform(self, data):
        return "<html>...</html>"

class XmlTransformer:

    def transform(self, data):
        return "<xml>...</xml>"

class ReportView:

    def __init__(self, transformer):
        self.transformer = transformer

    def render(self, data):
        return self.transformer.transform(data)
```

هنا استخدمنا Strategy لاختيار طريقة التحويل.

لكن:

- Strategy هدفه تبديل الخوارزميات.
- Transform View هدفه تحويل بيانات التطبيق إلى Presentation.

ممكن نستخدم Strategy لتنفيذ Transform View، لكن الاتنين مش نفس النمط.

### 2. Adapter

فيه تشابه من ناحية تحويل شكل البيانات إلى شكل آخر.

لكن Adapter هدفه التوفيق بين واجهتين غير متوافقتين، بينما Transform View هدفه إنتاج Presentation من بيانات التطبيق.

إذًا التشابه هنا في عملية التحويل فقط، مش في الـ Intent.

## 5. الفرق بين Template View وTransform View

دي أهم مقارنة في النمطين.

**Template View**

HTML Template

Data

Template Engine

**HTML Output**

---

**Transform View**

Source Data

Transformation Logic

**Presentation Output**

الفرق في الفكرة:

- **Template View:** عندك شكل جاهز (Template)، وبتملأه بالبيانات.
- **Transform View:** عندك بيانات، وبتحولها إلى شكل العرض المطلوب.

مش معنى كده إن Template View مفيهوش Transformation أو إن Transform View مينفعش يستخدم Templates مساعدة؛ المقصود هو اختلاف طريقة تنظيم مسؤولية العرض.

## 6. علاقته بـ Application Architecture

Transform View يعتبر Presentation Pattern.

ممكن تستخدمه داخل Layered Architecture أو MVC.

مثلًا:

```plain text
HTML Response  <---  Transform View  <---  Application Data  <---  Application Layer
```

الـ Application Layer يجهز البيانات، والـ Transform View يحولها إلى Presentation Output.

مش مطلوب من الـ Domain يعرف أي حاجة عن HTML أو XML.

## علاقته بالعمارة

في Clean Architecture، Transform View ممكن يكون جزءًا من الـ Presenter أو View Adapter في الطبقات الخارجية.

خلينا نفرق بين المسؤوليات:

- Use Case: ينفذ العملية ويرجع النتيجة.
- Presenter: يجهز شكل البيانات المناسب للعرض.
- Transform View: يحول البيانات إلى Presentation Output.

```plain text
HTML Response  <---  Transform View  <---  Presenter  <---  Use Case  <---  Domain
```

طبعًا ده تدفق توضيحي للنتيجة أثناء التنفيذ، مش اتجاه Dependency.

والـ Domain يفضل مستقل تمامًا عن طريقة العرض.

## 8. علاقته بـ DDD

في DDD، ممكن نستخدم Transform View لتحويل نتائج Application Layer إلى Presentation.

مثلًا عندك Domain Object:

```python
class Order:

    def __init__(self, order_id, total, status):
        self.id = order_id
        self.total = total
        self.status = status
```

مش ضروري تعرض الـ Domain Object نفسه مباشرة.

ممكن تعمل Projection أو View Model:

```python
def transform_order(order):

    return {
        "order_number": f"ORD-{order.id}",
        "total_label": f"${order.total}",
        "status_label": order.status.upper()
    }
```

وبعد كده تحول الـ View Model إلى HTML.

لكن خلي بالك: الـ Projection هنا مش هي نفسها Transform View؛ دي طريقة لتجهيز شكل البيانات، والـ Transform View مسؤولية تحويلها إلى Presentation.

## علاقته بأودو

في Odoo، عندنا أكثر من آلية لتحويل البيانات إلى Presentation.

مثلًا:

- QWeb Templates لعرض البيانات.
- Report Rendering لإنتاج تقارير PDF.
- Controllers لتحويل نتائج العمليات إلى HTTP Responses.

لكن لازم نفرق:

استخدام QWeb في Odoo أقرب مباشرةً إلى Template View، حتى لو كان فيه Expressions وعمليات تحويل داخل الـ Template.

أما لو عندك Component بياخد بيانات ويحولها إلى HTML أو XML أو صيغة تقرير، فممكن يكون قريبًا من فكرة Transform View.

مش كل عملية render() أو إنشاء PDF معناها تلقائيًا إننا بنطبق Fowler's Transform View؛ لازم نبص على تنظيم مسؤولية التحويل.

## 10. إمتى نستخدم Transform View؟

يكون مناسبًا لما:

- عندك Transformation Logic معقدة نسبيًا خاصة بالعرض.
- محتاج تفصل طريقة إنتاج Presentation عن Application Logic.
- عندك أكثر من Output Format.
- عايز تتحكم في تحويل البيانات دون وضع المسؤولية داخل الـ Domain أو Use Cases.

لكن لو الصفحة مجرد HTML ثابت نسبيًا مع قيم ديناميكية بسيطة، Template View غالبًا أبسط وأنسب.

---

## الخلاصة
**Transform View**

- يحول Source Data إلى Presentation Output.
- مسؤولية التحويل منفصلة عن Application Logic.
- لا يوجد GoF Equivalent مباشر.
- ممكن يستخدم Strategy أو Adapter كأدوات مساعدة.
- يختلف عن Template View في طريقة تنظيم عملية إنتاج العرض.

**النمط التالي: Two Step View.**

وده هيكمل معانا نفس الفكرة، لكن هيضيف خطوة وسيطة مهمة: بدل ما نحول البيانات مباشرةً إلى HTML النهائي، هنفصل إنتاج الشكل العام عن التفاصيل الخاصة بكل صفحة.


# Two Step View

وصلنا لنمط مهم جدًا في تنظيم عملية Presentation، وهو **Two Step View**.

في النمط السابق Transform View، كنا بنحول البيانات مباشرةً إلى Presentation Output.

لكن تخيل إن عندك تطبيق كبير فيه عشرات الصفحات والتقارير، وكلها لازم تلتزم بنفس التصميم العام:

- نفس Header.
- نفس Footer.
- نفس الألوان والخطوط.
- نفس طريقة عرض العناوين.
- نفس تنسيق الجداول.

لو كل صفحة بتنتج HTML كامل بنفسها، هتكرر نفس التصميم في أماكن كتير.

هنا بيظهر دور Two Step View.

## المشكلة

افترض عندك 3 صفحات:

- Products Report
- Orders Report
- Customers Report

كل صفحة عندها بيانات مختلفة، لكن التصميم العام واحد.

لو استخدمنا Transform View، ممكن كل واحدة تحول بياناتها إلى HTML كامل.

```plain text
Products Data  --->  Products HTML
Orders Data    --->  Orders HTML
Customers Data --->  Customers HTML
```

المشكلة إن كل صفحة هتحتاج تنفذ نفس قواعد التصميم.

وبالتالي:

1. تكرار Presentation Logic.
1. صعوبة تغيير التصميم العام.
1. اختلاف شكل الصفحات مع الوقت.
1. صعوبة الحفاظ على Consistent UI.

إحنا محتاجين نفصل بين حاجتين:

- تصميم الصفحة العام.
- التفاصيل الخاصة بكل صفحة.

## الفكرة والحل

فكرة Two Step View إننا نقسم عملية إنتاج الـ Presentation إلى مرحلتين.

**المرحلة الأولى:**

نحول البيانات إلى Logical Screen أو Intermediate Representation.

يعني نجهز شكلًا وسيطًا يحتوي على المعلومات اللي محتاجين نعرضها، بدون ربطها بالتصميم النهائي.

**المرحلة الثانية:**

ناخد الشكل الوسيط ونطبّق عليه Layout عام مسؤول عن التصميم المشترك، وننتج HTML النهائي.

**Two Step View**

**Source Data**

**Step 1: Logical Screen**

Page-specific presentation structure

**Step 2: Layout / Style**

Shared visual presentation

**Final HTML**

وبالاتجاه من اليمين للشمال:

```plain text
Final HTML  <---  Shared Layout  <---  Logical Screen  <---  Source Data
```

لاحظ إن عندنا مرحلتين منفصلتين فعلًا:

- الأولى تحدد *ماذا سنعرض؟*
- الثانية تحدد *كيف سيظهر؟*

## مثال

هنبني مثال بسيط لتقرير Orders.

### المرحلة الأولى: إنشاء Logical Screen

بدل ما ننتج HTML مباشرة، هنجهز Representation وسيط.

```python
def build_orders_screen(orders):

    return {
        "title": "Orders Report",
        "columns": ["Order", "Customer", "Total"],
        "rows": [
            [
                order["id"],
                order["customer"],
                order["total"]
            ]
            for order in orders
        ]
    }
```

البيانات:

```python
orders = [
    {
        "id": 101,
        "customer": "Saleh",
        "total": 1500
    },
    {
        "id": 102,
        "customer": "Ahmed",
        "total": 2000
    }
]

screen = build_orders_screen(orders)
```

الـ Logical Screen الناتج:

```python
{
    "title": "Orders Report",
    "columns": ["Order", "Customer", "Total"],
    "rows": [
        [101, "Saleh", 1500],
        [102, "Ahmed", 2000]
    ]
}
```

لاحظ إننا لسه ما حددناش ألوان أو Header أو Footer أو CSS.

إحنا جهزنا فقط المعلومات المنظمة الخاصة بالصفحة.

### المرحلة الثانية: تطبيق Shared Layout

دلوقتي عندنا Layout عام يقدر يعرض أي Logical Screen بنفس التصميم.

```python
from html import escape

def render_layout(screen):

    headers = "".join(
        f"<th>{escape(str(column))}</th>"
        for column in screen["columns"]
    )

    rows = ""

    for row in screen["rows"]:
        cells = "".join(
            f"<td>{escape(str(value))}</td>"
            for value in row
        )

        rows += f"<tr>{cells}</tr>"

    return f"""
    <html>
        <body>

            <header>
                <h1>My Company</h1>
            </header>

            <main>
                <h2>{escape(screen['title'])}</h2>

                <table>
                    <thead>
                        <tr>{headers}</tr>
                    </thead>

                    <tbody>
```

الاستخدام:

```python
html = render_layout(screen)
```

الآن عندنا فصل واضح:

- build_orders_screen: مسؤول عن تجهيز محتوى التقرير.
- render_layout: مسؤول عن التصميم العام وإنتاج HTML.

وممكن نستخدم نفس Layout مع Products Report أو Customers Report، طالما الـ Logical Screen ملتزم بنفس الشكل المتوقع.

المثال توضيحي مبسط لفكرة المرحلتين، وليس تنفيذًا كاملًا لمواصفات Fowler أو لمحرك Templates إنتاجي.

## أقرب GoF Pattern

هل Two Step View له GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern مطابق له مباشرةً.**

لكن فيه تشابهات تستحق نفهمها.

### 1. Builder

في Builder بنفصل عملية إنشاء Object معقد عن طريقة تمثيله النهائي.

وده قريب من فكرة إننا بنجهز Logical Screen في المرحلة الأولى.

لكن الفرق:

- Builder هدفه بناء Objects معقدة خطوة بخطوة.
- Two Step View هدفه فصل إعداد محتوى الشاشة عن تطبيق التصميم العام.

ممكن نستخدم Builder لبناء Logical Screen، لكن مش هو Two Step View نفسه.

### 2. Template Method

ممكن يكون عندنا Layout عام يحدد هيكل العرض، وكل نوع صفحة يحدد تفاصيله.

لكن Template Method قائم على وراثة وتخصيص خطوات Algorithm، بينما Two Step View قائم على مرحلتين منفصلتين لإنتاج Presentation.

**إذًا التشابهات دي أدوات تنفيذ محتملة، مش بدائل للنمط.**

## 5. الفرق بين Template View وTransform View وTwo Step View

خلينا نربط الثلاثة ببعض.

**Template View**

Template + Data

Template

Data

**Template Engine**

**HTML**

---

**Transform View**

Source Data

**Transformation**

**Presentation Output**

---

**Two Step View**

Source Data

**Step 1: Logical Screen**

**Step 2: Shared Layout**

**Final Presentation**

الفرق الجوهري:

- Template View: يدمج Template مع Data.
- Transform View: يحول Data إلى Presentation.
- Two Step View: يقسم التحويل إلى مرحلتين، محتوى الشاشة ثم التصميم العام.

## 6. علاقته بـ Application Architecture

Two Step View هو Presentation Pattern، وممكن نستخدمه داخل MVC أو Layered Architecture.

مثلًا:

```plain text
Final HTML
    ↑
    |
Shared Layout
    ↑
    |
Logical Screen
    ↑
    |
Controller / Presenter
    ↑
    |
Application Layer
```

وبالاتجاه من اليمين للشمال:

```plain text
Final HTML  <---  Shared Layout  <---  Logical Screen  <---  Presenter  <---  Application Layer
```

مش معنى وجود Logical Screen إننا أنشأنا Application Layer جديدة؛ دي مجرد مرحلة وسيطة في عملية العرض.

## علاقته بالعمارة

في Clean Architecture، ممكن نربط المرحلتين بالـ Output Boundary وPresenter.

مثلًا:

- Use Case ينفذ العملية.
- Output Boundary يحدد شكل النتيجة المطلوبة من التطبيق.
- Presenter يبني View Model أو Logical Screen.
- Web View أو Layout يحول الـ Representation إلى HTML.

لكن لازم نفرق بين مفاهيم Fowler وClean Architecture:

**Logical Screen في Two Step View مش بالضرورة هو نفسه View Model في Clean Architecture.**

فيه تقارب في الغرض، لكن المصطلحين جايين من سياقين مختلفين.

والأهم إن الـ Domain ما يعرفش أي حاجة عن Layout أو HTML.

## 8. علاقته بـ DDD

ممكن نستخدم Two Step View مع DDD بالشكل ده:

```plain text
Final HTML
    ↑
    |
Shared Layout
    ↑
    |
Logical Screen
    ↑
    |
Application Result
    ↑
    |
Domain
```

لكن الـ Logical Screen مش Domain Object.

مثلًا لو عندك Order Aggregate، مش المفروض الـ Aggregate يكون مسؤول عن تحديد:

- شكل الجدول.
- ترتيب الأعمدة.
- لون حالة الطلب.
- Header التقرير.

دي Presentation Responsibilities.

الـ Application Layer يجهز النتيجة، وبعدها Presentation Layer تتعامل مع تحويلها للشكل المناسب.

## علاقته بأودو

في Odoo، ممكن نلاحظ فصلًا مشابهًا في بعض أنظمة التقارير:

- Python يجهز البيانات.
- QWeb يحدد شكل التقرير.
- Report Layout يوفر تصميمًا مشتركًا.
- PDF Rendering ينتج الملف النهائي.

لكن لازم نكون دقيقين:

مجرد وجود QWeb Template وExternal Layout مش معناه إن كل تقارير Odoo تطبق Fowler's Two Step View حرفيًا.

النمط يكون أقرب عندما يكون عندنا فعلًا فصل بين Intermediate Presentation Structure وبين Layout النهائي، مش مجرد Template Inheritance.

---

## 10. إمتى نستخدم Two Step View؟

استخدمه لما:

- عندك صفحات أو تقارير كثيرة بتشارك نفس التصميم.
- محتاج توحد شكل الـ Presentation.
- محتاج تفصل محتوى الشاشة عن طريقة عرضه.
- عندك Presentation Logic معقدة نسبيًا ومحتاج تقسيمها لمراحل.

لكن لو عندك صفحة بسيطة، فغالبًا Template View كفاية، ومش محتاج تضيف مرحلة وسيطة تزيد التعقيد.

---

## الخلاصة
**Two Step View**

- يقسم إنتاج Presentation إلى مرحلتين.
- المرحلة الأولى: إنشاء Logical Screen.
- المرحلة الثانية: تطبيق Shared Layout.
- يساعد على توحيد التصميم وإعادة استخدامه.
- لا يوجد GoF Equivalent مباشر.
- يمكن استخدامه مع MVC وClean Architecture وDDD.

**النمط التالي والأخير في مجموعتنا: Application Controller.**

وده مهم جدًا؛ لأنه هيخلينا ننتقل من تنظيم عرض الصفحة نفسها إلى تنظيم **تدفق التنقل والتحكم في تنفيذ العمليات داخل التطبيق**.


# Application Controller

وصلنا لآخر نمط في مجموعة **Web Presentation Patterns** في خريطتنا.

النمط ده مهم؛ لأنه بيحل مشكلة مختلفة عن كل الأنماط السابقة.

إحنا اتكلمنا عن:

- Page Controller: مين يستقبل طلب الصفحة؟
- Front Controller: إزاي نوحد مدخل الطلبات؟
- Template View وTransform View وTwo Step View: إزاي ننتج الـ Presentation؟

لكن لسه فيه سؤال:

**مين المسؤول عن تحديد تسلسل خطوات التفاعل مع المستخدم، وتحديد الشاشة أو العملية التالية حسب حالة التطبيق؟**

هنا بيظهر دور Application Controller.

## المشكلة

تخيل عندك نظام E-Commerce، والمستخدم بيعمل Checkout.

عملية الـ Checkout فيها خطوات:

1. مراجعة المنتجات.
1. إدخال عنوان الشحن.
1. اختيار طريقة الدفع.
1. تأكيد الطلب.
1. عرض صفحة النجاح.

ممكن كل Controller يكون مسؤولًا عن الانتقال للخطوة التالية.

مثلًا:

```python
class CartController:

    def submit(self):
        # Validate cart
        # Redirect to address page
        pass

class AddressController:

    def submit(self):
        # Validate address
        # Redirect to payment page
        pass

class PaymentController:

    def submit(self):
        # Process payment
        # Redirect to confirmation page
        pass
```

في البداية ده يبدو طبيعيًا.

لكن تخيل إن عندك Workflows مختلفة حسب نوع المستخدم أو نوع الطلب:

- المستخدم بيدفع Online.
- المستخدم بيدفع عند الاستلام.
- الطلب محتاج موافقة إدارية.
- الطلب تابع لشركة لها خطوات إضافية.

هنا ممكن كل Controller يبدأ يعرف تفاصيل الـ Workflow، وتظهر مشاكل:

- تكرار منطق التنقل بين الصفحات.
- صعوبة تعديل ترتيب الخطوات.
- Controllers تصبح مرتبطة ببعضها.
- صعوبة إدارة Workflows مختلفة.
- توزيع قرار الخطوة التالية على أماكن كثيرة.

إحنا محتاجين Component مركزي مسؤول عن التحكم في تسلسل التفاعل مع التطبيق.

## الفكرة والحل

فكرة **Application Controller** إننا ننقل مسؤولية تحديد الخطوة التالية من الـ Page Controllers إلى Component مركزي مسؤول عن إدارة Application Flow.

بدل ما كل Controller يقرر بنفسه المستخدم يروح فين، الـ Application Controller هو اللي يحدد:

- العملية أو الشاشة المطلوبة.
- الـ Action المناسب.
- الـ View التي سيتم عرضها.
- الخطوة التالية بناءً على نتيجة العملية أو حالة التطبيق.

لاحظ إن Application Controller مش مسؤول عن تنفيذ Business Logic نفسه؛ هو مسؤول عن تنسيق تدفق التفاعل مع التطبيق.

**Application Controller Flow**

**User Action**

**Application Controller**

Decides what happens next

**Action / Use Case**

**Next View**

وبالاتجاه من اليمين للشمال:

```plain text
Next View  <---  Application Controller  <---  User Action
```

## مثال

هنرجع لمثال Checkout ونفترض إن عندنا طريقتين للدفع:

- Online Payment.
- Cash on Delivery.

بدل ما كل Controller يقرر الخطوة التالية، هنخلي Application Controller مسؤولًا عن القرار.

### أولًا: تعريف الـ Actions

```python
class CheckoutActions:

    def validate_cart(self):
        return True

    def process_online_payment(self):
        return True

    def confirm_cash_order(self):
        return True
```

### ثانيًا: Application Controller

```python
class CheckoutApplicationController:

    def __init__(self, actions):
        self.actions = actions

    def get_next_view(self, step, context):

        if step == "cart":
            return "address"

        if step == "address":
            if not context.get("address"):
                return "address"

            return "payment"

        if step == "payment":

            method = context.get("payment_method")

            if method == "online":
                success = self.actions.process_online_payment()

            elif method == "cash":
                success = self.actions.confirm_cash_order()

            else:
                return "payment"

            if success:
                return "confirmation"

            return "payment_error"

        return "not_found"
```

### ثالثًا: الاستخدام

```python
actions = CheckoutActions()

controller = CheckoutApplicationController(actions)

context = {
    "address": "Cairo",
    "payment_method": "online"
}

next_view = controller.get_next_view(
    step="payment",
    context=context
)

print(next_view)
```

الناتج:

```plain text
confirmation
```

إيه اللي حصل؟

1. المستخدم وصل لخطوة Payment.
1. Application Controller قرأ حالة العملية.
1. حدد طريقة الدفع.
1. طلب تنفيذ العملية المناسبة.
1. قرر الشاشة التالية بناءً على النتيجة.

لاحظ إن المثال مبسط، وفي تطبيق إنتاجي هنحتاج فصل تنفيذ الـ Use Cases عن قرار التنقل، ومعالجة الأخطاء والتحقق من صلاحيات الانتقال بين الخطوات.

## أقرب GoF Pattern

مفيش GoF Pattern مطابق تمامًا لـ Application Controller، لكن فيه تشابهات مهمة.

### 1. Command

في Command بنحول الطلب إلى Object مستقل يمثل عملية قابلة للتنفيذ.

مثلًا:

```python
class ProcessPaymentCommand:

    def __init__(self, amount):
        self.amount = amount

    def execute(self):
        print("Processing payment")
```

Application Controller ممكن يحدد أي Command يتم تنفيذه حسب حالة الـ Workflow.

الفرق:

- **Command:** Encapsulates an operation.
- **Application Controller:** يحدد العملية أو الخطوة التالية في تدفق التطبيق.

يعني ممكن Application Controller يستخدم Command، لكن مش بديل عنه.

### 2. State

في State Pattern، سلوك الـ Object بيتغير حسب حالته الداخلية.

مثلًا:

- Cart State.
- Address State.
- Payment State.
- Confirmation State.

ممكن نستخدم State لتنظيم سلوك كل مرحلة من مراحل Checkout.

لكن:

- **State:** ينظم السلوك المرتبط بالحالة.
- **Application Controller:** يدير تدفق التفاعل ويحدد الخطوة التالية.

ممكن نستخدم State لتنفيذ جزء من منطق Application Controller، لكن مش الاتنين نفس النمط.

### 3. Strategy

ممكن نستخدم Strategy لو عندنا طرق مختلفة لتنفيذ Workflow.

مثلًا:

- Standard Checkout.
- Corporate Checkout.
- International Checkout.

لكن Strategy مسؤول عن تبديل الخوارزميات، بينما Application Controller مسؤول عن التحكم في تدفق التطبيق.

## 5. الفرق بين Front Controller وApplication Controller

دي مقارنة مهمة جدًا؛ لأن الاسمين قريبين من بعض، لكن المسؤوليات مختلفة.

المقارنة	Front Controller	Application Controller
المسؤولية الأساسية	استقبال Web Requests	التحكم في Application Flow
نقطة التركيز	HTTP Request	User Interaction / Workflow
دوره	مدخل مركزي وتوجيه الطلب	تحديد العملية أو الشاشة التالية
مثال	استقبال /orders	تحديد الانتقال من Payment إلى Confirmation
علاقته بالـ Business Logic	لا ينفذها بنفسه	ينسق استدعاء العمليات ولا يمتلك قواعد العمل

خلينا نشوف الاتنين مع بعض:

```plain text
Confirmation View  <---  Application Controller  <---  Payment Handler  <---  Front Controller  <---  HTTP Request
```

الطلب يبدأ من اليمين:

1. Front Controller يستقبل HTTP Request.
1. يوجهه إلى Payment Handler.
1. Payment Handler يستدعي Application Controller.
1. Application Controller يحدد الخطوة التالية.
1. يتم عرض Confirmation View.

## الخلاصة

Front Controller يهتم بمدخل الطلب، أما Application Controller فيهتم بتدفق التفاعل داخل التطبيق.

## 6. علاقته بـ Application Architecture

Application Controller يعتبر Presentation Pattern في تصنيف Fowler، لكنه يتعامل مع مستوى أعلى من مجرد استقبال الطلب أو عرض الصفحة.

ممكن نستخدمه مع:

- MVC.
- Page Controller.
- Front Controller.
- Layered Architecture.

مثلًا:

```plain text
                Web Application
                       |
                       ↓
                Presentation
                       |
                       ↓
              Application Controller
                       |
                       ↓
                Page Controllers
                       |
                       ↓
               Application Layer
                       |
                       ↓
                  Domain Layer
```

وممكن في تصميم آخر يكون الـ Application Controller هو اللي ينسق مباشرةً مع Application Services بدل Page Controllers.

المهم هو فصل مسؤولية التحكم في تدفق التفاعل عن تنفيذ العمليات نفسها.

## علاقته بالعمارة

هنا لازم نكون دقيقين في توزيع المسؤوليات.

في Clean Architecture عندنا:

- Input Adapter: يستقبل مدخلات المستخدم ويحولها.
- Application Use Case: ينفذ عملية التطبيق.
- Presenter: يجهز نتيجة العملية للعرض.
- Application Controller: ينسق تدفق التفاعل ويحدد العملية أو العرض التالي.

ممكن يكون الشكل كالتالي:

```plain text
Next View  <---  Presenter  <---  Application Controller  <---  Input Adapter  <---  User Request
                                      |
                                      ↓
                                 Use Case
                                      |
                                      ↓
                                   Domain
```

لاحظ إن الرسم هنا يوضح تدفق التنفيذ بصورة مبسطة، مش Dependency Direction.

والنقطة المهمة:

**Application Controller مش هو Use Case Interactor.**

الـ Use Case مسؤول عن تنفيذ عملية محددة داخل التطبيق، أما Application Controller فيحدد إيه العملية أو الشاشة المناسبة في سياق التفاعل.

مثلًا:

- Application Controller يقرر إن المستخدم ينتقل إلى Payment.
- Payment Use Case ينفذ عملية الدفع.
- Domain يتحقق من قواعد العمل المرتبطة بالدفع.

## 8. علاقته بـ DDD

في DDD ممكن نستخدم Application Controller لتنظيم تدفق التفاعل بين المستخدم والتطبيق.

لكن لازم نفرق بين:

**Application Controller:**

- يحدد العملية التالية.
- ينسق الانتقال بين خطوات الـ Workflow.
- يختار الـ Use Case المناسب.

**Application Service:**

- ينفذ عملية على مستوى التطبيق.
- ينسق التعامل مع Domain Objects.
- يحدد حدود العملية والمعاملات حسب التصميم.

**Domain Model:**

- يحتوي على Business Rules.
- يحافظ على Invariants.
- لا يعرف أي شيء عن الصفحات أو التنقل بينها.

مثال: في عملية إنشاء Order، الـ Application Controller ممكن يقرر الانتقال لخطوة Payment، لكن هل الطلب صالح للتأكيد؟ دي مسؤولية قواعد العمل، مش الـ Application Controller.

## علاقته بأودو

في Odoo عندنا Controllers تستقبل Requests، وداخلها ممكن نستدعي Application Services أو Methods تنفذ عمليات مختلفة.

مثلًا:

```python
from odoo import http
from odoo.http import request

class CheckoutController(http.Controller):

    @http.route(
        "/checkout/payment",
        type="http",
        auth="user"
    )
    def payment(self, **kwargs):

        # Application operation
        order = request.env["sale.order"].browse(
            int(kwargs.get("order_id", 0))
        )

        if order.state == "sale":
            return request.redirect("/checkout/confirmation")

        return request.render(
            "my_module.payment_page",
            {"order": order}
        )
```

الكود ده فيه قرار متعلق بتدفق الصفحة، لكنه لا يعني بالضرورة إننا طبقنا Fowler's Application Controller.

لو عندنا Workflow كبير، ممكن نستخرج منطق التنقل واختيار الخطوات في Component مركزي بدل تكراره داخل Routes.

مثال واقعي: Checkout أو Approval Workflow أو Wizard متعدد المراحل.

لكن خلي بالك إن Odoo عنده بالفعل آليات Wizards وServer Actions وWorkflow-related logic، ووجودها لا يجعلها تلقائيًا تطبيقًا مطابقًا للنمط.

## 10. إمتى نستخدم Application Controller؟

يكون مفيدًا لما:

- التطبيق فيه Workflows متعددة الخطوات.
- ترتيب الشاشات بيتغير حسب حالة العملية.
- عندك أكثر من مسار لتنفيذ نفس العملية.
- منطق التنقل أصبح متكررًا بين Controllers.
- عايز تفصل التحكم في Application Flow عن تنفيذ Business Operations.

لكن لو عندك CRUD بسيط، وكل صفحة مستقلة، غالبًا مش محتاج Application Controller؛ لأنه ممكن يضيف تعقيدًا غير ضروري.

---

## الخلاصة النهائية لـ Web Presentation Patterns

كده خلصنا الأنماط السبعة اللي مشينا عليها في مجموعتنا.

## Web Presentation Patterns

1. **Model View Controller (MVC)**
  تقسيم مسؤوليات Presentation إلى Model وView وController.
1. **Page Controller**
  Controller لكل صفحة أو مجموعة عمليات مرتبطة.
1. **Front Controller**
  مدخل مركزي لاستقبال وتوجيه Web Requests.
1. **Template View**
  دمج Template مع Data لإنتاج Presentation.
1. **Transform View**
  تحويل Source Data إلى Presentation Output.
1. **Two Step View**
  فصل محتوى الشاشة عن التصميم العام على مرحلتين.
1. **Application Controller**
  تنظيم تدفق التفاعل وتحديد العملية أو الشاشة التالية.

**وأهم حاجة تخرج بيها من المجموعة دي:**

الأنماط دي مش Architecture بديلة لبعضها. ممكن تجمع أكثر من نمط في نفس التطبيق، لأن كل واحد بيحل مشكلة مختلفة في Web Presentation.

وبكده نكون انتهينا من **Web Presentation Patterns** حسب الخريطة اللي ماشيين عليها.

كمل بنفس الاسلوب دول من اليمين للشمال

## Distribution Patterns

تمام يا صاحبي 😂 نبدأ مجموعة جديدة من كتاب **Patterns of Enterprise Application Architecture (PoEAA)**.
