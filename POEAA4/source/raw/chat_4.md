---
title: مقارنة Separated Interface (4)
url: https://chatgpt.com/g/g-p-6aef8f7176848191b87a5d98247e8052-poeaa/c/6aef9680-517c-83ea-a8e4-58d462c81d41
h1s: ['2. Page Controller', '3. Front Controller', '4. Template View', '5. Transform View', '6. Two Step View', '7. Application Controller', 'Distribution Patterns', '1. Remote Facade', '6. Two Step View', '2. Data Transfer Object (DTO)', 'Offline Concurrency Patterns', '1. Optimistic Offline Lock', '10', '10', '2. Pessimistic Offline Lock', 'النمط الثالث: Coarse-Grained Lock', '3. Coarse-Grained Lock', 'User A locks Order 100', 'User B wants to update Line 1', 'النمط الرابع والأخير: Implicit Lock']
len: 106056
msgCount: 13
---

# 2. Page Controller

نكمل في **Web Presentation Patterns**.

النمط ده يعتبر أبسط طريقة لتنظيم الـ Controllers في تطبيقات الويب، وهنفهم منه الفرق بين إن كل صفحة يكون ليها Controller مستقل، وبين وجود Controller مركزي للتطبيق كله.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. مثال باستخدام Django

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

## 5. أقرب GoF Pattern

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

## 8. علاقته بـ Odoo

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


# 3. Front Controller

نكمل في **Web Presentation Patterns** بنفس أسلوبنا.

النمط ده مرتبط جدًا بـ Page Controller، والفرق بينهم مهم لفهم تصميم Web Frameworks زي Django وOdoo وASP.NET وغيرها.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. أقرب GoF Pattern

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

## 7. علاقته بـ Clean Architecture

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

## 8. علاقته بـ Odoo

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


# 4. Template View

بعد ما اتكلمنا عن تنظيم استقبال الـ HTTP Requests باستخدام Front Controller، هننتقل لمشكلة مختلفة تمامًا: **إزاي نفصل شكل صفحة HTML عن البيانات اللي هنعرضها فيها؟**

وده جوهر نمط Template View.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. أقرب GoF Pattern

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

## 6. علاقته بـ Clean Architecture

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

## 8. علاقته بـ Odoo

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


# 5. Transform View

في النمط السابق **Template View**، كنا بنجهز HTML Template ونملأه بالبيانات باستخدام Template Engine.

لكن فيه طريقة تانية للتعامل مع Presentation، وهي إننا ناخد البيانات ونحوّلها مباشرةً إلى الشكل المطلوب للعرض.

وده جوهر **Transform View**.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. أقرب GoF Pattern

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

## 7. علاقته بـ Clean Architecture

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

## 9. علاقته بـ Odoo

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


# 6. Two Step View

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

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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
                        {rows}
                    </tbody>
                </table>
            </main>

            <footer>
                Copyright 2026
            </footer>

        </body>
    </html>
    """
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

## 4. أقرب GoF Pattern

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

## 7. علاقته بـ Clean Architecture

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

## 9. علاقته بـ Odoo

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


# 7. Application Controller

وصلنا لآخر نمط في مجموعة **Web Presentation Patterns** في خريطتنا.

النمط ده مهم؛ لأنه بيحل مشكلة مختلفة عن كل الأنماط السابقة.

إحنا اتكلمنا عن:

- Page Controller: مين يستقبل طلب الصفحة؟
- Front Controller: إزاي نوحد مدخل الطلبات؟
- Template View وTransform View وTwo Step View: إزاي ننتج الـ Presentation؟

لكن لسه فيه سؤال:

**مين المسؤول عن تحديد تسلسل خطوات التفاعل مع المستخدم، وتحديد الشاشة أو العملية التالية حسب حالة التطبيق؟**

هنا بيظهر دور Application Controller.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. أقرب GoF Patterns

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

**الخلاصة:** Front Controller يهتم بمدخل الطلب، أما Application Controller فيهتم بتدفق التفاعل داخل التطبيق.

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

## 7. علاقته بـ Clean Architecture

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

## 9. علاقته بـ Odoo

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

# Distribution Patterns

قبل ما نبدأ، خلينا نفهم الأول المجموعة دي بتعالج مشكلة إيه.

## يعني إيه Distribution Patterns؟

لما يكون عندنا Application متقسم على أكثر من Process أو Machine، وعايزين الـ Components تتواصل مع بعضها عن طريق Network، بنواجه مشاكل مختلفة عن التواصل العادي داخل نفس البرنامج.

مثلًا تخيل عندك:

- Web Application.
- Application Server.
- Database Server.
- خدمة خارجية مسؤولة عن الدفع.

كل جزء ممكن يكون موجود في مكان مختلف، والتواصل بينهم بيتم عن طريق Network.

وده بيخلق تحديات:

1. Network Latency: الاتصال بالشبكة أبطأ من استدعاء Method داخل نفس البرنامج.
1. Network Failure: الاتصال ممكن يفشل.
1. Serialization: لازم نحول البيانات لصيغة قابلة للإرسال.
1. Remote Calls: استدعاء عملية على جهاز آخر مختلف عن استدعاء Method محلية.
1. Chatty Communication: كثرة الطلبات الصغيرة ممكن تسبب بطء شديد.

وهنا بييجي دور Distribution Patterns.

## خريطة المجموعة

في تصنيف Fowler هنركز على نمطين أساسيين:

## Distribution Patterns

1. **Remote Facade**
  توفير واجهة Remote بسيطة تقلل عدد الاتصالات وتخفي تعقيد النظام الداخلي.
1. **Data Transfer Object (DTO)**
  نقل مجموعة من البيانات بين العمليات أو الأنظمة في عملية اتصال واحدة.

---

# 1. Remote Facade

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. أقرب GoF Pattern

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

## 6. علاقته بـ Clean Architecture

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

## 8. علاقته بـ Odoo

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


# 6. Two Step View

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

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 4. أقرب GoF Pattern

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

## 7. علاقته بـ Clean Architecture

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

## 9. علاقته بـ Odoo

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


# 2. Data Transfer Object (DTO)

في النمط السابق **Remote Facade**، اتكلمنا عن توفير واجهة Remote تقلل عدد الاتصالات بين الـ Client والـ Server.

لكن فيه سؤال مهم:

**لما الـ Client يستدعي Remote Facade، هننقل البيانات بين الطرفين إزاي؟**

هل ننقل الـ Domain Objects نفسها؟ ولا ننقل مجموعة بيانات بسيطة مخصصة لعملية النقل؟

هنا بيظهر دور **Data Transfer Object (DTO)**.

## 1. المشكلة (Problem)

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

## 2. الفكرة والحل (Solution)

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

## 3. مثال عملي باستخدام Python

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

## 5. أقرب GoF Pattern

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

## 8. علاقته بـ Clean Architecture

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

## 10. علاقته بـ Odoo

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

## أولًا: نفهم المشكلة اللي المجموعة بتحلها

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

# 1. Optimistic Offline Lock

## 1. المشكلة (Problem)

نرجع لمثال الـ Order.

عندنا موظفين فتحوا نفس الطلب في نفس الوقت.

**سيناريو Lost Update**

الطلب رقم 101، والكمية الأصلية 10.

**الموظف الأول**

# 10

الكمية التي قرأها

يعدلها إلى 15

**الموظف الثاني**

# 10

الكمية التي قرأها

يعدلها إلى 20

---

**تسلسل الحفظ**

```plain text
Database  <---  Save: Quantity = 15  <---  Employee 1

Database  <---  Save: Quantity = 20  <---  Employee 2
```

(Lost Update)

التعديل الأول اختفى، وأصبحت الكمية 20 بدلًا من اكتشاف التعارض.

المشكلة إن الموظف الثاني مش عارف إن حد عدّل البيانات بعد ما قرأها.

إحنا محتاجين نكتشف إن البيانات اتغيرت قبل ما نسمح بالحفظ.

## 2. الفكرة والحل (Solution)

فكرة **Optimistic Offline Lock** إننا نفترض إن التعارضات مش بتحصل كثيرًا، وبالتالي نسمح لأكثر من مستخدم يقرأ ويعدل نفس البيانات بدون حجزها.

لكن عند الحفظ، نتحقق إن البيانات لم تتغير منذ لحظة قراءتها.

لو اتغيرت، نرفض الحفظ ونبلغ المستخدم بوجود Conflict.

أشهر طريقة لتنفيذ الفكرة هي استخدام **Version Number**.

كل Record عنده Version:

```plain text
Order ID = 101
Quantity = 10
Version  = 1
```

لما المستخدم يقرأ البيانات، يحتفظ بالـ Version اللي قرأه.

وعند الحفظ، نقارن الـ Version الحالي في قاعدة البيانات بالـ Version اللي المستخدم قرأه.

- لو متساويين: نسمح بالتعديل ونزيد Version.
- لو مختلفين: نرفض التعديل لأن فيه تغيير حصل بعد القراءة.

**Optimistic Offline Lock**

**قبل التعديل**

```plain text
Database Version = 1
User A Version   = 1
User B Version   = 1
```

---

**الموظف الأول يحفظ**

```plain text
Database Version = 1
User A Version   = 1

Update succeeds
Database Version = 2
```

(First Update Accepted)

---

**الموظف الثاني يحفظ**

```plain text
Database Version = 2
User B Version   = 1

2 != 1
```

(Concurrency Conflict)

النظام يرفض التعديل بدل ما يسمح بـ Lost Update.

وبالاتجاه من اليمين للشمال:

```plain text
Database  <---  Version Check  <---  Save Request  <---  User
```

## 3. مثال عملي باستخدام Python وSQL

هنستخدم Version Column.

### أولًا: تصميم الجدول

```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    quantity INTEGER NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);
```

البيانات:

```plain text
id | quantity | version
---|----------|--------
1  | 10       | 1
```

### ثانيًا: قراءة البيانات

```python
def get_order(cursor, order_id):

    cursor.execute(
        """
        SELECT id, quantity, version
        FROM orders
        WHERE id = %s
        """,
        (order_id,)
    )

    return cursor.fetchone()
```

المستخدم هيقرأ:

```python
{
    "id": 1,
    "quantity": 10,
    "version": 1
}
```

### ثالثًا: الحفظ مع التحقق من Version

```python
def update_order(
    cursor,
    order_id,
    new_quantity,
    expected_version
):

    cursor.execute(
        """
        UPDATE orders
        SET
            quantity = %s,
            version = version + 1
        WHERE
            id = %s
            AND version = %s
        """,
        (
            new_quantity,
            order_id,
            expected_version
        )
    )

    if cursor.rowcount == 0:
        raise Exception(
            "Concurrency Conflict"
        )
```

ركز في الجزء ده:

```sql
WHERE id = %s AND version = %s
```

إحنا مش بنعمل Update لمجرد إن الـ Record موجود.

إحنا بنعمل Update بشرط إن الـ Version ما زال هو نفسه اللي المستخدم قرأه.

والعملية كلها عبارة عن SQL Statement واحدة، وبالتالي التحقق والتعديل بيحصلوا بشكل Atomic على مستوى قاعدة البيانات.

### رابعًا: السيناريو

الموظف الأول:

```python
update_order(
    cursor,
    order_id=1,
    new_quantity=15,
    expected_version=1
)
```

النتيجة:

```plain text
quantity = 15
version  = 2
```

الموظف الثاني:

```python
update_order(
    cursor,
    order_id=1,
    new_quantity=20,
    expected_version=1
)
```

النتيجة:

```plain text
Concurrency Conflict
```

لأن Version الحالي أصبح 2، بينما الموظف الثاني بيحاول الحفظ باستخدام Version قديم وهو 1.

**ملحوظة مهمة:** لازم عملية التعديل تكون داخل Transaction، ولازم نتعامل مع Conflict بشكل مناسب، مثل إعادة تحميل البيانات ومراجعة التعديلات. مينفعش نعيد تنفيذ نفس التعديل القديم تلقائيًا بدون فهم أثره.

## 4. هل Version Number هي الطريقة الوحيدة؟

لا.

فيه أكثر من طريقة لتنفيذ Optimistic Locking:

1. **Version Number:** رقم يزيد مع كل تعديل.
1. **Timestamp:** مقارنة آخر وقت تعديل.
1. **Hash / Original Values:** مقارنة القيم القديمة بالقيم الحالية.

لكن Version Number غالبًا أوضح وأكثر أمانًا من الاعتماد على Timestamp، خصوصًا لو دقة الوقت أو تزامنه مش مضمونين.

## 5. أقرب GoF Pattern

هل Optimistic Offline Lock له GoF Equivalent مباشر؟

**لا، مفيش GoF Pattern مطابق له.**

لكن ممكن تلاحظ تشابهات جزئية:

### Observer

ممكن تستخدم Observer لإبلاغ المستخدم إن البيانات اتغيرت.

لكن الفرق:

- Observer هدفه نشر الإشعارات عند حدوث تغييرات.
- Optimistic Offline Lock هدفه منع الكتابة بناءً على نسخة قديمة.

### State

ممكن يكون عندك حالة للـ Record أو عملية الحفظ، مثل:

- Unchanged
- Modified
- Conflict

لكن State مش هو Optimistic Offline Lock.

الـ Optimistic Offline Lock آلية لإدارة التزامن والتحقق من صلاحية التعديل، وليس Behavioral Pattern من GoF.

## 6. علاقته بـ Application Architecture

Optimistic Offline Lock مش بديل عن Layered أو Clean Architecture.

هو Concurrency Pattern ممكن نستخدمه داخل أي Application Architecture تحتاج حماية التعديلات المتزامنة.

مثلًا:

```plain text
Database  <---  Repository  <---  Application Service  <---  Controller  <---  User
```

وقت الحفظ، الـ Repository أو Data Access Layer ينفذ عملية الـ Version Check والـ Conditional Update.

وممكن الـ Application Service يتعامل مع Conflict ويقرر إزاي يرجع النتيجة للمستخدم.

## 7. علاقته بـ Clean Architecture

في Clean Architecture ممكن يكون التنفيذ موزع كالتالي:

```plain text
Database  <---  Repository  <---  Use Case  <---  Input Adapter  <---  User
```

- Input Adapter يستقبل التعديل والـ Version المتوقع.
- Use Case ينسق عملية التحديث.
- Repository ينفذ الـ Conditional Update.
- Database تضمن Atomicity للشرط والتعديل.

لو حصل Conflict، الـ Repository يرجع نتيجة واضحة أو يرفع Exception مناسبة، والـ Use Case يحدد طريقة التعامل معها.

والـ Domain ممكن يحتوي على قواعد العمل، لكنه مش محتاج يعرف تفاصيل SQL أو كيفية تنفيذ Version Check.

## 8. علاقته بـ DDD

في DDD، ممكن نستخدم Optimistic Concurrency Control لحماية Aggregate من التعديل بناءً على نسخة قديمة.

تخيل إن عندك Order Aggregate.

موظفان حمّلا نفس الـ Aggregate، وكل واحد عمل تعديل مستقل.

عند حفظ الأول، يتغير الـ Version.

وعند محاولة حفظ الثاني، Repository يكتشف إن الـ Version اختلف ويرفض الحفظ.

ده مهم للحفاظ على **Aggregate Invariants** ومنع تعديل قديم من الكتابة فوق حالة أحدث.

لكن لازم نفرق بين:

- Version الخاص بالتزامن.
- Business Status الخاص بالـ Order.

مثلًا version = 5 مش معناه إن الطلب في الحالة الخامسة؛ ده مجرد رقم يمثل نسخة البيانات.

## 9. علاقته بـ Odoo وPostgreSQL

دي نقطة مهمة بالنسبة لطبيعة أنظمة ERP.

في PostgreSQL عندنا MVCC، وده بيسمح للـ Transactions بقراءة نسخ متسقة من البيانات حسب مستوى العزل.

لكن **MVCC مش هو نفسه Optimistic Offline Lock**.

الفرق:

- MVCC ينظم رؤية النسخ والتزامن على مستوى قاعدة البيانات.
- Optimistic Offline Lock يحمي Business Transaction طويلة نسبيًا من الكتابة فوق تعديلات مستخدم آخر.

يعني وجود MVCC مش معناه تلقائيًا إن عندك حماية كاملة من Lost Updates الناتجة عن تعديل المستخدم لنسخة قديمة.

في Odoo، لو عندك عملية طويلة بين فتح الفورم وحفظه، لازم تفكر في كيفية اكتشاف التعديلات المتزامنة، خصوصًا لو فيه Custom Logic أو API أو عمليات خارج دورة الحفظ المعتادة.

ولا تفترض إن كل موديلات Odoo عندها Version Column مخصص بنفس آلية المثال؛ آلية الحماية لازم تتحدد وتُنفذ حسب تصميم العملية.

## 10. إمتى نستخدم Optimistic Offline Lock؟

استخدمه لما:

- عدد التعارضات المتوقع قليل.
- المستخدمون ممكن يفتحوا نفس البيانات لفترات طويلة.
- مش عايز تحجز البيانات أثناء عمل المستخدم.
- محتاج تمنع Lost Updates.
- تقدر تطلب من المستخدم مراجعة التعديلات عند حدوث Conflict.

لكن لو التعارضات كثيرة جدًا، أو تكلفة رفض العملية وإعادتها عالية، ممكن تفكر في Pessimistic Offline Lock.

---

## الخلاصة

**Optimistic Offline Lock**

- يسمح لأكثر من مستخدم بتعديل نفس البيانات مبدئيًا.
- لا يحجز الـ Record أثناء فترة عمل المستخدم.
- يتحقق من عدم تغير البيانات عند الحفظ.
- أشهر تطبيق له Version Number.
- يمنع Lost Update عن طريق رفض التعديلات القديمة.
- مناسب عندما تكون التعارضات قليلة نسبيًا.

**النمط التالي: Pessimistic Offline Lock.**

وهنا هنقلب الفكرة تمامًا: بدل ما نسمح للجميع بالتعديل ونكتشف التعارض عند الحفظ، هنحاول نحجز البيانات من البداية حتى لا يعدلها مستخدم آخر في نفس الوقت.


# 2. Pessimistic Offline Lock

بعد ما فهمنا **Optimistic Offline Lock**، هننتقل لفكرة عكسية تقريبًا.

في Optimistic كنا بنسمح لأكثر من مستخدم يشتغل على نفس البيانات، ونكتشف التعارض وقت الحفظ.

أما هنا، فهنحاول نمنع التعارض من البداية عن طريق **حجز البيانات (Locking)**.

## 1. المشكلة (Problem)

تخيل عندنا نظام ERP، وموظف فاتح أمر بيع (Sales Order) وبيعدّل فيه.

في نفس الوقت، موظف تاني فتح نفس الأمر وعايز يعدّل فيه.

إحنا عايزين نضمن إن موظف واحد فقط هو اللي يقدر يعدّل الأمر في الوقت ده.

المشكلة إننا مش بنتكلم عن Database Transaction قصيرة؛ إحنا بنتكلم عن عملية مستخدم ممكن تستمر عدة دقائق.

مينفعش نفتح Database Transaction ونسيبها مفتوحة طول الوقت؛ ده ممكن يسبب مشاكل في الـ Locks والـ Connections والـ Transaction Management.

إذن محتاجين Lock مستقل عن عمر الـ Database Transaction.

## 2. الفكرة والحل (Solution)

فكرة **Pessimistic Offline Lock** إن المستخدم يحجز الـ Business Object قبل ما يبدأ تعديله.

لو الحجز نجح، يقدر يكمل شغله.

لو مستخدم تاني حاول يحجز نفس الـ Object، النظام يرفض أو يجعله ينتظر حسب تصميم النظام.

التدفق من اليمين للشمال:

```plain text
User A  <---  Acquire Lock  <---  Order 101
                                  |
User B  <---  Lock Rejected  <---  Order 101
```

بمعنى:

1. المستخدم الأول يطلب حجز Order 101.
1. النظام يمنحه الـ Lock.
1. المستخدم الأول يعدّل ويحفظ.
1. المستخدم الأول يحرر الـ Lock.
1. المستخدم الثاني يقدر يحجز الطلب بعد كده.

**مثال توضيحي**

**Order #101** (Locked)

---

الموظف الأول (Lock Owner)

الموظف الثاني (Access Denied)

الحجز هنا على مستوى الـ Business Object، وليس مجرد قفل SQL Transaction مفتوحة طوال فترة عمل الموظف.

## 3. مثال عملي باستخدام Python

هننفذ مثال مبسط باستخدام جدول منفصل لإدارة الأقفال.

### أولًا: تصميم الجدول

```sql
CREATE TABLE offline_locks (
    resource_type VARCHAR(100) NOT NULL,
    resource_id INTEGER NOT NULL,
    owner_id INTEGER NOT NULL,
    expires_at TIMESTAMP NOT NULL,

    PRIMARY KEY (resource_type, resource_id)
);
```

الجدول ده بيحدد:

- نوع الـ Object المحجوز.
- الـ ID الخاص به.
- المستخدم اللي حجزه.
- وقت انتهاء الحجز.

### ثانيًا: الحصول على Lock

```python
def acquire_lock(
    cursor,
    resource_type,
    resource_id,
    owner_id,
    expires_at
):
    cursor.execute(
        """
        INSERT INTO offline_locks (
            resource_type,
            resource_id,
            owner_id,
            expires_at
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        """,
        (
            resource_type,
            resource_id,
            owner_id,
            expires_at
        )
    )

    return cursor.rowcount == 1
```

لو المستخدم الأول حجز الطلب، الـ INSERT ينجح.

لو المستخدم الثاني حاول يحجز نفس الطلب، الـ Primary Key يمنع إنشاء Lock آخر لنفس الـ Resource.

### ثالثًا: تحرير الـ Lock

```python
def release_lock(
    cursor,
    resource_type,
    resource_id,
    owner_id
):
    cursor.execute(
        """
        DELETE FROM offline_locks
        WHERE resource_type = %s
          AND resource_id = %s
          AND owner_id = %s
        """,
        (
            resource_type,
            resource_id,
            owner_id
        )
    )
```

لاحظ إننا بنتأكد من owner_id قبل الحذف، عشان مستخدم ما يقدرش يحرر Lock مملوك لمستخدم تاني.

**ملحوظة مهمة:** المثال ده توضيحي، ومحتاج إدارة صحيحة للـ Transactions، وانتهاء الصلاحية، وتجديد الحجز، والتحقق من ملكية الـ Lock قبل كل عملية حفظ. مجرد وجود expires_at في الجدول مش كفاية لتطبيق انتهاء الحجز تلقائيًا.

### رابعًا: إيه اللي يحصل لو المستخدم قفل الصفحة بدون ما يحرر الـ Lock؟

هنا بنواجه مشكلة مهمة جدًا.

تخيل المستخدم حجز الطلب، وبعدها:

- قفل المتصفح.
- الإنترنت فصل.
- الجهاز عمل Restart.
- المستخدم نسي يحرر الحجز.

الطلب ممكن يفضل محجوز للأبد!

عشان كده بنستخدم مفهوم اسمه **Lease / Lock Expiration**.

يعني الـ Lock بيكون له مدة صلاحية.

مثلًا:

```plain text
Lock Owner = User A
Expires At = 10:30
```

لو المستخدم لم يجدد الحجز قبل 10:30، النظام يسمح بانتهاء الـ Lock.

وممكن المستخدم يجدد الحجز دوريًا عن طريق **Heartbeat**.

```plain text
User A  <---  Renew Lock  <---  Lock Manager
```

لكن فيه مشكلة إضافية: ماذا لو انتهى الحجز القديم، وحصل مستخدم آخر على حجز جديد، وبعدها المستخدم القديم حاول الحفظ؟

هنا نحتاج نتأكد إن المستخدم القديم لم يعد يملك صلاحية التعديل.

في الأنظمة الأكثر تعقيدًا ممكن نستخدم **Fencing Token**، وهو رقم متزايد مع كل Lock جديد، بحيث ترفض طبقة التخزين أي عملية قادمة من صاحب Lock قديم.

مثلًا:

```plain text
User A gets token = 10
Lock expires

User B gets token = 11

User A tries to save with token = 10
                         |
                         v
                    Rejected
```

دي نقطة مهمة جدًا في الأنظمة الموزعة؛ لأن انتهاء الـ Lock وحده لا يضمن إن صاحب الحجز القديم توقف فعلًا عن تنفيذ العمليات.

---

## 4. أقرب GoF Pattern

هل عندنا GoF Pattern مطابق لـ Pessimistic Offline Lock؟

**لا، مفيش نظير مباشر.**

لكن فيه تشابه في الفكرة مع:

**1. Monitor Object**

- Monitor Object بينظم الوصول المتزامن إلى Object داخل عملية أو بيئة تشغيل مشتركة.
- Pessimistic Offline Lock ينظم وصول المستخدمين إلى Business Object خلال Business Transaction طويلة.

الفرق إن Monitor Object غالبًا مرتبط بالتزامن داخل الذاكرة، بينما Pessimistic Offline Lock مرتبط بالتزامن بين مستخدمين وعمليات مستقلة.

**2. Proxy**

ممكن تستخدم Proxy لمنع الوصول إلى Object غير متاح أو غير محجوز للمستخدم.

لكن Proxy مجرد وسيلة لتنظيم الوصول، وليس آلية الـ Offline Lock نفسها.

إذن التشابه هنا في بعض آليات التنفيذ، مش في الـ Intent الأساسي.

---

## 5. علاقته بـ Application Architecture

زي ما اتفقنا، ده مش Application Architecture مستقل.

ممكن تستخدمه داخل Layered Architecture أو Clean Architecture.

مثال:

```plain text
User  <---  Controller  <---  Application Service
                                  |
                                  v
                            Lock Manager
                                  |
                                  v
                              Database
```

الـ Application Service ينسق العملية:

1. يطلب حجز الـ Object.
1. ينفذ الـ Business Operation.
1. يحفظ التعديلات.
1. يحرر الحجز.

والـ Lock Manager مسؤول عن تفاصيل إدارة الحجز.

مهم نفصل بين مسؤولية إدارة الحجز ومسؤولية تنفيذ الـ Business Logic.

## 6. علاقته بـ Clean Architecture

في Clean Architecture ممكن نعرّف Interface لإدارة الأقفال:

```python
from typing import Protocol

class LockManager(Protocol):

    def acquire(self, resource_id: int, owner_id: int):
        ...

    def release(self, resource_id: int, owner_id: int):
        ...
```

والـ Use Case يعتمد على الـ Interface بدل الاعتماد المباشر على PostgreSQL.

```python
class UpdateOrder:

    def __init__(self, lock_manager, order_repository):
        self.lock_manager = lock_manager
        self.order_repository = order_repository

    def execute(self, order_id, user_id, quantity):

        acquired = self.lock_manager.acquire(
            order_id,
            user_id
        )

        if not acquired:
            raise Exception("Order is already locked")

        try:
            order = self.order_repository.get(order_id)
            order.update_quantity(quantity)

            self.order_repository.save(order)

        finally:
            self.lock_manager.release(order_id, user_id)
```

ده مثال مبسط، لكنه يوضح فصل الـ Policy عن الـ Mechanism.

في تطبيق حقيقي لازم كمان نراعي إن الـ Lock يفضل محميًا خلال عملية الحفظ، وإن فشل الحفظ أو انقطاع الاتصال لا يترك النظام في حالة غير متسقة.

## 7. علاقته بـ DDD

ممكن نستخدم Pessimistic Offline Lock مع الـ Aggregate.

تخيل عندك:

```plain text
Order Aggregate
    |
    +-- Order Lines
    |
    +-- Customer Reference
```

لو عندك عملية تعديل حساسة على الـ Order، ممكن تحجز الـ Aggregate كله بحيث تمنع مستخدمًا آخر من إجراء عملية متعارضة عليه.

لكن خد بالك:

**الـ Lock مش جزء من الـ Aggregate بالضرورة.**

هو آلية لإدارة التزامن، وممكن تكون مسؤولية Application Layer أو Infrastructure Layer.

كمان لازم تحدد نطاق الحجز بناءً على قواعد العمل، مش لمجرد إن Objects مرتبطة ببعض.

## 8. علاقته بـ Odoo

في Odoo، تخيل إن عندك عملية تخصيص مخزون أو معالجة أمر بيع، وفيه أكثر من مستخدم بيحاول يعدل نفس الـ Business Resource.

ممكن تحتاج Lock منطقي على مستوى العملية، لكن لازم تفرق بين حاجتين:

- PostgreSQL SELECT FOR UPDATE: قفل على مستوى Database Transaction، وينتهي مع انتهاء الـ Transaction.
- Pessimistic Offline Lock: حجز يستمر خلال فترة عمل المستخدم، حتى لو كل عملية Database Transaction انتهت بالفعل.

فمش كل استخدام لـ SELECT FOR UPDATE يعتبر Pessimistic Offline Lock.

كمان لو هتطبق Lock Manager مخصص في Odoo، لازم تراعي تعدد الـ Workers، وملكية الحجز، وانتهاء الصلاحية، وعدم السماح بتعديل البيانات بعد فقدان الحجز.

---

## 9. مقارنة Optimistic وPessimistic

خلينا نثبت الفرق؛ لأن النمطين بيتلخبطوا بسهولة.

المقارنة	Optimistic	Pessimistic
الفكرة	اكتشاف التعارض	منع التعارض مسبقًا
الحجز	لا يوجد حجز مسبق	يوجد حجز
تعدد المستخدمين	مسموح مبدئيًا	مستخدم واحد يملك الحجز
اكتشاف المشكلة	عند الحفظ	عند طلب الحجز
التكلفة	تكلفة التعامل مع Conflict	تكلفة إدارة Lock
الأنسب	تعارضات قليلة	تعارضات متكررة أو مكلفة

## 10. إمتى نستخدم Pessimistic Offline Lock؟

استخدمه لما:

- التعارضات متكررة.
- تكلفة حدوث التعارض عالية.
- إعادة تنفيذ العملية صعبة.
- محتاج تضمن إن مستخدم واحد فقط يعدل موردًا معينًا في نفس الوقت.

لكن تجنبه لو الحجز هيعطل المستخدمين باستمرار، أو لو المستخدمين ممكن ينسوا تحرير الأقفال، أو لو نظامك موزع ومش عندك آلية موثوقة لإدارة انتهاء الحجز.

---

# النمط الثالث: Coarse-Grained Lock

النقطة اللي وصلنالها مهمة:

في Pessimistic Offline Lock عرفنا إزاي نحجز Object.

لكن ظهر سؤال جديد:

**ماذا لو العملية الواحدة بتتعامل مع مجموعة Objects مرتبطة ببعض؟ هل نحجز كل Object لوحده؟**

وده بالضبط اللي هنتكلم عنه في **Coarse-Grained Lock**.

هنشوف إزاي نختار نطاق القفل، وليه أحيانًا قفل Object واحد مش كفاية، وإيه علاقته بالـ Aggregate في DDD.


# 3. Coarse-Grained Lock

النمط ده مرتبط جدًا باللي فات، لكن فيه اختلاف مهم لازم نفهمه.

في **Pessimistic Offline Lock** كنا بنجاوب عن السؤال:

> إزاي أمنع أكثر من مستخدم من تعديل نفس الـ Business Object في نفس الوقت؟

أما في **Coarse-Grained Lock** فالسؤال مختلف:

> إيه حجم أو نطاق الـ Object اللي المفروض أحجزه أصلًا؟

يعني المشكلة هنا مش مجرد إزاي نعمل Lock، لكن **نحجز إيه بالضبط؟**

## 1. المشكلة (Problem)

تخيل عندنا نظام مبيعات، وعندنا Order بالشكل ده:

```plain text
Order #100
    |
    +--- Order Line #1
    |
    +--- Order Line #2
    |
    +--- Order Line #3
    |
    +--- Payment
```

موظف بيعدل Order Line #1، وموظف تاني بيعدل Order Line #2.

لو عملنا Lock لكل Object بشكل مستقل، الاتنين ممكن يشتغلوا في نفس الوقت.

لكن ماذا لو تعديل الـ Order Line الأول أثر على إجمالي الطلب، وتعديل الثاني أثر على نفس الإجمالي؟

ممكن نواجه مشاكل في اتساق البيانات (Consistency).

ولو قررنا نحجز كل Object لوحده، هنحتاج ندير مجموعة Locks:

- Lock للـ Order.
- Lock لكل Order Line.
- Lock للـ Payment.
- Lock لأي Object مرتبط بالعملية.

وده ممكن يؤدي إلى تعقيد كبير في إدارة الأقفال.

## 2. الفكرة والحل (Solution)

بدل ما نحجز كل Object بشكل مستقل، بنحدد **مجموعة Objects مترابطة** ونعتبرها وحدة واحدة للحجز.

يعني بدل:

```plain text
Line #1  <---  Lock A

Line #2  <---  Lock B

Payment  <---  Lock C

Order    <---  Lock D
```

نحجز الـ Order بالكامل:

```plain text
Order #100
    |
    +--- Order Line #1
    |
    +--- Order Line #2
    |
    +--- Order Line #3
    |
    +--- Payment

          ^
          |
     One Shared Lock
```

وبالترتيب من اليمين للشمال:

```plain text
Order + Lines + Payment  <---  One Coarse-Grained Lock
```

بالتالي أي مستخدم يريد تعديل جزء من المجموعة المحجوزة لازم يحصل على نفس الـ Lock.

الفكرة الأساسية هي تقليل عدد الأقفال التي يجب إدارتها، عن طريق توسيع نطاق القفل.

**مثال: Order #100**

Order (Locked)

---

Order Line #1 (Protected)

Order Line #2 (Protected)

Payment (Protected)

الـ Lock واحد على مستوى Order، لكن تأثيره يمتد إلى العمليات التي تعدّل الأجزاء التابعة له.

## 3. مثال Python

هنفترض إن عندنا Order يحتوي على مجموعة Order Lines.

بدل ما نحجز كل Line، هنحجز الـ Order نفسه.

```python
class LockManager:

    def __init__(self):
        self.locks = {}

    def acquire(self, resource_id, owner_id):
        if resource_id in self.locks:
            return False

        self.locks[resource_id] = owner_id
        return True

    def release(self, resource_id, owner_id):
        if self.locks.get(resource_id) != owner_id:
            return False

        del self.locks[resource_id]
        return True
```

استخدامه:

```python
locks = LockManager()

# User A locks Order 100
locks.acquire("order:100", "user_a")

# User B wants to update Line 1
can_update = locks.acquire("order:100", "user_b")

print(can_update)  # False
```

لاحظ إننا لم نستخدم:

```python
locks.acquire("order_line:1", "user_b")
```

لأننا قررنا إن نطاق الحجز هو الـ Order بالكامل.

لكن فيه شرط مهم جدًا:

**كل العمليات التي تعدّل أجزاء الـ Order لازم تحترم نفس Lock.**

لو فيه API أو Background Job بيعدل الـ Order Lines من غير ما يتحقق من Lock الـ Order، يبقى الحماية غير مكتملة.

المثال هنا تعليمي فقط؛ وفي الإنتاج نحتاج Lock Manager مشتركًا بين كل الـ Workers، مع تخزين ذري للأقفال وانتهاء صلاحيتها.

---

## 4. أقرب GoF Pattern

هل Coarse-Grained Lock له GoF Pattern مطابق؟

**لا يوجد GoF Pattern مطابق له.**

لكن ممكن نلاحظ تشابهًا جزئيًا مع:

**Facade Pattern**

الـ Facade بيقدم واجهة موحدة للتعامل مع مجموعة من الأنظمة أو الكائنات الفرعية.

أما Coarse-Grained Lock فبيتعامل مع مجموعة Objects كنطاق واحد للحجز.

الفرق:

- Facade هدفه تبسيط واجهة الاستخدام.
- Coarse-Grained Lock هدفه تقليل تعقيد إدارة التزامن عن طريق توسيع نطاق الحجز.

إذن التشابه في التعامل مع مجموعة Objects من خلال نقطة واحدة، وليس في الـ Intent.

---

## 5. علاقته بـ Application Architecture

النمط ده مش Architecture مستقلة، لكنه ممكن يظهر داخل أي Application Architecture.

مثلًا في Layered Architecture:

```plain text
User  <---  Controller  <---  Application Service
                                  |
                                  v
                              Lock Manager
                                  |
                                  v
                              Order Scope
```

الـ Application Service يطلب حجز الـ Order بالكامل قبل تنفيذ العملية.

ومش مهم إذا كان النظام Layered أو Clean أو Hexagonal؛ المهم إن كل عمليات التعديل على نفس النطاق تحترم سياسة الحجز.

## 6. علاقته بـ Clean Architecture

في Clean Architecture ممكن نعرّف Port مسؤول عن الحجز:

```python
class OrderLock(Protocol):

    def acquire(self, order_id: int, user_id: int) -> bool:
        ...

    def release(self, order_id: int, user_id: int) -> bool:
        ...
```

الـ Use Case يتعامل مع OrderLock بدل تفاصيل قاعدة البيانات.

```plain text
Database Lock Implementation
             |
             v
       OrderLock Port
             ^
             |
        Use Case
             ^
             |
        Controller
```

لاحظ اتجاه الاعتماد في الرسم من اليمين للشمال:

```plain text
Controller  --->  Use Case  --->  OrderLock Interface
```

والـ Infrastructure هي اللي تنفذ الـ Interface.

المهم هنا إن Clean Architecture لا تفرض علينا نطاق القفل؛ تحديد النطاق قرار متعلق بالـ Business Requirements.

---

## 7. علاقته بـ DDD

هنا عندنا ارتباط مهم جدًا.

في DDD عندنا مفهوم اسمه **Aggregate**.

الـ Aggregate عبارة عن مجموعة Objects مرتبطة ببعض، وبتتعامل مع قواعد اتساق محددة من خلال Aggregate Root.

مثلًا:

```plain text
Order (Aggregate Root)
    |
    +--- OrderLine
    |
    +--- OrderLine
    |
    +--- OrderLine
```

ممكن يكون الـ Order هو نطاق الحجز المناسب، لأن التعديلات على الـ Order Lines لازم تحافظ على قواعد الـ Order.

لكن خلي بالك من نقطة دقيقة:

**Coarse-Grained Lock مش هو نفسه Aggregate.**

- Aggregate مفهوم في DDD لتحديد حدود الاتساق والتحكم في التعديلات.
- Coarse-Grained Lock نمط لإدارة التزامن على نطاق مجموعة Objects.

ممكن نستخدم حدود الـ Aggregate لتحديد نطاق الـ Lock، لكن مش شرط يكونوا متطابقين في كل نظام.

كمان مش كل Object مرتبط بالـ Order لازم يكون جزءًا من نفس الـ Aggregate أو يدخل في نفس الحجز.

---

## 8. علاقته بـ Odoo

خلينا ناخد مثال من Odoo.

عندنا:

- sale.order
- sale.order.line

لو قررنا إن تعديل أي sale.order.line لازم يتم في ظل حجز الـ sale.order الأب، يبقى ممكن نستخدم الـ Order ID باعتباره Lock Resource.

```plain text
sale.order
    |
    +--- sale.order.line
    |
    +--- sale.order.line
    |
    +--- sale.order.line

        One Lock on sale.order
```

أي عملية تعديل على الـ Lines لازم تتحقق من حجز الـ Order.

لكن لازم ننتبه:

- Odoo ORM مش هيفرض علينا السياسة دي تلقائيًا.
- لازم نغطي كل مسارات التعديل: UI، RPC، API، Cron، وعمليات الـ Background.
- قفل الـ Order لا يمنع تلقائيًا أي كود يكتب مباشرة على الـ Lines.
- لا نحتاج بالضرورة إلى قفل كل الـ Database Rows؛ ممكن نستخدم Lock منطقيًا مستقلًا عن Database Row Locks.

---

## 9. عيوب ومميزات Coarse-Grained Lock

**المميزات:**

- عدد أقفال أقل.
- إدارة أبسط للتزامن.
- يقلل تعارضات التعديلات داخل مجموعة مترابطة.
- مناسب عندما تكون Objects مرتبطة بقواعد اتساق مشتركة.

**العيوب:**

- ممكن يمنع مستخدمًا من تعديل جزء لا يتعارض فعليًا مع تعديل مستخدم آخر.
- يقلل مستوى الـ Concurrency.
- ممكن يسبب انتظارًا غير ضروري.
- اختيار نطاق كبير جدًا يجعل النظام أقل قابلية للتوسع.

مثال:

لو موظف بيعدل عنوان Order، وموظف تاني بيعدل ملاحظة داخل Order Line، ممكن ما يكونش فيه تعارض حقيقي بين العمليتين، لكن الـ Coarse-Grained Lock هيمنعهم من العمل معًا.

وده هو الـ Trade-off الأساسي.

---

## 10. الفرق بين الأنماط الثلاثة حتى الآن

النمط	السؤال الذي يجيب عنه
Optimistic Offline Lock	إزاي أكتشف التعارض عند الحفظ؟
Pessimistic Offline Lock	إزاي أحجز المورد قبل التعديل؟
Coarse-Grained Lock	إيه نطاق المورد اللي هحجزه؟

---

# النمط الرابع والأخير: Implicit Lock

هنا هنتكلم عن مشكلة مختلفة شوية:

لو عندنا Locking Strategy، هل لازم كل Developer يفتكر بنفسه إنه يعمل Acquire وRelease في كل عملية؟

ولا ممكن نخلي الـ Lock يحصل بشكل ضمني من خلال آلية موجودة في النظام؟

وده موضوع **Implicit Lock**.
