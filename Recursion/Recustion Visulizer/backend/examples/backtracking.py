"""Backtracking examples. Inputs are small enough to finish under the call cap."""

from textwrap import dedent

CATEGORY = "Backtracking"


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
        "subsets",
        "Subsets",
        "subsets(nums)",
        _source('''
        def subsets(nums):
            """Every subset, by taking or skipping each number."""
            out = []

            def choose(i, path):
                if i == len(nums):
                    out.append(path[:])
                    return
                path.append(nums[i])
                choose(i + 1, path)
                path.pop()
                choose(i + 1, path)

            choose(0, [])
            return out


        nums = [1, 2, 3]
        '''),
    ),
    _ex(
        "subsets-ii",
        "Subsets II",
        "subsetsWithDup(nums)",
        _source('''
        def subsetsWithDup(nums):
            """Every subset when the input may contain duplicates."""
            nums = sorted(nums)
            out = []

            def choose(start, path):
                out.append(path[:])
                for i in range(start, len(nums)):
                    if i > start and nums[i] == nums[i - 1]:
                        continue
                    path.append(nums[i])
                    choose(i + 1, path)
                    path.pop()

            choose(0, [])
            return out


        nums = [1, 2, 2]
        '''),
    ),
    _ex(
        "permutations",
        "Permutations",
        "permute(nums)",
        _source('''
        def permute(nums):
            """Every ordering of the numbers."""
            out = []
            used = [False] * len(nums)

            def choose(path):
                if len(path) == len(nums):
                    out.append(path[:])
                    return
                for i, num in enumerate(nums):
                    if used[i]:
                        continue
                    used[i] = True
                    path.append(num)
                    choose(path)
                    path.pop()
                    used[i] = False

            choose([])
            return out


        nums = [1, 2, 3]
        '''),
    ),
    _ex(
        "permutations-ii",
        "Permutations II",
        "permuteUnique(nums)",
        _source('''
        def permuteUnique(nums):
            """Every distinct ordering when the input may contain duplicates."""
            nums = sorted(nums)
            out = []
            used = [False] * len(nums)

            def choose(path):
                if len(path) == len(nums):
                    out.append(path[:])
                    return
                for i, num in enumerate(nums):
                    if used[i]:
                        continue
                    if i and nums[i] == nums[i - 1] and not used[i - 1]:
                        continue
                    used[i] = True
                    path.append(num)
                    choose(path)
                    path.pop()
                    used[i] = False

            choose([])
            return out


        nums = [1, 1, 2]
        '''),
    ),
    _ex(
        "combination-sum",
        "Combination Sum",
        "combinationSum(candidates, target)",
        _source('''
        def combinationSum(candidates, target):
            """Combinations that add up to target. A number may be reused."""
            out = []

            def choose(start, left, path):
                if left == 0:
                    out.append(path[:])
                    return
                for i in range(start, len(candidates)):
                    if candidates[i] > left:
                        continue
                    path.append(candidates[i])
                    choose(i, left - candidates[i], path)
                    path.pop()

            choose(0, target, [])
            return out


        candidates = [2, 3, 6, 7]
        target = 7
        '''),
    ),
    _ex(
        "combination-sum-ii",
        "Combination Sum II",
        "combinationSum2(candidates, target)",
        _source('''
        def combinationSum2(candidates, target):
            """Combinations that add up to target. Each number is used at most once."""
            candidates = sorted(candidates)
            out = []

            def choose(start, left, path):
                if left == 0:
                    out.append(path[:])
                    return
                for i in range(start, len(candidates)):
                    if candidates[i] > left:
                        break
                    if i > start and candidates[i] == candidates[i - 1]:
                        continue
                    path.append(candidates[i])
                    choose(i + 1, left - candidates[i], path)
                    path.pop()

            choose(0, target, [])
            return out


        candidates = [10, 1, 2, 7, 6, 1, 5]
        target = 8
        '''),
    ),
    _ex(
        "palindrome-partitioning",
        "Palindrome Partitioning",
        "partition(s)",
        _source('''
        def partition(s):
            """Every way to cut the string so each piece is a palindrome."""
            out = []

            def choose(start, path):
                if start == len(s):
                    out.append(path[:])
                    return
                for end in range(start + 1, len(s) + 1):
                    piece = s[start:end]
                    if piece != piece[::-1]:
                        continue
                    path.append(piece)
                    choose(end, path)
                    path.pop()

            choose(0, [])
            return out


        s = "aab"
        '''),
    ),
    _ex(
        "n-queens",
        "N-Queens",
        "solveNQueens(n)",
        _source('''
        def solveNQueens(n):
            """Place n queens so none share a row, column, or diagonal."""
            cols = set()
            diag = set()
            anti = set()
            board = [["."] * n for _ in range(n)]
            out = []

            def place(row):
                if row == n:
                    out.append(["".join(line) for line in board])
                    return
                for col in range(n):
                    if col in cols or (row - col) in diag or (row + col) in anti:
                        continue
                    cols.add(col)
                    diag.add(row - col)
                    anti.add(row + col)
                    board[row][col] = "Q"
                    place(row + 1)
                    board[row][col] = "."
                    cols.remove(col)
                    diag.remove(row - col)
                    anti.remove(row + col)

            place(0)
            return out


        n = 4
        '''),
    ),
    _ex(
        "word-search",
        "Word Search",
        "exist(board, word)",
        _source('''
        def exist(board, word):
            """True when the word can be traced through adjacent cells."""
            rows, cols = len(board), len(board[0])

            def search(r, c, i):
                if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
                    return False
                if i == len(word) - 1:
                    return True
                saved = board[r][c]
                board[r][c] = "#"
                found = (
                    search(r + 1, c, i + 1)
                    or search(r - 1, c, i + 1)
                    or search(r, c + 1, i + 1)
                    or search(r, c - 1, i + 1)
                )
                board[r][c] = saved
                return found

            for r in range(rows):
                for c in range(cols):
                    if search(r, c, 0):
                        return True
            return False


        board = [
            ["A", "B", "C", "E"],
            ["S", "F", "C", "S"],
            ["A", "D", "E", "E"],
        ]
        word = "ABCCED"
        '''),
    ),
    _ex(
        "sudoku-solver",
        "Sudoku Solver",
        "solveSudoku(board)",
        _source('''
        def can_place(board, row, col, digit):
            for i in range(9):
                if board[row][i] == digit or board[i][col] == digit:
                    return False
                box_row = 3 * (row // 3) + i // 3
                box_col = 3 * (col // 3) + i % 3
                if board[box_row][box_col] == digit:
                    return False
            return True


        def solveSudoku(board):
            """Fill the blank cells. Only a few cells are open, so the search stays small."""
            blanks = [(r, c) for r in range(9) for c in range(9) if board[r][c] == "."]

            def solve(k):
                if k == len(blanks):
                    return True
                row, col = blanks[k]
                for digit in "123456789":
                    if not can_place(board, row, col, digit):
                        continue
                    board[row][col] = digit
                    if solve(k + 1):
                        return True
                    board[row][col] = "."
                return False

            solve(0)
            return board


        board = [
            [".", "3", "4", "6", "7", "8", "9", "1", "2"],
            ["6", ".", "2", "1", "9", "5", "3", "4", "8"],
            ["1", "9", "8", "3", "4", "2", "5", "6", "7"],
            ["8", "5", "9", "7", "6", "1", "4", "2", "3"],
            ["4", "2", "6", "8", ".", "3", "7", "9", "1"],
            ["7", "1", "3", "9", "2", "4", "8", "5", "6"],
            ["9", "6", "1", "5", "3", "7", "2", "8", "4"],
            ["2", "8", "7", "4", "1", "9", "6", "3", "5"],
            ["3", "4", "5", "2", "8", "6", "1", "7", "."],
        ]
        '''),
    ),
    _ex(
        "letter-combinations",
        "Letter Combinations of a Phone Number",
        "letterCombinations(digits)",
        _source('''
        def letterCombinations(digits):
            """Every string the digits could spell on a phone keypad."""
            if not digits:
                return []
            keys = {
                "2": "abc",
                "3": "def",
                "4": "ghi",
                "5": "jkl",
                "6": "mno",
                "7": "pqrs",
                "8": "tuv",
                "9": "wxyz",
            }
            out = []

            def choose(i, path):
                if i == len(digits):
                    out.append("".join(path))
                    return
                for ch in keys[digits[i]]:
                    path.append(ch)
                    choose(i + 1, path)
                    path.pop()

            choose(0, [])
            return out


        digits = "23"
        '''),
    ),
    _ex(
        "combination-sum-iii",
        "Combination Sum III",
        "combinationSum3(k, n)",
        _source('''
        def combinationSum3(k, n):
            """k distinct digits from 1..9 that add up to n."""
            out = []

            def choose(start, left, path):
                if len(path) == k:
                    if left == 0:
                        out.append(path[:])
                    return
                for num in range(start, 10):
                    if num > left:
                        break
                    path.append(num)
                    choose(num + 1, left - num, path)
                    path.pop()

            choose(1, n, [])
            return out


        k = 3
        n = 7
        '''),
    ),
    _ex(
        "restore-ip-addresses",
        "Restore IP Addresses",
        "restoreIpAddresses(s)",
        _source('''
        def restoreIpAddresses(s):
            """Every way to cut the string into four legal IP numbers."""
            out = []

            def choose(start, parts):
                if len(parts) == 4:
                    if start == len(s):
                        out.append(".".join(parts))
                    return
                remaining = 4 - len(parts)
                if len(s) - start < remaining or len(s) - start > remaining * 3:
                    return
                for length in range(1, 4):
                    if start + length > len(s):
                        break
                    piece = s[start:start + length]
                    if (len(piece) > 1 and piece[0] == "0") or int(piece) > 255:
                        continue
                    parts.append(piece)
                    choose(start + length, parts)
                    parts.pop()

            choose(0, [])
            return out


        s = "25525511135"
        '''),
    ),
    _ex(
        "partition-k-subsets",
        "Partition to K Equal Sum Subsets",
        "canPartitionKSubsets(nums, k)",
        _source('''
        def canPartitionKSubsets(nums, k):
            """True when the numbers can be split into k groups with the same sum."""
            total = sum(nums)
            if total % k:
                return False
            target = total // k
            nums = sorted(nums, reverse=True)
            if nums[0] > target:
                return False
            used = [False] * len(nums)

            def fill(start, left, groups):
                if groups == 0:
                    return True
                if left == 0:
                    return fill(0, target, groups - 1)
                for i in range(start, len(nums)):
                    if used[i] or nums[i] > left:
                        continue
                    if i and nums[i] == nums[i - 1] and not used[i - 1]:
                        continue
                    used[i] = True
                    if fill(i + 1, left - nums[i], groups):
                        return True
                    used[i] = False
                return False

            return fill(0, target, k)


        nums = [4, 3, 2, 3, 5, 2, 1]
        k = 4
        '''),
    ),
    _ex(
        "word-search-ii",
        "Word Search II",
        "findWords(board, words)",
        _source('''
        def findWords(board, words):
            """Every word that can be traced on the board. A trie prunes dead ends."""
            trie = {}
            for word in words:
                node = trie
                for ch in word:
                    node = node.setdefault(ch, {})
                node["#"] = word

            rows, cols = len(board), len(board[0])
            found = []

            def search(r, c, node):
                if not (0 <= r < rows and 0 <= c < cols):
                    return
                ch = board[r][c]
                nxt = node.get(ch)
                if nxt is None:
                    return
                if "#" in nxt:
                    found.append(nxt.pop("#"))
                board[r][c] = "#"
                search(r + 1, c, nxt)
                search(r - 1, c, nxt)
                search(r, c + 1, nxt)
                search(r, c - 1, nxt)
                board[r][c] = ch

            for r in range(rows):
                for c in range(cols):
                    search(r, c, trie)
            return found


        board = [
            ["o", "a", "a", "n"],
            ["e", "t", "a", "e"],
            ["i", "h", "k", "r"],
            ["i", "f", "l", "v"],
        ]
        words = ["oath", "pea", "eat", "rain"]
        '''),
    ),
    _ex(
        "matchsticks-to-square",
        "Matchsticks to Square",
        "makesquare(matchsticks)",
        _source('''
        def makesquare(matchsticks):
            """True when the sticks can form four equal sides of a square."""
            total = sum(matchsticks)
            if total % 4:
                return False
            side = total // 4
            matchsticks = sorted(matchsticks, reverse=True)
            if matchsticks[0] > side:
                return False

            def fill(i, sides):
                if i == len(matchsticks):
                    return True
                for s in range(4):
                    if sides[s] + matchsticks[i] <= side:
                        sides[s] += matchsticks[i]
                        if fill(i + 1, sides):
                            return True
                        sides[s] -= matchsticks[i]
                    if sides[s] == 0:
                        break
                return False

            return fill(0, [0, 0, 0, 0])


        matchsticks = [1, 1, 2, 2, 2]
        '''),
    ),
    _ex(
        "n-queens-ii",
        "N-Queens II",
        "totalNQueens(n)",
        _source('''
        def totalNQueens(n):
            """How many ways n queens can be placed. The boards themselves are not stored."""
            cols = set()
            diag = set()
            anti = set()

            def place(row):
                if row == n:
                    return 1
                count = 0
                for col in range(n):
                    if col in cols or (row - col) in diag or (row + col) in anti:
                        continue
                    cols.add(col)
                    diag.add(row - col)
                    anti.add(row + col)
                    count += place(row + 1)
                    cols.remove(col)
                    diag.remove(row - col)
                    anti.remove(row + col)
                return count

            return place(0)


        n = 4
        '''),
    ),
    _ex(
        "non-decreasing-subsequences",
        "Non-decreasing Subsequences",
        "findSubsequences(nums)",
        _source('''
        def findSubsequences(nums):
            """Every subsequence of length at least 2 that never steps downward."""
            out = []

            def choose(start, path):
                if len(path) >= 2:
                    out.append(path[:])
                used_here = set()
                for i in range(start, len(nums)):
                    if nums[i] in used_here:
                        continue
                    if path and nums[i] < path[-1]:
                        continue
                    used_here.add(nums[i])
                    path.append(nums[i])
                    choose(i + 1, path)
                    path.pop()

            choose(0, [])
            return out


        nums = [4, 6, 7, 7]
        '''),
    ),
    _ex(
        "beautiful-arrangement",
        "Beautiful Arrangement",
        "countArrangement(n)",
        _source('''
        def countArrangement(n):
            """Permutations where each position i divides its value, or the value divides i."""
            def place(pos, used):
                if pos > n:
                    return 1
                count = 0
                for num in range(1, n + 1):
                    if used[num]:
                        continue
                    if num % pos and pos % num:
                        continue
                    used[num] = True
                    count += place(pos + 1, used)
                    used[num] = False
                return count

            return place(1, [False] * (n + 1))


        n = 4
        '''),
    ),
    _ex(
        "split-descending",
        "Splitting a String Into Descending Consecutive Values",
        "splitString(s)",
        _source('''
        def splitString(s):
            """True when the string can be cut into numbers that fall by 1 each time."""
            def choose(start, prev, parts):
                if start == len(s):
                    return parts >= 2
                for end in range(start + 1, len(s) + 1):
                    if end - start > 1 and s[start] == "0":
                        break
                    val = int(s[start:end])
                    if prev is not None and val != prev - 1:
                        if val < prev - 1:
                            break
                        continue
                    if choose(end, val, parts + 1):
                        return True
                return False

            return choose(0, None, 0)


        s = "1098"
        '''),
    ),
]
