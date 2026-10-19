# Cloud Cost Review Skill — FinOps, Right-Sizing & Infracost for Claude Code, Cursor, Copilot

> **Find the money in your cloud bill.** Cost drivers, tagging gaps, unit economics, Infracost on Terraform diffs, and savings ranked by $, effort, and risk — on AWS, GCP, or Azure.

**Keywords**: cloud cost review, finops skill, aws cost optimization, gcp cost optimization, azure cost optimization, infracost terraform, right-sizing, nat gateway egress cost, cost per request, ai cost review, cost review claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- cost-review
```

## What it does

- Walks a **cost-driver checklist** — right-sizing, idle resources, commitments, spot, storage tiering, NAT / data-transfer egress, logs, metrics cardinality, managed-service tiers
- Checks **tagging and attribution** — required tags, shared-cost split, untagged spend %
- Computes **unit economics** — cost per 1k requests, per tenant
- Runs **Infracost** on Terraform diffs for the monthly delta
- **Ranks savings** by $/month, effort, and risk — right-size before you commit
- Every finding cites evidence (file:line, metric, or billing line)

## When it triggers

- "Review the cost of this service"
- "Why is our cloud bill so high?"
- "How much will this Terraform change cost?"
- "Find savings" / "FinOps review"

## Example

Terraform diff adds a multi-AZ `2xlarge` database in staging and a NAT gateway → two ranked findings: single-AZ smaller class (~$1,100/mo, 1 line) and an object-storage gateway endpoint (~$300/mo, 1 hour).

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [iac-review](../iac-review) — apply the Terraform / Helm fixes safely
- [observability](../observability) — reduce log and metric cardinality
- [perf-analysis](../perf-analysis) — cut compute by making the hot path cheaper
- [estimation](../estimation) — size the savings work
