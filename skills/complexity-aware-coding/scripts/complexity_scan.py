#!/usr/bin/env python3
"""
complexity_scan.py — static scanner for common time/space complexity pitfalls in Python.

Usage:
    python complexity_scan.py <file_or_dir> [more paths...] [--strict]

Heuristic (AST-based): it flags likely problems for review, not proven bugs.
--strict exits with code 1 when any HIGH finding exists (for CI / pre-commit).
"""
import ast
import re
import sys
from pathlib import Path

ORM_READ = {"get", "filter", "exclude", "first", "last", "count", "exists", "aggregate", "all", "values", "values_list"}
ORM_WRITE = {"save", "delete", "create", "update", "update_or_create", "get_or_create", "refresh_from_db"}
LINEAR_LIST_METHODS = {"index", "remove", "count"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "request"}
HTTP_CLIENTS = {"requests", "httpx", "session", "client"}
SORT_FUNCS = {"sorted"}
REDOS = re.compile(r"\((?:[^()\\]|\\.)*[+*](?:[^()\\]|\\.)*\)[+*{]")


class Finding:
    def __init__(self, path, line, severity, message, fix):
        self.path, self.line, self.severity, self.message, self.fix = path, line, severity, message, fix

    def __str__(self):
        return f"{self.path}:{self.line}: [{self.severity}] {self.message}\n    fix: {self.fix}"


def attr_chain(node):
    """Return dotted names for a call target, e.g. User.objects.filter -> ['User','objects','filter']."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    elif isinstance(node, ast.Call):
        parts.extend(reversed(attr_chain(node.func)))
    return list(reversed(parts))


class Scanner(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.findings = []
        self.loop_depth = 0
        self.list_names = [set()]  # per-scope names assigned list-like values
        self.str_names = [set()]   # per-scope names assigned string literals

    def add(self, node, sev, msg, fix):
        self.findings.append(Finding(self.path, getattr(node, "lineno", 0), sev, msg, fix))

    # ---- scopes -------------------------------------------------------
    def _visit_function(self, node):
        for deco in node.decorator_list:
            name = attr_chain(deco.func if isinstance(deco, ast.Call) else deco)
            last = name[-1] if name else ""
            if last == "cache":
                self.add(node, "MEDIUM", f"@cache on '{node.name}' is unbounded (space grows O(distinct inputs))",
                         "use @lru_cache(maxsize=N) in long-running processes (web/Celery workers)")
            if last == "lru_cache" and isinstance(deco, ast.Call):
                for kw in deco.keywords:
                    if kw.arg == "maxsize" and isinstance(kw.value, ast.Constant) and kw.value.value is None:
                        self.add(node, "MEDIUM", f"@lru_cache(maxsize=None) on '{node.name}' is unbounded",
                                 "set a finite maxsize")
        saved_depth = self.loop_depth
        self.loop_depth = 0
        self.list_names.append(set())
        self.str_names.append(set())
        self.generic_visit(node)
        self.list_names.pop()
        self.str_names.pop()
        self.loop_depth = saved_depth

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    # ---- track simple types -------------------------------------------
    def visit_Assign(self, node):
        is_list = isinstance(node.value, (ast.List, ast.ListComp)) or (
            isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == "list")
        is_str = isinstance(node.value, (ast.Constant, ast.JoinedStr)) and (
            isinstance(node.value, ast.JoinedStr) or isinstance(node.value.value, str))
        for t in node.targets:
            if isinstance(t, ast.Name):
                (self.list_names[-1].add if is_list else self.list_names[-1].discard)(t.id)
                (self.str_names[-1].add if is_str else self.str_names[-1].discard)(t.id)
        self.generic_visit(node)

    # ---- loops ---------------------------------------------------------
    def _visit_loop(self, node):
        if self.loop_depth >= 1:
            self.add(node, "LOW", f"nested loop (depth {self.loop_depth + 1}) — likely O(n^{self.loop_depth + 1}) if both sides grow",
                     "if matching items, index one side in a dict/set for O(n+m)")
        # iterate the loop header outside the loop context, body inside
        for field in ("target", "iter", "test"):
            child = getattr(node, field, None)
            if child is not None:
                self.visit(child)
        self.loop_depth += 1
        for stmt in node.body:
            self.visit(stmt)
        self.loop_depth -= 1
        for stmt in node.orelse:
            self.visit(stmt)

    visit_For = _visit_loop
    visit_AsyncFor = _visit_loop
    visit_While = _visit_loop

    def _visit_comp(self, node):
        self.loop_depth += 1
        self.generic_visit(node)
        self.loop_depth -= 1

    visit_ListComp = _visit_comp
    visit_SetComp = _visit_comp
    visit_DictComp = _visit_comp
    visit_GeneratorExp = _visit_comp

    # ---- checks --------------------------------------------------------
    def visit_Compare(self, node):
        if self.loop_depth:
            for op, comp in zip(node.ops, node.comparators):
                if isinstance(op, (ast.In, ast.NotIn)):
                    if isinstance(comp, (ast.List, ast.ListComp)) or (
                            isinstance(comp, ast.Name) and comp.id in self.list_names[-1]):
                        self.add(node, "HIGH", "membership test on a list inside a loop — O(n) per check, O(n·m) total",
                                 "convert to a set once before the loop")
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if self.loop_depth and isinstance(node.op, ast.Add) and isinstance(node.target, ast.Name):
            if node.target.id in self.str_names[-1]:
                self.add(node, "MEDIUM", f"string '{node.target.id} +=' inside a loop — can be O(n^2)",
                         "collect parts in a list and ''.join() once")
        self.generic_visit(node)

    def visit_Await(self, node):
        if self.loop_depth:
            self.add(node, "MEDIUM", "await inside a loop runs sequentially — total latency O(n × call latency)",
                     "asyncio.gather with a Semaphore for bounded concurrency, or batch the call")
        self.generic_visit(node)

    def visit_Call(self, node):
        chain = attr_chain(node.func)
        last = chain[-1] if chain else ""
        in_loop = self.loop_depth > 0

        # list.pop(0) / insert(0, x)
        if last in ("pop", "insert") and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == 0:
            self.add(node, "HIGH" if in_loop else "MEDIUM", f".{last}(0) on a list is O(n)",
                     "use collections.deque (popleft/appendleft are O(1))")

        if in_loop:
            # ORM queries inside loops (N+1)
            if "objects" in chain and last in ORM_READ | ORM_WRITE:
                self.add(node, "HIGH", f"ORM call '{'.'.join(chain[-3:])}' inside a loop — N+1 queries",
                         "fetch once with filter(id__in=...)/select_related/prefetch_related, or bulk_create/bulk_update/update()")
            elif last in {"save", "delete", "refresh_from_db"} and len(chain) >= 2 and chain[0] not in {"os", "shutil", "self"}:
                self.add(node, "MEDIUM", f".{last}() inside a loop — likely one DB query per item",
                         "use bulk_update/bulk_create/queryset.update()/queryset.delete()")
            elif last in {"execute", "query", "scalars", "scalar"} and len(chain) >= 2 and chain[-2] in {"session", "cursor", "db", "conn", "connection"}:
                self.add(node, "HIGH", f"database '{'.'.join(chain[-2:])}' inside a loop — one round trip per item",
                         "batch with IN (...), executemany, or a single set-based query")
            # HTTP calls in loops
            elif last in HTTP_METHODS and chain and chain[0] in HTTP_CLIENTS:
                self.add(node, "MEDIUM", f"HTTP call '{'.'.join(chain)}' inside a loop — O(n × network latency)",
                         "use a batch endpoint or bounded concurrent requests")
            # Linear list methods
            if last in LINEAR_LIST_METHODS and len(chain) >= 2 and chain[-2] in self.list_names[-1]:
                self.add(node, "HIGH", f"list.{last}() inside a loop — O(n) per call",
                         "use a dict/set/Counter keyed lookup")
            # sorting inside loops
            if last in SORT_FUNCS or (last == "sort" and len(chain) >= 2):
                self.add(node, "MEDIUM", "sorting inside a loop — O(k · n log n)",
                         "sort once outside the loop, or use heapq/bisect for incremental order")
            # copying
            if last in {"deepcopy", "copy"} and chain and chain[0] in {"copy"}:
                self.add(node, "LOW", "copy inside a loop — O(size) time and memory per iteration",
                         "avoid copying or copy once outside the loop")

        # ReDoS-prone regex literals
        if chain and chain[0] == "re" and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str) and REDOS.search(node.args[0].value):
            self.add(node, "HIGH", f"regex {node.args[0].value!r} has nested quantifiers — ReDoS risk (exponential backtracking)",
                     "remove nested quantifiers, bound input length, or use the 're2'/'regex' timeout options")

        # reading whole files/responses into memory
        if last in {"readlines"}:
            self.add(node, "LOW", ".readlines() loads the entire file — O(file size) memory",
                     "iterate the file object line by line")

        self.generic_visit(node)

    def visit_Subscript(self, node):
        # slicing in loops: a[1:] copies
        if self.loop_depth and isinstance(node.slice, ast.Slice) and isinstance(node.ctx, ast.Load):
            if node.slice.lower is not None or node.slice.upper is not None:
                self.add(node, "LOW", "slice inside a loop copies O(k) elements each iteration",
                         "iterate with indices or itertools.islice")
        self.generic_visit(node)


def scan_file(path):
    try:
        tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    except (SyntaxError, UnicodeDecodeError) as e:
        return [Finding(path, getattr(e, "lineno", 0) or 0, "SKIP", f"could not parse: {e.__class__.__name__}", "n/a")]
    s = Scanner(str(path))
    s.visit(tree)
    return s.findings


def iter_py_files(paths):
    skip = {".venv", "venv", "node_modules", "migrations", ".git", "__pycache__", "site-packages"}
    for p in map(Path, paths):
        if p.is_file() and p.suffix == ".py":
            yield p
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if not skip.intersection(f.parts):
                    yield f


def main(argv):
    strict = "--strict" in argv
    paths = [a for a in argv if not a.startswith("--")]
    if not paths:
        print(__doc__)
        return 2
    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2, "SKIP": 3}
    findings = [f for p in iter_py_files(paths) for f in scan_file(p)]
    findings.sort(key=lambda f: (order[f.severity], f.path, f.line))
    for f in findings:
        print(f)
    counts = {k: sum(f.severity == k for f in findings) for k in order}
    print(f"\n{len(findings)} findings — HIGH {counts['HIGH']}, MEDIUM {counts['MEDIUM']}, LOW {counts['LOW']}")
    return 1 if strict and counts["HIGH"] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
