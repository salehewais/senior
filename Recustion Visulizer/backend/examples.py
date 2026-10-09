"""Full Python functions the editor can load. Not body-only snippets."""

EXAMPLES = [
    {
        "id": "fibonacci",
        "title": "Fibonacci",
        "call": "fib(5)",
        "source": '''def fib(n):
    """Return the nth Fibonacci number."""
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
''',
    },
    {
        "id": "factorial",
        "title": "Factorial",
        "call": "factorial(5)",
        "source": '''def factorial(n):
    """Return n!."""
    if n <= 1:
        return 1
    return n * factorial(n - 1)
''',
    },
    {
        "id": "binomial",
        "title": "Binomial coefficient",
        "call": "binomial(5, 2)",
        "source": '''def binomial(n, k):
    """Return C(n, k) by Pascal's identity."""
    if k == 0 or k == n:
        return 1
    return binomial(n - 1, k - 1) + binomial(n - 1, k)
''',
    },
    {
        "id": "subset-sum",
        "title": "Subset sum",
        "call": "subset_sum(0, 5)",
        "source": '''nums = [3, 1, 4]


def subset_sum(i, remaining):
    """True when a subset of nums[i:] adds up to remaining."""
    if remaining == 0:
        return True
    if i == len(nums) or remaining < 0:
        return False
    if subset_sum(i + 1, remaining - nums[i]):
        return True
    return subset_sum(i + 1, remaining)
''',
    },
    {
        "id": "power",
        "title": "Power",
        "call": "myPow(2.0, 10)",
        "source": '''def myPow(x: float, n: int) -> float:
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
''',
    },
]
