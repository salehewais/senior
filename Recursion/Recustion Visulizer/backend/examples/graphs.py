"""Graph examples. Each search is a depth-first recursion on a small graph."""

from textwrap import dedent

CATEGORY = "Graphs"


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
        "number-of-islands",
        "Number of Islands",
        "numIslands(grid)",
        _source('''
        def numIslands(grid):
            """Count islands of land ("1"). A flood-fill sinks each one."""
            rows, cols = len(grid), len(grid[0])

            def sink(r, c):
                if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1":
                    return
                grid[r][c] = "0"
                sink(r + 1, c)
                sink(r - 1, c)
                sink(r, c + 1)
                sink(r, c - 1)

            count = 0
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == "1":
                        sink(r, c)
                        count += 1
            return count


        grid = [
            ["1", "1", "0", "0", "0"],
            ["1", "1", "0", "0", "0"],
            ["0", "0", "1", "0", "0"],
            ["0", "0", "0", "1", "1"],
        ]
        '''),
    ),
    _ex(
        "clone-graph",
        "Clone Graph",
        "cloneGraph(start)",
        _source('''
        class Node:
            def __init__(self, val=0, neighbors=None):
                self.val = val
                self.neighbors = neighbors if neighbors is not None else []

            def __repr__(self):
                return f"Node({self.val})"


        def cloneGraph(node):
            """Deep-copy a connected undirected graph."""
            copies = {}

            def clone(current):
                if current is None:
                    return None
                if current.val in copies:
                    return copies[current.val]
                copy = Node(current.val)
                copies[current.val] = copy
                for nei in current.neighbors:
                    copy.neighbors.append(clone(nei))
                return copy

            return clone(node)


        nodes = [Node(i) for i in range(1, 5)]
        nodes[0].neighbors = [nodes[1], nodes[3]]
        nodes[1].neighbors = [nodes[0], nodes[2]]
        nodes[2].neighbors = [nodes[1], nodes[3]]
        nodes[3].neighbors = [nodes[0], nodes[2]]
        start = nodes[0]
        '''),
    ),
    _ex(
        "max-area-of-island",
        "Max Area of Island",
        "maxAreaOfIsland(grid)",
        _source('''
        def maxAreaOfIsland(grid):
            """Size of the largest island of land (1)."""
            rows, cols = len(grid), len(grid[0])

            def area(r, c):
                if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != 1:
                    return 0
                grid[r][c] = 0
                return 1 + area(r + 1, c) + area(r - 1, c) + area(r, c + 1) + area(r, c - 1)

            best = 0
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == 1:
                        best = max(best, area(r, c))
            return best


        grid = [
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0],
            [0, 0, 0, 1, 1],
        ]
        '''),
    ),
    _ex(
        "course-schedule",
        "Course Schedule",
        "canFinish(numCourses, prerequisites)",
        _source('''
        def canFinish(numCourses, prerequisites):
            """True when the courses have no cycle, so every one can be finished."""
            graph = {course: [] for course in range(numCourses)}
            for course, earlier in prerequisites:
                graph[earlier].append(course)
            state = [0] * numCourses

            def visit(course):
                if state[course] == 1:
                    return False
                if state[course] == 2:
                    return True
                state[course] = 1
                for nxt in graph[course]:
                    if not visit(nxt):
                        return False
                state[course] = 2
                return True

            return all(visit(course) for course in range(numCourses))


        numCourses = 4
        prerequisites = [[1, 0], [2, 0], [3, 1], [3, 2]]
        '''),
    ),
    _ex(
        "pacific-atlantic",
        "Pacific Atlantic Water Flow",
        "pacificAtlantic(heights)",
        _source('''
        def pacificAtlantic(heights):
            """Cells that can reach both the Pacific (top, left) and the Atlantic (bottom, right)."""
            rows, cols = len(heights), len(heights[0])

            def reach(r, c, prev, seen):
                if not (0 <= r < rows and 0 <= c < cols) or (r, c) in seen:
                    return
                if heights[r][c] < prev:
                    return
                seen.add((r, c))
                height = heights[r][c]
                reach(r + 1, c, height, seen)
                reach(r - 1, c, height, seen)
                reach(r, c + 1, height, seen)
                reach(r, c - 1, height, seen)

            pacific = set()
            atlantic = set()
            for c in range(cols):
                reach(0, c, heights[0][c], pacific)
                reach(rows - 1, c, heights[rows - 1][c], atlantic)
            for r in range(rows):
                reach(r, 0, heights[r][0], pacific)
                reach(r, cols - 1, heights[r][cols - 1], atlantic)
            return [list(cell) for cell in sorted(pacific & atlantic)]


        heights = [
            [1, 2, 2, 3, 5],
            [3, 2, 3, 4, 4],
            [2, 4, 5, 3, 1],
            [6, 7, 1, 4, 5],
            [5, 1, 1, 2, 4],
        ]
        '''),
    ),
    _ex(
        "rotting-oranges",
        "Rotting Oranges",
        "orangesRotting(grid)",
        _source('''
        def orangesRotting(grid):
            """Minutes until every fresh orange is rotten. -1 if some orange stays fresh."""
            rows, cols = len(grid), len(grid[0])
            best = [[None] * cols for _ in range(rows)]

            def spread(r, c, minute):
                if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] == 0:
                    return
                if best[r][c] is not None and minute >= best[r][c]:
                    return
                best[r][c] = minute
                spread(r + 1, c, minute + 1)
                spread(r - 1, c, minute + 1)
                spread(r, c + 1, minute + 1)
                spread(r, c - 1, minute + 1)

            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == 2:
                        spread(r, c, 0)
            answer = 0
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c] == 1:
                        if best[r][c] is None:
                            return -1
                        answer = max(answer, best[r][c])
            return answer


        grid = [
            [2, 1, 1],
            [1, 1, 0],
            [0, 1, 1],
        ]
        '''),
    ),
    _ex(
        "graph-valid-tree",
        "Graph Valid Tree",
        "validTree(n, edges)",
        _source('''
        def validTree(n, edges):
            """True when the edges form a tree: connected, and no cycle."""
            if len(edges) != n - 1:
                return False
            graph = {node: [] for node in range(n)}
            for a, b in edges:
                graph[a].append(b)
                graph[b].append(a)
            seen = set()

            def walk(node, parent):
                if node in seen:
                    return False
                seen.add(node)
                for nei in graph[node]:
                    if nei == parent:
                        continue
                    if not walk(nei, node):
                        return False
                return True

            return walk(0, -1) and len(seen) == n


        n = 5
        edges = [[0, 1], [0, 2], [0, 3], [1, 4]]
        '''),
    ),
    _ex(
        "word-ladder",
        "Word Ladder",
        "ladderLength(beginWord, endWord, wordList)",
        _source('''
        def ladderLength(beginWord, endWord, wordList):
            """Length of the shortest word ladder. Each step changes one letter."""
            words = set(wordList)
            if endWord not in words:
                return 0

            def search(word, seen):
                if word == endWord:
                    return 1
                best = 0
                for i in range(len(word)):
                    for ch in "abcdefghijklmnopqrstuvwxyz":
                        if ch == word[i]:
                            continue
                        nxt = word[:i] + ch + word[i + 1:]
                        if nxt not in words or nxt in seen:
                            continue
                        seen.add(nxt)
                        got = search(nxt, seen)
                        seen.remove(nxt)
                        if got and (best == 0 or got + 1 < best):
                            best = got + 1
                return best

            return search(beginWord, {beginWord})


        beginWord = "hit"
        endWord = "cog"
        wordList = ["hot", "dot", "dog", "lot", "log", "cog"]
        '''),
    ),
    _ex(
        "network-delay",
        "Network Delay Time",
        "networkDelayTime(times, n, k)",
        _source('''
        def networkDelayTime(times, n, k):
            """How long until a signal from k reaches every node. -1 if some node is missed."""
            graph = {node: [] for node in range(1, n + 1)}
            for src, dst, weight in times:
                graph[src].append((dst, weight))
            best = {k: 0}

            def relax(node):
                for nei, weight in graph[node]:
                    cand = best[node] + weight
                    if nei not in best or cand < best[nei]:
                        best[nei] = cand
                        relax(nei)

            relax(k)
            if len(best) < n:
                return -1
            return max(best.values())


        times = [[2, 1, 1], [2, 3, 1], [3, 4, 1]]
        n = 4
        k = 2
        '''),
    ),
]
