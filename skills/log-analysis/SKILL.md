---
name: log-analysis
description: Parse and correlate raw logs into an incident timeline. Extracts request IDs, spans, errors, and latency; joins across services; produces a UTC-ordered timeline with severity, and surfaces the smallest set of log lines that explain the incident. Stack-agnostic — works on JSON logs, plaintext logs, or LogQL / SQL query results. Triggered when the user pastes logs, asks to "analyze these logs", or "correlate logs for incident X". Pairs with the rca skill.
---

# log-analysis

## When to use

- User pastes raw logs and asks "what happened"
- User asks: "correlate logs for X", "trace request Y through the logs", "build a timeline from these logs"
- Feeds into the [rca](../rca) skill's timeline phase

## Steps

1. **Detect the format**:
   - JSON logs (each line a JSON object) — parse directly
   - Plaintext with a prefix (`2026-07-14T10:03:04Z INFO ...`) — split by regex
   - Structured but non-JSON (logfmt, key=value) — parse as such
   - Multi-line stack traces — join until the next timestamp line
2. **Normalize** to a common shape: `{ts, level, service, request_id, message, ...}`. Everything downstream is easier once normalized.
3. **Convert all timestamps to UTC** with a common format. Log sources often mix TZs.
4. **Filter** to a reasonable window (± 5 min around the incident start).
5. **Correlate**:
   - Pick a **join key** — usually `request_id` / `trace_id` / `correlation_id`. If missing, fall back to `(user_id, endpoint, ts window)`.
   - Group log lines by that key
   - Order within each group by `ts`
6. **Extract signals**:
   - First error (message + which service)
   - Retries (same request_id, incrementing attempts)
   - Latency (time from first to last log line per request)
   - Fan-out (upstream calls emitted from this request)
7. **Rank incidents**: which request_ids had the most severe errors, longest latency, or highest retry counts.
8. **Produce the timeline** (see output).

## Common patterns to detect

| Pattern | Signal | What it means |
|---|---|---|
| Retry storm | Same `request_id` retries ≥3 times within 1s | Downstream failing; backoff missing or too short |
| Cascade | Error in service A precedes errors in B, C, D within seconds | A's failure caused the downstream failures |
| Latency spike | p99 for `endpoint=X` moves from 100ms → 5s at a specific `ts` | Something changed at that time — deploy, config, downstream |
| Error burst | Sudden 100x increase in ERROR lines for one service | Hot code path just started failing |
| Missing correlation | Request enters gateway but no downstream logs | Request dropped between services — network, timeout, silent crash |
| Log flood | Repeated identical error, high volume | Broken retry loop or shared crash on hot path |

## Output format

```markdown
# Log timeline — <request_id or incident>

## Window
2026-07-14 10:00Z → 10:15Z

## Timeline (UTC)
```
10:03:04.120  gateway    INFO   req_abc  POST /checkout — user_id=42
10:03:04.150  orders     INFO   req_abc  create_order start
10:03:04.220  orders     ERROR  req_abc  stripe.APIConnectionError: read timeout after 5000ms
10:03:04.221  orders     INFO   req_abc  retry attempt=1
10:03:09.221  orders     ERROR  req_abc  stripe.APIConnectionError: read timeout after 5000ms
10:03:09.222  orders     INFO   req_abc  retry attempt=2
10:03:14.223  orders     ERROR  req_abc  stripe.APIConnectionError: giving up after 3 attempts
10:03:14.240  gateway    ERROR  req_abc  500 Internal Server Error — duration=10120ms
```

## Observations
- Stripe client timeout is 5s; retry gives up after 3 attempts (~15s total)
- User's request took 10+ seconds and returned 500
- No backoff between retries — retries are back-to-back

## Suggested next steps
- Check Stripe status page for the window
- Look for other request_ids hitting the same error class in this window (retry storm indicator)
- Consider raising client timeout or adding jittered backoff
```

## Handling volume

- If the paste is > 1000 lines: sample the first N with any ERROR, then the surrounding context lines
- If the source is a live logging system (Loki, Elasticsearch, CloudWatch): give the query, don't paste raw results
- If timestamps are missing or unreliable: use log-line order but flag "timestamps missing — order may be ingest-order, not event-order"

## Rules

- NEVER invent log lines or timestamps
- NEVER trust local-TZ timestamps — normalize to UTC
- NEVER collapse a retry storm into "there were errors" — the retry count is the signal
- ALWAYS surface the SMALLEST set of lines that explains the incident — over-including is noise
- ALWAYS separate observations (from the logs) from suggestions (your inferences)
