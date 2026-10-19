---
name: cost-review
description: Review the cloud cost of a service or an infrastructure-as-code change. Inspects cost drivers (compute right-sizing, idle resources, storage tiering and lifecycle, data transfer and NAT egress, log and metric cardinality, managed-service tiers), checks tagging and cost attribution, computes unit economics (cost per request / per tenant), runs Infracost on Terraform diffs, and outputs savings ranked by dollars, effort, and risk. Generic across AWS, GCP, and Azure. Triggered when the user says "review the cost of X", "why is our cloud bill so high", "how much will this Terraform change cost", "find savings", "cost per request", "FinOps review", or "is this instance oversized".
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
---

# cost-review

## When to use

- User says: "cost review", "why is the bill up", "find savings", "how much will this PR cost"
- A Terraform / Pulumi / CloudFormation / Helm diff adds or resizes resources
- Monthly bill jumped and nobody knows which service caused it
- A new service is launching and needs a cost estimate and unit-cost baseline

## Steps

1. **Scope** — one service, one account/project, or one IaC diff. Read the IaC and deploy config first; never estimate from memory.
2. **Get the baseline** — billing export / cost explorer grouped by service + tag for the last 30–90 days. If unavailable, estimate from IaC and say so.
3. **For IaC diffs** — run Infracost (see commands) and record monthly delta.
4. **Walk the driver checklist** below; record each finding with evidence (file:line or billing line).
5. **Check attribution** — required tags present on every resource? Untagged spend %?
6. **Compute unit economics** — cost per 1k requests, per tenant, per GB processed.
7. **Rank savings** by `$/month ÷ effort`, then filter by risk (see ranking).
8. **Hand off** — IaC fixes to [iac-review](../iac-review); log/metric cardinality to [observability](../observability); hot-path efficiency to [perf-analysis](../perf-analysis).

## Cost-driver checklist

| Driver | Look for | Typical fix |
|---|---|---|
| Compute right-sizing | CPU p95 < 30%, memory p95 < 50%; k8s requests >> usage | Downsize one step; set requests from p95 usage |
| Idle resources | Unattached volumes, old snapshots, idle load balancers, stopped-but-billed instances, non-prod running 24/7 | Delete; schedule non-prod off nights/weekends |
| Commitment coverage | Steady baseline on on-demand pricing | Savings plans / committed-use / reservations for the floor only |
| Spot / preemptible | Stateless, retry-safe workers on on-demand | Move to spot with fallback |
| Storage tiering | Objects never read after 30d in hot tier; no lifecycle rules | Lifecycle to infrequent/archive tier; expire temp data |
| Block storage type | Provisioned-IOPS where general purpose suffices | Switch volume class |
| Data transfer / NAT egress | Traffic to object storage or registries via NAT; cross-AZ/region chatter | Private/gateway endpoints; keep chatty services in one zone |
| Logs | Debug logs in prod, full request bodies, long retention | Sample, drop fields, shorten retention, archive tier |
| Metrics cardinality | Labels with user_id, request_id, URL with IDs | Remove unbounded labels; aggregate |
| Managed-service tier | Oversized DB class, multi-AZ in dev, premium tier unused features | Downgrade tier in non-prod; right-size DB |
| Serverless | High memory setting, long timeouts, chatty invocations | Tune memory; batch |
| Orphaned environments | Preview/feature envs never torn down | TTL + automated cleanup |

## Attribution checklist

- [ ] Required tags/labels on every resource: `service`, `team`, `env`, `cost-center`
- [ ] Tag policy enforced in IaC (default tags / policy-as-code), not by hand
- [ ] Shared costs (clusters, NAT, networking) split by a stated rule (usage, requests, or even split)
- [ ] Untagged spend reported as its own line — target < 5%

## Unit economics

```text
cost_per_1k_requests = monthly_service_cost / (monthly_requests / 1000)
cost_per_tenant      = (direct_cost + allocated_shared_cost) / active_tenants
gross_margin_signal  = cost_per_tenant / revenue_per_tenant
```

Track the trend, not just the total — a rising bill with a falling unit cost is growth, not waste.

## Commands

```bash
# Terraform diff cost (public open-source tool)
# 1. On the base branch: snapshot current cost
infracost breakdown --path . --format json --out-file infracost-base.json
# 2. On the PR branch: show the monthly delta
infracost diff --path . --compare-to infracost-base.json

# Find candidate oversizing in k8s (requests vs actual usage)
kubectl top pods -n <ns> --containers
grep -rnE 'instance_type|machine_type|vm_size|sku|requests:' --include=*.tf --include=*.yaml .
```

## Ranking savings

| Score | $/month | Effort | Risk |
|---|---|---|---|
| High | > $1,000 | < 1 day, config only | none / non-prod |
| Medium | $200–1,000 | 1–5 days | reversible prod change |
| Low | < $200 | > 1 week | data-loss or availability risk |

Order: high $ + low effort + low risk first. Commitment purchases go last — right-size first, then commit to the smaller floor.

## Example

Input: Terraform diff adds `db.r6g.2xlarge` multi-AZ for `orders-service` staging and a NAT gateway.

Output (excerpt):
| # | Finding | Evidence | $/mo | Effort | Risk | Fix |
|---|---|---|---|---|---|---|
| 1 | Multi-AZ + 2xlarge in staging | `rds.tf:14` | ~$1,100 | 1 line | none | single-AZ, `large` class |
| 2 | Object storage traffic via NAT | `vpc.tf:40`, no gateway endpoint | ~$300 | 1 hr | none | add storage gateway endpoint |

## Output format

```markdown
## Cost review — <service / diff>

### Baseline
- Monthly cost: $X (source: billing export | IaC estimate)
- IaC delta (Infracost): +$Y/month
- Untagged spend: Z%

### Unit economics
| Metric | Value | Trend |

### Findings (ranked)
| # | Driver | Finding | Evidence | $/month | Effort | Risk | Fix |

### Attribution gaps
- [ ] ...

### Total identified savings
$N/month (high-confidence) + $M/month (needs validation)
```

## Rules

- NEVER recommend a change without evidence (file:line, metric, or billing line)
- NEVER buy commitments before right-sizing — you lock in the waste
- NEVER downsize prod below observed p95 + headroom
- NEVER present estimates as billed numbers — label the source of every $ figure
- ALWAYS separate one-time cleanup from recurring savings
- ALWAYS check data transfer and logs — they hide outside the compute line
- ALWAYS rank by $/effort/risk, not by $ alone
- ALWAYS report untagged spend as its own line

<!-- lifecycle:begin (generated by lifecycle/build.py — do not edit) -->
## Lifecycle

- **Phase**: operate · **Agent**: `operate`
- **Reads**: `diff` (from `.lifecycle/<run>/` when present)
- **Writes**: `findings` → `findings.json`
- **Hand off to**:
  - `iac-review` — if paths match `**/*.tf`, `**/helm/**`, `**/k8s/**`

When the step is done, record it so the next skill can pick up the output:
`route.py run record cost-review --artifact findings=<path>` (script ships with the `lifecycle-router` skill).
<!-- lifecycle:end -->
