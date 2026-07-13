# IaC Review Skill — Terraform, Helm, ECS, Kubernetes Config Review for Claude Code

> **Review your Infrastructure-as-Code before it ships.** Security (public exposure, IAM, encryption), reliability (probes, PDBs, autoscaling), drift risk, and cost — with severity-tagged findings and code-block fixes.

**Keywords**: terraform review, helm chart review, kubernetes manifest review, iac security review, terraform best practices, k8s security context, ecs task definition review, ai iac review, iac claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- iac-review
```

## What it does

- **Security**: flags `0.0.0.0/0`, IAM `*:*`, unencrypted storage, plaintext secrets, public S3
- **Reliability**: enforces readiness + liveness probes, PDBs on `replicas>1`, HPA on variable-load workloads, resource requests/limits
- **Drift**: catches hardcoded ARNs / AMI IDs and suspicious `ignore_changes`
- **Cost**: overprovisioned instances, missing log retention, unnecessary NAT gateways
- **Kubernetes**: securityContext defaults, non-default namespace + serviceAccount
- **Terraform**: pinned provider versions, remote backend, no local-exec

## When it triggers

- `.tf`, `values.yaml`, k8s manifests, `taskdef.json` in the diff
- "Review this Terraform" / "review this Helm chart" / "review this infra PR"

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — application-code PR review
- [observability](../observability) — dashboards + alerts for the infra you just shipped
- [runbook](../runbook) — runbooks for the alerts
