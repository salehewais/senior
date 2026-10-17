export interface Example {
  id: string;
  label: string;
  code: string;
  stdin: string;
}

export interface ExampleGroup {
  title: string;
  examples: Example[];
}

function example(id: string, label: string, code: string, stdin = ""): Example {
  return { id, label, code, stdin };
}

export const EXAMPLE_GROUPS: ExampleGroup[] = [
  {
    title: "Basic Examples",
    examples: [
      example("hello", "hello", 'print("hello world")\n'),
      example("happy", "happy", 'name = "world"\nprint("happy " + name)\n'),
      example("intro", "intro", 'x = 1\ny = "hello"\nz = x + 1\n'),
      example(
        "filter",
        "filter",
        "nums = [1, 2, 3, 4, 5]\nevens = []\nfor n in nums:\n    if n % 2 == 0:\n        evens.append(n)\n",
      ),
      example("tokenize", "tokenize", 'text = "one two three"\nwords = text.split()\n'),
      example(
        "insertion-sort",
        "insertion sort",
        "nums = [3, 1, 2]\nfor i in range(1, len(nums)):\n    key = nums[i]\n    j = i - 1\n    while j >= 0 and nums[j] > key:\n        nums[j + 1] = nums[j]\n        j = j - 1\n    nums[j + 1] = key\n",
      ),
      example(
        "list-comp",
        "list comprehension",
        "nums = [1, 2, 3, 4]\nsquares = [n * n for n in nums if n % 2 == 0]\n",
      ),
    ],
  },
  {
    title: "Math-Related Fun",
    examples: [
      example(
        "factorial",
        "factorial",
        "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n - 1)\n\nresult = factorial(4)\n",
      ),
      example(
        "fibonacci",
        "fibonacci",
        "def fib(n):\n    if n <= 1:\n        return n\n    return fib(n - 1) + fib(n - 2)\n\nresult = fib(4)\n",
      ),
      example(
        "fib-memo",
        "memoized fibonacci",
        "def fib_memo(n, memo):\n    if n in memo:\n        return memo[n]\n    if n <= 1:\n        memo[n] = n\n        return n\n    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)\n    return memo[n]\n\nresult = fib_memo(5, {})\n",
      ),
      example(
        "sqrt",
        "square root",
        "def sqrt(n):\n    guess = n / 2\n    for _ in range(4):\n        guess = (guess + n / guess) / 2\n    return guess\n\nresult = sqrt(9)\n",
      ),
      example(
        "gcd",
        "gcd",
        "def gcd(a, b):\n    while b:\n        a, b = b, a % b\n    return a\n\nresult = gcd(48, 18)\n",
      ),
      example(
        "hanoi",
        "towers of hanoi",
        'def hanoi(n, src, dst, aux):\n    if n == 1:\n        return [(src, dst)]\n    return hanoi(n - 1, src, aux, dst) + [(src, dst)] + hanoi(n - 1, aux, dst, src)\n\nmoves = hanoi(2, "A", "C", "B")\n',
      ),
    ],
  },
  {
    title: "Higher-Order Functions",
    examples: [
      example(
        "closure-1",
        "closure 1",
        "def make_adder(n):\n    def add(x):\n        return x + n\n    return add\n\nplus3 = make_adder(3)\nresult = plus3(10)\n",
      ),
      example(
        "closure-2",
        "closure 2",
        "def counter():\n    count = 0\n    def tick():\n        nonlocal count\n        count = count + 1\n        return count\n    return tick\n\ntick = counter()\ntick()\ntick()\n",
      ),
      example(
        "closure-3",
        "closure 3",
        "def compose(f, g):\n    def both(x):\n        return f(g(x))\n    return both\n\ndef inc(x):\n    return x + 1\n\ndef double(x):\n    return x * 2\n\nh = compose(inc, double)\nresult = h(3)\n",
      ),
      example(
        "closure-4",
        "closure 4",
        "def power(exp):\n    def raise_to(base):\n        return base ** exp\n    return raise_to\n\nsquare = power(2)\ncube = power(3)\na = square(4)\nb = cube(2)\n",
      ),
      example(
        "closure-5",
        "closure 5",
        "funcs = []\nfor i in range(3):\n    def show(i=i):\n        return i\n    funcs.append(show)\nvals = [f() for f in funcs]\n",
      ),
      example(
        "list-map",
        "list map",
        "def double(n):\n    return n * 2\n\nnums = [1, 2, 3]\nmapped = list(map(double, nums))\n",
      ),
      example(
        "summation",
        "summation",
        "def summation(n, term):\n    total = 0\n    i = 1\n    while i <= n:\n        total = total + term(i)\n        i = i + 1\n    return total\n\ndef square(x):\n    return x * x\n\nresult = summation(3, square)\n",
      ),
      example(
        "lambda-param",
        "lambda param",
        "def apply(fn, value):\n    return fn(value)\n\nresult = apply(lambda n: n + 5, 2)\n",
      ),
      example(
        "student-torture",
        "student torture",
        "def outer(a):\n    def middle(b):\n        def inner(c):\n            return a + b + c\n        return inner\n    return middle\n\nf = outer(1)\ng = f(2)\nresult = g(3)\n",
      ),
    ],
  },
  {
    title: "User Input",
    examples: [example("raw-input", "raw input", 'name = input()\nprint("Hello,", name)\n', "Ada\n")],
  },
  {
    title: "Object-Oriented Programming",
    examples: [
      example(
        "oop-1",
        "OOP 1",
        "class A:\n    x = 1\n    y = 'hello'\n\nclass B:\n    z = 'bye'\n\nclass C(A, B):\n    def salutation(self):\n        return '%d %s %s' % (self.x, self.y, self.z)\n\ninst = C()\nprint(inst.salutation())\ninst.x = 100\nprint(inst.salutation())\n",
      ),
      example(
        "oop-2",
        "OOP 2",
        "class Point:\n    def __init__(self, x, y):\n        self.x = x\n        self.y = y\n\n    def move(self, dx, dy):\n        self.x = self.x + dx\n        self.y = self.y + dy\n\np = Point(1, 2)\np.move(3, 4)\n",
      ),
      example(
        "oop-3",
        "OOP 3",
        "class Bag:\n    def __init__(self):\n        self.items = []\n\n    def add(self, item):\n        self.items.append(item)\n\nbag = Bag()\nbag.add('apple')\nbag.add('pear')\n",
      ),
      example(
        "inheritance",
        "inheritance",
        "class Animal:\n    def __init__(self, name):\n        self.name = name\n\n    def speak(self):\n        return '...'\n\nclass Dog(Animal):\n    def speak(self):\n        return self.name + ' says woof'\n\npet = Dog('Ada')\nprint(pet.speak())\n",
      ),
    ],
  },
  {
    title: "Linked Lists",
    examples: [
      example(
        "ll-1",
        "LL 1",
        "class Node:\n    def __init__(self, value, nxt):\n        self.value = value\n        self.next = nxt\n\nhead = Node(1, Node(2, Node(3, None)))\n",
      ),
      example(
        "ll-2",
        "LL 2",
        "class Node:\n    def __init__(self, value, nxt):\n        self.value = value\n        self.next = nxt\n\nhead = None\nfor n in [1, 2, 3]:\n    head = Node(n, head)\n",
      ),
      example(
        "ll-sum",
        "LL sum",
        "class Node:\n    def __init__(self, value, nxt):\n        self.value = value\n        self.next = nxt\n\ndef linked_sum(node):\n    total = 0\n    while node is not None:\n        total = total + node.value\n        node = node.next\n    return total\n\nhead = Node(1, Node(2, Node(3, None)))\nresult = linked_sum(head)\n",
      ),
    ],
  },
  {
    title: "Pointer Aliasing",
    examples: [
      example("alias-1", "aliasing 1", "a = [1, 2]\nb = a\n"),
      example("alias-2", "aliasing 2", "a = [1]\nb = a\nb.append(2)\n"),
      example("alias-3", "aliasing 3", "a = [1, 2]\nb = a[:]\n"),
      example("alias-4", "aliasing 4", "row = [0]\ngrid = [row, row]\ngrid[0][0] = 1\n"),
      example(
        "alias-5",
        "aliasing 5",
        "def push(items, value):\n    items.append(value)\n\nnums = [1]\npush(nums, 2)\n",
      ),
      example("alias-6", "aliasing 6", "a = [1]\nb = a\na = [2]\n"),
      example("alias-7", "aliasing 7", 'a = {"n": 1}\nb = a\nb["n"] = 2\n'),
      example(
        "alias-8",
        "aliasing 8",
        "class Box:\n    def __init__(self):\n        self.n = 1\n\na = Box()\nb = a\nb.n = 2\n",
      ),
      example(
        "sum-list",
        "sumList",
        "def sum_list(items):\n    total = 0\n    for n in items:\n        total = total + n\n    return total\n\nnums = [1, 2, 3]\nalias = nums\nresult = sum_list(alias)\n",
      ),
    ],
  },
  {
    title: "More Python Tricks",
    examples: [
      example(
        "decorators",
        "decorators",
        "def shout(fn):\n    def wrapped(text):\n        return fn(text).upper()\n    return wrapped\n\n@shout\ndef greet(name):\n    return 'hello ' + name\n\nprint(greet('ada'))\n",
      ),
      example(
        "generators",
        "generators",
        "def count(n):\n    i = 0\n    while i < n:\n        yield i\n        i = i + 1\n\nnums = list(count(3))\n",
      ),
      example(
        "gen-expr",
        "gen expr",
        "nums = [1, 2, 3]\nsquares = (n * n for n in nums)\nresult = list(squares)\n",
      ),
      example(
        "varargs",
        "varargs",
        "def total(*nums):\n    s = 0\n    for n in nums:\n        s = s + n\n    return s\n\nresult = total(1, 2, 3)\n",
      ),
      example(
        "exceptions",
        "exceptions",
        "try:\n    x = 1 / 0\nexcept ZeroDivisionError:\n    x = None\n",
      ),
      example(
        "for-else",
        "for-else",
        "found = None\nfor n in [1, 3, 5]:\n    if n == 4:\n        found = n\n        break\nelse:\n    found = 0\n",
      ),
      example(
        "nonlocal",
        "nonlocal",
        "def accumulator(start):\n    total = start\n    def add(n):\n        nonlocal total\n        total = total + n\n        return total\n    return add\n\nadd = accumulator(10)\nadd(1)\nadd(2)\n",
      ),
    ],
  },
];
