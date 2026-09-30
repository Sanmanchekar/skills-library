# Data Structure & Algorithm Complexity Cheatsheet

Language-agnostic. Averages unless noted; "amortized" = occasional expensive resize.

| Structure | Access | Search | Insert | Delete | Notes |
|---|---|---|---|---|---|
| Dynamic array (list/vector/ArrayList/slice) | O(1) | O(n) | O(1) amortized at end, O(n) front/middle | O(n) (O(1) at end) | Cache-friendly; preallocate when size known |
| Linked list | O(n) | O(n) | O(1) given node | O(1) given node | Poor cache locality; rarely faster in practice |
| Hash map / hash set | — | O(1) avg, O(n) worst | O(1) avg | O(1) avg | Needs good hash; resize is O(n) |
| Balanced BST (TreeMap, std::map, BTreeMap, SortedDict) | O(log n) | O(log n) | O(log n) | O(log n) | Ordered iteration, range queries |
| Binary heap (priority queue) | O(1) peek | O(n) | O(log n) | O(log n) pop | Top-k, scheduling |
| Deque (ring buffer) | O(1) ends | O(n) | O(1) both ends | O(1) both ends | Queues, sliding windows |
| Trie | — | O(key length) | O(key length) | O(key length) | Prefix search; memory-heavy |
| B-tree / B+tree (DB indexes) | — | O(log n) | O(log n) | O(log n) | Range scans |
| Bloom filter | — | O(k) | O(k) | n/a | Probabilistic membership, no false negatives |

## Algorithms
| Algorithm | Time | Space |
|---|---|---|
| Binary search | O(log n) | O(1) |
| Comparison sort (merge/Tim/intro) | O(n log n) | O(n) / O(log n) |
| Counting/radix sort (bounded keys) | O(n + k) | O(n + k) |
| BFS / DFS | O(V + E) | O(V) |
| Dijkstra (binary heap) | O((V + E) log V) | O(V) |
| Top-k via heap | O(n log k) | O(k) |
| Two pointers / sliding window | O(n) | O(1) |
| Hash join | O(n + m) | O(min(n, m)) |
| Nested-loop join | O(n · m) | O(1) |

## Growth intuition (n = 1,000,000)
O(log n) ≈ 20 · O(n) = 1e6 · O(n log n) ≈ 2e7 · O(n²) = 1e12 (unusable) · O(2ⁿ) never.

## Security: algorithmic-complexity attacks
- **ReDoS**: nested quantifiers like `(a+)+`, `(.*)*` backtrack exponentially on crafted input. Avoid them on user input; use linear-time engines (RE2, Go `regexp`, Rust `regex`) or input length limits.
- **Hash flooding**: user-controlled keys can force worst-case O(n) hash lookups; most modern runtimes randomize hashes, but cap request payload sizes and key counts.
- **Unbounded input**: always cap page sizes, batch sizes, upload sizes, and recursion depth on user-controlled data.
