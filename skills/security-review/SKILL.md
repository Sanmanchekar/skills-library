---
name: security-review
description: Security-focused review of a diff or file. OWASP Top 10 pass — injection (SQL/NoSQL/OS/LDAP), broken authz, secrets in code, insecure deserialization, SSRF, XSS, CSRF, cryptographic misuse, dependency CVEs, and unvalidated redirects. Emits severity-tagged findings with exploit sketch and concrete fix. Triggered when the user asks for a security review, "check this for vulnerabilities", or shares auth/crypto/input-handling code.
---

# security-review

## When to use

- User asks: "security review", "check this for vulnerabilities", "OWASP review", "is this exploitable"
- Diff touches auth, crypto, user input handling, file upload, deserialization, or config
- Pre-release audit of a service

## Review categories (in this order)

### 1. Injection
- **SQL**: any string concatenation into a query, `.format()`, f-strings with untrusted input, `%s` outside of parameter binding
- **NoSQL**: `$where`, `$eval`, or user-supplied objects passed as query filters
- **OS command**: `os.system`, `subprocess.run(shell=True)`, `exec`, `eval` with user input
- **LDAP / XPath / HTML template**: same principle — user input in a query string

### 2. Broken authentication
- Passwords stored without hashing (or with `md5`, `sha1`, `sha256` — must be bcrypt/argon2/scrypt)
- Session tokens in URL query strings
- JWT: `alg: none` accepted, secret hardcoded, no expiry, no signature verification
- Password reset tokens: reused, no expiry, guessable

### 3. Broken authorization
- IDOR: `GET /orders/{id}` without checking `order.user_id == current_user.id`
- Missing role checks — `is_admin` not enforced on admin endpoints
- Trusting client-supplied `user_id`, `tenant_id`, `role`

### 4. Secrets in code
- API keys, DB passwords, private keys, JWT secrets checked into source
- `.env` committed
- Secrets in log lines

### 5. Insecure deserialization
- `pickle.loads`, `yaml.load` (unsafe), `Marshal.load`, JS `eval` on JSON, Java `ObjectInputStream`

### 6. SSRF
- User-supplied URL passed to a fetch client without an allowlist
- No block on internal ranges (10.0.0.0/8, 169.254.169.254 — AWS IMDS)

### 7. XSS
- Server: user input rendered into HTML without escaping (`{{ user_input | safe }}`)
- Client: `innerHTML = userInput`, `dangerouslySetInnerHTML={{__html: userInput}}`
- Reflected: query params echoed unescaped

### 8. CSRF
- State-changing endpoint with cookie auth but no CSRF token, no SameSite cookie, no double-submit

### 9. Cryptographic misuse
- Homemade crypto
- Static IV/nonce, ECB mode, MD5/SHA1 for anything security-relevant
- `random.random()` for tokens (use `secrets.token_urlsafe`)
- TLS verification disabled (`verify=False`)

### 10. Unvalidated redirects + open CORS
- Redirect to user-supplied URL without allowlist
- `Access-Control-Allow-Origin: *` with `Allow-Credentials: true`

### 11. Dependency CVEs
- Check `requirements.txt` / `package.json` / `go.mod` against known-vuln versions
- Flag transitive vulns discoverable via `npm audit`, `pip-audit`, `govulncheck`

### 12. File upload
- No content-type validation, no size cap, uploaded to a path served by the web server, filename not sanitized (path traversal)

## Output format

```markdown
## Security review — <N> findings

| # | Severity | CWE | File:Line | Title |
|---|----------|-----|-----------|-------|
| 1 | CRITICAL | CWE-89 | src/orders.py:42 | SQL injection via order_id filter |

### 1. CRITICAL — CWE-89 — src/orders.py:42 — SQL injection via order_id filter
**Vulnerable code**:
` ` `python
db.execute(f"SELECT * FROM orders WHERE id = '{order_id}'")
` ` `

**Exploit**: `order_id = "' OR '1'='1"` returns all orders. `order_id = "'; DROP TABLE orders; --"` drops the table.

**Fix**:
` ` `python
db.execute("SELECT * FROM orders WHERE id = %s", (order_id,))
` ` `

**Why**: parameterized queries bind values separately from the query text; the DB driver never interprets the value as SQL.
```

## Severity guide

| Severity | Meaning |
|---|---|
| CRITICAL | Unauthenticated RCE, SQLi, auth bypass, secret leak of prod credentials |
| HIGH | Authenticated privilege escalation, IDOR, stored XSS, SSRF |
| MEDIUM | Reflected XSS, CSRF on non-critical actions, weak crypto |
| LOW | Info disclosure, missing security headers |

## Rules

- NEVER label something "won't be exploited in practice" — that's the developer's call, not the reviewer's
- ALWAYS cite the CWE (CWE-89 SQLi, CWE-79 XSS, CWE-352 CSRF, CWE-798 hardcoded creds, CWE-918 SSRF)
- ALWAYS include an exploit sketch (payload + expected effect) — abstract security advice gets ignored
- ALWAYS give a ready-to-apply fix (parameterized query, escaped output, allowlist)
- NEVER flag "use HTTPS" or "add a WAF" — these are infra, not diff-level findings
