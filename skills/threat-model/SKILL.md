---
name: threat-model
description: Design-time threat model for a feature, service, or architecture — inventories assets, entry points, and trust boundaries, draws the data-flow diagram, runs STRIDE per data-flow element (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege), writes abuse cases, and produces a threat register with mitigations, owners, and accepted residual risk. Works on a design doc or diagram before code exists; for reviewing an actual diff use security-review. Triggered when the user says "threat model this", "STRIDE analysis", "what could an attacker do here", "security design review", or shares an architecture/design doc and asks about attack surface.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# threat-model

## When to use

- User says: "threat model this", "STRIDE", "what's the attack surface", "what could an attacker do", "security design review"
- A design doc introduces a new entry point, trust boundary, data store, third-party integration, or privileged role
- Before building auth, payments, file upload, multi-tenancy, webhooks, admin tools, or anything handling PII
- NOT for reviewing a diff — that is `security-review`. This skill runs on the design, before or alongside code

## Method

1. **Scope** — name the system and the one question: "What are we building, what can go wrong, what will we do about it, did we do a good job?"
2. **Assets** — list what an attacker wants: data (PII, credentials, tokens, money movement), capabilities (admin actions, sending email), availability.
3. **Entry points** — every way in: public HTTP routes, webhooks, queues consumers, file uploads, admin consoles, CLIs, cron jobs, third-party callbacks. Grep routes/consumers if code exists.
4. **Data-flow diagram** — external entities, processes, data stores, data flows. Draw trust boundaries wherever privilege or ownership changes (internet → edge, service → DB, tenant A → tenant B, your code → vendor).
5. **STRIDE per element** — walk every element and every flow that crosses a boundary using the applicability table below. Write one threat per cell that applies.
6. **Abuse cases** — for each primary user story write "As an attacker, I want to … so that …". Prioritise ones touching assets from step 2.
7. **Rate** — likelihood (Low/Med/High) × impact (Low/Med/High) → risk. Use the matrix; do not invent scores.
8. **Mitigate** — each threat gets: control, owner, status (planned / in-design / done), and verification (test, config check, pentest item).
9. **Residual risk** — what remains after mitigation, and who explicitly accepted it.

## STRIDE applicability

| Element | S | T | R | I | D | E |
|---|---|---|---|---|---|---|
| External entity (user, vendor) | x | | x | | | |
| Process (service, worker) | x | x | x | x | x | x |
| Data store (DB, bucket, cache) | | x | x* | x | x | |
| Data flow (crosses a boundary) | | x | | x | x | |

\*Repudiation on a data store applies when it holds audit logs.

| Letter | Threat | Typical control |
|---|---|---|
| S | Spoofing identity | strong authn, mTLS, signed webhooks |
| T | Tampering | integrity checks, signatures, least-privilege writes |
| R | Repudiation | append-only audit log with actor + timestamp |
| I | Information disclosure | authz on every read, encryption, field-level redaction |
| D | Denial of service | rate limits, quotas, timeouts, bounded queues |
| E | Elevation of privilege | server-side authz, tenant scoping, no client-trusted roles |

## Risk matrix

| Likelihood ↓ / Impact → | Low | Med | High |
|---|---|---|---|
| High | Med | High | Critical |
| Med | Low | Med | High |
| Low | Low | Low | Med |

## Output format

````markdown
# Threat model — <system>

- **Version**: v1  **Date**: YYYY-MM-DD  **Design doc**: <link>

## Assets
| # | Asset | Why it matters |
## Entry points
| # | Entry point | Auth | Trust level |
## Data flow & trust boundaries
```mermaid
flowchart LR
```
## Threat register
| ID | Element | STRIDE | Threat | L | I | Risk | Mitigation | Owner | Status | Verification |
## Abuse cases
- AC1: As an attacker, I want to … so that …  → threats T1, T4
## Residual risk
| Threat | Remaining risk | Accepted by | Review date |
````

## Example

**Input**: "Design: `acme` storefront lets merchants upload product CSVs; `import-worker` parses them from an object-storage bucket and writes to `catalog-db`."

**Output (excerpt)**:

```markdown
## Entry points
| # | Entry point | Auth | Trust level |
|---|---|---|---|
| E1 | POST /imports (pre-signed upload URL) | merchant session | authenticated, untrusted content |
| E2 | bucket → import-worker event | IAM role | internal |

## Threat register
| ID | Element | STRIDE | Threat | L | I | Risk | Mitigation | Owner | Status | Verification |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 | E1 flow | E | Merchant A sets object key under merchant B's prefix | Med | High | High | Server generates key `merchants/{id}/{uuid}.csv`; worker re-checks prefix vs job owner | @catalog | planned | integration test |
| T2 | import-worker | D | 2 GB CSV / zip bomb exhausts worker memory | High | Med | High | 50 MB size cap on pre-signed URL; streaming parser; row limit | @catalog | planned | load test |
| T3 | CSV → admin export | T | Formula injection (`=HYPERLINK(...)`) re-exported to spreadsheets | Med | Med | Med | Prefix cells starting `= + - @` with `'` on export | @catalog | planned | unit test |
| T4 | catalog-db | R | No record of which merchant changed prices | Med | Med | Med | Audit row per import job: actor, file hash, row count | @catalog | in-design | query check |

## Abuse cases
- AC1: As a malicious merchant, I want to overwrite a competitor's catalog so that their prices break → T1
```

## Rules

- NEVER skip trust boundaries — a DFD without boundaries is just an architecture diagram
- NEVER leave a threat without a mitigation, an owner, or an explicit risk acceptance
- NEVER rate risk by gut — use the likelihood × impact matrix
- NEVER treat internal callers as trusted by default — say why a boundary is trusted
- ALWAYS cover every element crossing a boundary with the STRIDE applicability table
- ALWAYS give each mitigation a verification method so it can be checked later
- ALWAYS hand code-level checks to `security-review` once the implementation exists

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: plan · **Agent**: `plan` · **Loop**: `design`
- **Reads**: `design` (from `.lifecycle/<run>/` when present)
- **Writes**: `threat-model` → `threat-model.md`
- **Comes after**: tech-design
- **Hand off to**:
  - `estimation` — always

This skill works on its own; the hand-offs above are suggestions. If the `lifecycle-router` skill is installed, record the step so the next skill can pick up the output: `route.py run record threat-model --artifact threat-model=<path>`. If it is not installed, skip this and just name the next skill to the user.
<!-- lifecycle:end -->
