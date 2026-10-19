---
name: production-readiness
description: Run a go/no-go production readiness gate before a first launch or a major change. Grades every item pass / partial / fail / n-a from evidence found in the repo — testing, observability (logs, metrics, traces, dashboards, alerts), SLOs, runbook, on-call ownership, health probes, autoscaling and resource limits, backups and disaster recovery, security scanning, dependency and secret hygiene, and docs — then outputs a scorecard, a blocking-items list, and a GO / CONDITIONAL GO / NO-GO verdict. Triggered when the user says "production readiness review", "are we ready to launch", "go/no-go", "PRR", "launch checklist", or "is this service ready for prod".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# production-readiness

## When to use

- User says: "production readiness review", "PRR", "go/no-go", "launch checklist", "are we ready for prod"
- Before a service's first production traffic, a GA launch, or a major change (new region, 10x traffic, new datastore)
- After an incident revealed gaps and the team wants a re-baseline

## Grades

| Grade | Meaning |
|---|---|
| PASS | Evidence found in the repo (cite file:line) and it meets the bar |
| PARTIAL | Exists but incomplete (e.g. metrics but no alerts) |
| FAIL | Absent, or present but broken |
| N/A | Genuinely not applicable — state why (e.g. stateless → no backups) |
| UNVERIFIED | Lives outside the repo (cloud console, pager tool) — needs a human to confirm |

## Checklist

Each item is BLOCKING (B) or ADVISORY (A). Any B graded FAIL or UNVERIFIED → no GO.

| # | Area | Item | Evidence to look for | B/A |
|---|---|---|---|---|
| 1 | Testing | Unit + integration tests run in CI and gate merge | test dirs, CI workflow test job, required checks | B |
| 2 | Testing | Critical user path has e2e or contract coverage | e2e/, pact files | A |
| 3 | Testing | Load tested at target peak × headroom | load-test scripts + report | B for new high-traffic |
| 4 | Observability | Structured logs with request/trace ID, no PII | logger config, log calls | B |
| 5 | Observability | RED/USE metrics exported | metrics middleware, `/metrics` | B |
| 6 | Observability | Distributed tracing across service boundaries | OpenTelemetry SDK init, propagators | A |
| 7 | Observability | Dashboard for the service | dashboards-as-code JSON, links in README | A |
| 8 | Observability | Alerts on symptoms, each linked to a runbook | alert rules files, `runbook_url` labels | B |
| 9 | SLOs | SLIs + SLO targets defined, error budget policy | slo yaml, docs | B |
| 10 | Runbook | Runbook covers top failure modes + rollback | docs/runbook*, RUNBOOK.md | B |
| 11 | Ownership | Owning team + on-call rotation named | CODEOWNERS, service catalog file | B |
| 12 | Health | Liveness + readiness (+ startup) probes, readiness checks deps | k8s/Helm probes, `/healthz` `/readyz` | B |
| 13 | Health | Graceful shutdown on SIGTERM, drains in-flight work | signal handlers, `preStop`, grace period | B |
| 14 | Capacity | CPU/memory requests + limits set | manifests / task defs | B |
| 15 | Capacity | Autoscaling with sane min/max; min ≥ 2 for HA | HPA / scaling policy | A |
| 16 | Resilience | Timeouts, retries with backoff, circuit breakers on every downstream call | client config | B |
| 17 | Resilience | Disruption budget / multi-AZ spread | PDB, topology spread | A |
| 18 | Data | Backups automated, retention set, restore tested | IaC backup config, restore drill notes | B if stateful |
| 19 | Data | DR: RPO/RTO stated and achievable | DR doc | A |
| 20 | Data | Migrations backward-compatible and reversible | migration files | B if schema |
| 21 | Security | SAST + dependency (SCA) scan in CI | CI jobs (CodeQL, Semgrep, Dependabot, Trivy, etc.) | B |
| 22 | Security | Container/image scan, non-root, read-only FS where possible | Dockerfile `USER`, scan job | A |
| 23 | Security | Secrets from a secret manager; none committed | gitleaks/trufflehog scan, `.env*` in git | B |
| 24 | Security | AuthN/AuthZ on every non-public endpoint | middleware, route config | B |
| 25 | Deps | Lockfile committed, no EOL runtime, pinned base images | lockfiles, Dockerfile `FROM` | A |
| 26 | Deploy | Automated deploy with one-command rollback | CD config, deploy docs | B |
| 27 | Docs | README: what it does, how to run, config reference, API spec | README, OpenAPI/proto | A |

## Steps

1. **Detect the service shape** — HTTP API, worker, cron, frontend, library; stateful or stateless; platform (k8s, serverless, VM, PaaS). Mark items N/A only from this shape, with a reason.
2. **Collect evidence** — grep/glob for each row's evidence; read the matching file before grading. Cite file:line.
3. **Grade** each row PASS / PARTIAL / FAIL / N/A / UNVERIFIED. No evidence → FAIL (not PASS by assumption).
4. **List blocking items** — every B row not PASS or N/A, with the concrete fix and an owner placeholder.
5. **Verdict**:
   - **GO** — all B rows PASS or N/A
   - **CONDITIONAL GO** — only UNVERIFIED B rows remain and a named human confirms them before launch
   - **NO-GO** — any B row FAIL or PARTIAL
6. **Score** — `PASS = 1, PARTIAL = 0.5, FAIL = 0` over applicable rows; report as a % (directional only, the verdict comes from blocking items).

## Example — input → output

Input: "Is `payments-api` ready for GA?" — repo has CI tests, Helm chart with probes, Prometheus metrics, no alert rules, no runbook, no CODEOWNERS.

```markdown
| # | Item | Grade | Evidence |
|---|---|---|---|
| 1 | Tests gate merge | PASS | .github/workflows/ci.yml:22 `pytest`, branch protection UNVERIFIED |
| 5 | Metrics exported | PASS | app/main.py:14 `Instrumentator().instrument(app)` |
| 8 | Alerts + runbook links | FAIL | no alert rules found (searched *.rules.yml, alerts/, helm/templates) |
| 10 | Runbook | FAIL | no runbook files |
| 11 | Owner + on-call | FAIL | no CODEOWNERS, no catalog file |
| 12 | Probes | PARTIAL | helm/templates/deployment.yaml:48 liveness only, no readiness |

**Verdict: NO-GO** — 4 blocking items.
```

## Output format

```markdown
# Production readiness — <service> — <date>

**Shape**: <HTTP API | worker | cron | frontend> · <stateful | stateless> · <platform>
**Verdict**: GO | CONDITIONAL GO | NO-GO
**Score**: <n>% (<pass>/<applicable> applicable items; directional only)

## Scorecard
| # | Area | Item | B/A | Grade | Evidence (file:line) |
|---|---|---|---|---|---|

## Blocking items
| # | Item | Gap | Fix | Owner |
|---|---|---|---|---|
| 8 | Alerts | no alert rules | add symptom alerts on 5xx rate + p99, each with runbook_url | ⚠️ ACTION REQUIRED |

## Needs human confirmation (UNVERIFIED)
- <item> — confirm in <system> — ask <role>

## Advisory improvements
- <item> — <fix>
```

## Rules

- NEVER grade PASS without citing file:line evidence you actually read
- NEVER grade by assumption — missing evidence is FAIL, outside-the-repo evidence is UNVERIFIED
- NEVER mark N/A without a one-line reason tied to the service shape
- NEVER issue GO with any blocking item FAIL, PARTIAL, or unconfirmed UNVERIFIED
- NEVER let the % score override the verdict — blocking items decide
- NEVER invent owners, dashboards, or on-call rotations — use `⚠️ ACTION REQUIRED`
- ALWAYS give each blocking item a concrete fix, not "improve observability"
- ALWAYS re-run the gate after fixes rather than editing grades by hand

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: ship · **Agent**: `ship`
- **Reads**: `slo`, `runbook`, `dashboards`, `tests` (from `.lifecycle/<run>/` when present)
- **Writes**: `readiness` → `readiness.md`
- **Comes after**: load-testing, release-notes
- **Hand off to**:
  - `deploy-plan` — always

When the step is done, record it so the next skill can pick up the output:
`route.py run record production-readiness --artifact readiness=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
