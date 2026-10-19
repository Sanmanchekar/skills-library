#!/usr/bin/env python3
"""lifecycle-router — decide which skill runs now, and which runs next.

Stdlib only (Python 3.8+). Reads the registry generated from lifecycle/graph.yaml.

  route.py route  [--prompt TEXT] [--paths P ...] [--event E] [--base REF | --staged]
  route.py next   --after SKILL [--paths ...] [--base REF | --staged]
  route.py fanout [--paths ...] [--base REF | --staged] [--markdown]   (@verify reviewers for a diff)
  route.py run    start [--name NAME] | status | record SKILL [--artifact TYPE=PATH ...]
  route.py loop   tick LOOP [--metric N] | status LOOP
  route.py hook   < claude-code-hook.json        (never blocks, always exits 0)

Exit codes: 0 ok · 2 bad input · 3 nothing matched (route/next only).
"""
from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY = os.path.join(HERE, "..", "references", "registry.json")
SEVERITY = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Scoring weights. Intents are the strongest signal (the user said it); an
# `always_on` event is a standing rule, so it outranks everything.
W_INTENT, W_INTENT_EXTRA = 3, 1
W_PATH, W_CONTENT, W_EVENT, W_ALWAYS = 2, 2, 2, 5
HINT_THRESHOLD = 3  # minimum score before a hook bothers the agent


def die(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(msg, file=sys.stderr)
    sys.exit(2)


# ── registry & git ────────────────────────────────────────────────────────────
def load_registry(path: Optional[str] = None) -> Dict[str, Any]:
    path = path or os.environ.get("LIFECYCLE_REGISTRY") or DEFAULT_REGISTRY
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _git(args: List[str], cwd: Optional[str] = None) -> str:
    try:
        out = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=15)
        return out.stdout if out.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def repo_root(cwd: Optional[str] = None) -> str:
    return _git(["rev-parse", "--show-toplevel"], cwd).strip() or os.path.abspath(cwd or os.getcwd())


def default_base(cwd: Optional[str] = None) -> str:
    ref = _git(["symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"], cwd).strip()
    return ref or "main"


def collect_change(base: Optional[str], staged: bool, cwd: Optional[str] = None) -> Tuple[List[str], List[str]]:
    """Return (changed paths, added lines) for the working change."""
    if staged:
        specs = [["--cached"]]
    else:
        base = base or default_base(cwd)
        specs = [[f"{base}...HEAD"], ["--cached"], []]  # committed + staged + unstaged
    paths, added = set(), []
    for spec in specs:
        paths.update(p for p in _git(["diff", "--name-only"] + spec, cwd).splitlines() if p)
        for line in _git(["diff", "-U0", "--no-color"] + spec, cwd).splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:])
    return sorted(paths), added


# ── matching ──────────────────────────────────────────────────────────────────
def glob_match(path: str, pattern: str) -> bool:
    # fnmatch's `*` already crosses `/`; prefixing `/` lets `**/x` match a top-level `x`.
    return fnmatch.fnmatch(path, pattern) or fnmatch.fnmatch("/" + path, pattern)


def _rx(pattern: str) -> "re.Pattern[str]":
    return re.compile(pattern, re.IGNORECASE)


def score_node(name: str, node: Dict[str, Any], ctx: Dict[str, Any]) -> Tuple[int, List[str]]:
    t = node.get("triggers", {})
    score, why = 0, []
    prompt = ctx.get("prompt") or ""
    if prompt:
        hits = [p for p in t.get("intents", []) if _rx(p).search(prompt)]
        if hits:
            score += W_INTENT + W_INTENT_EXTRA * (len(hits) - 1)
            why.append(f"prompt matches /{hits[0]}/")
    paths = ctx.get("paths") or []
    if paths and t.get("paths"):
        hit = [p for p in paths if any(glob_match(p, g) for g in t["paths"])]
        if hit:
            score += W_PATH
            why.append(f"{len(hit)} file(s) match, e.g. {hit[0]}")
    added = ctx.get("added") or []
    if added and t.get("content"):
        for pat in t["content"]:
            rx = _rx(pat)
            line = next((ln for ln in added if rx.search(ln)), None)
            if line is not None:
                score += W_CONTENT
                why.append(f"diff adds /{pat}/: {line.strip()[:60]}")
                break
    event = ctx.get("event")
    if event:
        if event in t.get("always_on", []):
            score += W_ALWAYS
            why.append(f"always runs on {event}")
        elif event in t.get("events", []):
            score += W_EVENT
            why.append(f"listens for {event}")
    return score, why


def _review_rank(reg: Dict[str, Any], name: str) -> int:
    order = reg.get("conflicts", {}).get("review_order", [])
    return order.index(name) if name in order else len(order)


def rank(reg: Dict[str, Any], ctx: Dict[str, Any], phase: Optional[str] = None) -> List[Dict[str, Any]]:
    out = []
    for name, node in reg["nodes"].items():
        if phase and node["phase"] != phase:
            continue
        s, why = score_node(name, node, ctx)
        if s > 0:
            out.append({"skill": name, "phase": node["phase"], "score": s, "why": why})
    out.sort(key=lambda r: (-r["score"], _review_rank(reg, r["skill"]), r["skill"]))
    return out


def expand_verify(reg: Dict[str, Any], ctx: Dict[str, Any]) -> List[Dict[str, Any]]:
    """`@verify` fan-out: every reviewer whose own path/content triggers match the diff."""
    diff_ctx = {"paths": ctx.get("paths"), "added": ctx.get("added")}
    order = reg.get("conflicts", {}).get("review_order", [])
    picked = []
    for name in order:
        s, why = score_node(name, reg["nodes"][name], diff_ctx)
        if s > 0 or name == "code-review":
            picked.append({"skill": name, "score": s, "why": why or ["general reviewer, always last"]})
    return picked


# ── edges ─────────────────────────────────────────────────────────────────────
def findings_max_severity(run_dir: Optional[str]) -> Optional[str]:
    if not run_dir:
        return None
    path = os.path.join(run_dir, "findings.json")
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError):
        return None
    sev = [f.get("severity", "LOW").upper() for f in data.get("findings", []) if f.get("status", "open") == "open"]
    sev = [s for s in sev if s in SEVERITY]
    return max(sev, key=SEVERITY.index) if sev else None


def eval_when(when: Any, ctx: Dict[str, Any], manifest: Optional[Dict[str, Any]], run_dir: Optional[str]) -> Tuple[str, str]:
    """Return (verdict, detail): verdict ∈ ready | blocked | ask."""
    if when in (None, "always"):
        return "ready", "always"
    if "ask" in when:
        return "ask", when["ask"]
    if "paths" in when:
        paths = ctx.get("paths") or []
        hit = [p for p in paths if any(glob_match(p, g) for g in when["paths"])]
        return ("ready", f"changed files match ({hit[0]})") if hit else ("blocked", "no changed file matches")
    if "content" in when:
        added = ctx.get("added") or []
        for pat in when["content"]:
            if any(_rx(pat).search(ln) for ln in added):
                return "ready", f"diff matches /{pat}/"
        return "blocked", "diff does not match"
    if "artifact" in when:
        have = (manifest or {}).get("artifacts", {})
        return ("ready", f"artifact {when['artifact']} present") if when["artifact"] in have else ("blocked", f"no {when['artifact']} artifact yet")
    if "findings_at_least" in when:
        need = when["findings_at_least"].upper()
        top = findings_max_severity(run_dir)
        ok = top is not None and SEVERITY.index(top) >= SEVERITY.index(need)
        return ("ready", f"open findings reach {top}") if ok else ("blocked", f"no open {need}+ findings")
    return "blocked", f"unknown condition {when!r}"


def next_steps(reg: Dict[str, Any], after: str, ctx: Dict[str, Any], manifest=None, run_dir=None) -> List[Dict[str, Any]]:
    out = []
    for e in reg["edges"]:
        if e["from"] != after:
            continue
        verdict, detail = eval_when(e.get("when"), ctx, manifest, run_dir)
        if e["to"] == "@verify":
            for r in expand_verify(reg, ctx):
                out.append({"skill": r["skill"], "verdict": verdict, "detail": "; ".join(r["why"]), "via": "@verify"})
        else:
            out.append({"skill": e["to"], "verdict": verdict, "detail": detail})
    order = {"ready": 0, "ask": 1, "blocked": 2}
    out.sort(key=lambda r: (order[r["verdict"]], _review_rank(reg, r["skill"])))
    return out


# ── runs (hand-off contract) ──────────────────────────────────────────────────
def lifecycle_dir(cwd: Optional[str] = None) -> str:
    return os.path.join(repo_root(cwd), ".lifecycle")


def current_run(cwd: Optional[str] = None) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    base = lifecycle_dir(cwd)
    try:
        with open(os.path.join(base, "CURRENT"), encoding="utf-8") as fh:
            run_id = fh.read().strip()
        run_dir = os.path.join(base, run_id)
        with open(os.path.join(run_dir, "manifest.json"), encoding="utf-8") as fh:
            return run_dir, json.load(fh)
    except (OSError, ValueError):
        return None, None


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def save_manifest(run_dir: str, manifest: Dict[str, Any]) -> None:
    tmp = os.path.join(run_dir, ".manifest.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    os.replace(tmp, os.path.join(run_dir, "manifest.json"))


def run_start(name: Optional[str], cwd: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    base = lifecycle_dir(cwd)
    slug = re.sub(r"[^a-z0-9]+", "-", (name or "run").lower()).strip("-")[:40] or "run"
    run_id = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + slug
    run_dir = os.path.join(base, run_id)
    os.makedirs(run_dir, exist_ok=True)
    gitignore = os.path.join(base, ".gitignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "w", encoding="utf-8") as fh:
            fh.write("# lifecycle runs are local working state\n*\n")
    manifest = {"run_id": run_id, "name": name or "", "created": _now(), "steps": [], "artifacts": {}, "loops": {}}
    save_manifest(run_dir, manifest)
    with open(os.path.join(base, "CURRENT"), "w", encoding="utf-8") as fh:
        fh.write(run_id + "\n")
    return run_dir, manifest


def run_record(reg, skill: str, artifacts: List[str], cwd=None) -> Dict[str, Any]:
    if skill not in reg["nodes"]:
        die(f"unknown skill: {skill}")
    run_dir, manifest = current_run(cwd)
    if manifest is None:
        run_dir, manifest = run_start(skill, cwd)
    recorded = {}
    for spec in artifacts:
        if "=" not in spec:
            die(f"--artifact must be TYPE=PATH, got {spec!r}")
        kind, path = spec.split("=", 1)
        if kind not in reg["artifacts"]:
            die(f"unknown artifact type {kind!r}; known: {', '.join(sorted(reg['artifacts']))}")
        recorded[kind] = path
        manifest["artifacts"][kind] = {"path": path, "by": skill, "at": _now()}
    manifest["steps"].append({"skill": skill, "at": _now(), "artifacts": recorded})
    save_manifest(run_dir, manifest)
    return manifest


# ── loops (guardrails) ────────────────────────────────────────────────────────
def loop_tick(reg, loop: str, metric: Optional[float], cwd=None) -> Dict[str, Any]:
    spec = reg["loops"].get(loop)
    if spec is None:
        die(f"unknown loop {loop!r}; known: {', '.join(sorted(reg['loops']))}")
    run_dir, manifest = current_run(cwd)
    if manifest is None:
        run_dir, manifest = run_start(loop, cwd)
    st = manifest["loops"].setdefault(loop, {"iteration": 0, "history": [], "stalled": 0, "state": "running"})
    if st["state"] != "running":
        return {"loop": loop, "decision": "stop", "reason": f"loop already {st['state']}", **st}
    st["iteration"] += 1
    prev = st["history"][-1] if st["history"] else None
    st["history"].append(metric)
    if metric is not None and prev is not None and metric >= prev:
        st["stalled"] += 1
    elif metric is not None:
        st["stalled"] = 0

    if metric is not None and metric <= 0:
        decision, reason, st["state"] = "exit", f"metric {spec.get('metric')} reached 0 — confirm: {spec['exit']}", "done"
    elif st["iteration"] >= spec["max_iterations"]:
        decision, reason, st["state"] = "stop", f"hit max_iterations={spec['max_iterations']} — hand back to the human", "capped"
    elif st["stalled"] >= spec.get("no_progress", 2):
        decision, reason, st["state"] = "stop", f"no progress on {spec.get('metric')} for {st['stalled']} ticks — change approach or escalate", "stalled"
    else:
        decision, reason = "continue", f"iteration {st['iteration']}/{spec['max_iterations']}"
    checkpoint = spec.get("checkpoint") == "each_iteration" or (spec.get("checkpoint") == "on_exit" and decision != "continue")
    save_manifest(run_dir, manifest)
    return {"loop": loop, "decision": decision, "reason": reason, "checkpoint": checkpoint,
            "exit_criteria": spec["exit"], "iteration": st["iteration"], "history": st["history"]}


# ── optional judge for ambiguous prompts ──────────────────────────────────────
def judge_with_jev(prompt: str, candidates: List[Dict[str, Any]], reg: Dict[str, Any]) -> Optional[str]:
    """Break an intent tie with the `jev` CLI when LIFECYCLE_JUDGE=jev. Any failure = no verdict."""
    if os.environ.get("LIFECYCLE_JUDGE") != "jev" or len(candidates) < 2:
        return None
    crit = {c["skill"]: reg["nodes"][c["skill"]].get("summary", c["skill"]) for c in candidates[:4]}
    req = {"state": {"prompt": prompt},
           "questions": {"skill": {"type": "choice",
                                   "instructions": "Which engineering skill should handle the request in `prompt`?",
                                   "criteria": crit}}}
    try:
        out = subprocess.run(["jev"], input=json.dumps(req), capture_output=True, text=True, timeout=20)
        if out.returncode != 0:
            return None
        ans = json.loads(out.stdout).get("skill", {})
        if ans.get("confidence", 0) < 0.6:
            return None
        return ans.get("value") if ans.get("value") in crit else None
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


# ── route ─────────────────────────────────────────────────────────────────────
def route(reg, ctx, limit: Optional[int] = None) -> Dict[str, Any]:
    ranked = rank(reg, ctx)
    limit = limit or reg.get("conflicts", {}).get("max_parallel", 4)
    if ctx.get("prompt") and len(ranked) > 1 and ranked[0]["score"] == ranked[1]["score"]:
        tied = [r for r in ranked if r["score"] == ranked[0]["score"]]
        pick = judge_with_jev(ctx["prompt"], tied, reg)
        if pick:
            ranked.sort(key=lambda r: r["skill"] != pick)
            ranked[0]["why"].append("tie broken by jev")
    if not ranked:
        return {"matched": False, "skills": [], "also": []}
    top = ranked[0]
    agent = next((a for a, spec in reg["agents"].items() if top["skill"] in spec["owns"]), top["phase"])
    loop = reg["agents"].get(agent, {}).get("loop")
    run_dir, manifest = current_run(ctx.get("cwd"))
    return {
        "matched": True,
        "phase": top["phase"],
        "agent": f"lifecycle-{agent}",
        "loop": loop,
        "skills": ranked[:limit],
        "also": [r["skill"] for r in ranked[limit:]],
        "next": next_steps(reg, top["skill"], ctx, manifest, run_dir),
        "disambiguate": [d for d in reg.get("conflicts", {}).get("disambiguate", [])
                         if len({r["skill"] for r in ranked[:limit]} & set(d["pair"])) == 2],
    }


def fmt_route(res: Dict[str, Any]) -> str:
    if not res["matched"]:
        return "No skill matched. Ask what phase the work is in (plan/build/verify/ship/operate/learn/maintain)."
    lines = [f"phase: {res['phase']} · agent: {res['agent']}" + (f" · loop: {res['loop']}" if res["loop"] else "")]
    for i, r in enumerate(res["skills"], 1):
        lines.append(f"  {i}. {r['skill']}  (score {r['score']}: {'; '.join(r['why'])})")
    if res["also"]:
        lines.append("  also matched: " + ", ".join(res["also"]))
    for d in res.get("disambiguate", []):
        lines.append(f"  ⚖ {' vs '.join(d['pair'])}: {d['rule']}")
    if res.get("next"):
        lines.append("next after " + res["skills"][0]["skill"] + ":")
        lines += [f"  - {n['skill']} [{n['verdict']}] {n['detail']}" for n in res["next"][:8]]
    return "\n".join(lines)


def fmt_fanout_md(picks: List[Dict[str, Any]], ctx: Dict[str, Any]) -> str:
    esc = lambda t: t.replace("|", "\\|")  # noqa: E731
    rows = "\n".join(f"| {i} | `{r['skill']}` | {esc('; '.join(r['why']))} |" for i, r in enumerate(picks, 1))
    return ("<!-- lifecycle-router:fanout -->\n### Lifecycle router — reviewers for this PR\n\n"
            f"{len(ctx.get('paths') or [])} changed file(s). Run these skills in order (most specific first, "
            "`code-review` last), merging findings into one report:\n\n"
            "| # | Skill | Why |\n|---|---|---|\n" + rows +
            "\n\n<sub>Generated by the lifecycle-router skill. Advisory only — nothing is blocked.</sub>")


# ── Claude Code hook ──────────────────────────────────────────────────────────
_SEEN_DIR = os.path.join(tempfile.gettempdir(), "lifecycle-router")


def _seen(session: str, key: str) -> bool:
    """True if this hint was already given this session (each hint fires once)."""
    os.makedirs(_SEEN_DIR, exist_ok=True)
    path = os.path.join(_SEEN_DIR, re.sub(r"[^A-Za-z0-9_-]", "_", session or "nosession") + ".txt")
    try:
        with open(path, encoding="utf-8") as fh:
            if key in fh.read().splitlines():
                return True
    except OSError:
        pass
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(key + "\n")
    return False


BASH_EVENTS = [
    (re.compile(r"\bgit\s+commit\b"), "pre-commit", True),
    (re.compile(r"\bgh\s+pr\s+create\b"), "pr-opened", False),
    (re.compile(r"\b(terraform\s+apply|helm\s+(upgrade|install)|kubectl\s+apply|kubectl\s+rollout)\b"), "pre-deploy", False),
]


def hook(reg, payload: Dict[str, Any]) -> Optional[str]:
    ev = payload.get("hook_event_name")
    cwd = payload.get("cwd")
    session = payload.get("session_id", "")
    if ev == "UserPromptSubmit":
        prompt = (payload.get("prompt") or "").strip()
        if not prompt or prompt.startswith("/"):
            return None
        res = route(reg, {"prompt": prompt, "cwd": cwd}, limit=3)
        if not res["matched"] or res["skills"][0]["score"] < HINT_THRESHOLD:
            return None
        names = ", ".join(r["skill"] for r in res["skills"])
        return (f"[lifecycle-router] This request looks like {res['phase']} work. Consider these skills: {names}"
                f" — top: {res['skills'][0]['skill']} ({'; '.join(res['skills'][0]['why'])})."
                + (f" Run it inside the `{res['loop']}` loop (route.py loop tick {res['loop']})." if res["loop"] else ""))
    if ev == "PreToolUse" and payload.get("tool_name") == "Bash":
        cmd = (payload.get("tool_input") or {}).get("command", "")
        for rx, event, staged in BASH_EVENTS:
            if rx.search(cmd):
                paths, added = collect_change(None, staged, cwd)
                ctx = {"event": event, "paths": paths, "added": added, "cwd": cwd}
                picks = [r for r in rank(reg, ctx) if r["score"] >= HINT_THRESHOLD]
                if event == "pr-opened":
                    picks = [{"skill": r["skill"], "why": r["why"]} for r in expand_verify(reg, ctx)] + picks
                names, seen = [], set()
                for p in picks:
                    if p["skill"] not in seen:
                        seen.add(p["skill"]); names.append(p["skill"])
                key = f"{event}:{','.join(names)}"
                if not names or _seen(session, key):
                    return None
                return (f"[lifecycle-router] `{event}` — before this runs, apply: {', '.join(names[:6])}"
                        + (f" (+{len(names) - 6} more)" if len(names) > 6 else "")
                        + ". This is a hint, not a gate; the command is not blocked.")
        return None
    if ev == "PostToolUse" and payload.get("tool_name") in ("Edit", "Write", "MultiEdit"):
        ti = payload.get("tool_input") or {}
        path = ti.get("file_path", "")
        root = repo_root(cwd)
        rel = os.path.relpath(path, root) if path.startswith(root) else path
        text = ti.get("new_string") or ti.get("content") or "\n".join(e.get("new_string", "") for e in ti.get("edits", []))
        ctx = {"paths": [rel], "added": text.splitlines()[:400], "cwd": cwd, "event": "edit"}
        picks = [r for r in rank(reg, ctx) if r["phase"] in ("build", "verify") and r["score"] >= HINT_THRESHOLD]
        fresh = [r for r in picks if not _seen(session, f"edit:{r['skill']}")]
        if not fresh:
            return None
        return ("[lifecycle-router] The edit to " + rel + " touches: "
                + "; ".join(f"{r['skill']} ({r['why'][0]})" for r in fresh[:3])
                + ". Apply those rules before moving on.")
    return None


# ── CLI ───────────────────────────────────────────────────────────────────────
def _ctx_from_args(a) -> Dict[str, Any]:
    paths, added = (a.paths or []), []
    if not a.paths and (a.base or a.staged or a.git):
        paths, added = collect_change(a.base, a.staged)
    return {"prompt": getattr(a, "prompt", None), "paths": paths, "added": added, "event": getattr(a, "event", None)}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(prog="route.py", description=__doc__.split("\n")[0])
    ap.add_argument("--registry")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    # Accept --json after the subcommand too; SUPPRESS keeps a top-level --json from being reset.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def change_args(p):
        p.add_argument("--paths", nargs="*")
        p.add_argument("--base", help="diff against this ref (default: origin HEAD)")
        p.add_argument("--staged", action="store_true", help="use only the staged diff")
        p.add_argument("--git", action="store_true", help="read the change from git with the default base")

    p = sub.add_parser("route", parents=[common]); p.add_argument("--prompt"); p.add_argument("--event"); change_args(p)
    p.add_argument("--limit", type=int)
    p = sub.add_parser("next", parents=[common]); p.add_argument("--after", required=True); change_args(p)
    p = sub.add_parser("fanout", parents=[common]); change_args(p); p.add_argument("--markdown", action="store_true")
    p = sub.add_parser("run", parents=[common]); p.add_argument("action", choices=["start", "status", "record"])
    p.add_argument("skill", nargs="?"); p.add_argument("--name"); p.add_argument("--artifact", action="append", default=[])
    p = sub.add_parser("loop", parents=[common]); p.add_argument("action", choices=["tick", "status"]); p.add_argument("loop")
    p.add_argument("--metric", type=float)
    sub.add_parser("hook", parents=[common])

    a = ap.parse_args(argv)
    if a.cmd == "hook":
        # A hook must never break the session: swallow everything, exit 0.
        try:
            reg = load_registry(a.registry)
            payload = json.loads(sys.stdin.read() or "{}")
            msg = hook(reg, payload)
            if msg:
                print(json.dumps({"hookSpecificOutput": {"hookEventName": payload.get("hook_event_name"),
                                                         "additionalContext": msg}}))
        except Exception:  # noqa: BLE001 — deliberate: hooks are advisory
            pass
        return 0

    reg = load_registry(a.registry)
    emit = (lambda o, txt: print(json.dumps(o, indent=2) if a.json else txt))

    if a.cmd == "route":
        if not (a.prompt or a.paths or a.event or a.base or a.staged or a.git):
            print("route: give at least one of --prompt, --paths, --event, --base, --staged, --git", file=sys.stderr)
            return 2
        res = route(reg, _ctx_from_args(a), a.limit)
        emit(res, fmt_route(res))
        return 0 if res["matched"] else 3
    if a.cmd == "next":
        if a.after not in reg["nodes"]:
            print(f"unknown skill {a.after!r}", file=sys.stderr)
            return 2
        run_dir, manifest = current_run()
        steps = next_steps(reg, a.after, _ctx_from_args(a), manifest, run_dir)
        emit(steps, "\n".join(f"- {s['skill']} [{s['verdict']}] {s['detail']}" for s in steps) or "(terminal node)")
        return 0 if steps else 3
    if a.cmd == "fanout":
        a.git = a.git or not (a.paths or a.staged or a.base)
        ctx = _ctx_from_args(a)
        picks = expand_verify(reg, ctx)
        if a.markdown:
            print(fmt_fanout_md(picks, ctx))
        else:
            emit(picks, "\n".join(f"{i}. {r['skill']} — {'; '.join(r['why'])}" for i, r in enumerate(picks, 1)))
        return 0
    if a.cmd == "run":
        if a.action == "start":
            run_dir, m = run_start(a.name)
            emit(m, f"started {m['run_id']} → {run_dir}")
        elif a.action == "status":
            run_dir, m = current_run()
            if m is None:
                print("no current run — `route.py run start --name <task>`", file=sys.stderr)
                return 3
            emit(m, f"{m['run_id']}: {len(m['steps'])} step(s); artifacts: {', '.join(m['artifacts']) or 'none'}"
                    + "".join(f"\n  loop {k}: {v['state']} @ {v['iteration']}" for k, v in m["loops"].items()))
        else:
            if not a.skill:
                print("run record needs SKILL", file=sys.stderr)
                return 2
            m = run_record(reg, a.skill, a.artifact)
            emit(m, f"recorded {a.skill} in {m['run_id']}")
        return 0
    if a.cmd == "loop":
        if a.action == "tick":
            res = loop_tick(reg, a.loop, a.metric)
            emit(res, f"{res['decision'].upper()}: {res['reason']}" + ("\n⏸  checkpoint: confirm with the human before continuing" if res.get("checkpoint") else ""))
        else:
            _, m = current_run()
            st = (m or {}).get("loops", {}).get(a.loop)
            emit(st or {}, json.dumps(st) if st else f"loop {a.loop} not started")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
