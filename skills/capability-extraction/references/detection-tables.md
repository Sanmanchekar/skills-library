# Detection tables — capability-extraction

Per-capability grep patterns. Read this file when Step 2 (Sweep for capability signals) needs to run.

Every hit is recorded as `path:line`. Do NOT compare across services — this is a **single-service audit**.

## notifications
| Signal | Patterns to grep |
|---|---|
| Provider SDKs | `boto3.client\('ses'\|'sns'\)`, `smtplib`, `sendgrid`, `twilio\.rest`, `msg91`, `karix`, `firebase_admin.messaging`, `nodemailer`, `whatsapp_business` |
| Direct-send calls | `send_email`, `send_sms`, `send_otp`, `send_notification`, `sendMessage`, `.send_transactional` |
| Template rendering | `render_to_string`, `Template\(`, `render_template`, HTML strings near a send |
| Retry wrapping | `for.*attempt`, `retry\(`, `tenacity`, `backoff`, `sleep.*attempt` around a send |
| Opt-out check | `unsubscribed`, `opted_out`, `consent`, `preferences` near a send |
| Coupling smell | send inside `atomic\|transaction\|@transaction`, or in a request handler with no `.delay\(\)\|enqueue` |

## pdf-generation
| Signal | Patterns to grep |
|---|---|
| Libs | `wkhtmltopdf`, `pdfkit`, `weasyprint`, `reportlab`, `puppeteer`, `chromium`, `pdf-lib`, `iText` |
| Direct calls | `.generate_pdf`, `to_pdf`, `render_pdf`, `page\.pdf\(` |
| Templates + temp files | HTML template loaded, then `NamedTemporaryFile`, `mktemp`, `/tmp/.*\.pdf`, then upload |
| Coupling smell | PDF gen in request handler (blocking CPU); PDF gen in DB transaction |

## file-upload
| Signal | Patterns to grep |
|---|---|
| Storage SDKs | `boto3\.client\('s3'\)`, `google\.cloud\.storage`, `azure\.storage\.blob`, `cloudinary`, `MinioClient` |
| MIME / size validation | `content_type`, `mimetypes`, `python-magic`, extension allowlists |
| Signed URL logic | `generate_presigned_url`, `getSignedUrl` with hardcoded expiries |
| Coupling smell | upload in request handler; missing size cap; missing content-type validation |

## audit-log
| Signal | Patterns to grep |
|---|---|
| Direct writes | `AuditLog\.create`, `db\.insert.*audit`, `.log_action`, `record_activity` |
| Ad-hoc field naming | `user_id` vs `actor_id` vs `who` used inconsistently across the same service |
| Same-transaction | audit insert inside same DB transaction as business write |
| Coupling smell | audit write inside a transaction; audit failure would roll back business write |

## feature-flags
| Signal | Patterns to grep |
|---|---|
| SaaS SDKs | `launchdarkly`, `unleash`, `growthbook`, `statsig`, `split\.io`, `flagsmith` |
| Home-grown | `is_enabled\(`, `feature_flag\(`, `Feature\.`, config-file-based flags |
| Env-var flags | `os\.environ\.get\(.*FLAG` |
| Hardcoded percentages | `random\(\) < 0\.1`, `user_id % 10 == 0` |
| Coupling smell | flag decision inside a hot loop with no caching; multiple flag systems in one service |

## scheduling
| Signal | Patterns to grep |
|---|---|
| Libs | `celery.*beat`, `sidekiq.*scheduler`, `apscheduler`, `node-cron`, `bull.*repeat`, `@Scheduled`, `airflow\.DAG` |
| Cron in code + k8s | crontab strings in source AND in `k8s/*.yaml` for the same service |
| Ad-hoc timers | `setInterval\(`, `while True.*sleep`, `Thread.*sleep.*loop` |
| Coupling smell | scheduled job with no leader election on a multi-replica deployment |

## User-defined capability

If the user asks about a capability NOT in the canonical set (e.g., "analytics", "search", "billing"), ASK for their grep patterns before scanning. Do NOT invent detection rules.
