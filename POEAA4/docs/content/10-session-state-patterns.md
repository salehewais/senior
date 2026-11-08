# أنماط حالة الجلسة (Session State Patterns)

## الخريطة النهائية لـ Session State Patterns

```plain text
Session State Patterns
          |
          +--- Client Session State
          |
          +--- Server Session State
          |
          +--- Database Session State
```

**الخلاصة المهمة:**

الأنماط الثلاثة بتجاوب عن سؤال واحد:

> فين نخزن حالة المستخدم بين الـ HTTP Requests؟

- Client: عند العميل.
- Server: عند السيرفر.
- Database: في قاعدة البيانات.

لكن اختيار مكان التخزين مش قرار منفصل عن طبيعة البيانات، وحجمها، وأمانها، ومدة حياتها، ومتطلبات التوسع.

**وبكده نكون خلصنا Session State Patterns الثلاثة.**

تمام يا هندسة 😂 نبدأ مجموعة جديدة من كتاب **Patterns of Enterprise Application Architecture (PoEAA)**، وهي:

# Session State Patterns

قبل ما نبدأ، لازم نفهم المشكلة اللي المجموعة دي بتحاول تحلها.

## يعني إيه Session State؟

تخيل إن المستخدم دخل نظام ERP وعمل Login.

بعد كده بدأ يتنقل بين صفحات النظام:

- فتح صفحة العملاء.
- اختار Customer معين.
- بدأ يعمل Order.
- اختار منتجات.
- انتقل لصفحة الدفع.

السؤال هنا: إزاي التطبيق يحتفظ بالمعلومات المرتبطة بالمستخدم خلال تنقله بين الطلبات المختلفة؟

لأن HTTP بطبيعته Stateless، يعني كل Request مستقلة عن الطلب اللي قبلها، والتطبيق مش بيفتكر تلقائيًا إن الطلبين جايين من نفس المستخدم.

إذن محتاجين آلية للاحتفاظ بحالة المستخدم عبر مجموعة Requests.

وده اللي بنسميه **Session State**.

## خريطة Session State Patterns

عندنا في PoEAA ثلاثة أنماط أساسية:

```plain text
Session State Patterns
          |
          +--- Client Session State
          |
          +--- Server Session State
          |
          +--- Database Session State
```

الاختلاف الأساسي بينهم هو: **أين يتم تخزين حالة الـ Session؟**

- Client Session State: عند العميل.
- Server Session State: في ذاكرة السيرفر.
- Database Session State: في قاعدة البيانات.

هنبدأ بأول نمط.

---



# Client Session State

## المشكلة

عندنا Web Application، والمستخدم بيعمل Requests متعددة.

مثلاً:

```plain text
Open Products
      |
Add Product
      |
Update Quantity
      |
Checkout
```

كل Request مستقلة عن الثانية.

لكن التطبيق محتاج يحتفظ بمعلومات زي:

- User Preferences.
- Shopping Cart.
- Selected Language.
- Current Workflow Information.

ممكن نخزن المعلومات دي في السيرفر، لكن ده هيحتاج إدارة Sessions على السيرفر نفسه.

السؤال: هل ممكن نخزن حالة المستخدم عند العميل بدل السيرفر؟

## الفكرة والحل

فكرة **Client Session State** هي تخزين بيانات الـ Session على جهاز المستخدم نفسه، بحيث العميل يرسل البيانات دي مع كل Request يحتاجها التطبيق.

بالتالي السيرفر مش محتاج يحتفظ بنسخة من حالة كل مستخدم في ذاكرته.

التدفق من اليمين للشمال:

```plain text
Server  <---  Session Data  <---  Client
```

مثال:

المستخدم اختار اللغة العربية، والسلة فيها منتجين.

ممكن نخزن الحالة بالشكل ده:

```json
{
    "language": "ar",
    "cart": [
        {
            "product_id": 10,
            "quantity": 2
        },
        {
            "product_id": 20,
            "quantity": 1
        }
    ]
}
```

العميل يحتفظ بالبيانات، ويرسلها مع الطلبات المناسبة.

**مثال: Shopping Cart**

**Client Browser** (Stores State)

---

Product A × 2 Quantity: 2

Product B × 1 Quantity: 1

---

السيرفر يستقبل حالة السلة مع الطلب، بدل الاحتفاظ بحالة Session كاملة في ذاكرته.

لكن هنا فيه سؤال مهم:

هل ينفع نخزن البيانات دي في Cookie عادية؟

ممكن، لكن فيه اعتبارات مهمة:

- حجم الـ Cookie محدود.
- البيانات ممكن المستخدم يقرأها أو يحاول يعدلها.
- لازم نحمي سلامة البيانات من التلاعب.
- لازم نراعي إن الـ Cookie بتتبعت تلقائيًا مع الطلبات المطابقة لنطاقها، وده له اعتبارات أمنية.

عشان كده ممكن نستخدم:

- Signed Cookies.
- Encrypted Cookies.
- Tokens تحتوي على Session Claims.

**مهم:** التوقيع (Signing) يمنع اكتشاف التعديل غير المصرح به، لكنه لا يخفي محتوى البيانات. التشفير (Encryption) هو اللي يوفر السرية.

---

## مثال

هنعمل مثال مبسط يوضح الفكرة باستخدام Flask.

```python
from flask import Flask, request, make_response
import json

app = Flask(__name__)

@app.route("/cart")
def get_cart():

    cart = request.cookies.get("cart")

    if cart:
        cart_data = json.loads(cart)
    else:
        cart_data = []

    response = make_response({
        "cart": cart_data
    })

    return response

@app.route("/cart/add/<int:product_id>")
def add_to_cart(product_id):

    cart = request.cookies.get("cart")

    if cart:
        cart_data = json.loads(cart)
    else:
        cart_data = []

    cart_data.append({
        "product_id": product_id,
        "quantity": 1
    })
```

ده مثال تعليمي فقط، وليس تطبيقًا آمنًا للإنتاج؛ لأن المستخدم يقدر يغيّر قيمة الـ Cookie، ومفيش توقيع أو تشفير أو معالجة لتكرار المنتج.

في تطبيق حقيقي ممكن نستخدم Cookie موقعة ومشفرة، أو نخزن بيانات غير حساسة فقط عند العميل.

والأهم: **ماينفعش نثق في بيانات العميل عند تنفيذ عمليات مالية أو تغيير أسعار أو صلاحيات.**

مثلًا سعر المنتج لازم يتحدد ويتحقق منه على السيرفر، مش من قيمة مرسلة داخل الـ Cookie.

## أقرب GoF Pattern

هل فيه GoF Pattern مطابق لـ Client Session State؟

**لا يوجد GoF Pattern مطابق مباشرةً.**

لكن فيه تشابه جزئي مع:

**Memento Pattern**

الـ Memento بيحفظ حالة Object بحيث نقدر نسترجعها لاحقًا.

أما Client Session State فهدفه تخزين حالة المستخدم عند العميل ونقلها بين Requests.

الفرق في الـ Intent:

- Memento: حفظ واسترجاع حالة Object.
- Client Session State: إدارة حالة المستخدم عبر Requests باستخدام تخزين Client-Side.

ممكن تستخدم Memento كآلية لحفظ حالة، لكن مش هو نفس النمط.

## 5. علاقته بـ Application Architecture

Client Session State مش Application Architecture مستقلة.

ممكن تستخدمه داخل:

- Layered Architecture.
- Clean Architecture.
- Hexagonal Architecture.

مثلاً:

```plain text
Client  <---  HTTP Request + Session Data  <---  Controller
                                                    |
                                                    v
                                               Application
                                                    |
                                                    v
                                                 Domain
```

الـ Controller يستقبل بيانات الـ Session ويحوّلها إلى بيانات مناسبة للتطبيق.

لكن مش المفروض الـ Domain يعتمد على تفاصيل الـ Cookie أو HTTP Session.

## علاقته بالعمارة

في Clean Architecture، بيانات الـ Session تعتبر جزءًا من الـ Input القادم من الخارج.

ممكن يكون عندنا:

```python
class CheckoutInput:

    def __init__(self, user_id, cart_items):
        self.user_id = user_id
        self.cart_items = cart_items
```

الـ Controller يقرأ البيانات من الـ Client، ويتحقق من شكلها، وبعدها يمررها للـ Use Case.

```plain text
Client  <---  Controller  <---  Checkout Use Case
```

لكن فيه فرق مهم:

الـ Client Session State مش معناها إننا ننقل Business State بالكامل للعميل.

مثلًا:

- اختيار اللغة: مناسب للتخزين عند العميل.
- شكل الواجهة: مناسب للتخزين عند العميل.
- محتويات سلة التسوق: ممكن تخزينها عند العميل مع إعادة التحقق على السيرفر.
- رصيد الحساب البنكي: لا، لازم مصدر الحقيقة يكون موثوقًا على السيرفر.

## 7. علاقته بـ DDD

DDD بيفرق بين:

- Domain State.
- Application State.
- Presentation State.

Client Session State غالبًا مناسب للاحتفاظ بجزء من الـ Presentation أو Application State.

مثلاً:

```plain text
User Session
    |
    +--- Selected Language
    |
    +--- Current Page
    |
    +--- UI Preferences
    |
    +--- Temporary Workflow Data
```

لكن لا ينبغي اعتبار البيانات الموجودة عند العميل مصدر الحقيقة للـ Aggregate.

لو المستخدم أرسل:

```json
{
    "order_total": 100
}
```

مش معنى كده إن الـ Domain يقبل إن إجمالي الطلب هو 100.

لازم يحسب الإجمالي من البيانات الموثوقة وقواعد العمل.

## علاقته بأودو

في Odoo عندنا Session مرتبطة بمستخدم الويب، وبيتم التعامل معها من خلال HTTP Layer.

لكن لازم نفرّق بين:

- Client Session State: الحالة نفسها مخزنة عند العميل.
- Server Session State: العميل يحتفظ بمعرّف Session، والحالة الفعلية موجودة عند السيرفر.

في تطبيق Odoo، مجرد إن الـ Browser عنده Cookie فيها Session ID مش معناه إن Odoo بيستخدم Client Session State.

الـ Session ID مجرد وسيلة للتعرف على الـ Session، ومش هو بيانات الـ Session نفسها.

---

## 9. المميزات والعيوب

**المميزات:**

- يقلل احتياج السيرفر لتخزين Session لكل مستخدم.
- يسهل التوسع الأفقي (Horizontal Scaling) من ناحية حالة الجلسة.
- لا يحتاج بالضرورة إلى Session Store مشترك بين السيرفرات.
- مناسب للبيانات الصغيرة وغير الحساسة.

**العيوب:**

- حجم البيانات محدود.
- العميل ممكن يحاول التلاعب بالبيانات.
- إرسال البيانات المتكررة يزيد حجم الـ Requests.
- التشفير والتوقيع وإدارة المفاتيح يضيفوا تعقيدًا.
- إلغاء Session أو تحديث حالتها فورًا أصعب لو كل البيانات موجودة عند العميل.

## 10. إمتى نستخدم Client Session State؟

استخدمه لما تكون البيانات:

- صغيرة.
- مناسبة للتخزين عند العميل.
- لا تحتاج تحكمًا مركزيًا مستمرًا في تحديثها وإلغائها.
- يمكن التحقق منها عند السيرفر قبل تنفيذ أي Business Operation حساسة.

---

## الخلاصة
Client Session State بيحل مشكلة الاحتفاظ بحالة المستخدم عن طريق نقل مسؤولية تخزين الحالة إلى العميل بدل السيرفر.

لكن ده لا يعني إننا ننقل مسؤولية الـ Business Rules أو مصدر الحقيقة للعميل.

---

# النمط التالي: Server Session State

هنا هنقلب الفكرة تمامًا.

بدل ما نخزن حالة المستخدم عند العميل، هنخزنها عند السيرفر، والعميل يحتفظ فقط بمعرّف الـ Session.

وهنفهم الفرق بين تخزين الحالة في Server Memory وبين استخدام Session Store مشترك، وليه الموضوع ده مهم جدًا في الأنظمة اللي فيها أكثر من Application Server.


# Server Session State

في النمط السابق **Client Session State** كنا بنخزن حالة المستخدم عند العميل نفسه.

دلوقتي هنستخدم العكس تمامًا:

**هنخزن حالة المستخدم عند السيرفر، والعميل هيحتفظ فقط بمعرّف الـ Session.**

## المشكلة

تخيل عندنا مستخدم دخل نظام ERP وعمل Login.

بعد تسجيل الدخول، بدأ ينفذ مجموعة عمليات:

- اختار الشركة الحالية.
- اختار اللغة.
- حدد مجموعة فلاتر للتقارير.
- بدأ عملية إنشاء Order.
- اختار منتجات وكميات.

إحنا محتاجين نحتفظ بالحالة دي بين الـ Requests المختلفة.

ممكن نخزن كل البيانات عند العميل، لكن ده مش مناسب دائمًا، خصوصًا لو البيانات كبيرة أو حساسة أو محتاجة تحكم مركزي.

إذن نحتاج مكانًا على السيرفر يحتفظ بحالة كل مستخدم.

## الفكرة والحل

فكرة **Server Session State** هي إن السيرفر يحتفظ ببيانات الـ Session، بينما العميل يحتفظ بمعرّف يحدد الـ Session الخاصة به.

مثلًا:

```plain text
Client  <---  Session ID  <---  Server
```

العميل مش محتاج يعرف تفاصيل الحالة المخزنة عند السيرفر.

كل اللي محتاجه إنه يرسل Session ID مع كل Request.

والسيرفر يستخدم الـ ID لاسترجاع الحالة.

### مثال عملي

المستخدم عمل Login، والسيرفر أنشأ Session:

**Server Session Store**

Session ID
abc123

---

User ID
42

Current Company
5

Language
ar

Cart
Product A × 2

الـ Browser يحتفظ فقط بالـ Session ID.

وعندما يرسل Request جديدة:

```plain text
Browser  <---  Request + Session ID  <---  Server
```

السيرفر يستخرج الـ Session ID، ويبحث عن البيانات المرتبطة به.

### شكل المعمارية

```plain text
Browser  <---  Session ID  <---  Application Server
                                      |
                                      v
                                Session Store
                                      |
                                      v
                                Session Data
```

لاحظ إن الـ Session Store ممكن يكون داخل ذاكرة السيرفر نفسه، أو خدمة تخزين خارجية.

وده هيفرق معانا جدًا لما نبدأ نتكلم عن Distributed Systems.

## مثال

هنستخدم Flask لتوضيح الفكرة.

```python
from flask import Flask, session, jsonify

app = Flask(__name__)

app.secret_key = "development-secret-key"

@app.route("/login")
def login():

    session["user_id"] = 42
    session["company_id"] = 5
    session["language"] = "ar"

    return jsonify({
        "message": "Logged in"
    })

@app.route("/profile")
def profile():

    return jsonify({
        "user_id": session.get("user_id"),
        "company_id": session.get("company_id"),
        "language": session.get("language")
    })
```

هنا فيه تفصيلة مهمة جدًا:

**Flask الافتراضي بيستخدم Secure Cookie Session، مش Server-Side Session Store.**

يعني البيانات نفسها بتكون مخزنة داخل Cookie موقعة عند العميل، مش داخل ذاكرة السيرفر.

إذن المثال السابق يوضح واجهة التعامل مع Session، لكنه ليس تنفيذًا حقيقيًا لـ Server Session State.

خلينا نعمل تنفيذًا توضيحيًا باستخدام Server-Side Dictionary:

```python
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

sessions = {}

@app.route("/login")
def login():

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "user_id": 42,
        "company_id": 5,
        "language": "ar"
    }

    response = jsonify({
        "message": "Logged in"
    })

    response.set_cookie(
        "session_id",
        session_id,
        httponly=True,
        secure=True,
        samesite="Lax"
    )

    return response

@app.route("/profile")
def profile():

    session_id = request.cookies.get("session_id")
```

في المثال ده:

- الـ Dictionary هو Session Store.
- السيرفر هو اللي بيحتفظ بالبيانات.
- العميل بيحتفظ بالـ Session ID.
- كل Request بتستخدم الـ ID للوصول إلى الحالة.

ده مثال تعليمي فقط؛ Dictionary مش مناسب للإنتاج لأنه بيضيع عند إعادة تشغيل السيرفر، ومش مشترك بين Workers أو Servers، ومفيهوش انتهاء صلاحية أو إدارة آمنة للـ Sessions.

---

## 4. ماذا يحدث لو عندنا أكثر من Application Server؟

هنا تظهر أهمية النمط في الأنظمة الكبيرة.

تخيل عندنا Application Server عدد 2:

- Server A
- Server B

والمستخدم سجل الدخول من خلال Server A.

الـ Session اتخزنت في ذاكرة Server A.

بعد كده المستخدم بعت Request جديدة، والـ Load Balancer وجّهها إلى Server B.

المشكلة إن Server B مش عنده Session المستخدم!

```plain text
                         Load Balancer
                         /            \
                        v              v
                  Server A          Server B
                      |                  |
                      v                  v
                Local Sessions      Local Sessions
```

هنا عندنا أكثر من حل:

1. Sticky Sessions: الـ Load Balancer يحاول يوجه المستخدم دائمًا لنفس السيرفر.
1. Shared Session Store: كل السيرفرات تستخدم نفس مخزن الـ Sessions.
1. Client Session State: تخزين الحالة عند العميل بدل السيرفر، لو طبيعة البيانات تسمح بذلك.

الحل الشائع في الأنظمة الموزعة هو Shared Session Store، مثل Redis.

```plain text
User  <---  Load Balancer  <---  Server A
                    |
                    +--- Server B
                    |
                    v
              Shared Redis
                    |
                    v
              Session Data
```

وبالتالي أي Application Server يقدر يسترجع Session المستخدم.

---

## أقرب GoF Pattern

مفيش GoF Pattern مطابق لـ Server Session State.

لكن فيه تشابه جزئي مع:

**Registry Pattern**

لأن عندنا مكان مركزي نقدر من خلاله نصل إلى بيانات مرتبطة بمعرّف معين.

لكن الفرق:

- Registry: آلية للوصول إلى Objects أو Services مسجلة.
- Server Session State: تخزين حالة المستخدم واسترجاعها عبر Requests.

ممكن تستخدم Registry-like mechanism في تنفيذ Session Store، لكن مش هما نفس النمط.

كمان فيه تشابه مع **Memento Pattern** من ناحية حفظ واسترجاع الحالة، لكنه مش بديل مباشر.

## 6. علاقته بـ Application Architecture

Server Session State مش Architecture مستقلة.

ممكن نستخدمه في Layered أو Clean أو Hexagonal Architecture.

مثال:

```plain text
Browser  <---  HTTP Request + Session ID  <---  Controller
                                                   |
                                                   v
                                              Session Service
                                                   |
                                                   v
                                              Session Store
```

الـ Controller أو Middleware يستخرج الـ Session ID.

بعدها Session Service تسترجع الحالة المطلوبة.

ومن الأفضل إن الـ Domain Layer مايعرفش حاجة عن HTTP Session أو Cookie أو Redis.

## علاقته بالعمارة

في Clean Architecture ممكن نعرّف Port للتعامل مع Session:

```python
from typing import Protocol

class SessionStore(Protocol):

    def get(self, session_id: str):
        ...

    def save(self, session_id: str, data: dict):
        ...

    def delete(self, session_id: str):
        ...
```

والـ Infrastructure توفر Implementation باستخدام Redis أو Database أو Memory.

```plain text
Redis Implementation  <---  SessionStore Port  <---  Application Service
```

الـ Application Service يعتمد على Interface، مش على Redis مباشرة.

لكن فيه نقطة مهمة:

مش كل بيانات الـ Session لازم تدخل الـ Use Case.

مثلًا اللغة الحالية أو إعدادات الواجهة ممكن تتعامل معاها طبقة الـ Presentation.

أما بيانات مرتبطة بعملية Business طويلة، فممكن تحتاج إدارة مختلفة حسب طبيعة العملية.

## 8. علاقته بـ DDD

لازم نفرق بين Session State وDomain State.

مثلاً:

**Session State:**

- المستخدم الحالي.
- اللغة المختارة.
- الشركة الحالية.
- تفضيلات العرض.
- بيانات مؤقتة للتنقل.

**Domain State:**

- حالة Order.
- رصيد Account.
- حالة Invoice.
- قواعد تسعير المنتج.

الـ Session مش المفروض تكون مصدر الحقيقة للـ Domain Objects.

مثلًا لو المستخدم اختار Company ID في الـ Session، لازم التطبيق يتحقق إن المستخدم عنده صلاحية الوصول للشركة دي.

وجود القيمة في Session مش معناه إنها موثوقة أو مسموح بها تلقائيًا.

---

## علاقته بأودو

في Odoo عندنا Server-Side Session State بشكل واضح.

الـ Browser بيحتفظ بـ Session Cookie، والسيرفر يستخدم الـ Session ID للوصول إلى بيانات الـ Session.

ومن المعلومات اللي ممكن ترتبط بالـ Session:

- User Identity.
- Context.
- Company Information.
- Language.
- Authentication Information.

لكن لازم نفرق بين الـ Session وبين الـ Database Transaction.

الـ Session ممكن تستمر عبر Requests كثيرة، بينما كل HTTP Request لها دورة Transaction خاصة بها في Odoo.

يعني:

```plain text
Session Lifetime  <---  Multiple HTTP Requests
```

بينما:

```plain text
Database Transaction  <---  One Request Lifecycle
```

وده فرق مهم جدًا، خصوصًا لما نتعامل مع عمليات طويلة أو Background Jobs.

---

## 10. المميزات والعيوب

**المميزات:**

- السيرفر يتحكم في حالة المستخدم.
- مناسب للبيانات الأكبر نسبيًا من Client-Side Cookies.
- يقدر يلغي Session أو يعدلها من السيرفر.
- البيانات الحساسة مش مضطرة تتخزن داخل العميل.
- ممكن مشاركة الحالة بين عدة Application Servers باستخدام Shared Store.

**العيوب:**

- يحتاج مساحة تخزين على السيرفر أو خدمة خارجية.
- كل Request قد تحتاج قراءة Session من المخزن.
- محتاج إدارة Expiration وCleanup.
- محتاج حل لمشكلة مشاركة Sessions بين السيرفرات.
- Session Store نفسه ممكن يصبح نقطة ضغط أو فشل.

كمان لازم نراعي Session Fixation وSession Hijacking، ونستخدم Session ID عشوائي قوي، وHTTPS، وCookie Security Flags، وتجديد Session ID بعد تسجيل الدخول.

---

## 11. مقارنة Client وServer Session State

المقارنة	Client Session	Server Session
مكان الحالة	العميل	السيرفر
ما يرسله العميل	بيانات الحالة	Session ID
تحكم السيرفر	محدود نسبيًا	أكبر
حجم البيانات	محدود	أكبر نسبيًا
إلغاء الحالة	أصعب	أسهل مركزيًا
مشاركة الحالة بين Servers	غير مطلوبة غالبًا	تحتاج Shared Store أو Sticky Sessions

---


# Database Session State

وصلنا لآخر نمط في مجموعة **Session State Patterns**.

في النمط السابق **Server Session State** كنا بنخزن حالة المستخدم على السيرفر، سواء في Memory أو في Shared Store زي Redis.

لكن هنا هنستخدم قاعدة البيانات نفسها لتخزين حالة الـ Session.

## المشكلة

تخيل عندنا نظام Enterprise Application فيه آلاف المستخدمين.

كل مستخدم عنده Session تحتوي على بيانات مختلفة:

- User ID.
- Current Company.
- Language.
- Shopping Cart.
- Workflow Progress.
- Temporary Application Data.

لو خزّنا الـ Sessions في ذاكرة Application Server، هنواجه مشكلة لما السيرفر يعمل Restart.

ولو استخدمنا Redis، هنحتاج ندير Redis كخدمة إضافية، ونتأكد من إعدادات Persistence والـ Replication والـ Recovery حسب متطلبات النظام.

السؤال:

هل ممكن نخزن الـ Session State في قاعدة البيانات نفسها، بحيث تكون جزءًا من البيانات اللي النظام بيديرها؟

## الفكرة والحل

فكرة **Database Session State** هي تخزين حالة المستخدم في جدول داخل Database.

العميل يحتفظ فقط بالـ Session ID، والسيرفر يستخدمه للوصول إلى البيانات المخزنة.

التدفق من اليمين للشمال:

```plain text
Browser  <---  Session ID  <---  Application Server
                                      |
                                      v
                                  Database
                                      |
                                      v
                                  Session Data
```

مثلاً نعمل جدول:

```sql
CREATE TABLE user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

ممكن نخزن البيانات بالشكل ده:

```json
{
    "company_id": 5,
    "language": "ar",
    "cart": [
        {
            "product_id": 10,
            "quantity": 2
        }
    ]
}
```

وبالتالي كل Session ليها Record مستقل في قاعدة البيانات.

## مثال

هنستخدم psycopg كمثال مبسط.

### حفظ Session

```python
import json

def save_session(conn, session_id, user_id, data, expires_at):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO user_sessions (
                session_id,
                user_id,
                session_data,
                expires_at
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (session_id)
            DO UPDATE SET
                session_data = EXCLUDED.session_data,
                expires_at = EXCLUDED.expires_at
            """,
            (
                session_id,
                user_id,
                json.dumps(data),
                expires_at
            )
        )

    conn.commit()
```

### استرجاع Session

```python
def get_session(conn, session_id):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT session_data
            FROM user_sessions
            WHERE session_id = %s
              AND expires_at > NOW()
            """,
            (session_id,)
        )

        row = cursor.fetchone()

    if not row:
        return None

    return row[0]
```

### حذف Session

```python
def delete_session(conn, session_id):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM user_sessions
            WHERE session_id = %s
            """,
            (session_id,)
        )

    conn.commit()
```

لاحظ إننا بنستخدم expires_at عشان نتأكد إن الـ Session لسه صالحة.

وممكن نعمل Scheduled Job يحذف الـ Sessions المنتهية دوريًا.

المثال للتوضيح، وفي الإنتاج لازم نراعي Connection Pooling، وإدارة المعاملات، وتحديث الجلسة بشكل ذري عند تعدد الطلبات، وحماية Session ID، وتحديد سياسة انتهاء الصلاحية.

---

## 4. إيه اللي يميز Database Session State عن Server Session State؟

خلينا نرجع خطوة.

**Server Session State** بيحدد مكان تخزين الحالة بشكل عام: عند السيرفر.

لكن مكان التخزين ممكن يكون:

- In-Memory.
- Redis.
- Database.

أما **Database Session State** فهو نمط محدد بيستخدم قاعدة البيانات لتخزين الحالة.

يعني العلاقة بينهم إن Database Session State يعتبر أحد أساليب تطبيق Server-Side Session Storage.

مثال مقارنة:

**Server Session State باستخدام Memory**

```plain text
Client  <---  Server A  <---  Memory
```

(Local to Server)

---

**Server Session State باستخدام Redis**

```plain text
Client  <---  Server A  <---  Redis
                     ^
                     |
                  Server B
```

(Shared Store)

---

**Database Session State**

```plain text
Client  <---  Server  <---  PostgreSQL
```

(Database Persistence)

ملحوظة: Redis ممكن يكون عنده Persistence، وبالتالي مش معنى استخدام Redis إن البيانات هتضيع بالضرورة عند Restart. الموضوع متعلق بإعداداته ومتطلبات الاستمرارية.

## أقرب GoF Pattern

مفيش GoF Pattern مطابق لـ Database Session State.

لكن فيه تشابه جزئي مع:

**Data Mapper Pattern**

لأننا بنحتاج نحول بيانات الـ Session من شكلها داخل التطبيق إلى شكل قابل للتخزين في قاعدة البيانات، والعكس.

لكن الفرق:

- Data Mapper مسؤول عن نقل البيانات بين Objects وDatabase.
- Database Session State مسؤول عن مكان وطريقة تخزين حالة المستخدم.

Data Mapper ممكن يكون وسيلة تنفيذ، لكنه مش نفس النمط.

وممكن كمان تلاحظ تشابهًا مع Repository، لأننا ممكن نوفر واجهة لإدارة Sessions، لكن Repository نفسه مش بديل عن Database Session State.

## 6. علاقته بـ Application Architecture

النمط ده مش Application Architecture مستقلة.

ممكن تستخدمه داخل Layered Architecture أو Clean Architecture أو Hexagonal Architecture.

مثلاً:

```plain text
Browser  <---  Controller  <---  Application Service
                                      |
                                      v
                                Session Repository
                                      |
                                      v
                                  Database
```

الـ Application Service بيتعامل مع Session Repository، والـ Repository مسؤول عن القراءة والكتابة في قاعدة البيانات.

لكن مش كل Business Operation لازم تعتمد على Session Repository مباشرة.

## علاقته بالعمارة

ممكن نعرّف Port لإدارة Session:

```python
from typing import Protocol

class SessionRepository(Protocol):

    def get(self, session_id: str):
        ...

    def save(self, session_id: str, data: dict):
        ...

    def delete(self, session_id: str):
        ...
```

والـ Infrastructure تنفذ الـ Port باستخدام PostgreSQL.

```plain text
PostgreSQL Implementation  <---  SessionRepository Port  <---  Application
```

وبكده الـ Application مش محتاجة تعرف إننا بنستخدم PostgreSQL.

ممكن نستبدلها بـ Redis أو أي Storage تاني من غير تغيير في الـ Business Logic.

## 8. علاقته بـ DDD

هنا لازم نفرق بين حاجتين:

**Session State مش بالضرورة Domain State.**

مثلاً:

Session State	Domain State
اللغة المختارة	حالة الطلب
الشركة الحالية	رصيد الحساب
الصفحة الحالية	حالة الفاتورة
الفلاتر المختارة	قواعد التسعير

ممكن نخزن Session في Database، لكن ده مش معناه إننا حولناها إلى Domain Entity.

ومش معنى إن البيانات موجودة في نفس قاعدة البيانات إن ليها نفس المسؤوليات أو نفس دورة الحياة.

كمان لو عندنا Workflow طويل ومهم، لازم نفكر هل ده فعلًا مجرد Session State، ولا Business Process محتاج Persistence مستقلة.

مثلًا عملية اعتماد فاتورة ممكن تستمر أيامًا؛ مينفعش نعتمد على Session المستخدم لحفظ تقدم العملية، لأنها مرتبطة بعمر الجلسة، بينما العملية التجارية لها دورة حياة مستقلة.

## علاقته بأودو

في Odoo، قاعدة البيانات هي المكان الأساسي لتخزين بيانات الـ Business، لكن لازم نفرق بين تخزين بيانات المستخدم والجلسة.

ممكن تعمل Custom Session Model لو عندك احتياج خاص لتخزين حالة إضافية في Database.

لكن مش معنى إن Odoo بيستخدم PostgreSQL إن كل بيانات الـ Session بتتخزن داخل PostgreSQL.

كمان لازم تراعي:

- انتهاء صلاحية الـ Session.
- تنظيف الـ Records القديمة.
- عدم تخزين بيانات حساسة بدون حماية مناسبة.
- عدم الخلط بين Session وUser Preferences.
- عدم استخدام Session كبديل لتخزين Business Workflow.

---

## 10. المميزات والعيوب

**المميزات:**

- البيانات بتفضل موجودة بعد Restart للـ Application Server.
- كل Application Servers تقدر تستخدم نفس قاعدة البيانات.
- إدارة البيانات والـ Expiration ممكن تتم باستخدام SQL.
- ممكن الاستفادة من Backup وRecovery الخاصين بقاعدة البيانات.

**العيوب:**

- كل قراءة أو تحديث للـ Session ممكن يضيف ضغطًا على Database.
- ممكن يزيد عدد Queries في كل Request.
- محتاج Indexing مناسب على Session ID وExpiration.
- ممكن Session Store ينافس عمليات الـ Business على نفس موارد قاعدة البيانات.
- إدارة التحديثات المتزامنة للـ Session محتاجة تصميم دقيق.

---

## 11. مقارنة الأنماط الثلاثة

المقارنة	Client	Server	Database
مكان الحالة	العميل	السيرفر	Database
مكان Session ID	العميل	العميل	العميل
تخزين الحالة مركزيًا	لا	حسب التنفيذ	نعم
تحمل Restart	غالبًا نعم	حسب التخزين	حسب إعدادات DB
مشاركة عدة Servers	مش مطلوبة غالبًا	تحتاج Shared Store	متاحة
ضغط Database	غير مباشر	حسب التنفيذ	مباشر

---

# الخريطة النهائية لـ Session State Patterns

```plain text
Session State Patterns
          |
          +--- Client Session State
          |
          +--- Server Session State
          |
          +--- Database Session State
```

**الخلاصة المهمة:**

الأنماط الثلاثة بتجاوب عن سؤال واحد:

> فين نخزن حالة المستخدم بين الـ HTTP Requests؟

- Client: عند العميل.
- Server: عند السيرفر.
- Database: في قاعدة البيانات.

لكن اختيار مكان التخزين مش قرار منفصل عن طبيعة البيانات، وحجمها، وأمانها، ومدة حياتها، ومتطلبات التوسع.

**وبكده نكون خلصنا Session State Patterns الثلاثة.**

تمام يا هندسة 😂 نبدأ مجموعة جديدة من كتاب **Patterns of Enterprise Application Architecture (PoEAA)**، وهي:
