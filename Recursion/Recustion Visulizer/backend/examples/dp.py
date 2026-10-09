"""Dynamic-programming examples, written as top-down recursion."""

from textwrap import dedent

CATEGORY = "Dynamic Programming"


def _source(*parts: str) -> str:
    return "\n\n".join(dedent(part).strip() for part in parts) + "\n"


def _ex(example_id: str, title: str, call: str, source: str) -> dict[str, str]:
    return {
        "id": example_id,
        "title": title,
        "category": CATEGORY,
        "call": call,
        "source": source,
    }


EXAMPLES = [
    _ex(
        "climbing-stairs",
        "Climbing Stairs",
        "climbStairs(n)",
        _source('''
        def climbStairs(n):
            """Ways to climb n stairs taking 1 or 2 at a time."""
            def ways(k):
                if k <= 1:
                    return 1
                return ways(k - 1) + ways(k - 2)

            return ways(n)


        n = 5
        '''),
    ),
    _ex(
        "house-robber",
        "House Robber",
        "rob(nums)",
        _source('''
        def rob(nums):
            """Most you can rob when two neighboring houses set off the alarm."""
            def take(i):
                if i >= len(nums):
                    return 0
                return max(nums[i] + take(i + 2), take(i + 1))

            return take(0)


        nums = [2, 7, 9, 3, 1]
        '''),
    ),
    _ex(
        "house-robber-ii",
        "House Robber II",
        "rob(nums)",
        _source('''
        def rob(nums):
            """Same robbery, but the first and last houses are neighbors."""
            if len(nums) == 1:
                return nums[0]

            def take(i, end):
                if i >= end:
                    return 0
                return max(nums[i] + take(i + 2, end), take(i + 1, end))

            return max(take(0, len(nums) - 1), take(1, len(nums)))


        nums = [2, 3, 2]
        '''),
    ),
    _ex(
        "longest-palindrome",
        "Longest Palindromic Substring",
        "longestPalindrome(s)",
        _source('''
        def longestPalindrome(s):
            """Grow every center while the outer characters still match."""
            def expand(lo, hi):
                if lo < 0 or hi >= len(s) or s[lo] != s[hi]:
                    return s[lo + 1:hi]
                return expand(lo - 1, hi + 1)

            best = ""
            for i in range(len(s)):
                for candidate in (expand(i, i), expand(i, i + 1)):
                    if len(candidate) > len(best):
                        best = candidate
            return best


        s = "babad"
        '''),
    ),
    _ex(
        "coin-change",
        "Coin Change",
        "coinChange(coins, amount)",
        _source('''
        def coinChange(coins, amount):
            """Fewest coins that add up to amount. -1 when it cannot be done."""
            memo = {}

            def need(i, left):
                if left == 0:
                    return 0
                if i == len(coins) or left < 0:
                    return -1
                key = (i, left)
                if key in memo:
                    return memo[key]
                skip = need(i + 1, left)
                take = need(i, left - coins[i])
                if take >= 0:
                    take += 1
                if skip < 0:
                    best = take
                elif take < 0:
                    best = skip
                else:
                    best = min(skip, take)
                memo[key] = best
                return best

            return need(0, amount)


        coins = [1, 2, 5]
        amount = 11
        '''),
    ),
    _ex(
        "longest-increasing-subsequence",
        "Longest Increasing Subsequence",
        "lengthOfLIS(nums)",
        _source('''
        def lengthOfLIS(nums):
            """Length of the longest strictly increasing subsequence."""
            memo = {}

            def best(i, prev):
                if i == len(nums):
                    return 0
                key = (i, prev)
                if key in memo:
                    return memo[key]
                skip = best(i + 1, prev)
                take = 0
                if prev < 0 or nums[i] > nums[prev]:
                    take = 1 + best(i + 1, i)
                memo[key] = max(skip, take)
                return memo[key]

            return best(0, -1)


        nums = [10, 9, 2, 5, 3, 7, 101, 18]
        '''),
    ),
    _ex(
        "partition-equal-subset",
        "Partition Equal Subset Sum",
        "canPartition(nums)",
        _source('''
        def canPartition(nums):
            """True when the numbers can be split into two groups with the same sum."""
            total = sum(nums)
            if total % 2:
                return False
            target = total // 2

            def fill(i, left):
                if left == 0:
                    return True
                if i == len(nums) or left < 0:
                    return False
                return fill(i + 1, left - nums[i]) or fill(i + 1, left)

            return fill(0, target)


        nums = [1, 5, 11, 5]
        '''),
    ),
    _ex(
        "unique-paths",
        "Unique Paths",
        "uniquePaths(m, n)",
        _source('''
        def uniquePaths(m, n):
            """Paths from the top-left corner to the bottom-right, moving only right or down."""
            memo = {}

            def ways(r, c):
                if r == m - 1 and c == n - 1:
                    return 1
                if r >= m or c >= n:
                    return 0
                if (r, c) in memo:
                    return memo[(r, c)]
                memo[(r, c)] = ways(r + 1, c) + ways(r, c + 1)
                return memo[(r, c)]

            return ways(0, 0)


        m = 3
        n = 7
        '''),
    ),
    _ex(
        "edit-distance",
        "Edit Distance",
        "minDistance(word1, word2)",
        _source('''
        def minDistance(word1, word2):
            """Fewest inserts, deletes, and replacements that turn word1 into word2."""
            memo = {}

            def dist(i, j):
                if i == len(word1):
                    return len(word2) - j
                if j == len(word2):
                    return len(word1) - i
                key = (i, j)
                if key in memo:
                    return memo[key]
                if word1[i] == word2[j]:
                    memo[key] = dist(i + 1, j + 1)
                else:
                    memo[key] = 1 + min(
                        dist(i + 1, j),
                        dist(i, j + 1),
                        dist(i + 1, j + 1),
                    )
                return memo[key]

            return dist(0, 0)


        word1 = "horse"
        word2 = "ros"
        '''),
    ),
    _ex(
        "longest-common-subsequence",
        "Longest Common Subsequence",
        "longestCommonSubsequence(text1, text2)",
        _source('''
        def longestCommonSubsequence(text1, text2):
            """Length of the longest subsequence shared by both strings."""
            memo = {}

            def best(i, j):
                if i == len(text1) or j == len(text2):
                    return 0
                key = (i, j)
                if key in memo:
                    return memo[key]
                if text1[i] == text2[j]:
                    memo[key] = 1 + best(i + 1, j + 1)
                else:
                    memo[key] = max(best(i + 1, j), best(i, j + 1))
                return memo[key]

            return best(0, 0)


        text1 = "abcde"
        text2 = "ace"
        '''),
    ),
]
