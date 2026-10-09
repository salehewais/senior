"""Runnable examples for the recursion-tree visualizer."""

from backend.examples.backtracking import EXAMPLES as BACKTRACKING
from backend.examples.dp import EXAMPLES as DYNAMIC_PROGRAMMING
from backend.examples.graphs import EXAMPLES as GRAPHS
from backend.examples.recursion import EXAMPLES as RECURSION
from backend.examples.trees import EXAMPLES as TREES

EXAMPLES = [
    *RECURSION,
    *TREES,
    *BACKTRACKING,
    *DYNAMIC_PROGRAMMING,
    *GRAPHS,
]
