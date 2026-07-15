# Security Review Skill — OWASP Top 10 Diff Review for Claude Code, Cursor, Copilot

> **Find exploitable bugs before they ship.** OWASP-guided review of a diff — SQL/NoSQL/OS injection, broken authz (IDOR), secrets in code, SSRF, XSS/CSRF, crypto misuse, dependency CVEs — with CWE tags, exploit sketches, and concrete fixes.

**Keywords**: security review, owasp top 10 review, ai security review, sql injection review, xss review, csrf review, idor review, ssrf review, cwe review, secrets in code, dependency cve scanner, security review claude code skill

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Sanmanchekar/skills-library/main/install.sh | bash -s -- security-review
```

## What it does

- **12 review categories** — injection, authn, authz, secrets, deserialization, SSRF, XSS, CSRF, crypto, redirects, deps, file upload
- Every finding tagged with **CWE ID** (CWE-89, CWE-79, CWE-352, ...)
- Every finding includes an **exploit sketch** — payload + expected effect
- Every finding includes a **ready-to-apply fix** as a code block
- Severity rubric anchored to real-world impact — no fluff findings
- Refuses to hand-wave ("use HTTPS", "add a WAF") — diff-level only

## When it triggers

- "Security review"
- "Check this for vulnerabilities"
- "OWASP review this"
- Diff touches auth / crypto / input handling / file upload / deserialization

## Compatible with

Claude Code · Cursor · GitHub Copilot Chat · Codex CLI · Aider · Continue · Cline · Windsurf · Sourcegraph Cody · Roo Code · Zed AI

## Related skills

- [code-review](../code-review) — general PR review
- [dependency-upgrade](../dependency-upgrade) — dep bumps + CVE triage
- [iac-review](../iac-review) — infra-side security checks
