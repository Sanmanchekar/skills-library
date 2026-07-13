---
name: iac-review
description: Review Infrastructure-as-Code — Terraform, AWS CDK, Pulumi, Kubernetes manifests, Helm charts, ECS task definitions. Checks security (public exposure, IAM least privilege, encryption), drift risk (hardcoded ARNs, mutable resources), reliability (health checks, autoscaling, PDBs), and cost (right-sizing, unused resources). Triggered when the user asks to review a `.tf`, `.yaml`, `.json` infra file, or "review this infra change".
---

# iac-review

## When to use

- File extensions: `.tf`, `.tfvars`, `.hcl` (Terraform); `values.yaml`, `Chart.yaml` (Helm); `*.yaml` under `k8s/` or `manifests/`; `taskdef.json` (ECS)
- User asks: "review this Terraform", "review this Helm chart", "review this infra PR"

## Review rubric (per resource type)

### Security
- **Public exposure**: any `0.0.0.0/0` in a security group / NACL / firewall rule = HIGH (except explicit ALB ingress on 443)
- **IAM**: `Action: "*"` or `Resource: "*"` outside of assumed-role trust policies = CRITICAL
- **Encryption**: S3 buckets, RDS, EBS, secrets = CRITICAL if not encrypted
- **Secrets in plaintext**: any hardcoded token, password, key in `.tf` / `values.yaml` = CRITICAL
- **Public S3 / blob**: `acl = "public-read"` or public read policy = CRITICAL unless intentional (static site)

### Reliability
- **Health checks**: k8s Deployments need `readinessProbe` AND `livenessProbe`; ECS tasks need `healthCheck`
- **PodDisruptionBudget**: any Deployment with `replicas > 1` should have a PDB
- **HPA / autoscaling**: workloads with variable load need HPA — flag if absent
- **Resource requests + limits**: k8s containers MUST set `requests.cpu`, `requests.memory`, `limits.memory`; `limits.cpu` optional (throttling debate)
- **Rolling update strategy**: `maxUnavailable: 0` for critical services

### Drift + immutability
- **Hardcoded IDs**: AMI IDs, VPC IDs, ARNs pinned in code without a variable / data source
- **`ignore_changes`**: flag any `lifecycle { ignore_changes = ... }` — often masks drift

### Cost
- **Overprovisioned instance types**: `m5.4xlarge` for a stateless API with <100 req/s
- **Unused resources**: `count = 0` blocks, disconnected VPC peering, orphan EIPs
- **NAT gateways**: expensive; check if a NAT instance would work
- **Log retention**: CloudWatch Log Groups without `retention_in_days` accumulate forever

### Kubernetes-specific
- Namespace set (never default in prod)
- `serviceAccountName` set — do not use the default SA with cluster-wide permissions
- `securityContext`: `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`
- No `hostNetwork`, no `hostPath` mounts (except system pods)

### Terraform-specific
- Provider version pinned (`~> 5.0`, not unversioned)
- Backend configured — never local state for prod
- `terraform fmt` clean
- No `local-exec` provisioners running scripts (poorly reproducible)

## Output format

Same as [code-review](../code-review) — severity table + per-finding block with problem, impact, and a ready-to-apply code snippet.

## Rules

- NEVER approve a change that adds `0.0.0.0/0` without an explicit note in the PR description
- NEVER approve `IAM *:*` outside of a trust policy
- ALWAYS check state-file safety — remote backend, encryption, locking
- ALWAYS flag missing observability wiring (metrics scrape config, log shipping) on new services
