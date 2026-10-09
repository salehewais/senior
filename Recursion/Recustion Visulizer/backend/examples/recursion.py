"""Recursion examples. Each source is a complete function plus its starting data."""

from textwrap import dedent

CATEGORY = "Recursion"

LIST_NODE = """
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __repr__(self):
        parts = []
        node = self
        while node is not None and len(parts) < 12:
            parts.append(str(node.val))
            node = node.next
        return "->".join(parts)
"""

TREE_NODE = """
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

    def __repr__(self):
        if self.left is None and self.right is None:
            return str(self.val)
        left = "_" if self.left is None else repr(self.left)
        right = "_" if self.right is None else repr(self.right)
        return f"{self.val}[{left},{right}]"
"""


def _source(*parts: str) -> str:
    return "\n\n".join(dedent(part).strip() for part in parts) + "\n"


def _ex(example_id: str, title: str, call: str, source: str) -> dict[str, str]:
    return {
        "id": example_id,
        "title": title,
        "category": CATEGORY,
        "call": call,
        "source": source if source.endswith("\n") else source + "\n",
    }


EXAMPLES = [
    _ex(
        "fibonacci",
        "Fibonacci",
        "fib(5)",
        _source('''
        def fib(n):
            """Return the nth Fibonacci number."""
            if n < 2:
                return n
            return fib(n - 1) + fib(n - 2)
        '''),
    ),
    _ex(
        "reverse-string",
        "Reverse String",
        "reverseString(chars)",
        _source('''
        def reverseString(s):
            """Reverse the character list in place and return it as a string."""
            def rev(i, j):
                if i >= j:
                    return "".join(s)
                s[i], s[j] = s[j], s[i]
                return rev(i + 1, j - 1)

            return rev(0, len(s) - 1)


        chars = list("hello")
        '''),
    ),
    _ex(
        "merge-two-sorted-lists",
        "Merge Two Sorted Lists",
        "mergeTwoLists(list1, list2)",
        _source(
            LIST_NODE,
            '''
        def mergeTwoLists(list1, list2):
            """Merge two sorted lists by always linking the smaller head."""
            if list1 is None:
                return list2
            if list2 is None:
                return list1
            if list1.val <= list2.val:
                list1.next = mergeTwoLists(list1.next, list2)
                return list1
            list2.next = mergeTwoLists(list1, list2.next)
            return list2


        list1 = ListNode(1, ListNode(2, ListNode(4)))
        list2 = ListNode(1, ListNode(3, ListNode(4)))
        ''',
        ),
    ),
    _ex(
        "power",
        "Pow(x, n)",
        "myPow(2.0, 10)",
        _source('''
        def myPow(x: float, n: int) -> float:
            """Return x raised to n. The recursion lives in a nested helper."""
            if n < 0:
                x, n = 1 / x, -n

            def helper(x, n):
                if n == 0:
                    return 1.0
                half = helper(x, n // 2)
                if n % 2 == 0:
                    return half * half
                return half * half * x

            return helper(x, n)
        '''),
    ),
    _ex(
        "pascals-triangle",
        "Pascal's Triangle",
        "generate(5)",
        _source('''
        def generate(numRows):
            """Build the first numRows of Pascal's triangle from the row above."""
            if numRows == 1:
                return [[1]]
            rows = generate(numRows - 1)
            previous = rows[-1]
            row = [1]
            for i in range(len(previous) - 1):
                row.append(previous[i] + previous[i + 1])
            row.append(1)
            rows.append(row)
            return rows
        '''),
    ),
    _ex(
        "swap-nodes-in-pairs",
        "Swap Nodes in Pairs",
        "swapPairs(head)",
        _source(
            LIST_NODE,
            '''
        def swapPairs(head):
            """Swap every two nodes: A -> B -> rest becomes B -> A -> swapped rest."""
            if head is None or head.next is None:
                return head
            nxt = head.next
            head.next = swapPairs(nxt.next)
            nxt.next = head
            return nxt


        head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
        ''',
        ),
    ),
    _ex(
        "kth-symbol",
        "K-th Symbol in Grammar",
        "kthGrammar(4, 5)",
        _source('''
        def kthGrammar(n, k):
            """Row n is row n-1, then that row with 0 and 1 flipped. k is 1-based."""
            if n == 1:
                return 0
            half = 1 << (n - 2)
            if k <= half:
                return kthGrammar(n - 1, k)
            return 1 - kthGrammar(n - 1, k - half)
        '''),
    ),
    _ex(
        "add-two-numbers",
        "Add Two Numbers",
        "addTwoNumbers(l1, l2)",
        _source(
            LIST_NODE,
            '''
        def addTwoNumbers(l1, l2, carry=0):
            """Add two numbers stored as digit lists, least significant digit first."""
            if l1 is None and l2 is None and carry == 0:
                return None
            total = carry
            if l1 is not None:
                total += l1.val
                l1 = l1.next
            if l2 is not None:
                total += l2.val
                l2 = l2.next
            node = ListNode(total % 10)
            node.next = addTwoNumbers(l1, l2, total // 10)
            return node


        l1 = ListNode(2, ListNode(4, ListNode(3)))
        l2 = ListNode(5, ListNode(6, ListNode(4)))
        ''',
        ),
    ),
    _ex(
        "unique-bsts-ii",
        "Unique Binary Search Trees II",
        "generateTrees(3)",
        _source(
            TREE_NODE,
            '''
        def generateTrees(n):
            """Every binary search tree whose nodes are 1..n."""
            def build(lo, hi):
                if lo > hi:
                    return [None]
                trees = []
                for root in range(lo, hi + 1):
                    for left in build(lo, root - 1):
                        for right in build(root + 1, hi):
                            trees.append(TreeNode(root, left, right))
                return trees

            return build(1, n)
        '''),
    ),
    _ex(
        "decode-string",
        "Decode String",
        "decodeString(s)",
        _source('''
        def decodeString(s):
            """Expand k[text] by decoding the inside, then repeating it k times."""
            def read(i):
                parts = []
                while i < len(s) and s[i] != "]":
                    if s[i].isdigit():
                        count = 0
                        while s[i].isdigit():
                            count = count * 10 + int(s[i])
                            i += 1
                        inner, i = read(i + 1)
                        parts.append(inner * count)
                        i += 1
                    else:
                        parts.append(s[i])
                        i += 1
                return "".join(parts), i

            text, _end = read(0)
            return text


        s = "3[a2[c]]"
        '''),
    ),
    _ex(
        "factorial",
        "Factorial",
        "factorial(5)",
        _source('''
        def factorial(n):
            """Return n!."""
            if n <= 1:
                return 1
            return n * factorial(n - 1)
        '''),
    ),
    _ex(
        "binomial",
        "Binomial coefficient",
        "binomial(5, 2)",
        _source('''
        def binomial(n, k):
            """Return C(n, k) by Pascal's identity."""
            if k == 0 or k == n:
                return 1
            return binomial(n - 1, k - 1) + binomial(n - 1, k)
        '''),
    ),
    _ex(
        "subset-sum",
        "Subset sum",
        "subset_sum(0, 5)",
        _source('''
        nums = [3, 1, 4]


        def subset_sum(i, remaining):
            """True when a subset of nums[i:] adds up to remaining."""
            if remaining == 0:
                return True
            if i == len(nums) or remaining < 0:
                return False
            if subset_sum(i + 1, remaining - nums[i]):
                return True
            return subset_sum(i + 1, remaining)
        '''),
    ),
]
