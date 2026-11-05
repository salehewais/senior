# معمارية نظام المكتبة: MVC إلى Hexagonal {#library-architecture}

MVC وMVP وMVVM أنماط لطبقة العرض، وتختار الأنسب لكل واجهة. Clean وHexagonal ينظمان التطبيق: القواعد تبقى داخل الحدود، والتفاصيل تعتمد على عقود يملكها الـ Core. الذي يثبت المعمارية هو المسؤوليات واتجاه الاعتماد، لا اسم الكلاس أو المجلد.

- منتج واحد قد يجمع MVC في لوحة إدارة وMVVM في سطح المكتب.
- تبديل PostgreSQL بذاكرة لا يثبت Clean. الذي يثبته اعتماد Use Case على Port يملكه.
- وقت التشغيل يسير من CLI إلى Use Case ثم إلى التخزين. وقت التصميم تسير الاعتمادات نحو العقود.
- Model أو Repository أو Interface وحدها لا تسمي النمط.

@answer scope="نظام مكتبة · Python · CLI · Odoo"
@meta locale=ar style=editorial

## ما المشكلة قبل اختيار النمط؟ {#problem}

نظام المكتبة يضيف كتابًا، يعرض الكتب، يرفض عنوانًا فارغًا، ويخزّن في الذاكرة مع إمكان استبدال التخزين لاحقًا. الكيان `Book(id, title, author)` واحد في كل الأمثلة.

ثلاث مسؤوليات لا يجب خلطها: **قواعد العمل** (هل العنوان صالح؟)، **التخزين** (أين وكيف؟)، **العرض** (كيف يضيف المستخدم ويرى النتيجة؟). السؤالان المنفصلان: من **مسؤول** عن العملية، ومن **ينفّذ** التخزين فعليًا؟

@architecture id=library-responsibilities title="ثلاث مسؤوليات"
| rules | قواعد العمل | backend |
| persist | التخزين | database |
| present | العرض | frontend |
| present > rules | طلب إضافة |
| rules > persist | حفظ بعد التحقق |
| persist > present | بيانات للعرض |

## MVC: من يستقبل الطلب؟ {#mvc}

MVC هنا ينظم الطلب والعرض. **Controller** يستقبل الإدخال وينسق الاستجابة. **View** تعرض. **Model** في هذا الملف يحمل البيانات والتحقق والتخزين معًا، وهذا تبسيط تعليمي لا قاعدة.

وجود Model لا يعني أن كل قواعد العمل تعيش فيه. قاعدة خاصة بالعملية أو بالمستخدم قد تعيش خارج Model. وأطر الويب وسطح المكتب توزع الأسماء الثلاثة بأشكال مختلفة، فوجود الثلاثة لا يثبت MVC واحدًا.

@sequence id=mvc-add-book title="تسلسل controller.add_book"
| actor ctrl | Controller | backend |
| actor model | BookModel | database |
| actor view | BookView | frontend |
| ctrl | model | add_book(title, author) |
| model | ctrl | Book | return |
| ctrl | view | show_book_added(book) |
| phase | عنوان فارغ |
| ctrl | model | add_book("", author) |
| model | ctrl | ValueError | return |
| ctrl | view | show_error(message) |

```python title="MVC — CLI مبسّط"
from dataclasses import dataclass

@dataclass
class Book:
    id: int
    title: str
    author: str

class BookModel:
    def __init__(self):
        self._books = []
        self._next_id = 1

    def add_book(self, title, author):
        if not title.strip():
            raise ValueError("Title is required")
        book = Book(id=self._next_id, title=title, author=author)
        self._books.append(book)
        self._next_id += 1
        return book

    def get_all(self):
        return list(self._books)

class BookView:
    def show_book_added(self, book):
        print(f"Added: {book.id} — {book.title}")

    def show_error(self, message):
        print(f"Error: {message}")

    def show_all(self, books):
        for book in books:
            print(f"{book.id}: {book.title} by {book.author}")

class BookController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

    def add_book(self, title, author):
        try:
            book = self.model.add_book(title, author)
            self.view.show_book_added(book)
        except ValueError as exc:
            self.view.show_error(str(exc))

    def list_books(self):
        self.view.show_all(self.model.get_all())
```

@callout level=note title="حدود المثال"
معالجة `ValueError` داخل Controller اختيار في هذا الملف، وليست قاعدة MVC. وفي نظام أكبر لا تجمع Model الحالة والتحقق والتخزين إن كانت تلك القواعد يجب أن تبقى عند تغيير الواجهة.

## MVP: Presenter وعقد View {#mvp}

**Presenter** يجهّز صفوف العرض ويعتمد على عقدين: `BookViewContract` و`BookRepositoryPort`. التنفيذ `InMemoryBookRepository` يحقّق العقد، والـ Presenter لا يذكر اسمه في توقيعه.

`Protocol` وسيلة لكتابة العقد في Python، وليس تعريف MVP.

```python title="MVP — العقدان ثم التنفيذ"
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str

class BookRepositoryPort(Protocol):
    def add(self, title: str, author: str) -> Book: ...
    def get_all(self) -> list[Book]: ...

class InMemoryBookRepository:
    def __init__(self):
        self._books = []
        self._next_id = 1

    def add(self, title, author):
        book = Book(self._next_id, title, author)
        self._books.append(book)
        self._next_id += 1
        return book

    def get_all(self):
        return list(self._books)

class BookViewContract(Protocol):
    def show_message(self, message: str) -> None: ...
    def show_books(self, rows: list[tuple]) -> None: ...

class BookPresenter:
    def __init__(self, repo: BookRepositoryPort, view: BookViewContract):
        self.repo = repo
        self.view = view

    def add_book(self, title, author):
        if not title.strip():
            self.view.show_message("Title is required")
            return
        self.repo.add(title, author)
        self.view.show_books(self._rows())

    def _rows(self):
        return [(b.id, b.title, b.author) for b in self.repo.get_all()]
```

```python title="اختبار Presenter بـ FakeView"
class FakeView:
    def __init__(self):
        self.messages = []
        self.rows = []

    def show_message(self, message):
        self.messages.append(message)

    def show_books(self, rows):
        self.rows = rows

repo = InMemoryBookRepository()
fake_view = FakeView()
presenter = BookPresenter(repo, fake_view)
presenter.add_book("", "Unknown")
assert fake_view.messages == ["Title is required"]
assert repo.get_all() == []
```

`InMemoryBookRepository` يصلح هنا لأنه يحقّق `BookRepositoryPort`. اختبار آخر يمرر مستودعًا مزيفًا بنفس الدالتين. قابلية الاستبدال تأتي من العقد، لا من تحويل الكيانات إلى `dict`.

## MVVM: حالة ViewModel وإشعار الواجهة {#mvvm}

الواجهة تشترك في حالة ViewModel. عند التغيير، `_notify()` يعيد العرض. الربط هنا يدوي، والأطر الحقيقية توفر Data Binding.

`subscribe` تُرجع دالة إلغاء. عند إغلاق الواجهة تُستدعى حتى لا يبقى ViewModel محتفظًا بنداء View انتهى عمرها.

```python title="MVVM — subscribe تعيد unsubscribe"
from dataclasses import dataclass

@dataclass(frozen=True)
class Book:
    id: int
    title: str
    author: str

class BookViewModel:
    def __init__(self):
        self._books = []
        self._listeners = []
        self._next_id = 1
        self.message = ""

    @property
    def books(self):
        return tuple(self._books)

    def subscribe(self, callback):
        self._listeners.append(callback)
        callback(self)

        def unsubscribe():
            if callback in self._listeners:
                self._listeners.remove(callback)

        return unsubscribe

    def _notify(self):
        for callback in list(self._listeners):
            callback(self)

    def add_book(self, title, author):
        if not title.strip():
            self.message = "Title is required"
            self._notify()
            return
        self._books.append(Book(self._next_id, title, author))
        self._next_id += 1
        self.message = ""
        self._notify()

class ConsoleBookView:
    def __init__(self, vm):
        self._unsubscribe = vm.subscribe(self._render)

    def close(self):
        self._unsubscribe()

    def _render(self, vm):
        if vm.message:
            print(f"Error: {vm.message}")
        for book in vm.books:
            print(f"{book.id}: {book.title} by {book.author}")
```

في CLI قصير العمر لا يظهر أثر الإبقاء على النداء. في Desktop وMobile، View تُدمَّر وViewModel قد يبقى. بلا `unsubscribe`، النداء اللاحق يلمس واجهة ميتة أو يبقيها في الذاكرة.

## Clean Architecture: فصل القواعد عن التخزين {#clean}

تغيير PostgreSQL لا يجب أن يغيّر قواعد إضافة الكتاب. هذا يتحقق باتجاه الاعتماد وحدود القواعد، لا بمجرد القدرة على تبديل كلاس التخزين.

- **Domain**: `Book` وقواعد الكيان الثابتة.
- **Application**: Use Cases وعقد `BookRepository`. استيراد `Book` إلى هنا اعتماد نحو الداخل.
- **Infrastructure**: تنفيذ التخزين. يعتمد على العقد ولا يعرّف القاعدة.
- **main.py**: جذر التركيب. يحقن التنفيذ في Use Case، وهذا Dependency Injection.

@tree id=clean-layout title="هيكل مشروع Clean"
| root | library | - |
| domain | domain | root |
| book | book.py | domain |
| app | application | root |
| ports | ports.py | app |
| uc | use_cases.py | app |
| infra | infrastructure | root |
| mem | memory_repository.py | infra |
| main | main.py | root |

```python title="domain/book.py"
from dataclasses import dataclass

@dataclass(frozen=True)
class Book:
    id: int | None
    title: str
    author: str

    def __post_init__(self):
        if not self.title.strip():
            raise ValueError("Title is required")
        if not self.author.strip():
            raise ValueError("Author is required")
```

```python title="application/ports.py و use_cases.py"
from typing import Protocol
from library.domain.book import Book

class BookRepository(Protocol):
    def save(self, book: Book) -> Book: ...
    def find_all(self) -> list[Book]: ...

class AddBookUseCase:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def execute(self, title: str, author: str) -> Book:
        book = Book(id=None, title=title, author=author)
        return self.repository.save(book)

class ListBooksUseCase:
    def __init__(self, repository: BookRepository):
        self.repository = repository

    def execute(self) -> list[Book]:
        return self.repository.find_all()
```

```python title="infrastructure/memory_repository.py و main.py"
class InMemoryBookRepository:
    def __init__(self):
        self._books = []
        self._next_id = 1

    def save(self, book: Book) -> Book:
        saved = Book(
            id=self._next_id,
            title=book.title,
            author=book.author,
        )
        self._books.append(saved)
        self._next_id += 1
        return saved

    def find_all(self) -> list[Book]:
        return list(self._books)

repository = InMemoryBookRepository()
add_book = AddBookUseCase(repository)
list_books = ListBooksUseCase(repository)
add_book.execute("Clean Code", "Robert Martin")
for book in list_books.execute():
    print(f"{book.id}: {book.title} by {book.author}")
```

`__post_init__` مكان قاعدة ثابتة للكيان: العنوان والمؤلف غير فارغين. قاعدة مرتبطة بالعملية أو بالمستخدم، مثل حد الإعارة، لا تُكدس كلها داخل `Book`.

@callout level=warning title="التبديل وحده ليس Clean"
حقن `InMemoryBookRepository` بدل PostgreSQL ممكن في تصميم تقليدي بلا طبقات. Clean هنا تعني أن Use Case يعتمد على `BookRepository`، وأن التنفيذ الخارجي هو الذي يحقّق العقد، وأن قاعدة العنوان لا تعرف اسم قاعدة البيانات.

## Hexagonal: Ports وAdapters {#hexagonal}

الـ Core يملك العقود. **Input Ports** عمليات الدخول: `AddBookPort` و`ListBooksPort`. **Output Port** هو `BookRepositoryPort`. الـ CLI والذاكرة Adapters خارجية تعتمد على هذه العقود.

الرسم اتجاه اعتماد وقت التصميم، لا مسار النداء وقت التشغيل.

@architecture id=hexagonal-flow title="الاعتماد نحو العقود"
| hexcli | CLIAdapter | frontend |
| hexin | AddBookPort | backend |
| hexuc | AddBookService | backend |
| hexout | BookRepositoryPort | backend |
| hexmem | InMemoryAdapter | database |
| hexcli > hexin | يعتمد |
| hexuc > hexin | يحقّق |
| hexuc > hexout | يعتمد |
| hexmem > hexout | يحقّق |

| الاتجاه | المسار |
| --- | --- |
| وقت التشغيل | CLI يستدعي Use Case، ثم Use Case يستدعي الحفظ، ثم Adapter التخزين ينفّذ |
| وقت التصميم | CLIAdapter يعتمد على AddBookPort. Use Case يعتمد على BookRepositoryPort. InMemoryAdapter يحقّق ذلك العقد |

```python title="Hexagonal — العقدان معًا"
from typing import Protocol
from library.domain.book import Book

class BookRepositoryPort(Protocol):
    def save(self, book: Book) -> Book: ...
    def find_all(self) -> list[Book]: ...

class AddBookPort(Protocol):
    def execute(self, title: str, author: str) -> Book: ...

class ListBooksPort(Protocol):
    def execute(self) -> list[Book]: ...

class AddBookService:
    def __init__(self, repository: BookRepositoryPort):
        self.repository = repository

    def execute(self, title, author):
        book = Book(id=None, title=title, author=author)
        return self.repository.save(book)

class ListBooksService:
    def __init__(self, repository: BookRepositoryPort):
        self.repository = repository

    def execute(self):
        return self.repository.find_all()

class CLIAdapter:
    def __init__(self, add_book: AddBookPort, list_books: ListBooksPort):
        self.add_book = add_book
        self.list_books = list_books

    def run_add(self, title, author):
        book = self.add_book.execute(title, author)
        print(f"Added: {book.id} — {book.title}")

    def run_list(self):
        for book in self.list_books.execute():
            print(f"{book.id}: {book.title}")
```

Use Case يستدعي الـ Port. الـ Adapter يحقّق العقد الذي يملكه الـ Core. سهم التشغيل من CLI إلى التخزين ليس سهم الـ import.

Clean ترتب الطبقات. Hexagonal تسمي المنافذ. يمكن جمع الفكرتين في `domain` و`application` و`adapters`.

## مقارنة وجمع الأنماط {#compare}

الصفوف الثلاثة الأولى أنماط عرض، وتُختار لكل واجهة. الصفان الأخيران معماريات تطبيق، وتنظمان الحدود كلها. ليست خمسة بدائل من نوع واحد.

| النمط {#pattern-row} | الطبقة | السؤال | متى يناسب |
| --- | --- | --- | --- |
| MVC | Presentation | من يستقبل الطلب وينسق العرض؟ | واجهة طلب واستجابة {good:ويب} |
| MVP | Presentation | كيف أختبر منطق العرض؟ | عقد View بلا واجهة حقيقية {good:اختبار} |
| MVVM | Presentation | كيف تصل الحالة إلى الواجهة؟ | Desktop أو Mobile {good:Reactive} |
| Clean | تطبيق | أين تقف قاعدة العمل؟ | اعتماد نحو الداخل {good:فصل} |
| Hexagonal | تطبيق | من يملك العقود؟ | CLI وREST على Core واحد {good:منافذ} |

@facts id=combine-facts
| العرض | النمط الأنسب لكل واجهة |
| التطبيق | Use Case أمام Port |
| المجال | كيان وقواعده الثابتة |
| الخارج | Adapter يحقّق العقد |

جمع شائع: Controller يستدعي `AddBookUseCase`، والـ Use Case يعتمد على `BookRepository`، و`PostgresBookRepository` يحقّق العقد. الواجهة الأخرى في المنتج نفسه قد تكون MVVM وتستدعي Use Case نفسه.

## ما الفرق بين DIP وDI؟ {#dip}

**Dependency Inversion** يحدد اتجاه الاعتماد: السياسة العليا تعتمد على عقد تملكه، لا على تفصيلة التخزين. في الملف، `BookPresenter` و`AddBookUseCase` يذكران `Protocol` لا `InMemoryBookRepository`.

**Dependency Injection** يحدد من يمرر التنفيذ. `main.py` ينشئ المستودع ويمرره إلى Use Case. الحقن بلا عقد يبدّل كلاسات ملموسة ويبقى الاعتماد على التنفيذ. العقد بلا جذر تركيب يترك الكائن يبني المستودع بنفسه.

| | DIP | DI |
| --- | --- | --- |
| السؤال | على أي شيء يعتمد الكود؟ | من يمرر التنفيذ؟ |
| في المكتبة | Use Case يعتمد على BookRepository | main.py يمرر InMemoryBookRepository |
| وحدها | لا تركّب الكائنات | لا تعكس اتجاه الاعتماد |

## Repository أم Active Record؟ {#storage-style}

هذا اختلاف في أسلوب الوصول إلى البيانات، لا في أسماء الكلاسات.

**Repository** يجعل التطبيق يتحدث إلى مجموعة عبر Port. SQL أو الـ ORM يبقى في الـ Adapter. أمثلة Clean وHexagonal هنا من هذا الأسلوب.

**Active Record** يجعل الكيان نفسه يحمّل ويحفظ. سجل Odoo يرث `models.Model` ويستدعي `search` و`create` و`write`. القاعدة التي تعيش على هذا السجل تعرف الـ ORM.

| | Repository | Active Record |
| --- | --- | --- |
| من يحفظ | Adapter خلف Port | السجل نفسه |
| قاعدة الكيان | Domain لا يستورد ORM | غالبًا Method على Model |
| في هذا الملف | InMemoryBookRepository | نموذج Odoo |
| اسم مضلل | كلاس اسمه Repository ويستورد SQL داخل Domain | Method اسمها Use Case وهي تنفّذ write |

## أين تعيش قاعدة العمل؟ {#services}

**Application Service** ينسق عملية واحدة. `AddBookUseCase.execute` يبني `Book` ثم يستدعي `save`. يعرف مسار العملية، ولا يعرف اسم الجدول.

**Domain Service** قاعدة لا تنتمي إلى حقل واحد، ولا تعرف الواجهة ولا SQL. حد الإعارة يحتاج عدد الكتب الحالي، لذلك ليست `Book.__post_init__`. الـ Use Case يجلب العدد عبر العقد ثم يسأل السياسة.

```python title="سياسة مجال بلا تخزين"
class BorrowingPolicy:
    def assert_can_add(self, existing_count: int, limit: int) -> None:
        if existing_count >= limit:
            raise ValueError("Borrowing limit reached")
```

قاعدة «العنوان غير فارغ» تبقى على `Book`. قاعدة «هذا المستخدم تجاوز الحد» تبقى على السياسة. تنسيق «من طلب الإضافة حتى الحفظ» يبقى على Use Case.

## كيف يجلس MVC أمام Clean؟ {#mvc-clean}

Controller هنا Driving Adapter. لا يستورد `InMemoryBookRepository`. جذر التركيب في `main.py` هو الذي يجمع Use Case بالمستودع ويمررهما إلى Controller.

```python title="Controller يستدعي Use Case"
class BookController:
    def __init__(self, add_book: AddBookUseCase, view: BookView):
        self._add_book = add_book
        self.view = view

    def add_book(self, title, author):
        try:
            book = self._add_book.execute(title, author)
            self.view.show_book_added(book)
        except ValueError as exc:
            self.view.show_error(str(exc))

repository = InMemoryBookRepository()
controller = BookController(
    AddBookUseCase(repository),
    BookView(),
)
controller.add_book("Clean Code", "Robert Martin")
```

تغيير الواجهة يبدّل Controller وView. تغيير PostgreSQL يبدّل المستودع في سطر التركيب. `AddBookUseCase` و`Book` يبقيان ما دام العقد وقاعدة العنوان لم يتغيرا.

## Odoo: هل التأكيد Use Case؟ {#odoo}

@callout level=warning title="اسم المكون لا يثبت النمط"
وجود View وController وModel في Odoo لا يثبت MVC بالمعنى الدقيق، ولا Clean. ORM في Odoo أقرب إلى Active Record: العملية تعيش على السجل.

تأكيد أمر البيع في `sale.order` دالة على `models.Model`. تستدعي حقولًا وسجلات عبر الـ ORM. تسميتها Use Case لا تعزل القاعدة ما دامت تعرف `write` وبيئة الإطار. العزل يبدأ إذا صارت القاعدة قابلة للاختبار دون تشغيل الإطار، والتخزين خلف عقد لا تستورده القاعدة.

```python title="شكل Active Record، لا Repository"
class LibraryBook(models.Model):
    _name = "library.book"
    title = fields.Char(required=True)

    def action_archive_empty(self):
        if not self.title:
            raise UserError("Title is required")
        self.write({"active": False})
```

- [ ] هل القاعدة تعمل إن استبدلت الـ ORM، أم هي Method على السجل؟
- [ ] هل التكامل الخارجي خلف عقد، أم استدعاء مباشر داخل Model؟
- [ ] هل أختبر العملية دون تشغيل Registry الإطار؟
- [ ] هل تغيير التخزين يفرض تعديل القاعدة نفسها؟

## ما الذي يثبت النمط؟ {#proof}

- [ ] مسؤوليات العرض والقاعدة والتخزين مفصولة بمن يملك كلًا منها
- [ ] الاعتماد البرمجي يتجه إلى عقد يملكه الداخل
- [ ] سهم التشغيل من CLI إلى التخزين لم يُرسَم كأنه سهم import
- [ ] لكل View دالة إلغاء اشتراك إن كان ViewModel يعيش أطول منها
- [ ] Input Ports كلها مذكورة في توقيع الـ Adapter، لا عقد واحد وتنفيذ عارٍ
- [ ] تبديل PostgreSQL لم يُحتسب دليلًا وحده على Clean

## اختبر فهمك {#quiz}

| السؤال | الإجابة | السبب |
| --- | --- | --- |
| تبديل PostgreSQL بذاكرة | لا يثبت Clean وحده {caution:ناقص} | DI يبدّل التنفيذ. Clean تحتاج Port واتجاه اعتماد |
| سهم CLI إلى المستودع | نداء وقت التشغيل {good:صح} | الاعتماد عكسه: الـ Adapter يتجه إلى عقد الـ Core |
| subscribe بلا إلغاء | نداء قد يلمس View ميتة {bad:تسريب} | أعد unsubscribe وأغلقها مع الواجهة |
| كلاس اسمه Repository | لا يكفي {good:صح} | انظر هل Domain يستورد التخزين أم الـ Adapter يحقّق العقد |
