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
    _ex(
        "reverse-linked-list",
        "Reverse Linked List",
        "reverseList(head)",
        _source(
            LIST_NODE,
            '''
        def reverseList(head):
            """Reverse the list by reversing the tail, then pointing it back."""
            if head is None or head.next is None:
                return head
            new_head = reverseList(head.next)
            head.next.next = head
            head.next = None
            return new_head


        head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
        ''',
        ),
    ),
    _ex(
        "remove-linked-list-elements",
        "Remove Linked List Elements",
        "removeElements(head, 6)",
        _source(
            LIST_NODE,
            '''
        def removeElements(head, val):
            """Drop every node whose value is val, then return the rest."""
            if head is None:
                return None
            head.next = removeElements(head.next, val)
            if head.val == val:
                return head.next
            return head


        head = ListNode(1, ListNode(2, ListNode(6, ListNode(3, ListNode(6)))))
        ''',
        ),
    ),
    _ex(
        "power-of-two",
        "Power of Two",
        "isPowerOfTwo(16)",
        _source('''
        def isPowerOfTwo(n):
            """True when n can be halved down to 1."""
            if n == 1:
                return True
            if n <= 0 or n % 2 != 0:
                return False
            return isPowerOfTwo(n // 2)
        '''),
    ),
    _ex(
        "power-of-three",
        "Power of Three",
        "isPowerOfThree(27)",
        _source('''
        def isPowerOfThree(n):
            """True when n can be divided by 3 down to 1."""
            if n == 1:
                return True
            if n <= 0 or n % 3 != 0:
                return False
            return isPowerOfThree(n // 3)
        '''),
    ),
    _ex(
        "power-of-four",
        "Power of Four",
        "isPowerOfFour(64)",
        _source('''
        def isPowerOfFour(n):
            """True when n can be divided by 4 down to 1."""
            if n == 1:
                return True
            if n <= 0 or n % 4 != 0:
                return False
            return isPowerOfFour(n // 4)
        '''),
    ),
    _ex(
        "palindrome-linked-list",
        "Palindrome Linked List",
        "isPalindrome(head)",
        _source(
            LIST_NODE,
            '''
        def isPalindrome(head):
            """Walk to the end, then compare nodes on the way back."""
            front = head

            def check(node):
                nonlocal front
                if node is None:
                    return True
                if not check(node.next):
                    return False
                if front.val != node.val:
                    return False
                front = front.next
                return True

            return check(head)


        head = ListNode(1, ListNode(2, ListNode(2, ListNode(1))))
        ''',
        ),
    ),
    _ex(
        "palindrome-linked-list-v2",
        "Palindrome Linked List v2",
        "isPalindrome(head)",
        _source(
            "from typing import Optional",
            LIST_NODE,
            '''
        class Solution:
            def __repr__(self):
                return "Solution"

            def isPalindrome(self, head: Optional[ListNode]) -> bool:
                # 1. Set a pointer at the very beginning that we can manipulate globally
                self.curr = head
                return self.solve(head)

            def solve(self, head: Optional[ListNode]) -> bool:
                # Base case: hit the end of the list
                if head is None:
                    return True

                # 2. Dive deep to the end first.
                # 'ans' holds whether everything deeper down matched.
                ans = self.solve(head.next) and head.val == self.curr.val

                # 3. As we come back up, move our front pointer forward
                self.curr = self.curr.next

                return ans


        solution = Solution()
        isPalindrome = solution.isPalindrome
        head = ListNode(1, ListNode(2, ListNode(2, ListNode(1))))
        ''',
        ),
    ),
    _ex(
        "kth-character",
        "Find the K-th Character in String Game I",
        "kthCharacter(10)",
        _source('''
        def kthCharacter(k):
            """Each step appends the word with every letter shifted by one."""
            if k == 1:
                return "a"
            half = 1
            while half * 2 < k:
                half *= 2
            previous = kthCharacter(k - half)
            return chr(ord(previous) + 1)
        '''),
    ),
    _ex(
        "elimination-game",
        "Elimination Game",
        "lastRemaining(9)",
        _source('''
        def lastRemaining(n):
            """Remove every other number, alternating direction, until one remains."""
            def remaining(n, left):
                if n == 1:
                    return 1
                if left or n % 2 == 1:
                    return 2 * remaining(n // 2, not left)
                return 2 * remaining(n // 2, not left) - 1

            return remaining(n, True)
        '''),
    ),
    _ex(
        "find-kth-bit",
        "Find Kth Bit in Nth Binary String",
        "findKthBit(4, 11)",
        _source('''
        def findKthBit(n, k):
            """S(n) is S(n-1), then 1, then S(n-1) reversed and flipped."""
            if n == 1:
                return "0"
            length = (1 << n) - 1
            mid = length // 2 + 1
            if k == mid:
                return "1"
            if k < mid:
                return findKthBit(n - 1, k)
            mirrored = findKthBit(n - 1, length - k + 1)
            return "0" if mirrored == "1" else "1"
        '''),
    ),
    _ex(
        "circular-game",
        "Find the Winner of the Circular Game",
        "findTheWinner(5, 2)",
        _source('''
        def findTheWinner(n, k):
            """Every kth friend leaves. Positions are counted from 0, then shifted."""
            def winner(n):
                if n == 1:
                    return 0
                return (winner(n - 1) + k) % n

            return winner(n) + 1
        '''),
    ),
]
