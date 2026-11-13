/* Curated v2 fork of software-engineering-roadmap — sections edited by hand; concepts/mainTopics/stats rebuilt */
window.ROADMAP_CONTENT = {
  "meta": {
    "title": "Software Engineering Master Roadmap",
    "subtitle": "A Structured Learning Path for Senior Software Engineers",
    "originalSubtitle": "A structured roadmap for Backend Engineering and Senior Software Engineering",
    "introNote": "**تنظيم وتوسيع للمنهج الأصلي.** تم الحفاظ على المحاور والموضوعات الأصلية، مع إعادة ترتيبها، وتصحيح بعض التسميات الواضحة، وإضافة موضوعات مكملة. لم يتم حذف قوائم المسائل أو الأنماط الموجودة في الملف الأصلي.",
    "sourceFile": "Software_Engineering_Master_Roadmap.md"
  },
  "sections": [
    {
      "id": "roadmap-overview",
      "title": "Roadmap Overview",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "phase-1-engineering-foundations",
          "title": "Phase 1 — Engineering Foundations",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Problem Solving & Data Structures & Algorithms (DSA)",
                  "ordered": true,
                  "children": [],
                  "id": "phase-1-engineering-foundations--problem-solving-and-data-structures-and-algorithms-dsa-1"
                },
                {
                  "text": "DBMS & Data Management",
                  "ordered": true,
                  "children": [],
                  "id": "phase-1-engineering-foundations--dbms-and-data-management-2"
                },
                {
                  "text": "Object-Oriented Design (OOD)",
                  "ordered": true,
                  "children": [],
                  "id": "phase-1-engineering-foundations--object-oriented-design-ood-3"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "phase-2-software-design-and-architecture",
          "title": "Phase 2 — Software Design & Architecture",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Application Architecture",
                  "ordered": true,
                  "children": [],
                  "id": "phase-2-software-design-and-architecture--application-architecture-4"
                },
                {
                  "text": "Presentation Architecture",
                  "ordered": true,
                  "children": [],
                  "id": "phase-2-software-design-and-architecture--presentation-architecture-5"
                },
                {
                  "text": "Patterns of Enterprise Application Architecture (PoEAA)",
                  "ordered": true,
                  "children": [],
                  "id": "phase-2-software-design-and-architecture--patterns-of-enterprise-application-architecture-poeaa-6"
                },
                {
                  "text": "Domain-Driven Design (DDD)",
                  "ordered": true,
                  "children": [],
                  "id": "phase-2-software-design-and-architecture--domain-driven-design-ddd-7"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "phase-3-concurrency-and-integration",
          "title": "Phase 3 — Concurrency & Integration",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Concurrency Patterns",
                  "ordered": true,
                  "children": [],
                  "id": "phase-3-concurrency-and-integration--concurrency-patterns-8"
                },
                {
                  "text": "Enterprise Integration Patterns (EIP)",
                  "ordered": true,
                  "children": [],
                  "id": "phase-3-concurrency-and-integration--enterprise-integration-patterns-eip-9"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "phase-4-distributed-systems-and-system-architecture",
          "title": "Phase 4 — Distributed Systems & System Architecture",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "System Design",
                  "ordered": true,
                  "children": [],
                  "id": "phase-4-distributed-systems-and-system-architecture--system-design-10"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "supporting-foundations-study-alongside-the-roadmap",
          "title": "Supporting Foundations (study alongside the roadmap)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Software Engineering Practices",
                  "ordered": false,
                  "children": [],
                  "id": "supporting-foundations-study-alongside-the-roadmap--software-engineering-practices-11"
                },
                {
                  "text": "Operating Systems Fundamentals",
                  "ordered": false,
                  "children": [],
                  "id": "supporting-foundations-study-alongside-the-roadmap--operating-systems-fundamentals-12"
                },
                {
                  "text": "Computer Networking Fundamentals",
                  "ordered": false,
                  "children": [],
                  "id": "supporting-foundations-study-alongside-the-roadmap--computer-networking-fundamentals-13"
                }
              ]
            },
            {
              "type": "blockquote",
              "text": "ترتيب المراحل تعليمي وليس Dependency Graph صارمًا. يمكن دراسة بعض المحاور بالتوازي، كما يمكن البدء بأساسيات System Design مبكرًا ثم التعمق فيها بعد دراسة المحاور السابقة."
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "01-problem-solving-and-data-structures-and-algorithms-dsa",
      "title": "01 — Problem Solving & Data Structures & Algorithms (DSA)",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "11-complexity-analysis",
          "title": "1.1 Complexity Analysis",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Time Complexity & Space Complexity",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Big O, Big Omega, Big Theta",
                      "ordered": false,
                      "children": [],
                      "id": "11-complexity-analysis--big-o-big-omega-big-theta-15"
                    }
                  ],
                  "id": "11-complexity-analysis--time-complexity-and-space-complexity-14"
                },
                {
                  "text": "Amortized Analysis",
                  "ordered": false,
                  "children": [],
                  "id": "11-complexity-analysis--amortized-analysis-16"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "12-fundamental-data-structures",
          "title": "1.2 Fundamental Data Structures",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Arrays & Strings",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Prefix Sums",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--prefix-sums-18"
                    },
                    {
                      "text": "Matrix Manipulation",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--matrix-manipulation-19"
                    }
                  ],
                  "id": "12-fundamental-data-structures--arrays-and-strings-17"
                },
                {
                  "text": "Linked Lists",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Singly Linked Lists",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--singly-linked-lists-21"
                    },
                    {
                      "text": "Doubly Linked Lists",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--doubly-linked-lists-22"
                    },
                    {
                      "text": "Circular Linked Lists",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--circular-linked-lists-23"
                    }
                  ],
                  "id": "12-fundamental-data-structures--linked-lists-20"
                },
                {
                  "text": "Stacks & Queues",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Monotonic Stack",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--monotonic-stack-25"
                    },
                    {
                      "text": "Monotonic Queue",
                      "ordered": false,
                      "children": [],
                      "id": "12-fundamental-data-structures--monotonic-queue-26"
                    }
                  ],
                  "id": "12-fundamental-data-structures--stacks-and-queues-24"
                },
                {
                  "text": "Hash Tables / Hash Maps / Hash Sets",
                  "ordered": false,
                  "children": [],
                  "id": "12-fundamental-data-structures--hash-tables-hash-maps-hash-sets-27"
                },
                {
                  "text": "Heaps / Priority Queues",
                  "ordered": false,
                  "children": [],
                  "id": "12-fundamental-data-structures--heaps-priority-queues-28"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "13-advanced-data-structures",
          "title": "1.3 Advanced Data Structures",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Trees",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Binary Trees",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--binary-trees-30"
                    },
                    {
                      "text": "Binary Search Trees",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--binary-search-trees-31"
                    },
                    {
                      "text": "AVL / Self-Balancing Trees",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--avl-self-balancing-trees-32"
                    },
                    {
                      "text": "Tries",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--tries-33"
                    }
                  ],
                  "id": "13-advanced-data-structures--trees-29"
                },
                {
                  "text": "Graphs",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Adjacency Matrix / Adjacency List",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--adjacency-matrix-adjacency-list-35"
                    },
                    {
                      "text": "Directed / Undirected",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--directed-undirected-36"
                    },
                    {
                      "text": "Weighted / Unweighted",
                      "ordered": false,
                      "children": [],
                      "id": "13-advanced-data-structures--weighted-unweighted-37"
                    }
                  ],
                  "id": "13-advanced-data-structures--graphs-34"
                },
                {
                  "text": "Disjoint Set Union (Union-Find / DSU)",
                  "ordered": false,
                  "children": [],
                  "id": "13-advanced-data-structures--disjoint-set-union-union-find-dsu-38"
                },
                {
                  "text": "Segment Trees",
                  "ordered": false,
                  "children": [],
                  "id": "13-advanced-data-structures--segment-trees-39"
                },
                {
                  "text": "Fenwick Trees (Binary Indexed Tree)",
                  "ordered": false,
                  "children": [],
                  "id": "13-advanced-data-structures--fenwick-trees-binary-indexed-tree-40"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "14-core-problem-solving-patterns-and-techniques",
          "title": "1.4 Core Problem-Solving Patterns & Techniques",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Two Pointers",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--two-pointers-41"
                },
                {
                  "text": "Sliding Window",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--sliding-window-42"
                },
                {
                  "text": "Fast & Slow Pointers (Tortoise & Hare)",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--fast-and-slow-pointers-tortoise-and-hare-43"
                },
                {
                  "text": "Prefix Sum",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--prefix-sum-44"
                },
                {
                  "text": "Merge Intervals",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--merge-intervals-45"
                },
                {
                  "text": "Cyclic Sort",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--cyclic-sort-46"
                },
                {
                  "text": "In-place Reversal of a Linked List",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--in-place-reversal-of-a-linked-list-47"
                },
                {
                  "text": "Binary Search & Modified Binary Search",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--binary-search-and-modified-binary-search-48"
                },
                {
                  "text": "Tree Breadth-First Search (BFS) & Depth-First Search (DFS)",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--tree-breadth-first-search-bfs-and-depth-first-search-dfs-49"
                },
                {
                  "text": "Graph Traversal",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--graph-traversal-50"
                },
                {
                  "text": "Shortest Path",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Dijkstra",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--dijkstra-52"
                    },
                    {
                      "text": "Bellman-Ford",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--bellman-ford-53"
                    },
                    {
                      "text": "Floyd-Warshall",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--floyd-warshall-54"
                    }
                  ],
                  "id": "14-core-problem-solving-patterns-and-techniques--shortest-path-51"
                },
                {
                  "text": "Topological Sort",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Kahn's Algorithm",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--kahns-algorithm-56"
                    },
                    {
                      "text": "DFS-based",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--dfs-based-57"
                    }
                  ],
                  "id": "14-core-problem-solving-patterns-and-techniques--topological-sort-55"
                },
                {
                  "text": "Backtracking & Recursion",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--backtracking-and-recursion-58"
                },
                {
                  "text": "Dynamic Programming",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Memoization",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--memoization-60"
                    },
                    {
                      "text": "Tabulation",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--tabulation-61"
                    },
                    {
                      "text": "1D / 2D DP",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--1d-2d-dp-62"
                    },
                    {
                      "text": "Knapsack",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--knapsack-63"
                    },
                    {
                      "text": "LCS",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--lcs-64"
                    },
                    {
                      "text": "LIS",
                      "ordered": false,
                      "children": [],
                      "id": "14-core-problem-solving-patterns-and-techniques--lis-65"
                    }
                  ],
                  "id": "14-core-problem-solving-patterns-and-techniques--dynamic-programming-59"
                },
                {
                  "text": "Greedy Algorithms",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--greedy-algorithms-66"
                },
                {
                  "text": "Divide and Conquer",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--divide-and-conquer-67"
                },
                {
                  "text": "Bit Manipulation",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--bit-manipulation-68"
                },
                {
                  "text": "Mathematical Algorithms",
                  "ordered": false,
                  "children": [],
                  "id": "14-core-problem-solving-patterns-and-techniques--mathematical-algorithms-69"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "15-recursion-roadmap-and-problem-tracker",
          "title": "1.5 Recursion Roadmap & Problem Tracker",
          "level": 2,
          "blocks": [],
          "children": [
            {
              "id": "a-recursion-العودية",
              "title": "A. Recursion (العودية)",
              "level": 3,
              "blocks": [],
              "children": [
                {
                  "id": "a-recursion-العودية-common-problems",
                  "title": "Common Problems",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "509 — Fibonacci Number (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--509-fibonacci-number-easy-70"
                        },
                        {
                          "text": "344 — Reverse String (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--344-reverse-string-easy-71"
                        },
                        {
                          "text": "21 — Merge Two Sorted Lists (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--21-merge-two-sorted-lists-easy-72"
                        },
                        {
                          "text": "50 — Pow(x, n) (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--50-powx-n-medium-73"
                        },
                        {
                          "text": "118 — Pascal's Triangle (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--118-pascals-triangle-easy-74"
                        },
                        {
                          "text": "24 — Swap Nodes in Pairs (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--24-swap-nodes-in-pairs-medium-75"
                        },
                        {
                          "text": "779 — K-th Symbol in Grammar (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--779-k-th-symbol-in-grammar-medium-76"
                        },
                        {
                          "text": "2 — Add Two Numbers (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--2-add-two-numbers-medium-77"
                        },
                        {
                          "text": "95 — Unique Binary Search Trees II (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--95-unique-binary-search-trees-ii-medium-78"
                        },
                        {
                          "text": "394 — Decode String (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-common-problems--394-decode-string-medium-79"
                        }
                      ]
                    }
                  ],
                  "children": []
                },
                {
                  "id": "a-recursion-العودية-training-path",
                  "title": "Training Path",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "206 — Reverse Linked List (Easy): Recursive reversal of a linked list",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--206-reverse-linked-list-easy-recursive-reversal-of-a-li-80"
                        },
                        {
                          "text": "203 — Remove Linked List Elements (Easy): Recursive removal with a base case",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--203-remove-linked-list-elements-easy-recursive-removal-81"
                        },
                        {
                          "text": "231 — Power of Two (Easy): Recursive halving until the base",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--231-power-of-two-easy-recursive-halving-until-the-base-82"
                        },
                        {
                          "text": "326 — Power of Three (Easy): Recursive division and base cases",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--326-power-of-three-easy-recursive-division-and-base-cas-83"
                        },
                        {
                          "text": "342 — Power of Four (Easy): Recursive division by four",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--342-power-of-four-easy-recursive-division-by-four-84"
                        },
                        {
                          "text": "234 — Palindrome Linked List (Easy): Recursion to the end, then compare",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--234-palindrome-linked-list-easy-recursion-to-the-end-t-85"
                        },
                        {
                          "text": "3304 — Find the K-th Character in String Game I (Easy): Recursive string growth",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--3304-find-the-k-th-character-in-string-game-i-easy-recu-86"
                        },
                        {
                          "text": "390 — Elimination Game (Medium): A recurrence that shrinks the problem",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--390-elimination-game-medium-a-recurrence-that-shrinks-t-87"
                        },
                        {
                          "text": "1545 — Find Kth Bit in Nth Binary String (Medium): A string defined by recursion",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--1545-find-kth-bit-in-nth-binary-string-medium-a-string-88"
                        },
                        {
                          "text": "1823 — Find the Winner of the Circular Game (Medium): Josephus recurrence",
                          "ordered": false,
                          "children": [],
                          "id": "a-recursion-العودية-training-path--1823-find-the-winner-of-the-circular-game-medium-joseph-89"
                        }
                      ]
                    }
                  ],
                  "children": []
                }
              ]
            },
            {
              "id": "b-trees-الأشجار",
              "title": "B. Trees (الأشجار)",
              "level": 3,
              "blocks": [],
              "children": [
                {
                  "id": "b-trees-الأشجار-common-problems",
                  "title": "Common Problems",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "104 — Maximum Depth of Binary Tree (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--104-maximum-depth-of-binary-tree-easy-90"
                        },
                        {
                          "text": "226 — Invert Binary Tree (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--226-invert-binary-tree-easy-91"
                        },
                        {
                          "text": "100 — Same Tree (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--100-same-tree-easy-92"
                        },
                        {
                          "text": "102 — Binary Tree Level Order Traversal (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--102-binary-tree-level-order-traversal-medium-93"
                        },
                        {
                          "text": "98 — Validate Binary Search Tree (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--98-validate-binary-search-tree-medium-94"
                        },
                        {
                          "text": "236 — Lowest Common Ancestor of a Binary Tree (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--236-lowest-common-ancestor-of-a-binary-tree-medium-95"
                        },
                        {
                          "text": "572 — Subtree of Another Tree (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--572-subtree-of-another-tree-easy-96"
                        },
                        {
                          "text": "543 — Diameter of Binary Tree (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--543-diameter-of-binary-tree-easy-97"
                        },
                        {
                          "text": "124 — Binary Tree Maximum Path Sum (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--124-binary-tree-maximum-path-sum-hard-98"
                        },
                        {
                          "text": "105 — Construct Binary Tree from Preorder and Inorder Traversal (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "b-trees-الأشجار-common-problems--105-construct-binary-tree-from-preorder-and-inorder-traver-99"
                        }
                      ]
                    }
                  ],
                  "children": []
                }
              ]
            },
            {
              "id": "c-backtracking-التراجع",
              "title": "C. Backtracking (التراجع)",
              "level": 3,
              "blocks": [],
              "children": [
                {
                  "id": "c-backtracking-التراجع-core-problems",
                  "title": "Core Problems",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "78 — Subsets (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--78-subsets-medium-100"
                        },
                        {
                          "text": "90 — Subsets II (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--90-subsets-ii-medium-101"
                        },
                        {
                          "text": "46 — Permutations (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--46-permutations-medium-102"
                        },
                        {
                          "text": "47 — Permutations II (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--47-permutations-ii-medium-103"
                        },
                        {
                          "text": "39 — Combination Sum (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--39-combination-sum-medium-104"
                        },
                        {
                          "text": "40 — Combination Sum II (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--40-combination-sum-ii-medium-105"
                        },
                        {
                          "text": "131 — Palindrome Partitioning (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--131-palindrome-partitioning-medium-106"
                        },
                        {
                          "text": "51 — N-Queens (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--51-n-queens-hard-107"
                        },
                        {
                          "text": "79 — Word Search (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--79-word-search-medium-108"
                        },
                        {
                          "text": "37 — Sudoku Solver (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-core-problems--37-sudoku-solver-hard-109"
                        }
                      ]
                    }
                  ],
                  "children": []
                },
                {
                  "id": "c-backtracking-التراجع-additional-problems",
                  "title": "Additional Problems",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "17 — Letter Combinations of a Phone Number (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--17-letter-combinations-of-a-phone-number-medium-110"
                        },
                        {
                          "text": "216 — Combination Sum III (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--216-combination-sum-iii-medium-111"
                        },
                        {
                          "text": "93 — Restore IP Addresses (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--93-restore-ip-addresses-medium-112"
                        },
                        {
                          "text": "698 — Partition to K Equal Sum Subsets (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--698-partition-to-k-equal-sum-subsets-medium-113"
                        },
                        {
                          "text": "212 — Word Search II (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--212-word-search-ii-hard-114"
                        },
                        {
                          "text": "473 — Matchsticks to Square (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--473-matchsticks-to-square-medium-115"
                        },
                        {
                          "text": "52 — N-Queens II (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--52-n-queens-ii-hard-116"
                        },
                        {
                          "text": "491 — Non-decreasing Subsequences (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--491-non-decreasing-subsequences-medium-117"
                        },
                        {
                          "text": "526 — Beautiful Arrangement (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--526-beautiful-arrangement-medium-118"
                        },
                        {
                          "text": "1849 — Splitting a String Into Descending Consecutive Values (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "c-backtracking-التراجع-additional-problems--1849-splitting-a-string-into-descending-consecutive-values-119"
                        }
                      ]
                    }
                  ],
                  "children": []
                }
              ]
            },
            {
              "id": "d-dynamic-programming-البرمجة-الديناميكية",
              "title": "D. Dynamic Programming (البرمجة الديناميكية)",
              "level": 3,
              "blocks": [],
              "children": [
                {
                  "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems",
                  "title": "Common Problems",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "70 — Climbing Stairs (Easy)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--70-climbing-stairs-easy-120"
                        },
                        {
                          "text": "198 — House Robber (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--198-house-robber-medium-121"
                        },
                        {
                          "text": "213 — House Robber II (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--213-house-robber-ii-medium-122"
                        },
                        {
                          "text": "5 — Longest Palindromic Substring (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--5-longest-palindromic-substring-medium-123"
                        },
                        {
                          "text": "322 — Coin Change (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--322-coin-change-medium-124"
                        },
                        {
                          "text": "300 — Longest Increasing Subsequence (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--300-longest-increasing-subsequence-medium-125"
                        },
                        {
                          "text": "416 — Partition Equal Subset Sum (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--416-partition-equal-subset-sum-medium-126"
                        },
                        {
                          "text": "62 — Unique Paths (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--62-unique-paths-medium-127"
                        },
                        {
                          "text": "72 — Edit Distance (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--72-edit-distance-hard-128"
                        },
                        {
                          "text": "1143 — Longest Common Subsequence (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--1143-longest-common-subsequence-medium-129"
                        }
                      ]
                    }
                  ],
                  "children": []
                }
              ]
            },
            {
              "id": "e-graphs-الرسوم-البيانية",
              "title": "E. Graphs (الرسوم البيانية)",
              "level": 3,
              "blocks": [],
              "children": [
                {
                  "id": "e-graphs-الرسوم-البيانية-common-problems",
                  "title": "Common Problems",
                  "level": 4,
                  "blocks": [
                    {
                      "type": "list",
                      "items": [
                        {
                          "text": "200 — Number of Islands (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--200-number-of-islands-medium-130"
                        },
                        {
                          "text": "133 — Clone Graph (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--133-clone-graph-medium-131"
                        },
                        {
                          "text": "695 — Max Area of Island (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--695-max-area-of-island-medium-132"
                        },
                        {
                          "text": "207 — Course Schedule (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--207-course-schedule-medium-133"
                        },
                        {
                          "text": "417 — Pacific Atlantic Water Flow (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--417-pacific-atlantic-water-flow-medium-134"
                        },
                        {
                          "text": "994 — Rotting Oranges (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--994-rotting-oranges-medium-135"
                        },
                        {
                          "text": "261 — Graph Valid Tree (Medium, Premium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--261-graph-valid-tree-medium-premium-136"
                        },
                        {
                          "text": "127 — Word Ladder (Hard)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--127-word-ladder-hard-137"
                        },
                        {
                          "text": "743 — Network Delay Time (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--743-network-delay-time-medium-138"
                        },
                        {
                          "text": "787 — Cheapest Flights Within K Stops (Medium)",
                          "ordered": false,
                          "children": [],
                          "id": "e-graphs-الرسوم-البيانية-common-problems--787-cheapest-flights-within-k-stops-medium-139"
                        }
                      ]
                    }
                  ],
                  "children": []
                }
              ]
            }
          ]
        }
      ]
    },
    {
      "id": "02-dbms-and-data-management",
      "title": "02 — DBMS & Data Management",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "21-core-concepts-and-architecture",
          "title": "2.1 Core Concepts & Architecture",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "DBMS vs RDBMS",
                  "ordered": false,
                  "children": [],
                  "id": "21-core-concepts-and-architecture--dbms-vs-rdbms-140"
                },
                {
                  "text": "Database Architecture",
                  "ordered": false,
                  "children": [],
                  "id": "21-core-concepts-and-architecture--database-architecture-141"
                },
                {
                  "text": "Relational Model",
                  "ordered": false,
                  "children": [],
                  "id": "21-core-concepts-and-architecture--relational-model-142"
                },
                {
                  "text": "Tables, Rows, Columns",
                  "ordered": false,
                  "children": [],
                  "id": "21-core-concepts-and-architecture--tables-rows-columns-143"
                },
                {
                  "text": "Data Types",
                  "ordered": false,
                  "children": [],
                  "id": "21-core-concepts-and-architecture--data-types-144"
                },
                {
                  "text": "SQL vs NoSQL",
                  "ordered": false,
                  "children": [],
                  "id": "21-core-concepts-and-architecture--sql-vs-nosql-145"
                },
                {
                  "text": "ACID Properties",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Atomicity",
                      "ordered": false,
                      "children": [],
                      "id": "21-core-concepts-and-architecture--atomicity-147"
                    },
                    {
                      "text": "Consistency",
                      "ordered": false,
                      "children": [],
                      "id": "21-core-concepts-and-architecture--consistency-148"
                    },
                    {
                      "text": "Isolation",
                      "ordered": false,
                      "children": [],
                      "id": "21-core-concepts-and-architecture--isolation-149"
                    },
                    {
                      "text": "Durability",
                      "ordered": false,
                      "children": [],
                      "id": "21-core-concepts-and-architecture--durability-150"
                    }
                  ],
                  "id": "21-core-concepts-and-architecture--acid-properties-146"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "22-relational-database-design",
          "title": "2.2 Relational Database Design",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Keys",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Primary Key",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--primary-key-152"
                    },
                    {
                      "text": "Foreign Key",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--foreign-key-153"
                    },
                    {
                      "text": "Candidate Key",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--candidate-key-154"
                    },
                    {
                      "text": "Composite Key",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--composite-key-155"
                    },
                    {
                      "text": "Unique Key",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--unique-key-156"
                    }
                  ],
                  "id": "22-relational-database-design--keys-151"
                },
                {
                  "text": "Relationships",
                  "ordered": false,
                  "children": [
                    {
                      "text": "One-to-One",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--one-to-one-158"
                    },
                    {
                      "text": "One-to-Many",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--one-to-many-159"
                    },
                    {
                      "text": "Many-to-Many",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--many-to-many-160"
                    }
                  ],
                  "id": "22-relational-database-design--relationships-157"
                },
                {
                  "text": "Normalization",
                  "ordered": false,
                  "children": [
                    {
                      "text": "1NF",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--1nf-162"
                    },
                    {
                      "text": "2NF",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--2nf-163"
                    },
                    {
                      "text": "3NF",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--3nf-164"
                    },
                    {
                      "text": "BCNF",
                      "ordered": false,
                      "children": [],
                      "id": "22-relational-database-design--bcnf-165"
                    }
                  ],
                  "id": "22-relational-database-design--normalization-161"
                },
                {
                  "text": "Denormalization",
                  "ordered": false,
                  "children": [],
                  "id": "22-relational-database-design--denormalization-166"
                },
                {
                  "text": "Schema Design",
                  "ordered": false,
                  "children": [],
                  "id": "22-relational-database-design--schema-design-167"
                },
                {
                  "text": "Data Modeling",
                  "ordered": false,
                  "children": [],
                  "id": "22-relational-database-design--data-modeling-168"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "23-transactions-and-concurrency-control",
          "title": "2.3 Transactions & Concurrency Control",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Transactions",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--transactions-169"
                },
                {
                  "text": "Transaction Isolation Levels",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Read Uncommitted",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--read-uncommitted-171"
                    },
                    {
                      "text": "Read Committed",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--read-committed-172"
                    },
                    {
                      "text": "Repeatable Read",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--repeatable-read-173"
                    },
                    {
                      "text": "Serializable",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--serializable-174"
                    }
                  ],
                  "id": "23-transactions-and-concurrency-control--transaction-isolation-levels-170"
                },
                {
                  "text": "Concurrency Phenomena",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Dirty Reads",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--dirty-reads-176"
                    },
                    {
                      "text": "Non-repeatable Reads",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--non-repeatable-reads-177"
                    },
                    {
                      "text": "Phantom Reads",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--phantom-reads-178"
                    },
                    {
                      "text": "Lost Updates",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--lost-updates-179"
                    },
                    {
                      "text": "Write Skew",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--write-skew-180"
                    }
                  ],
                  "id": "23-transactions-and-concurrency-control--concurrency-phenomena-175"
                },
                {
                  "text": "Locks",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Shared Locks",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--shared-locks-182"
                    },
                    {
                      "text": "Exclusive Locks",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--exclusive-locks-183"
                    },
                    {
                      "text": "Intent Locks",
                      "ordered": false,
                      "children": [],
                      "id": "23-transactions-and-concurrency-control--intent-locks-184"
                    }
                  ],
                  "id": "23-transactions-and-concurrency-control--locks-181"
                },
                {
                  "text": "Deadlocks",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--deadlocks-185"
                },
                {
                  "text": "MVCC (Multi-Version Concurrency Control)",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--mvcc-multi-version-concurrency-control-186"
                },
                {
                  "text": "Optimistic Concurrency Control",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--optimistic-concurrency-control-187"
                },
                {
                  "text": "Pessimistic Concurrency Control",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--pessimistic-concurrency-control-188"
                },
                {
                  "text": "WAL (Write-Ahead Logging)",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--wal-write-ahead-logging-189"
                },
                {
                  "text": "Savepoints",
                  "ordered": false,
                  "children": [],
                  "id": "23-transactions-and-concurrency-control--savepoints-190"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "24-storage-indexing-and-query-performance",
          "title": "2.4 Storage, Indexing & Query Performance",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Indexing",
                  "ordered": false,
                  "children": [
                    {
                      "text": "B-Tree",
                      "ordered": false,
                      "children": [],
                      "id": "24-storage-indexing-and-query-performance--b-tree-192"
                    },
                    {
                      "text": "B+Tree",
                      "ordered": false,
                      "children": [],
                      "id": "24-storage-indexing-and-query-performance--btree-193"
                    },
                    {
                      "text": "Hash Index",
                      "ordered": false,
                      "children": [],
                      "id": "24-storage-indexing-and-query-performance--hash-index-194"
                    },
                    {
                      "text": "Clustered vs Non-Clustered",
                      "ordered": false,
                      "children": [],
                      "id": "24-storage-indexing-and-query-performance--clustered-vs-non-clustered-195"
                    },
                    {
                      "text": "Bitmap Index",
                      "ordered": false,
                      "children": [],
                      "id": "24-storage-indexing-and-query-performance--bitmap-index-196"
                    }
                  ],
                  "id": "24-storage-indexing-and-query-performance--indexing-191"
                },
                {
                  "text": "Query Processing",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--query-processing-197"
                },
                {
                  "text": "Query Planner / Optimizer",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--query-planner-optimizer-198"
                },
                {
                  "text": "Query Execution Plans",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--query-execution-plans-199"
                },
                {
                  "text": "Database Caching",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--database-caching-200"
                },
                {
                  "text": "Buffer Pool Management",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--buffer-pool-management-201"
                },
                {
                  "text": "Storage Engines",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--storage-engines-202"
                },
                {
                  "text": "Vacuuming and Maintenance",
                  "ordered": false,
                  "children": [],
                  "id": "24-storage-indexing-and-query-performance--vacuuming-and-maintenance-203"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "25-distributed-databases-and-scaling",
          "title": "2.5 Distributed Databases & Scaling",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Replication",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Primary-Replica (Master-Slave)",
                      "ordered": false,
                      "children": [],
                      "id": "25-distributed-databases-and-scaling--primary-replica-master-slave-205"
                    },
                    {
                      "text": "Multi-Primary (Master-Master)",
                      "ordered": false,
                      "children": [],
                      "id": "25-distributed-databases-and-scaling--multi-primary-master-master-206"
                    },
                    {
                      "text": "Synchronous vs Asynchronous",
                      "ordered": false,
                      "children": [],
                      "id": "25-distributed-databases-and-scaling--synchronous-vs-asynchronous-207"
                    }
                  ],
                  "id": "25-distributed-databases-and-scaling--replication-204"
                },
                {
                  "text": "Read Replicas",
                  "ordered": false,
                  "children": [],
                  "id": "25-distributed-databases-and-scaling--read-replicas-208"
                },
                {
                  "text": "Sharding",
                  "ordered": false,
                  "children": [],
                  "id": "25-distributed-databases-and-scaling--sharding-209"
                },
                {
                  "text": "Horizontal / Vertical Partitioning",
                  "ordered": false,
                  "children": [],
                  "id": "25-distributed-databases-and-scaling--horizontal-vertical-partitioning-210"
                },
                {
                  "text": "CAP Theorem",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Consistency",
                      "ordered": false,
                      "children": [],
                      "id": "25-distributed-databases-and-scaling--consistency-212"
                    },
                    {
                      "text": "Availability",
                      "ordered": false,
                      "children": [],
                      "id": "25-distributed-databases-and-scaling--availability-213"
                    },
                    {
                      "text": "Partition Tolerance",
                      "ordered": false,
                      "children": [],
                      "id": "25-distributed-databases-and-scaling--partition-tolerance-214"
                    }
                  ],
                  "id": "25-distributed-databases-and-scaling--cap-theorem-211"
                },
                {
                  "text": "ACID vs BASE",
                  "ordered": false,
                  "children": [],
                  "id": "25-distributed-databases-and-scaling--acid-vs-base-215"
                },
                {
                  "text": "Distributed Transactions (overview)",
                  "ordered": false,
                  "children": [],
                  "id": "25-distributed-databases-and-scaling--distributed-transactions-overview-216"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "26-database-types-and-engines",
          "title": "2.6 Database Types & Engines",
          "level": 2,
          "blocks": [],
          "children": [
            {
              "id": "relational-databases-sql",
              "title": "Relational Databases (SQL)",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "MySQL",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases-sql--mysql-217"
                    },
                    {
                      "text": "PostgreSQL",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases-sql--postgresql-218"
                    },
                    {
                      "text": "Microsoft SQL Server",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases-sql--microsoft-sql-server-219"
                    },
                    {
                      "text": "SQLite",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases-sql--sqlite-220"
                    },
                    {
                      "text": "Oracle Database",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases-sql--oracle-database-221"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "non-relational-databases-nosql",
              "title": "Non-Relational Databases (NoSQL)",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Document Stores",
                      "ordered": false,
                      "children": [
                        {
                          "text": "MongoDB",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--mongodb-223"
                        },
                        {
                          "text": "CouchDB",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--couchdb-224"
                        }
                      ],
                      "id": "non-relational-databases-nosql--document-stores-222"
                    },
                    {
                      "text": "Key-Value Stores",
                      "ordered": false,
                      "children": [
                        {
                          "text": "Redis",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--redis-226"
                        },
                        {
                          "text": "Amazon DynamoDB",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--amazon-dynamodb-227"
                        }
                      ],
                      "id": "non-relational-databases-nosql--key-value-stores-225"
                    },
                    {
                      "text": "Graph Databases",
                      "ordered": false,
                      "children": [
                        {
                          "text": "Neo4j",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--neo4j-229"
                        },
                        {
                          "text": "Amazon Neptune",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--amazon-neptune-230"
                        }
                      ],
                      "id": "non-relational-databases-nosql--graph-databases-228"
                    },
                    {
                      "text": "Time-Series Databases",
                      "ordered": false,
                      "children": [
                        {
                          "text": "InfluxDB",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--influxdb-232"
                        },
                        {
                          "text": "TimescaleDB",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--timescaledb-233"
                        }
                      ],
                      "id": "non-relational-databases-nosql--time-series-databases-231"
                    },
                    {
                      "text": "Column-Family / Wide-Column Stores",
                      "ordered": false,
                      "children": [
                        {
                          "text": "Apache Cassandra",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--apache-cassandra-235"
                        },
                        {
                          "text": "HBase",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--hbase-236"
                        }
                      ],
                      "id": "non-relational-databases-nosql--column-family-wide-column-stores-234"
                    },
                    {
                      "text": "Object-Oriented DBMS",
                      "ordered": false,
                      "children": [
                        {
                          "text": "db4o",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--db4o-238"
                        },
                        {
                          "text": "ObjectDB",
                          "ordered": false,
                          "children": [],
                          "id": "non-relational-databases-nosql--objectdb-239"
                        }
                      ],
                      "id": "non-relational-databases-nosql--object-oriented-dbms-237"
                    }
                  ]
                }
              ],
              "children": []
            }
          ]
        }
      ]
    },
    {
      "id": "03-object-oriented-design-ood",
      "title": "03 — Object-Oriented Design (OOD)",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "31-oop-fundamentals",
          "title": "3.1 OOP Fundamentals",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Encapsulation",
                  "ordered": false,
                  "children": [],
                  "id": "31-oop-fundamentals--encapsulation-240"
                },
                {
                  "text": "Abstraction",
                  "ordered": false,
                  "children": [],
                  "id": "31-oop-fundamentals--abstraction-241"
                },
                {
                  "text": "Inheritance",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Single",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--single-243"
                    },
                    {
                      "text": "Multiple",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--multiple-244"
                    },
                    {
                      "text": "Multilevel",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--multilevel-245"
                    },
                    {
                      "text": "Hierarchical",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--hierarchical-246"
                    },
                    {
                      "text": "Hybrid",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--hybrid-247"
                    }
                  ],
                  "id": "31-oop-fundamentals--inheritance-242"
                },
                {
                  "text": "Polymorphism",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Runtime Polymorphism",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--runtime-polymorphism-249"
                    },
                    {
                      "text": "Overriding",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--overriding-250"
                    },
                    {
                      "text": "Compile-Time Polymorphism",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--compile-time-polymorphism-251"
                    },
                    {
                      "text": "Method Overloading",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--method-overloading-252"
                    },
                    {
                      "text": "Operator Overloading",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--operator-overloading-253"
                    }
                  ],
                  "id": "31-oop-fundamentals--polymorphism-248"
                },
                {
                  "text": "Access Modifiers",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Public",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--public-255"
                    },
                    {
                      "text": "Private",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--private-256"
                    },
                    {
                      "text": "Protected",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--protected-257"
                    },
                    {
                      "text": "Protocol / Interface concepts",
                      "ordered": false,
                      "children": [],
                      "id": "31-oop-fundamentals--protocol-interface-concepts-258"
                    }
                  ],
                  "id": "31-oop-fundamentals--access-modifiers-254"
                },
                {
                  "text": "Classes and Objects",
                  "ordered": false,
                  "children": [],
                  "id": "31-oop-fundamentals--classes-and-objects-259"
                },
                {
                  "text": "Composition",
                  "ordered": false,
                  "children": [],
                  "id": "31-oop-fundamentals--composition-260"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "32-object-relationships",
          "title": "3.2 Object Relationships",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Association",
                  "ordered": false,
                  "children": [],
                  "id": "32-object-relationships--association-261"
                },
                {
                  "text": "Aggregation",
                  "ordered": false,
                  "children": [],
                  "id": "32-object-relationships--aggregation-262"
                },
                {
                  "text": "Composition",
                  "ordered": false,
                  "children": [],
                  "id": "32-object-relationships--composition-263"
                },
                {
                  "text": "Inheritance",
                  "ordered": false,
                  "children": [],
                  "id": "32-object-relationships--inheritance-264"
                },
                {
                  "text": "Realization",
                  "ordered": false,
                  "children": [],
                  "id": "32-object-relationships--realization-265"
                },
                {
                  "text": "Dependency",
                  "ordered": false,
                  "children": [],
                  "id": "32-object-relationships--dependency-266"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "33-design-principles",
          "title": "3.3 Design Principles",
          "level": 2,
          "blocks": [],
          "children": [
            {
              "id": "solid-principles",
              "title": "SOLID Principles",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Single Responsibility Principle",
                      "ordered": false,
                      "children": [],
                      "id": "solid-principles--single-responsibility-principle-267"
                    },
                    {
                      "text": "Open/Closed Principle",
                      "ordered": false,
                      "children": [],
                      "id": "solid-principles--open-closed-principle-268"
                    },
                    {
                      "text": "Liskov Substitution Principle",
                      "ordered": false,
                      "children": [],
                      "id": "solid-principles--liskov-substitution-principle-269"
                    },
                    {
                      "text": "Interface Segregation Principle",
                      "ordered": false,
                      "children": [],
                      "id": "solid-principles--interface-segregation-principle-270"
                    },
                    {
                      "text": "Dependency Inversion Principle",
                      "ordered": false,
                      "children": [],
                      "id": "solid-principles--dependency-inversion-principle-271"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "general-principles",
              "title": "General Principles",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "DRY (Don't Repeat Yourself)",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--dry-dont-repeat-yourself-272"
                    },
                    {
                      "text": "KISS (Keep It Simple, Stupid)",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--kiss-keep-it-simple-stupid-273"
                    },
                    {
                      "text": "YAGNI (You Aren't Gonna Need It)",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--yagni-you-arent-gonna-need-it-274"
                    },
                    {
                      "text": "Separation of Concerns",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--separation-of-concerns-275"
                    },
                    {
                      "text": "Encapsulate What Varies",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--encapsulate-what-varies-276"
                    },
                    {
                      "text": "Favor Composition Over Inheritance",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--favor-composition-over-inheritance-277"
                    },
                    {
                      "text": "Law of Demeter (Principle of Least Knowledge)",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--law-of-demeter-principle-of-least-knowledge-278"
                    },
                    {
                      "text": "POLA (Principle of Least Astonishment)",
                      "ordered": false,
                      "children": [],
                      "id": "general-principles--pola-principle-of-least-astonishment-279"
                    },
                    {
                      "text": "Cohesion & Coupling",
                      "ordered": false,
                      "children": [
                        {
                          "text": "High Cohesion",
                          "ordered": false,
                          "children": [],
                          "id": "general-principles--high-cohesion-281"
                        },
                        {
                          "text": "Low Coupling",
                          "ordered": false,
                          "children": [],
                          "id": "general-principles--low-coupling-282"
                        }
                      ],
                      "id": "general-principles--cohesion-and-coupling-280"
                    }
                  ]
                }
              ],
              "children": []
            }
          ]
        },
        {
          "id": "34-gof-design-patterns",
          "title": "3.4 GoF Design Patterns",
          "level": 2,
          "blocks": [],
          "children": [
            {
              "id": "creational-patterns-5",
              "title": "Creational Patterns (5)",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Singleton",
                      "ordered": false,
                      "children": [],
                      "id": "creational-patterns-5--singleton-283"
                    },
                    {
                      "text": "Factory Method",
                      "ordered": false,
                      "children": [],
                      "id": "creational-patterns-5--factory-method-284"
                    },
                    {
                      "text": "Abstract Factory",
                      "ordered": false,
                      "children": [],
                      "id": "creational-patterns-5--abstract-factory-285"
                    },
                    {
                      "text": "Builder",
                      "ordered": false,
                      "children": [],
                      "id": "creational-patterns-5--builder-286"
                    },
                    {
                      "text": "Prototype",
                      "ordered": false,
                      "children": [],
                      "id": "creational-patterns-5--prototype-287"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "structural-patterns-7",
              "title": "Structural Patterns (7)",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Adapter",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--adapter-288"
                    },
                    {
                      "text": "Bridge",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--bridge-289"
                    },
                    {
                      "text": "Composite",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--composite-290"
                    },
                    {
                      "text": "Decorator",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--decorator-291"
                    },
                    {
                      "text": "Facade",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--facade-292"
                    },
                    {
                      "text": "Flyweight",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--flyweight-293"
                    },
                    {
                      "text": "Proxy",
                      "ordered": false,
                      "children": [],
                      "id": "structural-patterns-7--proxy-294"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "behavioral-patterns-11",
              "title": "Behavioral Patterns (11)",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Chain of Responsibility",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--chain-of-responsibility-295"
                    },
                    {
                      "text": "Command",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--command-296"
                    },
                    {
                      "text": "Interpreter",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--interpreter-297"
                    },
                    {
                      "text": "Iterator",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--iterator-298"
                    },
                    {
                      "text": "Mediator",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--mediator-299"
                    },
                    {
                      "text": "Memento",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--memento-300"
                    },
                    {
                      "text": "Observer",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--observer-301"
                    },
                    {
                      "text": "State",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--state-302"
                    },
                    {
                      "text": "Strategy",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--strategy-303"
                    },
                    {
                      "text": "Template Method",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--template-method-304"
                    },
                    {
                      "text": "Visitor",
                      "ordered": false,
                      "children": [],
                      "id": "behavioral-patterns-11--visitor-305"
                    }
                  ]
                }
              ],
              "children": []
            }
          ]
        },
        {
          "id": "35-uml-and-object-modeling",
          "title": "3.5 UML & Object Modeling",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Class Diagram",
                  "ordered": false,
                  "children": [],
                  "id": "35-uml-and-object-modeling--class-diagram-306"
                },
                {
                  "text": "Use Case Diagram",
                  "ordered": false,
                  "children": [],
                  "id": "35-uml-and-object-modeling--use-case-diagram-307"
                },
                {
                  "text": "Sequence Diagram",
                  "ordered": false,
                  "children": [],
                  "id": "35-uml-and-object-modeling--sequence-diagram-308"
                },
                {
                  "text": "Activity Diagram",
                  "ordered": false,
                  "children": [],
                  "id": "35-uml-and-object-modeling--activity-diagram-309"
                },
                {
                  "text": "State Machine Diagram",
                  "ordered": false,
                  "children": [],
                  "id": "35-uml-and-object-modeling--state-machine-diagram-310"
                },
                {
                  "text": "Object / Domain Modeling",
                  "ordered": false,
                  "children": [],
                  "id": "35-uml-and-object-modeling--object-domain-modeling-311"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "04-application-architecture",
      "title": "04 — Application Architecture",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "41-architectural-styles",
          "title": "4.1 Architectural Styles",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "System Structure",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Monolithic Architecture",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--monolithic-architecture"
                    },
                    {
                      "text": "Modular Monolith",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--modular-monolith"
                    },
                    {
                      "text": "Microservices Architecture",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--microservices-architecture"
                    },
                    {
                      "text": "Service-Oriented Architecture (SOA)",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--soa"
                    }
                  ],
                  "id": "41-architectural-styles--system-structure"
                },
                {
                  "text": "Communication & Distribution",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Client-Server Architecture",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--client-server-architecture"
                    },
                    {
                      "text": "Event-Driven Architecture (EDA)",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--event-driven-architecture"
                    },
                    {
                      "text": "Serverless Architecture / FaaS",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--serverless-architecture"
                    }
                  ],
                  "id": "41-architectural-styles--communication-and-distribution"
                },
                {
                  "text": "Internal Organization",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Layered Architecture (N-Tier)",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--layered-architecture"
                    },
                    {
                      "text": "Pipe-and-Filter Architecture",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--pipe-and-filter-architecture"
                    },
                    {
                      "text": "Microkernel / Plugin Architecture",
                      "ordered": false,
                      "children": [],
                      "id": "41-architectural-styles--microkernel-plugin-architecture"
                    }
                  ],
                  "id": "41-architectural-styles--internal-organization"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "42-architectural-patterns",
          "title": "4.2 Architectural Patterns",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Clean Architecture (Uncle Bob)",
                  "ordered": false,
                  "children": [],
                  "id": "42-architectural-patterns--clean-architecture-uncle-bob-322"
                },
                {
                  "text": "Hexagonal Architecture (Ports and Adapters)",
                  "ordered": false,
                  "children": [],
                  "id": "42-architectural-patterns--hexagonal-architecture-ports-and-adapters-323"
                },
                {
                  "text": "Onion Architecture",
                  "ordered": false,
                  "children": [],
                  "id": "42-architectural-patterns--onion-architecture-324"
                },
                {
                  "text": "Model-View-Controller (MVC)",
                  "ordered": false,
                  "children": [],
                  "id": "42-architectural-patterns--model-view-controller-mvc-325"
                },
                {
                  "text": "Model-View-Presenter (MVP)",
                  "ordered": false,
                  "children": [],
                  "id": "42-architectural-patterns--model-view-presenter-mvp-326"
                },
                {
                  "text": "Model-View-ViewModel (MVVM)",
                  "ordered": false,
                  "children": [],
                  "id": "42-architectural-patterns--model-view-viewmodel-mvvm-327"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "43-core-concepts-and-principles",
          "title": "4.3 Core Concepts & Principles",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Separation of Concerns (SoC)",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--separation-of-concerns-soc-328"
                },
                {
                  "text": "Domain-Driven Design (DDD) Integration",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--domain-driven-design-ddd-integration-329"
                },
                {
                  "text": "Inversion of Control (IoC)",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--inversion-of-control-ioc-330"
                },
                {
                  "text": "Dependency Injection (DI)",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--dependency-injection-di-331"
                },
                {
                  "text": "Dependency Inversion",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--dependency-inversion-332"
                },
                {
                  "text": "Ports and Adapters (Interfaces and Implementations)",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--ports-and-adapters-interfaces-and-implementations-333"
                },
                {
                  "text": "Boundary Management",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--boundary-management-334"
                },
                {
                  "text": "Dependency Rules",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--dependency-rules-335"
                },
                {
                  "text": "Data Transfer Objects (DTOs)",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--data-transfer-objects-dtos-336"
                },
                {
                  "text": "Mappers",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--mappers-337"
                },
                {
                  "text": "Decoupling Business Logic from Infrastructure",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Databases",
                      "ordered": false,
                      "children": [],
                      "id": "43-core-concepts-and-principles--databases-339"
                    },
                    {
                      "text": "Frameworks",
                      "ordered": false,
                      "children": [],
                      "id": "43-core-concepts-and-principles--frameworks-340"
                    },
                    {
                      "text": "External APIs",
                      "ordered": false,
                      "children": [],
                      "id": "43-core-concepts-and-principles--external-apis-341"
                    }
                  ],
                  "id": "43-core-concepts-and-principles--decoupling-business-logic-from-infrastructure-338"
                },
                {
                  "text": "High Cohesion / Low Coupling",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--high-cohesion-low-coupling-342"
                },
                {
                  "text": "Testability and Modifiability",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--testability-and-modifiability-343"
                },
                {
                  "text": "Architectural Trade-offs",
                  "ordered": false,
                  "children": [],
                  "id": "43-core-concepts-and-principles--architectural-trade-offs-344"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "44-application-organization",
          "title": "4.4 Application Organization",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Modularization",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--modularization-345"
                },
                {
                  "text": "Module Boundaries",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--module-boundaries-346"
                },
                {
                  "text": "Package by Layer",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--package-by-layer-347"
                },
                {
                  "text": "Package by Feature",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--package-by-feature-348"
                },
                {
                  "text": "Component-Based Design",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--component-based-design-349"
                },
                {
                  "text": "Plugin Architecture",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--plugin-architecture-350"
                },
                {
                  "text": "Internal vs External Interfaces",
                  "ordered": false,
                  "children": [],
                  "id": "44-application-organization--internal-vs-external-interfaces-351"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "45-integration-architecture",
          "title": "4.5 Integration Architecture",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "API Integration",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--api-integration-352"
                },
                {
                  "text": "Synchronous vs Asynchronous Communication",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--synchronous-vs-asynchronous-communication-353"
                },
                {
                  "text": "Point-to-Point Integration",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--point-to-point-integration-354"
                },
                {
                  "text": "Hub-and-Spoke",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--hub-and-spoke-355"
                },
                {
                  "text": "Enterprise Service Bus (ESB)",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--enterprise-service-bus-esb-356"
                },
                {
                  "text": "API-Led Connectivity",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--api-led-connectivity-357"
                },
                {
                  "text": "Event-Driven Integration",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--event-driven-integration-358"
                },
                {
                  "text": "Canonical Data Model",
                  "ordered": false,
                  "children": [],
                  "id": "45-integration-architecture--canonical-data-model-359"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "05-presentation-architecture",
      "title": "05 — Presentation Architecture",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "51-core-architectural-patterns",
          "title": "5.1 Core Architectural Patterns",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "MVC (Model-View-Controller)",
                  "ordered": false,
                  "children": [],
                  "id": "51-core-architectural-patterns--mvc-model-view-controller-360"
                },
                {
                  "text": "MVP (Model-View-Presenter)",
                  "ordered": false,
                  "children": [],
                  "id": "51-core-architectural-patterns--mvp-model-view-presenter-361"
                },
                {
                  "text": "MVVM (Model-View-ViewModel)",
                  "ordered": false,
                  "children": [],
                  "id": "51-core-architectural-patterns--mvvm-model-view-viewmodel-362"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "52-advanced-and-mobile-specific-patterns",
          "title": "5.2 Advanced & Mobile-Specific Patterns",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "VIPER (View-Interactor-Presenter-Entity-Router)",
                  "ordered": false,
                  "children": [],
                  "id": "52-advanced-and-mobile-specific-patterns--viper-view-interactor-presenter-entity-router-363"
                },
                {
                  "text": "MVI (Model-View-Intent)",
                  "ordered": false,
                  "children": [],
                  "id": "52-advanced-and-mobile-specific-patterns--mvi-model-view-intent-364"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "53-modern-frontend-and-component-architectures",
          "title": "5.3 Modern Frontend & Component Architectures",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Component-Based Architecture",
                  "ordered": false,
                  "children": [
                    {
                      "text": "React",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--react-366"
                    },
                    {
                      "text": "Vue",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--vue-367"
                    },
                    {
                      "text": "Svelte",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--svelte-368"
                    },
                    {
                      "text": "Angular",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--angular-369"
                    }
                  ],
                  "id": "53-modern-frontend-and-component-architectures--component-based-architecture-365"
                },
                {
                  "text": "Container / Presentational Components",
                  "ordered": false,
                  "children": [],
                  "id": "53-modern-frontend-and-component-architectures--container-presentational-components-370"
                },
                {
                  "text": "Smart / Dumb Components",
                  "ordered": false,
                  "children": [],
                  "id": "53-modern-frontend-and-component-architectures--smart-dumb-components-371"
                },
                {
                  "text": "Unidirectional Data Flow",
                  "ordered": false,
                  "children": [],
                  "id": "53-modern-frontend-and-component-architectures--unidirectional-data-flow-372"
                },
                {
                  "text": "Flux Pattern",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Redux",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--redux-374"
                    },
                    {
                      "text": "NgRx",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--ngrx-375"
                    },
                    {
                      "text": "Pinia",
                      "ordered": false,
                      "children": [],
                      "id": "53-modern-frontend-and-component-architectures--pinia-376"
                    }
                  ],
                  "id": "53-modern-frontend-and-component-architectures--flux-pattern-373"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "54-state-management-and-reactive-patterns",
          "title": "5.4 State Management & Reactive Patterns",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Local State",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--local-state-377"
                },
                {
                  "text": "Global State",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--global-state-378"
                },
                {
                  "text": "State Management",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--state-management-379"
                },
                {
                  "text": "Reactive State",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--reactive-state-380"
                },
                {
                  "text": "Observable",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--observable-381"
                },
                {
                  "text": "Immutable State",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--immutable-state-382"
                },
                {
                  "text": "BLoC",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--bloc-383"
                },
                {
                  "text": "Provider",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--provider-384"
                },
                {
                  "text": "Riverpod",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--riverpod-385"
                },
                {
                  "text": "Signals",
                  "ordered": false,
                  "children": [],
                  "id": "54-state-management-and-reactive-patterns--signals-386"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "55-core-concepts-and-mechanisms",
          "title": "5.5 Core Concepts & Mechanisms",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Data Binding",
                  "ordered": false,
                  "children": [
                    {
                      "text": "One-Way Binding",
                      "ordered": false,
                      "children": [],
                      "id": "55-core-concepts-and-mechanisms--one-way-binding-388"
                    },
                    {
                      "text": "Two-Way Binding",
                      "ordered": false,
                      "children": [],
                      "id": "55-core-concepts-and-mechanisms--two-way-binding-389"
                    }
                  ],
                  "id": "55-core-concepts-and-mechanisms--data-binding-387"
                },
                {
                  "text": "Event Handling",
                  "ordered": false,
                  "children": [],
                  "id": "55-core-concepts-and-mechanisms--event-handling-390"
                },
                {
                  "text": "State Management & Reactivity",
                  "ordered": false,
                  "children": [],
                  "id": "55-core-concepts-and-mechanisms--state-management-and-reactivity-391"
                },
                {
                  "text": "Separation of UI Rendering from Business Logic",
                  "ordered": false,
                  "children": [],
                  "id": "55-core-concepts-and-mechanisms--separation-of-ui-rendering-from-business-logic-392"
                },
                {
                  "text": "Navigation",
                  "ordered": false,
                  "children": [],
                  "id": "55-core-concepts-and-mechanisms--navigation-393"
                },
                {
                  "text": "UI State",
                  "ordered": false,
                  "children": [],
                  "id": "55-core-concepts-and-mechanisms--ui-state-394"
                },
                {
                  "text": "Rendering Lifecycle",
                  "ordered": false,
                  "children": [],
                  "id": "55-core-concepts-and-mechanisms--rendering-lifecycle-395"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "06-patterns-of-enterprise-application-architecture-poeaa",
      "title": "06 — Patterns of Enterprise Application Architecture (PoEAA)",
      "level": 1,
      "blocks": [
        {
          "type": "blockquote",
          "text": "Reference classification: Martin Fowler's Patterns of Enterprise Application Architecture. Pattern names are retained, with spelling and grouping normalized. Some patterns have relationships or subtypes; those are noted below."
        }
      ],
      "children": [
        {
          "id": "61-domain-logic-patterns-4",
          "title": "6.1 Domain Logic Patterns (4)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Transaction Script",
                  "ordered": false,
                  "children": [],
                  "id": "61-domain-logic-patterns-4--transaction-script-396"
                },
                {
                  "text": "Domain Model",
                  "ordered": false,
                  "children": [],
                  "id": "61-domain-logic-patterns-4--domain-model-397"
                },
                {
                  "text": "Table Module",
                  "ordered": false,
                  "children": [],
                  "id": "61-domain-logic-patterns-4--table-module-398"
                },
                {
                  "text": "Service Layer",
                  "ordered": false,
                  "children": [],
                  "id": "61-domain-logic-patterns-4--service-layer-399"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "62-data-source-architectural-patterns-4",
          "title": "6.2 Data Source Architectural Patterns (4)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Table Data Gateway",
                  "ordered": false,
                  "children": [],
                  "id": "62-data-source-architectural-patterns-4--table-data-gateway-400"
                },
                {
                  "text": "Row Data Gateway",
                  "ordered": false,
                  "children": [],
                  "id": "62-data-source-architectural-patterns-4--row-data-gateway-401"
                },
                {
                  "text": "Active Record",
                  "ordered": false,
                  "children": [],
                  "id": "62-data-source-architectural-patterns-4--active-record-402"
                },
                {
                  "text": "Data Mapper",
                  "ordered": false,
                  "children": [],
                  "id": "62-data-source-architectural-patterns-4--data-mapper-403"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "63-object-relational-behavioral-patterns-3",
          "title": "6.3 Object-Relational Behavioral Patterns (3)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Unit of Work",
                  "ordered": false,
                  "children": [],
                  "id": "63-object-relational-behavioral-patterns-3--unit-of-work-404"
                },
                {
                  "text": "Identity Map",
                  "ordered": false,
                  "children": [],
                  "id": "63-object-relational-behavioral-patterns-3--identity-map-405"
                },
                {
                  "text": "Lazy Load",
                  "ordered": false,
                  "children": [],
                  "id": "63-object-relational-behavioral-patterns-3--lazy-load-406"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "64-object-relational-structural-patterns",
          "title": "6.4 Object-Relational Structural Patterns",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Identity Field",
                  "ordered": false,
                  "children": [],
                  "id": "64-object-relational-structural-patterns--identity-field-407"
                },
                {
                  "text": "Foreign Key Mapping",
                  "ordered": false,
                  "children": [],
                  "id": "64-object-relational-structural-patterns--foreign-key-mapping-408"
                },
                {
                  "text": "Association Table Mapping",
                  "ordered": false,
                  "children": [],
                  "id": "64-object-relational-structural-patterns--association-table-mapping-409"
                },
                {
                  "text": "Dependent Mapping",
                  "ordered": false,
                  "children": [],
                  "id": "64-object-relational-structural-patterns--dependent-mapping-410"
                },
                {
                  "text": "Embedded Value",
                  "ordered": false,
                  "children": [],
                  "id": "64-object-relational-structural-patterns--embedded-value-411"
                },
                {
                  "text": "Serialized LOB",
                  "ordered": false,
                  "children": [],
                  "id": "64-object-relational-structural-patterns--serialized-lob-412"
                },
                {
                  "text": "Inheritance Mappers",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Single Table Inheritance",
                      "ordered": false,
                      "children": [],
                      "id": "64-object-relational-structural-patterns--single-table-inheritance-414"
                    },
                    {
                      "text": "Class Table Inheritance",
                      "ordered": false,
                      "children": [],
                      "id": "64-object-relational-structural-patterns--class-table-inheritance-415"
                    },
                    {
                      "text": "Concrete Table Inheritance",
                      "ordered": false,
                      "children": [],
                      "id": "64-object-relational-structural-patterns--concrete-table-inheritance-416"
                    }
                  ],
                  "id": "64-object-relational-structural-patterns--inheritance-mappers-413"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "65-object-relational-metadata-mapping-patterns-3",
          "title": "6.5 Object-Relational Metadata Mapping Patterns (3)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Metadata Mapping",
                  "ordered": false,
                  "children": [],
                  "id": "65-object-relational-metadata-mapping-patterns-3--metadata-mapping-417"
                },
                {
                  "text": "Query Object",
                  "ordered": false,
                  "children": [],
                  "id": "65-object-relational-metadata-mapping-patterns-3--query-object-418"
                },
                {
                  "text": "Repository",
                  "ordered": false,
                  "children": [],
                  "id": "65-object-relational-metadata-mapping-patterns-3--repository-419"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "66-web-presentation-patterns-7",
          "title": "6.6 Web Presentation Patterns (7)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Model View Controller",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--model-view-controller-420"
                },
                {
                  "text": "Page Controller",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--page-controller-421"
                },
                {
                  "text": "Front Controller",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--front-controller-422"
                },
                {
                  "text": "Template View",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--template-view-423"
                },
                {
                  "text": "Transform View",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--transform-view-424"
                },
                {
                  "text": "Two-Step View",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--two-step-view-425"
                },
                {
                  "text": "Application Controller",
                  "ordered": false,
                  "children": [],
                  "id": "66-web-presentation-patterns-7--application-controller-426"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "67-distribution-patterns-2",
          "title": "6.7 Distribution Patterns (2)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Remote Facade",
                  "ordered": false,
                  "children": [],
                  "id": "67-distribution-patterns-2--remote-facade-427"
                },
                {
                  "text": "Data Transfer Object (DTO)",
                  "ordered": false,
                  "children": [],
                  "id": "67-distribution-patterns-2--data-transfer-object-dto-428"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "68-offline-concurrency-patterns-4",
          "title": "6.8 Offline Concurrency Patterns (4)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Optimistic Offline Lock",
                  "ordered": false,
                  "children": [],
                  "id": "68-offline-concurrency-patterns-4--optimistic-offline-lock-429"
                },
                {
                  "text": "Pessimistic Offline Lock",
                  "ordered": false,
                  "children": [],
                  "id": "68-offline-concurrency-patterns-4--pessimistic-offline-lock-430"
                },
                {
                  "text": "Coarse-Grained Lock",
                  "ordered": false,
                  "children": [],
                  "id": "68-offline-concurrency-patterns-4--coarse-grained-lock-431"
                },
                {
                  "text": "Implicit Lock",
                  "ordered": false,
                  "children": [],
                  "id": "68-offline-concurrency-patterns-4--implicit-lock-432"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "69-session-state-patterns-3",
          "title": "6.9 Session State Patterns (3)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Client Session State",
                  "ordered": false,
                  "children": [],
                  "id": "69-session-state-patterns-3--client-session-state-433"
                },
                {
                  "text": "Server Session State",
                  "ordered": false,
                  "children": [],
                  "id": "69-session-state-patterns-3--server-session-state-434"
                },
                {
                  "text": "Database Session State",
                  "ordered": false,
                  "children": [],
                  "id": "69-session-state-patterns-3--database-session-state-435"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "610-base-patterns-11",
          "title": "6.10 Base Patterns (11)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Gateway",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--gateway-436"
                },
                {
                  "text": "Service Stub",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--service-stub-437"
                },
                {
                  "text": "Mapper",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--mapper-438"
                },
                {
                  "text": "Layer Supertype",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--layer-supertype-439"
                },
                {
                  "text": "Separated Interface",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--separated-interface-440"
                },
                {
                  "text": "Registry",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--registry-441"
                },
                {
                  "text": "Value Object",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--value-object-442"
                },
                {
                  "text": "Money",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--money-443"
                },
                {
                  "text": "Special Case",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--special-case-444"
                },
                {
                  "text": "Plugin",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--plugin-445"
                },
                {
                  "text": "Record Set",
                  "ordered": false,
                  "children": [],
                  "id": "610-base-patterns-11--record-set-446"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "07-domain-driven-design-ddd",
      "title": "07 — Domain-Driven Design (DDD)",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "71-strategic-ddd",
          "title": "7.1 Strategic DDD",
          "level": 2,
          "blocks": [],
          "children": [
            {
              "id": "domain-understanding",
              "title": "Domain Understanding",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Domain",
                      "ordered": false,
                      "children": [],
                      "id": "domain-understanding--domain-447"
                    },
                    {
                      "text": "Subdomains",
                      "ordered": false,
                      "children": [
                        {
                          "text": "Core Domain",
                          "ordered": false,
                          "children": [],
                          "id": "domain-understanding--core-domain-449"
                        },
                        {
                          "text": "Supporting Subdomain",
                          "ordered": false,
                          "children": [],
                          "id": "domain-understanding--supporting-subdomain-450"
                        },
                        {
                          "text": "Generic Subdomain",
                          "ordered": false,
                          "children": [],
                          "id": "domain-understanding--generic-subdomain-451"
                        }
                      ],
                      "id": "domain-understanding--subdomains-448"
                    },
                    {
                      "text": "Ubiquitous Language",
                      "ordered": false,
                      "children": [],
                      "id": "domain-understanding--ubiquitous-language-452"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "model-boundaries",
              "title": "Model Boundaries",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Bounded Context",
                      "ordered": false,
                      "children": [],
                      "id": "model-boundaries--bounded-context-453"
                    },
                    {
                      "text": "Context Map",
                      "ordered": false,
                      "children": [],
                      "id": "model-boundaries--context-map-454"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "context-mapping-patterns",
              "title": "Context Mapping Patterns",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Partnership",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--partnership-455"
                    },
                    {
                      "text": "Shared Kernel",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--shared-kernel-456"
                    },
                    {
                      "text": "Customer-Supplier",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--customer-supplier-457"
                    },
                    {
                      "text": "Conformist",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--conformist-458"
                    },
                    {
                      "text": "Anti-Corruption Layer",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--anti-corruption-layer-459"
                    },
                    {
                      "text": "Open Host Service",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--open-host-service-460"
                    },
                    {
                      "text": "Published Language",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--published-language-461"
                    },
                    {
                      "text": "Separate Ways",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--separate-ways-462"
                    },
                    {
                      "text": "Big Ball of Mud",
                      "ordered": false,
                      "children": [],
                      "id": "context-mapping-patterns--big-ball-of-mud-463"
                    }
                  ]
                }
              ],
              "children": []
            }
          ]
        },
        {
          "id": "72-tactical-ddd",
          "title": "7.2 Tactical DDD",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Entity",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--entity-464"
                },
                {
                  "text": "Value Object",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--value-object-465"
                },
                {
                  "text": "Aggregate",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--aggregate-466"
                },
                {
                  "text": "Aggregate Root",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--aggregate-root-467"
                },
                {
                  "text": "Repository",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--repository-468"
                },
                {
                  "text": "Domain Service",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--domain-service-469"
                },
                {
                  "text": "Domain Event",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--domain-event-470"
                },
                {
                  "text": "Factory",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--factory-471"
                },
                {
                  "text": "Application Service",
                  "ordered": false,
                  "children": [],
                  "id": "72-tactical-ddd--application-service-472"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "73-ddd-implementation-and-modeling-concepts",
          "title": "7.3 DDD Implementation & Modeling Concepts",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Domain Model",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--domain-model-473"
                },
                {
                  "text": "Domain Layer",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--domain-layer-474"
                },
                {
                  "text": "Application Layer",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--application-layer-475"
                },
                {
                  "text": "Infrastructure Layer",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--infrastructure-layer-476"
                },
                {
                  "text": "Invariants",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--invariants-477"
                },
                {
                  "text": "Aggregate Boundaries",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--aggregate-boundaries-478"
                },
                {
                  "text": "Transaction Boundaries",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--transaction-boundaries-479"
                },
                {
                  "text": "Domain Event vs Integration Event",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--domain-event-vs-integration-event-480"
                },
                {
                  "text": "Eventual Consistency",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--eventual-consistency-481"
                },
                {
                  "text": "Anti-Corruption Layer Implementation",
                  "ordered": false,
                  "children": [],
                  "id": "73-ddd-implementation-and-modeling-concepts--anti-corruption-layer-implementation-482"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "08-concurrency-patterns",
      "title": "08 — Concurrency Patterns",
      "level": 1,
      "blocks": [
        {
          "type": "blockquote",
          "text": "A curated set of ten concurrency patterns covering task execution, synchronization, safety, and event-driven design."
        },
        {
          "type": "list",
          "items": [
            {
              "text": "Producer–Consumer — فصل الإنتاج عن الاستهلاك",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--producer-consumer"
            },
            {
              "text": "Thread Pool — مجموعة Threads يعاد استخدامها",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--thread-pool"
            },
            {
              "text": "Future / Promise — تمثيل نتيجة مستقبلية",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--future-promise"
            },
            {
              "text": "Read–Write Lock — تعدد القراءات وانفراد الكتابة",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--read-write-lock"
            },
            {
              "text": "Monitor / Condition Variable — حماية الحالة وتنظيم الانتظار على شرط",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--monitor-condition-variable"
            },
            {
              "text": "Thread Confinement — تخصيص البيانات لـThread واحد",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--thread-confinement"
            },
            {
              "text": "Fork–Join — تقسيم المهمة وتجميع النتائج",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--fork-join"
            },
            {
              "text": "Reactor — استقبال الأحداث وتوجيهها للمعالجات",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--reactor"
            },
            {
              "text": "Barrier Synchronization — انتظار وصول الجميع قبل المتابعة",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--barrier-synchronization"
            },
            {
              "text": "Active Object — فصل الطلب عن التنفيذ",
              "ordered": false,
              "children": [],
              "id": "08-concurrency-patterns--active-object"
            }
          ]
        }
      ],
      "children": []
    },
    {
      "id": "09-enterprise-integration-patterns-eip",
      "title": "09 — Enterprise Integration Patterns (EIP)",
      "level": 1,
      "blocks": [
        {
          "type": "blockquote",
          "text": "A curated set of ten enterprise integration patterns for messaging, routing, and reliable delivery — not the full EIP catalog."
        },
        {
          "type": "list",
          "items": [
            {
              "text": "Message Channel",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--message-channel"
            },
            {
              "text": "Content-Based Router",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--content-based-router"
            },
            {
              "text": "Message Translator",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--message-translator"
            },
            {
              "text": "Splitter",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--splitter"
            },
            {
              "text": "Aggregator",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--aggregator"
            },
            {
              "text": "Request–Reply",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--request-reply"
            },
            {
              "text": "Competing Consumers",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--competing-consumers"
            },
            {
              "text": "Dead Letter Channel",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--dead-letter-channel"
            },
            {
              "text": "Idempotent Receiver",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--idempotent-receiver"
            },
            {
              "text": "Transactional Outbox",
              "ordered": false,
              "children": [],
              "id": "09-enterprise-integration-patterns-eip--transactional-outbox"
            }
          ]
        }
      ],
      "children": []
    },
    {
      "id": "10-system-design",
      "title": "10 — System Design",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "101-system-design-fundamentals",
          "title": "10.1 System Design Fundamentals",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "What is System Design?",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--what-is-system-design-683"
                },
                {
                  "text": "Functional vs Non-Functional Requirements",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--functional-vs-non-functional-requirements-684"
                },
                {
                  "text": "Scalability",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--scalability-685"
                },
                {
                  "text": "Reliability",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--reliability-686"
                },
                {
                  "text": "Availability",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--availability-687"
                },
                {
                  "text": "Maintainability",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--maintainability-688"
                },
                {
                  "text": "Performance",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--performance-689"
                },
                {
                  "text": "Consistency",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--consistency-690"
                },
                {
                  "text": "Latency vs Throughput",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--latency-vs-throughput-691"
                },
                {
                  "text": "Capacity Estimation",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--capacity-estimation-692"
                },
                {
                  "text": "Load Estimation",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--load-estimation-693"
                },
                {
                  "text": "Back-of-the-Envelope Calculations",
                  "ordered": false,
                  "children": [],
                  "id": "101-system-design-fundamentals--back-of-the-envelope-calculations-694"
                },
                {
                  "text": "Quality Attributes and Trade-offs",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Modifiability",
                      "ordered": false,
                      "children": [],
                      "id": "101-system-design-fundamentals--modifiability-696"
                    },
                    {
                      "text": "Testability",
                      "ordered": false,
                      "children": [],
                      "id": "101-system-design-fundamentals--testability-697"
                    },
                    {
                      "text": "Extensibility",
                      "ordered": false,
                      "children": [],
                      "id": "101-system-design-fundamentals--extensibility-698"
                    },
                    {
                      "text": "Portability",
                      "ordered": false,
                      "children": [],
                      "id": "101-system-design-fundamentals--portability-699"
                    },
                    {
                      "text": "Interoperability",
                      "ordered": false,
                      "children": [],
                      "id": "101-system-design-fundamentals--interoperability-700"
                    },
                    {
                      "text": "Security",
                      "ordered": false,
                      "children": [],
                      "id": "101-system-design-fundamentals--security-701"
                    }
                  ],
                  "id": "101-system-design-fundamentals--quality-attributes-and-trade-offs-695"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "102-networking-and-communication",
          "title": "10.2 Networking & Communication",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "OSI Model",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--osi-model-702"
                },
                {
                  "text": "TCP/IP Model",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--tcp-ip-model-703"
                },
                {
                  "text": "HTTP / HTTPS",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--http-https-704"
                },
                {
                  "text": "TCP vs UDP",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--tcp-vs-udp-705"
                },
                {
                  "text": "TCP Handshake",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--tcp-handshake-706"
                },
                {
                  "text": "Connection Lifecycle",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--connection-lifecycle-707"
                },
                {
                  "text": "REST vs SOAP",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--rest-vs-soap-708"
                },
                {
                  "text": "gRPC",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--grpc-709"
                },
                {
                  "text": "WebSockets",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--websockets-710"
                },
                {
                  "text": "Long Polling",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--long-polling-711"
                },
                {
                  "text": "DNS",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--dns-712"
                },
                {
                  "text": "CDN",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--cdn-713"
                },
                {
                  "text": "Reverse Proxy",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--reverse-proxy-714"
                },
                {
                  "text": "Forward Proxy",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--forward-proxy-715"
                },
                {
                  "text": "NAT",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--nat-716"
                },
                {
                  "text": "API Gateway",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--api-gateway-717"
                },
                {
                  "text": "Connection Pooling",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--connection-pooling-718"
                },
                {
                  "text": "Rate Limiting",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--rate-limiting-719"
                },
                {
                  "text": "Throttling",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--throttling-720"
                },
                {
                  "text": "TLS",
                  "ordered": false,
                  "children": [],
                  "id": "102-networking-and-communication--tls-721"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "103-data-storage-databases",
          "title": "10.3 Data Storage (Databases)",
          "level": 2,
          "blocks": [],
          "children": [
            {
              "id": "relational-databases",
              "title": "Relational Databases",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "MySQL / PostgreSQL",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--mysql-postgresql-722"
                    },
                    {
                      "text": "ACID",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--acid-723"
                    },
                    {
                      "text": "Indexes",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--indexes-724"
                    },
                    {
                      "text": "Transactions",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--transactions-725"
                    },
                    {
                      "text": "Normalization vs Denormalization",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--normalization-vs-denormalization-726"
                    },
                    {
                      "text": "Read Replicas",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--read-replicas-727"
                    },
                    {
                      "text": "Sharding",
                      "ordered": false,
                      "children": [],
                      "id": "relational-databases--sharding-728"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "nosql-databases",
              "title": "NoSQL Databases",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Key-Value (Redis, DynamoDB)",
                      "ordered": false,
                      "children": [],
                      "id": "nosql-databases--key-value-redis-dynamodb-729"
                    },
                    {
                      "text": "Document (MongoDB)",
                      "ordered": false,
                      "children": [],
                      "id": "nosql-databases--document-mongodb-730"
                    },
                    {
                      "text": "Column Family (Cassandra)",
                      "ordered": false,
                      "children": [],
                      "id": "nosql-databases--column-family-cassandra-731"
                    },
                    {
                      "text": "Graph DB (Neo4j)",
                      "ordered": false,
                      "children": [],
                      "id": "nosql-databases--graph-db-neo4j-732"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "cap-theorem",
              "title": "CAP Theorem",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Consistency",
                      "ordered": false,
                      "children": [],
                      "id": "cap-theorem--consistency-733"
                    },
                    {
                      "text": "Availability",
                      "ordered": false,
                      "children": [],
                      "id": "cap-theorem--availability-734"
                    },
                    {
                      "text": "Partition Tolerance",
                      "ordered": false,
                      "children": [],
                      "id": "cap-theorem--partition-tolerance-735"
                    }
                  ]
                }
              ],
              "children": []
            },
            {
              "id": "database-design",
              "title": "Database Design",
              "level": 3,
              "blocks": [
                {
                  "type": "list",
                  "items": [
                    {
                      "text": "Schema Design",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--schema-design-736"
                    },
                    {
                      "text": "Data Modeling",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--data-modeling-737"
                    },
                    {
                      "text": "Hot Partitions",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--hot-partitions-738"
                    },
                    {
                      "text": "Data Migration",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--data-migration-739"
                    },
                    {
                      "text": "OLTP vs OLAP",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--oltp-vs-olap-740"
                    },
                    {
                      "text": "Data Warehouse",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--data-warehouse-741"
                    },
                    {
                      "text": "Read Models",
                      "ordered": false,
                      "children": [],
                      "id": "database-design--read-models-742"
                    }
                  ]
                }
              ],
              "children": []
            }
          ]
        },
        {
          "id": "104-caching",
          "title": "10.4 Caching",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "What is Caching?",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--what-is-caching-743"
                },
                {
                  "text": "Cache vs DB",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--cache-vs-db-744"
                },
                {
                  "text": "Cache Hit / Miss",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--cache-hit-miss-745"
                },
                {
                  "text": "Cache Eviction Policies",
                  "ordered": false,
                  "children": [
                    {
                      "text": "LRU",
                      "ordered": false,
                      "children": [],
                      "id": "104-caching--lru-747"
                    },
                    {
                      "text": "LFU",
                      "ordered": false,
                      "children": [],
                      "id": "104-caching--lfu-748"
                    },
                    {
                      "text": "FIFO",
                      "ordered": false,
                      "children": [],
                      "id": "104-caching--fifo-749"
                    }
                  ],
                  "id": "104-caching--cache-eviction-policies-746"
                },
                {
                  "text": "Cache-Aside",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--cache-aside-750"
                },
                {
                  "text": "Read-Through",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--read-through-751"
                },
                {
                  "text": "Write-Through",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--write-through-752"
                },
                {
                  "text": "Write-Back",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--write-back-753"
                },
                {
                  "text": "Write-Around",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--write-around-754"
                },
                {
                  "text": "Redis",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--redis-755"
                },
                {
                  "text": "Memcached",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--memcached-756"
                },
                {
                  "text": "CDN Caching",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--cdn-caching-757"
                },
                {
                  "text": "Cache Invalidation",
                  "ordered": false,
                  "children": [],
                  "id": "104-caching--cache-invalidation-758"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "105-scalability-patterns",
          "title": "10.5 Scalability Patterns",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Vertical Scaling",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--vertical-scaling-759"
                },
                {
                  "text": "Horizontal Scaling",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--horizontal-scaling-760"
                },
                {
                  "text": "Stateless Services",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--stateless-services-761"
                },
                {
                  "text": "Stateful Services",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--stateful-services-762"
                },
                {
                  "text": "Load Balancing",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Round Robin",
                      "ordered": false,
                      "children": [],
                      "id": "105-scalability-patterns--round-robin-764"
                    },
                    {
                      "text": "Least Connections",
                      "ordered": false,
                      "children": [],
                      "id": "105-scalability-patterns--least-connections-765"
                    },
                    {
                      "text": "Hash-based",
                      "ordered": false,
                      "children": [],
                      "id": "105-scalability-patterns--hash-based-766"
                    },
                    {
                      "text": "Consistent Hashing",
                      "ordered": false,
                      "children": [],
                      "id": "105-scalability-patterns--consistent-hashing-767"
                    }
                  ],
                  "id": "105-scalability-patterns--load-balancing-763"
                },
                {
                  "text": "Auto Scaling",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--auto-scaling-768"
                },
                {
                  "text": "Sharding Strategies",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--sharding-strategies-769"
                },
                {
                  "text": "Partitioning",
                  "ordered": false,
                  "children": [],
                  "id": "105-scalability-patterns--partitioning-770"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "106-distributed-systems-concepts",
          "title": "10.6 Distributed Systems Concepts",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Distributed Systems Basics",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--distributed-systems-basics-771"
                },
                {
                  "text": "Consistency Models",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Strong Consistency",
                      "ordered": false,
                      "children": [],
                      "id": "106-distributed-systems-concepts--strong-consistency-773"
                    },
                    {
                      "text": "Eventual Consistency",
                      "ordered": false,
                      "children": [],
                      "id": "106-distributed-systems-concepts--eventual-consistency-774"
                    },
                    {
                      "text": "Causal Consistency",
                      "ordered": false,
                      "children": [],
                      "id": "106-distributed-systems-concepts--causal-consistency-775"
                    }
                  ],
                  "id": "106-distributed-systems-concepts--consistency-models-772"
                },
                {
                  "text": "Leader Election",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--leader-election-776"
                },
                {
                  "text": "Consensus Algorithms",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Paxos",
                      "ordered": false,
                      "children": [],
                      "id": "106-distributed-systems-concepts--paxos-778"
                    },
                    {
                      "text": "Raft",
                      "ordered": false,
                      "children": [],
                      "id": "106-distributed-systems-concepts--raft-779"
                    }
                  ],
                  "id": "106-distributed-systems-concepts--consensus-algorithms-777"
                },
                {
                  "text": "Clock Synchronization",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--clock-synchronization-780"
                },
                {
                  "text": "Logical Clocks",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--logical-clocks-781"
                },
                {
                  "text": "Vector Clocks",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--vector-clocks-782"
                },
                {
                  "text": "Distributed Locks",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--distributed-locks-783"
                },
                {
                  "text": "Idempotency",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--idempotency-784"
                },
                {
                  "text": "Split Brain",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--split-brain-785"
                },
                {
                  "text": "Quorum",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--quorum-786"
                },
                {
                  "text": "Failure Detection",
                  "ordered": false,
                  "children": [],
                  "id": "106-distributed-systems-concepts--failure-detection-787"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "107-messaging-and-async-processing",
          "title": "10.7 Messaging & Async Processing",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Message Queues",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--message-queues-788"
                },
                {
                  "text": "Kafka",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--kafka-789"
                },
                {
                  "text": "RabbitMQ",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--rabbitmq-790"
                },
                {
                  "text": "SQS",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--sqs-791"
                },
                {
                  "text": "Pub/Sub",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--pub-sub-792"
                },
                {
                  "text": "Event-Driven Architecture",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--event-driven-architecture-793"
                },
                {
                  "text": "At-most-once Delivery",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--at-most-once-delivery-794"
                },
                {
                  "text": "At-least-once Delivery",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--at-least-once-delivery-795"
                },
                {
                  "text": "Exactly-once Semantics",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--exactly-once-semantics-796"
                },
                {
                  "text": "Dead Letter Queues",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--dead-letter-queues-797"
                },
                {
                  "text": "Backpressure",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--backpressure-798"
                },
                {
                  "text": "Message Ordering",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--message-ordering-799"
                },
                {
                  "text": "Consumer Groups",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--consumer-groups-800"
                },
                {
                  "text": "Transactional Outbox / Inbox",
                  "ordered": false,
                  "children": [],
                  "id": "107-messaging-and-async-processing--transactional-outbox-inbox-801"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "108-microservices-architecture",
          "title": "10.8 Microservices Architecture",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Monolith vs Microservices",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--monolith-vs-microservices-802"
                },
                {
                  "text": "Modular Monolith",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--modular-monolith-803"
                },
                {
                  "text": "Service Discovery",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--service-discovery-804"
                },
                {
                  "text": "Inter-Service Communication",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--inter-service-communication-805"
                },
                {
                  "text": "API Gateway",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--api-gateway-806"
                },
                {
                  "text": "Backend for Frontend (BFF)",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--backend-for-frontend-bff-807"
                },
                {
                  "text": "Circuit Breaker",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--circuit-breaker-808"
                },
                {
                  "text": "Retry & Timeout",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--retry-and-timeout-809"
                },
                {
                  "text": "Bulkhead",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--bulkhead-810"
                },
                {
                  "text": "Saga Pattern",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--saga-pattern-811"
                },
                {
                  "text": "Choreography vs Orchestration",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--choreography-vs-orchestration-812"
                },
                {
                  "text": "Data per Service",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--data-per-service-813"
                },
                {
                  "text": "Database per Service",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--database-per-service-814"
                },
                {
                  "text": "Microservices Anti-Patterns",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--microservices-anti-patterns-815"
                },
                {
                  "text": "Strangler Fig Pattern",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--strangler-fig-pattern-816"
                },
                {
                  "text": "Service Mesh",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--service-mesh-817"
                },
                {
                  "text": "Anti-Corruption Layer",
                  "ordered": false,
                  "children": [],
                  "id": "108-microservices-architecture--anti-corruption-layer-818"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "109-security",
          "title": "10.9 Security",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Authentication",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--authentication-819"
                },
                {
                  "text": "Authorization",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--authorization-820"
                },
                {
                  "text": "OAuth 2.0",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--oauth-20-821"
                },
                {
                  "text": "OpenID Connect (OIDC)",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--openid-connect-oidc-822"
                },
                {
                  "text": "JWT",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--jwt-823"
                },
                {
                  "text": "SSO",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--sso-824"
                },
                {
                  "text": "HTTPS / TLS",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--https-tls-825"
                },
                {
                  "text": "Encryption at Rest / In Transit",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--encryption-at-rest-in-transit-826"
                },
                {
                  "text": "Rate Limiting",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--rate-limiting-827"
                },
                {
                  "text": "DDoS Protection",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--ddos-protection-828"
                },
                {
                  "text": "Secrets Management",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--secrets-management-829"
                },
                {
                  "text": "RBAC",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--rbac-830"
                },
                {
                  "text": "ABAC",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--abac-831"
                },
                {
                  "text": "Least Privilege",
                  "ordered": false,
                  "children": [],
                  "id": "109-security--least-privilege-832"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "1010-high-availability-and-reliability",
          "title": "10.10 High Availability & Reliability",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Single Point of Failure",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--single-point-of-failure-833"
                },
                {
                  "text": "Replication",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--replication-834"
                },
                {
                  "text": "Failover",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--failover-835"
                },
                {
                  "text": "Health Checks",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--health-checks-836"
                },
                {
                  "text": "Heartbeats",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--heartbeats-837"
                },
                {
                  "text": "Graceful Degradation",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--graceful-degradation-838"
                },
                {
                  "text": "Disaster Recovery",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--disaster-recovery-839"
                },
                {
                  "text": "Backup Strategies",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--backup-strategies-840"
                },
                {
                  "text": "RTO / RPO",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--rto-rpo-841"
                },
                {
                  "text": "Fault Tolerance",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--fault-tolerance-842"
                },
                {
                  "text": "Redundancy",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--redundancy-843"
                },
                {
                  "text": "Retry and Timeout",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--retry-and-timeout-844"
                },
                {
                  "text": "Failure Isolation",
                  "ordered": false,
                  "children": [],
                  "id": "1010-high-availability-and-reliability--failure-isolation-845"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "1011-observability-and-monitoring",
          "title": "10.11 Observability & Monitoring",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Logging",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--logging-846"
                },
                {
                  "text": "Metrics",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--metrics-847"
                },
                {
                  "text": "Monitoring",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--monitoring-848"
                },
                {
                  "text": "Distributed Tracing",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--distributed-tracing-849"
                },
                {
                  "text": "Alerting",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--alerting-850"
                },
                {
                  "text": "SLIs / SLOs / SLAs",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--slis-slos-slas-851"
                },
                {
                  "text": "Prometheus",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--prometheus-852"
                },
                {
                  "text": "Grafana",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--grafana-853"
                },
                {
                  "text": "ELK Stack",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--elk-stack-854"
                },
                {
                  "text": "OpenTelemetry",
                  "ordered": false,
                  "children": [],
                  "id": "1011-observability-and-monitoring--opentelemetry-855"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "1012-design-patterns-system-level",
          "title": "10.12 Design Patterns (System Level)",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Singleton",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--singleton-856"
                },
                {
                  "text": "Factory",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--factory-857"
                },
                {
                  "text": "Observer",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--observer-858"
                },
                {
                  "text": "CQRS",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--cqrs-859"
                },
                {
                  "text": "Event Sourcing",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--event-sourcing-860"
                },
                {
                  "text": "Bulkhead",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--bulkhead-861"
                },
                {
                  "text": "Sidecar",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--sidecar-862"
                },
                {
                  "text": "Ambassador",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--ambassador-863"
                },
                {
                  "text": "Strangler Fig Pattern",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--strangler-fig-pattern-864"
                },
                {
                  "text": "API Composition",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--api-composition-865"
                },
                {
                  "text": "Cell-Based Architecture",
                  "ordered": false,
                  "children": [],
                  "id": "1012-design-patterns-system-level--cell-based-architecture-866"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "1013-data-processing",
          "title": "10.13 Data Processing",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Batch Processing",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--batch-processing-867"
                },
                {
                  "text": "Stream Processing",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--stream-processing-868"
                },
                {
                  "text": "ETL",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--etl-869"
                },
                {
                  "text": "ELT",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--elt-870"
                },
                {
                  "text": "MapReduce",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--mapreduce-871"
                },
                {
                  "text": "Spark",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--spark-872"
                },
                {
                  "text": "Flink",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--flink-873"
                },
                {
                  "text": "Data Pipelines",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--data-pipelines-874"
                },
                {
                  "text": "Data Warehouse",
                  "ordered": false,
                  "children": [],
                  "id": "1013-data-processing--data-warehouse-875"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "1014-cloud-and-infrastructure",
          "title": "10.14 Cloud & Infrastructure",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "IaaS / PaaS / SaaS",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--iaas-paas-saas-876"
                },
                {
                  "text": "AWS / GCP / Azure Concepts",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--aws-gcp-azure-concepts-877"
                },
                {
                  "text": "Containers (Docker)",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--containers-docker-878"
                },
                {
                  "text": "Kubernetes",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--kubernetes-879"
                },
                {
                  "text": "CI / CD",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--ci-cd-880"
                },
                {
                  "text": "Infrastructure as Code",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--infrastructure-as-code-881"
                },
                {
                  "text": "Terraform",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--terraform-882"
                },
                {
                  "text": "Service Mesh",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--service-mesh-883"
                },
                {
                  "text": "Container Orchestration",
                  "ordered": false,
                  "children": [],
                  "id": "1014-cloud-and-infrastructure--container-orchestration-884"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "1015-common-system-design-interview-problems",
          "title": "10.15 Common System Design Interview Problems",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Design URL Shortener",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-url-shortener-885"
                },
                {
                  "text": "Design WhatsApp",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-whatsapp-886"
                },
                {
                  "text": "Design Twitter",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-twitter-887"
                },
                {
                  "text": "Design Instagram",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-instagram-888"
                },
                {
                  "text": "Design YouTube",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-youtube-889"
                },
                {
                  "text": "Design Netflix",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-netflix-890"
                },
                {
                  "text": "Design Uber",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-uber-891"
                },
                {
                  "text": "Design Payment System",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-payment-system-892"
                },
                {
                  "text": "Design Notification System",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-notification-system-893"
                },
                {
                  "text": "Design Search Engine",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-search-engine-894"
                },
                {
                  "text": "Design File Storage (Google Drive)",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-file-storage-google-drive-895"
                },
                {
                  "text": "Design E-commerce System",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-e-commerce-system-896"
                },
                {
                  "text": "Design Ticket Booking System",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-ticket-booking-system-897"
                },
                {
                  "text": "Design Rate Limiter",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-rate-limiter-898"
                },
                {
                  "text": "Design Distributed Job Scheduler",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-distributed-job-scheduler-899"
                },
                {
                  "text": "Design Logging System",
                  "ordered": false,
                  "children": [],
                  "id": "1015-common-system-design-interview-problems--design-logging-system-900"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "supporting-foundations",
      "title": "Supporting Foundations",
      "level": 1,
      "blocks": [
        {
          "type": "paragraph",
          "text": "These topics support multiple roadmap pillars. They are not replacements for the ten main sections."
        }
      ],
      "children": [
        {
          "id": "a-software-engineering-practices",
          "title": "A. Software Engineering Practices",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Clean Code",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--clean-code-901"
                },
                {
                  "text": "Refactoring",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--refactoring-902"
                },
                {
                  "text": "Code Smells",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--code-smells-903"
                },
                {
                  "text": "Technical Debt",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--technical-debt-904"
                },
                {
                  "text": "Defensive Programming",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--defensive-programming-905"
                },
                {
                  "text": "Error Handling",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--error-handling-906"
                },
                {
                  "text": "Logging",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--logging-907"
                },
                {
                  "text": "Unit Testing",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--unit-testing-908"
                },
                {
                  "text": "Integration Testing",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--integration-testing-909"
                },
                {
                  "text": "End-to-End Testing",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--end-to-end-testing-910"
                },
                {
                  "text": "Test-Driven Development (TDD)",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--test-driven-development-tdd-911"
                },
                {
                  "text": "Behavior-Driven Development (BDD)",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--behavior-driven-development-bdd-912"
                },
                {
                  "text": "Test Doubles",
                  "ordered": false,
                  "children": [
                    {
                      "text": "Mocks",
                      "ordered": false,
                      "children": [],
                      "id": "a-software-engineering-practices--mocks-914"
                    },
                    {
                      "text": "Stubs",
                      "ordered": false,
                      "children": [],
                      "id": "a-software-engineering-practices--stubs-915"
                    },
                    {
                      "text": "Fakes",
                      "ordered": false,
                      "children": [],
                      "id": "a-software-engineering-practices--fakes-916"
                    }
                  ],
                  "id": "a-software-engineering-practices--test-doubles-913"
                },
                {
                  "text": "Code Review",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--code-review-917"
                },
                {
                  "text": "Version Control (Git)",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--version-control-git-918"
                },
                {
                  "text": "CI / CD",
                  "ordered": false,
                  "children": [],
                  "id": "a-software-engineering-practices--ci-cd-919"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "b-operating-systems-fundamentals",
          "title": "B. Operating Systems Fundamentals",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "Process vs Thread",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--process-vs-thread-920"
                },
                {
                  "text": "Process Scheduling",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--process-scheduling-921"
                },
                {
                  "text": "Context Switching",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--context-switching-922"
                },
                {
                  "text": "User Mode vs Kernel Mode",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--user-mode-vs-kernel-mode-923"
                },
                {
                  "text": "Memory Management",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--memory-management-924"
                },
                {
                  "text": "Virtual Memory",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--virtual-memory-925"
                },
                {
                  "text": "Stack vs Heap",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--stack-vs-heap-926"
                },
                {
                  "text": "Mutex / Semaphore",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--mutex-semaphore-927"
                },
                {
                  "text": "Inter-Process Communication (IPC)",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--inter-process-communication-ipc-928"
                },
                {
                  "text": "CPU-bound vs I/O-bound",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--cpu-bound-vs-i-o-bound-929"
                },
                {
                  "text": "Deadlocks",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--deadlocks-930"
                },
                {
                  "text": "Race Conditions",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--race-conditions-931"
                },
                {
                  "text": "File Descriptors",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--file-descriptors-932"
                },
                {
                  "text": "System Calls",
                  "ordered": false,
                  "children": [],
                  "id": "b-operating-systems-fundamentals--system-calls-933"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "c-computer-networking-fundamentals",
          "title": "C. Computer Networking Fundamentals",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "OSI Model",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--osi-model-934"
                },
                {
                  "text": "TCP/IP Model",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--tcp-ip-model-935"
                },
                {
                  "text": "IP Addressing",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--ip-addressing-936"
                },
                {
                  "text": "Subnetting",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--subnetting-937"
                },
                {
                  "text": "TCP Handshake",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--tcp-handshake-938"
                },
                {
                  "text": "Connection Lifecycle",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--connection-lifecycle-939"
                },
                {
                  "text": "DNS",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--dns-940"
                },
                {
                  "text": "TLS",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--tls-941"
                },
                {
                  "text": "HTTP Internals",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--http-internals-942"
                },
                {
                  "text": "Keep-Alive",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--keep-alive-943"
                },
                {
                  "text": "Connection Pooling",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--connection-pooling-944"
                },
                {
                  "text": "Socket Programming",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--socket-programming-945"
                },
                {
                  "text": "Routing Basics",
                  "ordered": false,
                  "children": [],
                  "id": "c-computer-networking-fundamentals--routing-basics-946"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "cross-topic-relationships-and-study-notes",
      "title": "Cross-Topic Relationships & Study Notes",
      "level": 1,
      "blocks": [],
      "children": [
        {
          "id": "ood-vs-poeaa-vs-ddd",
          "title": "OOD vs PoEAA vs DDD",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "**OOD** focuses on designing objects, responsibilities, relationships, and reusable design.",
                  "ordered": false,
                  "children": [],
                  "id": "ood-vs-poeaa-vs-ddd--ood-focuses-on-designing-objects-responsibilities-rela-947"
                },
                {
                  "text": "**PoEAA** provides patterns for implementing enterprise application logic, persistence, presentation, distribution, and concurrency.",
                  "ordered": false,
                  "children": [],
                  "id": "ood-vs-poeaa-vs-ddd--poeaa-provides-patterns-for-implementing-enterprise-appl-948"
                },
                {
                  "text": "**DDD** focuses on understanding and modeling complex business domains and defining meaningful domain boundaries.",
                  "ordered": false,
                  "children": [],
                  "id": "ood-vs-poeaa-vs-ddd--ddd-focuses-on-understanding-and-modeling-complex-busine-949"
                },
                {
                  "text": "These areas complement one another; none is a direct replacement for the others.",
                  "ordered": false,
                  "children": [],
                  "id": "ood-vs-poeaa-vs-ddd--these-areas-complement-one-another-none-is-a-direct-replace-950"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "application-architecture-vs-presentation-architecture",
          "title": "Application Architecture vs Presentation Architecture",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "**Application Architecture** organizes the application as a whole: modules, layers, dependencies, boundaries, and infrastructure.",
                  "ordered": false,
                  "children": [],
                  "id": "application-architecture-vs-presentation-architecture--application-architecture-organizes-the-application-as-a-951"
                },
                {
                  "text": "**Presentation Architecture** organizes the UI layer: views, presenters, view models, state, rendering, and user interaction.",
                  "ordered": false,
                  "children": [],
                  "id": "application-architecture-vs-presentation-architecture--presentation-architecture-organizes-the-ui-layer-views-952"
                },
                {
                  "text": "MVC can appear in both discussions because it can be studied at different levels and for different concerns.",
                  "ordered": false,
                  "children": [],
                  "id": "application-architecture-vs-presentation-architecture--mvc-can-appear-in-both-discussions-because-it-can-be-studied-953"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "concurrency-vs-eip",
          "title": "Concurrency vs EIP",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "**Concurrency** concerns coordinating tasks and accessing shared resources safely, within a process or across distributed nodes.",
                  "ordered": false,
                  "children": [],
                  "id": "concurrency-vs-eip--concurrency-concerns-coordinating-tasks-and-accessing-sh-954"
                },
                {
                  "text": "**EIP** concerns communication and integration between independent applications or services through messages.",
                  "ordered": false,
                  "children": [],
                  "id": "concurrency-vs-eip--eip-concerns-communication-and-integration-between-indep-955"
                },
                {
                  "text": "Related ideas can appear in both areas, but the concepts are not interchangeable.",
                  "ordered": false,
                  "children": [],
                  "id": "concurrency-vs-eip--related-ideas-can-appear-in-both-areas-but-the-concepts-are-956"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "eip-vs-system-design",
          "title": "EIP vs System Design",
          "level": 2,
          "blocks": [
            {
              "type": "list",
              "items": [
                {
                  "text": "**EIP** focuses on message-based integration patterns and the mechanics of routing, transforming, constructing, and consuming messages.",
                  "ordered": false,
                  "children": [],
                  "id": "eip-vs-system-design--eip-focuses-on-message-based-integration-patterns-and-th-957"
                },
                {
                  "text": "**System Design** uses messaging and integration as part of a larger system, alongside storage, networking, scaling, reliability, security, and operations.",
                  "ordered": false,
                  "children": [],
                  "id": "eip-vs-system-design--system-design-uses-messaging-and-integration-as-part-of-958"
                }
              ]
            }
          ],
          "children": []
        },
        {
          "id": "suggested-practical-project",
          "title": "Suggested Practical Project",
          "level": 2,
          "blocks": [
            {
              "type": "paragraph",
              "text": "Use one evolving E-commerce / Order Management System to connect the roadmap:"
            },
            {
              "type": "list",
              "items": [
                {
                  "text": "DSA: search, filtering, and data-processing problems.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--dsa-search-filtering-and-data-processing-problems-959"
                },
                {
                  "text": "OOD: Product, Order, Payment, Inventory objects and responsibilities.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--ood-product-order-payment-inventory-objects-and-responsi-960"
                },
                {
                  "text": "DBMS: schema, transactions, indexes, and concurrency.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--dbms-schema-transactions-indexes-and-concurrency-961"
                },
                {
                  "text": "Application Architecture: modules, layers, boundaries, and dependencies.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--application-architecture-modules-layers-boundaries-and-d-962"
                },
                {
                  "text": "Presentation Architecture: UI state and presentation flow.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--presentation-architecture-ui-state-and-presentation-flow-963"
                },
                {
                  "text": "PoEAA: Repository, Unit of Work, Service Layer, Data Mapper.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--poeaa-repository-unit-of-work-service-layer-data-mapper-964"
                },
                {
                  "text": "DDD: Order Aggregate, bounded contexts, domain events.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--ddd-order-aggregate-bounded-contexts-domain-events-965"
                },
                {
                  "text": "Concurrency: inventory race conditions and safe task execution.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--concurrency-inventory-race-conditions-and-safe-task-executi-966"
                },
                {
                  "text": "EIP: Order, Payment, and Inventory message flows.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--eip-order-payment-and-inventory-message-flows-967"
                },
                {
                  "text": "System Design: scaling, availability, observability, and distributed deployment.",
                  "ordered": false,
                  "children": [],
                  "id": "suggested-practical-project--system-design-scaling-availability-observability-and-dis-968"
                }
              ]
            }
          ],
          "children": []
        }
      ]
    },
    {
      "id": "recommended-study-strategy",
      "title": "Recommended Study Strategy",
      "level": 1,
      "blocks": [
        {
          "type": "paragraph",
          "text": "For every topic or pattern, document:"
        },
        {
          "type": "list",
          "items": [
            {
              "text": "**What is it?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--what-is-it-969"
            },
            {
              "text": "**What problem does it solve?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--what-problem-does-it-solve-970"
            },
            {
              "text": "**Why does that problem happen?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--why-does-that-problem-happen-971"
            },
            {
              "text": "**How does the solution work?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--how-does-the-solution-work-972"
            },
            {
              "text": "**When should it be used?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--when-should-it-be-used-973"
            },
            {
              "text": "**When should it not be used?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--when-should-it-not-be-used-974"
            },
            {
              "text": "**What are its trade-offs?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--what-are-its-trade-offs-975"
            },
            {
              "text": "**What is it similar to, and how is it different?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--what-is-it-similar-to-and-how-is-it-different-976"
            },
            {
              "text": "**How can it be implemented in Python?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--how-can-it-be-implemented-in-python-977"
            },
            {
              "text": "**Where can it appear in a real backend system?**",
              "ordered": true,
              "children": [],
              "id": "recommended-study-strategy--where-can-it-appear-in-a-real-backend-system-978"
            }
          ]
        },
        {
          "type": "blockquote",
          "text": "Keep the original topic tracker and problem lists as the source of study progress. Add practical implementation and trade-off analysis as a second layer, rather than turning the roadmap into a list of definitions to memorize."
        }
      ],
      "children": []
    }
  ],
  "concepts": [
    {
      "id": "phase-1-engineering-foundations--problem-solving-and-data-structures-and-algorithms-dsa-1",
      "title": "Problem Solving & Data Structures & Algorithms (DSA)",
      "path": [
        "Roadmap Overview",
        "Phase 1 — Engineering Foundations"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-1-engineering-foundations--dbms-and-data-management-2",
      "title": "DBMS & Data Management",
      "path": [
        "Roadmap Overview",
        "Phase 1 — Engineering Foundations"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-1-engineering-foundations--object-oriented-design-ood-3",
      "title": "Object-Oriented Design (OOD)",
      "path": [
        "Roadmap Overview",
        "Phase 1 — Engineering Foundations"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-2-software-design-and-architecture--application-architecture-4",
      "title": "Application Architecture",
      "path": [
        "Roadmap Overview",
        "Phase 2 — Software Design & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-2-software-design-and-architecture--presentation-architecture-5",
      "title": "Presentation Architecture",
      "path": [
        "Roadmap Overview",
        "Phase 2 — Software Design & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-2-software-design-and-architecture--patterns-of-enterprise-application-architecture-poeaa-6",
      "title": "Patterns of Enterprise Application Architecture (PoEAA)",
      "path": [
        "Roadmap Overview",
        "Phase 2 — Software Design & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-2-software-design-and-architecture--domain-driven-design-ddd-7",
      "title": "Domain-Driven Design (DDD)",
      "path": [
        "Roadmap Overview",
        "Phase 2 — Software Design & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-3-concurrency-and-integration--concurrency-patterns-8",
      "title": "Concurrency Patterns",
      "path": [
        "Roadmap Overview",
        "Phase 3 — Concurrency & Integration"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-3-concurrency-and-integration--enterprise-integration-patterns-eip-9",
      "title": "Enterprise Integration Patterns (EIP)",
      "path": [
        "Roadmap Overview",
        "Phase 3 — Concurrency & Integration"
      ],
      "hasChildren": false
    },
    {
      "id": "phase-4-distributed-systems-and-system-architecture--system-design-10",
      "title": "System Design",
      "path": [
        "Roadmap Overview",
        "Phase 4 — Distributed Systems & System Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "supporting-foundations-study-alongside-the-roadmap--software-engineering-practices-11",
      "title": "Software Engineering Practices",
      "path": [
        "Roadmap Overview",
        "Supporting Foundations (study alongside the roadmap)"
      ],
      "hasChildren": false
    },
    {
      "id": "supporting-foundations-study-alongside-the-roadmap--operating-systems-fundamentals-12",
      "title": "Operating Systems Fundamentals",
      "path": [
        "Roadmap Overview",
        "Supporting Foundations (study alongside the roadmap)"
      ],
      "hasChildren": false
    },
    {
      "id": "supporting-foundations-study-alongside-the-roadmap--computer-networking-fundamentals-13",
      "title": "Computer Networking Fundamentals",
      "path": [
        "Roadmap Overview",
        "Supporting Foundations (study alongside the roadmap)"
      ],
      "hasChildren": false
    },
    {
      "id": "11-complexity-analysis--time-complexity-and-space-complexity-14",
      "title": "Time Complexity & Space Complexity",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.1 Complexity Analysis"
      ],
      "hasChildren": true
    },
    {
      "id": "11-complexity-analysis--big-o-big-omega-big-theta-15",
      "title": "Big O, Big Omega, Big Theta",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.1 Complexity Analysis",
        "Time Complexity & Space Complexity"
      ],
      "hasChildren": false
    },
    {
      "id": "11-complexity-analysis--amortized-analysis-16",
      "title": "Amortized Analysis",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.1 Complexity Analysis"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--arrays-and-strings-17",
      "title": "Arrays & Strings",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures"
      ],
      "hasChildren": true
    },
    {
      "id": "12-fundamental-data-structures--prefix-sums-18",
      "title": "Prefix Sums",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Arrays & Strings"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--matrix-manipulation-19",
      "title": "Matrix Manipulation",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Arrays & Strings"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--linked-lists-20",
      "title": "Linked Lists",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures"
      ],
      "hasChildren": true
    },
    {
      "id": "12-fundamental-data-structures--singly-linked-lists-21",
      "title": "Singly Linked Lists",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Linked Lists"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--doubly-linked-lists-22",
      "title": "Doubly Linked Lists",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Linked Lists"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--circular-linked-lists-23",
      "title": "Circular Linked Lists",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Linked Lists"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--stacks-and-queues-24",
      "title": "Stacks & Queues",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures"
      ],
      "hasChildren": true
    },
    {
      "id": "12-fundamental-data-structures--monotonic-stack-25",
      "title": "Monotonic Stack",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Stacks & Queues"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--monotonic-queue-26",
      "title": "Monotonic Queue",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures",
        "Stacks & Queues"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--hash-tables-hash-maps-hash-sets-27",
      "title": "Hash Tables / Hash Maps / Hash Sets",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures"
      ],
      "hasChildren": false
    },
    {
      "id": "12-fundamental-data-structures--heaps-priority-queues-28",
      "title": "Heaps / Priority Queues",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.2 Fundamental Data Structures"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--trees-29",
      "title": "Trees",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures"
      ],
      "hasChildren": true
    },
    {
      "id": "13-advanced-data-structures--binary-trees-30",
      "title": "Binary Trees",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Trees"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--binary-search-trees-31",
      "title": "Binary Search Trees",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Trees"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--avl-self-balancing-trees-32",
      "title": "AVL / Self-Balancing Trees",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Trees"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--tries-33",
      "title": "Tries",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Trees"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--graphs-34",
      "title": "Graphs",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures"
      ],
      "hasChildren": true
    },
    {
      "id": "13-advanced-data-structures--adjacency-matrix-adjacency-list-35",
      "title": "Adjacency Matrix / Adjacency List",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Graphs"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--directed-undirected-36",
      "title": "Directed / Undirected",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Graphs"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--weighted-unweighted-37",
      "title": "Weighted / Unweighted",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures",
        "Graphs"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--disjoint-set-union-union-find-dsu-38",
      "title": "Disjoint Set Union (Union-Find / DSU)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--segment-trees-39",
      "title": "Segment Trees",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures"
      ],
      "hasChildren": false
    },
    {
      "id": "13-advanced-data-structures--fenwick-trees-binary-indexed-tree-40",
      "title": "Fenwick Trees (Binary Indexed Tree)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.3 Advanced Data Structures"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--two-pointers-41",
      "title": "Two Pointers",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--sliding-window-42",
      "title": "Sliding Window",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--fast-and-slow-pointers-tortoise-and-hare-43",
      "title": "Fast & Slow Pointers (Tortoise & Hare)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--prefix-sum-44",
      "title": "Prefix Sum",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--merge-intervals-45",
      "title": "Merge Intervals",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--cyclic-sort-46",
      "title": "Cyclic Sort",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--in-place-reversal-of-a-linked-list-47",
      "title": "In-place Reversal of a Linked List",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--binary-search-and-modified-binary-search-48",
      "title": "Binary Search & Modified Binary Search",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--tree-breadth-first-search-bfs-and-depth-first-search-dfs-49",
      "title": "Tree Breadth-First Search (BFS) & Depth-First Search (DFS)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--graph-traversal-50",
      "title": "Graph Traversal",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--shortest-path-51",
      "title": "Shortest Path",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": true
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--dijkstra-52",
      "title": "Dijkstra",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Shortest Path"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--bellman-ford-53",
      "title": "Bellman-Ford",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Shortest Path"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--floyd-warshall-54",
      "title": "Floyd-Warshall",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Shortest Path"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--topological-sort-55",
      "title": "Topological Sort",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": true
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--kahns-algorithm-56",
      "title": "Kahn's Algorithm",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Topological Sort"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--dfs-based-57",
      "title": "DFS-based",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Topological Sort"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--backtracking-and-recursion-58",
      "title": "Backtracking & Recursion",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--dynamic-programming-59",
      "title": "Dynamic Programming",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": true
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--memoization-60",
      "title": "Memoization",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Dynamic Programming"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--tabulation-61",
      "title": "Tabulation",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Dynamic Programming"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--1d-2d-dp-62",
      "title": "1D / 2D DP",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Dynamic Programming"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--knapsack-63",
      "title": "Knapsack",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Dynamic Programming"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--lcs-64",
      "title": "LCS",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Dynamic Programming"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--lis-65",
      "title": "LIS",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques",
        "Dynamic Programming"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--greedy-algorithms-66",
      "title": "Greedy Algorithms",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--divide-and-conquer-67",
      "title": "Divide and Conquer",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--bit-manipulation-68",
      "title": "Bit Manipulation",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "14-core-problem-solving-patterns-and-techniques--mathematical-algorithms-69",
      "title": "Mathematical Algorithms",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.4 Core Problem-Solving Patterns & Techniques"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--509-fibonacci-number-easy-70",
      "title": "509 — Fibonacci Number (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--344-reverse-string-easy-71",
      "title": "344 — Reverse String (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--21-merge-two-sorted-lists-easy-72",
      "title": "21 — Merge Two Sorted Lists (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--50-powx-n-medium-73",
      "title": "50 — Pow(x, n) (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--118-pascals-triangle-easy-74",
      "title": "118 — Pascal's Triangle (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--24-swap-nodes-in-pairs-medium-75",
      "title": "24 — Swap Nodes in Pairs (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--779-k-th-symbol-in-grammar-medium-76",
      "title": "779 — K-th Symbol in Grammar (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--2-add-two-numbers-medium-77",
      "title": "2 — Add Two Numbers (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--95-unique-binary-search-trees-ii-medium-78",
      "title": "95 — Unique Binary Search Trees II (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-common-problems--394-decode-string-medium-79",
      "title": "394 — Decode String (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--206-reverse-linked-list-easy-recursive-reversal-of-a-li-80",
      "title": "206 — Reverse Linked List (Easy): Recursive reversal of a linked list",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--203-remove-linked-list-elements-easy-recursive-removal-81",
      "title": "203 — Remove Linked List Elements (Easy): Recursive removal with a base case",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--231-power-of-two-easy-recursive-halving-until-the-base-82",
      "title": "231 — Power of Two (Easy): Recursive halving until the base",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--326-power-of-three-easy-recursive-division-and-base-cas-83",
      "title": "326 — Power of Three (Easy): Recursive division and base cases",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--342-power-of-four-easy-recursive-division-by-four-84",
      "title": "342 — Power of Four (Easy): Recursive division by four",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--234-palindrome-linked-list-easy-recursion-to-the-end-t-85",
      "title": "234 — Palindrome Linked List (Easy): Recursion to the end, then compare",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--3304-find-the-k-th-character-in-string-game-i-easy-recu-86",
      "title": "3304 — Find the K-th Character in String Game I (Easy): Recursive string growth",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--390-elimination-game-medium-a-recurrence-that-shrinks-t-87",
      "title": "390 — Elimination Game (Medium): A recurrence that shrinks the problem",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--1545-find-kth-bit-in-nth-binary-string-medium-a-string-88",
      "title": "1545 — Find Kth Bit in Nth Binary String (Medium): A string defined by recursion",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "a-recursion-العودية-training-path--1823-find-the-winner-of-the-circular-game-medium-joseph-89",
      "title": "1823 — Find the Winner of the Circular Game (Medium): Josephus recurrence",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "A. Recursion (العودية)",
        "Training Path"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--104-maximum-depth-of-binary-tree-easy-90",
      "title": "104 — Maximum Depth of Binary Tree (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--226-invert-binary-tree-easy-91",
      "title": "226 — Invert Binary Tree (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--100-same-tree-easy-92",
      "title": "100 — Same Tree (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--102-binary-tree-level-order-traversal-medium-93",
      "title": "102 — Binary Tree Level Order Traversal (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--98-validate-binary-search-tree-medium-94",
      "title": "98 — Validate Binary Search Tree (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--236-lowest-common-ancestor-of-a-binary-tree-medium-95",
      "title": "236 — Lowest Common Ancestor of a Binary Tree (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--572-subtree-of-another-tree-easy-96",
      "title": "572 — Subtree of Another Tree (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--543-diameter-of-binary-tree-easy-97",
      "title": "543 — Diameter of Binary Tree (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--124-binary-tree-maximum-path-sum-hard-98",
      "title": "124 — Binary Tree Maximum Path Sum (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "b-trees-الأشجار-common-problems--105-construct-binary-tree-from-preorder-and-inorder-traver-99",
      "title": "105 — Construct Binary Tree from Preorder and Inorder Traversal (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "B. Trees (الأشجار)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--78-subsets-medium-100",
      "title": "78 — Subsets (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--90-subsets-ii-medium-101",
      "title": "90 — Subsets II (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--46-permutations-medium-102",
      "title": "46 — Permutations (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--47-permutations-ii-medium-103",
      "title": "47 — Permutations II (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--39-combination-sum-medium-104",
      "title": "39 — Combination Sum (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--40-combination-sum-ii-medium-105",
      "title": "40 — Combination Sum II (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--131-palindrome-partitioning-medium-106",
      "title": "131 — Palindrome Partitioning (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--51-n-queens-hard-107",
      "title": "51 — N-Queens (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--79-word-search-medium-108",
      "title": "79 — Word Search (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-core-problems--37-sudoku-solver-hard-109",
      "title": "37 — Sudoku Solver (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Core Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--17-letter-combinations-of-a-phone-number-medium-110",
      "title": "17 — Letter Combinations of a Phone Number (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--216-combination-sum-iii-medium-111",
      "title": "216 — Combination Sum III (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--93-restore-ip-addresses-medium-112",
      "title": "93 — Restore IP Addresses (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--698-partition-to-k-equal-sum-subsets-medium-113",
      "title": "698 — Partition to K Equal Sum Subsets (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--212-word-search-ii-hard-114",
      "title": "212 — Word Search II (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--473-matchsticks-to-square-medium-115",
      "title": "473 — Matchsticks to Square (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--52-n-queens-ii-hard-116",
      "title": "52 — N-Queens II (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--491-non-decreasing-subsequences-medium-117",
      "title": "491 — Non-decreasing Subsequences (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--526-beautiful-arrangement-medium-118",
      "title": "526 — Beautiful Arrangement (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "c-backtracking-التراجع-additional-problems--1849-splitting-a-string-into-descending-consecutive-values-119",
      "title": "1849 — Splitting a String Into Descending Consecutive Values (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "C. Backtracking (التراجع)",
        "Additional Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--70-climbing-stairs-easy-120",
      "title": "70 — Climbing Stairs (Easy)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--198-house-robber-medium-121",
      "title": "198 — House Robber (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--213-house-robber-ii-medium-122",
      "title": "213 — House Robber II (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--5-longest-palindromic-substring-medium-123",
      "title": "5 — Longest Palindromic Substring (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--322-coin-change-medium-124",
      "title": "322 — Coin Change (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--300-longest-increasing-subsequence-medium-125",
      "title": "300 — Longest Increasing Subsequence (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--416-partition-equal-subset-sum-medium-126",
      "title": "416 — Partition Equal Subset Sum (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--62-unique-paths-medium-127",
      "title": "62 — Unique Paths (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--72-edit-distance-hard-128",
      "title": "72 — Edit Distance (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "d-dynamic-programming-البرمجة-الديناميكية-common-problems--1143-longest-common-subsequence-medium-129",
      "title": "1143 — Longest Common Subsequence (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "D. Dynamic Programming (البرمجة الديناميكية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--200-number-of-islands-medium-130",
      "title": "200 — Number of Islands (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--133-clone-graph-medium-131",
      "title": "133 — Clone Graph (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--695-max-area-of-island-medium-132",
      "title": "695 — Max Area of Island (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--207-course-schedule-medium-133",
      "title": "207 — Course Schedule (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--417-pacific-atlantic-water-flow-medium-134",
      "title": "417 — Pacific Atlantic Water Flow (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--994-rotting-oranges-medium-135",
      "title": "994 — Rotting Oranges (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--261-graph-valid-tree-medium-premium-136",
      "title": "261 — Graph Valid Tree (Medium, Premium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--127-word-ladder-hard-137",
      "title": "127 — Word Ladder (Hard)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--743-network-delay-time-medium-138",
      "title": "743 — Network Delay Time (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "e-graphs-الرسوم-البيانية-common-problems--787-cheapest-flights-within-k-stops-medium-139",
      "title": "787 — Cheapest Flights Within K Stops (Medium)",
      "path": [
        "01 — Problem Solving & Data Structures & Algorithms (DSA)",
        "1.5 Recursion Roadmap & Problem Tracker",
        "E. Graphs (الرسوم البيانية)",
        "Common Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--dbms-vs-rdbms-140",
      "title": "DBMS vs RDBMS",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--database-architecture-141",
      "title": "Database Architecture",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--relational-model-142",
      "title": "Relational Model",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--tables-rows-columns-143",
      "title": "Tables, Rows, Columns",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--data-types-144",
      "title": "Data Types",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--sql-vs-nosql-145",
      "title": "SQL vs NoSQL",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--acid-properties-146",
      "title": "ACID Properties",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture"
      ],
      "hasChildren": true
    },
    {
      "id": "21-core-concepts-and-architecture--atomicity-147",
      "title": "Atomicity",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture",
        "ACID Properties"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--consistency-148",
      "title": "Consistency",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture",
        "ACID Properties"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--isolation-149",
      "title": "Isolation",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture",
        "ACID Properties"
      ],
      "hasChildren": false
    },
    {
      "id": "21-core-concepts-and-architecture--durability-150",
      "title": "Durability",
      "path": [
        "02 — DBMS & Data Management",
        "2.1 Core Concepts & Architecture",
        "ACID Properties"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--keys-151",
      "title": "Keys",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design"
      ],
      "hasChildren": true
    },
    {
      "id": "22-relational-database-design--primary-key-152",
      "title": "Primary Key",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Keys"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--foreign-key-153",
      "title": "Foreign Key",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Keys"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--candidate-key-154",
      "title": "Candidate Key",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Keys"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--composite-key-155",
      "title": "Composite Key",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Keys"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--unique-key-156",
      "title": "Unique Key",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Keys"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--relationships-157",
      "title": "Relationships",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design"
      ],
      "hasChildren": true
    },
    {
      "id": "22-relational-database-design--one-to-one-158",
      "title": "One-to-One",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--one-to-many-159",
      "title": "One-to-Many",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--many-to-many-160",
      "title": "Many-to-Many",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--normalization-161",
      "title": "Normalization",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design"
      ],
      "hasChildren": true
    },
    {
      "id": "22-relational-database-design--1nf-162",
      "title": "1NF",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Normalization"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--2nf-163",
      "title": "2NF",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Normalization"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--3nf-164",
      "title": "3NF",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Normalization"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--bcnf-165",
      "title": "BCNF",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design",
        "Normalization"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--denormalization-166",
      "title": "Denormalization",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--schema-design-167",
      "title": "Schema Design",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "22-relational-database-design--data-modeling-168",
      "title": "Data Modeling",
      "path": [
        "02 — DBMS & Data Management",
        "2.2 Relational Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--transactions-169",
      "title": "Transactions",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--transaction-isolation-levels-170",
      "title": "Transaction Isolation Levels",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": true
    },
    {
      "id": "23-transactions-and-concurrency-control--read-uncommitted-171",
      "title": "Read Uncommitted",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Transaction Isolation Levels"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--read-committed-172",
      "title": "Read Committed",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Transaction Isolation Levels"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--repeatable-read-173",
      "title": "Repeatable Read",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Transaction Isolation Levels"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--serializable-174",
      "title": "Serializable",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Transaction Isolation Levels"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--concurrency-phenomena-175",
      "title": "Concurrency Phenomena",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": true
    },
    {
      "id": "23-transactions-and-concurrency-control--dirty-reads-176",
      "title": "Dirty Reads",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Concurrency Phenomena"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--non-repeatable-reads-177",
      "title": "Non-repeatable Reads",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Concurrency Phenomena"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--phantom-reads-178",
      "title": "Phantom Reads",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Concurrency Phenomena"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--lost-updates-179",
      "title": "Lost Updates",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Concurrency Phenomena"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--write-skew-180",
      "title": "Write Skew",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Concurrency Phenomena"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--locks-181",
      "title": "Locks",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": true
    },
    {
      "id": "23-transactions-and-concurrency-control--shared-locks-182",
      "title": "Shared Locks",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Locks"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--exclusive-locks-183",
      "title": "Exclusive Locks",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Locks"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--intent-locks-184",
      "title": "Intent Locks",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control",
        "Locks"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--deadlocks-185",
      "title": "Deadlocks",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--mvcc-multi-version-concurrency-control-186",
      "title": "MVCC (Multi-Version Concurrency Control)",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--optimistic-concurrency-control-187",
      "title": "Optimistic Concurrency Control",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--pessimistic-concurrency-control-188",
      "title": "Pessimistic Concurrency Control",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--wal-write-ahead-logging-189",
      "title": "WAL (Write-Ahead Logging)",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "23-transactions-and-concurrency-control--savepoints-190",
      "title": "Savepoints",
      "path": [
        "02 — DBMS & Data Management",
        "2.3 Transactions & Concurrency Control"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--indexing-191",
      "title": "Indexing",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": true
    },
    {
      "id": "24-storage-indexing-and-query-performance--b-tree-192",
      "title": "B-Tree",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance",
        "Indexing"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--btree-193",
      "title": "B+Tree",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance",
        "Indexing"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--hash-index-194",
      "title": "Hash Index",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance",
        "Indexing"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--clustered-vs-non-clustered-195",
      "title": "Clustered vs Non-Clustered",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance",
        "Indexing"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--bitmap-index-196",
      "title": "Bitmap Index",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance",
        "Indexing"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--query-processing-197",
      "title": "Query Processing",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--query-planner-optimizer-198",
      "title": "Query Planner / Optimizer",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--query-execution-plans-199",
      "title": "Query Execution Plans",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--database-caching-200",
      "title": "Database Caching",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--buffer-pool-management-201",
      "title": "Buffer Pool Management",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--storage-engines-202",
      "title": "Storage Engines",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "24-storage-indexing-and-query-performance--vacuuming-and-maintenance-203",
      "title": "Vacuuming and Maintenance",
      "path": [
        "02 — DBMS & Data Management",
        "2.4 Storage, Indexing & Query Performance"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--replication-204",
      "title": "Replication",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": true
    },
    {
      "id": "25-distributed-databases-and-scaling--primary-replica-master-slave-205",
      "title": "Primary-Replica (Master-Slave)",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling",
        "Replication"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--multi-primary-master-master-206",
      "title": "Multi-Primary (Master-Master)",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling",
        "Replication"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--synchronous-vs-asynchronous-207",
      "title": "Synchronous vs Asynchronous",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling",
        "Replication"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--read-replicas-208",
      "title": "Read Replicas",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--sharding-209",
      "title": "Sharding",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--horizontal-vertical-partitioning-210",
      "title": "Horizontal / Vertical Partitioning",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--cap-theorem-211",
      "title": "CAP Theorem",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": true
    },
    {
      "id": "25-distributed-databases-and-scaling--consistency-212",
      "title": "Consistency",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling",
        "CAP Theorem"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--availability-213",
      "title": "Availability",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling",
        "CAP Theorem"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--partition-tolerance-214",
      "title": "Partition Tolerance",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling",
        "CAP Theorem"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--acid-vs-base-215",
      "title": "ACID vs BASE",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": false
    },
    {
      "id": "25-distributed-databases-and-scaling--distributed-transactions-overview-216",
      "title": "Distributed Transactions (overview)",
      "path": [
        "02 — DBMS & Data Management",
        "2.5 Distributed Databases & Scaling"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases-sql--mysql-217",
      "title": "MySQL",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Relational Databases (SQL)"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases-sql--postgresql-218",
      "title": "PostgreSQL",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Relational Databases (SQL)"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases-sql--microsoft-sql-server-219",
      "title": "Microsoft SQL Server",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Relational Databases (SQL)"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases-sql--sqlite-220",
      "title": "SQLite",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Relational Databases (SQL)"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases-sql--oracle-database-221",
      "title": "Oracle Database",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Relational Databases (SQL)"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--document-stores-222",
      "title": "Document Stores",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)"
      ],
      "hasChildren": true
    },
    {
      "id": "non-relational-databases-nosql--mongodb-223",
      "title": "MongoDB",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Document Stores"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--couchdb-224",
      "title": "CouchDB",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Document Stores"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--key-value-stores-225",
      "title": "Key-Value Stores",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)"
      ],
      "hasChildren": true
    },
    {
      "id": "non-relational-databases-nosql--redis-226",
      "title": "Redis",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Key-Value Stores"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--amazon-dynamodb-227",
      "title": "Amazon DynamoDB",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Key-Value Stores"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--graph-databases-228",
      "title": "Graph Databases",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)"
      ],
      "hasChildren": true
    },
    {
      "id": "non-relational-databases-nosql--neo4j-229",
      "title": "Neo4j",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Graph Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--amazon-neptune-230",
      "title": "Amazon Neptune",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Graph Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--time-series-databases-231",
      "title": "Time-Series Databases",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)"
      ],
      "hasChildren": true
    },
    {
      "id": "non-relational-databases-nosql--influxdb-232",
      "title": "InfluxDB",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Time-Series Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--timescaledb-233",
      "title": "TimescaleDB",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Time-Series Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--column-family-wide-column-stores-234",
      "title": "Column-Family / Wide-Column Stores",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)"
      ],
      "hasChildren": true
    },
    {
      "id": "non-relational-databases-nosql--apache-cassandra-235",
      "title": "Apache Cassandra",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Column-Family / Wide-Column Stores"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--hbase-236",
      "title": "HBase",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Column-Family / Wide-Column Stores"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--object-oriented-dbms-237",
      "title": "Object-Oriented DBMS",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)"
      ],
      "hasChildren": true
    },
    {
      "id": "non-relational-databases-nosql--db4o-238",
      "title": "db4o",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Object-Oriented DBMS"
      ],
      "hasChildren": false
    },
    {
      "id": "non-relational-databases-nosql--objectdb-239",
      "title": "ObjectDB",
      "path": [
        "02 — DBMS & Data Management",
        "2.6 Database Types & Engines",
        "Non-Relational Databases (NoSQL)",
        "Object-Oriented DBMS"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--encapsulation-240",
      "title": "Encapsulation",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--abstraction-241",
      "title": "Abstraction",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--inheritance-242",
      "title": "Inheritance",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": true
    },
    {
      "id": "31-oop-fundamentals--single-243",
      "title": "Single",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Inheritance"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--multiple-244",
      "title": "Multiple",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Inheritance"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--multilevel-245",
      "title": "Multilevel",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Inheritance"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--hierarchical-246",
      "title": "Hierarchical",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Inheritance"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--hybrid-247",
      "title": "Hybrid",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Inheritance"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--polymorphism-248",
      "title": "Polymorphism",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": true
    },
    {
      "id": "31-oop-fundamentals--runtime-polymorphism-249",
      "title": "Runtime Polymorphism",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Polymorphism"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--overriding-250",
      "title": "Overriding",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Polymorphism"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--compile-time-polymorphism-251",
      "title": "Compile-Time Polymorphism",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Polymorphism"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--method-overloading-252",
      "title": "Method Overloading",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Polymorphism"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--operator-overloading-253",
      "title": "Operator Overloading",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Polymorphism"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--access-modifiers-254",
      "title": "Access Modifiers",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": true
    },
    {
      "id": "31-oop-fundamentals--public-255",
      "title": "Public",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Access Modifiers"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--private-256",
      "title": "Private",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Access Modifiers"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--protected-257",
      "title": "Protected",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Access Modifiers"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--protocol-interface-concepts-258",
      "title": "Protocol / Interface concepts",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals",
        "Access Modifiers"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--classes-and-objects-259",
      "title": "Classes and Objects",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "31-oop-fundamentals--composition-260",
      "title": "Composition",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.1 OOP Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "32-object-relationships--association-261",
      "title": "Association",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.2 Object Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "32-object-relationships--aggregation-262",
      "title": "Aggregation",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.2 Object Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "32-object-relationships--composition-263",
      "title": "Composition",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.2 Object Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "32-object-relationships--inheritance-264",
      "title": "Inheritance",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.2 Object Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "32-object-relationships--realization-265",
      "title": "Realization",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.2 Object Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "32-object-relationships--dependency-266",
      "title": "Dependency",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.2 Object Relationships"
      ],
      "hasChildren": false
    },
    {
      "id": "solid-principles--single-responsibility-principle-267",
      "title": "Single Responsibility Principle",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "SOLID Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "solid-principles--open-closed-principle-268",
      "title": "Open/Closed Principle",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "SOLID Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "solid-principles--liskov-substitution-principle-269",
      "title": "Liskov Substitution Principle",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "SOLID Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "solid-principles--interface-segregation-principle-270",
      "title": "Interface Segregation Principle",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "SOLID Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "solid-principles--dependency-inversion-principle-271",
      "title": "Dependency Inversion Principle",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "SOLID Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--dry-dont-repeat-yourself-272",
      "title": "DRY (Don't Repeat Yourself)",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--kiss-keep-it-simple-stupid-273",
      "title": "KISS (Keep It Simple, Stupid)",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--yagni-you-arent-gonna-need-it-274",
      "title": "YAGNI (You Aren't Gonna Need It)",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--separation-of-concerns-275",
      "title": "Separation of Concerns",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--encapsulate-what-varies-276",
      "title": "Encapsulate What Varies",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--favor-composition-over-inheritance-277",
      "title": "Favor Composition Over Inheritance",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--law-of-demeter-principle-of-least-knowledge-278",
      "title": "Law of Demeter (Principle of Least Knowledge)",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--pola-principle-of-least-astonishment-279",
      "title": "POLA (Principle of Least Astonishment)",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--cohesion-and-coupling-280",
      "title": "Cohesion & Coupling",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles"
      ],
      "hasChildren": true
    },
    {
      "id": "general-principles--high-cohesion-281",
      "title": "High Cohesion",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles",
        "Cohesion & Coupling"
      ],
      "hasChildren": false
    },
    {
      "id": "general-principles--low-coupling-282",
      "title": "Low Coupling",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.3 Design Principles",
        "General Principles",
        "Cohesion & Coupling"
      ],
      "hasChildren": false
    },
    {
      "id": "creational-patterns-5--singleton-283",
      "title": "Singleton",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Creational Patterns (5)"
      ],
      "hasChildren": false
    },
    {
      "id": "creational-patterns-5--factory-method-284",
      "title": "Factory Method",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Creational Patterns (5)"
      ],
      "hasChildren": false
    },
    {
      "id": "creational-patterns-5--abstract-factory-285",
      "title": "Abstract Factory",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Creational Patterns (5)"
      ],
      "hasChildren": false
    },
    {
      "id": "creational-patterns-5--builder-286",
      "title": "Builder",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Creational Patterns (5)"
      ],
      "hasChildren": false
    },
    {
      "id": "creational-patterns-5--prototype-287",
      "title": "Prototype",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Creational Patterns (5)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--adapter-288",
      "title": "Adapter",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--bridge-289",
      "title": "Bridge",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--composite-290",
      "title": "Composite",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--decorator-291",
      "title": "Decorator",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--facade-292",
      "title": "Facade",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--flyweight-293",
      "title": "Flyweight",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "structural-patterns-7--proxy-294",
      "title": "Proxy",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Structural Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--chain-of-responsibility-295",
      "title": "Chain of Responsibility",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--command-296",
      "title": "Command",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--interpreter-297",
      "title": "Interpreter",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--iterator-298",
      "title": "Iterator",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--mediator-299",
      "title": "Mediator",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--memento-300",
      "title": "Memento",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--observer-301",
      "title": "Observer",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--state-302",
      "title": "State",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--strategy-303",
      "title": "Strategy",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--template-method-304",
      "title": "Template Method",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "behavioral-patterns-11--visitor-305",
      "title": "Visitor",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.4 GoF Design Patterns",
        "Behavioral Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "35-uml-and-object-modeling--class-diagram-306",
      "title": "Class Diagram",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.5 UML & Object Modeling"
      ],
      "hasChildren": false
    },
    {
      "id": "35-uml-and-object-modeling--use-case-diagram-307",
      "title": "Use Case Diagram",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.5 UML & Object Modeling"
      ],
      "hasChildren": false
    },
    {
      "id": "35-uml-and-object-modeling--sequence-diagram-308",
      "title": "Sequence Diagram",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.5 UML & Object Modeling"
      ],
      "hasChildren": false
    },
    {
      "id": "35-uml-and-object-modeling--activity-diagram-309",
      "title": "Activity Diagram",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.5 UML & Object Modeling"
      ],
      "hasChildren": false
    },
    {
      "id": "35-uml-and-object-modeling--state-machine-diagram-310",
      "title": "State Machine Diagram",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.5 UML & Object Modeling"
      ],
      "hasChildren": false
    },
    {
      "id": "35-uml-and-object-modeling--object-domain-modeling-311",
      "title": "Object / Domain Modeling",
      "path": [
        "03 — Object-Oriented Design (OOD)",
        "3.5 UML & Object Modeling"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--system-structure",
      "title": "System Structure",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles"
      ],
      "hasChildren": true
    },
    {
      "id": "41-architectural-styles--monolithic-architecture",
      "title": "Monolithic Architecture",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "System Structure"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--modular-monolith",
      "title": "Modular Monolith",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "System Structure"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--microservices-architecture",
      "title": "Microservices Architecture",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "System Structure"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--soa",
      "title": "Service-Oriented Architecture (SOA)",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "System Structure"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--communication-and-distribution",
      "title": "Communication & Distribution",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles"
      ],
      "hasChildren": true
    },
    {
      "id": "41-architectural-styles--client-server-architecture",
      "title": "Client-Server Architecture",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "Communication & Distribution"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--event-driven-architecture",
      "title": "Event-Driven Architecture (EDA)",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "Communication & Distribution"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--serverless-architecture",
      "title": "Serverless Architecture / FaaS",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "Communication & Distribution"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--internal-organization",
      "title": "Internal Organization",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles"
      ],
      "hasChildren": true
    },
    {
      "id": "41-architectural-styles--layered-architecture",
      "title": "Layered Architecture (N-Tier)",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "Internal Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--pipe-and-filter-architecture",
      "title": "Pipe-and-Filter Architecture",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "Internal Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "41-architectural-styles--microkernel-plugin-architecture",
      "title": "Microkernel / Plugin Architecture",
      "path": [
        "04 — Application Architecture",
        "4.1 Architectural Styles",
        "Internal Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "42-architectural-patterns--clean-architecture-uncle-bob-322",
      "title": "Clean Architecture (Uncle Bob)",
      "path": [
        "04 — Application Architecture",
        "4.2 Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "42-architectural-patterns--hexagonal-architecture-ports-and-adapters-323",
      "title": "Hexagonal Architecture (Ports and Adapters)",
      "path": [
        "04 — Application Architecture",
        "4.2 Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "42-architectural-patterns--onion-architecture-324",
      "title": "Onion Architecture",
      "path": [
        "04 — Application Architecture",
        "4.2 Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "42-architectural-patterns--model-view-controller-mvc-325",
      "title": "Model-View-Controller (MVC)",
      "path": [
        "04 — Application Architecture",
        "4.2 Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "42-architectural-patterns--model-view-presenter-mvp-326",
      "title": "Model-View-Presenter (MVP)",
      "path": [
        "04 — Application Architecture",
        "4.2 Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "42-architectural-patterns--model-view-viewmodel-mvvm-327",
      "title": "Model-View-ViewModel (MVVM)",
      "path": [
        "04 — Application Architecture",
        "4.2 Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--separation-of-concerns-soc-328",
      "title": "Separation of Concerns (SoC)",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--domain-driven-design-ddd-integration-329",
      "title": "Domain-Driven Design (DDD) Integration",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--inversion-of-control-ioc-330",
      "title": "Inversion of Control (IoC)",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--dependency-injection-di-331",
      "title": "Dependency Injection (DI)",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--dependency-inversion-332",
      "title": "Dependency Inversion",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--ports-and-adapters-interfaces-and-implementations-333",
      "title": "Ports and Adapters (Interfaces and Implementations)",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--boundary-management-334",
      "title": "Boundary Management",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--dependency-rules-335",
      "title": "Dependency Rules",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--data-transfer-objects-dtos-336",
      "title": "Data Transfer Objects (DTOs)",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--mappers-337",
      "title": "Mappers",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--decoupling-business-logic-from-infrastructure-338",
      "title": "Decoupling Business Logic from Infrastructure",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": true
    },
    {
      "id": "43-core-concepts-and-principles--databases-339",
      "title": "Databases",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles",
        "Decoupling Business Logic from Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--frameworks-340",
      "title": "Frameworks",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles",
        "Decoupling Business Logic from Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--external-apis-341",
      "title": "External APIs",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles",
        "Decoupling Business Logic from Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--high-cohesion-low-coupling-342",
      "title": "High Cohesion / Low Coupling",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--testability-and-modifiability-343",
      "title": "Testability and Modifiability",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "43-core-concepts-and-principles--architectural-trade-offs-344",
      "title": "Architectural Trade-offs",
      "path": [
        "04 — Application Architecture",
        "4.3 Core Concepts & Principles"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--modularization-345",
      "title": "Modularization",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--module-boundaries-346",
      "title": "Module Boundaries",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--package-by-layer-347",
      "title": "Package by Layer",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--package-by-feature-348",
      "title": "Package by Feature",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--component-based-design-349",
      "title": "Component-Based Design",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--plugin-architecture-350",
      "title": "Plugin Architecture",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "44-application-organization--internal-vs-external-interfaces-351",
      "title": "Internal vs External Interfaces",
      "path": [
        "04 — Application Architecture",
        "4.4 Application Organization"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--api-integration-352",
      "title": "API Integration",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--synchronous-vs-asynchronous-communication-353",
      "title": "Synchronous vs Asynchronous Communication",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--point-to-point-integration-354",
      "title": "Point-to-Point Integration",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--hub-and-spoke-355",
      "title": "Hub-and-Spoke",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--enterprise-service-bus-esb-356",
      "title": "Enterprise Service Bus (ESB)",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--api-led-connectivity-357",
      "title": "API-Led Connectivity",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--event-driven-integration-358",
      "title": "Event-Driven Integration",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "45-integration-architecture--canonical-data-model-359",
      "title": "Canonical Data Model",
      "path": [
        "04 — Application Architecture",
        "4.5 Integration Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "51-core-architectural-patterns--mvc-model-view-controller-360",
      "title": "MVC (Model-View-Controller)",
      "path": [
        "05 — Presentation Architecture",
        "5.1 Core Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "51-core-architectural-patterns--mvp-model-view-presenter-361",
      "title": "MVP (Model-View-Presenter)",
      "path": [
        "05 — Presentation Architecture",
        "5.1 Core Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "51-core-architectural-patterns--mvvm-model-view-viewmodel-362",
      "title": "MVVM (Model-View-ViewModel)",
      "path": [
        "05 — Presentation Architecture",
        "5.1 Core Architectural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "52-advanced-and-mobile-specific-patterns--viper-view-interactor-presenter-entity-router-363",
      "title": "VIPER (View-Interactor-Presenter-Entity-Router)",
      "path": [
        "05 — Presentation Architecture",
        "5.2 Advanced & Mobile-Specific Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "52-advanced-and-mobile-specific-patterns--mvi-model-view-intent-364",
      "title": "MVI (Model-View-Intent)",
      "path": [
        "05 — Presentation Architecture",
        "5.2 Advanced & Mobile-Specific Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--component-based-architecture-365",
      "title": "Component-Based Architecture",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures"
      ],
      "hasChildren": true
    },
    {
      "id": "53-modern-frontend-and-component-architectures--react-366",
      "title": "React",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Component-Based Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--vue-367",
      "title": "Vue",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Component-Based Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--svelte-368",
      "title": "Svelte",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Component-Based Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--angular-369",
      "title": "Angular",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Component-Based Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--container-presentational-components-370",
      "title": "Container / Presentational Components",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--smart-dumb-components-371",
      "title": "Smart / Dumb Components",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--unidirectional-data-flow-372",
      "title": "Unidirectional Data Flow",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--flux-pattern-373",
      "title": "Flux Pattern",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures"
      ],
      "hasChildren": true
    },
    {
      "id": "53-modern-frontend-and-component-architectures--redux-374",
      "title": "Redux",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Flux Pattern"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--ngrx-375",
      "title": "NgRx",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Flux Pattern"
      ],
      "hasChildren": false
    },
    {
      "id": "53-modern-frontend-and-component-architectures--pinia-376",
      "title": "Pinia",
      "path": [
        "05 — Presentation Architecture",
        "5.3 Modern Frontend & Component Architectures",
        "Flux Pattern"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--local-state-377",
      "title": "Local State",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--global-state-378",
      "title": "Global State",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--state-management-379",
      "title": "State Management",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--reactive-state-380",
      "title": "Reactive State",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--observable-381",
      "title": "Observable",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--immutable-state-382",
      "title": "Immutable State",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--bloc-383",
      "title": "BLoC",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--provider-384",
      "title": "Provider",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--riverpod-385",
      "title": "Riverpod",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "54-state-management-and-reactive-patterns--signals-386",
      "title": "Signals",
      "path": [
        "05 — Presentation Architecture",
        "5.4 State Management & Reactive Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--data-binding-387",
      "title": "Data Binding",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": true
    },
    {
      "id": "55-core-concepts-and-mechanisms--one-way-binding-388",
      "title": "One-Way Binding",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms",
        "Data Binding"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--two-way-binding-389",
      "title": "Two-Way Binding",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms",
        "Data Binding"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--event-handling-390",
      "title": "Event Handling",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--state-management-and-reactivity-391",
      "title": "State Management & Reactivity",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--separation-of-ui-rendering-from-business-logic-392",
      "title": "Separation of UI Rendering from Business Logic",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--navigation-393",
      "title": "Navigation",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--ui-state-394",
      "title": "UI State",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": false
    },
    {
      "id": "55-core-concepts-and-mechanisms--rendering-lifecycle-395",
      "title": "Rendering Lifecycle",
      "path": [
        "05 — Presentation Architecture",
        "5.5 Core Concepts & Mechanisms"
      ],
      "hasChildren": false
    },
    {
      "id": "61-domain-logic-patterns-4--transaction-script-396",
      "title": "Transaction Script",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.1 Domain Logic Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "61-domain-logic-patterns-4--domain-model-397",
      "title": "Domain Model",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.1 Domain Logic Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "61-domain-logic-patterns-4--table-module-398",
      "title": "Table Module",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.1 Domain Logic Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "61-domain-logic-patterns-4--service-layer-399",
      "title": "Service Layer",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.1 Domain Logic Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "62-data-source-architectural-patterns-4--table-data-gateway-400",
      "title": "Table Data Gateway",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.2 Data Source Architectural Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "62-data-source-architectural-patterns-4--row-data-gateway-401",
      "title": "Row Data Gateway",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.2 Data Source Architectural Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "62-data-source-architectural-patterns-4--active-record-402",
      "title": "Active Record",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.2 Data Source Architectural Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "62-data-source-architectural-patterns-4--data-mapper-403",
      "title": "Data Mapper",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.2 Data Source Architectural Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "63-object-relational-behavioral-patterns-3--unit-of-work-404",
      "title": "Unit of Work",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.3 Object-Relational Behavioral Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "63-object-relational-behavioral-patterns-3--identity-map-405",
      "title": "Identity Map",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.3 Object-Relational Behavioral Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "63-object-relational-behavioral-patterns-3--lazy-load-406",
      "title": "Lazy Load",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.3 Object-Relational Behavioral Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--identity-field-407",
      "title": "Identity Field",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--foreign-key-mapping-408",
      "title": "Foreign Key Mapping",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--association-table-mapping-409",
      "title": "Association Table Mapping",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--dependent-mapping-410",
      "title": "Dependent Mapping",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--embedded-value-411",
      "title": "Embedded Value",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--serialized-lob-412",
      "title": "Serialized LOB",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--inheritance-mappers-413",
      "title": "Inheritance Mappers",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns"
      ],
      "hasChildren": true
    },
    {
      "id": "64-object-relational-structural-patterns--single-table-inheritance-414",
      "title": "Single Table Inheritance",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns",
        "Inheritance Mappers"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--class-table-inheritance-415",
      "title": "Class Table Inheritance",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns",
        "Inheritance Mappers"
      ],
      "hasChildren": false
    },
    {
      "id": "64-object-relational-structural-patterns--concrete-table-inheritance-416",
      "title": "Concrete Table Inheritance",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.4 Object-Relational Structural Patterns",
        "Inheritance Mappers"
      ],
      "hasChildren": false
    },
    {
      "id": "65-object-relational-metadata-mapping-patterns-3--metadata-mapping-417",
      "title": "Metadata Mapping",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.5 Object-Relational Metadata Mapping Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "65-object-relational-metadata-mapping-patterns-3--query-object-418",
      "title": "Query Object",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.5 Object-Relational Metadata Mapping Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "65-object-relational-metadata-mapping-patterns-3--repository-419",
      "title": "Repository",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.5 Object-Relational Metadata Mapping Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--model-view-controller-420",
      "title": "Model View Controller",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--page-controller-421",
      "title": "Page Controller",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--front-controller-422",
      "title": "Front Controller",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--template-view-423",
      "title": "Template View",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--transform-view-424",
      "title": "Transform View",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--two-step-view-425",
      "title": "Two-Step View",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "66-web-presentation-patterns-7--application-controller-426",
      "title": "Application Controller",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.6 Web Presentation Patterns (7)"
      ],
      "hasChildren": false
    },
    {
      "id": "67-distribution-patterns-2--remote-facade-427",
      "title": "Remote Facade",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.7 Distribution Patterns (2)"
      ],
      "hasChildren": false
    },
    {
      "id": "67-distribution-patterns-2--data-transfer-object-dto-428",
      "title": "Data Transfer Object (DTO)",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.7 Distribution Patterns (2)"
      ],
      "hasChildren": false
    },
    {
      "id": "68-offline-concurrency-patterns-4--optimistic-offline-lock-429",
      "title": "Optimistic Offline Lock",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.8 Offline Concurrency Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "68-offline-concurrency-patterns-4--pessimistic-offline-lock-430",
      "title": "Pessimistic Offline Lock",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.8 Offline Concurrency Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "68-offline-concurrency-patterns-4--coarse-grained-lock-431",
      "title": "Coarse-Grained Lock",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.8 Offline Concurrency Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "68-offline-concurrency-patterns-4--implicit-lock-432",
      "title": "Implicit Lock",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.8 Offline Concurrency Patterns (4)"
      ],
      "hasChildren": false
    },
    {
      "id": "69-session-state-patterns-3--client-session-state-433",
      "title": "Client Session State",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.9 Session State Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "69-session-state-patterns-3--server-session-state-434",
      "title": "Server Session State",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.9 Session State Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "69-session-state-patterns-3--database-session-state-435",
      "title": "Database Session State",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.9 Session State Patterns (3)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--gateway-436",
      "title": "Gateway",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--service-stub-437",
      "title": "Service Stub",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--mapper-438",
      "title": "Mapper",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--layer-supertype-439",
      "title": "Layer Supertype",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--separated-interface-440",
      "title": "Separated Interface",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--registry-441",
      "title": "Registry",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--value-object-442",
      "title": "Value Object",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--money-443",
      "title": "Money",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--special-case-444",
      "title": "Special Case",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--plugin-445",
      "title": "Plugin",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "610-base-patterns-11--record-set-446",
      "title": "Record Set",
      "path": [
        "06 — Patterns of Enterprise Application Architecture (PoEAA)",
        "6.10 Base Patterns (11)"
      ],
      "hasChildren": false
    },
    {
      "id": "domain-understanding--domain-447",
      "title": "Domain",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Domain Understanding"
      ],
      "hasChildren": false
    },
    {
      "id": "domain-understanding--subdomains-448",
      "title": "Subdomains",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Domain Understanding"
      ],
      "hasChildren": true
    },
    {
      "id": "domain-understanding--core-domain-449",
      "title": "Core Domain",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Domain Understanding",
        "Subdomains"
      ],
      "hasChildren": false
    },
    {
      "id": "domain-understanding--supporting-subdomain-450",
      "title": "Supporting Subdomain",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Domain Understanding",
        "Subdomains"
      ],
      "hasChildren": false
    },
    {
      "id": "domain-understanding--generic-subdomain-451",
      "title": "Generic Subdomain",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Domain Understanding",
        "Subdomains"
      ],
      "hasChildren": false
    },
    {
      "id": "domain-understanding--ubiquitous-language-452",
      "title": "Ubiquitous Language",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Domain Understanding"
      ],
      "hasChildren": false
    },
    {
      "id": "model-boundaries--bounded-context-453",
      "title": "Bounded Context",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Model Boundaries"
      ],
      "hasChildren": false
    },
    {
      "id": "model-boundaries--context-map-454",
      "title": "Context Map",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Model Boundaries"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--partnership-455",
      "title": "Partnership",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--shared-kernel-456",
      "title": "Shared Kernel",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--customer-supplier-457",
      "title": "Customer-Supplier",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--conformist-458",
      "title": "Conformist",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--anti-corruption-layer-459",
      "title": "Anti-Corruption Layer",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--open-host-service-460",
      "title": "Open Host Service",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--published-language-461",
      "title": "Published Language",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--separate-ways-462",
      "title": "Separate Ways",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "context-mapping-patterns--big-ball-of-mud-463",
      "title": "Big Ball of Mud",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.1 Strategic DDD",
        "Context Mapping Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--entity-464",
      "title": "Entity",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--value-object-465",
      "title": "Value Object",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--aggregate-466",
      "title": "Aggregate",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--aggregate-root-467",
      "title": "Aggregate Root",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--repository-468",
      "title": "Repository",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--domain-service-469",
      "title": "Domain Service",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--domain-event-470",
      "title": "Domain Event",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--factory-471",
      "title": "Factory",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "72-tactical-ddd--application-service-472",
      "title": "Application Service",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.2 Tactical DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--domain-model-473",
      "title": "Domain Model",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--domain-layer-474",
      "title": "Domain Layer",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--application-layer-475",
      "title": "Application Layer",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--infrastructure-layer-476",
      "title": "Infrastructure Layer",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--invariants-477",
      "title": "Invariants",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--aggregate-boundaries-478",
      "title": "Aggregate Boundaries",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--transaction-boundaries-479",
      "title": "Transaction Boundaries",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--domain-event-vs-integration-event-480",
      "title": "Domain Event vs Integration Event",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--eventual-consistency-481",
      "title": "Eventual Consistency",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "73-ddd-implementation-and-modeling-concepts--anti-corruption-layer-implementation-482",
      "title": "Anti-Corruption Layer Implementation",
      "path": [
        "07 — Domain-Driven Design (DDD)",
        "7.3 DDD Implementation & Modeling Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--producer-consumer",
      "title": "Producer–Consumer — فصل الإنتاج عن الاستهلاك",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--thread-pool",
      "title": "Thread Pool — مجموعة Threads يعاد استخدامها",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--future-promise",
      "title": "Future / Promise — تمثيل نتيجة مستقبلية",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--read-write-lock",
      "title": "Read–Write Lock — تعدد القراءات وانفراد الكتابة",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--monitor-condition-variable",
      "title": "Monitor / Condition Variable — حماية الحالة وتنظيم الانتظار على شرط",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--thread-confinement",
      "title": "Thread Confinement — تخصيص البيانات لـThread واحد",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--fork-join",
      "title": "Fork–Join — تقسيم المهمة وتجميع النتائج",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--reactor",
      "title": "Reactor — استقبال الأحداث وتوجيهها للمعالجات",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--barrier-synchronization",
      "title": "Barrier Synchronization — انتظار وصول الجميع قبل المتابعة",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "08-concurrency-patterns--active-object",
      "title": "Active Object — فصل الطلب عن التنفيذ",
      "path": [
        "08 — Concurrency Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--message-channel",
      "title": "Message Channel",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--content-based-router",
      "title": "Content-Based Router",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--message-translator",
      "title": "Message Translator",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--splitter",
      "title": "Splitter",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--aggregator",
      "title": "Aggregator",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--request-reply",
      "title": "Request–Reply",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--competing-consumers",
      "title": "Competing Consumers",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--dead-letter-channel",
      "title": "Dead Letter Channel",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--idempotent-receiver",
      "title": "Idempotent Receiver",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "09-enterprise-integration-patterns-eip--transactional-outbox",
      "title": "Transactional Outbox",
      "path": [
        "09 — Enterprise Integration Patterns (EIP)"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--what-is-system-design-683",
      "title": "What is System Design?",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--functional-vs-non-functional-requirements-684",
      "title": "Functional vs Non-Functional Requirements",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--scalability-685",
      "title": "Scalability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--reliability-686",
      "title": "Reliability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--availability-687",
      "title": "Availability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--maintainability-688",
      "title": "Maintainability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--performance-689",
      "title": "Performance",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--consistency-690",
      "title": "Consistency",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--latency-vs-throughput-691",
      "title": "Latency vs Throughput",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--capacity-estimation-692",
      "title": "Capacity Estimation",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--load-estimation-693",
      "title": "Load Estimation",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--back-of-the-envelope-calculations-694",
      "title": "Back-of-the-Envelope Calculations",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--quality-attributes-and-trade-offs-695",
      "title": "Quality Attributes and Trade-offs",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals"
      ],
      "hasChildren": true
    },
    {
      "id": "101-system-design-fundamentals--modifiability-696",
      "title": "Modifiability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals",
        "Quality Attributes and Trade-offs"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--testability-697",
      "title": "Testability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals",
        "Quality Attributes and Trade-offs"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--extensibility-698",
      "title": "Extensibility",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals",
        "Quality Attributes and Trade-offs"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--portability-699",
      "title": "Portability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals",
        "Quality Attributes and Trade-offs"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--interoperability-700",
      "title": "Interoperability",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals",
        "Quality Attributes and Trade-offs"
      ],
      "hasChildren": false
    },
    {
      "id": "101-system-design-fundamentals--security-701",
      "title": "Security",
      "path": [
        "10 — System Design",
        "10.1 System Design Fundamentals",
        "Quality Attributes and Trade-offs"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--osi-model-702",
      "title": "OSI Model",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--tcp-ip-model-703",
      "title": "TCP/IP Model",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--http-https-704",
      "title": "HTTP / HTTPS",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--tcp-vs-udp-705",
      "title": "TCP vs UDP",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--tcp-handshake-706",
      "title": "TCP Handshake",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--connection-lifecycle-707",
      "title": "Connection Lifecycle",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--rest-vs-soap-708",
      "title": "REST vs SOAP",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--grpc-709",
      "title": "gRPC",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--websockets-710",
      "title": "WebSockets",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--long-polling-711",
      "title": "Long Polling",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--dns-712",
      "title": "DNS",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--cdn-713",
      "title": "CDN",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--reverse-proxy-714",
      "title": "Reverse Proxy",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--forward-proxy-715",
      "title": "Forward Proxy",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--nat-716",
      "title": "NAT",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--api-gateway-717",
      "title": "API Gateway",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--connection-pooling-718",
      "title": "Connection Pooling",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--rate-limiting-719",
      "title": "Rate Limiting",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--throttling-720",
      "title": "Throttling",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "102-networking-and-communication--tls-721",
      "title": "TLS",
      "path": [
        "10 — System Design",
        "10.2 Networking & Communication"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--mysql-postgresql-722",
      "title": "MySQL / PostgreSQL",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--acid-723",
      "title": "ACID",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--indexes-724",
      "title": "Indexes",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--transactions-725",
      "title": "Transactions",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--normalization-vs-denormalization-726",
      "title": "Normalization vs Denormalization",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--read-replicas-727",
      "title": "Read Replicas",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "relational-databases--sharding-728",
      "title": "Sharding",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Relational Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "nosql-databases--key-value-redis-dynamodb-729",
      "title": "Key-Value (Redis, DynamoDB)",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "NoSQL Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "nosql-databases--document-mongodb-730",
      "title": "Document (MongoDB)",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "NoSQL Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "nosql-databases--column-family-cassandra-731",
      "title": "Column Family (Cassandra)",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "NoSQL Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "nosql-databases--graph-db-neo4j-732",
      "title": "Graph DB (Neo4j)",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "NoSQL Databases"
      ],
      "hasChildren": false
    },
    {
      "id": "cap-theorem--consistency-733",
      "title": "Consistency",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "CAP Theorem"
      ],
      "hasChildren": false
    },
    {
      "id": "cap-theorem--availability-734",
      "title": "Availability",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "CAP Theorem"
      ],
      "hasChildren": false
    },
    {
      "id": "cap-theorem--partition-tolerance-735",
      "title": "Partition Tolerance",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "CAP Theorem"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--schema-design-736",
      "title": "Schema Design",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--data-modeling-737",
      "title": "Data Modeling",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--hot-partitions-738",
      "title": "Hot Partitions",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--data-migration-739",
      "title": "Data Migration",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--oltp-vs-olap-740",
      "title": "OLTP vs OLAP",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--data-warehouse-741",
      "title": "Data Warehouse",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "database-design--read-models-742",
      "title": "Read Models",
      "path": [
        "10 — System Design",
        "10.3 Data Storage (Databases)",
        "Database Design"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--what-is-caching-743",
      "title": "What is Caching?",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--cache-vs-db-744",
      "title": "Cache vs DB",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--cache-hit-miss-745",
      "title": "Cache Hit / Miss",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--cache-eviction-policies-746",
      "title": "Cache Eviction Policies",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": true
    },
    {
      "id": "104-caching--lru-747",
      "title": "LRU",
      "path": [
        "10 — System Design",
        "10.4 Caching",
        "Cache Eviction Policies"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--lfu-748",
      "title": "LFU",
      "path": [
        "10 — System Design",
        "10.4 Caching",
        "Cache Eviction Policies"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--fifo-749",
      "title": "FIFO",
      "path": [
        "10 — System Design",
        "10.4 Caching",
        "Cache Eviction Policies"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--cache-aside-750",
      "title": "Cache-Aside",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--read-through-751",
      "title": "Read-Through",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--write-through-752",
      "title": "Write-Through",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--write-back-753",
      "title": "Write-Back",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--write-around-754",
      "title": "Write-Around",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--redis-755",
      "title": "Redis",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--memcached-756",
      "title": "Memcached",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--cdn-caching-757",
      "title": "CDN Caching",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "104-caching--cache-invalidation-758",
      "title": "Cache Invalidation",
      "path": [
        "10 — System Design",
        "10.4 Caching"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--vertical-scaling-759",
      "title": "Vertical Scaling",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--horizontal-scaling-760",
      "title": "Horizontal Scaling",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--stateless-services-761",
      "title": "Stateless Services",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--stateful-services-762",
      "title": "Stateful Services",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--load-balancing-763",
      "title": "Load Balancing",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": true
    },
    {
      "id": "105-scalability-patterns--round-robin-764",
      "title": "Round Robin",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns",
        "Load Balancing"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--least-connections-765",
      "title": "Least Connections",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns",
        "Load Balancing"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--hash-based-766",
      "title": "Hash-based",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns",
        "Load Balancing"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--consistent-hashing-767",
      "title": "Consistent Hashing",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns",
        "Load Balancing"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--auto-scaling-768",
      "title": "Auto Scaling",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--sharding-strategies-769",
      "title": "Sharding Strategies",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "105-scalability-patterns--partitioning-770",
      "title": "Partitioning",
      "path": [
        "10 — System Design",
        "10.5 Scalability Patterns"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--distributed-systems-basics-771",
      "title": "Distributed Systems Basics",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--consistency-models-772",
      "title": "Consistency Models",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": true
    },
    {
      "id": "106-distributed-systems-concepts--strong-consistency-773",
      "title": "Strong Consistency",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts",
        "Consistency Models"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--eventual-consistency-774",
      "title": "Eventual Consistency",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts",
        "Consistency Models"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--causal-consistency-775",
      "title": "Causal Consistency",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts",
        "Consistency Models"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--leader-election-776",
      "title": "Leader Election",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--consensus-algorithms-777",
      "title": "Consensus Algorithms",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": true
    },
    {
      "id": "106-distributed-systems-concepts--paxos-778",
      "title": "Paxos",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts",
        "Consensus Algorithms"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--raft-779",
      "title": "Raft",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts",
        "Consensus Algorithms"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--clock-synchronization-780",
      "title": "Clock Synchronization",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--logical-clocks-781",
      "title": "Logical Clocks",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--vector-clocks-782",
      "title": "Vector Clocks",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--distributed-locks-783",
      "title": "Distributed Locks",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--idempotency-784",
      "title": "Idempotency",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--split-brain-785",
      "title": "Split Brain",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--quorum-786",
      "title": "Quorum",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "106-distributed-systems-concepts--failure-detection-787",
      "title": "Failure Detection",
      "path": [
        "10 — System Design",
        "10.6 Distributed Systems Concepts"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--message-queues-788",
      "title": "Message Queues",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--kafka-789",
      "title": "Kafka",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--rabbitmq-790",
      "title": "RabbitMQ",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--sqs-791",
      "title": "SQS",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--pub-sub-792",
      "title": "Pub/Sub",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--event-driven-architecture-793",
      "title": "Event-Driven Architecture",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--at-most-once-delivery-794",
      "title": "At-most-once Delivery",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--at-least-once-delivery-795",
      "title": "At-least-once Delivery",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--exactly-once-semantics-796",
      "title": "Exactly-once Semantics",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--dead-letter-queues-797",
      "title": "Dead Letter Queues",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--backpressure-798",
      "title": "Backpressure",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--message-ordering-799",
      "title": "Message Ordering",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--consumer-groups-800",
      "title": "Consumer Groups",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "107-messaging-and-async-processing--transactional-outbox-inbox-801",
      "title": "Transactional Outbox / Inbox",
      "path": [
        "10 — System Design",
        "10.7 Messaging & Async Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--monolith-vs-microservices-802",
      "title": "Monolith vs Microservices",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--modular-monolith-803",
      "title": "Modular Monolith",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--service-discovery-804",
      "title": "Service Discovery",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--inter-service-communication-805",
      "title": "Inter-Service Communication",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--api-gateway-806",
      "title": "API Gateway",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--backend-for-frontend-bff-807",
      "title": "Backend for Frontend (BFF)",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--circuit-breaker-808",
      "title": "Circuit Breaker",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--retry-and-timeout-809",
      "title": "Retry & Timeout",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--bulkhead-810",
      "title": "Bulkhead",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--saga-pattern-811",
      "title": "Saga Pattern",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--choreography-vs-orchestration-812",
      "title": "Choreography vs Orchestration",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--data-per-service-813",
      "title": "Data per Service",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--database-per-service-814",
      "title": "Database per Service",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--microservices-anti-patterns-815",
      "title": "Microservices Anti-Patterns",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--strangler-fig-pattern-816",
      "title": "Strangler Fig Pattern",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--service-mesh-817",
      "title": "Service Mesh",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "108-microservices-architecture--anti-corruption-layer-818",
      "title": "Anti-Corruption Layer",
      "path": [
        "10 — System Design",
        "10.8 Microservices Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--authentication-819",
      "title": "Authentication",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--authorization-820",
      "title": "Authorization",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--oauth-20-821",
      "title": "OAuth 2.0",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--openid-connect-oidc-822",
      "title": "OpenID Connect (OIDC)",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--jwt-823",
      "title": "JWT",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--sso-824",
      "title": "SSO",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--https-tls-825",
      "title": "HTTPS / TLS",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--encryption-at-rest-in-transit-826",
      "title": "Encryption at Rest / In Transit",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--rate-limiting-827",
      "title": "Rate Limiting",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--ddos-protection-828",
      "title": "DDoS Protection",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--secrets-management-829",
      "title": "Secrets Management",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--rbac-830",
      "title": "RBAC",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--abac-831",
      "title": "ABAC",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "109-security--least-privilege-832",
      "title": "Least Privilege",
      "path": [
        "10 — System Design",
        "10.9 Security"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--single-point-of-failure-833",
      "title": "Single Point of Failure",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--replication-834",
      "title": "Replication",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--failover-835",
      "title": "Failover",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--health-checks-836",
      "title": "Health Checks",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--heartbeats-837",
      "title": "Heartbeats",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--graceful-degradation-838",
      "title": "Graceful Degradation",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--disaster-recovery-839",
      "title": "Disaster Recovery",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--backup-strategies-840",
      "title": "Backup Strategies",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--rto-rpo-841",
      "title": "RTO / RPO",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--fault-tolerance-842",
      "title": "Fault Tolerance",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--redundancy-843",
      "title": "Redundancy",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--retry-and-timeout-844",
      "title": "Retry and Timeout",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1010-high-availability-and-reliability--failure-isolation-845",
      "title": "Failure Isolation",
      "path": [
        "10 — System Design",
        "10.10 High Availability & Reliability"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--logging-846",
      "title": "Logging",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--metrics-847",
      "title": "Metrics",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--monitoring-848",
      "title": "Monitoring",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--distributed-tracing-849",
      "title": "Distributed Tracing",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--alerting-850",
      "title": "Alerting",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--slis-slos-slas-851",
      "title": "SLIs / SLOs / SLAs",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--prometheus-852",
      "title": "Prometheus",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--grafana-853",
      "title": "Grafana",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--elk-stack-854",
      "title": "ELK Stack",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1011-observability-and-monitoring--opentelemetry-855",
      "title": "OpenTelemetry",
      "path": [
        "10 — System Design",
        "10.11 Observability & Monitoring"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--singleton-856",
      "title": "Singleton",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--factory-857",
      "title": "Factory",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--observer-858",
      "title": "Observer",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--cqrs-859",
      "title": "CQRS",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--event-sourcing-860",
      "title": "Event Sourcing",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--bulkhead-861",
      "title": "Bulkhead",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--sidecar-862",
      "title": "Sidecar",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--ambassador-863",
      "title": "Ambassador",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--strangler-fig-pattern-864",
      "title": "Strangler Fig Pattern",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--api-composition-865",
      "title": "API Composition",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1012-design-patterns-system-level--cell-based-architecture-866",
      "title": "Cell-Based Architecture",
      "path": [
        "10 — System Design",
        "10.12 Design Patterns (System Level)"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--batch-processing-867",
      "title": "Batch Processing",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--stream-processing-868",
      "title": "Stream Processing",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--etl-869",
      "title": "ETL",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--elt-870",
      "title": "ELT",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--mapreduce-871",
      "title": "MapReduce",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--spark-872",
      "title": "Spark",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--flink-873",
      "title": "Flink",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--data-pipelines-874",
      "title": "Data Pipelines",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1013-data-processing--data-warehouse-875",
      "title": "Data Warehouse",
      "path": [
        "10 — System Design",
        "10.13 Data Processing"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--iaas-paas-saas-876",
      "title": "IaaS / PaaS / SaaS",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--aws-gcp-azure-concepts-877",
      "title": "AWS / GCP / Azure Concepts",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--containers-docker-878",
      "title": "Containers (Docker)",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--kubernetes-879",
      "title": "Kubernetes",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--ci-cd-880",
      "title": "CI / CD",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--infrastructure-as-code-881",
      "title": "Infrastructure as Code",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--terraform-882",
      "title": "Terraform",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--service-mesh-883",
      "title": "Service Mesh",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1014-cloud-and-infrastructure--container-orchestration-884",
      "title": "Container Orchestration",
      "path": [
        "10 — System Design",
        "10.14 Cloud & Infrastructure"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-url-shortener-885",
      "title": "Design URL Shortener",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-whatsapp-886",
      "title": "Design WhatsApp",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-twitter-887",
      "title": "Design Twitter",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-instagram-888",
      "title": "Design Instagram",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-youtube-889",
      "title": "Design YouTube",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-netflix-890",
      "title": "Design Netflix",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-uber-891",
      "title": "Design Uber",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-payment-system-892",
      "title": "Design Payment System",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-notification-system-893",
      "title": "Design Notification System",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-search-engine-894",
      "title": "Design Search Engine",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-file-storage-google-drive-895",
      "title": "Design File Storage (Google Drive)",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-e-commerce-system-896",
      "title": "Design E-commerce System",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-ticket-booking-system-897",
      "title": "Design Ticket Booking System",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-rate-limiter-898",
      "title": "Design Rate Limiter",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-distributed-job-scheduler-899",
      "title": "Design Distributed Job Scheduler",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "1015-common-system-design-interview-problems--design-logging-system-900",
      "title": "Design Logging System",
      "path": [
        "10 — System Design",
        "10.15 Common System Design Interview Problems"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--clean-code-901",
      "title": "Clean Code",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--refactoring-902",
      "title": "Refactoring",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--code-smells-903",
      "title": "Code Smells",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--technical-debt-904",
      "title": "Technical Debt",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--defensive-programming-905",
      "title": "Defensive Programming",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--error-handling-906",
      "title": "Error Handling",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--logging-907",
      "title": "Logging",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--unit-testing-908",
      "title": "Unit Testing",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--integration-testing-909",
      "title": "Integration Testing",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--end-to-end-testing-910",
      "title": "End-to-End Testing",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--test-driven-development-tdd-911",
      "title": "Test-Driven Development (TDD)",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--behavior-driven-development-bdd-912",
      "title": "Behavior-Driven Development (BDD)",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--test-doubles-913",
      "title": "Test Doubles",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": true
    },
    {
      "id": "a-software-engineering-practices--mocks-914",
      "title": "Mocks",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices",
        "Test Doubles"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--stubs-915",
      "title": "Stubs",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices",
        "Test Doubles"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--fakes-916",
      "title": "Fakes",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices",
        "Test Doubles"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--code-review-917",
      "title": "Code Review",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--version-control-git-918",
      "title": "Version Control (Git)",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "a-software-engineering-practices--ci-cd-919",
      "title": "CI / CD",
      "path": [
        "Supporting Foundations",
        "A. Software Engineering Practices"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--process-vs-thread-920",
      "title": "Process vs Thread",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--process-scheduling-921",
      "title": "Process Scheduling",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--context-switching-922",
      "title": "Context Switching",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--user-mode-vs-kernel-mode-923",
      "title": "User Mode vs Kernel Mode",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--memory-management-924",
      "title": "Memory Management",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--virtual-memory-925",
      "title": "Virtual Memory",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--stack-vs-heap-926",
      "title": "Stack vs Heap",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--mutex-semaphore-927",
      "title": "Mutex / Semaphore",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--inter-process-communication-ipc-928",
      "title": "Inter-Process Communication (IPC)",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--cpu-bound-vs-i-o-bound-929",
      "title": "CPU-bound vs I/O-bound",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--deadlocks-930",
      "title": "Deadlocks",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--race-conditions-931",
      "title": "Race Conditions",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--file-descriptors-932",
      "title": "File Descriptors",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "b-operating-systems-fundamentals--system-calls-933",
      "title": "System Calls",
      "path": [
        "Supporting Foundations",
        "B. Operating Systems Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--osi-model-934",
      "title": "OSI Model",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--tcp-ip-model-935",
      "title": "TCP/IP Model",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--ip-addressing-936",
      "title": "IP Addressing",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--subnetting-937",
      "title": "Subnetting",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--tcp-handshake-938",
      "title": "TCP Handshake",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--connection-lifecycle-939",
      "title": "Connection Lifecycle",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--dns-940",
      "title": "DNS",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--tls-941",
      "title": "TLS",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--http-internals-942",
      "title": "HTTP Internals",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--keep-alive-943",
      "title": "Keep-Alive",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--connection-pooling-944",
      "title": "Connection Pooling",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--socket-programming-945",
      "title": "Socket Programming",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "c-computer-networking-fundamentals--routing-basics-946",
      "title": "Routing Basics",
      "path": [
        "Supporting Foundations",
        "C. Computer Networking Fundamentals"
      ],
      "hasChildren": false
    },
    {
      "id": "ood-vs-poeaa-vs-ddd--ood-focuses-on-designing-objects-responsibilities-rela-947",
      "title": "**OOD** focuses on designing objects, responsibilities, relationships, and reusable design.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "OOD vs PoEAA vs DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "ood-vs-poeaa-vs-ddd--poeaa-provides-patterns-for-implementing-enterprise-appl-948",
      "title": "**PoEAA** provides patterns for implementing enterprise application logic, persistence, presentation, distribution, and concurrency.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "OOD vs PoEAA vs DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "ood-vs-poeaa-vs-ddd--ddd-focuses-on-understanding-and-modeling-complex-busine-949",
      "title": "**DDD** focuses on understanding and modeling complex business domains and defining meaningful domain boundaries.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "OOD vs PoEAA vs DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "ood-vs-poeaa-vs-ddd--these-areas-complement-one-another-none-is-a-direct-replace-950",
      "title": "These areas complement one another; none is a direct replacement for the others.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "OOD vs PoEAA vs DDD"
      ],
      "hasChildren": false
    },
    {
      "id": "application-architecture-vs-presentation-architecture--application-architecture-organizes-the-application-as-a-951",
      "title": "**Application Architecture** organizes the application as a whole: modules, layers, dependencies, boundaries, and infrastructure.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Application Architecture vs Presentation Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "application-architecture-vs-presentation-architecture--presentation-architecture-organizes-the-ui-layer-views-952",
      "title": "**Presentation Architecture** organizes the UI layer: views, presenters, view models, state, rendering, and user interaction.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Application Architecture vs Presentation Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "application-architecture-vs-presentation-architecture--mvc-can-appear-in-both-discussions-because-it-can-be-studied-953",
      "title": "MVC can appear in both discussions because it can be studied at different levels and for different concerns.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Application Architecture vs Presentation Architecture"
      ],
      "hasChildren": false
    },
    {
      "id": "concurrency-vs-eip--concurrency-concerns-coordinating-tasks-and-accessing-sh-954",
      "title": "**Concurrency** concerns coordinating tasks and accessing shared resources safely, within a process or across distributed nodes.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Concurrency vs EIP"
      ],
      "hasChildren": false
    },
    {
      "id": "concurrency-vs-eip--eip-concerns-communication-and-integration-between-indep-955",
      "title": "**EIP** concerns communication and integration between independent applications or services through messages.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Concurrency vs EIP"
      ],
      "hasChildren": false
    },
    {
      "id": "concurrency-vs-eip--related-ideas-can-appear-in-both-areas-but-the-concepts-are-956",
      "title": "Related ideas can appear in both areas, but the concepts are not interchangeable.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Concurrency vs EIP"
      ],
      "hasChildren": false
    },
    {
      "id": "eip-vs-system-design--eip-focuses-on-message-based-integration-patterns-and-th-957",
      "title": "**EIP** focuses on message-based integration patterns and the mechanics of routing, transforming, constructing, and consuming messages.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "EIP vs System Design"
      ],
      "hasChildren": false
    },
    {
      "id": "eip-vs-system-design--system-design-uses-messaging-and-integration-as-part-of-958",
      "title": "**System Design** uses messaging and integration as part of a larger system, alongside storage, networking, scaling, reliability, security, and operations.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "EIP vs System Design"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--dsa-search-filtering-and-data-processing-problems-959",
      "title": "DSA: search, filtering, and data-processing problems.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--ood-product-order-payment-inventory-objects-and-responsi-960",
      "title": "OOD: Product, Order, Payment, Inventory objects and responsibilities.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--dbms-schema-transactions-indexes-and-concurrency-961",
      "title": "DBMS: schema, transactions, indexes, and concurrency.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--application-architecture-modules-layers-boundaries-and-d-962",
      "title": "Application Architecture: modules, layers, boundaries, and dependencies.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--presentation-architecture-ui-state-and-presentation-flow-963",
      "title": "Presentation Architecture: UI state and presentation flow.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--poeaa-repository-unit-of-work-service-layer-data-mapper-964",
      "title": "PoEAA: Repository, Unit of Work, Service Layer, Data Mapper.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--ddd-order-aggregate-bounded-contexts-domain-events-965",
      "title": "DDD: Order Aggregate, bounded contexts, domain events.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--concurrency-inventory-race-conditions-and-safe-task-executi-966",
      "title": "Concurrency: inventory race conditions and safe task execution.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--eip-order-payment-and-inventory-message-flows-967",
      "title": "EIP: Order, Payment, and Inventory message flows.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "suggested-practical-project--system-design-scaling-availability-observability-and-dis-968",
      "title": "System Design: scaling, availability, observability, and distributed deployment.",
      "path": [
        "Cross-Topic Relationships & Study Notes",
        "Suggested Practical Project"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--what-is-it-969",
      "title": "**What is it?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--what-problem-does-it-solve-970",
      "title": "**What problem does it solve?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--why-does-that-problem-happen-971",
      "title": "**Why does that problem happen?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--how-does-the-solution-work-972",
      "title": "**How does the solution work?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--when-should-it-be-used-973",
      "title": "**When should it be used?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--when-should-it-not-be-used-974",
      "title": "**When should it not be used?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--what-are-its-trade-offs-975",
      "title": "**What are its trade-offs?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--what-is-it-similar-to-and-how-is-it-different-976",
      "title": "**What is it similar to, and how is it different?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--how-can-it-be-implemented-in-python-977",
      "title": "**How can it be implemented in Python?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    },
    {
      "id": "recommended-study-strategy--where-can-it-appear-in-a-real-backend-system-978",
      "title": "**Where can it appear in a real backend system?**",
      "path": [
        "Recommended Study Strategy"
      ],
      "hasChildren": false
    }
  ],
  "mainTopics": [
    {
      "id": "roadmap-overview",
      "title": "Roadmap Overview",
      "childCount": 5,
      "conceptCount": 13
    },
    {
      "id": "01-problem-solving-and-data-structures-and-algorithms-dsa",
      "title": "01 — Problem Solving & Data Structures & Algorithms (DSA)",
      "childCount": 17,
      "conceptCount": 126
    },
    {
      "id": "02-dbms-and-data-management",
      "title": "02 — DBMS & Data Management",
      "childCount": 8,
      "conceptCount": 100
    },
    {
      "id": "03-object-oriented-design-ood",
      "title": "03 — Object-Oriented Design (OOD)",
      "childCount": 10,
      "conceptCount": 72
    },
    {
      "id": "04-application-architecture",
      "title": "04 — Application Architecture",
      "childCount": 5,
      "conceptCount": 51
    },
    {
      "id": "05-presentation-architecture",
      "title": "05 — Presentation Architecture",
      "childCount": 5,
      "conceptCount": 36
    },
    {
      "id": "06-patterns-of-enterprise-application-architecture-poeaa",
      "title": "06 — Patterns of Enterprise Application Architecture (PoEAA)",
      "childCount": 10,
      "conceptCount": 51
    },
    {
      "id": "07-domain-driven-design-ddd",
      "title": "07 — Domain-Driven Design (DDD)",
      "childCount": 6,
      "conceptCount": 36
    },
    {
      "id": "08-concurrency-patterns",
      "title": "08 — Concurrency Patterns",
      "childCount": 0,
      "conceptCount": 10
    },
    {
      "id": "09-enterprise-integration-patterns-eip",
      "title": "09 — Enterprise Integration Patterns (EIP)",
      "childCount": 0,
      "conceptCount": 10
    },
    {
      "id": "10-system-design",
      "title": "10 — System Design",
      "childCount": 19,
      "conceptCount": 218
    },
    {
      "id": "supporting-foundations",
      "title": "Supporting Foundations",
      "childCount": 3,
      "conceptCount": 46
    },
    {
      "id": "cross-topic-relationships-and-study-notes",
      "title": "Cross-Topic Relationships & Study Notes",
      "childCount": 5,
      "conceptCount": 22
    },
    {
      "id": "recommended-study-strategy",
      "title": "Recommended Study Strategy",
      "childCount": 0,
      "conceptCount": 10
    }
  ],
  "stats": {
    "sectionCount": 14,
    "conceptCount": 801,
    "headingCount": 107
  }
};
