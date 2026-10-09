"""Binary-tree examples. Each tree is built in the same source the tracer runs."""

from textwrap import dedent

CATEGORY = "Trees"

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
        "source": source,
    }


EXAMPLES = [
    _ex(
        "max-depth",
        "Maximum Depth of Binary Tree",
        "maxDepth(root)",
        _source(
            TREE_NODE,
            '''
            def maxDepth(root):
                """Longest path from this node down to a leaf, counted in nodes."""
                if root is None:
                    return 0
                return 1 + max(maxDepth(root.left), maxDepth(root.right))


            # 3[9,20[15,7]]
            root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
            ''',
        ),
    ),
    _ex(
        "invert-tree",
        "Invert Binary Tree",
        "invertTree(root)",
        _source(
            TREE_NODE,
            '''
            def invertTree(root):
                """Swap every left and right child."""
                if root is None:
                    return None
                root.left, root.right = invertTree(root.right), invertTree(root.left)
                return root


            # 4[2[1,3],7[6,9]]
            root = TreeNode(
                4,
                TreeNode(2, TreeNode(1), TreeNode(3)),
                TreeNode(7, TreeNode(6), TreeNode(9)),
            )
            ''',
        ),
    ),
    _ex(
        "same-tree",
        "Same Tree",
        "isSameTree(p, q)",
        _source(
            TREE_NODE,
            '''
            def isSameTree(p, q):
                """True when both trees have the same shape and the same values."""
                if p is None and q is None:
                    return True
                if p is None or q is None or p.val != q.val:
                    return False
                return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)


            p = TreeNode(1, TreeNode(2), TreeNode(3))
            q = TreeNode(1, TreeNode(2), TreeNode(3))
            ''',
        ),
    ),
    _ex(
        "level-order",
        "Binary Tree Level Order Traversal",
        "levelOrder(root)",
        _source(
            TREE_NODE,
            '''
            def levelOrder(root):
                """Collect values level by level with a depth-first walk."""
                levels = []

                def walk(node, depth):
                    if node is None:
                        return
                    if len(levels) == depth:
                        levels.append([])
                    levels[depth].append(node.val)
                    walk(node.left, depth + 1)
                    walk(node.right, depth + 1)

                walk(root, 0)
                return levels


            root = TreeNode(3, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
            ''',
        ),
    ),
    _ex(
        "validate-bst",
        "Validate Binary Search Tree",
        "isValidBST(root)",
        _source(
            TREE_NODE,
            '''
            def isValidBST(root):
                """Every node must sit strictly between the values allowed by its ancestors."""
                def walk(node, lo, hi):
                    if node is None:
                        return True
                    if node.val <= lo or node.val >= hi:
                        return False
                    return walk(node.left, lo, node.val) and walk(node.right, node.val, hi)

                return walk(root, float("-inf"), float("inf"))


            # 5[3[2,4],7[,8]]
            root = TreeNode(
                5,
                TreeNode(3, TreeNode(2), TreeNode(4)),
                TreeNode(7, None, TreeNode(8)),
            )
            ''',
        ),
    ),
    _ex(
        "lowest-common-ancestor",
        "Lowest Common Ancestor of a Binary Tree",
        "lowestCommonAncestor(root, p, q)",
        _source(
            TREE_NODE,
            '''
            def lowestCommonAncestor(root, p, q):
                """The deepest node that still has both p and q in its subtree."""
                if root is None or root is p or root is q:
                    return root
                left = lowestCommonAncestor(root.left, p, q)
                right = lowestCommonAncestor(root.right, p, q)
                if left is not None and right is not None:
                    return root
                if left is not None:
                    return left
                return right


            root = TreeNode(
                3,
                TreeNode(5, TreeNode(6), TreeNode(2, TreeNode(7), TreeNode(4))),
                TreeNode(1, TreeNode(0), TreeNode(8)),
            )
            p = root.left
            q = root.left.right.right
            ''',
        ),
    ),
    _ex(
        "subtree",
        "Subtree of Another Tree",
        "isSubtree(root, subRoot)",
        _source(
            TREE_NODE,
            '''
            def isSubtree(root, subRoot):
                """True when subRoot matches this node or a node under it."""
                def same(a, b):
                    if a is None and b is None:
                        return True
                    if a is None or b is None or a.val != b.val:
                        return False
                    return same(a.left, b.left) and same(a.right, b.right)

                if root is None:
                    return False
                if same(root, subRoot):
                    return True
                return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)


            root = TreeNode(3, TreeNode(4, TreeNode(1), TreeNode(2)), TreeNode(5))
            subRoot = TreeNode(4, TreeNode(1), TreeNode(2))
            ''',
        ),
    ),
    _ex(
        "diameter",
        "Diameter of Binary Tree",
        "diameterOfBinaryTree(root)",
        _source(
            TREE_NODE,
            '''
            def diameterOfBinaryTree(root):
                """Longest path between two nodes, counted in edges."""
                best = 0

                def depth(node):
                    nonlocal best
                    if node is None:
                        return 0
                    left = depth(node.left)
                    right = depth(node.right)
                    best = max(best, left + right)
                    return 1 + max(left, right)

                depth(root)
                return best


            # 1[2[4,5],3] — the long path is 4-2-1-3
            root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
            ''',
        ),
    ),
    _ex(
        "max-path-sum",
        "Binary Tree Maximum Path Sum",
        "maxPathSum(root)",
        _source(
            TREE_NODE,
            '''
            def maxPathSum(root):
                """Best path anywhere in the tree. A path may bend through one node."""
                best = root.val

                def gain(node):
                    nonlocal best
                    if node is None:
                        return 0
                    left = max(gain(node.left), 0)
                    right = max(gain(node.right), 0)
                    best = max(best, node.val + left + right)
                    return node.val + max(left, right)

                gain(root)
                return best


            # -10[9,20[15,7]] — 15 + 20 + 7
            root = TreeNode(-10, TreeNode(9), TreeNode(20, TreeNode(15), TreeNode(7)))
            ''',
        ),
    ),
    _ex(
        "build-tree",
        "Construct Binary Tree from Preorder and Inorder",
        "buildTree(preorder, inorder)",
        _source(
            TREE_NODE,
            '''
            def buildTree(preorder, inorder):
                """The first preorder value is the root; inorder splits its left and right."""
                index = {val: i for i, val in enumerate(inorder)}

                def build(pre_lo, pre_hi, in_lo, in_hi):
                    if pre_lo > pre_hi:
                        return None
                    val = preorder[pre_lo]
                    mid = index[val]
                    left_count = mid - in_lo
                    left = build(pre_lo + 1, pre_lo + left_count, in_lo, mid - 1)
                    right = build(pre_lo + left_count + 1, pre_hi, mid + 1, in_hi)
                    return TreeNode(val, left, right)

                return build(0, len(preorder) - 1, 0, len(inorder) - 1)


            preorder = [3, 9, 20, 15, 7]
            inorder = [9, 3, 15, 20, 7]
            ''',
        ),
    ),
]
